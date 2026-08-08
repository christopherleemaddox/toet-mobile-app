#!/usr/bin/env python3
"""
TOET Mobile App preflight — runs automatically after Live Build/index.html or
App Blueprint/TOET-Blueprint.html is written, and can be run by hand any time.

It answers one question: did that edit quietly break something?

DESIGN RULE, learned the hard way: every check prints what it actually READ
(path, byte size, real counts). A checker that silently examines the wrong
file, or parses zero records, will otherwise report a confident PASS and
prove nothing. A pass you cannot trace to real numbers is worse than a fail.

Counts are compared against baseline.json rather than hardcoded, so growing
the card library is a deliberate two-line commit (change the app, change the
baseline) instead of a silent drift nobody notices.

Usage:
    python3 preflight.py <file> [<file> ...]
    python3 preflight.py --all          # both tracked files
Exit code 0 = all passed, 1 = something failed.
"""
import sys, os, re, json, base64, gzip, collections

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.abspath(os.path.join(HERE, '..', '..'))
LIVE = os.path.join(APP, 'Live Build', 'index.html')
BLUEPRINT = os.path.join(APP, 'App Blueprint', 'TOET-Blueprint.html')
BASELINE = os.path.join(HERE, 'baseline.json')

RED, GRN, YEL, DIM, OFF = '\033[31m', '\033[32m', '\033[33m', '\033[2m', '\033[0m'
fails, checks = [], [0]


def ok(msg):
    checks[0] += 1
    print(f"  {GRN}pass{OFF}  {msg}")


def bad(msg):
    checks[0] += 1
    fails.append(msg)
    print(f"  {RED}FAIL{OFF}  {msg}")


def read_template(path):
    """Decode the __bundler/template JSON string, and return the raw encoded
    block alongside it so the escaping can be checked separately."""
    raw = open(path, encoding='utf-8').read()
    m = re.search(r'<script type="__bundler/template">\s*\n(.*?)\n\s*</script>', raw, re.S)
    if not m:
        raise ValueError('no __bundler/template block found')
    block = m.group(1).strip()
    return raw, json.loads(block), block


def check_encoding(block):
    """The bug json.loads CANNOT see.

    The original encoder escapes every literal `</` inside the template to
    `<\\u002F`. That is not for JSON's benefit — `</` is perfectly legal
    inside a JSON string, so json.loads accepts the unescaped version
    happily. It is for the BROWSER's HTML parser, which scans the raw file
    first and will end the outer <script> tag early the moment it meets a
    literal `</script>`, truncating the JSON before any JS runs.

    So a file that round-trips fine through Python can still be dead on
    arrival in a browser with "Unterminated string in JSON". Checking that
    the encoded block contains zero literal `</` is the only way to catch
    it without opening a browser. Verified by selftest, which plants
    exactly this defect."""
    n = block.count('</')
    if n == 0:
        ok('template escaping intact (no literal "</" — the bug json.loads cannot see)')
    else:
        bad(f'{n} literal "</" in the encoded template. The browser HTML parser will cut '
            f'the script tag short and the app will die with "Unterminated string in JSON". '
            f'Re-encode with .replace("</", "<\\\\u002F")')


def parse_cards(js):
    start = js.index('window.CARDS')
    block = js[start:js.index('\n];', start)]
    cards = []
    for chunk in re.split(r'\n\s*\{', block)[1:]:
        def g(f):
            mm = re.search(r"\b%s:'((?:[^'\\]|\\.)*)'" % f, chunk)
            return mm.group(1) if mm else ''
        mid = re.search(r'\bid:(\d+)', chunk)
        cards.append({'id': int(mid.group(1)) if mid else -1, 'topic': g('topic'),
                      'cat': g('cat'), 'verse': g('verse'),
                      'truth': g('truth'), 'prayer': g('prayer')})
    return cards


