---
name: tolaria-save-resource
description: Save something the user has sent (typically from Telegram) as a Resources note in the Tolaria vault at /home/excsm/.openclaw/workspace/code/tolaria, then commit and push. Two modes — URL mode fires when the message contains a URL (a bare URL is enough); text mode fires when the message contains a save phrase like "save this clawd", "for tolaria", "add to vault", "save to tolaria", "make a resource". Use whenever the user is clearly asking to capture something into the vault, not when they're asking a question about it.
---

# Tolaria Save Resource

## Trigger and mode selection

Decide first which mode to run, or whether to run at all.

```
message contains a URL?
├── yes  → URL mode (the URL is the resource, even if save-phrase is also present)
└── no
    ├── message contains a save phrase?  → text mode (the message body is the resource)
    └── otherwise                        → do not fire
```

**Save phrases** (case-insensitive, anywhere in the message): `save this clawd`, `for tolaria`, `add to vault`, `save to tolaria`, `make a resource`, `add to the vault`, and obvious variants.

**Do not fire** when the user is asking a question *about* the content ("can you summarize this?", "is this any good?", "what does this say about X?"). Answer first; only save if they then ask.

If multiple URLs are in one message, run URL mode once per URL.

## Vault layout

Git repo at `/home/excsm/.openclaw/workspace/code/tolaria`. Notes are Markdown files at the vault root with YAML frontmatter and an H1 title. Type values are **plural** (`type: Resources`, `type: Topics`, `type: Projects`, `type: Responsibilities`, `type: Procedures`, `type: Events`). The `URL` property is uppercase. Read the vault's own `AGENTS.md` for full conventions before editing.

## Step 0 — sync the vault (always, both modes)

Before fetching, writing, or anything else, fast-forward the vault from origin so we don't write on top of stale state:

```bash
scripts/pull_vault.sh /home/excsm/.openclaw/workspace/code/tolaria
```

Exit codes:

- `0` — pulled (or already current). Continue.
- `2` — no upstream for current branch. Continue (skip-pull is acceptable in this case; mention it in the final confirmation).
- `1`, `3`, `4` — stop. Report the failure to the user (see "Error handling and replies"). Do not write any file, do not commit.

---

## URL mode

### 1. Fetch the page

Use `WebFetch` (or `mcp__openclaw__web_fetch` if available) on the URL with a prompt like: *"Return the page title on the first line, then a blank line, then exactly 2 to 3 paragraphs (each at least two sentences) summarising what this page is about: who it's for, what it covers, what kind of content / claims / tips it gives. Don't editorialize, don't add headers."*

If the model returns only one paragraph, re-prompt once asking for the missing detail. After a second short response, accept what you have and continue.

If the fetch fails, tell the user once and stop — do not save a stub.

### 2. Check for duplicates

Before doing anything else with the URL, check whether it is already saved:

```bash
scripts/find_duplicate_url.py /home/excsm/.openclaw/workspace/code/tolaria "<the link>"
```

Empty stdout → not a duplicate, continue. One or more filenames printed → the link (or a tracking-stripped, case-insensitive equivalent) is already in the vault. Stop the workflow, tell the user which existing file holds it, and offer to update that note instead of creating a new one. Do not write a new file in that case.

The script normalizes URLs (drops `utm_*`, `gclid`, `fbclid`, etc., the fragment, default ports, and trailing slashes; lowercases scheme and host) and reads both halves of legacy markdown-link `URL` values, so trivial differences are caught.

### 3. Title and filename

- **Title**: page `<title>` / H1, trimmed to **≤ 7 words**. Drop site-name suffixes (" | Acme Blog"), tracking junk, and emoji unless meaningful. Keep human-readable capitalization.
- **Filename**: kebab-case of the title, `.md` extension, e.g. `attention-is-all-you-need.md`. Lowercase, ASCII, hyphens only. If a file with that name exists, append `-2`, `-3`, etc.

### 4. List candidate relationships

```bash
scripts/list_vault_targets.sh /home/excsm/.openclaw/workspace/code/tolaria
```

Prints `# Topics`, `# Projects`, `# Responsibilities`, `# Procedures`, `# Events` sections with `<filename>\t<title>` per line.

- `related_to`: up to **2** Topics whose subject genuinely overlaps with the page. Skip if nothing fits — better empty than forced.
- `belongs_to`: at most **one** Project / Responsibility / Procedure, only if there is a clear obvious fit. Default to omitting it.

Wikilink form is the **filename without extension** (e.g. `[[ai]]`, not `[[AI / ML]]`). YAML list for `related_to`, quoted scalar for `belongs_to`.

### 5. Write the note

Create `<vault>/<filename>.md`:

```markdown
---
type: Resources
URL: "<the link>"
_icon: link
related_to:
  - "[[topic-one]]"
  - "[[topic-two]]"
belongs_to: "[[some-project]]"
---

# <Title (≤ 7 words)>

<2–3 paragraph summary of the page in plain language. What it is, what it argues / shows / offers, and any notable detail (author, date, key claim). Don't editorialize.>

## What could be useful for

<1–2 short paragraphs grounded in the candidate Projects / Responsibilities / Procedures / Events you saw in step 3. Connect concrete dots: "Useful for [[some-project]] because …". If nothing in the vault clearly applies, write one paragraph naming the kinds of work this could feed into, and skip `belongs_to`.>
```

