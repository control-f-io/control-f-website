#!/usr/bin/env python3
"""Keep the register for the thresholds the register in tokens.css excludes.

A threshold cannot be a design token — `var()` is not allowed in the prelude of
`@media` or `@container`, and `@custom-media` needs a build step this system
does not have. So every threshold is a literal typed into a stylesheet, and the
only defence against them multiplying is a register: one list, added to on
purpose. tokens.css carries that register, foundations/layout.html carries the
second copy of it, and scripts/check-breakpoints.py holds the two to each other.

That register is explicitly, correctly, about the three stylesheets that ship.
Its SCOPE section names what it leaves out, and the second entry is this file's
subject:

    inline <style>      per-page demo styles. foundations/iconography.html asks
                        a VIEWPORT 48rem where 48rem above is a CONTAINER
                        threshold.

The exclusion is right — governing page-local blocks from tokens.css would make
that register look like it governed the documentation chrome — but it left the
page-local thresholds registered nowhere, and a threshold registered nowhere is
a number the next person to reason about where this system folds will not find.

WHAT IT CHECKS

  live -> register    every width/height threshold in a page-local <style>
                      block has a row in THRESHOLDS below.
  register -> live    every row still has a query behind it, so a threshold
                      that was removed does not linger as a row describing
                      behaviour the system no longer has.
  register -> table   foundations/layout.html carries a table headed "What sits
                      outside the register, in full", and the word is the whole
                      claim. It must hold one row per threshold outside the
                      register's scope — the rows above, plus docs.css and
                      prototypes/, which this file does not govern but which the
                      table does have to list. Both directions, so a row cannot
                      outlive its query either. See below for why that table
                      needed a check rather than a proofread.
  the rem rule        no px width/height threshold under patterns/,
                      foundations/ or components/, and none in docs.css. A
                      media query's rem resolves against the BROWSER's default
                      font size, so a rem threshold is the only kind that
                      tracks a reader who has asked for larger type. There is
                      no PX DEBT tier any more: the four rows that carried it
                      were converted, and the rule now reaches every file in
                      front of a reader. Only prototypes/ is exempt, because
                      the README declares it unreconciled with the tokens.
                      NOTE THAT DOCS.CSS IS OUTSIDE THE REGISTER AND INSIDE
                      THIS RULE — being written down and answering to the
                      reader's font size are two different questions.
  the px gloss        the figure after each slash is what the threshold
                      resolves to at a 16 px default. Derived here, not trusted.

WHY THIS EXISTS, WHICH IS A BUG IT WOULD HAVE CAUGHT

patterns/expertise.html gated its pinned, scroll-scrubbed stage on
`(min-width: 820px)` — the number prototypes/expertise-scroll.html asks, carried
across into patterns/ along with the mechanism. patterns/landing-page.html runs
the same mechanism and gates it on `(min-width: 64rem) and (min-height: 45rem)`,
derived for its own card and documented in place.

The 820 was wrong in both units and both dimensions, and the reason is a fact
about the page rather than a taste about numbers: the stage is only habitable
once `.ex-step` has its TWO columns, and that fold is a CONTAINER query at
56rem. A px gate cannot track a rem fold. So the pin arrived at a fixed 820
while the two-column form arrived wherever 56rem of container happened to land,
and between the two the stage pinned a stacked step into 100vh of
`overflow: clip` and cropped it:

    default font   pins at   two columns at   cropped band   worst crop
      16 px          820          1007           187 px         84 px
      20 px          820          1259           439 px        173 px
      24 px          820          1511           691 px        297 px

The reader who asked for larger type lost the most, which is the exact failure
the register's rem rule exists to prevent. None of it is visible at 375, 768 or
1280 — the three widths anyone checks — because all three are outside the band.

AND A SECOND BUG, WHICH IS WHY THE TABLE RULE EXISTS

The table on foundations/layout.html was written before this file was, and it
opens "What sits outside the register, in full". It listed five queries and
counted them in prose: "one in docs.css, three in per-page <style> blocks, one
in a prototype". Measured against the tree it now merges into, that is five of
twelve. Missing: both of patterns/expertise.html's own thresholds and its
adopted pin gate, foundations/illustration.html's 640 and
foundations/transitions.html's 900, and both of
prototypes/expertise-scroll.html's.

The last of those is the interesting one. The table excused it in a
parenthesis — "the two prefers-reduced-motion queries in prototypes/ are not
thresholds and are not listed" — and that sentence was true of the queries it
was written about and false of this one, which reads

    @media screen and (prefers-reduced-motion: no-preference) and (min-width: 820px)

A MODE QUERY THAT CARRIES A WIDTH IS STILL A THRESHOLD. The layout changes
shape at 820 px whatever else the prelude also asks, and a rule that sorts
queries by their first feature will keep missing that shape. This file sorts by
whether a dimension appears anywhere in the prelude, which is why the sweep
finds it and the proofread did not.

Every one of those rows renders perfectly. What a short list costs is the next
person to ask where this system folds: they read a table that says "in full",
and it is not.

WHAT IT DOES NOT CHECK, deliberately

  Anything about classes, literals or inline layout in a page-local block. Those
  are the class-provenance check's subject — resolving every class use against
  the stylesheets that declare it, rejecting a colour or spacing literal where a
  token exists, rejecting inline layout under patterns/ — and it was written in
  the same hour as this file, in the same lane, from the same starting
  observation that page-local blocks were governed by nothing. Two scripts
  carrying overlapping rules are two things that can disagree, which is the
  failure mode this whole family exists to prevent. So this file stops at
  thresholds, which is the one part of that scope the other does not reach, and
  says so here rather than leaving the next reader to diff them.

  The shipping stylesheets — the three shared ones and acts.css, the landing
  page's own sheet. check-breakpoints.py owns those, keeps both copies of
  their register in step, and is stricter — no px threshold at all. A page
  stylesheet registers there rather than here because its thresholds ship:
  page-local ownership does not make a fold any less the reader's. This file
  governs only what that one names as out of scope.

  prototypes/, and docs.css — for the REGISTER. Declared not-yet-system by the
  README with their own unreconciled styling, and documentation chrome,
  respectively: out of scope by the same boundary every other check draws, and
  neither gets a row in THRESHOLDS. They ARE swept for the table rule, because
  listing a threshold is not governing it — that is the whole argument of the
  table, which exists to say what the register leaves out. A threshold that
  appears there and nowhere else is still findable; one that appears nowhere is
  not.

  THE REM RULE IS A DIFFERENT RULE AND DOCS.CSS IS NOW INSIDE IT. The register
  asks which thresholds are written down; the rem rule asks whose font size a
  threshold answers to. The second question is about a reader, not about
  ownership, and docs.css's frame is what every page of this documentation is
  read in — measured at 492 px of horizontal scroll at 200 % text before the
  conversion. prototypes/ stays exempt from both: reconciling a prototype is
  not the job, and the outside-the-register table says so in place.

  Crossovers. A min() or clamp() against a viewport unit also changes layout at
  a specific width, when its arms swap. None is a query, and the register in
  tokens.css spends a paragraph saying why they stay out. Widening the
  definition here would enforce a different rule than the one written down.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-local-thresholds.py       # check, exit 1 on a finding
    python3 scripts/check-local-thresholds.py -v    # print the register
"""

