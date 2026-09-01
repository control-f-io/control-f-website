# scripts/

Everything that generates this website, and everything that refuses to let it
ship broken. 144 files at this level, this one included, no shared library, no
package, no `__init__.py`, no build step: every one is `python3` against the
standard library and is run by its own path. There are exactly two dependencies
in the whole directory — Pillow, in `sync-news-notion.py` and nowhere else, and
Playwright, in `check-runtime.py` and nowhere else — and both are discussed
below.

This file exists because the directory has grown past the point where its shape
can be inferred by reading it. Several of the names in here are frozen strings
in five GitHub workflows, in twenty-seven of these scripts, in `wrangler.toml`
and in prompts that live outside the repository, and none of those consumers
appear in a grep for `import`. *Do not rename these* is the section that matters
most.

---

## What is in here

| Count | What | Who runs it |
| --- | --- | --- |
| 126 | `check-*.py` — one design-system invariant each, exit 0 or exit 1 | `design-system.yml` on every push, one enumerated step per check; `routine-merge.yml` on every routine branch, by glob |
| 7 | `build-*.py` — the generators, in the order below | both deploys and `news-sync.yml` (all seven, via `build-all.sh`), and both gates (via `build-and-verify.sh`) |
| 1 | `build-all.sh` | `news-sync.yml`, and a human. Nothing else. |
| 1 | `stage-site.py` — collects the website into `dist/` | both deploys, `--surface pages` and `--surface worker` |
| 3 | `gen-*.py` — deterministic SVG geometry spliced into pages | `design-system.yml`, `--check` only |
| 2 | `sync-{news,jobs}-notion.py` — Notion → `content/` | `news-sync.yml`, hourly at `:25` |
| 2 | `new-post.py`, `new-job.py` — write one file into `content/news/` or `content/jobs/` | nobody. They are human tools. |
| 1 | `build-and-verify.sh` — build, then fail if a tracked file moved | both gates, as their first step |

**The website is not in the checkout.** Since 2026-08-17 the 154 generated pages —
43 at the root, 43 under `en/`, 43 English patterns, 25 generated pattern pages —
are ignored rather than committed. Clone the repository and there is no site in it
until `sh scripts/build-all.sh` writes one, into exactly the paths it always
occupied. `check-tracked-outputs.py` fails a branch that adds one back.

Plus two subdirectories:

- **`data/`** — three vendored inputs. `world-110m.json` is Natural Earth
  110m admin-0, public domain, read by `gen-world-map.py`; it is vendored
  rather than fetched because a generator that needs the network is a
  generator CI cannot run. `notion-news.sample.json` and
  `notion-jobs.sample.json` are saved API responses for the sync scripts'
  `--fixture FILE` flag, which is how the Notion transform is exercised
  without a token. No workflow names any of the three; they are inputs, not
  steps.
- **`expertise-objects/`** — eight files. `isolib.py` (the isometric
  projection and primitives), `objects.py` (the four Expertise drawings),
  `gen-flow-root.py` (the landing page's branching root, and the only one of
  the three that CI runs, as `--check`), the four `0{1..4}-*.svg` those
  produce, and its own `README.md`, which is the authority on that
  subdirectory's two load-bearing conventions.

`check-runtime.py` is the one check that opens a browser instead of reading
files. It runs in its own `design-system.yml` job with Playwright installed, and
it skips with exit 0 when no browser is present — except when
`CF_REQUIRE_BROWSER` is set, which is how the CI job stops a broken install
step from silently dodging the gate.

### The 126 checks are two different kinds of file wearing one prefix

Roughly half assert a property of the design system: `check-spacing-scale.py`
holds `foundations/layout.html`'s published `--space-*` table to the shipping
CSS; `check-glass-budget.py` holds the two-blurred-layer rule that is invisible
in every screenshot; `check-grid-tracks.py` holds the rule that a bare `fr`
floors at `min-content`. These read `design-system/assets/css/` and every
`patterns/*.html`, and they keep working as pages come and go.

The other 46 name `landing-page.html` as a string — 39 of them as the literal
path `patterns/landing-page.html`, usually as a key in an exemption table or a
per-page budget. Those are page-regression tests. They have a different
lifecycle from a true invariant: they are correct only about the page as it
stands, they are the reason the pattern pages cannot be moved, and a page
deleted or renamed makes them either fail or, worse, pass vacuously. Treat the
two groups differently when you clean up.

