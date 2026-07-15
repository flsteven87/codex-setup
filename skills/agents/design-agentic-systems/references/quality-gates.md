# Quality Gates

Use this reference when hardening an agentic design for implementation or production.

## Contents

- Pre-Implementation Gate
- Guardrail Placement
- Evals
- Security And Governance
- Stop Conditions
- Review Checklist

## Pre-Implementation Gate

Do not implement until these are explicit:

- User-visible outcome and acceptance criteria.
- Simplest selected architecture and rejected alternatives.
- Deterministic responsibilities vs model-judgment responsibilities.
- Tool list with purpose, parameters, output contract, and side-effect class.
- State schema and routing fields.
- Guardrail and approval checkpoints.
- Trace and eval plan.
- Known failure modes and rollback path.

## Guardrail Placement

Use controls at the boundary where failure happens:

- Input guardrail: blocks disallowed or out-of-scope requests before main work.
- Retrieval/tool-output guardrail: treats untrusted content as data, not instructions.
- Tool-argument guardrail: validates side-effecting call arguments.
- Tool-result guardrail: validates returned data before acting on it.
- State guardrail: prevents invalid transitions or stale approvals.
- Output guardrail: redacts, validates, or blocks final output.
- Human review: pauses before irreversible, sensitive, financial, privileged, or production actions.

Prompts may describe policy, but enforce important policy in code, guardrails, approvals, or platform controls.

## Evals

Start with trace review, then convert recurring expectations into repeatable evals.

Trace questions:

- Did the agent choose the right tool?
- Did it avoid unnecessary tools?
- Did routing or handoff happen at the right time?
- Did it preserve ownership of the final answer?
- Did it use state rather than re-inferring facts from chat history?
- Did guardrails trigger, pause, or allow correctly?
- Did the run stop for the right reason?

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

Metrics:

- Task pass rate.
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

## Stop Conditions

Every agent loop needs explicit stop conditions:

- Final structured output emitted.
- No more tool calls needed.
- Required approval is pending.
- User input is required.
- Tool failure is unrecoverable.
- Max iterations or budget reached.
- Safety/policy guardrail blocks continuation.

If the agent can neither proceed nor ask a useful question, return a bounded failure with evidence.

## Review Checklist

Use this checklist before handoff:

- The design uses the simplest reliable architecture.
- Routing is typed or state-driven, not string matched.
- Skills use progressive disclosure.
- Tools have non-overlapping contracts.
- Deterministic logic is not delegated to the model.
- High-impact actions require approval.
- Prompt-injection paths from untrusted context are addressed.
- Traces expose model calls, tools, handoffs, guardrails, and state transitions.
- Evals cover tool choice, routing, guardrails, and final output.
- Remaining risks are named with concrete validation steps.
