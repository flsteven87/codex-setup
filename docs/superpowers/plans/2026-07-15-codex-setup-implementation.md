# Codex Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a clean, standalone, public Codex reference setup that tracks only hand-authored assets and safely documents third-party installation.

**Architecture:** Keep the repository at `~/.codex-setup` as a source repository, separate from the runtime-heavy `~/.codex`. Link portable instructions, rules, and custom skills into their native user locations; keep live config and authentication local; reference marketplace plugins and MCP servers through supported install commands. Document that current user `PreToolUse` hooks cannot enforce a deny decision.

**Tech Stack:** Bash, Python 3.11, TOML, JSON, Codex CLI 0.144.4+, Codex rules/skills/plugins/MCP, GitHub secret scanning.

## Global Constraints

- The repository is public and standalone; it must not depend on `claude-code-setup`.
- Never copy live `~/.codex/config.toml`, authentication, OAuth state, project trust, sessions, caches, databases, personal paths, or plugin contents.
- Do not vendor marketplace plugins or plugin-provided skills.
- Setup must be idempotent and must stop on existing non-matching targets.
- Setup must never overwrite `~/.codex/config.toml`.
- Examples must use OAuth, `bearer_token_env_var`, or `env_http_headers`; never literal secrets.
- Runtime model selection remains unpinned; documented compatibility pins require an update note.

---

### Task 1: Establish the public-repository safety gate

**Files:**
- Create: `.gitignore`
- Create: `scripts/check-secrets.sh`
- Create: `tests/test_check_secrets.sh`
- Create: `LICENSE`

**Interfaces:**
- Produces: `scripts/check-secrets.sh [--staged|--tracked|PATH...]`, returning `0` when clean and `1` on a high-confidence secret, credential filename, or personal absolute path.

- [ ] **Step 1: Write the failing scanner test**

Create `tests/test_check_secrets.sh` with isolated fixtures for a safe environment-variable example, a GitHub token-shaped value, a private-key marker, and a personal absolute home path assembled from path segments. The assertions are:

```bash
"$CHECK" "$tmp/safe.toml"
! "$CHECK" "$tmp/token.txt"
! "$CHECK" "$tmp/key.pem"
! "$CHECK" "$tmp/path.txt"
```

- [ ] **Step 2: Run the test and verify failure**

```bash
bash tests/test_check_secrets.sh
```

Expected: fail because `scripts/check-secrets.sh` does not exist.

- [ ] **Step 3: Implement the scanner**

Implement a Bash scanner that obtains NUL-delimited file lists from `git diff --cached --name-only -z`, `git ls-files -z`, or explicit paths; rejects credential filenames; and scans text with high-confidence token and private-key expressions. Construct the macOS and Linux home-path expressions from separate path-segment variables so the scanner does not flag its own source.

```text
gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY
```

Diagnostics print only the file and rule category, never the matching value.

- [ ] **Step 4: Add public ignores and license**

Ignore `.env*`, auth/credential files, private keys, certificates, sessions, logs, SQLite, caches, generated assets, local config, and OS/editor state. Use the MIT license with copyright `2026 Steven Wu`.

- [ ] **Step 5: Verify and commit**

```bash
bash tests/test_check_secrets.sh
bash scripts/check-secrets.sh --tracked
git diff --check
git add .gitignore LICENSE scripts/check-secrets.sh tests/test_check_secrets.sh
git commit -m "feat: add public repository safety gate"
```

Expected: tests and scanner pass; one focused commit is created.

### Task 2: Add portable Codex-owned instructions, rules, and skills

**Files:**
- Create: `AGENTS.md`
- Create: `rules/default.rules`
- Create: `skills/agents/<skill directories>`
- Create: `skills/codex/record-nexrex-with-loom/`
- Create: `tests/test_content.sh`

