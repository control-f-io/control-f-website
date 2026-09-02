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

AND THE FIRST --fix WRITTEN FOR IT WROTE TWO OF THE THREE, ON AN ARGUMENT THAT
DOES NOT HOLD. It excluded design-system/README.md's spelled-out sentence,
reasoning that the number counts a LIST rather than a directory, and that a list
which has gained an entry needs the entry written into the block as well as the
digit moved — so writing the word would paper over a missing row.

It rewrites all three counts, each to the number its own subject holds. It does
NOT reach the inventory below, and that one exclusion is sound where the other
was not: a file with no row needs a ROW written, and a row is a sentence about
what the file is rather than a number about how many there are.

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

AND THE REMEDY FOR A NUMBER NOBODY CAN BE EXPECTED TO REMEMBER IS NOT A BETTER
REMINDER. Four registers in this directory are generated rather than kept —
check-spacing-scale.py, check-motion-census.py, check-glass-budget.py and
check-lime-flat.py each carry --fix, and design-system/README.md says of the
first, in as many words, "run --fix rather than editing a count by hand". This
trio had no --fix and is the one that goes stale most often, because it moves
whenever ANY lane adds a check and two of its three numbers live in a file that
lane has no reason to open. Nothing in the trio is a judgement — the block is
the list and the directory is the directory — which is the whole test for what
may be written rather than merely reported, and it is the test the inventory
rows fail.

Usage:
    check-readme-check-count.py        fail if a stated count and its subject disagree
    check-readme-check-count.py -v     print each number and everything counted
    check-readme-check-count.py --fix  write all three counts from what is on disk,
                                       then re-assert what it wrote. The inventory
                                       rows are prose and are left alone.
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
    "thirty-nine": 39, "forty": 40, "forty-one": 41, "forty-two": 42,
    "forty-three": 43, "forty-four": 44, "forty-five": 45, "forty-six": 46,
    "forty-seven": 47, "forty-eight": 48, "forty-nine": 49, "fifty": 50,
}


NUMBERS = {value: word for word, value in WORDS.items()}


def rewrite(path, pattern, value, group=1):
    """Set the digits (or the word) `pattern` captures to `value`. Returns the
    old text if it changed, else None."""
    text = open(path, encoding="utf-8").read()
    match = pattern.search(text)
    if not match or match.group(group) == str(value):
        return None
    start, end = match.span(group)
    open(path, "w", encoding="utf-8").write(text[:start] + str(value) + text[end:])
    return match.group(group)


def repair(listed):
    """--fix: write all three numbers from what is actually on disk.

    The same standing check-spacing-scale.py, check-motion-census.py,
    check-glass-budget.py and check-lime-flat.py already take for the tables
    they own — the README says of those, in as many words, "run --fix rather
    than editing a count by hand". This trio is the one that had no --fix, and
    it is the one that goes stale most often: it moves whenever ANY lane adds a
    check, and two of its three numbers live in a file that lane has no reason
    to open. The script's own finding text has said so since it was written —
    "it was corrected an hour before it went stale again, by a lane that had no
    reason to look at it" — and the remedy for a number nobody can be expected
    to remember is not a better reminder.
    """
    entries, checks = directory_counts()
    done = []

    was = rewrite(SCRIPTS_README, FILE_COUNT, len(entries))
    if was is not None:
        done.append("scripts/README.md  files at this level  %s -> %d"
                    % (was, len(entries)))
    was = rewrite(SCRIPTS_README, CHECK_COUNT, len(checks))
    if was is not None:
        done.append("scripts/README.md  check-*.py           %s -> %d"
                    % (was, len(checks)))

    if len(listed) not in NUMBERS:
        done.append(
            "design-system/README.md  NOT written: the block lists %d and the "
            "sentence is spelled out.\n    Add %d to WORDS — the register is a "
            "word on purpose, and a digit there\n    would be the wrong register "
            "for that document." % (len(listed), len(listed)))
    else:
        was = rewrite(README, SENTENCE, NUMBERS[len(listed)])
        if was is not None:
            done.append("design-system/README.md  the sentence         %s -> %s"
                        % (was, NUMBERS[len(listed)]))

    return done


def directory_counts():
    """(files at this level, check-*.py) — counted, not remembered."""
    entries = [e for e in os.listdir(SCRIPTS)
               if os.path.isfile(os.path.join(SCRIPTS, e))]
    checks = [e for e in entries
              if e.startswith("check-") and e.endswith(".py")]
    return sorted(entries), sorted(checks)


def scripts_readme(verbose):
    """Hold scripts/README.md's two counts to the directory they describe.

    REPORTING ONLY. repair() owns every write in this file, including these
    two, and the reason is the re-assert: --fix writes and then re-runs the
    checking path over what it wrote, so a second writer inside the checking
    path would be repairing the file it was supposed to be judging.
    """
    text = open(SCRIPTS_README, encoding="utf-8").read()
    entries, checks = directory_counts()
    failures = []

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
            failures.append(
                "scripts/README.md says %d %s and the directory holds %d.\n"
                "    Derived by listing scripts/, not by remembering. This pair is\n"
                "    ungated history: it was corrected an hour before it went stale\n"
                "    again, by a lane that had no reason to look at it.\n"
                "    Run: python3 scripts/check-readme-check-count.py --fix"
                % (claimed, what, actual)
            )

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


def main_verify():
    """The checking path alone — what --fix re-runs on what it just wrote."""
    return main(fixing=False)


def main(fixing=None):
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    if fixing is None:
        fixing = "--fix" in sys.argv
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

    if fixing:
        # The block is the list, so the block is the count — and the same is
        # true of the directory for the other two. Nothing here is a judgement,
        # which is the whole test for what may be written rather than reported.
        done = repair(listed)
        for line in done:
            print("  %s" % line)
        if not done:
            print("readme check count: nothing to write; all three already match.")
            return 0
        print()
        # Re-read and re-assert, so --fix can never report a repair it did not
        # actually make.
        return main_verify()

    failures = []
    if claimed != len(listed):
        failures.append(
            'design-system/README.md says "%s" and lists %d:\n\n%s\n\n'
            "    The block is the list, so the block is the count. Set the word to match\n"
            "    it — this is the drift that follows two lanes adding a check on the same day.\n"
            "    Run: python3 scripts/check-readme-check-count.py --fix"
            % (word, len(listed), "\n".join("      %s" % n for n in listed))
        )

    failures.extend(scripts_readme(verbose))
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
