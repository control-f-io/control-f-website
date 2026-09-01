#!/usr/bin/env python3
"""Lime is never flat, and the list of where it is was three names long.

The one hundred and thirty-eighth check, and the first whose subject is the
light layer as a layer. foundations/colors.html has stated the rule since the
palette was written:

    LIME NEVER APPEARS AS A FLAT FILL. Wherever it fills an area, it fills it
    with a gradient -- one of the light family, running out of lime into Glas
    and away to CF-Grau. A rhombus painted #E1FF00 edge to edge is not the
    light layer; it is a yellow shape.

and then closed with a table headed "Three exceptions, and each is a technical
one": the palette swatch, the found state, and a stroke. Three names, kept by
hand, over a rule that reaches every stylesheet in the system.

WHAT THE HAND COUNT MISSED. Swept over the four shipping stylesheets, the
system paints a flat lime AREA in SEVEN places. The three names covered five of
them -- the found state's four registers plus the calendar's today, all one
kind. Two had no row at all:

  .lp-flow__src::after     the NUCLEUS of a source. Measured on the rendered
                           landing page at 1440 x 900: a 3.6 px core, flat
                           rgb(225,255,0), background-image `none`, standing
                           inside 5.4 px of lime and 12 px of Glas of glow.
                           The chapter's own table two paragraphs above the
                           exception list says "a rim, a ring, a NUCLEUS ->
                           --gradient-bloom", so the page and the rule
                           disagreed, twenty-five times, on the flagship.
  .map__key-dot--asset     a LEGEND KEY. The list's first row is "the palette
  .map__key-dot--kind      swatch on this page" -- the specimen on
                           foundations/colors.html, named as a place rather
                           than as a kind. A key on a map is the same argument
                           at a different address and had no row to sit in.

NEITHER IS A DEFECT IN THE DRAWING. Both are right and the rule was
incomplete, which is the more expensive way for a rule to be wrong: a stated
exception list that does not cover what ships teaches a reader that the rule is
advisory. foundations/light.html restates the list as a BOUNDARY with four
categories -- a highlight, a swatch, a source's nucleus, and a thing that is
not an area. Three of the four carry the seven; the fourth carries none by
construction, because it is the rule's edge rather than an exception inside it,
and it is enforced here by not looking. This file holds the boundary to what
the stylesheets actually do.

WHY A SCRIPT. Every failure here renders. A flat lime plane is a perfectly good
yellow rectangle; nothing overflows, no reference breaks, no contrast figure
moves -- lime on CF-Grau is 1.37:1 whether it is ramped or not, so the contrast
suite cannot see this either. What is lost is the only thing the light layer
says: where the light is coming from. That is invisible in a screenshot of the
element and obvious in a screenshot of the page next to every other lit mark,
which is the shape of defect the rest of this directory exists for.

WHAT COUNTS AS A FLAT LIME AREA IS DERIVED, NOT LISTED. The script reads the
four shipping stylesheets, walks every rule, and takes every declaration of an
AREA property whose value resolves to a lime and carries no ramp. Lime is
resolved through the stylesheets' own aliases rather than through a table of
names here: --accent, --found-light and --focus-ring are lime because tokens.css
says `var(--cf-lime)`, and a fifth alias enters this claim by being declared,
not by somebody remembering this file exists. That is the same argument
check-glass-budget.py makes about backdrop-filter and check-gradient-family.py
about the oklab waypoint.

THE AREA PROPERTIES ARE THE WHOLE OF THE RULE'S REACH, and the boundary is the
chapter's: `background`, `background-color`, `background-image`, `fill`. Not
stroke, not outline, not border-color, not box-shadow, not color, not
-webkit-text-fill-color. "A line has no plane to ramp across, and the rule is
about area" is the fourth boundary and it is enforced by not looking, which is
the honest way to enforce a rule about what a rule does not cover.

BOTH DIRECTIONS ARE HELD. An uncovered flat lime is a finding; so is a COVERED
entry that matches nothing, because a stale exemption is how a list stops being
read. The census below is stamped into foundations/light.html so the chapter
cannot drift from the stylesheets the way the three-name list did.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-lime-flat.py          # check, exit 1 on drift
    python3 scripts/check-lime-flat.py --fix    # rewrite the census + stamp
    python3 scripts/check-lime-flat.py -v       # list every area paint examined
"""

import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"
LIGHT_DOC = DS / "foundations" / "light.html"

# The stylesheets that ship to control-f.de. docs.css is documentation chrome
# and does not ship -- the same boundary check-glass-budget.py and
# check-spacing-scale.py draw, and for the same reason: a documentation page
# whose subject IS the colour has to be allowed to print the colour.
SHIPPING_CSS = ("tokens.css", "base.css", "components.css", "acts.css")

