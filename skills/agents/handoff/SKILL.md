---
name: handoff
description: Use when the user says /handoff, $handoff, asks to save session state, pause work, create continuity notes, preserve context before compaction, or prepare the cleanest next-session starting point.
---

# Handoff

Create the minimum durable context needed for a future Codex or other coding-agent session to continue safely.

## Operating Model

- Prefer repository evidence over narrative memory.
- Keep durable team rules in `AGENTS.md`; keep session state in the repository's existing handoff or memory surface.
- Update an existing durable handoff target when one is clearly present. If no convention exists, create repository-root `MEMORY.md` and use it as the durable handoff target.
- Do not use Codex Memories as the only handoff target. They are a local recall layer, not a shared source of truth.
- Keep the handoff actionable and concise. Avoid full transcripts.

## Evidence To Gather

Run the smallest useful read-only checks:

1. `git status --short --branch`
2. `git log --oneline -5`
3. `git diff --stat`
4. Inspect changed file paths and any nearby plan or handoff files.
5. If available, read existing `AGENTS.md`, `MEMORY.md`, `.agents/handoffs/*`, or `.codex/handoffs/*` only as needed.

## Target Selection

Use the first clearly established target:

1. Repository-root `MEMORY.md`
2. Existing `.agents/handoffs/` or `.codex/handoffs/`
3. Existing project-specific handoff convention documented in `AGENTS.md`

If more than one exists, prefer the target that the repository already says `/handoff` or catch-up flows use. Do not scatter duplicate handoffs across multiple files.

If none exists, create repository-root `MEMORY.md`. Do not ask for confirmation; invoking `/handoff` explicitly authorizes this single handoff file.

## Write Rules

- Preserve unrelated existing content.
- Creating repository-root `MEMORY.md` is authorized only when no durable handoff target exists; this does not authorize other new documentation files.
- Replace or update the active/current-state section instead of appending unbounded history.
- Keep historical notes only when they are still relevant to the next session.
- Redact secrets and token-like values.
- Never stage, commit, push, or start dev servers as part of handoff unless the user explicitly asks.

## Handoff Content

Include these sections, scaled to the situation:

- Current state: branch, cleanliness, active workstream, and remote/upstream caveats.
- Completed work: what changed and why it matters.
- Pending work: concrete next tasks, ordered by dependency.
- Key files: only files the next agent should read first.
- Validation: commands run, results, and commands not run.
- Decisions and constraints: choices that should not be re-litigated next session.
- Risks or blockers: unresolved failures, dirty generated artifacts, broken remotes, missing data, or required user approval.
- Exact next action: one recommended starting move.

## Final Response

Reply in the user's language. Include:

- The file updated, if any.
- A short summary of the saved state.
- Validation performed for the handoff itself, if any.
- If filesystem access is blocked or the repository root cannot be determined, provide the handoff in chat and state the blocker. Otherwise, a durable target must be written.
