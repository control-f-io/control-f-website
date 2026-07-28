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

  5. The short-screen block is the last word, and it SHORTENS the banner.

THE FIFTH LINK, AND WHY IT NEEDED ITS OWN NUMBER. Everything above verifies the
reservation is declared. None of it can see that the reservation does nothing,
and on a landscape phone it does nothing: a min-height cannot shrink a box whose
content is taller than it. The hero renders 467 px against a 122 px cap at
812 x 375, so the chain measures as applied all the way down and the button is
buried exactly as it was before any of it existed. The table above has no row
under 600 px of viewport height, which is the only reason that was ever missed.

Two queries govern the banner and both match on a landscape phone:
(max-width: 56.25rem), which stacks it, and (max-height: 35rem), which exists —
in the breakpoint register's own words — because "a tall banner on a short
screen hides the page it is asking about". The second held one declaration, a
70vh cap with an inner scroll, and a cap does nothing where the banner is
already shorter than it. The banner is 253 px at every width from 375 to 900, so
across the whole band this threshold governs the cap never engaged:

    viewport    banner   of screen   nav band   CLEAR between the two fixed layers
    667 x 375    253       68 %        84         38
    812 x 375    253       68 %        90         32
    844 x 390    253       65 %        90         47
    900 x 400    253       63 %        90         57

Both layers are `position: fixed`, so CLEAR is a constant — it does not move
with scroll. The hero's call to action is 48 px, `.cf-btn`'s own min-height, so
on five of those five sizes there is no scroll offset at which the page's one
button is a live target. Measured after: 191 px of banner and 94-119 of CLEAR.

WHAT IS CHECKED, and it is file shape rather than geometry because every other
check here is:

  a. the (max-height: 35rem) block appears AFTER the (max-width: 56.25rem) one
     in components.css. Both match on a landscape phone and the later block
     wins per declaration; ahead of it, nothing it says survives.
  b. it does more than cap: it returns `.cf-consent__actions .cf-btn--ghost`
     off a full-row flex basis. The ghost's own row is the tallest thing the
     narrow form adds — 52 of the 68 px — and it is a full row only because the
     screen is NARROW, which a short screen is not.
  c. the cap is stated against what it LEAVES, not as a share of the screen.
     70vh said nothing about the nav, which is fixed and present at every
     height: at 568 x 320 it engaged at 224 px and left 12. The value must
     subtract var(--nav-height), so whatever else it takes, the other fixed
     layer is not it.

THE SIXTH LINK, AND IT IS A THIRD CONSUMER RATHER THAN A SIXTH TEST OF THE
FIRST. Everything above is about the hero. The banner is fixed to the viewport's
bottom edge, so it lands on whatever else is pinned to that edge, and the
landing page pins a second thing there: the "Was wir machen" stage, `position:
sticky` at `height: 100vh`, with an index above the card and a progress hairline
under it. Its card is sized off the viewport HEIGHT — `calc((100vh - 13rem) * 2)`,
the derivation check-pin-measure.py declines to judge — and 100vh was read raw.

Measured on patterns/landing-page.html, first load, the stage stuck:

    viewport      bar buried   card foot buried   elementFromPoint at the bar's centre
    1280 x  720      99.4            82.4         the banner's "Datenschutzerklärung"
    1366 x  768      99.4            82.4         the banner's body copy
    1280 x  800      88.2            71.2         the banner's plate
    1024 x  720      81.4            64.4         the banner's plate
    1440 x  900      73.4            56.4         the banner's plate
    1024 x  768      57.4            40.4         the banner's plate
    1280 x  900      38.2            21.2         the banner's plate
    1024 x  900       0               0           the bar
    1920 x 1080       0               0           the bar

