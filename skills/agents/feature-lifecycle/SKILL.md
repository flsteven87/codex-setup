---
name: feature-lifecycle
description: Use only when the user explicitly asks for feature-lifecycle, a full feature workflow, an end-to-end feature process, 從需求到出貨, 完整 feature 流程, or 功能開發流程. Route one coherent feature through the installed Superpowers design, planning, execution, verification, and finish skills, adding local risk hardening only when justified.
---

# Feature Lifecycle

Act as a thin router over installed workflow skills. Do not recreate their instructions here.

## Scope

- Use this skill only when explicitly invoked for an end-to-end workflow.
- For a tiny edit, bounded implementation, bug investigation, or shipping-only request, use the
  matching focused skill instead.
- Split multiple independent subsystems into separate feature lifecycles.
- Follow direct user and repository instructions when they override a child skill's default docs,
  commit, branch, or worktree behavior.

## Pipeline

### 1. Establish The Boundary

Use `superpowers:brainstorming` whenever its current trigger requires design discovery. Establish
the goal, non-goals, success criteria, constraints, and approved approach. Reuse an already
approved design when the active instructions and child skill permit it.

Do not create or commit a design document when user or repository instructions require chat-only
planning or explicit documentation approval.

### 2. Write The Plan

Use `superpowers:writing-plans` for multi-step implementation. The plan must identify exact scope,
tests, commands, dependencies, and completion evidence. Keep plan artifacts in chat unless the
user or repository workflow authorizes a file.

### 3. Harden Only When Earned

Run a hardening pass when the change crosses layers or affects data integrity, auth, permissions,
billing, migrations, external integrations, async processing, deployment, rollback, or other
high-blast-radius behavior.

Check only three things:

1. Required facts are verified or explicitly assumed.
2. The smallest design still satisfies the goal.
3. Likely failure modes map to tests, validation, rollback, or an accepted risk.

Apply this checklist directly. When findings require plan changes, update only the affected tasks,
tests, validation, or rollback notes. Do not add speculative mitigations.

### 4. Execute

- Use `superpowers:subagent-driven-development` only when the user explicitly authorizes subagents
  or delegation in the current request.
- Otherwise use `superpowers:executing-plans` for a written plan. Execute bounded current-session
  work directly under the active user and repository instructions.
- Preserve unrelated changes and follow repository branch/worktree rules.

### 5. Verify And Finish

Use `superpowers:verification-before-completion` before any completion claim. Run the repository's
actual checks and read their output.

After verification:

- use `ship` when the user authorized delivery; it resolves branch push, PR merge, and deployment
  from the repository's actual workflow;
- otherwise report the verified local result without publishing it.

## Decision Gates

Stop only when the active child skill requires approval or when one of these decisions is missing:

- product or design boundary;
- high-risk assumption or accepted risk;
- material plan concern;
- commit, push, merge, destructive cleanup, or external write authorization.

Do not ask again for authority the user already granted in the current request.

## Completion

Report the phases used, key decisions, files changed, verification evidence, publishing state, and
remaining risk. Mention skipped phases only when the omission is meaningful.
