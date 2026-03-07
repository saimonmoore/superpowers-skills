#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


@dataclass(frozen=True)
class ConversionResult:
    at_timestamp: str
    resolved_iso: str
    rule: str
    assumptions: list[str]


class ConversionError(ValueError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert WHEN phrase to deterministic at -t timestamp")
    parser.add_argument("--when", required=True, help="Natural language time phrase")
    parser.add_argument("--timezone", help="IANA timezone name, e.g. Europe/Berlin")
    parser.add_argument("--now", help="ISO-8601 current time for deterministic tests")
    return parser.parse_args()


def resolve_timezone(args_timezone: str | None) -> tuple[ZoneInfo, list[str]]:
    assumptions: list[str] = []
    if args_timezone:
        try:
            return ZoneInfo(args_timezone), assumptions
        except Exception as error:
            raise ConversionError(f"Invalid timezone '{args_timezone}': {error}") from error

    env_tz = os.environ.get("TZ")
    if env_tz:
        try:
            tz = ZoneInfo(env_tz)
            assumptions.append(f"used TZ environment timezone {env_tz}")
            return tz, assumptions
        except Exception:
            assumptions.append(f"ignored invalid TZ environment value {env_tz}")

    local_tz = datetime.now().astimezone().tzinfo
    local_key = getattr(local_tz, "key", None) if local_tz is not None else None
    if local_key:
        assumptions.append(f"used local timezone {local_key}")
        return ZoneInfo(local_key), assumptions

    assumptions.append("fell back to UTC timezone")
    return ZoneInfo("UTC"), assumptions


def resolve_now(now_value: str | None, tz: ZoneInfo) -> datetime:
    if not now_value:
        return datetime.now(tz)

    parsed = datetime.fromisoformat(now_value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    else:
        parsed = parsed.astimezone(tz)
    return parsed


def minute_from_window(seed: str, start_minute: int, end_minute: int) -> int:
    slots = end_minute - start_minute + 1
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    offset = int(digest, 16) % slots
    return start_minute + offset


def next_weekday(base: datetime, weekday: int) -> datetime:
    delta_days = (weekday - base.weekday()) % 7
    if delta_days == 0:
        delta_days = 7
    return base + timedelta(days=delta_days)


def parse_clock(value: str) -> tuple[int, int]:
    normalized = value.strip().lower().replace(".", "")
    match = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", normalized)
    if not match:
        raise ConversionError(f"Unsupported clock format: {value}")

    hour = int(match.group(1))
    minute = int(match.group(2) or "0")
    meridiem = match.group(3)

    if minute > 59:
        raise ConversionError(f"Invalid minute value in: {value}")

    if meridiem:
        if hour < 1 or hour > 12:
            raise ConversionError(f"Invalid 12-hour clock in: {value}")
        if meridiem == "am":
            hour = 0 if hour == 12 else hour
        else:
            hour = 12 if hour == 12 else hour + 12
    else:
        if hour > 23:
            raise ConversionError(f"Invalid 24-hour clock in: {value}")

    return hour, minute


def at_timestamp(value: datetime) -> str:
    return value.strftime("%Y%m%d%H%M")


def apply_time(base: datetime, hour: int, minute: int) -> datetime:
    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


def convert_when_expression(raw_when: str, now: datetime, tz: ZoneInfo, assumptions: list[str]) -> ConversionResult:
    when = " ".join(raw_when.strip().lower().split())
    if not when:
        raise ConversionError("Missing --when value")

    rel = re.fullmatch(r"in\s+(\d+)\s+(minute|minutes|hour|hours|day|days)", when)
    if rel:
        amount = int(rel.group(1))
        unit = rel.group(2)
        if unit.startswith("minute"):
            resolved = now + timedelta(minutes=amount)
        elif unit.startswith("hour"):
            resolved = now + timedelta(hours=amount)
        else:
            resolved = now + timedelta(days=amount)
        resolved = resolved.replace(second=0, microsecond=0)
        return ConversionResult(at_timestamp(resolved), resolved.isoformat(), "relative_duration", assumptions)

    iso_date = re.fullmatch(r"(\d{4}-\d{2}-\d{2})(?:\s+(\d{1,2}:\d{2}))?", when)
    if iso_date:
        base_day = datetime.fromisoformat(f"{iso_date.group(1)}T00:00:00").replace(tzinfo=tz)
        clock = iso_date.group(2) or "09:00"
        hour, minute = parse_clock(clock)
        resolved = apply_time(base_day, hour, minute)
        return ConversionResult(at_timestamp(resolved), resolved.isoformat(), "iso_date", assumptions)

    tomorrow_explicit = re.fullmatch(r"tomorrow(?:\s+at\s+(.+))?", when)
    if tomorrow_explicit:
        base_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        clock_raw = tomorrow_explicit.group(1)
        if clock_raw:
            hour, minute = parse_clock(clock_raw)
        else:
            hour, minute = 9, 0
            assumptions.append("defaulted missing explicit tomorrow time to 09:00")
        resolved = apply_time(base_day, hour, minute)
        return ConversionResult(at_timestamp(resolved), resolved.isoformat(), "tomorrow", assumptions)

    tomorrow_window = re.fullmatch(r"tomorrow\s+(morning|evening)", when)
    if tomorrow_window:
        window = tomorrow_window.group(1)
        base_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_key = base_day.strftime("%Y-%m-%d")
        seed = f"{when}|{day_key}|{tz.key}"
        if window == "morning":
            minute_of_day = minute_from_window(seed, 8 * 60, 9 * 60)
        else:
            minute_of_day = minute_from_window(seed, 18 * 60, 23 * 60 + 59)
        hour, minute = divmod(minute_of_day, 60)
        resolved = apply_time(base_day, hour, minute)
        return ConversionResult(at_timestamp(resolved), resolved.isoformat(), f"tomorrow_{window}", assumptions)

    weekday_at = re.fullmatch(
        r"(?:next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)(?:\s+at\s+(.+))?",
        when,
    )
    if weekday_at:
        weekday_name = weekday_at.group(1)
        target_day = next_weekday(now, WEEKDAYS[weekday_name]).replace(hour=0, minute=0, second=0, microsecond=0)
        clock_raw = weekday_at.group(2)
        if clock_raw:
            hour, minute = parse_clock(clock_raw)
            resolved = apply_time(target_day, hour, minute)
            return ConversionResult(at_timestamp(resolved), resolved.isoformat(), "weekday_explicit_time", assumptions)

        assumptions.append("defaulted missing weekday time to 09:00")
        resolved = apply_time(target_day, 9, 0)
        return ConversionResult(at_timestamp(resolved), resolved.isoformat(), "weekday_default_time", assumptions)

    weekday_window = re.fullmatch(
        r"(?:next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(morning|evening)",
        when,
    )
    if weekday_window:
        weekday_name = weekday_window.group(1)
        window = weekday_window.group(2)
        target_day = next_weekday(now, WEEKDAYS[weekday_name]).replace(hour=0, minute=0, second=0, microsecond=0)
        day_key = target_day.strftime("%Y-%m-%d")
        seed = f"{when}|{day_key}|{tz.key}"
        if window == "morning":
            minute_of_day = minute_from_window(seed, 8 * 60, 9 * 60)
        else:
            minute_of_day = minute_from_window(seed, 18 * 60, 23 * 60 + 59)
        hour, minute = divmod(minute_of_day, 60)
        resolved = apply_time(target_day, hour, minute)
        return ConversionResult(at_timestamp(resolved), resolved.isoformat(), f"weekday_{window}", assumptions)

    raise ConversionError(
        "Unsupported WHEN phrase. Supported forms: 'in N minutes|hours|days', "
        "'tomorrow [at time]', 'tomorrow morning|evening', "
        "'weekday [at time]', 'weekday morning|evening', 'YYYY-MM-DD [HH:MM]'"
    )


def main() -> None:
    args = parse_args()

    try:
        tz, assumptions = resolve_timezone(args.timezone)
        now = resolve_now(args.now, tz)
        result = convert_when_expression(args.when, now, tz, assumptions)
    except ConversionError as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(1)

    resolved_dt = datetime.fromisoformat(result.resolved_iso)
    if resolved_dt <= now:
        print(json.dumps({"error": "Resolved datetime is not in the future"}))
        raise SystemExit(1)

    print(
        json.dumps(
            {
                "at_timestamp": result.at_timestamp,
                "resolved_iso": result.resolved_iso,
                "rule": result.rule,
                "assumptions": result.assumptions,
            }
        )
    )


if __name__ == "__main__":
    main()
