#!/usr/bin/env python3
"""Every SVG paint on a pattern page resolves against the illustration registers.

foundations/illustration.html states the whole of the system's drawing palette
in prose and swatches, and states it as a closed set. Three greys for a sparse
object -- "no more, because a face is either pointing at the sky, at the light,
or away from it". Five values for a dense one, where "faces run near-white,
the contour does all of the describing", plus the foundation trio one step
under the machine. One lit element per object, on the light family's ramp. And
the contour, which is black and is the drawing.

Every one of those values reaches a pattern page as an SVG presentation
attribute -- fill="#CFCFCF", stop-color="#E1FF00" -- because geometry lives in
the markup (components.css says so at .cf-iso) and a presentation attribute
cannot resolve a token. So the palette ships as literals, typed by hand or by
a generator, on the one surface no literal gate reads: check-local-literals.py
stops at CSS -- <style> blocks, style="" attributes, page stylesheets -- and
says so; check-gradient-family.py reads stop-colors but only to hold the lime
ramp's waypoint geometry, not membership; check-line-types.py holds the same
markup's dasharrays and not its paints.

The exposure is the one the gradient check's own preamble names: a rule stated
in prose and applied by hand is a rule that drifts. It is not hypothetical
here either. The palette decision that made lime #E1FF00 rather than the
export's #E0FF02 is written on two pages -- and eleven stop-colors under
prototypes/ still carry #E0FF02 today, one Figma paste away from a shipping
page. A stray paint renders correctly, looks approximately right, and diverges
the day the palette moves, which is the exact failure class this suite exists
for.

Measured on the day this gate was written, the fifteen pattern pages carry 726
paint attributes -- all on the five pages that draw -- and every single one
resolves: the contour ink, the two registers with the foundation trio, the
light family's four stops, and the structural values (none, currentColor,
url() indirection, var() pipes). Clean by hand, for now, on a surface nobody
re-counts. This is the thing that counts it.

WHAT IT CHECKS. In design-system/patterns/*.html, every fill=, stroke= and
stop-color= attribute (the three paint carriers the pages use; measured today
there is no flood-color, lighting-color, or paint inside a style="" attribute
-- the last is check-local-literals.py's surface anyway):

  structural   none, transparent, currentColor pass. url(#...) passes as
               indirection -- the gradient it points at is made of stop-color
               attributes read by this same pass, and its geometry is
               check-gradient-family.py's. A var() reference passes as a token
               pipe, unless its fallback smuggles a colour literal, which is
               the acts.css fallback fault (#300) on a new surface.

  hex          normalised (#000 == #000000, case-insensitive) and resolved
               against the register below. Anything with an alpha channel
               fails: no documented value carries one, and a translucent paint
               is an opacity decision hiding in a colour.

  anything     else -- a named colour, rgb()/hsl()/oklch(), a bare word --
               fails. There is no page-local colour decision on this site;
               check-local-literals.py holds that line for CSS and this file
               holds it for the markup.

THE REGISTER IS WRITTEN TWICE, and this script holds the two copies to each
other, the same defence check-breakpoints.py runs for thresholds. The palette
values here must each appear on foundations/illustration.html, where they are
documented with their meanings; the brand values are read out of tokens.css by
token name and compared. Re-tone a face on the foundations page and this copy
fails loudly instead of silently enforcing the old palette; retype a token and
the mismatch surfaces here rather than in a screenshot nobody takes.

SCOPE IS patterns/ ALONE, deliberately -- the same boundary check-registered.py
draws. foundations/, components/ and prototypes/ carry the same paint surface
(and prototypes/ carries the #E0FF02 strays, quarantined with the rest of that
page's open faults), but those sections belong to other lanes; a gate one lane
cannot fix red is a gate that teaches people to weaken gates. The scope
widens the day those surfaces are cleaned by their owners.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-paint-register.py
    python3 scripts/check-paint-register.py -v     # every paint, not only strays
"""

