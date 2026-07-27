#!/usr/bin/env python3
"""Enforce the spacing scale.

foundations/layout.html publishes two claims about --space-*: a table of how
many declarations use each rung, and a stamp that is a digest of those counts.
The stamp exists so a reader can tell a current table from a stale one in a
single command. It works — but nothing ran it, so the table drifted anyway:
seven of thirteen rows were wrong within a few commits of being measured.

A self-check nobody runs is documentation, not enforcement. This script is the
thing that runs it, and it also enforces the rule the scale exists for in the
first place: spacing is written as a token, not as a length.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-spacing-scale.py          # check, exit 1 on drift
    python3 scripts/check-spacing-scale.py --fix    # rewrite the table + stamp
"""

import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
LAYOUT_DOC = ROOT / "design-system" / "foundations" / "layout.html"

# The three stylesheets that ship to control-f.de. docs.css, per-page <style>
# blocks and prototypes/ are deliberately out of scope — same boundary the
# breakpoint register draws, and for the same reason.
SHIPPING = ("tokens.css", "base.css", "components.css")

# The scale, in order. The step number is the multiple of the 4 px base unit.
STEPS = (1, 2, 3, 4, 5, 6, 8, 12, 16, 20, 24, 30, 40)

# Steps allowed to sit at zero consumers. --space-30 (120) is the value the
# vertical rhythm lands on at the 1440 reference frame, kept as a landmark;
# foundations/layout.html records that as a deliberate exception to the
# delete-an-unused-rung rule. Anything else reaching zero is a finding.
UNUSED_OK = {30}

# Properties that carry spacing. A length here should be a token.
SPACING_PROP = re.compile(
    r"\b(?:margin|padding)(?:-(?:block|inline)(?:-(?:start|end))?|-(?:top|right|bottom|left))?"
    r"|\b(?:row-|column-)?gap\b"
)

# A bare length. em/ch/% are relative to something the scale does not govern
# (the element's own type, its measure, its parent) and are not flagged.
LENGTH = re.compile(r"(?<![\w.-])(-?\d*\.?\d+)(px|rem)(?![\w-])")

# Lengths that are not spacing decisions even in a spacing property.
FREE = {"0px", "0rem"}

# Justified literals, each with the reason it is not a token. Keep this list
# short: every entry is a place the scale does not reach, and a long list means
# the scale is wrong rather than that the exceptions are.
ALLOWED = {
    # The clip-rect recipe's own artifact, not a spacing decision. The element
    # is 1x1 and pulled back by exactly its own size so it occupies no space at
    # all; the -1px is bound to the 1px above it, not to the scale.
    ("base.css", "margin: -1px"),
}


def declarations(text):
    """Split CSS into declarations with comments stripped, keeping line numbers."""
    # Blank out comments in place so line numbers survive.
    out = []
    for m in re.finditer(r"/\*.*?\*/", text, re.S):
        out.append((m.start(), m.end()))
    chars = list(text)
    for a, b in out:
        for i in range(a, b):
            if chars[i] != "\n":
                chars[i] = " "
    stripped = "".join(chars)
    line = 1
    start = 0
    for i, ch in enumerate(stripped):
        if ch == "\n":
            line += 1
        if ch in ";{}":
            frag = stripped[start:i]
            if frag.strip():
                yield line - frag.count("\n"), frag.strip()
            start = i + 1


def measure():
    """The thirteen counts and their stamp — the same arithmetic layout.html
    publishes as a one-liner, so the two can never disagree about method."""
    text = "".join((CSS / f).read_text() for f in SHIPPING)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    counts = [sum(f"var(--space-{n})" in d for d in text.split(";")) for n in STEPS]
    stamp = hashlib.sha256(repr(counts).encode()).hexdigest()[:8]
    return counts, stamp


def off_scale():
    """Spacing declarations in shipping CSS whose value is a length, not a token."""
    hits = []
    for name in SHIPPING:
        for line, decl in declarations((CSS / name).read_text()):
            prop, _, value = decl.partition(":")
            if not value or not SPACING_PROP.fullmatch(prop.strip()):
                continue
            for m in LENGTH.finditer(value):
                if m.group(0) in FREE:
                    continue
                if (name, decl) in ALLOWED:
                    continue
                hits.append((name, line, decl))
                break
    return hits


