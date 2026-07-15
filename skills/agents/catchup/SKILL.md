---
name: catchup
description: Use when the user says /catchup, $catchup, asks to catch up, resume from prior work, rebuild context after a reset, inspect current work state, or update from git before summarizing what to do next.
---

# Catchup

Rebuild working context quickly from repository evidence, then tell the user the safest next action.

## Operating Model

- Read before inferring. Prefer git evidence, `AGENTS.md`, and existing handoff/memory files over guesswork.
- Default to read-only. Do not edit files, stage changes, commit, push, or start dev servers unless the user explicitly asks.
- Reply in Traditional Chinese by default. If the user writes in Chinese or does
  not specify a language, use Traditional Chinese for section headings and body
  text. Use another language only when the user clearly requests or uses it.
- Keep the answer short enough that the user can resume immediately.

## Optional Git Update

Only update from git when the user explicitly asks to pull, update, refresh from remote, or "git pull 更新一下".

When asked to update:

1. Run `git status --short --branch`.
2. If the worktree has modified, staged, deleted, or untracked files, do not pull by default. Explain that pulling could mix remote changes with local work, show the dirty summary, and ask for explicit permission if a pull is still desired.
3. If the worktree is clean and the branch has an upstream, run `git pull --ff-only`.
4. If `git pull --ff-only` fails because fast-forward is impossible, do not merge or rebase automatically. Report the failure and recommend the next safe choice.
5. If there is no upstream or the remote is unavailable, report that clearly and continue local catch-up.

Never use plain `git pull` for catch-up. Avoid merge commits and avoid `--autostash` unless the user explicitly asks for that behavior after seeing the dirty state.

## Evidence To Gather

Run the smallest useful checks:

1. `git status --short --branch`
2. `git log --oneline -5`
3. `git diff --stat`
4. Read relevant instruction and continuity files in this order when present:
   - `AGENTS.md`
   - `MEMORY.md`
   - `.agents/handoffs/*`
   - `.codex/handoffs/*`
   - nearby `docs/**/plans/*.md` or active plan files
5. Inspect only the highest-signal changed files needed to understand the current workstream.

## Reasoning Rules

- Separate evidence from inference.
- State uncertainty when evidence is stale, conflicting, or thin.
- If multiple workstreams are active, name the likely primary one and why.
- Do not treat Codex Memories as authoritative project state. They can support recall, but repository files and git state win.
- If the repository has Graphify guidance and the question is architectural or relationship-oriented, follow the nearest graph workflow from `AGENTS.md`.

## Output Shape

Use this compact structure:

- 目前工作主線
- Git 狀態與遠端狀態
- 看起來已完成
- 仍在進行或有風險
- 建議優先閱讀的檔案
- 建議下一步

If a requested git update was run, include the exact pull result or the reason it was skipped.
