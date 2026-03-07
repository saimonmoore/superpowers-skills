#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 5 ]; then
  echo "Usage: $0 <at-timestamp:YYYYMMDDHHMM> <prompt> [codex|omp] [mail-marker-prefix] [mail-subject-context]"
  exit 1
fi

at_timestamp="$1"
prompt="$2"
provider="${3:-omp}"
mail_marker_prefix="${4:-schedule-later-task-v2}"
mail_subject_context="${5:-}"

mail_subject_context="${mail_subject_context//\"/}"
mail_subject_context="${mail_subject_context//$'\n'/ }"
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

job_line="$job_line; job_rc=\$?; marker=\"[$mail_marker_prefix] provider=$provider exit=\$job_rc at=$at_timestamp\"; echo \"\$marker\"; exit \$job_rc"

at_output="$(printf '%s\n' "$job_line" | at -t "$at_timestamp" 2>&1)"
printf '%s\n' "$at_output"

job_id="$(printf '%s\n' "$at_output" | sed -n 's/^job \([0-9][0-9]*\) .*/\1/p' | sed -n '1p')"
if [ -z "$job_id" ]; then
  echo "Unable to parse scheduled job id from at output"
  exit 5
fi

if at -l | awk '{print $1}' | grep -Fxq "$job_id"; then
  if command -v mail >/dev/null 2>&1; then
    enqueue_subject="[$mail_marker_prefix] enqueued job=$job_id provider=$provider at=$at_timestamp"
    if [ -n "$mail_subject_context" ]; then
      enqueue_subject="$enqueue_subject $mail_subject_context"
    fi
    scheduled_for="$at_timestamp"
    if command -v date >/dev/null 2>&1; then
      scheduled_for="$(date -j -f '%Y%m%d%H%M' "$at_timestamp" '+%Y-%m-%d %H:%M %Z' 2>/dev/null || true)"
      if [ -z "$scheduled_for" ]; then
        scheduled_for="$(date -d "${at_timestamp:0:8} ${at_timestamp:8:2}:${at_timestamp:10:2}" '+%Y-%m-%d %H:%M %Z' 2>/dev/null || true)"
      fi
      if [ -z "$scheduled_for" ]; then
        scheduled_for="$at_timestamp"
      fi
    fi
    enqueue_body="Enqueued at job: $job_id"
    enqueue_body+=$'\n'"Provider: $provider"
    enqueue_body+=$'\n'"Timestamp: $at_timestamp"
    enqueue_body+=$'\n'"Scheduled for: $scheduled_for"
    enqueue_body+=$'\n'"Context: $mail_subject_context"
    if printf '%s\n' "$enqueue_body" | mail -s "$enqueue_subject" "$USER"; then
      echo "sent enqueue notification mail subject: $enqueue_subject"
    else
      echo "warning: failed to send enqueue notification mail"
  fi
  fi
  echo "verified job $job_id present in at queue"
  exit 0
fi

echo "Scheduled job $job_id not found in at queue"
exit 6
