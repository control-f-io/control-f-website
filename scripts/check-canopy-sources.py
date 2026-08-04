#!/usr/bin/env python3
"""One bead per unique leaf end, nowhere else, at a size the tightest pair holds.

WHAT THE LAYER IS. The flow tier draws one moment of act 1/2 — the finished
root — and .lp-flow-sources is how that tier still tells the story's subject:
one sensor bead per unique canopy entry, standing at the far end of the leaf
stroke that carries its readings down. The markup argues the composition
(patterns/landing-page.html, THE SOURCES); acts.css argues size, gate and
light. This check holds the three numbers neither prose can be trusted with.

  1. THE SET. Every leaf path ends on the canopy line, and the beads must be
     exactly the unique far ends of those paths: one bead per point, no bead
     anywhere else, no point left dark. Both sides are read from the shipped
     markup — the d attributes on one side, the --x custom properties on the
     other — so a leaf added, moved or removed without its bead is a finding,
     and so is a bead typed at a coordinate no stroke earns. The far-end y
     must be ONE value across all leaves, and the CSS top formula must place
     the row at exactly that value: a canopy is a line, not a scatter.

  2. THE LAW. The two tightest entries stand a fixed number of viewBox units
     apart. At the container floor where the layer first shows, that gap in
     CSS pixels must hold the bead's rendered diameter plus one pixel of air —
     two instruments that touch are one smudge. The floor, the clamp and the
     gap are all re-derived: the floor from the @container prelude, the
     diameter from --src-d's clamp() at that floor, the gap from the shipped
     paths. Above the floor the gap grows linearly while the clamp caps, so
     proving the floor proves every admitted width.

  3. THE GATE IS A REGISTER RUNG. The floor must be a threshold the breakpoint
     register in tokens.css already names — the layer is a second consumer of
     an existing rung, not a new row. (Which rung is not pinned here: if the
     law and the register both admit a lower one, moving is allowed; inventing
     44.5rem is not.)

The tier logic — drawn outside the pin gate, withdrawn inside it — is
check-act-moment.py's and is deliberately not restated here.

stdlib only, no build step, no dependency — the same contract as the checks
beside it.

    python3 scripts/check-canopy-sources.py       # check, exit 1 on a finding
    python3 scripts/check-canopy-sources.py -v    # print the set, the law, the rung
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
PAGE = DS / "patterns" / "landing-page.html"
ACTS = DS / "assets" / "css" / "acts.css"
TOKENS = DS / "assets" / "css" / "tokens.css"

AIR = 1.0          # px between the tightest pair's bodies at the floor
VIEWBOX_W = 1200.0


def leaf_far_ends(markup):
    """(unique xs, the single shared y) of every lp-flow__leaf far end."""
    ends = []
    for d in re.findall(
            r'class="lp-flow__light lp-flow__leaf"[^>]*\bd="([^"]+)"', markup):
        m = re.match(r"M([\d.]+) ([\d.]+)(?:V([\d.]+)|L([\d.]+) ([\d.]+))$", d)
        if not m:
            return None, ("leaf path %r is not the M…V / M…L shape every "
                          "leaf has carried; teach this check the new shape "
                          "before shipping it" % d)
        if m.group(3):
            ends.append((float(m.group(1)), float(m.group(3))))
        else:
            ends.append((float(m.group(4)), float(m.group(5))))
    ys = {y for _, y in ends}
    if len(ys) != 1:
        return None, ("the leaves end at %d different y values (%s) — the "
                      "canopy is no longer a line and the sources row cannot "
                      "be placed with one top formula"
                      % (len(ys), sorted(ys)))
    return (sorted({x for x, _ in ends}), ys.pop()), None


def bead_xs(markup):
    block = re.search(
        r'<div class="lp-flow-sources"[^>]*>(.*?)</div>', markup, re.S)
    if not block:
        return None
    return sorted(float(m) for m in
                  re.findall(r'class="lp-flow__src" style="--x:([\d.]+)"',
                             block.group(1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    markup = PAGE.read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", ACTS.read_text(encoding="utf-8"), flags=re.S)
    findings = []

    # ---- 1. the set ----
    got, err = leaf_far_ends(markup)
    if err:
        print("canopy-sources: 1 finding\n  - " + err)
        return 1
    xs, y = got
    beads = bead_xs(markup)
    if beads is None:
        findings.append(".lp-flow-sources is not in the markup. The flow "
                        "tier's sensors are this layer; without it the tier "
                        "is a tree with no subject again.")
        beads = []
    missing = [x for x in xs if x not in beads]
    extra = [x for x in beads if x not in xs]
    dupes = sorted({x for x in beads if beads.count(x) > 1})
    for x in missing:
        findings.append("the entry at x=%g has no bead: a leaf's readings "
                        "enter at a point this layer leaves dark." % x)
    for x in extra:
        findings.append("the bead at x=%g stands at no leaf's far end — a "
                        "typed coordinate, which is the drift this check "
                        "exists to refuse." % x)
    for x in dupes:
        findings.append("x=%g carries more than one bead; a sensor is a "
                        "place, and this place has two." % x)

    m = re.search(r"\.lp-flow__src\s*\{[^}]*top:\s*calc\(([\d.]+)\s*/\s*620\s*\*\s*100%\)",
                  css)
    if not m:
        findings.append(".lp-flow__src's top is not `calc(<y> / 620 * 100%)` "
                        "— the row must be placed by the canopy's own value.")
    elif float(m.group(1)) != y:
        findings.append("the CSS places the row at y=%s and the leaves end at "
                        "y=%g — the beads float off the line their strokes "
                        "end on." % (m.group(1), y))

    # ---- 2. the law ----
    gaps = [b - a for a, b in zip(xs, xs[1:])]
    min_gap = min(gaps)
    pair = min(zip(xs, xs[1:]), key=lambda p: p[1] - p[0])

    clamp = re.search(
        r"--src-d:\s*clamp\(\s*([\d.]+)px\s*,\s*([\d.]+)cqi\s*,\s*([\d.]+)px\s*\)",
        css)
    gates = re.findall(
        r"@container sp-root \(min-width:\s*([\d.]+)rem\)\s*\{\s*"
        r"\.lp-flow-sources\s*\{\s*display:\s*block", css)
    if len(gates) > 1:
        findings.append(
            "the layer has %d `@container sp-root (min-width: …rem)` show "
            "rules (%s). One gate is the law; a second, lower one shows the "
            "beads below the floor the first was solved at, and this check "
            "would have validated only the first it found."
            % (len(gates), ", ".join(g + "rem" for g in gates)))
    gate = re.match(r"(.*)", gates[0]) if gates else None
    if gates:
        class _G:  # keep the .group(1) shape the code below reads
            def __init__(self, v): self._v = v
            def group(self, _): return self._v
        gate = _G(min(gates, key=float))
    if not clamp:
        findings.append("--src-d is not a clamp(<px>, <cqi>, <px>) on "
                        ".lp-flow__src; the law below has nothing to hold.")
    if not gate:
        findings.append(".lp-flow-sources has no `@container sp-root "
                        "(min-width: …rem) { display: block }` gate; below "
                        "some width the tightest pair cannot hold a bead, and "
                        "nothing says where that is.")
    if clamp and gate:
        floor_px = float(gate.group(1)) * 16
        lo, slope, hi = (float(g) for g in clamp.groups())
        bead_at_floor = max(lo, min(hi, slope * floor_px / 100))
        gap_at_floor = min_gap * floor_px / VIEWBOX_W
        if bead_at_floor + AIR > gap_at_floor:
            findings.append(
                "at the %srem floor the tightest pair (x=%g and x=%g, %g "
                "units) offers %.2fpx of gap and the bead renders %.2fpx — "
                "%.2fpx short of a body and %.0fpx of air. Raise the floor, "
                "lower the clamp, or re-derive both."
                % (gate.group(1), pair[0], pair[1], min_gap, gap_at_floor,
                   bead_at_floor, bead_at_floor + AIR - gap_at_floor, AIR))
        # ---- 3. the rung ----
        register = TOKENS.read_text(encoding="utf-8")
        rung = re.search(r"^\s+%s\s*rem\s*/\s*\d+" % re.escape(gate.group(1)),
                         register, re.M)
        if not rung:
            findings.append(
                "the %srem floor is not a row of tokens.css's breakpoint "
                "register. The layer must consume an existing rung — see the "
                "register's own preamble for why a private threshold is a "
                "fork." % gate.group(1))

    if args.verbose:
        print("  %d entries at y=%g, min gap %g units (x=%g and x=%g)"
              % (len(xs), y, min_gap, pair[0], pair[1]))
        if clamp and gate:
            print("  floor %srem: gap %.2fpx, bead %.2fpx, air %.2fpx"
                  % (gate.group(1), gap_at_floor, bead_at_floor,
                     gap_at_floor - bead_at_floor))

    if findings:
        print("canopy-sources: %d finding%s"
              % (len(findings), "" if len(findings) == 1 else "s"))
        for f in findings:
            print("  - " + f)
        return 1

    print("canopy-sources OK — %d beads at the %d unique leaf ends on y=%g; "
          "at the %srem floor the tightest pair holds the bead with %.2fpx "
          "of air." % (len(beads), len(xs), y, gate.group(1),
                       gap_at_floor - bead_at_floor))
    return 0


if __name__ == "__main__":
    sys.exit(main())
