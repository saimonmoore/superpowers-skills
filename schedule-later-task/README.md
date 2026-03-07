# schedule-later-task

## Objective

Provide a faster, one-command scheduling workflow that is deterministic and machine-readable.

Compared to v1, v2 moves most flow logic into `scripts/schedule_task.py` and returns structured JSON for easier automation and debugging.

## Canonical Usage

```bash
skill_root="/Users/saimon.moore/Development/AI/superpowers-skills/schedule-later-task"

python3 "$skill_root/scripts/schedule_task.py" \
  --what "Create a task to open a PR formatting all files in the codebase" \
  --when "tomorrow morning" \
  --provider omp \\
  --timezone Europe/Berlin \
  --cwd "/Users/saimon.moore/Development/Onlyfy/jobs-b2b" \
  --require-confirmation if-ambiguous \
  --mail-marker-prefix schedule-later-task \
  --json
```

`--mail-marker-prefix` is optional and defaults to `schedule-later-task`.
Default provider is `omp`.

## Identify Scheduled Jobs

`atq` shows numeric IDs only. Use this helper to map IDs to marker prefix, provider, and bean path:

```bash
python3 "$skill_root/scripts/list_scheduled_jobs.py"
```

## Script Responsibilities

- `schedule_task.py` orchestrates end-to-end flow:
  - create `.beans/` if needed
  - render bean
  - resolve WHEN -> timestamp
  - verify `at`
  - schedule with provider
  - verify queue entry
  - emit JSON result
- `render_bean.py` handles deterministic bean creation.
- `convert_when_to_at_timestamp.py` handles deterministic time parsing.
- `schedule_with_at.sh` submits/validates queue placement.
- `list_scheduled_jobs.py` maps `atq` IDs to marker prefix/provider/bean path using `at -c`.

## Output JSON

Typical success response:

```json
{
  "status": "scheduled",
  "requires_confirmation": false,
  "bean_path": "/abs/path/.beans/jobs-scheduled--...md",
  "at_timestamp": "202603080849",
  "provider": "codex",
  "job_id": "42",
  "scheduled_for": "2026-03-08T08:49:00+01:00",
  "warnings": [],
  "assumptions": [],
  "errors": [],
  "mail_marker_prefix": "schedule-later-task",
  "schedule_output": "job 42 at Sun Mar  8 08:49:00 2026\nverified job 42 present in at queue"
}
```

Possible non-success states:
- `status: needs_confirmation` (exit code 2)
- `status: error` (exit code 1)

## Fast Mode

Add `--fast` for clear low-risk requests:

```bash
python3 "$skill_root/scripts/schedule_task.py" \
  --what "Create task to update docs links" \
  --when "in 20 minutes" \
  --provider codex \
  --timezone Europe/Berlin \
  --cwd "/Users/saimon.moore/Development/Onlyfy/jobs-b2b" \
  --fast \
  --json
```

## Notes

- No `config.toml` is used in v2.
- Prefer explicit `--timezone` for deterministic behavior.
- Keep v1 and v2 side-by-side for comparative testing.
- `schedule_with_at.sh` sends a custom notification mail immediately after enqueue + queue verification, with marker prefix/provider/timestamp/bean context.
- Queued job still prints completion marker at execution, so default `at` mail output is preserved.
