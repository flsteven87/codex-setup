#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


CREDENTIAL_URL_RE = re.compile(r"(https?://)[^/\s:@]+(?::[^/\s@]*)?@")
TOKEN_RE = re.compile(
    r"(github_pat_[A-Za-z0-9_]+|gh[opsur]_[A-Za-z0-9_]{10,}|"
    r"glpat-[A-Za-z0-9_-]{10,}|xox[baprs]-[A-Za-z0-9-]{10,}|"
    r"sk-[A-Za-z0-9]{20,})"
)
GITHUB_OWNER_RES = [
    re.compile(r"^https://github\.com/([^/\s]+)/[^/\s]+/?$"),
    re.compile(r"^git@github\.com:([^/\s]+)/[^/\s]+/?$"),
    re.compile(r"^ssh://git@github\.com/([^/\s]+)/[^/\s]+/?$"),
]


@dataclass(frozen=True)
class PorcelainSummary:
    staged: int
    unstaged: int
    untracked: int

    @property
    def clean(self) -> bool:
        return self.staged == 0 and self.unstaged == 0 and self.untracked == 0


@dataclass(frozen=True)
class CommandResult:
    name: str
    command: list[str]
    exit_code: int
    output: str


def redact(text: str) -> str:
    text = CREDENTIAL_URL_RE.sub(r"\1<redacted>@", text)
    return TOKEN_RE.sub("<redacted-token>", text)


def github_owner_from_remote(remote_url: str) -> str | None:
    normalized = remote_url.strip()
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    for pattern in GITHUB_OWNER_RES:
        match = pattern.match(normalized)
        if match:
            return match.group(1)
    return None


def is_github_auth_failure(output: str) -> bool:
    lowered = output.lower()
    markers = [
        "repository not found",
        "authentication failed",
        "could not read username",
        "permission denied",
    ]
    return any(marker in lowered for marker in markers)


def parse_gh_auth_accounts(output: str) -> tuple[set[str], str | None]:
    accounts: set[str] = set()
    active: str | None = None
    current: str | None = None

    for line in output.splitlines():
        account_match = re.search(r"account ([^\s(]+)", line)
        if account_match:
            current = account_match.group(1)
            accounts.add(current)
        if "Active account: true" in line and current:
            active = current

    return accounts, active


def summarize_porcelain(lines: Iterable[str]) -> PorcelainSummary:
    staged = 0
    unstaged = 0
    untracked = 0

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        if not line:
            continue
        if line.startswith("??"):
            untracked += 1
            continue
        if len(line) < 2:
            continue
        if line[0] not in (" ", "?"):
            staged += 1
        if line[1] not in (" ", "?"):
            unstaged += 1

    return PorcelainSummary(staged=staged, unstaged=unstaged, untracked=untracked)


def is_safe_pull_candidate(
    *,
    branch: str,
    upstream: str,
    clean: bool,
    ahead: int,
    behind: int,
) -> bool:
    return (
        branch == "main"
        and upstream == "origin/main"
        and clean
        and ahead == 0
        and behind > 0
    )


