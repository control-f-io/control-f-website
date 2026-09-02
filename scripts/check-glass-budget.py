#!/usr/bin/env python3
"""Enforce the glass budget.

`backdrop-filter` is the most expensive thing in this stylesheet, and
foundations/materials.html states what keeps it affordable as three rules in
prose: exactly two blurred layers on a shipping page and never a third, one
blur radius for the whole system, and nothing scroll-driven moving on a blurred
layer. It also publishes a census of where the layers are — "landing page 2,
Über uns 1, and 1 each on the component pages that demo it" — in a sentence
that names its own problem two paragraphs later: *a count somebody has to
remember*.

It also carries a second table nothing generates — "Every panel, and what it is
made of", the chapter's verdict on each panel in the system — and that one is
prose by necessity, because a verdict is an argument. Which is why it, and the
sentences around it, went stale while the stamped census beside them did not:
"Two surfaces in the whole system are frosted" outlived two more of them. A
stamp over a row count cannot read a paragraph. The sixth claim binds that table
to the same derived set the census is counted from.

AND IT BOUND ONLY THE FROSTED HALF OF IT, which is how the same drift happened
again one material over. That table is titled "Every panel, and what it is made
of" and its verdict on most panels is *not* glass — it is contour, and a
response made of light rather than of blur. Claim 6 held the glass rows to the
stylesheet and left every other row unbound, so a panel that answers a pointer
with `--sheen-panel` could be added, renamed or dropped and the table would
never notice. One had been: the register — `.cf-result`, `.cf-vacancy` and
`.cf-event`, one drawing behind the search results, the open positions and a
day on the calendar — is a panel on the page wash with a travelling light on it,
on two shipping pages, and the table that claims to name every panel did not
name it. The seventh claim is claim 6 read against the other derived set, so a
lit panel enters the verdict table by existing, exactly as a frosted one does.

AND THE LIT RIM WAS EIGHT COPIES OF THREE NUMBERS. The eighth claim is the
second claim read one property over. Claim 2 holds every backdrop-filter to
--glass-blur because "a literal anywhere is a second material wearing the first
one's name"; the specular band that crosses the lit edge is the same kind of
fact and had none of that protection. Its width and its two off-canvas
positions were written out on .cf-nav::after, .cf-btn--glass::before and
.cf-info-card--glass::before, and twice more inside three pairs of keyframes
holding identical values under three names — on three surfaces whose own token
comment says they share the band and differ only in the container and the
clock. The three are tokens now, the crossing is one keyframe set, and the two
endpoints are RE-DERIVED here from the band rather than compared to a table,
the way check-gradient-family.py recomputes its waypoint.

AND THE MOST EXPENSIVE LAYER ON THE LANDING PAGE WAS ONE NOBODY COULD SEE. The
ninth claim is the Don't list's oldest rule read from the other side. That list
already forbids `backdrop-filter` under an opaque background — the blur cannot
be seen and still costs a GPU pass — and a layer at `opacity: 0` cannot be seen
either, with the occluder simply on the other side of it.
`.act-rail--glass::before` was exactly that: the blur declared unconditionally
on a plate whose rest opacity is 0, on the one page this file grants its largest
allowance to, and PAGE_BUDGET's entry for that page argues from the opposite
premise in as many words — the plate "is painted only on :hover /
:focus-within". tokens.css said it too, and so did the verdict column on
materials.html. Three documents, one premise, and the stylesheet asserting the
other thing while leaving it to the compositor to notice that the result is
invisible. The claim resolves the rest state of every layer the census counts
and fails one that is both blurred and invisible; it reads the ELEMENT and not
the rule, because the pair is rarely in one block — here the blur is on the
modifier and the opacity is on the base it modifies.

AND THE LIT PANEL WAS THREE COPIES OF THREE NUMBERS. The tenth claim is the
eighth read one MATERIAL over. Claim 8 rescued the specular band's geometry from
being restated by every surface that used it; --sheen-panel, the light layer's
answer for a surface that is NOT glass, had exactly the protection the rim had
before it: none. A `200% 100%` size, a `0 0` park and a `100% 0` answer, written
out on .cf-accordion__summary, .cf-blog-card and the register. The three are
tokens now, and the resting state is RE-DERIVED rather than asserted — the sheen
slides where the rim crosses, so its endpoints are the image's own two ends and
claim 8's off-canvas arithmetic does not apply, but the park is an equality with
no air in it: the box shows the image's first 1/b there, so the panel is clean
only while the gradient's transparent head reaches that far. At b = 200 % the
window is 50 % and the head ends at exactly 50 %, in both themes, and each theme
is measured separately because their lit stops differ.

Every one of those is invisible in a screenshot. A third blurred layer renders
correctly; it just costs. A literal `blur(20px)` on some future panel renders
correctly; it just forks the material. A gradient animated across a blurred
sheet renders correctly; it re-rasterises the blur on every frame of a scroll.
Nothing goes red, nothing looks wrong, and the page is slower on the hardware
least able to afford it — which is the whole test for what belongs in one of
these scripts, and the reason the other three exist.

WHAT COUNTS AS GLASS IS READ OUT OF THE STYLESHEET, NOT LISTED HERE. The script
finds every rule in the shipping CSS that declares `backdrop-filter` and takes
its selectors as the definition. A fourth frosted surface added later therefore
enters the budget by existing, rather than by somebody remembering to add it to
a list in this file — the same reason check-gradient-family.py recomputes its
waypoint from the oklab path instead of comparing against a table of hexes. A
checker whose scope is hand-maintained drifts exactly the way the prose census
did. WHAT COUNTS AS A LIT PANEL IS READ OUT THE SAME WAY: every shipping rule
that paints `var(--sheen-panel)`, selectors taken as the definition. Two derived
sets, one walk of the pages, and neither of them a list.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-glass-budget.py          # check, exit 1 on drift
    python3 scripts/check-glass-budget.py --fix    # rewrite the census + stamp
    python3 scripts/check-glass-budget.py -v       # list every page, not only hits
"""

import argparse
import hashlib
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"
MATERIALS_DOC = DS / "foundations" / "materials.html"

# The stylesheets that ship to control-f.de. docs.css is documentation chrome
# and does not ship — the same boundary check-spacing-scale.py draws.
#
# acts.css IS one of them and was missing, which is the only kind of gap that
# matters in a script whose whole claim is that a frosted surface enters the
# budget by existing. patterns/landing-page.html loads it, so a backdrop-filter
# written there would have shipped on the page carrying the tightest budget in
# the system and been invisible to every one of the five claims below — the
# scope was hand-maintained after all, one list further out than the one this
# file's header is careful about. .act-rail::before is the surface that found
# it; the fix is not about that surface.
SHIPPING_CSS = ("tokens.css", "base.css", "components.css", "acts.css")

# A shipping page gets two blurred layers. The figure is not this script's: it
# is measured in foundations/materials.html, where the two layers on the landing
# page are shown to overlap for about 150 px of scroll at no measurable cost,
# and the rule kept is the one that pays rather than the stronger one that does
# not. Raising this number is a design decision about a page's frame budget, not
# a checker setting — something has to give up its blur first.
SHIPPING_BUDGET = 2

