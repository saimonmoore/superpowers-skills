---
name: prepare-peer-review
description: Plan and structure changes for peer review with manageable PRs and a single staging branch. Use when the user asks to “prepare for peer review” (including close variants like “prep for peer review” or “peer review prep”), to split work into reviewable PRs, set branch/commit strategy, and produce a plan before making changes.
---

# Prepare Peer Review

## Overview

Plan a review-friendly branch/commit/PR structure based on size and semantic boundaries, then wait for approval before any repo mutations.

## Workflow

### 1. Load Config And Repo Signals

- Read defaults from `~/.agent/skills/prepare-peer-review/references/defaults.yaml`.
- If present, merge repo overrides from `.agent/prepare-peer-review.yaml`.
- Detect `.github/PULL_REQUEST_TEMPLATE.md` and record whether it must be used.
- Check if `gh` is available and authenticated; if not, plan manual PR steps.

### 2. Gather Change Intent

- If changes already exist, inspect `git diff` to estimate lines/files.
- If no changes exist, ask for a list of intended tasks or change blocks.
- Group work into semantic change blocks by task intent, layer, or feature.
- Ask clarifying questions when block boundaries are ambiguous.

### 3. Propose PR Boundaries

- Target `optimal_lines` and enforce `max_lines` and `max_files` unless a mechanical exception applies.
- Prefer “one task per PR.”
- If a task is too large, split into smaller tasks before splitting into multiple PRs for the same task.
- Avoid PR chains. If dependencies are unavoidable, set base branches explicitly and call out dependency notes.
- Treat mechanical changes as exceptions (formatting, linting, codemods, or a single change applied to many files).

### 4. Build The Plan (No Changes Yet)

- Propose one staging branch containing all changes (for QA/staging).
- Propose one or more review branches with atomic commits per semantic block.
- Ensure the first commit in each PR includes `first_commit_token` if required.
- Use `.github/PULL_REQUEST_TEMPLATE.md` when present.
- Include ignored checks as configured.
- Summarize expected checks and validate them only after user approval.

### 5. Present And Wait

- Output a structured plan (see template below).
- Ask for approval before creating branches, commits, or PRs.

## Plan Output Template

Use this outline:

1. **Config Summary**: thresholds, exceptions, token rules, staging branch, base branch, PR template
2. **Repo Signals**: PR template found?, gh available?, current diff size?
3. **Staging Branch Plan**: branch name, purpose, whether created
4. **PR Plan** (repeat for each PR): branch name; scope / task summary; estimated size (lines/files); commit grouping (include token rule); base branch and dependency notes; checks to ignore
5. **Approval Request**: ask before any repo mutations

## Heuristics

- Keep PRs under `max_lines` and ideally near `optimal_lines`.
- Prefer fewer files; if many files, justify as mechanical or tightly related.
- Use short, human-reviewable PRs over “giant but isolated” PRs.
- If a PR would exceed limits, propose splitting the task itself.

## Resources

### references/

- `defaults.yaml` for global defaults. Merge `.agent/prepare-peer-review.yaml` if present.