### The prefix is not a taxonomy, and in three places it actively misleads

The first word of a check's name is the subject the author had in mind, not a
category anyone assigned. 89 distinct first words across 126 files, 72 of them
singletons. Where a prefix does repeat it usually means what it looks like —
the twelve `check-flow-*.py` are all about the statement-to-process root, the
four `check-pin-*.py` are all about the pinned-stage scroll contract — and then
there are these:

| Name | Actually about | Reads |
| --- | --- | --- |
| `check-band-flow.py` | JS scroll behaviour — the fraction `cf-pin-gate.js` keeps through a band across a reflow | `assets/js/cf-pin-gate.js` + four stylesheets |
| `check-band-inset.py` | layout — a band that re-derives the page margin must use `.container`'s one number | four stylesheets |
| `check-band-rule-continuity.py` | layout — a hairline drawn as a border sits inside its own box, so the same column line lands a pixel apart depending on which side drew it | three stylesheets |
| `check-label-ramp.py` | typography — `--text-xs` is mono labels only, never prose | three stylesheets |
| `check-label-clearance.py` | SVG annotation geometry — a numeral on the flow root holds the clearance the root publishes | `patterns/`, `prototypes/`, `tokens.css` |
| `check-label-frame.py` | SVG annotation geometry — an HTML layer placed in a drawing's coordinates gets the drawing's box | four stylesheets + every page |

Do not group by prefix, and do not assume two files with a shared stem read the
same inputs.

### The docstrings are load-bearing, and one check enforces that

Every check opens with a long docstring arguing its rule, and the strongest move
in those arguments is the hand-off: *this file holds one axis of the seam, that
one holds the other.* `check-cited-gates.py` exists because that move was once a
lie — `check-flow-handover.py` named two gates that had never been written, and
`git log -S` finds both names in exactly one commit: the one that added the
docstring naming them. The seam stayed open for four months of hourly routines.

So the rule now is mechanical: any `scripts/check-<name>.py` written inside any
file in `scripts/` must exist, every check named in `design-system.yml` must
exist, **and every check in `scripts/` must be named in `design-system.yml`**. A
gate written and never wired is prose with a shebang, and this repository has
shipped that too.

---

## The build order is semantic, and `build-all.sh` is the only complete statement of it

```
python3 scripts/build-news.py
python3 scripts/build-jobs.py
python3 scripts/build-i18n.py
python3 scripts/build-articles.py
python3 scripts/build-stellen.py
python3 scripts/build-site.py
python3 scripts/build-search-index.py
```

| # | Script | Writes | Splices into |
| --- | --- | --- | --- |
| 1 | `build-news.py` | `patterns/news.html`, `news-thema-<slug>.html` (3 today, one per topic in use), and the archive's titles into `i18n/en.json` | 5 `news:` regions |
| 2 | `build-jobs.py` | `patterns/karriere.html`, and the register's strings into `i18n/en.json` | 2 `jobs:` regions |
| 3 | `build-i18n.py` | `patterns/en/` — 21 source pages, translated | nothing; it rewrites whole pages |
| 4 | `build-articles.py` | `beitrag-<slug>.html` (18 today) in **both** editions | 9 `article:` regions of `blog-artikel.html` and `en/blog-artikel.html` |
| 5 | `build-stellen.py` | `stelle-<slug>.html` (4 today) in **both** editions | 10 `stelle:` regions of `karriere-stelle.html` and `en/karriere-stelle.html` |
| 6 | `build-site.py` | the 86 shipped pages — 43 German, 43 English. 18 per edition at the root, the other 25 under `blog/`, `stellen/` and `news/thema/` | nothing; four textual edits and no template |
| 7 | `build-search-index.py` | `assets/search/index-de.json` and `index-en.json` — 186 records per edition, one per page and one per `<h2>` under its `<main>` | nothing; it reads the shipped pages and writes beside the assets |

Step 7 is the odd one and its position is the whole of its argument: it reads the
**shipped** pages rather than the patterns, because a search result carries an
address and a pattern's address is not the page's — `beitrag-<slug>.html` is
served at `/blog/<slug>.html`, and re-deriving that mapping would be
`build-site.py`'s table written twice. Run it earlier and every link still
resolves; they just answer the question the site was asking one build ago, which
is the one failure a search index cannot show you.