# The rule's reach. foundations/light.html states it as "the rule is about
# area", and these four are what paints one. A stroke, an outline, a ring, a
# shadow and an ink are outside it by the chapter's own fourth boundary.
AREA_PROPS = ("background", "background-color", "background-image", "fill")

# The palette's own lime, as the swatch on foundations/colors.html prints it.
# The ramp steps are read out of tokens.css rather than listed, so a step added
# to the ramp is in scope on the day it is declared.
LIME_LITERAL = re.compile(r"#(?:e1ff00|E1FF00)\b")

# A value that carries a ramp is not flat, whatever colour it names. The three
# gradient functions are the CSS half; --bloom-image, --foil-image and the
# --gradient-* family are the tokens the system paints ramps through, and
# .material-bloom's own --bloom-ramp is a stop LIST rather than an image, so it
# is a ramp too. Matching on the shape rather than on a roster means a fifth
# ramp token is covered by being named like one.
RAMP = re.compile(
    r"(?:linear|radial|conic)-gradient\s*\(|var\(\s*--(?:gradient-[a-z0-9-]+|"
    r"bloom-(?:image|ramp)|foil-[a-z0-9-]+|rake-ramp|field-bloom|spectrum-stops)\b"
)

# THE SEVEN, AND WHAT MAKES EACH OF THEM RIGHT. A key here is a selector as the
# stylesheet writes it, normalised for whitespace. The value is the boundary in
# foundations/light.html it sits under, and the argument -- which is the part
# that has to survive review, because the boundary alone would let anything in.
#
# THIS IS NOT A PLACE TO PARK A FLAT LIME THAT IS MERELY SHIPPING. An entry has
# to name a boundary and say what makes the mark fall outside the rule: the
# platform refuses the declaration, the mark is a specimen of the colour rather
# than an application of it, or the mark is a source whose falloff is the glow
# around it. "It looked fine" is an argument for changing the drawing.
COVERED = {
    "::selection": (
        "highlight",
        "background-image is not painted on a highlight pseudo-element. There "
        "is no gradient form of this declaration to reach for.",
    ),
    "::target-text": (
        "highlight",
        "the same pseudo-element, and the register a reader arrives on from a "
        "shared link or a search engine.",
    ),
    "::highlight(cf-found-current)": (
        "highlight",
        "the same, through the Custom Highlight API.",
    ),
    ".cf-mark--current": (
        "highlight",
        "an ELEMENT, and it could take a ramp. It is held to the pseudo-"
        "element's means on purpose: a match is one drawing wherever it is "
        "drawn, and three of the four registers cannot ramp.",
    ),
    '.cf-calendar__day[aria-current="date"] > time': (
        "highlight",
        "the found state at day scale -- the same pair, the same reason, and "
        "the contrast is carried by --found-rule rather than by the plate.",
    ),
    ".lp-flow__src::after": (
        "nucleus",
        "the core of a source. A light's falloff is the glow it throws, not a "
        "ramp inside it: measured, 3.6 px of core inside 5.4 px of lime and "
        "12 px of Glas. The ramp is there and it is outside the fill.",
    ),
    ".map__key-dot--asset, .map__key-dot--kind": (
        "swatch",
        "a legend key. A swatch of a colour has to be the colour -- a ramp "
        "here would name a colour the key does not mean. Lime is the fallback "
        "and the value of one kind; the other five steps are not lime at all.",
    ),
}


def blank_comments(text):
    """Comments replaced by spaces IN PLACE, so every offset and every line
    number in the result is the one a reader will find in the file. The same
    device check-glass-budget.py uses, and for the same reason: these
    stylesheets are more prose than declaration, and a checker that names the
    wrong line is worse than one that names none."""
    chars = list(text)
    for m in re.finditer(r"/\*.*?\*/", text, re.S):
        for i in range(m.start(), m.end()):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)


def rules(text):
    """Every selector/block pair in a stylesheet, with the selector's line.

    At-rules are walked into rather than over: tokens.css redefines the whole
    light family inside @supports, and a flat lime written inside a
    @media (forced-colors) branch is exactly the one this rule would most like
    to miss.
    """
    text = blank_comments(text)
    out, stack, start = [], [], 0
    for i, ch in enumerate(text):
        if ch == "{":
            raw = text[start:i]
            sel_at = start + (len(raw) - len(raw.lstrip()))
            stack.append((raw.strip(), i + 1, text.count("\n", 0, sel_at) + 1))
            start = i + 1
        elif ch == "}":
            if stack:
                head, body_start, line = stack.pop()
                if not head.startswith("@"):
                    out.append((head, text[body_start:i], line))
            start = i + 1
    return out