import argparse
import pathlib
import re
import sys
from html import unescape

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# The second copy of this register, and the only place docs.css's and
# prototypes/'s thresholds are written down at all.
LAYOUT_DOC = DS / "foundations" / "layout.html"
TABLE_ID = "outside-register"

# Out of scope, with the reason in the docstring above.
EXCLUDED_DIRS = ("prototypes",)

# Swept for the table rule only: never governed, always listed. docs.css is the
# documentation chrome; prototypes/ are declared not-yet-system by the README.
OUT_OF_SCOPE = ("assets/css/docs.css", "prototypes")

# THE REM RULE AND THE REGISTER ARE TWO RULES, and separating them is what this
# line is for. The REGISTER decides which thresholds are written down, and
# docs.css stays outside it — its row in the outside-the-register table is the
# whole argument. The REM RULE decides whose font size a threshold answers to,
# and that question is about a reader rather than about ownership: a px gate in
# front of a rem layout opens a band that grows with the reader's type,
# whichever file it is typed in.
#
# docs.css's frame carried the last unconverted one, and nobody had measured
# it. Its sidebar track is 17rem and its fold was 900px, so the two drifted
# apart as the reader's default rose: measured in Chromium on four
# documentation pages, 161 px of horizontal scroll at a 901 px viewport at a
# 24 px default and 492 px at a 32 px one — 200 % text, which is what WCAG
# 1.4.4 asks for — against none at any width at 16 px. That is the fault the
# register's own rem rule was written after, an order of magnitude larger, on
# the pages that document the fix. The full record is on
# foundations/layout.html#outside-register and in the comment over the query.
PX_STRICT_FILES = ("assets/css/docs.css",)

