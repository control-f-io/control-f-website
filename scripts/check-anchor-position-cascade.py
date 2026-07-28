#!/usr/bin/env python3
"""An anchor is only acceptable to an ABSOLUTELY positioned element, and the
cascade gets the last word on which one that is.

The sixty-ninth check, and the second at anchor positioning's silent failure
mode. check-anchor-positioning.py holds three things about the NAMES -- that
every --name used resolves, that every one declared is used, and that every use
sits inside an @supports that tests the feature. All three are properties of a
single declaration read on its own. This one is a property of the CASCADE, and
it is the failure that check's own docstring was written about:

    "Giving the header's wrapper `position: relative` -- an ordinary thing to
     do, and done to get a sane percentage basis -- made .lp-flow unacceptable,
     and every anchor() in the rule fell back at once. The header dropped 250 px
     to its static position and drew a full-measure hairline through the middle
     of the root."

That paragraph is the story of how the fortieth check came to exist. The check
it produced could not see the thing it describes, and the thing it describes
came back on a different element and shipped.

WHAT WAS WRONG, measured at 1440 x 900 on the render before this commit.
patterns/landing-page.html anchors the "Was wir machen" header to the drawing,
inside `@supports (anchor-name: --lp-flow-box) and (top: anchor(...))`:

    .lp-proc-head { position: absolute;
                    top: max(calc(anchor(--lp-flow-box top) + ...), ...);
                    left: 50%; width: anchor-size(--lp-flow-box width); }

476 lines further down the same file, inside the same gate and at the same
specificity -- one class, no @supports of its own to narrow it -- stood

    .lp-proc-head { position: relative; ... }

written to give `.lp-proc-head::after` a containing block, which is a real need
and an ordinary declaration. Later rule, equal specificity, so it won. The
header was `position: relative`, an anchor is not acceptable to a relatively
positioned element, and so `top`, `left` and `width` were all invalid at
computed-value time:

    top     max(calc(anchor(...)), calc(anchor(...)))  ->  0px
    width   anchor-size(--lp-flow-box width)           ->  auto, 1280.02 px

The rule that is meant to be the drawing's horizon therefore rendered 1280.02 px
wide against the drawing's 1096, 315.6 px BELOW the rim it names, and EIGHT
strokes of the root crossed it -- at x 181.3, 272.3, 395.6, 690.1, 724.2, 868.2,
950.4 and 984.1. Nothing failed. Every other check in the repository passed, the
page rendered, and the only report was a screenshot.

THE INVARIANT, which is countable in a file and invisible in a screenshot:

    For every selector that reads anchor() or anchor-size(), the `position`
    that WINS the cascade for that selector must be absolute or fixed.

Not "is declared absolute somewhere" -- won. The whole defect is a declaration
that was there, correct, and outvoted by source order.

HOW THE WINNER IS FOUND. Rules are read in source order and grouped by their
normalised selector. Every rule considered here has the same specificity as the
one it is compared against, because they are the SAME selector text -- which is
the case that matters and the case that bit, since a selector written twice in
one file is how a property gets quietly reassigned. Later wins; the last
`position` for that selector is the winner. A selector that declares anchor()
and never declares `position` at all is the same finding by another route: an
unpositioned element falls back exactly as a relative one does.

WHAT IT DOES NOT CLAIM. Two rules for one selector can sit in @media blocks that
cannot both apply, and then the later one does not really win. That is reported
rather than assumed away: a rule in a disjoint at-rule chain is skipped and
named under -v, so a real exclusion is visible instead of silently trusted. The
narrow, common, and dangerous case -- the same at-rule chain, or a later rule in
a chain that is a PREFIX of the earlier one's, which is what "476 lines down,
same gate" is -- is the one this fails on.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-anchor-position-cascade.py       # exit 1 on a finding
    python3 scripts/check-anchor-position-cascade.py -v    # print every anchored
                                                           # selector and its winner
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHIPPING_CSS = [
    ROOT / "design-system" / "assets" / "css" / "tokens.css",
    ROOT / "design-system" / "assets" / "css" / "base.css",
    ROOT / "design-system" / "assets" / "css" / "components.css",
]

ANCHOR_RE = re.compile(r"\banchor(?:-size)?\s*\(")
POSITION_RE = re.compile(r"(?:^|;)\s*position\s*:\s*([^;}]+)", re.I)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S | re.I)

# `position` values an anchor is acceptable to. Per css-anchor-position-1, the
# positioned element must be absolutely positioned -- which is `absolute` and
# `fixed`. `sticky` and `relative` are relatively positioned and do not qualify.
ABSOLUTE = {"absolute", "fixed"}


def strip_comments(css):
    return COMMENT_RE.sub(" ", css)


def normalise(selector):
    """Collapse whitespace and combinator spacing so one selector has one name."""
    s = " ".join(selector.split())
    s = re.sub(r"\s*([>+~,])\s*", r"\1", s)
    return s


def parse_rules(css):
    """[(order, at_chain, selector_list, declarations)] in source order.

    A hand-rolled brace walker rather than a CSS parser, for the same reason
    every other script here is: stdlib only. It tracks the at-rule chain so a
    rule inside @supports/@media knows what it is gated by.
    """
    rules, stack, order = [], [], 0
    i, n, buf = 0, len(css), []
    while i < n:
        c = css[i]
        if c == "{":
            head = "".join(buf).strip()
            buf = []
            if head.startswith("@"):
                stack.append(normalise(head))
                rules.append(None)  # placeholder keeps nesting readable
                rules.pop()
            else:
                # find the matching close brace for this declaration block
                depth, j = 1, i + 1
                while j < n and depth:
                    if css[j] == "{":
                        depth += 1
                    elif css[j] == "}":
                        depth -= 1
                    j += 1
                body = css[i + 1:j - 1]
                if "{" not in body:  # a real declaration block, not nested rules
                    order += 1
                    sels = [normalise(s) for s in head.split(",") if s.strip()]
                    rules.append((order, tuple(stack), sels, body))
                    i = j
                    continue
                stack.append(head)
            i += 1
            continue
        if c == "}":
            if stack:
                stack.pop()
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    return rules


def disjoint(chain_a, chain_b):
    """True when two at-rule chains provably cannot both apply.

    Conservative on purpose: only a straightforwardly contradictory min-width /
    max-width pair counts. Everything else is treated as possibly co-applying,
    which is the direction that reports rather than hides.
    """
    def widths(chain):
        lo, hi = 0.0, float("inf")
        for at in chain:
            for m in re.finditer(r"min-width\s*:\s*([\d.]+)(rem|px)", at):
                v = float(m.group(1)) * (16 if m.group(2) == "rem" else 1)
                lo = max(lo, v)
            for m in re.finditer(r"max-width\s*:\s*([\d.]+)(rem|px)", at):
                v = float(m.group(1)) * (16 if m.group(2) == "rem" else 1)
                hi = min(hi, v)
        return lo, hi
    alo, ahi = widths(chain_a)
    blo, bhi = widths(chain_b)
    return alo > bhi or blo > ahi


def check_source(label, css, verbose):
    rules = parse_rules(strip_comments(css))

    anchored = {}   # selector -> first order that reads an anchor
    for order, chain, sels, body in rules:
        if not ANCHOR_RE.search(body):
            continue
        for s in sels:
            anchored.setdefault(s, (order, chain))

    findings, skipped, checked = [], [], 0
    for sel, (aorder, achain) in sorted(anchored.items()):
        declared = []
        for order, chain, sels, body in rules:
            if sel not in sels:
                continue
            m = POSITION_RE.search(";" + body)
            if not m:
                continue
            if order != aorder and disjoint(achain, chain):
                skipped.append(f"{label}: {sel} — a `position` at rule {order} is "
                               f"gated {chain} and cannot apply with {achain}")
                continue
            declared.append((order, chain, m.group(1).strip().split()[0].lower()))

        checked += 1
        if not declared:
            findings.append(
                f"{label}: {sel} reads an anchor and no rule gives it a `position` at "
                f"all. An anchor is only acceptable to an absolutely positioned "
                f"element; a static one falls back to exactly where it already was, "
                f"renders, and reports nothing.")
            continue

        winner_order, winner_chain, winner = max(declared, key=lambda d: d[0])
        if winner not in ABSOLUTE:
            others = ", ".join(f"rule {o}: {v}" for o, _, v in declared)
            findings.append(
                f"{label}: {sel} reads an anchor at rule {aorder}, and the `position` "
                f"that WINS the cascade for it is {winner!r}, set at rule "
                f"{winner_order}. An anchor is only acceptable to an absolutely "
                f"positioned element, so every anchor() and anchor-size() on this "
                f"selector is invalid at computed-value time and the element renders "
                f"at its static position and its static size, silently. Seen for this "
                f"selector: {others}. Later wins at equal specificity — the fix is "
                f"source order, not another declaration.")
        elif verbose:
            print(f"    {sel:<32} anchors at rule {aorder}, position {winner!r} "
                  f"wins at rule {winner_order}")
    return findings, skipped, checked


def main():
    parser = argparse.ArgumentParser(
        description="The `position` that wins the cascade for an anchored selector "
                    "must be absolute or fixed.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print every anchored selector and the position that wins")
    args = parser.parse_args()

    sources = []
    for page in sorted((ROOT / "design-system").rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        css = "\n".join(STYLE_RE.findall(text))
        if css.strip():
            sources.append((str(page.relative_to(ROOT)), css))
    for sheet in SHIPPING_CSS:
        if sheet.exists():
            sources.append((str(sheet.relative_to(ROOT)), sheet.read_text(encoding="utf-8")))

    findings, skipped, checked, files = [], [], 0, 0
    for label, css in sources:
        if not ANCHOR_RE.search(strip_comments(css)):
            continue
        files += 1
        if args.verbose:
            print(f"  {label}:")
        f, s, c = check_source(label, css, args.verbose)
        findings += f
        skipped += s
        checked += c

    if not checked:
        print("anchor position cascade: no selector on the shipping surface reads an "
              "anchor — the scan went stale")
        return 1
    if args.verbose:
        for s in skipped:
            print(f"  skipped: {s}")
    if findings:
        print(f"\nanchor position cascade: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"anchor position cascade OK — {checked} anchored selector(s) across {files} "
          f"file(s), and for every one of them the `position` that wins the cascade is "
          f"absolute or fixed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
