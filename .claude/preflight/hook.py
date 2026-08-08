#!/usr/bin/env python3
"""
PostToolUse hook: run preflight whenever the app or its Blueprint is touched.

Fires on Write/Edit of either tracked file, and also on any Bash command whose
text mentions them — because in practice these files usually get replaced with
`cp` from a scratchpad rather than edited in place, and a hook that only watched
Write/Edit would have sat there silently through every real change made so far.

Exit 2 sends the output back to Claude as a blocking error, so a broken bundle
cannot be quietly committed. Anything else exits 0 and stays out of the way —
a hook that breaks the session on its own bugs is worse than no hook.

Decisions are made in Python rather than shell because the tracked path
contains a space ("Live Build"), which shell word-splitting mangles.
"""
import sys, os, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PREFLIGHT = os.path.join(HERE, 'preflight.py')
MARKERS = ('Live Build/index.html', 'App Blueprint/TOET-Blueprint.html', 'TOET-Blueprint.html')


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0                                  # not our business, stay quiet

    tool = payload.get('tool_name', '')
    ti = payload.get('tool_input') or {}

    targets = []
    if tool in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit'):
        path = ti.get('file_path') or ''
        if any(path.endswith(m) for m in MARKERS[:2]):
            targets = [path]
    elif tool == 'Bash':
        cmd = ti.get('command') or ''
        if any(m in cmd for m in MARKERS):
            targets = ['--all']                   # cp/mv: check both, cheaply

    if not targets:
        return 0

    try:
        r = subprocess.run([sys.executable, PREFLIGHT] + targets,
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        print(f"preflight could not run ({type(e).__name__}: {e}) — skipping, not blocking",
              file=sys.stderr)
        return 0

    if r.returncode != 0:
        print(f"PREFLIGHT FAILED after {tool} — the app or Blueprint is in a bad state.\n"
              f"Fix this before committing or deploying. Full output:\n\n"
              f"{r.stdout}\n{r.stderr}", file=sys.stderr)
        return 2                                  # blocking: Claude must see this
    return 0


if __name__ == '__main__':
    sys.exit(main())
