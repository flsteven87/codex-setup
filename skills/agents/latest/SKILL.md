---
name: latest
description: "Align the local default branch, inventory every linked worktree and local Git artifact, and refresh the primary checkout's MEMORY.md from verified repository truth. Use when project state has drifted or needs consolidation before choosing the next task."
---

# Latest

Establish a verified checkpoint: align the active repository's local default branch with its
fetched remote, inventory every local Git artifact that needs attention, and reconcile the
primary-checkout `MEMORY.md` so the next move starts from current evidence.

## Mutation budget

- Fetch the canonical remote and tags, create a missing local default branch at the fetched tip,
  fast-forward that branch, and edit the primary checkout's `MEMORY.md`.
- Preserve every feature branch, non-default worktree, file change, stash, and unique commit in
  place. Cleanup, switching, committing, stashing, rebasing, non-fast-forward integration,
  deletion, and remote mutation require a separate explicit request.
- Treat Git, pull requests, tickets, specs, ADRs, changelog, and source as authoritative.
  The primary checkout's `MEMORY.md` is a compact operational cache shared by linked worktrees;
  `CONTEXT.md` remains the domain glossary.
- Limit default-branch synchronization to the active repository. Sibling repositories explicitly
  in scope are fetch-and-inventory only unless the user separately authorizes synchronization.

## Steps

1. **Establish control.** Resolve the skill directory, active worktree, canonical remote and its
   default branch, all linked worktrees, current branch, upstreams, operation state, the primary
   checkout from the first `git worktree list --porcelain` record, and
   `<primary-checkout>/MEMORY.md`. Read applicable `AGENTS.md` and `CLAUDE.md` from the active
   worktree, then read memory before external evidence. Complete this step when the pre-mutation Git
   anchors and every worktree path are captured.

2. **Align the local default.** Run:

   ```bash
   python3 "$skill_dir/scripts/git_state.py" sync-default "$repo" --fetch --json
   ```

   Pass `--remote` or `--default-branch` only when repository instructions identify a canonical
   value that remote HEAD cannot resolve. The helper performs exactly one safe branch:

   - create a missing local default branch at the fetched remote tip;
   - fast-forward its checkout when tracked state is clean and untracked paths do not collide;
   - atomically fast-forward its ref when it is not checked out; or
   - return a blocker for fetch failure, incomplete ancestry, local-only/diverged commits, a dirty
     or unavailable default worktree, an in-progress operation, or an incoming untracked collision.

   Keep the current feature checkout in place. Complete this step only when the helper proves the
   local and fetched remote default OIDs equal, or returns `blocked` with the exact refs and safety
   reason. A blocker does not prevent the read-only inventory and memory reconciliation that follow.

3. **Inventory local Git state.** Run after the synchronization attempt:

   ```bash
   python3 "$skill_dir/scripts/git_state.py" audit "$repo" --json
   ```

   Reconcile the output into these report classes:

   - default branch: aligned, ahead, diverged, missing, or sync-blocked;
   - worktrees needing attention: staged, unstaged, unmerged, untracked, detached, locked,
     prunable, missing, or carrying an in-progress Git operation;
   - local branches: default, mechanically integrated into fetched default, unique, diverged,
     upstream-gone, or unverified; name the owning worktree and upstream divergence;
   - hidden local work: stashes and detached worktrees.

   A mechanically integrated branch is a cleanup candidate, not deletion authority. Mark ownership
   as unresolved unless current evidence identifies it. Complete this step when every worktree and
   local branch appears once, all changed/untracked paths are attributed to their worktree, and all
   stashes and in-progress operations are accounted for. Never silently truncate: if file volume is
   too large for the reply, give exhaustive counts, affected worktrees, top path groups, and the
   exact omitted-entry count.

4. **Refresh checkpoint evidence.** Inspect recent fetched-default commits, tags, and the top of
   `CHANGELOG.md`. Verify only pull requests and tickets named by the current memory or user scope.
   Preserve user-owned decisions; record contradictory evidence as a tension. Complete this step
   when every current-state claim has a source or is labeled unverified.

5. **Reconcile the primary checkout's `MEMORY.md`.** If it exists, replace `## Current State` with
   one objective, default sync result, compact local-Git attention summary, exact next action,
   blockers or pending decisions, and current Git anchors. Keep load-bearing constraints and durable
   pointers; correct stale mechanical facts and remove completed narrative. Keep detailed
   branch/worktree/file lists in the report rather than memory. Prefer fewer than 120 lines without
   discarding required constraints. Complete this step when every changed claim matches the gathered
   evidence.

   If the primary checkout's `MEMORY.md` does not exist, report `NO_MEMORY`, provide the verified
   checkpoint, and recommend `handoff` when the user wants to establish shared memory.

6. **Verify and report.** Re-run the audit after memory edits and confirm the synchronization result
   did not change. Report, in the user's language:

   - fetched sources and local-default result with both OIDs;
   - dirty worktrees with categorized file counts and paths;
   - branch decision table with upstream/default divergence and cleanup candidates;
   - stashes, detached or in-progress state;
   - memory changes, preserved tensions, blockers, and validation gaps; and
   - a two-to-three-sentence ready-next summary.

## Completion

`latest` is complete only when the fetched remote default is identified; local default equality is
proved or an exact non-destructive blocker is recorded; every worktree, local branch, dirty path,
stash, and operation state is classified; each memory edit has evidence; and the next action is
explicit. Never describe the repository as clean when only the current worktree was inspected.
