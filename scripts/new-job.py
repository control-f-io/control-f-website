#!/usr/bin/env python3
"""One opening, scaffolded into content/jobs/ with every field the build needs.

WHY THIS EXISTS, AND IT IS new-post.py's ARGUMENT ONE REGISTER OVER. A news post
has had a scaffolding tool since the archive was generated; an opening has not.
So writing a vacancy meant hand-typing a header of sixteen required fields whose
only statements are build-jobs.py's REQUIRED tuple and a code block in
design-system/README.md — and getting one of them wrong is not caught by anything
until the build refuses the file, by which time the person who typed it has moved
on. Nine of those fields are German/English PAIRS, and the pairing is the half
people miss: `standort` without `location` is a register row that renders in
German on the English page, which is the exact failure the catalogue exists to
prevent everywhere else.

WHAT IT WRITES. content/jobs/<slug>.md, with the fields in the order build-jobs.py
reads them, the German/English pairs adjacent so a missing half is visible, and
every optional field present but commented in the header's own prose rather than
guessed at. The advertisement itself — the two-language body — is scaffolded with
--text, the same flag and the same `--- en ---` divider new-post.py uses.

THE SLUG IS NOT INVENTED HERE. sync-jobs-notion.py owns it, because the file
name, the register's anchor and the page's address are one string and Notion is
what wins once it is connected: a slug that disagreed with the sync's would make
the next hourly import delete this file and write its own. It is imported from
there rather than reimplemented.

AN OPENING WITHOUT AN ADVERTISEMENT IS LEGITIMATE and gets no page of its own —
its register entry links to its own row, which is what karriere.html shipped for
three of its four entries. --text is how you say you are writing the ad now.

    python3 scripts/new-job.py "{Data Engineer} (m/w/d)" \\
            --title "Data Engineer (m/f/d)" --kennung CF-2026-DE-02 \\
            --bereich Plattform --area Platform --text

Then `sh scripts/build-all.sh`, which is the only complete statement of the
order — the register, the catalogue, the Stelle page and the pages that ship.
"""

import argparse
import datetime
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
JOBS = ROOT / "content" / "jobs"


def slug(titel):
    """sync-jobs-notion.py's slug(), imported rather than repeated.

    The file name is also the URL and the register's anchor, and the Notion sync
    derives it from the German headline with its own function. Two
    implementations of one string is how a hand-written opening and an imported
    one end up as two files for one job.
    """
    spec = importlib.util.spec_from_file_location(
        "cf_sync_jobs", ROOT / "scripts" / "sync-jobs-notion.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.slug(titel)


# The header build-jobs.py reads, in its order, with each pair adjacent. The
# second element is the flag's default when there is a sensible one and None
# when leaving it blank is the instruction.
FIELDS = (
    ("kennung",    None, "required. The one identifier that does not move when the title does."),
    ("bereich",    None, "required, German. The section of the company."),
    ("area",       None, "required, English."),
    ("titel",      None, "required, German. Braces mark an English run: {Data Engineer} (m/w/d)."),
    ("title",      None, "required, English."),
    ("anriss",     None, "required, German. One or two sentences; the register shows it."),
    ("excerpt",    None, "required, English."),
    ("standort",   "Konstanz, hybrid",   "required, German. Fact 1 of the register's four."),
    ("location",   "Konstanz, hybrid",   "required, English."),
    ("anstellung", "Festanstellung",     "required, German. Fact 2."),
    ("employment", "Permanent employment", "required, English."),
    ("umfang",     "Voll- oder Teilzeit", "required, German. Fact 3."),
    ("hours",      "Full or part time",  "required, English."),
    ("start",      "ab sofort",          "required, German. Fact 4."),
    ("starts",     "immediately",        "required, English."),
    ("adresse",    "Am Seerhein 6, 78467 Konstanz.", "optional, German. The Stelle page has room for it."),
    ("address",    "Am Seerhein 6, 78467 Konstanz.", "optional, English."),
    ("verguetung", None, "optional, German. The page states a range; the register does not."),
    ("salary",     None, "optional, English."),
    ("gehalt_von", None, "optional. A number, for the JobPosting block."),
    ("gehalt_bis", None, "optional. A number."),
    ("art",        None, "optional. FULL_TIME, PART_TIME — the JobPosting employmentType."),
    ("seit",       None, "required, YYYY-MM-DD. Sorts the register, newest first."),
    ("frist",      None, "with-an-ad. The closing date the Stelle page states."),
)

WIDTH = max(len(name) for name, _, _ in FIELDS) + 2

BODY = [
    "Der erste Absatz ist der Einstieg — er sagt, worum die Stelle geht, und "
    "steht über den Abschnitten.",
    "",
    "## Ihre Aufgaben",
    "",
    "Text.",
    "",
    "## Was Sie mitbringen",
    "",
    "Text.",
    "",
    "--- en ---",
    "",
    "The first paragraph is the opening — it says what the role is about, and it "
    "stands above the sections.",
    "",
    "## What you will do",
    "",
    "Text.",
    "",
    "## What you bring",
    "",
    "Text.",
    "",
]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("titel", help="the German headline, in quotes; braces mark "
                                  "an English run")
    ap.add_argument("--title", default="", help="the English headline")
    ap.add_argument("--kennung", default="", help="e.g. CF-2026-DE-02")
    ap.add_argument("--bereich", default="", help="the section, German")
    ap.add_argument("--area", default="", help="the section, English")
    ap.add_argument("--seit", default=datetime.date.today().isoformat(),
                    help="YYYY-MM-DD, default today")
    ap.add_argument("--text", action="store_true",
                    help="scaffold the two-language advertisement, so the "
                         "opening gets a page")
    args = ap.parse_args()

    given = {"titel": args.titel, "title": args.title, "kennung": args.kennung,
             "bereich": args.bereich, "area": args.area, "seit": args.seit}

    JOBS.mkdir(parents=True, exist_ok=True)
    name = slug(args.titel)
    if not name:
        sys.exit("new-job: %r leaves no slug once the braces and the (m/w/d) "
                 "are dropped." % args.titel)
    path = JOBS / ("%s.md" % name)
    if path.exists():
        sys.exit("new-job: %s already exists. Edit it, or give a different "
                 "title." % path.relative_to(ROOT))

    lines = []
    for field, default, _ in FIELDS:
        value = given.get(field) or (default or "")
        lines.append((field + ":").ljust(WIDTH) + value)
    lines.append("")
    if args.text:
        lines += BODY

    path.write_text("\n".join(lines), encoding="utf-8")
    print("wrote %s" % path.relative_to(ROOT))

    # "with-an-ad" fields are required only when there is one, which is why the
    # note carries the condition rather than this filter guessing at it.
    def needed(note):
        return note.startswith("required") or (args.text and
                                              note.startswith("with-an-ad"))

    blank = [f for f, default, note in FIELDS
             if needed(note) and not (given.get(f) or default)]
    if blank:
        print("\n  Fill these in — the build refuses the file without them:")
        for field in blank:
            note = next(n for f, _, n in FIELDS if f == field)
            print("      %-12s %s" % (field, note))
        print("\n  Every German field has an English one beside it. A pair with "
              "one half\n  filled is a register row that renders in German on "
              "the English page.")

    if args.text:
        print("\n  It has an advertisement, so it gets a Stelle page in both "
              "editions.\n  `frist:` is required once it does — the page states "
              "a closing date.")
    else:
        print("\n  It has no advertisement, so its register entry links to its "
              "own row\n  rather than to a page. Write the two-language body "
              "into the file — or\n  start from a scaffold with --text.")

    print("\n  Then: sh scripts/build-all.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
