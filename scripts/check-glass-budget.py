#!/usr/bin/env python3
"""Enforce the glass budget.

`backdrop-filter` is the most expensive thing in this stylesheet, and
foundations/materials.html states what keeps it affordable as three rules in
prose: exactly two blurred layers on a shipping page and never a third, one
blur radius for the whole system, and nothing scroll-driven moving on a blurred
layer. It also publishes a census of where the layers are — "landing page 2,
Über uns 1, and 1 each on the component pages that demo it" — in a sentence
that names its own problem two paragraphs later: *a count somebody has to
remember*.

Every one of those is invisible in a screenshot. A third blurred layer renders
correctly; it just costs. A literal `blur(20px)` on some future panel renders
correctly; it just forks the material. A gradient animated across a blurred
sheet renders correctly; it re-rasterises the blur on every frame of a scroll.
Nothing goes red, nothing looks wrong, and the page is slower on the hardware
least able to afford it — which is the whole test for what belongs in one of
these scripts, and the reason the other three exist.

WHAT COUNTS AS GLASS IS READ OUT OF THE STYLESHEET, NOT LISTED HERE. The script
finds every rule in the shipping CSS that declares `backdrop-filter` and takes
its selectors as the definition. A fourth frosted surface added later therefore
enters the budget by existing, rather than by somebody remembering to add it to
a list in this file — the same reason check-gradient-family.py recomputes its
waypoint from the oklab path instead of comparing against a table of hexes. A
checker whose scope is hand-maintained drifts exactly the way the prose census
did.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-glass-budget.py          # check, exit 1 on drift
    python3 scripts/check-glass-budget.py --fix    # rewrite the census + stamp
    python3 scripts/check-glass-budget.py -v       # list every page, not only hits
"""

import argparse
import hashlib
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"
MATERIALS_DOC = DS / "foundations" / "materials.html"

# The three stylesheets that ship to control-f.de. docs.css is documentation
# chrome and does not ship — the same boundary check-spacing-scale.py draws.
SHIPPING_CSS = ("tokens.css", "base.css", "components.css")

# A shipping page gets two blurred layers. The figure is not this script's: it
# is measured in foundations/materials.html, where the two layers on the landing
# page are shown to overlap for about 150 px of scroll at no measurable cost,
# and the rule kept is the one that pays rather than the stronger one that does
# not. Raising this number is a design decision about a page's frame budget, not
# a checker setting — something has to give up its blur first.
SHIPPING_BUDGET = 2

# Documentation pages are censused, not capped. A page whose subject IS the
# material has to be allowed to show it: foundations/materials.html carries
# three plates of its own — two samples and the band in the layer stack — and
# capping it at a selling page's budget would mean documenting glass without
# drawing it. The census is what makes a jump here visible anyway.
DOC_BUDGET = None

# prototypes/ is out of scope. They are motion studies, none has been reconciled
# with the tokens, and nothing in components/ depends on them — the same
# exclusion check-gradient-family.py makes, for the same reason.
SKIP_DIRS = {"prototypes", "assets"}

# The one blur in the system. Every backdrop-filter in shipping CSS reads this
# token; a literal radius is two materials that merely resemble each other.
BLUR_TOKEN = "var(--glass-blur)"

# A selector this script can count: one class, optionally one pseudo-element.
# Deliberately narrow. Anything wider — a descendant combinator, an attribute,
# a :not() — would need a real selector engine to match against the HTML, and a
# checker that guesses at matching is worse than none. A selector that does not
# reduce is a finding rather than a skip, so the failure mode is "teach me or
# simplify it" and never "quietly stopped counting that one".
SIMPLE_SELECTOR = re.compile(r"^\.([A-Za-z0-9_-]+)(::[a-z-]+)?$")

# Properties whose animation re-rasterises the blur underneath on every frame.
# transform is here even though it is normally the cheap one: a blurred layer
# has to re-read its backdrop when it moves over it.
REPAINTS_BLUR = ("opacity", "background", "transform", "filter", "clip-path", "mask")


