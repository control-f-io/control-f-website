#!/usr/bin/env python3
"""Hold the ground under a bounded key to the number of lines that key can take.

A "bounded key" is this system's name for a label absolutely positioned under a
data point and confined to that point's own pitch — .cf-plot__key under a
column, .cf-block__key under a category. check-bound-key-wrap.py holds the two
declarations that decide HOW such a key breaks: `overflow-wrap: normal` takes
base.css's break-word net off, and `hyphens: manual` puts back only the breaks
the author placed with `&shy;`. This script holds the consequence of that pair,
which nothing checked: a key that is allowed to break is a key that can be two
lines tall, and the row it hangs under has to have reserved room for both.

WHAT WENT WRONG

The key is `position: absolute; top: 100%`, so it contributes no height at all.
Everything below it — the caption and its hairline — is held off by a fixed
reservation on the row's own box, and both figures reserved ONE label line:

    .cf-plot__set     margin-bottom: var(--space-8)   32 px
    .cf-block__frame  margin-block:  var(--space-8)   32 px

32 px is 8 px of drop (--space-2) plus one 11 px label at --leading-normal
(14.3 px) plus 9.7 px of air, and the comment over each rule said so. Two lines
are 28.6 px, which is 4.6 px more label than there was room for.

Both consumers that had already hit it bought the missing line back in the
CONSUMER rather than in the component: acts.css carried
`.lp-ev-card .cf-plot__set` and `.lp-ev-card .cf-block__frame` at --space-12,
one rung up, with a comment that named the fault exactly — "where a key takes
two lines the second line would print into the caption". Every other consumer
was still on one line. patterns/blog-artikel.html is the one that shows it:
its plot's German keys carry authored breaks, and measured against the
caption's hairline, with a positive number meaning the label ends below the
rule —

                       320      375      414      768     1024     1440
      lines             2        2        2        2        1        1
      key bottom     +4.59    +4.59    +4.59    +4.59    -9.70    -9.70

— so ZEIT/ZONE and AB/TASTUNG were drawn with the caption rule through the
bottom of their second line at every width the phone and tablet tiers cover,
and the figure only came right at 1024 px where the column is wide enough that
nothing wraps. Fixed by moving the rung into the components: --space-12 for
both rows, which is the drop plus two labels plus 11.4 px of air.

WHAT THIS SCRIPT CHECKS

For each bounded key, the room reserved under its row must cover the drop plus
every line that key can take. All four numbers are read out of the files:

  the drop        the key rule's own `margin-top`, resolved through the space
                  scale in tokens.css
  the line        the key rule's `font-size` x `line-height`, resolved through
                  --text-xs and --leading-normal
  the reservation the bottom margin or padding of the row the key hangs under
                  — and of every rule anywhere in the shipping stylesheets
                  whose selector ends in that row's class, because an override
                  can only be trusted to ADD room if it is read
  the lines       two, where any instance of that key carries an authored
                  `&shy;`, and one where none does. `hyphens: manual` means a
                  key breaks at an authored break and nowhere else, so whether
                  a key CAN take a second line is a fact about the markup and
                  not an estimate.

THE COUNT STOPS AT TWO, AND THAT IS A LIMIT WORTH STATING. 1 + the number of
authored breaks is the true upper bound on a key's line count, and reading it
that way was this script's first draft. It over-reads: an engine breaks a key
as many times as the pitch makes it and no more, so a name carrying three
breaks does not thereby take four lines. patterns/landing-page.html is the case
— its TECH&shy;NO&shy;LO&shy;GIE and SI&shy;CHER&shy;HEIT carry three breaks
and two, and measured across thirteen widths from 280 to 1920 the figure sets
them on one line from 600 px, two from 375, three at 320 and 360, and four at
280. Demanding four lines of every .cf-block would have widened a figure on
every page in the system to reserve for a wrap that only happens on one of
them, below the narrowest tier the register admits.

So the rung this script holds is the rung the system decided on — a key that
can break gets two lines of ground — and a key with MORE than one authored
break is outside what any fixed reservation can promise. Those are listed under
-v rather than failed, and the widths where one of them exceeds two lines are a
finding about that page's own key, not about the component's reservation.

Reading the overrides is the second half, and it is there because of a
recorded incident rather than for symmetry. `.lp-ev-card .cf-plot__set` was
once written `margin-bottom: var(--space-10)`. There is no --space-10 — the
scale runs 1 2 3 4 5 6 8 12 16 20 24 30 40 — so the declaration was invalid at
computed-value time and margin-bottom computed to 0; because the rule still WON
the cascade against the component, it did not fall back to the component's
reservation, it removed it, and the keys printed 10 px into the caption. An
override that names a token the scale does not have fails here.

The pairing of a key class to the box that reserves room under it is the one
fact this script is told rather than derives: it is a statement about the
component's box model that no amount of parsing the stylesheet reveals. So that
it cannot go stale silently, the script also checks the OTHER direction — every
bounded key defined in components.css must appear in the table below. A new one
added without a row to hang under fails rather than going unchecked.

SCOPE

  design-system/assets/css/tokens.css        the space scale and the type
                                             tokens the arithmetic resolves
                                             through
  design-system/assets/css/components.css    where every bounded key and every
                                             row that reserves for one is
                                             defined
  tokens.css, base.css, components.css,      searched for overrides of a
  acts.css                                   reserving class. docs.css and
                                             preview.css never ship and are
                                             not read
  design-system/**.html, minus patterns/en/  the markup the line count comes
  and the generated beitrag-/stelle-/         from. The English edition is
  news-thema- pages                          generated and duplicates no fact;
                                             the article and vacancy pages are
                                             spliced from their specimens and
                                             carry the specimen's keys

Only the reader's default text size can move these numbers, and it moves them
together: the reservation, the drop and the label are all rem, so the ratio the
script checks holds at any root size. The arithmetic below is quoted at 16 px
because that is what the measurements above were taken at.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-key-line-reserve.py       # check, exit 1 on a finding
    python3 scripts/check-key-line-reserve.py -v    # print the whole derivation
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
TOKENS = CSS / "tokens.css"
COMPONENTS = CSS / "components.css"
SHIPPING = ["tokens.css", "base.css", "components.css", "acts.css"]

# The one fact the script is told. A bounded key is `top: 100%` on a box that
# contributes no height, so the room under it belongs to some ancestor's bottom
# margin or padding — which ancestor is a property of the component's
# construction, not of any declaration.
FAMILIES = {
    ".cf-plot__key": ".cf-plot__set",
    ".cf-block__key": ".cf-block__frame",
}

ROOT_PX = 16.0

COMMENT = re.compile(r"/\*.*?\*/", re.S)


def strip_comments(text):
    return COMMENT.sub("", text)


def leaf_rules(text):
    """Yield (selector, declaration-block) for every rule with no nested rule.

    Comments are stripped first: this stylesheet's prose quotes selectors and
    declarations at length, and a parser that reads them finds rules that do
    not exist.
    """
    text = strip_comments(text)
    out = []
    depth = 0
    start = 0
    sel_start = 0
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                sel = text[sel_start:i]
                start = i + 1
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                body = text[start:i]
                if "{" not in body:
                    out.append((" ".join(sel.split()), body))
                sel_start = i + 1
    return out


def declarations(body):
    """The last value wins, which is what the cascade does inside one block."""
    decls = {}
    for part in body.split(";"):
        if ":" not in part:
            continue
        name, _, value = part.partition(":")
        decls[name.strip().lower()] = " ".join(value.split())
    return decls


def read_scale(text):
    """--space-N and the two type tokens, as px at a 16 px root."""
    text = strip_comments(text)
    scale = {}
    for name, value in re.findall(r"(--space-\d+)\s*:\s*([^;]+);", text):
        value = value.strip()
        m = re.fullmatch(r"([\d.]+)rem", value)
        if not m:
            m = re.fullmatch(r"([\d.]+)px", value)
            if not m:
                continue
            scale[name] = float(m.group(1))
            continue
        scale[name] = float(m.group(1)) * ROOT_PX
    types = {}
    for name in ("--text-xs", "--leading-normal"):
        m = re.search(re.escape(name) + r"\s*:\s*([^;]+);", text)
        if m:
            types[name] = m.group(1).strip()
    return scale, types


def resolve_length(value, scale):
    """A length written as a token, or as a raw rem/px. Returns (px, note)."""
    value = value.strip()
    m = re.fullmatch(r"var\((--space-\d+)\)", value)
    if m:
        token = m.group(1)
        if token not in scale:
            return None, "%s is not on the space scale" % token
        return scale[token], token
    m = re.fullmatch(r"([\d.]+)rem", value)
    if m:
        return float(m.group(1)) * ROOT_PX, value
    m = re.fullmatch(r"([\d.]+)px", value)
    if m:
        return float(m.group(1)), value
    if value == "0":
        return 0.0, "0"
    return None, "not a resolvable length: %r" % value


def _bottom_of_shorthand(value):
    """The bottom component of a 1-to-4 value box shorthand."""
    parts = value.split()
    if len(parts) == 1 or len(parts) == 2:
        return parts[0] if len(parts) == 1 else parts[0]
    if len(parts) == 3 or len(parts) == 4:
        return parts[2]
    return None


def bottom_reservation(decls, scale):
    """The room a rule leaves under its own box.

    MARGIN AND PADDING ARE ADDED, NOT COMPARED. Reading them as competing
    declarations is what the first draft of this script did, and it made
    `.cf-plot__set { margin: 0 0 var(--space-12); padding: 0 }` report a
    reservation of zero — the padding is the later declaration, so it won a
    contest the box model never holds. Within each of the two properties the
    later declaration does win, which is the cascade inside one block.
    """
    got = {}
    notes = []
    for prop, value in decls.items():
        if prop in ("margin", "padding"):
            cand = _bottom_of_shorthand(value)
        elif prop in ("margin-block", "padding-block"):
            parts = value.split()
            cand = parts[-1] if len(parts) >= 2 else parts[0]
        elif prop in ("margin-bottom", "padding-bottom", "margin-block-end",
                      "padding-block-end"):
            cand = value
        else:
            continue
        if cand is None:
            continue
        px, note = resolve_length(cand, scale)
        if px is None:
            return None, "%s: %s" % (prop, note)
        got["padding" if prop.startswith("padding") else "margin"] = (px, prop, note)
    if not got:
        return None, None
    total = 0.0
    for kind in ("margin", "padding"):
        if kind in got:
            px, prop, note = got[kind]
            total += px
            notes.append("%s: %s" % (prop, note))
    return total, " + ".join(notes)


def html_sources():
    base = ROOT / "design-system"
    skip_dir = base / "patterns" / "en"
    generated = re.compile(r"^(beitrag|stelle|news-thema)-")
    for path in sorted(base.rglob("*.html")):
        if skip_dir in path.parents:
            continue
        if generated.match(path.name):
            continue
        yield path


def max_lines(key_class, verbose):
    """Two lines where any instance of this key can break, one where none can.

    Capped at two on purpose — see THE COUNT STOPS AT TWO in the docstring. The
    keys that carry more than one authored break are printed under -v, because
    a fixed reservation cannot promise them and somebody should be able to see
    which they are.
    """
    cls = key_class.lstrip(".")
    pattern = re.compile(
        r"<(\w+)[^>]*\bclass=\"[^\"]*\b" + re.escape(cls) + r"\b[^\"]*\"[^>]*>(.*?)</\1>",
        re.S,
    )
    count = 0
    breaking = []
    beyond = []
    for path in html_sources():
        text = path.read_text(encoding="utf-8")
        for _, inner in pattern.findall(text):
            count += 1
            breaks = inner.count("&shy;") + inner.count("­")
            if breaks:
                label = "%s: %s" % (path.relative_to(ROOT),
                                    re.sub(r"\s+", " ", inner).strip()[:40])
                breaking.append(label)
                if breaks > 1:
                    beyond.append("%s (%d breaks)" % (label, breaks))
    lines = 2 if breaking else 1
    if verbose:
        print("    %-16s %d instance(s), %d can break, so %d line(s) of ground"
              % (cls, count, len(breaking), lines))
        for label in beyond:
            print("      beyond a fixed reservation: %s" % label)
    return lines


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    findings = []

    scale, types = read_scale(TOKENS.read_text(encoding="utf-8"))
    if not scale or "--text-xs" not in types or "--leading-normal" not in types:
        print("check-key-line-reserve: cannot read the scale out of tokens.css")
        return 1

    rules = {}
    for sel, body in leaf_rules(COMPONENTS.read_text(encoding="utf-8")):
        rules.setdefault(sel, {}).update(declarations(body))

    # Every bounded key in components.css must be in the table. Same shape
    # test check-bound-key-wrap.py uses: a single-class __key rule, absolutely
    # positioned, without the point key's nowrap.
    bounded = set()
    for sel, decls in rules.items():
        if not re.fullmatch(r"\.[a-z0-9-]+__key", sel):
            continue
        if decls.get("position") != "absolute":
            continue
        if decls.get("white-space") == "nowrap":
            continue
        bounded.add(sel)
    for sel in sorted(bounded - set(FAMILIES)):
        findings.append(
            "%s is a bounded key with no row named for it in FAMILIES — the "
            "room under it is unchecked." % sel)
    for sel in sorted(set(FAMILIES) - bounded):
        findings.append(
            "%s is named in FAMILIES but is no longer a bounded key rule in "
            "components.css." % sel)

    if verbose:
        print("the arithmetic, at a %g px root" % ROOT_PX)

    for key_sel in sorted(set(FAMILIES) & bounded):
        row_sel = FAMILIES[key_sel]
        decls = rules[key_sel]

        drop, drop_note = resolve_length(decls.get("margin-top", ""), scale)
        if drop is None:
            findings.append("%s: cannot resolve its drop (%s)" % (key_sel, drop_note))
            continue

        size, _ = resolve_length(
            types["--text-xs"] if decls.get("font-size") == "var(--text-xs)"
            else decls.get("font-size", ""), scale)
        if size is None:
            findings.append("%s: cannot resolve its font-size" % key_sel)
            continue
        try:
            leading = float(types["--leading-normal"])
        except ValueError:
            findings.append("--leading-normal is not a unitless number")
            continue
        if decls.get("line-height") != "var(--leading-normal)":
            findings.append(
                "%s: line-height is %r, so the line this script computes is not "
                "the line the browser sets." % (key_sel, decls.get("line-height")))
            continue
        line = size * leading

        if verbose:
            print("  %s under %s" % (key_sel, row_sel))
            print("    drop %.1f px (%s), line %.1f px (%g x %g)"
                  % (drop, drop_note, line, size, leading))
        lines = max_lines(key_sel, verbose)
        needed = drop + lines * line

        # The component's own reservation and every override of it.
        seen = 0
        for name in SHIPPING:
            path = CSS / name
            if not path.exists():
                continue
            for sel, body in leaf_rules(path.read_text(encoding="utf-8")):
                if not any(part == row_sel or part.endswith(" " + row_sel)
                           for part in sel.split(",")):
                    continue
                reserve, note = bottom_reservation(declarations(body), scale)
                if reserve is None:
                    if note is None:
                        continue  # a rule about this row that reserves nothing
                    findings.append("%s (%s) %s: %s" % (sel, name, row_sel, note))
                    seen += 1
                    continue
                seen += 1
                covers = int((reserve - drop) // line) if line else 0
                ok = reserve + 0.01 >= needed
                if verbose:
                    print("    %-46s %-24s %6.1f px = drop + %d line(s)%s"
                          % (sel, name, reserve, covers, "" if ok else "  <-- short"))
                if not ok:
                    findings.append(
                        "%s (%s) reserves %.1f px under a key that can take %d "
                        "line(s): %.1f px of drop plus %d x %.1f px needs %.1f px, "
                        "so the label ends %.2f px past it."
                        % (sel, name, reserve, lines, drop, lines, line, needed,
                           needed - reserve))
        if seen == 0:
            findings.append(
                "%s: nothing in the shipping stylesheets reserves room under "
                "%s." % (key_sel, row_sel))

    if findings:
        print("check-key-line-reserve: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  " + f)
        return 1
    print("check-key-line-reserve: every bounded key's row reserves the lines "
          "its own markup can produce.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