def find_card_asset(raw):
    """Assets are keyed by UUID and the card-data UUID changes if the app is
    ever re-exported, so find it by content, never by remembering the id.

    More than one asset MENTIONS window.CARDS (the search index reads it), so
    matching on the name alone picks a 10KB helper and reports zero cards.
    Every candidate is parsed and the one yielding the most cards wins."""
    dec = json.JSONDecoder()
    best = (None, None, -1)
    for s in [m.start() for m in re.finditer(r'\{"[0-9a-f]{8}-[0-9a-f]{4}-', raw)]:
        try:
            obj, _ = dec.raw_decode(raw, s)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        for uuid, meta in obj.items():
            if not isinstance(meta, dict) or 'data' not in meta:
                continue
            try:
                data = base64.b64decode(meta['data'])
                if meta.get('compressed'):
                    data = gzip.decompress(data)
                text = data.decode('utf-8', 'replace')
            except Exception:
                continue
            if 'window.CARDS' not in text:
                continue
            try:
                n = len(parse_cards(text))
            except Exception:
                n = 0
            if n > best[2]:
                best = (uuid, text, n)
    return (best[0], best[1]) if best[2] > 0 else (None, None)


# ---------------------------------------------------------------- Live Build
def check_live(path, base):
    print(f"\n{DIM}reading{OFF} {path}")
    raw, tpl, block = read_template(path)
    print(f"  {DIM}{len(raw):,} bytes on disk · template decoded to {len(tpl):,} chars{OFF}")
    ok('bundle template decodes as JSON')
    check_encoding(block)

    uuid, js = find_card_asset(raw)
    if not js:
        bad('card-data asset not found — cannot check any card content')
        return
    print(f"  {DIM}card asset {uuid[:8]} · {len(js):,} chars{OFF}")

    cards = parse_cards(js)
    topics = {c['topic'] for c in cards}
    print(f"  {DIM}parsed {len(cards)} cards across {len(topics)} topics{OFF}")

    if len(cards) == 0:
        bad('parsed ZERO cards — the parser is broken, every check below is meaningless')
        return
    for label, got, want in (('cards', len(cards), base['cards']),
                             ('topics', len(topics), base['topics'])):
        if got == want:
            ok(f'{label}: {got} (matches baseline)')
        else:
            bad(f'{label}: {got}, baseline says {want}. If deliberate, update '
                f'{os.path.relpath(BASELINE, APP)} in the same commit')

    empties = [c['id'] for c in cards if not c['truth'] or not c['prayer']]
    ok('every card has a truth and a prayer') if not empties else \
        bad(f'{len(empties)} card(s) missing truth or prayer: {empties[:8]}')

    dashes = [c['id'] for c in cards if any(d in c['truth'] + c['prayer'] for d in '—–')]
    ok('no em/en dashes in card copy (Humalingo rule)') if not dashes else \
        bad(f"{len(dashes)} card(s) with em/en dashes: {dashes[:8]}")

    straight = [c['id'] for c in cards if "'" in c['truth'] + c['prayer']]
    ok('no straight apostrophes in card copy (curly only)') if not straight else \
        bad(f"{len(straight)} card(s) with straight apostrophes: {straight[:8]}")

    amen = [c['id'] for c in cards if not c['prayer'].rstrip().endswith('Amen.')]
    ok('every prayer ends "Amen."') if not amen else \
        bad(f'{len(amen)} prayer(s) do not end "Amen.": {amen[:8]}')

    # regression guards: features that must not silently vanish from the template
    for label, needle in base['must_contain'].items():
        ok(f'still present: {label}') if needle in tpl else \
            bad(f'MISSING from the app: {label}  (looked for {needle!r})')


