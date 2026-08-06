# TOET Mobile App — daily encouragement cards

## What it is
A Bible-based affirmation/encouragement card app: 7 categories, 92 topics, 461 cards, free/premium structure. Each card gives a "truth" (a personalized affirmation grounded in a verse), the verse/reference, and a related prayer.

## Status: live and in daily use
Christopher runs this app on his own phone every day. It's deployed on Netlify at **bibletruthcards.netlify.app** (password-protected in Netlify's visitor-access settings — confirm whether that's intentional). Deploys are currently **manual** (drag-and-drop into the Netlify dashboard); moving to git-based auto-deploy via the GitHub remote (`github.com/christopherleemaddox/toet-mobile-app`) is the planned next step.

## What's in this folder — verified, not assumed
This folder was consolidated on 2026-08-06 from two places that had drifted apart: this Claude Projects location, and a separate working folder at `~/Desktop/TruthApp/`. Everything below was confirmed by direct comparison (MD5 hash and byte diffs against the live site), not guessed.

- **`Live Build/`** — **the real, current app.** `index.html` here is byte-for-byte identical (MD5-verified) to what's actually running at bibletruthcards.netlify.app right now. Also has `manifest.json`, `icon-180.png`, `icon-512.png` — this is a real installable PWA. **This is what "the app" means when Christopher refers to it. Work happens here.**
- **`Alternate Design (Unshipped)/`** — a genuine design pass built earlier (typography-first, no background photography, described in its own `DESIGN.md`). It was built to compare against "the original," but it was **never actually deployed** — confirmed by diffing it against the live site, which showed a completely different file. Worth keeping as a reference / possible future direction, but do not treat it as current, and do not assume its ideas need "porting" from anywhere — it stands on its own.
- **`Legacy Art (ChatGPT Prototype)/`** — background art and screenshots only, no working code, from an earlier prototype built with a different AI tool before Christopher switched to Claude. Kept for the artwork. Excluded from git (`.gitignore`) — not source.
- **`Archive/`** — moved here from `~/Desktop/TruthApp/` during consolidation, also excluded from git for size (100MB+):
  - `TOET Original APP (full predecessor build)/` — a complete earlier working version (real `index.html`, manual backup copies, full image library). More complete than `Legacy Art/` above — if the two ever need reconciling, this is the fuller one.
  - `Master Build TOET (old manual snapshots)/` — two different zip snapshots from before "Live Build," made by hand instead of with git. Superseded now that git tracks history going forward.
  - `Current TOET Chat (source of Live Build)/` — the original download `Live Build/` was extracted from. Kept as the paper trail.
  - `TOET-Blueprint/` — a bundled HTML page, not yet reviewed in detail.

## Working here
- Edits to `Live Build/index.html` affect something Christopher relies on daily — treat it as production code, not a draft.
- Card copy (the "truth" line, prayers) goes through the built-in Humalingo skill before it ships — this is exactly the kind of short, emotionally-loaded copy that reads as AI-written if it isn't deliberately humanized.
- Scripture quoted on a card: word-for-word, per the brand voice rules in the parent `TOET Projects/CLAUDE.md`. The "truth" affirmation can paraphrase but should stay recognizably tied to the verse's own words.
- This folder is a git repo (initialized 2026-08-06, remote at `github.com/christopherleemaddox/toet-mobile-app`). `Legacy Art/` and `Archive/` are intentionally excluded — only `Live Build/`, `Alternate Design (Unshipped)/`, and this file are tracked.

## Open questions to raise with Christopher, not assume
- Is the Netlify password gate on bibletruthcards.netlify.app intentional?
- What's actually inside `Archive/TOET-Blueprint/` — hasn't been reviewed yet.
- Whether `Archive/TOET Original APP (full predecessor build)/` should eventually replace `Legacy Art (ChatGPT Prototype)/` since it's more complete, or whether both stay.
- Long-term tech stack: stay single-file PWA, or move toward an app-store-distributed app eventually?
