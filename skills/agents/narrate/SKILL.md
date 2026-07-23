---
name: narrate
description: Turn one technical or product topic into a concise plain-language visual brief.
---

# Narrate

Turn one topic into a fixed-shape brief the user can understand quickly. This is read-only legibility, not strategy, ticket restructuring, implementation, or dispatch planning.

## Output Contract

Always produce these blocks in this order:

1. **BLUF**: one sentence, business-altitude, with a status word.
2. **One Diagram**: Mermaid by default; ASCII only if Mermaid would be noisy. Use no more than 9 boxes. Put plain-language labels on the diagram, not code identifiers.
3. **Key Nodes**: a markdown table with `節點 | 白話職責 | 位置`. This table is the only place for paths, APIs, flags, ticket IDs, or function names. Verify every path before listing it.
4. **Gaps**: up to 3 honest blockers, ambiguities, or follow-ups. If none, write one line: `無缺口`.

End after these blocks. Add one recommendation line only when the evidence supports an obvious next action.

## Diagram Grammar

- UI / product surface: sitemap. Containers are apps/surfaces; boxes are pages or entry points.
- Pipeline / system flow: swimlane. Top lane is user-visible output; bottom lane is system stages.
- Architecture / design decision: role diagram. Show SSOT, live consumers, transitional paths, and the invariant.
- Bug / incident: before-after.
- Binary decision: chosen vs rejected.

Use status or role color labels in Mermaid node text when useful, for example `已上線`, `收尾中`, `未開始`, `SSOT`, `退役中`. Keep labels short.

## Grounding

Default to a light pass:

- If the topic names a ticket or PR, verify current state with available tools before asserting status.
- If a path enters the Key Nodes table, confirm it exists with `rg --files` or a direct file read.
- If evidence conflicts, put the conflict in Gaps without dramatizing it.

Escalate to a deeper walkthrough only when the user explicitly asks for full coverage, onboarding, or a complete architecture explanation. Even then, start with the four-block brief.
