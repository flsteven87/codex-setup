#!/usr/bin/env python3
"""Safely synchronize a repository default branch and inventory local Git state."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


class GitStateError(RuntimeError):
    """Raised when repository state cannot be inspected safely."""


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    """Run Git without invoking a shell."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=False,
    )


def git_text(repo: Path, *args: str, required: bool = True) -> str:
    """Return decoded Git stdout or raise a redacted error."""
    result = run_git(repo, *args)
    if result.returncode != 0:
        if required:
            command = " ".join(args)
            raise GitStateError(f"git {command} failed with exit {result.returncode}")
        return ""
    return result.stdout.decode("utf-8", "surrogateescape").strip()


def resolve_repo(path: str) -> Path:
    """Resolve the active worktree root from any path inside it."""
    candidate = Path(path).expanduser().resolve()
    root = git_text(candidate, "rev-parse", "--show-toplevel")
    return Path(root).resolve()


def resolve_remote(repo: Path, requested: str | None) -> str:
    """Resolve one canonical remote without guessing among peers."""
    remotes = [line for line in git_text(repo, "remote").splitlines() if line]
    if requested:
        if requested not in remotes:
            raise GitStateError(f"remote {requested!r} does not exist")
        return requested
    if "origin" in remotes:
        return "origin"
    if len(remotes) == 1:
        return remotes[0]
    if not remotes:
        raise GitStateError("repository has no remote")
    raise GitStateError("multiple remotes exist and no canonical remote was supplied")


def resolve_default_branch(repo: Path, remote: str, requested: str | None) -> str:
    """Resolve the canonical remote default branch."""
    if requested:
        return requested.removeprefix("refs/heads/")

    result = run_git(repo, "ls-remote", "--symref", remote, "HEAD")
    if result.returncode == 0:
        output = result.stdout.decode("utf-8", "surrogateescape")
        for line in output.splitlines():
            if not line.startswith("ref: refs/heads/") or not line.endswith("\tHEAD"):
                continue
            return line.removeprefix("ref: refs/heads/").removesuffix("\tHEAD")

    symbolic = git_text(
        repo,
        "symbolic-ref",
        "--quiet",
        "--short",
        f"refs/remotes/{remote}/HEAD",
        required=False,
    )
    prefix = f"{remote}/"
    if symbolic.startswith(prefix):
        return symbolic[len(prefix) :]

    raise GitStateError(
        f"cannot resolve {remote}'s default branch; supply --default-branch explicitly"
    )


def verify_ref(repo: Path, ref: str) -> str | None:
    """Return a full object ID when a ref exists."""
    result = run_git(repo, "rev-parse", "--verify", ref)
    if result.returncode != 0:
        return None
    return result.stdout.decode("ascii").strip()


def ahead_behind(repo: Path, left: str, right: str) -> tuple[int, int]:
    """Return commits unique to left and right."""
    output = git_text(repo, "rev-list", "--left-right", "--count", f"{left}...{right}")
    left_count, right_count = output.split()
    return int(left_count), int(right_count)


def relation(repo: Path, local_ref: str, remote_ref: str) -> dict[str, Any]:
    """Describe local default branch position relative to its remote."""
    local_oid = verify_ref(repo, local_ref)
    remote_oid = verify_ref(repo, remote_ref)
    state: dict[str, Any] = {
        "local_oid": local_oid,
        "remote_oid": remote_oid,
        "ahead": None,
        "behind": None,
        "relation": "unresolved",
    }
    if remote_oid is None:
        state["relation"] = "missing_remote"
        return state
    if local_oid is None:
        state["relation"] = "missing_local"
        return state
    ahead, behind = ahead_behind(repo, local_ref, remote_ref)
    state.update({"ahead": ahead, "behind": behind})
    if ahead == 0 and behind == 0:
        state["relation"] = "equal"
    elif ahead == 0:
        state["relation"] = "behind"
    elif behind == 0:
        state["relation"] = "ahead"
    else:
        state["relation"] = "diverged"
    return state


