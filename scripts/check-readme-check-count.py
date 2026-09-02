#!/usr/bin/env python3
"""The README's count of its own checks is the count of what it lists.

design-system/README.md introduces its register of enforced rules with a number
spelled as a word — "The nineteen checks the system enforces rather than
documents" — standing over a block that names them one per line. The number is
hand-kept and the block is appended to by whichever lane adds a check, so the
two drift apart the moment two lanes land in the same day. That has now happened
three times:

  fifteen   the count before either of two additions
  sixteen   one lane added check-faq-count.py and moved the count with it; the
            lane that added check-stack-layers.py left the sentence alone, and
            both landed, so the block said seventeen and the sentence sixteen
  eighteen  reconciled by hand, and broken again in the same hour by a third
            lane adding check-illustration-source.py on a branch cut before the
            reconciliation landed

Every one of those was a correct change by a lane that could not see the other,
which is precisely the shape of defect a number in prose cannot survive and a
script settles for good. There is nothing to decide here — the block is the
list, so the block is the count — which is why this is the narrowest check in
the directory and why it carries no register of its own.

WHAT IS COUNTED. Distinct `scripts/check-*.py` named in the fenced block
immediately above the sentence. Distinct, because several are listed twice, once
plain and once with `-v`; and by the path rather than by a bare name, so a
mention in prose elsewhere cannot be swept in. check-a11y.py is counted like any
other — an earlier hand count came back one short by matching a name pattern
that its digit-free neighbours all satisfied and it did not, which is the other
reason to stop counting these by eye.

This script does not assert that the block is complete, or that everything in it
is registered in CI. Those are different claims about different files, and
.github/workflows/design-system.yml is where the second one is settled.

THE SAME NUMBER IS CLAIMED ONE DIRECTORY OVER, AND NOTHING WAS COUNTING THAT
ONE EITHER. scripts/README.md opens "N files at this level, this one included"
and carries a table row reading "| N | `check-*.py` — one design-system
invariant each". Both are counts of the directory the file sits in, both are
hand-kept, and both have exactly the failure mode above with none of the gate:
the sentence next door was caught and fixed three times because something reads
it, while its neighbour went stale silently. Measured on the day this was
extended, main said 156 files and 138 checks against a tree holding 158 and 140
— two lanes' additions, neither of which touched the paragraph.

These two are not counts of a list, so they are not read off a block. They are
counts of the directory, and the directory is right there, so they are derived
from `os.listdir` — the same move every other register in here makes, and the
reason this cannot itself go stale.

WHY THIS ONE GREW A --fix WHEN THE FINDING IS TWO DIGITS. Because two digits
is exactly the size of finding a lane refuses to stop for. Every other derived
register in here that goes stale on somebody else's push has one —
check-spacing-scale.py, check-motion-census.py, check-glass-budget.py — and
this pair, which the docstring above says went stale "an hour before it was
corrected" and then again in the same hour, did not. So the lane that trips it
is a lane that has just been told its own green branch is red for a reason that
is not its own and has no one-command way out, and the cheapest thing it can do
is nothing. --fix makes the cheapest thing the correct thing.

It rewrites ONLY the two counts in scripts/README.md, and only to the number
the directory holds. It does not touch design-system/README.md's spelled-out
sentence: that number counts a LIST, and a list that has gained an entry needs
the entry written into the block as well as the digit moved — a --fix there
would paper over a missing row rather than repair a count. The two halves of
this script fail for different reasons and only one of them has a mechanical
answer.

Usage:
    check-readme-check-count.py       fail if a stated count and its subject disagree
    check-readme-check-count.py -v    print each number and everything counted
    check-readme-check-count.py --fix rewrite scripts/README.md's two counts
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(ROOT, "design-system", "README.md")
SCRIPTS_README = os.path.join(SCRIPTS, "README.md")

# scripts/README.md's two claims about the directory it introduces. Each is
# (regex with one capturing group for the digits, what it counts, its label).
FILE_COUNT = re.compile(r"\b(\d+) files at this level, this one included\b")
CHECK_COUNT = re.compile(r"^\|\s*(\d+)\s*\|\s*`check-\*\.py`", re.M)

SENTENCE = re.compile(
    r"^The ([a-z-]+) checks the system enforces rather than documents\b", re.M
)
FENCED = re.compile(r"```[a-z]*\n(.*?)\n```", re.S)
NAMED = re.compile(r"scripts/(check-[a-z0-9-]+\.py)")

# Spelled out, because that is how the sentence reads and a digit there would be
# the wrong register for this document. Extended when the register outgrows it.
WORDS = {
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "twenty-one": 21, "twenty-two": 22,
    "twenty-three": 23, "twenty-four": 24, "twenty-five": 25,
    "twenty-six": 26, "twenty-seven": 27, "twenty-eight": 28,
    "twenty-nine": 29, "thirty": 30, "thirty-one": 31, "thirty-two": 32,
}


def directory_counts():
    """(files at this level, check-*.py) — counted, not remembered."""
    entries = [e for e in os.listdir(SCRIPTS)
               if os.path.isfile(os.path.join(SCRIPTS, e))]
    checks = [e for e in entries
              if e.startswith("check-") and e.endswith(".py")]
    return sorted(entries), sorted(checks)


def scripts_readme(verbose, fix=False):
    """Hold scripts/README.md's two counts to the directory they describe."""
    text = open(SCRIPTS_README, encoding="utf-8").read()
    entries, checks = directory_counts()
    failures, rewritten = [], []

    for pattern, actual, what, where in (
        (FILE_COUNT, len(entries), "files at this level",
         '"N files at this level, this one included"'),
        (CHECK_COUNT, len(checks), "check-*.py scripts",
         "the `check-*.py` row of the table under it"),
    ):
        match = pattern.search(text)
        if not match:
            failures.append(
                "scripts/README.md no longer carries %s.\n"
                "    That sentence is what this rule counts. Restore it, or retire the\n"
                "    rule with it — an uncounted count is how this file got here." % where
            )
            continue
        claimed = int(match.group(1))
        if verbose:
            print("  scripts/README.md says %d %s; the directory holds %d"
                  % (claimed, what, actual))
        if claimed != actual:
            if fix:
                # Substitute inside the matched span only. The digits are not
                # unique in this file -- "150" is a plausible substring of a
                # dozen other sentences -- so the replacement is anchored on
                # the match the pattern already found rather than on the number.
                start, end = match.span()
                span = text[start:end].replace(str(claimed), str(actual), 1)
                text = text[:start] + span + text[end:]
                rewritten.append("%s: %d -> %d" % (what, claimed, actual))
                continue
            failures.append(
                "scripts/README.md says %d %s and the directory holds %d.\n"
                "    Derived by listing scripts/, not by remembering. This pair is\n"
                "    ungated history: it was corrected an hour before it went stale\n"
                "    again, by a lane that had no reason to look at it.\n"
                "    Run: python3 scripts/check-readme-check-count.py --fix"
                % (claimed, what, actual)
            )

    if fix and rewritten:
        open(SCRIPTS_README, "w", encoding="utf-8").write(text)
        for line in rewritten:
            print("fixed   scripts/README.md %s" % line)

    return failures


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    fix = "--fix" in sys.argv
    text = open(README, encoding="utf-8").read()

    match = SENTENCE.search(text)
    if not match:
        print(
            "check-readme-check-count.py: the sentence this script counts is gone from\n"
            "design-system/README.md. It read \"The <number> checks the system enforces\n"
            "rather than documents\". Restore it, or retire this script with it."
        )
        return 1

    word = match.group(1)
    if word not in WORDS:
        print(
            'check-readme-check-count.py: "%s" is not a number this script knows.\n'
            "Add it to WORDS — the register is spelled out on purpose." % word
        )
        return 1
    claimed = WORDS[word]

    blocks = FENCED.findall(text[: match.start()])
    listed = sorted(set(NAMED.findall(blocks[-1]))) if blocks else []
    if not listed:
        print(
            "check-readme-check-count.py: found no check scripts in the block above the\n"
            "sentence. The block is the list; if it moved, this script has to move with it."
        )
        return 1

    if verbose:
        print("  sentence says %s (%d)" % (word, claimed))
        for name in listed:
            print("    %s" % name)

    failures = []
    if claimed != len(listed):
        failures.append(
            'design-system/README.md says "%s" and lists %d:\n\n%s\n\n'
            "    The block is the list, so the block is the count. Set the word to match\n"
            "    it — this is the drift that follows two lanes adding a check on the same day.\n"
            "    --fix does not reach this half: a count of a LIST that has gained an entry\n"
            "    needs the entry written into the block, and moving the digit alone would\n"
            "    hide the missing row rather than repair the count."
            % (word, len(listed), "\n".join("      %s" % n for n in listed))
        )

    failures.extend(scripts_readme(verbose, fix))

    if failures:
        print("readme check count: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    entries, checks = directory_counts()
    print(
        "README says %s, and lists %d checks; scripts/README.md counts %d files "
        "and %d check-*.py, and the directory holds both."
        % (word, len(listed), len(entries), len(checks))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
