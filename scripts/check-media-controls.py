#!/usr/bin/env python3
"""A media element nobody gave controls to must not stand where the browser adds them.

The sibling of check-hero-video.py, found by the same page in the one tier that
script's argument never reaches. That check holds the reduced-motion reader:
the loop is withdrawn and the bytes with it. This one holds the reader with
scripting off, where the withdrawal is not about motion or about cost at all —
it is about a control surface the page never asked for and cannot style away.

WHAT THE STANDARD SAYS, and it is easy to read past. The `controls` attribute
is what a page uses to ask for a media UI, and nothing in this system carries
one. But HTML's own rule for the attribute's absence is not "no UI":

    "If the attribute is absent, then the user agent should avoid exposing a
     user interface ... unless scripting is disabled for the media element, in
     which case the user agent should expose a user interface."

Every engine does. So a page that never asked for controls gets them, in the
one tier a developer never browses in, and the picture is exactly as bad as it
sounds. Photographed on patterns/landing-page.html at 1440 x 900 with
JavaScript off, before the fix this check now holds:

    a scrub track  the full width of the hero, at y 781
    a 0:00 readout at x 60, on the kicker rule's own baseline
    the buttons    x 1320 to 1420, over the artwork's lit edge
    a loading arc  at 735, 400, over the middle of the picture

under a <video> that is aria-hidden, muted, looped and decorative, and beside
the pause plate this page already draws for WCAG 2.2.2 — a checkbox and two ~
selectors, which need no script and were working correctly the whole time.

WHY NOT STYLE IT OUT. `::-webkit-media-controls { display: none }` loses to
Chromium's own !important, so the author rule needs one too; this system has
zero !important in 26 000 lines of stylesheet, and the pseudo-element answers
one engine anyway. The withdrawal is the answer the file already had written
twice: components.css hides the video and shows the still under print and under
prefers-reduced-motion, and `(scripting: none)` is the third state where
nothing is moving. No video box, no controls, on every engine, with no
declaration this system would not otherwise write.

WHY A SCRIPT. The fault is invisible from every seat that matters. The page is
correct with the guard and without it at every width, in every colour scheme,
in the console, in the network panel and in the accessibility tree — because
the tier that shows it is the one no tool defaults to. A screenshot finds it
only if somebody thought to take it with scripting off, which is how it was
found once and is not a plan for keeping it out. The invariant is countable in
the files, so it is counted.

WHAT IT CHECKS, over every <video> and <audio> under design-system/:

  a UI is asked for, or withdrawn
                an element carrying `controls` has made the decision on
                purpose and is skipped entirely. Every other one must be
                withdrawn by a `(scripting: none)` rule in a SHIPPING
                stylesheet — `display: none` on a selector whose subject is
                that element's tag under one of the classes it or an ancestor
                carries.

  something stands in its place
                the same query must show a still: a `display: block` (or
                `display: revert`) on an `img` selector, in a block whose
                prelude names (scripting: none). A withdrawal that leaves the
                hero empty trades one fault for a worse one.

  the bytes go with the paint
                every <source> under a withdrawn element must name
                (scripting: enabled) in its media attribute. `display: none`
                is not read by the resource selection algorithm — the whole
                argument of check-hero-video.py — so without this term the
                reader who is shown a still is still sent the loop. Reported
                with the byte count, which is read off the file.

THE BOUNDARY WITH check-hero-video.py. That script owns the reduced-motion
tier: `(prefers-reduced-motion: no-preference)` on every candidate and the
still swap inside a `reduce` query. This one owns the scripting tier and reads
nothing about motion. The two share one media query in components.css and one
<source> element on the landing page, and each asserts only its own term of
them, so a page can never satisfy one by restating the other.

→ design-system/assets/css/components.css, the hero's withdrawal block
→ design-system/patterns/landing-page.html, the gated <source>
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREE = ROOT / "design-system"

# The stylesheets that ship. docs.css and preview.css are documentation chrome
# and are never loaded by a visitor, so a guard written in one of them is not a
# guard — the same list acts.css's own header keeps.
SHIPPING = ["tokens.css", "base.css", "components.css", "acts.css"]

OFF = "scripting"
NONE = "none"
ENABLED = "enabled"

# Documentation quotes the markup it governs — this file's docstring does, and
# so does the comment above the hero. A checker that read prose would fail on
# the specification and pass on the regression. The same mask check-hero-video
# carries, for the same reason.
MASK = re.compile(
    r"<!--.*?-->|<pre\b.*?</pre>|<code\b.*?</code>|<textarea\b.*?</textarea>",
    re.S | re.I,
)
MEDIA = re.compile(r"<(video|audio)\b[^>]*>.*?</\1>|<(video|audio)\b[^>]*/?>", re.S | re.I)
OPEN = re.compile(r"<(?:video|audio)\b[^>]*>", re.I)
SOURCE = re.compile(r"<source\b[^>]*>", re.I)
ATTR = re.compile(r"""\b([\w-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""")
CLASSES = re.compile(r"""\bclass\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)


def blank(m):
    """Replace a masked region with spaces, keeping newlines for line numbers."""
    return re.sub(r"[^\n]", " ", m.group(0))


def attrs(tag):
    out = {}
    for name, dq, sq, bare in ATTR.findall(tag):
        out[name.lower()] = dq or sq or bare or ""
    for word in re.findall(r"(?<![\w-])([a-z-]+)(?![\w-]*\s*=)", tag):
        out.setdefault(word, "")
    return out


def enclosing_classes(text, at):
    """Every class token on the element and on the tags still open above it.

    Read by walking the source before the element and keeping the tags that
    have not been closed. Enough for a hand-written page, and this tree has no
    other kind: the generated pages are these pages with their strings swapped.
    """
    stack = []
    for m in re.finditer(r"<(/?)([a-zA-Z][\w-]*)\b([^>]*)>", text[:at]):
        closing, tag, rest = m.group(1), m.group(2).lower(), m.group(3)
        if tag in ("br", "img", "input", "source", "meta", "link", "hr", "use"):
            continue
        if rest.rstrip().endswith("/"):
            continue
        if closing:
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == tag:
                    del stack[i:]
                    break
        else:
            found = CLASSES.search(rest)
            stack.append((tag, (found.group(1) or found.group(2) or "") if found else ""))
    out = set()
    for _, names in stack:
        out.update(names.split())
    return out


def scripting_blocks():
    """Every @media block in a shipping stylesheet whose prelude names scripting.

    Returns (hidden, shown): the selectors set to display:none, and whether any
    img selector is restored. Comments are blanked first — this file's subject
    is a rule that is easy to describe and easy to forget to write.
    """
    hidden, shown, where = [], [], []
    for name in SHIPPING:
        path = TREE / "assets" / "css" / name
        if not path.exists():
            continue
        text = re.sub(r"/\*.*?\*/", blank, path.read_text(encoding="utf-8"), flags=re.S)
        for m in re.finditer(r"@media([^{]*)\{", text):
            prelude = m.group(1)
            if not re.search(r"\(\s*%s\s*:\s*%s\s*\)" % (OFF, NONE), prelude, re.I):
                continue
            depth, i = 1, m.end()
            while i < len(text) and depth:
                depth += (text[i] == "{") - (text[i] == "}")
                i += 1
            body = text[m.end():i]
            line = text.count("\n", 0, m.start()) + 1
            where.append((name, line))
            for rule in re.finditer(r"([^{}]+)\{([^{}]*)\}", body):
                selectors, decls = rule.group(1), rule.group(2)
                value = re.search(r"(?<![-\w])display\s*:\s*([\w-]+)", decls, re.I)
                if not value:
                    continue
                for sel in selectors.split(","):
                    sel = sel.strip()
                    if not sel:
                        continue
                    if value.group(1).lower() == "none":
                        hidden.append(sel)
                    elif re.search(r"(?<![\w-])img(?![\w-])", sel, re.I):
                        shown.append(sel)
    return hidden, shown, where


def withdraws(selectors, tag, classes):
    """Does one of these selectors hide THIS element?

    The subject of the selector — its last compound — has to name the tag, and
    every class the selector mentions has to be one this element or an ancestor
    carries. `.cf-hero__media video` withdraws the hero's loop; `.cf-x video`
    does not withdraw an element that stands nowhere near .cf-x.
    """
    for sel in selectors:
        subject = re.split(r"\s+|>|\+|~", sel.strip())[-1]
        if not re.match(r"^%s(?![\w-])" % tag, subject, re.I):
            continue
        named = set(re.findall(r"\.([\w-]+)", sel))
        if named <= classes:
            return sel
    return None


def weight(page, src):
    if not src or "://" in src:
        return None
    try:
        return (page.parent / src).resolve().stat().st_size
    except OSError:
        return None


def audit():
    findings, seen = [], []
    hidden, shown, where = scripting_blocks()

    for path in sorted(TREE.rglob("*.html")):
        rel = path.relative_to(ROOT)
        raw = path.read_text(encoding="utf-8")
        text = MASK.sub(blank, raw)
        for m in MEDIA.finditer(text):
            block = m.group(0)
            line = text.count("\n", 0, m.start()) + 1
            opening = OPEN.search(block)
            if not opening:
                continue
            tag = re.match(r"<(\w+)", opening.group(0)).group(1).lower()
            a = attrs(opening.group(0))
            if "controls" in a:
                # The page asked for a UI on purpose. Nothing to hold.
                continue

            classes = enclosing_classes(text, m.start())
            classes.update(a.get("class", "").split())
            guard = withdraws(hidden, tag, classes)
            if not guard:
                findings.append((rel, line, "<%s> carries no `controls`, and no "
                                 "(%s: %s) rule withdraws it — HTML has the browser "
                                 "expose a media UI over it for every reader with "
                                 "scripting off, and it cannot be styled away"
                                 % (tag, OFF, NONE)))
                continue
            if not shown:
                findings.append((rel, line, "<%s> is withdrawn under (%s: %s) and "
                                 "nothing is shown in its place — the still has to "
                                 "be restored in the same query or the box is empty"
                                 % (tag, OFF, NONE)))

            for stag in SOURCE.findall(block):
                sa = attrs(stag)
                media = sa.get("media", "")
                if not re.search(r"\(\s*%s\s*:\s*%s\s*\)" % (OFF, ENABLED), media, re.I):
                    findings.append((rel, line, "<source src=\"%s\"> media=%s — a "
                                     "withdrawn element still fetches its candidates; "
                                     "name (%s: %s) so the reader shown the still is "
                                     "not sent the file"
                                     % (sa.get("src", "")[:44],
                                        ("\"%s\"" % media) if media else "(absent)",
                                        OFF, ENABLED)))
                else:
                    seen.append((rel, line, guard, sa.get("src", ""),
                                 weight(path, sa.get("src", ""))))
    return findings, seen, where


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every withdrawn element and the bytes it withholds")
    args = ap.parse_args()

    findings, seen, where = audit()

    if args.verbose:
        for name, line in where:
            print("  guard  %s:%d" % (name, line))
        for rel, line, guard, src, size in seen:
            print("  %-40s %5d  %-24s %-34s %s"
                  % (str(rel)[-40:], line, guard[-24:], src[-34:],
                     ("%d bytes" % size) if size is not None else "(unresolved)"))
        print()

    if findings:
        for rel, line, why in findings:
            print("%s:%d\n    %s" % (rel, line, why), file=sys.stderr)
        print("\n%d finding%s: a media element this page never gave controls to is "
              "left standing in the one tier the browser adds them, or is withdrawn "
              "there and fetched anyway."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    total = sum(s for *_, s in seen if s)
    print("media controls: %d withdrawn element%s, %d bytes withheld from a reader "
          "with scripting off, still swap intact."
          % (len(seen), "" if len(seen) == 1 else "s", total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
