#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROTECTED_BRANCH_RE = re.compile(r"^(main|master|develop|release(?:/.*)?)$")


class SafetyError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandResult:
    args: list[str]
    exit_code: int
    stdout: str


@dataclass(frozen=True)
class Worktree:
    path: Path
    branch: str | None
    detached: bool
    locked: bool
    prunable: bool
    primary: bool


@dataclass(frozen=True)
class FinalizationPlan:
    repo: Path
    control_worktree: Path
    task_worktree: Worktree
    branch: str
    expected_head: str
    default_branch: str
    integrated_ref: str
    integrated_head: str
    proof: str
    force_delete: bool
    fast_forward_default: bool

    @property
    def actions(self) -> list[str]:
        delete_flag = "-D" if self.force_delete else "-d"
        if self.task_worktree.primary:
            actions = [
                shlex.join(
                    [
                        "git",
                        "-C",
                        str(self.task_worktree.path),
                        "switch",
                        self.default_branch,
                    ]
                )
            ]
            if self.fast_forward_default:
                actions.append(
                    shlex.join(
                        [
                            "git",
                            "-C",
                            str(self.task_worktree.path),
                            "merge",
                            "--ff-only",
                            self.integrated_head,
                        ]
                    )
                )
            actions.append(
                shlex.join(
                    [
                        "git",
                        "-C",
                        str(self.task_worktree.path),
                        "branch",
                        delete_flag,
                        "--",
                        self.branch,
                    ]
                )
            )
            return actions
        return [
            shlex.join(
                [
                    "git",
                    "-C",
                    str(self.task_worktree.path),
                    "switch",
                    "--detach",
                    self.expected_head,
                ]
            ),
            shlex.join(
                [
                    "git",
                    "-C",
                    str(self.task_worktree.path),
                    "branch",
                    delete_flag,
                    "--",
                    self.branch,
                ]
            ),
            shlex.join(
                [
                    "git",
                    "-C",
                    str(self.control_worktree),
                    "worktree",
                    "remove",
                    str(self.task_worktree.path),
                ]
            ),
        ]


def run(args: list[str], *, cwd: Path, input_text: str | None = None) -> CommandResult:
    completed = subprocess.run(
        args,
        cwd=str(cwd),
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env={**os.environ, "LC_ALL": "C"},
    )
    return CommandResult(
        args=args,
        exit_code=completed.returncode,
        stdout=(completed.stdout or "").strip(),
    )


def git(
    cwd: Path, *args: str, check: bool = True, input_text: str | None = None
) -> CommandResult:
    result = run(["git", *args], cwd=cwd, input_text=input_text)
    if check and result.exit_code != 0:
        command = " ".join(result.args)
        raise SafetyError(
            f"{command} failed (exit {result.exit_code}): {result.stdout}"
        )
    return result


def rev_parse(cwd: Path, revision: str) -> str:
    result = git(
        cwd, "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"
    )
    return result.stdout.splitlines()[-1]


def is_ancestor(cwd: Path, ancestor: str, descendant: str) -> bool:
    result = git(cwd, "merge-base", "--is-ancestor", ancestor, descendant, check=False)
    if result.exit_code not in (0, 1):
        raise SafetyError(
            f"git merge-base --is-ancestor failed (exit {result.exit_code}): {result.stdout}"
        )
    return result.exit_code == 0


def parse_worktrees(cwd: Path) -> list[Worktree]:
    output = git(cwd, "worktree", "list", "--porcelain").stdout
    records: list[dict[str, object]] = []
    current: dict[str, object] = {}
    for line in [*output.splitlines(), ""]:
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value if value else True

    worktrees: list[Worktree] = []
    for index, record in enumerate(records):
        branch_ref = record.get("branch")
        branch = None
        if isinstance(branch_ref, str) and branch_ref.startswith("refs/heads/"):
            branch = branch_ref.removeprefix("refs/heads/")
        worktrees.append(
            Worktree(
                path=Path(str(record["worktree"])).resolve(),
                branch=branch,
                detached=bool(record.get("detached", False)),
                locked="locked" in record,
                prunable="prunable" in record,
                primary=index == 0,
            )
        )
    return worktrees


