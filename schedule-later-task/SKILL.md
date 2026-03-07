---
name: schedule-later-task
description: Use when a user asks to create a task now and execute it at a later time/date (for example "tomorrow morning", "in 2 hours", "Monday at 5pm") and both WHAT and WHEN are present
---

# Schedule Later Task

## Overview

Convert a natural-language deferred-work request into a deterministic scheduled execution. Refine scope against the repository, persist a bean task, and schedule asynchronous execution through `at -t`.

## Trigger Conditions

Trigger only when BOTH elements are present:
1. **WHAT**: concrete task to execute.
2. **WHEN**: concrete scheduling phrase.

Do not trigger if WHEN is missing.

## Typical User Phrases

- "Create a task to ... and execute it tomorrow morning"
- "Create a task to ... and schedule it for Monday 5pm"
- "Create a task to ... for an hour from now"
- "Schedule a task to ... on Tuesday evening"

## Required Inputs

Collect/derive before scheduling:
- `task_description`
- `when_expression`
- `timezone` (IANA, for example `Europe/Berlin`; required unless user allows fallback)
- `llm_cli` (`codex` default, `omp` only when explicitly requested)

## Path Resolution

Resolve and use absolute paths for all script calls.

```bash
skill_root="/absolute/path/to/schedule-later-task"
```

All script invocations must use `$skill_root/scripts/...`.

## Workflow

### 1) Refine task against codebase

1. Inspect repository context using `find`, `grep`, `read`.
2. Clarify concrete scope (affected paths, constraints, verification expectations).
3. Produce refined execution checklist.

### 2) Create bean task from schema template (primary source)

Use `assets/bean-task-template.md` as the canonical structure.

Optional: use `.beans/jobs-b2b-idpo--tech-debt-cleanup-and-remove-unused-jobs-backend-d.md` only as style reference when available.

Before writing bean:

```bash
mkdir -p .beans
```

Then persist a bean under `.beans/` with:
- frontmatter (`title`, `status: todo`, `type: task`, `priority`, `tags`, `created_at`, `updated_at`)
- `## Goal`
- `## Scope`
- `## Checklist`
- `## Definition of Done`

### 3) Confirmation policy (conditional)

- **Proceed without blocking confirmation** when WHAT/WHEN are clear, non-destructive, and low-risk.
- **Require explicit confirmation** when request is ambiguous, destructive, high-risk, or impacts production/data/security boundaries.

In all cases, display the created bean content in the response.

### 4) Convert WHEN to deterministic timestamp

Use:

```bash
python3 "$skill_root/scripts/convert_when_to_at_timestamp.py" \
  --when "<when_expression>" \
  --timezone "<IANA timezone>"
```

Use `--now` only for deterministic testing.

Primary policy: pass explicit timezone.
Fallback policy (only when explicit timezone unavailable and user accepts): converter resolves from `TZ` environment, then local IANA timezone when available, then UTC.

### 5) Verify/install `at`

1. `bash "$skill_root/scripts/verify_at.sh"`
2. If missing, offer install via `bash "$skill_root/scripts/install_at.sh"`
3. Do not continue until verification succeeds.

### 6) Schedule asynchronous execution

Construct prompt:

`Complete the <absolute/path/to/bean-file> in <absolute/cwd>. Run required verification before reporting done.`

Schedule via:

```bash
bash "$skill_root/scripts/schedule_with_at.sh" \
  "<YYYYMMDDHHMM>" \
  "Complete the <absolute/path/to/bean-file> in <absolute/cwd>. Run required verification before reporting done." \
  "<codex|omp>"
```

### 7) Verify queue presence

After scheduling, verify returned job ID exists in queue (`at -l`). Treat missing queue entry as failure.

### 8) Return script output exactly

Return exact stdout/stderr from `schedule_with_at.sh`.

## Deterministic Safeguards

- Reject if WHAT or WHEN is missing.
- Reject if converter cannot parse WHEN.
- Reject if `.beans/` cannot be created/written.
- Reject if `at` is unavailable after install attempt.
- Reject if scheduled job ID is not present in `at -l`.

## Output Contract

On success, provide:
1. Bean path
2. Final `at` timestamp (`YYYYMMDDHHMM`)
3. Timezone used
4. Selected provider (`codex` or `omp`)
5. Exact scheduler script output

## Script References

- `scripts/verify_at.sh` — checks if `at` is available.
- `scripts/install_at.sh` — installs `at` on macOS/Linux.
- `scripts/convert_when_to_at_timestamp.py` — deterministic natural-language WHEN conversion.
- `scripts/schedule_with_at.sh` — submits command with `at -t` and verifies queue entry.
- `references/at-timespec-examples.md` — supported grammar and examples.
- `assets/bean-task-template.md` — canonical bean schema template.
