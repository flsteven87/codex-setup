#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECK="$ROOT/scripts/check-secrets.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

printf '%s\n' 'bearer_token_env_var = "EXAMPLE_API_TOKEN"' >"$TMP/safe.toml"
printf 'gh%s_%s\n' p "$(printf 'A%.0s' {1..24})" >"$TMP/token.txt"
printf '%s %s\n' '-----BEGIN' 'PRIVATE KEY-----' >"$TMP/key.pem"
printf '/%s/%s/project\n' Users example >"$TMP/path.txt"

"$CHECK" "$TMP/safe.toml"
! "$CHECK" "$TMP/token.txt"
! "$CHECK" "$TMP/key.pem"
! "$CHECK" "$TMP/path.txt"

echo "secret scanner tests: OK"
