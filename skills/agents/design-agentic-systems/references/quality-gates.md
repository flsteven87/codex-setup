# Quality Gates

Use this reference when hardening an agentic design for implementation or production.

## Contents

- Pre-Implementation Gate
- Trust Boundaries And Data Flow
- Guardrail Placement
- Approval Contract
- Durable Execution And Recovery
- Evals
- Security And Governance
- Operational Observability
- Stop Conditions
- Review Checklist

## Pre-Implementation Gate

Do not implement until these are explicit:

- User-visible outcome and acceptance criteria.
- External end-state predicate, representative workload, risk class, and budget envelope.
- Simplest selected architecture and rejected alternatives.
- Deterministic responsibilities vs model-judgment responsibilities.
- Tool list with purpose, identity, scopes, trust source, data contract, side-effect class, timeout,
  retryability, and idempotency.
- Context, state, artifact, and memory inventory with owners, versions, freshness, and invalidation.
- Guardrail and approval checkpoints.
- Checkpoint, replay, retry, compensation, and typed terminal-state contract when applicable.
- Trace and eval plan.
- Known failure modes and rollback path.

## Trust Boundaries And Data Flow

Model the full source-to-sink path:

- Untrusted sources: user input, web, email, documents, retrieval, MCP resources/results, subagent
  output, and memory.
- Sensitive sources: credentials, private data, identity, session state, and approval state.
- Effectful sinks: writes, network egress, messages, payments, code execution, credentialed reads,
  and durable memory writes.

For each path through the model, minimize and validate fields, enforce identity/scopes and egress
outside the model, and use allowlists, isolation, sandboxing, approval, or prohibition according to
risk. Server trust and content trust are separate. A trusted connector may still return hostile
content, and remote tool descriptions or annotations are not security evidence.

Assume prompt-injection detection can fail. Classifiers and model guardrails are signals, not
authorization boundaries; constrain the impact of a manipulated model.

## Guardrail Placement

Use controls at the boundary where failure happens:

- Input guardrail: blocks disallowed or out-of-scope requests before main work.
- Retrieval/tool-output guardrail: keeps external content out of high-authority instructions and
  reduces it to validated fields before privileged decisions.
- Tool-argument guardrail: validates side-effecting call arguments.
- Tool-result guardrail: validates returned data before acting on it.
- State guardrail: prevents invalid transitions or stale approvals.
- Output guardrail: redacts, validates, or blocks final output.
- Human review: pauses before irreversible, sensitive, financial, privileged, or production actions.

Prompts may describe policy, but enforce important policy in code, guardrails, approvals, or platform controls.

## Approval Contract

An approval record names:

- approver identity and delegated authority;
- exact tool, arguments, target, preview or diff, and data leaving the boundary;
- single-call or bounded-batch scope, expiry, and call or transaction ID;
- approve, reject, modify, timeout, and resume behavior.

Default to single-use. Invalidate approval when relevant arguments, target, actor, policy, tool
version, disclosed data, or external state changes. Persist rejection and pending state across
restart; never convert missing approval state into approval. Human approval does not replace
server-side authorization or make an incorrect action safe.

## Durable Execution And Recovery

For work that can outlive one process or repeat a side effect, define:

- durable checkpoint boundary and replay semantics;
- idempotency or deduplication key for every write;
- transient, model-recoverable, user-fixable, policy-blocked, and fatal failure classes;
- retryable errors, backoff, max attempts, timeout, and total retry budget;
- concurrency and partial fan-out merge policy;
- compensation or an explicit non-compensable boundary;
- workflow, state, prompt, policy, and tool versions used to resume or fail closed.

Address the crash window where a side effect succeeds before its checkpoint is committed.

## Evals

Start with trace review, then convert real tasks and failures into repeatable, isolated trials.
Grade the external environment outcome first. Grade traces when authorization, forbidden actions,
tool choice, or other path invariants matter.

Trace questions:

- Did the agent choose the right tool?
- Did it avoid unnecessary tools?
- Did routing or handoff happen at the right time?
- Did it preserve ownership of the final answer?
- Did it use state rather than re-inferring facts from chat history?
- Did guardrails trigger, pause, or allow correctly?
- Did the run stop for the right reason?
- Did the external state actually reach the claimed outcome?

