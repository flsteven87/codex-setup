#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="explicit"

case "${1:-}" in
  --staged|--tracked)
    MODE="${1#--}"
    shift
    ;;
esac

TOKEN_PATTERN='gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'
MAC_HOME_SEGMENT='Users'
LINUX_HOME_SEGMENT='home'
HOME_PATTERN="/${MAC_HOME_SEGMENT}/[^/[:space:]]+|/${LINUX_HOME_SEGMENT}/[^/[:space:]]+"

report() {
  printf 'sensitive content blocked: %s (%s)\n' "$1" "$2" >&2
}

credential_filename() {
  local path="$1"
  local name
  name="$(basename "$path")"
  case "$name" in
    .env|.env.*|auth.json|credentials|credentials.*|secrets|secrets.*|*.pem|*.key|*.p12|*.pfx|id_rsa|id_ed25519)
      return 0
      ;;
  esac
  return 1
}

scan_file() {
  local file="$1"
  [ -f "$file" ] || return 0

  if credential_filename "$file"; then
    report "$file" "credential filename"
    return 1
  fi

  if rg -q --text -e "$TOKEN_PATTERN" -- "$file"; then
    report "$file" "token or private-key pattern"
    return 1
  fi

  if rg -q --text -e "$HOME_PATTERN" -- "$file"; then
    report "$file" "personal absolute path"
    return 1
  fi

  return 0
}

status=0
if [ "$MODE" = "tracked" ]; then
  while IFS= read -r -d '' file; do
    scan_file "$ROOT/$file" || status=1
  done < <(git -C "$ROOT" ls-files -z)
elif [ "$MODE" = "staged" ]; then
  while IFS= read -r -d '' file; do
    scan_file "$ROOT/$file" || status=1
  done < <(git -C "$ROOT" diff --cached --name-only --diff-filter=ACMR -z)
else
  if [ "$#" -eq 0 ]; then
    printf 'usage: %s [--staged|--tracked|FILE ...]\n' "$0" >&2
    exit 2
  fi
  for file in "$@"; do
    scan_file "$file" || status=1
  done
fi

exit "$status"