**Why the order cannot be permuted.** Steps 1 and 2 write into
`design-system/i18n/en.json`, because a generated headline is copy that needs an
English counterpart like any other. Step 3 reads that catalogue and those pages
to produce the English edition, so it must come after them — run it first and
the English archive is a generation behind, which reads as a correct page and is
not. Steps 4 and 5 splice per-item text into the **translated specimens** step 3
produces (`en/blog-artikel.html`, `en/karriere-stelle.html`), so they cannot run
before it exists; and step 3 skips `beitrag-*.html` and `stelle-*.html` for the
matching reason — those pages are already in both languages before it looks at
them. Step 6 reads everything and writes the root.

**The splice mechanism.** Each generator owns a set of regions in a
hand-written specimen page, fenced by a pair of HTML comments in its own
namespace: `<!-- article:prose -->` … `<!-- /article:prose -->`. Everything
outside the fences — the head, the consent banner, the nav, the grid, the footer
— is authored once on the specimen and inherited by every generated page on the
next build. This works across the language boundary for one specific reason:
**`build-i18n.py` never touches HTML comments**, so the fences survive
translation and mark the same regions in `patterns/en/`. That is not an
incidental property. It is what lets steps 4 and 5 exist at all.

**Why CI builds instead of running the six `--check`s.** It used to run them: a
page edited by hand instead of regenerated had to *fail* rather than be silently
rebuilt under whoever's commit ran next. That question needed the output to be
committed, and since 2026-08-17 it is not — a fresh checkout has none of the 154
generated pages, so all six `--check`s would report them MISSING for the one
reason that is expected.

Both gates now run **`scripts/build-and-verify.sh`** as their first step: build
everything, then fail if any *tracked* file moved. It asserts strictly more than
the six did, because the files that are still tracked and still generator-written
are the ones a stale commit actually breaks —

| Tracked, and partly written by a generator | Written by |
| --- | --- |
| `design-system/i18n/en.json` | `build-news.py`, `build-jobs.py` (derived strings), and people |
| `design-system/patterns/news.html` | `build-news.py`, inside `<!-- news:… -->` fences |
| `design-system/patterns/karriere.html` | `build-jobs.py`, inside `<!-- jobs:… -->` fences |
| `content/news/.catalogue.json`, `content/jobs/.catalogue.json` | the two builders — the record of which `en.json` keys each owns |

None of those can be reconstructed from the pages, which is why they stay in git,
and comparing output to source could never see a stale ledger.

**It has to be the first step, not merely an early one.** Measured by taking the
154 files out of a built tree and running the suite: 114 of the 117 checks did not
notice. `check-form-contract.py` did — it reads `patterns/en/kontakt.html` and
`patterns/en/bewerbung.html` — and `check-links.py` reported 70 MISSING
references. Anything that reads a page must run after the build.

Both deploys run **all seven** generators in write mode before staging.
`build-i18n.py` and `build-site.py` alone was enough while the other five
generators' output was committed; now it would publish a site missing 25 pages per
edition, and `build-site.py`'s `SHIP` globs the generated patterns, so it would not
notice they were gone.

---

## One prefix means generated

| Pattern | Status | Written by |
| --- | --- | --- |
| `beitrag-<slug>.html` | generated, German and English | `build-articles.py` |
| `stelle-<slug>.html` | generated, German and English | `build-stellen.py` |
| `news-thema-<slug>.html` | generated, German; translated by `build-i18n.py` | `build-news.py` |
| `patterns/en/*.html` | generated in full | `build-i18n.py` |
| every `*.html` at the repository root | generated in full | `build-site.py` |
| `design-system/assets/search/index-*.json` | generated in full | `build-search-index.py` |
| `blog-artikel.html` | **authored** specimen — and it ships | a person |
| `karriere-stelle.html` | **authored** specimen — and it ships | a person |
| `news-thema.html` | **authored** specimen — and it ships | a person |
| `news.html`, `karriere.html` | authored, with fenced regions a generator owns | both |
| `content/news/YYYY-MM-DD-<slug>.md` | the store. One file per post. | `new-post.py`, or the Notion sync |
| `content/jobs/<slug>.md` | the store. One file per opening. | `new-job.py`, or the Notion sync |
| `content/autoren.json` | who wrote a post, and the title their byline carries | a person |
| `content/themen.json` | the topic vocabulary — one entry per chip on the archive's filter, in the order the chips stand | the Notion sync, out of the `Themen` property; the English name by a person |

