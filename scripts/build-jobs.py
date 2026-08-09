#!/usr/bin/env python3
"""The vacancy register on karriere.html, generated from content/jobs/.

WHY THIS EXISTS, AND IT IS THE ARGUMENT build-news.py ALREADY MADE. A vacancy
was forty lines of hand-written markup in one file and a number in another
part of the same file — "4 offene Stellen" in the page header, four
<li class="cf-vacancy"> six hundred pixels below it. Adding a fifth meant
editing both, in the German pattern, and then the English edition and the two
generated root pages followed from there. scripts/check-register-count.py
exists because the two had already drifted; the page's own comment says "Die
Zahl in der Meta-Zeile ist die Länge des Registers weiter unten", and nothing
made that true.

SO A VACANCY IS A FILE AND THE REGISTER IS OUTPUT. content/jobs/ holds one file
per opening, and this script writes the two regions of karriere.html that
depend on it:

    jobs:meta    the page header's second mono line — how many are open
    jobs:list    the register itself, newest first

Everything else on that page — what we look for, how the process runs, the
accordion — is authored and comes through untouched.

FOUR FACTS PER ENTRY AND NOT FIVE, which is components/vacancy.html's own rule:
Standort, Anstellung, Umfang, Start. "That is content for the job page." The
fifth and sixth — Vergütung, Bewerbungsschluss — are drawn by
scripts/build-stellen.py on the page that has room for them.

A VACANCY WITH TEXT LINKS TO ITS PAGE, one without links to its own row. That
second form is not a placeholder this script invented; it is what karriere.html
already did for three of its four entries, with its own note: "solange es die
Stellenseite dahinter nicht gibt, ist der Selbstverweis der ehrliche
Platzhalter." An opening is worth listing before its ad is written, and a link
to a page that does not exist is the one thing that must not ship.

BOTH EDITIONS COME OUT OF ONE FILE. Every field a reader sees is a pair —
`titel`/`title`, `anriss`/`excerpt`, `standort`/`location` — and this keeps
design-system/i18n/en.json in step with what it writes, the same way
build-news.py does for the archive. An admin adds a vacancy in one place.

    python3 scripts/build-jobs.py            # write the register
    python3 scripts/build-jobs.py --check    # fail if the page is stale
    python3 scripts/build-jobs.py -v         # name every opening it laid out

After it: build-i18n.py, then build-stellen.py, then build-site.py — or just
scripts/build-all.sh, which is the order they have to run in.

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import importlib.util
import json
import pathlib
import re
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
JOBS = ROOT / "content" / "jobs"
PAGE = ROOT / "design-system" / "patterns" / "karriere.html"
CATALOGUE = ROOT / "design-system" / "i18n" / "en.json"
LEDGER = JOBS / ".catalogue.json"

REGION = "<!-- jobs:%s -->"
REGION_END = "<!-- /jobs:%s -->"

# Every field a reader sees exists twice, and the pairs are named here so that
# one table decides what has to be translated. A German value with no English
# one is a build failure, for the reason build-i18n.py fails on any other: an
# English page with one German sentence in the middle of it.
PAIRS = (("titel", "title"), ("anriss", "excerpt"), ("bereich", "area"),
         ("standort", "location"), ("anstellung", "employment"),
         ("umfang", "hours"), ("start", "starts"),
         ("adresse", "address"), ("verguetung", "salary"))
REQUIRED = ("kennung", "titel", "title", "anriss", "excerpt", "bereich", "area",
            "standort", "location", "anstellung", "employment",
            "umfang", "hours", "start", "starts", "seit")

# The four facts of the register, in the order components/vacancy.html draws
# them. The term is German on the German page and translated from the
# catalogue, where all four have had entries since the page was written.
FACTS = (("Standort", "standort", "location"),
         ("Anstellung", "anstellung", "employment"),
         ("Umfang", "umfang", "hours"),
         ("Start", "start", "starts"))

# THE ENGLISH RUN INSIDE A GERMAN TITLE, marked with braces in the file.
# "Data Engineer (m/w/d)" is two languages in one line: the role is English and
# "(m/w/d)" is a German legal formula. karriere.html carries the rule in a
# comment — marking the whole link lang="en" hands the formula to an English
# voice, WCAG 3.1.2 — and every title in the register obeyed it by hand. The
# braces are how a post file says which run is which, and they are dropped on
# the English page, where the whole line is English already.
MARK = re.compile(r"\{([^{}]*)\}")


def fail(msg):
    print("build-jobs: " + msg, file=sys.stderr)
    sys.exit(1)


def store():
    """build-news.py's reader for the two-language body, imported.

    A job posting and a news post are written in the same grammar, in the same
    two halves, with the same divider — and the parser for that belongs in one
    file. This is the same import build-stellen.py and build-articles.py make.
    """
    spec = importlib.util.spec_from_file_location(
        "cf_build_news", pathlib.Path(__file__).with_name("build-news.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_jobs():
    """Every opening in content/jobs/, newest first.

    A file that cannot be read is a failure and never a skip: a vacancy
    silently dropped from the register looks exactly like one nobody wrote, and
    on this page that is somebody's job advertisement.
    """
    news = store()
    if not JOBS.is_dir():
        fail("no content/jobs/ directory. One file per opening — the fields are "
             "in this script's header.")
    out = []
    for path in sorted(JOBS.glob("*.md")):
        job = {"file": path.name, "slug": path.stem}
        head, _, body = path.read_text(encoding="utf-8").partition("\n\n")
        for n, line in enumerate(head.splitlines(), 1):
            line = line.rstrip()
            if not line:
                break
            if ":" not in line:
                fail("%s:%d is not `feld: wert` — %r" % (path.name, n, line))
            k, v = line.split(":", 1)
            job[k.strip()] = v.strip()
        missing = [k for k in REQUIRED if not job.get(k)]
        if missing:
            fail("%s has no %s.\n"
                 "    Every opening needs an identifier, a date, and both "
                 "languages of everything a reader sees — the register ships "
                 "twice." % (path.name, ", ".join(missing)))
        for de, en in PAIRS:
            if job.get(de) and not job.get(en):
                fail("%s has `%s` and no `%s`. The English edition would carry "
                     "a German line." % (path.name, de, en))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", job["seit"]):
            fail("%s: seit is %r, not YYYY-MM-DD." % (path.name, job["seit"]))
        if job.get("frist") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", job["frist"]):
            fail("%s: frist is %r, not YYYY-MM-DD." % (path.name, job["frist"]))
        job["de"], job["en"] = news.bodies(body, path.name)
        # A CLOSING DATE IS REQUIRED OF AN OPENING THAT HAS A PAGE, and it is
        # not this repository's rule: components/vacancy.html states it and
        # scripts/check-job-posting.py enforces it — "an opening with no
        # validThrough stays live in search results after it is filled". The
        # JobPosting block is only written for an opening with an
        # advertisement, so that is exactly where the field becomes required.
        # It is a date somebody chooses, never a default: a deadline this
        # script invented would be a promise the company did not make.
        if job["de"] and not job.get("frist"):
            fail("%s has an advertisement and no `frist`.\n"
                 "    Its page carries a JobPosting block, and a posting "
                 "without a closing date stays in search results after the "
                 "position is filled — components/vacancy.html's rule, which "
                 "scripts/check-job-posting.py enforces.\n"
                 "    Set Frist in Notion, or leave the page empty and the "
                 "opening stays a listing." % path.name)
        out.append(job)
    if not out:
        fail("content/jobs/ is empty. karriere-leer.html is the page for that "
             "state and it is written by hand — this script lays out a "
             "register that has something in it.")
    # Newest first, and the FILENAME breaks a tie forwards rather than
    # backwards: four openings posted on one day are not in an order the date
    # knows about, and reverse-alphabetical is the one order nobody would
    # choose. Two passes because sort is stable.
    out.sort(key=lambda j: j["file"])
    out.sort(key=lambda j: j["seit"], reverse=True)
    return out


def anchor(job):
    """The row's own address on the register, and the id it has always had."""
    return "stelle-" + job["slug"]


