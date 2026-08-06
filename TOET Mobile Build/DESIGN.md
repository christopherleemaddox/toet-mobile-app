# Claude Design — Bible Mobile Cards App

An independent design pass on Truth Over Every Thought. Same content (7 categories, 92 topics, 461 cards, free/premium structure), completely different visual and interaction system — built to sit next to the original as a separate Netlify deploy for side-by-side comparison.

## What changed, and why

**The card itself, not a photo behind it, is the hero.** The original app leans on full-bleed background art (Neo Deco, Splash Truth, Street Truth, Photos) behind a glass card. This version has no background photography at all — every screen is built from type, color, and motion alone. That's a deliberate bet: it means the whole app is done and testable today with zero image-generation turnaround, it never looks "off" while art is mid-batch, and it puts the actual words — the verse, the truth statement, the prayer — visually first instead of competing with a busy backdrop.

**Typography carries the emotional weight instead of glass/metal chrome.** The "truth" line for each card (the personalized affirmation) is set in large serif display type and treated as the actual centerpiece of the screen, the way a pull-quote works in editorial design. Scripture reference and verse sit above it in a smaller supporting role; the prayer lives on the reverse.

**Swipe, don't flip.** Instead of a 3D card-flip, moving between truth → prayer is a soft upward swipe/tap (spring-eased translate + cross-fade), and moving between cards within a topic is a horizontal swipe. This is closer to how people already use Stories/Reels/dating-app cards, so it should feel more native to habitual phone use.

**One accent color per category, used sparingly.** Each of the 7 categories keeps a signature color (as an underline, a tag, a progress dot) instead of tinting the entire screen. Keeps the visual language calm and legible while still giving categories a distinct identity at a glance.

**Browse leans on search + a flat list, not a decorative tile grid.** With 92 topics, findability matters more than a pretty grid. Top of Browse has a live search field and a horizontally scrolling row of category chips; below that is a flat, scannable list grouped by category.

**Light and dark are both first-class**, switchable in Settings or following system preference — a warm "paper" light mode and a deep "ink" dark mode, both using the same type system.

## Screens included in this pass

Onboarding (pick topics) · Home (today's card) · Browse (search/filter all 92 topics) · Saved · Prayer log · Settings (theme, text size, category color reference).

## Intentionally deferred (not in this pass)

Sharing/invite flow, Apple Watch companion screen, PIN/pattern app lock, scheduled reminders, group renaming, and the multi-background-style picker (Neo Deco / Splash Truth / Street Truth / Photos). These are real, working features in the original app — they were left out here so this pass could focus entirely on proving out the new visual/interaction direction first. Happy to port any of them over once you've decided what you like.

## Files

Single `index.html` — same single-file-PWA approach as the original (installable via Safari "Add to Home Screen," no build step, no separate manifest/service worker file).
