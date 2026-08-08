#!/usr/bin/env python3
"""Verify every card's `verse` text and `ref` against a public-domain KJV corpus."""
import re, json, os, unicodedata, difflib

SCRATCH = "/private/tmp/claude-501/-Users-christophermaddox-Documents-Claude-Projects/ad468a19-da65-46ab-9b4c-aa5485b1ce30/scratchpad"
KJV_DIR = f"{SCRATCH}/kjv"

cards = json.load(open(f"{SCRATCH}/cards_live.json", encoding="utf-8"))
print(f"cards: {len(cards)}")

# app book name -> KJV filename stem
FILE = {
    'Psalm': 'Psalms', 'Psalms': 'Psalms', 'Song of Solomon': 'SongofSolomon',
}
for n in ['Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges','Ruth',
          'Ezra','Nehemiah','Esther','Job','Proverbs','Ecclesiastes','Isaiah','Jeremiah',
          'Lamentations','Ezekiel','Daniel','Hosea','Joel','Amos','Obadiah','Jonah','Micah',
          'Nahum','Habakkuk','Zephaniah','Haggai','Zechariah','Malachi','Matthew','Mark',
          'Luke','John','Acts','Romans','Galatians','Ephesians','Philippians','Colossians',
          'Titus','Philemon','Hebrews','James','Jude','Revelation']:
    FILE[n] = n
for pre in ['1','2','3']:
    for bk in ['Samuel','Kings','Chronicles','Corinthians','Thessalonians','Timothy','Peter','John']:
        FILE[f'{pre} {bk}'] = f'{pre}{bk}'

# load corpus
CORPUS = {}
for fn in os.listdir(KJV_DIR):
    if not fn.endswith('.json'):
        continue
    d = json.load(open(os.path.join(KJV_DIR, fn), encoding='utf-8'))
    stem = fn[:-5]
    for ch in d['chapters']:
        c = int(ch['chapter'])
        for v in ch['verses']:
            CORPUS[(stem, c, int(v['verse']))] = v['text']
print(f"corpus verses: {len(CORPUS)}")


def norm(s):
    """Normalize for comparison: unify quotes/dashes, collapse space, strip wrapping quotes."""
    s = unicodedata.normalize('NFKC', s or '')
    s = (s.replace('’', "'").replace('‘', "'")
           .replace('“', '"').replace('”', '"')
           .replace('—', '-').replace('–', '-')
           .replace('…', '...'))
    s = s.strip().strip('"').strip()
    s = re.sub(r'\s+', ' ', s)
    return s


def norm_hard(s):
    """Looser: also drop all punctuation + case, to separate wording changes from punctuation."""
    s = norm(s).lower()
    s = re.sub(r"[^a-z0-9 ]+", '', s)
    return re.sub(r'\s+', ' ', s).strip()


results = {'exact': [], 'punct_only': [], 'wording': [], 'ref_error': []}

for c in cards:
    m = re.match(r'^(.+?)\s+(\d+):(\d+)(?:-(\d+))?$', c['ref'].strip())
    book, chap, v1 = m.group(1).strip(), int(m.group(2)), int(m.group(3))
    v2 = int(m.group(4)) if m.group(4) else v1
    stem = FILE.get(book)
    if not stem:
        results['ref_error'].append({**c, 'why': f'unmapped book "{book}"'})
        continue
    parts, missing = [], []
    for vn in range(v1, v2 + 1):
        t = CORPUS.get((stem, chap, vn))
        if t is None:
            missing.append(vn)
        else:
            parts.append(t)
    if missing:
        results['ref_error'].append({**c, 'why': f'verse(s) not found in KJV: {book} {chap}:{",".join(map(str,missing))}'})
        continue

    ref_text = ' '.join(parts)
    a, b = norm(c['verse']), norm(ref_text)
    if a == b:
        results['exact'].append(c['id'])
    elif norm_hard(a) == norm_hard(b):
        results['punct_only'].append({**c, 'kjv': ref_text})
    else:
        sm = difflib.SequenceMatcher(None, norm_hard(b).split(), norm_hard(a).split())
        ops = [f"{tag}: KJV[{' '.join(norm_hard(b).split()[i1:i2])}] -> APP[{' '.join(norm_hard(a).split()[j1:j2])}]"
               for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != 'equal']
        results['wording'].append({**c, 'kjv': ref_text, 'ratio': round(sm.ratio(), 3), 'diffs': ops[:6]})

print()
print("=" * 60)
print(f"EXACT MATCH (after quote/space normalization): {len(results['exact'])}")
print(f"PUNCTUATION/CAPITALIZATION ONLY:               {len(results['punct_only'])}")
print(f"ACTUAL WORDING DIFFERENCE:                     {len(results['wording'])}")
print(f"REFERENCE ERRORS (bad book/chapter/verse):     {len(results['ref_error'])}")
print("=" * 60)

json.dump(results, open(f"{SCRATCH}/kjv_verify_results.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if results['ref_error']:
    print("\n--- REFERENCE ERRORS ---")
    for r in results['ref_error'][:25]:
        print(f"  #{r['id']} [{r['topic']}] {r['ref']}: {r['why']}")

if results['wording']:
    print(f"\n--- WORDING DIFFERENCES (showing up to 25 of {len(results['wording'])}) ---")
    for r in sorted(results['wording'], key=lambda x: x['ratio'])[:25]:
        print(f"\n  #{r['id']} [{r['topic']}] {r['ref']}  (similarity {r['ratio']})")
        print(f"    APP: {r['verse'][:180]}")
        print(f"    KJV: {r['kjv'][:180]}")
        for d in r['diffs'][:3]:
            print(f"     ~ {d[:150]}")

if results['punct_only']:
    print(f"\n--- PUNCTUATION-ONLY (showing 8 of {len(results['punct_only'])}) ---")
    for r in results['punct_only'][:8]:
        print(f"\n  #{r['id']} {r['ref']}")
        print(f"    APP: {r['verse'][:160]}")
        print(f"    KJV: {r['kjv'][:160]}")
