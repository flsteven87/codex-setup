# Portable Handoff Discovery

Use this fallback only when `$catchup` received no explicit artifact and Codex task provenance did
not return `SELECTED`. Select by repository identity, never by recency alone.

## Find candidates

1. Check `.agents/handoffs/*` and `.codex/handoffs/*` in the active repository.
2. When neither location identifies a handoff, inspect the OS temporary directory read-only for
   Markdown files whose names contain `handoff` and which were modified within the last 14 days.
3. Reject files that do not identify an accessible repository root or credential-free canonical
   remote URL.

## Match repository identity

1. Normalize credential-free SSH and HTTPS forms of the same owner/repository before comparing.
2. Select a candidate only when exactly one file matches the active repository's absolute root or
   canonical remote.
3. A remote match does not choose between multiple clones or worktrees. Prefer an exact active
   workspace root; when no active repository disambiguates them, require the user to provide the
   exact repository path.
4. Never infer a repository from a project-like name.

## Return the intake result

- Return the exact path when one candidate is uniquely selected.
- When multiple candidates remain plausible, return their paths briefly. The calling skill
  classifies the run as `AMBIGUOUS` and requests the exact handoff path.
- When no candidate remains, return none. The calling skill classifies the run as `NO_HANDOFF`.

Do not combine candidates or reconstruct a competing workstream from Git while waiting for an exact
path.
