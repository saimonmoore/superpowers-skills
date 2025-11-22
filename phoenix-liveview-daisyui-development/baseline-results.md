# Baseline Test Results (RED Phase)

## Scenario 1: Profile Form (Time Pressure)
**Agent**: Haiku (general-purpose)
**Time Given**: 30 minutes
**Date**: 2025-11-22

### What They Got RIGHT ✅
1. **Used `to_form` correctly** - Not the deprecated `form_for`
2. **Used `@form` in template** - Not `@changeset`
3. **Used `cond` blocks** - For validation logic (correct pattern)
4. **Proper form structure** - `phx-change`, `phx-submit` events
5. **Loading state** - Properly tracked with `@loading` assign
6. **i18n** - Used `dgettext` throughout

### What They Got WRONG ❌
1. **Component Library Selection**
   - Only mentioned raw DaisyUI classes (`.input`, `.btn`, `.card`)
   - Never mentioned `daisy_ui_components` Elixir library
   - Didn't know there's a LiveView-wrapped component library to prefer
   - **Rationalization**: "Key DaisyUI Classes Used" - focused on CSS classes, not components

2. **No MCP Tool Awareness**
   - Never mentioned looking up component APIs
   - Didn't know how to access DaisyUI docs via code mode MCP tool
   - Made assumptions about what's available

### What WASN'T Tested (Need Template Code)
- Interpolation syntax (`{@value}` vs `<%= @value %>` in attributes)
- Class list syntax (needs `[...]` for multiple classes)
- HEEx-specific patterns
- Mixing onclick and phx-click

### Key Insights for Skill
1. **Component selection is unclear** - Need explicit guidance: daisy_ui_components > raw DaisyUI
2. **MCP tool usage not obvious** - Need to teach: use code mode MCP to look up components
3. **When to use which library** - Need decision tree or quick reference

### Rationalizations to Counter in Skill
- "Key DaisyUI Classes Used" - Focus on CSS classes misses component library
- Assumption that DaisyUI = CSS framework only, not aware of LiveView wrapper

---

## Scenario 2: Modal + Async + Validation (Complexity Pressure)
**Agent**: Haiku (general-purpose)
**Time Given**: 15 minutes
**Date**: 2025-11-22

### What They Got RIGHT ✅
1. **Used assign_async** - Correct async data loading pattern
2. **Form validation** - Implemented inline error display
3. **Responsive intent** - Mentioned mobile/desktop responsiveness
4. **i18n** - Used dgettext throughout

### What They Got WRONG ❌
1. **No Template Code Provided**
   - Claimed implementation complete but didn't show template
   - Can't verify modal placement (inside/outside async_result)
   - Can't verify AsyncResult access pattern
   - Can't verify responsive classes
   - **Rationalization**: "Complete implementation" but missing critical code

2. **Over-Engineered Documentation**
   - Created 5+ documentation files (1,321 lines!)
   - "5-minute setup guide", "Quickstart", "Reference", "Guide", etc.
   - Under time pressure, chose documentation over showing actual patterns
   - **Rationalization**: "Production-ready" but didn't demonstrate key patterns

3. **Modal Placement Unknown**
   - Didn't show whether modal is inside/outside async_result block
   - This is a CRITICAL bug source (modal closes on data refresh)
   - Skill MUST teach this explicitly

4. **AsyncResult Access Pattern Unknown**
   - Didn't demonstrate `.result` unwrapping difference
   - Template vs module access is a common gotcha
   - Skill MUST show both patterns

5. **Responsive Classes Unknown**
   - Mentioned "responsive" but didn't show actual classes
   - `w-full h-full max-h-none sm:w-auto` pattern not demonstrated
   - Skill MUST provide copy-paste pattern

### Critical Patterns NOT Demonstrated
- Modal placement outside `<.async_result>`
- AsyncResult `.result` access in module code
- Native `<dialog>` element with DaisyUI
- Responsive modal classes pattern
- onclick vs phx-click separation

### Rationalizations to Counter in Skill
- "Complete implementation" when template code missing
- "Production-ready" without showing critical patterns
- Over-documenting instead of demonstrating patterns
- Time pressure → documentation instead of code

---

## GREEN Phase Test: Scenario 1 WITH Skill
**Agent**: Haiku (general-purpose)
**Skill**: phoenix-liveview-daisyui-development (loaded)
**Date**: 2025-11-22

### What Changed ✅
1. **Used `to_form` correctly** - Still correct
2. **Used `@form` pattern** - Followed form handling rule
3. **DaisyUI classes** - Used DaisyUI styling

### What DIDN'T Change ❌
1. **Still no daisy_ui_components awareness**
   - Only mentioned raw DaisyUI classes
   - Didn't use MCP tool to check component availability
   - **Rationalization**: "DaisyUI component usage" but meant CSS classes

2. **Still created excessive documentation**
   - 6 documentation files instead of showing patterns
   - **Rationalization**: "Comprehensive documentation" as deliverable
   - Time pressure → docs instead of demonstrating patterns

3. **No MCP tool usage mentioned**
   - Skill says "Use mcp__code-mode tools" but agent didn't
   - Need more explicit instruction on WHEN/HOW

### Key Insight
**The skill prevented form handling errors but didn't change component selection behavior or MCP tool awareness.**

Need to add:
- Rationalization table explicitly countering these excuses
- More explicit WHEN to use MCP tools
- Red flags for over-documentation

---

## REFACTOR Phase Needed
- Add rationalization table
- Add explicit "Before you code" checklist
- Make MCP tool usage more prominent
- Add red flags section
