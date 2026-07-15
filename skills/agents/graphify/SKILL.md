---
name: graphify
description: Use when the user explicitly asks to build, refresh, query, audit, visualize, or inspect a Graphify knowledge graph, or when an existing graphify-out is the relevant evidence source for architecture, coupling, cleanup, dead-code, duplication, impact, or repository relationship analysis. Prefer exact search for single-symbol lookup.
---

# Graphify

Use Graphify as a persistent relationship map, not as a replacement for source code. Keep the
workflow CLI-first and load only the reference needed for the current operation.

## Operating Principles

- Follow repository Graphify instructions before this personal default.
- Prefer the nearest active surface graph over a repository-root graph.
- Use graph-first analysis for relationships, architecture, coupling, cleanup, impact, dead code,
  duplicate detection, and cross-file reasoning.
- Use `rg`, IDE navigation, or source reads for exact symbol and string lookup.
- Treat `graphify --help` as the command source of truth. Do not copy or invoke Graphify's internal
  Python APIs when a public CLI command exists.
- Distinguish `EXTRACTED`, `INFERRED`, and `AMBIGUOUS` edges. Verify important conclusions against
  the cited source before recommending code changes.

## Route The Request

| Need | Default action |
| --- | --- |
| Orient in an existing graph | Read `GRAPH_REPORT.md`, then `wiki/index.md` when present |
| Ask a relationship question | `graphify query` |
| Trace two concepts | `graphify path` |
| Inspect one node | `graphify explain` |
| Find downstream impact | `graphify affected` |
| Audit architecture or cleanup | Read [references/audits.md](references/audits.md) |
| Refresh code-only changes | Use the repository wrapper, otherwise `graphify update` |
| Build or semantically refresh a corpus | `graphify extract` |
| Recompute communities | `graphify cluster-only` |
| Add, watch, export, merge, or diagnose | Read [references/commands.md](references/commands.md) |

Read [references/commands.md](references/commands.md) before running a Graphify command whose
arguments or write behavior are not already clear.

## Select Scope

1. Read active repository instructions and use their declared graph surfaces and wrappers.
2. If a relevant graph already exists, choose the nearest graph root to the files or question.
3. Prefer a coherent service or package surface over the whole repository.
4. Use the current directory only when it is the intended corpus.

Do not create a repository-root graph when repository instructions require surface graphs. If a
semantic extraction would cover a very large or mixed corpus, summarize the proposed scope and
cost boundary before running it.

## Existing Graph Workflow

1. Locate the nearest `graphify-out/GRAPH_REPORT.md`, `wiki/index.md`, and `graph.json`.
2. Check `graphify-out/needs_update` and repository freshness guidance.
3. Read `GRAPH_REPORT.md` first. Use the wiki for broader navigation; never load the full
   `graph.json` into model context.
4. Run the smallest query command that answers the question.
5. Open cited source files for any conclusion that could drive a code change.
6. Report the graph root, freshness, evidence type, and any source verification performed.

If no graph exists, do not silently start a potentially costly semantic extraction. Build only
when the user asked for it or repository instructions make the action an expected part of the
requested workflow.

## Build Or Refresh Workflow

1. Confirm the target surface and whether the change set is code-only or includes semantic inputs
   such as docs, papers, images, or audio.
2. Use the repository's wrapper when one exists.
3. Use `graphify update <path>` for code-only refreshes.
4. Use `graphify extract <path>` when semantic extraction is required. Let the CLI own chunking,
   caching, model calls, merging, clustering, and output generation.
5. Use `graphify cluster-only <path>` when extraction is current and only community structure or
   labels need regeneration.
6. Verify `GRAPH_REPORT.md` and `graph.json` exist and are non-empty. Check the report for raw
   `Community N` labels when human labels matter.
7. Report the command, output location, node/edge summary when available, and any skipped semantic
   work.

Use `--force` only after a refactor intentionally deleted nodes and a normal update refuses the
smaller graph. Never use it merely to suppress a warning.

## Safety And Independence

- Do not run `graphify install` or `graphify codex install` during ordinary work; they can rewrite
  skill or instruction surfaces.
- Do not install hooks, start watchers, configure MCP, or mutate `AGENTS.md` unless the user
  explicitly requests that persistent integration.
- Do not add Claude, Cursor, or other platform integration as part of Codex setup.
- Do not start semantic extraction without the required API credentials and an authorized scope.
- Generated graph artifacts follow repository policy; do not commit them unless the repository
  explicitly tracks them.

## Evidence Rules

- Never invent a node or edge.
- State when the graph is missing, stale, incomplete, or ambiguous.
- Cite `source_file` and `source_location` when the graph provides them.
- Treat low-confidence and semantic-similarity edges as leads, not proof.
- For cleanup findings, verify reachability and runtime or configuration references in source.
- Keep the final answer focused on findings; link the report instead of pasting it in full.
