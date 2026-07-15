---
name: ship
description: "Finish a completed change through the applicable review, verification, commit, push, PR merge, deployment, and post-deploy check as one action. Use for /ship, $ship, ship this, commit and push, finish or close this branch/PR, merge this PR, deploy this, 出貨, 收尾, 本地收尾, 收掉或合併這個 PR, 推上去, or 部署. Explicit invocation authorizes bounded in-scope fixes and the clear repository delivery path; it does not authorize force-push, destructive data operations, or unrelated cleanup."
---

# Ship

Take completed work to its actual delivered state through one user action. Infer the delivery path
from repository instructions, git and PR state, and the established deployment workflow. Do not ask
the user to invoke separate commit, merge, or deploy skills.

## Authorization And Stops

Explicit invocation authorizes in-scope fixes, commit, push, PR merge, and deployment when the
target and repository workflow are clear. Preserve unrelated user or agent work.

Stop only for genuine ambiguity or unsafe expansion: uncertain target or ownership, unrelated dirty
state that cannot be isolated, stacked or diverged branches that could overwrite work, secrets,
destructive migrations or production-data operations, unresolved product/architecture/security
decisions, material scope growth, missing deployment credentials, or an in-scope failed gate.
Never force-push or perform destructive cleanup as a shortcut.

## Resolve The Delivery Path

1. Read active repository instructions, validation commands, merge convention, and deployment path.
2. Inspect worktrees, branch/upstream state, staged and unstaged changes, untracked files, unpushed
   commits, and any current-branch PR.
3. Define the exact ship surface and the terminal delivered state:
   - direct branch: committed and pushed;
   - PR flow: pushed, checks clear, merged, and default branch reconciled;
   - deployable change: deployment complete and minimally verified.
4. Treat an automatic deployment triggered by push or merge as part of the same pipeline: monitor it
   instead of starting a duplicate deployment.

## Quality Gate

1. Review the ship surface for regressions, contracts and schemas, auth or tenancy, security and
   data integrity, repository rules, missing tests, CI risk, and residue.
2. Audit actionable PR feedback and required checks when a PR exists.
3. For meaningful code or architecture changes, apply `$simplify` to the same scope and make only
   behavior-preserving, bounded improvements. Skip it for mechanical changes.
4. Fix confirmed in-scope blockers and add focused tests when behavior changed.
5. Run the smallest relevant checks first, then the full relevant repository gate when feasible.
6. Re-read the final diff; every dirty file must be intended, ignored, or deliberately unshipped.

Use a lightweight gate for low-risk prose, config, or styling changes. Use a full review and test
gate for logic, dependencies, schemas, auth, deployment, or cross-layer changes. Decide from the
evidence; ask only when intent or ownership is genuinely ambiguous.

## Deliver

1. Stage only intended files, inspect the staged diff, and commit with the repository convention.
2. Synchronize without rewriting shared history and push the required branch.
3. When a PR exists, re-check unresolved threads and required remote checks, then merge using the
   repository convention. Review-only language without `$ship` or clear close/merge intent does not
   authorize merge.
4. Reconcile the local default branch after merge while preserving unrelated local work.
5. If deployment is required, use the repository's established automation or documented command.
   When no trustworthy deployment target or procedure can be inferred, stop and name the missing
   fact rather than inventing one.
6. Monitor the deployment to a terminal state and run the smallest available health or smoke check.

Do not delete branches or worktrees unless the user also requested cleanup or repository guidance
clearly makes that cleanup part of the established ship workflow.

## Completion

Report the delivered branch or PR, commit and merge SHA when applicable, deployment target/status,
checks and smoke tests run, skipped validation, intentionally unshipped files, and residual risk.
If stopped, report the exact phase, blocker, partial state, and single action needed to continue.
