#!/usr/bin/env python3
"""A floating layer's height is reserved by the content it covers.

The system already knows this rule and pays it once. The nav floats over the
page, so `.cf-hero` opens with `margin-top: calc(var(--nav-height) * -1)` and
the comment above that line says why in one sentence: "The nav floats over the
artwork, so the hero starts where the page starts — pulled up by exactly the
nav's height, never by a rounded-off guess."

There are TWO floating layers on the landing page, and only the first one was
ever reserved. The consent banner is `position: fixed; inset: auto 0 0 0` — the
viewport's bottom edge — and the hero is `min(92vh, 56rem)` tall and hangs its
kicker and its one call to action off its OWN bottom edge. 92vh plus the
banner's height is more than the viewport at every height below about 1800 px,
so the banner landed on the hero's bottom row on every first visit, which is
the only visit it is shown on.

Measured on patterns/landing-page.html, first load, nothing dismissed:

    viewport      banner h   CTA buried   kicker buried   elementFromPoint at the CTA's centre
    375 x 812        333.5      48 / 48      48.8 / 48.9   the banner's "Nur notwendige" button
    768 x 1024       232.9      48 / 48         —          the banner's own heading
    1024 x 768       144.4    34.9 / 48      32.9 / 32.9   the banner's plate
    1280 x 900       144.4    24.4 / 48      24.4 / 32.9   the banner's plate
    1440 x 900       144.4    24.4 / 48      24.4 / 32.9   the banner's plate
    1920 x 1080      144.4         —            —          the button itself

Five of six sizes, and the two narrowest bury the control whole. It reads as a
paint fault — a button sliced through the middle by the banner's top edge — but
the hit test is the real finding: on five of six sizes the middle of
"Kennenlernen" belongs to the banner, so the page's primary call to action is a
dead target for as long as the notice is up. It renders correctly in every
screenshot of the dismissed page, which is the state anyone checking the page
is in by their second look.

WHY THIS NEEDS A SCRIPT RATHER THAN A NUMBER. The banner's height is 144.4,
232.9 and 333.5 px at the three widths its copy re-wraps at, and it moves again
with a reader's type size or a translated string. A constant would have been
the fourth hand-computed number this repository has had to go back and find. So
the height is measured by the script that already owns the banner's lifecycle
and published as --cf-consent-height, and the hero reads it back. That makes
the fix a chain of four links, three of which break silently:

  * the property is set while the banner is up            — breaks loudly
  * it is REMOVED when the banner goes                    — breaks silently:
      the hero would stay short forever after a dismissal, on a page that
      renders perfectly at every width
  * the hero's cap reads it with a `0px` fallback         — breaks silently:
      any other fallback reserves space on every page that has no banner at
      all, and the hero is simply the wrong height everywhere, always
  * the cap is a term of the min(), not padding           — breaks silently:
      padding pushes the same content down into the same banner, so the fix
      measures as applied and the button is buried exactly as before

WHAT IS CHECKED

  1. components.css's `.cf-hero` caps its min-height against the banner: a
     min() whose terms include the two original ones and a viewport-minus-
     banner term reading var(--cf-consent-height, 0px).
  2. That fallback is 0px wherever the property is read, in every stylesheet.
     Anything else is a reservation nobody asked for.
  3. cf-consent.js both SETS and REMOVES the property, and the removal is
     reached from the hide path, not only from a resize.
  4. The reservation is a cap and not padding: `.cf-hero` declares no
     padding-block-end/padding-bottom that reads the property.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
JS = ROOT / "design-system" / "assets" / "js" / "cf-consent.js"
PROP = "--cf-consent-height"

failures = []


def rule_body(text, selector):
    """The declaration block of the first top-level `selector { ... }`."""
    m = re.search(r"(?m)^" + re.escape(selector) + r"\s*\{", text)
    if not m:
        return None
    i = m.end()
    depth = 1
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[m.end(): i - 1]


def strip_comments(s):
    return re.sub(r"/\*.*?\*/", "", s, flags=re.S)


# ---- 1 · the hero caps its height against the banner ----------------------
components = (CSS / "components.css").read_text(encoding="utf-8")
hero = rule_body(components, ".cf-hero")
if hero is None:
    failures.append("components.css: no top-level `.cf-hero` rule found")
else:
    decls = strip_comments(hero)
    mh = re.search(r"min-height\s*:\s*([^;]+);", decls)
    if not mh:
        failures.append("components.css .cf-hero: no min-height declaration")
    else:
        value = " ".join(mh.group(1).split())
        if PROP not in value:
            failures.append(
                "components.css .cf-hero: min-height does not reserve the consent "
                "banner.\n    min-height: %s\n    The banner is fixed to the viewport's "
                "bottom edge and the hero hangs its kicker and its call to action off "
                "its own bottom edge; without a term reading var(%s, 0px) the banner "
                "buries both on every viewport under ~1800 px tall." % (value, PROP)
            )
        else:
            if not value.startswith("min("):
                failures.append(
                    "components.css .cf-hero: min-height must stay a min() of the "
                    "original terms plus the clearance, so the clearance can only ever "
                    "shrink the hero.\n    min-height: %s" % value
                )
            for term in ("92vh", "56rem"):
                if term not in value:
                    failures.append(
                        "components.css .cf-hero: min-height lost its original `%s` "
                        "term.\n    min-height: %s" % (term, value)
                    )
            if not re.search(r"calc\(\s*100vh\s*-\s*var\(\s*%s\s*,\s*0px\s*\)\s*\)"
                             % re.escape(PROP), value):
                failures.append(
                    "components.css .cf-hero: the clearance term must be "
                    "calc(100vh - var(%s, 0px)) — the hero has to end where the "
                    "banner begins.\n    min-height: %s" % (PROP, value)
                )
    # 4 · a cap, not padding
    for prop in ("padding-block-end", "padding-bottom", "padding-block", "padding"):
        for d in re.finditer(r"(?m)^\s*%s\s*:\s*([^;]+);" % re.escape(prop), decls):
            if PROP in d.group(1):
                failures.append(
                    "components.css .cf-hero: `%s` reads %s. The reservation has to be "
                    "a cap on the hero's height, not padding inside it — padding pushes "
                    "the same content down into the same banner and buries the button "
                    "exactly as before, while measuring as applied." % (prop, PROP)
                )

# ---- 2 · every read of the property falls back to 0px ---------------------
for css in sorted(CSS.glob("*.css")):
    text = strip_comments(css.read_text(encoding="utf-8"))
    for m in re.finditer(r"var\(\s*%s\s*(?:,([^()]*))?\)" % re.escape(PROP), text):
        fallback = (m.group(1) or "").strip()
        if fallback != "0px":
            failures.append(
                "%s: var(%s) falls back to %r, not `0px`. The property exists only "
                "while the banner does; any other fallback reserves space on every "
                "page that never shows one."
                % (css.name, PROP, fallback or "(no fallback)")
            )

# ---- 3 · the script sets it AND takes it away -----------------------------
if not JS.exists():
    failures.append("missing %s" % JS.relative_to(ROOT))
else:
    js = JS.read_text(encoding="utf-8")
    js_code = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    if not re.search(r"setProperty\(\s*['\"]%s['\"]" % re.escape(PROP), js_code):
        failures.append(
            "cf-consent.js: nothing sets %s. The hero reads it to size itself around "
            "the banner." % PROP
        )
    if not re.search(r"removeProperty\(\s*['\"]%s['\"]" % re.escape(PROP), js_code):
        failures.append(
            "cf-consent.js: nothing removes %s. Left set after a dismissal the hero "
            "stays short for the rest of the session — and renders perfectly at every "
            "width while it does." % PROP
        )
    # the publisher has to be reached from the hide path, or the removal above
    # can only ever be a resize away
    hide = re.search(r"function\s+hideBanner\s*\([^)]*\)\s*\{(.*?)\n    \}", js_code, re.S)
    if not hide:
        failures.append("cf-consent.js: no hideBanner() to check the removal against")
    elif "publishHeight" not in hide.group(1):
        failures.append(
            "cf-consent.js: hideBanner() does not republish the banner's height, so "
            "%s outlives the banner on every dismissal." % PROP
        )
    show = re.search(r"function\s+showBanner\s*\([^)]*\)\s*\{(.*?)\n    \}", js_code, re.S)
    if show and "publishHeight" not in show.group(1):
        failures.append(
            "cf-consent.js: showBanner() does not publish the banner's height, so the "
            "hero only clears the banner once something else resizes it."
        )

if failures:
    print("check-consent-clearance.py: %d problem(s)\n" % len(failures))
    for f in failures:
        print("  - %s\n" % f)
    sys.exit(1)

print("check-consent-clearance.py: consent clearance reserved and released.")
