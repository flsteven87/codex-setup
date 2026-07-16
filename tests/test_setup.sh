#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

run_setup() {
  local home="$1"
  shift
  HOME="$home" PATH="$PATH" bash "$ROOT/setup.sh" "$@"
}

HELP_HOME="$TMP/help"
run_setup "$HELP_HOME" --help >"$TMP/help.out"
rg -q -- '--dry-run' "$TMP/help.out"
rg -q -- '--uninstall' "$TMP/help.out"
test ! -e "$HELP_HOME/.codex"

LIST_HOME="$TMP/list"
run_setup "$LIST_HOME" --list >"$TMP/list.out"
rg -q '^Baseline' "$TMP/list.out"
rg -q 'ship' "$TMP/list.out"
test ! -e "$LIST_HOME/.codex"

DEFAULT_HOME="$TMP/default"
run_setup "$DEFAULT_HOME"
run_setup "$DEFAULT_HOME"
run_setup "$DEFAULT_HOME" --check
test -L "$DEFAULT_HOME/.codex/AGENTS.md"
test "$(readlink "$DEFAULT_HOME/.codex/AGENTS.md")" = "$ROOT/AGENTS.md"
test -L "$DEFAULT_HOME/.codex/rules/default.rules"
test -L "$DEFAULT_HOME/.codex/agents/explorer.toml"
test "$(readlink "$DEFAULT_HOME/.codex/agents/explorer.toml")" = "$ROOT/agents/explorer.toml"
test ! -e "$DEFAULT_HOME/.agents/skills"
test ! -e "$DEFAULT_HOME/.codex/config.toml"

SELECTED_HOME="$TMP/selected"
run_setup "$SELECTED_HOME" --skill ship --skill graphify
run_setup "$SELECTED_HOME" --check --skill ship --skill graphify
test -L "$SELECTED_HOME/.agents/skills/ship"
test -L "$SELECTED_HOME/.agents/skills/graphify"
test ! -e "$SELECTED_HOME/.agents/skills/catchup"

UNKNOWN_HOME="$TMP/unknown"
if run_setup "$UNKNOWN_HOME" --skill unknown-skill >"$TMP/unknown.out" 2>&1; then
  echo "unknown skill unexpectedly succeeded" >&2
  exit 1
fi
test ! -e "$UNKNOWN_HOME/.codex"

DRY_HOME="$TMP/dry"
run_setup "$DRY_HOME" --dry-run --skill catchup >"$TMP/dry.out"
rg -q 'AGENTS.md' "$TMP/dry.out"
rg -q 'catchup' "$TMP/dry.out"
test ! -e "$DRY_HOME/.codex"
test ! -e "$DRY_HOME/.agents"

MISSING_HOME="$TMP/missing"
if run_setup "$MISSING_HOME" --check >"$TMP/missing.out" 2>&1; then
  echo "check unexpectedly accepted a missing installation" >&2
  exit 1
fi

UNINSTALL_HOME="$TMP/uninstall"
run_setup "$UNINSTALL_HOME" --skill ship
run_setup "$UNINSTALL_HOME" --uninstall --skill ship
test ! -e "$UNINSTALL_HOME/.codex/AGENTS.md"
test ! -e "$UNINSTALL_HOME/.codex/rules/default.rules"
test ! -e "$UNINSTALL_HOME/.codex/agents/explorer.toml"
test ! -e "$UNINSTALL_HOME/.agents/skills/ship"
run_setup "$UNINSTALL_HOME" --uninstall --skill ship

FOREIGN_HOME="$TMP/foreign"
run_setup "$FOREIGN_HOME"
unlink "$FOREIGN_HOME/.codex/AGENTS.md"
ln -s "$TMP/foreign-source" "$FOREIGN_HOME/.codex/AGENTS.md"
if run_setup "$FOREIGN_HOME" --uninstall >"$TMP/foreign.out" 2>&1; then
  echo "uninstall unexpectedly removed a foreign symlink" >&2
  exit 1
fi
test "$(readlink "$FOREIGN_HOME/.codex/AGENTS.md")" = "$TMP/foreign-source"
test -L "$FOREIGN_HOME/.codex/rules/default.rules"

CONFLICT_HOME="$TMP/conflict"
mkdir -p "$CONFLICT_HOME/.codex"
printf '%s\n' 'local instructions' >"$CONFLICT_HOME/.codex/AGENTS.md"
if run_setup "$CONFLICT_HOME" >"$TMP/conflict.out" 2>&1; then
  echo "setup unexpectedly replaced a conflicting file" >&2
  exit 1
fi
test "$(cat "$CONFLICT_HOME/.codex/AGENTS.md")" = "local instructions"
test ! -e "$CONFLICT_HOME/.codex/rules/default.rules"

echo "setup tests: OK"
