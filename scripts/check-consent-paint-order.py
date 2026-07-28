#!/usr/bin/env python3
"""A box sized by --cf-consent-height is painted after the height is published.

The fifty-ninth check, and the third whose subject is a cost rather than a
picture — the glass budget and the hero's download are the other two. This one
costs the reader the first screen of the page.

WHAT THE PROPERTY IS. cf-consent.js measures the consent banner and writes its
height to --cf-consent-height, because nothing else can: the banner is
`position: fixed` on the viewport's bottom edge and its height is 144, 233 and
334 px at the three widths its copy wraps at, plus whatever a reader's type
size or a translation does to it. Three declarations spend it:

    base.css       html      scroll-padding-bottom
    components.css .cf-hero  min-height: min(92vh, 56rem, calc(100vh - …))
    components.css .cf-footer padding-block: … calc(--space-8 + …)

WHAT THE FAULT WAS. The property is an input to the FIRST PAINT — the hero is
the first screen — and the script that publishes it was the last <script> in
the body. So the browser painted the hero at 92vh, cf-consent.js then measured
the banner, and the hero collapsed onto the banner's top edge with the whole
document following it up. Measured on patterns/landing-page.html, first visit,
nothing stored:

    viewport      FCP      shift at   CLS        hero px
    375 x 812     192 ms   194 ms     0.32341    747 -> 501
    768 x 1024    192 ms   202 ms     0.09053    896 -> 791
    1280 x 900    224 ms   227 ms     0.03016    828 -> 756
    1440 x 900    240 ms   235 ms     0.02675    828 -> 756

0.32341 is over twice the 0.25 that counts as a poor score. Moving the tag to
sit directly after the banner markup — the parser is then still forty lines
above the hero — took the same four to 0.000 / 0.011 / 0.000 / 0.000.

WHY A SCRIPT, AND WHY THIS ONE IS WORSE THAN MOST. Every symptom is on the
first load and no other. A reader with a stored decision never sees the banner,
so --cf-consent-height is never set, so the hero is min(92vh, 56rem) from the
first frame and CLS is 0.000 at every width. That is every load after the first
— including every load anybody reviewing this page has, all day, on every
machine. The page is correct in the screenshot, correct in the DOM, correct on
the second visit, and correct in every check in this directory. It is wrong for
two hundred milliseconds, once, for a reader who has never been here before.

WHAT IS CHECKED, and it is derived rather than listed. The consumers come out
of the shipping stylesheets: every rule whose body reads var(--cf-consent-height)
in a property that sizes or positions a box. The elements come out of the
markup: for each such rule, the first element on the page wearing that class.
The publisher is the <script> tag pointing at cf-consent.js. The rule is a byte
offset comparison — the publisher comes first.

THE ONE EXEMPTION IS DERIVED TOO, and it is the reason this is not simply "the
tag goes first on every page". A consumer that nothing follows cannot move
anything: .cf-footer's reservation is bottom padding on the last element in the
body, so it lengthens the document and shifts no content, which is why the
fourteen pages that carry the footer and no hero measure 0.000 with the tag
still at the end. So a consumer is exempt when no element with a box follows it
— computed from the markup, not asserted here.

"Follows it" means follows it ON THE PAGE A READER GETS, which is one step
further and also derived. What sits after the footer in this tree is the
documentation nav — `<nav><a class="ds-back">` — and every page's head says in
the same sentence that it never ships: "in production the .ds-back nav is
removed and this link with it." So the classes preview.css declares and the
shipping stylesheets do not are the marker, read out of preview.css, and a
subtree wearing only those is not content anybody's layout can shift. Delete
preview.css and the exemption narrows by itself.

scroll-padding-bottom — the third consumer, on html — is out of scope for a
different reason: it moves a scroll position, never a box.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-consent-paint-order.py
    python3 scripts/check-consent-paint-order.py -v   # show every page
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"

# The three stylesheets that ship to control-f.de. docs.css is documentation
# chrome and does not ship — the same boundary check-glass-budget.py draws.
SHIPPING_CSS = ("tokens.css", "base.css", "components.css")

# Every page in the tree that can carry the banner.
PAGE_DIRS = ("patterns", "components", "foundations", "prototypes")

PROPERTY = "--cf-consent-height"
PUBLISHER = "cf-consent.js"

# Properties that give an element its box. A rule that spends the banner's
# height on one of these changes where the content after it lands, which is the
# whole subject here. The list is closed on purpose: it is not "every property",
# because scroll-padding-bottom — the third consumer, on html — moves a scroll
# position and never a box, and a check that flagged it would be asking the
# publisher to run before a paint it has no part in.
BOX_PROPERTIES = (
    "width", "min-width", "max-width", "inline-size", "min-inline-size", "max-inline-size",
    "height", "min-height", "max-height", "block-size", "min-block-size", "max-block-size",
    "padding", "padding-top", "padding-bottom", "padding-block", "padding-block-start",
    "padding-block-end", "padding-inline", "padding-left", "padding-right",
    "margin", "margin-top", "margin-bottom", "margin-block", "margin-block-start",
    "margin-block-end", "margin-inline", "margin-left", "margin-right",
    "top", "bottom", "left", "right", "inset", "inset-block", "inset-inline",
    "gap", "row-gap", "column-gap", "flex-basis", "translate", "border-width",
    "border-top-width", "border-bottom-width", "border-block-width",
    "grid-template-rows", "grid-template-columns", "aspect-ratio", "font-size",
)


def strip_comments(text):
    """CSS comments. For stylesheets."""
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def strip_markup_prose(text):
    """HTML comments and <style> bodies, which is not the same job as above and
    was briefly done with the same function. These pages explain themselves in
    comments that quote markup — `<a href="…"><img src="…" alt="…"></a>`, and
    elsewhere the very rules this check is about — so an element regex run over
    the raw file finds `class="cf-hero"` in a paragraph of prose thousands of
    bytes before the element itself, and every offset comparison after that is
    against the wrong byte. Offsets stay internally consistent because both the
    publisher and the consumers are located in this same stripped copy."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.sub(r"<style\b[^>]*>.*?</style\s*>", "", text, flags=re.S | re.I)


