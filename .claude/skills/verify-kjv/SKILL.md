---
name: verify-kjv
description: Verify every card's quoted Scripture and its reference against a public-domain KJV corpus. Run this whenever cards are added or edited, before shipping.
---

# Verify card Scripture against the real KJV

The brand rule is that quoted Scripture is word-for-word, never trimmed or reworded
(`TOET Projects/CLAUDE.md`). This check proves that instead of trusting it.

It verifies two things for all cards:
1. The `verse` text matches the KJV exactly (after normalizing curly quotes and whitespace).
2. The `ref` points at a real book/chapter/verse that actually contains that text.

Last full run: **2026-08-07, 1,861 / 1,861 exact, 0 reference errors.**

## Running it

**Step 1 — get the card data out of the bundle.** Card text lives inside a gzip-compressed
JS asset in `Live Build/index.html`, not in plain text. Extract it to
`<scratchpad>/cards_live.json` as a JSON array of objects with at least `id`, `topic`,
`ref`, `verse`. See the `read-dc-bundle` skill for the bundle format; the card objects
match this regex:

```
\{\s*(?:free:true,\s*)?id:(\d+),\s*topic:'...',\s*cat:'...',\s*ref:'...',\s*verse:'...',\s*truth:'...',\s*prayer:'...'\s*\}
```

**Step 2 — download the KJV corpus** into `<scratchpad>/kjv/`. This is 66 JSON files,
about 5MB total, from the public-domain dataset at `github.com/aruljohn/Bible-kjv`:

```bash
for b in Genesis Exodus Leviticus Numbers Deuteronomy Joshua Judges Ruth 1Samuel 2Samuel 1Kings 2Kings 1Chronicles 2Chronicles Ezra Nehemiah Esther Job Psalms Proverbs Ecclesiastes SongofSolomon Isaiah Jeremiah Lamentations Ezekiel Daniel Hosea Joel Amos Obadiah Jonah Micah Nahum Habakkuk Zephaniah Haggai Zechariah Malachi Matthew Mark Luke John Acts Romans 1Corinthians 2Corinthians Galatians Ephesians Philippians Colossians 1Thessalonians 2Thessalonians 1Timothy 2Timothy Titus Philemon Hebrews James 1Peter 2Peter 1John 2John 3John Jude Revelation; do
  curl -sfL -o "$b.json" "https://raw.githubusercontent.com/aruljohn/Bible-kjv/master/$b.json"
done
```

The corpus is deliberately **not** committed to this repo, to keep it lean. Downloading it
is a file download, so ask Christopher before fetching it, same as any download.

Note: this loop needs `bash`, or `${=BOOKS}` if you use a variable under `zsh` — plain
`for b in $BOOKS` silently does nothing in zsh because it does not word-split.

**Step 3 — run it**, after pointing `SCRATCH` at the session scratchpad:

```bash
python3 verify_kjv.py
```

## Reading the output

- **EXACT MATCH** — good. Text is byte-identical to the KJV once curly quotes/whitespace
  are normalized.
- **PUNCTUATION/CAPITALIZATION ONLY** — same words, different punctuation. Usually a KJV
  edition difference rather than an error, but look at each one.
- **ACTUAL WORDING DIFFERENCE** — a real problem. Scripture was altered. Fix the card.
- **REFERENCE ERRORS** — the ref points at a verse that does not exist, or the text does
  not belong to that ref. Fix the ref.

## Always sanity-check the checker

A 100% pass is exactly when a broken comparison looks like success. Before trusting a
clean run, corrupt a few cards in a copy and confirm the script flags them. Verified
working faults: a single-word swap (`hath` -> `has`), a dropped clause, a wrong-but-valid
reference, and a nonexistent reference. Beware writing a no-op fault: replacing a word
that is not present in that verse tests nothing.

## Scope

This checks that quoted Scripture is accurate. It **cannot** check whether the card's
`truth` affirmation is a sound application of the verse in context. That is a theological
judgment and needs a human (a pastor or elder), not a script.
