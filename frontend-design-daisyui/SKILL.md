---
name: frontend-design-daisyui
description: Use when designing interfaces requiring distinctive UI or responsive layouts - applies design thinking before coding with DaisyUI/Tailwind CSS to avoid generic "AI slop" aesthetics through intentional typography, color, and motion choices
---

# Frontend Design with DaisyUI

## Overview

Two-phase approach: design thinking → implementation. Avoid "AI slop" aesthetic (generic fonts, clichéd colors, predictable layouts) through intentional, creative choices. Framework-agnostic patterns for DaisyUI + Tailwind CSS.

## When to Use

**Use for:**
- New pages/components requiring distinctive design
- UI redesigns needing cohesive aesthetics
- Responsive layouts across devices
- Production-grade interfaces

**Skip for:** Quick prototypes, backend-only changes, minor text edits

## Phase 1: Design Thinking

Before coding, define:

**1. Purpose & Flow**: What problem? Mobile vs desktop differences? What makes users return?

**2. Aesthetic Tone**: Pick ONE and commit (brutalist, art deco, organic, luxury minimal, retro-futuristic, cyber punk). Don't hedge - go bold.

**3. Constraints**: Performance budget, accessibility requirements, framework limitations

**4. Differentiation**: What makes THIS interface memorable? How does it surprise and delight?

**Avoid "AI slop":**
- Fonts: Inter, Arial, Roboto (they scream "I didn't think about this")
- Colors: Purple gradients on white backgrounds
- Layouts: Centered grids with even spacing
- Sameness: Every design should look different

**Principle**: Vary themes, fonts, aesthetics completely between projects. No two designs should converge to the same "professional" look.

## Implementation Guidelines

### Typography

Choose distinctive, beautiful fonts that elevate the design.

**Avoid**: Inter, Arial, Roboto, system fonts
**Use**: Custom fonts via Tailwind typography plugin
**DaisyUI customization**: CSS variables `--font-sans`, `--font-serif`

```css
@theme {
  --font-sans: "Author", sans-serif;
  --font-serif: "Crimson Pro", serif;
}
```

### Color & Theme

**Pattern**: Dominant color + sharp accents. NOT even distribution.

Bad: Primary buttons, secondary cards, accent badges (scattered)
Good: Dominant primary throughout, one sharp accent for CTAs

**DaisyUI semantic colors**: `--p` (primary), `--s` (secondary), `--a` (accent), `--n` (neutral)
**Custom themes**: https://daisyui.com/theme-generator/
**Dark mode**: Toggle via `data-theme` attribute

```css
@plugin "../vendor/daisyui-theme" {
  name: "cyberpunk";
  --color-primary: oklch(80% 0.2 330);  /* Hot pink */
  --color-accent: oklch(90% 0.15 120);  /* Acid green */
}
```

### Motion & Animations

**Focus**: High-impact moments (page load with staggered reveals). NOT scattered micro-interactions.

**Strategic**:
- Page load: Stagger elements with `animation-delay`
- Transitions: Major state changes only
- CSS-only: `transition`, `@keyframes`

**Avoid**: Hover effects on every element

```html
<!-- Staggered page load -->
<div class="animate-fade-in [animation-delay:100ms]">Card 1</div>
<div class="animate-fade-in [animation-delay:200ms]">Card 2</div>
<div class="animate-fade-in [animation-delay:300ms]">Card 3</div>
```

### Responsive Layouts

**Mobile-first**: Scale up, not down.

**Grid**: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` (fluid adaptation)
**Breakpoints**: `sm:640px`, `md:768px`, `lg:1024px`, `xl:1280px`
**Modals**: Full-screen mobile → centered desktop

```html
<dialog class="modal">
  <div class="modal-box w-full h-full max-h-none
              sm:w-auto sm:h-auto sm:max-h-[calc(100vh-5em)] sm:max-w-md">
    <!-- Mobile: full screen, Desktop: centered -->
  </div>
</dialog>
```

### Backgrounds & Visual Details

Create atmosphere, not flat surfaces.

**Use**: Layered gradients, geometric patterns, contextual effects
**Avoid**: Solid white, solid gray

```html
<div class="bg-gradient-to-br from-amber-50 to-orange-100
            border-l-4 border-amber-600
            shadow-[0_8px_30px_rgb(251,146,60,0.12)]">
```

### Spatial Composition

**Break the grid**: Asymmetry, overlap, diagonal flow
**Whitespace**: Intentional, not filler
**Hierarchy**: Size, color, position contrasts

## Verification

**Visual Quality**:
- [ ] Typography NOT Inter/Arial/Roboto
- [ ] Dominant color + sharp accent (not even distribution)
- [ ] Strategic motion (staggered page load, not scattered hover)
- [ ] Unexpected composition (asymmetry, not centered grid)
- [ ] Rich details (gradients, shadows, textures)
- [ ] Matches chosen aesthetic tone

**Responsive**:
- [ ] iPhone SE 375px: appropriate full-screen
- [ ] iPad 768px: smooth transitions
- [ ] Desktop 1280px+: centered with max-width
- [ ] Touch targets 44x44px minimum

**Accessibility**:
- [ ] WCAG AA contrast minimum
- [ ] Keyboard navigation works
- [ ] Focus indicators visible

## Quick Reference

**DaisyUI Components**: Button, Card, Modal, Badge, Alert, Loading, Navbar, Drawer, Tabs, Accordion, Table, Dropdown

See https://daisyui.com/components/ for complete list.

## Anti-Patterns

**Generic "AI Slop" Aesthetics**:
- Inter/Roboto/Arial fonts (forgettable)
- Purple gradient on white (clichéd)
- Even color distribution (scattered, not cohesive)
- Hover animations everywhere (scattered, not strategic)
- Centered card grids (predictable)
- "Professional and modern" = safe and generic

**Motion Mistakes**:
- Animations on every hover
- Card lift + icon rotate + number pulse + row highlight = chaos
- "Alive and interactive" ≠ motion everywhere
- Strategic page load > scattered micro-interactions

## Example: Generic vs Distinctive

```html
<!-- ❌ Generic AI Slop -->
<div class="bg-white rounded-lg shadow-md p-6">
  <h2 class="text-2xl font-bold text-gray-900">Dashboard</h2>
  <p class="text-gray-600">Welcome back</p>
</div>

<!-- ✅ Distinctive with Purpose -->
<div class="bg-gradient-to-br from-amber-50 to-orange-100
            border-l-4 border-amber-600 p-8
            shadow-[0_8px_30px_rgb(251,146,60,0.12)]">
  <h2 class="font-display text-3xl tracking-tight text-amber-900">
    Dashboard
  </h2>
  <p class="font-serif text-lg text-amber-800/90 leading-relaxed">
    Welcome back
  </p>
</div>
```

**Differences**:
- Custom fonts (display, serif) vs defaults
- Layered gradient vs solid white
- Border accent vs generic shadow
- Custom shadow with color vs shadow-md
- Intentional hierarchy vs standard sizes
