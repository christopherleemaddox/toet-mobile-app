#!/usr/bin/env python3
"""Find exact and near-duplicate truth/prayer/verse content across all cards."""
import re, json, unicodedata, difflib
from collections import defaultdict, Counter

SCRATCH = "/private/tmp/claude-501/-Users-christophermaddox-Documents-Claude-Projects/ad468a19-da65-46ab-9b4c-aa5485b1ce30/scratchpad"

# reload full card set including truth+prayer
import gzip, base64
raw = open('/Users/christophermaddox/Documents/Claude Projects/TOET Projects/TOET Mobile App/Live Build/index.html', encoding='utf-8').read()
starts = [m.start() for m in re.finditer(r'\{"[0-9a-f]{8}-[0-9a-f]{4}-', raw)]
dec = json.JSONDecoder()
obj = None
for s in starts:
    try:
        o, _ = dec.raw_decode(raw, s)
    except Exception:
        continue
    if isinstance(o, dict) and any(k.startswith('d75f854d') for k in o.keys()):
        obj = o
        break
key = [k for k in obj if k.startswith('d75f854d')][0]
js = gzip.decompress(base64.b64decode(obj[key]['data'])).decode('utf-8')

card_re = re.compile(
    r"\{\s*(?:free:true,\s*)?id:(\d+),\s*topic:'((?:[^'\\]|\\.)*)',\s*cat:'((?:[^'\\]|\\.)*)',\s*ref:'((?:[^'\\]|\\.)*)',\s*"
    r"verse:'((?:[^'\\]|\\.)*)',\s*truth:'((?:[^'\\]|\\.)*)',\s*prayer:'((?:[^'\\]|\\.)*)'\s*\}", re.S)


def un(s):
    return s.replace("\\'", "'").replace('\\\\', '\\').replace('\\n', '\n')


cards = []
for m in card_re.finditer(js):
    cards.append({'id': int(m.group(1)), 'topic': un(m.group(2)), 'cat': un(m.group(3)),
                  'ref': un(m.group(4)), 'verse': un(m.group(5)),
                  'truth': un(m.group(6)), 'prayer': un(m.group(7))})
print(f"cards: {len(cards)}")
json.dump(cards, open(f"{SCRATCH}/cards_full.json", 'w', encoding='utf-8'), ensure_ascii=False)

STOP = set("a an the and or but if of to in on for with is are was were be been am i my me we our you your he she it his her its they them their that this these those as at by from not no so then than there here what which who whom when where how all any both each few more most other some such only own same too very can will just should now do does did doing have has had having would could may might must shall".split())


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = re.sub(r"[^a-z0-9' ]+", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def toks(s):
    return [w for w in norm(s).split() if w not in STOP and len(w) > 2]


def report(field, exact_ok=False):
    print("\n" + "=" * 70)
    print(f"FIELD: {field}")
    print("=" * 70)

    # --- exact duplicates ---
    by_text = defaultdict(list)
    for c in cards:
        by_text[norm(c[field])].append(c)
    exact = {k: v for k, v in by_text.items() if len(v) > 1}
    total_dupe_cards = sum(len(v) for v in exact.values())
    print(f"exact duplicate groups: {len(exact)}  (covering {total_dupe_cards} cards)")
    for k, v in sorted(exact.items(), key=lambda x: -len(x[1]))[:12]:
        ids = ', '.join(f"#{c['id']}({c['topic']})" for c in v)
        print(f"  x{len(v)}: {v[0][field][:110]}")
        print(f"       {ids}")

    # --- near duplicates via inverted index on rare-ish tokens ---
    idx = defaultdict(set)
    tokmap = {}
    for c in cards:
        t = set(toks(c[field]))
        tokmap[c['id']] = t
        for w in t:
            idx[w].add(c['id'])
    # skip very common tokens to keep candidate pairs manageable
    common = {w for w, s in idx.items() if len(s) > 220}
    cand = set()
    for w, s in idx.items():
        if w in common or len(s) < 2:
            continue
        s = sorted(s)
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                cand.add((s[i], s[j]))
    print(f"candidate pairs to score: {len(cand)}")

    byid = {c['id']: c for c in cards}
    near = []
    for a, b in cand:
        ta, tb = tokmap[a], tokmap[b]
        if not ta or not tb:
            continue
        jac = len(ta & tb) / len(ta | tb)
        if jac < 0.5:
            continue
        na, nb = norm(byid[a][field]), norm(byid[b][field])
        if na == nb:
            continue  # already counted as exact
        ratio = difflib.SequenceMatcher(None, na, nb).ratio()
        if ratio >= 0.72:
            near.append((round(ratio, 3), round(jac, 3), a, b))
    near.sort(reverse=True)
    print(f"near-duplicate pairs (>=0.72 similarity, excluding exact): {len(near)}")
    for ratio, jac, a, b in near[:18]:
        ca, cb = byid[a], byid[b]
        same = "SAME TOPIC" if ca['topic'] == cb['topic'] else f"{ca['topic']} / {cb['topic']}"
        print(f"\n  {ratio}  #{a} vs #{b}   [{same}]")
        print(f"    A: {ca[field][:130]}")
        print(f"    B: {cb[field][:130]}")

    return {'exact': {k: [c['id'] for c in v] for k, v in exact.items()}, 'near': near}


out = {}
for f in ['truth', 'prayer', 'verse']:
    out[f] = report(f)

json.dump({k: {'exact': v['exact'], 'near': v['near']} for k, v in out.items()},
          open(f"{SCRATCH}/dupes.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"\n\nsaved -> {SCRATCH}/dupes.json")
