# `schedule-later-task-v2` time conversion notes

The orchestrator uses `convert_when_to_at_timestamp.py` and schedules with `at -t`.

Supported `--when` grammar:
- `in N minutes|hours|days`
- `tomorrow [at HH(:MM)?(am|pm)?]`
- `tomorrow morning|evening`
- `weekday [at HH(:MM)?(am|pm)?]` (optional `next`)
- `weekday morning|evening` (optional `next`)
- `YYYY-MM-DD [HH:MM]`

Timezone resolution order in converter:
1. `--timezone`
2. `TZ` environment value (if valid)
3. local IANA timezone (if available)
4. UTC fallback

Morning/evening windows are deterministic hash-selected:
- morning: `08:00–09:00`
- evening: `18:00–23:59`
