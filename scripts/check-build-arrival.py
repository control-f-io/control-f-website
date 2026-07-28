#!/usr/bin/env python3
"""A build happens where the eye is.

The rule of record used to say the opposite, in as many words, on
foundations/motion.html: "Everything is finished by the time the object reaches
the middle of the viewport, so the illustration is never caught half-built while
it is being read. The last range ends at cover 50 %, which is exactly that
moment." Every number in that sentence is right and the conclusion is backwards.
A reader who scrolls at reading pace meets a finished drawing, because the build
ran, in full, in the strip of viewport below where anyone looks.

THE ARITHMETIC THAT MAKES IT ONE SENTENCE AND NOT TWO. A `cover` range opens the
instant the element's first pixel crosses the viewport bottom and closes when its
last pixel leaves the top, so it spans `vh + h`; the element is centred at
`(h + vh) / 2` into that span. Both heights cancel: THE MOMENT A FIGURE SITS
CENTRED IS COVER 50 %, EXACTLY, AT EVERY VIEWPORT. So "ends by cover 50 %" and
"is over before it is looked at" say the same thing, and a range table can be
obeyed to the point while the page it describes fails the reader.

WHAT THIS CHECKS. For every assembly in the register below, the rendered state at
cover 50 % must be no more than 60 % complete. Two things about that make it a
check and not a restatement:

  THE RENDERED STATE, NOT THE FRACTION OF THE RANGE SPENT. These animations carry
  --ease-out, and an eased visual state runs ahead of its linear range position:
  a first retime of the statement figure put it two thirds through its window at
  the centred position and it still read 78 % built. So the timing function is
  resolved here — cubic-bezier, evaluated, out of tokens.css rather than assumed
  — and the number compared is the value the browser would paint.

  INK, NOT A MEAN OVER PARTS, wherever the assembly is a drawing. A mean over
  parts is a different quantity every time the drawing is redrawn. The landing
  page's flow was a bus of ten strokes and became a root of thirty-seven; the
  envelope that read 67 % of its ink at the centred position under the first
  geometry read 78 % under the second, and its unweighted part mean barely moved,
  because a 40-unit fringe twig and the 201-unit taproot count the same in a mean
  and do not count the same to an eye. Each stroke is weighted by its own length,
  taken from the `d` the markup ships.

The failure this is written against is not hypothetical and not old: it arrived
in an ordinary, correct change. The root that replaced the bus put 37 strokes at
a mean --l of 1.52 where ten had sat at 1.93, and the timing envelope it inherited
— `24 + 8l`, written for the bus — resolved five points earlier on a drawing that
takes longer to finish. Nothing rendered wrong at any single scroll position. The
drawing was simply done by the time it was looked at, which is the one thing
about this page that has now had to be said three times.

REGISTER, and what is deliberately not in it. Held: the landing page's two
entry-phase assemblies, the statement figure and the flow. Not held: the default
.cf-iso ranges in components.css — cover 5-30 / 20-40 / 18-45 / 30-48 / 35-50,
every one of them closing at or before cover 50 %. They are shared by every
pattern page, so retiming them is a change to the whole system rather than to one
page; the finding is recorded on foundations/motion.html#arrival instead of being
made quietly by whichever routine happened to be passing. When they are retimed,
they belong here.

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANDING = ROOT / "design-system/prototypes/statement-to-process.html"
COMPONENTS = ROOT / "design-system/assets/css/components.css"
TOKENS = ROOT / "design-system/assets/css/tokens.css"

# The one position the rule is about, and the ceiling it sets.
CENTRED = 50.0
CEILING = 0.60

# WHERE A HELD FIGURE FIRST SITS CENTRED, AND WHY IT IS NOT COVER 50 ANY MORE.
#
# The arithmetic at the top of this file is still exactly right — cover 50 % IS
# the centred position, at every viewport, by the definition of the cover range.
# What changed under it is that this page's statement no longer ARRIVES at that
# position: #219 gave it a hold, and a held figure reaches centre at the hold's
# OPEN and stands there, motionless, until cover 50 % releases it.
#
# So for the statement and its root, cover 50 % is not the moment the reader
# first looks at the drawing. It is the moment the drawing STOPS being looked
# at from one place — the end of the long still stretch, after the whole held
# build. Sampling there asks "how much was built during the hold?", and the
# answer to that is meant to be "nearly all of it": the hold exists to put the
# build where the eye is. Read at cover 50 the ceiling scores the cure as the
# disease, and it caps --lp-hold at about four points of extra reservation.
#
# The rule this file is about does not change one word. The MOMENT it is
# evaluated at does: a figure is sampled where it FIRST sits centred, which for
# an unheld assembly is cover 50 % and for a held one is the hold's opening.
# What that still catches, and it is the real regression, is a build whose head
# drifts EARLIER than the hold's open — ink laid down while the drawing is
# still climbing into view, below where anyone is looking, which is the exact
# fault the file was written against and is now reachable by moving one token.
#
# THE HOLD IN POINTS NEEDS A VIEWPORT AND THIS SCRIPT DOES NOT HAVE ONE.
# --lp-hold is authored in vh; the cover range is `100vh + the flow's own
# height`, and that height is a stretch between two anchors, so no stylesheet
# and no stdlib can resolve it. What CAN be pinned is the ratio between them,
# measured at the six viewports the gate admits and recorded in the rule's own
# note in landing-page.html — cover range over viewport height:
#
#     1024 x  720   1190.9 / 720  = 1.654      1440 x  900   1492.5 / 900  = 1.658
#     1280 x  800   1334.1 / 800  = 1.668      1920 x 1080   1842.5 / 1080 = 1.706
#     1366 x  768   1314.5 / 768  = 1.712      2560 x 1440   2382.5 / 1440 = 1.655
#
# RE-MEASURED AFTER #227. That commit shrank the drawing against its viewport,
# which is exactly the change the paragraph below says to re-measure for, and
# the row both files were reading — 1.725 / 1.747 / 1.800 / 1.738 / 1.772 /
# 1.704 — was 4 % wide of the page from the moment it landed. It is data about
# a rendered box, so it goes stale silently: nothing fails, the numbers derived
# from it are simply wrong. In check-hold-ramp.py it was wrong in the direction
# that kept invariant 6 passing, which is the worst direction available.
#
# A hold of H vh is therefore H / ratio points of cover, and the LARGEST ratio
# gives the FEWEST points, which opens the hold LATEST and so leaves the most
# build already run before it. That is the conservative end and it is the one
# taken here. Re-measure this table when the flow's height law changes; it is
# the same table the note carries, and it is data, not a claim about geometry.
COVER_RANGE_PER_VH = (1.654, 1.668, 1.712, 1.658, 1.706, 1.655)


def first_centred(text):
    """The cover position at which the held figure first sits centred.

    Returns (position, hold_source). Without a hold the answer is cover 50 %,
    which is what this file always assumed and is still right for anything that
    travels the whole way past the eye.
    """
    m = re.search(r"--lp-hold:\s*([\d.]+)vh\s*;", text)
    if m is None:
        return CENTRED, None
    hold_vh = float(m.group(1))
    # Fewest points -> latest opening -> most build already run.
    points = hold_vh / max(COVER_RANGE_PER_VH)
    return CENTRED - points, f"{hold_vh:g}vh"

# WHAT THE CEILING IS ON, and it is not every animation a figure runs.
#
#   BUILD      the drawing being constructed — the strokes, the ghosts, the
#              construction points. This is what "half-built while it is being
#              read" means and it is the only role the ceiling gates.
#   DELIVERY   the whole scene arriving in place (.cf-iso__scene's 26.57° slide).
#              A figure that is still visibly sliding when it is centred is a
#              worse fault than one that has landed, so the ceiling would be
#              exactly the wrong bound here. Measured and printed, not gated.
#   LEAD       a pass that is authored to run AHEAD of the drawing — the flow's
#              light is eight points of `cover` in front of its own contour by
#              construction, and pulling it under 60 % would mean pulling the
#              contour it leads back to about 20 %. Measured and printed.
#
# Both exemptions are roles, not names: a family gets one because of what it
# does in the assembly, and -v prints the number for all three so a drift in an
# ungated one is still visible to whoever is looking.
BUILD, DELIVERY, LEAD = "build", "delivery", "lead"


# ---------------------------------------------------------------- easing ----

def cubic_bezier(x1, y1, x2, y2):
    """The CSS timing function, as a callable. Bisection on X, then read Y.

    Precision is 1e-7 on the parameter, which is four orders finer than the
    0.60 this decides against — no root-finder subtlety is doing any work here.
    """
    def bx(s):
        return 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s ** 2 * x2 + s ** 3

    def by(s):
        return 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s ** 2 * y2 + s ** 3

    def f(t):
        if t <= 0:
            return 0.0
        if t >= 1:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if bx(mid) < t:
                lo = mid
            else:
                hi = mid
        return by((lo + hi) / 2)

    return f


LINEAR = lambda t: min(1.0, max(0.0, t))


def read_ease(name):
    """--ease-out and friends, out of tokens.css rather than out of memory."""
    text = TOKENS.read_text(encoding="utf-8")
    m = re.search(rf"--{re.escape(name)}:\s*cubic-bezier\(([^)]*)\)", text)
    if not m:
        return None
    try:
        a, b, c, d = (float(v) for v in m.group(1).split(","))
    except ValueError:
        return None
    return cubic_bezier(a, b, c, d)


# ------------------------------------------------------------- geometry ----

SEG_RE = re.compile(
    r"M\s*(-?[\d.]+)[ ,]+(-?[\d.]+)\s*(?:L\s*(-?[\d.]+)[ ,]+(-?[\d.]+)|V\s*(-?[\d.]+)|H\s*(-?[\d.]+))\s*$"
)


def path_length(d):
    """Every stroke in these drawings is one straight segment; assert it."""
    m = SEG_RE.match(d.strip())
    if not m:
        return None
    x1, y1 = float(m.group(1)), float(m.group(2))
    if m.group(3) is not None:
        x2, y2 = float(m.group(3)), float(m.group(4))
    elif m.group(5) is not None:
        x2, y2 = x1, float(m.group(5))
    else:
        x2, y2 = float(m.group(6)), y1
    return math.hypot(x2 - x1, y2 - y1)


# --------------------------------------------------------------- ranges ----

# A cover position resolves to (base, coefficient on --l, coefficient on --u).
# Four written forms, all of them shipping somewhere on the page:
#
#   cover A%                                   a literal
#   cover calc((A + var(--l) * C) * 1%)        a stagger with the constant typed
#   cover calc((A + var(--l) * var(--N)) * 1%) the same, with the constant named
#   cover calc((A + (var(--l) + var(--u)) * var(--N)) * 1%)
#                                              a window BOUGHT BY THE STROKE'S
#                                              OWN RUN — the flow's chain
#
# The fourth is why this parser is no longer two regexes. A window whose end
# reads (l + u)·c closes where its children's windows open, which is the whole
# of the flow's relay; a scanner that cannot see --u reports "not two cover
# positions" and measures nothing, which is a check that has stopped checking.
COVER_FLAT = re.compile(r"cover\s+([\d.]+)%$")
COVER_CALC = re.compile(
    r"cover\s+calc\(\(\s*([\d.]+)\s*\+\s*"
    r"(?:var\(--l\)|\(\s*var\(--l\)\s*\+\s*var\(--u\)\s*\))"
    r"\s*\*\s*(?:([\d.]+)|var\((--[\w-]+)\))\s*\)\s*\*\s*1%\)$")


def read_const(text, name):
    """The last declared value of a custom property, as a number."""
    v = None
    for m in re.finditer(re.escape(name) + r"\s*:\s*([\d.]+)\s*;", text):
        v = float(m.group(1))
    return v


def parse_cover_pair(decl, text=""):
    """The first two `cover` positions in an animation-range declaration.

    The calc() form nests TWO levels now — `calc((32 + (var(--l) + var(--u)) *
    var(--flow-c)) * 1%)` — so the scanner allows a bracketed group inside a
    bracketed group inside the outer one. It was written for one level, and one
    level stops at var(--l)'s own bracket and matches nothing, which is how this
    silently found no ranges at all the first time it was written.
    """
    hits = []
    group = r"(?:[^()]|\((?:[^()]|\([^()]*\))*\))*"
    for m in re.finditer(r"cover\s+(?:calc\(\(" + group + r"\)\s*\*\s*1%\)|[\d.]+%)", decl):
        frag = m.group(0)
        c = COVER_CALC.match(frag)
        if c:
            coef = float(c.group(2)) if c.group(2) else read_const(text, c.group(3))
            if coef is None:
                return []                      # a named constant that is not declared
            on_u = c.group(0).count("--u") > 0
            hits.append((float(c.group(1)), coef, coef if on_u else 0.0))
            continue
        f = COVER_FLAT.match(frag)
        if f:
            hits.append((float(f.group(1)), 0.0, 0.0))
    return hits


def rule_body(text, selector):
    """The declaration block of the LAST rule with this exact selector."""
    body = None
    for m in re.finditer(re.escape(selector) + r"\s*\{([^}]*)\}", text):
        body = m.group(1)
    return body


def progress(start, end, l, u, ease, at):
    """Rendered progress of one part at the moment its figure first sits centred.

    `start` and `end` are (base, --l coefficient, --u coefficient) triples, so
    a window bought by the stroke's own run resolves here rather than at four
    call sites. `at` is that moment in cover %, which is cover 50 for a figure
    that travels and the hold's opening for one that is held.
    """
    a = start[0] + start[1] * l + start[2] * u
    b = end[0] + end[1] * l + end[2] * u
    if b <= a:
        return None
    return ease(min(1.0, max(0.0, (at - a) / (b - a))))


# --------------------------------------------------------------- checks ----

def check_flow(findings, verbose, at):
    """The root: contour ink, the light's own draw, and the junctions."""
    text = LANDING.read_text(encoding="utf-8")
    parts = {
        "lp-flow__seg": ("the contour", True, BUILD),
        "lp-flow__light": ("the light", True, LEAD),
        "lp-flow__node": ("the junctions", False, BUILD),
    }
    results = []
    for cls, (label, weighted, role) in parts.items():
        body = rule_body(text, f".{cls}")
        if body is None:
            findings.append(f"flow: no rule for .{cls} — the selector went stale")
            continue
        if "linear" not in body:
            findings.append(
                f"flow: .{cls} is not linear — scroll position IS this draw, so the "
                f"grammar says linear (foundations/motion.html)"
            )
        decl = re.search(r"animation-range:([^;]*);", body)
        if not decl:
            findings.append(f"flow: .{cls} has no animation-range")
            continue
        pairs = parse_cover_pair(decl.group(1), text)
        if len(pairs) < 2:
            findings.append(f"flow: .{cls}'s animation-range is not two cover positions")
            continue
        a, b = pairs[0], pairs[1]

        # every element carrying this class, with its --l and its own `d`.
        # Whole tag first, attributes second: an optional group inside one
        # regex happily matches nothing and reports 37 paths with no geometry.
        elems = []
        for tag in re.findall(rf'<(?:path|circle)\s+class="{cls}"[^>]*?/>', text):
            style = re.search(r'style="([^"]*)"', tag)
            d = re.search(r'\sd="([^"]*)"', tag)
            elems.append((style.group(1) if style else "", d.group(1) if d else ""))
        drawn = total = 0.0
        n = 0
        for style, d in elems:
            lm = re.search(r"--l:\s*([\d.]+)", style)
            if not lm:
                findings.append(f"flow: a .{cls} carries no --l")
                continue
            l = float(lm.group(1))
            um = re.search(r"--u:\s*([\d.]+)", style)
            if um is None and (a[2] or b[2]):
                findings.append(f"flow: .{cls}'s window is bought by --u and a part carries none")
                continue
            u = float(um.group(1)) if um else 0.0
            w = 1.0
            if weighted:
                w = path_length(d) if d else None
                if w is None:
                    findings.append(f"flow: a .{cls} has a `d` this check cannot measure: {d!r}")
                    continue
            p = progress(a, b, l, u, LINEAR, at)
            if p is None:
                findings.append(f"flow: .{cls}'s window ends before it starts at --l {l}")
                continue
            drawn += w * p
            total += w
            n += 1
        if not total:
            findings.append(f"flow: no .{cls} elements found in the markup")
            continue
        results.append((label, cls, drawn / total, n, role))

    for label, cls, f, n, role in results:
        if verbose:
            print(f"  flow · {label:14} ({cls}, {n} parts): {f * 100:5.1f} % at cover {at:.2f}  [{role}]")
        if role is not BUILD:
            continue
        if f > CEILING:
            findings.append(
                f"flow: {label} reads {f * 100:.1f} % complete at the moment the drawing "
                f"FIRST sits centred (cover {at:.2f} %), over the {CEILING * 100:.0f} % ceiling — "
                f"re-anchor the window later (foundations/motion.html#arrival)"
            )
    return results


