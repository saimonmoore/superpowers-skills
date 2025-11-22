---
name: phoenix-liveview-daisyui-development
description: Use when building Phoenix LiveView interfaces with DaisyUI/daisy_ui_components, or encountering HEEx syntax errors, form validation issues, modal placement bugs, or Svelte integration problems - provides critical patterns preventing compilation errors and runtime crashes
---

# Phoenix LiveView DaisyUI Development

## Overview

Prevent HEEx compilation errors, LiveView crashes, and integration bugs when building Phoenix LiveView applications with DaisyUI. Access component documentation via **code mode MCP tools** when needed.

## Tailwind v4 Limitation with .ex Files (CRITICAL!)

**Tailwind v4's extractor CANNOT parse HEEx templates embedded in `.ex` files.**

This is a known limitation: [Tailwind discussion #14462](https://github.com/tailwindlabs/tailwindcss/discussions/14462)

**Impact:**
- ✅ Standalone `.heex` files: Classes auto-detected
- ❌ Embedded `~H"""..."""` in `.ex` files: Responsive classes NOT auto-detected
- ⚠️ Non-responsive classes in `.ex` files: Unreliable detection

**REQUIRED: Add responsive utilities to `@source inline()` in `assets/css/app.css`**

### When to Add Classes to @source inline()

**ALWAYS add when using in `.ex` files:**
- All responsive variants (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`)
- Arbitrary values (e.g., `max-h-[calc(100vh-5em)]`)
- Any class that doesn't appear in generated CSS

**Auto-detected (no manual addition):**
- Classes in standalone `.heex` files
- Classes in `.js` and `.svelte` files
- Some non-responsive classes in `.ex` files (unreliable)

### Brace-Expansion Syntax

Use [brace-expansion](https://github.com/tailwindlabs/tailwindcss/pull/17147) to DRY up class generation:

```css
/* assets/css/app.css */

/* Generate flex-row and flex-col for all breakpoints */
@source inline("{sm:,md:,lg:,xl:,2xl:,}flex-{row,col}");

/* Generate items-center, items-start, items-end for all breakpoints */
@source inline("{sm:,md:,lg:,xl:,2xl:,}items-{center,start,end}");

/* Generate margin utilities: mr-2, mr-4, mr-8, ml-2, ml-4, ml-8, etc. */
@source inline("{sm:,md:,lg:,xl:,2xl:,}{m,p}{r,l,t,b,x,y,}-{2,4,8}");

/* Generate width/height utilities */
@source inline("{sm:,md:,lg:,xl:,2xl:,}{w,h}-{auto,full}");
```

**Example workflow:**

1. Add responsive class to LiveView `.ex` file:
   ```elixir
   <div class="sm:grid-cols-3 md:gap-6 lg:px-8">
   ```

2. Add to `assets/css/app.css`:
   ```css
   @source inline("{sm:,md:,lg:,}grid-cols-{1,2,3,4,6,12}");
   @source inline("{md:,lg:,}gap-6");
   @source inline("{lg:,}{p,m}{x,y,}-8");
   ```

3. Rebuild CSS:
   ```bash
   mix tailwind sic
   ```

**Troubleshooting:**
- If responsive classes don't work, check `@source inline()` in `assets/css/app.css`
- Verify in generated CSS: `grep "sm\\:" priv/static/assets/css/app.css`
- See `assets/README.md` for comprehensive setup guide

## Critical HEEx Syntax (Compilation Errors)

**These cause syntax errors - memorize these:**

### Interpolation Rules
```elixir
<%!-- ❌ WRONG - Syntax error --%>
<div id="<%= @id %>">

<%!-- ✅ CORRECT --%>
<div id={@id}>        <%!-- Attributes: use {@value} --%>
  {@text}              <%!-- Tag body: use {@value} --%>
  <%= if @show do %>   <%!-- Block constructs: use <%= %> --%>
    ...
  <% end %>
</div>
```

### Multiple Conditions (No else-if!)
```elixir
<%!-- ❌ FORBIDDEN - else if doesn't exist in Elixir --%>
<%= if @x do %>
<% else if @y do %>  <%!-- Syntax error! --%>

<%!-- ✅ CORRECT - Use cond --%>
<%= cond do %>
  <% @x -> %> ...
  <% @y -> %> ...
  <% true -> %> ...
<% end %>
```

### Class Lists (Must Use Brackets)
```elixir
<%!-- ❌ WRONG - Missing brackets --%>
<div class={"text-white", @active && "bg-blue"}>

<%!-- ✅ CORRECT - Use [...] for multiple classes --%>
<div class={[
  "text-white",
  @active && "bg-blue",
  if(@error, do: "border-red", else: "border-gray")
]}>
```

## Form Handling Anti-Pattern

**FORBIDDEN: Accessing `@changeset` in templates**

```elixir
# ❌ WRONG: <.form for={@changeset}>
# ✅ CORRECT: Use to_form and @form
assign(socket, :form, to_form(changeset))

# Template
<.form for={@form} id="unique-id">
  <.input field={@form[:name]} />
</.form>
```

## Component Selection

**Priority order:**
1. **daisy_ui_components** (Elixir LiveView wrappers) - PREFER THIS
2. **Raw DaisyUI** (CSS framework) - Fallback if not in daisy_ui_components

**Look up via MCP:**
```
Use mcp__code-mode tools to access:
- mcp__daisyui__search_daisyui_documentation
- mcp__daisyui__fetch_daisyui_documentation  

These tell you which components exist in which library.
```

**Quick reference:**
- **daisy_ui_components has**: Button, Modal, Dropdown, Form inputs, Alert, Table, Card, Badge, Accordion
- **Raw DaisyUI only**: Theme controller, Carousel, Chat bubble, Toast, Rating, File input

## Modal Pattern (Critical!)

**MUST place modals outside `<.async_result>` to prevent unexpected closing:**

```elixir
<%!-- ✅ CORRECT --%>
<.async_result :let={data} assign={@user_data}>
  ...
</.async_result>

<dialog id="modal" class="modal">
  <div class="modal-box w-full h-full max-h-none sm:w-auto sm:h-auto sm:max-w-md">
    <h3>Title</h3>
    <button onclick="document.getElementById('modal').close()">Cancel</button>
  </div>
</dialog>

<%!-- Control: onclick="document.getElementById('modal').showModal()" --%>
```

**Responsive classes:** `w-full h-full max-h-none sm:w-auto sm:h-auto sm:max-w-md` (mobile: full screen, desktop: centered)

## AsyncResult Access Pattern

**Template access auto-unwraps `.result`:**
```elixir
<.async_result :let={details} assign={@data}>
  {details.name}  <%!-- Already unwrapped --%>
</.async_result>
```

**Module access requires explicit `.result`:**
```elixir
def handle_event("save", _, socket) do
  data = socket.assigns.data.result  <%!-- Must access .result --%>
end
```

## JavaScript + phx-click Conflict

**FORBIDDEN: Mixing onclick and phx-click causes LiveView crashes**

```elixir
<%!-- ❌ WRONG - Causes crash --%>
<button onclick="modal.showModal()" phx-click="save">

<%!-- ✅ CORRECT - Separate concerns --%>
<button onclick="document.getElementById('modal').showModal()">  <%!-- UI only --%>
<button phx-click="save">                                      <%!-- Server action --%>
```

## LiveView Streams (Performance)

**Required for large collections:**
```elixir
# LiveView
stream(socket, :items, [new_item])                    # Append
stream(socket, :items, all_items, reset: true)        # Filter/reset
stream_delete(socket, :items, item)                   # Delete

# Template - MUST have phx-update="stream" and ids
<div id="items" phx-update="stream">
  <div :for={{id, item} <- @streams.items} id={id}>
    {item.name}
  </div>
</div>
```

**Limitations:**
- NOT enumerable (can't use `Enum.filter`)
- NO count/empty tracking (use separate assign)
- NEVER use deprecated `phx-update="append"`

## Svelte 5 Integration

**Avoid `bind:` on third-party components (causes jumpy interactions):**

```svelte
<!-- ❌ WRONG -->
<Marker bind:lnglat={position} />

<!-- ✅ CORRECT - One-way binding + events -->
<Marker lnglat={[position.lng, position.lat]} ondragend={(e) => {
  position = e.target.getLngLat();
  pushEvent('update', position);
}} />
```

**Echo detection:** Track `lastSent`, compare on prop updates, ignore echoes.
**Red flag:** 3+ boolean flags = architectural problem.

## Quick Reference

| Pattern | Rule |
|---------|------|
| Attribute interpolation | `<div id={@value}>` |
| Multiple conditions | Use `cond`, never `else if` |
| Class lists | `class={["a", @b && "c"]}` |
| Forms | `@form` not `@changeset` |
| Components | daisy_ui_components > raw DaisyUI |
| Modals | Outside `<.async_result>` |
| AsyncResult in module | Explicit `.result` access |
| onclick + phx-click | NEVER mix on same element |
| Streams | `phx-update="stream"` + ids |
| Svelte bind | Avoid on 3rd-party components |
| **Responsive classes in .ex** | **Add to `@source inline()` in app.css** |

## Before You Code Checklist

**STOP and verify:**
- [ ] Did I check daisy_ui_components via MCP tool BEFORE using raw DaisyUI?
- [ ] Am I showing actual template code (not just describing it)?
- [ ] Did I place modals OUTSIDE `<.async_result>` blocks?
- [ ] Am I using `@form` (not `@changeset`) in templates?
- [ ] Did I use `{@value}` for attributes (not `<%= @value %>`)?
- [ ] **Did I add responsive utility classes to `@source inline()` in `assets/css/app.css`?**

## Common Rationalizations (STOP if you think these)

| Excuse | Reality |
|--------|---------|
| "I'll use DaisyUI classes" | Check daisy_ui_components FIRST via MCP tool |
| "DaisyUI component usage" | Distinguish: LiveView wrapper vs CSS classes |
| "Comprehensive documentation" | Show code with patterns, not extensive docs |
| "Complete implementation" | Did you show template with HEEx syntax? |
| "Production-ready" | Did you demonstrate modal placement, AsyncResult access? |
| "I know what's available" | Use MCP tool to verify, don't assume |

## Common Mistakes

1. **"I'll use DaisyUI classes"** → Check daisy_ui_components first via MCP tool
2. **"Complete implementation"** → Did you show template code with patterns?
3. **Modal inside async_result** → Closes unexpectedly on data refresh
4. **"Production-ready" without patterns** → Show AsyncResult access, responsive classes
5. **3+ flags in Svelte** → Rethink architecture, not symptoms
6. **Responsive classes in `.ex` files** → Add to `@source inline()` in `assets/css/app.css`
7. **"Tailwind should auto-detect"** → It can't parse HEEx in `.ex` files, use `@source inline()`

## When to Use MCP Tools

**Use code mode MCP to look up:**
- Which library has which component
- Component props and API
- Advanced patterns and examples

**Don't look up (memorize):**
- HEEx syntax rules
- Form handling pattern
- Modal placement rule
- AsyncResult access difference
