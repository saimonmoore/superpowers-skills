# {Feature Name} - Manual QA Testing Guide

## Overview

This document defines manual QA test cases for {feature}. It is the source of truth for the QA loop and must be signed off before testing begins.

**Estimated Time**: {estimate}
**Test Case Count**: {count}

---

## Test Environment Setup

### Prerequisites

1. **QA Server / Host**
   - Host: {host}
   - Access: {credentials or VPN}

2. **Testing Tools**
   - MCP tools: {playwright, devtools, or other}
   - If none specified, default to Playwright + DevTools MCP.

3. **Feature Flags**
   - Flags required: {flag names}
   - Enablement steps: {how to enable}

4. **Test URLs / Targets**

| Scenario | URL / Target |
| --- | --- |
| {Scenario 1} | {URL} |
| {Scenario 2} | {URL} |

5. **Test Data / Seed Data**
   - Data sources: {seed scripts, fixtures, accounts}
   - Accounts: {roles, credentials}

6. **Observability**
   - Logs: {where to find}
   - Metrics: {optional}

---

## Testing Strategy

- Run P0 first, then P1, then P2.
- Skip any test case that depends on a failing or blocked case.
- Record PASS/FAIL/BLOCKED directly in this document.

**Priority Levels:**
- **P0**: Critical - must pass before release
- **P1**: High - important functionality
- **P2**: Medium - edge cases, nice to have

---

## Test Cases

### TC-001: {Test Case Title}

**Priority**: P0
**Dependencies**: none

**Preconditions:**
- {precondition}

**Test Steps:**
1. {step 1}
2. {step 2}

**Expected Results:**
- {expected 1}
- {expected 2}

**Actual Results:** [ ] PASS / [ ] FAIL / [ ] BLOCKED
**Evidence:** {logs/screenshots/notes}

---

### TC-002: {Test Case Title}

**Priority**: P1
**Dependencies**: TC-001

**Preconditions:**
- {precondition}

**Test Steps:**
1. {step 1}
2. {step 2}

**Expected Results:**
- {expected 1}

**Actual Results:** [ ] PASS / [ ] FAIL / [ ] BLOCKED
**Evidence:** {logs/screenshots/notes}

---

### Add Additional Test Cases Below

- Ensure each test case includes Priority, Dependencies, Preconditions, Steps, Expected Results, and Actual Results.
- Keep test cases small and focused on one behavior each.
