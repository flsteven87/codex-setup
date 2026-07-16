#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_ONLY=false

if [ "${1:-}" = "--source-only" ]; then
  SOURCE_ONLY=true
  shift
fi

if [ "$#" -ne 0 ]; then
  printf 'usage: %s [--source-only]\n' "$0" >&2
  exit 2
fi

cd "$ROOT"

printf 'Running source checks...\n'
bash tests/test_check_secrets.sh >/dev/null 2>&1
bash tests/test_content.sh >/dev/null
bash tests/test_readme.sh >/dev/null
bash tests/test_setup.sh >/dev/null 2>&1
uv run python -m unittest tests/test_config.py
(
  cd skills/agents/git-state-audit/scripts
  uv run python -m unittest test_git_state_audit.py
)

if [ "${CODEX_SETUP_SKIP_UPDATE_TEST:-0}" != "1" ]; then
  bash tests/test_update_all.sh >/dev/null
fi

while IFS= read -r -d '' script; do
  bash -n "$script"
done < <(find setup.sh bin scripts tests skills -type f -name '*.sh' -print0)

uv run --with ruff ruff check tests/test_config.py

codex execpolicy check --pretty --rules rules/default.rules -- git reset --hard HEAD~1 \
  | jq -e '.decision == "prompt"' >/dev/null
codex execpolicy check --pretty --rules rules/default.rules -- mkfs /dev/example \
  | jq -e '.decision == "forbidden"' >/dev/null

git diff --check
while IFS= read -r -d '' file; do
  scripts/check-secrets.sh "$ROOT/$file"
done < <(git ls-files --cached --others --exclude-standard -z)

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck setup.sh bin/*.sh scripts/*.sh tests/*.sh
fi

printf 'Source checks: OK\n'

if [ "$SOURCE_ONLY" = true ]; then
  exit 0
fi

printf 'Running Codex doctor...\n'
doctor_result="$(TERM="${TERM:-xterm-256color}" codex doctor --json)"
printf '%s' "$doctor_result" | jq -e '.overallStatus == "ok"' >/dev/null
printf 'Codex doctor: OK\n'
