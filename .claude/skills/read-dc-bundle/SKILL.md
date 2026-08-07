---
name: read-dc-bundle
description: Extract the real, readable source from a "DC-runtime" bundled HTML export — the format Live Build/index.html and App Blueprint/TOET-Blueprint.html are both built in. Use this whenever you need to inspect either file's actual screen structure, component logic, or card data, or any other file in a TOET project with a "Bundled Page" title and a #__bundler_loading element. Without this, the file looks like an opaque 200KB+ blob with no readable content.
---

# Reading a DC-runtime bundled file

Live Build/index.html and App Blueprint/TOET-Blueprint.html were both exported from the same AI app-builder tool. They render fine in a browser, but their actual source is not readable by just opening the file — it's packed as compressed, base64-encoded JSON. Grepping for plain text (screen names, button copy, card content) will mostly come back empty, which looks like the content isn't there. It is — it's just packed.

## The fast path

```bash
python3 "TOET Mobile App/.claude/skills/read-dc-bundle/extract.py" \
  "<path to the bundled .html file>" \
  <output-dir> \
  <a short label>
```

This writes, into `<output-dir>`:
- `<label>_template.html` — the real, unpacked page HTML.
- `<label>_dc_script.txt` — the inline `<script type="text/x-dc">` app logic (screen structure, component definitions, state). **This is almost always the file worth reading first** — it's small (10–70KB) and directly readable.
- `<label>_<uuid8>.js` / `.png` / etc. — every other bundled asset (usually shared framework code like React, or in a real app like Live Build, the actual data — e.g. `window.CATEGORIES` / `window.CARDS` lives in one of these, not in the small template script).

## Why this shape

- `<script type="__bundler/template">` holds the page's real HTML as a JSON-encoded string (escaped `\"`, `\n`). That's the outer shell.
- Elsewhere in the file, a big JSON object keyed by UUID (`{"<uuid>": {"mime": ..., "compressed": true/false, "data": "<base64>"}}`) holds every JS/font/image asset the shell references by `<script src="uuid">`. `compressed: true` means gzip — decode base64, then gunzip.
- Inside the unpacked template, `<script type="text/x-dc" data-dc-script="">` is the actual page-specific logic (JSX-like), separate from the big compiled bundles (which are usually shared framework code, not app content).

## When NOT to bother

If you just need to see what the app *looks like*, open it in the Browser tool instead — it renders normally. Reach for this extraction only when you need the actual source: verifying a claim about what a screen contains, checking whether a feature exists, or syncing the Blueprint against Live Build.

## Writing changes back (not just reading)

There's no visual editor for these files — the only way to change one is a scripted edit that decodes, edits, and re-encodes the `__bundler/template` JSON string. Worked successfully 2026-08-07 removing Mobile App's Account/payment flow. Pattern:

```python
import re, json
raw = open(SRC, encoding='utf-8').read()
m = re.search(r'<script type="__bundler/template">\s*\n(.*?)\n\s*</script>', raw, re.S)
decoded = json.loads(m.group(1).strip())

# Edit with exact-match, uniqueness-checked anchors — never blind regex substitution
def cut(text, start_marker, end_marker, label):
    assert text.count(start_marker) == 1, f"{label}: start not unique"
    assert text.count(end_marker) == 1, f"{label}: end not unique"
    i, j = text.find(start_marker), text.find(end_marker)
    assert i < j, f"{label}: markers out of order"
    return text[:i] + text[j:]   # deletes start_marker..end_marker, keeps end_marker onward

decoded = cut(decoded, "<exact opening tag/anchor>", "<exact next-sibling anchor>", "what this removes")

new_json_text = json.dumps(decoded, ensure_ascii=True)
new_json_text = new_json_text.replace('</', '<\\u002F')   # see gotcha below — do not skip this
new_raw = raw[:m.start(1)] + new_json_text + raw[m.end(1):]
open(SRC, 'w', encoding='utf-8').write(new_raw)
```

**The one gotcha that will silently break the file:** the original encoder escapes every literal `</` in the content to `/` (e.g. `</script>`), specifically so a real `</script>` occurring naturally inside the template's own nested `<script>` tags can't prematurely terminate the *outer* `<script type="__bundler/template">` tag when the browser's HTML parser scans the raw file. `json.dumps()` does not do this by default — it leaves `/` alone. Skipping the `.replace('</', '<\\u002F')` step produces a file that looks fine in a text editor and even round-trips through `json.loads()` correctly in isolation, but fails at runtime in an actual browser with `Bundle unpack error: Unterminated string in JSON` (because the HTML parser cut the script tag short before the JS ever got a chance to JSON.parse it). If you ever see that exact error after an edit, this is almost certainly why.

**A separate trap specific to `<head>` content:** the loader replaces the *entire* `<html>` element with the decoded template once its JS runs (look for `document.documentElement.replaceWith(...)` in the outer shell) — so there are actually two different `<head>`s in the raw file, serving two different audiences:
- The **outer** shell's `<head>` (plain, unescaped HTML near the top of the raw file, editable directly with the normal Edit tool — no JSON dance needed) is all a non-JS client ever sees. This is what search engines and social-media link-preview crawlers (Facebook, Twitter, iMessage, Slack) actually read, since none of them execute JavaScript before scraping `<title>`/OG tags.
- The **inner** template's `<head>` (inside the compressed `__bundler/template` JSON string) is what becomes the *real*, final DOM after the swap — this is what a live user's browser tab title reflects. `document.title` reads empty after the swap if the inner template has no `<title>` of its own, even if the outer shell had one.

If a fix needs to reach real users' browser chrome (tab title) **and** external crawlers (link previews), it has to go in **both** places — confirmed by checking `document.title` in a real browser both before and after the swap, not just by reading the raw file's text.

**Verification checklist before trusting an edit:**
1. `cut()`'s assertions already guarantee each anchor matched exactly once — don't skip them for "obviously unique" text.
2. After all edits, grep the decoded string for anything that should no longer exist (leftover state keys, handler names) — should be empty.
3. Diff the new raw file against the original — everything outside the one `__bundler/template` script tag's content should be byte-identical. If not, something's wrong with the splice.
4. Copy the result to a temp filename inside a browser-reachable folder (files outside the current project root may not load in the Browser tool) and open it on a **fresh tab** — a reused tab can carry over a stale console error from a previous failed attempt and make a working file look broken. Check the console for errors, not just a visual screenshot.
5. Only then overwrite the real file — keep a copy of the pre-edit original somewhere (git history is sufficient; this repo tracks `Live Build/index.html` and `App Blueprint/TOET-Blueprint.html`).
