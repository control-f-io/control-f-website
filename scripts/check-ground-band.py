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
                    would move the slice crop.
  gate off          the band is released ONLY inside the pin gate. A bare
                    `@media (min-width: 64rem)` releasing it is the finding
                    below.
  fold band         above 64rem the band is re-derived from the two-column
                    split rather than dropped, and the split it names is the
                    one .sp-stage__inner actually declares.

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
# The stage's copy layer. Prose is what the band exists to get out from under;
# clipping it would be the fault inverted.
COPY_LAYER = ".sp-say"
BAND = "--sp-ground"
CLIP = "--sp-ground-clip"
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


def declarations_with_offsets(selector, css):
    """As declarations_for, but each entry is (body, offset of the body).

    The offset is what the `gate off` clause is about: the same declaration is
    correct inside the pin gate and a defect outside it, so the check has to
    know where in the file it was written.
    """
    out = []
    pattern = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
    for m in pattern.finditer(css):
        selectors = [s.strip() for s in m.group(1).split(",")]
        if any(s == selector or s.endswith(" " + selector) for s in selectors):
            out.append((m.group(2), m.start(2)))
    return out


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
    for layer in INK_LAYERS:
        blocks = declarations_for(layer, css)
        if not blocks:
            findings.append(f"acts.css: {layer} has no declaration block to read.")
            continue
        clipped = any(f"var({CLIP})" in (value_of("clip-path", b) or "")
                      for b in blocks)
        if not clipped:
            findings.append(
                f"acts.css: {layer} does not clip to var({CLIP}). The field and "
                f"the notes are one picture -- a note whose bead has been "
                f"clipped away points at nothing -- so every ink layer inset to "
                f"the stage reads the same band or none of them does.")
        for b in blocks:
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
          f"does not, neither box is resized, it is re-derived above {RELEASE} "
          f"from the row's own column split, and it is released in the pin gate "
          f"and nowhere else.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
