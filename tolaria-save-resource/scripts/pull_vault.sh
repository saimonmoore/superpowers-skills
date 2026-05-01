#!/usr/bin/env bash
# Bring the Tolaria vault up to date with origin before writing.
# Fast-forward only — refuses to merge or rebase silently. Any failure exits
# non-zero and prints a one-line, human-meaningful error to stderr that the
# caller can pass through to the user.
#
# Usage: pull_vault.sh <vault-dir>
#
# Exit codes:
#   0  pulled cleanly (or already up to date)
#   1  bad args / not a git repo
#   2  no upstream configured for current branch — caller may decide to skip pull
#   3  pull failed (network, auth, non-fast-forward, conflicts)
#   4  vault has uncommitted changes that would block a clean state
set -euo pipefail

vault="${1:?usage: pull_vault.sh <vault-dir>}"
[[ -d "$vault" ]] || { echo "not a directory: $vault" >&2; exit 1; }
cd "$vault"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "not a git repo: $vault" >&2
  exit 1
fi

# Refuse to operate when there are unstaged changes in tracked files —
# pull --ff-only is safe with a dirty tree, but the user almost certainly
# wants to know rather than have us write on top of mystery state.
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "vault has uncommitted changes; resolve before saving a new resource" >&2
  git status --short >&2
  exit 4
fi

if ! git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
  echo "no upstream configured for current branch; skipping pull" >&2
  exit 2
fi

if ! out=$(git pull --ff-only 2>&1); then
  echo "git pull --ff-only failed:" >&2
  echo "$out" >&2
  exit 3
fi