def blank_comments(text):
    """Comments replaced by spaces IN PLACE, so every offset and every line
    number in the result is the one a reader will find in the file.

    Deleting them instead is the obvious version and makes every line number
    this script reports wrong by however much prose sits above it — which in
    these stylesheets is most of the file. `.cf-nav::before` is at line 916 and
    a delete-based strip puts it at 299. A checker that names the wrong line is
    worse than one that names none, because the reader goes and looks."""
    chars = list(text)
    for m in re.finditer(r"/\*.*?\*/", text, re.S):
        for i in range(m.start(), m.end()):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)


def rules(text):
    """Every selector/block pair in a stylesheet, with the selector's line.

    At-rules are walked into rather than over, because both of this system's
    conditional blocks matter here: the glass tokens are redefined inside
    @supports and @media, and a rule that animates a blurred layer would most
    naturally be written inside `@media (prefers-reduced-motion: no-preference)`
    — which is exactly where this script has to be able to see it.
    """
    text = blank_comments(text)
    out = []
    open_stack = []
    start = 0
    for i, ch in enumerate(text):
        if ch == "{":
            raw = text[start:i]
            # The line the SELECTOR starts on, not the line the brace is on: a
            # multi-line selector list should point at its first selector.
            sel_at = start + (len(raw) - len(raw.lstrip()))
            open_stack.append((raw.strip(), i + 1, text.count("\n", 0, sel_at) + 1))
            start = i + 1
        elif ch == "}":
            if open_stack:
                head, body_start, line = open_stack.pop()
                if not head.startswith("@"):
                    out.append((head, text[body_start:i], line))
            start = i + 1
    return out


def glass_rules():
    """Every shipping rule that declares backdrop-filter, with its selectors.

    This is the definition of "glass" for the whole script. It is derived rather
    than declared so that the budget cannot be evaded by adding a frosted
    surface the list in this file has never heard of.
    """
    found = []
    for name in SHIPPING_CSS:
        for head, body, line in rules((CSS / name).read_text()):
            decls = [d.strip() for d in body.split(";") if d.strip()]
            bf = [d for d in decls if re.match(r"^-?(?:webkit-)?backdrop-filter\s*:", d)]
            if not bf:
                continue
            found.append(
                {
                    "file": name,
                    "line": line,
                    "selectors": [s.strip() for s in head.split(",") if s.strip()],
                    "values": [d.split(":", 1)[1].strip() for d in bf],
                }
            )
    return found


def glass_classes(found):
    """The class names a blurred layer hangs off, and the selectors that failed
    to reduce to one."""
    classes, unreducible = set(), []
    for rule in found:
        for sel in rule["selectors"]:
            m = SIMPLE_SELECTOR.match(sel)
            if m:
                classes.add(m.group(1))
            else:
                unreducible.append((rule["file"], rule["line"], sel))
    return classes, unreducible


class GlassCounter(HTMLParser):
    """Counts ELEMENTS carrying a glass class, not class occurrences.

    The distinction is load-bearing on foundations/materials.html, whose veil
    samples carry `material-glass material-glass--veil` — two classes, one
    element, and exactly one blurred layer, because only the base class declares
    the filter. Counting class hits would report that page at five layers and
    then fail a budget nothing had actually spent.
    """

    def __init__(self, classes):
        super().__init__(convert_charrefs=True)
        self.classes = classes
        self.hits = []

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class") or ""
        names = set(cls.split())
        if names & self.classes:
            self.hits.append(tag + "." + ".".join(sorted(names & self.classes)))


def pages():
    for path in sorted(DS.rglob("*.html")):
        if set(p.name for p in path.relative_to(DS).parents) & SKIP_DIRS:
            continue
        yield path


def census(classes):
    """Every page under design-system/, with how many blurred layers it carries."""
    rows = []
    for path in pages():
        parser = GlassCounter(classes)
        parser.feed(path.read_text())
        rel = path.relative_to(DS).as_posix()
        shipping = rel.startswith("patterns/")
        rows.append((rel, len(parser.hits), shipping, parser.hits))
    return rows


def stamp_of(rows):
    return hashlib.sha256(
        repr([(r, n) for r, n, _, _ in rows if n]).encode()
    ).hexdigest()[:8]


