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

AND IT ENFORCED THAT RULE IN THREE STYLESHEETS WHILE THE MARKUP WAS OPEN. A
`style` attribute is the one place a spacing decision can sit where no reader of
a stylesheet will ever meet it and no gate in this directory was looking. Read
across every page under design-system/ that is not a generated mirror:

  114 spacing declarations inside style attributes
   88 of them 0 or auto — a reset, not a decision
   26 live, and NOT ONE of them on a page under patterns/

That last line is the tell rather than the reassurance. check-local-literals.py
already stands over patterns/ and narrows inline style there to custom
properties only, so those pages are clean because something reads them. The rest
of the directory — components/, foundations/, prototypes/ — had no reader at
all, and it is where the overrides collected. That is the worse half to leave
open: the documentation is what a reader learns the system from. base.css
carries three rules besides — .flow-*, .grid--sections, .after-register — each
written after somebody found an inline spacing override by reading, and each one
says so in place. Three finds, three fixes, no gate.

WHAT WAS IN THERE. Five values off the scale entirely — `padding-bottom: 8rem`
(128 px, between two rungs), `margin-top: 1rem` (16 px, which is --space-4 spelt
as a length), and three `<ol>` indents at two different values because the rule
beside .docs-section ul names ul and stops. Two `gap: 1px` seams on a class,
.docs-swatch-row, that was a name in the markup and a rule nowhere. One
`gap: var(--space-8)` on a `.stack` — the exact declaration base.css says the
.flow-* rungs were created to end, back on a different page. And four
`margin-top: var(--space-8)` on `<h3>` elements of foundations/layout.html, the
chapter that publishes this scale, every one of them a restatement of what
`.docs-section > h3` already says: measured in Chromium at 1280, 32 px with the
attribute and 32 px with it removed, four times.

THE TWO MARKUP RULES, and why they stop where they do. MARKUP holds an inline
spacing value to the scale by the same method the stylesheet half uses — the
same property list, the same length pattern, so px and rem are read and em, ch
and % are not, because those are relative to something the scale does not
govern. It does NOT ban inline spacing: a one-off distance on an anonymous
element in a demo is honestly written where it lands, and inventing a class per
demo would be the scale reaching past what it governs. FLOW is the one place
that argument fails, so it is the one place the ban is absolute: .stack and
.cluster resolve their spacing through --flow and the .flow-* rungs, so an
inline gap or margin on either does not sit beside the system's answer, it
overrides it.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-spacing-scale.py          # check, exit 1 on drift
    python3 scripts/check-spacing-scale.py -v       # every rung and the markup census
    python3 scripts/check-spacing-scale.py --fix    # rewrite the table + stamp
