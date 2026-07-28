#!/usr/bin/env python3
"""A skip link lands on something that can hold the focus, and draws no ring.

The thirty-eighth check, and the second whose subject is a keyboard guarantee
rather than a colour or a measurement.

WHAT WENT WRONG. Fourteen pattern pages open with the same two lines:

    <a class="skip-link" href="#inhalt">Zum Inhalt springen</a>
    ...
    <main id="inhalt">

The link is the first tab stop on every one of them and the only control in
this system that exists for a single reader. Measured on the landing page at
375 and 1440, over three sequences — a fresh load, a load where the consent
banner had been dismissed by mouse first, and a reader who had scrolled and
clicked before reaching for it — pressing Enter set location.hash to #inhalt
and left document.activeElement on <body>. Six runs out of six. <main> is not
a focusable element, so the fragment had nothing to give the focus to.

WHY NOBODY SAW IT. Chromium moves the sequential focus navigation starting
point to a fragment's target even when that target cannot hold focus, so the
next Tab does land inside <main> — verified in all six runs. A person testing
this by pressing Tab, Enter, Tab sees the skip link work. What does not move
is focus, and a screen reader in focus mode follows document.activeElement,
not a starting point no API exposes. The reader who pressed the control built
for them was told nothing had happened.

WHY THE OBVIOUS FIX IS HALF A FIX. tabindex="-1" on <main> makes the fragment
move focus for real. It also puts <main> inside the [tabindex] term of the
system's one focus indicator, and because the skip is a KEYBOARD activation
the element then matches :focus-visible: measured, `2px solid` around the
whole of <main>, a rectangle 10,892 px tall on the landing page at 1440. So
base.css carries a second rule keeping the ring off an element whose tabindex
is -1 — out of the tab order is the definition of not being a control — and
the two halves only work as a pair. This check holds the pair.

WHY A SCRIPT AND NOT A REVIEW. Every failure mode here is invisible in a
screenshot and invisible in Chromium's own behaviour. The unfixed page and the
fixed page render identically, tab identically in the one engine most likely
to be used for the review, and differ only in the value of a property nothing
on screen shows. The half-fixed page differs from the fixed page by an outline
that appears for one frame of one interaction. That is precisely the shape
this directory exists for.

WHAT IS CHECKED, per page that ships a .skip-link:

  the target exists      the fragment names an element in the same document.
                         A skip link to nothing is worse than no skip link.

  the target can hold    it is either natively focusable or carries a
  focus                  tabindex. <main>, <div>, <section> and every other
                         element this system has ever pointed a skip link at
                         are not focusable without one.

  the ring is off it     if the target's tabindex is -1, base.css has a rule
                         whose selector matches [tabindex="-1"] and which sets
                         outline: none — otherwise the fix ships the ring
                         around the whole document.

  and that rule WINS     which is not the same as existing. The indicator
                         wraps its list in :where(), so it carries (0,1,0) and
                         an override has to either outrank it or come after it.
                         The check computes both and asks only that one of them
                         holds — a rule that neither outranks the ring nor
                         follows it is a rule that paints nothing, and looks
                         exactly like one that works.

Nothing here is a hand-kept list of pages: the pages are whatever ships a
.skip-link, found by reading the tree.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "design-system" / "assets" / "css" / "base.css"

HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

# Elements the HTML standard puts in the sequential focus order with no author
# attribute. Same list, same reasoning, as check-focus-ring.py — a skip link
# that happens to point at one of these needs no tabindex.
NATIVELY_FOCUSABLE = {
    "a": lambda a: "href=" in a,
    "area": lambda a: "href=" in a,
    "button": lambda a: True,
    "input": lambda a: 'type="hidden"' not in a.replace("'", '"'),
    "select": lambda a: True,
    "textarea": lambda a: True,
    "summary": lambda a: True,
}

SKIP_LINK = re.compile(
    r'<a\b(?=[^>]*\bclass="[^"]*\bskip-link\b[^"]*")([^>]*)>', re.I)
HREF = re.compile(r'href="([^"]*)"', re.I)
TABINDEX = re.compile(r'\btabindex="\s*(-?\d+)\s*"', re.I)


def blank_comments(html: str) -> str:
    """Drop comment CONTENT and keep every newline, so a reported line number is
    the line the reader will find the tag on. Same device as check-a11y.py —
    this tree comments in paragraphs."""
    return HTML_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), html)


def find_by_id(html: str, ident: str):
    """The opening tag that carries id="ident", as (tag, attrs, line)."""
    pat = re.compile(
        r'<(\w+)\b((?:[^>"\']|"[^"]*"|\'[^\']*\')*?\bid="' + re.escape(ident)
        + r'"(?:[^>"\']|"[^"]*"|\'[^\']*\')*)>', re.I)
    m = pat.search(html)
    if not m:
        return None
    return m.group(1).lower(), m.group(2), html[: m.start()].count("\n") + 1


def specificity(selector: str):
    """(ids, classes+attributes+pseudo-classes, elements) for one compound.

    Enough of the cascade for the one comparison this check makes, and no more:
    :where() contributes ZERO — that is the whole reason the indicator is
    written with it — while :not()/:is() take their argument's, which neither
    rule here uses. Anything richer belongs in a CSS parser, not in a check."""
    sel = re.sub(r":where\([^)]*\)", "", selector)
    ids = len(re.findall(r"#[\w-]+", sel))
    cls = (len(re.findall(r"\.[\w-]+", sel))
           + len(re.findall(r"\[[^\]]+\]", sel))
           + len(re.findall(r"(?<!:):[\w-]+(?:\([^)]*\))?", sel)))
    els = len(re.findall(r"(?:^|[\s>+~,])([a-zA-Z][\w-]*)", sel))
    return (ids, cls, els)


def ring_rules(css: str):
    """(ring, override) as (source index, specificity), from a comment-free file.

    The override is any rule whose selector matches an element with
    tabindex="-1" and whose body turns the outline off. Matched on behaviour
    rather than on one spelling, so a later hand can rewrite the selector."""
    nc = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    ring = None
    for m in re.finditer(r"(:where\([^)]*\)\s*:focus-visible)\s*\{([^}]*)\}", nc, re.S):
        if "outline" in m.group(2) and "--focus-ring" in m.group(2):
            ring = (m.start(), specificity(m.group(1)))
    override = None
    for m in re.finditer(r"([^{}]*)\{([^}]*)\}", nc, re.S):
        sel, body = m.group(1), m.group(2)
        if 'tabindex="-1"' not in sel.replace("'", '"'):
            continue
        if ":focus" not in sel:
            continue
        if re.search(r"outline\s*:\s*(none|0)\b", body):
            override = (m.start(), specificity(sel.strip()))
    return ring, override


def main():
    failures = []

    pages = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        html = blank_comments(raw)
        m = SKIP_LINK.search(html)
        if not m:
            continue
        rel = path.relative_to(ROOT)
        line = html[: m.start()].count("\n") + 1
        href = HREF.search(m.group(1))
        if not href:
            failures.append(f"{rel}:{line}: .skip-link has no href.")
            continue
        href = href.group(1)
        if not href.startswith("#"):
            failures.append(
                f"{rel}:{line}: .skip-link points at {href!r}, which is not a fragment "
                "in this document. A skip link is a within-page control.")
            continue
        ident = href[1:]
        if not ident:
            failures.append(f"{rel}:{line}: .skip-link href is a bare '#'.")
            continue
        target = find_by_id(html, ident)
        if target is None:
            failures.append(
                f"{rel}:{line}: .skip-link points at #{ident} and no element in this "
                "document carries that id. The link moves nothing.")
            continue
        tag, attrs, tline = target
        ti = TABINDEX.search(attrs)
        native = NATIVELY_FOCUSABLE.get(tag)
        if ti is None:
            if native and native(attrs):
                pages.append((rel, tag, None))
                continue
            failures.append(
                f"{rel}:{tline}: the skip link's target <{tag} id=\"{ident}\"> cannot hold "
                "focus — it is not natively focusable and carries no tabindex.\n"
                f"    Pressing Enter on the link sets location.hash and leaves\n"
                "    document.activeElement on <body>, so a screen reader in focus mode\n"
                "    is told nothing happened. Chromium's sequential-focus starting point\n"
                "    hides this by moving the NEXT Tab into the target; focus never moves.\n"
                '    Add tabindex="-1" to the target. The ring is already kept off it by\n'
                "    the rule under the focus indicator in base.css.")
            continue
        pages.append((rel, tag, int(ti.group(1))))

    if not pages and not failures:
        failures.append(
            "check-skip-target: no .skip-link in the tree at all. Every pattern page in "
            "this system opens with one; if that has changed, rewrite this check with "
            "it — do not delete it.")

    # The second half of the fix, in the one file that can carry it.
    if any(ti == -1 for _, _, ti in pages):
        css = BASE.read_text(encoding="utf-8")
        ring, override = ring_rules(css)
        if ring is None:
            failures.append(
                f"{BASE.relative_to(ROOT)}: the system's focus indicator "
                "(`:where(...):focus-visible` painting var(--focus-ring)) is gone. "
                "check-focus-ring.py owns that rule; this check needs it to exist so it "
                "can prove the skip target is exempt from it.")
        elif override is None:
            failures.append(
                f"{BASE.relative_to(ROOT)}: no rule keeps the focus ring off an element "
                'with tabindex="-1".\n'
                "    A skip target given tabindex=\"-1\" matches :focus-visible when the\n"
                "    skip is activated from the keyboard, so the system's 2 px ring is\n"
                "    painted around the whole of <main> — 10,892 px tall on the landing\n"
                "    page at 1440. Restore a rule matching [tabindex=\"-1\"]:focus-visible\n"
                "    that sets outline: none.")
        elif not (override[1] > ring[1] or override[0] > ring[0]):
            failures.append(
                f"{BASE.relative_to(ROOT)}: the rule keeping the focus ring off "
                '[tabindex="-1"] never applies.\n'
                f"    override  specificity {override[1]}, at byte {override[0]}\n"
                f"    indicator specificity {ring[1]}, at byte {ring[0]}\n"
                "    It neither outranks the indicator nor comes after it, so the ring\n"
                "    wins and the skip target is drawn with a box around the whole\n"
                "    document. Raise the override's specificity or move it below.")

    if failures:
        print("check-skip-target: the skip link is the first tab stop and the only "
              "control in this system built for one reader.\n")
        for f in failures:
            print("  " + f)
        print()
        sys.exit(1)

    print(f"check-skip-target: {len(pages)} page(s) ship a .skip-link; every target "
          "holds focus and none draws the ring.")
    for rel, tag, ti in pages:
        print(f"  {rel}  ->  <{tag} tabindex={'-' if ti is None else ti}>")


if __name__ == "__main__":
    main()
