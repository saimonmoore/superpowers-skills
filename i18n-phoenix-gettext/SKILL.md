---
name: i18n-phoenix-gettext
description: Use when adding user-facing text, form errors, or validation messages in Phoenix/Elixir projects using gettext, or when translations aren't working - covers wrapping strings, extraction, translation automation, and Ash Framework integration
---

# Phoenix Gettext Internationalization

## Overview

**Core principle:** All user-facing strings must be translatable. Never hardcode English text.

This skill covers the complete i18n workflow: wrapping strings → extracting → translating → restarting → verifying across all locales.

## When to Use

Use this skill when:
- Adding UI copy (buttons, labels, messages, help text)
- Creating form validation errors
- Working with Ash resources (custom validations)
- Setting up i18n for a new Phoenix project
- User reports translations not working
- **Reviewing or auditing existing translations** (check for missing subjects and literal translations)
- Translating error messages (must add subjects and translate semantically)

**Critical checks:**
- Before adding ANY user-facing text: "Is this wrapped for translation?"
- Before marking translation work complete: "Did I add subjects to ALL validation errors?"
- Before translating semantic keys: "Am I translating the MEANING or just the words?"

## Quick Reference: The Complete i18n Workflow

```bash
# 1. Wrap strings in code (see Domain Selection Guide below)
dgettext("app", "welcome_message")           # UI copy
dgettext("errors", "username_invalid")        # Custom validation errors

# 2. Extract new strings to .po files
docker compose exec app mix gettext.extract --merge

# 3. Translate strings (CHECK FOR AUTOMATION FIRST!)
./bin/translate-gettext.sh  # If project has automation
# OR manually edit priv/gettext/*/LC_MESSAGES/*.po

# 3a. 🚨 QUALITY CHECK (CRITICAL!)
# - Add subjects to ALL validation errors ("This field..." / "Este campo...")
# - Translate semantic keys meaningfully (not literally!)
# - Review ALL locales together for consistency
# - No underscore-separated translations allowed!

# 4. RESTART app (gettext caches compiled .po files)
docker compose restart app

# 5. Verify in ALL supported locales
# Test via Accept-Language header, locale cookie, or UI switcher
# Verify validation errors show subjects
# Check semantic translations are natural, not literal
```

**Never skip steps 3-5!** Extract alone is incomplete. **Step 3a is MANDATORY for error messages!**

## Domain Selection Guide

Phoenix gettext uses **domains** to organize translations. Choose the right domain:

| Domain | Use For | Examples |
|--------|---------|----------|
| **app** (default) | UI copy, buttons, labels, page text | "Welcome!", "Learn More", "Items in your area" |
| **errors** | Custom validation error messages | "username_invalid", "start_date_past" |
| **ash_errors** | Reusable Ash framework errors | "is required", "is invalid", "length must be..." |
| **auth** | Authentication (if using AshAuthentication) | Provided by library |

### Decision Flowchart

```
Is this an error message?
├─ No → Use "app" domain
└─ Yes → Is this a custom validation?
    ├─ Yes → Use "errors" domain
    └─ No → Ash framework generates it → Use "ash_errors" domain
```

## Wrapping Strings for Translation

### UI Copy (Templates/LiveViews)

```elixir
# ❌ WRONG - Hardcoded English
<h1>Welcome to our sharing community!</h1>
<.button>Learn More</.button>

# ✅ CORRECT - Wrapped for translation
<h1>{gettext("welcome_message")}</h1>
<.button>{gettext("learn_more")}</.button>
```

**Function choice:**
- `gettext(msgid)` - Uses default "app" domain
- `dgettext("domain", msgid)` - Specify domain explicitly

### Semantic msgids vs English-as-key

**Two valid approaches:**

**Option A: English text as msgid** (simpler, works for small apps)
```elixir
gettext("Welcome to our sharing community!")
```
- ✅ Quick to implement
- ❌ Couples code to text, harder to grep

**Option B: Semantic msgids** (recommended for larger apps)
```elixir
dgettext("app", "home.welcome_message")
```
- ✅ Greppable, decoupled, reusable
- ✅ Can change English without touching code
- ❌ Requires maintaining .po files

**Choose based on app size.** Both are valid. Be consistent within a project.

### Custom Validation Errors (Ash Resources)

