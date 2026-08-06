# TOET Mobile App — daily encouragement cards

## What it is
A Bible-based affirmation/encouragement card app: 7 categories, 92 topics, 461 cards, free/premium structure. Each card gives a "truth" (a personalized affirmation grounded in a verse), the verse/reference, and a related prayer.

## Status: live and in daily use
Christopher runs this app on his own phone every day. It's deployed on Netlify at **bibletruthcards.netlify.app** (password-protected in Netlify's visitor-access settings — intentional). **Deploys are git-based auto-deploy, confirmed working 2026-08-07**: Christopher linked the site to `github.com/christopherleemaddox/toet-mobile-app` in Netlify's dashboard; `netlify.toml` (`publish = "Live Build"`) tells Netlify what to serve. Verified end-to-end with a real push/deploy/fetch round trip (an invisible HTML comment pushed to `main`, confirmed present on the live site once Netlify's deploy showed "Published," then removed in a follow-up commit). `git push` to `main` is now the actual way to ship a change — manual dashboard uploads are no longer the workflow.

## What's in this folder — verified, not assumed
This folder was consolidated on 2026-08-06 from two places that had drifted apart: this Claude Projects location, and a separate working folder at `~/Desktop/TruthApp/`. Everything below was confirmed by direct comparison (MD5 hash and byte diffs against the live site), not guessed.

- **`Live Build/`** — **the real, current app.** `index.html` here is byte-for-byte identical (MD5-verified) to what's actually running at bibletruthcards.netlify.app right now. Also has `manifest.json`, `icon-180.png`, `icon-512.png` — this is a real installable PWA. **This is what "the app" means when Christopher refers to it. Work happens here.**
- **`Alternate Design (Unshipped)/`** — a genuine design pass built earlier (typography-first, no background photography, described in its own `DESIGN.md`). It was built to compare against "the original," but it was **never actually deployed** — confirmed by diffing it against the live site, which showed a completely different file. Worth keeping as a reference / possible future direction, but do not treat it as current, and do not assume its ideas need "porting" from anywhere — it stands on its own.
- **`Legacy Art (ChatGPT Prototype)/`** — background art and screenshots only, no working code, from an earlier prototype built with a different AI tool before Christopher switched to Claude. Kept for the artwork. Excluded from git (`.gitignore`) — not source.
- **`Archive/`** — moved here from `~/Desktop/TruthApp/` during consolidation, also excluded from git for size:
  - `Master Build TOET (old manual snapshots)/` — two different zip snapshots from before "Live Build," made by hand instead of with git. Superseded now that git tracks history going forward.
  - `Current TOET Chat (source of Live Build)/` — the original download `Live Build/` was extracted from. Kept as the paper trail.

## `App Blueprint/` — the shared vocabulary for this app (mandatory, keep in sync)
`App Blueprint/TOET-Blueprint.html` is an interactive, click-to-label map of every screen in the app. Open it, pick a screen tab (Onboarding, Today, Browse, Reader, Kept, Prayers, Settings, Circle, Sending, Recap, Account, Sheets & Popups), click any element, and it shows a short code (e.g. `T8`) and a plain-English name (e.g. "Daily Word Card") in the bottom bar. This is how Christopher refers to specific UI pieces in chat — "fix T8" or "fix the Daily Word Card" — instead of describing them from scratch every time. Treat this as the naming authority for this app's UI.

**Verified 2026-08-06 against `Live Build/`:** both files are built with the same tool (a `DCLogic`/`text/x-dc` React component pattern — extract the inline `<script type="text/x-dc">` block from either file's decoded template to read the real source). Checked the Blueprint's claims against Live Build's actual source and a live render of onboarding:
- Onboarding welcome screen (O1–O3: wordmark, headline, Begin button) — confirmed word-for-word identical in a live render.
- All 12 screen concepts (onboarding, today, browse, kept, prayers, reader, settings, circle, sending, recap, account, sheets) — confirmed present in the real source, either as explicit `// today` / `// browse` etc. section comments or by direct keyword presence (settings, circle, sending, recap, account, sheet all appear multiple times).
- Today screen's dynamic greeting/memory-line logic (T5, T6) — confirmed matches the Blueprint's description; it's template-generated ("Good morning" + name, changes by hour, references recent prayers), not fixed text, which is why some literal phrase searches came back empty.
- **Not fully re-verified:** exact button/label copy for several interactive elements (e.g. "Draw Another" — the underlying `drawAnother()` handler exists, but the literal displayed text wasn't confirmed via live click-through, since this preview environment's click simulation isn't reliable on the real app's actual buttons). Structural drift looks unlikely; cosmetic copy drift on a handful of labels is possible.

**Bottom line:** treat the Blueprint as trustworthy for screen/component structure. If Christopher hits a spot in the real app where the Blueprint's exact wording doesn't match what's on screen, that's a copy-level fix, not evidence the whole thing is stale.

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
- `Archive/TOET Original APP (full predecessor build)/` vs `Legacy Art (ChatGPT Prototype)/`: Christopher only wanted the art. The full predecessor-code copy was deleted (moved to ~/.Trash, 2026-08-06) — `Legacy Art/` is the only surviving copy of that earlier build, images only.
- GitHub push is working (fixed via Personal Access Token, 2026-08-06). All commits are live at github.com/christopherleemaddox/toet-mobile-app, `main` in sync with `origin/main`.
