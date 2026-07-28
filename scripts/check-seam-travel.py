#!/usr/bin/env python3
"""A seam between two scroll contexts is two numbers, not one.

THE SEAM. patterns/landing-page.html hands the reader from .lp-flow — the root
that grows out of the statement's void — to .lp-frame, the lectern's six
hairlines. The root's sixteen terminals stop at the foot of its own box; the
frame's top rail is the line they are aimed at. check-flow-terminals.py holds
"a root has no free ends" inside the flow's own 1200 x 620 units, and
check-flow-handover.py holds the x axis of the join across the two viewBoxes.
Both are exact and neither can see what this check is for.

WHAT WAS MISSING. The y axis of that seam was measured, written down in the
.lp-flow note as a nine-row table, and handed to the craft lane. Every row of
that table was taken BEFORE THE PIN ENGAGES, and nothing said so loudly enough
to stop the number being read as the seam's whole behaviour. It is not:

    1440 x 900, gap = frame top - flow bottom, by distance from the scroll
    position .cf-pin__stage sticks at

        pin -400 .. -20      1.58 px    flat, the whole approach
        pin   +0             1.70 px    the sticky snap, +0.12
        pin  +60            61.70 px
        pin +160           161.70 px    flow bottom still at viewport y 9.3
        pin +200           201.70 px    flow bottom finally off screen

    Identical with the consent notice up or dismissed; only the scroll position
    the stage sticks at moves (1598 against 1670), because the hero reserves
    the notice's height. The gap column does not move, which is the point — the
    rate belongs to the asymmetry, not to the layout.

1440 x 900 is the ONE viewport the pre-pin table records the seam as made at,
and it is made only until the stage sticks. From that scroll position the gap
opens at 1.00 px per px, and for the next 160 px of scroll both ends are on
screen at once: sixteen stroke terminals hanging in wash with the rail they are
drawn to arrive on sitting well below them. It is the same picture #176 was
opened for — "a bus with two runs that stopped in mid-air" — reached from the
other direction, and no check could see it because no check reads a second
scroll position.

WHY IT HAPPENS, AND WHY IT IS STRUCTURAL RATHER THAN A NUMBER. .lp-frame sits
inside .cf-pin__stage, which is `position: sticky; top: 0`. .lp-flow sits in
static flow one section up. Once the stage sticks it holds still against the
viewport while the flow keeps travelling with the page, so the distance between
them grows by exactly the scroll delta. That rate is not tuned and cannot be
tuned: it is 1.00 px per px for as long as the stage is stuck, at every
viewport, for any join whose two sides sit in different scroll contexts.

So the fact worth holding is not a measurement — it is the asymmetry that
forces it. This check derives that asymmetry from the markup and the
stylesheets rather than trusting the note, and then requires the note to record
what the asymmetry implies. Three ways it breaks:

  * the flow moves into the stage, or the stage stops being sticky — the seam
    becomes one number again and the note's two-regime record goes stale
  * the note's record is dropped in an edit, and the next reader of the pre-pin
    table takes it for the whole truth, exactly as happened here
  * the record names an ancestor that is not the sticky one, or a rate that is
    not the one the asymmetry forces

WHAT THIS CHECK DOES NOT DO. It does not close the seam. Closing it is a change
to how the root terminates or to what the stage carries — the drawing's form
and the section's architecture — which is the craft lane's, and the two tables
(pre-pin, in the .lp-flow note; post-pin, here) are the measurement it needs.
A form change that closes the pre-pin gap at 1920 x 1080 and leaves the flow
outside the stage still opens this one at 1.00 px per px, which is the whole
reason the second number has to travel with the first.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-seam-travel.py
    python3 scripts/check-seam-travel.py -v
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "design-system" / "prototypes" / "statement-to-process.html"
SHIPPING = [ROOT / "design-system" / "assets" / "css" / n
            for n in ("tokens.css", "base.css", "components.css")]

# The one declared handover on this page: who hands over, and who receives.
SEAM = ("lp-flow", "lp-frame")

# The record the note must carry, in a grammar this check can resolve rather
# than merely match. Both the ancestor and the rate are verified against the
# markup and the stylesheets below.
RECORD_RE = re.compile(
    r"SEAM TRAVEL:\s*\.(?P<out>[\w-]+)\s+is\s+outside\s+\.(?P<sticky>[\w-]+)\s*"
    r"\(position:\s*sticky\).*?"
    r"(?P<rate>\d+\.\d\d)\s*px per px",
    re.S,
)

TAG_RE = re.compile(r"<(/?)([a-zA-Z][\w:-]*)((?:\"[^\"]*\"|'[^']*'|[^>\"'])*?)(/?)>")
CLASS_RE = re.compile(r"""\bclass\s*=\s*["']([^"']*)["']""")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr", "path", "circle", "rect",
        "line", "stop", "use", "ellipse", "polygon", "polyline", "image"}


def strip_comments(text):
    """Comments carry class names in prose; they are not markup."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def ancestor_classes(markup, wanted):
    """For each class in `wanted`, the set of classes on its ancestors."""
    found = {}
    stack = []
    for m in TAG_RE.finditer(markup):
        closing, tag, attrs, self_closing = m.groups()
        tag = tag.lower()
        if closing:
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == tag:
                    del stack[i:]
                    break
            continue
        classes = set()
        cm = CLASS_RE.search(attrs)
        if cm:
            classes = set(cm.group(1).split())
        for w in wanted:
            if w in classes and w not in found:
                found[w] = {c for _, cs in stack for c in cs}
        if not (self_closing or tag in VOID):
            stack.append((tag, classes))
    return found