```elixir
defmodule MyApp.Catalog.Event do
  use Gettext, backend: MyAppWeb.Gettext  # Import at module level

  use Ash.Resource,
    domain: MyApp.Catalog,
    data_layer: AshPostgres.DataLayer

  attributes do
    attribute :capacity, :integer do
      allow_nil?(false)  # Uses ash_errors: "is required"
    end
  end

  validations do
    # Custom validation with custom error message
    validate(fn changeset, _context ->
      capacity = Ash.Changeset.get_attribute(changeset, :capacity)

      if capacity && capacity < 5 do
        {:error,
         field: :capacity,
         message: dgettext("errors", "event_capacity_minimum")}
      else
        :ok
      end
    end)
  end
end
```

**Key pattern:**
1. `use Gettext, backend: YourAppWeb.Gettext` at module top
2. Return `{:error, field: :field_name, message: dgettext("errors", "key")}`
3. Use semantic msgids: `"event_capacity_minimum"` not `"error1"`

## Translation Automation

**🚨 CRITICAL: Check for project automation BEFORE manual translation!**

Many projects automate translation via Google Cloud, DeepL, or translation services.

```bash
# Look for project-specific scripts
ls ./bin/*translate* ./scripts/*translate*

# Common patterns
./bin/translate-gettext.sh           # Google Cloud Translation
./bin/translate.sh                   # DeepL
mix gettext.translate                # Custom mix task
```

**If automation exists:** Use it! Translating 100 strings × 6 languages manually = unsustainable.

**If no automation:** Ask user if translation service is available before doing manual work.

### Manual Translation (Last Resort)

If you must translate manually, follow **translation quality patterns** (see next section).

```bash
# Edit each locale file
vim priv/gettext/es/LC_MESSAGES/app.po
vim priv/gettext/fr/LC_MESSAGES/app.po
# ... repeat for all locales
```

Add translations:
```po
#: lib/my_app_web/live/home_live.ex:12
msgid "welcome_message"
msgstr "¡Bienvenido a nuestra comunidad!"  # Spanish
```

**Do ALL locales immediately.** Don't defer translation "for later."

## Translation Quality Patterns

**🚨 CRITICAL:** These patterns are MANDATORY for all translations.

### Pattern 1: Add Subjects to Form Validation Errors

**Problem:** Ecto/Ash validation messages lack context because `AshPhoenix.FormData.Error` strips field names.

**❌ WRONG - Subject-less translations:**
```po
# errors.po (English)
msgid "can't be blank"
msgstr "can't be blank"

msgid "should have at least %{count} item(s)"
msgstr[0] "should have at least %{count} item"
msgstr[1] "should have at least %{count} items"

msgid "must be less than %{number}"
msgstr "must be less than %{number}"

# errors.po (Spanish)
msgid "can't be blank"
msgstr "no puede estar en blanco"  # Missing subject!
```

**✅ CORRECT - Contextual translations with subjects:**
```po
# errors.po (English)
msgid "can't be blank"
msgstr "This field is required"  # Added subject + clearer wording

msgid "should have at least %{count} item(s)"
msgstr[0] "This field should have at least %{count} item"
msgstr[1] "This field should have at least %{count} items"

msgid "must be less than %{number}"
msgstr "This field must be less than %{number}"

# errors.po (Spanish)
msgid "can't be blank"
msgstr "Este campo es obligatorio"  # Subject + context

msgid "should have at least %{count} item(s)"
msgstr[0] "Este campo debe tener al menos %{count} elemento"
msgstr[1] "Este campo debe tener al menos %{count} elementos"
```

**Subject patterns by language:**
- **English**: "This field..." / "This item..." / "This value..."
- **Spanish**: "Este campo..." / "Este elemento..." / "Este valor..."
- **Catalan**: "Aquest camp..." / "Aquest element..." / "Aquest valor..."
- **French**: "Ce champ..." / "Cet élément..." / "Cette valeur..."
- **German**: "Dieses Feld..." / "Dieses Element..." / "Dieser Wert..."
- **Greek**: "Αυτό το πεδίο..." / "Αυτό το στοιχείο..." / "Αυτή η τιμή..."

**Why:** Without subjects, messages like "is required" or "must be less than 5" are confusing. Always add context.

### Pattern 2: Semantic Translation (Not Literal)

