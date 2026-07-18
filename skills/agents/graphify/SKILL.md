---
name: graphify
description: Use Graphify proactively for broad codebase architecture, cross-file control or data flow, dependencies, ownership, impact analysis, and unfamiliar-subsystem questions when an existing graph can narrow source inspection; also use when explicitly asked to query, build, or update Graphify. Do not invoke for known-file or known-symbol lookups, focused edits, or small local bugs where direct source inspection is cheaper.
---

# Graphify

Use Graphify as a lossy retrieval index, never as source-of-truth. Optimize for fewer files read and fewer tool loops.

## Retrieve from an existing graph

1. Run `scripts/discover_graphs.py --root <task-scope>` from this skill directory. Add `--include-tests` only when the task is specifically about tests.
2. Select the narrowest graph whose surface covers the question. Prefer a component graph over a repository-wide graph when both contain the target subsystem.
3. Prefer the narrowest command that can answer the question, and make one direct Graphify call with an absolute `--graph` path:

   - Two named concepts: `graphify path "<A>" "<B>" --graph <graph.json>`
   - One node and its neighbors: `graphify explain "<node>" --graph <graph.json>`
   - Reverse blast radius: `graphify affected "<node>" --depth 2 --graph <graph.json>`
   - Broad relationship or flow: `graphify query "<code-oriented question>" --budget 1200 --graph <graph.json>`
   - A specific chain without two reliable endpoints: add `--dfs` to `query`.

4. Treat the result as a shortlist. Open the highest-signal source locations and verify every material claim against current code.

## Keep retrieval bounded

- Use code vocabulary, identifiers, and likely English symbol names in queries even when the user writes in another language.
- Add an explicit edge filter when the intent is clear: `--context call`, `import`, `field`, `parameter_type`, or `return_type`. Repeat `--context` only when more than one edge type is material.
- If the first result is sparse or off-target, make at most one narrower retry with better code vocabulary. Then fall back to normal source search.
- If output truncates, narrow by node, path, or context before increasing the budget; raise the single retry to at most `--budget 2000` only when necessary.
- Stop querying once the result identifies enough source locations to answer or edit safely.
- Do not read `graph.json` directly. Do not load `GRAPH_REPORT.md` or a generated wiki unless the request is genuinely repository-wide and targeted queries are insufficient.
- If the graph appears stale, verify more aggressively in source. Do not mutate a graph during an answer-only, review, or diagnosis task.
- If no relevant graph exists or the CLI is unavailable, inspect source normally. Install or build only when setup work is explicitly in scope.

## Build or update deliberately

- For an explicit build, choose the smallest stable production-code surface and run `graphify extract <surface> --code-only`. Keep generated `graphify-out/` local and ignored.
- Include tests only when test architecture is itself the retrieval target.
- Ask before API-backed semantic extraction because it may send content externally and incur cost. Check current options with `graphify --help` instead of relying on copied command documentation.
- After modifying code, run one `graphify update <surface>` only when an existing graph covers that surface and the change materially alters symbols or relationships. Run it after validation, not after each edit.
- Never use `--force` unless the user explicitly authorizes overwriting a graph after a deletion-heavy refactor.

## Avoid setup churn

- Do not install hooks, file watchers, MCP servers, CI jobs, or commit-time refreshes for Graphify.
- Do not call `save-result` or `reflect` by default; enable feedback memory only for a measured evaluation.
- Do not add multi-agent extraction machinery. Use the local CLI directly and keep Codex responsible for source verification and the final answer.
- Upgrade the runtime with `uv tool upgrade graphifyy` during explicit setup work. Do not run `graphify install`, which would replace this intentionally lean local router with the bundled monolithic skill.
