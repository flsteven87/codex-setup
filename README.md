# Codex Setup

A small, reviewable reference setup for [OpenAI Codex](https://developers.openai.com/codex/). It combines a portable global baseline, Matt Pocock's upstream engineering skills, and a deliberately small set of personal skills without mirroring live Codex state.

> **Review before installing.** This repository intentionally excludes credentials, OAuth state, sessions, plugin caches, live configuration, and machine-specific paths. The installer never overwrites an existing file or foreign symlink.

Last verified: **2026-07-16** with **Codex CLI 0.144.4**, **skills CLI 1.5.17**, and Matt Pocock's skills at commit [`e9fcdf9`](https://github.com/mattpocock/skills/commit/e9fcdf95b402d360f90f1db8d776d5dd450f9234).

## Who this is for

Use this repository if you want a clean Codex setup with three clear ownership layers:

1. Codex owns its built-in system skills and plugins.
2. [Matt Pocock's upstream package](https://github.com/mattpocock/skills) owns the general engineering workflow and remains unmodified.
3. This repository owns only portable instructions, safety rules, and eleven focused personal skills.

The default installer creates only two baseline links. Personal skills are opt-in, and Matt's package is installed from its upstream repository rather than copied here.

Retired orchestration frameworks, replacement handoff implementations, and overlapping cleanup workflows are intentionally absent. Product-specific instructions and repository integrations belong in the repository that owns them.

## Prerequisites

The installer supports **macOS** and **Linux** with Bash. On Windows, use **WSL**; native PowerShell installation is not currently tested.

Install these before running setup:

- [Codex CLI](https://developers.openai.com/codex/cli/) with a working sign-in;
- Git;
- [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`); and
- Node.js with `npx` when installing Matt Pocock's skills.

The full repository verification command also requires `uv` and `jq`. Optional personal skills may have additional dependencies shown in the catalog.

## Preview-first quick start

Clone the repository into a stable location because installed baseline and personal components are symlinks back to this checkout:

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

It does not edit `~/.codex/config.toml`, authentication, MCP, plugin state, or third-party skills.

To install personal skills, name each one explicitly and reuse the same selection for checks or removal:

```bash
bash setup.sh --dry-run --skill catchup --skill ship
bash setup.sh --skill catchup --skill ship
bash setup.sh --check --skill catchup --skill ship
```

If a target already exists and is not the exact managed symlink, setup fails before changing anything. Review the existing target and merge or relocate it yourself; setup will not rename or replace it.

## Matt Pocock's engineering skills

Matt's package is an upstream dependency, not a fork in this repository. Install it with the author's recommended [`skills`](https://skills.sh/) workflow:

```bash
npx skills@latest add mattpocock/skills
```

Choose the global Codex installation and select the 22 core skills listed in [`config/matt-pocock-skills.txt`](config/matt-pocock-skills.txt), including `setup-matt-pocock-skills`. For a non-interactive installation of exactly that reviewed set from the current upstream branch:

```bash
rg -v '^(#|$)' config/matt-pocock-skills.txt \
  | xargs npx --yes skills@latest add mattpocock/skills \
      --global --agent codex --yes --skill
```

Do not substitute `--all` if you want this setup's reviewed scope. The upstream repository currently exposes additional general-purpose directories beyond the 22 core skills.

The catalog records the upstream commit used for this verification. The installer still reads the current upstream branch, so review upstream changes before reinstalling or updating:

```bash
git ls-remote https://github.com/mattpocock/skills.git HEAD
npx skills@latest update --global
```

Keep Matt's installed files unmodified. Run `$setup-matt-pocock-skills` once in each repository so the package can record its issue tracker, triage labels, and domain-document layout.

### Recommended workflow

Use the skills compositionally rather than treating them as one autonomous framework:

```text
$grill-with-docs → $to-spec → $to-tickets → fresh $implement per ticket → $ship
```

- `$implement` owns the spec or ticket, TDD, source changes, local validation, `$code-review`, and the final reviewed local commit.
- `$ship` starts from that reviewed commit and owns push, pull-request checks and feedback, merge, deployment, and post-deploy verification.
- Material product, architecture, security, or scope changes discovered during delivery return to `$implement`; `$ship` may make only a small, clearly bounded delivery fix.
- Matt's `$handoff` creates continuity notes. Personal `$catchup` is its read-only counterpart for rebuilding current context from repository evidence.

## Portable skill catalog

The component registry at [`config/components.tsv`](config/components.tsv) is the local installer's source of truth.

| Component | Default | Invocation | Purpose | Additional dependency |
|---|---:|---|---|---|
| `instructions` | Yes | Automatic | Portable global working agreements | None |
| `rules` | Yes | Automatic | Command escalation and denial policy | None |
| `catchup` | No | Explicit only | Rebuild context from repository evidence | None |
| `design-agentic-systems` | No | Task matched | Design and review agentic systems | None |
| `git-state-audit` | No | Explicit only | Produce a read-only git state and cleanup-risk report | GitHub CLI for GitHub-aware checks |
| `graphify` | No | Explicit only | Query and maintain persistent knowledge graphs | Graphify CLI |
| `housekeeping` | No | Task matched | Audit and tidy Codex artifacts | None |
| `latest` | No | Explicit only | Fast-forward main and reconcile established project memory | Git remotes for synchronization |
| `linear` | No | Task matched | Manage Linear work through its current MCP schema | Linear MCP |
| `narrate` | No | Explicit only | Create a concise plain-language visual brief | Visualization capability |
| `playwright` | No | Task matched | Automate a real browser from the terminal | Node.js and npm |
| `sentry` | No | Task matched | Inspect production errors read-only | Sentry CLI and authentication |
| `ship` | No | Explicit only | Deliver a reviewed commit after `$implement` | GitHub CLI and repository delivery tools |

`$catchup` and `$latest` are intentionally different. Use `$catchup` for a fast, read-only status rebuild. Use `$latest` when the active main checkout and persistent project memory must be synchronized with remotes, pull requests, tickets, changelogs, or sibling repositories.

Personal skills are linked to `~/.agents/skills/<name>`, the supported user-level location. Restart an open Codex task if a newly installed skill does not appear.

## Update

Update this reference checkout separately from Codex, Matt's skills, and plugins:

```bash
cd ~/.codex-setup
git pull --ff-only
bash setup.sh --check
```

Because links point into the checkout, a successful pull updates the installed baseline and selected personal skills immediately.

The following command is optional and changes the installed Codex CLI, Git marketplace snapshots, and currently enabled third-party plugins:

```bash
bash bin/update-all.sh
```

It leaves disabled plugins disabled and finishes with source checks plus `codex doctor`. Update Matt's package separately so its upstream diff can be reviewed on its own.

## Uninstall

Remove the baseline and the same selected personal skills:

```bash
bash setup.sh --uninstall --skill catchup --skill ship
```

To remove only the default baseline:

```bash
bash setup.sh --uninstall
```

Uninstall removes only symlinks that point to the corresponding source in this checkout. Real files, directories, foreign symlinks, Matt's package, live config, authentication, and plugin state are left untouched.

## Plugins and marketplaces

Plugins are optional and remain managed by Codex. Install them from their maintained marketplace rather than copying their code into this repository.

Inspect the current inventory before changing it:

```bash
codex plugin list
codex plugin marketplace list
```

Remove an unused third-party plugin or marketplace only after confirming that no active skill depends on it:

```bash
plugin_id="replace-with-plugin-id"
codex plugin remove "$plugin_id"

marketplace_name="replace-with-marketplace-name"
codex plugin marketplace remove "$marketplace_name"
```

OpenAI-bundled and primary-runtime plugins are managed by Codex. Install remote catalog plugins through the Codex plugin UI when their authorization should remain account-managed.

## MCP scope

Use global MCP only for capabilities useful across repositories. Put repository-specific servers in that trusted repository's `.codex/config.toml` and do not document them here.

[`config/config.example.toml`](config/config.example.toml) is a reference, not an install target. Copy only the sections you understand into live config.

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
- Last verified: Codex CLI 0.144.4 and skills CLI 1.5.17 on 2026-07-16.
- Matt core catalog: 22 unmodified upstream skills verified at `e9fcdf95b402d360f90f1db8d776d5dd450f9234`.
- Model selection is intentionally unset so Codex can use the account's current default.
- Marketplace and MCP commands are guidance, not pinned copies; review provider changes before updating commands or compatibility pins.

## Repository layout

```text
AGENTS.md                       Portable personal defaults
config/components.tsv           Installable local component registry
config/matt-pocock-skills.txt   Reviewed Matt core catalog and upstream commit
config/config.example.toml      Reviewed configuration examples
rules/default.rules             Command safety policy
skills/agents/                  Portable opt-in personal skills
scripts/check-secrets.sh        Public-repository secret scanner
setup.sh                        Previewable, conflict-safe local installer
bin/update-all.sh               Optional CLI and plugin refresh
bin/verify.sh                   Source and environment verification
```

## License

[MIT](LICENSE). Vendored personal skills that include their own license or notice retain those files in their directories.
