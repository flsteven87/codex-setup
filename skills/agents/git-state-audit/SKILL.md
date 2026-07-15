---
name: git-state-audit
description: Use when the user asks for git audit, git status audit, git 全景, git 現況, 整理 git, branch/stash/worktree cleanup, handoff safety, or whether local git state is safe to clean.
---

# Git State Audit

Produce an evidence-backed repository state report and cleanup risk map. Report only unless the user explicitly approves a specific follow-up action.

## Rules

- Final user-facing audit report MUST be in Traditional Chinese unless the user explicitly requests another language.
- Allowed: read-only git commands, `scripts/git_state_audit.py`, `git fetch --all --prune --tags`, and `git pull --ff-only` only when current branch is clean local `main` that is only behind `origin/main`.
- Never stage, commit, push, edit files, delete branches/stashes/worktrees, reset, clean, prune, force-push, or otherwise mutate repository state during the audit.
- If fetch/pull hits GitHub auth or visibility errors, inspect `gh auth status` and `gh auth switch --help`; if another authenticated account likely has access, switch once non-interactively and retry the safe fetch/pull once. Redact token-like values.
- If the audit supports cleanup/housekeeping, complete this audit before recommending any deletion.

## Codex Quick Path

Prefer the bundled evidence collector from the repository root:

```bash
python3 ~/.agents/skills/git-state-audit/scripts/git_state_audit.py .
```

The helper runs the standard evidence commands, redacts token-like values, summarizes dirty state, branch tracking, stash/worktree counts, shallow status, conditional branch checks, and skips optional checks with explicit reasons. It runs `git fetch --all --prune --tags` by default and only runs `git pull --ff-only` when the Rules allow it. If a GitHub fetch/pull fails with an auth or visibility error and `gh auth status` shows the remote owner is already logged in, the helper switches to that account once and retries. Use `--no-fetch`, `--no-safe-pull`, or `--no-gh-auth-switch` when the user explicitly wants to disable those automated steps.

Do not paste the whole helper output into the final answer unless the user asks for raw evidence. Use it to produce the concise report in the Output Format below. If the helper fails or is unavailable, fall back to the manual Evidence Commands.

## Evidence Commands

Run from the repository root. Parallelize independent reads when useful, but keep command evidence attributable.

```bash
git fetch --all --prune --tags 2>&1
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
git pull --ff-only 2>&1  # only when allowed by Rules
gh auth status 2>&1      # only after auth/visibility failure
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
git fsck --no-reflogs --lost-found 2>&1 | head -20
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
- Remote sync: stale refs, unpushed commits/tags, remote-only branches, shared-branch risk.
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

## Safety Stops

Stop and ask before action if:

- The current worktree has uncommitted changes and the user asks to switch branches, reset, clean, or remove a worktree.
- A stash or dangling commit may contain the only copy of work.
- A branch is ahead of upstream, local-only, or diverged, unless it has been proven squash-merged into `main` by PR metadata plus matching cumulative patch-id.
- `git fetch` reports errors or auth failures that make remote analysis incomplete.
- The repo is shallow and the requested conclusion depends on full history.
