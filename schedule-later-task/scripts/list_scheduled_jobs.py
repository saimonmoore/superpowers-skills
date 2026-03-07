#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass


@dataclass
class JobInfo:
    job_id: str
    run_at: str
    queue: str
    marker_prefix: str | None
    provider: str | None
    bean_path: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List at jobs with schedule-later-task labels")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def parse_atq_line(line: str) -> tuple[str, str, str] | None:
    match = re.match(r"^(\d+)\s+(.+?)(?:\s+([a-z]))?$", line.strip())
    if not match:
        return None
    queue = match.group(3) or "-"
    return match.group(1), match.group(2), queue


def extract_marker_prefix(script_body: str) -> str | None:
    match = re.search(r'\"\[([^\]]+)\] provider=', script_body)
    return match.group(1) if match else None


def extract_provider(script_body: str) -> str | None:
    match = re.search(r'\] provider=([^\s\"]+)', script_body)
    return match.group(1) if match else None


def extract_bean_path(script_body: str) -> str | None:
    match = re.search(r"(/[^\s]*\.beans/[^\s]*\.md)", script_body)
    if not match:
        return None
    return match.group(1).replace("\\", "")


def list_jobs() -> list[JobInfo]:
    atq = run(["atq"])
    if atq.returncode != 0:
        return []

    jobs: list[JobInfo] = []
    for raw in atq.stdout.splitlines():
        parsed = parse_atq_line(raw)
        if not parsed:
            continue
        job_id, run_at, queue = parsed

        body = run(["at", "-c", job_id]).stdout
        jobs.append(
            JobInfo(
                job_id=job_id,
                run_at=run_at,
                queue=queue,
                marker_prefix=extract_marker_prefix(body),
                provider=extract_provider(body),
                bean_path=extract_bean_path(body),
            )
        )

    return jobs


def print_table(jobs: list[JobInfo]) -> None:
    if not jobs:
        print("No at jobs found")
        return

    print(f"{'JOB':<6} {'RUN_AT':<26} {'MARKER':<28} {'PROVIDER':<10} BEAN")
    for job in jobs:
        marker = job.marker_prefix or "-"
        provider = job.provider or "-"
        bean = job.bean_path or "-"
        print(f"{job.job_id:<6} {job.run_at:<26} {marker:<28} {provider:<10} {bean}")


def main() -> None:
    args = parse_args()
    jobs = list_jobs()

    if args.json:
        print(json.dumps([job.__dict__ for job in jobs]))
    else:
        print_table(jobs)


if __name__ == "__main__":
    main()
