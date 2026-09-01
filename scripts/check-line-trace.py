#!/usr/bin/env python3
"""A line chart's drawing and its numbers are the same data. Prove it.

Every other figure in this system has exactly one copy of what it says.
`.cf-plot` puts the value on the column as `--v` and the drawing reads it, so
the number a reader takes off the picture and the height of the picture cannot
disagree — there is nothing to disagree with. `.cf-line` could not reach that,
and the component's own page says where it stops: SVG cannot read a custom
property off an `<li>`, and the CSS construction that would avoid the second
copy — a chain of rotated hairlines sized with `hypot()` and turned with
`atan2()` — has no fallback that is still a chart on an engine without CSS
trigonometry. The component's first law is that every fallback is the finished
chart, so the second copy stays and this file is what holds it.

WHAT THE TWO COPIES ARE. The drawing is one `<polyline class="cf-line__trace">`
in a `viewBox="0 0 100 100"` with `preserveAspectRatio="none"`. The data is one
`<ol class="cf-line__set">` whose items carry `--t` and `--v`. The mapping is
deliberately the identity so that a person can check a figure by eye as well:

    x == --t * 100                 y == (1 - --v) * 100

WHAT DRIFT LOOKS LIKE, and it is the reason this is a script. A label a few
pixels off its own line looks like a label. A trace drawn from last quarter's
numbers under this quarter's printed values looks like a chart. Neither renders
wrong, neither shows up in a screenshot diff that a person would read as a
fault, and the figure is at its most convincing exactly when it is worst — the
numbers are crisp, the line is smooth, and they are about different data.

THE FIVE RULES.

  PAIRING     A figure's n-th `.cf-line__set` is the n-th `.cf-line__trace`, in
              document order, and the two counts are equal. A set with no trace
              is a series nobody drew; a trace with no set is a line carrying no
              data and no accessible text at all.

  AGREEMENT   Point i of a set is vertex i of its trace, to 0.05 user units —
              a twentieth of one percent of the frame, which is under a device
              pixel at every width the frame is ever given and far inside what
              hand-authored decimals need.

  SPAN        The first point sits at `--t: 0` and the last at `--t: 1`. The
              domain is the frame; a series that stops at 0.9 has drawn itself
              a margin the reader will read as data ending early.

  ORDER       `--t` never goes backwards. An `<ol>` whose order does not match
              the domain reads correctly to the eye and wrongly to everything
              that consumes the list as a series.

  RANGE       `--t` and `--v` are both inside 0..1. Both are registered
              `<number>`, which rejects a unit but not a 4 or a -1, and the CSS
              clamps on top of that — so an out-of-range value is drawn at the
              frame's edge while the polyline, which nothing clamps, is drawn
              wherever it was typed. That is the one way these two halves can
              disagree while both look deliberate.

WHAT IT DOES NOT CLAIM. Not that a printed value matches its own `--v`: "84 %"
against `--v: .84` holds only while the frame runs 0 to 100, and the frame is
free — that is the whole point of `.cf-line__bounds`. The text a reader reads
and the number that places it are two different facts and only a human knows
the scale between them. This holds the half that is arithmetic.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-line-trace.py
    python3 scripts/check-line-trace.py -v     # every figure, not only strays
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# The drawing's own units. The viewBox is 0 0 100 100 and preserveAspectRatio
# is none, so one unit is one hundredth of the frame on both axes whatever the
# frame's ratio is.
SPAN = 100.0

# Half a twentieth of a percent of the frame. At --line-max (640 px) that is
# 0.32 px on the x and 0.16 px on the y; below it, less.
TOL = 0.05

# The designer's own material is not ours to hold to our rules — same boundary
# scripts/check-line-types.py draws, for the same reason.
SKIP_DIRS = {"source"}

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def numbers(text):
    """Every number in a `points` attribute, commas and spaces both separators."""
    return [float(m) for m in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", text or "")]


def custom_props(style):
    """`--t` and `--v` off a style attribute, as floats where they parse."""
    out = {}
    for name, raw in re.findall(r"(--[a-z-]+)\s*:\s*([^;]+)", style or "", re.I):
        value = raw.strip()
        try:
            out[name] = float(value)
        except ValueError:
            out[name] = value
    return out


class Figures(HTMLParser):
    """Every .cf-line in a document: its traces and its sets, in order.

    Nesting is not modelled and does not need to be — a figure inside a figure
    is not a shape this component has, and the parser closes each .cf-line at
    the tag depth it opened on.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.figures = []       # {line, traces: [...], sets: [...]}
        self.open_at = None     # depth the current .cf-line opened on
        self.set = None         # the set being filled

    # -- helpers ----------------------------------------------------------
    @property
    def current(self):
        return self.figures[-1] if self.open_at is not None else None

    def _start(self, tag, attrs):
        classes = set((attrs.get("class") or "").split())
        line = self.getpos()[0]

        if "cf-line" in classes and self.open_at is None:
            self.figures.append({"line": line, "traces": [], "sets": []})
            self.open_at = self.depth

        fig = self.current
        if fig is None:
            return

        if "cf-line__trace" in classes:
            fig["traces"].append({"line": line, "points": numbers(attrs.get("points"))})

        if "cf-line__set" in classes:
            self.set = {"line": line, "points": []}
            fig["sets"].append(self.set)

        if "cf-line__point" in classes and self.set is not None:
            props = custom_props(attrs.get("style"))
            self.set["points"].append({"line": line,
                                       "t": props.get("--t"),
                                       "v": props.get("--v")})

    # -- HTMLParser -------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        self._start(tag, dict(attrs))
        if tag not in VOID:
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        self._start(tag, dict(attrs))

    def handle_endtag(self, tag):
        self.depth = max(0, self.depth - 1)
        if self.open_at is not None and self.depth <= self.open_at:
            self.open_at = None
            self.set = None


