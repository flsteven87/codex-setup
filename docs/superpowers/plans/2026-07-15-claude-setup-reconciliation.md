# Claude Setup Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing dirty `~/.claude` worktree into one coherent, portable, secret-free Claude-only setup update and push it to `origin/main`.

**Architecture:** Preserve the hand-authored verification gate, workflow routing guard, routed deep-research workflow, and docs-cleanup skill. Exclude runtime team inboxes, remove the one hard-coded home path, reconcile plugin documentation with `settings.json`, and validate the complete public ship surface before committing.

**Tech Stack:** Claude Code settings JSON, Python 3.11 hook scripts, Claude Workflow JavaScript, Markdown skills and commands, Bash setup script, Git/GitHub CLI.

## Global Constraints

- Work only in `~/.claude`; do not create a runtime dependency on `codex-setup`.
- Preserve all pre-existing hand-authored changes unless validation proves a specific defect.
- Never commit `teams/`, credentials, tokens, API keys, OAuth state, local absolute paths, caches, or sessions.
- Use one final coherent Claude-only commit after validation.
- Push only with a fast-forward update to the tracked `origin/main` branch.

---

### Task 1: Classify and protect the ship surface

**Files:**
- Modify: `~/.claude/.gitignore`
- Inspect: `~/.claude/CLAUDE.md`
- Inspect: `~/.claude/commands/merge-pr.md`
- Inspect: `~/.claude/commands/ship.md`
- Inspect: `~/.claude/settings.json`
- Inspect: `~/.claude/hooks/verify_gate.py`
- Inspect: `~/.claude/hooks/workflow_route_guard.py`
- Inspect: `~/.claude/skills/docs-cleanup/SKILL.md`
- Inspect: `~/.claude/workflows/deep-research.js`

**Interfaces:**
- Consumes: the dirty working tree at `~/.claude`.
- Produces: a Git ship surface where runtime team messages are ignored and every remaining dirty file is intentional.

- [ ] **Step 1: Record the exact dirty state**

Run:

```bash
git -C ~/.claude fetch --all --prune --tags
git -C ~/.claude status --porcelain=v2
git -C ~/.claude diff --check
```

Expected: `main` is not behind or diverged; only the known setup files and runtime `teams/` entries appear.

- [ ] **Step 2: Add the failing ignore assertion**

Run before editing:

```bash
git -C ~/.claude check-ignore teams/example/inbox.json
```

Expected: non-zero because `teams/` is not yet ignored.

- [ ] **Step 3: Add the runtime ignore rule**

Append this entry in the session/runtime section of `.gitignore`:

```gitignore
teams/
```

- [ ] **Step 4: Verify the ignore behavior**

Run:

```bash
git -C ~/.claude check-ignore teams/example/inbox.json
git -C ~/.claude status --short
```

Expected: the sample path resolves to `teams/`, and the two real inbox JSON files disappear from status without being deleted.

### Task 2: Make the new Claude assets portable and documented

**Files:**
- Modify: `~/.claude/hooks/workflow_route_guard.py`
- Modify: `~/.claude/README.md`
- Modify: `~/.claude/setup.sh`

**Interfaces:**
- Consumes: the enabled plugin inventory in `settings.json` and the routed workflow path `~/.claude/workflows/deep-research.js`.
- Produces: documentation and diagnostics with no personal absolute home path and one consistent plugin inventory.

- [ ] **Step 1: Prove the current portability failure**

Run:

```bash
rg -n -F "$HOME" ~/.claude/hooks/workflow_route_guard.py
```

Expected: one match inside `DENY_REASON`.

- [ ] **Step 2: Replace the diagnostic path**

Change the route guidance to this portable text:

```python
DENY_REASON = (
    "Named workflows are un-routed — every agent() inherits the session model "
    "and bills at top tier. Use the routed copy via scriptPath (for example, "
    "~/.claude/workflows/deep-research.js), or resolve the built-in script, "
    "pin per-stage models per CLAUDE.md Multi-Agent Model Economics (haiku "
    "scan/fetch, sonnet review/verify, session model for synthesis only), then "
    "launch via scriptPath."
)
```

- [ ] **Step 3: Reconcile plugin instructions**

Use `settings.json.enabledPlugins` as the source of truth. Update both `README.md` and `setup.sh` so the recommended enabled set contains exactly:

```text
superpowers@superpowers-marketplace
codex@openai-codex
code-review@claude-plugins-official
typescript-lsp@claude-plugins-official
pyright-lsp@claude-plugins-official
andrej-karpathy-skills@karpathy-skills
impeccable@impeccable
ralph-loop@claude-plugins-official
```

