# Deterministic `at -t` Timestamp Conversion Guide

Convert a natural-language WHEN phrase into a strict `at -t` timestamp (`YYYYMMDDHHMM`) using `scripts/convert_when_to_at_timestamp.py`.

## Why `at -t`

- Avoid shell/locale-dependent `at` free-form parsing.
- Ensure repeated runs with same input resolve to same schedule.
- Make scheduling output testable and auditable.

## Canonical Flow

1. Run converter script:
   ```bash
   python3 scripts/convert_when_to_at_timestamp.py --when "tomorrow morning"
   ```
2. Read JSON output field: `at_timestamp`
3. Schedule with:
   ```bash
   bash scripts/schedule_with_at.sh "<at_timestamp>" "Complete the <absolute/path/to/bean-file>" "codex"
   ```

## Supported WHEN Grammar

- `in N minutes|hours|days`
- `tomorrow [at HH(:MM)?(am|pm)?]`
- `tomorrow morning|evening`
- `weekday [at HH(:MM)?(am|pm)?]` (`next` optional)
- `weekday morning|evening` (`next` optional)
- `YYYY-MM-DD [HH:MM]`

Unsupported phrases must fail fast and ask user for a supported form.

## Deterministic Window Rules

### Morning
- Window: `08:00`–`09:00`
- Slot count: 61 minutes
- Result selected by deterministic hash; no RNG.

### Evening
- Window: `18:00`–`23:59`
- Slot count: 360 minutes
- Result selected by deterministic hash; no RNG.

## Examples

Use fixed `--now` in tests to make outputs reproducible.

```bash
python3 scripts/convert_when_to_at_timestamp.py \
  --when "tomorrow morning" \
  --timezone "Europe/Berlin" \
  --now "2026-03-07T10:15:00+01:00"
```

```json
{"at_timestamp":"202603080849","resolved_iso":"2026-03-08T08:49:00+01:00","rule":"tomorrow_morning","assumptions":[]}
```

```bash
python3 scripts/convert_when_to_at_timestamp.py \
  --when "monday at 5pm" \
  --timezone "Europe/Berlin" \
  --now "2026-03-07T10:15:00+01:00"
```

```json
{"at_timestamp":"202603091700","resolved_iso":"2026-03-09T17:00:00+01:00","rule":"weekday_explicit_time","assumptions":[]}
```

## Validation Checklist

1. Confirm converter output is valid JSON with `at_timestamp`.
2. Confirm timestamp format is exactly 12 digits (`YYYYMMDDHHMM`).
3. Confirm `resolved_iso` is future relative to execution time.
4. Pass only `at_timestamp` to `schedule_with_at.sh`.
