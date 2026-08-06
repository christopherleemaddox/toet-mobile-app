#!/usr/bin/env python3
"""
Extract the real, readable source out of a "DC-runtime" bundled HTML export
(the format Live Build/index.html and App Blueprint/TOET-Blueprint.html are
both built with — recognizable by a <title>Bundled Page</title> loading
shell, a #__bundler_loading element, and __bundler/* script tags).

These files LOOK like a single opaque blob, but the real content is always
findable in two places:

  1. <script type="__bundler/template"> — a JSON-encoded STRING containing
     the actual page's HTML (script tags, DOM, etc). This is where you find
     the reference to the app's own JS bundle by UUID.

  2. A big JSON object earlier in the file, keyed by UUID, of the shape
     {"<uuid>": {"mime": "...", "compressed": true/false, "data": "<base64>"}}
     — this holds every JS/font/image asset. For "compressed": true entries,
     data is base64(gzip(content)); decode + gunzip to get readable source.

Inside the unpacked template HTML, look for:
  <script type="text/x-dc" data-dc-script="">...</script>
This is the actual page-specific application logic (JSX-like), NOT the big
compiled bundle (which is usually a shared "dc-runtime" framework, or —
for a real app like Live Build — a separate DATA file, e.g. window.CATEGORIES
/ window.CARDS). Read the x-dc script first; it's almost always small enough
to read directly and is where screen/component structure actually lives.

Usage:
    python3 extract.py <path-to-bundled.html> <output-dir> <label>

Writes:
    <output-dir>/<label>_template.html   — the unpacked page HTML
    <output-dir>/<label>_dc_script.txt   — the inline app logic (if present)
    <output-dir>/<label>_<uuid8>.<ext>   — every decoded asset (js/html/png/bin)
"""
import sys, os, re, json, base64, gzip


def extract_assets(text, outdir, label):
    starts = [m.start() for m in re.finditer(r'\{"[0-9a-f]{8}-[0-9a-f]{4}-', text)]
    decoder = json.JSONDecoder()
    for s in starts:
        try:
            obj, _ = decoder.raw_decode(text, s)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        count = 0
        for uuid, meta in obj.items():
            if not isinstance(meta, dict) or 'data' not in meta:
                continue
            mime = meta.get('mime', '')
            compressed = meta.get('compressed', False)
            raw = base64.b64decode(meta['data'])
            if compressed:
                try:
                    raw = gzip.decompress(raw)
                except Exception as e:
                    print(f"  gzip fail for {uuid}: {e}")
                    continue
            ext = 'js' if 'javascript' in mime else ('html' if 'html' in mime else ('png' if 'png' in mime else 'bin'))
            outpath = os.path.join(outdir, f"{label}_{uuid[:8]}.{ext}")
            with open(outpath, 'wb') as out:
                out.write(raw)
            print(f"  {uuid[:8]}  {mime:24s} {'compressed' if compressed else 'raw':10s} {len(raw):>8} bytes -> {outpath}")
            count += 1
        print(f"{label}: extracted {count} asset(s)")
        return  # first valid dict is the asset dict; stop after it


def extract_template(text, outdir, label):
    m = re.search(r'<script type="__bundler/template">\s*\n(.*?)\n\s*</script>', text, re.S)
    if not m:
        print(f"{label}: no __bundler/template script found — this file may not be DC-runtime bundled")
        return None
    html = json.loads(m.group(1).strip())
    outpath = os.path.join(outdir, f"{label}_template.html")
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"{label}: wrote unpacked template ({len(html)} chars) -> {outpath}")
    return html


def extract_dc_script(template_html, outdir, label):
    m = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', template_html, re.S)
    if not m:
        print(f"{label}: no inline text/x-dc script found in template")
        return
    outpath = os.path.join(outdir, f"{label}_dc_script.txt")
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(m.group(1))
    print(f"{label}: wrote app logic ({len(m.group(1))} chars) -> {outpath}")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    path, outdir, label = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    print(f"=== {label}: assets ===")
    extract_assets(text, outdir, label)
    print(f"=== {label}: template ===")
    template = extract_template(text, outdir, label)
    if template:
        print(f"=== {label}: app logic ===")
        extract_dc_script(template, outdir, label)
