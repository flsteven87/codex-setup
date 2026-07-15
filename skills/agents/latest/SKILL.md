---
name: latest
description: Use when project memory or handoff state may be stale, bloated, or out of sync with git, PRs, tickets, changelog, or sibling repos, and when the current main checkout should be refreshed by safe fast-forward pull; triggers include /latest, latest, 進入最新狀況, 同步最新, 拉到最新, consolidate memory, 清理 memory, memory 太長, or session-start state refresh.
---

# Latest

Bring the working context and the current main checkout up to reality before planning or coding. This is heavier than `catchup`: it can fast-forward pull the active main checkout and rewrite an established memory or handoff surface so future sessions start from current truth, not stale notes.

## Use Versus Catchup

- Use `catchup` for a fast, read-only status rebuild.
- Use `latest` when memory/handoff files have drifted, accumulated old session history, or will guide the next decision.
- Do not use on brand-new projects with no durable memory surface.

## Principles

- Evidence first: git, PRs, tickets, changelog, repo files, then memory.
- Focus over completeness: session-start memory should answer "what should I do next?" not serve as a project journal.
- Autonomy for value-neutral cleanup: trim stale or off-topic memory without asking when evidence is clear.
- Do not rewrite user-owned decisions silently. If a locked rule or personal preference conflicts with evidence, leave it and report the tension.

## Workflow

1. Detect scope:
   - repo root and branch
   - established memory or handoff target, if any
   - sibling repos named by memory or located beside the current repo
   - ticket prefixes and available ticket/PR tools
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
   - avoid creating new documentation files unless the user asked or the memory system already uses topic files
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
6. If not safe, do not pull; report the exact blocker and leave the checkout untouched.

Do not merge, rebase, stash, delete, or overwrite local work as part of `latest`. Do not pull feature branches or sibling repos unless the user explicitly asks; fetch them and report their divergence instead.

## Safety

- Never print secrets.
- Do not pull or mutate sibling repos beyond fetch unless explicitly asked.
- Do not modify team-visible ticket state from this skill; propose changes instead.
- Do not turn `latest` into implementation or cleanup of unrelated code.

## Output Shape

Use the user's language. For zh-tw, use:

- 已同步
- Memory 編輯
- 需要你確認的張力
- 起手就緒

Keep the final "起手就緒" paragraph to 2-3 sentences.
Always include whether the active checkout was pulled, already current, or skipped with a concrete reason.
