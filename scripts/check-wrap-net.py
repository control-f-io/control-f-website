#!/usr/bin/env python3
"""Hold base.css's overflow-wrap net to the markup it is supposed to cover.

German builds compounds, a compound is one word to a line breaker, and a word
that does not fit does not wrap — it hangs out of its box. base.css answers
that with a net:

    h1..h6, p, li, dt, dd, blockquote, figcaption, td, th, a, button, label,
    summary, span, option, caption { overflow-wrap: break-word; }

THIS IS THE SECOND HALF OF A PAIR, and saying so is most of what this file is
for. foundations/layout.html#intrinsic-minimum states the division in a note of
its own: intrinsic sizing runs BEFORE line breaking, so overflow-wrap never
stops a page scrolling sideways — a floor does, on the track (minmax(0, 1fr))
or on the item (min-width: 0). scripts/check-grid-tracks.py guards the floors.
What the net does is make the result read well afterwards: with the floor and
without the net, the compound in the landing page's first FAQ question sat in a
280 px row and painted 322 px wide, straight through the arrow.

The net was written by hand, and a hand-written list of "the elements that hold
text" turns out to be a list of the elements that MEAN text. Four tags on the
pattern pages held copy and were not in it — summary, span, option, caption —
and layout.html had meanwhile written down that the reset "sets it on
everything", which is the shape of claim this directory exists to keep true.
Measured on the landing page at a 16 px default with one real compound
(Kraftfahrzeughaftpflichtversicherungsschutz, 42 characters):

    element                          floor      net      box     painted
    summary.cf-accordion__summary    absent     absent    280      322   (doc 384)
    summary.cf-accordion__summary    present    absent    280      322
    summary.cf-accordion__summary    present    present   280      280
    span.cf-section-header__count    absent     absent    199      306   (doc 384)
    span.cf-section-header__count    present    present   199      199

WHAT IT CHECKS

  the net is read out of base.css     not restated here. One copy, and this
                                      script fails if that copy shrinks.
  every text leaf under patterns/     is covered, by itself or by an ancestor.
                                      overflow-wrap INHERITS, so a <span> in a
                                      <p> was always covered and is not a
                                      finding; the faults are the leaves whose
                                      whole ancestor chain is uncovered.
  break-word or anywhere              either satisfies the net. base.css uses
                                      break-word deliberately — `anywhere` also
                                      shrinks min-content and would change how
                                      tracks size at widths where nothing was
                                      wrong — but a component that has chosen
                                      `anywhere` is covered, not flagged.

SCOPE, and why it stops there

  design-system/patterns/*.html   the designed pages. Same boundary
                                  check-local-thresholds.py draws when it
                                  refuses a px threshold under patterns/ and
                                  tolerates one elsewhere: these are the pages
                                  that are the product rather than the manual.

  NOT foundations/ or components/ the documentation chrome is about 5 900 text
                                  leaves of <span> and <div> in demo plates.
                                  Reaching them would make this a check about
                                  the manual's markup rather than the site's.

  NOT the repository root         index.html and its siblings are the outgoing
                                  generation and link assets/css/, not
                                  design-system/assets/css/. A different net
                                  lives there; this script does not read it and
                                  must not be made to look like it does.

  NOT <pre>, <code>, <script>,    a scrollport is a deliberate horizontal
      <style>, inline SVG         scroll, not a fault, and .docs-code and
                                  .docs-table-scroll are both. Text inside an
                                  inline SVG is laid out by the SVG.

WHY NOT JUST PUT IT ON body

  Because overflow-wrap inherits, one declaration on body or div would cover
  every leaf in the tree — and a net that cannot be caught short cannot be
  checked either, so this file would pass forever while meaning nothing. It is
  also wrong on its own terms: <pre> and .docs-code are horizontal scrollports
  on purpose, and a net that reaches them turns a code sample that scrolls into
  one that wraps. So the net stays a list of the elements that hold their own
  copy; a <div> that holds copy is a component and covers itself where it is
  declared, which .cf-accordion__content does and this script accepts.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-wrap-net.py       # check, exit 1 on a finding
    python3 scripts/check-wrap-net.py -v    # list the net and every leaf tag
"""

import argparse
import collections
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHIPPING = ("tokens.css", "base.css", "components.css")
PAGES = ROOT / "design-system" / "patterns"

