---
name: latest
description: Refresh an established project memory or handoff and the active default checkout against current Git, PR, ticket, changelog, and explicitly relevant repository evidence. Use when durable session-start memory has drifted; unlike catchup, this may fast-forward main and rewrite that surface.
---

# Latest

Bring the current default checkout and its established session-start memory up to verified reality.

## Principles

- Evidence first: git, PRs, tickets, changelog, repo files, then memory.
- Focus over completeness: session-start memory should answer "what should I do next?" not serve as a project journal.
- Autonomy for value-neutral cleanup: trim stale or off-topic memory without asking when evidence is clear.
- Preserve user-owned decisions; report conflicts with locked rules or personal preferences as tensions.

## Workflow

1. Detect scope:
   - repo root and branch
   - established memory or handoff target, if any
   - sibling repos explicitly named by the user or by a direct pointer in the selected memory whose
     state affects the current objective
   - ticket prefixes and available ticket/PR tools
   - scope derives from those explicit names and pointers, not filesystem adjacency
2. Sync truth:
   - fetch remote refs when safe
   - if the active checkout is `main`, `master`, or `trunk`, safely fast-forward it to its upstream before classifying memory
   - read status, recent commits, tags, open/merged PRs when tooling exists
   - read the top of `CHANGELOG.md` when present
   - verify named tickets when tools are available
3. Classify memory claims:
   - confirmed and still useful
   - stale but mechanically correctable
   - accurate but too detailed for session-start memory
   - user-owned tension that should be reported, not edited
   - unverified
4. Edit the established memory/handoff surface only when one clearly exists:
   - keep current WIP, immediate next step, recent ships, locked constraints, and routing pointers
   - remove or compress old ship narratives, transient PR lists, closed tickets, dead plans, and stale operational todos
   - move durable but non-immediate detail into an existing topic file when the project already has that convention
   - inspect the final diff and verify every edited claim against the evidence used to classify it
5. Report:
   - what sources were synced
   - what memory changed
   - what was left untouched due to tension
   - the cleanest next action

## Size Rule

If the memory surface is loaded into every session, keep it short. Prefer one-line pointers over paragraphs. If a section is true but only useful when working on a specific subsystem, it belongs behind a pointer or should be looked up on demand.

## Pull Policy

When the active repo checkout is on `main`, `master`, or `trunk`, run a safe refresh after fetch:

1. Confirm the branch has an upstream and is behind or diverged.
2. Confirm the branch can fast-forward (`git merge-base --is-ancestor HEAD @{u}`).
3. Confirm there are no tracked local changes.
4. Check untracked files for path collisions with incoming upstream files.
5. If safe, run `git pull --ff-only`.
6. Otherwise leave the checkout untouched and report the exact blocker.

Do not merge, rebase, stash, delete, or overwrite local work as part of `latest`. Do not pull feature branches or sibling repos unless the user explicitly asks; fetch them and report their divergence instead.

## Completion

| Branch | Complete when |
|---|---|
| Active default branch | It was fast-forwarded, was already current, or was skipped with the exact safety blocker. |
| Feature branch | Remote refs and divergence were inspected without pulling or rewriting the branch. |
| Memory reconciliation | Every changed claim has evidence, the final diff was inspected, and user-owned tensions remain visible. |
| Named sibling evidence | Only the named repository was inspected; any fetch or skipped access is reported. |
| No established memory | No file is created; the missing target and the read-only status result are reported. |

## Boundaries

- Keep sibling repositories read-only beyond fetch unless explicitly requested.
- Propose team-visible ticket changes rather than applying them.
- Keep implementation and unrelated code cleanup outside this workflow.

## Output Shape

Report synced sources, memory edits, user-owned tensions, and a two-to-three-sentence ready-next
action. State whether the active checkout was pulled, already current, or skipped and why.
