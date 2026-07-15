#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
README="$ROOT/README.md"

for heading in \
  '## Who this is for' \
  '## Prerequisites' \
  '## Preview-first quick start' \
  '## Portable skill catalog' \
  '## Update' \
  '## Uninstall' \
  '## Plugins and marketplaces' \
  '## MCP scope' \
  '## Compatibility'; do
  rg -Fxq "$heading" "$README"
done

for command in \
  'bash setup.sh --list' \
  'bash setup.sh --dry-run' \
  'bash setup.sh --skill' \
  'bash setup.sh --uninstall' \
  'codex plugin list' \
  'codex plugin remove' \
  'codex mcp list' \
  'codex mcp remove'; do
  rg -Fq "$command" "$README"
done

while IFS='|' read -r id _rest; do
  [ -n "$id" ] || continue
  rg -Fq "\`$id\`" "$README"
done <"$ROOT/config/components.tsv"

rg -Fq 'macOS' "$README"
rg -Fq 'Linux' "$README"
rg -Fq 'WSL' "$README"

echo "README tests: OK"
