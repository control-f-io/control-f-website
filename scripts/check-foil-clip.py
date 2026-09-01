#!/usr/bin/env python3
"""The foil's clip box is capped at its ink, and `fit-content()` cannot do it.

`background-clip: text` clips a background painted across the WHOLE element
box. A display headline in a block is as wide as its column however short the
words are, so an uncapped .text-foil samples only the first fraction of its
ramp: Weiss and Glas render, Sky barely arrives, and Violett -- the far end of
the brand's own spectrum, and the whole reason the foil is a foil -- never
appears on the page at all. base.css states that in as many words and calls it
load-bearing.

IT HAD BEEN STATED AND NOT SHIPPED. The cap was written `width:
fit-content(100%)`, described in three places as "the function, with an
explicit stretch basis". `fit-content()` is css-sizing-4 GRID TRACK SIZING; no
engine implements it as a value of a box property, and `CSS.supports("width",
"fit-content(100%)")` is false on Chromium 141. The declaration was
guaranteed-invalid and dropped, and the class had `width: auto` for as long as
the line existed. Measured on the shipped tree at 1280, ink over box:

    Über uns   23.6 %      Karriere  21.1 %
    Suche      16.7 %      News      14.8 %

The measurement that put the function form there could not have caught this.
It was an h3 in a 100 px box: the bare keyword rendered 277.84 px, the
function form rendered 100 -- which is exactly what a DROPPED width does in a
100 px box. A dropped declaration and a working clamp are the same number when
the box IS the containing block, and that was the only case the isolated test
had.

So this script asks two questions, and the second is the general form of the
first:

  1. THE CAP EXISTS, as a max-width off the content rather than as a width.
     `width` with an intrinsic keyword asks a box to size itself from its own
     content, which is cyclic wherever the content is written by script --
     measured on expertise.html, where cf-stream.js empties the element it
     types into: `width: max-content` collapsed all four card titles to 22 px
     and 0. `max-width: max-content` over `width: auto` is min(max-content,
     available) written as the one property that cannot be cyclic.

  2. NO BOX PROPERTY ANYWHERE IN THE SHIPPING CSS TAKES `fit-content()`.
     That is the defect one level up from the one that happened: a value no
     engine implements renders as no value, silently, and the thing it was
     supposed to do is then documented as done. It is legitimate in a grid or
     flex track list and nowhere else, so the track-list properties are the
     exemption and every other property is an error.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-foil-clip.py       # check, exit 1 on drift
    python3 scripts/check-foil-clip.py -v    # list every declaration considered
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# The shipping stylesheets. docs.css is documentation chrome and does not ship,
# which is the boundary check-glass-budget.py and check-gradient-family.py both
# already draw.
CSS = ("tokens.css", "base.css", "components.css", "acts.css")

# Where `fit-content()` is a real value: a grid or flex track list. Everything
# else is a box property and takes the keyword or nothing.
TRACK_PROPS = {
    "grid-template-columns", "grid-template-rows", "grid-template-areas",
    "grid-auto-columns", "grid-auto-rows", "grid-template", "grid",
    "flex-basis",
}

DECL = re.compile(r"([-a-zA-Z]+)\s*:\s*([^;{}]+)", re.S)
COMMENT = re.compile(r"/\*.*?\*/", re.S)


def strip_comments(text):
    """Blank the comments and KEEP THE LINE COUNT, so a reported line is real.

    Substituting a single space collapses every newline inside a comment, and
    this file's comments are the length of essays: the first version of this
    script reported the clip-box rule at base.css:646, twelve hundred lines
    off, and printed it with the confidence of a line number.
    """
    return COMMENT.sub(lambda m: "\n" * m.group(0).count("\n") or " ", text)


def line_of(text, index):
    return text[:index].count("\n") + 1


def rule_bodies(text):
    """(selector, body, line) for every rule in one stylesheet, at-rules flattened.

    A brace-counting walk rather than a regex, because the clip-box rule lives
    two levels in -- inside @supports -- and a regex for `.text-foil {...}`
    reads straight past the nesting and answers about the wrong rule.

    The selector is whatever stands between the previous structural character
    -- an opening brace, a closing brace or a semicolon -- and this rule's own
    opening brace, which is the same span a parser would take it from.
    """
    out, stack, mark = [], [], 0
    for i, ch in enumerate(text):
        if ch == "{":
            stack.append((text[mark:i].strip(), i))
            mark = i + 1
        elif ch == "}":
            if stack:
                head, open_at = stack.pop()
                out.append((head, text[open_at + 1:i], line_of(text, open_at)))
            mark = i + 1
        elif ch == ";":
            mark = i + 1
    return out


def declarations(body):
    """Only this rule's own declarations -- nothing inside a nested block."""
    flat, depth, cur = [], 0, ""
    for ch in body:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            continue
        if depth == 0:
            cur += ch
    for m in DECL.finditer(cur):
        yield m.group(1).strip().lower(), " ".join(m.group(2).split())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    findings, seen = [], []

    # --- 2. fit-content() on a box property, anywhere it ships ---------------
    for name in CSS:
        path = DS / "assets" / "css" / name
        text = strip_comments(path.read_text(encoding="utf-8"))
        for m in DECL.finditer(text):
            prop, value = m.group(1).strip().lower(), " ".join(m.group(2).split())
            if "fit-content(" not in value:
                continue
            where = "%s:%d" % (name, line_of(text, m.start()))
            if prop in TRACK_PROPS:
                seen.append(("ok  ", where, prop, value[:60]))
                continue
            findings.append(
                "%s  `%s: %s` -- fit-content() is grid track sizing. On a box "
                "property no engine implements it, so the declaration is "
                "guaranteed-invalid and dropped. Use the bare `fit-content` "
                "keyword, or a max-width off the content." % (where, prop, value))
            seen.append(("FAIL", where, prop, value[:60]))

    # --- 1. the clip box is capped, and capped the right way ----------------
    base = strip_comments((DS / "assets" / "css" / "base.css").read_text(encoding="utf-8"))
    capped, widths = [], []
    for sel, body, line in rule_bodies(base):
        if ".text-foil" not in sel:
            continue
        for prop, value in declarations(body):
            if prop == "max-width" and "max-content" in value:
                capped.append((sel, line))
                seen.append(("ok  ", "base.css:%d" % line,
                             " ".join(sel.split())[:44], "%s: %s" % (prop, value)))
            elif prop in ("width", "inline-size") and re.search(
                    r"\b(max-content|min-content|fit-content)\b", value):
                widths.append((sel, line, value))
                seen.append(("FAIL", "base.css:%d" % line,
                             " ".join(sel.split())[:44], "%s: %s" % (prop, value)))

    if not capped:
        findings.append(
            "base.css: .text-foil has no `max-width: max-content`. The clip box "
            "is then the column, and the ramp dies inside the first words -- see "
            "THE CLIP BOX IS SIZED TO THE TEXT.")
    for sel, line, value in widths:
        findings.append(
            "base.css:%d  `%s` sizes .text-foil's box from its own content "
            "(`width: %s`). That is cyclic wherever a script writes the content: "
            "cf-stream.js empties the element it types into, and the four card "
            "titles on expertise.html collapsed to 22 px and 0. Cap with "
            "max-width instead." % (line, sel.strip()[:40], value))

    if args.verbose:
        for status, where, prop, value in seen:
            print("%-4s %-22s %-44s %s" % (status, where, prop, value))
        print()

    if findings:
        print("check-foil-clip: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  " + f + "\n")
        return 1

    print("check-foil-clip: the clip box is capped at the ink, and no box "
          "property takes fit-content()")
    return 0


if __name__ == "__main__":
    sys.exit(main())
