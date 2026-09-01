#!/usr/bin/env python3
"""The motion chapter's census of its own tokens is the stylesheets' count.

foundations/motion.html publishes two tables — the four durations and the three
curves — and each row ends in a column headed "In the CSS today": how many rules
in the shipping stylesheets reach for that token. The page says of that column,
in its own words, that it "has now gone stale three times, and it is still the
only part of this page that can rot without anything rendering wrong", and then
asks the reader to run a python one-liner rather than read the numbers.

It went stale a fourth time. Measured on 2026-09-01 the page published 15 / 11 /
8 / none against stylesheets holding 18 / 13 / 11 / 1 — and the "1" is the part
that matters, because the prose beneath the table went further than the number:
"--duration-scene genuinely has no consumer", and of --ease-in-out, "it is still
the one curve with no consumer". Both sentences were true when written. The
scroll cue's comet has run at --duration-scene since the cue was drawn, and the
indeterminate progress rail sweeps on --ease-in-out. Nothing rendered wrong, and
a page that exists to say what the system does was saying the opposite about two
of its seven tokens.

A number a reader is told not to trust is a number that should not be on the
page by hand. This script is the one-liner the page used to print, run by CI,
holding the column to the stylesheets in both directions, with `--fix` to
rewrite the cells the way check-spacing-scale.py rewrites its table.

WHAT IS COUNTED. Rules, not var() occurrences — the page's own distinction: a
rule naming a token twice is one consumer, not two. Comments are stripped first,
because the stylesheets discuss these tokens in prose at length and a naive
grep counts the discussion. A consumer is a declaration block containing
`var(--<token>)` or `var(--<token>, <fallback>)`; the block in tokens.css that
DEFINES the token is not a var() and never enters the count.

THE SCOPE IS THE FOUR SHIPPING STYLESHEETS, and the fourth is the correction.
The page's one-liner read tokens.css, base.css and components.css. acts.css —
6 300 lines of scroll composition that patterns/landing-page.html loads — was
not among them, which is the exact omission check-gradient-family.py records
having made once already: "it was never excluded on purpose". acts.css names
--ease-out in a dozen rules and --ease-in-out in two. docs.css and preview.css
do not ship, which is the boundary check-spacing-scale.py draws.

THE SECOND RULE IS THE ONE THAT WAS BROKEN ON A DESIGNED PAGE. The tokens exist
so that every curve on the site is one of three; foundations/motion.html states
it — "there is no elastic curve in the system and there should not be one" —
and the lane brief for anything that moves reads "durations and curves are
already tokenised; use them". acts.css ran the sensor field's pulse on the
KEYWORD `ease-in-out` in two rules: cubic-bezier(0.42, 0, 0.58, 1), where the
token is cubic-bezier(0.4, 0, 0.2, 1). A pulse — a state that swells and
settles back — is the token's stated purpose to the word; so is the leaf
shimmer two rules further on, an `alternate` loop between two stroke opacities,
which ran on the same keyword. Four rules, one stylesheet, and every one of them
the token's own sentence. So: no `ease`,
`ease-in`, `ease-out`, `ease-in-out` or bare `cubic-bezier()` in a transition
or animation value in the shipping stylesheets, except as the FALLBACK inside a
var() — `var(--ease-out, ease-out)` is the token with a net under it, which is
right. `linear` is not a curve and is left alone: the motion chapter reaches
for it on purpose wherever light crosses a surface. `steps()` likewise.

AND THE VALUES ARE HELD TOO, because a table with a checked column and an
unchecked one beside it teaches the wrong lesson. The "Duration" and "Value"
cells must be the token's declaration in tokens.css — 120ms as "120 ms",
cubic-bezier(0.2, 0, 0, 1) as "cubic-bezier(.2, 0, 0, 1)" — compared as
numbers, so the page's leading-zero style is not a finding.

WHAT THIS DELIBERATELY DOES NOT DO. It does not judge which token a rule should
have used, and it does not read the prose: a sentence claiming a token is
unconsumed is the reader's to weigh against the column beside it. The column
is the fact; the sentences are the argument.

Usage:
    check-motion-census.py          fail if the tables or the curves are off
    check-motion-census.py -v       print every consumer, by selector
    check-motion-census.py --fix    rewrite the count cells in motion.html
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DS = os.path.join(ROOT, "design-system")
PAGE = os.path.join(DS, "foundations", "motion.html")
TOKENS = os.path.join(DS, "assets", "css", "tokens.css")

# The shipping stylesheets. docs.css and preview.css are documentation chrome.
SHEETS = ["tokens.css", "base.css", "components.css", "acts.css"]

DURATIONS = ["duration-fast", "duration-base", "duration-slow", "duration-scene"]
CURVES = ["ease-standard", "ease-out", "ease-in-out"]

COMMENT = re.compile(r"/\*.*?\*/", re.S)
BLOCK = re.compile(r"([^{}]*)\{([^{}]*)\}")
# A raw curve in a transition/animation value: the keywords and a bare
# cubic-bezier(), outside any var(). linear and steps() are not curves here.
MOTION_DECL = re.compile(
    r"(?:^|[;{\s])(transition|animation)(?:-timing-function)?\s*:\s*([^;{}]+)"
)
RAW_CURVE = re.compile(r"(?<![-\w])(ease-in-out|ease-in|ease-out|ease|cubic-bezier\()(?![-\w])")
VAR = re.compile(r"var\(\s*--[\w-]+(?:\s*,[^()]*(?:\([^()]*\))?[^()]*)?\)")

# One row is one line of the page. Anchored on the newline rather than on `.*?`
# with DOTALL, which was measured spanning from one row's third cell into the
# next row's before it found a fourth.
ROW = (
    r"<tr><td><code>--(%s)</code></td><td>([^<\n]*)</td><td>([^\n]*?)</td><td>([^\n]*?)</td></tr>"
)
NUM = re.compile(r"-?\d*\.?\d+")


def strip(css):
    # Newlines survive so a finding's line number is the file's, not the
    # stripped text's.
    return COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), css)


def stylesheets():
    out = []
    for name in SHEETS:
        path = os.path.join(DS, "assets", "css", name)
        with open(path, encoding="utf-8") as fh:
            out.append((name, strip(fh.read())))
    return out


def consumers(sheets, token):
    """Every declaration block reaching for var(--token), as (sheet, selector)."""
    needle = re.compile(r"var\(\s*--%s\s*[,)]" % re.escape(token))
    found = []
    for name, css in sheets:
        for m in BLOCK.finditer(css):
            body = m.group(2)
            if needle.search(body):
                selector = m.group(1).strip().split("\n")[-1].strip()
                found.append((name, selector))
    return found


def raw_curves(sheets):
    """Transition/animation values carrying a curve that is not a token."""
    found = []
    for name, css in sheets:
        for m in MOTION_DECL.finditer(css):
            value = VAR.sub("VAR", m.group(2))
            hit = RAW_CURVE.search(value)
            if hit:
                line = css[: m.start()].count("\n") + 1
                found.append((name, line, hit.group(1), " ".join(m.group(0).split())))
    return found


def token_values():
    """The declared value of each token, from tokens.css's :root."""
    with open(TOKENS, encoding="utf-8") as fh:
        css = strip(fh.read())
    values = {}
    for token in DURATIONS + CURVES:
        # The first declaration is :root's; the reduced-motion block redeclares
        # the durations to 1ms further down and is not the value the table states.
        m = re.search(r"--%s\s*:\s*([^;]+);" % re.escape(token), css)
        if m:
            values[token] = m.group(1).strip()
    return values