Seven of nine sizes the gate admits, and the two clear ones are 900 and 1080 —
the heights anyone checks at, which is the same reason the width half of this
stage's chrome went unseen (see check-pin-measure.py's table, whose zeroes are
the same two rows). The bar is the only element on the stage that says the
section scrubs at all; on seven sizes the middle of it belongs to the banner.

  6. THE STAGE RESERVES THE LAYER OVER ITS FOOT, in both terms, because the
     card's size and the stage's box are two different declarations that have
     to agree:

       --lp-measure          the card's width, derived from the viewport height
       .lp-proc-stage's      the stage's own box, so the trio is centred in
         block axis          what is left rather than in the whole screen

     Both must read var(--cf-consent-height, 0px), and both must be FLOORED at
     the gate's own min-height — read out of the page's own @media prelude here,
     not typed, so the floor cannot drift from the gate it is a floor for.

     The floor is load-bearing and is the one part of this that is not obvious.
     The card's height is max(width / 2, the copy), and the copy is the taller
     column below about 1000 px of card, so past that crossover narrowing the
     card makes it TALLER. An unfloored reservation therefore crops the card
     against the stage's own clip — 90.7 px at 1280 x 720 with the banner up,
     measured — which is a worse picture than the one it was fixing. Floored,
     the reservation is paid in full at and above 820 px of viewport, tapers to
     nothing at the gate's floor, and is byte-identical to the unreserved
     rendering wherever the banner is not up, because max() against a 0px
     fallback is the expression it replaced.

     It also has to be the BLOCK SIZE and not padding, for the mirror image of
     the reason link 4 gives for the hero: the inner is height: 100% of the
     sticky box with align-content: center, so shortening the box lifts the
     trio while padding inside it would push the same content into the same
     banner.

  7. The 0px fallback rule (link 2) reaches page-local <style> blocks as well.
     It used to read assets/css/ only, which is the boundary check-grid-tracks
     .py draws and the one check-page-local-tracks.py exists because of: the
     three consumers of this property are now two stylesheet rules and two
     page-local ones, and a page-local read with a non-zero fallback would
     reserve the banner's space on every visit after the banner is gone.
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
#          — in the sheets AND in the page-local blocks (link 7)
STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)


def property_reads():
    """(where, fallback) for every var(--cf-consent-height, …) that ships."""
    for css in sorted(CSS.glob("*.css")):
        text = strip_comments(css.read_text(encoding="utf-8"))
        for m in re.finditer(r"var\(\s*%s\s*(?:,([^()]*))?\)" % re.escape(PROP), text):
            yield css.name, (m.group(1) or "").strip()
    for page in sorted((ROOT / "design-system").rglob("*.html")):
        if "prototypes" in page.parts:
            continue
        for block in STYLE_BLOCK.findall(page.read_text(encoding="utf-8")):
            text = strip_comments(block)
            for m in re.finditer(r"var\(\s*%s\s*(?:,([^()]*))?\)" % re.escape(PROP),
                                 text):
                yield str(page.relative_to(ROOT)), (m.group(1) or "").strip()


