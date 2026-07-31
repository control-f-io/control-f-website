#!/usr/bin/env python3
"""Every page in design-system/ must be made of tags that open and close.

The markup grammar check. Beside it, check-a11y.py reads what a page says —
ids, labels, headings, landmarks — and seventy-odd siblings read what the
stylesheets claim. Not one of them reads the page's grammar. An unclosed
<div>, a </section> with no section open, a <b><i></b></i> overlap: every
checker in this directory happily parses right past all of them, because
every checker in this directory is built on a parser that recovers — the
same reason a browser renders these faults without a word. HTML parsers do
not fail; they guess. Four elements swallowed into the wrong parent render
identically on the day the tag is dropped, and differently three commits
later when a stylesheet starts selecting `section > *`.

WHAT FOUND THIS. A full sweep of the fourteen pattern pages with two real
validators — html5lib's HTML5 parsing algorithm and the W3C Nu validator —
found their grammar CLEAN: zero structural errors, with every remaining
complaint an artefact of the validators trailing the specs (`--` inside
comments, which WHATWG allows; `@container` and `animation-timeline`, which
are CSS; `pathLength` on <line>, which is SVG 2). Fourteen clean pages and
no gate is not a fact, it is a coincidence: a dozen routines edit these
files every hour, and the class of error a browser recovers from silently
is exactly the class a routine ships without noticing. The one structural
fault the sweep did find sits outside the gate's strict scope and proves
the class is real: prototypes/services-scroll.html carries sixteen numeric
character references that are UTF-8 bytes escaped one at a time —
`&#195;&#182;` for what was once ö — including four references to U+009F,
a C1 control character no HTML document may name. That is what an encoding
accident fossilised into markup looks like, and nothing here would have
said a word.

WHAT IT CHECKS, on every .html file under design-system/:

  STRAY-END     an end tag with nothing open to close. The parser drops it;
                the next reader trips over it.
  MIS-NEST      an end tag that has to force other elements shut to reach
                its own — <b><i></b>: the overlap the adoption agency
                algorithm exists to guess about.
  UNCLOSED      an element still open when the document ends and its end
                tag is not one the spec lets a page omit.
  VOID-END      an end tag for a void element: </br>, </img>. There is no
                such tag; a parser invents an element or drops it.
  DUP-ATTR      the same attribute twice on one tag. The parser keeps the
                first and discards the second silently — whichever one was
                the edit.
  NEST-INTERACT an <a> or <button> containing another interactive element.
                The parser splits or re-parents it; a keyboard meets two
                stops where the page drew one.

And under patterns/ — the strict scope, the same line check-a11y.py draws:

  BAD-NCR       a numeric character reference to a codepoint HTML forbids:
                C0/C1 controls, surrogates, noncharacters. Consecutive
                references in the &#194;–&#195; + &#128;–&#191; shape are
                reported as what they are — UTF-8 bytes escaped separately,
                mojibake fossilised at export time.
  ID-SPACE      an id containing whitespace. Everything that points at ids
                — CSS, fragments, label/for, aria-labelledby — treats a
                space as a separator, so such an id can never be referred
                to whole.

Implied end tags are honoured, not flagged: a <li> is closed by the next
<li>, a <p> by an arriving block element, exactly as the specification
omits them. The check reads grammar, not style — a legal omission is not a
finding, and a finding is never a legal omission.

WHAT IT DOES NOT READ. Text inside <pre>, <code>, <script> and <style> is
content, not markup, and comments are neither — a documentation page
quoting a broken tag must fail nothing. The outgoing generation at the
repository root is the previous generation and not this system's to
govern; the same boundary every check here draws.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-markup.py       # check, exit 1 on a finding
    python3 scripts/check-markup.py -v    # per-file element counts too
"""

import argparse
import pathlib
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREE = ROOT / "design-system"
PATTERNS = TREE / "patterns"

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}

