# Architecture Patterns

Use this reference when choosing the system shape or reviewing an existing agent design.

## Pattern Selection

| Shape | Use When | Avoid When |
| --- | --- | --- |
| Direct model call | One model response can complete the task with stable context and no tool loop. | The task needs external data, side effects, state, or multi-step recovery. |
| Deterministic workflow | Steps are known in advance and can be represented in code. | The model must dynamically decide the sequence or recover from novel states. |
| Prompt chain | Each step transforms or validates the previous output. | A single structured output would be enough. |
| Parallel workflow | Independent subtasks can run concurrently and be synthesized. | Subtasks share mutable state or require sequential unlocks. |
| Orchestrator-worker | A planner creates dynamic work units, workers produce bounded outputs, and a synthesizer combines them. | The work units are fixed or simple enough for static code. |
| Evaluator-optimizer | Output quality improves through critique/revision and eval criteria are clear. | Latency is critical or there is no measurable quality target. |
| Single agent with tools | A bounded specialist needs to plan, call tools, and recover across varied requests. | The tool surface is overloaded, policies differ, or ownership is unclear. |
| Skill | The same agent needs reusable procedure, reference material, scripts, or conventions. | The task requires a separate runtime owner or different permissions. |
| Manager/subagents | A manager owns the final answer and calls specialists as bounded tools. | Specialists need direct user interaction or persistent per-agent state. |
| Handoff | A specialist should take over the next response or a state must unlock sequential capabilities. | The manager must synthesize all results or parallel consultation matters. |
| Router | A typed decision selects one or more specialist branches. | Routing needs long multi-turn ownership; use handoff instead. |
| Swarm/hierarchical | The task is open-ended, ambiguous, and benefits from multiple levels of decomposition. | A single agent, workflow, or manager pattern can meet the target. |

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

Start with one agent and improve tools/context/evals first. Split only when at least one condition is true:

- A specialist needs a different tool or MCP surface.
- A specialist needs different instructions, model settings, guardrails, approval policy, or output style.
- Context windows should be isolated to prevent overload or contamination.
- A subtask benefits from parallel work.
- Different teams need independent ownership of specialist behavior.
- Traces need explicit routing boundaries for debugging or compliance.

Do not split only because:

- The prompt is long but can be turned into a skill or reference.
- Tool descriptions are vague.
- There are many edge cases but no evaluated failure modes.
- The implementation looks more impressive with multiple agents.

## LangGraph Guidance

Model the graph around explicit state:

- `task_type`: typed classification or workflow family.
- `active_agent`: current conversation owner for handoff-style flows.
- `flow_version`: behavior version for long-lived persisted threads.
- `approval_state`: pending, approved, rejected, or not_required.
- `next_action`: typed instruction for the next node.
- `artifacts`: IDs, file paths, or handles rather than large content blobs.

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
3. Which state can it read/write?
4. Which actions require approval?
5. What trace evidence proves ownership transferred correctly?

If these answers are unclear, the design is not ready for implementation.