**Problem:** Custom validation keys use semantic msgids, but translations must interpret MEANING, not translate literally.

**❌ WRONG - Literal translation of key:**
```po
# errors.po (English)
msgid "invitation_cannot_invite_yourself"
msgstr "invitation_cannot_invite_yourself"  # Key as translation!

msgid "latitude_out_of_range"
msgstr "latitude_out_of_range"  # Literal key

# errors.po (Spanish)
msgid "invitation_cannot_invite_yourself"
msgstr "invitación_no_puede_invitarse_a_usted_mismo"  # Literal translation of key!

msgid "latitude_out_of_range"
msgstr "latitud_fuera_de_rango"  # Still looks like a key
```

**✅ CORRECT - Semantic interpretation:**
```po
# errors.po (English)
msgid "invitation_cannot_invite_yourself"
msgstr "You cannot invite yourself"  # User-friendly message

msgid "latitude_out_of_range"
msgstr "Latitude must be between -90 and 90"  # Clear, actionable

msgid "start_time_cannot_be_past"
msgstr "Start time cannot be in the past"  # Natural language

# errors.po (Spanish)
msgid "invitation_cannot_invite_yourself"
msgstr "No puedes invitarte a ti mismo"  # Natural Spanish

msgid "latitude_out_of_range"
msgstr "La latitud debe estar entre -90 y 90"  # Clear constraint

msgid "start_time_cannot_be_past"
msgstr "La hora de inicio no puede estar en el pasado"  # Natural
```

**Pattern recognition:**
- If msgid contains underscores → semantic key → translate the MEANING
- Read the key, understand the validation, write natural language
- Use proper articles, pronouns, sentence structure
- Make it helpful (e.g., include valid ranges: "between -90 and 90")

**Common semantic patterns:**
- `field_name_invalid` → "The [field name] format is invalid"
- `something_already_exists` → "This [something] already exists"
- `cannot_do_action` → "You cannot [do action]"
- `must_be_after_X` → "[Field] must be after [X]"
- `out_of_range` → "[Field] must be between X and Y"

### Pattern 3: Consistency Across Locales

**All locales must follow the same patterns:**

```po
# English - Set the pattern
msgid "phone_format_invalid"
msgstr "Phone number format is invalid"

# Spanish - Follow the pattern
msgid "phone_format_invalid"
msgstr "El formato del número de teléfono no es válido"

# French - Follow the pattern
msgid "phone_format_invalid"
msgstr "Le format du numéro de téléphone n'est pas valide"

# German - Follow the pattern
msgid "phone_format_invalid"
msgstr "Das Telefonnummernformat ist ungültig"
```

