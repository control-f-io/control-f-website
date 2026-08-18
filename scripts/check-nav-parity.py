#!/usr/bin/env python3
"""Every pattern page's navigation bar is the same bar, drift-for-drift.

The companion to check-footer-parity.py, and the other half of its argument.
There is no build step and no include: fifteen pattern pages each carry a
hand-typed copy of the one component that reaches every other page — the
cf-nav bar, its logo, its toggle and its seven links. The footer earned its
parity gate after four of its fifteen copies had quietly stopped being the
same block (#293), and the fix's own docstring names the exposure: a block
hand-typed once per page, "edited hourly by twelve routines, is the exact
surface this directory keeps finding forks on". The nav is that surface
exactly — the same fifteen copies, the same hourly edits — and it is a more
expensive place to fork than the footer, because below 780 px the bar's seven
links are the ONLY way off any page: a copy that loses a link does not render
wrong, it just strands a phone reader one route short, on one page, invisibly.

WHAT FOUND THIS. A full sweep of the fifteen copies, the way the footer was
swept. Raw, they differ three ways; after the two lawful axes below are
normalised away they are CHARACTER-IDENTICAL, fifteen for fifteen. Clean
without a gate is a coincidence, not a fact — the footer's copies were
presumably identical once too, and what #293 found four of them doing later
is what this file exists to make impossible here. The same sweep drove every
copy in a browser: the toggle opens, Escape closes and restores focus, and
the panel folds identically on all fifteen pages today — behaviour parity
that holds precisely as long as the markup the script reads stays one block.

THE LAWFUL AXES. Three, fewer than the footer needs — the bar is the same
everywhere by design, which is why anything else is a finding:

  ARIA-CURRENT   moves per page, naturally. Whether each copy marks the
                 RIGHT link the RIGHT way is check-a11y.py's CURRENT rule
                 and is not re-judged here; this file only refuses to call
                 the moving marker a fork.

  LANG-HREF      the language switch points at the SAME page in the other
                 edition — /kontakt offers /en/kontakt, not /en/. That
                 target therefore moves per page for the same reason
                 aria-current does, and for the same reason it is not a
                 fork. Only the href moves: the label, the two language
                 declarations and the aria-label are the bar's and are
                 compared like everything else, so a copy that offers the
                 wrong language, or offers it unlabelled, still fails.

  COMMENTS       datenschutz.html and impressum.html each argue in place
                 why their bar carries no aria-current at all — the page is
                 beside the seven routes, not in them. An argument is not
                 markup and is stripped before comparing, on every page.

THE RULES. Two, on every design-system/patterns/*.html:

  ONE-NAV   the page carries exactly one cf-nav bar. Zero is a page with no
            way anywhere below 780 px; two is two bars fighting for one
            aria-label and one id.

  PARITY    after stripping comments and aria-current and collapsing
            whitespace, every copy is character-identical to the consensus
            of all fifteen. A dissenting copy is named with the first point
            of divergence, majority against dissenter, so whatever the next
            fork is — a link lost, a label rephrased, an attribute dropped —
            it fails here without this file having to predict it.

The consensus and not a canonical file, deliberately. check-footer-parity.py
holds its copies to components/footer.html because that demo mirrors the
shipping footer link-for-link. The nav component's demo does not and should
not: components/navigation.html teaches the component with `#` hrefs, its own
demo ids and a five-entry list, chrome abstracted away from any page's
reality. Holding fifteen shipping copies to a teaching abstraction would
mean editing the demo every time the site's routes change — a coupling the
demo's whole shape argues against — so the fifteen hold each other, and the
demo stays what it is: another section's file, judged by another section's
routine. If the fifteen ever split with no majority, every variant is
reported and nothing is guessed.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-nav-parity.py       # check, exit 1 on a finding
    python3 scripts/check-nav-parity.py -v    # list every bar audited
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

COMMENT = re.compile(r"<!--.*?-->", re.S)
NAV = re.compile(r"<nav\s+class=\"cf-nav\"[^>]*>.*?</nav>", re.S)


def flatten(nav_html):
    """One line: whitespace runs become one space, whitespace between tags
    disappears, so indentation is never a difference."""
    text = re.sub(r"\s+", " ", nav_html).strip()
    text = re.sub(r"> <", "><", text)
    return text


LANG_HREF = re.compile(r"(<a class=\"cf-nav__lang\" href=\")[^\"]*\"")


def normalise(flat):
    """Remove the two lawful markup axes: the moving aria-current marker, and
    the language switch's target, which moves with the page it stands on."""
    flat = re.sub(r"\s+aria-current=\"[^\"]*\"", "", flat)
    return LANG_HREF.sub(r"\1…\"", flat)


def divergence(a, b):
    """Where two normalised bars first part, with enough context to read."""
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    lo = max(0, i - 60)
    return ("      consensus  …%s…\n      this copy  …%s…"
            % (a[lo:i + 80], b[lo:i + 80]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    findings = []
    bars = {}  # name -> normalised bar

    pages = sorted(PATTERNS.glob("*.html"))
    for path in pages:
        rel = path.relative_to(ROOT)
        text = COMMENT.sub("", path.read_text(encoding="utf-8"))
        found = NAV.findall(text)
        if len(found) != 1:
            findings.append(
                "%s\n    ONE-NAV  the page carries %d cf-nav bars; every "
                "pattern page carries exactly one"
                % (rel, len(found)))
            continue
        bars[path.name] = normalise(flatten(found[0]))

    groups = {}
    for name, bar in bars.items():
        groups.setdefault(bar, []).append(name)

    if len(groups) > 1:
        ranked = sorted(groups.items(), key=lambda kv: -len(kv[1]))
        canon, majority = ranked[0]
        if len(ranked[1][1]) == len(majority):
            # No majority to trust: report the split whole, guess nothing.
            findings.append(
                "design-system/patterns\n    PARITY  the fifteen bars split "
                "into %d equal camps (%s); no consensus to hold anyone to"
                % (len(ranked), "; ".join(
                    ", ".join(sorted(names)) for _, names in ranked)))
        else:
            for bar, names in ranked[1:]:
                for name in sorted(names):
                    findings.append(
                        "design-system/patterns/%s\n    PARITY  this bar is "
                        "not the bar the other %d pages carry — first "
                        "divergence:\n%s"
                        % (name, len(majority), divergence(canon, bar)))

    if args.verbose:
        for name in sorted(bars):
            print("  %-24s %5d chars normalised" % (name, len(bars[name])))
        print("  %d bars, %d distinct after lawful axes" %
              (len(bars), len(groups)))

    if findings:
        print("check-nav-parity: %d finding(s)\n" % len(findings))
        for f in findings:
            print(f)
        return 1
    print("check-nav-parity: %d bars, one block. OK" % len(bars))
    return 0


if __name__ == "__main__":
    sys.exit(main())
