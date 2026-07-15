# Codex Setup

A clean, portable reference setup for [OpenAI Codex](https://developers.openai.com/codex/): personal instructions, command safety rules, hand-authored skills, and maintainable plugin/MCP guidance.

> **Security notice:** review every tracked script and rule before installing it. This repository intentionally excludes credentials, OAuth state, sessions, plugin caches, live configuration, and machine-specific paths.

Last verified: **2026-07-15** with **Codex CLI 0.144.4**.

## Design

Codex stores both durable configuration and several gigabytes of runtime state under `~/.codex`. This repository therefore lives separately at `~/.codex-setup` and links only hand-authored assets into Codex's supported user locations.

```text
~/.codex-setup/
├── AGENTS.md                  # Portable personal development defaults
├── config/config.example.toml # Reviewed examples, never the live config
├── rules/default.rules        # Command escalation policy
├── skills/
│   ├── agents/                # Hand-authored cross-agent Codex skills
│   └── codex/                 # Codex-local personal skills
├── scripts/check-secrets.sh   # Public-repo secret and path scanner
├── setup.sh                   # Conflict-safe symlink installer
└── bin/
    ├── update-all.sh          # CLI + marketplace + enabled plugin refresh
    └── verify.sh              # Complete source and environment gate
```

Marketplace plugins and plugin-provided skills remain owned by Codex. They are installed through the supported CLI and are never copied into this repository.

## Quick start

### 1. Clone and review

```bash
git clone https://github.com/flsteven87/codex-setup.git ~/.codex-setup
cd ~/.codex-setup
bash bin/verify.sh --source-only
```

### 2. Install links

```bash
bash setup.sh
```

The installer is idempotent. It stops if a target already exists and is not the exact managed symlink; it never overwrites or renames existing files and never edits `~/.codex/config.toml`.

For an existing Codex installation, compare the tracked assets with your current files and adopt them deliberately. Use `bash setup.sh --check` after the links are in place.

### 3. Review configuration

[`config/config.example.toml`](config/config.example.toml) is a curated reference, not a file that setup copies automatically. Apply only the sections you want to your live `~/.codex/config.toml`.

The example deliberately leaves model selection unset so Codex can use the account's current default. It also keeps Serena disabled for normal work.

### 4. Verify the installation

```bash
bash bin/verify.sh
```

This runs source tests, rule fixtures, secret scanning, and `codex doctor` without printing authentication contents.

## Plugins and marketplaces

Use marketplace identifiers and installation commands rather than storing plugin code.

### Superpowers

```bash
codex plugin marketplace add obra/superpowers-marketplace
codex plugin add superpowers@superpowers-marketplace
```

### Paper desktop design tools

```bash
codex plugin marketplace add paper-design/agent-plugins
codex plugin add paper-desktop@paper
```

OpenAI-bundled and primary-runtime plugins are managed by the Codex application/runtime. Install remote catalog plugins such as GitHub or Gmail through the Codex plugin UI so their authorization remains account-managed.

To refresh configured Git marketplaces and currently enabled third-party plugins:

```bash
bash bin/update-all.sh
```

Disabled plugins are left untouched so an update cannot silently re-enable them. Re-add a disabled plugin explicitly when you intend to update and enable it.

## MCP scope

Use global MCP only for tools that are broadly useful across repositories. Put product- or account-specific servers in the trusted repository's `.codex/config.toml`.

### OAuth servers

```bash
codex mcp login linear
```

Never place an access token directly in TOML. For non-OAuth servers, use `bearer_token_env_var` or `env_http_headers`:

```toml
[mcp_servers.example]
url = "https://mcp.example.com/mcp"
bearer_token_env_var = "EXAMPLE_API_TOKEN"
```

### Project-scoped PostHog

As of Codex CLI 0.144.4, plugin enablement is user-level and cannot be reliably scoped by project config. To keep PostHog isolated to one repository, disable the global plugin and configure only its MCP server in that trusted project:

```toml
# <project>/.codex/config.toml
[mcp_servers.posthog]
url = "https://mcp.posthog.com/mcp"
http_headers = { "x-posthog-mcp-consumer" = "plugin" }
```

Authenticate through Codex's MCP UI or `codex mcp login posthog`. Do not commit OAuth state.

### Optional Serena

Modern Codex handles most repository navigation without Serena. The example keeps Serena available but disabled, uses its stable `1.5.3` release, selects `--context=codex`, and derives the active project from the current directory.

Enable it for a single run:

```bash
codex --config mcp_servers.serena.enabled=true
```

Review the current Serena release before changing the compatibility pin.

## Hook limitation

Codex supports lifecycle hooks, but the current public hook contract does not provide Claude Code's `PreToolUse` deny response. `PreToolUse` supports advisory `systemMessage` output; unsupported blocking fields are treated as hook failures and the tool call continues.

For that reason this repository does not install a misleading pre-write blocker. It uses Codex sandboxing and command rules for execution boundaries, plus local secret scanning and GitHub push protection for the public repository.

## Secret handling

- No live `config.toml`, auth file, OAuth cache, session, database, or plugin cache is tracked.
- Examples contain environment-variable names, never credential values.
- `scripts/check-secrets.sh --staged` scans a pending commit without echoing the suspected value.
- `scripts/check-secrets.sh --tracked` scans committed files.
- GitHub secret scanning and push protection are enabled on the public repository.

## Customization

- Edit `AGENTS.md` for personal defaults.
- Add focused hand-authored skills under the appropriate `skills/` subtree.
- Adjust `rules/default.rules`, then verify decisions with `codex execpolicy check`.
- Keep project-specific instructions in that project's `AGENTS.md` and project-specific MCP in `.codex/config.toml`.
- Keep third-party capabilities in their marketplace/plugin rather than copying their files here.

## License

[MIT](LICENSE)
