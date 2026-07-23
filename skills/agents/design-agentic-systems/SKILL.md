---
name: design-agentic-systems
description: Design or review agents, LLM workflows, skills, tool-calling, RAG, LangGraph, and multi-agent systems. Choose the simplest architecture and define contracts, controls, runtime reliability, observability, and evals.
---

# Design Agentic Systems

Design agentic behavior before implementation.

## Core Rule

Keep deterministic work in code and contracts. Use model judgment only where the task requires interpretation, planning, routing under ambiguity, synthesis, or recovery from partial information.

Improve the task boundary, context, tools, and evals before adding complexity. Treat every agent,
loop, retry, memory layer, and prompt rule as a hypothesis retained only when representative evals
justify its latency, cost, and operational burden.

## Evidence Gates

### 1. Define the job and risk contract

- State the user-visible outcome, external end state, representative tasks, acceptance criteria,
  non-goals, users or tenants, data sensitivity, latency/cost budget, and side effects.
- Identify validation, counting, ranking, permission checks, formatting, schema integrity, retries,
  and policy enforcement that belong in deterministic code.

Complete this gate when success, risk, budgets, and deterministic responsibilities are measurable.

### 2. Choose the simplest system shape

Choose an augmented model call, deterministic workflow, single agent, skill, or multi-agent design.
Read [architecture patterns](references/architecture-patterns.md) when the shape is not already
constrained or when reviewing an existing architecture.

Establish a capable-model baseline before adding model routing or downgrading stages. Require
measured independence, context-isolation or parallelism value, and acceptable economics before
splitting into multiple agents.

Complete this gate when the selected shape and materially rejected alternatives have eval evidence.

### 3. Define tool, context, state, and memory contracts

- Define each agent or workflow owner and each tool's purpose, identity, authority, trust source,
  input/output schema, data class, side-effect class, timeout, retryability, and idempotency.
- Give each state or memory field an owner, source of truth, schema/version, freshness or TTL,
  write policy, and invalidation rule.
- Keep model context, runtime context, session history, durable workflow state, artifacts, and
  long-term memory distinct.

Read [skills, context, and tools](references/skill-context-tools.md) when writing or reviewing
prompts, skills, tool schemas, context retrieval, MCP surfaces, or progressive disclosure.

Complete this gate when every tool and state field has one owner, an explicit contract, and a
traceable control-flow role.

### 4. Model trust boundaries and place controls

Map untrusted and sensitive sources through the model to effectful sinks. Place input, retrieval,
tool, state, output, authorization, egress, sandbox, and human-review controls at the boundary where
failure can occur. Bind every proposed action to the user's current intent and server-side
authority; model compliance, classifiers, and remote tool annotations are not authorization.

Read [quality gates](references/quality-gates.md) completely for production hardening, high-impact
actions, security controls, or formal review.

Complete this gate when every source-to-sink path has enforceable data-flow and authorization
controls and every high-impact action has a scoped approval rule.

### 5. Define runtime reliability

For long-running or side-effecting work, define checkpoint and replay semantics, idempotency or
deduplication keys, bounded retries and timeouts, concurrency rules, partial-failure merge policy,
compensation, versioned resume behavior, budgets, and typed terminal outcomes.

Complete this gate when a crash or resume cannot silently duplicate effects, retries are bounded,
and every run ends in one explicit outcome.

### 6. Define eval and observability proof

Grade external outcomes first and trace invariants where the path matters. Use representative,
isolated trials; separate capability from regression suites; run enough trials for nondeterminism;
prefer deterministic graders and calibrate model graders with humans. Trace versions, routing,
tools, state transitions, approvals, retries, termination, latency, and cost without retaining
unnecessary sensitive payloads.

Complete this gate when model-judgment responsibilities and known failures map to evals, regression
thresholds gate releases, and production signals can identify failure provenance.

### 7. Produce the implementation plan

List the agents or workflows, skills, tools, state schema, routing rules, controls, eval cases,
runtime recovery, observability, deterministic code paths, rollout/rollback, and remaining risks.
Give each implementation step its owner, first verification command or observable check, and
recovery check.

Complete this gate when the plan can be implemented without inventing an owner, contract, control,
recovery rule, or acceptance test.

For framework-specific API syntax, fetch current official docs before implementation. Agent
frameworks and managed platforms change quickly; this skill provides design principles, not stable
API signatures.

## Output Shape

When producing a design, use this structure unless the user asks for a different artifact:

1. Recommendation: the simplest suitable system shape and why.
2. Architecture: agents/workflows/skills/tools/state and ownership boundaries.
3. Contracts: tools, context, memory, routing state, authority, and deterministic code paths.
4. Controls: source-to-sink boundaries, approvals, permissions, and stopping conditions.
5. Reliability: checkpoints, replay, idempotency, retries, compensation, and terminal outcomes.
6. Evals and observability: outcome/trace graders, suites, thresholds, versions, and telemetry.
7. Implementation plan: small steps, verification, rollout/rollback, and recovery checks.