# A page allowed more than the default, with the argument written next to the
# number. The default above is a proxy: tokens.css states the rule as "the count
# of SIMULTANEOUSLY blurred layers", and a static count of elements is the
# conservative reading of it, which is the right default because on almost every
# page every blurred layer is live whenever the page is.
#
# patterns/landing-page.html is the one page where the proxy and the rule come
# apart, and the reason is legible in the CSS rather than asserted here.
# .act-rail--glass::before is painted only on :hover / :focus-within; the rail
# catches neither without pointer-events, which it only has while act-rail.js
# has set .is-live, which happens while the acts own the viewport — about 4 000
# px past the hero CTA that is the page's second layer. The nav band, which is
# always one of the two, is the only layer the plate can ever be composited
# with. Two at a time, three on the page.
#
# THE PLATE IS A MODIFIER FOR THIS PARAGRAPH'S SAKE. patterns/expertise.html
# adopted the same rail and could not make the same argument: its second layer
# is the lectern inside the four-field stage, which is on screen for the whole
# of the chapter the rail exists to skip, and no gate, query or state in the
# stylesheet keeps the two apart. Rather than write the entry this comment
# forbids, the blur moved onto .act-rail--glass — so the plate there is the
# opaque stand-in tokens.css already swaps in wherever the browser cannot blur,
# and the census counts what the page actually paints.
#
# THIS IS NOT A PLACE TO PUT A PAGE THAT IS MERELY OVER. An entry here has to
# name two layers that cannot be lit together and say what makes that true in
# the stylesheet — a scroll gate, a media query, a state that excludes the
# other. "It measured fine" is the argument for raising SHIPPING_BUDGET, and
# something still has to give up its blur first.
#
# patterns/expertise.html is the second entry, and it is a weaker argument than
# the first — so the number it buys is written here with what it costs and not
# only with what excludes what.
#
# Five of its six are the plate and the four copy cards, and those five ARE
# excluded from each other by a media query the page already had: inside the
# pinned gate (64rem x 45rem, view timelines, no reduced-motion) the plate is
# the material and `.ex-step .cf-info-card` sets backdrop-filter: none on every
# card; outside it the plate is display: none and each card carries the
# material instead, because down there there is no plate to stand on and the
# cards stand on the same full-bleed lattice the plate was put there to calm.
# So the pinned tier spends the nav and the plate. Two, the rule unchanged.
#
# THE FLOW TIER SPENDS THREE, AT THE SEAMS. The four cards are one column, so
# two of them are on screen together whenever the reader is between steps:
# measured at 375 x 812, a copy card is about 650 px tall and 349 px of figure
# and gap separate one from the next, which puts two cards and the navigation
# band on screen together for 463 px of each roughly 1 050 px step — a third
# composited layer for about 44 % of that section's scroll, on the hardware
# this budget exists for. That is the exception this entry buys, it is the
# first one in the system that is not free, and the cheaper answer it was
# weighed against is in the page: --surface-glass-solid on the same cards,
# which is the material's own no-blur stand-in and costs nothing.
PAGE_BUDGET = {"patterns/landing-page.html": 3, "patterns/expertise.html": 6}

# Documentation pages are censused, not capped. A page whose subject IS the
# material has to be allowed to show it: foundations/materials.html carries
# three plates of its own — two samples and the band in the layer stack — and
# capping it at a selling page's budget would mean documenting glass without
# drawing it. The census is what makes a jump here visible anyway.
DOC_BUDGET = None

# prototypes/ is out of scope. They are motion studies, none has been reconciled
# with the tokens, and nothing in components/ depends on them — the same
# exclusion check-gradient-family.py makes, for the same reason.
SKIP_DIRS = {"prototypes", "assets"}

# The one blur in the system. Every backdrop-filter in shipping CSS reads this
# token; a literal radius is two materials that merely resemble each other.
BLUR_TOKEN = "var(--glass-blur)"

# The user-action states a rule may be written in without changing WHICH element
# it lands on. That is the whole test for admitting one here, and it is why the
# set is these five and not "pseudo-classes": :hover, :focus and their relatives
# are a fact about the reader, not about the document, so a selector carrying one
# hangs off exactly the elements the same selector without it hangs off. A
# structural pseudo-class does not have that property — .cf-x:first-child names a
# subset of .cf-x and admitting it would make the census a guess — and neither
# does :not(), which needs a selector engine to answer at all.
#
# WHAT THIS BUYS, AND WHAT IT DOES NOT. It lets a surface declare the material in
# the state that shows it and not at rest, which is what .act-rail--glass now
# does. It does not widen the census by one element: GlassCounter matches on the
# class attribute, and a state pseudo-class contributes nothing to that. The
# count is unchanged by construction, which is the point — the budget is a
# statement about elements, and this is a statement about when.
STATE_PSEUDO = "hover|focus|focus-within|focus-visible|active"

# A selector this script can count: one class, optionally one user-action state,
# optionally one pseudo-element. Deliberately narrow. Anything wider — a
# descendant combinator, an attribute, a :not() — would need a real selector
# engine to match against the HTML, and a checker that guesses at matching is
# worse than none. A selector that does not reduce is a finding rather than a
# skip, so the failure mode is "teach me or simplify it" and never "quietly
# stopped counting that one".
SIMPLE_SELECTOR = re.compile(
    r"^\.([A-Za-z0-9_-]+)(?::(?:%s))?(::[a-z-]+)?$" % STATE_PSEUDO
)

# The same shape read for its middle rather than its ends: which state a rule is
# written in, empty string for the rest state. Claim 9 is entirely about that
# distinction, and asking SIMPLE_SELECTOR for it would mean a third capture
# group on a pattern two other call sites already read by position.
SELECTOR_PARTS = re.compile(
    r"^\.([A-Za-z0-9_-]+)(:(?:%s))?(::[a-z-]+)?$" % STATE_PSEUDO
)

# Properties whose animation re-rasterises the blur underneath on every frame.
# transform is here even though it is normally the cheap one: a blurred layer
# has to re-read its backdrop when it moves over it.
REPAINTS_BLUR = ("opacity", "background", "transform", "filter", "clip-path", "mask")

# THE MATERIAL'S SWITCHABLE HALF: the blur, and every tint it composites under.
# tokens.css carries three blocks whose job is to turn the material off — the
# browser cannot blur, the reader asked for less transparency, the reader chose
# the palette — and its own comment already states the invariant for one axis of
# them: "repeat every token the inverse block declares, not just the ones that
# differ". The other axis went unstated and was broken. --surface-glass-thin sat
# out the forced-colours block entirely, so the one surface using it stayed
# translucent in a mode where nothing else was.
#
# A PREFIX AND NOT A LIST, for the reason SIMPLE_SELECTOR is a shape and not a
# roster: a fourth tint enters this claim by being named like a tint, rather than
# by somebody remembering this file exists.
#
# --glass-edge, --glass-rim-light, --glass-border and --glass-lookahead are
# deliberately NOT in the family, and the boundary is the chapter's own, not a
# convenience. The three blocks neutralise TRANSLUCENCY. An edge is a contour:
# foundations/materials.html says in as many words that the edge light stays,
# and forced colours recovers it as a border next to the rule that draws it. A
# token that is out of scope for the fallbacks has no business being demanded by
# a checker that enforces them.
GLASS_TINT = re.compile(r"^--surface-glass(-[a-z]+)?$")
GLASS_SWITCH = "--glass-blur"

# What makes a block one that neutralises the material — derived, so a fourth
# fallback answering a fourth question is held to the same standard on the day
# it is written. There is nothing else --glass-blur: none could mean.
NEUTRALISED = re.compile(r"^\s*%s\s*:\s*none\s*$" % GLASS_SWITCH)


def blank_comments(text):
    """Comments replaced by spaces IN PLACE, so every offset and every line
    number in the result is the one a reader will find in the file.

    Deleting them instead is the obvious version and makes every line number
    this script reports wrong by however much prose sits above it — which in
    these stylesheets is most of the file. `.cf-nav::before` is at line 916 and
    a delete-based strip puts it at 299. A checker that names the wrong line is
    worse than one that names none, because the reader goes and looks."""
    chars = list(text)
    for m in re.finditer(r"/\*.*?\*/", text, re.S):
        for i in range(m.start(), m.end()):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)


def rules(text):
    """Every selector/block pair in a stylesheet, with the selector's line.

    At-rules are walked into rather than over, because both of this system's
    conditional blocks matter here: the glass tokens are redefined inside
    @supports and @media, and a rule that animates a blurred layer would most
    naturally be written inside `@media (prefers-reduced-motion: no-preference)`
    — which is exactly where this script has to be able to see it.
    """
    text = blank_comments(text)
    out = []
    open_stack = []
    start = 0
    for i, ch in enumerate(text):
        if ch == "{":
            raw = text[start:i]
            # The line the SELECTOR starts on, not the line the brace is on: a
            # multi-line selector list should point at its first selector.
            sel_at = start + (len(raw) - len(raw.lstrip()))
            open_stack.append((raw.strip(), i + 1, text.count("\n", 0, sel_at) + 1))
            start = i + 1
        elif ch == "}":
            if open_stack:
                head, body_start, line = open_stack.pop()
                if not head.startswith("@"):
                    out.append((head, text[body_start:i], line))
            start = i + 1
    return out


