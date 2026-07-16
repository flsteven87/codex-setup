#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
LOG="$TMP/codex.log"
FAKE_CODEX="$TMP/codex"

cat >"$FAKE_CODEX" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$*" >>"$CODEX_TEST_LOG"

case "$*" in
  "update")
    exit 0
    ;;
  "plugin marketplace upgrade --json")
    printf '%s\n' '{"selectedMarketplaces":["example"],"errors":[]}'
    ;;
  "plugin list --json")
    cat <<'JSON'
{"installed":[
  {"pluginId":"enabled-example@example-marketplace","enabled":true,"marketplaceSource":{"sourceType":"git"}},
  {"pluginId":"disabled-example@example-marketplace","enabled":false,"marketplaceSource":{"sourceType":"git"}},
  {"pluginId":"browser@openai-bundled","enabled":true,"marketplaceSource":{"sourceType":"local"}}
]}
JSON
    ;;
  "plugin add enabled-example@example-marketplace --json")
    printf '%s\n' '{"pluginId":"enabled-example@example-marketplace"}'
    ;;
  "doctor --json")
    printf '%s\n' '{"overallStatus":"ok"}'
    ;;
  *)
    printf 'unexpected fake codex command: %s\n' "$*" >&2
    exit 1
    ;;
esac
SH
chmod +x "$FAKE_CODEX"

CODEX_BIN="$FAKE_CODEX" CODEX_TEST_LOG="$LOG" bash "$ROOT/bin/update-all.sh"

rg -Fxq 'update' "$LOG"
rg -Fxq 'plugin marketplace upgrade --json' "$LOG"
rg -Fxq 'plugin list --json' "$LOG"
rg -Fxq 'plugin add enabled-example@example-marketplace --json' "$LOG"
rg -Fxq 'doctor --json' "$LOG"

if rg -q 'plugin add disabled-example@example-marketplace' "$LOG"; then
  echo "disabled plugin was unexpectedly re-added" >&2
  exit 1
fi

if rg -q 'plugin add browser@openai-bundled' "$LOG"; then
  echo "bundled plugin was unexpectedly re-added" >&2
  exit 1
fi

echo "update script tests: OK"
