# Safety and Authorization Edges

Use this reference only for blocked or destructive edge cases. Apply the ownership, default
authorization, and completion boundaries from `SKILL.md`. Require mechanical proof from the bundled
helper or semantic proof from `semantic-convergence.md`; age, names, `[gone]`, subjects, and
`git cherry` are investigation leads, not deletion authority.

## Contents

- [Dirty merged branch rescue](#dirty-merged-branch-rescue)
- [Remote cleanup boundaries](#remote-cleanup-boundaries)

## Dirty merged branch rescue

Preserve the only copy before changing refs. Use `stash push -u`, apply rather than pop, verify the
new branch contains the complete staged/unstaged/untracked set, and retain the stash through commit
validation. Do not auto-generate a WIP commit unless committing was explicitly requested.

Avoid rebasing or merging a squash-merged source branch onto the default branch. Those operations
replay already-incorporated commits and obscure the new work. Move only the dirty delta to a fresh
branch based on the default remote.

## Remote cleanup boundaries

Remote branch deletion is an external write. Require explicit finish/remote-cleanup intent and
limit automatic deletion to the configured prefix (default `codex/`). Exclude the current branch,
protected branches, open PR heads, and any branch whose tip moved after its merged PR. Keep remote
branches outside the prefix as reported exceptions.

An explicit request to drop named PRs, or to drop the exact PRs just classified in the active
conversation, authorizes closing those PRs and deleting their exact head branches even outside the
default prefix or owner scope. This is item-specific authority, not namespace-wide authority. Pin
each PR's open state, head OID, and branch immediately before mutation; abort that item if any value
changed. Never extend this authority to adjacent branches or another open PR.

After deletion, fetch/prune, confirm the PR is closed, and require `git ls-remote --heads` to return
no exact matching ref. Record the deleted branch and final head OID so the action remains auditable.
