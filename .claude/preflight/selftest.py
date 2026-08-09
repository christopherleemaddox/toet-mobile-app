#!/usr/bin/env python3
"""
Proves preflight.py can actually FAIL.

A checker that has only ever returned "pass" is indistinguishable from a
checker that is broken. This plants one specific defect at a time into a
throwaway copy of the real files and asserts preflight catches that exact
one. If a mutation is planted and preflight still says pass, the check
guarding it is dead and this exits non-zero.

Run after any change to preflight.py:
    python3 selftest.py
"""
import os, re, json, base64, gzip, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.abspath(os.path.join(HERE, '..', '..'))
LIVE = os.path.join(APP, 'Live Build', 'index.html')
BP = os.path.join(APP, 'App Blueprint', 'TOET-Blueprint.html')


def tpl_span(raw):
    return re.search(r'<script type="__bundler/template">\s*\n(.*?)\n\s*</script>', raw, re.S)


def edit_template(raw, fn):
    m = tpl_span(raw)
    t = fn(json.loads(m.group(1).strip()))
    nj = json.dumps(t, ensure_ascii=True).replace('</', '<\\u002F')
    return raw[:m.start(1)] + nj + raw[m.end(1):]


def edit_cards(raw, fn):
    """Mutate the card-data asset in place: base64 -> gunzip -> edit -> regzip."""
    dec = json.JSONDecoder()
    for s in [m.start() for m in re.finditer(r'\{"[0-9a-f]{8}-[0-9a-f]{4}-', raw)]:
        try:
            obj, end = dec.raw_decode(raw, s)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        for uuid, meta in obj.items():
            if not isinstance(meta, dict) or 'data' not in meta:
                continue
            try:
                data = base64.b64decode(meta['data'])
                text = gzip.decompress(data).decode('utf-8') if meta.get('compressed') \
                    else data.decode('utf-8')
            except Exception:
                continue
            if "window.CARDS = window.CARDS" not in text:
                continue
            new = fn(text)
            assert new != text, 'mutation was a no-op — it changed nothing'
            blob = gzip.compress(new.encode('utf-8')) if meta.get('compressed') else new.encode('utf-8')
            obj[uuid]['data'] = base64.b64encode(blob).decode('ascii')
            return raw[:s] + json.dumps(obj) + raw[end:]
    raise AssertionError('card asset not found for mutation')


def once(text, old, new):
    assert text.count(old) >= 1, f'mutation anchor not present: {old[:60]!r}'
    return text.replace(old, new, 1)


# (label, which file, mutate fn, substring expected in preflight's failure output)
CASES = [
    ('broken re-encode (the classic missing escape)', LIVE,
     lambda r: r.replace('<\\u002F', '</', 1), 'decode'),
    ('a card deleted (count drift)', LIVE,
     lambda r: edit_cards(r, lambda t: re.sub(r'\n  \{ id:\d+.*?\n(?=  \{ id:)', '\n', t, count=1, flags=re.S)),
     'cards:'),
    ('em dash introduced into card copy', LIVE,
     lambda r: edit_cards(r, lambda t: once(t, "truth:'", "truth:'Broken — copy. ")), 'em/en dash'),
    ('straight apostrophe introduced', LIVE,
     lambda r: edit_cards(r, lambda t: once(t, "truth:'", "truth:'Don\\'t. ")), 'straight apostrophe'),
    ('a prayer no longer ends Amen.', LIVE,
     lambda r: edit_cards(r, lambda t: once(t, " Amen.'", " Amen. Extra.'")), 'Amen'),
    ('crisis help screen removed', LIVE,
     lambda r: edit_template(r, lambda t: t.replace('If you need help right now', 'Gone')),
     'crisis help screen'),
    ('crisis 988 link removed', LIVE,
     lambda r: edit_template(r, lambda t: t.replace('tel:988', 'tel:000')), 'crisis 988'),
    ('two screens claim the same code', BP,
     lambda r: edit_template(r, lambda t: t.replace("['PV1','Back Link'", "['K1','Back Link'")),
     'duplicate codes'),
    ('legend entry with no clickable region', BP,
     lambda r: edit_template(r, lambda t: t.replace("['H8','Footer Disclaimer'", "['H99','Footer Disclaimer'")),
     'no clickable region'),
    ('Blueprint self-check banner removed', BP,
     lambda r: edit_template(r, lambda t: t.replace('hasClash', 'hasNothing')), 'self-check'),
    ('chrome-paint bg reverts to a hardcoded light/dark literal '
     '(would recreate the white-block mismatch bug found on Christopher\'s phone 2026-08-08)', LIVE,
     lambda r: edit_template(r, lambda t: once(
         t, "this.sharePal().bg:this.pal().bg;",
         "this.sharePal().bg:(this.isDark()?'#12141c':'#faf6ee');")),
     'pal().bg'),
    ('Coming Soon gate reverts to the resettable onboarded/testerUnlocked pair '
     '(would recreate the Start-over lockout bug found on Christopher\'s phone 2026-08-08)', LIVE,
     lambda r: edit_template(r, lambda t: once(t, 'comingSoonOpen:!S.everAccessed,',
                                                 'comingSoonOpen:!S.onboarded&&!S.testerUnlocked,')),
     'everAccessed'),
    ('Coming Soon manual code-entry handler removed '
     '(the only unlock path that survives Add to Home Screen)', LIVE,
     lambda r: edit_template(r, lambda t: once(t, 'csUnlock:()=>{', 'csGone:()=>{')),
     'csUnlock'),
    ("Christopher's private owner code deleted from isValidCode "
     '(would lock him out again with no independent way back in)', LIVE,
     lambda r: edit_template(r, lambda t: once(
         t, "v==='toet2026'||v==='trustgod2026!#'", "v==='toet2026'")),
     'trustgod2026'),
]