def page_name(job):
    """The page an opening is read on, or None when there is no ad yet.

    scripts/build-stellen.py writes a page for every opening that has text, and
    this is where both scripts agree on which. `stelle-` and not `karriere-`
    because karriere-stelle.html is the specimen they are built from: one
    prefix means generated.
    """
    return "stelle-%s.html" % job["slug"] if job.get("de") else None


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def title_html(job, edition):
    """The title, with the English run marked on the German page only."""
    raw = job["titel"] if edition == "de" else job["title"]
    if edition != "de":
        return esc(MARK.sub(r"\1", raw))
    out, pos = [], 0
    for m in MARK.finditer(raw):
        out.append(esc(raw[pos:m.start()]))
        out.append('<span lang="en">%s</span>' % esc(m.group(1)))
        pos = m.end()
    out.append(esc(raw[pos:]))
    return "".join(out)


def plain_title(job, edition="de"):
    return MARK.sub(r"\1", job["titel"] if edition == "de" else job["title"])


def entries(jobs, indent="        "):
    """The register: one <li class="cf-vacancy"> per opening."""
    out = []
    for job in jobs:
        href = page_name(job) or ("karriere.html#" + anchor(job))
        out.append('%s<li class="cf-vacancy" id="%s">' % (indent, anchor(job)))
        out.append('%s  <p class="cf-vacancy__meta"><span>%s</span></p>'
                   % (indent, esc(job["bereich"])))
        out.append('%s  <h3 class="cf-vacancy__title">' % indent)
        out.append('%s    <a class="cf-vacancy__link" href="%s">%s</a>'
                   % (indent, href, title_html(job, "de")))
        out.append("%s  </h3>" % indent)
        out.append('%s  <p class="cf-vacancy__excerpt">' % indent)
        # Wrapped the way the page was written by hand: a generated file is
        # read in the repository as often as in a browser, and a paragraph on
        # one 200-character line is a diff nobody can review.
        out.append(textwrap.fill(esc(job["anriss"]), width=96 - len(indent),
                                 initial_indent=indent + "    ",
                                 subsequent_indent=indent + "    ",
                                 break_long_words=False, break_on_hyphens=False))
        out.append("%s  </p>" % indent)
        out.append('%s  <dl class="cf-vacancy__facts">' % indent)
        for term, de, _ in FACTS:
            out.append('%s    <div class="cf-vacancy__fact">' % indent)
            out.append('%s      <dt class="cf-vacancy__term">%s</dt>' % (indent, term))
            out.append('%s      <dd class="cf-vacancy__value">%s</dd>'
                       % (indent, esc(job[de])))
            out.append("%s    </div>" % indent)
        out.append("%s  </dl>" % indent)
        out.append("%s</li>" % indent)
        out.append("")   # a blank line between entries, as the page was written
    return "\n".join(out).rstrip()