def scoped_rules(text):
    """rules(), but each rule carries the at-rule condition enclosing it.

    The other four claims are about a declaration wherever it happens to be, so
    rules() can throw the @-heads away. This one is about a BLOCK — which
    selectors sit together under one condition, and what the set of them
    declares — so the condition has to survive the walk. Nested conditions join
    with " and ", which is what they mean and what makes the message readable.
    """
    text = blank_comments(text)
    out, stack, at, start = [], [], [], 0
    for i, ch in enumerate(text):
        if ch == "{":
            raw = text[start:i]
            sel_at = start + (len(raw) - len(raw.lstrip()))
            head = raw.strip()
            stack.append((head, i + 1, text.count("\n", 0, sel_at) + 1))
            if head.startswith("@"):
                at.append(head)
            start = i + 1
        elif ch == "}":
            if stack:
                head, body_start, line = stack.pop()
                if head.startswith("@"):
                    at.pop()
                else:
                    out.append((" and ".join(at), head, text[body_start:i], line))
            start = i + 1
    return out


RIM_LIGHT = "--glass-rim-light"
RIM_BAND = "--glass-rim-band"
RIM_PARK = "--glass-rim-park"
RIM_CROSS = "--glass-rim-cross"


def rim_geometry():
    """The specular band's three published numbers, read out of tokens.css.

    Percentages, unitless in the dict. --glass-rim-band is how wide the band is
    as a share of the sheet it crosses; --glass-rim-park and --glass-rim-cross
    are the two background-position values that stand it fully off one end and
    fully off the other. Every one of the three used to be a literal written out
    on three surfaces and inside three pairs of keyframes.
    """
    text = blank_comments((CSS / "tokens.css").read_text())
    out = {}
    for name in (RIM_BAND, RIM_PARK, RIM_CROSS):
        m = re.search(r"^\s*%s\s*:\s*(-?[0-9.]+)%%\s*;" % name, text, re.M)
        if m:
            out[name] = float(m.group(1))
    return out


def rim_rules():
    """Every shipping rule that paints the specular band, every rule that
    animates one of those selectors, and every keyframe block that moves a
    background-position.

    Derived the same way glass itself is: the definition of "a rim" is "a rule
    that paints --glass-rim-light", read out of the stylesheet, so a fourth lit
    surface is held to this claim by existing rather than by being listed here.
    """
    painters, animators, frames = [], [], {}
    for name in SHIPPING_CSS:
        text = (CSS / name).read_text()
        for head, body, line in rules(text):
            sels = {s.strip() for s in head.split(",") if s.strip()}
            if RIM_LIGHT in body:
                painters.append((name, line, sels, body))
            names = set()
            for decl in (d.strip() for d in body.split(";") if d.strip()):
                prop, sep, value = decl.partition(":")
                if prop.strip() in ("animation", "animation-name"):
                    names |= {
                        w
                        for w in re.findall(r"[A-Za-z_-][\w-]*", value)
                        if w.startswith("cf-")
                    }
            if names:
                animators.append((sels, names))
        for at, head, body, line in scoped_rules(text):
            m = re.search(r"@keyframes\s+([\w-]+)", at)
            if m and "background-position" in body:
                frames.setdefault(m.group(1), []).append((name, line, head, body))
    return painters, animators, frames


def declared(body):
    """Custom properties this block declares, and every one it reads."""
    sets, reads = {}, set()
    for decl in (d.strip() for d in body.split(";") if d.strip()):
        prop, sep, value = decl.partition(":")
        if sep and prop.strip().startswith("--"):
            sets[prop.strip()] = value.strip()
        reads |= set(re.findall(r"var\(\s*(--[A-Za-z0-9_-]+)", decl))
    return sets, reads


def fallback_holes():
    """Claim 5: every block that switches the material off switches ALL of it off.

    The glass fallbacks work by redefining tokens rather than by giving each
    component its own branch — "Redefining the tokens here means no component
    needs its own fallback", as tokens.css puts it. That architecture buys a
    great deal and has exactly one failure mode, which is silent: a tint left
    out of one block keeps its live value there, and the component reading it
    keeps a material the block was written to take away. Nothing renders wrong.
    It renders as though the reader had never asked.

    A token is excused from a block if the block READS it — --surface-glass-solid
    is the answer two of the three blocks give, and demanding that an answer
    also be redefined in terms of itself would be asking for a circle.
    """
    text = (CSS / "tokens.css").read_text()
    scoped = scoped_rules(text)

    # The family, taken from the base cascade: every tint declared outside any
    # block that turns the material off. Derived, so a fourth tint is in scope
    # the moment it is declared.
    switching = {
        at
        for at, _, body, _ in scoped
        if at and any(NEUTRALISED.match(d) for d in body.split(";"))
    }
    family = {
        name
        for at, _, body, _ in scoped
        if at not in switching
        for name in declared(body)[0]
        if GLASS_TINT.match(name)
    }

    holes = []
    for at in sorted(switching):
        for _, head, body, line in [r for r in scoped if r[0] == at]:
            sets, reads = declared(body)
            if not (GLASS_SWITCH in sets or set(sets) & family):
                continue    # a rule that is in the block for some other reason
            missing = sorted(family - set(sets) - reads)
            if missing:
                holes.append((at, head, line, missing))
    return sorted(family), holes


def glass_rules():
    """Every shipping rule that declares backdrop-filter, with its selectors.

    This is the definition of "glass" for the whole script. It is derived rather
    than declared so that the budget cannot be evaded by adding a frosted
    surface the list in this file has never heard of.
    """
    found = []
    for name in SHIPPING_CSS:
        for head, body, line in rules((CSS / name).read_text()):
            decls = [d.strip() for d in body.split(";") if d.strip()]
            bf = [d for d in decls if re.match(r"^-?(?:webkit-)?backdrop-filter\s*:", d)]
            if not bf:
                continue
            found.append(
                {
                    "file": name,
                    "line": line,
                    "selectors": [s.strip() for s in head.split(",") if s.strip()],
                    "values": [d.split(":", 1)[1].strip() for d in bf],
                }
            )
    return found


# The other material a panel can be made of, and the reason the seventh claim
# exists. --sheen-panel is the light layer's answer for a surface that is NOT
# glass: a gradient parked in its own transparent half and slid across on hover,
# so a contour panel reads as lit rather than tinted. foundations/materials.html
# calls it "a response" and draws the line the whole verdict column turns on —
# a panel gets one only if it answers, because lighting a panel that does
# nothing when you click it promises otherwise.
#
# READ AS A CONSUMPTION AND NOT AS A DECLARATION, which is the one difference
# from the blur. `backdrop-filter: ...` is only ever written by a surface that
# is glass; `--sheen-panel` is written once in tokens.css, twice counting the
# inverse theme, by the token itself. So the set is the rules that READ it —
# declared()'s second return — and the two declarations fall out for free by
# never appearing in it.
SHEEN_TOKEN = "--sheen-panel"


def sheen_rules():
    """Every shipping rule that paints --sheen-panel, with its selectors.

    The mirror of glass_rules(), and derived for the same reason: a lit panel
    added later enters the verdict table by existing rather than by somebody
    remembering this file. An opt-out is not a consumer — .cf-blog-card--listing
    sets `background-image: none` on the archive entry that has no article
    behind it, reads nothing, and correctly never enters the set.
    """
    found = []
    for name in SHIPPING_CSS:
        for head, body, line in rules((CSS / name).read_text()):
            if SHEEN_TOKEN not in declared(body)[1]:
                continue
            # No "values" key, unlike glass_rules(): that one carries the blur's
            # declared value because claim 2 reads it back, and a sheen has no
            # single declared value to carry. The whole body rides along
            # instead, because claim 10 reads two properties off it rather than
            # one — the band and the park are separate declarations and the
            # claim fails them separately.
            found.append(
                {
                    "file": name,
                    "line": line,
                    "selectors": [s.strip() for s in head.split(",") if s.strip()],
                    "body": body,
                }
            )
    return found


SHEEN_BAND = "--sheen-band"
SHEEN_PARK = "--sheen-park"
SHEEN_CROSS = "--sheen-cross"


