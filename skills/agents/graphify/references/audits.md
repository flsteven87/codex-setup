# Graph-Based Audits

Use this reference for architecture, cleanup, coupling, dead-code, duplication, and impact work.
The graph identifies candidates; source and runtime evidence confirm findings.

## Contents

- [Audit Entry Points](#audit-entry-points)
- [Workflow](#workflow)
- [Confidence And Verification](#confidence-and-verification)
- [Reporting](#reporting)

## Audit Entry Points

| Question | Start with | Follow with |
| --- | --- | --- |
| Architectural centers or god components | `God Nodes`, community fan-in | `graphify explain` and source reads |
| Hidden coupling or cross-boundary dependencies | `Surprising Connections`, cross-community edges | `graphify path` |
| Shared flows involving 3+ components | Hyperedges and community summaries | Source call/data-flow verification |
| Change impact | `graphify affected` | Tests, config, entrypoints, and callers |
| Duplicate behavior | `semantically_similar_to` edges | Exact source comparison and usage search |
| Dead or orphaned code | Low-connectivity/orphan candidates | `rg`, entrypoints, reflection/config checks |
| Cleanup sequencing | Community boundaries and fan-in | Delete/modify lowest-impact leaves first |
| Missing documentation links | Code-to-doc and rationale relationships | Read canonical docs and source comments |

For a repository with a generated wiki, use its index to navigate communities before opening raw
files. Use the report's God Nodes, Surprising Connections, Hyperedges, and community summaries as
the primary audit surfaces.

## Workflow

1. Select the nearest fresh surface graph.
2. Read `GRAPH_REPORT.md`; note node/edge counts, warnings, communities, and freshness markers.
3. Form one bounded audit question rather than scanning the entire graph indiscriminately.
4. Run `query`, `path`, `explain`, or `affected` to obtain a small evidence subgraph.
5. Open the cited source locations.
6. Search for dynamic references that static graphs can miss: configuration strings, dependency
   injection, route registration, reflection, templates, migrations, tests, and runtime plugins.
7. Classify the result as confirmed, likely, or unproven.
8. Recommend the smallest safe change and the validation needed to prove it.

## Confidence And Verification

- `EXTRACTED` is structural evidence, but can still be incomplete.
- `INFERRED` is a hypothesis that requires source verification.
- `AMBIGUOUS` is a review lead, never a finding by itself.
- Semantic similarity indicates comparable intent, not interchangeable behavior.
- Missing edges do not prove dead code. Check entrypoints, runtime registration, configuration, and
  external consumers.
- High degree does not automatically mean poor design. Confirm whether the node is an intentional
  stable interface or an accidental dependency hub.
- A stale graph may support orientation but not deletion decisions.

Do not recommend deleting code solely because Graphify cannot reach it. Require at least one
independent source-level or runtime signal.

## Reporting

For each actionable finding, report:

```text
[severity] component or file
Graph evidence: nodes, edge relation, confidence, community/path
Source verification: files and exact mechanism
Risk: user-visible or maintenance consequence
Action: smallest safe change
Validation: focused checks needed
```

Separate graph-derived inference from verified facts. Link `GRAPH_REPORT.md` and relevant source
files instead of pasting large graph payloads.
