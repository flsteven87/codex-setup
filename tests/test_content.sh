#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

test -f "$ROOT/AGENTS.md"
test -f "$ROOT/rules/default.rules"

AGENT_SKILLS=(
  catchup
  design-agentic-systems
  feature-lifecycle
  git-state-audit
  graphify
  handoff
  housekeeping
  latest
  linear
  narrate
  plan-symphony-ticket
  playwright
  sentry
  ship
  simplify
  stitch-design
)

check_skill() {
  local file="$1"
  test -f "$file"
  test "$(sed -n '1p' "$file")" = "---"
  test "$(rg -n '^---$' "$file" | wc -l | tr -d ' ')" -ge 2
  rg -q '^name:[[:space:]]*[^[:space:]]+' "$file"
  rg -q '^description:' "$file"
}

for name in "${AGENT_SKILLS[@]}"; do
  check_skill "$ROOT/skills/agents/$name/SKILL.md"
done

check_skill "$ROOT/skills/codex/record-nexrex-with-loom/SKILL.md"

test "$(find "$ROOT/skills/agents" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')" = "${#AGENT_SKILLS[@]}"
! rg -n -F "$HOME" "$ROOT/AGENTS.md" "$ROOT/rules" "$ROOT/skills"
"$ROOT/scripts/check-secrets.sh" "$ROOT/AGENTS.md" "$ROOT/rules/default.rules"

repo_scoped_integration="post""hog"
if rg -n -i --hidden -g '!.git/**' "$repo_scoped_integration" "$ROOT"; then
  echo "repository-specific integration found in setup repo" >&2
  exit 1
fi

echo "content tests: OK"
