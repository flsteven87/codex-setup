---
name: plan-symphony-ticket
description: Use when the user wants to discuss a topic, feature, bug, refactor, investigation, or product idea and turn it into a Linear ticket that Symphony can execute with Codex.
---

# Plan Symphony Ticket

## Overview

Use this skill to move from exploratory local discussion to a Symphony-ready Linear ticket. The local Codex session owns discovery and ticket quality; Symphony owns execution after the ticket is clear.

## Default Pipeline

1. Confirm target repo/project. Default to `ai-commerce-ready` and Linear project `ai-commerce-ready` unless the user says otherwise.
2. Update local context before analysis when a repo is involved: fetch/pull latest `main` safely, preserving unrelated local changes.
3. Use `superpowers:brainstorming` for fuzzy topics, product decisions, UX, architecture choices, or unclear requirements.
4. Use repo context only as needed. Read `AGENTS.md` first, then the nearest Graphify surface report/wiki for architecture or relationship questions. Do not refresh Graphify artifacts unless the user explicitly asks.
5. Use `superpowers:writing-plans` when implementation scope spans multiple steps, files, or validation gates.
6. Create the Linear issue directly when the ticket scope is clear enough for Symphony to execute. Do not stop for approval just because the ticket body could be improved.
7. Ask a concise clarification only when a missing decision would materially change the repo, project, implementation boundary, or validation gate.
8. Create the Linear issue in the intended project, with status `Todo`, so Symphony can pick it up.
9. Report the created issue identifier, URL, Symphony handoff state, and blockers. If the user writes Chinese, report in Traditional Chinese.

## Ticket Quality Bar

Do not hand Symphony a vague ticket. Include:

- **Background**: the observed problem, user need, or decision context.
- **Goal**: the outcome to deliver.
- **Non-goals**: boundaries that prevent scope creep.
- **Acceptance criteria**: concrete, testable bullets.
- **Implementation notes**: relevant files, services, constraints, or Graphify findings.
- **Validation**: exact commands or checks expected when feasible.
- **Risks/blockers**: credentials, external services, migrations, or human decisions.

Prefer one ticket per coherent implementation slice. Split tickets when acceptance criteria require unrelated code paths, separate review owners, or sequential decisions.

## Symphony Handoff Rules

- The ticket is the contract. Symphony's Codex session will not inherit this chat's hidden reasoning.
- Put all required context into the issue body or linked docs.
- Keep exploration, tradeoff debates, and large unknowns in the local session before ticket creation.
- For `ai-commerce-ready`, expect Symphony to branch from latest `origin/main`, use `symphony/<issue-id>`, push a PR, update the Linear workpad, and move the issue to `Human Review`.
- Before telling the user Symphony can run, verify the issue is in the correct Linear project and an active state (`Todo`, `In Progress`, `Rework`, or `Merging`).

## Linear Creation Checklist

When creating the issue:

- Project: `ai-commerce-ready` unless overridden.
- Team/workspace: Aithentic / `AIT` for `ai-commerce-ready`.
- Status: `Todo`.
- Title: imperative or outcome-oriented, specific enough to scan.
- Body: use the ticket quality sections above.
- Labels/priority/assignee/cycle: set only when known or requested.

After creation, report the issue identifier and URL, plus whether Symphony should pick it up automatically. Do not paste a full draft first unless the user explicitly asks for a draft or clarification is required.

## Clarification Threshold

Default to creating the ticket after reasonable discovery. Ask first only when one of these is unknown and cannot be inferred safely:

- Target repository, Linear project, or team is ambiguous.
- The requested outcome could map to multiple unrelated implementation slices.
- Acceptance criteria depend on a product decision the user has not made.
- Validation requires credentials, migrations, destructive operations, or paid external services.
- The user explicitly asks to review the ticket before creation.
