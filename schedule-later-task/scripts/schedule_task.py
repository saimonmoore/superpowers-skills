#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RISK_MARKERS = [
    "delete",
    "drop",
    "truncate",
    "production",
    "prod",
    "migration",
    "backfill",
    "security",
    "secret",
    "credential",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic schedule-later orchestrator")
    parser.add_argument("--what", required=True, help="Task to execute later")
    parser.add_argument("--when", required=True, help="Natural language schedule expression")
    parser.add_argument("--provider", default="omp", choices=["codex", "omp"], help="CLI provider")
    parser.add_argument("--timezone", help="IANA timezone")
    parser.add_argument("--cwd", default=os.getcwd(), help="Repository working directory")
    parser.add_argument(
        "--require-confirmation",
        choices=["always", "if-ambiguous", "never"],
        default="if-ambiguous",
        help="Confirmation policy",
    )
    parser.add_argument("--fast", action="store_true", help="Skip optional repo refinement and keep compact bean checklist")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--mail-marker-prefix", default="schedule-later-task", help="Prefix for guaranteed at mail marker line")
    parser.add_argument("--now", help="Fixed current time for deterministic tests")
    return parser.parse_args()


def run_command(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)


def detect_ambiguity(what: str, when: str) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not what.strip():
        reasons.append("missing_what")
    if not when.strip():
        reasons.append("missing_when")

    what_lower = what.lower()
    if any(marker in what_lower for marker in RISK_MARKERS):
        reasons.append("risky_intent")

    return (len(reasons) > 0, reasons)


def parse_job_id(schedule_output: str) -> str | None:
    match = re.search(r"^job\s+(\d+)\s+at\s+", schedule_output, re.MULTILINE)
    return match.group(1) if match else None


def emit(result: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(result))
    else:
        print(json.dumps(result, indent=2))


def main() -> None:
    args = parse_args()

    skill_root = Path(__file__).resolve().parent
    cwd = Path(args.cwd).expanduser().resolve()

    result: dict[str, object] = {
        "status": "error",
        "requires_confirmation": False,
        "bean_path": None,
        "at_timestamp": None,
        "provider": args.provider,
        "job_id": None,
        "scheduled_for": None,
        "warnings": [],
        "assumptions": [],
        "errors": [],
        "mail_marker_prefix": args.mail_marker_prefix,
    }

    if not cwd.exists() or not cwd.is_dir():
        result["errors"] = [f"Invalid cwd: {cwd}"]
        emit(result, args.json)
        raise SystemExit(1)

    beans_dir = cwd / ".beans"
    beans_dir.mkdir(parents=True, exist_ok=True)

    render_cmd = [
        sys.executable,
        str(skill_root / "render_bean.py"),
        "--what",
        args.what,
        "--when",
        args.when,
        "--cwd",
        str(cwd),
        "--output-dir",
        str(beans_dir),
        "--json",
    ]
    if args.fast:
        render_cmd.append("--fast")

    rendered = run_command(render_cmd)
    if rendered.returncode != 0:
        result["errors"] = [rendered.stdout.strip() or rendered.stderr.strip() or "bean_render_failed"]
        emit(result, args.json)
        raise SystemExit(1)

    bean_data = json.loads(rendered.stdout)
    result["bean_path"] = bean_data["bean_path"]
    bean_name = Path(str(result["bean_path"])).name

    ambiguous, ambiguity_reasons = detect_ambiguity(args.what, args.when)
    if args.require_confirmation == "always" or (args.require_confirmation == "if-ambiguous" and ambiguous):
        result["status"] = "needs_confirmation"
        result["requires_confirmation"] = True
        result["warnings"] = ["confirmation_required", *ambiguity_reasons]
        emit(result, args.json)
        raise SystemExit(2)

    convert_cmd = [
        sys.executable,
        str(skill_root / "convert_when_to_at_timestamp.py"),
        "--when",
        args.when,
    ]
    if args.timezone:
        convert_cmd.extend(["--timezone", args.timezone])
    if args.now:
        convert_cmd.extend(["--now", args.now])

    converted = run_command(convert_cmd)
    if converted.returncode != 0:
        result["errors"] = [converted.stdout.strip() or converted.stderr.strip() or "when_conversion_failed"]
        emit(result, args.json)
        raise SystemExit(1)

    conversion_data = json.loads(converted.stdout)
    result["at_timestamp"] = conversion_data["at_timestamp"]
    result["scheduled_for"] = conversion_data["resolved_iso"]
    result["assumptions"] = conversion_data.get("assumptions", [])

    verify = run_command(["bash", str(skill_root / "verify_at.sh")])
    if verify.returncode != 0:
        result["errors"] = [verify.stdout.strip() or verify.stderr.strip() or "at_verification_failed"]
        emit(result, args.json)
        raise SystemExit(1)

    prompt = (
        f"Complete the {result['bean_path']} in {cwd}. "
        "Run required verification before reporting done."
    )

    scheduled = run_command(
        [
            "bash",
            str(skill_root / "schedule_with_at.sh"),
            str(result["at_timestamp"]),
            prompt,
            args.provider,
            args.mail_marker_prefix,
            bean_name,
        ]
    )
    schedule_output = (scheduled.stdout + scheduled.stderr).strip()
    if scheduled.returncode != 0:
        result["errors"] = [schedule_output or "scheduling_failed"]
        emit(result, args.json)
        raise SystemExit(1)

    job_id = parse_job_id(schedule_output)
    if not job_id:
        result["errors"] = ["scheduled but job id parsing failed", schedule_output]
        emit(result, args.json)
        raise SystemExit(1)

    result["status"] = "scheduled"
    result["job_id"] = job_id
    result["schedule_output"] = schedule_output

    emit(result, args.json)


if __name__ == "__main__":
    main()
