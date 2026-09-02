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
answer. Nor does it reach the inventory below, for the same reason: a file with
no row needs a row written, and the row is a sentence about what the file is.

AND THE TABLE UNDER THAT SENTENCE IS A THIRD CLAIM, WHICH NOTHING WAS READING.
scripts/README.md's "What is in here" table gives one row per family of files —
check-*.py, build-*.py, gen-*.py, and five singletons — with a count in front of
each. The rows are an inventory: read together they say what the directory
contains. They did not. Measured on the day this was extended, with both counts
above freshly correct at 175 and 155, the eight rows accounted for 173 files and
README.md itself makes 174 — so one file at that level appeared in no row at
all, and had appeared in none for the twenty-three commits since it landed.

That file is og_meta.py, and it is the worst one in the directory to have left
out: it is the only shared module here, imported by build-news.py,
build-articles.py, build-stellen.py and check-open-graph.py and executed by
none, which made the opening sentence's "no shared library ... every one is run
by its own path" false in two clauses for the whole of that window. Seven of
those twenty-three commits edited that sentence to move the number in front of
the clause they were leaving wrong. A wrong TOTAL is caught above; a file with
no ROW was not, because the two are independent claims and only one was gated.

So the rows are read as globs and matched against the same os.listdir: a row's
number must be the number of files its own pattern matches, no file may be
claimed by two rows, and every file at that level except README.md — which the
sentence excludes by saying "this one included" — must be claimed by one. The
patterns come from the code spans in front of each row's em dash, so the table
stays the source and this stays a reader of it.

Usage:
    check-readme-check-count.py       fail if a stated count and its subject disagree
    check-readme-check-count.py -v    print each number and everything counted
    check-readme-check-count.py --fix rewrite scripts/README.md's two counts (not its
                                      inventory rows: a missing row is prose)
"""

import fnmatch
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

# The inventory table under that sentence. It starts at its own heading and ends
# at the first blank line after the header rule, which is what a markdown table
# is; anything further down the file that happens to open a row with digits is
# therefore out of reach.
TABLE_HEAD = "## What is in here"
TABLE_RULE = "| --- |"
ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|", re.M)
SPAN = re.compile(r"`([^`]+)`")
BRACE = re.compile(r"\{([^{}]*)\}")

# README.md is the one file at this level with no row, and the sentence above the
# table says so in three words — "this one included". Everything else is claimed.
UNROWED = "README.md"

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
    "thirty-three": 33, "thirty-four": 34, "thirty-five": 35,
    "thirty-six": 36, "thirty-seven": 37, "thirty-eight": 38,
    "thirty-nine": 39, "forty": 40,
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


def expand(pattern):
    """`sync-{news,jobs}-notion.py` is two file names. Everything else is one."""
    match = BRACE.search(pattern)
    if not match:
        return [pattern]
    out = []
    for alt in match.group(1).split(","):
        out.extend(expand(pattern[:match.start()] + alt.strip()
                          + pattern[match.end():]))
    return out


def inventory_rows(text):
    """(count, [glob, ...], row text) for each row of the table, in file order."""
    start = text.find(TABLE_HEAD)
    if start < 0:
        return None
    rule = text.find(TABLE_RULE, start)
    if rule < 0:
        return None
    end = text.find("\n\n", rule)
    table = text[rule:end if end > 0 else len(text)]

    rows = []
    for match in ROW.finditer(table):
        what = match.group(2)
        # The What cell is "`glob`[, `glob`] \u2014 prose". Only the code spans in
        # front of the em dash name files; the prose behind it quotes directories
        # and workflow names that are not at this level at all.
        head = what.split("\u2014")[0]
        globs = []
        for span in SPAN.findall(head):
            globs.extend(expand(span))
        rows.append((int(match.group(1)), globs, what.strip()))
    return rows


def inventory(entries, verbose):
    """Hold the table's rows to the directory: every file claimed exactly once."""
    text = open(SCRIPTS_README, encoding="utf-8").read()
    rows = inventory_rows(text)
    failures = []

    if not rows:
        return ['scripts/README.md no longer carries a "%s" table.\n'
                "    That table is this directory's inventory and this rule reads it.\n"
                "    Restore it, or retire the rule with it." % TABLE_HEAD]

    claimed = {}
    for count, globs, what in rows:
        if not globs:
            failures.append(
                'the inventory row "%s" names no file.\n'
                "    A row's file names are the code spans before its em dash; this one\n"
                "    has none, so nothing in the directory can be counted against it."
                % what)
            continue
        matched = sorted({e for g in globs for e in entries
                          if fnmatch.fnmatch(e, g)})
        if verbose:
            print("  row %-28s claims %d, matches %d"
                  % (", ".join(globs), count, len(matched)))
        if count != len(matched):
            failures.append(
                "the inventory row for %s says %d and the directory holds %d:\n%s\n"
                "    Counted by listing scripts/, not by reading the row. --fix does not\n"
                "    reach this half either: a row whose count moved is a row whose prose\n"
                "    may need to move with it."
                % (", ".join("`%s`" % g for g in globs), count, len(matched),
                   "\n".join("      %s" % m for m in matched) or "      (nothing)"))
        for name in matched:
            claimed.setdefault(name, []).append(", ".join(globs))

    twice = sorted(n for n, by in claimed.items() if len(by) > 1)
    if twice:
        failures.append(
            "the inventory claims %d file(s) under two rows:\n%s\n"
            "    Every file at this level belongs to exactly one family, or the rows\n"
            "    stop adding up to the number above them."
            % (len(twice), "\n".join("      %s \u2014 %s" % (n, " and ".join(claimed[n]))
                                     for n in twice)))

    missing = sorted(set(entries) - set(claimed) - {UNROWED})
    if missing:
        failures.append(
            "the inventory has no row for %d file(s) at this level:\n%s\n"
            "    The table is what the directory contains, so a file absent from it is\n"
            "    invisible to every reader of this README. Write it a row saying what it\n"
            "    is and who runs it. This is how og_meta.py \u2014 the one shared module\n"
            '    here \u2014 stayed unlisted while the opening sentence called the\n'
            '    directory "no shared library" for twenty-three commits.'
            % (len(missing), "\n".join("      %s" % m for m in missing)))

    if UNROWED not in entries:
        failures.append(
            "%s is not at this level any more, and it is the one file this rule\n"
            '    exempts from the table on the strength of "this one included".' % UNROWED)

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
    failures.extend(inventory(directory_counts()[0], verbose))

    if failures:
        print("readme check count: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    entries, checks = directory_counts()
    print(
        "README says %s, and lists %d checks; scripts/README.md counts %d files "
        "and %d check-*.py, its inventory rows claim every one of the %d but %s, "
        "and the directory holds all of it."
        % (word, len(listed), len(entries), len(checks), len(entries), UNROWED)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