# patterns/ is held to the rem rule outright. A pattern page stands in for a
# page of the real site, so a reader's font size is a reader's font size there.
#
# foundations/ JOINED IT, and the note that used to sit over its four px rows
# is why: they were "counted rather than failed because foundations/ is not
# this lane's". Thresholds are the layout lane's subject and this is that lane,
# so the debt was collected rather than handed on. The second half of that
# note — "a demo page's threshold is about a specimen rather than about a page
# a reader reads" — is true of a specimen and false of a frame, and the two
# 900s were frames: docs.css's sidebar and transitions.html's stack of demos
# are what a reader reads the documentation IN. components/ carries no width
# threshold of its own and joins on the same terms.
PX_STRICT_DIRS = ("patterns", "foundations", "components")

# ---------------------------------------------------------------------------
# THE REGISTER
#
# (file, prelude-fragment) -> why the threshold exists. The fragment is matched
# against the normalised prelude, so one row covers a compound query. Same
# convention as tokens.css: the figure after a slash is what the threshold
# resolves to at a 16 px default and is derived, never typed twice.
# ---------------------------------------------------------------------------
THRESHOLDS = {
    # -- patterns/ — both pages run one mechanism, and now on one gate --------
    ("patterns/expertise.html", "(max-height: 53.75rem)"):
        "--field-unit steps 6rem -> 4.5rem so the lattice and the drawing standing on "
        "it shrink as a pair and the object stays one cell per lattice step.",
    ("patterns/expertise.html", "layout (min-width: 56rem)"):
        "the step takes its two columns. A CONTAINER query, and the one the pinned "
        "gate below has to clear — the whole argument in the docstring above.",
    ("patterns/expertise.html", "(min-width: 64rem) and (min-height: 45rem)"):
        "the pinned, scroll-scrubbed stage. THE LANDING PAGE'S GATE, adopted rather "
        "than re-derived: one mechanism, one gate. Was `820px`, which is where the "
        "crop band came from. The mechanism is .cf-pin in components.css now and the "
        "gate is registered in tokens.css; this copy of the prelude only scopes what "
        "stays page-local.",

    # -- foundations/ — documentation chrome ---------------------------------
    # ALL FIVE ARE rem NOW, and the four that were px are the debt this lane
    # collected rather than handed on — see PX_STRICT_DIRS. Each renders
    # identically at a 16 px default and folds where the reader actually runs
    # out of room above it. The count is printed on every run and cannot grow
    # without an edit here.
    ("foundations/iconography.html", "(max-width: 48rem)"):
        "the icon grid folds. Already named in tokens.css's SCOPE list, as the example "
        "of a page-local VIEWPORT 48rem colliding with a shipping CONTAINER 48rem — "
        "same figure, unrelated queries, do not reconcile them.",
    ("foundations/illustration.html", "(max-width:40rem)"):
        "The illustration plate folds to one column. Was `640px`; 640 / 16 = 40.",
    ("foundations/layout.html", "(max-width:40rem)"):
        "The space-scale demo folds. Was `640px`; 640 / 16 = 40.",
    ("foundations/materials.html", "(max-width:48.75rem)"):
        "The glass demos stack. Was `780px`; 780 / 16 = 48.75, which makes it a "
        "DUPLICATE of the shipping nav threshold again rather than the divergence it "
        "had become. Same figure, unrelated queries — do not reconcile them.",
    ("foundations/transitions.html", "(max-width: 56.25rem)"):
        "The transition demos stack. Was `900px`; 900 / 16 = 56.25. Now the same "
        "figure as the shipping 56.25rem and as docs.css's own sidebar query, which "
        "it was already renderng at — and unrelated to both.",
}


def blank(match):
    """Replace a span with as many newlines as it held, so line numbers survive.

    Every line number reported here is a line number in the FILE: a finding you
    cannot jump to is a finding somebody has to go and find.
    """
    return "\n" * match.group(0).count("\n")