Document `workflow_route_guard.py`, `verify_gate.py`, `workflows/deep-research.js`, and `docs-cleanup` in the tracked inventory.

- [ ] **Step 4: Verify documentation consistency**

Run a Python comparison that extracts enabled plugin keys and checks every key appears in both files:

```bash
uv run python - <<'PY'
import json
from pathlib import Path

root = Path.home() / ".claude"
settings = json.loads((root / "settings.json").read_text())
enabled = {name for name, value in settings["enabledPlugins"].items() if value}
for relative in ("README.md", "setup.sh"):
    text = (root / relative).read_text()
    missing = sorted(name for name in enabled if name not in text)
    assert not missing, f"{relative} missing enabled plugins: {missing}"
print("plugin documentation: OK")
PY
```

Expected: `plugin documentation: OK`.

### Task 3: Validate hooks, settings, workflow, and public safety

**Files:**
- Test: the complete intended `~/.claude` diff.

**Interfaces:**
- Consumes: Tasks 1–2 output plus the pre-existing hook/workflow/skill changes.
- Produces: evidence that the public commit is syntactically valid, portable, and secret-free.

- [ ] **Step 1: Run Python and JSON checks**

```bash
uv run ruff check ~/.claude/hooks/verify_gate.py ~/.claude/hooks/workflow_route_guard.py
uv run python -m py_compile ~/.claude/hooks/verify_gate.py ~/.claude/hooks/workflow_route_guard.py
jq empty ~/.claude/settings.json
```

Expected: all commands exit `0`.

- [ ] **Step 2: Exercise the routing guard contract**

```bash
printf '%s' '{"tool_input":{"name":"deep-research"}}' | uv run ~/.claude/hooks/workflow_route_guard.py | jq -e '.hookSpecificOutput.permissionDecision == "deny"'
test -z "$(printf '%s' '{"tool_input":{"scriptPath":"~/.claude/workflows/deep-research.js","name":"deep-research"}}' | uv run ~/.claude/hooks/workflow_route_guard.py)"
```

Expected: named launch is denied; routed `scriptPath` emits no denial.

- [ ] **Step 3: Exercise the verification gate in an isolated home**

```bash
tmp_home="$(mktemp -d)"
HOME="$tmp_home" uv run ~/.claude/hooks/verify_gate.py arm "test task" "observable state"
printf '%s' "{\"cwd\":\"$PWD\"}" | HOME="$tmp_home" uv run ~/.claude/hooks/verify_gate.py | jq -e '.decision == "block"'
HOME="$tmp_home" uv run ~/.claude/hooks/verify_gate.py clear
```

Expected: the gate arms, blocks, and clears without touching the real gate directory.

- [ ] **Step 4: Scan the intended public surface**

```bash
git -C ~/.claude diff --check
! git -C ~/.claude diff --name-only | rg '^(teams/|auth|projects/|sessions/|logs/)'
! rg -n -F "$HOME" \
  ~/.claude/CLAUDE.md ~/.claude/README.md ~/.claude/setup.sh ~/.claude/settings.json \
  ~/.claude/commands ~/.claude/hooks ~/.claude/skills/docs-cleanup ~/.claude/workflows
! rg -n 'gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY' \
  ~/.claude/CLAUDE.md ~/.claude/README.md ~/.claude/setup.sh ~/.claude/settings.json \
  ~/.claude/commands ~/.claude/hooks ~/.claude/skills/docs-cleanup ~/.claude/workflows
```

Expected: no secret-like value, personal absolute path, or runtime directory is in the ship surface.

### Task 4: Commit and push Claude setup

**Files:**
- Stage: only the intended Claude setup files.

**Interfaces:**
- Consumes: a green Task 3 validation gate.
- Produces: one fast-forward commit on `origin/main` and a clean local worktree except ignored runtime state.

- [ ] **Step 1: Stage the explicit file list**

```bash
git -C ~/.claude add .gitignore CLAUDE.md README.md setup.sh settings.json \
  commands/merge-pr.md commands/ship.md hooks/verify_gate.py \
  hooks/workflow_route_guard.py skills/docs-cleanup/SKILL.md \
  workflows/deep-research.js
git -C ~/.claude diff --cached --check
git -C ~/.claude diff --cached --stat
```

Expected: no `teams/` paths and no unrelated files.

- [ ] **Step 2: Commit**

```bash
git -C ~/.claude commit -m "feat(harness): enforce routed workflows and observed delivery"
```

Expected: one new commit on `main`.

- [ ] **Step 3: Push and verify**

```bash
git -C ~/.claude push origin main
git -C ~/.claude status --short --branch
git -C ~/.claude ls-remote --heads origin main
```

Expected: local and remote SHA match; worktree is clean.