The three authored specimens are the surfaces the generated pages are made of,
and they ship as themselves as well — they are documented, linked and read,
which is why they are worth keeping honest. A change to the reading surface is
made once, on `blog-artikel.html`, and every published article has it on the
next build.

**The vocabulary mixes German and English stems, and this is documented rather
than fixed.** A news post lives in `content/news/`, is listed on `news.html`,
and its page is `beitrag-<slug>.html` off the specimen `blog-artikel.html` —
three languages' worth of stems for one object. A vacancy lives in
`content/jobs/`, is listed on `karriere.html`, and its page is
`stelle-<slug>.html` off the specimen `karriere-stelle.html`. The reason none of
this is renamed is that every one of those names is either a live URL that has
been served and may be linked, or the file identity the Notion sync matches on
to decide whether a row is a new post or an existing one. Renaming the stems
means a redirect table and a sync that re-imports the whole archive as new
files. The inconsistency is cheaper than the migration.

---

## Do not rename these

Each row names a string and who reads it. None of these consumers is visible to
a grep for `import`, and several are outside this repository.

| Frozen string | Consumed by | What breaks |
| --- | --- | --- |
| `design-system/patterns/` | 27 scripts contain the literal path `design-system/patterns`; 114 name `design-system` as a quoted path component; 46 checks key on `landing-page.html` as a *string*, 39 of them as `patterns/landing-page.html`; routine prompts outside the repo name the directory and the page | the checks stop finding the pages, or pass vacuously against nothing. This is why the patterns cannot be `git mv`'d to the root and `build-site.py` exists instead. |
| the `check-` prefix | `routine-merge.yml`'s gate loop is `for s in scripts/check-*.py` | a check renamed out of the prefix stops running on every routine branch. Globbed rather than enumerated on purpose: a check written by a later run is enforced by existing. |
| `check-image-scale.py` | imported by `build-news.py`, `build-articles.py`, `check-content-images.py` (`intrinsic()`), and `sync-news-notion.py` (`intrinsic_bytes()`) | the builds and the Notion sync fail. It owns the raster header reader because it is also the file that fails a `width`/`height` disagreeing with the file — two readers of a progressive JPEG would disagree exactly once, and the check would be right while the page was wrong. |
| `check-content-images.py` | imported by `sync-news-notion.py` for `MIN_WIDTH`, `MAX_WIDTH`, `MAX_BYTES` | the sync loses the plate it fits pictures to. The gate is the authority on its own numbers. |
| `check-grid-tracks.py` | imported by `check-page-local-tracks.py` for one definition of `floored` | a second, drifting definition of the `fr` floor rule. |
| `build-news.py` | imported by `build-jobs.py`, `build-articles.py` (and transitively `build-stellen.py`) as the reader of `content/`'s two-language body and `page_name()` | a second opinion about what a post is. The first thing two readers would disagree about is which posts have a page at all. |
| `build-i18n.py` | imported by `build-news.py` and `build-jobs.py` to ask which catalogue keys other pages actually use | dead `en.json` entries, which fail the next build. |
| `build-jobs.py`, `build-articles.py` | imported by `build-stellen.py` (`JOBS`, `ART`) | the job pages lose the register reader and the splice helpers. |
| `build-site.py` | imported by `stage-site.py` for `ship()` | `dist/` reverts to a typed list. It used to be one, and the generated content pages were missing from it: the Worker answered `/stelle-data-engineer.html` with the 404 page while Pages served it correctly. |
| `sync-news-notion.py` | imported by `sync-jobs-notion.py` for `plain()`, `rich()`, `body_from()`, `children()`, `fetch()` | the jobs sync loses the entire Notion transform. |
| all seven `build-*.py` filenames | invoked by literal path from `deploy.yml`, `deploy-worker.yml`, `news-sync.yml` (via `build-all.sh`), `design-system.yml`, `routine-merge.yml` (via `build-and-verify.sh`), and each other | the deploy or the gate fails on a missing file, or the gate quietly stops asserting what the deploy asserts. |
| `content/news/`, `content/jobs/` | `build-news.py`, `build-jobs.py`, both syncs, `check-content-images.py`; each holds a `.catalogue.json` ledger | the stores stop being found and the pages regenerate as empty. |
| `content/themen.json` | `build-news.py` (the vocabulary a post's `themen:` is checked against, and the chips), `sync-news-notion.py` (writes it) | no post can be filed and the archive has no filter to draw — both scripts stop rather than guess. |
| the fence namespaces `news:`, `jobs:`, `article:`, `stelle:` | the four builders match `<!-- ns:name -->` … `<!-- /ns:name -->` by exact string against the specimens | the splice finds no region and the build fails — or, if a fence is half-renamed, splices into the wrong place. |
| `dist/` | `wrangler.toml`'s `assets.directory = "dist"`, `upload-pages-artifact`'s `path: dist` | neither deploy finds the website. |
| `"Deploy to GitHub Pages"`, `"Deploy the Worker"` | `routine-merge.yml` runs `gh workflow run "<display name>"` after it merges | main gains content and both surfaces keep serving the previous version. The merge push uses `GITHUB_TOKEN`, which never raises the push event those workflows listen for, so the dispatch by *display name* is the only trigger. |
| `routine/system-pages-**` | `routine-merge.yml`'s push filter, `news-sync.yml`'s branch naming and its `workflow_call` handoff, and the hourly routine's own branch name | a routine's work sits on the remote, gated by nothing, merged by nobody. It has happened: branch `routine/system-pages-news-20260807-2155`, ninety-six files of imported archive, zero workflow runs, stranded until a person opened the PR by hand. |
| `.github/workflows/routine-merge.yml` | called by path from `news-sync.yml`'s `uses:` | the sync pushes a branch and nothing gates or merges it. |

**Hyphenated filenames are why every one of these imports is a path hack.**
`check-image-scale` is not an identifier, so `import check_image_scale` cannot
work and `from . import` cannot work either — there is no package. Every
cross-script dependency therefore goes through
`importlib.util.spec_from_file_location`, and the whole web is these fourteen
call sites:

```
build-news.py      → check-image-scale.py, build-i18n.py
build-jobs.py      → build-news.py, build-i18n.py
build-articles.py  → check-image-scale.py, build-news.py
build-stellen.py   → build-jobs.py, build-articles.py
stage-site.py      → build-site.py
build-search-index.py → build-site.py         (ship(), for the addresses)
check-search-contract.py → cf-search.js, assets/search/index-*.json
sync-news-notion.py→ check-image-scale.py, check-content-images.py
sync-jobs-notion.py→ sync-news-notion.py
check-content-images.py   → check-image-scale.py
check-page-local-tracks.py → check-grid-tracks.py
new-post.py        → build-news.py            (the topic vocabulary, which is
                                               content/themen.json — read
                                               through the file that reads it)
new-job.py         → sync-jobs-notion.py      (the slug)
```

The last two are the pattern used deliberately rather than worked around: a
scaffolding tool that invented its own copy of the topic names, or its own
slug, would write a file the build rejects — or, worse, one the next hourly
Notion sync deletes and rewrites under a different name.

Note the shape of the dependency that matters: **three `check-*.py` files are
libraries.** `check-image-scale.py`, `check-content-images.py` and
`check-grid-tracks.py` are imported by builders, by another check, and by the
Notion sync. Renaming any of them breaks the build and the hourly content
import, and it does so invisibly to a grep for `import` — the filename appears
only as a quoted string inside a `with_name()` call. `check-cited-gates.py`
catches a *docstring* that names a script which does not exist, and it does not
read `.github/ROUTINES.md` or the routine prompts, so a check named individually
in a prompt can be renamed with nothing failing anywhere. (`ROUTINES.md`
currently names `check-seam-anchor.py`, which is not in this directory.)

---

## The pins

Three version numbers in this repository are exact, and each one is exact
because the failure from bumping it is silent.

| Pin | Where | What a bump does |
| --- | --- | --- |
| `Pillow==12.0.0` | `news-sync.yml`, `pip install` step | **Renames every picture in the archive.** A fitted image is stored as `<name>-<8 hex>.<ext>` where the hex is `sha1` of the *encoded bytes after fitting*. A Pillow release that re-encodes a JPEG differently — different subsampling, different progressive scan — produces different bytes, a different digest, a different filename, and the next sync writes the whole picture folder again under new names while the old ones are swept. Pillow is this repository's one dependency and is loaded in `sync-news-notion.py` and nowhere else. |
| `wranglerVersion: "4.119.0"` | `deploy-worker.yml`, `cloudflare/wrangler-action@v3` | **Deploys green and 405s the contact form.** Without the pin the action installs `wrangler@3.90.0`, which does not understand two fields this configuration depends on. It does not fail on them; it prints `Unexpected fields found in assets field: "run_worker_first"` and `Unexpected fields found in top-level field: "ratelimits"`, drops both, deploys, and exits 0. The Worker then never runs for `/kontakt.html`: Cloudflare's asset server answers the POST with 405, and there is no rate limit either. Measured on the deploy of `c0a6a9b`. Pinned to the patch rather than to `4` because a floating major puts the same class of surprise back one release later, and the failure is invisible from inside the deploy — which is why the last step of that workflow POSTs the honeypot form and requires a 303. |
| `VERSION = "2022-06-28"` | `sync-news-notion.py` (and `sync-jobs-notion.py` through it) | **Turns one request into two, or into a 404.** This is the Notion API version whose `/v1/databases/{id}/query` still exists and returns properties in the shape the sync parses. The 2025 line splits a database into data sources, so the same content needs a different endpoint and a different traversal. An API version that follows "latest" is a script that breaks on somebody else's release day. |

---

## Known traps

These are known, measured, and deliberately not fixed. Each one has a migration
recipe, and each recipe is larger than the bug.

### `slug()` strips hyphens *before* it truncates, so four live URLs end in one

The function is `re.sub(...).strip("-")[:48]`. The `strip("-")` runs on the full
string and the `[:48]` runs after it, so a title long enough to be cut can be
cut immediately after a hyphen and nothing removes it. Measured across the two
stores today: 22 slugs, **13 sitting exactly at the 48-character ceiling**, of
which **4 end in a trailing hyphen** —

```
2024-10-27-wie-blockchaintechnologie-die-energiewirtschaft-.md
2024-11-10-speicherloesungen-im-vergleich-lithium-vs-redox-.md
2024-11-24-nachts-strom-sparen-warum-nachtabsenkung-wieder-.md
2026-01-01-energiearmut-in-deutschland-ein-unterschaetztes-.md
```

— and the other nine are cut mid-word (`…solarpanel-koex`,
`…databricks-te`, `…hausbesitzer-jetzt-wi`).

*Migration.* Swapping the two operations to `[:48].rstrip("-")`, or truncating
at the last hyphen before 48, renames files in `content/`, renames every
`beitrag-*.html` and `stelle-*.html` in both editions, and changes URLs that
have been served. It needs a redirect table, and it must land as **one change
across every copy of `slug()` in this directory**, because the function has to
stay byte-identical in all of them. Three carry it today —

```sh
grep -n 'strip("-")\[:48\]' scripts/*.py
```

— `new-post.py`, `sync-news-notion.py` and `sync-jobs-notion.py`. Run that grep
rather than trusting this list: the copy count grows every time a store gains a
scaffolding tool, and the first two are already documented as required to agree
("a post drafted at the command line and then moved into Notion does not arrive
as a second file"). A one-file fix silently splits every long post into two.

### There is no shared library, and the duplication is measurable

- **36 definitions of `strip_comments()`** across 36 check scripts, in 21
  distinct code forms and five distinct behaviours: 18 delete the comment
  outright, 6 replace it with spaces of equal length (byte offsets survive), 6
  replace it with newlines only (line numbers survive), 4 collapse it to a
  single space, and 2 are hand-rolled scanners with a configurable delimiter.
  The behaviours are not interchangeable — a check that reports a line number
  needs the newline-preserving one and a check that reports a column needs the
  length-preserving one — so this is four or five *legitimate* functions copied
  seven times each, not one function copied 36 times.
- **22 private `HTMLParser` subclasses** across 21 files. No two agree on what
  they collect.
- **55 independent readers of `tokens.css`**, each building the path and
  regexing out the custom properties it cares about. 65 scripts name the file
  at all.

*Migration.* A `scripts/cflib/` package with the four comment strippers, one
parameterised HTML walker and one token table is the obvious answer, and it is
blocked on nothing technical. What it costs is a simultaneous edit to about 60
files that are individually correct, reviewed under a gate that runs all of them
on every push, while five hourly routines are editing the same directory. Do it
as its own change, not as a side effect of something else, and start with the
tokens reader — it has the most call sites and the least behavioural variation.

### `design-system/i18n/en.json` is a catalogue of exact German strings, so rewording German copy fails the build twice

The catalogue is a flat table of 1012 German → English pairs plus one `@pages`
key for the two strings that mean different things on different pages.
`build-i18n.py --check` fails on a German string with no entry (`UNTRANSLATED`)
**and** on an entry that matches no string on any page (`UNUSED`), and it exits
1 on either. Changing a comma in a German sentence therefore produces both
errors at once: the new wording is untranslated and the old wording is unused.
That pairing is deliberate — it is what makes a mistyped key name itself instead
of appearing as a mysterious missing translation — but it means **copy edits and
translation edits are one commit, never two.**

This is also the failure that forced the six builders into
`routine-merge.yml`'s gate. That step used to glob `scripts/check-*.py` and stop
there, while the `--check`s lived only in `design-system.yml` — a workflow a
`GITHUB_TOKEN` push never starts. A branch that changed German copy without
adding the pair self-merged green, then went red on `main`, and again in
`deploy.yml`, which runs `build-i18n.py` in **write** mode before uploading and
exits 1 on the missing entry. The site stops deploying — both editions, every
page — until somebody repairs the catalogue by hand.

*Migration.* `python3 scripts/build-i18n.py --extract` prints the missing
entries as JSON lines ready to paste. There is no migration away from
exact-string keys that keeps the property the catalogue exists for, which is
that a German sentence with no English counterpart is a build failure rather
than a page that ships with German in it.

---

## Running things locally

The full gate is what both workflows run, and it is a few hundred milliseconds
of stdlib python:

```sh
cd "$(git rev-parse --show-toplevel)"

fail=0
sh scripts/build-and-verify.sh || { fail=1; echo "FAILED the build"; }
for s in scripts/check-*.py; do
  python3 "$s" || { fail=1; echo "FAILED $s"; }
done
exit $fail
```

That is `routine-merge.yml`'s gate step verbatim, including the order: **the
build first**, because a fresh checkout has no pages and two of the checks read
them, and because building is what asserts the tracked half of the tree. Then the
checks, so a broken drawing is still reported when a catalogue entry is also
missing. `check-runtime.py` is in the glob and will skip with exit 0 unless
you have Playwright and set `CF_REQUIRE_BROWSER=1`; the four `gen-*.py`
`--check`s are wired in `design-system.yml` but are *not* in the glob, so add
them by hand when you have touched a generated drawing:

```sh
python3 scripts/gen-stmt-field.py --check
python3 scripts/gen-proto-field.py --check
python3 scripts/gen-world-map.py --check
python3 scripts/expertise-objects/gen-flow-root.py --check
```

To regenerate rather than assert, run `sh scripts/build-all.sh`. Never run one
builder alone unless you know it is the last one that matters — the order is the
whole point.

**`wrangler dev` needs `stage-site.py` run first.** `wrangler.toml` points its
assets directory at `dist/`, which is not tracked and does not exist in a fresh
checkout:

```sh
python3 scripts/build-i18n.py && python3 scripts/build-site.py
python3 scripts/stage-site.py            # --surface worker is the default
python3 scripts/stage-site.py --check    # asserts every directory index is a URL the Worker serves
npx wrangler dev
```

The staging step is not just convenience. Pointing wrangler at the repository
root makes it watch the directory it writes `.wrangler/` into, and `wrangler
dev` then reloads forever — measured at 387 reloads in two minutes before this
script existed. `.assetsignore` does not help; it governs what is uploaded, not
what is watched. Use `--surface pages` only to reproduce the GitHub Pages
artifact; it omits the `_headers` file that marks the Cloudflare copy `noindex`,
and it skips the Worker-routing assertions so a Cloudflare question can never
fail the Pages deploy.
