#!/usr/bin/env python3
"""Two drawings are the same width, or the seam between them is a coincidence.

The fifty-second check, and it is check-flow-handover.py's own blind spot — the one
assumption that check makes, states in prose, and never reads.

WHAT HANDOVER ACTUALLY CHECKS. The flow's fourteen drops end at the foot of a
1200-unit viewBox; the lectern's rails span a 1000-unit one. Handover maps one
onto the other with a single line:

    basis = frame_vb[2] / flow_vb[2]

and then proves, exactly, that every drop lands inside the top rail's span and
that every vertical continues a drop. That proof is worth exactly as much as the
sentence above the line, which is this one:

    "Both drawings are the same width by construction: --lp-measure is declared
     once on main, .lp-proc-stage passes it to the card as --pin-measure, and
     .lp-flow reads it directly. So the two viewBoxes share a width basis, and a
     flow x maps to a frame x by 1000/1200 exactly."

BY CONSTRUCTION IS A CSS CHAIN, AND NOTHING READ IT. Four declarations, in two
files, none of them in the markup handover parses:

    landing-page.html   main            { --lp-measure: calc((100vh - 13rem) * 2) }
    landing-page.html   .lp-proc-stage  { --pin-measure: var(--lp-measure) }
    landing-page.html   .lp-flow        { width: min(100%, var(--lp-measure)) }
    components.css      .cf-pin__inner > * { max-inline-size: var(--pin-measure, none) }

Break any one of them and the two boxes are different page widths, all fourteen
drops land beside the lectern instead of on it — and handover still prints OK,
because the two viewBox attributes it reads never moved. Measured on the shipped
page at 1440 x 900 with the second declaration changed to
`calc(var(--lp-measure) * 0.92)`, which is the smallest edit that breaks it:

    flow box    x   79.98   w 1280.02      unchanged
    lectern box x   83.36   w 1273.27      3.38 px right, 6.75 px narrow

    left taproot  (flow x 0)     4.69 px off the lectern's left vertical
    right taproot (flow x 1200)  4.68 px off the lectern's right vertical
    centre drop   (flow x 600)   3.27 px off the top rail's own T-junction

Every one of the repository's checks stayed green on that state, this one
included until it existed. It is the picture #176 was opened for and #183
re-opened — fourteen strokes ending beside the thing they are drawn to arrive
on — reached from the one direction no gate was watching.

AND THIS SEAM'S HISTORY IS ENTIRELY CSS-SIDE. #177 was the stage narrowing and
the card not being told; #178 was the frame standing 1 px inside the border it
replaced. Neither was a markup edit. The x arrivals are the half of this seam
that IS bought — the y half is recorded in the .lp-flow note's table and belongs
to the craft lane — and what bought them was these four declarations, not the
`d` attributes handover reads.

WHAT IS CHECKED, on every pattern page that carries both drawings:

  1. ONE MEASURE, ONE PLACE. --lp-measure is declared exactly once. A second
     declaration under a selector only one consumer inherits from diverges the
     two boxes silently, at one viewport, in a media query nobody re-reads.

  2. THE PASS-THROUGH IS BARE. .lp-proc-stage's --pin-measure is exactly
     `var(--lp-measure)`. Not a calc on it, not a clamp of it, not a fallback
     that resolves to something else — any arithmetic here is the 0.92 above.

  3. ONE PIN-MEASURE, ONE PLACE, for the same reason as 1.

  4. THE FLOW READS THE MEASURE ITSELF. The rule that sizes .lp-flow caps its
     width at var(--lp-measure) AND at its container, in one min().

  5. THE CARD READS THE PASS-THROUGH. components.css caps .cf-pin__inner's
     inline size at var(--pin-measure).

  6. THE TWO CAPS ARE THE SAME CAP. Both are min(container, measure) — the
     flow's written out, the card's as a max-inline-size, which is the same
     function. If one gained a term the other has not, they stop agreeing at
     the viewport where that term binds, which is the shape of every previous
     break at this seam.

What this cannot check is that the two containers are the same width; both are
.container and the markup says so in two places. That is one link of prose left,
against four that were, and it is the link no edit to the drawing can touch.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
# The statement-to-process chain moved to prototypes/ on 2026-07-28;
# these checks follow the drawing, not the folder.
PROTOTYPES = ROOT / "design-system" / "prototypes"
COMPONENTS = ROOT / "design-system" / "assets" / "css" / "components.css"

COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S)


def strip_comments(css):
    return COMMENT_RE.sub(" ", css)


def rules(css):
    """(selector, declaration-block) for every rule, at any nesting depth.

    Written rather than imported because the only alternative in this repo's
    toolchain is a regex over the whole file, and a regex cannot tell a
    declaration inside @media from one beside it — which is finding 1's whole
    subject."""
    css = strip_comments(css)
    out, depth, buf, stack = [], 0, "", []
    i = 0
    while i < len(css):
        c = css[i]
        if c == "{":
            head = buf.strip()
            buf = ""
            stack.append(head)
            depth += 1
        elif c == "}":
            head = stack.pop() if stack else ""
            if not head.startswith("@"):
                out.append((head, buf))
            buf = ""
            depth -= 1
        else:
            buf += c
        i += 1
    return out


def declarations(block):
    for decl in block.split(";"):
        if ":" not in decl:
            continue
        prop, _, value = decl.partition(":")
        yield prop.strip(), " ".join(value.split())


def selects(selector, needle):
    return any(needle in part for part in selector.split(","))


def find(page_rules, prop):
    """Every declaration of prop, with the selector it was made under."""
    return [(sel, val) for sel, block in page_rules
            for p, val in declarations(block) if p == prop]


def caps_at(value, term):
    """The value caps at term inside a min() — the one function that means
    'no wider than', which is what both consumers have to be doing."""
    for call in re.findall(r"min\(([^()]*(?:\([^()]*\)[^()]*)*)\)", value):
        if term in call:
            return True
    return False


def check_page(page, comp_rules, verbose):
    text = page.read_text(encoding="utf-8")
    if 'class="lp-flow"' not in text:
        return [], False

    page_rules = []
    for block in STYLE_RE.findall(text):
        page_rules += rules(block)

    findings = []

    # 1. ONE MEASURE, ONE PLACE.
    measures = find(page_rules, "--lp-measure")
    if len(measures) != 1:
        where = ", ".join(f"{sel.strip()!r}" for sel, _ in measures) or "nowhere"
        findings.append(
            f"{page.name}: --lp-measure is declared {len(measures)} times ({where}). "
            f"The flow reads it a section above the card that reads it through "
            f"--pin-measure; a second declaration either consumer does not inherit "
            f"parts the two boxes at whichever viewport it binds.")
        measure_sel, measure_val = (measures[0] if measures else ("", ""))
    else:
        measure_sel, measure_val = measures[0]

    # 2. THE PASS-THROUGH IS BARE.
    pins = find(page_rules, "--pin-measure")
    for sel, val in pins:
        if val != "var(--lp-measure)":
            findings.append(
                f"{page.name}: {sel.strip()} passes --pin-measure as {val!r}, not the bare "
                f"var(--lp-measure). Arithmetic here is exactly what parts the lectern "
                f"from the drops — a 0.92 on this line puts all fourteen 3 to 5 px "
                f"beside the rails while every check still passes.")

    # 3. ONE PIN-MEASURE, ONE PLACE.
    if len(pins) != 1:
        where = ", ".join(f"{sel.strip()!r}" for sel, _ in pins) or "nowhere"
        findings.append(
            f"{page.name}: --pin-measure is declared {len(pins)} times ({where}); "
            f"the card takes one width and the drawing above it takes another.")

    # 4. THE FLOW READS THE MEASURE ITSELF.
    flow_caps = [(sel, prop, val) for sel, block in page_rules
                 if selects(sel, ".lp-flow")
                 for prop, val in declarations(block)
                 if prop in ("width", "inline-size", "max-width", "max-inline-size")]
    if not any(caps_at(val, "var(--lp-measure)") for _, _, val in flow_caps):
        findings.append(
            f"{page.name}: no rule on .lp-flow caps its width at var(--lp-measure) "
            f"inside a min(). The drawing then takes its container's width and the "
            f"lectern takes the measure, and check-flow-handover.py maps one onto "
            f"the other regardless — its basis is the two viewBox attributes, which "
            f"a change here never touches. Found: "
            f"{[f'{p}: {v}' for _, p, v in flow_caps] or 'no width declaration at all'}")

    # 6a. THE FLOW'S CAP IS ALSO A CONTAINER CAP.
    if not any(caps_at(val, "var(--lp-measure)") and "100%" in val
               for _, _, val in flow_caps):
        findings.append(
            f"{page.name}: .lp-flow caps at the measure but not at its container in the "
            f"same min(). The card's cap is a max-inline-size, which is min(container, "
            f"measure) by definition; a flow that is only min()'d against the measure "
            f"overflows its column at every width the measure does not bind.")

    # 5. THE CARD READS THE PASS-THROUGH.
    card_caps = [(sel, prop, val) for sel, block in comp_rules
                 if selects(sel, ".cf-pin__inner")
                 for prop, val in declarations(block)
                 if prop in ("max-inline-size", "max-width")]
    if not any("var(--pin-measure" in val for _, _, val in card_caps):
        findings.append(
            f"components.css: no max-inline-size on .cf-pin__inner reads "
            f"var(--pin-measure), so the page's measure reaches the drawing and not "
            f"the lectern it hands over to. Found: "
            f"{[f'{p}: {v}' for _, p, v in card_caps] or 'no inline-size cap at all'}")

    if verbose:
        print(f"  {page.name}: --lp-measure on {measure_sel.strip()!r} = {measure_val}")
        for sel, val in pins:
            print(f"    --pin-measure on {sel.strip()!r} = {val}")
        for sel, prop, val in flow_caps:
            print(f"    {sel.strip()!r} {prop}: {val}")
        for sel, prop, val in card_caps:
            print(f"    components.css {sel.strip()!r} {prop}: {val}")

    return findings, True


def main():
    parser = argparse.ArgumentParser(
        description="Two drawings are the same width, or the seam is a coincidence.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the whole chain, declaration by declaration")
    args = parser.parse_args()

    comp_rules = rules(COMPONENTS.read_text(encoding="utf-8"))

    findings, seams = [], 0
    for page in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
        f, found = check_page(page, comp_rules, args.verbose)
        findings += f
        seams += 1 if found else 0

    if not seams:
        print("shared measure: no page carries the drawing — the selector went stale")
        return 1
    if findings:
        print(f"\nshared measure: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"shared measure OK — {seams} seam(s): one --lp-measure, passed bare to "
          f"--pin-measure, capped the same way by the drawing and by the lectern")
    return 0


if __name__ == "__main__":
    sys.exit(main())