def main():
    tmp = tempfile.mkdtemp(prefix='toet-selftest-')
    print(f"scratch: {tmp}\n")
    # a working copy of the whole app so preflight resolves its own paths
    for sub in ('Live Build', 'App Blueprint', '.claude/preflight'):
        os.makedirs(os.path.join(tmp, sub), exist_ok=True)
    shutil.copy(LIVE, os.path.join(tmp, 'Live Build', 'index.html'))
    shutil.copy(BP, os.path.join(tmp, 'App Blueprint', 'TOET-Blueprint.html'))
    for f in ('preflight.py', 'baseline.json'):
        shutil.copy(os.path.join(HERE, f), os.path.join(tmp, '.claude/preflight', f))

    pf = os.path.join(tmp, '.claude/preflight/preflight.py')
    target = {LIVE: os.path.join(tmp, 'Live Build', 'index.html'),
              BP: os.path.join(tmp, 'App Blueprint', 'TOET-Blueprint.html')}
    pristine = {p: open(p, encoding='utf-8').read() for p in target.values()}

    # sanity: the untouched copy must PASS, or every result below is noise
    r = subprocess.run([sys.executable, pf, '--all'], capture_output=True, text=True)
    if r.returncode != 0:
        print('ABORT: the unmutated copy already fails preflight.\n' + r.stdout[-1500:])
        return 1
    print('baseline: unmutated copy passes\n')

    bad = 0
    for label, src, fn, expect in CASES:
        dst = target[src]
        try:
            open(dst, 'w', encoding='utf-8').write(fn(pristine[dst]))
        except Exception as e:
            print(f"  ?? could not plant  {label}: {type(e).__name__}: {e}")
            bad += 1
            open(dst, 'w', encoding='utf-8').write(pristine[dst])
            continue
        r = subprocess.run([sys.executable, pf, dst], capture_output=True, text=True)
        out = r.stdout + r.stderr
        caught = r.returncode != 0 and expect.lower() in out.lower()
        print(f"  {'ok  caught' if caught else 'MISSED    '}  {label}")
        if not caught:
            bad += 1
            print(f"      expected {expect!r} in a failing run; exit={r.returncode}")
            print('      ' + '\n      '.join(out.strip().splitlines()[-6:]))
        open(dst, 'w', encoding='utf-8').write(pristine[dst])

    shutil.rmtree(tmp, ignore_errors=True)
    print()
    if bad:
        print(f"SELFTEST FAILED — {bad} of {len(CASES)} planted defects were not caught.")
        print("A check that cannot fail is not protecting anything.")
        return 1
    print(f"selftest passed — all {len(CASES)} planted defects were caught")
    return 0


if __name__ == '__main__':
    sys.exit(main())
