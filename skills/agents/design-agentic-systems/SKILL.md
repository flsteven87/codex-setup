---
name: design-agentic-systems
description: Design and review agentic systems and LLM pipelines using best practices for workflows vs agents, skills, context engineering, tool contracts, routing, state, guardrails, human review, tracing, and evals. Use when Codex is asked to build, refactor, critique, plan, or harden an AI agent, LangGraph graph, multi-agent workflow, skill, prompt stack, tool-calling system, RAG workflow, or LLM pipeline.
---

# Design Agentic Systems

Use this skill to design agentic behavior before implementation. Optimize for a system that is simple enough to debug, flexible enough for the task, and measurable enough to improve.

## Core Rule

Keep deterministic work in code and contracts. Use model judgment only where the task requires interpretation, planning, routing under ambiguity, synthesis, or recovery from partial information.

Do not make a system more agentic because the prompt is hard to maintain. First improve the task boundary, context shape, tool contracts, and evals.

## Workflow

1. Define the job.
   - State the user-visible outcome, success criteria, non-goals, latency/cost tolerance, and side effects.
   - Identify what must be deterministic: validation, counting, ranking, permission checks, formatting, schema integrity, retries, and policy enforcement.

2. Choose the simplest system shape.
   - Direct model call: use for one-shot classification, extraction, summarization, rewrite, or generation with stable context.
   - Workflow or LLM pipeline: use when steps are known in advance.
   - Single agent with tools: use when the path varies but ownership, policy, and tool surface fit one specialist.
   - Multi-agent: use only when separate ownership, tools, policies, models, context windows, or team boundaries materially improve reliability.
   - Skill: use when a general agent needs reusable procedural knowledge, reference material, scripts, or conventions without creating a separate runtime actor.

3. Shape context and skills.
   - Keep the top-level prompt at the right altitude: concrete heuristics, not brittle case tables.
   - Use progressive disclosure: metadata first, short core instructions second, references/scripts only when needed.
   - Use a few canonical examples for behavior calibration; do not list every edge case.

4. Design tools as contracts.
   - Give each tool one clear purpose, unambiguous parameters, concise outputs, and explicit usage criteria.
   - Remove or split overlapping tools before adding routing instructions.
   - Put fragile argument construction rules in tool descriptions or schemas, not only in the main prompt.
   - Prefer structured outputs and typed return values over free-form text when downstream code depends on the result.

5. Design routing and state.
   - Do not route by raw substring matching on user text or model prose.
   - Route from typed decisions, state fields, tool calls, or explicit handoff commands.
   - Persist routing facts such as `task_type`, `active_agent`, `flow_version`, `approval_state`, and `next_action` when they affect later turns.
   - For LangGraph, model behavior as State + Nodes + Edges; use `Command` when one step must update state and choose the next node.

6. Add guardrails and human review.
   - Use input guardrails before expensive or side-effecting work.
   - Use tool guardrails around arguments/results for risky tools.
   - Use output guardrails before user-visible or externally stored output.
   - Require human approval for writes, destructive actions, financial actions, permission changes, shell commands, production changes, or sensitive MCP/tool calls.

7. Define evals before trusting the design.
   - Start with trace inspection for early behavior debugging.
   - Add repeatable cases once "good" is clear.
   - Evaluate tool choice, routing, handoff, guardrail behavior, stopping rules, and final output quality.
   - Compare prompt/skill/tool changes with pass rate, error type, latency, cost, and human-review load.

8. Produce an implementation plan.
   - List agents, skills, tools, state schema, routing rules, guardrails, eval cases, and observability.
   - Call out what stays deterministic in application code.
   - State remaining risks and what evidence would prove the design is working.

## Read References

- Read `references/architecture-patterns.md` when choosing between direct calls, workflows, single agents, multi-agent patterns, LangGraph, routers, subagents, or handoffs.
- Read `references/skill-context-tools.md` when writing or reviewing prompts, skills, tool schemas, context retrieval, MCP surfaces, or tool-search/progressive-disclosure behavior.
- Read `references/quality-gates.md` when defining guardrails, human review, evals, trace checks, security controls, or production readiness criteria.

For framework-specific API syntax, fetch current official docs before implementation. Agent frameworks and managed platforms change quickly; this skill provides design principles, not stable API signatures.

## Output Shape

When producing a design, use this structure unless the user asks for a different artifact:

1. Recommendation: the simplest suitable system shape and why.
2. Architecture: agents/workflows/skills/tools/state and ownership boundaries.
3. Contracts: tool schemas, structured outputs, routing state, and deterministic code paths.
4. Controls: guardrails, approvals, permissions, and stopping conditions.
5. Evals: trace checks, dataset cases, metrics, and expected failure modes.
6. Implementation plan: small steps and first verification commands.

## Anti-Patterns

- Replacing a bad prompt with many agents before improving tool contracts and context.
- Encoding business logic as a long list of natural-language if/else cases.
- Routing by string contains checks on raw user text or model prose.
- Giving the model every tool, document, and policy up front.
- Treating prompts as the only safety layer for high-impact actions.
- Adding subagents that do not provide different tools, ownership, context, policy, or model choice.
- Using open-ended loops without explicit stop conditions and traceable progress.
