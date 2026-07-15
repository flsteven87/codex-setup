#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_HOME="$(mktemp -d)"
trap 'rm -rf "$TMP_HOME"' EXIT

run_setup() {
  HOME="$TMP_HOME" PATH="$PATH" bash "$ROOT/setup.sh" "$@"
}

run_setup
run_setup
run_setup --check

test -L "$TMP_HOME/.codex/AGENTS.md"
test "$(readlink "$TMP_HOME/.codex/AGENTS.md")" = "$ROOT/AGENTS.md"
test -L "$TMP_HOME/.codex/rules/default.rules"
test -L "$TMP_HOME/.agents/skills/ship"
test -L "$TMP_HOME/.codex/skills/record-nexrex-with-loom"
test ! -e "$TMP_HOME/.codex/config.toml"

unlink "$TMP_HOME/.codex/AGENTS.md"
printf '%s\n' 'local instructions' >"$TMP_HOME/.codex/AGENTS.md"
if run_setup; then
  echo "setup unexpectedly replaced a conflicting file" >&2
  exit 1
fi
test "$(cat "$TMP_HOME/.codex/AGENTS.md")" = "local instructions"
test ! -e "$TMP_HOME/.codex/config.toml"

echo "setup tests: OK"