# An element on the left is implicitly closed by any arriving start tag on
# the right — the specification's optional end tags, honoured silently.
CLOSED_BY_START = {
    "p": {"address", "article", "aside", "blockquote", "details", "div",
          "dl", "fieldset", "figcaption", "figure", "footer", "form",
          "h1", "h2", "h3", "h4", "h5", "h6", "header", "hgroup", "hr",
          "main", "menu", "nav", "ol", "p", "pre", "search", "section",
          "table", "ul"},
    "li": {"li"},
    "dt": {"dt", "dd"},
    "dd": {"dt", "dd"},
    "option": {"option", "optgroup", "hr"},
    "optgroup": {"optgroup", "hr"},
    "tr": {"tr"},
    "td": {"td", "th", "tr"},
    "th": {"td", "th", "tr"},
    "thead": {"tbody", "tfoot"},
    "tbody": {"tbody", "tfoot"},
    "caption": {"colgroup", "thead", "tbody", "tfoot", "tr"},
    "colgroup": {"thead", "tbody", "tfoot", "tr"},
    "rt": {"rt", "rp"},
    "rp": {"rt", "rp"},
}

# End tags the specification lets a page omit: popping one of these on the
# way to an outer end tag, or finding one open at EOF, is legal HTML.
OMISSIBLE = {"html", "head", "body", "p", "li", "dt", "dd", "option",
             "optgroup", "tr", "td", "th", "thead", "tbody", "tfoot",
             "caption", "colgroup", "rt", "rp"}

# Inside these, HTML's implied-end-tag rules do not apply: foreign content
# closes every element explicitly or self-closes it.
FOREIGN = {"svg", "math"}

# Interactive content may not nest inside these two — <label> is deliberately
# not one of them: wrapping the control it names is its canonical form.
INTERACTIVE_CONTAINERS = {"a", "button"}
INTERACTIVE = {"a", "button", "select", "textarea", "label", "details",
               "embed", "iframe"}
# An <input> is interactive unless type=hidden; handled inline.

# Codepoints a numeric character reference may not name: NUL, C0 controls
# other than tab/lf/cr, DEL and the C1 range, surrogates, noncharacters.
def forbidden_codepoint(cp):
    if cp == 0 or (0x01 <= cp <= 0x1F and cp not in (0x09, 0x0A, 0x0D)):
        return "a C0 control character"
    if 0x7F <= cp <= 0x9F:
        return "a C1 control character"
    if 0xD800 <= cp <= 0xDFFF:
        return "a surrogate"
    if (cp & 0xFFFE) == 0xFFFE or 0xFDD0 <= cp <= 0xFDEF:
        return "a noncharacter"
    return None