def local_css(text):
    """The page's <style> content, with everything else blanked line-for-line."""
    out, pos = [], 0
    for m in re.finditer(r"(<style[^>]*>)(.*?)(</style>)", text, re.S):
        out.append("\n" * text.count("\n", pos, m.start(2)))
        out.append(m.group(2))
        pos = m.end(2)
    out.append("\n" * text.count("\n", pos, len(text)))
    return re.sub(r"/\*.*?\*/", blank, "".join(out), flags=re.S)


def preludes(css):
    """(prelude, line) for every @media/@container at-rule, whitespace-normalised."""
    return [
        (" ".join(m.group(2).split()), css[: m.start()].count("\n") + 1)
        for m in re.finditer(r"@(media|container)([^{]*)\{", css)
    ]


DIMENSION = re.compile(r"\((?:min|max)-(?:width|height)\s*:\s*[^)]+\)")


def squash(text):
    """Whitespace removed entirely, so two spellings of one query compare equal.

    The tree writes both `(max-width: 640px)` and `(max-width:640px)`, and the
    table is transcribed by hand. Comparing on the characters that carry meaning
    is the difference between a rule about thresholds and a rule about typing.
    """
    return "".join(text.split())


def dimensions(prelude):
    """Every width/height feature in a prelude, squashed.

    Anywhere in the prelude, not only at its head: a mode query that carries a
    width is still a threshold. See the docstring — that is the row the hand-kept
    table missed.
    """
    return [squash(t) for t in DIMENSION.findall(prelude)]


def out_of_scope_thresholds():
    """(file, prelude, line) for every threshold this file lists but never governs."""
    out = []
    for entry in OUT_OF_SCOPE:
        base = DS / entry
        for path in sorted(base.rglob("*.html")) if base.is_dir() else [base]:
            text = path.read_text(encoding="utf-8")
            css = (
                re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
                if path.suffix == ".css"
                else local_css(text)
            )
            for pre, line in preludes(css):
                if dimensions(pre):
                    out.append((path.relative_to(DS).as_posix(), pre, line))
    return out


def table_rows():
    """(where, query) for every row of the outside-the-register table, as text.

    Two cells, both stripped of markup: the file a threshold is written in and
    the query as transcribed. Cell three is prose about what it collides with
    and is nobody's to check.
    """
    doc = LAYOUT_DOC.read_text(encoding="utf-8")
    start = doc.find('id="%s"' % TABLE_ID)
    if start < 0:
        sys.exit(
            "check-local-thresholds: foundations/layout.html has no table with "
            'id="%s". That table is the second copy of this register; without it '
            "there is nothing to hold the register to." % TABLE_ID
        )
    block = doc[start : doc.find("</table>", start)]

    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", block, re.S):
        cells = [
            unescape(re.sub(r"<[^>]+>", "", c)).strip()
            for c in re.findall(r"<td>(.*?)</td>", tr, re.S)
        ]
        if len(cells) >= 2:
            rows.append((cells[0], cells[1]))
    return rows


def px_gloss(value):
    """What a threshold resolves to at a 16 px default, or None if not derivable."""
    m = re.fullmatch(r"([\d.]+)(rem|em|px)", value.strip())
    if not m:
        return None
    n, unit = float(m.group(1)), m.group(2)
    return int(round(n * 16)) if unit in ("rem", "em") else int(round(n))

