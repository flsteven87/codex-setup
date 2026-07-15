#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_ONLY=false

if [ "${1:-}" = "--check" ]; then
  CHECK_ONLY=true
  shift
fi

if [ "$#" -ne 0 ]; then
  printf 'usage: %s [--check]\n' "$0" >&2
  exit 2
fi

pass() { printf '  OK  %s\n' "$1"; }
fail() { printf '  ERR %s\n' "$1" >&2; }

printf 'Codex Setup\n\n'
printf 'Checking prerequisites...\n'
missing=0
for command_name in codex git uv jq rg; do
  if command -v "$command_name" >/dev/null 2>&1; then
    pass "$command_name"
  else
    fail "$command_name is required"
    missing=1
  fi
done
[ "$missing" -eq 0 ] || exit 1

printf '\nValidating source...\n'
bash "$ROOT/tests/test_content.sh" >/dev/null
bash "$ROOT/scripts/check-secrets.sh" --tracked
pass "repository content"

mappings=(
  "$ROOT/AGENTS.md|$HOME/.codex/AGENTS.md"
  "$ROOT/rules/default.rules|$HOME/.codex/rules/default.rules"
)

for source in "$ROOT"/skills/agents/*; do
  [ -d "$source" ] || continue
  mappings+=("$source|$HOME/.agents/skills/$(basename "$source")")
done

mappings+=(
  "$ROOT/skills/codex/record-nexrex-with-loom|$HOME/.codex/skills/record-nexrex-with-loom"
)

printf '\nChecking targets...\n'
issues=0
for mapping in "${mappings[@]}"; do
  source="${mapping%%|*}"
  target="${mapping#*|}"

  if [ -L "$target" ] && [ "$(readlink "$target")" = "$source" ]; then
    pass "$target"
  elif [ -e "$target" ] || [ -L "$target" ]; then
    fail "$target already exists and is not the managed symlink"
    issues=1
  elif [ "$CHECK_ONLY" = true ]; then
    fail "$target is not installed"
    issues=1
  fi
done

[ "$issues" -eq 0 ] || exit 1

if [ "$CHECK_ONLY" = true ]; then
  printf '\nSetup check complete.\n'
  exit 0
fi

printf '\nInstalling links...\n'
for mapping in "${mappings[@]}"; do
  source="${mapping%%|*}"
  target="${mapping#*|}"

  if [ -L "$target" ] && [ "$(readlink "$target")" = "$source" ]; then
    continue
  fi

  mkdir -p "$(dirname "$target")"
  ln -s "$source" "$target"
  pass "$target"
done

printf '\nSetup complete. Live config and authentication were not modified.\n'
printf 'Review config/config.example.toml and README.md for optional setup.\n'