def numbers(text):
    return [float(n) for n in NUM.findall(text)]


def cell_count(text):
    """'18 rules' -> 18, '1 rule' -> 1, 'none' (optionally wrapped) -> 0."""
    plain = re.sub(r"<[^>]+>", "", text).strip()
    if plain == "none":
        return 0
    m = re.fullmatch(r"(\d+) rules?", plain)
    return int(m.group(1)) if m else None


def cell_text(n):
    return "none" if n == 0 else ("1 rule" if n == 1 else "%d rules" % n)


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    fix = "--fix" in sys.argv

    sheets = stylesheets()
    values = token_values()
    with open(PAGE, encoding="utf-8") as fh:
        page = fh.read()

    findings = []
    counts = {}
    for token in DURATIONS + CURVES:
        rules = consumers(sheets, token)
        counts[token] = len(rules)
        if verbose:
            print("--%s  %d rule(s)" % (token, len(rules)))
            for name, selector in rules:
                print("    %-16s %s" % (name, selector))

    # The two tables, row by row.
    seen = set()
    for family in (DURATIONS, CURVES):
        pattern = re.compile(ROW % "|".join(re.escape(t) for t in family))
        for m in pattern.finditer(page):
            token, value_cell, _, count_cell = m.groups()
            seen.add(token)
            declared = values.get(token)
            if declared is None:
                findings.append("--%s is in the table and not in tokens.css" % token)
            elif numbers(value_cell) != numbers(declared):
                findings.append(
                    "--%s: the page states %r, tokens.css declares %r"
                    % (token, value_cell.strip(), declared)
                )
            stated = cell_count(count_cell)
            if stated is None:
                findings.append(
                    "--%s: the count cell reads %r, which is not 'N rules' or 'none'"
                    % (token, count_cell)
                )
            elif stated != counts[token]:
                findings.append(
                    "--%s: the page says %s, the stylesheets hold %s"
                    % (token, cell_text(stated), cell_text(counts[token]))
                )
                if fix:
                    page = page.replace(m.group(0), m.group(0).replace(
                        "<td>%s</td></tr>" % count_cell,
                        "<td>%s</td></tr>" % cell_text(counts[token])))
    for token in DURATIONS + CURVES:
        if token not in seen:
            findings.append("--%s has no row in foundations/motion.html" % token)

    raw = raw_curves(sheets)
    for name, line, curve, decl in raw:
        findings.append(
            "%s:%d reaches past the tokens for `%s`: %s" % (name, line, curve, decl[:80])
        )

    if fix:
        with open(PAGE, "w", encoding="utf-8") as fh:
            fh.write(page)
        fixed = [f for f in findings if "the page says" in f]
        findings = [f for f in findings if "the page says" not in f]
        for f in fixed:
            print("fixed   " + f)

    if findings:
        print("check-motion-census.py: %d finding(s)" % len(findings))
        for f in findings:
            print("  " + f)
        if any("the page says" in f for f in findings):
            print("  run with --fix to rewrite the count cells")
        return 1

    print(
        "motion census: %s; %s; every value the tokens' own; no raw curve in %s."
        % (
            ", ".join("--%s %d" % (t, counts[t]) for t in DURATIONS),
            ", ".join("--%s %d" % (t, counts[t]) for t in CURVES),
            "/".join(SHEETS),
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
