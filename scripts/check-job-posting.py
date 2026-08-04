#!/usr/bin/env python3
"""A JobPosting must say what the page says, and only one page may say it.

Structured data is the one thing on a page that no screenshot can check. It is
not rendered, it is not read aloud, it does not reflow, and it is consumed
entirely by machines that never file a bug — they just publish whatever it
claims. A JSON-LD block that has drifted away from the page under it looks
exactly like one that has not, from every angle a human uses to look at a page.

components/vacancy.html already states the whole rule, in prose, under
"Before launch":

    Google's job posting documentation is explicit that `JobPosting` markup
    goes on a page describing exactly one opening, one URL per opening, and
    that a careers landing page listing several must not carry it. So the
    register links out and stays plain HTML; the JSON-LD — title, description,
    datePosted, validThrough, jobLocation, hiringOrganization — goes on
    /karriere/<rolle>, and EVERY FIELD IN IT HAS TO MATCH WHAT THE READER SEES
    ON THAT PAGE.

    An opening with no `validThrough` stays live in search results after it is
    filled.

Three sentences, three things nothing enforced. And the drift they describe is
not hypothetical maintenance work — it is the ordinary life of a job page. A
posting gets extended and someone edits the date the reader sees; the salary
band moves and someone edits the row in the table; the role gets renamed in the
headline. Each of those is a one-line edit to the visible page, and each of them
leaves a second copy of the same fact, in a block the editor never scrolled to,
saying the old thing to every search engine that asks. Google's own policy for
that state is not a warning: it is a manual action against the site.

THE RULE, in five parts. Every .html under design-system/ is read.

  ONE BLOCK      A page carries at most one JobPosting block, and it must
                 parse as JSON. Two blocks on one page is two answers to
                 "which opening is this page about".

  ONE OPENING    A page that carries one has exactly one <h1>, and the block's
                 `title` is that <h1>, character for character. This is what
                 keeps the block off the careers overview without the checker
                 having to guess what a careers overview is: /karriere's <h1>
                 is "Karriere", which is not a job title, so the moment anybody
                 pastes a JobPosting onto it, that page fails. And the page's
                 own opening may not also appear in a register on it — a job
                 page that lists itself among the others is a listing page.

  SIX FIELDS     title, description, datePosted, validThrough, jobLocation and
                 hiringOrganization are all present. The list is the component
                 page's, not this script's; `validThrough` is in it for the
                 reason quoted above, and `datePosted` must not be later than
                 it.

  THE MATCH      Every field a reader could check appears in the rendered text
                 of the same page, with the same value:

                   title              as written, in the visible text
                   datePosted         as a German date — 2026-07-06 → 06.07.2026
                   validThrough       likewise
                   hiringOrganization the organisation's name
                   jobLocation        street, postal code and locality
                   baseSalary         both bounds, German thousands separator
                   employmentType     the German word for it (table below)

                 `description` is exempt: it is a summary of the page rather
                 than a fact on it, and requiring it verbatim would only teach
                 people to paste a paragraph twice.

  ONE URL        No two pages in the tree carry a JobPosting with the same
                 title or the same identifier. One URL per opening is the other
                 half of the sentence, and duplicate postings are the single
                 most common reason a job feed gets dropped.

WHY THE GERMAN DATE. The site is German, so the rendered date is 30.09.2026 and
the block's is 2026-09-30, and those are the same fact written twice in two
notations — which is exactly the shape of drift this check exists for. The
script converts rather than compares text, so a page that writes the date in
ISO for the reader also passes: what is checked is the value, not the spelling.

EMPLOYMENT TYPES. schema.org's vocabulary is English and the page is not, so
the check knows the four this system uses and accepts any one of the German
words that carry the same meaning. A type the table does not know is reported
rather than silently accepted, because an unknown type is either a typo or a
new case for the table — and both want a human.
"""

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TREE = os.path.join(ROOT, "design-system")

# The six the component page names. Order is the order it names them in.
REQUIRED = ["title", "description", "datePosted", "validThrough",
            "jobLocation", "hiringOrganization"]

# schema.org's employmentType values, and the German a reader would see for
# each. Any one of the alternatives satisfies the match — "Voll- oder Teilzeit"
# contains "Voll-" and "Teilzeit" and is one line covering two types.
EMPLOYMENT_WORDS = {
    "FULL_TIME": ("Vollzeit", "Voll-"),
    "PART_TIME": ("Teilzeit",),
    "INTERN": ("Praktikum", "Werkstudium"),
    "TEMPORARY": ("befristet", "Befristet"),
    "CONTRACTOR": ("freiberuflich", "Freiberuflich"),
    "PER_DIEM": ("Aushilfe",),
    "VOLUNTEER": ("ehrenamtlich",),
    "OTHER": (),
}