**Interfaces:**
- Consumes: hand-authored sources under current `~/.codex/AGENTS.md`, `~/.codex/rules/default.rules`, `~/.agents/skills`, and `~/.codex/skills/record-nexrex-with-loom`.
- Produces: repository-owned portable assets with the original skill directory names and no plugin-delivered content.

- [ ] **Step 1: Write the failing content test**

The test requires `AGENTS.md`, at least one `.rules` file, all 16 current `~/.agents/skills/*/SKILL.md` names, the Codex-local Loom skill, valid YAML frontmatter delimiters, and zero personal absolute paths or secret patterns.

Run:

```bash
bash tests/test_content.sh
```

Expected: fail because the assets are not present.

- [ ] **Step 2: Add the global profile and command rules**

Copy the current hand-authored content, replacing the title `Global Working Profile (po-chi)` with `Global Working Profile` and keeping command examples generic. Preserve restrictive decisions for destructive operations and inline `match` fixtures for `codex execpolicy check`.

- [ ] **Step 3: Add only hand-authored skills**

Add these current agent skills under `skills/agents/`:

```text
catchup design-agentic-systems feature-lifecycle git-state-audit graphify
handoff housekeeping latest linear narrate plan-symphony-ticket playwright
sentry ship simplify stitch-design
```

Add `record-nexrex-with-loom` under `skills/codex/`. Do not copy `.system`, `vendor_imports`, plugin caches, or plugin-provided skills.

- [ ] **Step 4: Normalize public paths without changing workflow meaning**

Replace personal absolute paths with `$HOME`, `~`, or repository-relative paths. Keep external public URLs and user-facing product names. If a skill requires a machine-local executable, document the prerequisite instead of embedding the current machine path.

- [ ] **Step 5: Validate rules and skills**

```bash
bash tests/test_content.sh
codex execpolicy check --pretty --rules rules/default.rules -- git reset --hard HEAD~1 | jq -e '.decision == "prompt"'
codex execpolicy check --pretty --rules rules/default.rules -- mkfs /dev/example | jq -e '.decision == "forbidden"'
bash scripts/check-secrets.sh --tracked
```

Expected: content test passes; the destructive rule fixtures produce the expected decisions.

- [ ] **Step 6: Commit**

```bash
git add AGENTS.md rules skills tests/test_content.sh
git commit -m "feat: add portable codex instructions and skills"
```

### Task 3: Add the safe linker

**Files:**
- Create: `setup.sh`
- Create: `tests/test_setup.sh`

**Interfaces:**
- Produces: `setup.sh [--check]` that links repository assets without replacing existing non-matching targets.

- [ ] **Step 1: Write failing setup tests**

In an isolated temporary `HOME`, assert first-run symlink creation, second-run idempotence, `--check` success, conflict failure, and absence of `config.toml` writes.

Run:

```bash
bash tests/test_setup.sh
```

Expected: fail because `setup.sh` does not exist.

- [ ] **Step 2: Implement setup**

Check `codex`, `git`, `uv`, `jq`, and `rg`; validate source content; then link:

```text
AGENTS.md                         -> ~/.codex/AGENTS.md
rules/default.rules               -> ~/.codex/rules/default.rules
skills/agents/<name>              -> ~/.agents/skills/<name>
skills/codex/record-nexrex-with-loom -> ~/.codex/skills/record-nexrex-with-loom
```

If the target is the correct symlink, report success. If any other target exists, report every conflict and exit non-zero without modifying conflicts. Never create or edit `~/.codex/config.toml`.

- [ ] **Step 3: Verify and commit**

```bash
bash tests/test_setup.sh
git add setup.sh tests/test_setup.sh
git commit -m "feat: add conflict-safe codex setup"
```

### Task 4: Document stable config, plugins, MCP scope, and updates

**Files:**
- Create: `config/config.example.toml`
- Create: `README.md`
- Create: `bin/update-all.sh`
- Create: `bin/verify.sh`
- Create: `tests/test_config.py`
- Create: `tests/test_update_all.sh`

