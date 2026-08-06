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