class Rendered(HTMLParser):
    """The page as a reader meets it: text, the <h1>s, and the register links.

    <script> and <style> contents are not text — including them would let a
    block match itself, which is the one thing this check must never do.
    """

    SKIP = {"script", "style", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks = []
        self.h1s = []
        self.vacancy_links = []
        self._skip = 0
        self._h1 = None
        self._link = None

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
            return
        classes = dict(attrs).get("class", "").split()
        if tag == "h1":
            self._h1 = []
        if tag == "a" and "cf-vacancy__link" in classes:
            self._link = []

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self._skip = max(0, self._skip - 1)
            return
        if tag == "h1" and self._h1 is not None:
            self.h1s.append(norm("".join(self._h1)))
            self._h1 = None
        if tag == "a" and self._link is not None:
            self.vacancy_links.append(norm("".join(self._link)))
            self._link = None

    def handle_data(self, data):
        if self._skip:
            return
        self.chunks.append(data)
        if self._h1 is not None:
            self._h1.append(data)
        if self._link is not None:
            self._link.append(data)

    @property
    def text(self):
        return norm("".join(self.chunks))


def norm(s):
    """Collapse whitespace and the soft hyphen, which is invisible to a reader.

    A word broken with &shy; is one word on screen and two in the source, and a
    check that cannot see that would fail on correct pages.
    """
    return re.sub(r"\s+", " ", s.replace("­", "")).strip()


def ld_blocks(source):
    """Every application/ld+json block in a file, with its line number."""
    out = []
    pattern = re.compile(
        r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.S | re.I)
    for m in pattern.finditer(source):
        out.append((source.count("\n", 0, m.start()) + 1, m.group(1)))
    return out


def job_postings(payload):
    """The JobPosting objects inside one parsed block, @graph included."""
    found = []

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            if node.get("@type") == "JobPosting":
                found.append(node)
            for value in node.values():
                if isinstance(value, (list, dict)):
                    walk(value)

    walk(payload)
    return found


def german_date(iso):
    """2026-09-30 → 30.09.2026. None if the value is not a plain ISO date."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(iso))
    if not m:
        return None
    y, mo, d = m.groups()
    return "%s.%s.%s" % (d, mo, y)


def thousands(n):
    """58000 → 58.000. German separator, which is what the page prints."""
    return "{:,}".format(int(n)).replace(",", ".")


def claims(posting):
    """(label, needle) for every value the reader must be able to find.

    A needle of None means the field was there but in a shape this script
    cannot check — reported as a finding rather than passed over, because an
    unreadable value is how a wrong one hides.
    """
    out = []

    if isinstance(posting.get("title"), str):
        out.append(("title", posting["title"]))

    for field in ("datePosted", "validThrough"):
        if field in posting:
            out.append((field, german_date(posting[field])))

    org = posting.get("hiringOrganization")
    if isinstance(org, dict) and isinstance(org.get("name"), str):
        out.append(("hiringOrganization.name", org["name"]))

    loc = posting.get("jobLocation")
    if isinstance(loc, list):
        loc = loc[0] if loc else None
    if isinstance(loc, dict):
        addr = loc.get("address")
        if isinstance(addr, dict):
            for key in ("streetAddress", "postalCode", "addressLocality"):
                if isinstance(addr.get(key), str):
                    out.append(("jobLocation." + key, addr[key]))

    salary = posting.get("baseSalary")
    if isinstance(salary, dict):
        value = salary.get("value")
        if isinstance(value, dict):
            for key in ("minValue", "maxValue", "value"):
                if key in value:
                    out.append(("baseSalary." + key, thousands(value[key])))

    return out


def audit(paths):
    findings = []          # (file, line, what)
    postings = []          # (file, line, posting)
    checked = 0

    for path in paths:
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as fh:
            source = fh.read()

        blocks = ld_blocks(source)
        if not blocks:
            continue

        page = Rendered()
        page.feed(source)

        here = []
        for line, raw in blocks:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                findings.append((rel, line,
                                 "ld+json does not parse: %s" % exc))
                continue
            for posting in job_postings(payload):
                here.append((line, posting))

        if not here:
            continue
        checked += 1

        if len(here) > 1:
            findings.append((rel, here[1][0],
                             "%d JobPosting blocks on one page. One page "
                             "describes one opening." % len(here)))

        line, posting = here[0]
        postings.append((rel, line, posting))

        # ONE OPENING — the block's title is the page's headline.
        title = posting.get("title")
        if len(page.h1s) != 1:
            findings.append((rel, line,
                             "%d <h1> on a page carrying a JobPosting; a page "
                             "about one opening has one headline"
                             % len(page.h1s)))
        elif isinstance(title, str) and norm(title) != page.h1s[0]:
            findings.append((rel, line,
                             "title %r is not the page's <h1> %r"
                             % (title, page.h1s[0])))

        if isinstance(title, str) and norm(title) in page.vacancy_links:
            findings.append((rel, line,
                             "the page's own opening %r is also an entry in a "
                             "register on it — that is a listing page" % title))

        # SIX FIELDS.
        for field in REQUIRED:
            if field not in posting or posting[field] in ("", None, [], {}):
                findings.append((rel, line, "no %s" % field))

        posted, through = posting.get("datePosted"), posting.get("validThrough")
        if german_date(posted) and german_date(through) and str(through) < str(posted):
            findings.append((rel, line,
                             "validThrough %s is before datePosted %s"
                             % (through, posted)))

        # THE MATCH.
        for label, needle in claims(posting):
            if needle is None:
                findings.append((rel, line,
                                 "%s is not a plain ISO date, so nothing on "
                                 "the page can be matched against it" % label))
            elif needle not in page.text:
                findings.append((rel, line,
                                 "%s says %r and the rendered page never says it"
                                 % (label, needle)))

        types = posting.get("employmentType")
        if isinstance(types, str):
            types = [types]
        for kind in types or []:
            if kind not in EMPLOYMENT_WORDS:
                findings.append((rel, line,
                                 "employmentType %r is not a schema.org value "
                                 "this check knows" % kind))
            else:
                words = EMPLOYMENT_WORDS[kind]
                if words and not any(w in page.text for w in words):
                    findings.append((rel, line,
                                     "employmentType %s and the page says none "
                                     "of %s" % (kind, " / ".join(words))))

    # ONE URL — across the whole tree, not within a page.
    for key in ("title", "identifier"):
        seen = {}
        for rel, line, posting in postings:
            value = posting.get(key)
            if isinstance(value, dict):
                value = value.get("value")
            if not isinstance(value, str):
                continue
            if value in seen:
                findings.append((rel, line,
                                 "%s %r is already the %s of a posting in %s. "
                                 "One URL per opening."
                                 % (key, value, key, seen[value])))
            else:
                seen[value] = rel

    return findings, postings, checked

# The English edition under patterns/en/ is generated, not written —
# scripts/build-i18n.py builds it from the German page beside it and changes
# only the words. It carries the same markup, the same classes, the same
# thresholds and the same glass by construction, so every fact this file
# keeps is already kept one directory up; asserting it twice would only mean
# two tables to edit whenever one page changes. `build-i18n.py --check` is
# what holds the mirror to its source. Same argument check-links.py makes
# about the generated pages at the repository root.
GENERATED = "patterns/en/"


def html_files():
    out = []
    for base, dirs, names in os.walk(TREE):
        dirs.sort()
        for name in sorted(names):
            if name.endswith(".html"):
                path = os.path.join(base, name)
                if os.path.relpath(path, TREE).replace(os.sep, "/").startswith(GENERATED):
                    continue
                out.append(path)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every claim checked, not only the failures")
    args = ap.parse_args()

    files = html_files()
    findings, postings, checked = audit(files)

    if args.verbose:
        for rel, line, posting in postings:
            print("  %s:%d  %s" % (rel, line, posting.get("title")))
            for label, needle in claims(posting):
                print("      %-26s %s" % (label, needle))
        print()

    if findings:
        for rel, line, why in findings:
            print("%s:%d  %s" % (rel, line, why), file=sys.stderr)
        print("\n%d JobPosting problem%s. The block and the page have to say "
              "the same thing." % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    total = sum(len(claims(p)) for _, _, p in postings)
    print("job postings: %d posting%s on %d page%s, %d claims matched against "
          "rendered text, %d files read."
          % (len(postings), "" if len(postings) == 1 else "s",
             checked, "" if checked == 1 else "s", total, len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
