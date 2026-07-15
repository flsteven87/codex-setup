#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_BIN="${CODEX_BIN:-codex}"

printf 'Updating Codex CLI...\n'
"$CODEX_BIN" update

printf '\nRefreshing Git marketplaces...\n'
marketplace_result="$("$CODEX_BIN" plugin marketplace upgrade --json)"
printf '%s' "$marketplace_result" | jq -e '(.errors // []) | length == 0' >/dev/null

printf '\nRefreshing enabled third-party plugins...\n'
plugin_inventory="$("$CODEX_BIN" plugin list --json)"
while IFS= read -r plugin_id; do
  [ -n "$plugin_id" ] || continue
  "$CODEX_BIN" plugin add "$plugin_id" --json >/dev/null
  printf '  updated %s\n' "$plugin_id"
done < <(
  printf '%s' "$plugin_inventory" | jq -r '
    .installed[]
    | select(.enabled == true)
    | select(.marketplaceSource.sourceType == "git")
    | .pluginId
  '
)

printf '\nVerifying setup source...\n'
CODEX_SETUP_SKIP_UPDATE_TEST=1 bash "$ROOT/bin/verify.sh" --source-only

printf '\nRunning Codex doctor...\n'
doctor_result="$("$CODEX_BIN" doctor --json)"
printf '%s' "$doctor_result" | jq -e '.overallStatus == "ok"' >/dev/null

printf '\nUpdate complete. Restart open Codex tasks to load refreshed plugins.\n'
printf 'Disabled plugins were intentionally left unchanged.\n'
