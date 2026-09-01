#!/usr/bin/env python3
"""A glass rim stands on its sheet's border box, not one pixel inside it.

The sixtieth check, and the second in this directory about the same one-pixel
mistake in a different construction. check-contour-box.py states the rule for
the form it was found in:

    `inset` on an absolutely positioned box resolves against its containing
    block's PADDING box. Giving up `border-color` does not give up
    `border-width`: the component still reserves it, so its padding box is one
    border-width inside its border box on every side.

That script goes on to enforce it for <svg> EDGE FRAMES, because an edge frame
was what it was written after. This one is the same sentence about a 1 px
pseudo-element, which is the other way this system draws an edge over an edge.

THE MATERIAL RULE IT PROTECTS. foundations/materials.html and tokens.css both
say it and neither could check it: glass in this brand is edged with light and
never outlined with ink, and it is edged ONCE. Every frosted surface ends at a
single lit pixel of --glass-edge, optionally with --glass-rim-light crossing
it. A rim written at `inset: 0` over a sheet that reserves a border does not
replace that border — it lands one pixel below it, two pixels short of it at
each end, and the sheet draws two parallel lines: the flat --glass-border on
the outside and the material's whole Weiss-Glas-Sky travel on the inside.

WHAT IT WOULD HAVE CAUGHT, measured on components/info-card.html at 1440 x 900,
device scale 1, .cf-info-card--glass' border box 608 px wide, reading the ink:

    row 0   253-254 flat                the border, drawn by the card
    row 1   251 .. (240, 248, 246)      --glass-edge, drawn by the rim, x 1..607
    row 2   251                         the bearing tint

Three of the system's three rims were written by hand against the same idiom
and one of them was written against the wrong box. .cf-btn--glass::before
cancels the width on `top` and `left` and carries the cancellation into its own
62 % window; .cf-nav::after has no border to cancel; .cf-info-card--glass
::before did not, on the one glass surface whose only shipping use is a stage
the reader scrolls through at reading distance. Nothing rendered wrong. There
was a second line.

That is the whole test for what belongs in one of these scripts, and it is the
same one check-contour-box.py passes: the component is the right size, the
strip is the right height, the gradient is the right gradient, every stop is in
the right place, and the edge is one pixel low.

THE RULE. For every rule in the shipping CSS whose selector names a pseudo-
element (::before / ::after) and whose background reaches --glass-edge or
--glass-rim-light — that is a rim, and its originating element is the sheet —
let B be the border-width the sheet reserves on each side. For every side the
rim positions with a non-auto inset, that inset must equal -B on that side.
Sides the rim leaves `auto` are unconstrained: a windowed rim positions two
edges and sizes itself across the third, which is what the hero button does.

WHAT IT DOES NOT CHECK, so that the next reader does not assume it did.

  * The rim's WIDTH. .cf-btn--glass::before writes `62% + 0.62 * 2 *
    var(--stroke-1)` — the window, plus the same cancellation expressed
    through a percentage — and a checker that could verify that arithmetic
    would have to resolve the percentage against a box only a browser knows.
    The insets are the half that is stateable, and they are the half the
    defect was in.
  * The CASCADE. The sheet's border is read off every rule in the shipping
    CSS whose selector list contains the originating selector literally, last
    declaration winning per side. That is not selector matching: a border put
    on .cf-info-card--glass through some other selector that also matches it
    is invisible here. It is enough for the three rims that exist and it is
    written down rather than implied.

TOKENS ARE RESOLVED, AND DISAGREEMENT IS A FINDING. --stroke-1 and
--glass-border are custom properties, and --glass-border is redeclared in the
inverse theme. A rim cancelling 1 px over a sheet whose border is 2 px in one
theme is the same defect in one theme only, so every declaration of a token
this script resolves has to agree on its length; if two disagree the script
says so rather than picking one.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-glass-rim-box.py       # check, exit 1 on drift
    python3 scripts/check-glass-rim-box.py -v    # list every rim, not only hits
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

# The stylesheets that ship to control-f.de, in the order the pages load them.
# docs.css is documentation chrome and does not ship — the same boundary
# check-glass-budget.py and check-spacing-scale.py draw.
SHIPPING_CSS = ("tokens.css", "base.css", "components.css", "acts.css")

# What makes a pseudo-element a rim. Both are the material's own tokens: one is
# the lit edge itself and one is the specular that crosses it, and a strip that
# carries either is a glass perimeter rather than decoration. Reading the TOKENS
# rather than a list of selectors is the same choice check-glass-budget.py makes
# about what counts as glass — a fourth rim enters this check by existing.
RIM_TOKENS = ("--glass-edge", "--glass-rim-light")

SIDES = ("top", "right", "bottom", "left")


def strip_comments(text):
    """Comments out, LINE NUMBERS INTACT.

    Every comment is replaced by its own newlines rather than deleted, so an
    offset into the stripped text is still an offset into the file. These
    stylesheets are more comment than declaration — the rule this script was
    written about sits under forty lines of them — and a report that points
    2 500 lines above its subject is a report nobody can act on.
    """
    return re.sub(r"/\*.*?\*/",
                  lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def rules(text):
    """Every `selector { declarations }` in the sheet, at any nesting depth.

    A brace walk rather than a regex: these sheets nest rules inside @media,
    @supports and @container, and the blocks that matter here are inside all
    three. An at-rule's own prelude is not a selector, so a block whose
    prelude starts with @ is descended into rather than recorded.
    """
    out = []
    depth = 0
    start = 0
    stack = []
    i = 0
    while i < len(text):
        c = text[i]
        if c == "{":
            prelude = text[start:i].strip()
            stack.append((prelude, i + 1))
            depth += 1
            start = i + 1
        elif c == "}":
            if stack:
                prelude, body_start = stack.pop()
                body = text[body_start:i]
                if prelude and not prelude.startswith("@"):
                    # Only the declarations directly in this block; nested
                    # blocks are recorded separately by their own turn here.
                    flat = re.sub(r"\{[^{}]*\}", "", body)
                    out.append((prelude, flat, body_start))
                depth -= 1
            start = i + 1
        i += 1
    return out


def declarations(body):
    """name -> value for one block, last declaration winning."""
    out = {}
    for part in body.split(";"):
        if ":" not in part:
            continue
        name, _, value = part.partition(":")
        name = name.strip()
        if not name or "{" in name or "}" in name:
            continue
        out[name] = value.strip()
    return out


def custom_properties(all_rules):
    """Every custom property declared anywhere in the shipping CSS.

    Keyed by name, valued by the SET of distinct values declared for it, so a
    token two blocks disagree about is visible instead of being resolved to
    whichever came last.
    """
    props = {}
    for _selector, body, _pos in all_rules:
        for name, value in declarations(body).items():
            if name.startswith("--"):
                props.setdefault(name, set()).add(value)
    return props


def to_px(token):
    """A CSS length in px, or None if it is not one this script can read."""
    token = token.strip()
    if token in ("0", "0px"):
        return 0.0
    m = re.match(r"^(-?\d*\.?\d+)(px|rem|em)$", token)
    if not m:
        return None
    value = float(m.group(1))
    # rem and em only ever appear here through a token nobody has written yet;
    # 16 px is the root size base.css sets and the same assumption
    # check-breakpoints.py makes about a rem.
    return value * (16.0 if m.group(2) in ("rem", "em") else 1.0)


VAR = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,([^()]*))?\)")


def expand(value, props, touched=None):
    """Substitute var() until there is none left. Fallbacks are honoured.

    `touched`, when given, collects the name of every token the substitution
    passed through, so the caller can afterwards ask whether all of that
    token's declarations agree — see agreement() below.
    """
    seen = set()
    for _ in range(8):
        m = VAR.search(value)
        if not m:
            return value
        name, fallback = m.group(1), (m.group(2) or "").strip()
        values = props.get(name)
        if touched is not None:
            touched.add(name)
        if values:
            replacement = sorted(values)[0]
        elif fallback:
            replacement = fallback
        else:
            return value
        if name in seen:
            return value
        seen.add(name)
        value = value[:m.start()] + replacement + value[m.end():]
    return value


def agreement(names, props):
    """The tokens this run resolved whose declarations disagree on a length.

    --glass-border is declared twice — once on :root and once on
    [data-theme="inverse"] — and both happen to be 1 px. If one of them were
    ever 2 px, every rim in this script would be checked against a border half
    the sheet does not have in that theme, and every one would pass. A token
    two blocks disagree about is a finding, not a value to pick from.
    """
    out = []
    for name in sorted(names):
        values = props.get(name) or set()
        if len(values) < 2:
            continue
        lengths = {first_length(v, props) for v in values}
        if len(lengths) > 1:
            out.append("%s is declared %d ways and they do not agree on a "
                       "length: %s" % (name, len(values), sorted(values)))
    return out


def first_length(value, props, touched=None):
    """The first length in a value — a border shorthand's width, or a length."""
    flat = expand(value, props, touched)
    for token in re.split(r"[\s,]+", flat.strip()):
        px = to_px(token)
        if px is not None:
            return px
    return None


