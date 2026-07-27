#!/usr/bin/env python3
"""Enforce that a CROP is a crop and not an accidental scroll container.

`overflow: hidden` does two things at once. It crops — which is the thing
anybody writing it wants — and it makes the element a scroll container, which
almost nobody writing it wants and which is invisible in every screenshot. A
scroll container changes what a view timeline resolves against, it changes what
`position: sticky` is measured inside, it gives the box a scrollport that can be
panned to with a keyboard or a script, and it does all of that while rendering
identically to the thing that was intended.

The system has already been bitten by both halves of this, twice, and wrote
each up where it happened rather than anywhere a checker could read:

  the timeline    .cf-hero cropped its artwork with `overflow: hidden`, and so
                  every `animation-timeline: view()` inside that header
                  resolved against a box that never scrolls.
                  .cf-btn--glass::before reported a live ViewTimeline whose
                  progress sat at 0.116 and did not move at any scroll position
                  on the page. No error, no warning, and no visible difference
                  from an animation that had simply not been written.
                  components.css says all of this, in prose, on the fix.

  the scrollport  prototypes/demon-core.html cropped an ambient wash inset
                  -10 % with `overflow-x: hidden` on <body>. That declaration
                  never cropped anything: `overflow` on <body> PROPAGATES to
                  the viewport and leaves body itself computing to `visible`,
                  so the wash sailed past it and the document sat 128 px
                  scrollable sideways at 1280, 77 at 768 and 38 at 375, with
                  nothing out there to look at. `clip` is excluded from that
                  propagation, so it stays on the box that declared it.

Both fixes are the same word, and the second one is the tell: the system is
now three prose statements deep on `hidden` versus `clip` — components.css on
.cf-hero, foundations/materials.html and foundations/motion.html — and prose is
what the other five checks in this directory exist because of.

THE RULE. In the three shipping stylesheets, a declaration of `overflow`,
`overflow-x` or `overflow-y` whose value is `hidden` must be accompanied, in
the same declaration block, by the same property set to `clip`. The pair is how
this system already writes it:

    overflow: hidden;
    overflow: clip;

A browser without `clip` drops the second and keeps the crop it always had; a
browser with it takes the second and the scrollport never exists. Nothing about
the paint changes in either.

TWO EXEMPTIONS, both because the block is not cropping a layer at all:

  text-overflow   A block that also declares `text-overflow` is truncating a
                  line of text. `overflow` there is the switch that makes the
                  ellipsis legal rather than a crop of a composed layer, the
                  box is a single line, and the scrollport it makes has nothing
                  in it. .cf-breadcrumb__current, .cf-blog-card--compact and
                  .cf-result__path are the three.

  .visually-hidden  The standard clip-rect idiom, which is a 1 px box whose
                  whole job is to hold text out of sight of a sighted reader
                  and in the accessibility tree. It is quoted verbatim from the
                  practice it comes from and is not this system's to reword.

Scope is the three shipping stylesheets, the same boundary check-grid-tracks.py
and check-spacing-scale.py draw: docs.css styles the documentation and does not
ship, per-page <style> blocks are one page's business, and prototypes/ is
unshipped on purpose. The prototype above is what found the bug; it is not what
the rule is for.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-overflow-clip.py       # check, exit 1 on a finding
    python3 scripts/check-overflow-clip.py -v    # list every crop, not only failures
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

SHIPPING = ("tokens.css", "base.css", "components.css")

# `overflow`, `overflow-x`, `overflow-y`. `overflow-block`/`overflow-inline`
# are here so a logical-property rewrite later does not walk around the check.
OVERFLOW = re.compile(
    r"(?<![\w-])(overflow(?:-x|-y|-block|-inline)?)\s*:\s*([^;{}]+)", re.I
)
COMMENT = re.compile(r"/\*.*?\*/", re.S)
EXEMPT_SELECTOR = re.compile(r"\.visually-hidden(?![\w-])")


def blocks(text):
    """Every rule as (line, selector, body), comments blanked in place.

    Comments go first and in place — newlines kept — so line numbers survive
    and so an `overflow: hidden` quoted inside a comment is never read as a
    declaration. Half of this system's stylesheets are comment by volume and
    several of those comments are about this exact property.

    Nesting is not parsed and does not need to be: a rule inside @media still
    arrives here with its own selector, because a declaration block is the
    innermost thing between braces and CSS declaration blocks do not nest.
    """
    text = COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    out = []
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        selector = " ".join(m.group(1).split())
        # An at-rule prelude (@media …) is picked up as the selector of the
        # block that follows it; strip it back to the real selector.
        if "{" not in m.group(1) and selector.startswith("@"):
            continue
        out.append((text.count("\n", 0, m.start(2)) + 1, selector, m.group(2)))
    return out


def crops(body):
    """{property: set(values)} for every overflow declaration in a block."""
    found = {}
    for prop, value in OVERFLOW.findall(body):
        found.setdefault(prop.lower(), set()).add(value.strip().lower())
    return found


def audit():
    findings, seen = [], []
    for name in SHIPPING:
        path = CSS / name
        if not path.exists():
            findings.append((name, 0, "", "stylesheet is missing"))
            continue
        for line, selector, body in blocks(path.read_text(encoding="utf-8")):
            found = crops(body)
            if not found:
                continue
            exempt = None
            if re.search(r"(?<![\w-])text-overflow\s*:", body, re.I):
                exempt = "text-overflow"
            elif EXEMPT_SELECTOR.search(selector):
                exempt = ".visually-hidden"
            for prop, values in sorted(found.items()):
                if "hidden" not in values:
                    seen.append((name, line, selector, prop, "clip only"
                                 if "clip" in values else " / ".join(sorted(values))))
                    continue
                if exempt:
                    seen.append((name, line, selector, prop, "exempt: " + exempt))
                elif "clip" in values:
                    seen.append((name, line, selector, prop, "hidden + clip"))
                else:
                    findings.append((name, line, selector,
                                     "%s: hidden with no `%s: clip` beside it — this "
                                     "crop is also a scroll container" % (prop, prop)))
    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every overflow declaration, not only the failures")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for name, line, selector, prop, note in seen:
            print("  %-16s %5d  %-46s %-12s %s"
                  % (name, line, selector[:46], prop, note))
        print()

    if findings:
        for name, line, selector, why in findings:
            print("%s:%d  %s\n    %s" % (name, line, selector or "(file)", why),
                  file=sys.stderr)
        print("\n%d crop%s that is also a scrollport. Add the matching `clip` "
              "declaration under the `hidden` one."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    paired = sum(1 for *_, note in seen if note == "hidden + clip")
    exempted = sum(1 for *_, note in seen if note.startswith("exempt"))
    print("overflow: %d crops paired with clip, %d exempt, %d declarations read."
          % (paired, exempted, len(seen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