def meta(jobs, indent="          "):
    """The header's claim, which check-register-count.py holds to the list."""
    return "%s<span>%d offene %s</span>" % (
        indent, len(jobs), "Stelle" if len(jobs) == 1 else "Stellen")


def splice(html, name, body):
    start, end = REGION % name, REGION_END % name
    m = re.search(re.escape(start) + r".*?" + re.escape(end), html, re.S)
    if not m:
        fail("karriere.html has no %s … %s region. The fences are how this "
             "script knows what it owns; restore them." % (start, end))
    pad = re.match(r"[ \t]*", html[html.rfind("\n", 0, m.start()) + 1:m.start()]).group(0)
    inner = "\n%s\n%s" % (body, pad) if body else "\n%s" % pad
    return html[:m.start()] + start + inner + end + html[m.end():]


# --------------------------------------------------------------------------
# the catalogue
# --------------------------------------------------------------------------

def derived(jobs):
    """Every string this script writes onto the page, with its English twin.

    The same division build-news.py draws: what an admin types belongs in the
    file, in both languages, and what this script DERIVES from those fields —
    the count — is translated here, mechanically, in the catalogue's own idiom.
    """
    pairs = {}
    for job in jobs:
        pairs[plain_title(job, "de")] = plain_title(job, "en")
        pairs[job["anriss"]] = job["excerpt"]
        pairs[job["bereich"]] = job["area"]
        for _, de, en in FACTS:
            pairs[job[de]] = job[en]
    pairs["%d offene %s" % (len(jobs), "Stelle" if len(jobs) == 1 else "Stellen")] = \
        "%d open %s" % (len(jobs), "position" if len(jobs) == 1 else "positions")
    return pairs


