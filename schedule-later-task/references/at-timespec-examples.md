# Deterministic `at -t` Timestamp Conversion Guide

Convert natural-language `WHEN` phrases to strict `YYYYMMDDHHMM` and schedule with `at -t`.

## Path Convention

Use absolute skill paths:

```bash
skill_root="/absolute/path/to/schedule-later-task"
```

## Canonical Flow

1. Verify `at`:
   ```bash
   bash "$skill_root/scripts/verify_at.sh"
   ```
2. Convert `WHEN`:
   ```bash
   python3 "$skill_root/scripts/convert_when_to_at_timestamp.py" \
     --when "tomorrow morning" \
     --timezone "Europe/Berlin"
   ```
3. Schedule:
   ```bash
   bash "$skill_root/scripts/schedule_with_at.sh" \
     "<YYYYMMDDHHMM>" \
     "Complete the <absolute/path/to/bean-file> in <absolute/cwd>. Run required verification before reporting done." \
     "codex"
   ```

## Supported WHEN Grammar

- `in N minutes|hours|days`
- `tomorrow [at HH(:MM)?(am|pm)?]`
- `tomorrow morning|evening`
- `weekday [at HH(:MM)?(am|pm)?]` (`next` optional)
- `weekday morning|evening` (`next` optional)
- `YYYY-MM-DD [HH:MM]`

Unsupported phrases must fail fast.

## Timezone Policy

Preferred: pass explicit `--timezone` (IANA key).

Fallback hierarchy in converter:
1. `TZ` environment variable
2. local IANA timezone (if available)
3. `UTC`

Converter reports assumptions in output JSON.

## Deterministic Windows

- `morning`: `08:00–09:00`
- `evening`: `18:00–23:59`

Time slot is selected by deterministic hash. Same inputs produce the same output.

## Example

```bash
python3 "$skill_root/scripts/convert_when_to_at_timestamp.py" \
  --when "tomorrow morning" \
  --timezone "Europe/Berlin" \
  --now "2026-03-07T10:15:00+01:00"
```

```json
{"at_timestamp":"202603080849","resolved_iso":"2026-03-08T08:49:00+01:00","rule":"tomorrow_morning","assumptions":[]}
```

## Scheduler Verification

`schedule_with_at.sh` validates queue presence after submit.
Expected tail output:

```text
verified job <id> present in at queue
```
