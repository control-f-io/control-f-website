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

THE RULE. Any `scripts/check-<name>.py` written inside any file in scripts/ must
name a file that is there. That is the whole check. It is deliberately narrower
than "every path mentioned anywhere resolves": docstrings name CSS classes,
custom properties, pull requests and tokens, none of which this can adjudicate,
and a check that is right about one thing beats a check that is nearly right
about five. A script path is unambiguous — it is either in this directory or it
is not.

AND THE WORKFLOW IS HELD TO THE SAME LINE, for the reason the fold exists: a
check nobody runs is prose with a shebang. Every `scripts/check-*.py` named in
.github/workflows/design-system.yml must exist too, and — the half that bites —
every check in scripts/ must be named in the workflow. A gate written and never
wired is the same failure one step earlier, and this repository has shipped
that too: the four checks added with the acts sheet ran nowhere for a week.

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
WORKFLOW = ROOT / ".github" / "workflows" / "design-system.yml"

# A `scripts/` path to a check, wherever it is written — in a docstring, in a
# comment, in a `print()` that tells a reader what to run next, or in the
# workflow's own run lines. The prefix is required: a bare "check-links.py"
# inside a sentence is a name, and this check is about paths.
CITE = re.compile(r"scripts/(check-[a-z0-9-]+\.py)")


def cited(text):
    """Every scripts/check-*.py named in one file, in order of first mention."""
    out, seen = [], set()
    for line_no, line in enumerate(text.splitlines(), 1):
        for name in CITE.findall(line):
            if name in seen:
                continue
            seen.add(name)
            out.append((name, line_no))
    return out


def audit():
    present = {p.name for p in SCRIPTS.glob("check-*.py")}
    findings, seen = [], []

    for path in sorted(SCRIPTS.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for name, line_no in cited(text):
            if name == path.name:
                continue                       # a file naming its own usage line
            if name in present:
                seen.append((path.name, line_no, name, "exists"))
            else:
                findings.append(
                    (f"scripts/{path.name}", line_no,
                     f"names scripts/{name}, which is not in scripts/",
                     "A reader takes that name for the gate on whatever this "
                     "paragraph hands off. Write the check or drop the claim."))

    if not WORKFLOW.exists():
        findings.append((str(WORKFLOW.relative_to(ROOT)), 0,
                         "the workflow is missing", "nothing runs any of these"))
        return findings, seen

    wf_text = WORKFLOW.read_text(encoding="utf-8")
    wired = {name for name, _ in cited(wf_text)}
    for name, line_no in cited(wf_text):
        if name in present:
            seen.append(("design-system.yml", line_no, name, "wired"))
        else:
            findings.append(
                (".github/workflows/design-system.yml", line_no,
                 f"runs scripts/{name}, which is not in scripts/",
                 "The job fails on the missing file, or worse, silently does "
                 "not run the gate it is named for."))
    for name in sorted(present - wired):
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
    print("cited gates: %d citation%s across scripts/ and %d check%s wired into "
          "design-system.yml, every name a file that is there."
          % (cites, "" if cites == 1 else "s", runs, "" if runs == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
