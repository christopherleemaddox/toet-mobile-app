---
name: edit-app-safely
description: The method for changing Live Build/index.html or App Blueprint/TOET-Blueprint.html without shipping a silent break. Use BEFORE writing any script that edits either file, and before trusting any audit or checker you write against them. Covers anchor uniqueness, proving a checker can actually fail, testing the negative case, and browser verification. These rules exist because each one was learned from a real mistake on this project.
---

# Editing the TOET app without breaking it quietly

The `preflight` hook catches a **broken file** after you write it. It cannot catch
a **broken method** — a checker that quietly examined the wrong thing, an edit
anchored on a string that appears four times, a feature tested only in the case
where it works. Those are what this skill is for.

Every rule below is here because it already went wrong once.

## 1. Any checker must print what it actually read

Before you believe a single result, the script must print its input path, its
size, and how many records it parsed. Then compare that number against what you
expect **before** reading the verdict.

> An audit of all 1,861 cards for language discouraging medical treatment
> reported "0 violations, all clear." The parser regex was wrong and had matched
> **zero cards**. The all-clear was real output from a script that had examined
> nothing. It was caught only because it printed `CARDS PARSED: 0`.

A pass you cannot trace to a real count is not a pass.

## 2. Prove the checker can fail, with a planted defect

A checker that has only ever printed "pass" is indistinguishable from a broken
one. Plant a deliberate violation, confirm it is caught, then remove it.

> The same card audit got a planted control card containing *"You don't need
> medicine when you have faith; just pray."* Four of the eight patterns fired on
> it. That is what made the clean result on the real 1,861 mean something.

`.claude/preflight/selftest.py` does exactly this for preflight — plants ten
defects one at a time and asserts each is caught. Run it after changing
`preflight.py`. Mirror the pattern for any new checker.

## 3. Anchor every edit on a string proven unique

Never blind-replace. Count occurrences first and assert exactly one, or you will
patch one of several identical-looking spots and believe you are done.

```python
def once(text, needle, label):
    n = text.count(needle)
    assert n == 1, f"{label}: matched {n}x, need exactly 1"
    return text.find(needle)
```

> A reader button was added by finding one seemingly-unique anchor. The reader
> actually has **four** near-duplicate action rows, one per reading mode, so the
> button was silently missing from three of them until a broader grep found the
> rest.

Before treating a markup edit as done, grep for every occurrence of the
surrounding pattern, not just the anchor that happened to match.

## 4. Test the negative case, not just the positive

If a feature is supposed to appear *conditionally*, proving it appears is half a
test. Prove it is **absent** where it should be absent.

> The crisis line was built to show on 15 of 93 topics. Confirming it appeared on
> Hopelessness proved nothing about the design — a line rendering on all 93 would
> have looked identical from that one check. The real test was confirming it was
> absent on Gratitude, Wisdom and Praise.

## 5. Verify the bytes you did not mean to touch

After re-encoding, assert everything outside the edited region is byte-identical
to the original. Splices go wrong silently.

```python
assert out[:m.start(1)] == raw[:m.start(1)]
assert out[len(out)-(len(raw)-m.end(1)):] == raw[m.end(1):]
```

## 6. Two escaping traps, opposite answers

- **Re-encoding the template:** after `json.dumps`, you must
  `.replace('</', '<\\u002F')`. Skipping it produces a file that parses fine in
  Python and dies in the browser with *"Unterminated string in JSON"*, because
  the HTML parser ends the `<script>` tag early. `json.loads` cannot see this;
  preflight now checks it explicitly.
- **Apostrophes and arrows:** in **HTML/markup text**, write the real character
  (`'`, `→`). In **JS source strings**, a `’` escape is correct. Getting
  this backwards once rendered the literal characters `’` on screen.

## 7. Browser-verify, and drive it with JavaScript

Screenshot-coordinate clicking on this app is unreliable and times out. Drive it
by finding elements by text and calling `.click()`, then re-query after a delay:

```js
new Promise(res => {
  [...document.querySelectorAll('button')].find(b => b.innerText.includes('Browse')).click();
  setTimeout(() => res(document.body.innerText.slice(0, 400)), 400);
})
```

Open a **fresh tab** — a reused tab carries stale console errors and makes a
working file look broken. Check the console for errors, not just the screenshot.
Check **both themes**; three of the four contrast fixes were light-mode only.

## 8. Finish the job

- **Update the Blueprint in the same session.** Mandatory. Then sync all three
  copies (project, `TOET Blueprints/`, iCloud) and redeploy the Blueprints site.
- **Run `python3 .claude/preflight/preflight.py --all`** and read the counts.
- **Confirm a deploy actually happened** — check the published deploy id changed
  and `curl` the URL. A 401 means alive and gated; a 404 means broken. A site
  once sat at zero deploys for a day because a manual dashboard step was
  described but never verified.

## What none of this catches

Judgment. A Hopelessness header sitting above a Peace verse passed every
mechanical check on this list and was caught only by looking at a screenshot.
When the change is visual or editorial, look at the rendered thing.
