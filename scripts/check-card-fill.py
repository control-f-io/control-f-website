#!/usr/bin/env python3
"""A card is a contour. The only fill inside one is a veil on a block.

The hundred-and-sixty-ninth check, and the third attempt to hold a rule that
this system has stated in prose since before the process card was drawn.

THE RULE, IN THE CHAPTER'S OWN WORDS. foundations/materials.html asks one
question of every panel — "is there something complex behind this, which
frosted glass would calm?" — and answers it "contour" for every card in the
system. foundations/colors.html closes the same argument from the token end: "a
panel that needs a surface takes the veil; a panel that needs a boundary takes
a contour. There is no third thing to reintroduce." A card is the second kind.
It is a box drawn with an edge, divided by more edges, and the fill it is
allowed is one veil on a block INSIDE it — the process card's note, which reads
as content inset into the card rather than as a plate under part of it.

THAT RULE HAS BEEN BROKEN THREE TIMES, ALL THREE ON THE SAME COMPONENT, and
each time by somebody who had read the chapter:

  --surface-card    on .cf-process          the card's own plate, grey-050,
                    while the census beside it said contour. Retired.
  --surface-raised  on .cf-process__panel   a second plate in the same grey
                    inside the first. One plate painted twice, half of it dead.
  --surface-lifted  on .cf-process__panel   a 26 % white veil on the copy half,
                    derived from the mockup, measured, argued in three files —
                    and on the rendered card a light block filling the right
                    half of a card whose left half is the page.

THE FIRST TWO WERE INVISIBLE AND THE THIRD WAS NOT, which is why prose could
not hold this. Two plates of the same grey cancel: the card looked exactly the
way it looks now and one declaration was doing nothing, so no screenshot,
review or measurement could find it. The third was visible in every screenshot
of the landing page for as long as it shipped, and shipped anyway, because it
arrived with a measurement behind it — mockups/landing-page.jpg genuinely does
draw that half as a light plate, +22 to +29 over the page margin. A rule that
loses to a measurement is a rule that needs a gate, not a better sentence.

AND THE SENTENCE WAS THERE. components/process-card.html's Don't list has said
"Don't fill the card" since the component was documented. The fill went on a
HALF of the card, which that sentence does not name and a reader adding a plate
to one column does not think it names. materials.html's panel census, the
register that says what every panel is made of, carried "contour" for both
halves the whole time and nothing read that column — the same shape of failure
check-glass-budget.py was written for one material over, and the reason its
docstring says a verdict "is prose by design".

WHAT IT CHECKS, over base.css, components.css and acts.css — the stylesheets
that ship, the same scope check-glass-budget.py draws:

  FILL      No card, and no part of a card, declares a SURFACE. A surface is a
            `background` or `background-color` that resolves to a colour. The
            exceptions are in ALLOWED below, each with the argument for it and
            the exact value it is allowed to carry.
  SPENT     Every entry in ALLOWED still names a rule that exists and still
            declares that value. A permission that outlives its rule is read by
            the next run as headroom, and it was never that — the direction
            check-glass-budget.py's 4b claim takes for the same reason.
  ROSTER    Every root in ROOTS still draws a contour in the shipping CSS. A
            card that stopped being a bordered box, or was renamed, takes its
            entry with it rather than leaving a name nothing holds.
  SCOPE     Every class in the shipping CSS whose NAME says card belongs to a
            root in ROOTS. This is the clause that survives the next component:
            a `.cf-x-card` added by a lane that never opened this file fails
            here on the day it lands.
  READABLE  A background on a card family selector that this script cannot
            classify is a finding rather than a pass. The same move
            check-glass-budget.py makes with its unreducible selectors: a
            checker that quietly skips what it cannot read is a checker whose
            coverage is a guess.

WHAT IS NOT A SURFACE, and each of these is the system's own vocabulary rather
than a convenience:

  background-image      is never one. A rim light, the panel sheen, a dashed
                        rule and the scroll shadows are all written as images,
                        and they belong to other chapters with their own gates —
                        check-line-types.py, check-glass-solid-edge.py, and the
                        sheen half of check-glass-budget.py.
  a gradient anywhere   same reason, when it arrives through the shorthand.
  none / transparent    is the absence this check is about.
  a --border-* token    is INK. base.css paints the whole .rule family as
                        `background: var(--border-strong)`, and two card parts
                        draw a hairline the same way. A line painted as a block
                        is still a line; check-line-types.py owns them.

FORCED COLOURS IS OUT OF SCOPE, deliberately and narrowly. Inside
`@media (forced-colors: active)` the reader has chosen the palette: Canvas IS
the page there, so a rule painting it declares no step, and any other colour is
repainted by the engine anyway. tokens.css neutralises the veils in that mode
for exactly this reason, and the block that does it is one door over from this
check's subject.

WHAT THIS CANNOT SEE, stated so nobody reads a green run as more than it is.
It holds a NAMED family. A card whose class does not say "card" — .cf-process,
.cf-vacancy, .cf-result, .cf-event — is on the roster by hand, because nothing
in a stylesheet distinguishes a card from any other bordered box, and inventing
a predicate for it would be a checker guessing at a design decision. The SCOPE
claim closes the half that can be closed. The other half is a one-line entry in
ROOTS, and the failure it prevents has cost this system three declarations.

    python3 scripts/check-card-fill.py       # check, exit 1 on a finding
    python3 scripts/check-card-fill.py -v    # list every background it read
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

# The stylesheets that reach control-f.de. docs.css is documentation chrome and
# does not ship — the boundary check-spacing-scale.py and check-glass-budget.py
# both draw. tokens.css is read too, but for its declarations rather than for
# its rules: nothing in it selects a card.
SHIPPING = ("base.css", "components.css", "acts.css")
TOKENS = "tokens.css"

# THE ROSTER. Each root is a card: a bordered box that holds one item's content
# and is repeated, or divided, or both. The parts of a card are derived from it
# by BEM — `<root>__part` and `<root>--modifier` — so a part added later is
# covered on the day it is written and needs no entry here.
#
# A cell of a table and a rung of a list are not cards and are not here. The
# test is the one the chapter uses: a card is a panel with a verdict in the
# census on foundations/materials.html, or a box drawn like one of those.
ROOTS = {
    "cf-process": "the process card — figure half, copy half, one hairline between them",
    "lp-ev-card": "the landing page's evidence card, the same figure/panel anatomy in acts.css",
    "cf-info-card": "the info card, the one card in the system with a frosted modifier",
    "cf-blog-card": "the blog grid's cell",
    "cf-result": "a search hit, one of the three register rows",
    "cf-vacancy": "an open position, and the row that carries a picture",
    "cf-event": "a day in the calendar, drawn as the same row",
    "cf-value-row": "a row of the value table — figure beside copy, a card by construction",
    "cf-culture": "the culture strip's rows, figure beside copy again",
    "cf-team-grid": "the team grid and its cells",
    "cf-team-strip": "the team strip and its cells",
}

# THE STANDING FILLS, with the argument each one stands on. An entry is a class
# and the exact declared value it may carry: a permission for a token, not for
# "a background". Changing the value is a new decision and shows up here as one.
#
# There are three, and the shape of all three is the same: none of them is a
# plate under a part the card is divided into. That is the whole ruling. A veil
# on a block INSIDE a part reads as content set into the card; a fill on the
# card, or on one of its halves, draws a second division along the seam the
# card's own edge already draws, and wins — which is what the copy half's plate
# did on every screenshot of the landing page for as long as it shipped.
ALLOWED = {
    "cf-process__note": (
        "var(--surface-sunken)",
        "the one veil in the card, on a block inset inside the copy half. It is "
        "the census's own row: a note set INTO the card rather than a plate "
        "under part of it. → foundations/materials.html#panel-census",
    ),
    "cf-info-card--glass": (
        "var(--info-card-tint, var(--surface-glass))",
        "a modifier that makes the whole card the material rather than a fill on "
        "a part of it. Glass is the other chapter and carries its own gates — "
        "check-glass-budget.py counts it, check-glass-solid-edge.py holds its "
        "fallback, and the census names it.",
    ),
    "cf-vacancy__image": (
        "var(--surface-raised)",
        "the ground under a photograph, on the <img> itself — the same plate "
        "`.cf-prose figure :is(img, svg, video)` takes, and what "
        "foundations/colors.html says --surface-raised is for. A picture that "
        "has not loaded stands on a plate; the row around it stays a contour.",
    ),
}

# A background that carries one of these is a line or a light rather than a
# surface. Written as substrings of the AUTHORED value, before resolution,
# because that is where the system's vocabulary is: --border-strong is ink
# wherever it lands, and a gradient is a gradient however it is spelled.
# CanvasText is deliberately NOT in here. It is ink in the reader's own palette,
# and every use of it in this tree is inside a forced-colours block, which this
# check does not read at all — so listing it would only excuse a card painting
# itself the reader's text colour outside that mode, which is a black plate.
INK_TOKENS = ("var(--border-", "currentColor")
IMAGE_MARKS = ("gradient(", "url(", "image-set(", "cross-fade(")
NOTHING = ("none", "transparent", "initial", "unset", "revert")

# What a colour looks like once the var()s are gone. The system colours are in
# here because a card must not paint one outside forced colours either.
COLOUR = re.compile(
    r"(#[0-9A-Fa-f]{3,8}\b|\brgba?\(|\bhsla?\(|\boklch\(|\bcolor-mix\(|"
    r"\b(?:Canvas|CanvasText|Highlight|HighlightText|Mark|MarkText|ButtonFace|"
    r"ButtonText|Field|FieldText|LinkText|GrayText|AccentColor)\b|"
    r"\b(?:white|black|red|blue|green|grey|gray|silver)\b)"
)

BACKGROUND = re.compile(r"^(background|background-color|background-image)\s*:\s*(.+)$", re.S)
DECLARATION = re.compile(r"(--[A-Za-z0-9-]+)\s*:\s*([^;{}]+);")
VAR = re.compile(r"var\(\s*(--[A-Za-z0-9-]+)\s*(?:,\s*([^()]*(?:\([^()]*\)[^()]*)*))?\)")
CLASS = re.compile(r"\.([A-Za-z][A-Za-z0-9_-]*)")
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
# Every spelling of "this box has an edge" the shipping CSS uses, physical and
# logical alike. .cf-team-strip draws its two rails with `border-block`, and a
# roster clause that reads only the physical properties reports the one card
# that is a scroll box as no longer being a card.
BORDER = re.compile(
    r"^border(-(top|right|bottom|left|block|inline)(-(start|end))?)?(-color|-width)?"
    r"\s*:\s*(.+)$"
)


def blank_comments(text):
    """Strip comments and keep every newline, so line numbers survive."""
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def forced_spans(text):
    """The [start, end) spans of every `forced-colors: active` block.

    Found by brace matching from the at-rule's own opening brace rather than by
    regex: these blocks nest selectors and this needs the whole extent of one.
    """
    spans = []
    for m in re.finditer(r"@media[^{]*forced-colors[^{]*\{", text):
        depth, i = 0, m.end() - 1
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        spans.append((m.start(), i))
    return spans


def tokens():
    """Every custom property the stylesheets declare, name -> set of its values.

    A set, because the same name is declared in the light block, in the inverse
    block and in the fallback blocks, and a value that is a colour in ANY of
    them is a colour for this check's purpose.

    ALL FOUR FILES, NOT ONLY tokens.css. A component that declares its own
    property and paints it — `--info-card-tint`, and any `--x-bg` a lane writes
    next — is painting whatever that property holds, and a resolver that only
    knows the token file would report the one case it most needs to read as
    unreadable. Page-local <style> blocks are out of scope, which is the same
    boundary check-local-literals.py draws and the reason it exists.
    """
    table = {}
    for name in (TOKENS,) + SHIPPING:
        text = blank_comments((CSS / name).read_text())
        for m in DECLARATION.finditer(text):
            table.setdefault(m.group(1), set()).add(" ".join(m.group(2).split()))
    return table


def resolve(value, table, depth=0):
    """Every value a declaration can compute to, var()s expanded.

    Fallbacks are expanded as candidates of their own: `var(--a, var(--b))` can
    paint either, so both are read. Depth-capped because a token file is a graph
    and this check is not the place to discover a cycle in it.
    """
    if depth > 6:
        return {value}
    m = VAR.search(value)
    if not m:
        return {" ".join(value.split())}
    name, fallback = m.group(1), m.group(2)
    candidates = set(table.get(name, ()))
    if fallback:
        candidates.add(fallback.strip())
    if not candidates:
        candidates = {"<undeclared %s>" % name}
    out = set()
    for candidate in candidates:
        out |= resolve(value[: m.start()] + candidate + value[m.end():], table, depth + 1)
    return out


def classify(prop, value, table):
    """surface | ink | image | nothing | unreadable, for one declaration."""
    if prop == "background-image":
        return "image"
    if any(mark in value for mark in INK_TOKENS):
        return "ink"
    computed = resolve(value, table)
    if all(any(mark in c for mark in IMAGE_MARKS) for c in computed):
        return "image"
    if all(c.strip() in NOTHING for c in computed):
        return "nothing"
    if any(mark in c for c in computed for mark in IMAGE_MARKS):
        # A shorthand painting an image in one theme and a colour in another is
        # two materials behind one name, which no reader of this file can be
        # expected to hold in their head. Say so rather than picking one.
        return "unreadable"
    if any(COLOUR.search(c) for c in computed):
        return "surface"
    return "unreadable"


def family(selector):
    """The card classes a selector targets, root and parts alike."""
    hits = set()
    for name in CLASS.findall(selector):
        for root in ROOTS:
            if name == root or name.startswith(root + "__") or name.startswith(root + "--"):
                hits.add(name)
    return hits


def rules(name):
    """(selector, [(declaration, line)], line, forced) for every rule.

    The line numbers are the DECLARATION's, not the rule's. A card's rule can be
    forty lines of comment and geometry, and a finding that points at its head
    sends a reader looking for a background that is nowhere near it — which is
    the same courtesy check-figure-letterbox.py extends by naming the property
    it measured.
    """
    text = blank_comments((CSS / name).read_text())
    forced = forced_spans(text)
    for m in RULE.finditer(text):
        raw = m.group(1)
        head = m.start(1) + (len(raw) - len(raw.lstrip()))
        selector = " ".join(raw.split())
        if selector.startswith("@") or not selector:
            continue
        body, at = m.group(2), m.start(2)
        declarations, cursor = [], 0
        for chunk in body.split(";"):
            stripped = chunk.strip()
            if stripped:
                start = at + cursor + (len(chunk) - len(chunk.lstrip()))
                declarations.append((stripped, text.count("\n", 0, start) + 1))
            cursor += len(chunk) + 1
        inside = any(start <= head < end for start, end in forced)
        yield selector, declarations, text.count("\n", 0, head) + 1, inside


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every background read on a card, not only the findings")
    args = ap.parse_args()

    table = tokens()
    findings, seen = [], []
    used = set()          # ALLOWED entries this run actually met
    contoured = set()     # roster roots found drawing a contour
    named = set()         # every class in the shipping CSS whose name says card

    for name in SHIPPING:
        for selector, declarations, line, forced in rules(name):
            for cls in CLASS.findall(selector):
                if "card" in cls:
                    named.add(cls)

            hits = family(selector)

            for decl, _ in declarations:
                border = BORDER.match(decl)
                if border and "--border-" in border.group(6):
                    for cls in CLASS.findall(selector):
                        if cls in ROOTS:
                            contoured.add(cls)

            if not hits:
                continue

            for decl, decl_line in declarations:
                m = BACKGROUND.match(decl)
                if not m:
                    continue
                prop, value = m.group(1), " ".join(m.group(2).split())
                kind = classify(prop, value, table)
                where = "%s:%d" % (name, decl_line)

                if forced:
                    seen.append((where, selector, prop, value, "forced colours, out of scope"))
                    continue

                seen.append((where, selector, prop, value, kind))

                if kind in ("image", "ink", "nothing"):
                    continue

                if kind == "unreadable":
                    findings.append(
                        "%s  %s\n"
                        "        %s: %s\n"
                        "    This check cannot tell whether that paints a surface or an image.\n"
                        "    It holds cards to one rule — a card is a contour, and the only fill\n"
                        "    inside one is a veil on a block — and it may not pass a declaration\n"
                        "    it cannot read. Write the value so its material is legible, or teach\n"
                        "    this script the token." % (where, selector, prop, value)
                    )
                    continue

                # kind == "surface"
                entry = None
                for cls in sorted(hits):
                    if cls in ALLOWED:
                        entry = (cls, ALLOWED[cls])
                if entry and entry[1][0] == value:
                    used.add(entry[0])
                    continue
                if entry:
                    used.add(entry[0])
                    findings.append(
                        "%s  %s\n"
                        "        %s: %s\n"
                        "    .%s is allowed one fill and it is not this one: %s.\n"
                        "    The register in this script names the value, not the property, so a\n"
                        "    surface that moved is a decision somebody has to make again. If the\n"
                        "    new value is right, the entry says why in one sentence.\n"
                        "    %s" % (where, selector, prop, value, entry[0], entry[1][0], entry[1][1])
                    )
                    continue

                findings.append(
                    "%s  %s\n"
                    "        %s: %s\n"
                    "    A card is a contour, and %s is a card or a part of one. The card's\n"
                    "    divisions are drawn with edges: a fill on the card, or on one of the\n"
                    "    parts it is divided into, draws a second division along the seam the\n"
                    "    edge already draws — and wins. The copy half of the process card\n"
                    "    carried exactly this for the length of its life on main and read as a\n"
                    "    light block filling half the card.\n"
                    "    A veil on a block INSIDE a part is the fill this system allows: see\n"
                    "    .cf-process__note. If this is that, add it to ALLOWED with the\n"
                    "    sentence that makes it one. Otherwise take the fill off.\n"
                    "    → design-system/foundations/materials.html#card-fill"
                    % (where, selector, prop, value, ", ".join("." + h for h in sorted(hits)))
                )

    # SPENT. An allowance whose rule is gone is not a spare.
    for cls in sorted(set(ALLOWED) - used):
        findings.append(
            "ALLOWED names .%s, and no rule in the shipping CSS gives it that fill.\n"
            "        %s\n"
            "    Either the rule was removed and the permission outlived it — delete the\n"
            "    entry — or the class was renamed and this still names the old one. A\n"
            "    permission nobody needs is read by the next lane as room to fill\n"
            "    something." % (cls, ALLOWED[cls][0])
        )

    # ROSTER. A card that stopped drawing an edge is not a card.
    for root in sorted(set(ROOTS) - contoured):
        findings.append(
            ".%s is on the roster and draws no contour in the shipping CSS.\n"
            "    %s\n"
            "    A card is a bordered box; this one has no border rule naming a --border-\n"
            "    token. Renamed, deleted, or no longer a card — move the entry or drop it,\n"
            "    because everything this check says about its parts is said about a name\n"
            "    that no longer selects one." % (root, ROOTS[root])
        )

    # SCOPE. The clause that survives the next component.
    for cls in sorted(named):
        if not family("." + cls):
            findings.append(
                ".%s is a class whose name says card and it belongs to no root in ROOTS.\n"
                "    Every card in the system is held to one rule — a card is a contour, and\n"
                "    the only fill inside one is a veil on a block — and a card this script\n"
                "    cannot see is a card the rule is not stated about. Add its root to ROOTS\n"
                "    with the line that says what it is." % cls
            )

    if args.verbose:
        for where, selector, prop, value, kind in seen:
            print("%-24s %-14s %s\n    %s: %s" % (where, kind, selector, prop, value))
        print()

    if findings:
        print("card fill: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  - " + f + "\n")
        return 1

    surfaces = sum(1 for *_, kind in seen if kind == "surface")
    print("card fill: %d card(s), %d background(s) read, %d surface(s), all %d registered."
          % (len(ROOTS), len(seen), surfaces, len(ALLOWED)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
