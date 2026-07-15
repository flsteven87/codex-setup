# Codex Setup Design

## Context

`claude-code-setup` is a public reference repository for a clean, portable
Claude Code environment. The Codex equivalent must provide the same kind of
reference implementation without coupling the two environments or copying
machine-generated state into source control.

The current Codex home contains several gigabytes of sessions, caches, plugin
artifacts, OAuth state, and application data. It is therefore not suitable as
a Git repository or as the source for a public snapshot.

## Goals

- Publish `flsteven87/codex-setup` as a standalone public reference setup.
- Document a current, maintainable Codex configuration using native Codex
  concepts: `AGENTS.md`, skills, rules, plugins, MCP, project config, and the
  documented limitations of user hooks.
- Track only hand-authored, Codex-specific assets.
- Make setup safe to inspect and copy without overwriting an existing Codex
  installation.
- Keep third-party plugins and marketplaces updateable through their supported
  installation mechanisms rather than vendoring their contents.
- Prevent credentials, tokens, API keys, local paths, and runtime state from
  entering Git history.

## Non-goals

- The repository will not mirror or depend on `claude-code-setup`.
- It will not synchronize skills or instructions between Claude and Codex.
- It will not reproduce the current machine byte-for-byte.
- It will not vendor marketplace plugins, plugin-provided skills, MCP packages,
  or generated caches.
- It will not automatically overwrite `~/.codex/config.toml`.
- It will not publish project trust entries, account state, Fugu configuration,
  provider credentials, or project-specific MCP configuration.

## Repository Layout

```text
codex-setup/
├── AGENTS.md
├── README.md
├── LICENSE
├── config/
│   └── config.example.toml
├── rules/
│   └── default.rules
├── skills/
│   └── <hand-authored Codex skills>
├── bin/
│   ├── update-all.sh
│   └── verify.sh
├── scripts/
│   └── check-secrets.sh
└── setup.sh
```

Plugin caches, plugin-delivered skills, sessions, logs, databases, shell
snapshots, generated media, authentication files, and application state are
excluded.

## Ownership Boundaries

### Tracked

- A portable global `AGENTS.md` containing personal development defaults.
- Hand-authored Codex skills that currently live outside plugins.
- Codex-native command rules maintained by this repository.
- Hook guidance that does not claim unsupported blocking behavior.
- A curated `config.example.toml` built from scratch.
- Bootstrap, update, verification, and secret-scanning scripts.
- Installation and maintenance documentation.

### Referenced, not tracked

- Marketplace and plugin identifiers with official installation commands.
- MCP package names, URLs, OAuth commands, and recommended scope.
- Stable version pins only where reproducibility or known compatibility issues
  justify them, together with an explicit update path.

### Local only

- `~/.codex/config.toml` and profile files in active use.
- `auth.json`, OAuth caches, tokens, environment files, and private keys.
- Project trust entries and absolute local project paths.
- Sessions, logs, SQLite databases, memories, attachments, generated images,
  shell snapshots, and plugin caches.
- App-generated UI state, Fugu state, and local model-provider configuration.
- Project-specific MCP servers such as the PostHog server in `nr-platform`.

## Configuration Strategy

`config/config.example.toml` is documentation-quality configuration, not a
managed copy of the user's live file. It will:

- Prefer stable Codex keys and omit short-lived experimental feature flags.
- Avoid pinning a model so Codex can follow the account's current default.
- Demonstrate safe approval, sandbox, shell environment, and MCP patterns.
- Use `bearer_token_env_var`, `env_http_headers`, or OAuth for authentication.
- Show global MCP only when it is broadly useful across projects.
- Put project-specific MCP examples under `.codex/config.toml` documentation.
- Keep Serena optional and disabled by default, with its Codex context and
  project-from-current-directory behavior documented.
- Never contain a real token, project reference, account identifier, username,
  home path, or organization-specific endpoint.