def sheen_geometry():
    """The lit panel's three published numbers, read out of tokens.css.

    The mirror of rim_geometry(), and unitless in the dict for the same reason.
    --sheen-band is how many times the box the gradient image is drawn at;
    --sheen-park and --sheen-cross are the two background-position values that
    put the image's own two ends against the box. All three used to be literals
    written out on three surfaces.
    """
    text = blank_comments((CSS / "tokens.css").read_text())
    out = {}
    for name in (SHEEN_BAND, SHEEN_PARK, SHEEN_CROSS):
        m = re.search(r"^\s*%s\s*:\s*(-?[0-9.]+)%%\s*;" % name, text, re.M)
        if m:
            out[name] = float(m.group(1))
    return out


def sheen_heads():
    """Where every declared --sheen-panel stops being fully transparent.

    One entry per declaration, so the inverse theme's own gradient is measured
    rather than assumed to match the light theme's — the two differ in their lit
    stops (0.5/0.34 against 0.12/0.10) and a claim that read only the first
    would pass a theme it had never looked at.

    Returns [(line, head_pct)] where head_pct is the position of the LAST stop
    whose alpha is still zero. Everything before it is clear; light begins
    somewhere after it. Stops with no explicit position are not read: every
    --sheen-panel in the tree writes all four, and a gradient whose stops are
    positional guesses is not something this claim should be quietly averaging.
    """
    text = blank_comments((CSS / "tokens.css").read_text())
    heads = []
    for m in re.finditer(r"%s\s*:\s*([^;]*);" % SHEEN_TOKEN, text):
        head = 0.0
        for stop in re.finditer(
            r"rgba?\([^)]*?,\s*([0-9.]+)\s*\)\s+(-?[0-9.]+)%", m.group(1)
        ):
            if float(stop.group(1)) == 0:
                head = max(head, float(stop.group(2)))
        line = text[: m.start()].count("\n") + 1
        heads.append((line, head))
    return heads


def rest_layers():
    """The rest state of every countable layer in the shipping CSS.

    A "layer" is one class plus one pseudo-element — `("act-rail", "::before")`
    — which is the finest thing this script can name without a selector engine,
    and exactly the granularity a backdrop-filter lives at. "Rest" means every
    rule for that layer written in NO user-action state, in source order, so the
    last declaration of a property wins the way the cascade would. Everything
    here is a single class, so specificity never separates two of them and
    source order is the whole answer.

    Returns {(class, pseudo): {property: (value, file, line)}}. The provenance
    rides along because the finding has to name the line that declared the
    value, which is often not the line that declared the other half of the pair.
    """
    layers = {}
    for name in SHIPPING_CSS:
        for head, body, line in rules((CSS / name).read_text()):
            for sel in (s.strip() for s in head.split(",") if s.strip()):
                m = SELECTOR_PARTS.match(sel)
                if not m or m.group(2):        # unreducible, or a state rule
                    continue
                key = (m.group(1), m.group(3) or "")
                slot = layers.setdefault(key, {})
                for decl in (d.strip() for d in body.split(";") if d.strip()):
                    prop, sep, value = decl.partition(":")
                    if not sep:
                        continue
                    slot[prop.strip()] = (value.strip(), name, line)
    return layers


def glass_classes(found):
    """The class names a blurred layer hangs off, and the selectors that failed
    to reduce to one.

    Shape work only — it reads selectors, never declarations — so sheen_rules()
    goes through it unchanged. The register is why that matters: its three
    classes share one rule and one drawing, and a helper that assumed one class
    per rule would have had to be told about them."""
    classes, unreducible = set(), []
    for rule in found:
        for sel in rule["selectors"]:
            m = SIMPLE_SELECTOR.match(sel)
            if m:
                classes.add(m.group(1))
            else:
                unreducible.append((rule["file"], rule["line"], sel))
    return classes, unreducible


class GlassCounter(HTMLParser):
    """Counts ELEMENTS carrying a glass class, not class occurrences.

    The distinction is load-bearing on foundations/materials.html, whose veil
    samples carry `material-glass material-glass--veil` — two classes, one
    element, and exactly one blurred layer, because only the base class declares
    the filter. Counting class hits would report that page at five layers and
    then fail a budget nothing had actually spent.
    """

    def __init__(self, classes):
        super().__init__(convert_charrefs=True)
        self.classes = classes
        self.hits = []
        # WHICH glass, beside how much of it. The hits are formatted for a
        # reader — `tag.class`, and `tag.class.class` where one element carries
        # two — so reading the names back out of them is parsing a message.
        # Claim 6 needs the names, so the parser keeps them.
        self.seen = set()
        # AND CLAIM 9 NEEDS THE OTHER NAMES — every class on a counted element,
        # not only the glass ones. The rest state of a blurred layer is rarely
        # declared by the class that carries the blur: .act-rail--glass::before
        # is the material and .act-rail::before is the plate it is a modifier
        # of, and the opacity that decides whether any of it can be seen is on
        # the second. A set of glass classes cannot reach that rule; the
        # element's own class attribute can, and it is the only thing in this
        # file that knows the two belong to one layer.
        self.carried = set()

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class") or ""
        names = set(cls.split())
        if names & self.classes:
            self.hits.append(tag + "." + ".".join(sorted(names & self.classes)))
            self.seen |= names & self.classes
            self.carried.add(frozenset(names))

# The English edition under patterns/en/ is generated, not written —
# scripts/build-i18n.py builds it from the German page beside it and changes
# only the words. It carries the same markup, the same classes, the same
# thresholds and the same glass by construction, so every fact this file
# keeps is already kept one directory up; asserting it twice would only mean
# two tables to edit whenever one page changes. `build-i18n.py --check` is
# what holds the mirror to its source. Same argument check-links.py makes
# about the generated pages at the repository root.
GENERATED = "patterns/en/"

# The same argument, one page further: patterns/beitrag-*.html is one post of
# the news archive spliced into blog-artikel.html, patterns/stelle-*.html is
# one opening spliced into karriere-stelle.html, and patterns/news-thema-*.html
# is one topic's slice of the archive spliced into news-thema.html.
# The glass on it is that page's glass, layer for layer — the consent banner and
# nothing else — and it arrives there without anybody choosing it. Counted
# separately, the census would gain a row per published post, every one of them
# a copy of the row above it, and writing an article would fail this check until
# somebody re-stamped a number that had not changed in meaning.
GENERATED_PAGE = re.compile(r"^patterns/(?:beitrag|stelle|news-thema)-.+\.html$")


def pages():
    for path in sorted(DS.rglob("*.html")):
        if set(p.name for p in path.relative_to(DS).parents) & SKIP_DIRS:
            continue
        rel = path.relative_to(DS).as_posix()
        if rel.startswith(GENERATED) or GENERATED_PAGE.match(rel):
            continue
        yield path


def census(classes, sheen):
    """Every page under design-system/, with how many blurred layers it carries.

    Returns the rows and, beside them, the glass classes that actually reach a
    SHIPPING page. One walk answers both, and it has to be one walk: the second
    answer is what claim 6 holds the panel table to, and a separate pass would
    be a second opinion about which pages ship.

    THE LIT PANELS RIDE THE SAME WALK, for the same sentence one material over.
    Claim 7 needs to know which sheened classes reach a shipping page, and "which
    pages ship" has to have one answer in this file, not two. Only the blurred
    layers are counted — a sheen costs nothing and is not on any budget — so the
    third return is a set and never a column.
    """
    rows, shipping_classes, shipping_sheen, carried = [], set(), set(), set()
    for path in pages():
        html = path.read_text()
        parser = GlassCounter(classes)
        parser.feed(html)
        lit = GlassCounter(sheen)
        lit.feed(html)
        rel = path.relative_to(DS).as_posix()
        shipping = rel.startswith("patterns/")
        if shipping:
            shipping_classes |= parser.seen
            shipping_sheen |= lit.seen
        carried |= parser.carried
        rows.append((rel, len(parser.hits), shipping, parser.hits))
    # Documentation pages contribute here as well as shipping ones, and
    # deliberately: a blurred layer nobody can see costs the same GPU pass on
    # foundations/materials.html as it does on the landing page, and the samples
    # there are the one place a hidden one would be easiest to write by accident.
    return rows, shipping_classes, shipping_sheen, carried


def stamp_of(rows):
    return hashlib.sha256(
        repr([(r, n) for r, n, _, _ in rows if n]).encode()
    ).hexdigest()[:8]


CENSUS_TABLE = re.compile(r'<table[^>]*\bid="glass-census"[^>]*>.*?</table>', re.S)


