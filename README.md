# Website of control-f

The website is the 2026 brand: the pages under [`design-system/patterns/`](design-system/patterns/),
served from the repository root. **Eighteen written pages** — landing page, Expertise,
Über uns, News and a topic and an article, Suche and its empty state, Karriere and a
posting and its empty state, Kontakt and its confirmation, Bewerbung and its
confirmation, Datenschutz, Impressum, 404 — each in two languages, German at the root
and English under `/en/`.

**And twenty-five more that are generated from content rather than written**: one
reading page per news post that has text, one Stelle page per opening that has an
advertisement, and one page per topic in use. Which is why the count in the pattern
directory is 43 and the count at the root is 86: `ls` sees the written pages and the
generated ones together, and only the prefix says which is which — `beitrag-`,
`stelle-` and `news-thema-<slug>` are output. `scripts/README.md` is the table of what
owns what.

The generation before it — nine hand-written pages against `assets/css/main.css` — has
been removed.

## The root is generated

Every `.html` file at the root is written by [`scripts/build-site.py`](scripts/build-site.py)
out of the matching page in `design-system/patterns/`, **and none of it is in git.**
Clone this repository and there is no website in it until you build one:

```bash
sh scripts/build-all.sh                  # the whole chain, in the one order that works
python3 -m http.server 8000              # then it is there
```

Until 2026-08-17 the output was committed beside its sources — the 43 pages here, the
43 under `en/`, the 43 English patterns and the 25 generated pattern pages. 154 files,
four copies of every logical page, 70 % of the tracked HTML lines. A one-word copy
change rewrote four files; `grep` answered four times over and one of the answers was
the source; an hourly Notion import arrived as a ninety-six-file diff nobody read.

What replaced `--check` as the gate:

```bash
sh scripts/build-and-verify.sh           # build, then fail if a TRACKED file moved
python3 scripts/check-tracked-outputs.py # fail if generated output is tracked
```

The first is the one that catches real mistakes now. `en.json`, the fenced regions of
`patterns/news.html` and `patterns/karriere.html`, and the two `content/*/.catalogue.json`
ledgers are written by generators and *are* committed — they are the record of which
strings a build owns, and no build can reconstruct them. Building and then asking git
whether anything moved is what holds those to their sources, and it catches a stale
ledger, which comparing output to source never could.

`--check` still exists on every builder and is still the right thing to run at a desk:
it answers "is the tree in front of me current?". It cannot be the CI gate any more,
because a fresh checkout has no pages for it to compare.

The patterns cannot simply live at the root: 117 `scripts/check-*.py` read them
from `design-system/patterns/`, several keyed on that path by string, and the routines run
against it. So the pattern stays where it is checked and the root holds its shipped form,
which differs by four edits and nothing else — asset paths, the landing page's name, and
the two pieces of preview chrome that never ship. The script's own header lists them.

`design-system.yml` builds first and then runs the checks — it has to, since two of
them read pages — and both deploys build the whole chain before they stage, so there is
no such thing as a forgotten rebuild reaching production.

There is one copy of every stylesheet, script, font and image, in
`design-system/assets/`. The shipped pages and the documentation load the same files.

## So is the English edition

`/en/` is the same pages with the words changed, and it is generated one step
earlier in the same chain by [`scripts/build-i18n.py`](scripts/build-i18n.py):
`design-system/patterns/en/` is built from the German pattern beside it, and
`build-site.py` then ships that directory the way it ships the German one.

Twenty-one written sources go through the catalogue that way. The article and
Stelle pages do not: they arrive already bilingual, because their text is two
halves of one file in `content/` — divided by a `--- en ---` line — and
`build-articles.py` and `build-stellen.py` splice each half into the edition it
belongs to. No article's prose ever enters `en.json`.

```bash
python3 scripts/build-i18n.py            # write design-system/patterns/en/
python3 scripts/build-i18n.py --check    # fail if any page is stale or missing
python3 scripts/build-i18n.py --extract  # print every German string with no entry
```

What is written by hand is one file: [`design-system/i18n/en.json`](design-system/i18n/en.json),
German copy on the left and English on the right. Markup, class names, comments, ids,
page-local `<style>` and `<script>`, the isometric drawings and the act structure are not
duplicated — they come through from the German page byte for byte, so
`diff patterns/kontakt.html patterns/en/kontakt.html` is a list of sentences. Anchors and
ids stay German in both editions on purpose: they are identifiers, and sharing them means
a deep link works in either language.

**A German string with no entry in the catalogue fails the build.** That is the part
worth having. The alternative is an English page that quietly ships one German sentence
in the middle of it, which is the failure nobody reviews — and for a month it was five
scheduled routines writing new sentences into the landing pattern every hour, unattended.
Add the copy in German, run `--extract`, translate what it prints, rebuild.

The catch is that the entry is keyed on the German text itself, so **rewording a
sentence fails the build twice**: `UNTRANSLATED` for the new string and `UNUSED` for
the entry the old one left behind. Both are `--extract`-able and both are deliberate;
`scripts/README.md` records it as a known trap rather than a bug.

The two editions point at each other from the nav — the `EN` / `DE` plate at the top
right — and from a `<link rel="alternate" hreflang>` pair in the head. Both are written
by the generator, so they cannot disagree about where the other edition is.

