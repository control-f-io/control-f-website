#!/usr/bin/env python3
"""Re-add every .cf-pie in the tree and hold it to the arithmetic it claims.

The hundred and twenty-fourth check, and the first whose subject is a number a
drawing cannot show.

A pie states two numbers per share and neither of them is checkable by looking.
`--v` is the share; `--turn` is where the share starts, which is the running sum
of every `--v` before it. CSS cannot take that sum -- it cannot see a preceding
sibling's value -- so the author writes it out, and an author writing a running
sum by hand is an author who will one day write .72 for .73.

WHAT THAT FAILURE LOOKS LIKE, and it is the reason this is a script rather than
a review note: nothing. A ring whose cuts are one per cent out of step is a ring.
Every contour still closes, every label still stands against an arc, the figure
still renders at every width and prints correctly, and the one thing that is
wrong -- which arc belongs to which number -- is the one thing a drawing of a
circle cannot tell you. The same is true of shares that come to 99 %: the last
cut simply lands a degree short of the first, on a ring that is 360 degrees
round and forgiving to the eye at every one of them.

    python3 scripts/check-pie-shares.py        # check, exit 1 on a finding
    python3 scripts/check-pie-shares.py -v     # print every figure it re-added

THE FIVE RULES, and each is a rule the component's own page states.

  1. THE RUNNING SUM. Share n's --turn is the sum of every --v before it. The
     first share starts at 0, which is 12 o'clock and --angle-square.
  2. THE WHOLE. The shares come to 1. A pie draws parts OF something, and the
     total in the hole is a claim about them: shares that do not add up make the
     figure's own centre a lie.
  3. THE CEILING. Three to five shares. Five is where the labels stop clearing
     each other on a 375 px screen, and it is also where a picture stops being
     worth more than a table.
  4. ONE LIGHT. At most one .cf-pie__seg--lit per figure. One lime moment per
     object, everywhere in this system.
  5. THE FLOOR. No share below 5 %. Two stacked label lines are about 5 % of the
     label circle, so a smaller share has nowhere to put the words that name it
     -- fold the tail into one share and say so.

The tolerance is 0.001, half of the last digit an author writing three decimals
can control, and every comparison is made in integer thousandths so that .46 +
.27 + .18 + .09 does not fail on the binary representation of a tenth.

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# Thousandths. An authored share is three decimals at the most, so this is one
# unit of the last place an author can type -- not a fudge factor.
TOL = 1

MIN_SHARE = 50    # 5 %, in thousandths
MAX_SEGS = 5
MIN_SEGS = 3

# The designer's own material is not ours to hold to our rules, and a figure
# quoted inside <pre>/<code> is documentation rather than a drawing.
SKIP_DIRS = {"source"}
MASK = re.compile(
    r"<!--.*?-->|<pre\b.*?</pre>|<code\b.*?</code>|<textarea\b.*?</textarea>",
    re.S | re.I,
)

# One <li class="… cf-pie__seg …" style="… --v:…; --turn:… …">. The class list
# and the style attribute are read in whichever order they were written.
SEG = re.compile(r"<li\b[^>]*\bclass\s*=\s*[\"'][^\"']*\bcf-pie__seg\b[^\"']*[\"'][^>]*>",
                 re.I)
ATTR = re.compile(r"(class|style)\s*=\s*[\"']([^\"']*)[\"']", re.I)
NUM = re.compile(r"--(v|turn)\s*:\s*(-?\.\d+|-?\d+(?:\.\d+)?)")


def blank(m):
    """Replace a masked region with spaces, keeping newlines for line numbers."""
    return re.sub(r"[^\n]", " ", m.group(0))


def pages():
    for path in sorted(DS.rglob("*.html")):
        if SKIP_DIRS & {p.name for p in path.parents}:
            continue
        yield path


def thousandths(raw):
    """A share as an integer count of thousandths, or None if it is not a number."""
    try:
        return int(round(float(raw) * 1000))
    except ValueError:
        return None


def figures(text):
    """[(line, [(line, v, turn, lit), ...]), ...] — one entry per .cf-pie.

    Split on the figure rather than on the list, because a page may carry more
    than one and their shares are separate arithmetic.
    """
    out = []
    for fig in re.finditer(r"<figure\b[^>]*\bclass\s*=\s*[\"'][^\"']*\bcf-pie\b[^\"']*[\"']",
                           text, re.I):
        start = fig.start()
        end = text.find("</figure>", start)
        end = len(text) if end == -1 else end
        segs = []
        for m in SEG.finditer(text, start, end):
            attrs = dict((k.lower(), v) for k, v in ATTR.findall(m.group(0)))
            nums = dict(NUM.findall(attrs.get("style", "")))
            segs.append((
                text.count("\n", 0, m.start()) + 1,
                thousandths(nums["v"]) if "v" in nums else None,
                thousandths(nums["turn"]) if "turn" in nums else None,
                "cf-pie__seg--lit" in attrs.get("class", ""),
            ))
        out.append((text.count("\n", 0, start) + 1, segs))
    return out


def audit_figure(segs):
    """Every finding for one figure, as plain sentences."""
    out = []
    for line, v, turn, _ in segs:
        if v is None:
            out.append((line, "no --v: a share with no value is drawn at nothing"))
        if turn is None:
            out.append((line, "no --turn: a share with no start is drawn at 12 o'clock"))
    if any(v is None or turn is None for _, v, turn, _ in segs):
        return out

    if not MIN_SEGS <= len(segs) <= MAX_SEGS:
        out.append((segs[0][0] if segs else 0,
                    "%d shares; the component is three to five" % len(segs)))

    lit = [line for line, _, _, is_lit in segs if is_lit]
    if len(lit) > 1:
        out.append((lit[1], "%d lit shares; one lime moment per object" % len(lit)))

    running = 0
    for line, v, turn, _ in segs:
        if abs(turn - running) > TOL:
            out.append((line, "--turn:%s, but the shares before it come to %s"
                        % (fmt(turn), fmt(running))))
        if v < MIN_SHARE:
            out.append((line, "--v:%s is below the 5 %% floor; its label has "
                              "nowhere to stand" % fmt(v)))
        running += v

    if abs(running - 1000) > TOL:
        out.append((segs[-1][0], "the shares come to %s, not 1 — the total in the "
                                 "hole is a claim about them" % fmt(running)))
    return out


def fmt(n):
    return ("%.3f" % (n / 1000)).rstrip("0").rstrip(".") or "0"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every figure and the sum it came to")
    args = ap.parse_args()

    findings, seen = [], 0
    for path in pages():
        rel = path.relative_to(ROOT)
        text = MASK.sub(blank, path.read_text(encoding="utf-8"))
        for fig_line, segs in figures(text):
            seen += 1
            for line, note in audit_figure(segs):
                findings.append((rel, line, note))
            if args.verbose:
                total = sum(v for _, v, _, _ in segs if v is not None)
                print("  %s:%d  %d shares, %s"
                      % (rel, fig_line, len(segs), fmt(total)))

    if findings:
        for rel, line, note in findings:
            print("%s:%d\n    %s" % (rel, line, note), file=sys.stderr)
        print("\n%d finding%s. A ring whose arithmetic is out still renders as a "
              "ring, which is why this is counted rather than looked at."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    print("pie shares: %d figure%s, every --turn the running sum of the --v before it."
          % (seen, "" if seen == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