def patch_id(cwd: Path, start: str, end: str) -> str:
    diff = git(cwd, "diff", "--full-index", "--binary", start, end).stdout
    if not diff:
        raise SafetyError(f"empty cumulative diff for {start}..{end}")
    result = git(cwd, "patch-id", "--stable", input_text=diff)
    fields = result.stdout.split()
    if not fields:
        raise SafetyError(f"git patch-id produced no proof for {start}..{end}")
    return fields[0]


def squash_patch_matches(cwd: Path, expected_head: str, squash_commit: str) -> bool:
    parents = git(cwd, "rev-list", "--parents", "-n", "1", squash_commit).stdout.split()
    if len(parents) != 2:
        raise SafetyError("squash proof requires a single-parent squash commit")
    squash_parent = parents[1]
    branch_base = git(cwd, "merge-base", squash_parent, expected_head).stdout.strip()
    return patch_id(cwd, branch_base, expected_head) == patch_id(
        cwd, squash_parent, squash_commit
    )


def path_contains(parent: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def assert_clean_worktree(worktree: Path) -> None:
    status = git(worktree, "status", "--porcelain=v1", "--untracked-files=all").stdout
    if status:
        raise SafetyError(f"task worktree is dirty:\n{status}")


def build_plan(
    *,
    repo: Path,
    worktree_path: Path,
    branch: str,
    expected_head_revision: str,
    default_branch: str,
    integrated_ref: str,
    squash_commit_revision: str | None,
) -> FinalizationPlan:
    repo = repo.resolve()
    git(repo, "rev-parse", "--show-toplevel")
    worktrees = parse_worktrees(repo)
    task_path = worktree_path.resolve()
    matches = [worktree for worktree in worktrees if worktree.path == task_path]
    if len(matches) != 1:
        raise SafetyError(f"task worktree is not registered exactly once: {task_path}")
    task_worktree = matches[0]

    if PROTECTED_BRANCH_RE.fullmatch(branch):
        raise SafetyError(f"refusing to finalize protected branch: {branch}")
    if branch == default_branch:
        raise SafetyError("delivery branch and default branch must differ")
    if task_worktree.detached or task_worktree.branch != branch:
        raise SafetyError(
            f"task worktree branch mismatch: expected {branch}, found {task_worktree.branch or 'DETACHED'}"
        )
    if task_worktree.locked or task_worktree.prunable:
        raise SafetyError("task worktree is locked or prunable")

    assert_clean_worktree(task_path)

    branch_head = rev_parse(repo, f"refs/heads/{branch}")
    expected_head = rev_parse(repo, expected_head_revision)
    if branch_head != expected_head:
        raise SafetyError(
            f"delivery branch moved: recorded {expected_head}, current {branch_head}"
        )

    integrated_head = rev_parse(repo, integrated_ref)
    proof = ""
    force_delete = False
    if is_ancestor(repo, expected_head, integrated_head):
        proof = "delivered head is an ancestor of the integration ref"
    elif squash_commit_revision:
        squash_commit = rev_parse(repo, squash_commit_revision)
        if not is_ancestor(repo, squash_commit, integrated_head):
            raise SafetyError(
                "supplied squash commit is not contained by the integration ref"
            )
        if not squash_patch_matches(repo, expected_head, squash_commit):
            raise SafetyError("squash commit patch does not match the delivered branch")
        proof = f"cumulative patch matches squash commit {squash_commit}"
        force_delete = True
    else:
        raise SafetyError(
            "delivered head is not contained by the integration ref and no squash proof was supplied"
        )

    default_ref = f"refs/heads/{default_branch}"
    default_head = rev_parse(repo, default_ref)
    fast_forward_default = default_head != integrated_head

    if task_worktree.primary:
        checked_out_elsewhere = [
            worktree for worktree in worktrees[1:] if worktree.branch == default_branch
        ]
        if checked_out_elsewhere:
            raise SafetyError(
                f"default branch is already checked out at {checked_out_elsewhere[0].path}"
            )
        if not is_ancestor(repo, default_head, integrated_head):
            raise SafetyError(
                f"local {default_branch} cannot fast-forward to {integrated_ref}"
            )
        control_worktree = task_path
    else:
        controls = [
            worktree
            for worktree in worktrees
            if worktree.path != task_path
            and worktree.path.exists()
            and not worktree.prunable
        ]
        if not controls:
            raise SafetyError("no surviving control worktree is available")
        control_worktree = controls[0].path

    return FinalizationPlan(
        repo=repo,
        control_worktree=control_worktree,
        task_worktree=task_worktree,
        branch=branch,
        expected_head=expected_head,
        default_branch=default_branch,
        integrated_ref=integrated_ref,
        integrated_head=integrated_head,
        proof=proof,
        force_delete=force_delete,
        fast_forward_default=fast_forward_default,
    )


def execute_plan(plan: FinalizationPlan) -> None:
    if not plan.task_worktree.primary and path_contains(
        plan.task_worktree.path, Path.cwd()
    ):
        raise SafetyError("run --execute from outside the linked task worktree")

    refreshed = build_plan(
        repo=plan.repo,
        worktree_path=plan.task_worktree.path,
        branch=plan.branch,
        expected_head_revision=plan.expected_head,
        default_branch=plan.default_branch,
        integrated_ref=plan.integrated_ref,
        squash_commit_revision=(
            plan.proof.removeprefix("cumulative patch matches squash commit ")
            if plan.force_delete
            else None
        ),
    )
    if refreshed != plan:
        raise SafetyError("finalization state changed after preview; run a new preview")

    delete_flag = "-D" if plan.force_delete else "-d"
    if plan.task_worktree.primary:
        git(plan.task_worktree.path, "switch", plan.default_branch)
        if plan.fast_forward_default:
            git(plan.task_worktree.path, "merge", "--ff-only", plan.integrated_head)
        assert_clean_worktree(plan.task_worktree.path)
        current_branch_head = rev_parse(
            plan.task_worktree.path, f"refs/heads/{plan.branch}"
        )
        if current_branch_head != plan.expected_head:
            raise SafetyError("delivery branch moved immediately before deletion")
        git(plan.task_worktree.path, "branch", delete_flag, "--", plan.branch)
    else:
        git(plan.task_worktree.path, "switch", "--detach", plan.expected_head)
        assert_clean_worktree(plan.task_worktree.path)
        current_branch_head = rev_parse(
            plan.task_worktree.path, f"refs/heads/{plan.branch}"
        )
        if current_branch_head != plan.expected_head:
            raise SafetyError("delivery branch moved immediately before deletion")
        git(plan.task_worktree.path, "branch", delete_flag, "--", plan.branch)
        git(plan.control_worktree, "worktree", "remove", str(plan.task_worktree.path))


def render(plan: FinalizationPlan, *, executed: bool) -> dict[str, object]:
    return {
        "safe": True,
        "mode": "executed" if executed else "preview",
        "branch": plan.branch,
        "expected_head": plan.expected_head,
        "worktree": str(plan.task_worktree.path),
        "integration_ref": plan.integrated_ref,
        "integration_head": plan.integrated_head,
        "proof": plan.proof,
        "actions": plan.actions,
        "remote_branch": "untouched",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely finalize the local branch and worktree from one completed delivery."
    )
    parser.add_argument(
        "--repo",
        required=True,
        type=Path,
        help="Any surviving worktree for the repository.",
    )
    parser.add_argument(
        "--worktree", required=True, type=Path, help="Exact task worktree path."
    )
    parser.add_argument("--branch", required=True, help="Exact local delivery branch.")
    parser.add_argument(
        "--expected-head", required=True, help="Recorded delivery HEAD."
    )
    parser.add_argument(
        "--default-branch", required=True, help="Local default branch name."
    )
    parser.add_argument(
        "--integrated-ref",
        required=True,
        help="Fresh ref containing the delivered work.",
    )
    parser.add_argument(
        "--squash-commit", help="Verified squash commit for patch-equivalence proof."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Recheck the preview and perform local cleanup.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        plan = build_plan(
            repo=args.repo,
            worktree_path=args.worktree,
            branch=args.branch,
            expected_head_revision=args.expected_head,
            default_branch=args.default_branch,
            integrated_ref=args.integrated_ref,
            squash_commit_revision=args.squash_commit,
        )
        if args.execute:
            execute_plan(plan)
        print(json.dumps(render(plan, executed=args.execute), indent=2))
        return 0
    except SafetyError as error:
        print(
            json.dumps({"safe": False, "error": str(error)}, indent=2), file=sys.stderr
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
