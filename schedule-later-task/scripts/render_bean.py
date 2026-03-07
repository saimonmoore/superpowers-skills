#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render deterministic bean task file")
    parser.add_argument("--what", required=True, help="Task description")
    parser.add_argument("--when", required=True, help="Scheduling phrase")
    parser.add_argument("--cwd", required=True, help="Absolute working directory")
    parser.add_argument("--output-dir", required=True, help="Bean output directory")
    parser.add_argument("--priority", default="normal", choices=["low", "normal", "high", "urgent"], help="Bean priority")
    parser.add_argument("--tags", default="scheduled-task", help="Comma-separated tags")
    parser.add_argument("--fast", action="store_true", help="Use compact checklist")
    parser.add_argument("--json", action="store_true", help="Emit machine JSON output")
    return parser.parse_args()


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    return lowered or "task"


def git_branch(cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def render_content(title: str, when: str, cwd: Path, branch: str, priority: str, tags: list[str], created_at: str, fast: bool) -> str:
    checklist = [
        "- [ ] Review bean context and constraints.",
        "- [ ] Execute implementation steps for the requested task.",
        "- [ ] Run targeted verification and collect evidence.",
    ]
    if not fast:
        checklist.append("- [ ] Prepare delivery artifact (commit/PR/summary) with verification notes.")

    tags_block = "\n".join(f"  - {tag}" for tag in tags)
    checklist_block = "\n".join(checklist)

    return f"""---
title: '{title}'
status: todo
type: task
priority: {priority}
tags:
{tags_block}
created_at: {created_at}
updated_at: {created_at}
---

## Goal
{title}

## Scope
- Requested WHEN: {when}
- Current Working Directory: {cwd}
- Git branch: {branch}

## Checklist
{checklist_block}

## Definition of Done
- Task requirements from this bean are fully implemented.
- Relevant verification checks are executed and results recorded.
- Final output summarizes changes and verification evidence.
"""


def main() -> None:
    args = parse_args()

    cwd = Path(args.cwd).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    title = args.what.strip()
    if not title:
        print(json.dumps({"error": "--what cannot be empty"}))
        raise SystemExit(1)

    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    if not tags:
        tags = ["scheduled-task"]

    slug = slugify(title)[:80]
    hash_seed = f"{args.what}|{args.when}|{cwd}"
    suffix = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()[:8]
    base_name = f"jobs-scheduled--{slug}--{suffix}"

    created_at = iso_utc_now()
    branch = git_branch(cwd)
    content = render_content(title, args.when, cwd, branch, args.priority, tags, created_at, args.fast)

    candidate = output_dir / f"{base_name}.md"
    if candidate.exists():
        existing = candidate.read_text(encoding="utf-8")
        if existing != content:
            index = 1
            while True:
                alt = output_dir / f"{base_name}-{index}.md"
                if not alt.exists():
                    candidate = alt
                    break
                if alt.read_text(encoding="utf-8") == content:
                    candidate = alt
                    break
                index += 1

    candidate.write_text(content, encoding="utf-8")

    result = {
        "bean_path": str(candidate),
        "bean_title": title,
        "created_at": created_at,
        "branch": branch,
        "tags": tags,
    }

    if args.json:
        print(json.dumps(result))
    else:
        print(str(candidate))


if __name__ == "__main__":
    main()