def parse_worktrees(repo: Path) -> list[dict[str, Any]]:
    """Parse the stable NUL-delimited worktree porcelain format."""
    result = run_git(repo, "worktree", "list", "--porcelain", "-z")
    if result.returncode != 0:
        raise GitStateError(f"git worktree list failed with exit {result.returncode}")

    records: list[dict[str, Any]] = []
    for raw_block in result.stdout.split(b"\0\0"):
        if not raw_block:
            continue
        record: dict[str, Any] = {
            "path": None,
            "head": None,
            "branch_ref": None,
            "branch": None,
            "detached": False,
            "bare": False,
            "locked": False,
            "locked_reason": None,
            "prunable": False,
            "prunable_reason": None,
        }
        for raw_line in raw_block.split(b"\0"):
            line = raw_line.decode("utf-8", "surrogateescape")
            key, separator, value = line.partition(" ")
            if key == "worktree":
                record["path"] = value
            elif key == "HEAD":
                record["head"] = value
            elif key == "branch":
                record["branch_ref"] = value
                record["branch"] = value.removeprefix("refs/heads/")
            elif key == "detached":
                record["detached"] = True
            elif key == "bare":
                record["bare"] = True
            elif key == "locked":
                record["locked"] = True
                record["locked_reason"] = value if separator else None
            elif key == "prunable":
                record["prunable"] = True
                record["prunable_reason"] = value if separator else None
        records.append(record)
    return records


def parse_status(repo: Path) -> dict[str, Any]:
    """Parse tracked and untracked changes into one lossless entry list."""
    result = run_git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if result.returncode != 0:
        return {
            "ok": False,
            "error": f"git status failed with exit {result.returncode}",
            "entries": [],
            "counts": {},
            "dirty": True,
        }

    fields = result.stdout.split(b"\0")
    entries: list[dict[str, Any]] = []
    index = 0
    unmerged_codes = {"DD", "AU", "UD", "UA", "DU", "AA", "UU"}
    while index < len(fields):
        raw = fields[index]
        index += 1
        if not raw:
            continue
        decoded = raw.decode("utf-8", "surrogateescape")
        if len(decoded) < 3:
            continue
        xy = decoded[:2]
        path = decoded[3:]
        entry: dict[str, Any] = {"xy": xy, "path": path, "categories": []}
        if (xy[0] in {"R", "C"} or xy[1] in {"R", "C"}) and index < len(fields):
            original = fields[index]
            index += 1
            entry["orig_path"] = original.decode("utf-8", "surrogateescape")
        if xy == "??":
            entry["categories"].append("untracked")
        elif xy in unmerged_codes:
            entry["categories"].append("unmerged")
        else:
            if xy[0] != " ":
                entry["categories"].append("staged")
            if xy[1] != " ":
                entry["categories"].append("unstaged")
        entries.append(entry)

    counts = Counter(category for entry in entries for category in entry["categories"])
    return {
        "ok": True,
        "error": None,
        "entries": entries,
        "counts": dict(sorted(counts.items())),
        "dirty": bool(entries),
    }


def operation_state(repo: Path) -> list[str]:
    """Return in-progress Git operations for one worktree."""
    git_dir_text = git_text(repo, "rev-parse", "--absolute-git-dir", required=False)
    if not git_dir_text:
        return ["unreadable_git_dir"]
    git_dir = Path(git_dir_text)
    probes = {
        "merge": git_dir / "MERGE_HEAD",
        "rebase": git_dir / "rebase-merge",
        "rebase_apply": git_dir / "rebase-apply",
        "cherry_pick": git_dir / "CHERRY_PICK_HEAD",
        "revert": git_dir / "REVERT_HEAD",
        "bisect": git_dir / "BISECT_LOG",
        "sequencer": git_dir / "sequencer",
    }
    return [name for name, path in probes.items() if path.exists()]


def upstream_state(repo: Path) -> dict[str, Any]:
    """Return upstream identity and divergence for the checked-out branch."""
    upstream = git_text(
        repo,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
        required=False,
    )
    if not upstream:
        return {"upstream": None, "upstream_exists": False, "ahead": None, "behind": None}
    upstream_exists = verify_ref(repo, upstream) is not None
    if not upstream_exists:
        return {"upstream": upstream, "upstream_exists": False, "ahead": None, "behind": None}
    ahead, behind = ahead_behind(repo, "HEAD", upstream)
    return {
        "upstream": upstream,
        "upstream_exists": True,
        "ahead": ahead,
        "behind": behind,
    }


