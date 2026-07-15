# Codex Setup

A small, reviewable reference setup for [OpenAI Codex](https://developers.openai.com/codex/). It provides portable global instructions, command safety rules, opt-in skills, and installation guidance without mirroring live Codex state.

> **Review before installing.** This repository intentionally excludes credentials, OAuth state, sessions, plugin caches, live configuration, and machine-specific paths. The installer never overwrites an existing file or foreign symlink.

Last verified: **2026-07-15** with **Codex CLI 0.144.4**.

## Who this is for

Use this repository if you want a baseline you can read, fork, and customize rather than a preconfigured opinionated environment.

It includes:

- a two-file portable baseline installed by default;
- ten hand-authored, cross-repository skills installed only when named;
- a configuration example that is never copied automatically; and
- guidance for capabilities that should remain owned by plugins or MCP providers.

It does not include product-specific workflows, account authorization, repository configuration, or third-party plugin code. Keep those in the owning repository, provider, or marketplace.

## Prerequisites

The installer supports **macOS** and **Linux** with Bash. On Windows, use **WSL**; native PowerShell installation is not currently tested.

Install these before running setup:

- [Codex CLI](https://developers.openai.com/codex/cli/) and a working sign-in;
- Git; and
- [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`).

The full repository verification command also requires `uv` and `jq`. Optional skills may have additional dependencies shown in the catalog.

## Preview-first quick start

Clone the repository into a stable location because installed components are symlinks back to this checkout:

```bash
git clone https://github.com/flsteven87/codex-setup.git ~/.codex-setup
cd ~/.codex-setup
```

Review what is available and preview the default two links without changing files:

```bash
bash setup.sh --help
bash setup.sh --list
bash setup.sh --dry-run
```

Install only the portable baseline:

```bash
bash setup.sh
bash setup.sh --check
```

This links:

- `AGENTS.md` to `~/.codex/AGENTS.md`; and
- `rules/default.rules` to `~/.codex/rules/default.rules`.

It does not edit `~/.codex/config.toml`, authentication, MCP, or plugin state.

To install portable skills, name each one explicitly and reuse the same selection for checks or removal:

```bash
bash setup.sh --dry-run --skill catchup --skill simplify
bash setup.sh --skill catchup --skill simplify
bash setup.sh --check --skill catchup --skill simplify
```

If any target already exists and is not the exact managed symlink, setup fails before changing anything. Review the existing target and merge or relocate it yourself; setup will not rename or replace it.

## Portable skill catalog

The component registry at [`config/components.tsv`](config/components.tsv) is the installer's source of truth.

| Component | Default | Purpose | Additional dependency |
|---|---:|---|---|
| `instructions` | Yes | Portable global working agreements | None |
| `rules` | Yes | Command escalation and denial policy | None |
| `catchup` | No | Rebuild context and summarize current work | None |
| `design-agentic-systems` | No | Design and review agentic systems | None |
| `feature-lifecycle` | No | Run an explicit end-to-end feature workflow | Superpowers plugin |
| `git-state-audit` | No | Audit repository state and cleanup safety | GitHub CLI for GitHub-aware checks |
| `handoff` | No | Prepare concise continuity notes | None |
| `housekeeping` | No | Audit and tidy Codex artifacts | None |
| `latest` | No | Refresh repository and handoff context safely | Git remotes for synchronization |
| `narrate` | No | Create a plain-language visual brief | Visualization capability for rendered output |
| `ship` | No | Verify and deliver a completed change | Superpowers plugin and repository delivery tools |
| `simplify` | No | Reduce accidental complexity | None |

Skills are linked to `~/.agents/skills/<name>`, the supported user-level location. Codex discovers symlinked skills automatically; restart an open Codex task if a newly installed skill does not appear.

## Update

Update this reference checkout separately from Codex and its plugins:

```bash
cd ~/.codex-setup
git pull --ff-only
bash setup.sh --check
```

Because links point into the checkout, a successful pull updates installed baseline files and selected skills immediately.

The following command is optional and changes your installed Codex CLI, Git marketplace snapshots, and currently enabled third-party plugins:

```bash
bash bin/update-all.sh
```

It leaves disabled plugins disabled and finishes with source checks plus `codex doctor`.

## Uninstall

Remove the baseline and the same selected skills:

```bash
bash setup.sh --uninstall --skill catchup --skill simplify
```

To remove only the default baseline:

```bash
bash setup.sh --uninstall
```

Uninstall removes only symlinks that point to the corresponding source in this checkout. Real files, directories, foreign symlinks, live config, authentication, and plugin state are left untouched.

## Plugins and marketplaces

Plugins are optional. Install them from their maintained marketplace instead of copying their code into this repository.

### Superpowers

- **Provides:** structured design, planning, debugging, TDD, review, and delivery workflows.
- **Use when:** you want a more explicit engineering process or install the `feature-lifecycle` and `ship` skills from this repository.
- **Trust boundary:** plugin instructions can influence how Codex plans and executes repository work; review its source and marketplace before enabling it.

Install and verify:

```bash
codex plugin marketplace add obra/superpowers-marketplace
codex plugin add superpowers@superpowers-marketplace
codex plugin list
```

Remove it when no installed skill depends on it:

```bash
codex plugin remove superpowers@superpowers-marketplace
```

### Paper desktop design tools

- **Provides:** Paper design-to-code and code-to-design workflows.
- **Use when:** Paper is part of your design workflow; it is unnecessary for general coding.
- **Trust boundary:** the plugin can read project context and create or edit design assets through Paper's tools.

Install and verify:

```bash
codex plugin marketplace add paper-design/agent-plugins
codex plugin add paper-desktop@paper
codex plugin list
```

Remove:

```bash
codex plugin remove paper-desktop@paper
```

List configured marketplace names before removing an unused marketplace source:

```bash
codex plugin marketplace list
marketplace_name="replace-with-marketplace-name"
codex plugin marketplace remove "$marketplace_name"
```

OpenAI-bundled and primary-runtime plugins are managed by Codex. Install remote catalog plugins through the Codex plugin UI when their authorization should remain account-managed.

## MCP scope

Use global MCP only for capabilities useful across repositories. Put repository-specific servers in that trusted repository's `.codex/config.toml` and do not document them here.

[`config/config.example.toml`](config/config.example.toml) is a reference, not an install target. Copy only the sections you understand into your live config.

Prefer OAuth or environment-backed credentials over literal tokens:

```toml
[mcp_servers.example]
url = "https://mcp.example.com/mcp"
bearer_token_env_var = "EXAMPLE_API_TOKEN"
```

Use Codex to inspect, authenticate, and remove servers without exposing stored credentials:

```bash
codex mcp list
server_name="replace-with-server-name"
codex mcp login "$server_name"
codex mcp remove "$server_name"
```

Serena remains disabled in the example because modern Codex usually handles everyday repository navigation without it. Review its current release before changing the compatibility pin.

## Security

- No live `config.toml`, auth file, OAuth cache, session, database, or plugin cache is tracked.
- Examples contain environment-variable names, never credential values.
- `scripts/check-secrets.sh --staged` scans a pending commit without printing the suspected value.
- `scripts/check-secrets.sh --tracked` scans committed files.
- GitHub secret scanning and push protection are enabled on the public repository.

Run the repository gate before publishing changes:

```bash
bash bin/verify.sh --source-only
scripts/check-secrets.sh --staged
```

Run `bash bin/verify.sh` when you also want `codex doctor` to validate the active environment.

## Compatibility

- Installer: macOS and Linux Bash; WSL is the Windows path.
- Last verified: Codex CLI 0.144.4 on 2026-07-15.
- Model selection is intentionally unset so Codex can use the account's current default.
- Marketplace and MCP commands are guidance, not pinned copies; review provider changes before updating commands or compatibility pins.

## Repository layout

```text
AGENTS.md                  Portable personal defaults
config/components.tsv      Installable component registry
config/config.example.toml Reviewed configuration examples
rules/default.rules        Command safety policy
skills/agents/             Portable opt-in skills
scripts/check-secrets.sh   Public-repository secret scanner
setup.sh                   Previewable, conflict-safe installer
bin/update-all.sh          Optional CLI and plugin refresh
bin/verify.sh              Source and environment verification
```

## License

[MIT](LICENSE)
