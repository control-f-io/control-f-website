#!/usr/bin/env python3
"""A band the reader can never stand in must not be allowed to hold their place.

THE FAULT. assets/js/cf-pin-gate.js keeps the reader's FRACTION through the band
they are reading across a reflow, and a band is an element child of <main>. Every
term in it rests on one line of arithmetic:

    top = el.getBoundingClientRect().top + window.scrollY

which converts a viewport rect into a document position. That conversion is only
true for an element the document's flow contains. For `position: fixed` the rect
is measured against the viewport and never moves, so the sum is not a place in
the document at all — it is the reader's own scroll position plus a constant.

`nav.act-rail` is a child of <main> on patterns/landing-page.html and on
prototypes/statement-to-process.html, and above (min-width: 64rem) it is
`position: fixed`. Measured at 1280 x 900 its rect.top is 378 and its height 144,
so cf-pin-gate.js's own test

    y < top + height        ->        y < scrollY + 522

is TRUE at every scroll position past the hero's foot. The rail therefore
answered "the reader is inside me" for the whole of the document below 828 px,
held a fraction of -3.77, and — because the correction re-measured the same fixed
element and got the same scrollY back — moved the page to within a pixel of where
the browser had already left it. The cure was a no-op on both pages that carry
the composition it exists for, and it read as working because it loaded, listened
on resize, and called scrollTo: every property check-pin-gate.py asserts about it
was true while it did nothing.

Measured, reader carried 1280 x 900 -> 700 x 900 -> back, patterns/landing-page:

    start y   band before      round-trip drift       with the guard
      1203    sp-track  .06         +1812 px               +2 px
      2881    sp-track  .36         +5905 px              +68 px
      7111    section   .08         +9604 px               +0 px
     10386    section   .56        +11506 px               +0 px
     15728    sp4-track .65         +6164 px               +0 px

Four of nine start positions clamped to y 21892 — the end of the document — so a
reader half way through "Was wir machen" who turned a tablet arrived at the FAQ.
patterns/expertise.html, whose <main> has no out-of-flow child, held its fraction
to within 1 px throughout and is unchanged: that is what said the fault was the
band list and not the arithmetic.

WHAT THIS CHECKS. Nothing renders wrong in either mode, and nothing renders wrong
during the reflow either — the only way to see the fault is to be mid-band at the
instant the viewport crosses a threshold. Three things are countable:

  the cure EXCLUDES out-of-flow bands    a position test naming fixed and sticky
  the cure ANCHORS BY ELEMENT            no index into a list whose membership
                                         changes across the very reflow it spans
  the coupling is REAL                   pages that load the cure, whose <main>
                                         has a child a shipping stylesheet puts
                                         out of flow

The first two are the guard. The third is why it has to be there, and it is
reported rather than forbidden: the rail is where it should be, in <main>, in the
tab order after the hero. A page is free to put a fixed child in <main>; the cure
is not free to mistake it for ground.

Remove the position filter from collect() and this fails. Put the anchor back on
an index and this fails. Add a sixth out-of-flow band and this reports it.

SCOPE: design-system/ and blog/ — the root HTML is the outgoing generation, is a
different site, and loads none of this.
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CURE = os.path.join("design-system", "assets", "js", "cf-pin-gate.js")

SHEETS = [os.path.join("design-system", "assets", "css", n)
          for n in ("tokens.css", "base.css", "components.css", "acts.css")]

LOADS = re.compile(r'<script\b[^>]*\bsrc="[^"]*\bcf-pin-gate\.js"')

HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)

# Innermost brace pairs only — a body with no braces in it is a declaration
# block, so this skips @media wrappers and lands on the rules inside them.
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
OUT_OF_FLOW = re.compile(r"(?<![\w-])position\s*:\s*(fixed|sticky)\b")

TAG = re.compile(r"<(/?)([a-zA-Z][\w:-]*)((?:\"[^\"]*\"|'[^']*'|[^>\"'])*)>")
CLASS_ATTR = re.compile(r'\bclass\s*=\s*"([^"]*)"')

# Elements that never open a container, so never move the depth counter. The
# drawings in these pages are full of them.
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr",
        "circle", "ellipse", "line", "path", "polygon", "polyline", "rect",
        "stop", "use", "image", "animate", "feoffset", "fegaussianblur",
        "femerge", "femergenode", "feblend", "fecolormatrix", "fefunca",
        "fefuncr", "fefuncg", "fefuncb", "fedropshadow", "feflood",
        "fecomposite"}


def html_files():
    out = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
        rel = os.path.relpath(base, ROOT)
        if rel == ".":
            continue
        if rel.split(os.sep)[0] not in ("design-system", "blog"):
            continue
        for n in sorted(names):
            if n.endswith(".html"):
                out.append(os.path.relpath(os.path.join(base, n), ROOT))
    return sorted(out)


def out_of_flow_classes():
    """Class -> (position value, sheet, line) for every class a shipping sheet
    puts out of flow. Keyed on the last compound of each selector, which is the
    element the declaration lands on."""
    found = {}
    for rel in SHEETS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        # Blank comments rather than delete them, so line numbers survive.
        src = CSS_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), raw)
        for m in RULE.finditer(src):
            hit = OUT_OF_FLOW.search(m.group(2))
            if not hit:
                continue
            line = src.count("\n", 0, m.start(2)) + 1
            for sel in m.group(1).split(","):
                sel = sel.strip()
                if not sel or sel.startswith("@") or sel.startswith("%"):
                    continue
                # The subject is the last compound: the rightmost run with no
                # combinator or whitespace in it.
                subject = re.split(r"[\s>+~]+", sel)[-1]
                for cls in re.findall(r"\.([\w-]+)", subject):
                    found.setdefault(cls, (hit.group(1), rel, line))
    return found


def bands(html):
    """The depth-1 element children of <main>, in document order, as
    (tag, [classes])."""
    m = re.search(r"<main\b[^>]*>", html)
    if not m:
        return None
    src = html[m.end():]
    depth = 0
    out = []
    for t in TAG.finditer(src):
        closing, name, attrs = t.group(1), t.group(2).lower(), t.group(3)
        # A closing tag for a name that never opened a container must not move
        # the counter. <use href="…"></use> is written both ways in this tree,
        # and treating its close as a close made the depth go negative one hop
        # into the hero — after which every band named was the wrong element.
        if name in VOID:
            continue
        if closing:
            if name == "main" and depth == 0:
                break
            depth -= 1
            continue
        if attrs.rstrip().endswith("/"):
            continue
        if depth == 0:
            cm = CLASS_ATTR.search(attrs)
            out.append((name, cm.group(1).split() if cm else []))
        depth += 1
    return out


def audit():
    findings = []
    path = os.path.join(ROOT, CURE)
    if not os.path.exists(path):
        return [(CURE, "the cure is missing entirely")], [], {}
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    body = CSS_COMMENT.sub("", src)   # the file's own prose names both values

    if "getComputedStyle" not in body or "position" not in body:
        findings.append((CURE,
            "the band list never asks a child whether it is in flow. A "
            "`position: fixed` child of <main> reports its viewport rect as a "
            "document position, so it contains every scroll offset below it and "
            "swallows the anchor for the rest of the page"))
    else:
        missing = [v for v in ("fixed", "sticky") if "'%s'" % v not in body
                   and '"%s"' % v not in body]
        if missing:
            findings.append((CURE,
                "the band list excludes some out-of-flow positions and not %s. "
                "Both are measured against the viewport rather than against the "
                "document, so both return the reader's own scroll offset plus a "
                "constant" % " or ".join(missing)))

    if re.search(r"bands\s*\[\s*anchor\.i\s*\]", body) or re.search(r"\bi\s*:\s*i\b", body):
        findings.append((CURE,
            "the anchor is held as an index into the band list. The list is "
            "rebuilt on the resize the anchor has to span, and its membership "
            "changes with the viewport — the act rail leaves it going up "
            "through (min-width: 64rem) — so the index names the wrong band on "
            "exactly the reflow this file exists for. Hold the element"))
    guarded = not findings

    oof = out_of_flow_classes()
    seen = []
    for rel in html_files():
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            raw = fh.read()
        clean = HTML_COMMENT.sub("", raw)
        if not LOADS.search(clean):
            continue
        bs = bands(clean)
        if bs is None:
            findings.append((rel, "loads cf-pin-gate.js and has no <main> — the "
                                  "file has no bands to hold and does nothing"))
            continue
        loose = []
        for tag, classes in bs:
            for c in classes:
                if c in oof:
                    loose.append((tag, c) + oof[c])
                    break
        seen.append((rel, len(bs), loose))
        if loose and not guarded:
            for tag, c, pos, sheet, line in loose:
                findings.append((rel,
                    "<%s class=\"%s\"> is a band, and %s:%d makes it "
                    "`position: %s`. Its document-space top is the reader's own "
                    "scroll offset plus a constant, so it contains every "
                    "position below it and the reader's place is never held"
                    % (tag, c, sheet, line, pos)))
    return findings, seen, oof


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every page that loads the cure and its bands")
    args = ap.parse_args()

    findings, seen, oof = audit()

    if args.verbose:
        print("  %d class%s put out of flow by the shipping sheets"
              % (len(oof), "" if len(oof) == 1 else "es"))
        for cls, (pos, sheet, line) in sorted(oof.items()):
            print("    .%-26s %-6s %s:%d" % (cls, pos, sheet, line))
        print()
        for rel, n, loose in seen:
            print("  %-52s %d bands, %d out of flow" % (rel, n, len(loose)))
            for tag, c, pos, sheet, line in loose:
                print("      <%s class=\"%s\">  %s  %s:%d" % (tag, c, pos, sheet, line))
        print()

    if findings:
        for where, why in findings:
            print("%s\n    %s" % (where, why), file=sys.stderr)
        print("\n%d finding%s. A band is an IN-FLOW element child of <main>: "
              "cf-pin-gate.js converts a viewport rect to a document position, "
              "and that conversion is only true for an element the flow "
              "contains." % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    loose = sum(len(l) for _, _, l in seen)
    print("band flow: %d page%s loading the cure, %d band%s, %d out of flow and "
          "excluded by the guard."
          % (len(seen), "" if len(seen) == 1 else "s",
             sum(n for _, n, _ in seen), "" if sum(n for _, n, _ in seen) == 1 else "s",
             loose))
    return 0


if __name__ == "__main__":
    sys.exit(main())