def check_statement(findings, verbose, at):
    """The statement figure: parts that fade, so a mean over parts is the measure."""
    css = COMPONENTS.read_text(encoding="utf-8")
    html = LANDING.read_text(encoding="utf-8")
    ease = read_ease("ease-out")
    if ease is None:
        findings.append("statement: --ease-out is not a cubic-bezier in tokens.css")
        return []
    figure = html
    m = re.search(r'<svg class="cf-iso"[^>]*>(.*?)</svg>', html, re.S)
    if m:
        figure = m.group(1)
    families = {
        ".cf-statement .cf-iso__scene": ("cf-iso__scene", DELIVERY),
        ".cf-statement .cf-iso__ghost": ("cf-iso__ghost", BUILD),
    }
    results = []
    for selector, (cls, role) in families.items():
        body = rule_body(css, selector)
        if body is None:
            findings.append(f"statement: no rule for `{selector}` — the selector went stale")
            continue
        decl = re.search(r"animation-range:([^;]*);", body)
        if not decl:
            findings.append(f"statement: `{selector}` has no animation-range")
            continue
        pairs = parse_cover_pair(decl.group(1), css)
        if len(pairs) < 2:
            findings.append(f"statement: `{selector}`'s first range is not two cover positions")
            continue
        a, b = pairs[0], pairs[1]
        n = len(re.findall(rf'class="{cls}"', figure)) or 1
        p = progress(a, b, 0.0, 0.0, ease, at)
        results.append((cls, p, n, a[0], b[0], role))

    for cls, p, n, a, b, role in results:
        if verbose:
            print(f"  statement · {cls:16} (cover {a:g}-{b:g}, {n} parts): "
                  f"{p * 100:5.1f} % at cover {at:.2f}  [{role}]")
        if role is not BUILD:
            continue
        if p > CEILING:
            findings.append(
                f"statement figure: .{cls} reads {p * 100:.1f} % complete at the moment the "
                f"figure FIRST sits centred (cover {at:.2f} %), over the {CEILING * 100:.0f} % ceiling — "
                f"re-anchor the window later (foundations/motion.html#arrival)"
            )
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Every assembly must still be running when its figure is centred.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the rendered state of every family at that moment")
    args = parser.parse_args()

    findings = []
    at, hold = first_centred(LANDING.read_text(encoding="utf-8"))
    if args.verbose:
        where = (f"cover {at:.2f} % — the opening of a {hold} hold, where the figure "
                 f"FIRST sits centred" if hold else
                 f"cover {at:g} % — the moment a figure sits centred")
        print(f"build arrival, at {where}:")
    flow = check_flow(findings, args.verbose, at)
    stmt = check_statement(findings, args.verbose, at)

    if not flow or not stmt:
        findings.append("nothing was measured — the register no longer matches the tree")

    if findings:
        print(f"\nbuild arrival: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    gated = ([f for _, _, f, _, role in flow if role is BUILD]
             + [p for _, p, _, _, _, role in stmt if role is BUILD])
    print(f"build arrival OK — {len(flow) + len(stmt)} families across 2 assemblies, "
          f"{len(gated)} of them the build itself and none over {CEILING * 100:.0f} % "
          f"at cover {at:.2f} %, where the figure first sits centred; "
          f"worst is {max(gated) * 100:.1f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
