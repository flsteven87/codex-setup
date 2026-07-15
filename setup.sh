#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="$ROOT/config/components.tsv"
ACTION="install"
DRY_RUN=false
SHOW_HELP=false
SHOW_LIST=false
ACTION_SET=false
SELECTED_SKILLS=()
SELECTED_SKILL_COUNT=0

usage() {
  cat <<'EOF'
Usage:
  bash setup.sh --help
  bash setup.sh --list
  bash setup.sh --dry-run [--skill NAME ...]
  bash setup.sh [--skill NAME ...]
  bash setup.sh --check [--skill NAME ...]
  bash setup.sh --uninstall [--skill NAME ...]

With no --skill option, setup manages only the portable baseline.
Repeat --skill to opt into individual portable skills.
EOF
}

fail() { printf '  ERR %s\n' "$1" >&2; }
pass() { printf '  OK  %s\n' "$1"; }

set_action() {
  local requested="$1"
  if [ "$ACTION_SET" = true ]; then
    fail "choose only one of --check or --uninstall"
    exit 2
  fi
  ACTION="$requested"
  ACTION_SET=true
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --help|-h)
      SHOW_HELP=true
      shift
      ;;
    --list)
      SHOW_LIST=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --check)
      set_action check
      shift
      ;;
    --uninstall)
      set_action uninstall
      shift
      ;;
    --skill)
      if [ "$#" -lt 2 ] || [[ "$2" == --* ]]; then
        fail "--skill requires a name"
        exit 2
      fi
      SELECTED_SKILLS+=("$2")
      SELECTED_SKILL_COUNT=$((SELECTED_SKILL_COUNT + 1))
      shift 2
      ;;
    *)
      fail "unknown option: $1"
      usage >&2
      exit 2
      ;;
  esac
done

if [ "$SHOW_HELP" = true ]; then
  if [ "$SHOW_LIST" = true ] || [ "$DRY_RUN" = true ] || [ "$ACTION_SET" = true ] || [ "$SELECTED_SKILL_COUNT" -gt 0 ]; then
    fail "--help cannot be combined with other options"
    exit 2
  fi
  usage
  exit 0
fi

if [ "$DRY_RUN" = true ] && [ "$ACTION" != install ]; then
  fail "--dry-run is only available for installation"
  exit 2
fi

if [ ! -f "$REGISTRY" ]; then
  fail "component registry is missing: $REGISTRY"
  exit 1
fi

COMPONENT_IDS=()
COMPONENT_KINDS=()
COMPONENT_SOURCES=()
COMPONENT_TARGETS=()
COMPONENT_DESCRIPTIONS=()
COMPONENT_DEPENDENCIES=()

while IFS='|' read -r id kind source target description dependencies; do
  [ -n "$id" ] || continue
  if [ -z "$kind" ] || [ -z "$source" ] || [ -z "$target" ] || [ -z "$description" ] || [ -z "$dependencies" ]; then
    fail "invalid component registry row: $id"
    exit 1
  fi
  COMPONENT_IDS+=("$id")
  COMPONENT_KINDS+=("$kind")
  COMPONENT_SOURCES+=("$source")
  COMPONENT_TARGETS+=("$target")
  COMPONENT_DESCRIPTIONS+=("$description")
  COMPONENT_DEPENDENCIES+=("$dependencies")
done <"$REGISTRY"

if [ "$SHOW_LIST" = true ]; then
  if [ "$DRY_RUN" = true ] || [ "$ACTION_SET" = true ] || [ "$SELECTED_SKILL_COUNT" -gt 0 ]; then
    fail "--list cannot be combined with other options"
    exit 2
  fi
  printf 'Baseline (installed by default)\n'
  for index in "${!COMPONENT_IDS[@]}"; do
    if [ "${COMPONENT_KINDS[$index]}" = baseline ]; then
      printf '  %-24s %s\n' "${COMPONENT_IDS[$index]}" "${COMPONENT_DESCRIPTIONS[$index]}"
    fi
  done
  printf '\nPortable skills (opt-in with --skill NAME)\n'
  for index in "${!COMPONENT_IDS[@]}"; do
    if [ "${COMPONENT_KINDS[$index]}" = skill ]; then
      printf '  %-24s %s [dependencies: %s]\n' \
        "${COMPONENT_IDS[$index]}" \
        "${COMPONENT_DESCRIPTIONS[$index]}" \
        "${COMPONENT_DEPENDENCIES[$index]}"
    fi
  done
  exit 0
