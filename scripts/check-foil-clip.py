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

AND THE CAP HAD AN EXCLUSION THE SCRIPT TOOK ON TRUST. `max-width:
max-content` is written `.text-foil:not(:has(.cf-stream__text))`, because
capping a rewritten element at its own content is cyclic -- the reason is
sound and it is measured. What was never measured is what the excluded case
then renders. It is the four card titles on expertise.html, which are the four
largest foil moments in the system, and on the rendered page they sat 136-406
px of ink inside a 518 px box at 1280 and a 593 px one at 1920:

    Maschinenbau           53.4 % of the ramp at 1280,  46.6 % at 1920
    Erneuerbare Energien   78.4 %                       68.4 %
    Großanlagen            47.0 %                       41.1 %
    Flotten                26.2 %                       22.9 %

Sampled against --gradient-foil-ink, whose stops sit at 0 / 23.5 / 47 / 73.5 /
100 %, VIOLETT 800 APPEARED ON NONE OF THEM AT EITHER WIDTH, and at 1920 two
of the four did not reach Sky 800 either. That is the same sentence the header
opens with, printed by the exemption instead of by the missing declaration --
which is why a gate that only asks whether the cap EXISTS cannot see it.
cf-stream.js publishes the element's real max-content as --stream-inline
before it empties it, and the excluded case caps on that; question 3 below is
what holds the pair together.

So this script asks three questions, and each is the general form of the one
before it:

  1. THE CAP EXISTS, as a max-width off the content rather than as a width.
     `width` with an intrinsic keyword asks a box to size itself from its own
     content, which is cyclic wherever the content is written by script --
     measured on expertise.html, where cf-stream.js empties the element it
     types into: `width: max-content` collapsed all four card titles to 22 px
     and 0. `max-width: max-content` over `width: auto` is min(max-content,
     available) written as the one property that cannot be cyclic.

  3. NOTHING IS EXCLUDED FROM THE CAP WITHOUT BEING CAPPED ANOTHER WAY, and
     the number it is capped on is one something actually sets. A
     `.text-foil:not(:has(...))` cap has to be answered by a
     `.text-foil:has(...)` one; that answer has to clamp at the available
     space, so a reservation wider than the column cannot widen the box; and
     every custom property it caps on has to be written by a shipping script.
     A cap on a var nothing sets is `max-width: 100%` wearing an argument --
     the same shape of failure as a value no engine implements, one level of
     indirection out.

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
# `:not(:has(X))` -- the shape an exclusion from the cap takes. X is what the
# answering rule has to select on.
EXCLUSION = re.compile(r":not\(\s*:has\(\s*([^)]+?)\s*\)\s*\)")
VAR = re.compile(r"var\(\s*(--[\w-]+)")
# A whole var() call, fallback and all, so the clamp test below reads the cap's
# own terms rather than a fallback that only looks like one.
VAR_CALL = re.compile(r"var\(\s*--[\w-]+\s*(?:,[^()]*)?\)")


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
    scripts = [p.read_text(encoding="utf-8")
               for p in sorted((DS / "assets" / "js").glob("*.js"))]

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
    capped, widths, excluded, answers = [], [], [], []
    for sel, body, line in rule_bodies(base):
        if ".text-foil" not in sel:
            continue
        flat = " ".join(sel.split())
        for prop, value in declarations(body):
            if prop == "max-width" and "max-content" in value:
                capped.append((sel, line))
                for m in EXCLUSION.finditer(flat):
                    excluded.append((m.group(1), flat, line))
                seen.append(("ok  ", "base.css:%d" % line, flat[:44],
                             "%s: %s" % (prop, value)))
            elif prop == "max-width" and ":has(" in flat and ":not(" not in flat:
                answers.append((flat, line, value))
                seen.append(("ok  ", "base.css:%d" % line, flat[:44],
                             "%s: %s" % (prop, value)))
            elif prop in ("width", "inline-size") and re.search(
                    r"\b(max-content|min-content|fit-content)\b", value):
                widths.append((sel, line, value))
                seen.append(("FAIL", "base.css:%d" % line, flat[:44],
                             "%s: %s" % (prop, value)))

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

    # --- 3. the exclusion is answered, clamped, and caps on a real number ----
    #
    # An exclusion is `:not(:has(X))` on the rule that carries the cap. Its
    # answer is a rule matching the same X with no negation, setting max-width
    # of its own. Matching on the ARGUMENT and not on the whole selector is the
    # point: the two rules are a pair by what they select, so a second
    # exclusion added later needs its own answer rather than inheriting this
    # one's.
    for arg, sel, line in excluded:
        pair = [a for a in answers if arg in a[0]]
        if not pair:
            findings.append(
                "base.css:%d  `%s` excludes `%s` from the cap and nothing caps "
                "it instead. The excluded box is then the column, which is what "
                "the cap exists to stop -- measured on expertise.html, the four "
                "card titles rendered 22.9-78.4 %% of --gradient-foil-ink and "
                "Violett 800 appeared on none of them." % (line, sel[:52], arg))
            continue
        for answer, at, value in pair:
            # The clamp has to be the CAP's own term, not a var()'s fallback.
            # `max-width: var(--x, 100%)` reads as clamped and is not: when the
            # property is set it is the whole of the cap, and a reservation
            # wider than the column widens the box. So the fallbacks come out
            # before the term is looked for.
            outer = VAR_CALL.sub("", value)
            if "100%" not in outer:
                findings.append(
                    "base.css:%d  `%s` answers the exclusion with `max-width: "
                    "%s` and never clamps at the available space. A reservation "
                    "wider than the column would then widen the box; the cap is "
                    "min(max-content, available) and both halves have to say "
                    "so." % (at, answer[:52], value))
            for prop in set(VAR.findall(value)):
                if not any(("setProperty('%s'" % prop) in js
                           or ('setProperty("%s"' % prop) in js for js in scripts):
                    findings.append(
                        "base.css:%d  `%s` caps on `var(%s)` and no shipping "
                        "script sets it. An unset custom property falls back, "
                        "so the cap silently becomes its fallback -- a value no "
                        "engine implements and a value nothing supplies fail "
                        "the same way, and neither leaves a mark."
                        % (at, answer[:52], prop))
                else:
                    seen.append(("ok  ", "assets/js", prop, "set by a shipping script"))

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