def strings_used_elsewhere():
    """Every catalogue key some OTHER German pattern page actually shows.

    Asked of build-i18n.py rather than guessed at, for the reason build-news.py
    states at length: a grep finds a string inside a comment and inside another
    string, and both of those are dead entries that fail the next build. This
    page is excluded — its strings are exactly what `pairs` holds, and the copy
    on disk is the version being replaced.
    """
    spec = importlib.util.spec_from_file_location(
        "cf_build_i18n", pathlib.Path(__file__).with_name("build-i18n.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cat, overrides = mod.load_catalogue()
    before = set(mod.USED)
    for page in mod.source_pages():
        if page == PAGE:
            continue
        mod.build(page.read_text(encoding="utf-8"), page.name,
                  mod.for_page(cat, overrides, page.name), set())
    return set(mod.USED) - before


def catalogue(pairs, write):
    """Add what the register now shows, remove what it no longer shows.

    A ledger and not a shape, for the reason build-news.py learned twice: a
    vacancy's fact value is "Konstanz, hybrid", which is also a string the team
    page could use tomorrow, and "Vollzeit" is a word. Only keys this script
    wrote last time are ever taken back, and only when nothing else shows them.
    """
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    added = {k: v for k, v in pairs.items() if data.get(k) != v}
    owned = set(json.loads(LEDGER.read_text(encoding="utf-8"))) if LEDGER.exists() else set()
    used = strings_used_elsewhere()
    stale = sorted(k for k in owned if k in data and k not in pairs and k not in used)
    if write:
        if added or stale:
            for k in stale:
                del data[k]
            data.update(added)
            CATALOGUE.write_text(
                json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
        ledger = json.dumps(sorted(pairs), ensure_ascii=False, indent=2) + "\n"
        if not LEDGER.exists() or LEDGER.read_text(encoding="utf-8") != ledger:
            LEDGER.write_text(ledger, encoding="utf-8")
    elif sorted(pairs) != sorted(owned):
        stale = sorted(set(owned) ^ set(pairs)) or stale
    return added, stale


# --------------------------------------------------------------------------

def build(jobs):
    html = PAGE.read_text(encoding="utf-8")
    html = splice(html, "meta", meta(jobs))
    html = splice(html, "list", entries(jobs))
    return html


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="fail if the page or the catalogue is stale")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    jobs = read_jobs()
    html = build(jobs)
    current = PAGE.read_text(encoding="utf-8")
    missing, stale = catalogue(derived(jobs), write=not args.check)

    if args.check:
        if html != current:
            fail("design-system/patterns/karriere.html is stale — content/jobs/ "
                 "has %d opening(s) and the page does not say so.\n"
                 "    run: python3 scripts/build-jobs.py" % len(jobs))
        if missing or stale:
            fail("en.json is out of step with the register: %d string(s) shown "
                 "have no entry and %d retired one(s) are still there.\n%s\n"
                 "    run: python3 scripts/build-jobs.py"
                 % (len(missing), len(stale),
                    "\n".join(["      + " + t for t in missing]
                              + ["      - " + t for t in stale])))
        print("jobs OK — %d opening(s), the register matches content/jobs/"
              % len(jobs))
        return 0

    if html != current:
        PAGE.write_text(html, encoding="utf-8")
    note = ""
    if missing or stale:
        note = ", catalogue %+d/%-d" % (len(missing), len(stale))
    with_page = [j for j in jobs if page_name(j)]
    print("jobs built — %d opening(s), %d with an ad%s"
          % (len(jobs), len(with_page), note))
    if args.verbose:
        for j in jobs:
            print("  %-28s %s  %s" % (j["slug"], j["seit"],
                                      page_name(j) or "(no ad — links to its row)"))
    print("     then: python3 scripts/build-i18n.py && python3 scripts/build-stellen.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