def declarations(body):
    """property, value pairs, with nested blocks already removed by rules()."""
    for decl in body.split(";"):
        prop, sep, value = decl.partition(":")
        if sep:
            yield prop.strip().lower(), value.strip()


def lime_names():
    """Every custom property that resolves to the palette's lime.

    Seeded with --cf-lime and the ramp's own steps, then closed over the
    stylesheets' aliases until nothing new appears: --accent is lime because
    tokens.css says so, --found-light because tokens.css says --accent, and a
    fifth alias joins on the day it is declared rather than on the day somebody
    remembers this file. Only the LIT end of the ramp is lime for this rule --
    --lime-700, -800 and -900 are the dark steps the system uses as INK on a
    light ground, and ink is not the light layer.
    """
    names = {"--cf-lime"}
    text = "\n".join(blank_comments((CSS / f).read_text()) for f in SHIPPING_CSS)

    for m in re.finditer(r"(--lime-[0-9]{3})\s*:\s*(#[0-9A-Fa-f]{6})", text):
        if LIME_LITERAL.search(m.group(2)):
            names.add(m.group(1))

    alias = re.compile(r"(--[A-Za-z0-9_-]+)\s*:\s*var\(\s*(--[A-Za-z0-9_-]+)\s*\)\s*(?:;|$)", re.M)
    grew = True
    while grew:
        grew = False
        for m in alias.finditer(text):
            if m.group(2) in names and m.group(1) not in names:
                names.add(m.group(1))
                grew = True
    return names


def is_flat_lime(value, names):
    """A value that paints a lime area and carries no ramp.

    The var() fallback counts: `var(--map-k, var(--cf-lime))` paints lime
    wherever --map-k is unset, which on the map is every element that has no
    data-k, and a rule that only saw the first argument would have missed the
    one entry in COVERED that is a fallback.
    """
    if RAMP.search(value):
        return False
    if LIME_LITERAL.search(value):
        return True
    return any(re.search(r"var\(\s*%s\b" % re.escape(n), value) for n in names)


def sweep():
    """Every flat lime area paint in the shipping stylesheets, in file order."""
    names = lime_names()
    found = []
    for filename in SHIPPING_CSS:
        text = (CSS / filename).read_text()
        for selector, body, line in rules(text):
            for prop, value in declarations(body):
                if prop in AREA_PROPS and is_flat_lime(value, names):
                    found.append(
                        {
                            "file": filename,
                            "line": line,
                            "selector": re.sub(r"\s*,\s*", ", ", " ".join(selector.split())),
                            "property": prop,
                            "value": " ".join(value.split()),
                        }
                    )
    return found


def rows(found):
    """The census: one row per covered flat lime area, sorted for stability.

    THE LINE NUMBER IS NOT IN THE ROW, and that is the whole difference between
    a census a reader trusts and one every lane learns to run --fix on without
    reading. Four lanes edit these stylesheets hourly and most of what they add
    is prose; the first merge from main after this file was written moved three
    of the seven rules by 16, 16 and 48 lines and changed nothing about any of
    them. A stamp that churns on an edit that is not about its subject is a
    stamp nobody reads, which is the failure this script exists to prevent one
    level up.

    The file survives, because a rule moving between stylesheets IS a change of
    subject -- a flat lime crossing from components.css into acts.css has moved
    onto the page carrying the tightest budget in the system. The line is
    reported in -v and in every failure message, where it points a reader at
    the declaration and is read once rather than stored.
    """
    out = []
    for hit in found:
        boundary, _ = COVERED.get(hit["selector"], ("uncovered", ""))
        out.append((hit["selector"], boundary, hit["file"]))
    return sorted(out)


def stamp_of(census):
    """A digest of the rows, so a reader can tell a current table from an old
    one without diffing it against a stylesheet they have not opened."""
    payload = "\n".join("\t".join(row) for row in census)
    return hashlib.sha256(payload.encode()).hexdigest()[:8]


CENSUS_TABLE = re.compile(r'(<table[^>]*\bid="lime-flat-census"[^>]*>).*?(</table>)', re.S)

# The stamp is found by its SHAPE and there must be exactly one of it on the
# page, which is the convention check-glass-budget.py established for the census
# in foundations/materials.html. A class would be a hook that exists for a
# script and is declared nowhere — check-class-provenance.py says so, and it is
# right: a page's classes are what draws it, not what reads it.
STAMP = re.compile(r"<code>[0-9a-f]{8}</code>")


