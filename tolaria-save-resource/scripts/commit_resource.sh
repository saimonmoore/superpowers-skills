#!/usr/bin/env bash
# Commit a single newly-created Resources note in the Tolaria vault and push.
# Stages only the named file (no -A) so unrelated dirty state is left alone.
#
# Usage: commit_resource.sh <vault-dir> <relative-file> <commit-message>
#
# Exit codes:
#   0  committed and pushed
#   2  committed, push skipped (no upstream)
#   3  committed, push failed (network/auth/non-ff) — message printed to stderr
#   1  anything else (bad args, file missing, commit failed)
set -euo pipefail

vault="${1:?usage: commit_resource.sh <vault-dir> <relative-file> <commit-message>}"
file="${2:?missing relative file}"
msg="${3:?missing commit message}"

cd "$vault"
[[ -f "$file" ]] || { echo "file not found in vault: $file" >&2; exit 1; }

git add -- "$file"
# Bail out if nothing was actually staged (e.g. file is identical to HEAD).
if git diff --cached --quiet -- "$file"; then
  echo "nothing to commit for $file" >&2
  exit 1
fi
git commit -m "$msg"

# Push only if an upstream exists for the current branch.
if ! git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
  echo "no upstream configured; skipping push" >&2
  exit 2
fi

if ! git push; then
  echo "push failed; commit is local" >&2
  exit 3
fi