def signed_length(value, props, touched=None):
    """An inset value in px. None means `auto` — the side is not positioned."""
    flat = expand(value, props, touched).strip()
    if flat == "auto" or not flat:
        return None
    m = re.match(r"^calc\(\s*-1\s*\*\s*(.+?)\s*\)$", flat)
    if m:
        inner = first_length(m.group(1), props)
        return None if inner is None else -inner
    m = re.match(r"^calc\(\s*(.+?)\s*\*\s*-1\s*\)$", flat)
    if m:
        inner = first_length(m.group(1), props)
        return None if inner is None else -inner
    return to_px(flat)


def top_level_split(value):
    """Split on whitespace that is not inside parentheses.

    `inset: calc(-1 * var(--stroke-1)) calc(-1 * var(--stroke-1)) auto` is
    three components and eight spaces, and a regex that cannot count brackets
    reads it as eight. It read it as none — the first version of this split
    returned an empty list for the one rule this script was written about,
    which is the shape of failure a checker must not have: green because it
    could not see its own subject.
    """
    parts = []
    depth = 0
    current = ""
    for c in value:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if c.isspace() and depth == 0:
            if current:
                parts.append(current)
                current = ""
            continue
        current += c
    if current:
        parts.append(current)
    return parts


def inset_sides(decls, props, touched=None):
    """side -> px offset, for the sides this rule actually positions.

    Longhands beat the shorthand, which is what the cascade does inside one
    block: `inset: 0; top: -1px` positions the top at -1.
    """
    out = {}
    if "inset" in decls:
        parts = top_level_split(decls["inset"].strip())
        if len(parts) == 1:
            parts = parts * 4
        elif len(parts) == 2:
            parts = [parts[0], parts[1], parts[0], parts[1]]
        elif len(parts) == 3:
            parts = [parts[0], parts[1], parts[2], parts[1]]
        for side, part in zip(SIDES, parts[:4]):
            out[side] = signed_length(part, props, touched)
    for side in SIDES:
        if side in decls:
            out[side] = signed_length(decls[side], props, touched)
    return out