def run_command(
    args: list[str],
    *,
    cwd: Path,
    name: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        output = completed.stdout or ""
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + f"\nTimed out after {timeout}s"
        exit_code = 124

    return CommandResult(
        name=name or " ".join(args),
        command=args,
        exit_code=exit_code,
        output=redact(output.strip()),
    )


def git(args: list[str], *, cwd: Path, name: str | None = None, timeout: int = 120) -> CommandResult:
    return run_command(["git", *args], cwd=cwd, name=name, timeout=timeout)


def git_output(args: list[str], *, cwd: Path) -> str:
    result = git(args, cwd=cwd)
    if result.exit_code != 0:
        return ""
    return result.output.strip()


def retry_after_github_auth_switch(
    result: CommandResult,
    *,
    cwd: Path,
    decisions: list[str],
    enabled: bool,
) -> list[CommandResult]:
    if result.exit_code == 0 or not is_github_auth_failure(result.output):
        return [result]
    if not enabled:
        decisions.append(f"GitHub auth switch not enabled after {result.name} failed")
        return [result]
    if shutil.which("gh") is None:
        decisions.append(f"GitHub auth switch skipped because gh is unavailable after {result.name} failed")
        return [result]

    remote_url = git_output(["remote", "get-url", "origin"], cwd=cwd)
    owner = github_owner_from_remote(remote_url)
    if not owner:
        decisions.append(f"GitHub auth switch skipped because origin is not a github.com remote after {result.name} failed")
        return [result]

    status_result = run_command(["gh", "auth", "status"], cwd=cwd, name="gh auth status")
    accounts, active = parse_gh_auth_accounts(status_result.output)
    retry_results = [result, status_result]
    if owner not in accounts:
        decisions.append(f"GitHub auth switch skipped because account {owner} is not logged in")
        return retry_results
    if active == owner:
        decisions.append(f"GitHub auth switch skipped because {owner} is already active")
        return retry_results

    switch_result = run_command(
        ["gh", "auth", "switch", "--hostname", "github.com", "--user", owner],
        cwd=cwd,
        name=f"gh auth switch --hostname github.com --user {owner}",
    )
    retry_results.append(switch_result)
    if switch_result.exit_code != 0:
        decisions.append(f"GitHub auth switch to {owner} failed; {result.name} was not retried")
        return retry_results

    retry_result = run_command(result.command, cwd=cwd, name=f"{result.name} (retry after gh auth switch)")
    retry_results.append(retry_result)
    decisions.append(
        f"GitHub auth switched to {owner} after {result.name} failed; retry exit={retry_result.exit_code}"
    )
    return retry_results


def resolve_repo_root(cwd: Path) -> Path:
    result = git(["rev-parse", "--show-toplevel"], cwd=cwd)
    if result.exit_code != 0 or not result.output.strip():
        print("Not a git repository.", file=sys.stderr)
        raise SystemExit(2)
    return Path(result.output.strip())


def parse_ahead_behind(cwd: Path) -> tuple[int, int]:
    result = git(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"], cwd=cwd)
    if result.exit_code != 0:
        return (0, 0)
    parts = result.output.split()
    if len(parts) < 2:
        return (0, 0)
    try:
        return (int(parts[0]), int(parts[1]))
    except ValueError:
        return (0, 0)


def branch_track_counts(ref_output: str) -> dict[str, int]:
    counts = {"local": 0, "ahead": 0, "behind": 0, "diverged": 0, "gone": 0}
    for line in ref_output.splitlines():
        if not line.strip():
            continue
        counts["local"] += 1
        fields = line.split("\t")
        track = fields[1] if len(fields) > 1 else ""
        has_ahead = "ahead" in track
        has_behind = "behind" in track
        if "[gone]" in track:
            counts["gone"] += 1
        if has_ahead:
            counts["ahead"] += 1
        if has_behind:
            counts["behind"] += 1
        if has_ahead and has_behind:
            counts["diverged"] += 1
    return counts


def count_remote_branches(cwd: Path) -> int:
    refs = git_output(["for-each-ref", "--format=%(refname:short)", "refs/remotes"], cwd=cwd)
    return len(
        [
            line
            for line in refs.splitlines()
            if line.strip() and not line.strip().endswith("/HEAD")
        ]
    )


def summarize_worktrees(output: str) -> dict[str, object]:
    count = 0
    notes: list[str] = []
    current_path = ""
    for line in output.splitlines():
        if line.startswith("worktree "):
            count += 1
            current_path = line.removeprefix("worktree ")
        elif line.startswith("locked"):
            notes.append(f"locked: {current_path}")
        elif line.startswith("prunable"):
            notes.append(f"prunable: {current_path}")
    return {"count": count, "notes": notes}


def oldest_stash(stash_output: str) -> str:
    lines = [line for line in stash_output.splitlines() if line.strip()]
    if not lines:
        return "none"
    return lines[-1].split(":", 1)[0]


def command_block(result: CommandResult) -> str:
    output = result.output if result.output else "(no output)"
    command = " ".join(result.command)
    return f"### {result.name}\n`{command}`\nexit: {result.exit_code}\n\n```text\n{output}\n```"


def build_summary(
    *,
    repo_root: Path,
    branch: str,
    head: str,
    porcelain: str,
    ref_output: str,
    remote_count: int,
    stash_output: str,
    worktree_output: str,
    remote_output: str,
    shallow_output: str,
) -> dict[str, object]:
    status = summarize_porcelain(porcelain.splitlines())
    branch_counts = branch_track_counts(ref_output)
    worktrees = summarize_worktrees(worktree_output)
    remote_lines = [line for line in remote_output.splitlines() if line.strip()]

    if status.clean:
        working_tree = "clean"
    else:
        working_tree = (
            f"{status.staged} staged, {status.unstaged} unstaged, "
            f"{status.untracked} untracked"
        )

    return {
        "repo": str(repo_root),
        "branch": branch or "DETACHED",
        "head": head,
        "working_tree": working_tree,
        "working_tree_counts": asdict(status),
        "branches": branch_counts,
        "remote_branch_count": remote_count,
        "stash_count": len([line for line in stash_output.splitlines() if line.strip()]),
        "oldest_stash": oldest_stash(stash_output),
        "worktrees": worktrees,
        "remotes": remote_lines,
        "is_shallow": shallow_output.strip() or "unknown",
    }


def render_markdown(summary: dict[str, object], decisions: list[str], results: list[CommandResult]) -> str:
    branches = summary["branches"]
    worktrees = summary["worktrees"]
    worktree_notes = ", ".join(worktrees["notes"]) if worktrees["notes"] else "no locked/prunable notes"
    remotes = summary["remotes"] or ["none"]

    lines = [
        "# Git State Audit Evidence",
        "",
        "## Git 全景",
        f"- Repo / current branch / HEAD: {summary['repo']} / {summary['branch']} / {summary['head']}",
        f"- Working tree: {summary['working_tree']}",
        (
            "- Branches: "
            f"{branches['local']} local ({branches['ahead']} ahead, "
            f"{branches['behind']} behind, {branches['diverged']} diverged, "
            f"{branches['gone']} gone), {summary['remote_branch_count']} remote"
        ),
        f"- Stash: {summary['stash_count']} entries (oldest: {summary['oldest_stash']})",
        f"- Worktrees: {worktrees['count']} ({worktree_notes})",
        "- Remote:",
        *[f"  - {remote}" for remote in remotes],
        f"- Shallow repository: {summary['is_shallow']}",
        "",
        "## Auto Decisions",
        *[f"- {decision}" for decision in decisions],
        "",
        "## Command Evidence",
    ]
    lines.extend(command_block(result) for result in results)
    return "\n\n".join(lines)


def origin_main_exists(cwd: Path) -> bool:
    result = git(["rev-parse", "--verify", "--quiet", "origin/main"], cwd=cwd)
    return result.exit_code == 0


def collect_audit(
    cwd: Path,
    *,
    fetch: bool,
    safe_pull: bool,
    gh_auth_switch: bool,
    edge_checks: bool,
) -> dict[str, object]:
    repo_root = resolve_repo_root(cwd)
    results: list[CommandResult] = []
    decisions: list[str] = []

    if fetch:
        fetch_result = git(["fetch", "--all", "--prune", "--tags"], cwd=repo_root, name="git fetch --all --prune --tags")
        fetch_results = retry_after_github_auth_switch(
            fetch_result,
            cwd=repo_root,
            decisions=decisions,
            enabled=gh_auth_switch,
        )
        results.extend(fetch_results)
        decisions.append(f"fetch final exit={fetch_results[-1].exit_code}")
    else:
        decisions.append("fetch skipped; pass --fetch only after an explicit sync request")

    branch = git_output(["branch", "--show-current"], cwd=repo_root)
    upstream = git_output(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], cwd=repo_root)
    porcelain_now = git_output(["status", "-uall", "--porcelain"], cwd=repo_root)
    ahead, behind = parse_ahead_behind(repo_root)
    clean = summarize_porcelain(porcelain_now.splitlines()).clean

    if safe_pull and is_safe_pull_candidate(
        branch=branch,
        upstream=upstream,
        clean=clean,
        ahead=ahead,
        behind=behind,
    ):
        pull_result = git(["pull", "--ff-only"], cwd=repo_root, name="git pull --ff-only")
        pull_results = retry_after_github_auth_switch(
            pull_result,
            cwd=repo_root,
            decisions=decisions,
            enabled=gh_auth_switch,
        )
        results.extend(pull_results)
        decisions.append(
            "safe pull ran because clean local main was behind origin/main; "
            f"final exit={pull_results[-1].exit_code}"
        )
    elif safe_pull:
        decisions.append(
            "safe pull skipped "
            f"(branch={branch or 'DETACHED'}, upstream={upstream or 'none'}, "
            f"clean={clean}, ahead={ahead}, behind={behind})"
        )
    else:
        decisions.append("safe pull skipped; pass --safe-pull only after an explicit update request")

    command_specs = [
        ("git status -sb", ["status", "-sb"]),
        ("git status -uall --porcelain", ["status", "-uall", "--porcelain"]),
        ("git branch -vv", ["branch", "-vv"]),
        ("git branch -r", ["branch", "-r"]),
        ("git remote -v", ["remote", "-v"]),
        ("git stash list --date=iso", ["stash", "list", "--date=iso"]),
        ("git worktree list --porcelain", ["worktree", "list", "--porcelain"]),
        ("git log --oneline --all --graph --decorate -30", ["log", "--oneline", "--all", "--graph", "--decorate", "-30"]),
        ("git reflog --date=iso", ["reflog", "--date=iso"]),
        (
            "git for-each-ref refs/heads",
            ["for-each-ref", "--format=%(refname:short)\t%(upstream:track)\t%(committerdate:iso)", "refs/heads"],
        ),
        ("git rev-parse --is-shallow-repository", ["rev-parse", "--is-shallow-repository"]),
    ]

    if origin_main_exists(repo_root):
        command_specs.extend(
            [
                ("git branch --merged origin/main", ["branch", "--merged", "origin/main"]),
                ("git branch --no-merged origin/main", ["branch", "--no-merged", "origin/main"]),
            ]
        )
    else:
        decisions.append("origin/main conditional branch checks skipped because origin/main is unavailable")

    if (repo_root / ".gitmodules").exists():
        command_specs.append(("git submodule status --recursive", ["submodule", "status", "--recursive"]))
    else:
        decisions.append("submodule check skipped because .gitmodules is absent")

    gitattributes = repo_root / ".gitattributes"
    if gitattributes.exists() and "filter=lfs" in gitattributes.read_text(errors="replace"):
        if shutil.which("git-lfs") or shutil.which("git-lfs.exe") or "lfs" in git(["lfs", "version"], cwd=repo_root).output:
            command_specs.append(("git lfs status", ["lfs", "status"]))
        else:
            decisions.append("git lfs status skipped because git-lfs is unavailable")
    else:
        decisions.append("LFS check skipped because .gitattributes has no filter=lfs entry")

    if edge_checks:
        command_specs.append(("git fsck --no-reflogs --lost-found", ["fsck", "--no-reflogs", "--lost-found"]))
    else:
        decisions.append("git fsck edge check skipped by default; pass --edge-checks when recovery analysis needs it")

    for name, args in command_specs:
        result = git(args, cwd=repo_root, name=name, timeout=180 if args and args[0] == "fsck" else 120)
        if name == "git reflog --date=iso":
            result = CommandResult(
                name=result.name,
                command=result.command,
                exit_code=result.exit_code,
                output="\n".join(result.output.splitlines()[:40]),
            )
        if name == "git fsck --no-reflogs --lost-found":
            result = CommandResult(
                name=result.name,
                command=result.command,
                exit_code=result.exit_code,
                output="\n".join(result.output.splitlines()[:20]),
            )
        results.append(result)

    result_by_name = {result.name: result.output for result in results}
    summary = build_summary(
        repo_root=repo_root,
        branch=git_output(["branch", "--show-current"], cwd=repo_root),
        head=git_output(["rev-parse", "--short", "HEAD"], cwd=repo_root),
        porcelain=result_by_name.get("git status -uall --porcelain", ""),
        ref_output=result_by_name.get("git for-each-ref refs/heads", ""),
        remote_count=count_remote_branches(repo_root),
        stash_output=result_by_name.get("git stash list --date=iso", ""),
        worktree_output=result_by_name.get("git worktree list --porcelain", ""),
        remote_output=result_by_name.get("git remote -v", ""),
        shallow_output=result_by_name.get("git rev-parse --is-shallow-repository", ""),
    )

    return {
        "summary": summary,
        "decisions": decisions,
        "commands": [asdict(result) for result in results],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect git state audit evidence safely.")
    parser.add_argument("path", nargs="?", default=os.getcwd(), help="Repository path or subdirectory.")
    parser.add_argument("--fetch", action="store_true", help="Run git fetch --all --prune --tags after an explicit sync request.")
    parser.add_argument("--safe-pull", action="store_true", help="Allow conditional git pull --ff-only after an explicit update request.")
    parser.add_argument("--gh-auth-switch", action="store_true", help="Allow one GitHub CLI account switch after separate explicit approval.")
    parser.add_argument("--edge-checks", action="store_true", help="Run slower recovery-oriented edge checks.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of Markdown.")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    audit = collect_audit(
        Path(args.path).resolve(),
        fetch=args.fetch,
        safe_pull=args.safe_pull,
        gh_auth_switch=args.gh_auth_switch,
        edge_checks=args.edge_checks,
    )
    if args.json:
        print(json.dumps(audit, ensure_ascii=False, indent=2))
    else:
        commands = [CommandResult(**command) for command in audit["commands"]]
        print(render_markdown(audit["summary"], audit["decisions"], commands))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