WRAP_OK = re.compile(r"overflow-wrap\s*:\s*(break-word|anywhere)\b")
TYPE_SELECTOR = re.compile(r"[a-z][a-z0-9]*$")

# Void elements never hold text, so they never open a scope on the stack.
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr", "use"}

# Subtrees whose text is not page copy, or whose horizontal scroll is the point.
OPAQUE = {"script", "style", "svg", "template", "pre", "code", "head", "title"}


def rules(path):
    """(selector, body) for every rule in a stylesheet, comments stripped.

    Comments go first so a declaration quoted inside one — this system's
    stylesheets are more comment than code — is never read as live.
    """
    text = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        sel = " ".join(m.group(1).split())
        if sel and not sel.startswith("@"):
            yield sel, m.group(2)


def read_net():
    """The element names and class names the shipping sheets cover.

    Read, never restated: if the list in base.css shrinks, this returns fewer
    names and the pages start failing, which is the regression to catch.
    """
    tags, classes = set(), set()
    for name in SHIPPING:
        path = ROOT / "design-system" / "assets" / "css" / name
        for sel, body in rules(path):
            if not WRAP_OK.search(body):
                continue
            for part in sel.split(","):
                part = part.strip()
                if TYPE_SELECTOR.fullmatch(part):
                    tags.add(part)
                elif re.fullmatch(r"\.[A-Za-z0-9_-]+", part):
                    classes.add(part[1:])
    return tags, classes


class Leaves(HTMLParser):
    """Every text leaf in a page, with the ancestor chain that could cover it."""

    def __init__(self, tags, classes):
        super().__init__(convert_charrefs=True)
        self.net_tags, self.net_classes = tags, classes
        self.stack = []
        self.findings = []
        self.leaves = 0
        self.by_tag = collections.Counter()

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        d = dict(attrs)
        self.stack.append((tag, (d.get("class") or "").split(), d.get("style") or ""))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        # Unbalanced markup is not this script's subject; unwind to the nearest
        # matching open tag and carry on rather than desynchronising the stack.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if not data.strip():
            return
        if any(t in OPAQUE for t, _, _ in self.stack):
            return
        self.leaves += 1
        for tag, classes, style in self.stack:
            if tag in self.net_tags:
                return
            if any(c in self.net_classes for c in classes):
                return
            if WRAP_OK.search(style):
                return
        tag = self.stack[-1][0] if self.stack else "?"
        self.by_tag[tag] += 1
        chain = "/".join(t for t, _, _ in self.stack[-4:])
        self.findings.append((self.getpos()[0], tag, chain, " ".join(data.split())[:60]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    tags, classes = read_net()
    if not tags:
        print("FAIL  no overflow-wrap net found in base.css — the rule this "
              "script reads is gone, not merely narrowed.")
        return 1

    if args.verbose:
        print(f"net: {len(tags)} elements — {', '.join(sorted(tags))}")
        if classes:
            print(f"     {len(classes)} classes — {', '.join('.' + c for c in sorted(classes))}")

    findings, leaves, pages = [], 0, 0
    for path in sorted(PAGES.glob("*.html")):
        parser = Leaves(tags, classes)
        parser.feed(path.read_text(encoding="utf-8"))
        pages += 1
        leaves += parser.leaves
        for line, tag, chain, text in parser.findings:
            findings.append((path.relative_to(ROOT), line, tag, chain, text))
        if args.verbose and parser.by_tag:
            print(f"  {path.name}: {dict(parser.by_tag)}")

    if findings:
        print(f"FAIL  {len(findings)} text leaves under design-system/patterns/ are "
              f"outside base.css's overflow-wrap net.\n")
        for rel, line, tag, chain, text in findings:
            print(f"  {rel}:{line}  <{tag}> in {chain}")
            print(f"      {text}")
        uncovered = sorted({f[2] for f in findings})
        print(f"\n  {len(uncovered)} element(s) hold copy and are not in the net: "
              f"{', '.join(uncovered)}")
        print("  Add them to the rule in design-system/assets/css/base.css, or give the")
        print("  component its own overflow-wrap. Do not narrow the scope of this check:")
        print("  a compound that does not wrap is a page that scrolls sideways at 320 px.")
        return 1

    print(f"OK    {leaves} text leaves across {pages} pattern pages, every one of them "
          f"inside the net of {len(tags)} elements.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