import argparse
import pathlib
import re
import sys
from collections import Counter
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
PATTERNS = DS / "patterns"
ILLUSTRATION = DS / "foundations" / "illustration.html"
TOKENS = DS / "assets" / "css" / "tokens.css"

# The drawing palette, exactly as foundations/illustration.html documents it.
# Every hex is normalised lowercase six-digit. The label is what the page says
# the value means -- it is printed with a finding so the fix names itself.
INK = {"#000000": "ink -- the contour is the drawing"}

REGISTER_1 = {
    "#dadada": "register 1: top, facing the sky",
    "#cfcfcf": "register 1: lit side -- CF-Grau itself",
    "#c4c4c4": "register 1: shaded side",
}

REGISTER_2 = {
    "#ffffff": "register 2: top, facing the sky",
    "#f6f6f6": "register 2: lit side",
    "#eaeaea": "register 2: shaded side",
    "#919191": "register 2: accent -- a slot, a recess",
    "#484848": "register 2: aperture -- never a whole face",
    "#fbfbfb": "register 2: foundation, one step under the machine",
    "#f0f0f0": "register 2: foundation, one step under the machine",
    "#e2e2e2": "register 2: foundation, one step under the machine",
}

# The light family's stops. Three are tokens and are read out of tokens.css by
# name below; the waypoint is the documented #DBFC60 literal whose POSITION
# and derivation check-gradient-family.py recomputes -- membership is all this
# file asks.
LIGHT_TOKENS = {"--lime-500": "#e1ff00", "--glas-500": "#c5ebe2", "--grey-300": "#cfcfcf"}
LIGHT_WAYPOINT = {"#dbfc60": "light family: the 19 % oklab waypoint"}

PAINT_ATTRS = ("fill", "stroke", "stop-color")

STRUCTURAL = {"none", "transparent", "currentcolor"}

# A value this script accepts although it is not on the register, keyed
# (page filename, raw value) -> the argument. Empty today; an entry needs the
# argument written here, in the one place the next reader will look.
EXEMPT = {}

# Any colour literal a var() fallback could smuggle -- hex or functional.
COLOUR_LITERAL = re.compile(
    r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color|color-mix)\s*\(",
)

HEX = re.compile(r"#([0-9a-fA-F]{3,8})\Z")


def register():
    """The full sanctioned set, hex -> label."""
    out = {}
    out.update(INK)
    out.update(REGISTER_1)
    out.update(REGISTER_2)
    for name, hexval in LIGHT_TOKENS.items():
        out[hexval] = "light family: var(%s)" % name
    out.update(LIGHT_WAYPOINT)
    return out


def normalise(raw):
    """A hex paint as lowercase six-digit, or None when it is not 3/6-digit.

    A 4- or 8-digit hex carries alpha and returns None on purpose: nothing on
    the register is translucent.
    """
    m = HEX.match(raw.strip())
    if not m:
        return None
    digits = m.group(1).lower()
    if len(digits) == 3:
        return "#" + "".join(c * 2 for c in digits)
    if len(digits) == 6:
        return "#" + digits
    return None


def classify(raw, sanctioned):
    """(ok, note). `note` names the value's standing either way."""
    value = raw.strip()
    lowered = value.lower()
    if lowered in STRUCTURAL:
        return True, "structural"
    if lowered.startswith("url("):
        return True, "indirection -- the stops it points at are read here too"
    if lowered.startswith("var("):
        smuggled = COLOUR_LITERAL.search(value)
        if smuggled:
            return False, ("a var() whose fallback carries %r -- a token pipe "
                           "with a literal poured in at the bottom. Drop the "
                           "fallback or make it a token." % smuggled.group(0))
        return True, "token pipe"
    hexval = normalise(value)
    if hexval is None:
        return False, ("%r is not on any register and not a form this gate can "
                       "resolve. Paint comes from the registers on "
                       "foundations/illustration.html; there is no page-local "
                       "colour decision on this site." % value)
    label = sanctioned.get(hexval)
    if label is None:
        return False, ("%s is not on the register. The registers on "
                       "foundations/illustration.html are the whole palette; "
                       "if this drawing genuinely needs a new value, the value "
                       "needs to be argued onto that page first." % value)
    return True, label