def sheet_borders(origin, all_rules, props, touched=None):
    """side -> reserved border-width in px for the rim's originating element.

    Every rule whose selector list names the origin literally, in source order,
    last declaration winning per side. Not selector matching; see the header.
    """
    widths = {side: 0.0 for side in SIDES}
    for selector, body, _pos in all_rules:
        names = [s.strip() for s in selector.split(",")]
        if origin not in names:
            continue
        decls = declarations(body)
        if "border" in decls:
            width = first_length(decls["border"], props, touched)
            if width is None and decls["border"].strip() in ("0", "none"):
                width = 0.0
            if width is not None:
                for side in SIDES:
                    widths[side] = width
        if "border-width" in decls:
            width = first_length(decls["border-width"], props, touched)
            if width is not None:
                for side in SIDES:
                    widths[side] = width
        for side in SIDES:
            for name in ("border-%s" % side, "border-%s-width" % side):
                if name in decls:
                    width = first_length(decls[name], props, touched)
                    if width is None and decls[name].strip() in ("0", "none"):
                        width = 0.0
                    if width is not None:
                        widths[side] = width
    return widths


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every rim, not only the ones that drift")
    args = ap.parse_args()

    all_rules = []
    for name in SHIPPING_CSS:
        path = CSS / name
        if not path.exists():
            print("missing stylesheet: %s" % path)
            return 1
        text = strip_comments(path.read_text(encoding="utf-8"))
        for selector, body, pos in rules(text):
            line = text.count("\n", 0, pos) + 1
            all_rules.append((selector, body, (name, line)))

    props = custom_properties(all_rules)

    problems = []
    touched = set()
    rims = 0

    for selector, body, where in all_rules:
        decls = declarations(body)
        painted = " ".join(v for k, v in decls.items()
                           if k in ("background", "background-image"))
        if not any(token in painted for token in RIM_TOKENS):
            continue
        for one in [s.strip() for s in selector.split(",")]:
            m = re.match(r"^(.*?)(::?(?:before|after))$", one)
            if not m:
                continue
            origin = m.group(1).strip()
            if not origin:
                continue
            rims += 1
            borders = sheet_borders(origin, all_rules, props, touched)
            insets = inset_sides(decls, props, touched)
            positioned = {s: v for s, v in insets.items() if v is not None}
            bad = []
            for side, offset in sorted(positioned.items()):
                reserved = borders[side]
                if reserved and abs(offset + reserved) > 0.01:
                    bad.append("%s is %+g px where the sheet reserves %g px of "
                               "border, so the rim lands %g px inside it"
                               % (side, offset, reserved, reserved + offset))
            if bad:
                problems.append(
                    "%s:%d  %s\n      sheet %s reserves %s\n      %s"
                    % (where[0], where[1], one, origin,
                       ", ".join("%s %g" % (s, borders[s]) for s in SIDES
                                 if borders[s]),
                       "\n      ".join(bad)))
            elif args.verbose:
                print("ok  %-34s over %-24s insets %s" % (
                    one, origin,
                    ", ".join("%s %+g" % (s, v)
                              for s, v in sorted(positioned.items())) or "none"))

    # A check whose subject has vanished passes for the wrong reason. Three
    # rims ship today; a run that finds none is a rename this script did not
    # follow, not a system with no glass in it.
    if rims == 0:
        print("check-glass-rim-box: found no glass rim at all.")
        print("Nothing in the shipping CSS declares a ::before or ::after that")
        print("paints %s." % " or ".join(RIM_TOKENS))
        print("Either the material was retired or this script's definition of")
        print("a rim has gone stale. Neither is a pass.")
        return 1

    if problems:
        print("A glass rim is not standing on its sheet's border box.\n")
        for problem in problems:
            print("  " + problem + "\n")
        print("`inset` resolves against the PADDING box, and a sheet that")
        print("reserves a border is one border-width wider than that on every")
        print("side. A rim written at 0 lands inside the border it is meant to")
        print("replace and the sheet draws two lines. Cancel the width:")
        print("`inset: calc(-1 * var(--stroke-1)) calc(-1 * var(--stroke-1)) auto`,")
        print("the same way .cf-btn--glass::before does.")
        print("\nSee foundations/materials.html and scripts/check-contour-box.py,")
        print("which states the identical rule for <svg> edge frames.")
        return 1

    disagreements = agreement(touched, props)
    if disagreements:
        print("Every rim above cancels a border-width that is not one number.\n")
        for line in disagreements:
            print("  " + line + "\n")
        print("A rim cancels a length, so the length has to be the same one in")
        print("every theme the sheet is drawn in. Where they differ, the rim is")
        print("right in one theme and a pixel out in the other — and passes")
        print("this check in both.")
        return 1

    print("check-glass-rim-box: %d glass rim%s, every one on its sheet's "
          "border box (%s resolved, %d agreeing)."
          % (rims, "" if rims == 1 else "s",
             ", ".join(sorted(touched)) or "no token", len(touched)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