def inspect_worktrees(repo: Path, raw_worktrees: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach status and operation state to every worktree record."""
    inspected: list[dict[str, Any]] = []
    for record in raw_worktrees:
        item = dict(record)
        path_text = record.get("path")
        path = Path(path_text) if path_text else None
        item["exists"] = bool(path and path.exists())
        item["active"] = bool(path and path.exists() and path.resolve() == repo)
        if record.get("bare") or not path or not path.exists():
            item["status"] = {
                "ok": False,
                "error": "worktree path is unavailable",
                "entries": [],
                "counts": {},
                "dirty": True,
            }
            item["operations"] = []
            item["upstream_state"] = {
                "upstream": None,
                "upstream_exists": False,
                "ahead": None,
                "behind": None,
            }
        else:
            item["status"] = parse_status(path)
            item["operations"] = operation_state(path)
            item["upstream_state"] = (
                upstream_state(path)
                if record.get("branch")
                else {"upstream": None, "upstream_exists": False, "ahead": None, "behind": None}
            )
        item["attention"] = bool(
            item["status"]["dirty"]
            or item["operations"]
            or item["detached"]
            or item["locked"]
            or item["prunable"]
            or not item["exists"]
        )
        inspected.append(item)
    return inspected


def branch_names(repo: Path) -> list[str]:
    """Return every local branch name."""
    output = git_text(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    return [line for line in output.splitlines() if line]


def branch_inventory(
    repo: Path,
    default_branch: str,
    remote_ref: str,
    worktrees: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Classify every local branch mechanically against the remote default."""
    worktree_by_branch = {
        item["branch"]: item for item in worktrees if item.get("branch") is not None
    }
    remote_exists = verify_ref(repo, remote_ref) is not None
    branches: list[dict[str, Any]] = []
    for name in branch_names(repo):
        ref = f"refs/heads/{name}"
        oid = verify_ref(repo, ref)
        upstream = git_text(
            repo,
            "for-each-ref",
            "--format=%(upstream:short)",
            ref,
            required=False,
        )
        upstream = upstream or None
        upstream_exists = bool(upstream and verify_ref(repo, upstream))
        upstream_ahead = None
        upstream_behind = None
        if upstream_exists and upstream:
            upstream_ahead, upstream_behind = ahead_behind(repo, ref, upstream)

        ahead = None
        behind = None
        integrated = None
        if remote_exists:
            ahead, behind = ahead_behind(repo, ref, remote_ref)
            integrated = (
                run_git(repo, "merge-base", "--is-ancestor", ref, remote_ref).returncode == 0
            )

        checked_out = worktree_by_branch.get(name)
        if name == default_branch:
            classification = "default"
        elif upstream and not upstream_exists:
            classification = "upstream_gone"
        elif integrated:
            classification = "integrated"
        elif ahead and behind:
            classification = "diverged"
        elif ahead:
            classification = "unique"
        else:
            classification = "unverified"

        commit_meta = git_text(repo, "log", "-1", "--format=%cI%x00%s", ref)
        commit_date, _, subject = commit_meta.partition("\0")
        branches.append(
            {
                "name": name,
                "oid": oid,
                "upstream": upstream,
                "upstream_exists": upstream_exists,
                "upstream_ahead": upstream_ahead,
                "upstream_behind": upstream_behind,
                "ahead_of_remote_default": ahead,
                "behind_remote_default": behind,
                "integrated_into_remote_default": integrated,
                "classification": classification,
                "checked_out": checked_out is not None,
                "worktree_path": checked_out.get("path") if checked_out else None,
                "worktree_attention": checked_out.get("attention") if checked_out else False,
                "commit_date": commit_date,
                "subject": subject,
            }
        )
    return branches


def stash_inventory(repo: Path) -> list[dict[str, str]]:
    """Return stashes because they are hidden local work."""
    output = git_text(repo, "stash", "list", "--format=%gd%x00%H%x00%cI%x00%s")
    stashes: list[dict[str, str]] = []
    for line in output.splitlines():
        if not line:
            continue
        name, oid, date, subject = line.split("\0", 3)
        stashes.append({"name": name, "oid": oid, "date": date, "subject": subject})
    return stashes


def build_audit(
    repo: Path,
    remote: str,
    default_branch: str,
) -> dict[str, Any]:
    """Build a complete read-only inventory."""
    remote_ref = f"refs/remotes/{remote}/{default_branch}"
    local_ref = f"refs/heads/{default_branch}"
    raw_worktrees = parse_worktrees(repo)
    worktrees = inspect_worktrees(repo, raw_worktrees)
    branches = branch_inventory(repo, default_branch, remote_ref, worktrees)
    stashes = stash_inventory(repo)
    classifications = Counter(item["classification"] for item in branches)
    dirty_entries = sum(len(item["status"]["entries"]) for item in worktrees)
    return {
        "repo_root": str(repo),
        "remote": remote,
        "default_branch": default_branch,
        "local_default_ref": local_ref,
        "remote_default_ref": remote_ref,
        "default_state": relation(repo, local_ref, remote_ref),
        "summary": {
            "worktrees": len(worktrees),
            "attention_worktrees": sum(bool(item["attention"]) for item in worktrees),
            "dirty_worktrees": sum(bool(item["status"]["dirty"]) for item in worktrees),
            "detached_worktrees": sum(bool(item["detached"]) for item in worktrees),
            "operation_worktrees": sum(bool(item["operations"]) for item in worktrees),
            "local_branches": len(branches),
            "branch_classifications": dict(sorted(classifications.items())),
            "dirty_entries": dirty_entries,
            "stashes": len(stashes),
        },
        "worktrees": worktrees,
        "branches": branches,
        "stashes": stashes,
    }


def path_collision(left: str, right: str) -> bool:
    """Return whether two repository-relative paths can obstruct checkout."""
    left_parts = PurePosixPath(left).parts
    right_parts = PurePosixPath(right).parts
    shortest = min(len(left_parts), len(right_parts))
    return left_parts[:shortest] == right_parts[:shortest]


def incoming_paths(repo: Path, local_oid: str, remote_oid: str) -> list[str]:
    """Return paths changed by the fetched default-branch fast-forward."""
    result = run_git(repo, "diff", "--name-only", "-z", f"{local_oid}..{remote_oid}")
    if result.returncode != 0:
        raise GitStateError("cannot enumerate incoming default-branch paths")
    return [
        item.decode("utf-8", "surrogateescape")
        for item in result.stdout.split(b"\0")
        if item
    ]


def colliding_paths(candidates: list[str], incoming: list[str]) -> list[str]:
    """Return local paths that overlap paths changed by the fast-forward."""
    return sorted(
        path
        for path in candidates
        if any(path_collision(path, incoming_path) for incoming_path in incoming)
    )


def untracked_collisions(
    repo: Path,
    worktree: dict[str, Any],
    local_oid: str,
    remote_oid: str,
) -> list[str]:
    """Return untracked paths that can collide with the fetched fast-forward."""
    incoming = incoming_paths(repo, local_oid, remote_oid)
    untracked = [
        entry["path"]
        for entry in worktree["status"]["entries"]
        if "untracked" in entry["categories"]
    ]
    return colliding_paths(untracked, incoming)


def ignored_collisions(
    repo: Path,
    worktree: dict[str, Any],
    local_oid: str,
    remote_oid: str,
) -> list[str]:
    """Return ignored paths that can collide with the fetched fast-forward."""
    worktree_path = Path(worktree["path"])
    result = run_git(
        worktree_path,
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "-z",
    )
    if result.returncode != 0:
        raise GitStateError("cannot enumerate ignored default-worktree paths")
    ignored = [
        item.decode("utf-8", "surrogateescape")
        for item in result.stdout.split(b"\0")
        if item
    ]
    return colliding_paths(ignored, incoming_paths(repo, local_oid, remote_oid))


def blocked_result(
    repo: Path,
    remote: str | None,
    default_branch: str | None,
    fetch: dict[str, Any],
    blockers: list[dict[str, Any]],
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one stable blocked result."""
    return {
        "repo_root": str(repo),
        "remote": remote,
        "default_branch": default_branch,
        "status": "blocked",
        "action": "none",
        "fetch": fetch,
        "before": before,
        "after": after if after is not None else before,
        "blockers": blockers,
    }


def sync_default(
    repo: Path,
    requested_remote: str | None,
    requested_default: str | None,
    fetch_requested: bool,
) -> dict[str, Any]:
    """Fetch and safely align the local default branch to its remote tip."""
    fetch: dict[str, Any] = {"attempted": fetch_requested, "ok": None}
    try:
        remote = resolve_remote(repo, requested_remote)
    except GitStateError as error:
        return blocked_result(
            repo,
            None,
            requested_default,
            fetch,
            [{"code": "remote_unresolved", "detail": str(error)}],
        )

    if fetch_requested:
        result = run_git(repo, "fetch", "--prune", "--tags", remote)
        fetch["ok"] = result.returncode == 0
        if result.returncode != 0:
            return blocked_result(
                repo,
                remote,
                requested_default,
                fetch,
                [
                    {
                        "code": "fetch_failed",
                        "detail": f"git fetch failed with exit {result.returncode}",
                    }
                ],
            )

    try:
        default_branch = resolve_default_branch(repo, remote, requested_default)
    except GitStateError as error:
        return blocked_result(
            repo,
            remote,
            requested_default,
            fetch,
            [{"code": "default_branch_unresolved", "detail": str(error)}],
        )

    local_ref = f"refs/heads/{default_branch}"
    remote_ref = f"refs/remotes/{remote}/{default_branch}"
    before = relation(repo, local_ref, remote_ref)
    if before["remote_oid"] is None:
        return blocked_result(
            repo,
            remote,
            default_branch,
            fetch,
            [{"code": "remote_default_missing", "detail": remote_ref}],
            before,
        )
    if before["relation"] == "equal":
        return {
            "repo_root": str(repo),
            "remote": remote,
            "default_branch": default_branch,
            "status": "aligned",
            "action": "already_current",
            "fetch": fetch,
            "before": before,
            "after": before,
            "blockers": [],
        }
    if before["relation"] in {"ahead", "diverged"}:
        return blocked_result(
            repo,
            remote,
            default_branch,
            fetch,
            [
                {
                    "code": f"local_default_{before['relation']}",
                    "detail": "local-only default-branch commits require an explicit recovery decision",
                }
            ],
            before,
        )

    shallow = git_text(repo, "rev-parse", "--is-shallow-repository") == "true"
    if shallow and before["relation"] != "missing_local":
        return blocked_result(
            repo,
            remote,
            default_branch,
            fetch,
            [{"code": "shallow_repository", "detail": "ancestry proof is incomplete"}],
            before,
        )

    if before["relation"] == "missing_local":
        result = run_git(repo, "branch", "--track", default_branch, f"{remote}/{default_branch}")
        if result.returncode != 0:
            return blocked_result(
                repo,
                remote,
                default_branch,
                fetch,
                [
                    {
                        "code": "create_local_default_failed",
                        "detail": f"git branch failed with exit {result.returncode}",
                    }
                ],
                before,
            )
        action = "created_local_default"
    else:
        raw_worktrees = parse_worktrees(repo)
        default_worktrees = [item for item in raw_worktrees if item.get("branch_ref") == local_ref]
        if len(default_worktrees) > 1:
            return blocked_result(
                repo,
                remote,
                default_branch,
                fetch,
                [
                    {
                        "code": "multiple_default_worktrees",
                        "detail": [item.get("path") for item in default_worktrees],
                    }
                ],
                before,
            )
        if default_worktrees:
            worktree = inspect_worktrees(repo, default_worktrees)[0]
            blockers: list[dict[str, Any]] = []
            if worktree["locked"]:
                blockers.append({"code": "default_worktree_locked", "detail": worktree["path"]})
            if worktree["prunable"] or not worktree["exists"]:
                blockers.append(
                    {"code": "default_worktree_unavailable", "detail": worktree["path"]}
                )
            if worktree["operations"]:
                blockers.append(
                    {"code": "default_operation_in_progress", "detail": worktree["operations"]}
                )
            tracked_entries = [
                entry
                for entry in worktree["status"]["entries"]
                if "untracked" not in entry["categories"]
            ]
            if tracked_entries:
                blockers.append(
                    {
                        "code": "default_tracked_changes",
                        "detail": [entry["path"] for entry in tracked_entries],
                    }
                )
            if not worktree["status"]["ok"]:
                blockers.append(
                    {"code": "default_status_unreadable", "detail": worktree["status"]["error"]}
                )
            if worktree["prunable"] or not worktree["exists"] or not worktree["status"]["ok"]:
                return blocked_result(
                    repo,
                    remote,
                    default_branch,
                    fetch,
                    blockers,
                    before,
                )
            collisions = untracked_collisions(
                repo,
                worktree,
                before["local_oid"],
                before["remote_oid"],
            )
            if collisions:
                blockers.append({"code": "untracked_incoming_collision", "detail": collisions})
            ignored = ignored_collisions(
                repo,
                worktree,
                before["local_oid"],
                before["remote_oid"],
            )
            if ignored:
                blockers.append({"code": "ignored_incoming_collision", "detail": ignored})
            if blockers:
                return blocked_result(
                    repo,
                    remote,
                    default_branch,
                    fetch,
                    blockers,
                    before,
                )
            result = run_git(
                Path(worktree["path"]),
                "merge",
                "--ff-only",
                "--no-overwrite-ignore",
                before["remote_oid"],
            )
            if result.returncode != 0:
                return blocked_result(
                    repo,
                    remote,
                    default_branch,
                    fetch,
                    [
                        {
                            "code": "fast_forward_worktree_failed",
                            "detail": f"git merge --ff-only failed with exit {result.returncode}",
                        }
                    ],
                    before,
                )
            action = "fast_forwarded_default_worktree"
        else:
            result = run_git(
                repo,
                "update-ref",
                local_ref,
                before["remote_oid"],
                before["local_oid"],
            )
            if result.returncode != 0:
                return blocked_result(
                    repo,
                    remote,
                    default_branch,
                    fetch,
                    [
                        {
                            "code": "fast_forward_ref_failed",
                            "detail": f"git update-ref failed with exit {result.returncode}",
                        }
                    ],
                    before,
                )
            action = "fast_forwarded_default_ref"

    after = relation(repo, local_ref, remote_ref)
    if after["relation"] != "equal":
        return blocked_result(
            repo,
            remote,
            default_branch,
            fetch,
            [
                {
                    "code": "postcondition_failed",
                    "detail": "local and remote default refs are not equal after synchronization",
                }
            ],
            before,
            after,
        )
    return {
        "repo_root": str(repo),
        "remote": remote,
        "default_branch": default_branch,
        "status": "aligned",
        "action": action,
        "fetch": fetch,
        "before": before,
        "after": after,
        "blockers": [],
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("sync-default", "audit"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("repo", help="Repository or linked-worktree path")
        subparser.add_argument(
            "--remote", help="Canonical remote; defaults to origin or sole remote"
        )
        subparser.add_argument("--default-branch", help="Canonical branch; defaults to remote HEAD")
        subparser.add_argument("--json", action="store_true", help="Emit structured JSON")
        if command == "sync-default":
            subparser.add_argument(
                "--fetch", action="store_true", help="Fetch remote refs and tags"
            )
    return parser.parse_args()


def main() -> int:
    """Run the requested operation and emit one deterministic result."""
    args = parse_args()
    try:
        repo = resolve_repo(args.repo)
        if args.command == "sync-default":
            result = sync_default(repo, args.remote, args.default_branch, args.fetch)
            exit_code = 0 if result["status"] == "aligned" else 2
        else:
            remote = resolve_remote(repo, args.remote)
            default_branch = resolve_default_branch(repo, remote, args.default_branch)
            result = build_audit(repo, remote, default_branch)
            exit_code = 0
    except GitStateError as error:
        result = {"status": "error", "error": str(error)}
        exit_code = 2

    if args.json:
        json.dump(result, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