def consumers():
    """(stylesheet, selector, property) for every box property spending the
    banner's height. Derived from the stylesheets — nothing listed here."""
    found = []
    for name in SHIPPING_CSS:
        path = CSS / name
        if not path.exists():
            continue
        css = strip_comments(path.read_text(encoding="utf-8"))
        # walk declaration blocks, keeping the prelude that opened each one
        prelude, stack = "", []
        for piece in re.split(r"([{}])", css):
            if piece == "{":
                stack.append(prelude.strip())
            elif piece == "}":
                if stack:
                    stack.pop()
            else:
                prelude = piece.rsplit(";", 1)[-1].rsplit("}", 1)[-1]
                if not stack or PROPERTY not in piece:
                    continue
                for decl in piece.split(";"):
                    if PROPERTY not in decl or ":" not in decl:
                        continue
                    prop = decl.split(":", 1)[0].strip()
                    if prop in BOX_PROPERTIES:
                        found.append((name, " ".join(s for s in stack if s), prop))
    return found


def classes_in(selector):
    """The class names a selector needs an element to wear."""
    return set(re.findall(r"\.([A-Za-z_][\w-]*)", selector))


ELEMENT_RE = re.compile(r"<([a-zA-Z][\w-]*)\b([^>]*)>", re.S)
# Elements that never generate a box, so their presence after a consumer does
# not mean anything can move.
BOXLESS = {"script", "template", "link", "meta", "title", "style", "noscript"}


def preview_only_classes():
    """Classes declared by preview.css and by nothing that ships.

    Every page's head says it in the same sentence — "Preview only: styles the
    .ds-back link into the documentation. Never ships — in production the
    .ds-back nav is removed and this link with it." So an element whose classes
    are all owned by that one stylesheet is not on the page a reader gets, and
    what happens to it is not a layout shift anybody has. Read out of the
    stylesheet rather than named here, the same way the consumers above are.
    """
    preview = CSS / "preview.css"
    if not preview.exists():
        return set()
    owned = set(re.findall(r"\.([A-Za-z_][\w-]*)",
                           strip_comments(preview.read_text(encoding="utf-8"))))
    for name in SHIPPING_CSS:
        path = CSS / name
        if path.exists():
            owned -= set(re.findall(r"\.([A-Za-z_][\w-]*)",
                                    strip_comments(path.read_text(encoding="utf-8"))))
    return owned


