# Skills, Context, And Tools

Use this reference when designing prompts, skills, tool contracts, MCP/tool-search surfaces, or context retrieval.

## Contents

- Prompt Altitude
- Skill Design
- Context Engineering
- Context And State Inventory
- Tool Contracts
- Tool Loading
- Structured Outputs

## Prompt Altitude

Write prompts at the altitude between vague principles and brittle case logic:

- Give outcome, role, constraints, tradeoffs, and stopping rules.
- Explain why a heuristic matters when contextual judgment is expected.
- Include a few canonical examples that cover different behavior modes.
- Avoid long edge-case inventories that compete with the current task.
- Put deterministic checks in code, schemas, validators, or guardrails.

Good prompt sections:

- Objective
- Available context
- Tool guidance
- Decision criteria
- Output contract
- Stopping conditions
- Escalation or clarification rules

## Skill Design

Use a skill when the agent needs reusable procedural knowledge rather than a new runtime actor.

Keep `SKILL.md` lean:

- Put the trigger conditions in frontmatter `description`, not the body.
- Keep core workflow and routing guidance in `SKILL.md`.
- Put detailed variants in one-level `references/` files.
- Put deterministic or repeated operations in `scripts/`.
- Put reusable templates or static assets in `assets/`.
- Prefer defaults with escape hatches over menus of equal options.

Calibrate freedom:

- High freedom: flexible review, research, synthesis, design.
- Medium freedom: preferred templates, structured workflows, configurable scripts.
- Low freedom: migrations, destructive operations, compliance checks, fragile file formats.

Avoid:

- Teaching the model general facts it already knows.
- Duplicating the same rule in multiple files.
- Burying critical gotchas in a large reference file without navigation.
- Time-sensitive facts without instructions to verify current sources.

## Context Engineering

Minimize up-front context and provide retrievable handles:

- File paths instead of full files.
- Query names instead of full datasets.
- Source URLs instead of copied articles, unless exact content is needed.
- IDs, object handles, and artifact paths instead of large payloads.

Use just-in-time retrieval:

- Let the agent inspect only relevant files or references.
- Search before reading large sources.
- Summarize large tool outputs before returning them to the model.
- Keep intermediate bulk data in code/runtime storage when the model does not need to see it.

Separate context types:

- Model context: facts the model must reason over.
- Runtime context: clients, credentials, database handles, authenticated user info, and private implementation state.
- Session history: conversation and tool events carried across turns.
- Durable workflow state: routing, approval, attempt, checkpoint, and resume facts.
- Artifact store: versioned handles to files and large results.
- Long-term memory: curated facts or preferences that survive beyond one workflow.

## Context And State Inventory

For each context, state, artifact, or memory class, define:

- owner and source of truth;
- schema/version and tenant boundary;
- provenance, trust level, timestamp, freshness, and TTL;
- read/write authority and validation;
- compaction, invalidation, correction, deletion, and retention;
- whether it may enter model context, logs, or serialized run state.

Memory is data, not authority. It may be stale or poisoned and must not silently override current
user intent, policy, authorization, or an authoritative external source. Preserve a durable,
recoverable session/event record separately from the model's curated context; evaluate compaction
and retrieval on long traces.

## Tool Contracts

Write tools like APIs for a capable but literal caller:

- One clear responsibility per tool.
- Clear `name`, concise description, and explicit use criteria.
- Parameters named for user intent, not internal implementation details.
- Enums and structured parameters where possible.
- Required fields only when genuinely required.
- Outputs that are concise, typed, and directly useful for the next decision.
- Error messages that say what failed and what the agent can do next.
- Caller identity, tenant/resource boundary, and required scopes.
- Server owner, provenance, trust assumptions, and data classification.
- Side-effect, reversibility, timeout, retryability, idempotency, deduplication, and concurrency.
- Pagination, filtering, truncation, and response-size limits.
- Typed error class, retry hint, and partial-result behavior.

Reduce tool ambiguity:

- Namespace tools by domain when many tools exist.
- Keep each namespace small enough to be searchable.
- Avoid overlapping tools with similar names and purposes.
- If two tools overlap, add a decision rule or merge/split them.

Make tools hard to misuse:

- Prefer absolute paths when file location matters.
- Use IDs instead of names when names are ambiguous.
- Validate arguments before side effects.
- Return previews or dry-run results before writes.
- Bind approval to the exact target, arguments, diff or preview, and disclosed data.
- Enforce authorization in the runtime or server, not in the prompt.

## Tool Loading

When many tools or MCP servers exist:

- Expose a compact catalog first.
- Use tool search, namespaces, MCP server descriptions, or filesystem-discoverable tool docs.
- Load full schemas only when the task needs them.
- For large data transfers, prefer code execution that filters/transforms data before returning concise results to the model.
- Filter tools by task, actor, tenant, and current authority.
- Trace catalog and schema versions and treat dynamic tool-list changes as security-relevant.
- Treat remote tool descriptions and annotations as untrusted hints unless independently verified.
- Prefer official or otherwise verified servers; sandbox local or executable servers with minimal
  filesystem, network, credential, and process access.

Programmatic tool calling or code execution is appropriate for bounded deterministic filtering and
aggregation, but requires resource limits and explicit network/data-egress controls.

## Structured Outputs

Use structured outputs when downstream code depends on:

- Routing destination.
- Extracted facts.
- Compliance decisions.
- Tool plans.
- Final report schema.
- Eval grading.

Do not parse model prose for critical control flow when a typed object is possible.

Structured output constrains shape; it does not confer trust, authorization, freshness, or factual
correctness. Validate semantic constraints at every privilege boundary and retain provenance fields
when downstream policy depends on the source.
