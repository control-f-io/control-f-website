#!/usr/bin/env python3
"""The mobile record covers every pattern page there is, and says how many that is.

foundations/mobile.html is the breakpoint register's other half: the measured
record of what the shipping pattern pages do on the way down to a phone. Its
two load-bearing claims are counts — "no page overflows sideways at any width
down to 320", measured page by page, and a target-size table with one row per
page. Both go stale the same way: a sixteenth page lands in patterns/ and the
record silently stops covering the section while every sentence in it stays
true of the pages it was measured on.

THIS HAS HAPPENED FOUR TIMES, AND THE PAGE SAYS SO ITSELF. Its own notes read
"This note said 'seven pattern pages' until there were twelve", "It went stale
again while this was being written", "And a third time: twelve became
fourteen" — and the run that added this check found the fourth: karriere-leer
landed in the same hour as the footer unification, and the page said fourteen
while the directory held fifteen. Each time, the drift was found by a reader,
because a count in prose binds nothing. The page's history is the argument
for the gate; the gate is what the history was missing.

WHAT THIS KNOWS THAT A SCREENSHOT CANNOT. A stale count renders perfectly.
The fourteen measured pages still measure zero overflow; the missing page is
exactly the one nothing measured, and it is invisible on every page anyone
opens. But the claim is countable in two files: the pattern directory is a
set of filenames, and the record is a table of rows plus a handful of typed
numbers. They either agree or they do not.

THE RULES, all read from foundations/mobile.html with comments, <pre> and
<code> masked:

  TABLE   the target-size table (the one headed Page / Controls / Under 24 px)
          carries exactly one row per file in design-system/patterns/ — no
          page missing, no row for a page that is gone.
  PHRASE  every "all N pattern pages" states N equal to the file count.
  WIDTHS  every "N page-widths" states N equal to three times the file count
          — the circle test runs at 320, 375 and 768, as the sentence around
          the number says.
  MATRIX  every "N measurements" states N equal to six times the file count —
          the overflow matrix is 320/375/390/768/1280/1920, as the note
          around the number says. Add a seventh width and this fails until
          the multiplier here is changed with it, which is the point: a
          measured claim's arithmetic is not allowed to move silently.

N may be typed as digits or as an English number word up to ninety-nine,
hyphenated or not, because the page writes both ("Forty-five page-widths",
"90 measurements").

WHAT A FAILURE MEANS. Do not patch the number. The page's own third note
states the house rule: a claim this page has watched go false four times "is
not one to update by arithmetic". Re-run the matrix — serve the tree, drive a
real browser across every page in patterns/ at the six widths, re-count the
targets — and update the table and every count from the run, in the same
commit as the page that moved them.

Reintroduce the bug — delete the karriere-leer row, or set any of the four
counts back one step — and this fails, naming the row or the number and the
line it sits on.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system/patterns"
MOBILE = ROOT / "design-system/foundations/mobile.html"

UNITS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}


def number(token):
    """Digits or an English number word up to ninety-nine, else None."""
    token = token.lower()
    if token.isdigit():
        return int(token)
    if token in UNITS:
        return UNITS[token]
    if token in TENS:
        return TENS[token]
    if "-" in token:
        tens, _, unit = token.partition("-")
        if tens in TENS and unit in UNITS and UNITS[unit] < 10:
            return TENS[tens] + UNITS[unit]
    return None


def mask(html):
    """Blank comments, <pre> and <code> spans, preserving offsets so line
    numbers stay honest."""
    def blank(match):
        return re.sub(r"[^\n]", " ", match.group(0))
    html = re.sub(r"<!--.*?-->", blank, html, flags=re.S)
    html = re.sub(r"<pre\b.*?</pre>", blank, html, flags=re.S | re.I)
    html = re.sub(r"<code\b.*?</code>", blank, html, flags=re.S | re.I)
    return html


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def main():
    # THE SPECIMENS, AND NOT THE CONTENT. patterns/beitrag-*.html is one post
    # of the news archive spliced into blog-artikel.html by
    # scripts/build-articles.py: same markup, same components, same widths,
    # different words. patterns/news-thema-<slug>.html is the same relationship
    # to news-thema.html — one topic's slice of the archive, in the columns the
    # specimen was measured in. The record this file holds is a set of
    # MEASUREMENTS, and the page's own notes say a count is never updated by
    # arithmetic — so a page per post or per topic would mean a re-run of the
    # matrix every time somebody publishes, to record the numbers already
    # recorded for the specimen.
    pages = sorted(p.stem for p in PATTERNS.glob("*.html")
                   if not p.name.startswith(("beitrag-", "stelle-", "news-thema-")))
    if not pages:
        print("check-mobile-coverage: no pages found under design-system/patterns/")
        return 1
    count = len(pages)

    raw = MOBILE.read_text(encoding="utf-8")
    html = mask(raw)
    text = re.sub(r"<[^>]+>", " ", html)  # tag-stripped copy, offsets kept

    failures = []

    # TABLE — find the target-size table by its header row.
    table_match = None
    for m in re.finditer(r"<table\b.*?</table>", html, flags=re.S | re.I):
        head = re.sub(r"<[^>]+>", " ", m.group(0)[:600])
        if re.search(r"\bPage\b", head) and re.search(r"\bControls\b", head) \
                and re.search(r"Under\s*24", head):
            table_match = m
            break
    if table_match is None:
        failures.append("the target-size table (Page / Controls / Under 24 px) "
                        "was not found in foundations/mobile.html at all")
    else:
        rows = re.findall(r"<tr>\s*<td>(.*?)</td>", table_match.group(0),
                          flags=re.S | re.I)
        row_names = {re.sub(r"<[^>]+>", "", r).strip() for r in rows}
        table_line = line_of(html, table_match.start())
        for page in pages:
            if page not in row_names:
                failures.append(
                    f"patterns/{page}.html has no row in the target-size table "
                    f"(line {table_line}) — the record stopped covering the "
                    f"section; re-run the matrix, do not just add a row")
        for name in sorted(row_names - set(pages)):
            failures.append(
                f"the target-size table (line {table_line}) has a row for "
                f"“{name}” but patterns/{name}.html does not exist")

    # PHRASE / WIDTHS / MATRIX — typed counts against the directory.
    claims = (
        (r"\ball\s+([A-Za-z-]+|\d+)\s+pattern\s+pages", count,
         "pattern pages in design-system/patterns/"),
        (r"\b([A-Za-z-]+|\d+)\s+page-widths", 3 * count,
         "page-widths (three circle-test widths per page)"),
        (r"\b([A-Za-z-]+|\d+)\s+measurements", 6 * count,
         "measurements (six overflow widths per page)"),
    )
    for pattern, expected, what in claims:
        for m in re.finditer(pattern, text, flags=re.I):
            n = number(m.group(1))
            if n is None:
                continue
            if n != expected:
                failures.append(
                    f"line {line_of(text, m.start())}: “{m.group(0)}” "
                    f"— the directory holds {count} pages, so this should read "
                    f"{expected} {what}")

    if failures:
        print(f"check-mobile-coverage: {len(failures)} failure(s) against "
              f"{count} pages in design-system/patterns/\n")
        for f in failures:
            print(f"  {f}")
        print("\nA failure here means the measured record and the pattern "
              "directory disagree. Re-run the measurements on every page and "
              "update foundations/mobile.html from the run — the page's own "
              "notes say why a count is never updated by arithmetic.")
        return 1

    print(f"mobile coverage: the record in foundations/mobile.html covers all "
          f"{count} pattern pages — table complete, every typed count agrees "
          f"with the directory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
