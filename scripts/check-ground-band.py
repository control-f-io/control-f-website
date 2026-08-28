#!/usr/bin/env python3
"""The ground's horizon is the drawing's own height, in the drawing's own ratio.

THE FINDING THIS EXISTS FOR. Act 1's stage carries three absolutely-positioned
`inset: 0` layers over one box -- the field (.sp-field), the notes
(.sp-annots-fig) and the copy (.sp-say). `inset: 0` of the stage was the
drawing's box for as long as the drawing was the only thing in the stage, and
stopped being it the moment act 2's copy was moved out from under the drawing
into a row of its own below it. The stage's box grew to hold the prose; the two
ink layers followed it down.

Measured on the shipped render before the fix, sensor beads and their halos
landing on act 2's body copy: five objects at 320, six at 375, four at 600, six
at 768, five at 900 -- a 104 px halo across "Von oben nach unten gelesen." at
375, two 84 px halos on "rechnen lasst" and "und entwickelt", and at 768 the
readouts "74 °C", "96 %" and "51 Hz" in the same lines as the prose. Nothing
overflowed, nothing clipped, no console message, every gate green: two
information layers were simply sharing the same pixels, and the only way to see
it was to look at a phone-width render.

This is the third time this exact fault has been recorded in this stylesheet.
.lp-flow-data's own note is the second -- "`inset: 0` ... was only ever true by
coincidence ... which held while the last child was the drawing and stopped
holding the moment the copy below joined the flow" -- and the numeral layer was
fixed there while the ground it sits on was not. A comment that has to be
written three times is a check that was not written once.

THE FIX IT HOLDS. Outside the pin gate both ink layers are clipped to the
drawing's own band, and the band is not a chosen number: .lp-flow is
viewBox="0 0 1200 620" at width 100 % of the container's inner box, so its used
height IS that width x 620/1200. acts.css states it as

    --sp-ground: calc((100vw - var(--gutter) * 2) * 620 / 1200)

which is exact where the stack is one column -- verified against the rendered
svg at 144.7/145 (320), 172.4/172 (375), 275.9/276 (600), 353.1/353 (768) and
413.8/414 (900).

Every term in that expression is load-bearing and every one of them can drift
away from the thing it is derived from without a single render changing:

  1. THE RATIO. 620/1200 is the flow svg's viewBox, restated in a stylesheet
     that cannot read it. Re-draw the root on a different canvas -- which has
     happened twice in this drawing's history -- and the band silently becomes
     the wrong height: too short and the drawing stands on nothing, too tall and
     the prose is back under the field. Nothing else in the tree compares these
     two numbers.

  2. THE GUTTER. The inner box is the viewport less two gutters, so the
     expression names --gutter. Any other spacing token here is a guess at a
     number tokens.css owns.

  3. BOTH LAYERS OR NEITHER. The field and the notes are one picture: a note
     whose bead has been clipped away points at nothing. Measured with only the
     field clipped, at 375: five leaders and two labels ("S15", "S16") still
     stood on act 2's copy, pointing at beads that were no longer drawn. So
     every ink layer inset to the stage must read the same band, and .sp-say --
     which is the copy, not ink -- must not.

  4. CLIPPED, NOT RESIZED. The box is the crop: `slice` throws the surplus axis
     away, so shortening the box changes which units survive and at what scale.
     At 375 the box is 375 x 901 and the lattice renders at 1.001; give the box
     the band instead and width binds at 0.234, so every bead on a phone comes
     out a quarter of the size it has on a desktop. check-slice-crop.py names
     .sp-field in UNREGISTERED_OK for the neighbouring reason -- "no
     aspect-ratio and cannot have one" -- so the box must stay untouched and the
     clip must be a clip. A `height` or an `aspect-ratio` on either layer is the
     regression this clause catches.

WHAT IS CHECKED, in acts.css and the pages that load it:

  band -> drawing   the ratio in --sp-ground equals the viewBox ratio of every
                    .lp-flow in the tree, and is written as the viewBox's own
                    two numbers rather than as a decimal.
  band -> tokens    --sp-ground is expressed in --gutter, not in a literal
                    length or another spacing token.
  layers            every ink layer inset to .sp-stage carries the shared band
                    as a clip-path; .sp-say, the copy layer, does not.
  clip, not box     neither ink layer takes a height or an aspect-ratio that
                    would move the slice crop -- outside the two tiers that
                    SIZE the ink, where the band IS the box on purpose. See
                    THE TIERS THAT SIZE THE INK below.
  band, not fit     in each of those tiers both ink layers take the SAME
                    band -- one ratio, one floor, one cap -- and the floor
                    exists, because a band at exactly the field's own ratio
                    is the one box that does not crop and a field that does
                    not crop is a field scaled to the width.
  crop side         and in each of them the crop comes off the half the claim
                    reserves rather than being split around it. The field is
                    not a symmetrical drawing -- gen-proto-field.py keeps a
                    680 x 500 hole in its right middle for act 1's sentence --
                    and `slice` is symmetrical, so a centred crop spends a
                    phone's right half on a reservation that in these tiers is
                    empty. The clause reads the box that moves it: the same
                    width on the field and on its notes, naming the band and
                    the same ratio the aspect-ratio beside it states, with the
                    reset's max-width undone and the stage clipping.
  one band, twice   and the two tiers take the same band as each other. The
                    arrangement is written out twice because it lives in two
                    @supports branches and a media query cannot be shared
                    across them; two copies of five declarations is the drift
                    every other duplicate in this stylesheet is checked for.
  cap reserves      that cap subtracts the claim's own band from the viewport
                    rather than being the viewport. The tier stands act 1's
                    sentence under act 1's field, and a band free to take the
                    whole view is a sentence that only ever arrives with act
                    2's root -- absent from the act it names, captioning the
                    one it contradicts.
  cap floors        and the cap has a floor of its own, because a cap on this
                    box is a VERTICAL CROP: the box is `slice` at the field's
                    ratio, so every pixel the cap takes off the height throws
                    (that / scale) field units off the top and the same off the
                    bottom. The floor is re-derived from the beads themselves --
                    the drawing's own margin above its topmost rim and below its
                    lowest -- and the cap may not admit a crop past it.
  stack only        the reservation is released above the register's 64rem and
                    declared below it. Above the fold the claim stands IN the
                    field's band, in the hole the beads leave in the right half,
                    where it costs the stage no height; reserving a band for it
                    there buys nothing and pays for it in crop.
  gate off          the band is released ONLY inside the pin gate or the
                    no-support tier. A bare `@media (min-width: 64rem)`
                    releasing it is the finding below.
  fold band         above 64rem the band is re-derived from the two-column
                    split rather than dropped, and the split it names is the
                    one .sp-stage__inner actually declares.
  claim row         --sp-band, the length that tier gives the claim's grid row
                    above the fold, is the ink layers' own three declarations
                    restated: their min-height as its floor, their aspect-ratio
                    as its vw term, their max-height as its cap. It has to be a
                    restatement rather than the thing itself -- a grid track
                    takes no percentage of an indefinite block size, and the
                    field's percentage basis (.sp-stage) is not the grid's
                    (.container, narrower by two gutters that are a clamp of
                    their own) -- so nothing but this clause holds the two
                    together.

WHAT THE `gate off` CLAUSE USED TO SAY, AND WHY IT WAS WRONG. It read "the band
is released above the register's 64rem, so the pinned tier and the two-column
flow tier keep the whole stage as their ground", and acts.css released it with a
bare `@media (min-width: 64rem) { .sp-stage { --sp-ground-clip: none } }`. Half
of that sentence is true. Above the fold .cf-statement__text -- act 1's claim --
does sit beside the drawing in grid column 2, and it was measured clear.

.sp-say -- act 2's four paragraphs -- does not. Its absolute placement over the
root is declared inside the @supports block, so in every tier that does not pin
it is ordinary flow INSIDE the figure column, directly under the drawing. One
release therefore covered two tiers with opposite needs: the pinned stage, which
has no copy under the drawing and wants the whole ground, and the flow tier
above 64rem, which has exactly the copy the band exists to uncover.

Measured under prefers-reduced-motion, act 2's copy box screenshotted with and
without the two ink layers, pixels differing by more than 8/255:

    1024 x 900   11 799 px      1440 x 900    6 930 px
    1024 x 700   12 372         1600 x 900    6 682
    1100 x 900   12 098         1920 x 1080   6 332
    1280 x 900   10 825         768, 375           0   (already clipped)

Zero at every one of them after the band was re-derived, and the same numbers
within 200 px on prototypes/statement-to-process.html, which shares this sheet.

And the old clause could not have caught it: it searched for a `@media` prelude
carrying `min-width` and `64rem`, and the pin gate's own prelude carries both.
Moving the release into the gate -- which is where its own note always said it
belonged -- left the clause green while the premise under it had been inverted.
So the clause now asks WHERE the release is, not whether there is one.

THE TIERS THAT SIZE THE INK, and why clause 4 has an exception rather than a
hole. This file's clause 4 was written against a layer that stays inset
to the stage and is CLIPPED to the band -- the box is the stage, the crop is
the band, and a `height` on the layer moves the crop. That is still the whole
of the base tier and of the flow tier.

The no-support tier is not that arrangement any more. Release Firefox ships
scroll-driven animations behind a pref that is OFF in 154.0, so every Firefox
reader is in the tier with no timeline at all -- and that tier was drawing act
1's claim beside act 2's finished root with no act 1 anywhere, three beats of
a scroll composition arriving as one block. acts.css now sequences them in
SPACE there: act 1's field takes a band of its own at the head of the stage,
sized rather than clipped, with the claim under it and the root under that.

AND THERE ARE TWO SUCH TIERS SINCE THE FLOW TIER TOOK THE SAME ARRANGEMENT.
The flow tier is every viewport under the pin gate that CAN resolve a view
timeline -- every iPhone from Safari 26, every Android Chrome, every short
laptop window -- and it was drawing act 2 and nothing else: the field, the
callouts and the canopy's stand-in row all computed `display: none` at
390 x 844, so the one drawing on this site whose subject is data arriving
opened on a phone as a tree growing out of blank ground. It has a time axis,
so it takes the no-support tier's band and puts the arrival back in it. Same
five declarations, same floor, same cap; what it adds is when.

So in those tiers the layer's own box IS the band, and the two clauses above
swap places: sizing it is the fix, and the regression clause 4 names -- "give
the box the band instead and width binds at 0.234" -- comes back through the
FLOOR going missing rather than through the height arriving. Measured at 390
wide with the band left at the field's own 16 / 9 and no floor: 219 px tall,
the whole 1600 x 900 at 0.24, twenty-one 11 px labels inside 390 px, every one
overlapping its neighbour. With the 30rem floor: 480 px tall, height binds,
0.53, and the crop is the middle 732 units. The `band, not fit` clause is that
floor, and it requires both layers to take the identical band because they are
one picture -- the same sentence clause 3 makes about the clip.

Countable in a file, invisible in a render -- the same test the checks beside it
pass. Run with -v for the resolved band and the viewBoxes it was held to.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ACTS = ROOT / "design-system" / "assets" / "css" / "acts.css"
TREE = ROOT / "design-system"

# The stage's ink layers -- drawn things inset to .sp-stage, which the band owns.
#
# .sp-stage::before IS THE THIRD, AND IT ARRIVED WITHOUT A STYLESHEET. The stage
# carries .cf-ground now: base.css draws the isometric floor on a pseudo-element
# at `position: absolute; inset: 0` of its originating element, so dropping the
# class on the stage created exactly the layer this file's header describes --
# ink at `inset: 0` of a box that grew to hold act 2's prose. Nothing in acts.css
# had to say `position: absolute` for that to happen, which is the point: a class
# from another file can open the same hole a rule can, and the clause below is
# what closes it. acts.css clips it to var(--sp-ground-clip) beside the other two.
INK_LAYERS = (".sp-field", ".sp-annots-fig", ".sp-stage::before")
# The two that are one picture: the field of beads and the callouts naming it.
# .sp-stage::before is the floor under both and is never given a band of its
# own -- it is the stage's, in every tier.
BAND_LAYERS = (".sp-field", ".sp-annots-fig")
# The band the no-support tier sizes the ink with, and the three declarations
# that make it a CROP rather than a fit. Read as a set: the finding is a layer
# whose set differs from its twin's, or one with no floor in it.
BAND_PROPS = ("aspect-ratio", "min-height", "max-height")
# WHICH SIDE THE CROP COMES OFF, and the two boxes that have to agree on it.
# The notes are placed from the field's own centre -- `calc(50% + <offset> *
# var(--sp-u))`, written into the markup by gen-proto-field.py -- so the layer
# that carries them is only over the drawing while it is the SAME box. The
# field's <svg> is the one the site's own reset clamps, which is why the pair
# is read with max-width as well as width. See the `crop side` clause.
CROP_LAYERS = (".sp-field", ".sp-annots")
CROP_PROPS = ("width", "max-width")
# AND THE WIDTH HAS TO HAVE THE STAGE'S OWN IN IT. `max(100%, …)` is what makes
# the box inert wherever the band is already the field's ratio and there is no
# crop to move -- above 853 px of width, and under the cap, the two terms are
# equal to the pixel. A bare `var(--sp-band) * 16 / 9` passes every other test
# in this clause and hands the stage a field NARROWER than it is at those
# widths, which is a full-bleed backdrop with bare ground beside it.
CROP_ROOM = re.compile(r"\bmax\(\s*100%\s*,")
# The cap has to leave the claim room, and the only shape that does is a
# subtraction inside a calc(): `calc(100vh - <the claim's band>)`. A bare
# viewport unit passes every other clause here and still orphans act 1's
# sentence -- see the `cap reserves` clause.
CAP_RESERVES = re.compile(r"calc\([^)]*-\s*\S")
# The cap's own floor, and the property it reserves for. A cap on this box is a
# vertical crop, so the cap needs a length below which it stops taking height --
# `max(<floor>vw, calc(100vh - …))`. The floor is in vw because both terms of the
# crop are ratios of the same viewport: visible units = viewBox width x
# (floor / 100), so one number holds at every width or at none.
CAP_FLOOR = re.compile(r"max\(\s*(\d+(?:\.\d+)?)vw\s*,")
CLAIM_BAND = "--sp-claim-band"
# The drawing the crop is measured against: act 1's field, and the beads that
# ARE act 1. A bead is a <circle class="… cf-stmt-sensor__bead …"> in the
# field's own units, so its rim is cy -+ r and the margin the crop may eat is
# the smaller of the two the drawing leaves. Read out of the markup, because a
# number typed here is a second copy of a decision gen-proto-field.py makes.
FIELD_SVG = re.compile(
    r'<svg\b[^>]*\bclass="[^"]*\bsp-field\b[^"]*"[^>]*>.*?</svg>', re.S | re.I)
BEAD = re.compile(r"<circle\b[^>]*\bcf-stmt-sensor__bead\b[^>]*>", re.I)
ATTR = {n: re.compile(r'\b%s="\s*([-\d.]+)\s*"' % n, re.I) for n in ("cy", "r")}
VIEWBOX = re.compile(r'viewBox="\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*"', re.I)
# The stage's copy layer. Prose is what the band exists to get out from under;
# clipping it would be the fault inverted.
COPY_LAYER = ".sp-say"
BAND = "--sp-ground"
CLIP = "--sp-ground-clip"
# The length the no-support tier gives the claim's grid row above the fold. It
# is the ink layers' own band restated in viewport units -- see the clause.
CLAIM_ROW = "--sp-band"
# The register's name for the one-column stack's ceiling. tokens.css: "64rem /
# 1024 ... that fold is the container 56rem above, reached at a viewport of
# about 1007. A px gate cannot track a rem fold".
RELEASE = "64rem"


def strip_comments(css):
    """Blank out /* */ runs, keeping length so offsets still line up."""
    return re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), css, flags=re.S)


def declarations_for(selector, css):
    """Every declaration block whose selector list names this selector exactly."""
    return [body for body, _ in declarations_with_offsets(selector, css)]


BLOCK = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
_BLOCKS = {}


def blocks(css):
    """(selector list, body, body offset) for every rule in the sheet, once.

    THE SCAN IS THE EXPENSIVE PART OF THIS FILE AND IT DOES NOT DEPEND ON THE
    SELECTOR. `([^{}]+)\\{([^{}]*)\\}` over 367 kB of stylesheet costs 4.2 s a
    pass — the pattern's `+` backtracks across every brace-free run, and this
    stylesheet's longest is 10 351 characters of prose — and each clause below
    used to ask for a pass of its own. Fourteen clauses, 60 s; the crop clause
    would have made it twenty-four and 105 s. Only the FILTERING is per
    selector, so the sheet is scanned once and every clause reads the same
    list: 4.4 s for the run, and a clause costs what its filter costs.
    """
    got = _BLOCKS.get(css)
    if got is None:
        got = [([s.strip() for s in m.group(1).split(",")], m.group(2), m.start(2))
               for m in BLOCK.finditer(css)]
        _BLOCKS[css] = got
    return got


def declarations_with_offsets(selector, css):
    """As declarations_for, but each entry is (body, offset of the body).

    The offset is what the `gate off` clause is about: the same declaration is
    correct inside the pin gate and a defect outside it, so the check has to
    know where in the file it was written.
    """
    return [(body, at) for selectors, body, at in blocks(css)
            if any(s == selector or s.endswith(" " + selector) for s in selectors)]


def block_span(css, opener):
    """(start, end) of the braced body opened by the at-rule matching `opener`.

    Brace-matched rather than regex'd, because the pin gate nests an @media
    inside an @supports and holds a few hundred declarations.
    """
    m = re.search(opener, css)
    if not m:
        return None
    i = css.find("{", m.end() - 1)
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(css)):
        if css[j] == "{":
            depth += 1
        elif css[j] == "}":
            depth -= 1
            if depth == 0:
                return (i, j)
    return None


def fallback_span(css):
    """(start, end) of the @supports block for the tier with no timeline."""
    return block_span(
        css, r"@supports\s+not\s*\(\s*\(\s*animation-timeline\s*:\s*view\(\s*\)\s*\)")


def flow_spans(css):
    """Every (start, end) whose prelude is the pin gate's negation, inside the
    positive @supports.

    THE SECOND TIER THAT SIZES THE INK. This used to be the counter-example in
    fallback_span's own docstring -- "the flow tier is outside the gate too and
    is a different tier with a different answer: it has a time axis and spends
    it on the root". It spends it on BOTH acts now. The band was act 1's answer
    for a tier that could not sequence the moments at all; a tier that can
    sequence them and has the band anyway gets the same picture with the time
    put back in it, which is what a phone running Safari 26 now sees.

    So both spans are exceptions to `clip, not box` and both are held by
    `band, not fit` -- and by the clause under it, which is new with the second
    tier: the two bands have to be the SAME band. They are two copies of five
    declarations in two @supports branches, which cannot share a media query,
    and two copies of a number is the drift this whole stylesheet is written
    against.

    Anchored on the media prelude rather than on a comment, and on the
    NEGATION -- `not all and (min-width) and (min-height)` is the flow tier and
    the same terms without it are the pinned stage.

    THERE ARE TWO OF THEM AND THAT IS THE POINT, so this returns a list rather
    than the first. The band is a LAYOUT and sits in the outer one, which the
    reduced-motion query does not cover; the arrival, the pulse and the
    convergence sit in the inner one, which it does. Returning `re.search`'s
    first match would hold whichever half happened to be written first and go
    green the day somebody swapped them.
    """
    out, at = [], 0
    pat = re.compile(r"@media\s+not all and \(min-width:\s*64rem\)\s*and\s*"
                     r"\(min-height:\s*45rem\)")
    while True:
        m = pat.search(css, at)
        if not m:
            return out
        span = block_span(css[m.start():], pat.pattern)
        if span is None:
            return out
        out.append((m.start() + span[0], m.start() + span[1]))
        at = out[-1][1]


def column_split(css):
    """The figure column's share of .sp-stage__inner, as (numerator, total).

    Read from the grid rather than assumed, because the band above the fold is
    the drawing's used height and the drawing is that share of the row. Change
    the grid to 2fr/3fr and the band has to move with it; that is the whole
    reason this is derived and not typed.
    """
    for body, _ in declarations_with_offsets(".sp-stage__inner", css):
        v = value_of("grid-template-columns", body)
        if not v:
            continue
        frs = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)fr", v)]
        if len(frs) == 2:
            return (frs[0], frs[0] + frs[1])
    return None


def split_top(s):
    """Split on commas that are not inside parens.

    clamp()'s three terms, one of which is a calc() with a comma-free but
    paren-heavy body -- `calc(100vh - var(--sp-claim-band))`. A plain split
    would not break that one today and would the day a term takes min() or a
    two-argument function, which is exactly the day this clause has to keep
    working."""
    out, depth, cur = [], 0, ""
    for c in s:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if c == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += c
    out.append(cur)
    return out


def value_of(prop, block):
    """One declaration's value, or None. Handles nested parens in calc()."""
    i = block.find(prop + ":")
    if i < 0:
        return None
    i += len(prop) + 1
    depth = 0
    for j in range(i, len(block)):
        c = block[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == ";" and depth == 0:
            return block[i:j].strip()
    return block[i:].strip()


def own_value_of(prop, block):
    """value_of, with the property's own left edge stated.

    `width:` is a substring of `max-width:`, and value_of takes whichever
    comes first in the block. The crop clause reads both from the SAME rule,
    so it cannot leave which one it got to the order they were typed in.
    """
    m = re.search(r"(?<![-\w])" + re.escape(prop) + r"\s*:", block)
    if not m:
        return None
    i, depth = m.end(), 0
    for j in range(i, len(block)):
        c = block[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == ";" and depth == 0:
            return block[i:j].strip()
    return block[i:].strip()


def viewboxes(tree):
    """Every .lp-flow viewBox in the tree, as (relpath, w, h)."""
    found = []
    for path in sorted(tree.rglob("*.html")):
        raw = path.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"<svg\b([^>]*\bclass=\"[^\"]*\blp-flow\b[^\"]*\"[^>]*)>",
                             raw, re.I):
            vb = re.search(r"viewBox=\"\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\"",
                           m.group(1), re.I)
            if vb:
                found.append((path.relative_to(ROOT).as_posix(),
                              float(vb.group(1)), float(vb.group(2))))
    return found


def bead_margins(tree):
    """Every act 1 field in the tree, as (relpath, viewBox w, h, margin).

    `margin` is what a SYMMETRIC vertical crop may eat before it reaches a bead:
    the smaller of the drawing's own clearance above its topmost rim and below
    its lowest. Symmetric because the field is `xMidYMid slice` -- the surplus
    goes off both edges in equal halves -- so the tighter of the two is the one
    that decides, and it is the top one on this drawing by 73 units.

    Beads and not halos. A halo is a circle of 2.6 x the bead's radius filled
    with a gradient that reaches zero at its own rim, so its outer ring is
    already transparent and clipping it costs the drawing nothing anyone can
    see. A bead is a contour with a fill; a contour cut by the frame is the
    finding check-slice-crop.py's constraint 2 is written for, arriving here
    because this band is the box that cuts it.

    prototypes/ is out, by the boundary every register in this system draws.
    """
    out = []
    for path in sorted(tree.rglob("*.html")):
        if "prototypes" in path.parts:
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        for m in FIELD_SVG.finditer(raw):
            svg = m.group(0)
            vb = VIEWBOX.search(svg[:svg.find(">") + 1])
            rims = []
            for tag in BEAD.findall(svg):
                cy, r = ATTR["cy"].search(tag), ATTR["r"].search(tag)
                if cy and r:
                    rims.append((float(cy.group(1)), float(r.group(1))))
            if not (vb and rims):
                continue
            w, h = float(vb.group(1)), float(vb.group(2))
            top = min(cy - r for cy, r in rims)
            bottom = h - max(cy + r for cy, r in rims)
            out.append((path.relative_to(ROOT).as_posix(), w, h, min(top, bottom)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    findings = []
    if not ACTS.exists():
        print(f"UNREADABLE  {ACTS.relative_to(ROOT).as_posix()}")
        return 1

    raw = ACTS.read_text(encoding="utf-8", errors="replace")
    css = strip_comments(raw)

    # ---- the band itself -------------------------------------------------
    band = None
    for block in declarations_for(".sp-stage", css):
        v = value_of(BAND, block)
        if v:
            band = v
    if band is None:
        findings.append(
            f"acts.css: no {BAND} on .sp-stage. The horizon the two ink layers "
            f"clip to has to be declared once, on the box they are inset to, so "
            f"both read one number -- see this check's docstring, clause 3.")
        band = ""

    ratio = None
    if band:
        # The ratio must be the viewBox's own two integers, in that order, so a
        # reader can see which canvas it came from. A decimal hides the source.
        m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*\)?\s*$", band)
        pair = re.findall(r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)", band)
        if not pair:
            findings.append(
                f"acts.css: {BAND} carries no `h / w` ratio ({band!r}). The band "
                f"is the drawing's used height and the drawing's height is its "
                f"viewBox ratio; a literal length is a number with no source.")
        else:
            h, w = pair[-1]
            ratio = (float(w), float(h))
        if "var(--gutter)" not in band:
            findings.append(
                f"acts.css: {BAND} does not read var(--gutter) ({band!r}). The "
                f"container's inner box is the viewport less two gutters; any "
                f"other figure is a guess at a number tokens.css owns.")
        _ = m

    # ---- the ratio against every drawing it claims to describe -----------
    boxes = viewboxes(TREE)
    # And act 1's own drawing, which the cap's floor is measured against. Its
    # beads are what a vertical crop reaches first -- see the `cap floors`
    # clause and bead_margins() above.
    fields = bead_margins(TREE)
    if not fields:
        findings.append(
            "design-system/: no .sp-field carrying .cf-stmt-sensor__bead "
            "circles. The cap's floor is the clearance act 1's own drawing "
            "leaves above its topmost bead, and there is no drawing left to "
            "read it out of.")
    if not boxes:
        findings.append(
            "design-system/: no .lp-flow with a viewBox in the tree. The band's "
            "ratio has nothing left to be derived from.")
    elif ratio:
        for rel, w, h in boxes:
            if (w, h) != ratio:
                findings.append(
                    f"{rel}: .lp-flow is viewBox 0 0 {w:g} {h:g} and {BAND} is "
                    f"built on {ratio[1]:g} / {ratio[0]:g}. The band is the "
                    f"svg's used height -- width x h/w -- so these are one "
                    f"number written twice. Re-derive the band from the canvas, "
                    f"in the canvas's own two figures.")

    # ---- both ink layers, and only the ink layers ------------------------
    fallback = fallback_span(css)
    # THE TIERS THAT SIZE THE INK, and there are two of them now. Both give the
    # layer its own band as a BOX instead of clipping the stage's, so both are
    # exceptions to the clause below and both are held by `band, not fit`.
    sizing = [s for s in [fallback] + flow_spans(css) if s]
    for layer in INK_LAYERS:
        blocks = declarations_with_offsets(layer, css)
        if not blocks:
            findings.append(f"acts.css: {layer} has no declaration block to read.")
            continue
        clipped = any(f"var({CLIP})" in (value_of("clip-path", b) or "")
                      for b, at in blocks
                      if not any(s[0] < at < s[1] for s in sizing))
        if not clipped:
            findings.append(
                f"acts.css: {layer} does not clip to var({CLIP}). The field and "
                f"the notes are one picture -- a note whose bead has been "
                f"clipped away points at nothing -- so every ink layer inset to "
                f"the stage reads the same band or none of them does.")
        for b, at in blocks:
            # The two sizing tiers do this on purpose -- the band IS the box
            # there, and the `band, not fit` clause below is what holds them.
            if any(s[0] < at < s[1] for s in sizing):
                continue
            for prop in ("height", "block-size", "aspect-ratio"):
                v = value_of(prop, b)
                if v and v not in ("100%", "auto"):
                    findings.append(
                        f"acts.css: {layer} sets {prop}: {v}. The box is the "
                        f"crop -- `slice` throws the surplus axis away, so a box "
                        f"given the band instead of the stage renders the "
                        f"lattice at 0.234 instead of 1.001 at 375 and every "
                        f"bead on a phone comes out a quarter size. Clip the "
                        f"ink; leave the box.")

    # ---- the band the two sizing tiers size them with ---------------------
    flows = flow_spans(css)
    if fallback is None:
        findings.append(
            "acts.css: no @supports not ((animation-timeline: view()) and "
            "(animation-range: ...)) block. Release Firefox is that tier -- the "
            "pref is off in 154 -- and without it act 1's field, act 1's claim "
            "and act 2's root arrive as one block with no act 1 drawn at all.")
    if not flows:
        findings.append(
            "acts.css: no `@media not all and (min-width: 64rem) and "
            "(min-height: 45rem)` block inside the gate. That is the flow tier "
            "-- every phone with scroll-driven animations, which is every "
            "iPhone from Safari 26 -- and it draws act 1 in the same band this "
            "clause holds.")
    tiers = {"the no-support tier": [fallback] if fallback else [],
             "the flow tier": flows}
    per_tier = {}
    for label, spans in tiers.items():
        if not spans:
            continue
        bands = {}
        for layer in BAND_LAYERS:
            got = {}
            for b, at in declarations_with_offsets(layer, css):
                if not any(s[0] < at < s[1] for s in spans):
                    continue
                for prop in BAND_PROPS:
                    v = value_of(prop, b)
                    if v:
                        got[prop] = re.sub(r"\s+", " ", v.strip())
            bands[layer] = got
        per_tier[label] = bands
        for layer, got in bands.items():
            if got.get("aspect-ratio") and not got.get("min-height"):
                findings.append(
                    f"acts.css: {layer} takes a band in {label} with no "
                    f"min-height. A band at the field's own ratio is the one "
                    f"box that does not crop, and an uncropped field is a field "
                    f"scaled to the width: measured at 390 wide, 219 px of "
                    f"band, the whole 1600 x 900 at 0.24, twenty-one 11 px "
                    f"labels inside 390 px. The floor is what makes the height "
                    f"bind and the crop happen.")
            cap = got.get("max-height")
            # THE CAP IS A CROP, AND THE CROP HAS A FLOOR. Everything the cap
            # takes off this box comes off the drawing, not off the layout: the
            # field is `slice`, so a shorter box shows fewer of its own units
            # rather than smaller ones, half off the top and half off the
            # bottom. Visible units = viewBox width x (band / 100vw), so a floor
            # written in vw fixes the crop at every width in one number --
            # crop a side = (viewBox height - floor/100 x viewBox width) / 2 --
            # and the drawing's own margin says how large that may be.
            floor = CAP_FLOOR.search(cap or "")
            if cap and not floor:
                findings.append(
                    f"acts.css: {layer}'s no-support band caps at {cap} with no "
                    f"floor under it. A cap on this box is a vertical crop and "
                    f"the drawing has five rows of instruments in it: measured "
                    f"in Firefox at 2000 x 1175, 100vh - 16rem against "
                    f"56.25vw is 206 px of crop, 82 field units a side, and the "
                    f"top row stands at y 80 -- all six beads gone and their six "
                    f"labels left on the frame's edge pointing at nothing. Floor "
                    f"the cap with `max(<vw>, …)` at the height where the crop "
                    f"reaches the topmost rim.")
            elif floor and fields:
                have = float(floor.group(1))
                for rel, w, h, margin in fields:
                    need = (h - 2 * margin) / w * 100
                    if have + 1e-9 < need:
                        crop = (h - have / 100 * w) / 2
                        findings.append(
                            f"acts.css: {layer}'s cap floors at {have:g}vw and "
                            f"{rel} needs {need:.4g}vw. The field is {w:g} x "
                            f"{h:g} and leaves {margin:g} units above its "
                            f"topmost bead; a floor of {have:g}vw shows "
                            f"{have / 100 * w:.4g} of the {h:g} and crops "
                            f"{crop:.4g} a side, so the frame is drawn through "
                            f"the rim. The floor is not a taste: it is that "
                            f"clearance read back out of the beads. Raise it, or "
                            f"move the row -- the number lives in "
                            f"gen-proto-field.py's Y0 and R_MAX.")
            if cap and not CAP_RESERVES.search(cap):
                findings.append(
                    f"acts.css: {layer}'s band in {label} caps at {cap}, which "
                    f"is the whole viewport. Both tiers stand act 1's claim "
                    f"UNDER act 1's field, so a band that may take every pixel "
                    f"of the view is a claim that can never be on screen with "
                    f"the field it names -- it arrives with act 2's root "
                    f"instead and captions the answer drawing. Measured with "
                    f"the bare cap, field top to claim bottom against the view "
                    f"that has to hold it: 767/720 at 1024, 957/800 at 1280, "
                    f"1005/768 at 1366, 1047/900 at 1440, 1317/1080 at 1920 -- "
                    f"six laptops and act 1 whole in none of them. Subtract the "
                    f"claim's own band from the viewport instead.")
        shapes = {layer: tuple(sorted(got.items())) for layer, got in bands.items()}
        if len(set(shapes.values())) > 1:
            detail = "; ".join(f"{layer} {dict(shape) or dict()}"
                               for layer, shape in shapes.items())
            findings.append(
                f"acts.css: {label}'s ink layers take different bands "
                f"({detail}). The field and the notes are one picture and the "
                f"notes are placed in the field's own sliced units -- give them "
                f"two boxes and all twenty-one land off the beads they name. "
                f"Same sentence as the clip clause, one tier along.")

    # ---- and the crop comes off the half the claim reserves ---------------
    # THE DRAWING IS NOT SYMMETRICAL AND `slice` IS. gen-proto-field.py states
    # it as CLAIM = (920, 180, 680) -- "no sensor stands in x >= 920,
    # 180 <= y <= 680 ... because a glow behind the claim is contrast debt" --
    # which takes seven crossings of the supergrid out and leaves a 680 x 500
    # hole in the field's right middle for act 1's sentence to stand in. Above
    # the container's 56rem fold it does stand in it. In THESE tiers it does
    # not: the claim is a row under the field, and `xMidYMid slice` centres the
    # crop on the box, whose centre is inside the hole. Measured at 390 x 844
    # before the box below: the crop ran field x 434..1166, the middle row was
    # ONE bead with 493 units of nothing to its right, and 6 of the 11 readings
    # on screen had both a whole label and a whole bead. It reads on a phone as
    # a gap in the field, which is how it was reported.
    #
    # THE FIX IS A BOX AND NOT AN ATTRIBUTE, because preserveAspectRatio is
    # markup and no tier can reach it from a stylesheet. Give the layer the
    # drawing's own WIDTH at the band's own height -- var(--sp-band) times the
    # viewBox's ratio -- and `slice` has no surplus left to centre: the crop is
    # the whole of it and it comes off the right. 0..731 at the same viewport,
    # thirteen beads in a 3/2/3/2/3 lattice, 11 whole readings, and identical
    # in all three engines.
    #
    # FOUR WAYS IT REVERTS WITHOUT A RENDER CHANGING, which is the whole reason
    # this clause exists rather than a fifth paragraph of prose in acts.css:
    #
    #   the clamp   base.css's own reset is `img, svg, video { display: block;
    #               max-width: 100% }`, and it took this box straight back to
    #               the stage's width the first time the width was written --
    #               measured, .sp-field still 375 px wide inside a 375 px stage
    #               with the width declared. Without `max-width: none` beside
    #               it the width is decoration.
    #   the notes   .sp-annots is placed from the field's own centre, so it is
    #               over the drawing only while it is the same box. Widen one
    #               and not the other and all twenty-one notes stand off the
    #               beads they name -- the `band, not fit` clause's own
    #               sentence, one axis along.
    #   the ratio   the width restates the viewBox's ratio, which the
    #               aspect-ratio in the same tier already states. Two copies of
    #               one number is what every other clause in this file is here
    #               about.
    #   the clip    a box wider than the stage is a document wider than the
    #               view: 853 px of scrollWidth inside a 375 px phone without
    #               a clip on the stage. `clip` and not `hidden`, because
    #               hidden makes the stage a scroll container and inside the
    #               pin gate this stage is `position: sticky`.
    crops = {}
    for label, spans in tiers.items():
        if not spans:
            continue
        crop_boxes = {}
        for layer in CROP_LAYERS:
            props = {}
            for body, at in declarations_with_offsets(layer, css):
                if not any(s[0] < at < s[1] for s in spans):
                    continue
                for prop in CROP_PROPS:
                    v = own_value_of(prop, body)
                    if v:
                        props[prop] = re.sub(r"\s+", " ", v.strip())
            crop_boxes[layer] = props
        stage = {}
        for body, at in declarations_with_offsets(".sp-stage", css):
            if not any(s[0] < at < s[1] for s in spans):
                continue
            for prop in ("overflow", "overflow-x"):
                v = own_value_of(prop, body)
                if v:
                    stage[prop] = re.sub(r"\s+", " ", v.strip())
        crops[label] = (crop_boxes, stage)

        crop = crop_boxes[".sp-field"].get("width", "")
        if not (CROP_ROOM.search(crop) and CLAIM_ROW in crop):
            findings.append(
                f"acts.css: .sp-field takes width {crop or '<none>'} in "
                f"{label}. The crop is centred on the box and the drawing is "
                f"not centred in it: gen-proto-field.py keeps a 680 x 500 hole "
                f"in the field's right middle for a claim that in this tier "
                f"stands UNDER the field, so a centred crop spends a phone's "
                f"right half on it -- measured at 390 x 844, the middle row was "
                f"one bead with 493 units of nothing beside it. The box is what "
                f"moves the crop, and it has to be `max(100%, "
                f"var({CLAIM_ROW}) * <the viewBox's ratio>)`: the field's own "
                f"width at the band's own height, so `slice` has no surplus "
                f"left to centre and the max() is inert wherever there is no "
                f"crop to move.")
            continue
        if crop_boxes[".sp-annots"].get("width") != crop:
            findings.append(
                f"acts.css: .sp-annots takes width "
                f"{crop_boxes['.sp-annots'].get('width') or '<none>'} in {label} "
                f"against .sp-field's {crop}. The callouts are placed at "
                f"`calc(50% + <offset> * var(--sp-u))` from the FIELD's own "
                f"centre, which is 50 % of the field's box and of nothing "
                f"else, so the two are one box or all twenty-one notes stand "
                f"off the beads they name.")
        crop_ratio = (per_tier.get(label, {}).get(".sp-field", {})
                 .get("aspect-ratio", ""))
        if crop_ratio and crop_ratio.replace(" ", "") not in crop.replace(" ", ""):
            findings.append(
                f"acts.css: .sp-field's crop width in {label} is {crop} while "
                f"its band is aspect-ratio {crop_ratio}. One is the drawing's width "
                f"at the band's height and the other is the band's height at "
                f"the drawing's width -- the same viewBox, written twice. Two "
                f"copies means a re-drawn field moves the box and not the crop, "
                f"and the notes go with the one that moved.")
        if crop_boxes[".sp-field"].get("max-width") != "none":
            findings.append(
                f"acts.css: .sp-field takes the crop width in {label} with no "
                f"`max-width: none` beside it. base.css's own reset is `img, "
                f"svg, video {{ display: block; max-width: 100% }}` and it "
                f"clamps this box straight back to the stage: measured, the "
                f"field still 375 px wide inside a 375 px stage with the width "
                f"declared and the crop still centred on the hole.")
        clip = stage.get("overflow-x") or stage.get("overflow")
        if clip != "clip":
            findings.append(
                f"acts.css: .sp-stage does not clip horizontally in {label} "
                f"(overflow-x {clip or '<none>'}). The field is wider than the "
                f"stage in this tier and a box wider than the view is a "
                f"document wider than the view: 853 px of scrollWidth inside a "
                f"375 px phone without it. `clip` and not `hidden` -- hidden "
                f"makes this box a scroll container, and inside the pin gate "
                f"the same element is `position: sticky`.")

    if len(crops) == 2:
        (la, ca), (lb, cb) = crops.items()
        if ca != cb:
            findings.append(
                f"acts.css: the crop's box differs between the two tiers that "
                f"size the ink -- {la} {ca}, {lb} {cb}. Same clause as the "
                f"band's own: one arrangement written twice because two "
                f"@supports branches cannot share a media query, and two boxes "
                f"is two crops.")

    # AND THE TWO TIERS TAKE THE SAME BAND, which is the clause the second tier
    # brought with it. They are two copies of one arrangement -- act 1's field
    # at the head of the stage, act 1's claim under it, act 2's root under that
    # -- written twice because they sit in two @supports branches and a media
    # query cannot be shared across them. Everything else in this file that
    # exists twice is held to its twin by a check for the same reason; without
    # this clause the phone that CAN sequence the acts and the phone that
    # cannot would drift into two different pictures one edit at a time, and
    # each would go on passing every clause above on its own.
    if len(per_tier) == 2:
        (la, ba), (lb, bb) = per_tier.items()
        for layer in BAND_LAYERS:
            if ba.get(layer, {}) != bb.get(layer, {}):
                findings.append(
                    f"acts.css: {layer}'s band differs between the two tiers "
                    f"that size it -- {la} {ba.get(layer, {})}, {lb} "
                    f"{bb.get(layer, {})}. One arrangement, written twice "
                    f"because two @supports branches cannot share a media "
                    f"query; two bands is two pictures.")

        # ---- the reservation belongs to the stack, and only to it ----------
        # THE CAP CLAUSE ABOVE READS A SHAPE AND THIS ONE READS THE NUMBER IN
        # IT. `calc(100vh - var(--sp-claim-band))` goes on subtracting whatever
        # that property happens to hold, so the whole `cap reserves` argument can
        # be defeated without touching a character of the declaration it is
        # written against -- set the band to zero and the cap is the viewport
        # again, with the check still passing. It is also the one edit that is
        # RIGHT above the fold, which is why this is two findings and not one:
        # the tier stands the claim IN the field's band there, in the hole the
        # beads leave, where reserving a band for it buys nothing and is paid
        # for in crop. So the reservation has to exist below 64rem and be
        # released above it, and neither half may go missing quietly.
        base, release_at = None, []
        fold_spans = []
        for m in re.finditer(r"@media([^{]*)\{", css):
            prelude = m.group(1)
            if "min-width" not in prelude or RELEASE not in prelude:
                continue
            if "min-height" in prelude:      # the pin gate, not the fold
                continue
            span = block_span(css[m.start():], r"@media")
            if span:
                fold_spans.append((m.start() + span[0], m.start() + span[1]))
        for body, at in declarations_with_offsets(".sp-stage", css):
            if not (fallback[0] < at < fallback[1]):
                continue
            v = value_of(CLAIM_BAND, body)
            if v is None:
                continue
            zero = re.match(r"^0[a-z%]*$", v.strip()) is not None
            if any(lo < at < hi for lo, hi in fold_spans):
                release_at.append((v.strip(), zero))
            else:
                base = v.strip()
        if base is None or re.match(r"^0[a-z%]*$", base):
            findings.append(
                f"acts.css: {CLAIM_BAND} is {base!r} in the no-support tier "
                f"outside the fold. Below 64rem this tier stands act 1's "
                f"sentence UNDER act 1's field -- .sp-stage__inner is one "
                f"column, text in row 1, figure in row 2 -- so a band with "
                f"nothing reserved under it is the `cap reserves` finding "
                f"arriving through the property instead of the declaration: "
                f"the cap reads as a subtraction and subtracts nothing.")
        if not any(zero for _, zero in release_at):
            findings.append(
                f"acts.css: {CLAIM_BAND} is never released in a bare @media "
                f"(min-width: {RELEASE}) inside the no-support tier. Above the "
                f"fold the claim stands IN the field's band and costs the stage "
                f"no height, so the reservation is 256 px of crop bought for a "
                f"sentence that is not under anything. Measured before the "
                f"release, vertical crop in field units: 75 at 1024 x 600, 92 "
                f"at 1440 x 900, 82 at 2000 x 1175 -- against a drawing whose "
                f"top row of beads stands at y 80.")

        # ---- and the claim's row is that same band, written as a length ----
        # Above the fold this tier stands act 1's claim IN the field rather
        # than under it: .sp-stage__inner is pulled back by --sp-band and its
        # first row is --sp-band tall, so the sentence lands in the hole the
        # beads leave in the right half and the root still starts below the
        # last one. That only holds while --sp-band IS the ink layers' height.
        # It cannot BE their height -- a grid track takes no percentage of an
        # indefinite block size, and the field's basis (.sp-stage) is not the
        # grid's (.container, narrower by two gutters that are themselves a
        # clamp) -- so it is restated in viewport units and held here.
        #
        # Get it wrong and nothing overflows: the claim slides off the hole
        # into the beads, or the row stops short and act 2's root is drawn
        # through act 1's last bead row, which is the double exposure this
        # tier was built to take apart.
        want = None
        ref = bands.get(".sp-field") or {}
        if ref.get("aspect-ratio") and ref.get("min-height") and ref.get("max-height"):
            m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$",
                         ref["aspect-ratio"])
            if m:
                w, h = float(m.group(1)), float(m.group(2))
                want = (ref["min-height"], f"{h / w * 100:g}vw", ref["max-height"])
        row = None
        for body, at in declarations_with_offsets(".sp-stage", css):
            if not (fallback[0] < at < fallback[1]):
                continue
            v = value_of(CLAIM_ROW, body)
            if v:
                row = re.sub(r"\s+", " ", v.strip())
        if want and row is None:
            findings.append(
                f"acts.css: the no-support tier declares no {CLAIM_ROW} on "
                f".sp-stage. Above the fold the claim's grid row is the field's "
                f"band and the grid is pulled back by it; with no length to "
                f"pull by, act 1's sentence returns to the foot of its own "
                f"field and the right half of the field stays the 580 x 400 px "
                f"of nothing it was.")
        elif want and row is not None:
            inner = re.match(r"^clamp\((.*)\)$", row)
            parts = ([p.strip() for p in split_top(inner.group(1))]
                     if inner else [])
            if len(parts) != 3:
                findings.append(
                    f"acts.css: {CLAIM_ROW} is {row!r}, which is not a "
                    f"three-term clamp(). The field's band has a floor, a "
                    f"ratio and a cap, and the row that has to match it needs "
                    f"all three or it matches at one width and drifts at the "
                    f"rest.")
            else:
                names = ("floor (min-height)", "ratio (aspect-ratio)",
                         "cap (max-height)")
                for name, mine, theirs in zip(names, parts, want):
                    if re.sub(r"\s+", "", mine) != re.sub(r"\s+", "", theirs):
                        findings.append(
                            f"acts.css: {CLAIM_ROW}'s {name} is {mine!r} and "
                            f"the ink layers' is {theirs!r}. The claim's row "
                            f"is the field's own height restated as a length; "
                            f"the two disagree, so the sentence is drawn for a "
                            f"band the field does not have. Measured in "
                            f"Firefox 153 while they agree: 480 px at 390 and "
                            f"768, 576 at 1024, 644 at 1280 and 1440, 824 at "
                            f"1920 -- floor, ratio and cap each binding "
                            f"somewhere in that sweep.")

    copy_blocks = declarations_for(COPY_LAYER, css)
    for b in copy_blocks:
        if f"var({CLIP})" in (value_of("clip-path", b) or ""):
            findings.append(
                f"acts.css: {COPY_LAYER} clips to var({CLIP}). That layer is the "
                f"copy, and prose under the horizon is what the band exists to "
                f"uncover -- clipping it is the fault inverted.")

    # ---- released inside the pin gate, and only there ---------------------
    gate = block_span(css, r"@supports\s*\(\s*animation-timeline\s*:\s*view\(\)\s*\)")
    if gate is None:
        findings.append(
            "acts.css: no @supports (animation-timeline: view()) block. The "
            "release of the band is scoped to the pinned tier, and the pinned "
            "tier is that block.")
    releases_in, releases_out = 0, 0
    for body, at in declarations_with_offsets(".sp-stage", css):
        v = value_of(CLIP, body)
        if not (v and v.strip() == "none"):
            continue
        if gate and gate[0] < at < gate[1]:
            releases_in += 1
        elif fallback and fallback[0] < at < fallback[1]:
            # The no-support tier releases it for the pinned tier's own reason,
            # arrived at from the other side: the horizon exists to keep act 1's
            # ink off act 2's prose, and there the ink is a band that ends above
            # the claim -- .sp-annots-fig's `overflow: hidden` ends the notes at
            # the same edge. What the clip would do is stop the lattice half way
            # down a stage the reader is still inside.
            releases_in += 1
        else:
            releases_out += 1
            line = css[:at].count("\n") + 1
            findings.append(
                f"acts.css:{line}: {CLIP} is released outside the pin gate. "
                f"Only the pinned tier has no copy under the drawing -- .sp-say "
                f"is placed over the root inside the @supports block and is "
                f"ordinary flow under it everywhere else, so a release that "
                f"reaches the flow tier hands the field and all twenty-one "
                f"callouts back to act 2's four paragraphs. Measured before "
                f"this clause: 11 799 px of ink on that copy at 1024 x 900 "
                f"under reduced motion, 6 332 at 1920 x 1080.")
    if gate and not releases_in:
        findings.append(
            f"acts.css: {CLIP} is never released inside the pin gate. There the "
            f"stage IS the viewport and act 1's field is full bleed by "
            f"construction; with the flow tier's band left on, the sliced "
            f"1600 x 900 backdrop is cropped to 387 px of an 800 px stage at "
            f"1440 x 900 -- 48 % of the screen it was drawn to fill.")

    # ---- and re-derived above the fold rather than dropped ---------------
    split = column_split(css)
    if split is None:
        findings.append(
            "acts.css: .sp-stage__inner declares no two-track "
            "grid-template-columns. The band above the fold is the figure "
            "column's share of the row, and there is no row to read it from.")
    fold_band = None
    for m in re.finditer(r"@media([^{]*)\{", css):
        prelude = m.group(1)
        if "min-width" not in prelude or RELEASE not in prelude:
            continue
        if "min-height" in prelude:      # the pin gate, not the fold
            continue
        span = block_span(css[m.start():], r"@media")
        if not span:
            continue
        lo, hi = m.start() + span[0], m.start() + span[1]
        for body, at in declarations_with_offsets(".sp-stage", css):
            if lo < at < hi:
                v = value_of(BAND, body)
                if v:
                    fold_band = v
    if fold_band is None:
        findings.append(
            f"acts.css: {BAND} is not re-derived in a bare @media (min-width: "
            f"{RELEASE}). Above the fold .cf-statement takes its two-column "
            f"form and the drawing stops being the whole row, so the one-column "
            f"band is too tall by the width of the text column -- 198 px at "
            f"1023, mid-field, through two labels. Dropping the band instead is "
            f"the defect the clause above catches; the answer is a band for the "
            f"arrangement that is actually on screen.")
    elif split:
        want = f"{split[0]:g} / {split[1]:g}"
        if want not in re.sub(r"\s+", " ", fold_band):
            findings.append(
                f"acts.css: the fold band does not name the column split "
                f"{want} that .sp-stage__inner declares ({fold_band!r}). The "
                f"drawing is the figure track's width and the figure track is "
                f"that share of the row less the gap; re-track the grid and "
                f"this number moves with it or the horizon lands mid-field "
                f"again.")
        for token in ("var(--gutter)", "var(--container-max)", "var(--space-8)"):
            if token not in fold_band:
                findings.append(
                    f"acts.css: the fold band does not read {token} "
                    f"({fold_band!r}). Its terms are the container's inner box "
                    f"-- min(100vw - 2 gutters, --container-max) -- less the "
                    f"grid's own gap. Any other figure is a guess at a number "
                    f"tokens.css owns.")
        if ratio:
            pair = re.findall(r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)", fold_band)
            if not pair or (float(pair[-1][1]), float(pair[-1][0])) != ratio:
                findings.append(
                    f"acts.css: the fold band does not end in the drawing's own "
                    f"{ratio[1]:g} / {ratio[0]:g} ({fold_band!r}). Both bands "
                    f"are the same svg's used height; they differ only in how "
                    f"wide the svg is.")
    released = bool(releases_in) and not releases_out

    if args.verbose:
        print(f"band   {BAND}: {band or '-'}")
        if ratio:
            print(f"ratio  {ratio[1]:g} / {ratio[0]:g}  (h / w)")
        for rel, w, h in boxes:
            print(f"  .lp-flow  viewBox 0 0 {w:g} {h:g}   {rel}")
        for rel, w, h, margin in fields:
            print(f"  .sp-field viewBox 0 0 {w:g} {h:g}   bead margin {margin:g}"
                  f"   cap floor >= {(h - 2 * margin) / w * 100:.4g}vw   {rel}")
        print(f"ink    {', '.join(INK_LAYERS)}")
        print(f"copy   {COPY_LAYER}")
        if split:
            print(f"split  {split[0]:g} / {split[1]:g}  (figure track of the row)")
        print(f"fold   {BAND} above {RELEASE}: {fold_band or '-'}")
        print(f"release inside the pin gate only: {'yes' if released else 'no'}\n")

    for f in findings:
        print(f"FINDING     {f}")
    if findings:
        print(f"\n{len(findings)} finding(s).")
        return 1
    print(f"OK  the ground band is {boxes[0][1]:g} x {boxes[0][2]:g}'s own ratio "
          f"in --gutter's own terms, both ink layers clip to it, the copy layer "
          f"does not, no box is resized outside the two tiers that size the "
          f"ink and in each of them both layers take one band -- the same band "
          f"in both -- taken off the half the claim reserves rather than split "
          f"around it, with a floor and a cap that leaves the claim its room "
          f"below the fold, releases it above {RELEASE} and stops at the "
          f"beads' own rim either way, it is re-derived above {RELEASE} "
          f"from the row's own column split, {CLAIM_ROW} restates that band's "
          f"own floor, ratio and cap, and it is released in the pin gate "
          f"and those tiers and nowhere else.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