def census_table(html):
    """Just the generated table. Same rule check-spacing-scale.py learned the
    hard way: a generator that cannot say which table it owns will eventually
    rewrite one it does not."""
    m = CENSUS_TABLE.search(html)
    if not m:
        sys.exit(
            'foundations/materials.html has no <table id="glass-census">. That id is how\n'
            "this script finds the generated census; without it the script cannot tell the\n"
            "census from any other table on the page. Restore the id."
        )
    return m.start(), m.end(), m.group(0)


def render_table(rows):
    body = "\n".join(
        "        <tr><td><code>%s</code></td><td>%s</td><td>%d</td></tr>"
        % (rel, "shipping" if shipping else "documentation", n)
        for rel, n, shipping, _ in rows
        if n
    )
    # .docs-table is not decoration: it is `display: block; overflow-x: auto` on
    # a phone, so a table wider than its column scrolls inside itself instead of
    # pushing the whole document sideways. Without it this table overflowed the
    # page by 24 px at 375.
    return (
        '<table class="docs-table" id="glass-census">\n'
        "      <thead>\n"
        "        <tr><th>Page</th><th>Kind</th><th>Blurred layers</th></tr>\n"
        "      </thead>\n"
        "      <tbody>\n"
        "%s\n"
        "      </tbody>\n"
        "    </table>" % body
    )


STAMP = re.compile(r"<code>[0-9a-f]{8}</code>")


def sole_stamp(html):
    """The stamp, and proof that it is the only thing on the page shaped like one.

    The stamp is prose rather than table, so it can only be found by shape — and
    the shape is eight hex digits in a <code>, which a colour with an alpha pair
    also has. check-spacing-scale.py asserts in a comment that nothing else on
    its page matches; this checks instead, because the two failure modes are not
    symmetrical. A second match means --fix silently overwrites whatever it is,
    and the thing most likely to be written next to a materials chapter is a
    colour."""
    hits = STAMP.findall(html)
    if len(hits) != 1:
        sys.exit(
            "foundations/materials.html has %d things shaped like the census stamp; there\n"
            "must be exactly one. --fix rewrites every match, so a second one would be\n"
            "overwritten with a digest. Found: %s"
            % (len(hits), ", ".join(hits) or "none")
        )
    return hits[0][6:-7]


# The OTHER table on the page, and the one no generator owns. "Every panel, and
# what it is made of" is the chapter's verdict column: for each panel, is there
# something complex behind it that frosted glass would calm, and what does the
# panel do about it. It is prose by design — a verdict is an argument and cannot
# be computed — which is exactly why it drifted while the census beside it did
# not. The census is stamped, and a stamp over a row count cannot notice that
# the paragraph above the table says "two surfaces" while the table says four.
VERDICTS_TABLE = re.compile(r'<table[^>]*\bid="panel-census"[^>]*>.*?</table>', re.S)

# A class selector written as a reader writes one. Deliberately anchored to the
# leading dot: the same table names --surface-sunken, --sheen-panel and
# --glass-border in <code> too, and those are tokens rather than panels. The dot
# is the whole discrimination, and it is the author's own notation rather than a
# convention this script invents.
CLASS_CODE = re.compile(r"<code>\.([A-Za-z0-9_-]+)</code>")


def verdict_classes():
    """The glass classes the panel table names, read out of the table itself.

    Scoped to the table for the reason census_table() is scoped to its own: the
    page is a chapter about this material and mentions every one of these class
    names in prose somewhere. A check that searched the page would pass on a
    sentence, which is the failure it exists to catch."""
    html = MATERIALS_DOC.read_text()
    m = VERDICTS_TABLE.search(html)
    if not m:
        sys.exit(
            'foundations/materials.html has no <table id="panel-census">. That id is how\n'
            "this script finds the panel table — the prose verdict on every panel in the\n"
            "system, which is a different table from the generated census and is not\n"
            "interchangeable with it. Restore the id."
        )
    return set(CLASS_CODE.findall(m.group(0)))


def doc_rows():
    html = MATERIALS_DOC.read_text()
    found = re.findall(
        r"<tr><td><code>([^<]+)</code></td><td>[^<]*</td><td>(\d+)</td></tr>",
        census_table(html)[2],
    )
    return sole_stamp(html), {a: int(b) for a, b in found}


