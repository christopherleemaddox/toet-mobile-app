# TOET Mobile App — daily encouragement cards

## What it is
A Bible-based affirmation/encouragement card app: 7 categories, 92 topics, 461 cards, with a free/premium structure. Each card gives the user a "truth" (a personalized affirmation grounded in a verse), the verse/reference, and a related prayer.

## Status: live and in daily use
This isn't a prototype — Christopher runs `TOET Mobile Build/` on his own phone every day, deployed on Netlify. Treat it as the real, current product, not a design exercise.

## What's in this folder
- **`TOET Mobile Build/`** — **the real app.** `index.html` + `DESIGN.md`, single-file PWA, no build step, installable via Safari "Add to Home Screen," deployed to Netlify. Type-first design: the affirmation itself, in large serif display type, is the visual centerpiece; no background photography. Swipe/tap moves between truth and prayer. This is what to work on when Christopher says "the app."
- **`Legacy Art (ChatGPT Prototype)/`** — reference only, not a working app. Background art (Prism Truth, Splash Truth, Street Truth styles) and screenshots from an earlier prototype built with a different AI tool before Christopher switched to Claude. Kept because Christopher likes the artwork, not because it's a build to maintain or compare against. Do not treat this as "the original app" or assume its features need to be ported — there is no working code behind it.
- `DESIGN.md` (inside `TOET Mobile Build/`) describes this build as being made "to sit next to the original... for side-by-side comparison" — that language predates this clarification. The features it lists as deferred (sharing/invite, Apple Watch companion, PIN lock, scheduled reminders, group renaming, multi-background picker) are real ideas worth keeping on a roadmap, but they aren't sitting in some other finished build waiting to be ported — confirm with Christopher what actually existed before treating any of them as "already built elsewhere."

## Working here
- Card copy (the "truth" line, prayers) goes through the built-in Humalingo skill before it ships. This is exactly the kind of short, emotionally-loaded copy that reads as AI-written if it isn't deliberately humanized.
- Scripture quoted on a card: word-for-word, per the brand voice rules in the parent `TOET Projects/CLAUDE.md`. The "truth" affirmation itself can paraphrase, but should stay recognizably tied to the verse's own words, not a loose gloss.
- This is a shipped, daily-used app — changes to `TOET Mobile Build/index.html` affect something Christopher actually relies on. Treat edits with the same care as production code, not a draft.
- Netlify is the live deploy target. Wiring it up as a proper connector (so deploys can happen from here) is a later step — that needs an interactive session to authorize, which isn't available in every session.

## Open questions to raise with Christopher, not assume
- Confirm the exact Netlify site/URL this deploys to, so it's documented here instead of implied.
- Long-term tech stack: stay single-file PWA, or move toward a proper app-store-distributed app eventually?
- Whether any of the deferred features (sharing, Apple Watch, PIN lock, reminders, group renaming, background picker) are actually wanted on the roadmap, and in what order.
