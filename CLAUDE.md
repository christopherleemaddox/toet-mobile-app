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

## `App Blueprint/` — the shared vocabulary for this app (mandatory, keep in sync)
`App Blueprint/TOET-Blueprint.html` is an interactive, click-to-label map of every screen in the app. Open it, pick a screen tab (Onboarding, Today, Browse, Reader, Kept, Prayers, Settings, Circle, Sending, Recap, Account, Sheets & Popups), click any element, and it shows a short code (e.g. `T8`) and a plain-English name (e.g. "Daily Word Card") in the bottom bar. This is how Christopher refers to specific UI pieces in chat — "fix T8" or "fix the Daily Word Card" — instead of describing them from scratch every time. Treat this as the naming authority for this app's UI.

**Known gap, flag until fixed:** this file is dated 2026-08-01; `Live Build/` is from 2026-08-02 or later. The Blueprint has not been regenerated since, so some codes/names may not match the current build exactly. Whoever next makes a UI change to `Live Build/` should verify the Blueprint still matches before relying on it, and update it if not.

**Standing rule — this is mandatory, not optional:** any session that changes the UI in `Live Build/index.html` (adds, removes, renames, or restructures a screen or component) must update `App Blueprint/TOET-Blueprint.html` to match, in the same session, before considering the change done. This is not yet an automated pipeline — there's no script that regenerates the Blueprint from the app's code by itself. Right now it's a manual step Claude is required to do every time. If Christopher wants true automatic regeneration later, that's a separate, larger build (parsing the live HTML and generating the Blueprint's screen/code map programmatically) — worth its own conversation, not assumed.

## Working here
- Edits to `Live Build/index.html` affect something Christopher relies on daily — treat it as production code, not a draft.
- Card copy (the "truth" line, prayers) goes through the built-in Humalingo skill before it ships — this is exactly the kind of short, emotionally-loaded copy that reads as AI-written if it isn't deliberately humanized.
- Scripture quoted on a card: word-for-word, per the brand voice rules in the parent `TOET Projects/CLAUDE.md`. The "truth" affirmation can paraphrase but should stay recognizably tied to the verse's own words.
- This folder is a git repo (initialized 2026-08-06, remote at `github.com/christopherleemaddox/toet-mobile-app`). `Legacy Art/` and `Archive/` are intentionally excluded — only `Live Build/`, `Alternate Design (Unshipped)/`, and this file are tracked.

## Open questions to raise with Christopher, not assume
- Long-term tech stack: stay single-file PWA, or move toward an app-store-distributed app eventually?
- Whether Christopher wants a real automated Blueprint-regeneration pipeline built at some point, versus the current mandatory-manual-update rule.

## Decided, don't re-litigate
- Netlify password gate on bibletruthcards.netlify.app: intentional, confirmed by Christopher (2026-08-06). Leave it on.
- `Archive/TOET Original APP (full predecessor build)/` vs `Legacy Art (ChatGPT Prototype)/`: keep both as-is. Christopher only cares about `Legacy Art/` (the images); no consolidation needed.
