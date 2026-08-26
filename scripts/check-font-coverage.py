#!/usr/bin/env python3
"""A character the shipped font cannot draw is a width the engines choose.

The hundred-and-nineteenth, and the first about the two font files rather than
about the markup or the CSS that arranges them.

THE FAULT CLASS. Every other check here can be answered by reading a file: a
token that is not in the register, a track without a minimum, a link that lands
nowhere. This one cannot, because the text is right, the CSS is right, and the
fault is that a codepoint on the page is not in `assets/fonts/`. What happens
then is not an error and not a blank box — the engine picks a fallback face out
of the system it is running on and draws the character from that, and the two
engines do not pick the same one. The page renders. Nothing throws, nothing
overflows, no capture looks wrong. The element is simply a different width in
Firefox than it is in Chromium, and every measurement this repository took of
the layout around it was taken in one of the two.

WHAT IT COST. `scripts/gen-proto-field.py` grouped the thousands in its sensor
readings with U+2009 THIN SPACE. Neither shipped face has one — Geist and Geist
Mono both stop at U+0020 and U+00A0, which are the only two Zs codepoints in
either cmap — so it came from a fallback, and the fallbacks disagreed by a
factor of three:

                    U+2009 advance    "2 870 rpm"    .cf-annot__label
    Chromium 141       2.20 px          55.00 px         84.14 px
    Firefox 153        6.62 px          59.42 px         88.62 px

Measured on the shipped landing page at 1280 with the pinned tier active in
both engines. Twenty-one notes stand on that field; nineteen of them agree
between the engines to 0.05 px, which is rounding. S04 and S16 — the only two
readings with four digits, and so the only two carrying a separator — were
4.48 px wider in Firefox, against a label the field places by its own edge
among twenty other labels and a frame that crops them.

THREE THINGS SAY IT IS THE FONT AND NOT THE ENGINE. The same string set in
Geist rather than Geist Mono measures 3.2 px in both engines, because there the
two happen to land on the same fallback; U+0020 and U+00A0, which ARE in both
faces, measure 6.6 px in both engines at every size tried; and the English
edition of that page has always been 59.42 px in both, because build-i18n.py's
key_of() collapses `\\s+` and en.json therefore carries the reading with plain
spaces. Two editions of one drawing, built from one source, already differed —
and the German half was the one whose width depended on who was reading it.

THE RULE THIS KEEPS is narrower than "every character must be in the font", and
deliberately so. A missing letter is not this fault class: it is visible on
sight, in any engine, to anyone who opens the page once. A missing SEPARATOR is
invisible by construction — it has no ink — so the only evidence it leaves is a
number in a measurement nobody re-took. So what is asserted is the separators:
no page may carry a Unicode Zs codepoint other than the two the faces contain.
Zs comes from unicodedata rather than from a list typed here, so U+2007 FIGURE
SPACE, U+202F NARROW NO-BREAK SPACE, U+205F and the rest of the block are held
by the same clause that holds U+2009 without anyone having thought of them.

WHY THE PAIR IS A CONSTANT AND NOT READ FROM THE FILES. The faces ship as
woff2, whose table directory is Brotli-compressed, and there is no Brotli in
the standard library — reading the cmap here would put a third-party dependency
in front of a check that today needs nothing but python3, which is the whole
reason the other hundred and eighteen run in one job. The pair is therefore
recorded, with the reading that produced it: fontTools 4.63 over both files,
`getBestCmap()`, U+0020 at 600/1000 em in Geist Mono and 250/1000 in Geist,
U+00A0 at the same advance as U+0020 in each, and nothing else in Zs present in
either. A face swap is the one change that can falsify it, and a face swap is
not a thing that happens quietly: base.css names both files and the licence
sits beside them.

Exit 1 on any finding. Run with -v for the pages scanned and the Zs codepoints
each one uses.
"""

import argparse
import pathlib
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# Every Zs codepoint, from the character database rather than from a list.
SEPARATORS = {cp for cp in range(0x110000) if unicodedata.category(chr(cp)) == "Zs"}

# The two the shipped faces contain. See the note above for the reading.
IN_THE_FONT = {0x0020, 0x00A0}

FORBIDDEN = SEPARATORS - IN_THE_FONT

# The written pages, the prototypes they are built beside, and the documentation
# that renders in the same two faces. patterns/en/ is generated and is not read,
# for the reason check-a11y.py and its ninety siblings give: it carries the
# German page's markup by construction, and build-i18n.py --check is what holds
# the mirror to its source.
DIRS = ("patterns", "prototypes", "components", "foundations")


def pages():
    for name in DIRS:
        for path in sorted((DS / name).glob("*.html")):
            yield path
    for path in sorted(DS.glob("*.html")):
        yield path


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    findings = []
    scanned = []
    for path in pages():
        text = path.read_text(encoding="utf-8")
        used = {}
        for i, ch in enumerate(text):
            cp = ord(ch)
            if cp in FORBIDDEN:
                used.setdefault(cp, []).append(line_of(text, i))
        scanned.append((path.relative_to(ROOT), used))
        for cp, lines in sorted(used.items()):
            try:
                name = unicodedata.name(chr(cp))
            except ValueError:
                name = "unnamed"
            where = ", ".join(str(n) for n in lines[:6])
            more = f" and {len(lines) - 6} more" if len(lines) > 6 else ""
            findings.append(
                f"{path.relative_to(ROOT)}: U+{cp:04X} {name} on line(s) "
                f"{where}{more} ({len(lines)} occurrence(s)). Neither Geist nor "
                f"Geist Mono has this codepoint, so every engine draws it from a "
                f"fallback of its own and the box around it is a different width "
                f"in each. Use U+0020, or U+00A0 where the run must not break."
            )

    if args.verbose:
        for rel, used in scanned:
            mark = (
                ", ".join(f"U+{cp:04X} x{len(v)}" for cp, v in sorted(used.items()))
                if used
                else "-"
            )
            print(f"{str(rel):58s} {mark}")
        print()

    for f in findings:
        print(f"FINDING     {f}")
    if findings:
        print(f"\n{len(findings)} finding(s).")
        return 1
    print(
        f"OK  {len(scanned)} pages carry no space character outside the two the "
        f"shipped faces contain (U+0020, U+00A0); "
        f"{len(FORBIDDEN)} Zs codepoints are held"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
