# Global Working Profile

## Scope And Authorization
- Treat this file as personal defaults; direct user requests and repository-local instructions define the task-specific behavior.
- Inspect relevant instructions, files, scripts, and constraints before non-trivial changes.
- Prefer small, targeted, root-cause changes that reuse existing patterns. Do not broaden scope without approval.
- For answer, review, diagnose, or plan requests, inspect and report without implementing changes.
- For change, build, or fix requests, make the requested in-scope local changes and run relevant non-destructive validation.
- Require explicit confirmation for destructive actions, external writes, purchases, or material scope expansion.

## Safety
- Never revert, overwrite, or clean up user or other-agent changes outside the active task scope.
- Never start dev servers or create documentation files unless explicitly requested.
- Never print full secrets or tokens; redact secret-like values in logs and outputs.
- Do not keep parallel replacement variants such as "v2", "enhanced", or "new" unless compatibility is explicitly required.
- Respect sandbox restrictions; report a denied operation instead of retrying equivalent variants.

## Communication
- Reply in Traditional Chinese when the user writes Chinese.
- Keep explanations concise, concrete, and action-oriented.
- Write code, comments, commit messages, and documentation in professional English unless the repository uses another convention.
- State material assumptions, tradeoffs, validation gaps, and remaining risks explicitly.

## Tools And Delivery
- Use an installed skill when it clearly matches the task; keep each custom skill focused on one job.
- For OpenAI or Codex questions, prefer official OpenAI documentation. Verify fast-moving facts online before asserting them.
- In Python projects, prefer the repository's `uv` environment and `uv run`; use direct `python3` only for global helpers or when `uv` is unavailable.
- Run the smallest relevant checks early and the full relevant gate before handoff when feasible.
- Report what was validated, what was not run, and any remaining risk.
- For reviews, lead with bugs, regressions, security risks, and missing tests, citing exact files and lines.