fi

SELECTED_IDS=()
for index in "${!COMPONENT_IDS[@]}"; do
  if [ "${COMPONENT_KINDS[$index]}" = baseline ]; then
    SELECTED_IDS+=("${COMPONENT_IDS[$index]}")
  fi
done

if [ "$SELECTED_SKILL_COUNT" -gt 0 ]; then
  for requested_skill in "${SELECTED_SKILLS[@]}"; do
    found=false
    already_selected=false
    for index in "${!COMPONENT_IDS[@]}"; do
      if [ "${COMPONENT_KINDS[$index]}" = skill ] && [ "${COMPONENT_IDS[$index]}" = "$requested_skill" ]; then
        found=true
        for selected_id in "${SELECTED_IDS[@]}"; do
          if [ "$selected_id" = "$requested_skill" ]; then
            already_selected=true
          fi
        done
        if [ "$already_selected" = false ]; then
          SELECTED_IDS+=("$requested_skill")
        fi
        break
      fi
    done
    if [ "$found" = false ]; then
      fail "unknown portable skill: $requested_skill"
      printf 'Run `bash setup.sh --list` to see available skills.\n' >&2
      exit 2
    fi
  done
fi

SELECTED_SOURCES=()
SELECTED_TARGETS=()
for selected_id in "${SELECTED_IDS[@]}"; do
  for index in "${!COMPONENT_IDS[@]}"; do
    if [ "${COMPONENT_IDS[$index]}" = "$selected_id" ]; then
      SELECTED_SOURCES+=("$ROOT/${COMPONENT_SOURCES[$index]}")
      SELECTED_TARGETS+=("$HOME/${COMPONENT_TARGETS[$index]}")
      break
    fi
  done
done

if [ "$DRY_RUN" = true ]; then
  printf 'Codex Setup dry run\n\n'
  for index in "${!SELECTED_SOURCES[@]}"; do
    printf '  LINK %s -> %s\n' "${SELECTED_TARGETS[$index]}" "${SELECTED_SOURCES[$index]}"
  done
  printf '\nNo files were changed.\n'
  exit 0
fi

if [ "$ACTION" = install ]; then
  printf 'Codex Setup\n\nChecking prerequisites...\n'
  missing=0
  for command_name in codex git rg; do
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
fi

printf '\nPreflight...\n'
issues=0
for index in "${!SELECTED_SOURCES[@]}"; do
  source="${SELECTED_SOURCES[$index]}"
  target="${SELECTED_TARGETS[$index]}"

  if [ "$ACTION" = uninstall ]; then
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$source" ]; then
      pass "$target is managed"
    elif [ -e "$target" ] || [ -L "$target" ]; then
      fail "$target exists but is not the managed symlink"
      issues=1
    else
      pass "$target is already absent"
    fi
  elif [ -L "$target" ] && [ "$(readlink "$target")" = "$source" ]; then
    pass "$target"
  elif [ -e "$target" ] || [ -L "$target" ]; then
    fail "$target already exists and is not the managed symlink"
    issues=1
  elif [ "$ACTION" = check ]; then
    fail "$target is not installed"
    issues=1
  else
    pass "$target is available"
  fi
done
[ "$issues" -eq 0 ] || exit 1

if [ "$ACTION" = check ]; then
  printf '\nSetup check complete.\n'
  exit 0
fi

if [ "$ACTION" = uninstall ]; then
  printf '\nRemoving managed links...\n'
  for index in "${!SELECTED_SOURCES[@]}"; do
    source="${SELECTED_SOURCES[$index]}"
    target="${SELECTED_TARGETS[$index]}"
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$source" ]; then
      unlink "$target"
      pass "$target"
    fi
  done
  printf '\nUninstall complete. Real files and foreign symlinks were not modified.\n'
  exit 0
fi

printf '\nInstalling links...\n'
for index in "${!SELECTED_SOURCES[@]}"; do
  source="${SELECTED_SOURCES[$index]}"
  target="${SELECTED_TARGETS[$index]}"
  if [ -L "$target" ] && [ "$(readlink "$target")" = "$source" ]; then
    continue
  fi
  mkdir -p "$(dirname "$target")"
  ln -s "$source" "$target"
  pass "$target"
done

printf '\nSetup complete. Live config, authentication, and plugin state were not modified.\n'
printf 'Run `bash setup.sh --check` with the same --skill options to verify the links.\n'