def check_figure(rel, fig, findings, seen):
    at = lambda line: (rel, line)

    if len(fig["traces"]) != len(fig["sets"]):
        findings.append((rel, fig["line"],
                         "%d trace%s against %d set%s"
                         % (len(fig["traces"]), "" if len(fig["traces"]) == 1 else "s",
                            len(fig["sets"]), "" if len(fig["sets"]) == 1 else "s"),
                         "Every series is drawn once and written once. A set with no "
                         "trace is a series nobody drew; a trace with no set is a line "
                         "with no numbers behind it."))
        return

    if not fig["traces"]:
        findings.append((rel, fig["line"], "no trace and no set",
                         "A .cf-line with nothing in it is a frame."))
        return

    for trace, series in zip(fig["traces"], fig["sets"]):
        coords, points = trace["points"], series["points"]

        if len(coords) % 2:
            findings.append((rel, trace["line"], "%d numbers in points" % len(coords),
                             "A points list is pairs."))
            continue

        vertices = list(zip(coords[0::2], coords[1::2]))
        if len(vertices) != len(points):
            findings.append((rel, trace["line"],
                             "%d vertices against %d points" % (len(vertices), len(points)),
                             "Point i of the set is vertex i of its trace. The two "
                             "halves are the same series or they are two series."))
            continue

        last_t = None
        for index, (point, (x, y)) in enumerate(zip(points, vertices)):
            t, v = point["t"], point["v"]

            if not isinstance(t, float) or not isinstance(v, float):
                findings.append((rel, point["line"], "point %d" % index,
                                 "carries --t=%r --v=%r. Both are registered <number>: "
                                 "a unit or a percentage here resolves to the initial 0 "
                                 "and stacks the point in the frame's corner."
                                 % (t, v)))
                continue

            if not (0.0 <= t <= 1.0) or not (0.0 <= v <= 1.0):
                findings.append((rel, point["line"], "point %d" % index,
                                 "--t %g / --v %g is outside 0..1. The CSS clamps and "
                                 "the polyline does not, so the label and its own "
                                 "vertex part company while both look deliberate."
                                 % (t, v)))
                continue

            if last_t is not None and t < last_t - 1e-9:
                findings.append((rel, point["line"], "point %d" % index,
                                 "--t %g follows %g. The domain does not go backwards."
                                 % (t, last_t)))
            last_t = t

            want = (t * SPAN, (1.0 - v) * SPAN)
            if abs(x - want[0]) > TOL or abs(y - want[1]) > TOL:
                findings.append((rel, trace["line"], "vertex %d" % index,
                                 "is %g,%g; --t %g / --v %g on line %d places it at "
                                 "%g,%g. x is --t x 100 and y is (1 - --v) x 100."
                                 % (x, y, t, v, point["line"], want[0], want[1])))

        if points:
            first, last = points[0], points[-1]
            if isinstance(first["t"], float) and abs(first["t"]) > TOL / SPAN:
                findings.append((rel, first["line"], "the first point",
                                 "sits at --t %g. The domain is the frame: the series "
                                 "starts at 0." % first["t"]))
            if isinstance(last["t"], float) and abs(last["t"] - 1.0) > TOL / SPAN:
                findings.append((rel, last["line"], "the last point",
                                 "sits at --t %g. The domain is the frame: the series "
                                 "ends at 1." % last["t"]))

        seen.append((rel, trace["line"], len(vertices)))


def pages():
    for path in sorted(DS.rglob("*.html")):
        if SKIP_DIRS & set(p.name for p in path.parents):
            continue
        yield path


def audit():
    findings, seen = [], []
    for path in pages():
        text = path.read_text(encoding="utf-8")
        if "cf-line__trace" not in text and "cf-line__set" not in text:
            continue
        rel = path.relative_to(DS).as_posix()
        parser = Figures()
        parser.feed(text)
        for fig in parser.figures:
            check_figure(rel, fig, findings, seen)
    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every series, not only the strays")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for rel, line, count in seen:
            print("  %-46s %5d  %3d points" % (rel[:46], line, count))
        print()

    if findings:
        for rel, line, what, why in findings:
            print("%s:%d  %s\n    %s" % (rel, line, what, why), file=sys.stderr)
        print("\n%d series where the drawing and its numbers disagree. The picture is "
              "the data or it is decoration -- see components/line.html, \"the one "
              "seam\"." % len(findings), file=sys.stderr)
        return 1

    total = sum(count for *_, count in seen)
    print("line trace: %d series, %d points, every vertex on its own number."
          % (len(seen), total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
