---
name: git-state-audit
description: Use only when the user explicitly invokes `$git-state-audit` to collect read-only repository evidence and produce a broad git-state, recovery, and cleanup-risk report. This skill never delivers work, pulls updates, switches accounts, or deletes Git state; route proven local branch/worktree cleanup to `$git-cleanup`.
---

# Git State Audit

Produce an evidence-backed repository state report and cleanup risk map. Report only unless the user explicitly approves a specific follow-up action.

## Rules

- Final user-facing audit report MUST be in Traditional Chinese unless the user explicitly requests another language.
- Default to read-only local evidence. Run `git fetch` only when the user explicitly requests a
  remote evidence refresh; fetching updates remote-tracking refs but does not authorize any other
  mutation.
- Never stage, commit, push, edit files, delete branches/stashes/worktrees, reset, run `git clean` or `git worktree prune`, force-push, or otherwise mutate repository state during the audit.
- Never pull, switch branches, switch GitHub accounts, or retry through a different identity. Report
  authentication or visibility failures as limitations. Redact token-like values.
- If the audit supports cleanup/housekeeping, complete this audit before recommending any deletion.

## Codex Quick Path

Prefer the bundled evidence collector from the repository root:

```bash
skill_dir="<absolute path to this skill directory>"
python3 "$skill_dir/scripts/git_state_audit.py" .
```

The helper runs the standard local evidence commands, redacts token-like values, summarizes dirty state, branch tracking, stash/worktree counts, shallow status, conditional branch checks, and skips optional checks with explicit reasons.

Only when the user explicitly asks to synchronize remote evidence, add `--fetch`. A request to update
the local default branch or change GitHub identity is a separate action outside this skill.

Do not paste the whole helper output into the final answer unless the user asks for raw evidence. Use it to produce the concise report in the Output Format below. If the helper fails or is unavailable, fall back to the manual Evidence Commands.

## Evidence Commands

Run from the repository root. Parallelize independent reads when useful, but keep command evidence attributable.

```bash
git status -sb
git status -uall --porcelain
git branch -vv
git branch -r
git remote -v
git stash list --date=iso
git worktree list --porcelain
git log --oneline --all --graph --decorate -30
git reflog --date=iso | head -40
git for-each-ref --format='%(refname:short) %(upstream:track) %(committerdate:iso)' refs/heads
git rev-parse --is-shallow-repository
```

Conditional commands:

```bash
git fetch --all --prune --tags 2>&1  # only after an explicit sync request
git branch --merged origin/main
git branch --no-merged origin/main
git log --oneline origin/main..<branch>
git cherry -v origin/main <branch>
gh pr list --state all --search '<branch> repo:<owner>/<repo>' --json number,title,state,mergedAt,headRefName,baseRefName,url --limit 20
gh pr view <number> --json number,title,state,mergedAt,mergeCommit,headRefName,baseRefName,commits,files,url
git diff $(git merge-base origin/main <branch>)..<branch> | git patch-id --stable
git diff <mergeCommit>^..<mergeCommit> | git patch-id --stable
```

Optional edge checks, when relevant:

```bash
git fsck --no-reflogs --unreachable --no-progress 2>&1 | head -20
git submodule status --recursive
test -f .gitattributes && rg -n 'filter=lfs|diff=lfs|merge=lfs' .gitattributes
git lfs status
```

Skip optional commands that are clearly irrelevant or unavailable, and state what was skipped.

## Analyze

- Working tree: staged, unstaged, untracked, ignored-worthy artifacts, local config, mode/line-ending noise.
- Branches: merged, ahead, behind, diverged, no upstream, `[gone]`, local-only work.
- Stash: count, age, branch context, whether it may be the only copy.
- Worktrees: dirty, locked, missing, orphaned, clean merged branches.
- Remote evidence: freshness limits, unpushed commits/tags, remote-only branches, shared-branch risk.
- Recovery: reflog-only commits, dangling commits newer than 7 days, detached HEAD-only commits.

## Output Format

Keep the final report concise and in Traditional Chinese. Preserve command names, branch names, paths, commit subjects, and exact errors in original form when useful.

```text
## Git 全景
- Repo / current branch / HEAD
- Working tree: <clean | N staged, M unstaged, K untracked>
- Branches: <local count> local (<ahead> ahead, <behind> behind, <diverged> diverged, <gone> gone), <remote count> remote
- Stash: <count> entries (oldest: <age or none>)
- Worktrees: <count> (<dirty/orphan/locked notes>)
- Remote: <names and URLs redacted if token-like>

## 深度分析
<Findings grouped by dimension. Cite command evidence, not guesses. Keep this compact.>

## 處置建議（依風險分級）

### Safe
<Reversible/read-only actions, and local cleanup only when evidence proves no unique work remains.>

### Needs Review
<Items requiring semantic confirmation, such as stale stashes, local-only branches, remote deletion, or large untracked files.>

### Destructive
<Irreversible/high-risk actions needing explicit per-item approval.>

## 未執行 / 限制
<Skipped commands, shallow clone caveats, missing remotes, auth failures, or submodule/LFS checks not applicable.>
```

## Recommendation Rules

- Evidence first, recommendation second.
- Local branch/worktree cleanup is Safe only when the tip is reachable from `main`/`origin/main` or proven squash-merged, the worktree is clean and unlocked, and no unique local work remains.
- Treat `[gone]` plus ahead commits as unpushed work unless PR metadata plus matching cumulative patch-id proves squash merge. Do not rely on `git cherry` alone.
- Classify untracked files before cleanup: artifact, local config, generated output, or in-progress work.
- For detached HEAD, list commits reachable only from HEAD before suggesting any branch switch.
- Redact token-like values in URLs or command output.
- When the audit identifies user-approved Safe local branch or worktree cleanup,
  recommend an explicit `$git-cleanup` follow-up. Do not invoke it automatically.
- Do not repeat `$git-cleanup`'s complete branch grouping and deletion plan. Identify candidates and
  risks; let `$git-cleanup` collect fresh deletion evidence at its own approval gates.
- Do not hand off stashes, remote branches, remote PRs, reflog-only commits,
  dangling commits, or repository maintenance to `$git-cleanup`; keep those in
  this report as separate follow-up work requiring explicit scope and approval.

## Safety Stops

Stop and ask before action if:

- The current worktree has uncommitted changes and the user asks to switch branches, reset, clean, or remove a worktree.
- A stash or dangling commit may contain the only copy of work.
- A branch is ahead of upstream, local-only, or diverged, unless it has been proven squash-merged into `main` by PR metadata plus matching cumulative patch-id.
- `git fetch` reports errors or auth failures that make remote analysis incomplete.
- The repo is shallow and the requested conclusion depends on full history.
