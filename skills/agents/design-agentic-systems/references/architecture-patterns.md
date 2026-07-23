# Architecture Patterns

Use this reference when choosing the system shape or reviewing an existing agent design.

## Contents

- Pattern Selection
- Workflow vs Agent
- Single vs Multi-Agent
- Model And Effort Routing
- Long-Running And Durable Work
- LangGraph Guidance
- Ownership Rule

## Pattern Selection

| Shape | Use When | Avoid When |
| --- | --- | --- |
| Direct model call | One model response can complete the task from supplied context. | The task needs retrieval, side effects, state, or multi-step recovery. |
| Augmented model call | One call with retrieval, structured output, or deterministic preprocessing can complete the task. | The model must adapt its next action from environment feedback. |
| Deterministic workflow | Steps are known in advance and can be represented in code. | The model must dynamically decide the sequence or recover from novel states. |
| Durable workflow | Known steps span process restarts, approvals, long waits, or effectful retries. | The work is short-lived and has no recovery requirement. |
| Prompt chain | Each step transforms or validates the previous output. | A single structured output would be enough. |
| Parallel workflow | Independent subtasks can run concurrently and be synthesized. | Subtasks share mutable state or require sequential unlocks. |
| Orchestrator-worker | A planner creates dynamic work units, workers produce bounded outputs, and a synthesizer combines them. | The work units are fixed or simple enough for static code. |
| Evaluator-optimizer | Output quality improves through critique/revision and eval criteria are clear. | Latency is critical or there is no measurable quality target. |
| Single agent with tools | A bounded specialist needs to plan, call tools, and recover across varied requests. | The tool surface is overloaded, policies differ, or ownership is unclear. |
| Skill | The same agent needs reusable procedure, reference material, scripts, or conventions. | The task requires a separate runtime owner or different permissions. |
| Manager/subagents | A manager owns the final answer and calls specialists as bounded tools. | Specialists need direct user interaction or persistent per-agent state. |
| Handoff | A specialist should take over the next response or a state must unlock sequential capabilities. | The manager must synthesize all results or parallel consultation matters. |
| Router | A typed decision selects one or more specialist branches. | Routing needs long multi-turn ownership; use handoff instead. |
| Swarm/hierarchical | Eval evidence shows bounded manager-worker decomposition cannot handle independently decomposable, high-value work. | Work shares mutable state, requires one complete context, or lacks a fan-out budget and merge owner. |

## Workflow vs Agent

Prefer a workflow when:

- The order of steps is predictable.
- The main challenge is transformation, validation, or aggregation.
- Deterministic code can decide the next step.
- You need lower latency, lower cost, and simpler debugging.

Prefer an agent when:

- The number or order of steps is not known up front.
- The task requires tool use based on environmental feedback.
- The model must recover from partial failures or missing information.
- The task has clear success criteria and can tolerate tool-loop latency.

## Single vs Multi-Agent

Start with one agent and improve tools/context/evals first. A split needs all of these:

- Work units can complete independently or have an explicit dependency graph.
- A coordinator owns synthesis, shared-state merging, and partial failure.
- Fan-out, token, latency, and cost budgets are bounded.
- Representative evals show a material benefit from context isolation, specialization, or
  parallelism over a single-agent baseline.

Different tools, instructions, models, guardrails, teams, or trace boundaries are supporting
signals, not sufficient proof by themselves. Do not split only because:

- The prompt is long but can be turned into a skill or reference.
- Tool descriptions are vague.
- There are many edge cases but no evaluated failure modes.
- The implementation looks more impressive with multiple agents.

## Model And Effort Routing

1. Establish task quality with a capable model and representative evals.
2. Try lower-cost models or effort settings per stage, keeping the same release threshold.
3. Escalate only on typed evidence such as task class, confidence gate, or recoverable failure.
4. Bound fallbacks; do not let models repeatedly upgrade or retry themselves.
5. Trace the selected model, effort, route reason, fallback reason, tokens, latency, and cost.

Revisit routing and architecture after model, tool, or workload changes. Harness components encode
assumptions about model limitations; remove one component at a time when ablation evals show it has
become dead weight.

## Long-Running And Durable Work

Separate the durable session/event log, the orchestration harness, and the execution sandbox or
tool runtime. Define:

- checkpoint boundaries and what replays after a restart;
- idempotency or deduplication for every write;
- timeout, retry, and total budget policy;
- version compatibility for persisted runs;
- partial-result merge and compensation behavior;
- a typed terminal outcome and recovery owner.

## LangGraph Guidance

Model the graph around explicit state:

- `task_type`: typed classification or workflow family.
- `active_agent`: current conversation owner for handoff-style flows.
- `flow_version`: behavior version for long-lived persisted threads.
- `checkpoint_version`: schema and replay contract for persisted state.
- `approval_state`: pending, approved, rejected, or not_required.
- `attempt_count`: bounded retry state.
- `termination_reason`: typed terminal outcome.
- `next_action`: typed instruction for the next node.
- `artifacts`: IDs, file paths, or handles rather than large content blobs.
- `idempotency_key`: or a handle to the runtime-owned deduplication record for effectful steps.

Prefer these routing methods:

- Structured model output with an enum destination.
- Deterministic classifier for rules that do not need judgment.
- Tool or handoff function that returns a state update.
- `Command(update=..., goto=...)` when a node should update state and choose the next node.
- `Send` for dynamic parallel worker fan-out.

Avoid:

- `if "refund" in user_message` style routing for production behavior.
- Parsing model prose to infer the next node.
- Repeating routing facts only in conversation history instead of graph state.
- Sharing mutable state across concurrent workers without reducers or merge rules.

## Ownership Rule

Before adding any agent, answer:

1. Who owns the user-visible reply at this point?
2. Which tools can this owner call?
3. Under whose identity, tenant, and scopes do calls execute?
4. Which state can it read/write?
5. Who owns the external side effect, merge, or compensation after partial failure?
6. Which actions require approval?
7. What trace evidence proves ownership transferred correctly?

If these answers are unclear, the design is not ready for implementation.
