---
name: axi-routing
description: Route tool-heavy work to one primary surface across connectors, Codex apps or MCP, AXI CLIs, official CLIs, and UI automation. Use for overlapping GitHub, browser/DevTools, task-state, quota, or structured-review tools, or when the user requests AXI.
---

# AXI Routing

Choose one primary tool surface for each operation. Optimize for complete evidence per call, compact structured output, deterministic state, least privilege, and the fewest state transitions—not for using AXI everywhere.

## Routing Procedure

1. Honor the user's explicit tool choice and any more specific skill instructions.
2. Define the operation, required evidence, authentication context, side effects, and source of truth.
3. Consider only surfaces that can complete the operation:
   - Prefer a purpose-built native connector or Codex app when it already has the required authenticated context and complete structured coverage.
   - Prefer an AXI CLI when the work is terminal-first, local-repository-aware, cross-harness, more compact or deterministic through AXI, or must share durable agent state.
   - Prefer the vendor's official raw CLI for capability gaps, low-level diagnostics, logs, or APIs that the higher-level surface does not expose.
   - Use browser or computer UI automation only when the operation depends on visible UI state or no semantic interface can complete it.
4. Select one primary surface per step.
5. Before the first use of an AXI command in a task, run its current `--help` and the relevant subcommand help. Do not rely on remembered flags.
6. Use a second surface only to verify a material external mutation, resolve inconsistent evidence, or bridge a documented capability gap.
7. Report the routing choice only when it materially affects behavior, permissions, or the source of truth.

Routing is complete when every operation has one primary surface and every secondary surface is justified by verification, inconsistent evidence, or a documented capability gap.

## Domain Routes

### GitHub

- Use the connected GitHub app for structured pull request, issue, review, comment, label, and repository operations it fully supports, especially when its authenticated context is already available.
- Use `gh-axi` for compact agent-facing GitHub workflows, local repository context, dashboards, and supported operations where it reduces calls or output.
- Use raw `gh` for Actions logs, GraphQL, unsupported API fields, or documented gaps.
- Never perform the same mutation through both the app and a CLI. Read back through a second surface only when verification is warranted.

### Browser and DevTools

- Use a purpose-built connector for semantic access to its own service.
- Use the Chrome integration when an existing signed-in Chrome session is required.
- Use the in-app Browser for general interactive browsing and visible page state.
- Use Playwright for repeatable repository-owned browser tests and scripted UI flows.
- Use `chrome-devtools-axi` for terminal-first DevTools work, compact DOM interaction, console or network evidence, performance analysis, and cross-harness browser control.
- Keep authenticated, isolated, and test browser sessions distinct unless the user explicitly asks to reuse one.

### Agent Task State

- Use Codex's built-in plan for progress within the current Codex task.
- Use `tasks-axi` only when the repository, Firstmate workflow, or user declares it the durable shared agent task state. Do not mirror every Codex plan step into it.
- Keep Linear or another team tracker as the product or team source of truth when configured; use `tasks-axi` only for agent execution state unless told otherwise.

### Model Quota

- Use `quota-axi` when the user asks about quota or when quota should materially influence provider, model, or harness routing.
- Do not check quota routinely when it cannot change the decision.
- Run authentication or keychain flows only when the selected operation requires and authorizes them.

### Rich Human Review

- Use `lavish-axi` when a complex plan, comparison, diagram, code review surface, or structured decision materially benefits from interactive visual feedback.
- Use ordinary chat Markdown for simple explanations and decisions.
- Keep local review local. Treat `lavish-axi share` as an external publication and require explicit authorization before publishing.

## Safety and Fallbacks

- Preserve the task's authorization boundaries regardless of tool convenience.
- If the preferred tool is missing or insufficient, use the next qualified installed surface and state the limitation when material.
- Treat installation, updates, authentication, publication, and broader external access as separate scoped actions.
- Stop and request direction when the remaining choices differ materially in side effects, authority, or source of truth.