CENSUS_TABLE = re.compile(r'<table[^>]*\bid="glass-census"[^>]*>.*?</table>', re.S)


def census_table(html):
    """Just the generated table. Same rule check-spacing-scale.py learned the
    hard way: a generator that cannot say which table it owns will eventually
    rewrite one it does not."""
    m = CENSUS_TABLE.search(html)
    if not m:
        sys.exit(
            'foundations/materials.html has no <table id="glass-census">. That id is how\n'
            "this script finds the generated census; without it the script cannot tell the\n"
            "census from any other table on the page. Restore the id."
        )
    return m.start(), m.end(), m.group(0)


def render_table(rows):
    body = "\n".join(
        "        <tr><td><code>%s</code></td><td>%s</td><td>%d</td></tr>"
        % (rel, "shipping" if shipping else "documentation", n)
        for rel, n, shipping, _ in rows
        if n
    )
    # .docs-table is not decoration: it is `display: block; overflow-x: auto` on
    # a phone, so a table wider than its column scrolls inside itself instead of
    # pushing the whole document sideways. Without it this table overflowed the
    # page by 24 px at 375.
    return (
        '<table class="docs-table" id="glass-census">\n'
        "      <thead>\n"
        "        <tr><th>Page</th><th>Kind</th><th>Blurred layers</th></tr>\n"
        "      </thead>\n"
        "      <tbody>\n"
        "%s\n"
        "      </tbody>\n"
        "    </table>" % body
    )


STAMP = re.compile(r"<code>[0-9a-f]{8}</code>")


def sole_stamp(html):
    """The stamp, and proof that it is the only thing on the page shaped like one.

    The stamp is prose rather than table, so it can only be found by shape — and
    the shape is eight hex digits in a <code>, which a colour with an alpha pair
    also has. check-spacing-scale.py asserts in a comment that nothing else on
    its page matches; this checks instead, because the two failure modes are not
    symmetrical. A second match means --fix silently overwrites whatever it is,
    and the thing most likely to be written next to a materials chapter is a
    colour."""
    hits = STAMP.findall(html)
    if len(hits) != 1:
        sys.exit(
            "foundations/materials.html has %d things shaped like the census stamp; there\n"
            "must be exactly one. --fix rewrites every match, so a second one would be\n"
            "overwritten with a digest. Found: %s"
            % (len(hits), ", ".join(hits) or "none")
        )
    return hits[0][6:-7]


def doc_rows():
    html = MATERIALS_DOC.read_text()
    found = re.findall(
        r"<tr><td><code>([^<]+)</code></td><td>[^<]*</td><td>(\d+)</td></tr>",
        census_table(html)[2],
    )
    return sole_stamp(html), {a: int(b) for a, b in found}


