# Proposal: Deterministic Orchestrator for `schedule-later-task`

## Objective
Speed up and harden the scheduling workflow by moving most operational logic from model-driven steps into a single deterministic script.

## Why change
Current flow requires many separate actions (refine, write bean, convert time, verify `at`, schedule, verify output), which increases latency and introduces avoidable variance.

A single orchestrator can:
- reduce tool calls and round trips
- enforce stable behavior across environments
- simplify `SKILL.md` into a short execution contract

## Proposed architecture

### 1) Add a unified entrypoint
Create:
- `schedule-later-task/scripts/schedule_task.py`

This script should perform end-to-end scheduling in one call:
1. Parse args (`--what`, `--when`, `--provider`, `--timezone`, `--cwd`, policy flags)
2. Ensure `.beans/` exists
3. Generate deterministic bean filename slug
4. Render bean content from template
5. Stamp UTC timestamps
6. Convert WHEN -> `at_timestamp`
7. Verify `at` availability
8. Schedule the job
9. Verify job appears in queue (`at -l`)
10. Emit structured result JSON

### 2) Make machine-readable output first-class
All relevant scripts should support deterministic JSON output and stable exit codes.

Target output contract:

```json
{
  "bean_path": "/abs/path/.beans/jobs-...md",
  "at_timestamp": "YYYYMMDDHHMM",
  "provider": "codex",
  "job_id": "27",
  "scheduled_for": "2026-03-07T16:10:00+01:00",
  "warnings": []
}
```

### 3) Deterministic bean rendering
Add:
- `schedule-later-task/scripts/render_bean.py`

Responsibilities:
- enforce valid frontmatter schema
- canonical field ordering
- UTC timestamps
- collision-safe deterministic naming
- no placeholder root keys

### 4) Script-driven confirmation policy
Encode confirmation as a deterministic policy flag instead of free-text interpretation:
- `--require-confirmation always|if-ambiguous|never`
- default: `if-ambiguous`

Ambiguity should be detected by script rules (missing WHAT/WHEN, unsupported WHEN grammar, or policy-defined risky intent markers).

### 5) Explicit timezone strategy
Use deterministic resolution order:
1. `--timezone` arg
2. `TZ` environment variable (if valid IANA)
3. configured default (e.g., `Europe/Madrid`)
4. hard fail with actionable error

This avoids platform-specific local timezone edge cases.

### 6) Fast-path mode
Add `--fast` mode for clear user requests.

`--fast` behavior:
- skip optional repository context refinement
- use compact default bean sections
- still run strict scheduling and verification pipeline

### 7) Single documented command
Skill docs should prefer one canonical command:

```bash
python3 schedule-later-task/scripts/schedule_task.py \
  --what "Find best place in Spain for next solar eclipse" \
  --when "in 5 minutes" \
  --provider codex \
  --timezone Europe/Madrid \
  --cwd "$PWD" \
  --json
```

Then the assistant can return script output directly with minimal post-processing.

### 8) Optional config file
Add:
- `schedule-later-task/config.toml`

Candidate defaults:
- `default_timezone`
- `default_provider`
- `confirmation_mode`
- default bean tags/priority

## Suggested implementation phases

### Phase 1: Core orchestrator
- Implement `schedule_task.py`
- Reuse existing converter and scheduler internals where possible
- Add JSON contract and deterministic exit codes

### Phase 2: Bean renderer
- Implement `render_bean.py`
- Validate frontmatter and section completeness

### Phase 3: Docs simplification
- Update `SKILL.md` and `README.md` to the one-command workflow
- Keep manual fallback instructions in an appendix

### Phase 4: Hardening
- Add tests for:
  - timezone fallback behavior
  - unsupported WHEN handling
  - filename collision handling
  - queue verification failures

## Acceptance criteria
- One command performs create+schedule+verify end-to-end
- Output is deterministic JSON and includes `bean_path`, `at_timestamp`, and `job_id`
- Skill guidance is reduced to a short deterministic runbook
- Manual multi-step path remains available as fallback, not primary

## Expected impact
- Faster execution (fewer tool round-trips)
- Lower variance in behavior between sessions/environments
- Easier maintenance and easier debugging with explicit structured outputs