def sticky_classes(sources):
    """Class names whose rule declares position: sticky or fixed."""
    out = {}
    for name, css in sources:
        # a rule is a selector list up to '{', then declarations up to '}'
        for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            pm = re.search(r"(?<![-\w])position\s*:\s*(sticky|fixed)\s*[;!}]", body + "}")
            if not pm:
                continue
            for cls in re.findall(r"\.([\w-]+)", sel):
                out.setdefault(cls, (name, pm.group(1)))
    return out


def main():
    p = argparse.ArgumentParser(description="A seam between two scroll contexts is two numbers.")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    if not PAGE.exists():
        print("seam travel: patterns/landing-page.html is gone — the selector went stale")
        return 1
    text = PAGE.read_text(encoding="utf-8")
    markup = strip_comments(text)

    sources = [(f.name, f.read_text(encoding="utf-8")) for f in SHIPPING if f.exists()]
    local = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", text, re.S))
    sources.append(("landing-page.html (page-local)", local))
    sticky = sticky_classes(sources)

    hands_over, receives = SEAM
    anc = ancestor_classes(markup, set(SEAM))
    findings = []
    for cls in SEAM:
        if cls not in anc:
            findings.append(f".{cls} is not in the markup — the seam's {'giving' if cls == hands_over else 'receiving'} side went stale")
    if findings:
        print(f"\nseam travel: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1

    out_sticky = sorted(anc[hands_over] & set(sticky))
    in_sticky = sorted(anc[receives] & set(sticky))

    if args.verbose:
        print(f"  .{hands_over} ancestors in a sticky/fixed context: {out_sticky or 'none'}")
        print(f"  .{receives} ancestors in a sticky/fixed context: {in_sticky or 'none'}")
        for c in in_sticky:
            print(f"    .{c}: position: {sticky[c][1]} — {sticky[c][0]}")

    shared = set(out_sticky) & set(in_sticky)
    asymmetric = sorted(set(in_sticky) - set(out_sticky))

    m = RECORD_RE.search(text)

    if not asymmetric:
        if m:
            findings.append(
                f"the note carries a SEAM TRAVEL record, but .{hands_over} and .{receives} now "
                f"share every scroll context they sit in ({sorted(shared) or 'none'}) — the seam is "
                f"one number again and the record is stale"
            )
    else:
        holder = asymmetric[-1]
        if not m:
            findings.append(
                f".{receives} sits inside .{holder} (position: {sticky[holder][1]}, "
                f"{sticky[holder][0]}) and .{hands_over} does not, so the gap between them opens "
                f"1.00 px per px of scroll from the moment .{holder} sticks — and nothing in "
                f"{PAGE.name} records it. The pre-pin table in the .{hands_over} note reads as "
                f"the seam's whole behaviour and is half of it."
            )
        else:
            if m.group("out") != hands_over:
                findings.append(
                    f"the SEAM TRAVEL record says .{m.group('out')} is the side outside the "
                    f"sticky context; the markup says it is .{hands_over}"
                )
            if m.group("sticky") != holder:
                findings.append(
                    f"the SEAM TRAVEL record names .{m.group('sticky')} as the sticky ancestor; "
                    f"the one .{receives} actually sits inside and .{hands_over} does not is "
                    f".{holder}"
                )
            elif sticky[holder][1] != "sticky":
                findings.append(
                    f"the SEAM TRAVEL record says .{holder} is position: sticky; "
                    f"{sticky[holder][0]} declares position: {sticky[holder][1]}"
                )
            if m.group("rate") != "1.00":
                findings.append(
                    f"the SEAM TRAVEL record states {m.group('rate')} px per px. A held layer "
                    f"against a travelling one separates at exactly the scroll delta: 1.00"
                )

    if findings:
        print(f"\nseam travel: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1

    if not asymmetric:
        print(f"seam travel OK — .{hands_over} and .{receives} share their scroll contexts, "
              f"so the seam is one number and no travel record is owed")
    else:
        print(f"seam travel OK — .{receives} sits inside .{asymmetric[-1]} (position: sticky) and "
              f".{hands_over} does not, and the note records the 1.00 px per px that asymmetry "
              f"forces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