def render_table(census):
    lines = [
        "      <thead>",
        "        <tr><th>Where</th><th>Boundary</th><th>Stylesheet</th></tr>",
        "      </thead>",
        "      <tbody>",
    ]
    for selector, boundary, where in census:
        lines.append(
            "        <tr><td><code>%s</code></td><td>%s</td><td><code>%s</code></td></tr>"
            % (selector.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;"),
               boundary, where)
        )
    lines.append("      </tbody>")
    return "\n".join(lines)


def doc_state():
    """The table and the stamp as the chapter currently carries them.

    The stamp is required to be SOLE: zero means the sentence naming it was
    edited away and the digest is no longer published; two means a later edit
    put another eight-hex code on the page and --fix would rewrite whichever
    one it reached first. Both are reported rather than guessed at.
    """
    html = LIGHT_DOC.read_text()
    table = CENSUS_TABLE.search(html)
    stamps = STAMP.findall(html)
    body = []
    if table:
        for m in re.finditer(r"<tr><td><code>(.*?)</code></td><td>(.*?)</td><td><code>(.*?)</code></td></tr>",
                             table.group(0)):
            body.append((m.group(1).replace("&amp;", "&").replace("&lt;", "<").replace("&quot;", '"'),
                         m.group(2), m.group(3)))
    return html, table, body, stamps


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fix", action="store_true", help="rewrite the census and the stamp")
    ap.add_argument("-v", "--verbose", action="store_true", help="list every area paint examined")
    args = ap.parse_args()

    found = sweep()
    census = rows(found)
    stamp = stamp_of(census)
    failures = []

    if args.verbose:
        for hit in found:
            boundary, why = COVERED.get(hit["selector"], ("UNCOVERED", ""))
            print("%-14s %-5s %-46s %-9s %s"
                  % (hit["file"], hit["line"], hit["selector"], boundary, hit["value"]))
            if why:
                print("%s%s" % (" " * 16, why))

    # 1. Every flat lime area sits under a boundary, with an argument.
    for hit in found:
        if hit["selector"] not in COVERED:
            failures.append(
                "%s:%d  %s { %s: %s }\n"
                "    A flat lime area with no boundary. foundations/light.html names four:\n"
                "    a highlight, a swatch, a source's nucleus, and a thing that is not an\n"
                "    area. If this is a lit SURFACE it takes a ramp -- see the table on\n"
                "    foundations/colors.html#lime-is-never-flat for which one. If it is not,\n"
                "    add it to COVERED in this file with the argument that puts it outside\n"
                "    the rule."
                % (hit["file"], hit["line"], hit["selector"], hit["property"], hit["value"])
            )

    # 2. No boundary outlives the thing it was written for. A stale exemption is
    #    how a list stops being read, which is the defect this file was written
    #    about in the first place.
    live = {hit["selector"] for hit in found}
    for selector in sorted(COVERED):
        if selector not in live:
            failures.append(
                "COVERED carries `%s` and nothing in the shipping CSS matches it.\n"
                "    Either the rule moved and this entry follows it, or the flat lime is\n"
                "    gone and so is its exemption." % selector
            )

    # 3. The chapter's census is the sweep's.
    html, table, doc_rows, stamps = doc_state()
    where = LIGHT_DOC.relative_to(ROOT)
    if args.fix:
        if not table or len(stamps) != 1:
            print("check-lime-flat: %s carries no #lime-flat-census table, or %d stamps "
                  "where there must be one" % (where, len(stamps)), file=sys.stderr)
            return 1
        html = CENSUS_TABLE.sub(
            lambda m: "%s\n%s\n    %s" % (m.group(1), render_table(census), m.group(2)), html)
        html = STAMP.sub("<code>%s</code>" % stamp, html)
        LIGHT_DOC.write_text(html)
        print("check-lime-flat: rewrote %d rows, stamp %s" % (len(census), stamp))
        return 0

    if not table:
        failures.append('%s carries no table with id="lime-flat-census".' % where)
    elif doc_rows != census:
        failures.append(
            "the census in %s is not the sweep. Run --fix.\n    page: %d rows\n    css:  %d rows"
            % (where, len(doc_rows), len(census)))
    if len(stamps) != 1:
        failures.append("%s carries %d eight-hex stamps; there must be exactly one."
                        % (where, len(stamps)))
    elif stamps[0] != "<code>%s</code>" % stamp:
        failures.append("the stamp in %s is stale. Run --fix." % where)

    if failures:
        print("check-lime-flat: %d finding(s)\n" % len(failures), file=sys.stderr)
        for text in failures:
            print("  " + text + "\n", file=sys.stderr)
        return 1

    print("check-lime-flat: %d flat lime areas, all four boundaries, stamp %s"
          % (len(census), stamp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