class Grammar(HTMLParser):
    """One page's element tree, replayed tag by tag."""

    def __init__(self, strict):
        # convert_charrefs=False so every &#…; arrives as its own event —
        # the BAD-NCR rule reads the reference, not the character.
        HTMLParser.__init__(self, convert_charrefs=False)
        self.strict = strict
        self.stack = []          # [(tag, line)]
        self.findings = []       # [(line, rule, why)]
        self.elements = 0
        self.previous_ncr = None  # (line, codepoint) of the last charref

    def note(self, line, rule, why):
        self.findings.append((line, rule, why))

    def line(self):
        return self.getpos()[0]

    def in_foreign(self):
        return any(tag in FOREIGN for tag, _ in self.stack)

    def open_interactive(self):
        for tag, line in reversed(self.stack):
            if tag in INTERACTIVE_CONTAINERS:
                return tag, line
        return None

    # -- start tags ---------------------------------------------------------

    def handle_starttag(self, tag, attrs):
        self.elements += 1

        raw = [name for name, _ in attrs]
        for name in sorted(set(n for n in raw if raw.count(n) > 1)):
            self.note(self.line(), "DUP-ATTR",
                      "<%s> carries %r twice; a parser keeps the first and "
                      "drops the second without a word." % (tag, name))

        got = dict(attrs)
        if self.strict:
            ident = got.get("id")
            if ident is not None and any(c.isspace() for c in ident):
                self.note(self.line(), "ID-SPACE",
                          "<%s id=%r>: an id with whitespace in it can never "
                          "be referred to whole — every consumer of ids "
                          "reads a space as a separator." % (tag, ident))

        interactive = tag in INTERACTIVE or (
            tag == "input" and got.get("type", "").lower() != "hidden")
        if interactive:
            outer = self.open_interactive()
            if outer:
                self.note(self.line(), "NEST-INTERACT",
                          "<%s> opens inside the <%s> from line %d; "
                          "interactive content may not nest, and the "
                          "parser un-nests it its own way."
                          % (tag, outer[0], outer[1]))

        if not self.in_foreign():
            while self.stack and tag in CLOSED_BY_START.get(self.stack[-1][0], ()):
                self.stack.pop()      # the spec's own omission — silent
            if tag in VOID:
                return
        self.stack.append((tag, self.line()))

    def handle_startendtag(self, tag, attrs):
        # <x/> — self-closing. Real in foreign content; in HTML the slash is
        # ignored on non-void elements, so treat it as open+close: for the
        # grammar's purposes nothing stays on the stack either way only when
        # the element has no separate end tag coming. Pages here use the
        # form only in SVG, where it is exact.
        self.elements += 1
        raw = [name for name, _ in attrs]
        for name in sorted(set(n for n in raw if raw.count(n) > 1)):
            self.note(self.line(), "DUP-ATTR",
                      "<%s/> carries %r twice; a parser keeps the first and "
                      "drops the second without a word." % (tag, name))

    # -- end tags -----------------------------------------------------------

    def handle_endtag(self, tag):
        if tag in VOID and not self.in_foreign():
            self.note(self.line(), "VOID-END",
                      "</%s>: %s is a void element and has no end tag; a "
                      "parser drops it or invents an element for it."
                      % (tag, tag))
            return
        open_tags = [t for t, _ in self.stack]
        if tag not in open_tags:
            self.note(self.line(), "STRAY-END",
                      "</%s> with no <%s> open to close. The parser drops "
                      "it; whatever it was meant to close is still open."
                      % (tag, tag))
            return
        while self.stack:
            top, where = self.stack.pop()
            if top == tag:
                return
            if top not in OMISSIBLE:
                self.note(self.line(), "MIS-NEST",
                          "</%s> forces <%s> (line %d) shut on its way out — "
                          "the elements overlap instead of nesting."
                          % (tag, top, where))

    # -- character references ----------------------------------------------

    def handle_charref(self, name):
        if not self.strict:
            return
        try:
            cp = int(name[1:], 16) if name.lower().startswith("x") else int(name)
        except ValueError:
            self.note(self.line(), "BAD-NCR",
                      "&#%s;: not a number, so not a character." % name)
            return
        what = forbidden_codepoint(cp)
        line = self.line()
        prev = self.previous_ncr
        self.previous_ncr = (line, cp)
        if prev and prev[0] == line and 0xC2 <= prev[1] <= 0xC3 and 0x80 <= cp <= 0xBF:
            decoded = bytes([prev[1], cp]).decode("utf-8")
            self.note(line, "BAD-NCR",
                      "&#%d;&#%d;: the UTF-8 bytes of %r escaped one at a "
                      "time — mojibake written into the file. Write the "
                      "character." % (prev[1], cp, decoded))
            return
        if what:
            self.note(line, "BAD-NCR",
                      "&#%s; names U+%04X, %s — a codepoint no HTML "
                      "document may reference." % (name, cp, what))

    # -- end of file --------------------------------------------------------

    def close(self):
        HTMLParser.close(self)
        for tag, where in self.stack:
            if tag not in OMISSIBLE and tag not in FOREIGN:
                self.note(where, "UNCLOSED",
                          "<%s> opened here is still open when the document "
                          "ends." % tag)
        self.stack = []


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="per-file counts, not only the failures")
    args = ap.parse_args()

    findings, seen = [], []
    for path in sorted(TREE.rglob("*.html")):
        page = Grammar(strict=PATTERNS in path.parents)
        page.feed(path.read_text(encoding="utf-8"))
        page.close()
        rel = path.relative_to(ROOT)
        seen.append((rel, page.strict, page.elements, len(page.findings)))
        for line, rule, why in sorted(page.findings):
            findings.append((rel, line, rule, why))

    if args.verbose:
        print("  %-56s %-6s %9s" % ("file", "scope", "elements"))
        for rel, strict, elements, _ in seen:
            print("  %-56s %-6s %9d"
                  % (str(rel)[-56:], "page" if strict else "docs", elements))
        print()

    if findings:
        for rel, line, rule, why in findings:
            print("%s:%d  %s\n    %s" % (rel, line, rule, why), file=sys.stderr)
        print("\n%d grammar finding%s across %d file%s."
              % (len(findings), "" if len(findings) == 1 else "s",
                 len({f[0] for f in findings}),
                 "" if len({f[0] for f in findings}) == 1 else "s"),
              file=sys.stderr)
        return 1

    pages = sum(1 for _, strict, _, _ in seen if strict)
    print("markup: %d files parsed (%d pattern pages under the strict rules), "
          "%d elements, every tag matched."
          % (len(seen), pages, sum(s[2] for s in seen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
