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
  the rem rule        no px width/height threshold under patterns/. A media
                      query's rem resolves against the BROWSER's default font
                      size, so a rem threshold is the only kind that tracks a
                      reader who has asked for larger type. Elsewhere a px
                      threshold gets a row marked PX DEBT and is counted rather
                      than failed — see the scope note below.
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

  The three shipping stylesheets. check-breakpoints.py owns those, keeps both
  copies of their register in step, and is stricter — no px threshold at all.
  This file governs only what that one names as out of scope.

  prototypes/. Declared not-yet-system by the README, with their own
  unreconciled styling, and out of scope by the same boundary every other check
  draws. The register in tokens.css already notes werte-scroll.html's viewport
  820 as a figure that is out of scope and collides with nothing.

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

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# Out of scope, with the reason in the docstring above.
EXCLUDED_DIRS = ("prototypes",)

# patterns/ is held to the rem rule outright. A pattern page stands in for a
# page of the real site, so a reader's font size is a reader's font size there;
# and this lane owns patterns/, so there is nobody to hand a debt row to.
PX_STRICT_DIRS = ("patterns",)

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
    ("patterns/expertise.html", "(max-width: 28rem)"):
        "the trace weight steps 1.17 -> 2, where the two weight bands cross. Not a "
        "layout fold: below it `max-width: 100%` binds instead of the calc, so the "
        "render scale becomes the column's and falls with the viewport.",
    ("patterns/expertise.html", "(max-height: 53.75rem)"):
        "--field-unit steps 6rem -> 4.5rem so the lattice and the drawing standing on "
        "it shrink as a pair and the object stays one cell per lattice step.",
    ("patterns/expertise.html", "layout (min-width: 56rem)"):
        "the step takes its two columns. A CONTAINER query, and the one the pinned "
        "gate below has to clear — the whole argument in the docstring above.",
    ("patterns/expertise.html", "(min-width: 64rem) and (min-height: 45rem)"):
        "the pinned, scroll-scrubbed stage. THE LANDING PAGE'S GATE, adopted rather "
        "than re-derived: one mechanism, one gate. Was `820px`, which is where the "
        "crop band came from.",
    ("patterns/landing-page.html", "(min-width: 64rem) and (min-height: 45rem)"):
        "the pinned, scroll-scrubbed stage for the four process objects. The origin of "
        "the pair above; measured for this page's card, which is width/2 high plus its "
        "copy, and stated in place.",

    # -- foundations/ — documentation chrome ---------------------------------
    # Four of these six are px. They are counted rather than failed because
    # foundations/ is not this lane's, and because a demo page's threshold is
    # about a specimen rather than about a page a reader reads. Each names its
    # owner; the count is printed on every run and cannot grow without an edit
    # here.
    ("foundations/iconography.html", "(max-width: 48rem)"):
        "the icon grid folds. Already named in tokens.css's SCOPE list, as the example "
        "of a page-local VIEWPORT 48rem colliding with a shipping CONTAINER 48rem — "
        "same figure, unrelated queries, do not reconcile them.",
    ("foundations/illustration.html", "(max-width:33rem)"):
        "the single-figure demo drops its caption column.",
    ("foundations/illustration.html", "(max-width:640px)"):
        "PX DEBT — foundations. The illustration plate folds to one column.",
    ("foundations/layout.html", "(max-width:640px)"):
        "PX DEBT — foundations. The space-scale demo folds.",
    ("foundations/materials.html", "(max-width:780px)"):
        "PX DEBT — foundations. The glass demos stack. Renders at the same width as "
        "the shipping 48.75rem nav threshold and is unrelated to it.",
    ("foundations/transitions.html", "(max-width: 900px)"):
        "PX DEBT — foundations. The transition demos stack. Renders at the same width "
        "as the shipping 56.25rem and as docs.css's own sidebar query, and is "
        "unrelated to both.",
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


def px_gloss(value):
    """What a threshold resolves to at a 16 px default, or None if not derivable."""
    m = re.fullmatch(r"([\d.]+)(rem|em|px)", value.strip())
    if not m:
        return None
    n, unit = float(m.group(1)), m.group(2)
    return int(round(n * 16)) if unit in ("rem", "em") else int(round(n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    failures = []
    seen = set()
    found = []

    for path in sorted(DS.rglob("*.html")):
        rel = path.relative_to(DS).as_posix()
        if rel.split("/")[0] in EXCLUDED_DIRS:
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
        "%d in px, none under %s."
        % (len(found), len({r for r, _, _, _ in found}), n_px, "/".join(PX_STRICT_DIRS))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
