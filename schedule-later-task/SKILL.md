---
name: schedule-later-task
description: Use when a user asks to create a task now and execute it at a later time/date and both WHAT and WHEN are present; runs a deterministic one-command scheduling orchestrator
---

# Schedule Later Task V2

## Overview

Run deferred task scheduling through one deterministic orchestrator command. The command creates a bean task, converts WHEN to `at -t` timestamp, verifies `at`, schedules execution, and returns structured JSON.

## Trigger Conditions

Trigger only when BOTH are present:
1. WHAT task should be executed.
2. WHEN it should run.

Do not trigger if WHEN is missing.

## Canonical Command

Set skill root to an absolute path:

```bash
skill_root="/Users/saimon.moore/Development/AI/superpowers-skills/schedule-later-task"
```

Run:

```bash
python3 "$skill_root/scripts/schedule_task.py" \
  --what "<task description>" \
  --when "<when expression>" \
  --provider "<codex|omp>" \
  --timezone "<IANA timezone>" \
  --cwd "<absolute/repo/path>" \
  --require-confirmation if-ambiguous \
  --mail-marker-prefix schedule-later-task \
  --json
```

`--mail-marker-prefix` is optional and defaults to `schedule-later-task`.
Default provider is `omp`.

## Fast Mode

For clear low-risk requests, add `--fast` to keep compact bean checklist and skip optional refinement.

## Confirmation Policy

Use `--require-confirmation` with:
- `always`
- `if-ambiguous` (default)
- `never`

If confirmation is required, script returns `status: needs_confirmation` and exits non-zero.

## Output Contract

Successful run returns JSON with:
- `status: "scheduled"`
- `bean_path`
- `at_timestamp`
- `provider`
- `job_id`
- `scheduled_for`
- `warnings`
- `assumptions`
- `mail_marker_prefix`

Failure returns `status: "error"` and `errors`.

## Deterministic Safeguards

- `.beans/` is created before bean write.
- Bean naming is deterministic and collision-safe.
- WHEN parsing is strict and deterministic.
- Queue verification is required (`verified job <id> present in at queue`).
- Scheduler sends a custom notification mail immediately after `at` enqueue + queue verification, with marker prefix/provider/timestamp/bean context.
- Queued job still emits completion marker at execution so default `at` mail contains outcome details.

Inspect queue entries with labels:

```bash
python3 "$skill_root/scripts/list_scheduled_jobs.py"
```

## Script References

- `scripts/schedule_task.py` — orchestrator entrypoint.
- `scripts/render_bean.py` — deterministic bean renderer.
- `scripts/convert_when_to_at_timestamp.py` — deterministic WHEN converter.
- `scripts/verify_at.sh` / `scripts/install_at.sh` — at utility lifecycle.
- `scripts/schedule_with_at.sh` — schedules and confirms queue presence.
- `scripts/list_scheduled_jobs.py` — shows `atq` jobs enriched with marker prefix, provider, and bean path.