Dataset cases:

- Happy path.
- Ambiguous request.
- No-op or no relevant tool.
- Tool failure.
- Missing permission.
- Unsafe or prompt-injected tool output.
- Stale or conflicting context.
- Multi-turn continuation.
- Long context or compaction pressure.
- High-impact action requiring approval.
- Similar tools that could be confused.
- Cross-tool or cross-MCP exfiltration.
- Poisoned or stale memory.
- Stale approval after arguments or state change.
- Crash-and-resume after a successful write.
- Partial fan-out failure and bounded model fallback.

Use both positive and negative cases. Run multiple trials when model behavior is nondeterministic.
Keep capability suites separate from near-100%-threshold regression suites. Start every trial from
a clean environment close to production.

Use deterministic graders for objective outcomes and invariants. Use model graders for open-ended
quality only with a specific rubric and periodic human calibration. Prefer outcome grading over
requiring one exact trajectory unless the path itself is the policy.

Metrics:

- Task pass rate.
- First-attempt success and repeated-trial consistency.
- Tool-choice accuracy.
- False route and missed route rates.
- Guardrail false positive/negative rates.
- Loop or timeout rate.
- Human-review load.
- Latency and cost.
- Token usage by context segment.
- Regression count by failure mode.

## Security And Governance

Treat agents as software with identity, permissions, and audit needs:

- Use least privilege for every tool and connector.
- Separate read tools from write tools.
- Avoid exposing secrets in prompts, traces, logs, or tool outputs.
- Treat retrieved documents, web pages, email, tickets, and tool outputs as untrusted.
- Validate that tool calls match the user's intent and authorization.
- Log safe summaries, IDs, and decisions; do not log full sensitive payloads unless required and approved.
- Version skills, prompts, tool schemas, guardrails, and routing policies.
- Require review for new skills that contain executable code or broad tool permissions.
- Isolate tenants, sessions, artifacts, and long-term memory.
- Treat memory as potentially stale or poisoned data with provenance, write authority, and expiry.
- Treat MCP servers, tool catalogs, annotations, and dynamic tool-list changes as supply-chain and
  trust-boundary inputs.
- Keep credentials outside model context and execution sandboxes where possible.
- Validate identity, token audience, scopes, and resource boundaries at the server on every call.

## Operational Observability

Correlate run, step, model call, tool call, handoff, approval, retry, checkpoint, and state
transition. Record the model/effort and versions of prompts, tools, policies, routing, state, and
eval harness; termination reason; failure provenance; latency; token/tool usage; and cost.

Define trace access, redaction, sampling, retention, and deletion. Do not retain raw sensitive model
or tool payloads merely because the tracing platform supports them.

## Stop Conditions

Every agent loop needs a task-specific success predicate, no-progress or duplicate-call detector,
and budgets for turns, tool calls, wall time, tokens, cost, retries, and fan-out. End in one typed
state such as:

- `SUCCEEDED`
- `NEEDS_USER_INPUT`
- `NEEDS_APPROVAL`
- `BLOCKED_BY_POLICY`
- `PARTIAL`
- `EXHAUSTED_BUDGET`
- `FAILED_RETRYABLE`
- `FAILED_FATAL`

If the agent can neither proceed nor ask a useful question, return a bounded failure with evidence.

## Review Checklist

Use this checklist before handoff:

- The design uses the simplest reliable architecture.
- Routing is typed or state-driven, not string matched.
- Skills use progressive disclosure.
- Tools have non-overlapping contracts.
- Deterministic logic is not delegated to the model.
- High-impact actions require approval.
- Source-to-sink prompt-injection and cross-tool exfiltration paths have enforceable controls.
- Resumable writes have replay, idempotency, retry, and compensation rules.
- Approvals bind to exact actions and invalidate on relevant change.
- Traces expose versions, model calls, tools, handoffs, guardrails, state, retries, and termination
  without unnecessary sensitive payloads.
- Evals grade outcomes and required trace invariants across isolated repeated trials.
- Remaining risks are named with concrete validation steps.
