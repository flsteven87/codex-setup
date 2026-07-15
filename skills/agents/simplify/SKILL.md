---
name: simplify
description: Reduce accidental complexity in code, architecture, prompts, workflows, or PR diffs while preserving intended behavior. Use when the user says simplify, /simplify, make this simpler, reduce complexity, over-engineered, accidental complexity, 精簡, 簡化, or when another skill needs a simplification pass before verification or merge.
---

# Simplify

Find the smallest behavior-preserving path. Prefer deleting complexity over adding abstractions.

## Workflow

1. Identify the target and intended behavior.
   - For PRs, use the PR diff scope such as `git diff origin/main...HEAD --name-only`.
   - For local changes, use the user's named files or the current diff.
2. Separate load-bearing complexity from accidental complexity.
   - Load-bearing: required domain rules, compatibility contracts, security checks, data migrations, performance constraints, or explicit product requirements.
   - Accidental: duplicate paths, speculative config, parallel v2/enhanced variants, unused abstraction, defensive branches for impossible states, stale comments, or custom machinery where a local pattern already exists.
3. Prefer the smallest safe action:
   - Delete dead code before refactoring.
   - Inline one-off abstractions before creating new shared layers.
   - Collapse parallel implementations into the single current path.
   - Reuse existing helpers, conventions, and validation commands.
4. Stop before changing public behavior unless the user explicitly chooses that tradeoff.
5. Verify the simplified path with the smallest relevant checks when edits are made.

## Review Mode Output

When called by another pipeline, output a terse fix list:

```text
[HIGH] file:line - accidental complexity and smaller path
[MEDIUM] file:line - simplification that reduces maintenance risk
[LOW] file:line - optional mechanical cleanup
```

If clean, output exactly:

```text
no simplification findings
```

## Edit Mode Output

When the user directly asks you to simplify and edits are appropriate, implement the smallest safe change, then report:

- What was unnecessarily complex.
- What was simplified.
- What behavior was preserved.
- What validation ran.
- What remains intentionally complex and why.

## Rules

- Keep scope tight. This is not permission for a broad refactor.
- Do not introduce a new abstraction for one call site.
- Do not keep old/new/enhanced/v2 variants unless backward compatibility is explicitly required.
- Do not remove validation, auth, tenancy, RLS, migrations, or error handling that protects a real boundary.
- Do not simplify by hiding uncertainty behind defensive catch-all branches.
- If simplification would touch files outside the requested or PR diff scope, surface the tradeoff before editing.
