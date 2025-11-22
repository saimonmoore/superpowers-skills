# Phoenix LiveView DaisyUI Development Skill

## Summary

This skill prevents HEEx compilation errors, LiveView crashes, and component selection mistakes when building Phoenix LiveView applications with DaisyUI/daisy_ui_components.

## What Was Created

**Files:**
- `SKILL.md` - Main skill document (974 words)
- `test-scenarios.md` - Pressure test scenarios for validation
- `baseline-results.md` - RED/GREEN/REFACTOR test results
- `README.md` - This file

## Skill Creation Process (TDD for Documentation)

### RED Phase (Write Failing Tests)
- Created 3 pressure scenarios combining time pressure, complexity, and decision paralysis
- Ran scenarios WITHOUT skill - documented baseline behavior
- Identified specific rationalizations agents used to avoid correct patterns

**Key Findings:**
- Agents didn't know about daisy_ui_components LiveView wrapper library
- Agents created excessive documentation instead of demonstrating patterns
- Agents didn't use MCP tools to look up component availability
- Agents confused raw DaisyUI CSS classes with daisy_ui_components

### GREEN Phase (Write Minimal Skill)
- Wrote SKILL.md addressing baseline failures
- Focused on:
  - HEEx syntax rules (prevent compilation errors)
  - Form handling pattern (@form not @changeset)
  - Component selection priority (daisy_ui_components > raw DaisyUI)
  - Modal placement (outside async_result)
  - AsyncResult access patterns
  - LiveView streams basics
  - Svelte 5 integration anti-patterns

- Tested with skill loaded - some improvements but still gaps

### REFACTOR Phase (Close Loopholes)
- Added "Before You Code Checklist"
- Added "Common Rationalizations" table with explicit counters
- Made MCP tool usage more prominent
- Added red flags for over-documentation

## Key Patterns Taught

1. **HEEx Syntax** - Prevents compilation errors
2. **Form Handling** - Must use `@form` not `@changeset`
3. **Component Selection** - daisy_ui_components first, use MCP tool via code mode
4. **Modal Placement** - Outside `<.async_result>` to prevent unexpected closing
5. **AsyncResult Access** - `.result` unwrapped in template, explicit in module
6. **Streams** - For large collections with proper template syntax
7. **Svelte Integration** - Avoid `bind:` on third-party components

## MCP Tool Integration

**Critical Note:** The skill teaches that DaisyUI and daisy_ui_components documentation is accessed via **code mode MCP tools**:
- `mcp__daisyui__search_daisyui_documentation`
- `mcp__daisyui__fetch_daisyui_documentation`

These are accessed through the mcp__code-mode tool.

## Testing Notes

### Scenarios Tested
✅ **Scenario 1:** Profile form with time pressure and component selection
✅ **Scenario 2:** Modal with async data and validation (complexity pressure)
⏭️ **Scenario 3:** Streams + Svelte integration (optional, patterns already identified)

### What Improved
- Form handling (@form usage)
- HEEx syntax awareness
- Validation patterns

### What Still Needs Work
- Component library selection (daisy_ui_components vs raw DaisyUI)
- Proactive MCP tool usage
- Avoiding over-documentation under pressure

### Further Testing Recommended
To fully bulletproof this skill:
1. Run Scenario 1 again with REFACTOR changes
2. Test with different agent models (Sonnet, Opus)
3. Add more pressure scenarios if new rationalizations emerge
4. Consider adding specific examples for daisy_ui_components usage

## Word Count

- Target: 700-800 words
- Actual: 974 words
- Justification: Extra ~150 words for rationalization table and checklist necessary based on baseline testing

## CSO (Claude Search Optimization)

**Description format:**
- ✅ Starts with "Use when..."
- ✅ Lists specific triggers/symptoms
- ✅ Written in third person
- ✅ Under 500 characters
- ✅ Includes technology-specific context

**Frontmatter:**
- ✅ Only `name` and `description` fields
- ✅ Name uses letters, numbers, hyphens only
- ✅ Under 1024 characters total

## Usage

The skill is now available in `~/.claude/skills/phoenix-liveview-daisyui-development/` and will be automatically discoverable by Claude Code when relevant patterns are detected.

## Next Steps (Optional)

1. **Test iteration:** Run pressure scenario 1 with REFACTOR changes to verify improvements
2. **Contribute back:** Consider PR to share with community if beneficial
3. **Monitor usage:** Watch for new rationalizations and update skill as needed
4. **Extend:** Add more specific daisy_ui_components examples if pattern emerges
