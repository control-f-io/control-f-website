#!/usr/bin/env python3
"""No sentence is inside an aria-hidden subtree.

WHAT WENT WRONG. Act 1+2's stage on the landing page is one .cf-statement: a
figure holding the root drawing, and a text block holding act 1's claim. Act 2's
copy — .sp-say, two leads and two bodies, 528 characters — is inside the FIGURE,
and it has to be: above the gate acts.css places it `position: absolute;
inset: 0` of .sp-root, which is how the two columns stay level with the orb at
every viewport, and .sp-root is the figure's only child.

The figure carried aria-hidden="true". That attribute was there for the drawing
and it was never doing anything for the drawing: the <svg class="lp-flow">
carries its own, the .lp-flow-data numeral layer carries its own, and the empty
.sp-say__act stage carries its own. Every decorative child was already declared
decorative on its own element. The one thing the ancestor's copy of the
attribute still reached was the prose — and aria-hidden cannot be opted out of
from within, so nothing inside could win it back.

Measured off Chromium's full AX tree at 1440 x 900 and at 375 x 812, before:

    "Tausende Sensoren, ein Strom."        not in the tree
    "Steuerungen, Zähler und Sensoren …"   not in the tree
    "Von oben nach unten gelesen."         not in the tree
    "Oben tritt jede Messung für sich …"   not in the tree

A screen reader went hero -> act 1's claim -> "Was wir machen". Act 2 did not
exist. The act rail offers a mark labelled "Ein Strom" that led to four
paragraphs nobody could hear, at every width and in every tier, and the same
fault stood in prototypes/statement-to-process.html — the lab this act was built
in, which shares acts.css with the shipped page and shared this too.

WHY A SCRIPT AND NOT A REVIEW. This is the failure mode that looks like success
from every direction a person checks from. The page renders identically with the
attribute and without it — aria-hidden paints nothing. It scrolls identically,
tabs identically, and the copy is selectable with a mouse either way. Nothing in
a screenshot differs by one pixel. The only instrument that shows it is an
accessibility tree, and the only reason anyone opens one is that they already
suspect. Meanwhile the attribute is one word on a line 600 lines from the prose
it silences, and it is CORRECT-looking there: a figure holding a drawing is
exactly the thing that should be aria-hidden, and it stopped being only that the
day prose moved inside it.

WHAT IS CHECKED. Every .html in the tree is walked, and inside every subtree
rooted at an element with aria-hidden="true" the check looks for a SENTENCE: a
<p> or an <h1>–<h6> holding at least MIN_CHARS characters of text. That is the
line between a label and an argument. A drawing legitimately hides plenty of
text — 19 numerals on the root, 21 readings in the sensor field, tick labels on
the map — and every one of those is a <span> or a <b> of a few characters inside
its own <li>. None of them is a paragraph, because a paragraph is prose, and
prose in a drawing is prose in the wrong place: either it belongs to the reader,
in which case the subtree must not be hidden, or it does not, in which case it
should not be authored as a paragraph.

So the rule is not "this figure must not be aria-hidden" — that would be a
hand-kept exception list, and the next act to put copy inside a drawing would
walk past it. The rule is that hiding a subtree is a promise about what is in
it, and a sentence breaks the promise.

NOT A SUBSTITUTE FOR check-a11y.py, which reads the attributes; this one reads
what they cover.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Long enough that no label, unit, numeral, tick or count reaches it; short
# enough that every sentence in this tree's German copy clears it comfortably.
# The shortest .sp-say lead is "Tausende Sensoren, ein Strom." at 29.
MIN_CHARS = 25

PROSE_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6"}

# Void elements never open a subtree, so they must not be pushed on the stack —
# html.parser reports them through handle_starttag like anything else when they
# are written without a slash, which is how this tree writes <img> and <br>.
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class Walk(HTMLParser):
    """Collect (line, tag, text, hider_line, hider_tag) for prose under a hide.

    Written on html.parser rather than on a regex because the question is
    ancestry, and ancestry is the one thing a regex cannot answer. convert_
    charrefs is left on so "&nbsp;" counts as the character it is.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [(tag, line, hidden_here)]
        self.hidden = []         # the open aria-hidden ancestors, innermost last
        self.capture = None      # (tag, line, [chunks], hider) while inside prose
        self.found = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in VOID:
            return
        d = {k.lower(): (v or "") for k, v in attrs}
        hides = d.get("aria-hidden", "").strip().lower() == "true"
        line = self.getpos()[0]
        self.stack.append((tag, line, hides))
        if hides:
            self.hidden.append((tag, line))
        # A prose element nested in prose is not a second finding.
        if tag in PROSE_TAGS and self.hidden and self.capture is None:
            self.capture = (tag, line, [], self.hidden[0])

    def handle_startendtag(self, tag, attrs):
        return  # self-closed: opens nothing

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID:
            return
        # Unwind to the matching open tag, so one stray </div> cannot desync the
        # whole file. Nothing in this tree is unbalanced; this is cheap honesty.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for _, ln, hid in self.stack[i:][::-1]:
                    if hid and self.hidden and self.hidden[-1][1] == ln:
                        self.hidden.pop()
                if self.capture and self.capture[0] == tag:
                    ctag, cline, chunks, hider = self.capture
                    text = re.sub(r"\s+", " ", "".join(chunks)).strip()
                    if len(text) >= MIN_CHARS:
                        self.found.append((cline, ctag, text, hider))
                    self.capture = None
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.capture is not None:
            self.capture[2].append(data)


def main():
    failures = []
    pages = 0
    hidden_seen = 0

    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        w = Walk()
        w.feed(raw)
        w.close()
        pages += 1
        hidden_seen += raw.lower().count('aria-hidden="true"')
        rel = path.relative_to(ROOT)
        for line, tag, text, (htag, hline) in w.found:
            failures.append(
                f'{rel}:{line}: <{tag}> holds {len(text)} characters of prose inside the '
                f'aria-hidden <{htag}> opened at line {hline}.\n'
                f'    "{text[:88]}{"…" if len(text) > 88 else ""}"\n'
                "    aria-hidden on an ancestor cannot be opted out of from within, so this\n"
                "    sentence is not in the accessibility tree at any width or in any tier.\n"
                "    Either the subtree is decorative — in which case this is not a\n"
                "    paragraph — or it is not, and the attribute belongs on the drawing\n"
                "    inside it rather than on the box that also holds the copy.")

    if not hidden_seen:
        failures.append(
            'check-act-copy-exposed: no aria-hidden="true" anywhere in the tree. This '
            "system hides every drawing it ships; if that has changed, rewrite this "
            "check with it — do not delete it.")

    if failures:
        print("check-act-copy-exposed: hiding a subtree is a promise about what is in "
              "it, and a sentence breaks the promise.\n")
        for f in failures:
            print("  " + f)
        print()
        sys.exit(1)

    print(f"check-act-copy-exposed: {pages} page(s), {hidden_seen} aria-hidden "
          f'subtree(s); none contains a <p> or heading of {MIN_CHARS}+ characters.')


if __name__ == "__main__":
    main()
