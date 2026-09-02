#!/usr/bin/env python3
"""A check that names a gate has to name one that exists.

The ninety-first check, and the only one whose subject is the other ninety.

Every check in this directory opens with a docstring that argues its rule, and
the strongest move in that argument is the hand-off: "this file holds one axis
of the seam, that one holds the other." It is how a reader learns that a thing
they can see is uncovered is in fact covered somewhere else, and it is the only
way they learn it, because nothing in a docstring is executable and a reader is
not going to run `ls scripts/` against every name in a paragraph they have no
reason to doubt.

WHICH IS EXACTLY HOW THE ONE SEAM ON THE LANDING PAGE STAYED OPEN. Measured on
main on 2026-08-03, the drawing's foot and the lectern's rail — the single join
between .lp-flow and .lp-frame, aimed at each other to 0.02 px on the x — stood
218.59 to 514.59 px apart at nine desktop sizes and opened a further 1.00 px
per px of scroll past the pin. check-flow-handover.py, the file whose whole
subject is that seam, said it was closed: a stroke called .lp-flow__stem
crossed it, and two more scripts in this directory — one for the anchor, one
for the travel — held the two axes between them. The stroke had been removed on
2026-07-28 and the two scripts had never been written. `git log -S` finds both
of their names in exactly one commit: the one that added the docstring naming
them.

Three things had to be true at once for that to survive four months of hourly
routines: the seam is invisible in a still (a gap in a wash between two
sections a reader never sees at the same moment), the claim was specific enough
to be convincing, and the two names looked like the two gates. Only the third
is fixable by a script, and it is fixable completely.

THE RULE. Any `scripts/…py` path written anywhere in the design system or in
scripts/ must name a file that is there. That is the whole check. It is
deliberately narrower than "every path mentioned anywhere resolves": the same
paragraphs name CSS classes, custom properties, pull requests and tokens, none
of which this can adjudicate, and a check that is right about one thing beats a
check that is nearly right about five. A script path is unambiguous — it is
either in that directory or it is not.

THE CORPUS WIDENED, AND A CLAIM THIS CHECK COULD NOT SEE IS WHY. It read the
gates' own docstrings and the workflow, and not the chapters — which is the half
a reader actually reads. design-system/foundations/motion.html closed its
argument for the arrival rule by naming check-build-arrival.py as the script
that "counts ink and holds the ceiling, so this rule is enforced rather than
merely written here." That file has never existed in any commit; `git log -S`
finds the name in exactly one, the commit that wrote the sentence, and the claim
then stood through 49 merges to main — under a heading whose whole subject is a
rule this same chapter had already stated backwards once. It is the landing
page's seam again, one corpus over.

So the existence half now reads every .html, .css and .js under design-system/
as well, plus both READMEs. Measured on the tree the day it was widened: 101
authored files carrying 556 mentions of a scripts/ path across 157 distinct
names — the chapters, the four stylesheets and the markup — of which two named
nothing at all.

AND IT READS ANY scripts/ PATH NOW, not only check-*.py, one directory deep. The
second stray was gen-flow-root.py — cited at the top of scripts/ in
foundations/illustration.html and, copied from the same finding, in
check-figure-roster.py's own docstring, where the generator actually stands one
directory down in expertise-objects/. A generator writes markup that ships, so a
reader sent to the wrong path to regenerate a drawing is in the same position as
one sent to a gate that is not there: they conclude the thing is held, and stop
looking.

BOTH NAMES ARE WRITTEN WITHOUT THEIR PREFIX IN THIS PARAGRAPH, deliberately, and
that is not a dodge — it is the rule stated once more. This check is about
paths and not about names, because a name in a sentence is how a reader refers
to a thing and a path is how they go and find it. A record of a bad path that
was itself a bad path would fail its own gate on every run, and the record is
worth more than the symmetry.

AND THE WORKFLOW IS HELD TO THE SAME LINE, for the reason the fold exists: a
check nobody runs is prose with a shebang. Every `scripts/check-*.py` named in
.github/workflows/design-system.yml must exist too, and — the half that bites —
every check in scripts/ must be named in the workflow. A gate written and never
wired is the same failure one step earlier, and this repository has shipped
that too: the four checks added with the acts sheet ran nowhere for a week.
This half stays narrow where the other one widened: design-system.yml is the
run list for check-*.py sitting directly in scripts/, and a builder or a
generator named there is a citation like any other rather than a missing step.

WHAT THIS CANNOT SEE, stated so it is not mistaken for covered. It reads names,
not claims. A check that exists, is wired, and asserts nothing about what its
docstring says it asserts passes here and should — that is the reader's job,
and it is why the docstrings are long. This holds the one part of the argument
that is a fact about the filesystem.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-cited-gates.py
    python3 scripts/check-cited-gates.py -v     # every citation, not only strays
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
TREE = ROOT / "design-system"
WORKFLOW = ROOT / ".github" / "workflows" / "design-system.yml"

# A `scripts/` path, wherever it is written — in a docstring, in a chapter's
# prose, in a stylesheet's comment, in a `print()` that tells a reader what to
# run next, or in the workflow's own run lines. The prefix is required: a bare
# "check-links.py" inside a sentence is a name, and this check is about paths.
# One optional directory segment, because scripts/expertise-objects/ is the one
# place a generator lives below the top of that directory.
CITE = re.compile(r"scripts/((?:[a-z0-9_-]+/)?[a-z0-9_-]+\.py)")

# THE SPECIMENS, AND NOT WHAT IS SPLICED INTO THEM. patterns/en/ is the English
# edition build-i18n.py writes, and beitrag-/stelle-/news-thema- prefixed pages
# are one post, one opening or one topic spliced into a specimen. Their prose is
# a copy of a specimen's, so a stray in one of them is the same stray reported
# twice and fixed in a file the next build overwrites.
GENERATED = ("beitrag-", "stelle-", "news-thema-")


def authored():
    """Every authored file in the design system, in path order."""
    out = []
    for path in sorted(TREE.rglob("*")):
        if path.suffix not in (".html", ".css", ".js", ".md"):
            continue
        if path.relative_to(TREE).parts[:2] == ("patterns", "en"):
            continue
        if path.name.startswith(GENERATED):
            continue
        out.append(path)
    out.append(ROOT / "README.md")
    return out


def cited(text):
    """Every scripts/…py path named in one file, in order of first mention."""
    out, seen = [], set()
    for line_no, line in enumerate(text.splitlines(), 1):
        for name in CITE.findall(line):
            if name in seen:
                continue
            seen.add(name)
            out.append((name, line_no))
    return out


def audit():
    present = {str(p.relative_to(SCRIPTS)) for p in SCRIPTS.rglob("*.py")}
    checks = {p.name for p in SCRIPTS.glob("check-*.py")}
    findings, seen = [], []

    for path in sorted(SCRIPTS.rglob("*.py")) + authored():
        if not path.exists():
            continue
        where = str(path.relative_to(ROOT))
        # A file naming its own usage line, compared as the path this check
        # reads — not as a bare filename, which would let a generator one
        # directory down excuse itself by citing the wrong path to itself.
        own = str(path.relative_to(SCRIPTS)) if SCRIPTS in path.parents else None
        text = path.read_text(encoding="utf-8")
        for name, line_no in cited(text):
            if name == own:
                continue
            if name in present:
                seen.append((where, line_no, name, "exists"))
            else:
                findings.append(
                    (where, line_no,
                     f"names scripts/{name}, which is not in scripts/",
                     "A reader takes that name for the gate — or the generator "
                     "— on whatever this paragraph hands off. Write it, correct "
                     "the path, or drop the claim."))

    if not WORKFLOW.exists():
        findings.append((str(WORKFLOW.relative_to(ROOT)), 0,
                         "the workflow is missing", "nothing runs any of these"))
        return findings, seen

    wf_text = WORKFLOW.read_text(encoding="utf-8")
    # The run list is check-*.py sitting directly in scripts/. A builder or a
    # generator named in the workflow is a citation, held by the loop above.
    wired = {name for name, _ in cited(wf_text) if name in checks}
    for name, line_no in cited(wf_text):
        if name in present:
            seen.append(("design-system.yml", line_no, name,
                         "wired" if name in checks else "exists"))
        else:
            findings.append(
                (".github/workflows/design-system.yml", line_no,
                 f"runs scripts/{name}, which is not in scripts/",
                 "The job fails on the missing file, or worse, silently does "
                 "not run the gate it is named for."))
    for name in sorted(checks - wired):
        findings.append(
            (f"scripts/{name}", 0,
             "is not run by .github/workflows/design-system.yml",
             "A check nobody runs is prose with a shebang. Add it to the "
             "workflow or delete it."))

    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every citation, not only the strays")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for where, line_no, name, how in seen:
            print("  %-34s %5d  %-34s %s" % (where[:34], line_no, name, how))
        print()

    if findings:
        for where, line_no, what, why in findings:
            head = "%s:%d" % (where, line_no) if line_no else where
            print("%s\n    %s\n    %s" % (head, what, why), file=sys.stderr)
        print("\n%d citation%s naming a gate that is not there. A name is not a "
              "check — see the seam this cost in scripts/check-flow-handover.py."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    cites = sum(1 for _, _, _, how in seen if how == "exists")
    runs = sum(1 for _, _, _, how in seen if how == "wired")
    print("cited gates: %d citation%s across scripts/ and the design system, and "
          "%d check%s wired into design-system.yml, every name a file that is "
          "there."
          % (cites, "" if cites == 1 else "s", runs, "" if runs == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
