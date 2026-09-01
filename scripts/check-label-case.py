#!/usr/bin/env python3
"""A case-sensitive name inside a documentation label is marked up as one.

WHAT THIS IS ABOUT, IN ONE LINE. A label in this system is uppercase mono. That
is right for a word and wrong for a name, and the documentation pages are made
almost entirely of names.

THE RULE ALREADY EXISTED AND HAD BEEN APPLIED ONCE. docs.css argues it out in
full over `.docs-table th[scope="row"]`: "`.cf-blog-card--lead` uppercased is
`.CF-BLOG-CARD--LEAD`, which is not that class: CSS class names are
case-sensitive, and so is every other thing a row header names here — a token,
an attribute, a file, a cookie." That fix was scoped to the row header, because
the row header is where it had been found. acts.css states the same rule for the
other family of case-sensitive strings, over `.sp-stream`: "THE UNIT IS NOT A
WORD. `.cf-annot__label` uppercases, which is right for a note and wrong for a
measure: it prints MM/S for mm/s and KPA for kPa, and an SI symbol whose case
has been changed is a different quantity."

Two statements of one rule, in two stylesheets, each applied at the one place
its author was standing. Measured in a browser across all 46 documentation
pages, this is what was left standing between them:

  foundations/motion.html    120 MS · --DURATION-FAST      four caption tiles,
                             with `--duration-fast` printed correctly in a spec
                             table 100 px below them, on the same screen
  foundations/layout.html    --GUTTER, --SECTION-GAP       column heads
  foundations/found.html     .CF-MARK--CURRENT             column heads, twice
  foundations/motion.html    .CF-ISO--BUILD                column head
  foundations/geometry.html  .RULE                         line-type captions
  foundations/field.html     --FIELD-UNIT: 3REM            caption tiles
                             .CF-GROUND .CF-GROUND--LIT    demo label
                             [DATA-THEME="INVERSE"]        demo label
  foundations/iconography.h  --BOLD                        weight caption
  reference.html             FOUNDATIONS/ICONOGRAPHY.HTML  three plate captions

None of them renders wrong in a way a screenshot review catches — they are
label-shaped text in a label, and they look exactly like every other label on
the page. They are wrong as NAMES: two of the tokens do not exist under the
name printed, the class selectors match nothing, and the paths 404 on any host
that is case-sensitive about them.

THE INVARIANT THIS CHECKS, and it is deliberately a markup one rather than a
rendered one. `<code>` is the element that says "this is a literal". docs.css
now declares `text-transform: none` on it — on the element, so an inherited
uppercase can never beat it whatever the specificity upstream — which means the
question "is this name safe from the label around it?" reduces to "is it inside
a `<code>`?", and that is a question about the file. No cascade to resolve, no
browser to open, stdlib and one HTMLParser.

WHAT COUNTS AS A NAME. A CSS custom property (`--field-unit`) and a class
selector written as one (`.cf-ground`). Both are unambiguous in prose — nothing
else in German or English starts with two hyphens or with a dot and `cf-`. Units
are NOT swept: `ms`, `px` and `bar` are ordinary words in the wrong context and
a regex over them cannot tell "120 ms" from "Wir bauen Code statt PowerPoints",
so the unit half of the rule stays where it can be judged — in the caption
device, one declaration at a time.

WHERE IT LOOKS. Every page under design-system/ that loads docs.css: the
foundations, the components, the index and the reference. The pattern pages are
not swept — they carry no `<code>` in a label and their prose is German copy,
not documentation.

WHAT IT DOES NOT ASSERT. That every name in the documentation is inside a
`<code>` for its own sake — only that a name is not left bare where a label can
reach it. Text inside an SVG `<text>` is exempt: SVG has no `<code>` to put it
in, and no label device in this system reaches inside an `<svg>`.

THE REGISTER, same shape as the FOREIGN register in check-a11y.py and the muted
register in check-contrast.py: a hand-kept list of the bare names that are
deliberate, each with its reason, whose value is not that it is complete but
that what is on it can never rot silently. Two devices are on it, and both are
there because putting a `<code>` inside them would make the page worse rather
than better — which is the only reason the list accepts.

Keyed by the class of the box the name sits in, not by the name itself, so a
NEW bare name in a registered device passes and a bare name anywhere else does
not. A device that stops being safe — one that starts uppercasing — is the case
the register cannot catch on its own, which is why each entry says in as many
words what makes it safe.

    python3 scripts/check-label-case.py       # check, exit 1 on a finding
    python3 scripts/check-label-case.py -v    # print every name and where it is
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# A CSS custom property, or a class selector written as one. Both need the two
# leading characters to be unambiguous; a bare `--` followed by a digit is a
# dash in prose ("1200 ms — the scene"), so the first character after is a
# letter. Three characters minimum keeps `--` and `.cf-` themselves out.
#
# Two class prefixes, because the system has two: `cf-` for the components and
# `t-` for the type utilities. `t-` was added after the first pass, when
# foundations/typography.html turned out to hold eleven specimen notes reading
# `.T-DISPLAY-1 · PUBLICA SANS BOLD · …` — a class name inside a `.t-label`,
# which is the utility that uppercases. It is the only page in the tree with a
# `t-` name outside a <code>, and it was invisible to a sweep that knew about
# `cf-` alone. No third prefix: `docs-` is this documentation's own shell and
# never appears as a selector in its prose.
NAME = re.compile(
    r"(?<![\w.-])(--[a-z][a-z0-9-]{2,}|\.(?:cf|t)-[a-z][a-z0-9_-]*)(?![\w-])"
)

# Elements that mark their content as a literal. Anything inside one of these is
# safe by construction — docs.css takes the case change off `code`, and `pre`
# and `kbd` were never inside a label to begin with.
LITERAL = {"code", "pre", "kbd", "samp"}

# Not swept. <script> and <style> are not text; <svg> has no element to mark a
# literal with, and no label device reaches inside one.
OPAQUE = {"script", "style", "svg"}

# HTML void elements plus the SVG shapes that appear unclosed in this tree. A
# stack walker that pushes these never pops them and loses its place.
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}

# A bare name is allowed inside a box carrying one of these classes, because the
# box is already the marker and declares no case change. See THE REGISTER above.
REGISTERED = {
    "docs-swatch__var":
        "the core-palette swatch's token name. The class exists for nothing "
        "else — mono, --text-xs, label tracking, and no text-transform, in "
        "docs.css — so the device IS the literal marker, and nesting a <code> "
        "inside it would take the size off --text-xs and grow the name past "
        "the hex above it.",
    "field-demo":
        "the two labels on foundations/field.html's ground demos — "
        "`.cf-ground .cf-ground--lit` and `[data-theme=\"inverse\"]`. They sit "
        "inside .docs-demo, where docs.css deliberately does not reach, so a "
        "<code> here would render in the browser's default mono beside a Geist "
        "Mono label. The page took the transform off .field-demo p instead, "
        "which is the other fix this check's message offers.",
}


class Names(HTMLParser):
    """Collect every NAME in text that no LITERAL or REGISTERED ancestor covers."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, frozenset-of-classes)
        self.found = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        classes = ""
        for k, v in attrs:
            if k == "class" and v:
                classes = v
        self.stack.append((tag, frozenset(classes.split())))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if any(t == tag for t, _ in self.stack):
            while self.stack.pop()[0] != tag:
                pass

    def handle_data(self, data):
        tags = {t for t, _ in self.stack}
        if tags & OPAQUE or tags & LITERAL:
            return
        for _, classes in self.stack:
            if classes & REGISTERED.keys():
                return
        for m in NAME.finditer(data):
            self.found.append((m.group(0), " ".join(data.split())[:70],
                               " > ".join(t for t, _ in self.stack[-3:]),
                               self.getpos()[0]))


