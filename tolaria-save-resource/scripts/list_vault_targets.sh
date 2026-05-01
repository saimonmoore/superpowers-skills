#!/usr/bin/env bash
# List existing notes in the Tolaria vault grouped by type, so the agent can
# pick relationship targets (related_to Topics, belongs_to Project/Responsibility/Procedure)
# without scanning every file.
#
# Usage: list_vault_targets.sh <vault-dir>
#
# Output: blocks per type, e.g.
#   # Topics
#   ai	AI / ML
#   adhd	ADHD
#   # Projects
#   global-pulse	Global Pulse
#   ...
set -euo pipefail

vault="${1:?usage: list_vault_targets.sh <vault-dir>}"
[[ -d "$vault" ]] || { echo "not a directory: $vault" >&2; exit 1; }

print_type() {
  local type="$1"
  echo "# $type"
  # Find files whose frontmatter declares this type, then print "<basename>\t<H1>".
  while IFS= read -r -d '' file; do
    awk -v fname="$(basename "$file" .md)" -v wanted="$type" '
      BEGIN { in_fm=0; fm_done=0; type_match=0 }
      NR==1 && /^---[[:space:]]*$/ { in_fm=1; next }
      in_fm && /^---[[:space:]]*$/ { in_fm=0; fm_done=1; next }
      in_fm && /^type:[[:space:]]*/ {
        val=$0
        sub(/^type:[[:space:]]*/, "", val)
        gsub(/[[:space:]"'\'']+$/, "", val)
        gsub(/^["'\'']/, "", val)
        if (val == wanted) type_match=1
      }
      fm_done && type_match && /^#[[:space:]]+/ {
        title=$0; sub(/^#[[:space:]]+/, "", title)
        printf "%s\t%s\n", fname, title
        exit
      }
    ' "$file"
  done < <(find "$vault" -maxdepth 1 -name '*.md' -type f -print0 | sort -z)
}

for t in Topics Projects Responsibilities Procedures Events; do
  print_type "$t"
done
