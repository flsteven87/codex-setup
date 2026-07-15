# User-Facing Reference Setup Design

## Goal

Turn `codex-setup` into a public, reference-first Codex starter that a stranger can understand, preview, install selectively, verify, update, and uninstall without adopting the maintainer's product-specific environment.

## Audience and support boundary

The primary audience is a Codex CLI user who is comfortable reviewing shell scripts and wants a safe baseline they can fork or copy. The supported installer environments are macOS and Linux with Bash. Windows users should use WSL; native Windows installation is not claimed until it has a dedicated implementation and test path.

The repository is both:

- a readable reference for global instructions, command rules, portable skills, plugin selection, MCP scope, and secret handling; and
- an optional installer for a deliberately small user-level baseline.

It is not a complete mirror of `~/.codex`, a product configuration repository, a plugin cache, or a place for organization-specific workflows.

## Content boundary

Every tracked capability belongs to exactly one category:

1. **Portable baseline** — global instructions and command rules that are safe to review and reuse across repositories.
2. **Portable optional skill** — a hand-authored cross-repository workflow that is installed only when the user names it.
3. **External integration** — a plugin, curated skill, MCP server, CLI, or account-backed capability that is documented through current installation guidance and is not vendored here.
4. **Repository-specific workflow** — product, customer, organization, ticket-project, or deployment-specific behavior that belongs in the owning repository and is forbidden from this public setup.

The portable optional skill set is:

- `catchup`
- `design-agentic-systems`
- `feature-lifecycle`
- `git-state-audit`
- `handoff`
- `housekeeping`
- `latest`
- `narrate`
- `ship`
- `simplify`

Skills whose behavior or tool schema is owned by an external product are removed from the tracked skill tree. The README may describe how to install an official or marketplace-owned replacement, but it must not copy that implementation. Existing organization-specific skills are removed from the public repository and must not remain as examples.

## Installer interface

Running `bash setup.sh` installs only the portable baseline:

- `AGENTS.md` to `~/.codex/AGENTS.md`
- `rules/default.rules` to `~/.codex/rules/default.rules`

Portable skills are explicit and repeatable:

```bash
bash setup.sh --skill catchup --skill simplify
```

The supported commands are:

```text
bash setup.sh --help
bash setup.sh --list
bash setup.sh --dry-run [--skill NAME ...]
bash setup.sh [--skill NAME ...]
bash setup.sh --check [--skill NAME ...]
bash setup.sh --uninstall [--skill NAME ...]
```

Behavioral rules:

- `--help` prints usage and exits successfully without requiring prerequisites.
- `--list` prints the baseline and portable skill catalog without changing files.
- `--dry-run` validates arguments and prints the exact planned links without changing files.
- Repeating `--skill` selects only named portable skills; unknown names fail before any mutation.
- Installation remains conflict-safe and idempotent. It never overwrites a file or a symlink managed by another source.
- `--check` verifies only the baseline plus the explicitly selected skills.
- `--uninstall` removes only exact symlinks whose targets are the corresponding files in this checkout. It refuses real files, directories, and foreign symlinks.
- Live config, authentication, plugin state, and repository-specific configuration are never modified.

The component registry has one source of truth consumed by the installer and tests. It stores component name, type, source path, target path, description, and optional dependency note. The README catalog is checked against that registry so documentation cannot silently omit an installable component.

## User-facing documentation

The README follows a stranger's decision path:

1. What this repository is and is not.
2. Supported platforms and prerequisites, with links to current Codex installation documentation.
3. What the default installer changes.
4. Preview-first quick start.
5. Selective skill installation.
6. Existing-installation conflict handling.
7. Verification, update, and uninstall.
8. Portable skill catalog with purpose, dependencies, and mutation level.
9. Optional plugin and MCP guidance.
10. Security model, compatibility policy, and license.

Plugin guidance is decision-oriented rather than a command dump. Each documented plugin includes:

- what it provides;
- when to install it;
- its trust or authorization boundary;
- the supported installation path;
- how to verify it is enabled; and
- how to remove or disable it.

The repository does not duplicate plugin code or account authorization. It links to the provider or official marketplace source and records the date and Codex version on which the guidance was verified.

## Compatibility and release policy

The README records the most recently verified Codex CLI version and date. A compatibility section distinguishes:

- supported installer platforms;
- required command-line prerequisites;
- optional dependencies used only by selected skills; and
- unverified surfaces.

After the redesign passes the full verification gate, publish a tagged baseline release. Later compatibility changes update the verification stamp and release notes rather than silently redefining an existing tag.

The GitHub repository metadata should include focused discovery topics for Codex setup, agent skills, dotfiles, and developer tooling. No homepage is required unless a separate documentation site exists.

## Migration safety

Removing tracked skills must not create broken links in the maintainer's active Codex environment. Before deleting a tracked skill, inspect its installed user-level path:

- If it is an exact symlink into this checkout, migrate or uninstall that link before deleting the source.
- If it is an independent local directory, leave it untouched.
- Repository-specific skills move to the owning repository's `.agents/skills` only when that repository is available and the move can be verified.
- The public repository must not retain a fallback copy, example, or migration note containing product-specific implementation details.

The current preflight found the affected active user-level skills as independent local directories, not symlinks into this checkout. Removing their public copies therefore does not delete or break the maintainer's active local copies.

## Testing strategy

Installer behavior is developed test-first with isolated temporary homes. Tests cover:

- help and list are read-only and succeed;
- default installation links only the baseline;
- selected skills install only when named;
- unknown skills fail before mutation;
- dry-run makes no filesystem changes;
- check reports missing and correctly installed selections;
- uninstall removes exact managed links and refuses foreign targets;
- repeated install and uninstall are idempotent;
- component registry entries match the tracked portable skills;
- README catalogs every installable component; and
- forbidden repository-specific content and vendored external integration skills are absent.

The existing secret scanner, shell syntax checks, ShellCheck when available, Python tests, rule fixtures, and `codex doctor` remain part of the full verification gate.

## Delivery

Implementation is delivered in reviewable commits: installer and tests, content-boundary cleanup, user-facing documentation, then release metadata. The final push occurs only after the complete verification gate passes and the working tree contains no secret-like values or broken managed links.