SCALE_TABLE = re.compile(r'<table[^>]*\bid="space-scale"[^>]*>.*?</table>', re.S)


def scale_table(html):
    """Just the generated table, which is the only part of the page this script
    may read or rewrite.

    It used to work on the whole document, and the row pattern is loose enough
    that any OTHER table starting `--space-N | number | number` was read as a
    competing claim about the scale — and, under --fix, silently rewritten to
    the measured count. That is not hypothetical: the note on root-font-size
    behaviour under Vertical rhythm opens exactly that way, listing --space-8 at
    three root sizes, and the checker read its `40` as a claim that 40
    declarations use the rung. A generator that cannot say which table it owns
    will eventually corrupt one it does not."""
    m = SCALE_TABLE.search(html)
    if not m:
        sys.exit(
            "foundations/layout.html has no <table id=\"space-scale\">. That id is how this\n"
            "script finds the generated table; without it the script cannot tell the scale\n"
            "table from any other table on the page. Restore the id."
        )
    return m.start(), m.end(), m.group(0)


def doc_claims():
    """The stamp and the thirteen Declarations cells currently in layout.html."""
    html = LAYOUT_DOC.read_text()
    stamp = re.search(r"<code>([0-9a-f]{8})</code>\s*&mdash;|<code>([0-9a-f]{8})</code>\s*—", html)
    stamp = next(g for g in stamp.groups() if g) if stamp else None
    rows = re.findall(
        r"<tr><td><code>--space-(\d+)</code></td><td>\d+</td><td>(?:<strong>)?(\d+)(?:</strong>)?</td>",
        scale_table(html)[2],
    )
    return stamp, {int(a): int(b) for a, b in rows}


def fix(counts, stamp):
    html = LAYOUT_DOC.read_text()
    start, end, table = scale_table(html)
    for step, n in zip(STEPS, counts):
        strong = "<strong>%d</strong>" % n if n == 0 else str(n)
        table = re.sub(
            r"(<tr><td><code>--space-%d</code></td><td>\d+</td><td>)(?:<strong>)?\d+(?:</strong>)?(</td>)" % step,
            lambda m: m.group(1) + strong + m.group(2),
            table,
        )
    html = html[:start] + table + html[end:]
    # The stamp is prose rather than table, so it stays a whole-document
    # substitution — but it is anchored to an 8-hex-digit <code>, which nothing
    # else on the page is.
    html = re.sub(r"<code>[0-9a-f]{8}</code>", "<code>%s</code>" % stamp, html)
    LAYOUT_DOC.write_text(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="rewrite the table and stamp in layout.html")
    args = ap.parse_args()

    counts, stamp = measure()
    failures = []

    if args.fix:
        fix(counts, stamp)
        print("layout.html rewritten: stamp %s" % stamp)
        return 0

    doc_stamp, doc_rows = doc_claims()
    if doc_stamp != stamp:
        failures.append(
            "foundations/layout.html publishes stamp %s; the shipping CSS measures %s.\n"
            "    %s\n"
            "    Run: python3 scripts/check-spacing-scale.py --fix"
            % (
                doc_stamp,
                stamp,
                ", ".join(
                    "--space-%d %s->%s" % (s, doc_rows.get(s, "?"), c)
                    for s, c in zip(STEPS, counts)
                    if doc_rows.get(s) != c
                ),
            )
        )

    for step, n in zip(STEPS, counts):
        if n == 0 and step not in UNUSED_OK:
            failures.append(
                "--space-%d has no consumer in the shipping CSS. The scale's own rule is to\n"
                "    delete a rung that loses its last consumer rather than leave it as a\n"
                "    suggestion — see foundations/layout.html. Delete it, or add it to\n"
                "    UNUSED_OK here with the reason it is kept." % step
            )

    for name, line, decl in off_scale():
        failures.append(
            "%s:%d writes spacing as a length rather than a token:\n"
            "        %s\n"
            "    Use a --space-* token, or compose one with calc() so the value cannot\n"
            "    drift from what it is derived from. If it genuinely sits outside the\n"
            "    scale, add it to ALLOWED here with the reason." % (name, line, decl)
        )

    if failures:
        print("spacing scale: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    print("spacing scale: stamp %s, %d rungs, no off-scale literals." % (stamp, len(STEPS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
