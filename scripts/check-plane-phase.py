#!/usr/bin/env python3
"""Hold .cf-plot--ground's ground to the phase that puts a column on a crossing.

The subject is a half of one unit, and like the pie's running sum it is a number
the drawing cannot show you is wrong. A zero plane whose lattice is out by half
a cell is a lattice: every diamond closes, the band tiles seamlessly, the
columns stand at the right heights, and the one thing that is wrong -- that the
verticals leave the ground between its lines instead of at them -- reads as
"something about this looks odd" and nothing more. It was shipped once and found
by eye, not by rule.

    python3 scripts/check-plane-phase.py        # check, exit 1 on a finding
    python3 scripts/check-plane-phase.py -v     # show the arithmetic

THE ARITHMETIC. The plane is .cf-ground's material at the plot's own scale: the
field unit is 2u, so --field-step is 2u/sqrt(5) and one diamond is 2u wide and
1u tall -- exactly a column's footprint. The band is 2u tall and the zero line
is its middle, y = 1u in the band's own box.

A CSS repeating gradient anchors its period at the STARTING CORNER of the box,
not at its centre, and the stops put the ink half a step into each period. With
H = 2u that places the two families at

    A  (start corner bottom-left)   y =  0.5x + (1.5u - k*u)
    B  (start corner top-left)      y = -0.5x + (0.5u + m*u)

which cross wherever both hold: x = n*u and y = -0.5*n*u + 0.5u + m*u, for
integer n, m.

A column's footprint is the rhombus with vertices

    left (4i)u, 1u      near (4i+1)u, 1.5u
    right (4i+2)u, 1u   far  (4i+1)u, 0.5u

and the rule is simply that all four of those are crossings. Unshifted, none of
them is -- every one lands half a cell out, at a diamond's centre. Shifted down
by --plane-phase all four solve at once, and the footprint becomes a cell of the
ground rather than a shape laid over it. The lattice is periodic in y with
period u and the band is 2u, so the shift wraps seamlessly and costs nothing at
the band's edges.

The check reads the phase out of components.css rather than trusting it, and
re-solves the four vertices for the first three columns.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css" / "components.css"

# The rule this file is about, located by its selector rather than by line.
BLOCK = re.compile(r"\.cf-plot--ground\s+\.cf-plot__set::before\s*\{(.*?)\n\}", re.S)


def decl(body, prop):
    m = re.search(r"(?<![-\w])%s:\s*([^;]+);" % re.escape(prop), body)
    return m.group(1).strip() if m else None


def u_multiple(value, what):
    """Read `calc(var(--plot-u) * k)` or `0` and return k."""
    if value is None:
        return None
    if value.strip() in ("0", "0px"):
        return 0.0
    m = re.search(r"var\(--plot-u\)\s*\*\s*([0-9.]+)", value)
    if m:
        return float(m.group(1))
    m = re.search(r"([0-9.]+)\s*\*\s*var\(--plot-u\)", value)
    if m:
        return float(m.group(1))
    m = re.search(r"var\(--plot-u\)\s*/\s*([0-9.]+)", value)
    if m:
        return 1.0 / float(m.group(1))
    return None


def crossings(n, shift, lo=-0.01, hi=None):
    """Every lattice crossing at x = n*u inside the band, after `shift`."""
    hi = 2.0 + 0.01 if hi is None else hi
    out = []
    for m in range(-4, 8):
        y = -0.5 * n + 0.5 + m + shift
        if lo <= y <= hi:
            out.append(round(y, 6))
    return sorted(out)


def on_crossing(n, y, shift):
    return any(abs(c - y) < 1e-9 for c in crossings(n, shift))


def main():
    verbose = "-v" in sys.argv
    if not CSS.exists():
        print("check-plane-phase: %s not found" % CSS, file=sys.stderr)
        return 1

    css = CSS.read_text(encoding="utf-8")
    m = BLOCK.search(css)
    if not m:
        print("check-plane-phase: no .cf-plot--ground .cf-plot__set::before rule; "
              "the zero plane this checks is gone or renamed.", file=sys.stderr)
        return 1
    body = m.group(1)
    line_of = css[: m.start()].count("\n") + 1

    findings = []

    height = u_multiple(decl(body, "height"), "height")
    if height != 2.0:
        findings.append("the band is %s, not 2u — the family offsets below are "
                        "derived from H = 2u and do not hold at another height."
                        % (decl(body, "height"),))

    unit = u_multiple(decl(body, "--field-unit"), "--field-unit")
    if unit != 2.0:
        findings.append("--field-unit is %s, not 2u — one diamond is then not "
                        "one column's footprint." % (decl(body, "--field-unit"),))

    step = decl(body, "--field-step")
    if step is None or "2.2360679775" not in step:
        findings.append("--field-step is %s — it must be the unit over sqrt(5), "
                        "which is what makes the rake 2:1." % (step,))

    pos = decl(body, "background-position")
    if pos is None:
        findings.append("no background-position: the ground is unshifted, so every "
                        "column leaves it from the middle of a cell.")
        shift = 0.0
    else:
        parts = pos.split(None, 1)
        shift = u_multiple(parts[1] if len(parts) > 1 else None, "background-position")
        if shift is None:
            findings.append("background-position %r is not a multiple of --plot-u; "
                            "this check cannot solve it." % pos)
            shift = 0.0

    # The four vertices of the footprint, for the first three columns.
    checked = 0
    if not findings or shift is not None:
        for i in range(3):
            for n, y, name in ((4 * i, 1.0, "left"),
                               (4 * i + 1, 1.5, "near"),
                               (4 * i + 2, 1.0, "right"),
                               (4 * i + 1, 0.5, "far")):
                checked += 1
                if not on_crossing(n, y, shift or 0.0):
                    findings.append(
                        "column %d's %s vertex at x=%gu y=%gu is not a crossing "
                        "(crossings there: %s) — it sits at a cell centre, so the "
                        "vertical leaves the ground between the lattice's lines."
                        % (i, name, n, y, crossings(n, shift or 0.0)))
                if verbose:
                    print("  col %d %-5s  x=%2gu y=%.1fu  crossings %s"
                          % (i, name, n, y, crossings(n, shift or 0.0)))

    if findings:
        for note in findings:
            print("%s:%d\n    %s" % (CSS.relative_to(ROOT), line_of, note),
                  file=sys.stderr)
        print("\n%d finding%s. A plane half a cell out of phase still tiles, still "
              "closes and still measures — which is why this is solved rather than "
              "looked at." % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    print("plane phase: band 2u, field unit 2u, ground shifted %gu — %d footprint "
          "vertices re-solved, every one on a lattice crossing." % (shift, checked))
    return 0


if __name__ == "__main__":
    sys.exit(main())