The 117 `scripts/check-*.py` do not read `patterns/en/`. Every fact they keep is
already kept on the German page one directory up, and the English page carries the same
markup, classes, thresholds and glass by construction; asserting it twice would only mean
two tables to edit whenever one page changes. `build-i18n.py --check` is what holds the
mirror to its source.

## Development

```bash
python3 -m http.server 8000    # repo root
```

- Website: <http://localhost:8000/> · English: <http://localhost:8000/en/>
- Design system: <http://localhost:8000/design-system/>

The design system is there in a fresh clone; the website is not. `sh scripts/build-all.sh`
first, or the root is a directory of sources and `/` is a 404.

## Automation

Most commits on `main` **were** written by scheduled cloud agents that merged their own
pull requests, with no human review gate — at peak, 145 in a day. All 29 of them are
switched off as of 2026-08-17, and the only thing still writing to `main` on a schedule
is in this repository: `news-sync.yml`, hourly at `:25`, importing the news archive and
the vacancy register from Notion.

That matters in both directions, and [.github/ROUTINES.md](.github/ROUTINES.md) is the
record: what each routine was, what it was told, the trigger ids to check them by — and
why switching one back on unread is the hazard, since eighteen of the briefs predate the
generated root and would edit a pattern without ever rebuilding the page that ships.

## The contact form has a server

Every page is a static file except one route. `design-system/components/forms.html`
says of the error summary "It is rendered by the server, not by a script", and
`patterns/kontakt.html` posts to its own URL so a failed submit lands on that summary
with nothing running. [`worker/`](worker/) is that server — one path, one method:

| | |
|---|---|
| honeypot filled | `303` → `kontakt-danke.html`, discarded silently |
| validation fails | `422`, the same page with the summary, the per-field messages and the values already typed |
| sent | `303` → `kontakt-danke.html` (Post/Redirect/Get, so a reload does not send twice) |

No JavaScript is involved on either path. The form's markup did not change to make
this work — posting to its own address was always the precondition.

Mail goes out through **Resend**. Its `eu-west-1` region dispatches from Ireland, but
account data, logs and metadata are stored in the US — a third-country transfer, and
`datenschutz.html` names it as one. `worker/mail.js` is the only file that knows the
provider; swapping it for an EU-domiciled one is about twenty lines and would let that
section shrink.

```bash
npx wrangler dev --local
```

Needs `RESEND_API_KEY` in `.dev.vars` (gitignored). `scripts/check-form-contract.py`
holds the form and the Worker to each other — field names, ids, topics, the honeypot,
the summary's anchor, two error strings and both routes.

## Deployment

Every merge to `main` publishes the website to GitHub Pages via
`.github/workflows/deploy.yml`.

`deploy-worker.yml` publishes the same pages to Cloudflare with the Worker in front of
them. It runs only when the `CLOUDFLARE_ENABLED` variable is set, so it is inert until
someone turns it on, and **both deploys run in parallel** — the cutover is a DNS change,
not a merge. Cloudflare serves `dist/`, which `scripts/stage-site.py` fills with the
86 generated pages and `design-system/` and nothing else in the repository.

**GitHub Pages serves that same directory now.** It used to upload the checkout —
`path: .`, which excludes `.git` and `.github` and nothing else — so the public site
answered 200 for every generator, every check script, the Worker's source,
`wrangler.toml` and the content store. `deploy.yml` stages with
`stage-site.py --surface pages` and uploads `dist/`, so both deploys ship the same
bytes and neither ships the repository.

One difference between the two hosts is configured away: Cloudflare's asset server
answers `/kontakt.html` with a `307` to `/kontakt` by default, which would rewrite every
address on the site and break the form outright. `html_handling = "none"` turns that off,
at the price of the directory indexes — so the Worker serves `/` and `/design-system/`,
and `stage-site.py --check` fails if a third one ever appears without a route.

- Website: https://control-f-io.github.io/control-f-website/
- Design system: https://control-f-io.github.io/control-f-website/design-system/

Because the site is served from a subpath, links and asset references must stay
**relative** (`design-system/assets/css/tokens.css`, `expertise.html`) — a leading `/`
would resolve against `control-f-io.github.io` and 404. `scripts/check-links.py` holds
that rule for the design system; the generator carries it to the root.

## Fragen

- Answered 2026-08-03: the contact address is `info@control-f.io` and the press
  address `presse@control-f.io`. `jobs@` and `datenschutz@` were not named and
  still write `control-f.de`.
- Answered 2026-08-13: the phone number on Impressum and Datenschutz was
  Simon's personal mobile, not a company line — removed from the pages (and
  from this file, and from git history) rather than replaced.
- host control-f.io or controlf.io or both?
- Three of these were about the outgoing homepage and the new design has already
  answered them: the header folds into a menu button below 780 px and is a flat bar
  above it, "Home" is the first item in it, and the map/mail/LinkedIn strip is gone.
  Say so if any of that is wrong.
- Legal placeholders still to be filled by a lawyer: `HRB 000000`, `DE000000000`, the
  Amtsgericht, the photography credit, the log retention, the hosting provider, and
  whether Matomo and the LinkedIn tags are what actually ships.
  → `design-system/README.md`

## TODOs

- SEO optimizations
- optimize for Google Lighthouse
- Redirects for the outgoing URLs (`experten.html`, `dienstleistungen.html`,
  `energie.html`, `maschinenbau.html`, `blog/`) if any of them are linked from outside
