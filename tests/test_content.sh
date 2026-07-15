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
  handoff
  housekeeping
  latest
  narrate
  ship
  simplify
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

test "$(find "$ROOT/skills/agents" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')" = "${#AGENT_SKILLS[@]}"
test ! -d "$ROOT/skills/codex"

REGISTRY_SKILLS=()
while IFS='|' read -r id kind _rest; do
  if [ "$kind" = skill ]; then
    REGISTRY_SKILLS+=("$id")
  fi
done <"$ROOT/config/components.tsv"

test "${#REGISTRY_SKILLS[@]}" = "${#AGENT_SKILLS[@]}"
for index in "${!AGENT_SKILLS[@]}"; do
  test "${REGISTRY_SKILLS[$index]}" = "${AGENT_SKILLS[$index]}"
done

! rg -n -F "$HOME" "$ROOT/AGENTS.md" "$ROOT/rules" "$ROOT/skills"
"$ROOT/scripts/check-secrets.sh" "$ROOT/AGENTS.md" "$ROOT/rules/default.rules"

for repo_scoped_term in "post""hog" "nex""rex" "ai-commerce""-ready"; do
  if rg -n -i --hidden -g '!.git/**' "$repo_scoped_term" "$ROOT"; then
    echo "repository-specific content found in setup repo" >&2
    exit 1
  fi
done

echo "content tests: OK"
