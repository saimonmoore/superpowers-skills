# Pressure Scenarios for Phoenix LiveView DaisyUI Development Skill

## Scenario 1: Time Pressure + Component Selection
**Pressure Types**: Time constraint, decision paralysis

**Setup**: "You have 30 minutes to build a user profile form with validation. Use DaisyUI components. The form needs: name input, email input, avatar upload, bio textarea, submit button with loading state."

**Expected Baseline Failures** (without skill):
- Uses deprecated form patterns (`form_for` instead of `to_form`)
- Accesses `@changeset` in template instead of `@form`
- Uses `if/else if` in template (syntax error)
- Doesn't know whether to use daisy_ui_components or raw DaisyUI
- Mixes `onclick` and `phx-click` on same button
- Uses wrong class attribute syntax (missing brackets)

**Success Criteria** (with skill):
- Uses `to_form` and `@form[:field]` pattern
- Uses `cond` for multiple conditions
- Chooses daisy_ui_components first, knows when to use MCP tools via code mode
- Separates JavaScript-only and phx-click handlers
- Proper class list syntax with brackets

---

## Scenario 2: Modal + Async + Validation Errors
**Pressure Types**: Complexity, sunk cost, debugging pressure

**Setup**: "Create an edit profile modal that loads user data asynchronously, shows a form, and handles validation errors. The modal should be responsive (full screen on mobile, centered on desktop). When save fails, show errors inline without closing the modal."

**Expected Baseline Failures** (without skill):
- Places modal inside `<.async_result>` block (closes unexpectedly)
- Uses two-way binding on async data
- Doesn't understand AsyncResult access pattern difference (template vs module)
- Missing responsive modal classes
- Form validation errors don't display properly
- Uses wrong interpolation syntax in modal

**Success Criteria** (with skill):
- Places modal outside `<.async_result>` block
- Understands `.result` unwrapping in template vs module
- Uses proper responsive modal class pattern
- Correct form validation pattern
- Proper HEEx syntax throughout

---

## Scenario 3: Interactive List + LiveSvelte Integration
**Pressure Types**: Performance concern, third-party integration, time pressure

**Setup**: "Build a draggable task list with 100+ items. Tasks can be reordered via drag-and-drop (use a Svelte component for the draggable interaction). Tasks can be marked complete, filtered by status, and deleted. The list should use LiveView streams for performance."

**Expected Baseline Failures** (without skill):
- Uses regular assigns instead of streams (memory issues)
- Tries to use `Enum.filter` on stream (not enumerable)
- Uses `bind:` on Svelte draggable component (jumpy behavior)
- Creates 5+ boolean flags trying to manage drag state
- Doesn't implement echo detection for position updates
- Uses `phx-update="append"` (deprecated)
- Missing `phx-update="stream"` on parent
- Wrong stream template syntax

**Success Criteria** (with skill):
- Uses streams with proper template syntax
- Understands stream limitations (not enumerable, needs reset)
- Uses one-way binding for Svelte component
- Implements echo detection pattern
- Recognizes flag proliferation anti-pattern
- Proper stream deletion and filtering

---

## Testing Instructions

### Baseline (RED)
1. Launch subagent without skill loaded
2. Provide scenario setup
3. Give 10 minute time limit for scenario 1, 15 for scenarios 2-3
4. Document exact choices, code patterns, and rationalizations
5. Note specific errors encountered
6. Save verbatim quotes of rationalization

### With Skill (GREEN)
1. Launch new subagent WITH skill loaded
2. Provide same scenario
3. Same time constraints
4. Verify compliance with patterns
5. Check if errors prevented
6. Note any new rationalizations

### Iteration (REFACTOR)
1. For each new rationalization discovered
2. Add explicit counter to skill
3. Re-test scenario
4. Repeat until bulletproof
