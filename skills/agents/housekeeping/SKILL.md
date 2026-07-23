---
name: housekeeping
description: Audit and tidy Codex agent artifacts, including AGENTS.md, skills, .codex config, handoffs, completed plans, stale notes, and context hygiene. Use for explicit housekeeping or accumulated agent-artifact cleanup.
---

# Housekeeping

Keep agent-facing context lean, current, and discoverable without touching product source code.

## Operating Model

- Report first, modify only after explicit user approval.
- Prefer durable rules in `AGENTS.md`, repeatable workflows in `.agents/skills`, external integrations in MCP/config, and recurring schedules in automations.
- Keep housekeeping Codex-native. Do not read or write legacy agent surfaces unless the user explicitly asks for a migration audit.
- Never delete, rewrite, or consolidate source code as part of housekeeping.

## Phase 1: Scan

Run the bundled read-only scan from the relevant repository root:

```bash
bash ~/.agents/skills/housekeeping/scripts/scan.sh
```

For a specific project:

```bash
bash ~/.agents/skills/housekeeping/scripts/scan.sh --project /path/to/project
```

Present the scan results before proposing changes. If the script is unavailable, manually inspect the same surfaces: global and repo `AGENTS.md`, `.agents/skills`, `.codex`, existing handoff or memory files, plans, and stale docs.

## Phase 2: Triage

Group findings by risk:

- Deletion candidates: completed plan files or scratch notes with no pending markers. This label is evidence for review, not authorization to delete.
- Consolidate: overlapping memory or handoff notes, oversized `AGENTS.md` sections that should become a skill or referenced guide, duplicate or conflicting Codex workflow instructions.
- Needs user review: empty files, generated temp notes, stale but possibly meaningful project memory, old handoff state, disabled skill configs, abandoned branch/worktree notes, conflicting instructions.
- Out of scope: source code, tests, migrations, lockfiles, active specs, secrets, local env files, and repo docs unrelated to agent workflow.

For Codex-specific alignment, prefer these destinations:

- Personal reusable skill: `~/.agents/skills/<skill-name>/`.
- Repo shared skill: `<repo>/.agents/skills/<skill-name>/`.
- Personal defaults: `~/.codex/AGENTS.md`.
- Repo rules: `<repo>/AGENTS.md` or nearer `AGENTS.override.md`.
- Session continuity: the repo's existing handoff surface, or chat output if none exists.

### Git handoff

Keep Git state outside housekeeping's implementation:

If cleanup reaches a branch, stash, worktree, remote PR/ref, reflog recovery, or repository
maintenance item, stop at the exact overlap and recommend explicit `$git-converge-main` invocation.
That skill owns classification, proof, authorization, and mutation.

## Phase 3: Execute After Approval

Before any destructive edit:

1. State the exact files and intended action.
2. Confirm the item is completed or otherwise explicitly approved for removal.
3. Preserve unrelated content.
4. Show before/after summaries for consolidations and trims.

Do not create backup files as part of housekeeping. If an item is not clearly
completed, leave it in place and report why it was skipped.

Cleanup rules:

- Completed plans: only remove plans that are fully completed. Verify no `[ ]`, `TODO`, `PENDING`, `IN PROGRESS`, or equivalent unfinished markers before deletion. Do not archive incomplete plans.
- Memory and handoffs: keep only decisions, constraints, gotchas, validation state, and next actions that help a future agent. Remove transcript-like history and facts derivable from code or git.
- `AGENTS.md`: keep concise, practical, and scoped. Move repeatable procedures into skills; move volatile external facts into MCP-backed lookups or task prompts.
- Skills: keep one job per skill, concise trigger descriptions, and scripts only when they improve deterministic reliability.
- Automations: recommend only after the manual workflow is stable; skills define method, automations define schedule.

## Phase 4: Report

Report counts for deleted files and freed size, consolidations, trims and removed lines, updated
files, skipped items, and validation. For an audit-only run, report the scan and recommendations
and state that no files changed.

## Completion

| Branch | Complete when |
|---|---|
| Audit only | The scan scope, evidence-backed candidates, review-required items, and untouched surfaces are reported; no files changed. |
| Approved cleanup | Every touched file was named in the approval, unrelated content was preserved, and the final counts plus validation are reported. |
| Consolidation | The destination owns the surviving rule, the removed copies add no unique constraint, and the before/after summary is reported. |
| Git overlap | Housekeeping stops with the exact overlap and recommends explicit `$git-converge-main` invocation; it does not classify the Git item itself. |

## Safety Stops

Stop and ask before proceeding if:

- A memory item may encode a business decision not present elsewhere.
- A file contains secret-like values.
- A `git status` shows unrelated user changes in files you would modify.