"""

import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"
LAYOUT_DOC = DS / "foundations" / "layout.html"

# The three stylesheets that ship to control-f.de. docs.css, per-page <style>
# blocks and prototypes/ are deliberately out of scope — same boundary the
# breakpoint register draws, and for the same reason.
SHIPPING = ("tokens.css", "base.css", "components.css")

# The scale, in order. The step number is the multiple of the 4 px base unit.
STEPS = (1, 2, 3, 4, 5, 6, 8, 12, 16, 20, 24, 30, 40)

# Steps allowed to sit at zero consumers. None today. --space-30 (120) sat
# here for as long as it was a landmark with no consumer — the value the
# rhythm landed on at the 1440 frame while the clamp's ceiling was written as
# --space-40. The ceiling is --space-30 now, so the landmark is the consumer,
# and every rung of the scale is earned. A step reaching zero is a finding;
# foundations/layout.html says what to do about it: delete the rung.
UNUSED_OK = set()

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

# ---------------------------------------------------------------------------
# The markup half.

# An opening tag, and the style attribute inside one. Double quotes only:
# this system does not write single-quoted attributes, and a pattern that
# accepted them would start reading apostrophes in German prose as delimiters.
TAG = re.compile(r"<[a-zA-Z][^<>]*>")
STYLE_ATTR = re.compile(r'\sstyle="([^"]*)"')

# Values that are a reset rather than a distance. `0` in any unit is already
# covered by FREE; these are the wordy ones a shorthand can carry.
INLINE_FREE = {"0", "auto", "none", "0 auto", "auto 0"}

# The two flow primitives own their spacing through --flow and the .flow-*
# rungs. An inline gap or margin on either is not a distance the scale is
# missing, it is the rung family being bypassed — see base.css.
FLOW_OWNERS = ("stack", "cluster")

# Inline spacing values that are genuinely outside the scale, each with the
# reason. Same rule as ALLOWED above: a long list means the scale is wrong.
ALLOWED_MARKUP = set()


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


def pages():
    """Every page under design-system/, source only.

    /en/ is skipped because those files are built from these by
    build-i18n.py — a finding there is the same finding twice, reported
    against a path a fix cannot be written to."""
    for path in sorted(DS.rglob("*.html")):
        if "/en/" in path.as_posix():
            continue
        yield path, path.read_text(encoding="utf-8")


def inline_spacing():
    """(path, line, classes, prop, value) for every spacing declaration that
    lives in a style attribute rather than in a stylesheet.

    Scanned tag by tag rather than line by line, and that is not tidiness.
    These pages quote inline overrides in their own prose — foundations/
    layout.html sets `style="gap:var(--space-8)"` in a <code> span, inside the
    paragraph explaining why that declaration is the thing the .flow-* rungs
    exist to replace. A pattern that reads a style attribute out of running text
    would report the documentation of the defect as the defect. A tag is what an
    attribute belongs to, so a tag is what this reads. Escaped samples are safe
    by the same construction: `&lt;div style=...` never opens a tag."""
    for path, text in pages():
        for tag in TAG.finditer(text):
            attrs = tag.group(0)
            style = STYLE_ATTR.search(attrs)
            if not style:
                continue
            cls = re.search(r'\sclass="([^"]*)"', attrs)
            classes = cls.group(1).split() if cls else []
            line_no = text.count("\n", 0, tag.start()) + 1
            for decl in style.group(1).split(";"):
                prop, sep, value = decl.partition(":")
                prop, value = prop.strip().lower(), " ".join(value.split())
                if not sep or not SPACING_PROP.fullmatch(prop):
                    continue
                yield path, line_no, classes, prop, value


def markup_findings(verbose):
    """MARKUP and FLOW, over the same declarations."""
    failures = []
    live = 0
    for path, line, classes, prop, value in inline_spacing():
        rel = path.relative_to(ROOT).as_posix()
        if value in INLINE_FREE:
            continue
        live += 1
        if verbose:
            print("  %s:%d  %s%s: %s"
                  % (rel, line, "." + ".".join(classes) + " " if classes else "",
                     prop, value))

        owner = next((c for c in classes if c in FLOW_OWNERS), None)
        if owner:
            failures.append(
                "%s:%d writes spacing into a .%s:\n"
                "        %s: %s\n"
                "    .stack and .cluster resolve their spacing through --flow, so this does\n"
                "    not sit beside the system's answer, it overrides it. Use a .flow-* rung\n"
                "    — .flow-2/3/6/8/12 — or add the rung the family is missing to base.css."
                % (rel, line, owner, prop, value))
            continue

        off = [m.group(0) for m in LENGTH.finditer(value)
               if m.group(0) not in FREE]
        if off and (rel, "%s: %s" % (prop, value)) not in ALLOWED_MARKUP:
            failures.append(
                "%s:%d writes spacing as a length rather than a token, in markup:\n"
                "        %s: %s\n"
                "    A style attribute is the one place a distance hides from every reader\n"
                "    of a stylesheet. Use a --space-* token; if the same decision is made\n"
                "    twice, it is a rule and belongs in a stylesheet under a name. If it\n"
                "    genuinely sits outside the scale, add it to ALLOWED_MARKUP here with\n"
                "    the reason." % (rel, line, prop, value))
    return failures, live


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
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every rung and every inline spacing declaration")
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

    if args.verbose:
        for step, n in zip(STEPS, counts):
            print("  --space-%-3d %4d px  %3d declaration(s)" % (step, step * 4, n))
        print()
    markup, live = markup_findings(args.verbose)
    failures.extend(markup)

    if failures:
        print("spacing scale: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    print("spacing scale: stamp %s, %d rungs, no off-scale literals in the three "
          "stylesheets and none in the %d live inline declaration(s)."
          % (stamp, len(STEPS), live))
    return 0


if __name__ == "__main__":
    sys.exit(main())
