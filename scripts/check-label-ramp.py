#!/usr/bin/env python3
"""Hold the mono label ramp.

base.css calls .t-label "the single most recognisable text style in the brand"
and tokens.css writes the size into the token itself:

    --text-xs: 0.6875rem; /* 11 - mono labels only, never prose */

Mono AND uppercase is that style's signature. It is on the section header's
label and its counter, the nav, every eyebrow, every meta line, every counter
on every card - and every one of them is 11 px, because a label ramp with two
sizes in it is not a ramp. The system has exactly one deliberate step above
it, and it is a named class: .t-label-lg at --text-sm, which .cf-btn and
.cf-prose h4 also take.

WHAT THIS CHECK IS FOR. The failure it caught is not a wrong-looking rule. It
is a rule that copies four of .t-label's five declarations by hand and gets the
fifth wrong, which is what a hand-restated utility does eventually. On the
landing page's partner wall that produced mono uppercase at --text-lg: the one
run of it in the system above 13 px, on a GHOSTED placeholder, 45 % larger than
the <h2> standing on the hairline directly above it. Nothing about it read as
broken in isolation. It read as broken beside the heading it dwarfed, and no
existing check looks at type size at all.

THE RAMP, and it is short on purpose:

    --text-xs   0.6875rem / 11   the label. 51 rules.
    --text-sm   0.875rem  / 14   the named larger form: .t-label-lg, and the
                                 two components that take that form, .cf-btn
                                 and .cf-prose h4.

A rule that sets font-family to the mono stack and text-transform: uppercase,
and sets a font-size that is neither, is a finding until the size becomes one
of the two or the rule is added to EXEMPT below with a reason.

SCOPE is every stylesheet that ships plus every <style> block on a page in
design-system/ - wider than check-spacing-scale.py's, because this is exactly
the boundary the defect crossed. A page's own <style> block is where a utility
gets restated by hand; a check that stopped at the shipping stylesheets would
have looked straight past the only occurrence there has ever been. docs.css is
documentation chrome and is out, the same call every check here makes.

Sizes are compared as tokens, not as computed lengths. `var(--text-xs)` and
`var(--text-xs, .6875rem)` are the same decision; a bare `0.6875rem` is not,
because the point of the ramp is that the size is named.

stdlib only, no build step, no dependency - the same contract as the
twenty-two checks beside it.

    python3 scripts/check-label-ramp.py       # check, exit 1 on a finding
    python3 scripts/check-label-ramp.py -v    # print every rule on the ramp
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
DESIGN_SYSTEM = ROOT / "design-system"

SHIPPING = ("tokens.css", "base.css", "components.css")

# The ramp. A mono uppercase rule sets one of these or it is a finding.
RAMP = ("--text-xs", "--text-sm")

# Rules that are mono and uppercase and off the ramp, each with the reason.
# Keep this list short: every entry is a place the ramp does not reach, and a
# long list would mean the ramp is wrong rather than that the exceptions are.
EXEMPT = {
    # Type inside an SVG, not type on the page. The plan is drawn in a
    # viewBox and scales with it, so its 13 px is a coordinate in the
    # drawing's own space - the ramp governs px that land on the document.
    ("foundations/sight.html", ".sight-plan text"),
}

MONO = re.compile(r"font-family:[^;]*--font-mono")
UPPER = re.compile(r"text-transform:\s*uppercase")
SIZE = re.compile(r"font-size:\s*([^;}]+)")
TOKEN = re.compile(r"var\(\s*(--[\w-]+)")


def blocks(text):
    """Every `selector { ... }` pair, comments blanked, line numbers kept.

    A brace walker and not a parser, the same shape as the other checks: at-
    rules nest, so a block whose body still contains a brace is passed over
    and its inner blocks are found on their own.
    """
    text = re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), text, flags=re.S)
    for m in re.finditer(r"\{([^{}]*)\}", text):
        body = m.group(1)
        head = text[:m.start()]
        selector = re.split(r"[{}]", head)[-1]
        selector = selector.rsplit(";", 1)[-1].strip()
        selector = " ".join(selector.split())
        yield selector, body, head.count("\n") + 1


def sources():
    """(label, text) for every file whose rules this check governs."""
    for name in SHIPPING:
        yield name, (CSS / name).read_text(encoding="utf-8")
    for page in sorted(DESIGN_SYSTEM.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        label = str(page.relative_to(DESIGN_SYSTEM))
        for m in re.finditer(r"<style[^>]*>(.*?)</style>", text, flags=re.S):
            # Keep the offset so reported line numbers are the page's own.
            lead = text[:m.start(1)].count("\n")
            yield label, "\n" * lead + m.group(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every mono uppercase rule and its size")
    args = ap.parse_args()

    on_ramp, findings, exempt_seen = [], [], set()

    for label, text in sources():
        for selector, body, line in blocks(text):
            if not (MONO.search(body) and UPPER.search(body)):
                continue
            m = SIZE.search(body)
            size = m.group(1).strip() if m else None
            if size is None:
                # No size of its own: it inherits one, and inheriting is not a
                # decision this check can read. .t-numeric and the colour-only
                # utilities land here.
                continue
            token = TOKEN.search(size)
            named = token.group(1) if token else None
            entry = (label, selector, size, line)
            if named in RAMP:
                on_ramp.append(entry)
            elif (label, selector) in EXEMPT:
                exempt_seen.add((label, selector))
                on_ramp.append(entry)
            else:
                findings.append(entry)

    if args.verbose:
        for label, selector, size, line in sorted(on_ramp):
            print("  %-28s %-34s %s" % (label, selector[:34], size))
        print("  %d rules on the ramp" % len(on_ramp))

    stale = EXEMPT - exempt_seen
    for label, selector in sorted(stale):
        print("check-label-ramp: %s %s is exempted and no longer exists. "
              "Drop the entry." % (label, selector), file=sys.stderr)

    for label, selector, size, line in findings:
        print("check-label-ramp: %s:%d  %s sets mono + uppercase at %s.\n"
              "    The label ramp is --text-xs (11, .t-label) and --text-sm "
              "(14, .t-label-lg). Take one of the two, use the class rather "
              "than restating it, or add the rule to EXEMPT in this file with "
              "a reason." % (label, line, selector, size), file=sys.stderr)

    if findings or stale:
        return 1
    print("check-label-ramp: %d mono uppercase rules, all on the ramp "
          "(%d exempt)." % (len(on_ramp), len(exempt_seen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
