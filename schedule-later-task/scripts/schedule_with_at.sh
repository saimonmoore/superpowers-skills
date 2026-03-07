#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "Usage: $0 <at-timestamp:YYYYMMDDHHMM> <prompt> [codex|omp]"
  exit 1
fi

at_timestamp="$1"
prompt="$2"
provider="${3:-codex}"

if ! printf '%s' "$at_timestamp" | grep -Eq '^[0-9]{12}$'; then
  echo "Invalid at timestamp: $at_timestamp (expected YYYYMMDDHHMM)"
  exit 1
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"
bash "$script_dir/verify_at.sh" >/dev/null

case "$provider" in
  codex)
    if ! command -v codex >/dev/null 2>&1; then
      echo "codex CLI not found in PATH"
      exit 3
    fi
    cmd=(script -q /dev/null codex e --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "$prompt")
    ;;
  omp)
    omp_bin="$HOME/.bun/bin/omp"
    if [ ! -x "$omp_bin" ]; then
      echo "omp CLI not found at $omp_bin"
      exit 4
    fi
    cmd=(script -q /dev/null "$omp_bin" --no-pty --no-lsp --no-extensions --print "$prompt")
    ;;
  *)
    echo "Unsupported provider: $provider (expected codex or omp)"
    exit 2
    ;;
esac

job_line="$(printf '%q ' "${cmd[@]}")"
job_line="${job_line% }"

at_output="$(printf '%s\n' "$job_line" | at -t "$at_timestamp" 2>&1)"

printf '%s\n' "$at_output"