#!/usr/bin/env python3
"""Hold every five-column subdivision to the fold that five columns need.

The fold width is a property of the COLUMN COUNT, not of the primitive.
base.css folds .subdivide at 44rem and carries the measurement for why that
number is right for three columns and wrong for five: at the pixel after the
44rem fold — a viewport of 792, a container of 705 — a five-column grid gives
each single-line tail headline 116 px of text, and the widest first words in
the blog grid ("Smart-Home-Systeme" at 123, "Erneuerbaren-Ausbau" at 120)
no longer fit. Two of twelve headlines render as a fragment of one word plus
an ellipsis: not a shortened headline, an unlabelled link. So the five-column
form opts up to 56rem with .subdivide--late.

That sentence — "a five-column grid takes .subdivide--late" — is written three
times in prose: on the 44rem and 56rem rows of the register in tokens.css and
on the same rows of the table in foundations/layout.html. Nothing read the
markup. The modifier was minted on the landing page's blog grid, the acts
rewrite deleted that grid, and the two five-column call sites that remained —
patterns/news.html and components/blog-grid.html — never carried it. Every
copy of the rule stayed true in the stylesheet while every consumer violated
it, and news.html drew the documented failure for every viewport between 792
and 1006 px: a window nobody's phone and nobody's desktop ever shows them.

WHAT IT CHECKS

  late is worn    every .subdivide call site whose effective column count is
                  five or more carries .subdivide--late. The count is read the
                  way the cascade reads it: a depth modifier (.subdivide--3 …
                  .subdivide--6) wins over an inline --subdivide-count, which
                  wins over the default the base rule declares — and the
                  default is parsed out of base.css rather than repeated here.
  late is earned  the reverse: .subdivide--late on a call site running fewer
                  than five columns folds a grid that still reads — three
                  columns of a 44rem container are 234 px each — a full 192 px
                  of container early. A modifier that strong is not a default.

WHAT IT DOES NOT CHECK

  Whether 56rem is the right number for five columns. That is a measurement,
  and it lives next to the rule in base.css. Whether the fold and the axis
  agree on it — check-subdivide-fold.py holds that pair. Whether the
  thresholds are registered — check-breakpoints.py owns the register.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-subdivide-late.py       # check, exit 1 on a finding
    python3 scripts/check-subdivide-late.py -v    # list every call site
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
BASE = DS / "assets" / "css" / "base.css"

# A real opening tag with a class attribute. Documentation code samples write
# class=&quot;…&quot;, so escaped markup never matches this.
TAG = re.compile(r"<[a-zA-Z][^>]*\bclass=\"([^\"]*)\"[^>]*>")

DEPTH = re.compile(r"subdivide--([3-6])\b")
COUNT = re.compile(r"--subdivide-count\s*:\s*(\d+)")

# The default column count is whatever the base rule's var() fallback says —
# parsed, not repeated, so this file cannot disagree with the stylesheet.
DEFAULT = re.compile(r"--subdivide-even\s*:\s*repeat\(\s*var\(--subdivide-count\s*,\s*(\d+)\s*\)")


def call_sites():
    """(path, line, classes, count) for every .subdivide call site."""
    default = None
    m = DEFAULT.search(BASE.read_text(encoding="utf-8"))
    if m:
        default = int(m.group(1))
    sites = []
    for path in sorted(DS.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        for m in TAG.finditer(text):
            classes = m.group(1).split()
            if "subdivide" not in classes:
                continue
            tag = m.group(0)
            line = text.count("\n", 0, m.start()) + 1
            depths = [int(d) for d in DEPTH.findall(" ".join(classes))]
            styled = COUNT.search(tag)
            if depths:
                # Multiple depth classes resolve by stylesheet order, which
                # is ascending — the highest number wins.
                count = max(depths)
            elif styled:
                count = int(styled.group(1))
            else:
                count = default
            sites.append((path, line, classes, count))
    return sites, default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    sites, default = call_sites()
    failures = []

    if default is None:
        failures.append(
            "base.css no longer declares the subdivision's default column count\n"
            "    (the var(--subdivide-count, N) fallback on --subdivide-even).\n"
            "    This check reads the default from there so the two cannot disagree;\n"
            "    if the declaration moved, move the pattern in this file with it."
        )

    for path, line, classes, count in sites:
        rel = path.relative_to(ROOT)
        late = "subdivide--late" in classes
        if count is None:
            continue
        if count >= 5 and not late:
            failures.append(
                "%s:%d runs the subdivision at %d columns without .subdivide--late.\n"
                "    The primitive's own fold at 44rem is the number for THREE columns.\n"
                "    Between 44rem and 56rem of container this grid draws %d columns at\n"
                "    widths where a single-line headline's first word no longer fits —\n"
                "    base.css carries the measurement. Add .subdivide--late."
                % (rel, line, count, count)
            )
        if count < 5 and late:
            failures.append(
                "%s:%d runs the subdivision at %d columns WITH .subdivide--late.\n"
                "    The late fold is what five columns need; three columns of a 44rem\n"
                "    container are 234 px each and read fine. This folds a readable\n"
                "    grid 192 px of container early. Drop the modifier."
                % (rel, line, count)
            )

    if args.verbose:
        print("subdivision call sites (default count %s)\n" % default)
        for path, line, classes, count in sites:
            print(
                "  %s:%d   %d column(s)   %s"
                % (
                    path.relative_to(ROOT),
                    line,
                    count if count is not None else -1,
                    "late" if "subdivide--late" in classes else "-",
                )
            )
        print()

    if failures:
        print("subdivide late: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    late = sum(1 for _, _, c, _ in sites if "subdivide--late" in c)
    print(
        "subdivide late: %d call site(s), %d at five or more columns, "
        "all of those wearing .subdivide--late (%d total)."
        % (len(sites), sum(1 for s in sites if s[3] is not None and s[3] >= 5), late)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
