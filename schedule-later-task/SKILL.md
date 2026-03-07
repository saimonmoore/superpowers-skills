---
name: schedule-later-task
description: Use when a user asks to create a task now and execute it later at a specified time/date (for example "tomorrow morning", "in 2 hours", "Monday at 5pm"); refines the task against the repo, persists a bean in .beans/, confirms it with the user, verifies at(1), and schedules asynchronous execution with codex or omp
---

# Schedule Later Task

## Overview

Convert a natural-language request into a deferred execution task. Refine scope against the active repository, persist a bean task in `.beans/`, confirm the bean content with the user, and schedule asynchronous execution through `at`.

## Trigger Conditions

Trigger only when BOTH elements are present:
1. **WHAT**: a concrete task to execute later.
2. **WHEN**: a concrete scheduling phrase (date/time/delay/time window).

Do not trigger if WHEN is missing.

## Typical User Phrases

- "Create a task to ... and execute it tomorrow morning"
- "Create a task to ... and schedule it for Monday 5pm"
- "Create a task to ... for an hour from now"
- "Schedule a task to ... on Tuesday evening"

## Required Inputs

Collect/derive these values before scheduling:

- `task_description`: what needs to be done.
- `when_expression`: user’s natural-language schedule phrase.
- `llm_cli`: `codex` (default) or `omp` (if user explicitly asks).

## Workflow

### 1) Refine the task against the codebase

1. Inspect repository context using `find`, `grep`, and `read`.
2. Clarify concrete scope:
   - affected directories/packages/apps
   - constraints/risk areas
   - verification expectations
3. Produce a refined task statement and checklist appropriate for execution by an autonomous agent.

### 2) Build bean content using template structure

Use the file shape from `.beans/jobs-b2b-idpo--tech-debt-cleanup-and-remove-unused-jobs-backend-d.md` as the format baseline.

If that file is unavailable, use `assets/bean-task-template.md`.

Persist a new bean file under `.beans/` with:
- YAML frontmatter (`title`, `status: todo`, `type: task`, `priority`, `tags`, timestamps)
- `## Goal`
- `## Scope`
- `## Checklist`
- `## Definition of Done`

Set `created_at`/`updated_at` to current UTC timestamp.

### 3) Display bean for confirmation

Read back the created bean file and present it verbatim.

Require explicit user confirmation that the bean accurately matches intent before scheduling.

### 4) Convert WHEN to deterministic `at` timestamp

Use `scripts/convert_when_to_at_timestamp.py` to convert natural language into a strict `YYYYMMDDHHMM` timestamp for `at -t`.
Use `references/at-timespec-examples.md` for supported grammar and examples.

Rules:
- Preserve exact date/time if provided.
- If only **morning** is provided, resolve deterministically inside **08:00–09:00**.
- If only **evening** is provided, resolve deterministically inside **18:00–23:59**.
- If timezone is ambiguous, use local system timezone and state that assumption.
- Reject unsupported WHEN phrases and request a supported phrase.

### 5) Verify/install `at`

1. Run `scripts/verify_at.sh`.
2. If verification fails, offer installation via `scripts/install_at.sh`.
3. Do not continue scheduling until `at` is available.

### 6) Schedule asynchronous execution

Construct prompt:

`Complete the <absolute/path/to/bean-file>`

Schedule via:

`bash scripts/schedule_with_at.sh "<YYYYMMDDHHMM>" "Complete the <absolute/path/to/bean-file>" "<codex|omp>"`

Default `llm_cli` to `codex`; switch to `omp` only when the user explicitly requests omp.

### 7) Return script output exactly

Return the exact stdout/stderr produced by `scripts/schedule_with_at.sh`.

## Deterministic Safeguards

- Reject scheduling if WHAT or WHEN is missing.
- Reject scheduling if bean confirmation was not provided.
- Reject scheduling if `.beans/` cannot be written.
- Reject scheduling if `at` remains unavailable after install attempt.

## Output Contract

When successful, provide:
1. Created bean path.
2. Final `at` timestamp used (`YYYYMMDDHHMM`).
3. Selected provider (`codex` or `omp`).
4. Exact scheduling script output.

## Script References

- `scripts/verify_at.sh` — checks if `at` is installed and minimally usable on macOS/Linux.
- `scripts/install_at.sh` — best-effort install flow for macOS/Linux package managers.
- `scripts/convert_when_to_at_timestamp.py` — deterministic converter from natural language WHEN to `at -t` timestamp.
- `scripts/schedule_with_at.sh` — submits the asynchronous LLM command via `at -t`.
- `references/at-timespec-examples.md` — deterministic conversion guide and examples.
- `assets/bean-task-template.md` — fallback bean template structure.