# ----------------------------------------------------------------- Blueprint
def check_blueprint(path):
    print(f"\n{DIM}reading{OFF} {path}")
    raw, tpl, block = read_template(path)
    print(f"  {DIM}{len(raw):,} bytes on disk · template decoded to {len(tpl):,} chars{OFF}")
    ok('blueprint template decodes as JSON')
    check_encoding(block)

    leg = re.search(r'LEG = \{(.*?)\n  \};', tpl, re.S)
    if not leg:
        bad('LEG legend object not found — cannot check codes')
        return
    screens = re.findall(r'\n    (\w+): \[(.*?)\n    \],', leg.group(1), re.S)
    owners = collections.defaultdict(list)
    for name, body in screens:
        for cid, label, _d in re.findall(r"\['([^']+)','((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)'\]", body):
            owners[cid].append((name, label))
    print(f"  {DIM}parsed {len(owners)} codes across {len(screens)} screens{OFF}")

    if not owners:
        bad('parsed ZERO codes — parser broken, checks below prove nothing')
        return

    # a code claimed twice with DIFFERENT names silently overwrites; identical
    # repeats (TB / Tab Bar) are deliberate and fine
    clash = {c: v for c, v in owners.items() if len({l for _s, l in v}) > 1}
    ok(f'no duplicate codes across screens ({len(owners)} codes checked)') if not clash else \
        bad('duplicate codes, later screen silently wins: ' +
            '; '.join(f"{c} ({', '.join(s + '/' + l for s, l in v)})" for c, v in clash.items()))

    # every legend code needs a clickable region, and every region a legend entry
    handlers = set(re.findall(r'p_([A-Z]+\d*) ', tpl))
    legend = set(owners)
    orphan_leg = sorted(legend - handlers - {'TB'})
    orphan_mock = sorted(handlers - legend)
    ok('every legend code has a clickable region in the mockup') if not orphan_leg else \
        bad(f'legend codes with no clickable region: {orphan_leg}')
    ok('every clickable region has a legend entry') if not orphan_mock else \
        bad(f'mockup regions with no legend entry: {orphan_mock}')

    sc = re.search(r'SCREENS = \[(.*?)\];', tpl, re.S)
    if sc:
        listed = [k for k, _l in re.findall(r"\['(\w+)','([^']*)'\]", sc.group(1))]
        missing = [k for k, _b in screens if k not in listed]
        extra = [k for k in listed if k not in {n for n, _b in screens}]
        ok(f'screen tabs and legend agree ({len(listed)} screens)') if not (missing or extra) else \
            bad(f'screen list mismatch — in legend but no tab: {missing}; tab but no legend: {extra}')

    ok('self-check banner still wired into the Blueprint') if 'hasClash' in tpl else \
        bad('the Blueprint duplicate-code self-check has been removed')


def main():
    args = sys.argv[1:]
    if not args or args == ['--all']:
        targets = [LIVE, BLUEPRINT]
    else:
        targets = [os.path.abspath(a) for a in args]

    base = json.load(open(BASELINE, encoding='utf-8'))
    print(f"{DIM}baseline: {BASELINE}{OFF}")

    ran = 0
    for path in targets:
        if not os.path.exists(path):
            print(f"{YEL}skip{OFF} (not found) {path}")
            continue
        try:
            if os.path.samefile(path, LIVE):
                check_live(path, base); ran += 1
            elif os.path.samefile(path, BLUEPRINT):
                check_blueprint(path); ran += 1
        except Exception as e:
            bad(f'{os.path.basename(path)}: crashed while checking — {type(e).__name__}: {e}')
            ran += 1

    if not ran:
        print(f"\n{YEL}nothing to check{OFF} (no tracked file among the arguments)")
        return 0

    print()
    if fails:
        print(f"{RED}PREFLIGHT FAILED{OFF} — {len(fails)} of {checks[0]} checks failed:")
        for f in fails:
            print(f"  {RED}·{OFF} {f}")
        print("\nDo not ship or commit this until it is resolved or deliberately re-baselined.")
        return 1
    print(f"{GRN}preflight passed{OFF} — {checks[0]} checks, 0 failures")
    return 0


if __name__ == '__main__':
    sys.exit(main())
