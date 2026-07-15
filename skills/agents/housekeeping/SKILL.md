---
name: housekeeping
description: Audit and safely tidy Codex agent artifacts, including AGENTS.md guidance, .agents skills, .codex config and handoffs, completed plans, stale notes, and context hygiene issues. Use when the user says housekeeping, clean up, tidy, context hygiene, reset accumulated cruft, 整理, 清理, or before/after a major project phase.
---

# Housekeeping

Keep agent-facing context lean, current, and discoverable without touching product source code.

## Operating Model

- Report first, modify only after explicit user approval.
- Prefer durable rules in `AGENTS.md`, repeatable workflows in `.agents/skills`, external integrations in MCP/config, and recurring schedules in automations.
- Keep housekeeping Codex-native. Do not read or write legacy agent surfaces unless the user explicitly asks for a migration audit.
- Do not create documentation files unless the user explicitly approves a target and purpose.
- Never delete, rewrite, or consolidate source code as part of housekeeping.
- Match the user's language for reports. When the user writes Chinese, report in Traditional Chinese.

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

- Safe to delete: completed plan files or completed scratch notes with no pending markers.
- Consolidate: overlapping memory or handoff notes, oversized `AGENTS.md` sections that should become a skill or referenced guide, duplicate or conflicting Codex workflow instructions.
- Needs user review: empty files, generated temp notes, stale but possibly meaningful project memory, old handoff state, disabled skill configs, abandoned branch/worktree notes, conflicting instructions.
- Do not touch: source code, tests, migrations, lockfiles, active specs, secrets, local env files, or repo docs unrelated to agent workflow.

For Codex-specific alignment, prefer these destinations:

- Personal reusable skill: `~/.agents/skills/<skill-name>/`.
- Repo shared skill: `<repo>/.agents/skills/<skill-name>/`.
- Personal defaults: `~/.codex/AGENTS.md`.
- Repo rules: `<repo>/AGENTS.md` or nearer `AGENTS.override.md`.
- Session continuity: the repo's existing handoff surface, or chat output if none exists.

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

End in the user's language. When reporting in Chinese, use Traditional Chinese and translate the fixed labels instead of leaving the final block in English.

English template:

```text
Housekeeping Complete
Deleted:      <count> files (<size> freed)
Consolidated: <before> files -> <after> files
Trimmed:      <count> files (<lines> lines removed)
Updated:      <files>
Skipped:      <items declined or deferred>
Validation:   <commands run or not run>
```

Traditional Chinese template:

```text
Housekeeping 完成
已刪除:      <count> 個檔案（釋放 <size>）
已整併:      <before> 個檔案 -> <after> 個檔案
已精簡:      <count> 個檔案（移除 <lines> 行）
已更新:      <files>
已略過:      <items declined or deferred>
驗證:        <commands run or not run>
```

If no changes were made, report the scan, recommendations, and that no files were modified.

## Safety Stops

Stop and ask before proceeding if:

- A cleanup item touches product source code or test files.
- A memory item may encode a business decision not present elsewhere.
- A file contains secret-like values.
- A `git status` shows unrelated user changes in files you would modify.
- The requested cleanup overlaps with branch, stash, or worktree deletion. Use `$git-state-audit` first.
