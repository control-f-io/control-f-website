#!/usr/bin/env python3
"""Every page under design-system/patterns/ is registered in the section index.

The sixteenth check, and the third about the system as a site. The Patterns
section holds one file per route of the site the system describes, and
design-system/index.html holds one .docs-card per page — title, one line of
description, a link. That index is the only place the section is enumerated:
there is no build step to generate a listing, no directory browsing on Pages,
and no page in the section links to all of its siblings. A pattern page whose
card is missing is therefore not late documentation, it is unreachable — it
ships to production, renders perfectly at its address, and no reader who did
not already know the address can ever arrive at it.

The build lane's own working rule states it in prose: "a page nothing links to
is not shipped." Nothing ran that rule. The failure it describes is the same
shape as the fifteen checks beside this one: a tree with an orphaned page
renders identically to a tree without one, in every screenshot, on every page
anyone actually visits — the difference is a card that is not there, and an
absence photographs as nothing at all. check-links.py guards the opposite
direction (a card pointing at a file that does not exist dies as MISSING);
until this check, the direction that matters for shipping had no guard.

WHAT IT CHECKS. For every design-system/patterns/*.html there is at least one
href="patterns/<file>" inside design-system/index.html, read with comments,
<pre>, <code> and <textarea> bodies masked — a card quoted in documentation
prose is prose, not a route in. The scope is patterns/ alone, deliberately:
foundations/ and components/ carry the same card convention but belong to
other lanes, and prototypes/ keeps deliberately unlisted work — a boundary,
not an omission.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-registered.py       # check, exit 1 on a finding
    python3 scripts/check-registered.py -v    # list every page and its card line
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
INDEX = ROOT / "design-system" / "index.html"

# Regions whose contents are documentation, not markup the browser acts on.
MASK = re.compile(
    r"<!--.*?-->|<pre\b.*?</pre>|<code\b.*?</code>|<textarea\b.*?</textarea>",
    re.S | re.I,
)


def blank(m):
    """Replace a masked region with spaces, keeping newlines for line numbers."""
    return re.sub(r"[^\n]", " ", m.group(0))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every page and the index line that registers it")
    args = ap.parse_args()

    text = MASK.sub(blank, INDEX.read_text(encoding="utf-8"))
    cards = {}  # href target -> line of its first live occurrence
    for m in re.finditer(r"""href\s*=\s*["'](patterns/[^"'#?]+\.html)["']""", text):
        cards.setdefault(m.group(1), text.count("\n", 0, m.start()) + 1)

    findings = []
    for path in sorted(PATTERNS.glob("*.html")):
        target = "patterns/" + path.name
        line = cards.get(target)
        if line is None:
            findings.append(path.relative_to(ROOT))
        elif args.verbose:
            print("  %-44s registered at index.html:%d" % (target, line))

    if findings:
        for rel in findings:
            print("%s\n    no href=\"patterns/%s\" anywhere live in "
                  "design-system/index.html — the page ships, renders, and "
                  "cannot be arrived at" % (rel, rel.name), file=sys.stderr)
        print("\n%d orphaned page%s in the one section that exists to be walked. "
              "Every file under design-system/patterns/ carries a .docs-card in "
              "the section index." % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    print("registered: %d pattern pages, every one carded in the section index."
          % len(list(PATTERNS.glob("*.html"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