`_icon` is always the literal Phosphor name `link` for URL resources — not a favicon URL.

---

## Text mode

### 1. Extract the content

Strip the trigger phrase from the message; what remains is the **source text**. Examples:

- `save this clawd: ideas about caching layers …` → source text = `ideas about caching layers …`
- `for tolaria — Marek's quote on focus …` → source text = `Marek's quote on focus …`

If the user supplies an explicit title with the pattern `<phrase> "Title here": <body>` or `<phrase> "Title here" <body>`, take the quoted string as the title and the rest as the source text. Otherwise derive the title in step 2.

### 2. Title and filename

- **Title**: if explicitly supplied, use that (still trimmed to ≤ 7 words). Otherwise derive a ≤ 7-word title from the source text — the gist of it, not the first 7 words.
- **Filename**: kebab-case of the title, `.md`. Lowercase, ASCII, hyphens only. Append `-2`, `-3` on collision.

### 3. List candidate relationships

Same as URL mode step 3 — run `scripts/list_vault_targets.sh` and pick `related_to` (up to 2 Topics) and optional `belongs_to`.

### 4. Write the note

Create `<vault>/<filename>.md`:

```markdown
---
type: Resources
_icon: note-pencil
related_to:
  - "[[topic-one]]"
belongs_to: "[[some-project]]"
---

# <Title (≤ 7 words)>

<1–2 sentence summary in your own words — the point of the message.>

> <The source text, verbatim, in a Markdown blockquote.
> Multi-line content keeps the `> ` prefix on every line.>

## What could be useful for

<1–2 short paragraphs grounded in the candidate Projects / Responsibilities / Procedures / Events you saw. Skip `belongs_to` if nothing clearly fits.>
```

Notes for text mode specifically:

- No `URL:` field — omit it entirely.
- `_icon` is `note-pencil` (literal Phosphor name).
- Preserve the source text exactly inside the blockquote (don't fix typos, don't re-flow). If it has its own block-level Markdown (lists, code), keep them inside the quote; nested blockquotes (`>>`) are fine.
- **Multi-paragraph source text**: every line must start with `> `, and paragraph breaks must be a `>` line on its own (no blank line, otherwise Markdown closes the blockquote). Example:

  ```
  > First paragraph of the source text.
  >
  > Second paragraph of the source text.
  ```

---

## Both modes — finish

### Commit and push

From the vault directory:

```bash
scripts/commit_resource.sh /home/excsm/.openclaw/workspace/code/tolaria <filename>.md "<commit message>"
```

Commit message: short imperative, e.g. `Add Attention Is All You Need resource` (URL mode) or `Add note on focus from Marek` (text mode). The script does `git add <file> && git commit -m … && git push`. On push failure, surface the exact error — don't retry blindly, don't `--force`.

### Confirm to the user

One line: filename, title, the topics/container it was linked to (or "no links"), and that the commit pushed. Keep it tight.

## Error handling and replies

The user is talking to this agent through Telegram via the openclaw harness. Whatever final text the agent emits is routed back to them as a Telegram reply — there is no separate "send to telegram" tool to call.

When **any** step of the workflow fails (pull, fetch, dup-check, file write, commit, push), stop the workflow immediately and emit a single, plain message that:

1. Names the step that failed.
2. Includes the underlying error text verbatim (one line is enough; full block if it's helpful).
3. Says what state the vault is in now (file written? committed? still local? rolled back?).
4. Suggests one concrete next step where one is obvious — never invent a remediation.

Don't paper over failures. Don't retry blindly. Don't `--force` anything. Don't keep going with a partial save and pretend it worked.

**Reply templates:**

- Pull failed: `Couldn't sync vault before saving — git pull --ff-only said: "<error>". Nothing was written. Resolve and try again.`
- Fetch failed (URL mode): `Couldn't fetch <url>: <error>. Nothing was written.`
- Duplicate found (URL mode): `Already saved as <existing-file>.md. Want me to update that note instead of creating a new one?`
- Write failed: `Couldn't write <filename>.md: <error>. No commit made.`
- Commit failed: `Wrote <filename>.md but the commit failed: <error>. The file is still on disk — please review.`
- Push failed (commit ok): `Saved and committed as <filename>.md, but push failed: <error>. The commit is local. Run \`git push\` from the vault when you can.`
- No upstream (commit ok, push skipped): `Saved and committed as <filename>.md. No upstream configured, so I didn't push.`

**Success reply** stays one tight line, as before:

> `Saved as <filename>.md ("<title>"), linked to <topics/container or "no links">, committed and pushed.`

## Edge cases

- **URL mode, paywall / login wall**: if the fetch can still yield a real title and meaningful summary, save. If it's just a login screen, tell the user and stop.
- **URL mode, PDF / video / tweet**: save as Resources with the URL; summary describes what's at the link based on whatever metadata is available.
- **Text mode, very short message** (one sentence): summary may be redundant with the source text — write a one-sentence summary that frames *why* the user might have saved it (the gist or the implied question), not just a paraphrase.
- **Text mode, message contains both a URL and a save phrase**: this is URL mode (per the decision tree). The save phrase is just confirmation.
- **Vault dirty**: only stage the new file. The script already does this (no `-A`).
- **No git remote / push disabled**: commit anyway and tell the user push was skipped.