The setup script will never replace an existing live config. On a fresh
installation it may offer the example as a starting point, but applying it is
an explicit user action.

## Plugin and Marketplace Strategy

The repository stores instructions and identifiers, not plugin contents.

- README lists the supported `codex plugin marketplace` and `codex plugin add`
  commands.
- Bundled or runtime-managed plugins are described as such instead of copied.
- Plugin caches and plugin-provided skills remain owned by Codex.
- The update script refreshes configured marketplaces and installed plugins
  through the Codex CLI.
- Documentation records a last-verified date and tested version, but avoids
  turning that record into a permanent runtime pin.
- Local-only plugins are excluded unless their source is publicly reusable.

## Installation Flow

The reference clone location is `~/.codex-setup`.

1. Check required commands such as Codex, Git, `uv`, `jq`, and `rg`.
2. Validate the repository before installing links.
3. Link the tracked global instructions, rules, and custom skills into
   Codex's supported user locations.
4. Stop on any existing non-matching file or directory. Do not overwrite,
   rename, or delete it.
5. Leave live config and authentication untouched.
6. Print the explicit marketplace, plugin, MCP, and OAuth commands that remain
   user-controlled.
7. Run verification and report the resulting state.

The setup must be idempotent: running it again with the correct links in place
is a successful no-op.

## Update Flow

`bin/update-all.sh` will:

1. Update the Codex CLI through its supported update path.
2. Refresh configured plugin marketplaces.
3. Update installed plugins without vendoring them.
4. Re-run repository verification.
5. Run `codex doctor` and clearly distinguish local config failures from
   optional authentication or network issues.

It will not broadly upgrade unrelated global Python or Node tools.

## Secret and Privacy Controls

The public repository uses defense in depth:

- `.gitignore` blocks authentication files, environment files, credentials,
  private keys, certificates, runtime state, caches, and databases.
- Examples use placeholder names and environment-variable references only.
- A local staged-file check rejects high-confidence provider token formats,
  private-key markers, credential filenames, and personal absolute paths.
- A full tracked-files scan runs before every release.
- GitHub secret scanning and push protection are enabled when supported.
- Setup and verification scripts never read or print the contents of live auth
  files or secret-bearing environment variables.
- The initial commit and every shipped diff receive a manual secret review in
  addition to automated checks.

If a suspected secret is found, release stops. The value is never echoed in
full in diagnostic output.

## Validation

The repository's verification gate covers:

- Shell syntax and ShellCheck when available.
- Python syntax and focused Ruff checks for repository scripts.
- TOML and JSON parsing.
- Codex rule parsing with `codex execpolicy check` fixtures.
- Skill frontmatter and required file structure.
- Symlink targets and setup idempotence using an isolated temporary home.
- Secret, credential-file, and personal-path scans.
- `codex doctor` on the real installation after links are applied.

No test may need production credentials or print current environment values.

## Claude Setup Reconciliation

The existing `~/.claude` working tree is handled independently before Codex
implementation is shipped.

- Keep coherent hand-authored hooks, the routed deep-research workflow, the
  docs-cleanup skill, and their matching settings/documentation updates.
- Add `teams/` to runtime ignores; do not commit team inbox artifacts.
- Reconcile README and setup instructions with the actual plugin inventory.
- Run syntax, configuration, path-portability, and secret checks.
- Commit and push only the intended Claude-specific files to `main`.

No Claude file becomes a runtime dependency of `codex-setup`.

## Delivery Sequence

1. Commit this approved design as the initial `codex-setup` commit.
2. Reconcile, verify, commit, and push the pending Claude setup changes.
3. Create a detailed Codex implementation plan from this design.
4. Implement the Codex repository in reviewable slices.
5. Verify install behavior in an isolated home and against the current local
   Codex installation without overwriting live config.
6. Run secret scans, commit, and push the public Codex repository.

The terminal state is two independent, clean public repositories whose setup
instructions can be copied and maintained without storing third-party plugin
code or machine-specific state.
