#!/usr/bin/env python3
"""A video this system hides may not still be fetched.

The twenty-first check, and the second whose subject is a cost rather than a
picture — the glass budget is the other. Both fail the same way: the page
renders exactly as designed, and somebody pays for it who was never shown
anything.

components.css opens the hero's reduced-motion block by naming the cost it
knew about:

    "display: none removes the video from the presentation but does not pause
     the element, so decoding continues in the background. That is an honest
     cost and it is worth naming"

It named the decode. The larger half was the download, and nothing named it,
because nothing could see it. `display: none` is a rendering instruction and
the resource selection algorithm has never read one: a <video> with a src
attribute loads whether or not a box is ever generated for it. Measured on
patterns/landing-page.html at 1280 x 800, the transfer was byte-identical in
both states — 1,890,957 total, of which 995,398 was hero-abstract-art.mp4 —
for a reader whose own operating-system setting says they will not be shown a
frame of it. 53 % of the page, spent on the one reader who asked for less.

That share is 69 % since 2026-08-03: the artwork was replaced and the file went
from 995,398 bytes to 3,328,598 of a 4,798,744-byte page. The -v figure below
is read off the files as they ship, so it moves with them and this paragraph
does not have to be trusted for the check to be right.

`preload="none"` does not fix it and looks like it should, which is the part
worth writing down. autoplay overrides the hint: measured, the mp4 was still
requested in both states with preload="none" on the element. What does fix it
is a <source> with a media attribute, because that is the resource selection
algorithm rather than a hint to it — a candidate whose media does not match
the environment is skipped, currentSrc stays empty, and no request is made.
Measured: requested under (prefers-reduced-motion: no-preference), not
requested under reduce, poster shown identically in both.

WHY A SCRIPT. Every symptom of the regression is on the wrong machine. The
page renders correctly with the gate and without it; the still appears either
way; no console message, no failed request, no layout difference, and the
reviewer with the OS preference set sees the poster they expect while a
megabyte they cannot see arrives behind it. It is visible only in a network
panel opened with the preference on — which is a thing nobody does twice. The
one number that would show it is a byte count, and a byte count is exactly
what a checker can hold and a screenshot cannot.

WHAT IT CHECKS, on every <video> under design-system/:

  no bare src   the element may not carry a src attribute. That attribute is
                the ungated path; it is selected before any <source> is
                considered and no media query can stand in front of it.
  every source gated  each <source> child must carry a media attribute naming
                (prefers-reduced-motion: no-preference). One ungated candidate
                is enough — selection stops at the first match, so an ungated
                <source> after a gated one is simply the old behaviour with
                more markup in front of it.
  a poster      the gated-out reader is shown the poster and the still <img>;
                without a poster attribute the element paints nothing at all
                while the CSS is deciding, which is a flash of empty hero on
                the readers least well served by one.

And, on the CSS side, that the thing the gate assumes is still true:

  the still exists   components.css must still carry, inside a
                (prefers-reduced-motion: reduce) query, both halves of the
                swap: `video { display: none }` and `img { display: block }`.
                The markup gate and that block are one mechanism. Delete the
                block and the gate turns from a saving into a bug — the video
                element would be visible, selected nothing, and painted only
                its poster with the still hidden behind it. Neither half is
                safe to hold alone, so both are held here.

WHAT IT DOES NOT CHECK. The reader's own switch — .cf-hero__still-toggle —
still loads the file, and that is correct rather than an oversight. That
switch exists for readers who did NOT set the OS preference (WCAG 2.2.2 asks
for a mechanism, and the media query is not one), so the loop has to be there
to be switched off; and it is a runtime toggle, by which point selection has
long since happened. The media gate answers the door that was opened before
the page was laid out. The other door is answered by the person standing in
it.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-hero-video.py       # check, exit 1 on a finding
    python3 scripts/check-hero-video.py -v    # print every video and its weight
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREE = ROOT / "design-system"
COMPONENTS = TREE / "assets" / "css" / "components.css"

GATE = "prefers-reduced-motion"
UNGATED = "no-preference"

# Documentation quotes the markup it governs — this file's own docstring does,
# and so does the comment above the hero in landing-page.html. A checker that
# read prose would fail on the specification and pass on the regression.
MASK = re.compile(
    r"<!--.*?-->|<pre\b.*?</pre>|<code\b.*?</code>|<textarea\b.*?</textarea>",
    re.S | re.I,
)
VIDEO = re.compile(r"<video\b[^>]*>.*?</video>|<video\b[^>]*/?>", re.S | re.I)
OPEN = re.compile(r"<video\b[^>]*>", re.I)
SOURCE = re.compile(r"<source\b[^>]*>", re.I)
ATTR = re.compile(r"""\b([\w-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""")


def blank(m):
    """Replace a masked region with spaces, keeping newlines for line numbers."""
    return re.sub(r"[^\n]", " ", m.group(0))


def attrs(tag):
    out = {}
    for name, dq, sq, bare in ATTR.findall(tag):
        out[name.lower()] = dq or sq or bare or ""
    # Valueless attributes (autoplay, muted, loop) never carry a value.
    for word in re.findall(r"(?<![\w-])([a-z-]+)(?![\w-]*\s*=)", tag[7:]):
        out.setdefault(word, "")
    return out


def weight(page, src):
    """Bytes of a source file, resolved the way the browser would."""
    if not src or "://" in src:
        return None
    target = (page.parent / src).resolve()
    try:
        return target.stat().st_size
    except OSError:
        return None


def audit_markup():
    findings, seen = [], []
    for path in sorted(TREE.rglob("*.html")):
        rel = path.relative_to(ROOT)
        text = MASK.sub(blank, path.read_text(encoding="utf-8"))
        for m in VIDEO.finditer(text):
            block = m.group(0)
            line = text.count("\n", 0, m.start()) + 1
            opening = OPEN.search(block)
            a = attrs(opening.group(0)) if opening else {}

            if "src" in a:
                findings.append((rel, line, "<video src=\"%s\"> — a src attribute is "
                                 "selected before any <source> and no media query can "
                                 "stand in front of it; move it to a gated <source>"
                                 % a["src"][:52]))
            if not a.get("poster"):
                findings.append((rel, line, "<video> with no poster — the reader the "
                                 "gate excludes is shown nothing while the CSS decides"))

            sources = SOURCE.findall(block)
            if not sources and "src" not in a:
                findings.append((rel, line, "<video> with no <source> and no src — "
                                            "nothing will ever play"))
            for tag in sources:
                sa = attrs(tag)
                media = sa.get("media", "")
                if GATE not in media or UNGATED not in media:
                    findings.append((rel, line, "<source src=\"%s\"> media=%s — every "
                                     "candidate must be gated on (%s: %s) or the file "
                                     "is fetched for a reader who is shown the still"
                                     % (sa.get("src", "")[:44],
                                        ("\"%s\"" % media) if media else "(absent)",
                                        GATE, UNGATED)))
                else:
                    seen.append((rel, line, sa.get("src", ""), weight(path, sa.get("src", ""))))
    return findings, seen


def audit_css():
    """The swap the markup gate assumes: both halves, inside a reduce query."""
    findings = []
    if not COMPONENTS.exists():
        return [(pathlib.Path("design-system/assets/css/components.css"), 0,
                 "stylesheet is missing")]
    text = re.sub(r"/\*.*?\*/", blank, COMPONENTS.read_text(encoding="utf-8"), flags=re.S)
    rel = COMPONENTS.relative_to(ROOT)

    hides = shows = None
    for m in re.finditer(r"@media[^{]*%s\s*:\s*reduce[^{]*\{" % GATE, text, re.I):
        depth, i = 1, m.end()
        while i < len(text) and depth:
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        body = text[m.end():i]
        line = text.count("\n", 0, m.start()) + 1
        if re.search(r"video\s*\{[^}]*display\s*:\s*none", body, re.I):
            hides = line
        if re.search(r"img\s*\{[^}]*display\s*:\s*block", body, re.I):
            shows = line

    if hides is None:
        findings.append((rel, 0, "no (%s: reduce) rule hides a video — the markup gate "
                                 "empties the element for a reader nothing then shows a "
                                 "still to" % GATE))
    if shows is None:
        findings.append((rel, 0, "no (%s: reduce) rule shows the still <img> — the gated "
                                 "reader gets an empty hero" % GATE))
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every gated source and the bytes it withholds")
    args = ap.parse_args()

    findings, seen = audit_markup()
    findings += audit_css()

    if args.verbose:
        for rel, line, src, size in seen:
            print("  %-44s %5d  %-46s %s"
                  % (str(rel)[-44:], line, src[-46:],
                     ("%d bytes" % size) if size is not None else "(unresolved)"))
        print()

    if findings:
        for rel, line, why in findings:
            print("%s:%d\n    %s" % (rel, line, why), file=sys.stderr)
        print("\n%d finding%s: a video this system hides is fetched anyway, or the "
              "still that replaces it is gone. Either way a reader who asked for "
              "less is paying for it."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    total = sum(s for *_, s in seen if s)
    print("hero video: %d gated <source>%s, %d bytes withheld from a "
          "prefers-reduced-motion reader, still swap intact."
          % (len(seen), "" if len(seen) == 1 else "s", total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