**Interfaces:**
- Produces: a parseable, secret-free config example.
- Produces: an update script that refreshes Codex and configured plugins through supported CLI commands.
- Produces: `bin/verify.sh [--source-only]` as the complete local quality gate.

- [ ] **Step 1: Write failing config tests**

Use Python `tomllib` to assert the example parses, has no `model` key, contains no `[projects]` table, contains no literal authorization header, keeps Serena disabled with `--context=codex`, and configures PostHog nowhere globally.

Run:

```bash
uv run python -m unittest tests/test_config.py -v
```

Expected: fail because the example does not exist.

- [ ] **Step 2: Add the curated config example**

Include stable approval/sandbox/shell-environment defaults, OpenAI Docs MCP, Context7, Linear OAuth MCP, and disabled Serena. Use environment-variable authentication fields only. Explain project-specific configuration in README, not the global example.

- [ ] **Step 3: Add marketplace and plugin guidance**

Document supported CLI commands discovered from `codex plugin --help`, distinguish bundled/runtime-managed plugins from third-party marketplaces, list a last-verified date and Codex version, and show an `nr-platform`-style project-scoped PostHog example without a project identifier or token.

- [ ] **Step 4: Write and implement update-script tests**

Use a fake `codex` executable in `PATH` to record calls. Assert `update-all.sh` invokes the supported CLI update, marketplace refresh, installed-plugin refresh, source verification, and doctor; assert it never reads auth files or upgrades unrelated global tools.

- [ ] **Step 5: Implement the full verification gate**

`bin/verify.sh --source-only` runs all repository tests, JSON/TOML parsing, rule fixtures, shell syntax, Python compilation/Ruff when present, skill checks, Git diff checks, and tracked secret scanning. Without `--source-only`, it additionally runs `codex doctor --json` and requires `overallStatus == "ok"`.

- [ ] **Step 6: Verify and commit**

```bash
uv run python -m unittest tests/test_config.py -v
bash tests/test_update_all.sh
bash bin/verify.sh --source-only
git add README.md config bin tests/test_config.py tests/test_update_all.sh
git commit -m "docs: add maintainable plugin and MCP setup"
```

### Task 5: Validate installation and publish

**Files:**
- Modify: repository files only for confirmed in-scope defects found by final validation.

**Interfaces:**
- Consumes: Tasks 1–4 commits.
- Produces: a clean public `main` whose remote SHA matches local HEAD and whose setup succeeds in an isolated home.

- [ ] **Step 1: Run the isolated install twice**

```bash
tmp_home="$(mktemp -d)"
HOME="$tmp_home" PATH="$PATH" bash setup.sh
HOME="$tmp_home" PATH="$PATH" bash setup.sh
HOME="$tmp_home" PATH="$PATH" bash setup.sh --check
test ! -e "$tmp_home/.codex/config.toml"
```

Expected: first and second run pass, check mode passes, and no live config is created.

- [ ] **Step 2: Run the complete source and environment gate**

```bash
bash bin/verify.sh --source-only
TERM=xterm-256color bash bin/verify.sh
git diff --check
bash scripts/check-secrets.sh --tracked
```

Expected: every check passes and `codex doctor` reports `overallStatus: ok`.

- [ ] **Step 3: Review the final public diff and GitHub security state**

```bash
git status --short --branch
git log --oneline --decorate -10
gh api repos/flsteven87/codex-setup --jq '.security_and_analysis | {secret_scanning, secret_scanning_push_protection}'
```

Expected: only intentional commits exist; secret scanning and push protection are enabled.

- [ ] **Step 4: Push and verify remote parity**

```bash
git push origin main
test "$(git rev-parse HEAD)" = "$(git ls-remote origin refs/heads/main | cut -f1)"
git status --short --branch
```

Expected: remote and local SHA match; worktree is clean.