for where, fallback in property_reads():
    if fallback != "0px":
        failures.append(
            "%s: var(%s) falls back to %r, not `0px`. The property exists only "
            "while the banner does; any other fallback reserves space on every "
            "page that never shows one."
            % (where, PROP, fallback or "(no fallback)")
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

# ---- 5 · the short-screen block is the last word, and it shortens ---------
NARROW = "@media (max-width: 56.25rem)"
SHORT = "@media (max-height: 35rem)"


def at_rule_body(text, prelude):
    """The body of the first top-level at-rule with this exact prelude."""
    i = text.find(prelude)
    if i < 0:
        return None, -1
    j = text.index("{", i) + 1
    depth = 1
    k = j
    while k < len(text) and depth:
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
        k += 1
    return text[j: k - 1], i


narrow_body, narrow_at = at_rule_body(components, NARROW)
short_body, short_at = at_rule_body(components, SHORT)

if short_body is None:
    failures.append(
        "components.css: no `%s` block. It is the one height threshold in the "
        "register and the only thing standing between a landscape phone and a "
        "banner that covers 68 %% of it." % SHORT
    )
elif narrow_body is None:
    failures.append("components.css: no `%s` block to order the height one against"
                    % NARROW)
else:
    # a · order
    if short_at < narrow_at:
        failures.append(
            "components.css: `%s` is written before `%s`. Both match on a landscape "
            "phone, and the later block wins per declaration — ahead of the narrow "
            "one the short-screen block cannot undo a single thing it says."
            % (SHORT, NARROW)
        )
    short_decls = strip_comments(short_body)
    # b · the ghost comes off its own row
    ghost = re.search(r"\.cf-consent__actions\s+\.cf-btn--ghost\s*\{([^}]*)\}",
                      short_decls)
    if not ghost:
        failures.append(
            "components.css %s: nothing returns `.cf-consent__actions .cf-btn--ghost` "
            "off the full-width row the narrow block gives it. That row is 52 of the "
            "68 px this block has to save, and it is a full row only because the "
            "screen is NARROW — a screen under 35rem tall is landscape, so width is "
            "the axis with room. Without it the banner stands 253 px on a 375 px "
            "screen and leaves 32 px between the nav and itself, which is less than "
            "the 48 px call to action that has to fit there." % SHORT
        )
    else:
        flex = re.search(r"flex\s*:\s*([^;]+)", ghost.group(1))
        if not flex:
            failures.append(
                "components.css %s: the `.cf-btn--ghost` rule declares no `flex`, so "
                "the narrow block's `flex: 1 1 100%%` still stands and the ghost still "
                "holds a row of its own." % SHORT
            )
        elif "100%" in flex.group(1):
            failures.append(
                "components.css %s: `.cf-btn--ghost` is back on a 100%% basis — a row "
                "of its own. That is the narrow screen's answer on the short screen's "
                "axis.\n    flex: %s" % (SHORT, " ".join(flex.group(1).split()))
            )
    # c · the cap says what it leaves
    cap = re.search(r"\.cf-consent\s*\{([^}]*)\}", short_decls)
    cap_value = re.search(r"max-height\s*:\s*([^;]+)", cap.group(1)) if cap else None
    if not cap_value:
        failures.append(
            "components.css %s: the banner has no max-height backstop left. It is "
            "rarely reached now and it is still what holds the line at 320 px of "
            "screen." % SHORT
        )
    elif "--nav-height" not in cap_value.group(1):
        failures.append(
            "components.css %s: the banner's max-height does not subtract "
            "var(--nav-height).\n    max-height: %s\n    A cap has to be stated "
            "against what it LEAVES. A bare share of the screen says nothing about "
            "the nav, which is the other fixed layer and is there at every height: "
            "70vh engaged at 568 x 320 and left 12 px of page between the two of them."
            % (SHORT, " ".join(cap_value.group(1).split()))
        )

# ---- 6 · the pinned stage reserves the layer over its foot ----------------
# The pinned stage this section holds moved to the prototype on 2026-07-28.
PAGE = ROOT / "design-system" / "prototypes" / "statement-to-process.html"
STAGE_SEL = ".lp-proc-stage"
MEASURE = "--lp-measure"
# The block axis, in both spellings — a stage shortened by either is shortened
# the same amount, the way check-pin-measure.py reads the inline one.
BLOCK_SIZE = re.compile(r"(?<![-\w])(?:height|block-size)\s*:\s*([^;]+)", re.I)

if not PAGE.exists():
    failures.append("missing %s" % PAGE.relative_to(ROOT))
else:
    page_css = "\n".join(STYLE_BLOCK.findall(PAGE.read_text(encoding="utf-8")))
    page_css = strip_comments(page_css)

    # The floor is the gate's own min-height, read rather than typed. The gate
    # is the one prelude on this page carrying both a min-width and a
    # min-height — .cf-pin's, adopted from here.
    gate = re.search(r"@media[^{]*\(\s*min-height\s*:\s*([\d.]+rem)\s*\)", page_css)
    if not gate:
        failures.append(
            "landing-page.html: no @media prelude with a min-height, so there is no "
            "gate to floor the stage's reservation against. The floor cannot be "
            "typed here — it has to be the number the gate admits the stage at."
        )
        floor = None
    else:
        floor = gate.group(1)

    def page_rule_bodies(text, selector):
        """Every `selector { … }` in a page block, at any indent, joined.

        rule_body() above anchors at column 0 for the sheets; a page-local
        block is indented inside <style>, and this page declares the stage
        twice — the measure pass-through and the grid. Both are the rule.
        """
        out = []
        for m in re.finditer(r"(?m)^\s*" + re.escape(selector) + r"\s*\{", text):
            i, depth = m.end(), 1
            while i < len(text) and depth:
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                i += 1
            out.append(text[m.end(): i - 1])
        return "\n".join(out)

    def reserves(value):
        return re.search(r"var\(\s*%s\s*,\s*0px\s*\)" % re.escape(PROP), value)

    def floored(value):
        return floor and re.search(r"max\(\s*%s\s*," % re.escape(floor), value)

    consumers = [
        (MEASURE, re.search(r"%s\s*:\s*([^;]+)" % re.escape(MEASURE), page_css),
         "the card's width is derived from the viewport height, so it has to be "
         "derived from the part of it the reader can see"),
        (STAGE_SEL + " block axis",
         BLOCK_SIZE.search(page_rule_bodies(page_css, STAGE_SEL)),
         "the stage's own box has to end where the banner begins, or the trio is "
         "centred in a screen 144 px of which is not there"),
    ]
    for name, found, why in consumers:
        if not found:
            failures.append(
                "landing-page.html: no %s declaration in the page's <style> block. "
                "%s." % (name, why[0].upper() + why[1:])
            )
            continue
        value = " ".join(found.group(1).split())
        if not reserves(value):
            failures.append(
                "landing-page.html %s does not reserve the consent banner.\n"
                "    %s\n"
                "    The banner is fixed to the viewport's bottom edge and this stage "
                "is pinned to the same edge — %s. Without a var(%s, 0px) term the "
                "banner buries the progress bar on seven of the nine viewports the "
                "gate admits, and elementFromPoint at the middle of the bar returns "
                "the banner." % (name, value, why, PROP)
            )
        elif not floored(value):
            failures.append(
                "landing-page.html %s reserves the banner without flooring at the "
                "gate's own min-height (%s).\n    %s\n"
                "    The card's height is max(width / 2, the copy) and the copy is "
                "the taller column below about 1000 px of card, so past that "
                "crossover an unfloored reservation makes the card TALLER and the "
                "stage's clip crops it — 90.7 px at 1280 x 720, measured. Write the "
                "reservation as max(%s, …)." % (name, floor or "?", value, floor or "?")
            )
    # a cap on the box, not padding inside it — the mirror of link 4
    stage_body = page_rule_bodies(page_css, STAGE_SEL)
    for prop in ("padding-block-end", "padding-bottom", "padding-block", "padding"):
        for d in re.finditer(r"(?m)^\s*%s\s*:\s*([^;]+);" % re.escape(prop),
                             stage_body):
            if PROP in d.group(1):
                failures.append(
                    "landing-page.html %s: `%s` reads %s. The inner is height: 100%% "
                    "of the sticky box with align-content: center, so the reservation "
                    "has to shorten the BOX — padding inside it pushes the same trio "
                    "into the same banner while measuring as applied."
                    % (STAGE_SEL, prop, PROP)
                )

if failures:
    print("check-consent-clearance.py: %d problem(s)\n" % len(failures))
    for f in failures:
        print("  - %s\n" % f)
    sys.exit(1)

print("check-consent-clearance.py: consent clearance reserved and released.")