def something_follows(html, end_offset, preview_classes):
    """Is there a SHIPPING element with a box after this offset, before </body>?

    Trailing padding on the last block cannot move anything — it lengthens the
    document and shifts no content — which is why the pages that carry the
    footer's reservation and no hero measure 0.000 with the publisher still at
    the end of the body.
    """
    tail = html[end_offset:]
    body_end = tail.lower().find("</body>")
    if body_end != -1:
        tail = tail[:body_end]
    pos = 0
    while True:
        m = ELEMENT_RE.search(tail, pos)
        if not m:
            return False
        tag = m.group(1).lower()
        if tag in BOXLESS:
            pos = m.end()
            continue
        # The documentation chrome is a bare <nav> around an <a class="ds-back">,
        # so the test is on the SUBTREE and not on the element: every class in it
        # belongs to preview.css and there is at least one to judge by.
        subtree = tail[m.start():close_of(tail, m.start())]
        worn = set()
        for c in re.finditer(r"\bclass\s*=\s*\"([^\"]*)\"", subtree):
            worn |= set(c.group(1).split())
        if worn and worn <= preview_classes:
            pos = m.start() + max(len(subtree), 1)
            continue
        return True


def close_of(html, start):
    """Offset just past the element opening at `start`, or the end of its tag."""
    tag = ELEMENT_RE.match(html, start)
    if not tag:
        return start
    name = tag.group(1)
    depth, pos = 0, start
    open_re = re.compile(r"<%s\b" % re.escape(name), re.I)
    close_re = re.compile(r"</%s\s*>" % re.escape(name), re.I)
    while pos < len(html):
        o = open_re.search(html, pos)
        c = close_re.search(html, pos)
        if not c:
            return len(html)
        if o and o.start() < c.start():
            depth += 1
            pos = o.end()
            continue
        depth -= 1
        pos = c.end()
        if depth <= 0:
            return pos
    return len(html)


def pages():
    for d in PAGE_DIRS:
        for p in sorted((DS / d).glob("*.html")):
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    spend = consumers()
    preview = preview_only_classes()
    if not spend:
        print("check-consent-paint-order: no box property reads %s in the shipping\n"
              "  stylesheets. Either the reservation was removed — in which case delete\n"
              "  this check with it — or the property was renamed and this check has\n"
              "  gone blind." % PROPERTY)
        return 1

    findings, seen = [], 0
    for page in pages():
        html = page.read_text(encoding="utf-8")
        if "data-cf-consent-banner" not in html:
            continue
        bare = strip_markup_prose(html)
        pub = re.search(r"<script[^>]*\bsrc\s*=\s*[\"'][^\"']*%s[\"']" % re.escape(PUBLISHER), bare)
        rel = page.relative_to(ROOT)
        if not pub:
            findings.append("%s carries the banner and never loads %s, so nothing\n"
                            "     publishes %s and every consumer of it silently\n"
                            "     falls back to 0px." % (rel, PUBLISHER, PROPERTY))
            continue
        seen += 1
        for sheet, selector, prop in spend:
            need = classes_in(selector)
            if not need:
                continue                      # a bare element selector: html, body
            for m in re.finditer(r"<[a-zA-Z][\w-]*\b[^>]*\bclass\s*=\s*\"([^\"]*)\"", bare):
                worn = set(m.group(1).split())
                if not need <= worn:
                    continue
                if not something_follows(bare, close_of(bare, m.start()), preview):
                    break                     # nothing after it can move
                if m.start() < pub.start():
                    findings.append(
                        "%s paints %s before %s runs.\n"
                        "     %s sets `%s` from %s (%s), the element is at byte\n"
                        "     %d and the script at byte %d. The first paint sizes that box\n"
                        "     with the property unset; publishing it afterwards moves\n"
                        "     everything below. Move the <script> above the element."
                        % (rel, selector, PUBLISHER, selector, prop, PROPERTY, sheet,
                           m.start(), pub.start()))
                break                         # first wearer is the one that matters
        if args.verbose:
            print("  ok  %s (publisher at byte %d)" % (rel, pub.start()))

    if findings:
        print("check-consent-paint-order: %d page(s) size a box with %s before the\n"
              "height exists.\n" % (len(findings), PROPERTY))
        for f in findings:
            print("  -  %s\n" % f)
        return 1

    print("check-consent-paint-order: ok — %d box propert%s spend %s; on all %d page(s)\n"
          "carrying the banner the publisher runs first, or nothing follows the consumer."
          % (len(spend), "y" if len(spend) == 1 else "ies", PROPERTY, seen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
