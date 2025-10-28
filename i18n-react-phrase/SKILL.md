---
name: i18n-react-phrase
description: Use when adding user-facing text, updating translations, or translation changes aren't syncing in React/TypeScript projects using ICU MessageFormat and Phrase - covers proper push/pull workflow, multi-project configuration, and avoiding translation loss
---

# i18n React + Phrase

## Overview

**This stack uses React-Intl with ICU MessageFormat syntax, managed via Phrase translation platform.**

**Core principle:** Phrase projects merge into shared locale files. Always push to specific tag, then pull ALL projects to avoid losing translations.

## When to Use

**Use this skill when:**
- Adding or updating any user-facing text (form labels, buttons, error messages, validation)
- Translations not appearing after pushing to Phrase
- Translations mysteriously disappearing from locale files
- Working with ICU MessageFormat (plurals, interpolation, select)
- Multi-project Phrase setup (country codes, shared strings, app-specific)

**Don't use for:**
- Non-React i18n (see other i18n skills)
- Single-project Phrase setups (simpler workflow)

## The Iron Law

```
PUSH WITH TAG → PULL ALL PROJECTS → VERIFY BOTH PRESENT
```

**Never skip the pull step. Never.**

## Multi-Project Architecture

Your `.phrase.yml` configures multiple Phrase projects writing to the same locale files:

```yaml
phrase:
  pull:
    targets:
      # Project 1: Jobs B2B (app-specific translations)
      - file: ./packages/core-tools/i18n/locales/en.json
        project_id: 0df41ad30ec55b921117588181f32e7f
        params:
          tags: job-promotion,shared,job_creation,jobs-b2b-frontend-app

      # Project 2: ALL XING (country codes, shared across all apps)
      - file: ./packages/core-tools/i18n/locales/en.json
        project_id: 6d96f77dfdb867677f18dd85119815d3
        params:
          tags: country_tags
```

**Critical:** Both projects write to SAME file. Phrase CLI merges them. If you skip pulling one project, you lose those translations.

## ICU MessageFormat Quick Reference

| Pattern | Syntax | Example |
|---------|--------|---------|
| **Interpolation** | `{variable}` | `"Hello {name}"` |
| **Plural** | `{count, plural, one {...} other {...}}` | `"{count, plural, one {# item} other {# items}}"` |
| **Select** | `{gender, select, male {...} female {...} other {...}}` | `"{gender, select, male {He} female {She} other {They}}"` |
| **Number** | `{value, number}` | `"{price, number, ::currency/USD}"` |
| **Date** | `{date, date, short}` | `"{timestamp, date, long}"` |

**Plural with interpolation:**
```json
{
  "KEY": "You can add up to {remaining} additional {locations, plural, one {location} other {locations}}"
}
```

## The Correct Workflow

### 1. Add Translation Keys to Code

```typescript
// In React component
import { useI18n } from '@core-tools/infrastructure/i18n';

export const MyComponent = () => {
  const { i18n } = useI18n();

  return (
    <div>
      {i18n('MY_NEW_KEY', { count: 5 })}
    </div>
  );
};
```

### 2. Push to Phrase with Specific Tag

**CRITICAL:** Always specify which project/tag you're targeting.

```typescript
// Using Phrase MCP tool
mcp__phrase__phrase_push_translations({
  translations: {
    "MY_NEW_KEY": {
      "en": "You have {count, plural, one {# item} other {# items}}",
      "de": "Sie haben {count, plural, one {# Artikel} other {# Artikel}}"
    }
  },
  tags: "jobs-b2b-frontend-app"  // ← SPECIFIC TAG
})
```

### 3. Pull ALL Projects (MANDATORY)

```bash
# This pulls from ALL configured projects in .phrase.yml
phrase pull
```

**Or via MCP:**
```typescript
mcp__phrase__phrase_pull()  // No parameters = pulls all configured targets
```

### 4. Verify Both Project Translations Present

```bash
# Check your new translations are there
grep "MY_NEW_KEY" packages/core-tools/i18n/locales/en.json

# Check other project translations still there (e.g., country codes)
grep "COUNTRY_DE" packages/core-tools/i18n/locales/en.json
```

**If country codes (or other project translations) are missing:** You skipped the pull step or it failed. Run `phrase pull` again.

## Common Mistakes

| Mistake | Why Bad | Fix |
|---------|---------|-----|
| **Push without tag** | Unclear which Phrase project to target | Always specify tag: `tags: "jobs-b2b-frontend-app"` |
| **Pull only one project** | Loses other project's translations | Use `phrase pull` (no target specified) to pull ALL |
| **Skip pull after push** | Local files out of sync with Phrase | ALWAYS pull after push. No exceptions. |
| **Modify locale files directly** | Changes lost on next pull | Always push to Phrase first, then pull |
| **Forget ICU syntax** | Plurals don't work | Use `{var, plural, one {...} other {...}}` |
| **Don't verify after pull** | Don't notice translations were lost | Always `grep` for both your keys AND other project keys |

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I only changed Jobs B2B, don't need to pull ALL" | ALL projects write to same file. You'll lose country codes. |
| "Pulling takes time, I'll do it later" | Later = production bug when translations missing. Pull takes 10 seconds. |
| "I manually edited the JSON, faster than Phrase" | Next pull overwrites your changes. Always push to Phrase first. |
| "The tag doesn't matter, just pushing" | Wrong project means translations in wrong place or lost. |
| "I checked my new keys, they're there" | Did you check OTHER project's keys still there? |

## Red Flags - STOP

- Editing locale JSON files directly
- Pushing without specifying tag
- Pulling but specifying a target (pulls only one project)
- Not running `phrase pull` after `phrase push`
- Not verifying both projects' translations after pull
- Thinking "I'll pull later when I have time"
- Saying "I verified my keys are there" (did you check OTHER projects?)
- Assuming tag is optional
- Planning a "quick JSON edit" to save time

**Any of these mean: STOP. Delete your changes. Follow the workflow above.**

## ICU Plural Rules

Different languages have different plural forms:

**English** (2 forms):
```json
"{count, plural, one {# item} other {# items}}"
```

**German** (2 forms, but "one" is only for count=1):
```json
"{count, plural, one {# Artikel} other {# Artikel}}"
```

**Arabic** (6 forms!):
```json
"{count, plural, zero {...} one {...} two {...} few {...} many {...} other {...}}"
```

**Always test with count = 0, 1, 2, 5, 100** to verify plural rules.

## Project-Specific Tags

Check `.phrase.yml` to know which tags exist:

**Jobs B2B Project tags:**
- `job-promotion`
- `shared`
- `job-metrics`
- `job_creation`
- `app-header`
- `job-ad-reports`
- `jobs-edition-job-list`
- `jobs-b2b-frontend-app` ← Most common for new features
- `jobs-edition-b2b-recommendations`
- `jobs-edition-candidate-list`

**ALL XING Project tags:**
- `country_tags` ← Country name translations (COUNTRY_DE, COUNTRY_US, etc.)

**When adding translations for a new feature in the main app:** Use `jobs-b2b-frontend-app` tag.

## The Bottom Line

**Multi-project Phrase setups are dangerous.** One wrong move and you lose hundreds of translations.

**The safe workflow:**
1. Push to Phrase with SPECIFIC tag
2. Pull ALL projects (no target specified)
3. Verify BOTH your new keys AND other project keys present

**Skip any step = production bug. Follow the workflow every time.**
