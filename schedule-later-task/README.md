# schedule-later-task

## Objective

Schedule repository tasks for later execution in a deterministic and auditable way.

The skill refines a task, writes a bean task file, converts natural language time to a strict `at -t` timestamp, and schedules asynchronous execution with `codex` (default) or `omp`.

## Trigger Conditions

Trigger only when both are present:
- **WHAT**: task to execute.
- **WHEN**: scheduling phrase.

Do not trigger if `WHEN` is missing.

## Path Setup

Resolve the skill path first and use absolute script paths.

```bash
skill_root="/absolute/path/to/schedule-later-task"
```

## Components

- `SKILL.md` — behavior contract and workflow.
- `assets/bean-task-template.md` — canonical bean schema template.
- `references/at-timespec-examples.md` — supported WHEN grammar and conversion examples.
- `scripts/verify_at.sh` — verify `at` availability.
- `scripts/install_at.sh` — install `at` if missing.
- `scripts/convert_when_to_at_timestamp.py` — deterministic `WHEN` to `YYYYMMDDHHMM` converter.
- `scripts/schedule_with_at.sh` — schedule with `at -t` and verify queue entry.

## Usage Flow

1. Capture `task_description`, `when_expression`, `timezone`, `provider`.
2. Refine task against repo context.
3. Ensure bean directory exists:
   ```bash
   mkdir -p .beans
   ```
4. Create bean file under `.beans/` using `assets/bean-task-template.md`.
5. Show bean content.
   - Auto-proceed for clear low-risk requests.
   - Require explicit confirmation for ambiguous/high-risk/destructive requests.
6. Verify `at`:
   ```bash
   bash "$skill_root/scripts/verify_at.sh"
   ```
7. Convert WHEN:
   ```bash
   python3 "$skill_root/scripts/convert_when_to_at_timestamp.py" \
     --when "tomorrow morning" \
     --timezone "Europe/Berlin"
   ```
8. Schedule using converter output:
   ```bash
   bash "$skill_root/scripts/schedule_with_at.sh" \
     "<YYYYMMDDHHMM>" \
     "Complete the <absolute/path/to/bean-file> in <absolute/cwd>. Run required verification before reporting done." \
     "codex"
   ```
9. Return exact scheduler stdout/stderr.

## Determinism and Timezone Policy

- Preferred: always pass explicit IANA timezone (`--timezone`).
- Fallback hierarchy in converter (if explicit timezone unavailable):
  1. `TZ` environment variable (IANA key)
  2. local IANA timezone (if available)
  3. UTC (with assumption note)
- `morning` resolves deterministically in `08:00–09:00`.
- `evening` resolves deterministically in `18:00–23:59`.

## Examples

### Example A — Tomorrow morning

```bash
python3 "$skill_root/scripts/convert_when_to_at_timestamp.py" \
  --when "tomorrow morning" \
  --timezone "Europe/Berlin" \
  --now "2026-03-07T10:15:00+01:00"
```

Output:
```json
{"at_timestamp": "202603080849", "resolved_iso": "2026-03-08T08:49:00+01:00", "rule": "tomorrow_morning", "assumptions": []}
```

### Example B — Monday at 5pm

```bash
python3 "$skill_root/scripts/convert_when_to_at_timestamp.py" \
  --when "monday at 5pm" \
  --timezone "Europe/Berlin" \
  --now "2026-03-07T10:15:00+01:00"
```

Output:
```json
{"at_timestamp": "202603091700", "resolved_iso": "2026-03-09T17:00:00+01:00", "rule": "weekday_explicit_time", "assumptions": []}
```

### Example C — Scheduling output

```bash
bash "$skill_root/scripts/schedule_with_at.sh" "202603091700" "Complete the /abs/.beans/task.md in /abs/repo. Run required verification before reporting done." "codex"
```

Possible output:
```text
job 42 at Mon Mar  9 17:00:00 2026
verified job 42 present in at queue
```

## Failure Cases

- Missing WHAT/WHEN.
- Unsupported WHEN grammar.
- Bean file cannot be created after `mkdir -p .beans`.
- `at` unavailable after install attempt.
- Invalid timestamp (not 12 digits).
- Scheduled job ID not present in `at -l`.
