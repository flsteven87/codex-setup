# Semantic Convergence Protocol

Use this protocol only for owned items that survive mechanical reachability and exact squash
checks.

Before applying it, verify ownership under `SKILL.md`'s ownership boundary. For an other-authored
PR or branch, record `EXTERNAL`, its owner, and at most the narrow dependency or conflict affecting
owned work. Do not perform full semantic convergence unless the user explicitly names that exact
external item.

## Contents

- [Reconstruct the real comparison boundary](#reconstruct-the-real-comparison-boundary)
- [Use an evidence ladder](#use-an-evidence-ladder)
- [Analyze branches](#analyze-branches)
- [Analyze stashes and recovery commits](#analyze-stashes-and-recovery-commits)
- [Choose a disposition](#choose-a-disposition)
- [Handle owned open PRs](#handle-owned-open-prs)
- [Record a decision table](#record-a-decision-table)

## Reconstruct the real comparison boundary

Patch mismatches usually mean the comparison boundary is wrong, not that Git is broken.

1. Resolve the PR's merge-time head, base, merge commit, and commit list.
2. Compare the merge-time head with the current remote tip to detect post-merge pushes.
3. For stacked PRs, compare `original base..head`; do not substitute today's `main`.
4. For split delivery, map each old commit to every successor PR rather than comparing whole trees.
5. Distinguish normal merge commits, squash commits, rebases, and conflict-resolution commits.
6. Compare final behavior and tests when history equivalence alone cannot prove supersession.

## Use an evidence ladder

Prefer the strongest applicable evidence:

1. **Reachability** — the exact tip is an ancestor of refreshed default upstream.
2. **Exact squash proof** — exact PR head/base plus matching stable cumulative patch.
3. **Tree equivalence** — the relevant branch tree equals the landed result at the correct boundary.
4. **Split-commit proof** — every unique commit patch maps to one or more merged successor PRs.
5. **Behavioral supersession** — current source and regression tests implement the same requirement
   with newer or safer behavior.
6. **Negative proof** — the old delta contradicts current contracts, docs, migrations, or tests.

Evidence 5–6 requires code review and an explicit written rationale. Commit subjects, branch age,
`git cherry`, matching file counts, and matching shortstats are leads, never sufficient proof alone.

## Analyze branches

For each unresolved owned branch:

- verify PR author, commit email, and Codex provenance before treating it as owned;
- list unique commits and the merge base;
- identify related PRs/issues/specs from commits and GitHub metadata;
- inspect paths and symbols changed by each unique commit;
- search current default branch for the behavior, tests, migrations, and follow-up fixes;
- use `range-diff`, stable patch IDs, and targeted tree diffs where appropriate;
- identify branch-after-merge commits separately from the original PR content;
- check whether merging the branch would reintroduce removed APIs, stale migrations, unsafe
  behavior, duplicated modules, or obsolete documentation;
- distinguish an independently shippable feature from a mixed historical integration branch.

Prefer `ADAPT` when useful behavior exists but the branch contains unrelated work, stale seams, or
already-squashed commits. Prefer `FINISH` only when the remaining delta is coherent and current.

## Analyze stashes and recovery commits

Treat a stash or reflog-only commit as a possible last copy until proven otherwise.

For a stash:

1. Record its object ID, parent commit, timestamp, message, file set, and shortstat.
2. Determine which branch and task produced it.
3. Compare its delta against the final landed commit or PR at the same base.
4. Separate later-main drift from stash-authored changes.
5. Drop it only when every valuable semantic landed or was intentionally rejected.

For a recovery-only commit:

1. Inspect the complete patch and its original parent/base.
2. Review it against current specs and source.
3. Extract useful semantics onto fresh default branch; do not create a permanent rescue branch for
   an otherwise obsolete commit.
4. Leave the unreferenced object to normal Git garbage collection after disposition; do not rewrite
   reflogs or run immediate destructive pruning merely for visual cleanliness.

## Choose a disposition

### DROP

For an item that survived the helper's mechanical reachability and exact-squash checks, require one
of:

- complete split-commit mapping;
- tree equivalence at the correct boundary;
- reviewed behavioral supersession plus evidence the old version is redundant or worse.

Record the proof and exact authorized action. Preserve the item when it is dirty, is the sole
recovery copy, requires unauthorized remote deletion, or otherwise crosses a safety boundary.

### ADAPT

Use when only part of the work remains valuable. Write a tiny acceptance list, implement it from
fresh default branch, validate it, merge it, then drop the historical source.

Treat unported UX, tests, requirements, data contracts, and operational knowledge as unique value
even when the source implementation is architecturally wrong. Retain the source until the exact
destination and owner are recorded and the acceptance list is delivered, unless the user explicitly
rejects the remaining value.

### FINISH

Use when the whole remaining delta is current, cohesive, and aligned with the spec. Rebase only
within normal repository policy and never to hide already-squashed history. Prefer a fresh delivery
branch when the source history is noisy.

### RETAIN

Name the owner, reason, intended destination, and next review point. Retention without a next action
is deferred noise, not a decision.

### BLOCKED

State the missing evidence or authorization and preserve the only copy. Do not downgrade a blocker
to a warning and delete anyway.

### EXTERNAL

Record the verified owner and any narrow dependency on owned work. Take no convergence action unless
the user explicitly named that exact item.

## Handle owned open PRs

- For `DROP`, close the PR and delete its branch only when the active request authorizes remote
  cleanup; otherwise record the exact pending remote action.
- For `FINISH`, review and deliver through normal protection only when terminal delivery was
  authorized; otherwise record the remaining gate.
- For `ADAPT`, preserve the source branch until its acceptance list, destination, and owner are
  recorded and the valuable behavior is delivered, or until the user explicitly rejects that value.

## Record a decision table

Before execution, produce:

| Item | Evidence | Unique value | Risk if merged | Disposition | Exact action |
|---|---|---|---|---|---|

After execution, record the delivered PR/commit for every `ADAPT` or `FINISH` row and deletion
receipts for every `DROP` row. Re-run the inventory instead of assuming the commands converged.
