# schedule-later-task

## Objective

Enable deterministic deferred execution of coding tasks.

When a user asks to do work later (for example, "tomorrow morning"), this skill:
1. Refines the task against the active codebase.
2. Persists a bean task in `.beans/` using the established bean structure.
3. Shows the bean to the user for confirmation.
4. Converts `WHEN` into a deterministic `at -t` timestamp (`YYYYMMDDHHMM`).
5. Schedules asynchronous execution with `codex` (default) or `omp`.

## Trigger Conditions

Trigger only when both are present:
- **WHAT**: the task to execute.
- **WHEN**: a scheduling phrase.

Do not trigger if `WHEN` is missing.

## Skill Components

- `SKILL.md` — main workflow and guardrails.
- `scripts/verify_at.sh` — verify `at` availability.
- `scripts/install_at.sh` — install `at` on macOS/Linux.
- `scripts/convert_when_to_at_timestamp.py` — deterministic `WHEN` → `YYYYMMDDHHMM` converter.
- `scripts/schedule_with_at.sh` — submit async job via `at -t`.
- `references/at-timespec-examples.md` — supported grammar and conversion examples.
- `assets/bean-task-template.md` — fallback bean template if in-repo example is unavailable.

## Usage Flow

1. Capture `task_description`, `when_expression`, and optional provider (`codex`/`omp`).
2. Refine scope against repo context (`find`, `grep`, `read`).
3. Create bean file under `.beans/`.
4. Present bean file and require user confirmation.
5. Verify `at`:
   ```bash
   bash scripts/verify_at.sh
   ```
6. Convert `WHEN` deterministically:
   ```bash
   python3 scripts/convert_when_to_at_timestamp.py --when "tomorrow morning"
   ```
7. Schedule using converter output (`at_timestamp`):
   ```bash
   bash scripts/schedule_with_at.sh "<YYYYMMDDHHMM>" "Complete the <absolute/path/to/bean-file>" "codex"
   ```
8. Return exact scheduler stdout/stderr.

## Deterministic Conversion Rules

Supported `WHEN` forms:
- `in N minutes|hours|days`
- `tomorrow [at HH(:MM)?(am|pm)?]`
- `tomorrow morning|evening`
- `weekday [at HH(:MM)?(am|pm)?]` (with optional `next`)
- `weekday morning|evening` (with optional `next`)
- `YYYY-MM-DD [HH:MM]`

Window handling:
- `morning` resolves deterministically inside `08:00–09:00`.
- `evening` resolves deterministically inside `18:00–23:59`.
- No RNG is used; same inputs resolve to the same timestamp.

## Command Examples

### Example 1: Tomorrow morning

```bash
python3 scripts/convert_when_to_at_timestamp.py \
  --when "tomorrow morning" \
  --timezone "Europe/Berlin" \
  --now "2026-03-07T10:15:00+01:00"
```

Expected output:
```json
{"at_timestamp": "202603080849", "resolved_iso": "2026-03-08T08:49:00+01:00", "rule": "tomorrow_morning", "assumptions": []}
```

Then schedule:
```bash
bash scripts/schedule_with_at.sh "202603080849" "Complete the /absolute/path/to/.beans/my-task.md" "codex"
```

### Example 2: Monday at 5pm

```bash
python3 scripts/convert_when_to_at_timestamp.py \
  --when "monday at 5pm" \
  --timezone "Europe/Berlin" \
  --now "2026-03-07T10:15:00+01:00"
```

Expected output:
```json
{"at_timestamp": "202603091700", "resolved_iso": "2026-03-09T17:00:00+01:00", "rule": "weekday_explicit_time", "assumptions": []}
```

Then schedule:
```bash
bash scripts/schedule_with_at.sh "202603091700" "Complete the /absolute/path/to/.beans/my-task.md" "omp"
```

## Failure Cases

- Missing `WHEN` phrase.
- Unsupported `WHEN` grammar.
- Bean not confirmed by user.
- `.beans/` not writable.
- `at` missing and installation not completed.
- Invalid timestamp format passed to scheduler (must be 12 digits).

## Notes

- Scheduler defaults to `codex`; use `omp` only when explicitly requested.
- `schedule_with_at.sh` prints raw `at` output and should be returned exactly to the user.
