# Graphify CLI Commands

Use this reference for command selection and flags. Confirm fast-moving details with
`graphify --help` before execution.

## Contents

- [Preflight](#preflight)
- [Locate Existing Graphs](#locate-existing-graphs)
- [Build And Refresh](#build-and-refresh)
- [Query And Impact](#query-and-impact)
- [Diagnostics And Outputs](#diagnostics-and-outputs)
- [Advanced Operations](#advanced-operations)
- [Validation](#validation)

## Preflight

```bash
command -v graphify
graphify --version
graphify --help
```

If Graphify is missing, prefer `uv tool install graphifyy`. Do not install with `pip` into the
project environment. Follow repository bootstrap instructions when they specify another method.

Use a repository wrapper when present, for example `scripts/graphify.sh`. A wrapper may encode
surface boundaries, output locations, label preservation, or environment selection that the raw
CLI does not know.

## Locate Existing Graphs

Because generated graphs are often ignored, include ignored files when searching:

```bash
rg --files -uu \
  -g '**/graphify-out/GRAPH_REPORT.md' \
  -g '**/graphify-out/wiki/index.md' \
  -g '**/graphify-out/graph.json' \
  -g '**/graphify-out/needs_update'
```

Read the nearest `GRAPH_REPORT.md` first. Read `wiki/index.md` when it exists. Do not paste or load
the complete `graph.json` into context.

## Build And Refresh

Full extraction, including semantic inputs:

```bash
graphify extract <path>
```

Useful optional flags include `--backend`, `--model`, `--max-concurrency`, `--token-budget`,
`--no-cluster`, and `--out`. Select them only when the environment or user request requires them.

Code-only incremental refresh:

```bash
graphify update <path>
```

Use `--force` only after intentional deletion or a refactor makes a smaller replacement graph
correct. Use `--no-cluster` only when another step will cluster the result.

Recompute communities and report without re-extracting:

```bash
graphify cluster-only <path>
```

Use `--no-viz` for large graphs or when HTML is unnecessary. If docs, papers, images, or audio
changed, `update` is insufficient; use semantic extraction or the repository's full extraction
flow.

## Query And Impact

```bash
graphify query "<question>" --graph <path/to/graph.json>
graphify query "<question>" --dfs --budget 1500 --graph <path/to/graph.json>
graphify path "<source>" "<target>" --graph <path/to/graph.json>
graphify explain "<node>" --graph <path/to/graph.json>
graphify affected "<node>" --depth 2 --graph <path/to/graph.json>
```

Use default BFS queries for nearby context and `--dfs` for a dependency chain. Use repeated
`--context` or `--relation` filters only when the graph contains those edge contexts or relations.

Answer from the returned subgraph, then verify consequential findings in source. Save a useful
answer back only when the repository expects Graphify memory:

```bash
graphify save-result --question "<question>" --answer "<answer>" --type query --nodes <labels>
```

## Diagnostics And Outputs

Check multigraph edge-collapse risk:

```bash
graphify diagnose multigraph --graph <path/to/graph.json>
```

Measure graph token reduction for a large corpus:

```bash
graphify benchmark <path/to/graph.json>
```

Generate optional views:

```bash
graphify tree --graph <path/to/graph.json> --output <path/to/GRAPH_TREE.html>
graphify export callflow-html
```

Normal output is under `<surface>/graphify-out/` and should include `GRAPH_REPORT.md` and
`graph.json`; `graph.html` and wiki output depend on the extraction and repository workflow.

## Advanced Operations

Only run these when explicitly requested or required by repository policy:

```bash
graphify add <url> --dir <path>
graphify watch <path>
graphify hook status
graphify merge-graphs <graph-a> <graph-b> --out <path>
graphify global list
graphify global add <graph.json> --as <tag>
```

Do not install hooks, watchers, global graph registration, MCP servers, or instruction-surface
integrations as a side effect of ordinary analysis.

## Validation

After a write operation:

```bash
test -s <surface>/graphify-out/GRAPH_REPORT.md
test -s <surface>/graphify-out/graph.json
```

Then inspect:

- whether `needs_update` remains;
- node and edge counts reported by the CLI;
- raw `Community 0/1/...` labels when human labels are expected;
- warnings about a smaller replacement graph, missing semantic credentials, or skipped files;
- repository `git status` to confirm generated artifacts follow local tracking policy.
