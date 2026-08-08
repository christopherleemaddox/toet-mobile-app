---
name: audit-card-content
description: Find duplicate or near-duplicate truth/prayer/verse text across all cards, and profile the structural shape of the writing. Run when cards are added, alongside verify-kjv.
---

# Audit card content for repetition

Hand-built card sets tend to repeat themselves as they grow. A user who meets the same
affirmation under two topics feels the seams, and it makes a large library feel thin.
This finds that before a user does.

Companion to the `verify-kjv` skill: that one checks Scripture is *accurate*, this one
checks the surrounding writing is *varied*.

Last full run: **2026-08-07, 1,841 cards. Zero duplicate truths, zero duplicate prayers.**

## Running it

`find_dupes.py` reads `Live Build/index.html` directly (it decompresses the card asset
itself, no separate extraction step) and reports, per field:

- **exact duplicates** after normalizing case/punctuation/quotes
- **near duplicates** above a similarity threshold, via a token-overlap prefilter then
  `difflib` on the survivors

`dupe_topn.py` is the more useful one on a clean corpus: it ignores the threshold and just
shows the genuinely most-similar pairs that exist, plus a built-in negative control.

```bash
python3 find_dupes.py     # thresholded report
python3 dupe_topn.py      # top-N most similar + negative control
```

Both take a couple of minutes; they score roughly 200,000 candidate pairs per field.

## Always sanity-check the checker

"Zero duplicates found" and "the comparison is broken" look identical. `dupe_topn.py` has
a negative control built in: it plants an exact copy and a lightly-reworded copy of a real
card and confirms both are detected. Verified working, planted pairs scored 1.000 and
0.957. Do not report a clean result without that control passing.

## Interpreting results on this card set

The 2026-08-07 baseline, for comparison on future runs:

- **truth**: highest genuine similarity between any two cards was **0.689**. No duplicates.
- **prayer**: highest was **0.788**. No duplicates.
- **verse**: 4 groups share verse text, but every one is a genuinely *different* Scripture
  reference whose wording Scripture itself repeats (Psalm 42:5 vs 42:11, Matthew 25:21 vs
  25:23, Psalm 107:1 vs 1 Chronicles 16:34 vs Psalm 136:1, Lamentations 3:22 vs 3:22-23).
  The truth and prayer on each are different. **Repeated verse text is not automatically a
  defect here** — check whether the two cards sit in the same topic before calling it one.

**The one thing worth acting on:** cards #372 and #1187 are both in the **Gratitude** topic
with near-identical verse text (Psalm 107:1 / 1 Chronicles 16:34). Different references,
different truths, but someone browsing Gratitude sees the same words twice. Every other
overlap spans two different topics, so it is unlikely to be encountered in one sitting.

## Structural profile, and why most of it is fine

The script also profiles shape. On the 2026-08-07 run: 100% of prayers end "Amen.", 86%
open with "Lord," (49.6%) or "Father," (36.3%), 99.6% are 2-3 sentences, median 14 words.

Resist the urge to call that AI-formula and "fix" it. Addressing God and closing with Amen
is what prayer *is*; liturgical repetition is a feature. The real test is whether the
middle varies, and it does (see the similarity numbers above). The only mild note is the
Lord/Father split covering 86% of openings.

Truths are structurally looser: the most common opening two words account for just 1.3%,
75.6% are two sentences, median 17 words.