def fix(rows, stamp):
    html = MATERIALS_DOC.read_text()
    sole_stamp(html)
    start, end, _ = census_table(html)
    html = html[:start] + render_table(rows) + html[end:]
    MATERIALS_DOC.write_text(STAMP.sub("<code>%s</code>" % stamp, html))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="rewrite the census and stamp")
    ap.add_argument("-v", "--verbose", action="store_true", help="list every page")
    args = ap.parse_args()

    found = glass_rules()
    if not found:
        print(
            "glass budget: no backdrop-filter in the shipping CSS at all. Either the\n"
            "material has been removed — in which case delete this check and the chapter\n"
            "it enforces — or the parser has stopped seeing the rules it is meant to."
        )
        return 1

    classes, unreducible = glass_classes(found)
    rows = census(classes)
    stamp = stamp_of(rows)
    failures = []

    if args.fix:
        fix(rows, stamp)
        print("materials.html rewritten: stamp %s" % stamp)
        return 0

    # 1. Every selector carrying a blur has to be countable, or the census is a
    #    number with an unstated exception in it.
    for name, line, sel in unreducible:
        failures.append(
            "%s:%d declares backdrop-filter on a selector this script cannot count:\n"
            "        %s\n"
            "    The census would silently omit it, which is worse than not having one.\n"
            "    Either reduce the selector to a single class (optionally with one\n"
            "    pseudo-element), or widen SIMPLE_SELECTOR here and teach GlassCounter to\n"
            "    match it." % (name, line, sel)
        )

    # 2. One blur for the whole system. tokens.css measures 16 px as the radius
    #    past which nothing reads better and everything costs more; a literal
    #    anywhere is a second material wearing the first one's name.
    for rule in found:
        for value in rule["values"]:
            if BLUR_TOKEN not in value:
                failures.append(
                    "%s:%d writes its own blur rather than reading the token:\n"
                    "        backdrop-filter: %s\n"
                    "    Use %s. The radius is measured in tokens.css, and a component that\n"
                    "    states its own cannot be moved with the material."
                    % (rule["file"], rule["line"], value, BLUR_TOKEN)
                )

    # 3. Nothing scroll-driven moves on a blurred layer. A transition is left
    #    alone deliberately — see the note in foundations/materials.html: it is
    #    bounded, user-initiated and measured free, where an animation on a
    #    scroll timeline runs for the length of the document.
    blurred_selectors = {s for rule in found for s in rule["selectors"]}
    for name in SHIPPING_CSS:
        for head, body, line in rules((CSS / name).read_text()):
            sels = {s.strip() for s in head.split(",") if s.strip()}
            if not (sels & blurred_selectors):
                continue
            for decl in (d.strip() for d in body.split(";") if d.strip()):
                prop, _, value = decl.partition(":")
                prop = prop.strip()
                if prop == "animation-timeline" or (
                    prop.startswith("animation")
                    and any(p in value for p in REPAINTS_BLUR)
                ):
                    failures.append(
                        "%s:%d animates a property on a blurred layer:\n"
                        "        %s\n"
                        "    Re-rasterises the blur on every frame it runs. Both of the\n"
                        "    navigation's lights live on its unblurred 1 px rim for exactly\n"
                        "    this reason, and .cf-btn--glass::before exists to keep the\n"
                        "    button's band off its plate. Move it to a layer that is not\n"
                        "    blurred." % (name, line, decl)
                    )

    # 4. The budget, and the census that publishes it.
    for rel, n, shipping, hits in rows:
        if shipping and n > SHIPPING_BUDGET:
            failures.append(
                "%s carries %d blurred layers; a shipping page gets %d.\n"
                "        %s\n"
                "    foundations/materials.html names the four surfaces that look like they\n"
                "    want glass and must not have it. If this is a genuine third case,\n"
                "    something else on the page has to give up its blur first."
                % (rel, n, SHIPPING_BUDGET, ", ".join(hits))
            )

    doc_stamp, published = doc_rows()
    measured = {rel: n for rel, n, _, _ in rows if n}
    if doc_stamp != stamp:
        drift = sorted(
            set(published) | set(measured),
            key=lambda k: (published.get(k, 0) == measured.get(k, 0), k),
        )
        failures.append(
            "foundations/materials.html publishes census stamp %s; the tree measures %s.\n"
            "    %s\n"
            "    Run: python3 scripts/check-glass-budget.py --fix"
            % (
                doc_stamp,
                stamp,
                ", ".join(
                    "%s %s->%s" % (k, published.get(k, 0), measured.get(k, 0))
                    for k in drift
                    if published.get(k, 0) != measured.get(k, 0)
                )
                or "row order or wording changed",
            )
        )

    if args.verbose:
        print("glass, as read out of the shipping CSS: %s\n" % ", ".join(sorted(classes)))
        for rel, n, shipping, hits in rows:
            print(
                "  %2d  %-46s %-13s %s"
                % (n, rel, "shipping" if shipping else "documentation", ", ".join(hits))
            )
        print()

    if failures:
        print("glass budget: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    total = sum(n for _, n, _, _ in rows)
    print(
        "glass budget: stamp %s, %d blurred layers across %d pages, max %d on a shipping page."
        % (
            stamp,
            total,
            sum(1 for _, n, _, _ in rows if n),
            max((n for _, n, s, _ in rows if s), default=0),
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
