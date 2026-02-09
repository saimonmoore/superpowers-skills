# {Feature Name} - QA Test Findings

**Test Date:** {date}
**Branch:** {branch}
**Tester:** {name}
**Testing Method:** {tools}

---

## Executive Summary

**Overall Assessment:** {PASS/FAIL/BLOCKER SUMMARY}

| Metric | Value |
| --- | --- |
| Total Test Cases | {count} |
| Tests Executed | {count} |
| Tests Passed | {count} |
| Tests Failed | {count} |
| Tests Blocked | {count} |
| Critical Issues Found | {count} |
| Production Readiness | {status} |

### Key Findings

1. {Finding summary}
2. {Finding summary}

---

## Findings

### DEF-001: {Short Title}

**Severity:** BLOCKER / HIGH / MEDIUM / LOW
**Related Test Case:** TC-001
**Status:** OPEN / FIXED / BLOCKED

**Steps to Reproduce:**
1. {step 1}
2. {step 2}

**Expected Result:**
- {expected}

**Actual Result:**
- {actual}

**Evidence:**
- {logs/screenshots/notes}

**Dependencies / Blockers:**
- {dependency}

---

### DEF-002: {Short Title}

**Severity:** HIGH / MEDIUM / LOW
**Related Test Case:** TC-002
**Status:** OPEN / FIXED / BLOCKED

**Steps to Reproduce:**
1. {step 1}

**Expected Result:**
- {expected}

**Actual Result:**
- {actual}

**Evidence:**
- {logs/screenshots/notes}

**Dependencies / Blockers:**
- {dependency}

---

## Test Execution Summary

| Priority | Total | Executed | Passed | Failed | Blocked |
| --- | --- | --- | --- | --- | --- |
| P0 | {count} | {count} | {count} | {count} | {count} |
| P1 | {count} | {count} | {count} | {count} | {count} |
| P2 | {count} | {count} | {count} | {count} | {count} |

---

## Notes

- Keep findings aligned to QA.md test case IDs.
- Remove or mark findings FIXED only after the exact test case passes.
