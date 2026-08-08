#!/usr/bin/env python3
"""Show the genuinely most-similar pairs regardless of threshold, plus a negative control."""
import re, json, unicodedata, difflib, heapq
from collections import defaultdict

SCRATCH = "/private/tmp/claude-501/-Users-christophermaddox-Documents-Claude-Projects/ad468a19-da65-46ab-9b4c-aa5485b1ce30/scratchpad"
cards = json.load(open(f"{SCRATCH}/cards_full.json", encoding='utf-8'))

STOP = set("a an the and or but if of to in on for with is are was were be been am i my me we our you your he she it his her its they them their that this these those as at by from not no so then than there here what which who whom when where how all any both each few more most other some such only own same too very can will just should now do does did doing have has had having would could may might must shall".split())


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    s = s.replace('’', "'").replace('‘', "'")
    s = re.sub(r"[^a-z0-9' ]+", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def toks(s):
    return [w for w in norm(s).split() if w not in STOP and len(w) > 2]


def top_pairs(field, extra=None, n=20):
    pool = list(cards) + (extra or [])
    idx = defaultdict(set)
    tokmap, normmap = {}, {}
    for c in pool:
        t = set(toks(c[field]))
        tokmap[c['id']] = t
        normmap[c['id']] = norm(c[field])
        for w in t:
            idx[w].add(c['id'])
    common = {w for w, s in idx.items() if len(s) > 220}
    cand = set()
    for w, s in idx.items():
        if w in common or len(s) < 2:
            continue
        s = sorted(s)
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                cand.add((s[i], s[j]))
    heap = []
    for a, b in cand:
        ta, tb = tokmap[a], tokmap[b]
        if not ta or not tb:
            continue
        jac = len(ta & tb) / len(ta | tb)
        if jac < 0.34:      # low prefilter so we see the real tail
            continue
        r = difflib.SequenceMatcher(None, normmap[a], normmap[b]).ratio()
        heapq.heappush(heap, (r, jac, a, b))
        if len(heap) > n:
            heapq.heappop(heap)
    return sorted(heap, reverse=True), len(cand)


byid = {c['id']: c for c in cards}
for field in ['truth', 'prayer']:
    print("\n" + "=" * 74)
    print(f"TOP MOST-SIMILAR PAIRS: {field}   (no threshold, just the highest that exist)")
    print("=" * 74)
    top, ncand = top_pairs(field)
    print(f"(scored {ncand} candidate pairs)")
    for r, jac, a, b in top[:14]:
        ca, cb = byid[a], byid[b]
        tag = "SAME TOPIC" if ca['topic'] == cb['topic'] else f"{ca['topic']} / {cb['topic']}"
        print(f"\n  similarity {r:.3f}  #{a} vs #{b}  [{tag}]")
        print(f"    A: {ca[field]}")
        print(f"    B: {cb[field]}")

# ---- negative control: inject a deliberate near-duplicate and a paraphrase ----
print("\n\n" + "=" * 74)
print("NEGATIVE CONTROL: injecting known duplicates, do we find them?")
print("=" * 74)
src = byid[1]
fakes = [
    {'id': 999001, 'topic': 'FAKE-exact-copy', 'cat': 'mind', 'ref': 'X 1:1',
     'verse': 'x', 'truth': src['truth'], 'prayer': src['prayer']},
    {'id': 999002, 'topic': 'FAKE-light-reword', 'cat': 'mind', 'ref': 'X 1:2',
     'verse': 'x',
     'truth': src['truth'].replace('God has not given me', 'God did not give me'),
     'prayer': src['prayer'].replace('Lord', 'Father')},
]
print(f"  source #1 truth: {src['truth']}")
print(f"  fake 999001    : {fakes[0]['truth']}   (exact copy)")
print(f"  fake 999002    : {fakes[1]['truth']}   (light reword)")

for field in ['truth', 'prayer']:
    top, _ = top_pairs(field, extra=fakes, n=30)
    hits = [(r, a, b) for r, jac, a, b in top if a >= 999000 or b >= 999000]
    print(f"\n  {field}: planted pairs detected = {len(hits)}")
    for r, a, b in hits:
        print(f"    similarity {r:.3f}  #{a} vs #{b}  <-- planted duplicate found")