def fix(rows, stamp):
    html = MATERIALS_DOC.read_text()
    sole_stamp(html)
    start, end, _ = census_table(html)
    html = html[:start] + render_table(rows) + html[end:]
    MATERIALS_DOC.write_text(STAMP.sub("<code>%s</code>" % stamp, html))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="rewrite the census and stamp")
    ap.add_argument("-v", "--verbose", action="store_true", help="list every page")
    args = ap.parse_args()

    found = glass_rules()
    if not found:
        print(
            "glass budget: no backdrop-filter in the shipping CSS at all. Either the\n"
            "material has been removed — in which case delete this check and the chapter\n"
            "it enforces — or the parser has stopped seeing the rules it is meant to."
        )
        return 1

    classes, unreducible = glass_classes(found)
    sheen, sheen_unreducible = glass_classes(sheen_rules())
    rows, shipping_classes, shipping_sheen, carried = census(classes, sheen)
    stamp = stamp_of(rows)
    failures = []

    if args.fix:
        fix(rows, stamp)
        print("materials.html rewritten: stamp %s" % stamp)
        return 0

    # 1. Every selector carrying a blur has to be countable, or the census is a
    #    number with an unstated exception in it.
    for name, line, sel in unreducible:
        failures.append(
            "%s:%d declares backdrop-filter on a selector this script cannot count:\n"
            "        %s\n"
            "    The census would silently omit it, which is worse than not having one.\n"
            "    Either reduce the selector to a single class (optionally with one\n"
            "    pseudo-element), or widen SIMPLE_SELECTOR here and teach GlassCounter to\n"
            "    match it." % (name, line, sel)
        )

    # 2. One blur for the whole system. tokens.css measures 16 px as the radius
    #    past which nothing reads better and everything costs more; a literal
    #    anywhere is a second material wearing the first one's name.
    #
    #    `none` IS NOT A LITERAL, and this claim had no way to say so until a
    #    surface needed to declare the material absent in one state and present
    #    in another. There is nothing else backdrop-filter: none could mean — it
    #    is the material switched off, exactly as --glass-blur: none is in the
    #    three fallback blocks, which is a vocabulary this file already has and
    #    keeps in NEUTRALISED. A radius says "blur, but my own amount"; `none`
    #    says "no blur", and only the first of those is a second material.
    for rule in found:
        for value in rule["values"]:
            if value.strip() == "none":
                continue
            if BLUR_TOKEN not in value:
                failures.append(
                    "%s:%d writes its own blur rather than reading the token:\n"
                    "        backdrop-filter: %s\n"
                    "    Use %s. The radius is measured in tokens.css, and a component that\n"
                    "    states its own cannot be moved with the material."
                    % (rule["file"], rule["line"], value, BLUR_TOKEN)
                )

    # 3. Nothing scroll-driven moves on a blurred layer. A transition is left
    #    alone deliberately — see the note in foundations/materials.html: it is
    #    bounded, user-initiated and measured free, where an animation on a
    #    scroll timeline runs for the length of the document.
    blurred_selectors = {s for rule in found for s in rule["selectors"]}
    for name in SHIPPING_CSS:
        for head, body, line in rules((CSS / name).read_text()):
            sels = {s.strip() for s in head.split(",") if s.strip()}
            if not (sels & blurred_selectors):
                continue
            for decl in (d.strip() for d in body.split(";") if d.strip()):
                prop, _, value = decl.partition(":")
                prop = prop.strip()
                if prop == "animation-timeline" or (
                    prop.startswith("animation")
                    and any(p in value for p in REPAINTS_BLUR)
                ):
                    failures.append(
                        "%s:%d animates a property on a blurred layer:\n"
                        "        %s\n"
                        "    Re-rasterises the blur on every frame it runs. Both of the\n"
                        "    navigation's lights live on its unblurred 1 px rim for exactly\n"
                        "    this reason, and .cf-btn--glass::before exists to keep the\n"
                        "    button's band off its plate. Move it to a layer that is not\n"
                        "    blurred." % (name, line, decl)
                    )

    # 4. The budget, and the census that publishes it.
    for rel, n, shipping, hits in rows:
        budget = PAGE_BUDGET.get(rel, SHIPPING_BUDGET)
        if shipping and n > budget:
            failures.append(
                "%s carries %d blurred layers; %s gets %d.\n"
                "        %s\n"
                "    foundations/materials.html names the four surfaces that look like they\n"
                "    want glass and must not have it. If this is a genuine extra case,\n"
                "    something else on the page has to give up its blur first — or the two\n"
                "    layers provably cannot be lit at the same moment, which is an entry in\n"
                "    PAGE_BUDGET and has to name what in the CSS makes it true."
                % (
                    rel,
                    n,
                    "this page" if rel in PAGE_BUDGET else "a shipping page",
                    budget,
                    ", ".join(hits),
                )
            )

    # 4b. An allowance nothing needs any more is a finding, not a spare. Same
    #     reason the register in check-contrast.py is a list of floors rather
    #     than of values: a permission that outlives its argument is read by the
    #     next run as headroom, and it was never that.
    measured_rows = {rel: n for rel, n, _, _ in rows}
    for rel in sorted(PAGE_BUDGET):
        n = measured_rows.get(rel)
        if n is None:
            failures.append(
                "PAGE_BUDGET names %s, which is not a page under design-system/.\n"
                "    Renamed or deleted — drop the entry." % rel
            )
        elif n <= SHIPPING_BUDGET:
            failures.append(
                "PAGE_BUDGET allows %s %d blurred layers and it carries %d, which is\n"
                "    within the default. The argument for the allowance is spent: delete the\n"
                "    entry so the next surface added here has to make its own."
                % (rel, PAGE_BUDGET[rel], n)
            )

    # 5. Every block that turns the material off turns all of it off, in every
    #    selector it names. The one claim here that is about a fallback rather
    #    than about a cost, and it is in this script because it is about the
    #    same tokens: a tint left live in one block is a blurred surface's twin
    #    still asserting a material the reader has switched off.
    family, holes = fallback_holes()
    for at, head, line, missing in holes:
        failures.append(
            "tokens.css:%d — %s\n"
            "    %s neutralises the material and leaves %s live:\n"
            "        %s\n"
            "    The tint keeps its translucency there while the blur is gone, so whatever\n"
            "    reads it shows its backdrop SHARP — the one state worse than either the\n"
            "    material or a flat plate. Redeclare it in this rule, or read it as the\n"
            "    answer the way --surface-glass-solid is read." % (
                line,
                head,
                at,
                "a tint" if len(missing) == 1 else "%d tints" % len(missing),
                ", ".join(missing),
            )
        )

    # 6. Every glass surface that reaches a shipping page has a VERDICT on
    #    foundations/materials.html, and not only a row in the count.
    #
    #    The census claim below catches a number going stale. It cannot catch a
    #    sentence, and the sentence is what went stale: "Two surfaces in the
    #    whole system are frosted" survived the info-card plate shipping and
    #    then the act rail shipping, on the page tokens.css and acts.css both
    #    send a reader to, forty lines above a generated table that had counted
    #    both the whole time. tokens.css names the cost in its own comment —
    #    "a stale enumeration is worse than none, because the next run in this
    #    lane reads it as permission to add the surface it thinks is missing" —
    #    which is a warning about prose, kept in prose, and it aged the same way.
    #
    #    THE SHIPPING QUALIFIER IS DERIVED, NOT AN EXEMPTION LIST. .material-glass
    #    is glass by the same definition this script reads out of the stylesheet
    #    and it appears on no page under patterns/. It is the material's own
    #    sample, and a documentation utility owes a reader a swatch rather than a
    #    verdict on a panel it is not. The split is the same one the census
    #    column publishes, so a utility that ever lands on a shipping page starts
    #    owing a verdict on the day it does.
    #
    #    AND IT RUNS BOTH WAYS. A class named in that table which no longer
    #    declares a blur is the identical defect one direction over: a verdict
    #    outliving its surface, read by the next reader as a panel that exists.
    verdicts = verdict_classes()
    for name in sorted(shipping_classes - verdicts):
        failures.append(
            "%s carries backdrop-filter and reaches a shipping page, and the panel table\n"
            "    on foundations/materials.html does not name it.\n"
            "    That table is the chapter's verdict on every panel in the system — what is\n"
            "    behind it, what it is made of, how it responds. A frosted surface missing\n"
            "    from it leaves the prose around it describing a smaller system than the one\n"
            "    that ships, which is what the census cannot notice. Add a row naming\n"
            "    .%s in a <code>, or take the blur off it." % ("." + name, name)
        )
    #    THE REVERSE DIRECTION IS ONE CHECK FOR BOTH MATERIALS, and it has to be
    #    one. A class in that table is a panel, and this half asks whether the
    #    stylesheet still draws it at all — a question neither derived set can
    #    answer alone, because a row moving from glass to sheen is a panel
    #    changing material rather than a panel disappearing. Subtracting only
    #    the glass set would have failed on every honest sheen row below.
    for name in sorted(verdicts - classes - sheen):
        failures.append(
            ".%s is named in the panel table on foundations/materials.html, and nothing\n"
            "    in the shipping CSS gives it a material: no rule declares backdrop-filter\n"
            "    for it and none paints %s.\n"
            "    Either the rule was removed and the verdict outlived it — delete the row or\n"
            "    move the panel to its honest material — or the class was renamed and the\n"
            "    table still names the old one." % (name, SHEEN_TOKEN)
        )

    # 7. CLAIM 6, READ AGAINST THE OTHER DERIVED SET. The panel table's title is
    #    "Every panel", and most of its rows are not glass — the verdict there is
    #    contour, with a response made of light. So binding only the frosted rows
    #    left the majority of that table exactly as unbound as the whole of it
    #    used to be, and it drifted the same way and for the same reason: the
    #    register grew a travelling light, reached two shipping pages, and
    #    nothing could notice that the table naming every panel had never heard
    #    of it. (No count of those rows here, deliberately. Counting them in a
    #    comment is the habit this claim exists to retire.)
    #
    #    A SHEEN IS NOT ON A BUDGET, so this claim is only about the verdict and
    #    never about a count. It costs a gradient and a background-position; the
    #    reason it belongs in a checker at all is that the table's own rule is a
    #    design ruling with teeth — light is a response, and a panel that does
    #    nothing when you click it may not have one — and a row nobody wrote is a
    #    ruling nobody made.
    #
    #    Same shipping qualifier as claim 6, and it excuses the same shape of
    #    thing: .cf-event is the register's third class, it stands on a day of
    #    .cf-calendar, and today it appears only on the component page that
    #    demonstrates it. The table names it anyway, beside the two that ship,
    #    because they are one rule and one drawing — which the reverse direction
    #    above accepts and this direction never demanded.
    for name in sorted(shipping_sheen - verdicts):
        failures.append(
            "%s paints %s and reaches a shipping page, and the panel table on\n"
            "    foundations/materials.html does not name it.\n"
            "    That table is the chapter's verdict on every panel in the system, not only\n"
            "    on the frosted ones, and its last column is a ruling: light crossing a\n"
            "    surface is a response to a pointer arriving at something that will answer.\n"
            "    Add a row naming .%s in a <code>, with what is behind it and what it\n"
            "    answers — or, if it answers nothing, take the sheen off it."
            % ("." + name, SHEEN_TOKEN, name)
        )
    for name, line, sel in sheen_unreducible:
        failures.append(
            "%s:%d paints %s on a selector this script cannot reduce to a class:\n"
            "        %s\n"
            "    Claim 7 holds the panel table to the set of lit panels, and a selector it\n"
            "    cannot name silently leaves one out. Either reduce it to a single class\n"
            "    (optionally with one pseudo-element), or widen SIMPLE_SELECTOR here."
            % (name, line, SHEEN_TOKEN, sel)
        )

    # 8. THE SPECULAR BAND IS ONE GEOMETRY, AND THE TWO ENDPOINTS ARE ARITHMETIC.
    #
    #    Claim 2 already says every backdrop-filter reads --glass-blur rather
    #    than writing its own radius, on the argument that "a literal anywhere is
    #    a second material wearing the first one's name". The band that crosses
    #    the lit edge is the same kind of fact and had none of that protection:
    #    its width and its two off-canvas positions were written out on
    #    .cf-nav::after, .cf-btn--glass::before and .cf-info-card--glass::before,
    #    and twice more inside three pairs of keyframes holding identical values
    #    under three names. Eight copies, on three surfaces whose own token
    #    comment says they share the band and differ only in "the container and
    #    the clock". Nothing would have reported one of them being edited alone:
    #    each rim renders correctly on its own, and the drift is only visible
    #    with all three on screen at once, which they never are.
    #
    #    THE ENDPOINTS ARE RE-DERIVED HERE RATHER THAN COMPARED TO A TABLE, the
    #    same way check-gradient-family.py recomputes its waypoint instead of
    #    trusting a hex. A background layer positioned at P is offset by
    #    P x (container - image), so a band b wide has its left edge at P(1-b)W
    #    and its right edge at P(1-b)W + bW. Fully off the left needs
    #    P <= -b/(1-b); fully off the right needs P >= 1/(1-b). Move the band and
    #    both bounds move with it — which is the trap this claim exists for,
    #    because a band widened without moving its endpoints leaves a sliver of
    #    the specular parked ON the rim at rest, and the resting state is what
    #    every one of the four fallback doors falls back TO.
    geom = rim_geometry()
    missing = [n for n in (RIM_BAND, RIM_PARK, RIM_CROSS) if n not in geom]
    painters, animators, frames = rim_rules()
    if missing:
        failures.append(
            "tokens.css does not declare %s as a plain percentage.\n"
            "    The specular band's geometry is published there so the three lit glass\n"
            "    surfaces can read it instead of restating it. Declare it, or — if the band\n"
            "    has genuinely been retired — delete this claim with it."
            % ", ".join(missing)
        )
    elif geom[RIM_BAND] >= 100:
        failures.append(
            "tokens.css sets %s to %g %%, which is the whole sheet or more.\n"
            "    A specular that wide is the rim brightening rather than light passing, and\n"
            "    the endpoint arithmetic below divides by (1 - band)." % (RIM_BAND, geom[RIM_BAND])
        )
    else:
        b = geom[RIM_BAND] / 100.0
        park_max = -100.0 * b / (1 - b)
        cross_min = 100.0 / (1 - b)
        if geom[RIM_PARK] > park_max:
            failures.append(
                "%s is %g %% and %s is %g %%, which leaves the band ON the rim at rest.\n"
                "    A band %g %% wide is clear of the left edge only at or below %.1f %%.\n"
                "    The parked position is the state every fallback door falls back to — no\n"
                "    scroll timeline, reduced motion, print, forced colours — so a sliver\n"
                "    left showing there is not a stray frame, it is the designed drawing."
                % (RIM_BAND, geom[RIM_BAND], RIM_PARK, geom[RIM_PARK], geom[RIM_BAND], park_max)
            )
        if geom[RIM_CROSS] < cross_min:
            failures.append(
                "%s is %g %% and %s is %g %%, so the band never fully leaves.\n"
                "    A band %g %% wide clears the right edge only at or above %.1f %%. The\n"
                "    crossing is one pass that arrives and goes; ending it mid-sheet leaves\n"
                "    the light parked on the far end of every surface that ran it."
                % (RIM_BAND, geom[RIM_BAND], RIM_CROSS, geom[RIM_CROSS], geom[RIM_BAND], cross_min)
            )

    #    And the same three numbers may not be written out again by the surfaces
    #    that use them. This is the half of the claim that keeps the tokens from
    #    becoming decoration beside a literal that is what actually renders.
    for name, line, sels, body in painters:
        for prop, token in (
            ("background-size", RIM_BAND),
            ("background-position", RIM_PARK),
        ):
            m = re.search(r"(?:^|;)\s*%s\s*:([^;]*)" % prop, body)
            if not m:
                continue
            value = re.sub(r"var\(\s*", "var(", m.group(1)).strip()
            if "var(%s" % token not in value:
                failures.append(
                    "%s:%d paints %s and writes its own %s:\n"
                    "        %s: %s\n"
                    "    Read %s. The band is one geometry shared by every lit glass surface;\n"
                    "    a literal here is a fourth copy of a number that already drifted."
                    % (name, line, RIM_LIGHT, prop, prop, value, token)
                )

    #    ONE CROSSING, NOT ONE PER SURFACE. The keyframes are collected by what
    #    they move rather than by name, so a second set written under a new name
    #    is a finding even if its values are identical today — identical today is
    #    exactly what the three that existed were.
    rim_selectors = {s for _, _, sels, _ in painters for s in sels}
    crossing = {
        n
        for sels, names in animators
        if sels & rim_selectors
        for n in names
        if n in frames
    }
    if len(crossing) > 1:
        failures.append(
            "%d keyframe sets move the specular across a lit glass rim: %s.\n"
            "    There is one band and one crossing; what differs between the surfaces is\n"
            "    the timeline, not the motion. Point them all at one set and keep the\n"
            "    animation-timeline local to each surface."
            % (len(crossing), ", ".join(sorted(crossing)))
        )
    for n in sorted(crossing):
        for fname, fline, head, body in frames[n]:
            if RIM_PARK not in body and RIM_CROSS not in body:
                failures.append(
                    "%s:%d — @keyframes %s { %s } moves the rim to a literal position:\n"
                    "        %s\n"
                    "    Read %s and %s. A keyframe is where the endpoint arithmetic above\n"
                    "    is least visible and most likely to be left behind by the band."
                    % (fname, fline, n, head.strip(), body.strip(), RIM_PARK, RIM_CROSS)
                )

    # 9. NO COUNTED GLASS LAYER IS INVISIBLE AT REST.
    #
    #    foundations/materials.html's Don't list already rules out one way of
    #    paying for a blur nobody can see — "no backdrop-filter under an opaque
    #    background, the blur cannot be seen and still costs a GPU pass". This is
    #    the same sentence with the occluder on the other side: a layer at
    #    opacity 0 is not seen either, and the pass is the same pass.
    #
    #    IT WAS FOUND ON THE PAGE THIS FILE HAS ITS LARGEST ALLOWANCE FOR.
    #    .act-rail--glass::before declared backdrop-filter unconditionally on a
    #    plate whose rest opacity is 0, and PAGE_BUDGET's entry for the landing
    #    page is written on the opposite premise, in as many words: the plate
    #    "is painted only on :hover / :focus-within". tokens.css says it, the
    #    verdict column on materials.html says it, and the stylesheet said the
    #    other thing while three documents argued from this one. Whether a given
    #    compositor throws the pass away for a transparent layer is not in any
    #    specification and not in this system's gift; what is, is declaring the
    #    material in the state that shows it.
    #
    #    THE PAIR IS RARELY IN ONE RULE, which is why this reads the ELEMENT and
    #    not the block. The blur is on the modifier and the opacity is on the
    #    base — .act-rail--glass::before and .act-rail::before — so the only
    #    thing that knows they are one layer is the class attribute of the
    #    element carrying both. carried is that, straight off the pages, and the
    #    resolution below is the cascade this file can honestly do: single
    #    classes only, so source order decides and specificity never enters.
    #
    #    VISIBILITY AND DISPLAY ARE NOT HERE, and the omission is the claim being
    #    narrow rather than incomplete. `display: none` takes the box out of
    #    layout, so there is no layer to blur and nothing to find;
    #    `visibility: hidden` is the one this claim would extend to, and nothing
    #    in the tree writes it on a blurred layer today. Adding a branch for a
    #    case with no instance is how a checker grows a rule nobody has read.
    layers = rest_layers()
    for names in sorted(carried, key=lambda s: sorted(s)):
        for pseudo in ("", "::before", "::after"):
            blur = opacity = None
            owner = None
            for cls in sorted(names):
                slot = layers.get((cls, pseudo))
                if not slot:
                    continue
                if "backdrop-filter" in slot:
                    blur, owner = slot["backdrop-filter"], cls
                if "opacity" in slot:
                    opacity = slot["opacity"]
            if not blur or blur[0].strip() == "none":
                continue
            if not opacity or opacity[0].strip() not in ("0", "0.0", "0%"):
                continue
            failures.append(
                "%s:%d declares a live blur on a layer that is invisible at rest:\n"
                "        backdrop-filter: %s\n"
                "    and %s:%d sets opacity: %s on the same layer — .%s%s, carried by an\n"
                "    element whose classes are %s.\n"
                "    The reader cannot see it and the compositor is not obliged to skip it.\n"
                "    Declare the blur in the state that shows the surface, and hold it there\n"
                "    for the fade out with a zero-duration transition delayed by the fade's\n"
                "    own length — see .act-rail--glass::before in acts.css, which is this\n"
                "    idiom and the reason this claim exists."
                % (
                    blur[1], blur[2], blur[0],
                    opacity[1], opacity[2], opacity[0],
                    owner, pseudo,
                    " ".join(sorted(names)),
                )
            )

    # 10. THE LIT PANEL IS ONE GEOMETRY TOO, AND ITS REST STATE IS AN EQUALITY.
    #
    #     Claim 8 read claim 2 one property over and found the specular band
    #     restated eight times. This is claim 8 read one MATERIAL over. The sheen
    #     is the light layer's answer for a surface that is not glass, and its
    #     geometry had exactly the protection the rim's had before claim 8: none.
    #     A `200% 100%` size, a `0 0` park and a `100% 0` answer, written out on
    #     .cf-accordion__summary, .cf-blog-card and the register — three copies
    #     of three numbers on three surfaces that are never on screen together,
    #     which is the same reason nothing could have reported a drift in the rim.
    #
    #     THE PARK IS AN EQUALITY AND NOT AN INEQUALITY WITH AIR, which is what
    #     makes it worth re-deriving rather than reading. The rim's endpoints
    #     clear their bounds "with a little air"; the sheen's do not, and cannot.
    #     At the park the box shows the image's first 1/b, so the panel is clean
    #     at rest only while the gradient's transparent head reaches at least
    #     that far — at b = 200 % the window is 50 % and the head ends at exactly
    #     50 %. Narrow the band, or move that stop one point right, and every lit
    #     panel in the system carries a permanent white wash across its text at
    #     rest. Not a stray frame: the park is also what the reduced-motion
    #     reader sees, because the durations collapse to 1 ms and the transition
    #     stops being a transition. Both halves of the equality are read out of
    #     the tokens — the band from its own declaration, the head from
    #     --sheen-panel's stops, in every theme that declares one.
    sheen_geom = sheen_geometry()
    sheen_missing = [n for n in (SHEEN_BAND, SHEEN_PARK, SHEEN_CROSS)
                     if n not in sheen_geom]
    if sheen_missing:
        failures.append(
            "tokens.css does not declare %s as a plain percentage.\n"
            "    The lit panel's geometry is published there so the three sheened surfaces\n"
            "    can read it instead of restating it. Declare it, or — if the sheen has\n"
            "    genuinely been retired — delete this claim with it."
            % ", ".join(sheen_missing)
        )
    elif sheen_geom[SHEEN_BAND] <= 100:
        failures.append(
            "tokens.css sets %s to %g %%, which is the box or less.\n"
            "    A sheen no wider than the panel it crosses has nowhere to be parked: the\n"
            "    box sees the whole gradient at every position, so the light never leaves."
            % (SHEEN_BAND, sheen_geom[SHEEN_BAND])
        )
    else:
        window = 100.0 * 100.0 / sheen_geom[SHEEN_BAND]
        for line, head in sheen_heads():
            if head + 1e-9 < window:
                failures.append(
                    "tokens.css:%d declares %s with %g %% of clear head, and %s is %g %%,\n"
                    "    so the box sees the image's first %.1f %% at the park — %.1f %% of\n"
                    "    lit gradient standing on the panel with no pointer near it.\n"
                    "    The park is the drawing a reduced-motion reader gets, and this one\n"
                    "    lands under prose on the page wash. Widen the head or the band."
                    % (line, SHEEN_TOKEN, head, SHEEN_BAND, sheen_geom[SHEEN_BAND],
                       window, window - head)
                )
        if sheen_geom[SHEEN_PARK] != 0 or sheen_geom[SHEEN_CROSS] != 100:
            failures.append(
                "%s is %g %% and %s is %g %%; the two ends of the image are 0 %% and 100 %%.\n"
                "    The sheen SLIDES — it arrives and stays for as long as the pointer does —\n"
                "    where the rim CROSSES and leaves, which is why claim 8's off-canvas\n"
                "    arithmetic is not this claim's. Anything inside those two ends parks the\n"
                "    light part-way onto the panel or stops it part-way across."
                % (SHEEN_PARK, sheen_geom[SHEEN_PARK], SHEEN_CROSS, sheen_geom[SHEEN_CROSS])
            )

    #     And, as with the rim, the numbers may not be written out again by the
    #     surfaces that read them. The answer rule is checked as well as the
    #     painter: a panel that parks from the token and crosses to a literal is
    #     half-bound, and the half left loose is the one that moves.
    sheen_painters = sheen_rules()
    for rule in sheen_painters:
        for prop, token in (
            ("background-size", SHEEN_BAND),
            ("background-position", SHEEN_PARK),
        ):
            m = re.search(r"(?:^|;)\s*%s\s*:([^;]*)" % prop, rule["body"])
            if not m:
                continue
            value = re.sub(r"var\(\s*", "var(", m.group(1)).strip()
            if "var(%s" % token not in value:
                failures.append(
                    "%s:%d paints %s and writes its own %s:\n"
                    "        %s: %s\n"
                    "    Read %s. The band is one geometry shared by every lit panel; a\n"
                    "    literal here is a fourth copy of a number the rim already drifted on."
                    % (rule["file"], rule["line"], SHEEN_TOKEN, prop, prop, value, token)
                )

    #     THE ANSWER IS FOUND BY WHAT IT MOVES, not by a list. Any rule whose
    #     selectors reduce to a sheened class in a user-action state and that
    #     declares a background-position is that panel's answer, wherever it is
    #     written — the register's three classes share one, and a fourth panel
    #     added later is held to this by existing.
    for name in SHIPPING_CSS:
        for head, body, line in rules((CSS / name).read_text()):
            m = re.search(r"(?:^|;)\s*background-position\s*:([^;]*)", body)
            if not m:
                continue
            value = re.sub(r"var\(\s*", "var(", m.group(1)).strip()
            if "var(%s" % SHEEN_CROSS in value:
                continue
            hits = set()
            for sel in (s.strip() for s in head.split(",") if s.strip()):
                part = SELECTOR_PARTS.match(sel)
                if part and part.group(2) and part.group(1) in sheen:
                    hits.add(sel)
            if hits:
                failures.append(
                    "%s:%d answers a sheened panel and writes its own far end:\n"
                    "        %s { background-position: %s }\n"
                    "    Read %s. A panel that parks from the token and crosses to a literal\n"
                    "    is bound on the half that does not move."
                    % (name, line, ", ".join(sorted(hits)), value, SHEEN_CROSS)
                )

    doc_stamp, published = doc_rows()
    measured = {rel: n for rel, n, _, _ in rows if n}
    if doc_stamp != stamp:
        drift = sorted(
            set(published) | set(measured),
            key=lambda k: (published.get(k, 0) == measured.get(k, 0), k),
        )
        failures.append(
            "foundations/materials.html publishes census stamp %s; the tree measures %s.\n"
            "    %s\n"
            "    Run: python3 scripts/check-glass-budget.py --fix"
            % (
                doc_stamp,
                stamp,
                ", ".join(
                    "%s %s->%s" % (k, published.get(k, 0), measured.get(k, 0))
                    for k in drift
                    if published.get(k, 0) != measured.get(k, 0)
                )
                or "row order or wording changed",
            )
        )

    if args.verbose:
        print("glass, as read out of the shipping CSS: %s" % ", ".join(sorted(classes)))
        print("lit panels, the same way:               %s\n" % ", ".join(sorted(sheen)))
        for rel, n, shipping, hits in rows:
            print(
                "  %2d  %-46s %-13s %s"
                % (n, rel, "shipping" if shipping else "documentation", ", ".join(hits))
            )
        print()

    if failures:
        print("glass budget: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    total = sum(n for _, n, _, _ in rows)
    print(
        "glass budget: stamp %s, %d blurred layers across %d pages, max %d on a shipping page."
        % (
            stamp,
            total,
            sum(1 for _, n, _, _ in rows if n),
            max((n for _, n, s, _ in rows if s), default=0),
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
