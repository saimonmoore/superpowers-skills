# Frontend Design DaisyUI - Test Scenarios

## RED Phase: Baseline Testing (Without Skill)

These scenarios test what agents naturally do when asked to create UI with DaisyUI/Tailwind.

### Scenario 1: Generic Design Convergence

**Prompt:**
```
Create a dashboard page using DaisyUI and Tailwind CSS with the following:
- Welcome header
- 4 statistics cards showing metrics (users, revenue, orders, growth)
- Recent activity section
- Make it look professional and modern
```

**Expected baseline behavior:**
- Uses Inter, Arial, or system fonts
- Standard 4-column card grid
- Purple/blue gradient or generic colors
- Centered layout, predictable spacing
- Standard shadow-md on cards

**Measure:**
- Font choices (looking for Inter/Arial/Roboto)
- Color scheme (looking for purple gradients, generic blues)
- Layout predictability (centered grid, even spacing)
- Generic "professional" aesthetic

---

### Scenario 2: Responsive Antipattern

**Prompt:**
```
I have this desktop dashboard design (provide the code from Scenario 1).
Now make it mobile-friendly for phones and tablets.
```

**Expected baseline behavior:**
- Adds `@media` queries to shrink desktop layout
- Uses breakpoints to downsize, not scale up
- Keeps desktop-first mindset
- May add `hidden md:block` without mobile-first thinking

**Measure:**
- Does code start with desktop or mobile styles?
- Are breakpoints scaling up (sm:, md:) or scaling down (@media max-width)?
- Is mobile an afterthought or primary design?

---

### Scenario 3: Color Distribution

**Prompt:**
```
I'm building a project management app with DaisyUI.
Choose a color scheme that makes the interface vibrant and engaging.
Apply colors to buttons, cards, badges, and alerts throughout.
```

**Expected baseline behavior:**
- Even distribution: purple buttons, blue cards, green badges, yellow alerts
- No dominant color + accent pattern
- Uses multiple DaisyUI semantic colors equally
- "Vibrant" interpreted as "many colors"

**Measure:**
- How many different colors used?
- Is there a dominant color with accents, or even distribution?
- Does it feel cohesive or scattered?

---

### Scenario 4: Scattered Motion

**Prompt:**
```
This dashboard feels static. Add animations to make it feel alive and interactive.
Use Tailwind CSS animations and transitions.
```

**Expected baseline behavior:**
- Adds hover effects on every interactive element
- Transition on buttons, cards, links, badges
- Scattered micro-interactions without orchestration
- No focus on page load choreography

**Measure:**
- Are animations strategic (page load) or scattered (every hover)?
- Is there animation-delay used for staggered reveals?
- High-impact moments vs low-impact everywhere?

---

## GREEN Phase: With Skill

Run same scenarios with skill loaded. Expected improvements:

**Scenario 1**: Distinctive font, unique color scheme, unexpected layout
**Scenario 2**: Mobile-first approach from start
**Scenario 3**: Dominant color + sharp accent pattern
**Scenario 4**: Strategic page load animation, minimal hover effects

---

## REFACTOR Phase: Rationalization Tracking

### Scenario 1 Rationalizations (Dashboard Design)
- "Professional and modern" = safe, generic choices
- Used standard DaisyUI semantic colors without customization
- No custom font specified (defaults to theme font)
- Gradient header (from-primary to-secondary) = predictable
- Standard grid layout (grid-cols-1 md:grid-cols-2 lg:grid-cols-4)
- **Key rationalization**: "Professional" equated with "safe and familiar"

### Scenario 2 Rationalizations (Responsive)
- ✅ Actually used mobile-first naturally (grid-cols-1 → sm: → lg:)
- ✅ Progressive enhancement approach
- **Finding**: Modern agents may handle responsive better than expected
- **Note**: Keep responsive guidance but don't overemphasize as anti-pattern