**Review all locales together** to ensure consistency in:
- Subject usage (all have subjects or all don't)
- Tone (formal vs informal)
- Structure (similar sentence patterns)
- Completeness (no missing translations)

## Ash Framework Integration

### Understanding the Error Flow

```
Ash Validation
    ↓
AshPhoenix.FormData.Error protocol strips field names
    ↓ ("attribute email is required" → "is required")
CoreComponents.translate_error/1
    ↓
Checks domains: ash_errors → errors → fallback
    ↓
Translated error message
```

### Three-Domain Architecture

**Why three domains?**

1. **ash_errors** - Reusable across any Ash project
   - Messages: "is required", "is invalid", "length must be..."
   - Copy these .po files to new projects

2. **errors** - App-specific custom validations
   - Messages: "username_invalid", "event_capacity_minimum"
   - Unique to your application

3. **app** - UI copy (not errors)
   - Messages: "Welcome!", "Learn More", buttons, labels

### translate_error/1 Implementation

Ensure your `core_components.ex` has proper domain fallback:

```elixir
def translate_error({msg, opts}) do
  if count = opts[:count] do
    Gettext.dngettext(MyAppWeb.Gettext, "errors", msg, msg, count, opts)
  else
    # Try ash_errors domain first (framework messages)
    translated = Gettext.dgettext(MyAppWeb.Gettext, "ash_errors", msg, opts)

    # Fall back to errors domain (custom messages)
    if translated == msg do
      Gettext.dgettext(MyAppWeb.Gettext, "errors", msg, opts)
    else
      translated
    end
  end
end
```

**Pattern:** ash_errors → errors → fallback to original message

## Verification Checklist

**Before claiming "i18n is done":**

### Workflow Completeness
- [ ] All user-facing strings wrapped in gettext/dgettext
- [ ] Ran `mix gettext.extract --merge`
- [ ] Translated to ALL supported locales (not just one)
- [ ] Restarted app after .po changes
- [ ] Tested in at least 2 locales (e.g., English + Spanish)
- [ ] Verified via browser (Accept-Language header or locale cookie)
- [ ] Checked that missing translations fall back gracefully

### Translation Quality (🚨 CRITICAL)
- [ ] **All form validation errors have subjects** ("This field is required" not "is required")
- [ ] **Semantic msgids have semantic translations** ("You cannot invite yourself" not "invitation_cannot_invite_yourself")
- [ ] No literal translation of underscore-separated keys
- [ ] Consistent tone and structure across all locales
- [ ] Reviewed all 6 locales together (not one at a time)
- [ ] Error messages are user-friendly and actionable

### Domain Correctness
- [ ] UI copy uses "app" domain
- [ ] Custom validations use "errors" domain
- [ ] Ash framework messages use "ash_errors" domain
- [ ] No domain confusion or mixing

**If you can't check all boxes, work is incomplete.**

## Testing in Multiple Locales

### Method 1: Browser with Accept-Language Header

Chrome DevTools → Network → Right-click request → "Edit and Resend"
```
Accept-Language: es,es-ES;q=0.9,en;q=0.8
```

### Method 2: Locale Cookie

Browser console:
```javascript
document.cookie = "locale=es; path=/; max-age=31536000";
location.reload();
```

### Method 3: Programmatic Test

```elixir
test "displays Spanish translations", %{conn: conn} do
  conn = conn |> put_req_header("accept-language", "es") |> get("/")

  assert html_response(conn, 200) =~ "¡Bienvenido!"
  refute html_response(conn, 200) =~ "Welcome!"
end
```

## Common Mistakes

### ❌ Incomplete Workflow
```bash
# WRONG - Only extracts, doesn't translate or restart
mix gettext.extract --merge
# ... then declares "done"
```

**Fix:** Complete the workflow: extract → translate → restart → verify

### ❌ Wrong Domain
```elixir
# WRONG - Error message in "app" domain
dgettext("app", "username_invalid")

# WRONG - UI copy in "errors" domain
dgettext("errors", "welcome_message")
```

**Fix:** Use domain selection guide above

### ❌ Manual Translation Without Checking for Automation
```bash
# WRONG - Immediately editing .po files manually
vim priv/gettext/es/LC_MESSAGES/app.po
```

**Fix:** Check for `./bin/*translate*` scripts first

### ❌ Not Restarting App
```bash
# Edit .po files but don't restart
# Translations appear not to work!
```

**Fix:** Always restart after .po changes: `docker compose restart app`

### ❌ Testing Only One Locale
```bash
# Only test English, assume others work
curl http://localhost:4000/
```

**Fix:** Test at least 2 locales to catch translation issues

### ❌ Subject-less Form Validation Errors
```po
# WRONG - Missing context
msgid "can't be blank"
msgstr "no puede estar en blanco"  # Spanish

msgid "must be less than %{number}"
msgstr "debe ser inferior a %{number}"  # Spanish
```

**Fix:** Add subjects to provide context
```po
# CORRECT
msgid "can't be blank"
msgstr "Este campo es obligatorio"  # Spanish

msgid "must be less than %{number}"
msgstr "Este campo debe ser inferior a %{number}"  # Spanish
```

### ❌ Literal Translation of Semantic Keys
```po
# WRONG - Literal translation
msgid "invitation_cannot_invite_yourself"
msgstr "invitación_no_puede_invitarse_a_usted_mismo"  # Looks like a key!

msgid "latitude_out_of_range"
msgstr "latitud_fuera_de_rango"  # Still underscore-separated
```

**Fix:** Translate the MEANING, not the words
```po
# CORRECT - Semantic interpretation
msgid "invitation_cannot_invite_yourself"
msgstr "No puedes invitarte a ti mismo"  # Natural Spanish

msgid "latitude_out_of_range"
msgstr "La latitud debe estar entre -90 y 90"  # User-friendly
```

### ❌ Inconsistent Translation Quality Across Locales
```po
# English - Good quality
msgid "phone_format_invalid"
msgstr "Phone number format is invalid"

# Spanish - Missing subject
msgid "phone_format_invalid"
msgstr "formato no válido"  # Incomplete!

# French - Literal key translation
msgid "phone_format_invalid"
msgstr "phone_format_invalide"  # Wrong!
```

**Fix:** Review all locales together for consistency
```po
# All locales following same pattern
# English
msgstr "Phone number format is invalid"
# Spanish
msgstr "El formato del número de teléfono no es válido"
# French
msgstr "Le format du numéro de téléphone n'est pas valide"
```

## Rationalizations to Avoid

| Excuse | Reality |
|--------|---------|
| "I'll manually translate the .po files" | For 6 languages, this is unsustainable. Check for automation first. |
| "Just run gettext.extract and you're done" | Workflow incomplete. Must: extract → translate → restart → verify all locales. |
| "The code is correct" | Mechanics ≠ complete workflow. Did you restart? Test all locales? Check translation quality? |
| "I'll add translations to other languages later" | "Later" never comes. Do all locales now or document why not. |
| "This domain seems right" | Don't guess. Use decision guide: UI copy → app, validation → errors, framework → ash_errors. |
| "Translation is simple/obvious" | Simple for 1 locale ≠ simple for 6 locales × 100 strings. |
| **"The translation matches the English"** | **Not enough! Must add subjects to validation errors and translate semantically.** |
| **"I translated all the words"** | **Literal translation ≠ semantic translation. Interpret the MEANING, not the words.** |
| **"Underscores in Spanish are fine"** | **No! Underscore-separated text = looks like a key = bad UX. Use natural language.** |
| **"Users will understand 'is required'"** | **No subject = confusing. Always add "This field..." / "Este campo..." / etc.** |
| **"I'll review locales individually"** | **Must review ALL locales together to ensure consistency in patterns and quality.** |

## Red Flags - STOP and Reconsider

### Workflow Red Flags
- 🚩 Manually editing multiple .po files (without checking for automation)
- 🚩 Not testing in at least 2 locales
- 🚩 Saying "done" after just `mix gettext.extract`
- 🚩 Not restarting app after .po changes
- 🚩 Guessing which domain to use
- 🚩 Using English text as msgid without discussing trade-offs
- 🚩 Forgetting some languages (if app supports 6, translate all 6)

### Translation Quality Red Flags (🚨 CRITICAL)
- 🚩 **Validation errors without subjects** ("is required" instead of "This field is required")
- 🚩 **Underscore-separated translations** ("latitud_fuera_de_rango" instead of "La latitud debe estar...")
- 🚩 **Literal translation of keys** (translating "invitation_cannot_invite_yourself" word-by-word)
- 🚩 **Inconsistent subjects across locales** (English has subject, Spanish doesn't)
- 🚩 **Only reviewing one locale at a time** (instead of comparing all 6 together)
- 🚩 **Translation that looks like a key** (if it has underscores, it's wrong!)
- 🚩 **Subject-less error messages in any language** (check ALL locales)

**All of these mean: Translation quality is poor. Review "Translation Quality Patterns" section.**

## Project Setup (Reference)

### Gettext Configuration

Typical Phoenix setup in `config/config.exs`:
```elixir
config :my_app, MyAppWeb.Gettext,
  default_locale: "en",
  locales: ~w(en es fr de ca el)
```

### Directory Structure

```
priv/gettext/
  en/LC_MESSAGES/
    app.po          # UI copy
    errors.po       # Custom validation errors
    ash_errors.po   # Ash framework errors (if using Ash)
    auth.po         # Authentication (if using AshAuthentication)
  es/LC_MESSAGES/
    app.po
    errors.po
    ash_errors.po
  # ... other locales
```

### Locale Detection

Common pattern in router:
```elixir
pipeline :browser do
  plug :accepts, ["html"]
  plug MyAppWeb.Plugs.SetLocale  # Detects locale from headers/cookies
  # ...
end
```

## Real-World Impact

**Without this workflow:**
- Users see English when they selected Spanish
- App appears broken in production
- Manual translation becomes bottleneck
- Inconsistent domain usage causes missing translations

**With this workflow:**
- All locales work consistently
- Automation scales to 100+ strings
- Clear domain separation aids debugging
- Verified multi-locale support before deployment
