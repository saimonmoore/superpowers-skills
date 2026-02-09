---
name: findings-fixings-browser-qa-loop
description: Use when a user asks to run manual QA in a repeated findings/fixing loop, to create or maintain QA.md and QA_FINDINGS.md for a feature, or to perform browser-based QA (often with Playwright/DevTools) with prioritized, dependency-aware test cases.
---

# Findings Fixings Browser QA Loop

## Overview

Run a disciplined manual QA loop that creates or validates `QA.md`, executes prioritized test cases, records failures in `QA_FINDINGS.md`, fixes issues with re-test evidence, and repeats until all tests pass or the user stops.

## Workflow

### 0. Resolve Inputs

1. Identify the feature key `{feature}` and target path `docs/features/{feature}/QA.md`.
2. Confirm where the feature was implemented (branches/PRs/commits). If unclear, ask the user.

### 1. Ensure QA.md Exists and Is Approved

1. If `docs/features/{feature}/QA.md` exists, read it.
2. If missing, derive requirements from specs and history:
   - Search `docs/`, `documentation/`, `specs/`, `requirements/`, PR descriptions, and commit history.
   - If requirements are still unclear, stop and ask the user for the missing inputs.
3. Generate `docs/features/{feature}/QA.md` using `assets/QA.template.md`.
4. Require a complete **Test Environment Setup** section before testing. It must include:
   - QA server host and access method
   - MCP tool to use for testing (default to Playwright + DevTools MCP if none specified)
   - Feature flags and how to enable them
   - Test URLs/targets
   - Test data/seed data
   - Testing strategy
5. Ask the user to **review and explicitly sign off** on QA.md. Do not start testing until sign-off is received.

### 2. FINDINGS Phase (Manual QA Execution)

**Always re-read this skill at the start of the phase.**

1. Create or update `docs/features/{feature}/QA_FINDINGS.md` using `assets/QA_FINDINGS.template.md`.
2. Select test cases in priority order (P0 -> P1 -> P2).
3. Only test cases that:
   - Are not already PASS
   - Have no dependencies on failing or blocked cases
4. Execute each selected test case with the tools specified in QA.md.
5. Update QA.md with PASS/FAIL/BLOCKED for each executed case.
6. For each FAIL, add a finding to QA_FINDINGS.md with:
   - Test case ID and title
   - Steps to reproduce
   - Expected vs actual behavior
   - Evidence (logs/screenshots if available)
   - Dependencies or blockers
7. End the FINDINGS phase when all non-blocked, untested cases have a definitive PASS/FAIL.

### 3. FIXING Phase (Root Cause and Repair)

**Always re-read this skill at the start of the phase.**

1. Select findings to fix in this order:
   - BLOCKER findings first
   - Higher priority before lower
   - Only findings that do not depend on unresolved issues
2. For each finding:
   - Perform root-cause analysis.
   - If the fix is trivial, implement it.
   - If the fix is complex or risky, propose it and wait for explicit user approval.
3. Re-run the **exact** failing test case.
4. Only when the test passes:
   - Mark the test case PASS in QA.md
   - Remove or resolve the finding in QA_FINDINGS.md
5. If not fixed, update the finding with new details and mark it BLOCKER if it blocks other cases.
6. **Atomic change rule:** When commits are required, commit code changes and QA docs together for each fixed finding. If commits are not requested, keep updates grouped and clearly noted.

### 4. Loop

Repeat FINDINGS and FIXING phases until all test cases in QA.md are PASS or the user explicitly stops the loop.

### 5. Refresh Instruction

After each FINDINGS or FIXING phase, re-read this skill before continuing.

## Artifacts

- `docs/features/{feature}/QA.md` (authoritative test inventory)
- `docs/features/{feature}/QA_FINDINGS.md` (failure log and worklist)
- `assets/QA.template.md` (generic QA template)
- `assets/QA_FINDINGS.template.md` (generic findings template)

## Quick Reference

| Phase | Entry Criteria | Actions | Exit Criteria |
| --- | --- | --- | --- |
| QA.md Setup | Feature identified | Gather requirements, generate QA.md, require environment setup, get sign-off | User signs off on QA.md |
| FINDINGS | QA.md signed off | Execute non-blocked tests by priority, update QA.md, log failures in QA_FINDINGS.md | All non-blocked tests PASS/FAIL |
| FIXING | QA_FINDINGS.md has items | Fix by priority/deps, re-run failing tests, update QA docs | Selected findings attempted with PASS or BLOCKER |
| LOOP | FINDINGS or FIXING completed | Re-read skill, continue next phase | All tests PASS or user stops |

## Example

User: "Please QA automatically in a loop for multi-locations."

1. Resolve `docs/features/multi-locations/QA.md`.
2. If missing, generate from `assets/QA.template.md` and require environment details.
3. Get user sign-off on QA.md.
4. Run FINDINGS: execute P0/P1 tests in the browser, update PASS/FAIL, log failures in QA_FINDINGS.md.
5. Run FIXING: fix highest-priority non-dependent failures, re-test, and update QA docs.
6. Repeat until all tests pass or user stops.

## Common Mistakes

- Starting testing before QA.md exists and is signed off
- Guessing test environment details instead of asking
- Testing cases that depend on unresolved failures
- Marking PASS without re-running the exact test case after a fix
- Forgetting to re-read this skill between phases

## Rationalization Table

| Excuse | Reality |
| --- | --- |
| "We already tested a bit, so skip QA.md" | QA.md is the source of truth and must exist before testing. |
| "I can guess the URL/flags" | Missing environment setup invalidates test results. Ask and confirm. |
| "Fixing easy items first is faster" | Dependency ordering prevents wasted work and false passes. |
| "I fixed it, no need to re-test" | No PASS without re-running the exact test case. |

## Red Flags - STOP and Reset

- No QA.md or no explicit user sign-off
- Environment setup missing host/flags/URLs/test data
- Testing a case that depends on a failing/blocked case
- Marking PASS without re-running the test case
- Continuing after a phase without re-reading this skill