class PaintFinder(HTMLParser):
    """Every fill/stroke/stop-color attribute in a document, with its line.

    HTMLParser hands comments to handle_comment (unimplemented, so they are
    dropped) and escaped markup inside <pre>/<code> arrives as data, not tags
    -- so a paint quoted in documentation prose never reaches the gate.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hits = []  # (line, tag, attr, raw)

    def _record(self, tag, attrs):
        for attr, raw in attrs:
            if attr in PAINT_ATTRS and raw is not None:
                self.hits.append((self.getpos()[0], tag, attr, raw))

    def handle_starttag(self, tag, attrs):
        self._record(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._record(tag, attrs)


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), css, flags=re.S)


def double_entry():
    """Hold this file's copy of the register to the two documented copies.

    Palette values must appear on foundations/illustration.html, where each is
    documented with its meaning; token values are read out of tokens.css by
    name and compared. A mismatch is a finding against THIS file's copy -- the
    documentation moved and the gate did not.
    """
    findings = []

    doc = ILLUSTRATION.read_text(encoding="utf-8").lower()
    documented = {}
    documented.update(REGISTER_1)
    documented.update(REGISTER_2)
    documented.update(LIGHT_WAYPOINT)
    for hexval, label in sorted(documented.items()):
        if hexval not in doc:
            findings.append(("foundations/illustration.html", 0, hexval,
                             "this script's register carries %s (%s) and the "
                             "page no longer documents it. The palette moved; "
                             "move this copy with it." % (hexval, label)))

    css = strip_comments(TOKENS.read_text(encoding="utf-8"))
    for name, expected in sorted(LIGHT_TOKENS.items()):
        m = re.search(re.escape(name) + r"\s*:\s*([^;]+);", css)
        declared = normalise(m.group(1).strip()) if m else None
        if declared != expected:
            findings.append(("assets/css/tokens.css", 0, name,
                             "declares %r; this script's register carries %s. "
                             "The token moved; move this copy with it."
                             % (m.group(1).strip() if m else None, expected)))
    return findings


def audit():
    findings = double_entry()
    seen = []
    sanctioned = register()

    for path in sorted(PATTERNS.glob("*.html")):
        rel = path.relative_to(DS).as_posix()
        finder = PaintFinder()
        finder.feed(path.read_text(encoding="utf-8"))
        for line, tag, attr, raw in finder.hits:
            if (path.name, raw.strip()) in EXEMPT:
                seen.append((rel, line, tag, attr, raw, "exempt -- see EXEMPT"))
                continue
            ok, note = classify(raw, sanctioned)
            if ok:
                seen.append((rel, line, tag, attr, raw, note))
            else:
                findings.append((rel, line, "%s %s=" % (tag, attr), note))

    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every paint, not only the strays")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for rel, line, tag, attr, raw, note in seen:
            print("  %-28s %5d  %-8s %-10s %-28s %s"
                  % (rel[:28], line, tag, attr, raw[:28], note))
        print()

    if findings:
        for rel, line, what, why in findings:
            print("%s:%d  %s\n    %s" % (rel, line, what, why), file=sys.stderr)
        print("\n%d paint%s off the register. The palette is the two registers "
              "on foundations/illustration.html and the light family in "
              "tokens.css -- resolve each paint against those, or argue it "
              "onto the page first." % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    hexes = Counter()
    structural = 0
    for *_, raw, note in seen:
        h = normalise(raw)
        if h is None:
            structural += 1
        else:
            hexes[h] += 1
    census = ", ".join("%s x%d" % (h, n) for h, n in sorted(hexes.items()))
    print("paint register: %d paints across %d pattern pages, every one on the "
          "register -- %d structural, %s."
          % (len(seen), len(set(r for r, *_ in seen)), structural, census))
    return 0


if __name__ == "__main__":
    sys.exit(main())