# The English edition under patterns/en/ is generated, not written —
# scripts/build-i18n.py builds it from the German page beside it and changes
# only the words. It carries the same markup, the same classes, the same
# thresholds and the same glass by construction, so every fact this file
# keeps is already kept one directory up; asserting it twice would only mean
# two tables to edit whenever one page changes. `build-i18n.py --check` is
# what holds the mirror to its source. Same argument check-links.py makes
# about the generated pages at the repository root.
GENERATED = "patterns/en/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    failures = []
    seen = set()
    found = []

    for path in sorted(DS.rglob("*.html")):
        rel = path.relative_to(DS).as_posix()
        if rel.split("/")[0] in EXCLUDED_DIRS or rel.startswith(GENERATED):
            continue
        css = local_css(path.read_text())
        for pre, line in preludes(css):
            dims = re.findall(r"\((?:min|max)-(?:width|height)\s*:\s*([^)]+)\)", pre)
            if not dims:
                continue

            row = next((k for k in THRESHOLDS if k[0] == rel and k[1] in pre), None)
            if row is None:
                failures.append(
                    "%s:%d asks a threshold with no row in THRESHOLDS:\n"
                    "        @media/@container %s\n"
                    "    Page-local blocks are out of scope for the register in tokens.css by its\n"
                    "    own SCOPE list, so this file is their register. Add the row in the same\n"
                    "    commit, or fold the threshold onto one that already exists."
                    % (rel, line, pre)
                )
            else:
                seen.add(row)

            px = [d.strip() for d in dims if d.strip().endswith("px")]
            if px and rel.split("/")[0] in PX_STRICT_DIRS:
                failures.append(
                    "%s:%d writes a threshold in px: %s\n"
                    "        @media/@container %s\n"
                    "    A media query's rem resolves against the browser's default font size, so\n"
                    "    only a rem threshold tracks a reader who asked for larger type. A px gate\n"
                    "    in front of a rem fold opens a band that grows with the reader — which is\n"
                    "    the bug this file was written after. Convert it to rem."
                    % (rel, line, ", ".join(px), pre)
                )

            found.append((rel, pre, line, dims))

    for row in sorted(set(THRESHOLDS) - seen):
        failures.append(
            "THRESHOLDS has a stale row: %s no longer asks `%s`.\n"
            "    An entry with no query behind it describes behaviour the system does not\n"
            "    have. Delete it." % row
        )

    # --- register -> table ---------------------------------------------------
    # Everything outside the breakpoint register in tokens.css: the page-local
    # blocks this file governs, plus the two scopes it only lists.
    listed_only = out_of_scope_thresholds()
    outside = [(rel, pre, line) for rel, pre, line, _ in found] + listed_only

    # The rem rule reaches a file this register never governs — see
    # PX_STRICT_FILES. Listing a threshold is not governing it, and answering to
    # the reader's font size is not the same thing as being written down.
    for rel, pre, line in listed_only:
        if rel not in PX_STRICT_FILES:
            continue
        px = [d.strip() for d in re.findall(
            r"\((?:min|max)-(?:width|height)\s*:\s*([^)]+)\)", pre) if d.strip().endswith("px")]
        if px:
            failures.append(
                "%s:%d writes a threshold in px: %s\n"
                "        @media/@container %s\n"
                "    This file is outside the register and still inside the rem rule: the two\n"
                "    are different rules. A media query's rem resolves against the browser's\n"
                "    default font size, so only a rem threshold folds where the reader actually\n"
                "    runs out of room. Convert it — the arithmetic is value / 16."
                % (rel, line, ", ".join(px), pre)
            )

    rows = table_rows()
    matched = set()

    for rel, pre, line in outside:
        dims = dimensions(pre)
        hits = [
            i
            for i, (where, query) in enumerate(rows)
            if rel.endswith(where) and all(d in squash(query) for d in dims)
        ]
        if hits:
            matched.update(hits)
        else:
            failures.append(
                "%s:%d is not in the table on foundations/layout.html:\n"
                "        @media/@container %s\n"
                "    That table opens \"What sits outside the register, in full\", and the\n"
                "    word is the claim. Add the row in the same commit as the query — id=\"%s\",\n"
                "    three cells: where, the query as written, what figure it collides with."
                % (rel, line, pre, TABLE_ID)
            )

    for i, (where, query) in enumerate(rows):
        if i not in matched:
            failures.append(
                "the table on foundations/layout.html has a stale row: %s no longer asks\n"
                "        %s\n"
                "    A row with no query behind it describes a fold the system does not have."
                % (where, query)
            )

    if args.verbose:
        print("page-local threshold register — %d rows\n" % len(THRESHOLDS))
        for rel, pre, line, dims in found:
            gloss = ", ".join(
                "%s / %s" % (d.strip(), px_gloss(d) if px_gloss(d) else "?")
                for d in dims
            )
            debt = "  [PX DEBT]" if any(d.strip().endswith("px") for d in dims) else ""
            print("  %s:%d%s\n      %s\n      %s" % (rel, line, debt, pre, gloss))
        print()

    if failures:
        print("local thresholds: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    n_px = sum(
        1 for _, pre, _, dims in found if any(d.strip().endswith("px") for d in dims)
    )
    print(
        "local thresholds: %d page-local thresholds in %d files, all registered; "
        "%d in px, none under %s.\n"
        "                  %d outside the register in all, all listed in full on "
        "foundations/layout.html."
        % (
            len(found),
            len({r for r, _, _, _ in found}),
            n_px,
            "/".join(PX_STRICT_DIRS),
            len(outside),
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