### Scenario 3 Rationalizations (Color Distribution)
- Even distribution: primary, secondary, accent all used equally
- Three stat cards = three different background colors
- "Vibrant and engaging" = use many colors
- Status colors well-chosen but no dominant theme
- **Key rationalization**: "More colors = more visual interest"
- **Missing**: Dominant color + sharp accent pattern

### Scenario 4 Rationalizations (Motion)
- Scattered micro-interactions on EVERY element:
  * Card hover (scale, shadow)
  * Icon hover (rotate, scale)
  * Number hover (scale, pulse)
  * Table row hover (background, scale, shadow)
  * Individual cell transitions
  * Bar hover effects
- **Good**: Did have staggered page load animation
- **Key rationalization**: "Alive and interactive" = animations everywhere
- **Paradox**: Claimed "delight without distraction" while adding 15+ hover animations

---

## Testing Log

### RED Phase - Run 1 (Completed)

**Scenario 1 (Dashboard):**
- ❌ No custom fonts (defaults to theme)
- ❌ Standard DaisyUI semantic colors without customization
- ❌ Predictable gradient header (from-primary to-secondary)
- ❌ Standard grid layout
- ❌ Rationalization: "Professional" = safe choices

**Scenario 2 (Responsive):**
- ✅ Used mobile-first naturally (grid-cols-1 → sm: → lg:)
- ✅ Good responsive approach
- Note: Modern agents handle this well

**Scenario 3 (Colors):**
- ❌ Even distribution: primary, secondary, accent all used equally
- ❌ Three stat cards = three different backgrounds
- ❌ No dominant color + accent pattern
- ❌ Rationalization: "Vibrant = many colors"

**Scenario 4 (Motion):**
- ❌ Scattered animations on EVERY element (15+ hover effects)
- ❌ Card hover, icon hover, number hover, row hover, cell transitions
- ✅ Did have good staggered page load
- ❌ Rationalization: "Alive = animations everywhere"

### GREEN Phase - Expected Improvements (Skill loaded)

**Note**: Subagent testing limitation - skills don't transfer to subagents.
Documenting expected behavior based on skill content:

**Scenario 1 (Dashboard):**
- ✅ Custom fonts via @theme variables
- ✅ Dominant color + sharp accent (not even distribution)
- ✅ Unexpected layout (asymmetry, overlap)
- ✅ Custom gradients/shadows for atmosphere

**Scenario 2 (Responsive):**
- ✅ Already handled well naturally
- ✅ Skill reinforces mobile-first

**Scenario 3 (Colors):**
- ✅ ONE dominant color throughout
- ✅ Sharp accent for CTAs only
- ✅ Cohesive theme, not scattered

**Scenario 4 (Motion):**
- ✅ Strategic page load animation only
- ✅ Minimal/no hover effects
- ✅ High-impact moments, not scattered

### REFACTOR Phase - Skill Content

**Key Counters Added to Skill:**

1. **Anti-Pattern Section** explicitly calls out:
   - Inter/Arial/Roboto = "forgettable"
   - Purple gradients = "clichéd"
   - Even distribution = "scattered, not cohesive"
   - Hover everywhere = "chaos"
   - "Professional and modern" = "safe and generic"

2. **Motion Mistakes Section** with concrete example:
   - "Card lift + icon rotate + number pulse + row highlight = chaos"
   - "Strategic page load > scattered micro-interactions"

3. **Color Pattern** explicitly states:
   - "Dominant color + sharp accents. NOT even distribution."
   - Bad example: "Primary buttons, secondary cards, accent badges (scattered)"
   - Good example: "Dominant primary throughout, one sharp accent for CTAs"

4. **Typography** forcefully states:
   - "Avoid: Inter, Arial, Roboto (they scream 'I didn't think about this')"

**Skill Addresses All Baseline Failures:**
- ✅ Generic fonts → Custom fonts required
- ✅ Even color distribution → Dominant + accent pattern
- ✅ Scattered motion → Strategic page load only
- ✅ Predictable layouts → Break the grid, asymmetry