def pages():
    """Every documentation page — the ones that load docs.css.

    Read from the file rather than assumed from the directory: the check has to
    follow the stylesheet, because the rule it enforces lives in the stylesheet.
    """
    for path in sorted(DS.rglob("*.html")):
        if "/en/" in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8")
        if "css/docs.css" in text:
            yield path, text


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    swept = 0
    findings = []
    for path, text in pages():
        swept += 1
        parser = Names()
        parser.feed(text)
        for name, context, where, line in parser.found:
            findings.append((path.relative_to(ROOT), line, name, context, where))

    # The escape itself. Without this declaration every name below is marked up
    # correctly and still renders in the label's case, so the markup invariant
    # above is only worth what this one line is worth.
    docs_css = (DS / "assets" / "css" / "docs.css").read_text(encoding="utf-8")
    escaped = re.search(
        r"\.docs-section code[^{]*\{[^}]*text-transform:\s*none", docs_css, re.S
    )
    if not escaped:
        print("docs.css no longer takes the case change off .docs-section code.")
        print()
        print("Every name below is marked up as a literal and relies on that one")
        print("declaration to render in its own case. Put it back, or this check")
        print("is asserting nothing.")
        return 1

    if findings:
        print(f"{len(findings)} case-sensitive name(s) outside <code> on a page that "
              f"loads docs.css:")
        print()
        for rel, line, name, context, where in findings:
            print(f"  {rel}:{line}")
            print(f"      {name}   in   {context!r}")
            print(f"      inside {where}")
        print()
        print("A label in this system is uppercase mono, and the documentation is")
        print("made of names. `--field-unit` in a caption renders --FIELD-UNIT,")
        print("which is not that property; `.cf-ground` renders .CF-GROUND, which")
        print("matches nothing. Wrap it in <code> — docs.css takes the case change")
        print("off that element — or, where the whole label is a measure and a")
        print("token with no word in it, drop the transform from the device the way")
        print("foundations/motion.html's .motion-demo figcaption does.")
        return 1

    print(f"label case: {swept} documentation pages, every CSS custom property and "
          f"class selector in their text inside a <code>, {len(REGISTERED)} devices "
          f"registered, and docs.css still takes the case change off it.")
    if args.verbose:
        for cls, why in sorted(REGISTERED.items()):
            print(f"  registered  .{cls}")
            print(f"      {why}")
        for path, _ in pages():
            print(f"  swept       {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
