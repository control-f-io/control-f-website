# Control-F Design System

The implementation of the 2026 brand for the web. Hand-written HTML + CSS, no
dependencies — but not "no build step" any more, which this line used to claim:
the pages under `patterns/` are the source the shipped website is generated from,
and `scripts/build-all.sh` is the chain that generates it.

Source material — the brand manual, the logo files and the Figma mockups of the
Landing Page and Über uns — is **not in this repository**. It is ~194 MB and
`.gitignore` keeps it out; the path it is expected at, beside the checkout, is
`control_f_website_new_design/`. This line used to hyperlink that directory,
which 404s for everyone who does not already have it, including every reader of
the published copy of this page. The plates that are quoted rather than merely
referenced live in `assets/source/` and are rendered by
[`reference.html`](reference.html).

## Run it

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/design-system/>. It also works by opening
`index.html` directly from disk.

## Add a news post

```bash
python3 scripts/new-post.py "Neue Anlage in Konstanz ans Netz gegangen" \
        --title "New plant in Konstanz connected to the grid" \
        --themen "Energie" \
        --autor "Henry Beiker" --minuten 3
sh scripts/build-all.sh
```

That is the whole job. The first command writes one file under `content/news/`;
the second lays out the archive, keeps its counters and its year axis true,
translates what it generated, and rewrites the pages that ship. Both titles are
required — the site ships in two languages and a half-translated page is what
the catalogue exists to prevent — and the build says so rather than guessing.

**`--themen` is required too, and leaving it out of this command used to be what
this page told you to do.** A post filed under nothing is a card the topic
filter cannot place, so `build-news.py` refuses it — which means the two
commands above, written without it, wrote a file and then failed the build on
it. `new-post.py` prints what is missing when you omit the flag, and it now
rejects a name outside the vocabulary rather than letting the build find it.
The vocabulary is `content/themen.json`, and that file is the `Themen`
multi-select in Notion written out — **a new topic is added there, not in a
script.** → [The topics](#the-topics-and-the-one-word-notion-cannot-hold)

The post file is six lines and readable on its own:

```
datum:   2026-08-07          required, YYYY-MM-DD. Sorts the archive.
autor:   Henry Beiker        optional. Only the lead card has room to show it.
minuten: 3                   optional. Reading time, as the cards state it.
themen:  Energie             required. One or more names from
                             content/themen.json, comma-separated. The chips on
                             the archive and the links under the finished article.
titel:   Neue Anlage …       required, German.
title:   New plant …         required, English.
bild:    anlage-konstanz.jpg optional. A file in
                             design-system/assets/img/news/; it becomes the
                             card's picture and the article's title plate.
```

Deleting a post is deleting its file and building again; nothing else has to be
tidied up after it — including the last post on a topic: that topic's page is
removed with it, and so is every link into it. Three pages carry those links —
the chips on `patterns/news.html` and on `patterns/news-thema.html`, and the tag
list under the text on `patterns/blog-artikel.html` — and `build-news.py` writes
all three, because a topic page exists only while a post carries the topic and a
link to one typed by hand is a 404 waiting for the day it does not. **Do not
edit the archive in `patterns/news.html`** — the four regions fenced by
`<!-- news:… -->` are output, and `build-news.py --check` fails in CI when they
drift from `content/news/`.

### The topics, and the one word Notion cannot hold

The chips on the archive are the options of the **`Themen`** multi-select on the
Notion database, and nothing else. `scripts/sync-news-notion.py` writes them into
`content/themen.json` on every run — which topics there are, what they are
called, and the order they stand in, so dragging an option above another moves
its chip — and `build-news.py` draws a chip for each one a post actually carries,
with a page and a set of links behind it. **Adding a topic is adding an option in
Notion.** It used to be a code edit here, which meant an admin could invent a
topic, tag a post with it, and get a red build whose fix was a pull request.

```json
{ "slug": "telemetrie", "de": "Telemetrie", "en": "telemetry" }
```

`slug` is the address the topic is read at — `/news/thema/telemetrie` — so
renaming a topic in Notion moves its page. `en` is **the one field a person
writes**, because a multi-select option is a name, an id and a colour and there
is nowhere in it for a translation. Write the English word *as it stands inside a
sentence* — “8 posts on telemetry” — and the chip is the same word with a capital
(`Telemetry`); one string, so the chip and the sentence under it cannot end up
about different subjects.

A topic invented in Notion arrives here with `en` empty. Nothing breaks: a topic
no post carries draws no chip, and every sync says the word is missing. The build
stops the day a **published** post carries it, rather than shipping a German chip
and a half-German sentence into the English edition — so the window to write it
is between inventing the topic and publishing under it.

### The text, and the page it becomes

Everything after the header's blank line is the post's text, **in both
languages, divided by `--- en ---` on a line of its own**:

```
titel:   Wärmepumpen im Winter …
title:   Heat pumps in winter …

Der erste Absatz ist der Lead — er steht größer.

## Eine Zwischenüberschrift

Text. `**fett**`, `` `code` `` und [Links](news.html) gehen im Absatz,
`- ` ist eine Liste und `1. ` eine nummerierte.

--- en ---

The first paragraph is the lead — it is set larger.

## A section heading

Text.
```

**Pictures** are written the same way: `![Bildunterschrift](news/datei.jpg)`, on
a line of its own. The file lives in `design-system/assets/img/news/` and is
drawn as a full-width plate with its caption under a hairline. The caption is
required — it is also what stands in for the picture for a reader who cannot
see it, which is why the `<img>` carries `alt=""` and not a repeat of the same
sentence. `scripts/check-content-images.py` holds the file to the plate it is drawn
on: **1008–2016 px wide, under 800 kB**, no dangling reference, no file left
behind by a post that is gone.

A post with text gets its own reading page — `beitrag-<name>.html`, in both
editions — and its card in the archive links there. `scripts/build-articles.py`
writes it by splicing the text into the regions of `patterns/blog-artikel.html`
fenced by `article:…` comments, so the nav, the consent banner, the article
furniture and the footer are that page's, not a copy of it: **change the reading
surface once, on the specimen, and every published article has it.** The
contents rail on the left is built from the `##` headings.

A post **without** text is a listing and stays one: its card is drawn as a
`<span>` rather than as a link, because a card that opens somebody else's
article is worse than a card that opens nothing. Eighteen entries carried over
from the mock-up are in that state — they are a headline and a date, and nothing
was ever written behind them. Writing the text is what turns any of them into a
page; nothing else has to change.

`blog-artikel.html` itself stays hand-written. It is the specimen of the reading
surface and it carries the isometric figure, the plot, the table and the pull
quote that the markdown above cannot express.

### …or write it in Notion

`scripts/sync-news-notion.py` imports the archive from a Notion database into
those same files, and `.github/workflows/news-sync.yml` runs it hourly, rebuilds,
and pushes the result through the same gate every other change goes through. The
admin's loop is then one place: write the post, set **Status** to
`Veröffentlicht`, and it is on the site within the hour.

**The database exists**: [News (Website)](https://app.notion.com/p/3b52e8e3987781138144cfea278747d8),
under *Branding / Marketing*, seeded with the eighteen posts that were already in
`content/news/`. Its eight properties are the ones the script reads:

| Property | Type | |
|---|---|---|
| `Titel` | Title | the German headline |
| `Title` | Text | the English headline — required, the site ships twice |
| `Datum` | Date | sorts the archive |
| `Themen` | Multi-select | **required.** One or more. Its options *are* the archive's filter — the sync writes them into `content/themen.json` and the chips follow, so a new topic is a new option here. A post filed under nothing is a card the topic filter cannot place, and the build refuses it. → [The topics](#the-topics-and-the-one-word-notion-cannot-hold) |
| `Autor` | Text | optional; only the lead card has room to show it |
| `Minuten` | Number | optional; reading time |
| `Titelbild` | Files | optional; the card's picture and the article's title plate. The sync downloads it (Notion's URLs expire within the hour), fits it to the plate and names the file after the digest of the bytes it stored. Upload it here and nowhere else — this property is where a post's picture comes from, and an empty one means the post has none. `scripts/news-objects/` draws the isometric plates on request; what it exports is uploaded by hand |
| `Status` | Select | `Entwurf` → `In Review` → `Veröffentlicht`; only the last is imported |

**What you write inside the page is the article.** German text, a **divider
block** (type `---` in Notion), then the English text — the same convention the
post file carries, because the sync writes one into the other. Paragraphs,
headings, bulleted and numbered lists, bold, code and links come across; a
quote or callout arrives as a paragraph; anything with no form on the reading
page — an embed, a table, a video — is left out and named in the run's log. A
page with no text at all is a listing in the archive and gets no page of its
own, which is a legitimate state and not an error.

**Pictures**: drop an image block into the page and **write a caption on it**.
The sync downloads the file into `design-system/assets/img/news/` and the post
points at it there — a Notion file URL is signed and expires within the hour, so
a page that linked to one would show a broken image by lunchtime. The caption is
not optional: it is printed under the picture and it is what a reader who cannot
see the picture gets instead.

Put the image in **both halves** — copy the block below the divider and write
its caption in English. Each edition carries its own caption; the file is
downloaded once either way, and the build fails if one half has a picture the
other does not. Keep it between **1008 and 2016 px wide and under 800 kB**
(the plate it is drawn on is 1008 px); `scripts/check-content-images.py` states
the numbers and fails the sync's pull request if a photograph misses them.

What is left is two secrets, under **Settings → Secrets and variables → Actions**:

    NOTION_TOKEN     the website_news integration's secret
    NOTION_NEWS_DB   3b52e8e3-9877-8113-8144-cfea278747d8

Until both secrets exist the workflow exits quietly rather than failing hourly.

**Notion wins once it is connected.** The sync makes `content/news/` match what
the database publishes, so a post written with `new-post.py` and not present
there is *removed* on the next run. Pick one source. There is a floor under the
deletions — a sync that would remove most of the archive stops and asks for
`--force`, because that is what a wrong database id or a renamed Status looks
like from the script's side — but the rule still holds.

`--dry-run` says what would change without touching anything, and `--fixture
FILE` runs the whole transform against a saved API response, which is how it is
tested without a token.

Reasoning, and what is deliberately *not* generated, is in the header of
`scripts/build-news.py`.

## Advertise a position

The same pipeline, one register over. `content/jobs/` holds one file per
opening; `scripts/build-jobs.py` writes the register on `patterns/karriere.html`
— the entries and the "4 offene Stellen" in the header, which
`scripts/check-register-count.py` has always held to each other — and
`scripts/build-stellen.py` writes `stelle-<name>.html` for every opening that
has an advertisement behind it, in both editions, by splicing it into
`patterns/karriere-stelle.html`.

**An opening with text gets a page; one without stays a listing** whose title
links to its own row on the register. That is not new behaviour: `karriere.html`
shipped exactly that for three of its four entries, with its own note that a
link to a page which does not exist is the thing that must not ship.

The file is the record, and everything a reader sees is a pair:

```
kennung:    CF-2026-DE-01            the reference that goes in the subject line
bereich:    Plattform                area / Area
bild:       jobs/werkshalle.jpg      Titelbild — optional, the square at the row
titel:      {Data Engineer} (m/w/d)  title / Title
anriss:     Sie bauen die Strecken … excerpt / Excerpt — the register's two lines
standort:   Konstanz, hybrid         location / Location  ┐
anstellung: Festanstellung           employment           │ the register's
umfang:     Voll- oder Teilzeit      hours                │ four facts
start:      ab sofort                starts               ┘
adresse:    Am Seerhein 6, …         address   — optional, the long form
verguetung: 58.000–72.000 € …        salary    — optional
gehalt_von: 58000                    gehalt_bis: 72000    — optional, for the JobPosting
art:        FULL_TIME, PART_TIME     — optional, schema.org's employmentType
seit:       2026-07-06               frist: 2026-09-30    — datePosted, validThrough
```

**The braces in a title are not a typo.** `{Data Engineer} (m/w/d)` is two
languages in one line: the braces mark the English run, so the German page wraps
it in `lang="en"` and the English page drops them. WCAG 3.1.2, and the rule
`karriere.html` has carried in a comment since it was written.

The text after the header is the advertisement, in both languages divided by
`--- en ---`, in the same grammar a post uses: the paragraphs before the first
heading become **Die Aufgabe**, and each `## heading` and its list becomes one
block of **Ihre Arbeit und was sie voraussetzt**.

**The square at the row**: a `Titelbild` files property in the Stellen register
syncs to a `bild:` line and downloads into
`design-system/assets/img/jobs/` — the register row draws it as a square,
decorative and unlinked, because in this component the title is the only link.
It is the one field that is not a pair: there is no English twin, both editions
draw the same file. And it is drawn only on the register — the job page never
shows it. Same plate as a news picture (`scripts/check-content-images.py`
states the numbers), and optional: an opening without one is the row the
register has always drawn.

**The JobPosting block is generated with the page** — title, identifier, dates,
employment type and salary all from the same fields the visible page is drawn
from, because a structured-data block that says one thing while the page says
another is the one error a reader cannot see and a search engine acts on.
`scripts/check-job-posting.py` holds them to each other, and its "one URL per
opening" rule is why `karriere-stelle.html` now carries a *Musterausschreibung*:
it is the template, not an opening.

### …or write it in Notion

`scripts/sync-jobs-notion.py` imports the register from a second Notion
database, and the hourly workflow pulls both stores in one run.

**The database**: [Stellen (Website)](https://app.notion.com/p/3b62e8e3987781e685a0e8e04b83f118),
under *Hiring*, seeded with the four openings that were already in the register.
Its properties are the fields above, German and English side by side, plus
`Status` (`Entwurf` → `In Review` → `Veröffentlicht`). Write the advertisement
inside the page — German text, a **divider block**, then the English text.

One more secret, beside the two the news sync uses:

    NOTION_JOBS_DB   3b62e8e3-9877-81e6-85a0-e8e04b83f118

Each store is configured on its own: with only `NOTION_NEWS_DB` set, the job
step is skipped rather than failed on.

**A filled position leaves Notion and leaves the site.** Pull it out of
`Veröffentlicht` and the next sync removes its file, its register entry and its
page. An empty result stops the sync instead — the zero state is
`karriere-leer.html`, which is written by hand — unless `--force` says so.

## Check it

```bash
python3 scripts/check-spacing-scale.py         # from the repo root
python3 scripts/check-spacing-scale.py --fix   # rewrite the table in foundations/layout.html
python3 scripts/check-gradient-family.py       # the light family, in every shipped SVG, stylesheet and emitted ramp
python3 scripts/check-gradient-family.py -v    # list every gradient, not only the failures
python3 scripts/check-gradient-angle.py        # the angle each one is raked at, resolved through its transforms
python3 scripts/check-gradient-angle.py -v     # print the whole rake register, gradient by gradient
python3 scripts/check-wash-derivation.py       # the page wash's three stops, re-derived from the palette
python3 scripts/check-wash-derivation.py -v    # print the whole derivation, stop by stop
python3 scripts/check-ramp-ink.py              # every ramp step's label ink, recomputed from the swatch under it
python3 scripts/check-ramp-ink.py -v           # every step, its two ratios and the ink it takes
python3 scripts/check-iso-motion.py            # the isometric assembly's invariants
python3 scripts/check-motion-census.py         # the motion chapter's token census is the stylesheets' count, and every curve is a token
python3 scripts/check-motion-census.py --fix   # rewrite the count cells in foundations/motion.html
python3 scripts/check-glass-budget.py          # what backdrop-filter is allowed to cost
python3 scripts/check-glass-budget.py --fix    # rewrite the census in foundations/materials.html
python3 scripts/check-glass-budget.py -v       # list every page, not only the ones carrying glass
python3 scripts/check-glass-solid-edge.py      # when glass goes opaque, its edge turns over with it
python3 scripts/check-glass-solid-edge.py -v   # list every tier and surface examined, not only the faults
python3 scripts/check-card-fill.py             # a card is a contour, and its one fill goes inside
python3 scripts/check-card-fill.py -v          # list every background read on a card, not only the findings
python3 scripts/check-grid-tracks.py           # every fr track has a floor
python3 scripts/check-grid-tracks.py -v        # list every track list, not only the failures
python3 scripts/check-breakpoints.py           # every threshold is in the register, in rem
python3 scripts/check-breakpoints.py -v        # list every threshold, not only the failures
python3 scripts/check-fluid-crossovers.py      # every width a clamp swaps arms at is published
python3 scripts/check-fluid-crossovers.py --fix  # rewrite the census in foundations/layout.html
python3 scripts/check-fluid-crossovers.py -v   # every declaration read, and every one deliberately not
python3 scripts/check-demo-fold-band.py        # each framed demo is documented at the fold it actually answers to
python3 scripts/check-demo-fold-band.py -v     # every fold rule and every subdivision call site
python3 scripts/check-overflow-clip.py         # a crop is a crop, not a scroll container
python3 scripts/check-overflow-clip.py -v      # list every overflow declaration, not only the failures
python3 scripts/check-cut-edge.py              # a crop that hides a column says which edge is hiding it
python3 scripts/check-cut-edge.py -v           # every inline crop in the shipping tree, marked or exempt
python3 scripts/check-highlight-fill.py        # every highlight states its ink as a fill, so a clip cannot erase it
python3 scripts/check-highlight-fill.py -v     # list every highlight rule, not only the failures
python3 scripts/check-line-types.py            # every dash pattern is one of the four line types
python3 scripts/check-line-types.py -v         # list every dash pattern, not only the strays
python3 scripts/check-cap-line.py              # every text-box trim states both edges, inside its @supports branch
python3 scripts/check-cap-line.py -v           # every trim, and the context it sits in
python3 scripts/check-cap-line.py --fix        # rewrite the census in foundations/capline.html, and the code example under it
python3 scripts/check-merge-markers.py         # no file in the tree carries a conflict marker
python3 scripts/check-morph-pairs.py           # both halves of every page-to-page morph are present
python3 scripts/check-morph-pairs.py -v        # the register, and every pair it walked
python3 scripts/check-links.py                 # every reference resolves on the host that serves it
python3 scripts/check-job-posting.py           # the JobPosting block matches the posting the reader sees
python3 scripts/check-a11y.py                  # the accessibility facts that are arithmetic rather than judgement
python3 scripts/check-class-provenance.py      # every class in the markup is declared by something
python3 scripts/check-class-provenance.py --report  # the census: who declares what, and what is written twice
python3 scripts/check-anatomy-provenance.py    # every class a chapter's anatomy table names is one something declares
python3 scripts/check-anatomy-provenance.py -v # every class mention read, and where it resolves
python3 scripts/check-markup-answered.py       # nothing in the markup writes into a void
python3 scripts/check-markup-answered.py -v    # the counts, and the gaps parked in KNOWN
python3 scripts/check-viewport-zoom.py         # no page revokes the reader's pinch zoom
python3 scripts/check-local-thresholds.py      # every page-local threshold is registered, and in rem under patterns/
python3 scripts/check-local-thresholds.py -v   # print the register
python3 scripts/check-stack-layers.py          # the front door's six planes, and the one that is lit
python3 scripts/check-stack-layers.py -v       # print the stack: every plane, its place and its route to the light
python3 scripts/check-faq-count.py             # the counter above an accordion counts its rows
python3 scripts/check-faq-count.py -v          # every accordion, counted or skipped, and why
python3 scripts/check-section-header-rule.py   # a flush section header stands over something that draws the rule it gave up
python3 scripts/check-section-header-rule.py -v # every flush header, and what draws its edge
python3 scripts/check-illustration-source.py   # the four process objects are still the designer's vectors
python3 scripts/check-illustration-source.py -v  # every element, matched or deviated, and why
python3 scripts/check-figure-roster.py         # the two chapters that census the isometric figures count the tree
python3 scripts/check-figure-roster.py --fix   # rewrite the assembly roster in foundations/motion.html from the tree
python3 scripts/check-readme-check-count.py    # the count above this block is the length of this block, and scripts/README.md's two are the directory
python3 scripts/check-readme-check-count.py --fix  # write all three from what is on disk
python3 scripts/check-readme-check-count.py -v # every number, and everything counted for it
python3 scripts/check-count-atom.py            # a section head taken off the label ramp keeps its counter in one piece
python3 scripts/check-count-atom.py -v         # every section header row, and the ramp it is on
python3 scripts/check-docs-caption.py          # the caption under a demo tile is one device, not twenty
python3 scripts/check-docs-caption.py -v       # every caption rule read, and whether it is a copy
python3 scripts/check-field-family.py          # every field control is accounted for in the family's shared rules
python3 scripts/check-field-family.py -v       # every shared rule and the controls it names
python3 scripts/check-hover-focus-parity.py    # a response written for :hover is written for :focus-visible in the same rule
python3 scripts/check-hover-focus-parity.py -v # every :hover rule, paired, exempt or stray
python3 scripts/check-foil-clip.py             # the foil's clip box is capped at its ink, every exclusion from the cap is answered, and no box property takes fit-content()
python3 scripts/check-foil-clip.py -v          # every declaration considered
python3 scripts/check-foil-doors.py            # every gradient in the letters hands its ink back on paper, under forced colours and for more contrast
python3 scripts/check-foil-doors.py -v         # every clipping context, every state, every door
python3 scripts/check-forced-texture.py        # no forced-colours rule fills a texture's box with an ink, which is a slab where the drawing was
python3 scripts/check-forced-texture.py -v     # every textured subject and the forced-colours answer it was given
python3 scripts/check-lime-flat.py             # every flat lime area sits on one of the light layer's four boundaries
python3 scripts/check-lime-flat.py --fix       # rewrite the census in foundations/light.html
python3 scripts/check-lime-flat.py -v          # every area paint examined, and the argument that covers it
python3 scripts/build-i18n.py --check          # the English edition matches its German source
python3 scripts/build-i18n.py --extract        # every German string with no entry in the catalogue
```

**The English edition** under `patterns/en/` is generated, not written:
`scripts/build-i18n.py` builds it from the German pattern beside it and replaces only the
words, from `i18n/en.json`. Nothing else is duplicated — markup, classes, comments, ids
and page-local `<style>`/`<script>` come through byte for byte — and none of the checks
above read it, because every fact they keep is already kept one directory up. Add copy in
German; run `--extract`; translate what it prints; rebuild. A German string with no entry
fails the build rather than shipping a German sentence in an English page.

The forty-three checks the system enforces rather than documents, run by CI on every push and
pull request — one job, because each is a few hundred milliseconds of stdlib python.
Stdlib only: they do not give the system a build step. The count is one of them:
`check-readme-check-count.py` reads this sentence and counts the block, because the number
had gone stale three times — every time as a correct change by a lane that could not see
the other one landing the same day. It went stale a fourth time an hour after that was
written, and the gate caught it. **The same claim one directory over had no gate**:
`scripts/README.md` opens on a file count and carries a `check-*.py` row, both about the
directory it sits in, and both were two behind. They are derived from the directory now,
by the same script.

**And a gate that only reports is a gate somebody has to satisfy by hand every time, which
for this trio is every time any lane adds a check.** Two of its three numbers live in
`scripts/README.md` — a file a lane adding a check has no reason to open — so the pair went
two behind again within the hour, three lanes deep, with the gate red on `main` and each of
those three changes correct on its own. The finding text had been saying so since it was
written: *"it was corrected an hour before it went stale again, by a lane that had no reason
to look at it."* `--fix` writes all three from what is on disk and then re-asserts what it
wrote, the way the space scale's table and the glass census already do; nothing in the trio
is a judgement, which is the test for what may be generated rather than merely counted.

**The space scale** holds to four rules: `foundations/layout.html`'s table of who uses each
rung must match the shipping CSS, spacing in the shipping CSS must be written as a
token rather than as a length, spacing in a `style` attribute must be written the same way,
and neither `.stack` nor `.cluster` may carry one at all. The table in that page is
**generated** — run `--fix` rather than editing a count by hand.

**The third and fourth were added because the rule stopped at the stylesheet door.** A
`style` attribute is the one place a distance can sit where no reader of a stylesheet meets
it, and no gate in `scripts/` was looking. Across every page here that is not a generated
mirror: **114 spacing declarations inside `style` attributes, 88 of them `0` or `auto`, 26
live distances, and not one of them on a page under `patterns/`.** That last number is the
tell rather than the reassurance: `check-local-literals.py` already stands over `patterns/`
and narrows inline `style=` there to custom properties only, so the shipping pages were
clean because something was reading them. Everything else in this directory —
`components/`, `foundations/`, `prototypes/` — had no reader at all, and it is where the
overrides collected. That is the worse half to leave open, because the documentation is the
copy a reader learns the system from. In it: five
values off the scale (`padding-bottom: 8rem`, and a `margin-top: 1rem` that is `--space-4`
spelt as a length), two `gap: 1px` seams on `.docs-swatch-row` — a class that was a name in
the markup and a rule nowhere — one `gap: var(--space-8)` on an element declaring `.stack`
and then overriding its display, and **four `margin-top: var(--space-8)` on `<h3>` elements
of `foundations/layout.html` itself**, the chapter that publishes the scale, each one a
restatement of what `.docs-section > h3` already says. Measured in Chromium at 1280: 32 px
with the attribute, 32 px without, four times.

The ban is total on `.stack` and `.cluster` and partial everywhere else, and the asymmetry
is the argument. Those two resolve their spacing through `--flow` and the `.flow-*` rungs,
so an inline gap there does not sit beside the system's answer — it overrides it. Elsewhere
a one-off distance on an anonymous element inside a demo is honestly written where it
lands, and a class per demo would be the scale reaching past what it governs. The line is
repetition: a distance written twice is a rule, and a rule belongs in a stylesheet under a
name. → `foundations/layout.html#space-in-markup`

**The light family** holds every `<linearGradient>` and `<radialGradient>` the site ships
to one ramp. SVG has no `in oklab`, so a drawing that carries the family's ramp carries
the oklab path by hand: one waypoint at 19 % of the lime leg, coloured at the oklab path's
value there. The script recomputes both — the offset from the leg's own two ends, the
colour from the path — so `#DBFC60` and `#E6FF66` are re-derived rather than compared
against a list, and it also catches a stop that is *almost* a chromatic brand colour, which
is how `#E0FF02` gets in. `assets/source/` and `prototypes/` are out of scope: the first is
the designer's own material and the second is unshipped, and both carry raw Figma exports
on purpose.

**The other half of the family is in CSS,** and it went unchecked for as long as the script
existed. Two more conventions live in `tokens.css` as prose over literals nobody can
recompute by eye, and both are checked now, in the three shipping stylesheets:

| | |
|---|---|
| **the arc** | Every leg that *turns* carries one waypoint at its own OKLCh midpoint. A waypoint is recognised by **being** that midpoint rather than by appearing on a list, so `#B9E3EB`, `#B8CCF3`, `#33494E` and `#273650` are re-derived on every run — the same standing `#DBFC60` has. A leg that turns and carries nothing is a chord and fails. |
| **the path** | A ramp carrying a **lime** leg exists somewhere with `in oklab`. lime → Glas is ΔEok 0.0443 between the two paths where every other leg in the family is under 0.0015, which is why `--glass-edge` and `--sheen-panel` are left in sRGB by name and the lime legs are not. |

What the arc does *not* govern is where the second rule gets its scope. A leg touching lime,
CF-Grau or Weiss is a **falloff** — light's source and what it falls away to — and oklab's
straight line is already its correct path. Only what happens in the band between them turns.
The premise is not just "chromatic at both ends": lime at C 0.2201 against Glas at C 0.0414 is
a radial move, and the polar path through it bows out to `#A8FFB6`, a green in no palette at
three times the chroma of the stop it is travelling to.

**The arc used to stop at the first translucent stop, and that exemption hid a defect the size
of the one the arc exists to fix.** `--glass-edge` — the lit rim of every glass sheet, drawn the
full width of the navigation bar and across the hero button's plate — runs Glas into Sky at 0.42
and 0.28 alpha: chromatic at both ends, 64.6° of hue, no waypoint. The gate let it through on the
grounds that *what a translucent stop renders as depends on what is behind it*, which is true of
the colour and false of the **path**. A gradient interpolates premultiplied, so over any fixed
backdrop the pixel is `lerp(C₁a₁, C₂a₂) + bg(1 − lerp(a₁, a₂))` — affine in *t*, a straight line
between the two composited ends on every surface it is ever drawn over. The chord is a fact about
the stop pair; only its size moves with the backdrop, never its sign. Chroma at the midpoint sags
**16.9 %** over CF-Grau, 20.1 % over Weiss and 22.4 % over Schwarz in the inverse theme, against
the 16.0 % the foil's own Glas → Sky leg was corrected for. Both variants of the edge carry their
waypoint now, computed the way CSS Color 4 interpolates a polar space — rectangular components
premultiplied by the two alphas, hue at a plain half, alpha the mean — which is what
`color-mix(in oklch shorter hue, …)` returns for the pair and what two opaque ends reduce to with
weights of a half, so the four hexes above are re-derived by the same expression unchanged.
Rendered: chroma at the midpoint up 26.6 %, both endpoints byte-identical, and 4 levels at most
on one row of the two designed pages.
→ `foundations/colors.html#the-arc`

**The one member both rules exempt is the largest gradient in the system,** and it needed a
check of its own. The page wash is the reversed foil at chroma 0.005, so it carries no lime
leg and nothing for an arc to bow out of — `check-gradient-family.py` exempts it on both
counts, correctly, and therefore reads `#CFCFD2`, `#E1E4E7` and `#F3F8F7` as data. They are
not data. Each is `oklch(L, 0.005, h)` where `L` is the neutral ramp's own lightness at that
stop's position and `h` is the foil hue being reversed, and `tokens.css` says so and then
names the trap: *"they are literals, so they do not follow `--cf-grau`. Move CF-Grau and these
must be recomputed or the wash quietly stops starting where the page starts."* Nothing ran
that paragraph. `check-wash-derivation.py` does — it re-derives all three from `--cf-grau`,
`--cf-glas`, `--sky-300`, `--violett-300` and the foil's own stop positions, holds the
lightness path to the neutral ramp it claims to be identical to, holds the chroma to the grain
that sets its ceiling, and recomputes the hue travel against the lit foil's own stops rather
than against the number in the prose. It pairs with `check-hero-scrim.py` in the opposite
direction: that one holds the hero's scrim tint *to* the wash, this one holds the wash to the
palette.

The second rule had already been broken. `.cf-btn--glass` drew Glas into lime on the sRGB path
with no `@supports` branch — the only lime ramp in the system's CSS never put on the family's
path, at ΔEok 0.03866 composited over CF-Grau, seventy-nine times the divergence of the
`--glass-edge` layer directly above it that the family deliberately declines to correct. Its
stops are a custom property now and only the path changes.

**Each of the gate's two rules had only ever seen half the tree, and it is the same gap read
twice.** The SVG rule was written for *the lime leg*, and the family has two falloff sources:
`.cf-plot__col--fell` draws Violett → `#8A94E3` → Glas → CF-Grau on the evidence plot's two
falling columns, on the Landing Page and not only on the component page. Every number in it is
the lime ramp's — the near rake's Glas at 0.32, CF-Grau at the rim, the waypoint at 19 % of the
leg on the oklab path — and none of them was re-derived by anything, which is exactly the
standing `#DBFC60` had before this gate existed and exactly how Expertise came to paint the mid
rake's offset on four near-rake objects. The ARC rule was stated for *every gradient the site
ships* and applied to the CSS quarter of them; the wallpapers and the Landing Page draw five
turning legs in SVG that nothing had read. Both halves are gated now, and the arc had to learn
one thing to cross over: an SVG writes its source waypoint *inside* a leg, so those stops come
out before the arc looks, or a three-stop ramp presents it with two sub-legs and demands a
midpoint in each for ever.

**Closing the second gap turned up a defect in the first.** The arc decided *turn* versus
*falloff* by naming lime — an enumeration of the sources that existed when it was written.
Violett → Glas names no lime, so the old test called it a turn and would have demanded its polar
midpoint, `#74C1E6`: a vivid sky blue at twice the chroma of the stop that leg travels to, in no
palette in this brand, and the `#A8FFB6` failure the lime case is documented with one source
over. The premise was never the endpoints. It is that *two stops of similar chroma sit on roughly
the same circle about the neutral axis* — so the test is now the ratio of the two ends' chroma,
and every leg the family draws answers it with a gap between 2.37 (Glas 800 → Sky 800, the
narrowest turn) and 3.50 (Violett → Glas, the widest falloff). The ceiling is 2.88, the geometric
mean of that gap. An achromatic end has chroma zero and no finite ratio, so *no waypoint on a leg
that ends in grey* falls out of the same arithmetic rather than standing as a second clause: two
rules become one, and no shipped gradient changes classification.
→ `foundations/colors.html#the-arc`

**Both of those settle what a gradient is made of. Nothing settled which way it runs**, and
the brand states that law as squarely as it states the ramp: *the only sanctioned angles are
26.57, 45, 63.43 and 90 degrees.* A gradient is light crossing a surface, so it is spatial by
the same definition the drawings are, and those four close under direction into sixteen.
`check-gradient-angle.py` resolves what every gradient in the shipping tree actually paints
at — 222 in SVG, 80 in CSS — and every one of them is on the set today.

**It has to be a gate rather than a reading, because a gradient's angle is not written in the
file that declares it.** `#cf-ex-01` reads 52.02° off its own coordinates; painted, it runs at
exactly 180° — straight down — because a `userSpaceOnUse` paint server resolves in the user
space the *referencing* element establishes, and that ellipse carries `rotate(127.98)`. The
declaration and the paint are 128° apart and both are correct. That is not hypothetical:
`isolib.py` records the same mechanism shipping wrong in the same place, found by rasterising
the page and reading pixels back — *"the lightest pixel of this object's light sat 68 % of the
way DOWN the disc"* — because nothing static could see it. The check resolves the transform
chain, so the number it reports is the one a reader sees.

The two exemptions are **derived, not listed**: process cards 01 and 03 paint at 151.26° and
130.04°, and card 04's two orbits at 63.31° and 332.48° — a tenth and a degree off the brand
angles beside them — because `01-discovery.svg`, `03-weniger-ausfaelle.svg` and
`04-mehr-leistung.svg` carry exactly those vectors. The material wins, so the script reads the
source and accepts what it finds there rather than carrying four numbers' worth of folklore.
Three things it *cannot* read it names on every run instead of passing in silence: a paint
server chosen by a selector (`.map__fill`), an `objectBoundingBox` vector that is diagonal, and
`--foil-angle`, which is the swing.
→ `foundations/colors.html#the-rake-register`

**A gradient in the letters is a solid colour at every door,** and the third door was not
there. A clipping context — `background-clip: text` with the fill transparent, which is
`.text-foil` and the black button's label — hands its ink back on paper and under forced
colours, and both of those are limitations. `prefers-contrast: more` is a request, and no
rule in the four shipping stylesheets read it: a reader who had set it was handed the ink
foil at its 5.24:1 floor on the page's own grey where solid ink is 13.48:1. Both contexts
answer it now with the solid ink of their surface, and `check-foil-doors.py` holds every
clipping context to all three doors **in every state it clips in** — which is how it found
that the button's two older doors were written for the resting button only, and were beaten
on hover by the rule that restates the clip at a higher specificity. That never showed,
because the fill each door hands back happens to be declared later in source than the
transparent one; a label legible by source order rather than by statement is the dependency
the button's own comment names as the way this bug comes back.

**And the cap that makes a foil a foil had an exclusion nothing measured.** `background-clip:
text` paints across the WHOLE element box, so a headline in a column samples only the first
fraction of its ramp — `base.css` says so, calls it load-bearing, and caps `.text-foil` at
`max-width: max-content`. The cap is written `:not(:has(.cf-stream__text))`, because
`cf-stream.js` empties the element it types into and capping a rewritten element at its own
content is cyclic: measured, that collapsed all four card titles on `patterns/expertise.html`
to 22 px and 0. **The reason is right; what the excluded case then renders was never looked
at.** Those four titles are the four largest foil moments in the system, and on the rendered
page they sat 136–406 px of ink inside a 518 px box at 1280 and a 593 px one at 1920:

| | ink / box at 1280 | at 1920 |
|---|---|---|
| Maschinenbau | 53.4 % | 46.6 % |
| Erneuerbare Energien | 78.4 % | 68.4 % |
| Großanlagen | 47.0 % | 41.1 % |
| Flotten | 26.2 % | 22.9 % |

Against `--gradient-foil-ink`, whose stops sit at 0 / 23.5 / 47 / 73.5 / 100 %, **Violett 800
appeared on none of them at either width**, and at 1920 two of the four did not reach Sky 800
either — the same sentence `base.css` records for the footer title *before* the cap existed,
printed by the exemption instead of by a missing declaration.

**So the stream hands the axis back before it takes it.** The full string is still in the
element when `prepare()` runs, so its `max-content` is the real one; `cf-stream.js` publishes
it as `--stream-inline` and the excluded rule caps on that. Nothing is cyclic — the
measurement happens once, before the first character is removed — and the ramp is then fixed
at the *full* string's width for the whole of the typing, so it does not rescale letter by
letter either, which is the other failure the class names. It is published in `em` because
`prepare()` runs once per gate flip and not once per resize, and the same string in the same
face scales with its own font-size. The caret is inside the measurement rather than named as
`0.55em` in a second file: it is a real inline-block in the flow, and a box capped at the ink
alone drops it to a second line the moment the line finishes typing. That is the whole of the
residual — the four now run **86.1 % to 94.9 %** of the ramp instead of 22.9 % to 78.4 %, all
four cross the Sky → Violett waypoint at 73.5 %, and the violet leg renders. Contrast only
improves: the stops this exposes are the ramp's darkest, 7.12:1 and 8.53:1 on CF-Grau against
the 5.24:1 floor at Glas 800 that was always painted.

`check-foil-clip.py` asks a third question now, and it is the general form of the first two: an
exclusion has to be answered by a cap of its own, that cap has to clamp at the available space
with its own term rather than with a `var()` fallback that only looks like one, and every
custom property it caps on has to be written by a shipping script. A cap on a var nothing sets
is `max-width: 100%` wearing an argument — a value no engine implements and a value nothing
supplies fail the same way, and neither leaves a mark.

**The isometric assembly** holds to seven rules, all of which were already written down in
prose and none of which anything ran:

| | |
|---|---|
| `--iso-travel` | Every figure that assembles travels `viewBox width / 40` — 2.5 % of its own drawing — resolved the way the cascade does: inline styles, then the component-keyed rules in `components.css`, then the `:root` default. |
| `--iso-orbit-travel` | A whole multiple of the `--dash-1-4` period, or every orbit settles off the phase the source vector drew. |
| `pathLength="1"` | On every `.cf-iso__trace`, and `non-scaling-stroke` on none of them. The trace is a retired layer — this holds the ones already drawn. |
| `.cf-iso__orbit` | Always carries `.cf-iso__ghost` too — an orbit is a ghost that also turns, and the shared rule names the ghost. |
| one light | At most one `.cf-iso__light` per object. |
| `screen` | Every `animation-timeline` declaration sits inside a `@media` that names `screen`. |
| `--build-stages` | Every `.cf-iso--build` declares the deepest `--stage` it actually draws, and the light and the construction points wait for *that* rather than for the plate the lime is painted on. → [the object, not the plate](foundations/motion.html#light-object) |

Every one of the seven is invisible in a screenshot and countable in a file, which is the
whole test for what belongs in any of these four — and the reason two of the four in
[Redrawing an illustration](#redrawing-an-illustration-five-things-that-vanish-quietly)
are deliberately left out.

**The glass budget** holds `backdrop-filter` — the most expensive thing in the stylesheet —
to what `foundations/materials.html` states in prose and nothing ran. Three claims: at most
two blurred layers composited at once on a shipping page, every `backdrop-filter` reading `var(--glass-blur)`
rather than its own radius, and no `animation` or `animation-timeline` on a rule that
declares one. All three pass the same test: a third blurred layer renders perfectly and
simply costs more, on the hardware least able to afford it. The page's own census was a
sentence naming its own problem two paragraphs later — *a count somebody has to remember* —
and is a generated table now, with a stamp, the same way the space scale's is.

**A fourth claim is about the fallbacks, and it is the one that is not about cost.** The
three blocks at the foot of `tokens.css` turn the material off — the browser cannot blur,
the reader asked for less transparency, the reader chose the palette — and they do it by
redefining tokens rather than by giving every component a branch of its own. That buys a
great deal and has exactly one failure mode: a tint left out of one block keeps its live
value there, and whatever reads it keeps a material the block was written to take away.
Nothing renders wrong; it renders as though the reader had never asked, and with the blur
already gone what comes through the surviving translucency is **sharp** — worse than either
the material or a flat plate. The file's own comment already stated the invariant for one
axis of this (*repeat every token the inverse block declares, not just the ones that
differ*) and the other axis was broken: `--surface-glass-thin` sat out the forced-colours
block entirely, so the Expertise lectern was the one glass surface in the system still
translucent in that mode, measured at `rgba(255, 255, 255, 0.30)` with the blur already
`none`. The check now asserts that every block turning the material off turns *all* of it
off, in every selector it names, excusing only a token the block reads as its own answer —
`--surface-glass-solid` is two blocks' answer and cannot be redefined in terms of itself.
The family is a name shape rather than a roster, so a fourth tint is in scope the moment it
is declared. The lit edge is deliberately outside it: an edge is a contour, not a
translucency, and forced colours recovers it as a border next to the rule that draws it.

**It survived because the tint was the one tint nothing drew.** `--surface-glass-thin` was
declared, documented and reached for by `patterns/expertise.html`, and no page rendered it —
so no screenshot of any fallback ever contained it. `.material-glass--thin` is that plate,
and it stands on `.cf-ground` rather than on the poster the other two samples use, because
the backdrop is the demo: 30 % is what one measurement on one **named** backdrop came back
with, not a lighter look available on request.

**What counts as glass is read out of the stylesheet, not listed in the script.** It takes
the selectors of every shipping rule declaring `backdrop-filter` as the definition, so a
fourth frosted surface enters the budget by existing rather than by somebody remembering to
add it — the same reason the light-family script recomputes its waypoint instead of
comparing against a table of hexes. A selector it cannot count is a finding, never a silent
skip.

**A card is a contour, and its one fill goes inside — which is the same register read for
the panels that carry no material at all.** The glass claims bind the rows of the panel
census that name a material; a row whose verdict is the *absence* of one was bound to
nothing, and that is every card in the system. It cost three declarations, all on the
process card: `--surface-card` on the card itself, `--surface-raised` on its copy half — a
second plate in the same grey inside the first, so the two cancelled and half of it was
dead — and `--surface-lifted` on that half again, a veil argued from the mockup, which draws
the copy column as a flat plate. **Two of the three were invisible and the third was not.**
Cancelling plates render exactly like no plate, so no screenshot could hold them; the veil
was in every screenshot of the landing page for as long as it shipped, and shipped anyway,
because a measurement is a stronger argument than a sentence. `check-card-fill.py` reads
every `background` on a card or a part of one out of the shipping stylesheets, resolves it
through every custom property those files declare — a component that paints its own
`--x-bg` is painting whatever that property holds — and fails on anything computing to a
colour that is not one of three registered fills — the note's veil, the info card's frosted modifier, and the plate under
the vacancy row's photograph. A line painted as a block is not a fill and neither is a
gradient: the sheen, the rim and the dashed rules have their own gates. The ruling it
enforces is narrower than *don't fill the card*, because none of the three was on the card:
**a card's divisions are edges, so a surface on one side of an edge divides it twice, and
the fill a card may carry is a veil on a block inside one of its parts.** The roster is
hand-kept, for the reason nothing in a stylesheet tells a card from any other bordered box —
and a class whose *name* says card and is not on it fails, so the next card cannot arrive
uncovered. → `foundations/materials.html#card-fill`

**The lit rim is one geometry, and it was written out eight times.** Three glass surfaces
carry a specular that crosses their rim — the navigation sheet, the hero button, the
info-card plate — and the token comment on `--glass-rim-light` already said what they share:
*the same band, the same parking positions; only the container and the clock differ*. Each of
them stated that band and those positions for itself anyway, and then again inside a pair of
keyframes under a name of its own. Eight copies of three numbers, on three surfaces that are
never on screen at the same time, so a hand edit to one of them would have rendered perfectly
and been invisible to every reader and every check. The geometry is `--glass-rim-band`,
`--glass-rim-park` and `--glass-rim-cross` now, and the crossing is one
`@keyframes cf-glass-rim` all three name; the timeline stays local, because that is the half
that genuinely differs. **The two endpoints are re-derived rather than compared.** A
background layer positioned at `P` is offset by `P × (container − image)`, so a band `b` wide
clears the left edge only at or below `−b/(1−b)` and the right edge only at or above
`1/(1−b)` — at 40 % that is −66.7 % and +166.7 %. Widen the band without moving them and a
sliver of the specular is parked *on* the rim at rest, which is not a stray frame: the parked
position is what all four fallback doors fall back to, so it is the drawing itself. The check
fails a band that no longer clears its own box, a rim rule that writes any of the three as a
literal, and a second set of keyframes moving a rim — even one whose values are identical
today, which is exactly what the three that existed were.

**And the chapter's other table is now held to two derived sets, not one.** *Every panel, and
what it is made of* is the verdict column — for each panel: what is behind it, what it is made
of, how it responds — and it is prose by necessity, because a verdict is an argument. The
claim that binds it read only the frosted rows, so the majority of a table titled *every*
panel was bound to nothing at all, and it drifted exactly the way the census had before it was
generated: the register — `.cf-result`, `.cf-vacancy`, `.cf-event`, one rule behind the search
results, the open positions and a day on the calendar — carries `--sheen-panel` on two
shipping pages and the table had never heard of it. The chapter had written *"it is on nothing
else in the system"* twice, once about the accordion row and once about this. A closing "and
nothing else" is a census in a sentence. So the lit panels are derived the same way the
frosted ones are — every shipping rule painting `var(--sheen-panel)`, selectors taken as the
definition — and a panel that answers a pointer with light now enters the verdict table by
existing. It is a verdict claim and never a budget one: a sheen is a gradient and a
`background-position`, and costs nothing to composite.

**The list one step further out was hand-maintained anyway, and that is where it broke.**
Which *stylesheets* count as shipping was three names, and `acts.css` — which
`patterns/landing-page.html` loads — was not among them. A `backdrop-filter` written there
would have landed on the page carrying the tightest budget in the system and been invisible
to every claim above: uncounted, free to state its own radius, free to be animated. Found by
`.act-rail::before`, the act rail's plate, which is now the fourth blurred surface and is
glass for the material's own reason — it is the one panel on that page standing over
artwork, where an opaque plate is the grey box the chapter warns about. It also lands the
page on three, and **the budget did not move**: the plate paints only on hover or focus,
which needs the `.is-live` the rail only carries while the acts own the viewport, some
4 000 px past the hero button it therefore cannot appear beside. That argument is a named
entry in `PAGE_BUDGET` rather than prose — no other page inherits it, an entry has to name
two layers the CSS keeps apart, and an allowance whose page drops back under the default
fails, because a permission that outlives its argument gets read as headroom.

**And it moved the type, which the screenshot would not have.** A translucent plate makes
each row's backdrop the artwork, and this page's artwork reaches near-black. Swept at 250 px
steps across the whole act range at three widths, the plate's darkest composite is
`rgb(164,165,165)`, where `--text-secondary` reads 3.70:1 — so the five titles take black
and the recession moves to the three `aria-hidden` marks in each row. 46 % is derived as the
floor for **black** type over a backdrop nobody controls; the second tier the rail used to
run on was asking that tint for a guarantee it never made. The one rule it deliberately does **not** enforce is a transition, and that is a
correction to the chapter rather than a gap in the script: *Cost* had said **never move
anything** on a blurred layer while `.cf-btn--glass` has always travelled its specular
across its own blurred plate. Measured, that plate is indistinguishable from the same plate
with no blur at all — so the line is how long a thing runs and what it runs against, not
whether it moves, and a scroll-scrubbed animation is the half that pays.

**The waypoint is the light family's, not the assembly's,** and it is checked once. The
isometric script was written with a seventh rule of its own — no inline gradient runs lime
straight into Glas without `#DBFC60` between them — and it is gone: the light-family script
recomputes that waypoint's offset *and* its colour from the oklab path, which is strictly
the stronger claim. Two scripts asserting one invariant to two standards is the drift these
scripts exist to stop.

**Every grid track that carries an `fr` carries a floor,** and this is the fifth check
for the same reason as the other four: `base.css` states the rule twice, in prose, on
`.tiles` and on `.subdivide`, and nothing ran either. `1fr` is `minmax(auto, 1fr)`, and
as a *minimum* `auto` is the item's min-content width — so a bare `fr` track distributes
free space **or** the widest unbreakable word inside it, whichever is larger. One long
German compound then sets the track and pushes the page sideways.

Thirty-two of the system's thirty-three `fr` track lists already carried a minimum —
twenty-eight floored on the track, four guarded by `min-width: 0` on their items.
`.cf-progress` had neither, and measured with a 61-character compound in its label the
document went **320 → 469 px** wide at a 320 px viewport. `overflow-wrap: break-word` is
on it — the reset puts it on everything — and does not help: it breaks the word when the
track is drawn, and intrinsic track sizing has already happened. That is the whole reason
this belongs in a script rather than in a screenshot review: the page is correct until the
content is long enough, and then it is broken at a width nobody re-opens.

The check credits **both** fixes the system uses, because both are right. A floor on the
track — `minmax(0, 1fr)` — is what most of them do. `min-width: 0` on the items is what
`.subdivide` does, and it has to: its geometric sets are `4fr 2fr 2fr`, exact halves whose
whole point is the ratio, and `minmax(0, 4fr)` would state that ratio twice. A deliberate
*non-zero* floor passes too — `.tiles`' `min(--tile, 100%)`, `.cf-team-strip__list`'s
`15rem` inside a scroll box — because the rule is that a floor was chosen, not that it is
zero. → `foundations/layout.html#intrinsic-minimum`

**And the same defect had a second axis the check could not read.** A rule that declares
`display: grid` and no columns at all still has one — an *implicit* track, sized `auto`,
which in the minimum slot is the same min-content floor a bare `fr` carries. The script reads
track *lists*, so a rule declaring none was invisible to it, and this one was found by
sweeping instead: all 38 pattern pages, 25 widths from 320 to 2560, at browser default font
sizes of **16, 20 and 24 px**. At 16 and 20 the system has zero sideways scroll anywhere. At
24 — 150 %, a common low-vision setting and well inside WCAG 1.4.4 — it had exactly one page:
`patterns/ueber-uns.html` went **320 → 359 px** wide at a 320 px viewport, 22 px over at 340
and 5 at 360, clean again by 380.

`.cf-team-grid__item` was the rule, at `display: grid` with `grid-template-rows: subgrid` and
no column. It is the one place in the system where that can push the *page* sideways rather
than merely widen a box, and the reason is the subgrid: a grid whose own width is free absorbs
a wide track by growing, and this card cannot — its row axis is its parent's, so it stands in
a cell `auto-fill` has already sized and the track grows through it. That makes the case
decidable, so it is the **gate** the check now carries: a grid whose rows are `subgrid`
declares its columns or guards its items. The other thirteen implicit columns are a **census** —
seven guarded, six neither and all fine today — because whether an implicit column can be
squeezed depends on what its children hold, and that is a fact about content no reading of the
stylesheet settles. Six named exemptions would be six judgements the script cannot make;
counting them means the number cannot grow quietly. `-v` prints the census.
Nothing moves at a 16 px default: a single `auto` column in a grid of definite width already
stretches to fill it, so `minmax(0, 1fr)` draws the identical card and removes only the
minimum. → `foundations/layout.html#intrinsic-implicit`

**The rule outlived its scope, and where it landed is the interesting part.** Swept across
all 33 pages at eighteen widths from 320 to 2560, the system had exactly one horizontal
overflow: `foundations/colors.html` took the document **320 → 368 px** at a 320 px viewport.
The cause was not a stylesheet. It was `style="grid-template-columns:repeat(10,1fr)"`,
written **inline in the markup** on the Grey ramp — ten mono step labels flooring a track set
at 344 px inside a 272 px column.

That is the one place `check-grid-tracks.py` can never reach, and not by an oversight in the
script: its scope is the three stylesheets that ship, and an inline style on a documentation
page is outside that boundary twice over. The boundary is right and is not moved — a check
that governed the documentation chrome would be claiming the chrome is the product. What the
finding actually says is narrower and worth keeping: **a rule enforced over stylesheets is
not enforced over `style=` attributes**, and the system's own documentation pages are where
those attributes live.

Five bare `fr` track lists were floored, in `colors.html` (three, inline), `docs.css`
(`.docs-ramp__steps`) and the per-page blocks in `transitions.html` and `illustration.html`.
Only the ten-step ramp was overflowing today; the other four were the same defect at a cell
count that happened to fit. The sweep now reports zero sideways scroll on every page at every
width.

**That boundary has a second reading, on the same component, and this one was a WCAG
failure.** A ramp step is a rectangle painted the hex it names with that name printed on it
in 10 px mono, so its ink is not a preference: it is whichever end of the neutral ramp reads
on that particular swatch, and the answer moves the day the hex does. It was `color:#fff`
inside the `style` attribute of **twelve** of the thirty-eight steps — twelve copies of one
decision, in a shorthand the palette never uses, on the chapter whose subject is that a
colour has a name — and eleven of the twelve were right. The twelfth was **Sky 700**: white
on `#5684A9` is **3.99:1** against the 4.5:1 a 10 px label owes, where black on the same
swatch is **5.27:1** and clears it. It reads as a copy down the row rather than as a choice —
the two steps under it in that ramp are genuinely dark and genuinely take white.

`check-contrast.py` could not see it and is not at fault: it is the register of the pairs the
**tokens** guarantee, and neither end of this pair is a token — the swatch is a literal in a
`style` attribute and the ink was another literal beside it. Every other check that reads
colour reads a stylesheet, and this decision was not in one. The ink is
`.docs-ramp__step--dark` in `docs.css` now, spelt `var(--grey-000)`, and the modifier names
the *swatch* rather than the ink because the swatch is the reason.
`check-ramp-ink.py` recomputes both inks against the background each step declares and fails
a step that takes the worse of the two — so the eleven surviving judgements are arithmetic
rather than memory, and Sky 700 went from the only failure on the page to its tightest pass.
Nothing here is a screenshot's job: 3.99 and 5.27 render identically to everybody who is not
the reader the floor exists for.

**Every threshold is in the register,** and this is the sixth check for a reason the other
five had to be argued and this one only has to be counted. A threshold cannot be a token —
`var()` is not allowed in the prelude of `@media` or `@container`, and `@custom-media` needs
a build step this system does not have — so every one of them is a literal typed into a
stylesheet, and the only defence against them multiplying is a list added to on purpose.
That list is written twice, as a comment in `tokens.css` and as a table on
`foundations/layout.html`, and it says of itself that it is only worth having if it is
complete.

Kept by hand it was never complete for long. It was caught four times: `60rem` and the
height threshold; then `34rem` with two consumers and a `62rem` media query with one; then
`51.25rem`, hiding behind a true statement about a different file; then `28rem`, `30rem` and
`34.625rem` — three live container queries, one of them added the same day the sweep that
found them ran. Every one of those fixes ended with the same instruction to the next person:
*grep the preludes, and do not trust the previous fix to have been exhaustive.* Four times is
enough evidence about the instruction. Nothing ran.

The script holds the three copies to each other **in both directions** — a query with no
entry, an entry no query reaches, and the two copies disagreeing are each a finding — keeps
the rule that a threshold is written in `rem` rather than `px` so it tracks the reader's own
default font size, and re-derives each px gloss instead of comparing the number against
itself. It reads the range syntax too, so adopting `(width >= 40rem)` later cannot quietly
opt a threshold out of the check. What it deliberately does not read: non-dimensional
features, which are modes rather than thresholds, and `min()`/`clamp()` crossovers, which
change the layout at a width without being queries — the register says so in as many words,
and a checker that widened the definition would be enforcing a different rule than the one
written down. → `foundations/layout.html#breakpoints`

**And that left the other half standing on nothing.** The sentence above is right about the
register and it is the *last* thing anything ran on the subject. The panel directly under the
register on `foundations/layout.html` covers what the register drops — a `min()` or `clamp()`
against a viewport unit swaps arms at a width too — and it listed **three** and said "the three
in shipping CSS". There are **thirty, in sixteen declarations.** The three were the three
somebody had noticed: the consent dialog's two and the hero's `min-height`. Eleven token-level
crossovers were excused in a clause — *"the token-level clamps are documented already"* — which
is true of the gutter and `--section-gap` and silent about the rest. A completeness claim about
a four-file corpus, kept by hand, on the page whose neighbouring tables are generated precisely
because hand-kept counts went stale four times.

**The finding is 941 px.** `.cf-plot`'s `--plot-u` and `.cf-pie`'s `--pie-u` both reach their
32 px ceiling there — past every phone, short of every desktop frame this design was drawn on,
which is the band a fluid middle is least likely to be looked at and the classic place a
`clamp()` goes wrong unnoticed. Both figures stop growing there and hold one size for the next
thousand pixels. That is *correct* — a fixed-count geometric drawing has a size past which it is
merely large — and it was written down nowhere, with `.cf-plot`'s own comment naming the gap:
*"this is a crossover, not a threshold, so it is deliberately absent from the breakpoint
register."* Right about the register, and nothing underneath it.

**It has to be a gate rather than a reading, because a crossover is not written in the
declaration that has one.** `--section-gap` says `100vw / 12` and reaches its ceiling at 1440;
`--plot-u` says `clamp(16px, 3.4vw, 32px)` and stops at 941. So the script resolves rather than
reads: each value becomes a tree of `min()`/`max()` over linear forms in px, vw and vh —
`clamp(a, b, c)` is `max(a, min(b, c))`, `var()` resolves through `tokens.css`, and addition and
scalar multiplication distribute into the branches, because `min(a, b) + c` is
`min(a + c, b + c)` and a negative factor turns a `min()` into a `max()`. The result is piecewise
linear, so a crossover is exactly a width at which the selected arm changes: swept to find, then
solved off the two arms that swapped. **640, 920 and 974 are re-derived every run** the same way
941.2 is, which is the same standing `#DBFC60` has one chapter over.

Three things it cannot read it names on every run rather than passing in silence: 36 declarations
with an arm in `%` or `cqi`, which swap at a **container** width and are a different axis; 19 that
are unitless, where there is no arm measured in anything to swap; and **6 genuinely unread** —
four landing-page rules taking `max(49vw, 100vh − …)` against a page-local property, where the
swap is a curve in two axes rather than a width, and two resolving through a custom property no
reading of a stylesheet settles. Six is small enough to read, and counting them is what stops the
number growing quietly. → `foundations/layout.html#crossover-census`

**A crop says so,** and this is the seventh check, for the same reason as the other six.
`overflow: hidden` does two things: it crops, which is what anyone writing it wants, and
it makes the element a **scroll container**, which almost nobody does — and the second
half renders identically to the first, so nothing about a screenshot can tell them apart.
A scroll container is what a view timeline resolves against, what `position: sticky` is
measured inside, and a box that can be panned to with a keyboard or a script.

The system has been bitten by both halves and wrote each up where it happened rather than
anywhere that could run. `.cf-hero` cropped its artwork with `hidden`, and every
`animation-timeline: view()` in that header silently resolved against a box that never
scrolls — `.cf-btn--glass::before` reported a live ViewTimeline whose progress sat at
**0.116 and did not move at any scroll position on the page**. And
`prototypes/demon-core.html` cropped an ambient wash inset −10 % with `overflow-x: hidden`
on `<body>`, a declaration that never cropped anything: `overflow` on `<body>`
**propagates** to the viewport and leaves body itself computing to `visible`, so the wash
sailed past it and the document sat **128 px scrollable sideways at 1280** — 77 at 768,
38 at 375 — with nothing out there to look at. `clip` is excluded from that propagation,
so it stays on the box that declared it.

The rule is the pair the hero already writes: `overflow: hidden` and `overflow: clip`
under it. A browser without `clip` drops the second and keeps the crop it always had; a
browser with it never makes the scrollport. Two exemptions, both because the block is not
cropping a composed layer at all — a block that also declares `text-overflow` is
truncating one line of text, and `.visually-hidden` is the standard clip-rect idiom quoted
from the practice it comes from. → `foundations/materials.html`

**And the other half of that subject had no gate and no drawing.** `check-overflow-clip.py`
holds a crop to *saying* it is a crop rather than a scrollport, which is a fact about the
stylesheet. What nothing held is the fact about the reader: the system ships **five inline
scroll boxes** — a table, the same table inside an article, a month, a plan, the team strip
— and every one of them drew the edge it *hides a column behind* exactly like the edge where
the drawing stops. `foundations/geometry.html` allows a line to be an edge or a division and
calls anything else decoration; a crop is a third thing, and it had no line.

**The construction every other system reaches for cannot draw this mark**, and the reason is
the whole argument for the one that replaced it. A scroll shadow is two background layers,
one of them `background-attachment: local`, and a `local` layer is positioned against the
*scrollable area* — so the pair can only ever **occlude** each other. Both states are
therefore always painted, and the resting state here has to be **nothing**: the alternative
is a permanent vertical rule at both ends of every table in the system, which
`components/table.html` bans by name (*"a grid of boxes says spreadsheet"*).
`scroll-state(scrollable: …)` is a state and not a picture, and it is false at the end of the
travel **and** when there is no travel — the pair a hand-written scroll listener gets wrong
first, because a listener starts at position zero and so does a box that never scrolls. So the
fallback is not a lesser drawing: a reader without the query gets the page that shipped
yesterday, and a box with nothing hidden gets that page too.

The mark is one `--stroke-1` column at the edge that is hiding something, on
`--presence-absent` — the 1-4 ghost, the rung the presence ladder reserves for a thing that
is there and not drawn. **A container cannot query itself**, so it is the box's own `::before`
and `::after`: child boxes of the container, and the only children five components can be
given without touching a line of their markup. That costs one layout declaration — a
single-column grid, because a pseudo-element in normal flow has no depth and the mark is the
full depth of the crop — and the track is `minmax(min-content, 1fr)` rather than `1fr`,
because a table outgrowing its column is the entire subject. Measured against the same pages
before the change at 375, 768 and 1280: every box, every child and every document identical,
with one exception that paints nothing — the team strip's `<ul>` now measures its own content
rather than its port.

`check-cut-edge.py` holds three things a screenshot cannot. **The roster is read out of the
stylesheets** the way the glass budget reads what counts as glass — every rule declaring an
inline-axis `overflow` of `auto` or `scroll` is a crop, so a sixth scroll box enters the
census by existing rather than by somebody remembering it; one is exempt, with the argument,
because `.cf-prose pre` is the single inline crop whose port edge and drawn edge are not the
same line. **One element child**, because grid auto-placement skips a cell an explicitly
placed item already holds and a second child would land in row 2, under a mark drawn only to
the depth of row 1 — which renders as though nothing were wrong. And **the base tier draws
nothing**: an `opacity` raised anywhere but inside a `@container scroll-state()` query is the
permanent rule above, and on a browser without the query it is the only thing drawn. All three
were verified against a mutation of each rule rather than assumed. The block axis is out of
scope by argument — two of its three boxes are panels the reader opened rather than crops, and
`.cf-blog-grid--port .cf-blog-col` is a genuine cut wanting a different construction, named in
the chapter rather than half-covered. → `foundations/cut.html`

**A dash pattern is one of four,** and this is the ninth check — the one that had been
broken on a designed page the whole time. `tokens.css` realises the manual's three dashed
line types as px pairs, `.cf-iso` puts `non-scaling-stroke` on every contour so a dasharray
is measured in **device pixels**, and components.css says in as many words that this is what
"keeps a ghost's 1-4 dash a 1-4 dash at any size". The CSS side has honoured that from the
beginning: every `stroke-dasharray` declaration in the shipping stylesheets is a `var()`.
The **markup** side never has and cannot — a dasharray in an inline SVG is a presentation
attribute, a literal typed next to the path data and usually carried over from an export,
and a literal resolves no token. Counted, the tree shipped **eight distinct dash patterns
for a rule that has three**: the 1-2 ratio at units of 0.5, 1 and 2, the 2-1 ratio at units
of 0.5, 1.5 and 2, and one `4 1`, which is not a line type at all. Six of the strays were on
`patterns/ueber-uns.html`, under a comment claiming its dashes were "pinned to `--dash-*`".
Nothing about a screenshot says otherwise: a 3 px dash period and a 5 px dash period are the
same picture at a glance.

Two contexts, two standards, and the distinction is the whole of it. Where the stroke is
**non-scaling** the dasharray is device pixels, so it must be exactly a token value. Where
it is in **user units** the numbers belong to the frame rather than to the rule, and only
the ratio is checked — `foundations/iconography.html` blows a 24-unit icon box up 13× and
draws its keylines at 0.25 units, and holding those to `4 2` would put a 53 px dash on a
diagram of a 24 px glyph. `.cf-iso__trace` is exempt from both: components.css takes
`non-scaling-stroke` off it on purpose so `pathLength="1"` works, and its
`stroke-dasharray: 1` is a draw mechanism, not a line type. The script also re-reads the
three tokens themselves, so a silent edit to a dash period fails here rather than in a
screenshot nobody takes. → `foundations/geometry.html#lines`

**Type stands on a line too, and the system was measuring to the box around it.** A block
holding one line of type is as tall as its `line-height`, and what the glyphs do not fill
is leading — split above the cap line and below the baseline. A `padding-bottom` under a
line therefore starts under the *descender slot*, not at the baseline, so the drawn
distance is the token plus a slice of the font. `.cf-section-header` is where that was
worth a check: its rule has always said *the header owns the air beneath it, so every
section on the site opens on the same axis*, and it declares `--space-3`. Swept at 1280 px
over all 38 pattern pages with each label trimmed to its baseline so the distance
could be read off the rule: **54 headers, two axes, 12 px declared and 16.94 px drawn on
53 of them, 17.63 on the fifty-fourth.** 41 % over the token, and not one axis.

Neither number is computable, which is the argument for trimming the slot rather than
compensating for it. Between `--leading-normal` and `--leading-relaxed` at 11 px the line
box grows 1.64 px and *all* of it lands under the baseline — the engine places the
baseline on a whole pixel (measured at 9, 10, 11, 11, 15, 17, 27 and 34 px from the box
top across the type scale, every one an integer) and the rounding is absorbed by whichever
slot is left over. A magic number that cancels the slot is right at one size, one leading
and one font, and this system has three of each.

`text-box-trim: trim-end; text-box-edge: cap alphabetic` takes the slot off, and the axis
is `--space-4` at every size and every leading. **16 px is the drawn distance moved onto
the space scale rather than changed**: within 0.94 px of what 53 of those headers draw
today and 1.63 px of the fifty-fourth, so the composition does not move and the number under
it becomes true. Outside the `@supports` branch the padding stays `--space-3` and the
drawing is exactly today's — Chrome 133, Edge 132, Safari 18.2 and Firefox 154 have it,
and anything older is 0.94 px looser and correct.

`check-cap-line.py` is the twelfth check for the same reason as the eleven before it, and
the sharpest case of it so far: **this property's correct use and its worst misuse are the
same declaration with one value left off.** `text-box-edge: cap` is legal and means
`cap text` — the under edge falls back to the font's own descent, which *is* the slot the
trim beside it was reached for — so the rule reads as a trim, draws as none, and sits one
character away from the one that works. Leaving the property off is worse again: the
initial is `auto`, the font's own metrics, and the display face is not licensed yet. The
third claim is the pair — a trim and the padding that replaces the slot it removes are one
decision and share one branch, or the drawing comes apart between browsers — and the
fourth is the census on the chapter page, generated the way the glass budget's and the
space scale's are. → `foundations/capline.html`

**And the thirty-fourth is not about a design decision at all.** A pull request landed on
`main` with its own rebase unresolved: `<<<<<<< HEAD` and the sha line under it shipped as
literal text in five files — the design system's index, the reference page, two paragraphs
of `foundations/construction.html`, this README, and a 29-line block inside a comment in
`components.css`.

**Every gate above passed over it, and none of them was wrong to.** A marker inside a CSS
comment is comment text; a marker in a documentation page is a paragraph; a marker in
Markdown is a line of prose. Each of the thirty-three reads one decision — a distance, a
ramp, a dash period, a count — and a conflict marker is not a wrong *value* of anything. It
is the one shape that is never correct in any file type this repository ships, and nothing
was reading for it. `check-merge-markers.py` reads every tracked text file for it in one
pass. A bare `=======` counts only *between* an opening and a closing marker, because seven
equals signs is also a setext heading rule and a divider in an ASCII figure, and failing
those would be enforcing a rule nobody wrote.

**The tenth, eleventh and twelfth are about the system as a site** rather than about a drawing
in it: every link resolves on the host that actually serves the pages, the `JobPosting` block
matches the page a reader sees, and the part of accessibility that is arithmetic rather than
judgement. Their arguments are in `scripts/check-links.py`, `scripts/check-job-posting.py`,
`scripts/check-a11y.py` and the header comment of `.github/workflows/design-system.yml`.

**Every class in the markup is declared by something,** and this is the thirteenth check —
the first one that reads the markup and the stylesheets as two halves of the same claim.
The twelve above it all read CSS, JSON-LD or the document outline and ask whether a value
is right. None asks the prior question: when a page writes `class="cf-blog-card"`, is there
a `.cf-blog-card`. Counted across the 56 pages, **27 class uses resolve to nobody at all** — `.docs-rule--do`, which
docs.css never styles because the "do" half *is* the base; `.cf-error__lead`, a real grid
child of `.cf-error--page` that components.css declares no rule for; `.h1` on
`foundations/sight.html`, which exists in no file in this repository, so the foil demo asks
for a display size it never gets. Each of those renders exactly like a class that works,
which is why counting them is the only way to see them.

**The `.h1` one is fixed and the fix was not the size.** `.sight-stage .text-foil` sets a
`clamp()` of its own, so the demo had a size all along; what the dead class cost it was the
rest of the treatment. Measured at 1280 before: Geist at `font-weight: 300` with no tracking,
against the display face at 700 with `--tracking-display` that every foil moment on the site
actually ships — `.cf-footer__title`, which is the line this demo quotes verbatim. The one
demo of the foil in the system was drawing it on the thinnest letterform in the type scale,
which is the worst possible mass for a material whose whole subject is light caught on a
stroke. It carries `.t-display-2` now, the class whose declarations are the footer title's.

It also closes the gap every other check leaves open by name. `check-spacing-scale.py` says
it in its own header — the shipping stylesheets are in scope and "page-local `<style>`
blocks are deliberately out of scope" — and so does every check after it, which made those
blocks the one place in the tree where a hex could sit unchallenged. They are checked
here for the two literal classes the system has tokens for: a colour a token already names
exactly, and a length in a spacing property. Inline `style=` is held to a narrower rule and
only under `patterns/`, where a page stands in for a page of the real site: it may carry
custom properties, which are per-instance data the markup genuinely owns — `--i`,
`--stage`, `--build-dx`, 110 of them — and nothing else. A documentation page under
`foundations/` frequently writes CSS as the specimen it is demonstrating, and is not held
to that.

The census is the part to read. `--report` resolves every class use against who declares
it, inventories every page-local block, and prints the two tables a name-based census
needs to be honest: **the same name on more than one page**, which is how `.ds-back` turned
out to ship in 14 copies already forked into two versions — folded into `preview.css` now,
with a rule that fails the build if a page-local copy comes back — and **the same rule under more
than one name**, which is how the pinned stage on `patterns/expertise.html` and the one on
`patterns/landing-page.html` turn out to share **eleven identical rule bodies** under `ex-`
and `lp-proc-` prefixes — the report prints the five that are more than a single
declaration. Neither table is a gate. A component the system has not named yet is a finding
about the system, not a build failure.

**The fourteenth is the one whose failure no measurement in this repository can see.** Every
page must carry `width=device-width, initial-scale=1` and nothing that pins the scale, because
pinch zoom is how a large share of people read on a phone at all — and a page that revokes it
renders identically at every width, in every screenshot, on every machine a designer owns. Its
argument is in `scripts/check-viewport-zoom.py` and the workflow header.

**A threshold cannot be a token,** so every one is a literal and the only defence is a
register — and this is the fifteenth check, for the thresholds the register in `tokens.css`
names as the thing it leaves out:

> `inline <style>` — per-page demo styles. `foundations/iconography.html` asks a **viewport**
> 48rem where 48rem above is a **container** threshold.

That exclusion is right. Governing documentation chrome from a shipping stylesheet's register
would make it look like it governed the chrome, and `check-breakpoints.py` is correct to stop
where it stops. But it left the page-local thresholds registered *nowhere*, and a threshold
registered nowhere is a number the next person reasoning about where this system folds will
not find. There are **eleven of them, in seven files**; four are px.

**The gap had a live bug in it for as long as it existed.** `patterns/expertise.html` gated its
pinned, scroll-scrubbed stage on `(min-width: 820px)` — the number
`prototypes/expertise-scroll.html` asks, carried across into `patterns/` along with the
mechanism — while `patterns/landing-page.html` runs *the same mechanism* on
`(min-width: 64rem) and (min-height: 45rem)`, derived for its own card and documented in place.

The 820 was wrong in both units and both dimensions, and the reason is a fact about the page
rather than a taste about numbers: the stage is only habitable once `.ex-step` has its **two
columns**, and that fold is a **container** query at `56rem`. A px gate cannot track a rem
fold. So the pin arrived at a fixed 820 while the two-column form arrived wherever 56rem of
container happened to land, and between the two the stage pinned a **stacked** step into
`100vh` of `overflow: clip` and cropped it:

| default font size | stage pins at | two columns at | cropped band | worst crop |
|---|---|---|---|---|
| 16 px | 820 | 1007 | 187 px | 84 px |
| 20 px | 820 | 1259 | 439 px | 173 px |
| 24 px | 820 | 1511 | 691 px | 297 px |

The reader who asked for larger type lost the most, which is exactly the failure the rem rule
exists to prevent — and none of it is visible at 375, 768 or 1280, the three widths anyone
checks, because all three are outside the band. Both figures are the landing page's now,
unchanged: one mechanism, one gate.

`patterns/` is held to the rem rule outright — a pattern page stands in for a page of the real
site, so a reader's font size is a reader's font size there. A px threshold in documentation
chrome gets a row marked `PX DEBT` instead, naming its owner; the count prints on every run and
cannot grow without a visible edit to the script. What this check deliberately does **not**
touch is classes, literals and inline layout in a page-local block: `check-class-provenance.py`
above owns all three. Two scripts carrying overlapping rules are two things that can disagree,
which is the failure mode this whole family exists to prevent — so this one stops at
thresholds, the part of that scope the other does not reach.

The two checks were written in the same hour and found the same fork from opposite ends. The
census reports that the pinned stage on `patterns/expertise.html` and the one on
`patterns/landing-page.html` share **eleven identical rule bodies** under `ex-` and
`lp-proc-` prefixes; this check reports that until now they did not share the **gate**.

**The counter above an accordion counts the rows under it,** and this one is here because
another check wrote down the day it stopped being able to say so. `check-section-counts.py`
owns `patterns/landing-page.html` — every counter on it, by a hand-kept register of what one
item's markup looks like in each section — and it was written because four of that page's
five counters were wrong. Its register then recorded a loss in as many words: the FAQ moved
to `patterns/expertise.html` on 2026-08-04, *"its counter travelled with it unchanged and is
still the true one (`6 Fragen`, six questions); what this register can no longer say is that
it is true, because the register is this one page."*

It was right that it could no longer say it, and wrong within the month about the fact. The
migrated set grew from six questions to eleven and its counter grew with it. The two copies
left behind did not, and both of them are documentation: `components/accordion.html`, the
page that teaches the component, shipped `6 Fragen` over four `<details>`; and
`components/section-header.html`, the page that publishes the counter's own four forms,
shipped `6 Fragen` over two. Neither is visible. A counter is eleven pixels of mono at the
end of a hairline — correct at every width, in every contrast check, in every screenshot, and
a count of rows that do not all fit on the screen at once.

The rule is narrow enough to be decidable and is scoped to one component: on every page
except the one next door owns, a `.cf-section-header__count` standing above a `.cf-accordion`
is read as a **position** if it carries `aria-hidden` and as a **quantity** if it does not —
which is the distinction `section-header.html` already publishes, in the markup rather than in
a list — and a quantity's leading integer must equal the number of `cf-accordion__item` under
it. `karriere`'s `05` and `kontakt`'s `03` are skipped by that rule, not by being named. The
marker is the item class for the same reason the partner wall's marker is its `<img>`: it is
the thing the number is a count *of*, and a row cannot be drawn without it.
→ `components/accordion.html`, `components/section-header.html#counters`

**The other end of the same hairline had a modifier that promises something about a
different element, and nothing read the two together.** `.cf-section-header--flush` sets
`border-bottom: 0` and `margin-bottom: 0` on the device that opens every section, on the
understanding components.css states plainly: *the content below is a ruled container and ITS
top border is the rule.* Over `.cf-accordion` or `.cf-vacancies` that is exactly right and
saves a doubled line 1 px away. Over anything else it does not move the rule, it **deletes**
it — and what ships is a mono label and a counter floating with no hairline under them and no
clearance either, because the modifier drops the gap too. It renders as a smaller version of
the correct thing, which is why every contrast, link, layout and a11y check in the directory
passes a section drawn that way.

**Eight of the thirty-seven were written that way, and the two files each blamed the other.**
The comment over `.cf-contact` read *"No top border. The section header above it draws that
hairline; giving the list one of its own is what `--flush` exists to avoid"* — true of a
plain header in its first clause, and naming in its second the one modifier that makes the
first false. `patterns/impressum.html` read the second clause and wrote `--flush`, so its
`03` opened on nothing between an `01` and an `02` that both draw a rule.
`patterns/karriere-stelle.html` did it twice, over `.cf-prose` and over a `.stack`, leaving
`04` ruleless one section above an `05` that is flush and correct — and the four generated
`stelle-*.html` inherit its specimen verbatim. `patterns/expertise.html` handed its rule to
an element that is not there at all: nothing follows that header inside the container, since
the pin stage below is full-bleed and a sibling of it.

**The sharpest two are the zero states**, and they are the reason this is a script. On
`karriere.html` and `suche.html` the header IS flush and IS right, because `.cf-vacancies`
and `.cf-results` bring the edge. `karriere-leer.html` and `suche-leer.html` swap that
register for `.cf-error--inline`, which brings none — so the rule was present in the state
anyone looks at and absent in the state that ships the day the register empties. All eight
are plain headers now; the rule lands on the same axis it did before, because a flush
container's top border and a plain header's bottom border sit at the same place, and only the
clearance under it differs — which is right, since a message is not a register.

The set of containers allowed under a flush header is **derived, not listed**: any rule in a
shipping stylesheet declaring a top border of stroke ink, in the longhand or in the `border`
and `border-block` shorthands that contain it. Reading only the longhand credited
`.cf-process` — which states its whole contour as `border` — with no edge, and reading the
last *class* of a selector rather than its last *compound* credited `.cf-prose` with the
border only its `figure` has. That second error is not incidental: `.cf-prose` is one of the
eight sites. The inverse direction is deliberately not checked — a plain header over a ruled
container draws two hairlines a few pixels apart, which is a drawing decision with more than
one right answer, not the disappearance of a line.
→ `components/section-header.html`

### The other half: nothing in the markup writes into a void

`check-class-provenance.py` asks who **declares** a class. `check-markup-answered.py` asks who
**answers** the markup, which is a different question with the same failure mode — the page is
correct, the screenshot is correct, and something it says is heard by nothing. Two rules, both
of them live when it was written:

- **A modifier the component's own page does not show.** `.cf-footer--detached` shipped on
  `ueber-uns` and `blog-artikel`, was named in the rhythm table on `foundations/layout.html`,
  and was already guarded by `check-footer-parity.py` — and `components/footer.html`, the page
  with the live footer on it, never mentioned it. Somebody building a footer from the component
  page could not learn that the modifier exists, or that a biconditional binds it to
  `.section--flush`. **"Mentioned somewhere" is not the bar**: a rhythm table names a class, it
  does not teach it. The page that has to show a state is the page with a **live specimen** of
  the block on it, and where a block has no specimen anywhere the rule softens to its floor —
  findable at all. The hero's pause switch is that case.
- **An inline custom property no rule reads.** `patterns/ueber-uns.html` set
  `style="--layer:N"` on the four grid layers of the Werte mark and nothing read it: the
  animation ranges were four hand-written pairs picked out by `:nth-of-type` instead. One index,
  written twice, one copy inert — and the inert copy is the dangerous one. Reorder those layers,
  or wrap them in a `<g>` for a clip, and `:nth-of-type` follows the new positions while
  `--layer` goes on saying what the drawing meant, with nothing able to tell you they have come
  apart. `--layer` is the copy that runs now, and the four pairs are one rule.

`KNOWN` in that script is the register of gaps open today, each with its reason. **It is empty**,
and that is the register working rather than the register being ignored. It held two rows, and
they were the largest documentation gap in the system: `cf-culture` — the culture band on
`patterns/karriere.html` — had no documentation page at all, no specimen, no anatomy, no mention
anywhere under `components/` or `foundations/`, and its two row modifiers were the visible edge of
that. [`components/culture.html`](components/culture.html) is that page, and it shows both frames
live, so the rows went with the gap they named. A row whose gap has been closed fails the check
too, because a register that outlives its subject is how the next one hides inside it.

### And the third direction: a class the documentation names

Those two read the markup. `check-anatomy-provenance.py` reads the **chapter**: every class
named in a whole-`<code>` table cell under `components/` or `foundations/` has to be declared
by a shipping stylesheet or by that page's own `<style>`. That is the register the other two
cannot see, because a class name inside `<code>` is prose to a script that reads `class=`
attributes.

**How many of them there are is the run's output, not a number in this paragraph.** It was one
for an hour — "351 mentions across 34 chapters" — and two lanes landed chapters inside that
hour. A gate against hand-kept documentation whose own documentation is hand-kept is the
failure it was written for, one level up.

**The failure it is for is a clean rename**, which is the ordinary edit and the one most likely
to be made by a lane that has never opened the chapter: the rule is in `components.css`, the
markup is in the pages, and the sentence describing the part is in a third file nobody is
touching. Renamed consistently in the first two, `check-class-provenance.py` reports 5108 class
uses all resolved and the anatomy table goes on naming a class that no longer exists — a row
that renders like every other row and is the one thing on the page a reader copies out of.
Proven on exactly that shape with `.cf-process__benefit-label`.

It is deliberately narrow, on the argument `check-cited-gates.py` makes for reading only script
paths: only cells that are **nothing but** code (a sentence may legitimately name a class that
was removed — this repository keeps records), only class names (custom properties have
`check-registered.py`), and a wildcard like `.col-*` passes, because a family is not a class and
a check that forced twelve rows to say one thing would be making the documentation worse.

## Layout

```
design-system/
├── index.html              overview + how to include the CSS
├── foundations/            colour, type, layout, geometry, iconography, materials,
│                           illustration, logo, photo, motion, mobile,
│                           page transitions, field, found state, line of sight,
│                           the sheet (print), the share plate (link previews)
├── components/             buttons, nav, breadcrumb, section header, statement +
│                           value table, plot, line, pie, gantt, annotation,
│                           process card, accordion, blog grid,
│                           subdivision field, search + results, vacancy,
│                           pagination, error + empty state, arrival + progress,
│                           article + prose, table, team, culture, forms, footer,
│                           consent
├── patterns/               the website — landing-page.html, expertise.html,
│                           ueber-uns.html,
│                           news.html, blog-artikel.html, suche.html,
│                           karriere.html, kontakt.html,
│                           datenschutz.html, impressum.html, 404.html
├── prototypes/             motion studies — standalone, not yet system
├── reference.html          the designer's source material, next to what implements it
└── assets/
    ├── css/
    │   ├── tokens.css      every design decision as a custom property
    │   ├── base.css        fonts, reset, type classes, layout primitives, utilities
    │   ├── components.css  every component
    │   └── docs.css        this documentation site only — does not ship
    ├── js/
    │   ├── cf-consent.js   the consent banner + settings dialog. Ships.
    │   ├── cf-nav.js       the phone layout's menu disclosure. Ships.
    │   ├── cf-icons.js     the icon set — the one place a glyph is drawn. Ships.
    │   ├── cf-stream.js    types the copy on a pinned track. Ships, optional — see below.
    │   ├── cf-sight.js     the reader's position across the screen. Ships, optional.
    │   └── docs.js         sidebar, swatch copy, arrow sprite — documentation only
    ├── fonts/              (empty — see below)
    ├── icon/               generated — the App-Icon tile at 180/192/512 and the
    │                       manifest that names them. build-app-icons.py, gitignored
    ├── img/                logo SVGs, icons, hero poster, team photos, wallpaper
    ├── video/hero-abstract-art.mp4
    └── source/             reference only, never linked from a shipping page
        ├── manual/         22 brand-manual plates as compressed renders
        ├── mockups/        both designed pages, full length
        └── illustrations/  the 4 process cards as source vectors + Figma spec dump
```

`assets/source/` is the curated slice of the designer's archive that the system was built
from — enough to check or extend any decision without the full 194 MB folder. See
`reference.html` for what each plate governs.

## Using it in the website

**`patterns/` *is* the website.** Every page in it is served from the repository root,
generated by `scripts/build-site.py` — `landing-page.html` becomes `index.html`, the
`../assets/` paths become `design-system/assets/`, and the preview stylesheet and the
`← Design System` nav are dropped. That is the whole difference. Edit a pattern, run
`python3 scripts/build-site.py`, and the page the site serves changes with it; CI runs
`--check` and refuses a root page that has drifted from its pattern.

The paths below are what that generator writes, in the absolute form a site at a domain
root would use. On this project page they ship relative, for the reason
`scripts/check-links.py` states.

Three stylesheets, in this order:

```html
<link rel="stylesheet" href="/design-system/assets/css/tokens.css">
<link rel="stylesheet" href="/design-system/assets/css/base.css">
<link rel="stylesheet" href="/design-system/assets/css/components.css">
```

Then paste the arrow sprite right after `<body>` (see `components/buttons.html`), add
the icon sprite with `<script src="/design-system/assets/js/cf-icons.js"></script>` — or
paste its markup instead, see `foundations/iconography.html` — and build pages from the
classes documented in `components/`.
`patterns/landing-page.html` is a working reference for a whole page.

Four scripts ship. Two are required, two are not:

```html
<!-- in the <head>, after the three stylesheets -->
<script src="/design-system/assets/js/cf-nav.js"></script>

<!-- at the foot of the body -->
<script src="/design-system/assets/js/cf-consent.js"></script>
<script src="/design-system/assets/js/cf-stream.js" defer></script>
<script src="/design-system/assets/js/cf-sight.js" defer></script>
```

`cf-consent.js` drives the consent banner and the settings dialog, which the site
cannot legally do without (TDDDG § 25). It is dependency-free, creates no markup of
its own, and if it never runs, no non-essential script runs either.
→ `components/consent.html`

`cf-nav.js` is the disclosure behind the menu button on the phone layout, and the only
implementation of it — the behaviour used to live in seven identical inline scripts on
the pattern pages plus an eighth in `docs.js`, which is documentation chrome and does
not ship, so a page built from this system got a button that did nothing. It creates no
markup either, and it follows the WAI-ARIA Authoring Practices disclosure navigation
pattern: `Esc` closes and returns focus to the button, focus leaving the bar closes it,
a pointer outside it closes it, and the open state is dropped on the way past 780 px.
**The tag goes in the `<head>`,** because every rule that folds the bar is gated on the
attribute this file writes: with no script the links are a stacked list and no dead
control is drawn, and that fallback is only free if the attribute is there before the
first paint. → `components/navigation.html#script`

`cf-stream.js` is **optional and additive**. Every section that uses it is complete without it
— the copy is real markup and a view timeline does the pinning, the scrubbing and the
mark. All it adds is the copy arriving character by character rather than whole, which
is the one thing a view timeline cannot do because there is no per-character unit to
animate. It refuses to run unless the pinned layout is actually active, and it keeps
the full sentence in a `.visually-hidden` twin so assistive technology never gets a
half-written value. Delete the tag and the section still works.

`cf-sight.js` is **optional and additive** in the same sense, and answers the one question
CSS cannot ask: where across the screen the reader is. It writes two custom properties —
`--sight-h` on `.text-foil` and `--field-light-x` on `.cf-ground--lit` — and nothing else.
Both rest at the identity value of the expression that consumes them, so deleting the tag
renders every page exactly as it did before the file existed, to the digit.
→ [The line of sight](#the-line-of-sight)

Everything else in the system is HTML and CSS.

## Animation prototypes

`prototypes/` holds motion studies. They are **not part of the system**: each one carries
its own styling and its own engine, none has been reconciled with the tokens, and nothing
in `components/` depends on them. They are in the sidebar so the motion they propose can
be reviewed against the pages it would land on.

| | |
|---|---|
| `werte-scroll.html` | The mark builds itself from its own isometric subdivision grid across six value stages, with the copy streaming in char by char. Scroll-scrubbed, so it un-builds on the way back up. |
| `services-scroll.html` | The four process cards assemble inside a pinned section — cubes telescoping up, layers sliding in, contours drawing themselves. 1.4 MB, almost all of it one inline Figma export. |
| `expertise-scroll.html` | The four fields of expertise on one track — Maschinenbau, Großanlagen, Erneuerbare, Flotten. No script at all: one view timeline, four windows over it, and a step that hands over to the next on the rake. Stacked and readable below 820 px and under reduced motion. |
| `demon-core.html` | The Über-uns header object, made live. Click the core: the reflector travels down the axis, holds, snaps shut, and the assembly goes critical in the full palette. |
| `evidence-scroll.html` | The numbers behind the landing page's promise — one sourced figure per service (pie, plot, plot, line) on one pinned track, each chart's own keyframes re-timed onto `--cf-pin` because a `view()` timeline freezes inside a sticky stage. Every figure is verified against its primary source; the source links stand on the cards. |

The first two scrub from scroll position rather than playing on a timer, which is what the
system already commits to in `foundations/motion.html` — the animation tracks the reader's
hand and reverses when they scroll back. `demon-core.html` is the exception and has to be:
it is not a reveal, it is a *consequence*, and a consequence the reader can scrub backwards
out of is not one. It runs once per click, on a timer, and resets itself. Its reduced-motion
path skips the travel and shows the end state.

The screwdriver is gone. The designer's file staged the accident with the tool wedged in
the gap — wiggling, slipping, falling out of frame — and the sequence is retimed around
its absence: the beat the wiggle used to fill is now a held pause with the reflector
stopped one step short of the core. It is the only version that survives being 585 px wide
in a page header, which is the size it would ship at.

The static half of this object has already shipped: it is the figure in the `Über uns`
page header, drawn from the same source vectors in the same coordinate system.

**`werte-scroll.html` has shipped.** It is the *Unsere Werte* section of
`patterns/ueber-uns.html` now, rebuilt as `.cf-values`. What changed on the way in:

| | prototype | shipped |
|---|---|---|
| engine | ~120 lines of JS | a view timeline, no script |
| copy | typed char by char out of a JS array | six list items, typed by an optional script |
| reduced motion | the 660 vh track and the gating both survive | stacked, readable, mark finished |
| no JS / no support / print | nothing to read | every value readable, whole |
| below 820 px | pinned | stacked, so a phone gets no seven-viewport hijack |

The typing does survive, but only as an enhancement on top: `assets/js/cf-stream.js`,
which follows the prototype's own timing — a 62 % reveal window per stage, the title in
its first 28 %, the body starting at 14 % and spanning the rest, smoothstepped. Because
it reads scroll position rather than running a timer, scrolling back up un-types the
text exactly as the prototype does. Without the file the values arrive whole and
everything else is unchanged.

The prototype file stays where it is as the reference.

`services-scroll.html` is still a prototype. Its reduced-motion path is already correct —
the scrub script returns early, the pinned section goes `static` and auto-height, and the
illustration renders in its authored, finished state, the same shape as the fix in #11.

## The system in one paragraph

The site sits on CF-Grau, not on white — a data space, not a sheet of paper, with a
slow vertical wash from `#CFCFCF` to white across the full page height. Everything is
drawn with 1 px contours rather than filled, and anything spatial is constructed in
2:1 isometry (26.57°). Structure is square and objects — controls, plates, photos —
carry a 2 px corner; nothing is a pill, and avatars are the one circle. Lime is light,
not a surface: one element per screen, which is why the black button's label is filled
with the foil rather than the lime ramp. Publica Sans sets display headlines, Geist sets
everything readable, Geist Mono sets labels and every number.

## The front door is the stack

`index.html` opened on that paragraph and then on a grid of cards, which is a sheet of
paper describing a space — the one thing the paragraph directly above it says this brand
is not. The system's own front door was the last page in the tree still laid out like
every other documentation site.

**What was missing was not a picture of the layers. It was the model.**
`foundations/materials.html` draws the six twice already: once as six samples in a row,
once composited into a facsimile of the hero. Both answer *what does frosted glass look
like*. Neither answers *what is this system made of* — that the six stand in a fixed
order, back to front, that the order never changes, and that every chapter here is a
chapter about one of them. A reader arriving at this repository had no way to see that
without reading a chapter that assumes it.

So the index now opens on the stack itself: six 2:1 rhombi, half-width 200 and
half-height 100 in a 640-unit frame, 84 units apart so they overlap by 116 and read as
one object rather than as six. Layer 6 stands at the top because it is the top of the
stack, and the paint order is its reverse — in isometry higher is nearer, so 6 occludes
5 and SVG paints last on top. Written the other way round the drawing is correct right
up until a plane is lit, and then the base wash's fill covers the five layers standing
in front of it. The two struts and the axis are `--dash-1-4`, the
[absent rung](#the-presence-ladder): a strut is not an edge of anything, it is where an
edge would be.

**One lime moment, and it has a default.** Exactly one plane carries the light family at
a time. With no pointer and no focus anywhere in the block, the lit plane is layer 5 —
the light layer, lighting itself, which is the only default that does not have to be
argued for. Hovering or focusing a row moves the light to that row's plane and lifts the
plane 16 px out of the pile, and it *moves*: the ramp travels in along the 26.57° its own
top-left edge runs, rather than switching on. The other five recede to `stroke-opacity`
0.55 — a rank, not a way of turning a contour off, and the number is a floor rather than
a taste. Black at 0.55 composites to `#707070` on this page's ground and measures
**4.66:1**; on CF-Grau, where the same drawing would stand inside a pattern page, `#5D5D5D`
and **4.23:1**. Both clear the 3:1 the system holds a contour to at both ends.

**No script, and the binding is `:has()`.** Six rules key a row's `:hover` or
`:focus-within` to its own plane, so the drawing answers a keyboard exactly as it answers
a pointer — verified: focusing a link in row 02 lights plane 02 and nothing else. The
figure is `aria-hidden` and carries no destination; every link is in the list beside it,
in the same order the planes stand in. A browser with no `:has()` gets a figure in its
default state next to a list of links, which is what the block is anyway, and loses no
information at all.

**Every fallback tier keeps the mechanism, including the one that has no colour.** Under
`prefers-reduced-motion` the lift goes to `0px` — the state still switches, because a lit
plane is information, it simply arrives where it already stood. Under `forced-colors`
the recession is dropped, since a `stroke-opacity` is a paint operation the mode does not
touch and five planes would otherwise sit at 55 % of a system colour the mode chose to be
read at 100 %. The light goes with every other gradient, and the lit plane is still the
lit plane: `.cf-iso [fill]` maps to `Canvas`, the five unlit copies are at opacity 0, so
exactly one plane in the stack is a solid plate and it occludes the plane behind it.
Verified in both palettes at 1440. → `assets/css/docs.css`, "THE STACK"

## Lime is never flat

Wherever lime fills an area it fills it with a **gradient** — one of the light family,
running out of lime into Glas and away to CF-Grau. A rhombus painted `#E1FF00` edge to
edge is not the light layer; it is a yellow shape. Light in this brand is *a source and a
falloff*, which is what the three rakes are, what the bloom is, what the foil is — and a
flat lime plane has neither, so it says nothing about where the light comes from.

Pick the ramp by what the mark is: a flat face takes the near rake, a curved body the mid
rake, a rim or a nucleus the bloom, a horizontal run `--gradient-light-90`. A mark on a
**dark** surface takes the same ramp **stopped at Glas**, because CF-Grau over black is a
mid grey and the far end of the ramp would read as a grey pill rather than as light
falling off. In SVG the ramp is a paint server and carries the `#DBFC60` oklab waypoint,
because a CSS gradient cannot be an SVG `fill`.

Four boundaries, each technical rather than aesthetic: a **swatch** (the palette chip on
`foundations/colors.html`, a legend key on a map — a swatch of a colour has to be the
colour), a **highlight** (`background-image` is ignored on a highlight pseudo-element, so no
ramp of this family can be painted into `::selection`, `::target-text` or `::highlight()` —
see below), a **source's nucleus** (a light's falloff is the glow it throws, not a ramp
inside it), and anything that is **not an area** — a stroke, an outline, a focus ring. The
flat lime cube on `foundations/illustration.html` is a labelled *don't*, drawn wrong on
purpose.

→ `foundations/colors.html#lime-is-never-flat`, `foundations/light.html#flat`

## The light layer

`foundations/light.html` is the chapter for the one of the six material layers that had
none. The front door draws the six and gives each a route into the system; five of them
land on a chapter that is about that layer — the wash, materials, glass, geometry,
typography — and **layer 5 pointed at three chapters, none of which is about light**: a
section of the colour chapter, the found state, and the line of sight. Light was documented
as a property of the palette, which is a category error, and it produced a real one.

**The law is one source per screen, and a falloff is unbudgeted.** The system's oldest
rule about light — *one lime moment per screen* — is right and is a count standing in for
it. A **source** is where light comes from: a nucleus, a lit contour, a lit face, a cap, a
rim. It says *this is the place something happens*, and a screen with two of them has two
places and therefore none. A **falloff** is a surface catching light from somewhere else —
a foil headline, a glass rim, the pool on a lit ground, a black button's label — and it
makes no claim about where the eye should go, so counting it was never the point.

The distinction is not new; it was discovered three times and written down as three
separate exemptions, none of which could see the other two. The black button's foil label
("under no budget, because there the foil is the component's colour rather than an
emphasis"), the found state's twelve matches ("satisfied by the drawing rather than waived
for it") and the annotation layer's six notes ("one lit anchor and five contoured ones") are
one rule. Naming it once tells the next component which side it is on before it needs an
exemption written for it.

**The boundary was a list of places, and it had gone stale.** *Lime is never flat* closed
with "three exceptions" — the palette swatch, the found state, a stroke. Swept over the four
shipping stylesheets, the system paints a flat lime **area** in seven places. The three
names covered five of them — the found state's registers, all one kind — and two had no row: the **nucleus** of a source (`.lp-flow__src::after`,
twenty-five of them on the landing page) and a **legend key** (`.map__key-dot--*`, the
swatch argument at a different address). Neither is a defect in the drawing — measured on
the rendered page, a nucleus is 3.6 px of flat lime standing inside 5.4 px of lime and 12 px
of Glas of glow, so the falloff is there and is three times the diameter of the thing
throwing it. A ramp inside it would be a more expensive way to draw a flat dot. The rule was
never violated; the list of addresses was the wrong shape for it.

`scripts/check-lime-flat.py` is the boundary made executable. It derives what counts as lime
from the stylesheets' own aliases rather than from a roster — `--accent`, `--found-light` and
`--focus-ring` are lime because `tokens.css` says `var(--cf-lime)` — takes every declaration
of an area property (`background`, `background-color`, `background-image`, `fill`) carrying
no ramp, and fails in **both** directions: an uncovered flat lime, and a covered entry that
matches nothing. The second half is the one this section is about, because a stale exemption
is how a list stops being read. The census is stamped into the chapter.

→ `foundations/light.html`, `foundations/colors.html#lime-is-never-flat`

## Where a line may go

The system runs on hairlines, so the one rule that keeps it from reading as generic is
about **where** they are, not what they look like. Every line is an **edge** (it closes a
surface), a **division** (content on both sides of it), or a **label rule** (a mono label
with the hairline running out of it, so the line and the word are one mark). A line that
is none of the three is decoration.

The decoration this bans by name is **the bar beside a block** — a rule down the left
side of a quote or a callout. It is not an edge, since the other three sides are not
drawn; not a division, since nothing is on the far side of it; and it carries no label,
so it says "different" without saying how. It is also the default in every generated
interface, which is why a page carrying one reads as generic however carefully the rest
is drawn. The same test applies to a lone object parked at one side — an icon in a
callout's gutter, a glyph beside a heading.

Two components used to break it and no longer do: `.cf-prose__note` opens with a label
rule instead of a 2 px bar, and `.cf-quote` has no rule of its own at all — the type goes
one step up and the attribution closes the block under a hairline, the same way every
other caption in an article does. → `foundations/geometry.html#where-lines-go`

Grids are the exception that proves the test: `.cf-blog-grid`, `.cf-team-grid` and
`.cf-subdiv` each put two borders on the container and two on the cells, which *looks*
like the banned declaration and is the opposite of it — the finished field carries one
hairline everywhere instead of a doubled seam. Judge the drawing, not the declaration.

## The field

`foundations/field.html` is the chapter for the one thing the brand had claimed since its
first line and never drawn: the space. The manual's *Isometrie-Raster* plate is a **ground**
— a rhombic lattice running to all four edges with the cube and the cylinder standing on it
— and every spatial object in the system is cut from that lattice while the lattice itself
was invisible. `.cf-ground` is it, as a surface.

It does not break the rule above, and it is worth saying why, because it is a page full of
hairlines that are none of the three. A lattice line is not a line **in the layout** — it
draws no edge and divides nothing. It is a **material**, the way the grain on the page wash
is a material: a texture on the ground, under everything, at a tenth of an ink. The test in
that section is about lines that carry meaning; this one carries surface.

Two gradients drawn along `--angle-b` and its mirror, one shared stop list, a step of
`--field-unit / √5` because two families of lines that miss the lattice point are a moiré
rather than an isometry, and 1 px of contour at every cell size — which is the reason it is
a gradient and not a tiled SVG, since scaling a tile scales its stroke. `.cf-ground--lit`
masks it with a 2:1 pool of light that travels down the surface on a `view()` timeline, so
the floor materialises ahead of the reader and dissolves behind them.

The ink is capped at 10 % black, and the cap is measured rather than chosen:
`--text-secondary` on CF-Grau **under a lattice line** is 4.71:1 there and 4.51:1 at 12 %.
Every later state only removes ink — the lit variant masks, nothing composites over — so
that one row bounds every variant and every frame by construction.

**Its first application is the wallpaper**, which is the manual's other unused chapter.
`assets/img/wallpaper/` holds three hand-drawn SVGs — 16:9 dark, 9:19.5 light, and a
video-call background that gives up the middle of the frame, its brightness and the
bottom-left corner for reasons the page states. No type in them, no raster, no dependency.

All three carry the page wash's own grain, and two of them only since it was measured. A
wallpaper is the worst case the wash already solved — a member of the light family across a
whole screen with nothing over it — and the two **dark** files shipped without any dither at
all: 53.1 % of the video-call frame sat in a flat plateau of eight pixels or more, one of them
running its full 1080 px height. The strength does not carry over from the wash, because the
grain's own mean is a **floor lift**: 8 % costs nothing on a ramp ending at white and is the
first thing you see on a ground whose job is to stay black. So the rule is the least grain that
clears the banding — 8 % on the wash, 4 % on a dark ground, where the second four per cent
moves the banded area 0.6 % → 0.4 % and mean luminance 12.84 → 16.31.

All three also draw a CSS ramp by hand — `--spectrum-stops`, `--foil-stops`, `--foil-ink-stops` —
and all three were written before the two foils were put on the polar path, so the drawings kept
the chord the tokens had already left behind. They carry the arc waypoints now: same colours,
same order, one stop per turning leg at its own OKLCh midpoint. Measured against the files
before, 4 to 6 levels at most and the picture's peak chroma unchanged at lime's own 0.2201.
→ `foundations/field.html#wallpaper`

**The field is not on either designed page.** Neither mockup draws a lattice, and the
material wins over an improvement. It ships as available material with the wallpapers as
its sanctioned application; putting it behind a section of the Landing Page is a designer's
call, not a routine's.

## The presence ladder

The *Formsprache > Linien* plate is drawn twice and the system had only implemented the
top half of it. Above: four line types side by side, equals, each with a use — which is
what `foundations/geometry.html` catalogues. Below: **one** object, a rhombus with an
ellipse in it, drawn four times along a single dotted axis, solid and small at the left
and 1-4 and huge at the right. Four types, one figure. Read across, it is a thing coming
into being.

So the four types carry two registers, and they do not conflict. A line has a **use** —
where it is allowed to appear — and, when the same object is drawn more than once, a
**rank**. The second register is only ever legible in a state, which is why no static page
had needed it: `--presence-present` (solid) is here, `--presence-absent` (1-4) is not here
yet, and an object may move *along* the ladder but never across it. A thing that has not
arrived is the same drawing as the thing that has, one rung down — same box, same size,
same place.

That is the whole argument against the grey slab every other system loads with: it is not
a low-presence drawing of anything. `components/arrival.html` is the chapter —
`.cf-arrive` is the pending end of the ladder (contour, no fill, one light crossing it at
`--angle-b` above the contour, because the light layer is layer 5), and `.cf-progress` is
the ladder traversed: solid behind the head, 1-4 ahead of it, and the head is the lattice
cell filled with lime. One line changing type as it is crossed.

The light is capped at `--arrive-light-peak`, 0.18. Light sits above the contour, so the
band lightens the ghost, and that is the one thing here that could fail in frames too
short to catch in a screenshot — so it was measured. Composited in sRGB, which is how CSS
composites, the whitest stop over the blackest contour on CF-Grau gives 9.51:1 at 0.18 and
does not reach the 3:1 floor until 0.52; sampled off rendered pixels across eight frames of
one period, the worst inked pixel on the shipped ghost is 9.57:1. So contrast is not what
chooses the number — restraint is, and 0.52 is the ceiling it must never cross.

**Nothing dynamic ships here,** so no page carries one of these states today — the same
way `patterns/news.html` renders page 1 of 11 flat and the server owns the paging. What
the chapter fixes is the drawing and the contract; `components/arrival.html#who` lists the
three places the behaviour will land.

## The construction layer

`--presence-absent`'s own comment in `tokens.css` names three jobs for the rung and the
first of them is **construction geometry**. Every consumer it had was the fourth thing the
comment does not mention — the not-here-yet register on `.cf-arrive`, `.cf-progress` and
`.cf-line__trace--ghost`. The word was in the token and the drawing was nowhere.

`foundations/construction.html` is that drawing. Every plate in the brand manual shows how
it was made: the mark inside a measured frame on a grid of X, the *Winkelraster* as a star
of rays with the isometric rhombus laid over it, the illustration example carrying the
angles it was struck at. The manual is not a gallery of finished objects, and for a company
whose first line is *Find the answers* that is the argument rather than the decoration.
The website had only ever shipped the object. `.cf-construct` is a second drawing behind
the first, in the first's own coordinates, dormant until a reader asks — the rays it was
set out along, the cells it was cut from, the points where those meet, and the measures.

**It reaches the website on `patterns/404.html`**, and until it did, the layer had three
consumers and all three were documentation about the system. A material whose whole
argument is *show the working*, appearing only in the chapter that explains it, is the
same shape of thing as the core on Über uns before this chapter existed: real, and
reaching nothing. The error page draws a row of identical units on the ground plane with
one of them missing, and it had carried its own construction since it was written — `u =
60`, the origin at the empty socket's left corner, the four angles and nothing else — **in
a source comment**, which is the one place a construction cannot be read. It is drawn now:
the eight rays of the *Winkelraster* through `(200, 340)`, the setting-out point as a ring
around the corner dot the object kept, and the unit measured at `2u` on the one unit you
can see through. Three of the eight rays carry something — the datum is the row's standing
line, the two at 26.57° are the empty socket's left edges, the vertical is the missing
unit's plumb — and the other five run out of the frame carrying nothing, which is the
isometry stated as a fact rather than claimed.

A 404 is the one address where a reader has nothing to do, and the subject of that drawing
is already an absence. **Two marks are deliberately not there.** No cell: all three ground
cells of the row lie under an object or under the lit socket, so the mark would draw
nothing anyone can see — the cost of *it paints under the object* when the object is
opaque. And the measure stands in the void above the row rather than in the empty band
below it, because that band already carries the drawing's *Leerstelle* annotation; at 375
the leader shortens, the label travels left, and two label rules in one band are a
collision at some width even when they clear at the width you tested.
→ `foundations/construction.html#shipped`

**The rank is the line type, not the ink**, and that decision is what makes the layer cheap.
The obvious way to hold construction back is to draw it fainter, and that loses the
distinction in the two modes that discard ink strength — forced colours remaps authored
colour, a printer renders a 20 % black as a grey mesh. The presence ladder is a ladder of
*dash patterns*: same box, same size, same place, one rung down. So the working is drawn in
`--border-strong`, the same contour ink as the object, and told apart by `--presence-absent`
alone. Nothing had to be measured for contrast that the contour had not already been
measured for, and on paper the layer arrives whole.

Forced colours still needs one line, and not the one that was expected: **the mode does not
force SVG paint**, so a stroke authored as `--border-strong` stays `#000` on a dark system
canvas and the whole working disappears. It rendered as a mark on nothing, and
screenshotting the logo plate in the dark palette is what found it. What did come through
unaided is the rank — a dasharray is not something the mode touches — which is the half
that would have been expensive.

**`--angle-neutral` has a consumer.** The token had a definition in `tokens.css`, a row in
`foundations/geometry.html`'s angle table and **zero** uses anywhere in the tree: no
stylesheet, no page, no drawing named it. The *angle* was not absent — 45° is written as a
literal four times in the shipping stylesheets, inside `--iso-transform` itself, the
checkbox's tick, the radio's rhombus and one act rule — but every one of those is a
rotation applied to a mark, and not one is a line struck at 45° across a drawing, which is
the only thing the plate uses the angle for. On the *Winkelraster* the 45° rays are drawn
dotted beside the solid isometric pair: they are construction, and in a 2:1 system nothing
is ever built on them, so a system that never draws construction has nowhere to put the
angle. The specimen makes the point by standing on it — two of its eight rays leave the
setting-out point and become edges of the object, and the other six run out of the frame
carrying nothing.

**A measure is not drawn.** Every label here was an SVG `<text>` first, and a phone is what
that costs — a 22-unit label in a 780-unit `viewBox` rendered at **7 px** on a 375 frame,
below anything this system sets type at. SVG text is drawn *in* the user coordinate system
and no unit survives the transform. So the labels are HTML over the plate, positioned in the
drawing's coordinates as percentages: `__figure` is `width: 100%` with no height, so the
plate's box *is* the `viewBox`'s box and `--x` / `--y` are
`(coordinate − viewBox min) / viewBox extent`. They take `--text-xs` and the mono face, they
grow with the reader's own text size rather than with the drawing, and they are selectable —
which on a site named after find-in-page is not a small thing. That construction is
`check-label-frame.py`'s subject and this is its third member: registered UNSIZED, and the
first one that carries a `viewBox` **per instance** rather than one, so RULE 1 reads the
other way for it — a divisor in a material's rule is the finding.

**Its first application corrected the chapter it was drawn for.**
`foundations/logo.html#construction` puts the symbol on its unit, and the plate the page had
always named — *Logo Design > Konstruktion* — is the plate it had never drawn. The page said
“the construction is based on the unit X — the height of one bar of the symbol. The symbol is
8X wide, the horizontal lockup 10X.” Measured off `cf-symbol-black.svg`, every clause of that
is wrong except the first six words: **X is 60** in the symbol's own 600 × 480 units, the
frame is **10X wide and 8X tall**, one bar is **2X** thick and the gap between the bars is X.
The horizontal lockup is 3331 × 480 — 55.5X — and has no round measure in X at all, because
the wordmark's length is set by the letters and not by the grid. Every number solves out of
the path data: the exported paths round each acute vertex with a 2-unit fillet, so no point
in the file sits on the frame and each tip is the intersection of the two edges that meet
there — (0, 240), (480, 0), (600, 60), (480, 480). All four land on a node of the grid.

## The found state

`foundations/found.html` is the chapter for the thing the brand is **named after**. Control-F
is find-in-page, the site's whole argument is that data can be found in a space rather than
read off a sheet, and until this chapter the system had no drawing for a match. The platform
gives an author four registers for *this is the thing you were looking for* and exactly one of
them was styled here: `::selection`. `<mark>` was UA yellow, `::target-text` was UA yellow, and
`::highlight()` had no names registered against it at all.

All three of the missing ones became Baseline inside the window this system was built in —
scroll-to-text-fragment March 2025, the Custom Highlight API June 2025, `hidden="until-found"`
December 2025. Finding used to be something a browser did *to* a page. It is now something a
page takes part in.

**What the drawing may be made of was decided from outside, and it selected for the language
rather than bending it.** Highlight pseudo-elements take a closed property list so the browser
can repaint a moving highlight without relayout: colour, background-colour, `text-decoration`
and its longhands, `text-shadow`, the text stroke properties. No border, no outline, no
padding, and **no `background-image`** — which makes the found state the one surface in the
system that may not carry a gradient. No foil, no light ramp, no member of the family. Told it
may have one line and one flat colour, this system draws the line first and treats the colour
as light, which is what every other page already says.

| | |
|---|---|
| **every match** | The **ground line** alone: `text-decoration: underline`, `--stroke-2`, in ink. An isometric object has no bounding box — what places it is the lattice edge under it, which is how every object in `foundations/illustration.html` stands. A match is a word standing on one. |
| **the current one** | The same word with `--found-light` behind it. Material layer 5 sits under layer 6, so a lime fill behind text is the light layer in its correct place. |

Two rungs, one drawing, which is the [presence ladder](#the-presence-ladder) read as attention
rather than as arrival — and it settles the lime budget without an exception. One lime moment
per screen is a rule about *composition*; a result set is answered, not composed. A page with
twelve matches has one lit match and eleven contoured ones, so the budget is satisfied by the
drawing rather than waived for it.

**Contrast is carried by the ink, not by the fill,** and that is why the ground line is not
optional. A custom highlight owes two figures — 4.5:1 for text on the highlight, 3:1 for the
highlight against the surface around it. Black on lime is 18.51:1. Lime on CF-Grau is 1.37:1
and on the white end of the wash 1.13:1: the fill cannot hold that boundary at either end of
the page, at any opacity, because lime sits at 87.5 % of white's luminance, which is what makes
it light and what makes it useless as an edge. Schwarz measures 13.48:1 and 21:1 across the same
two ends. In the same stroke that discharges *never carry a state by colour alone* — the rule
makes the mark, the fill ranks it.

Underline **plus overline** was built first and is the obvious answer: two rules, the cell's top
and bottom edge, the only box a highlight is allowed. It was dropped after looking at it. There
is no `text-overline-offset`, so the underline can be pushed clear of the descenders and the
overline lands on the font's ascent well above cap height, reading as a detached rule floating
over the word. An asymmetric band is worse than no band. The weight is 2 px rather than the
system hairline for a different reason: `a:not([class])` is already a 1 px underline at 0.2em,
one notch inside the mark's 0.22em, so at the hairline a match and a link would be the same
drawing.

Three more things the chapter settles:

- **`<mark>` is held to the pseudo-element's means.** It is an element, so `.cf-mark` *could*
  carry a real border, padding and a 2 px corner. `::target-text` cannot, ever, and two drawings
  for one meaning is worse than one constrained drawing. A match looks the same whether the
  server marked it, a script registered it or the URL arrived carrying it.
- **Every pseudo-element gets its own rule, and the repetition is load-bearing.** A selector
  list is not forgiving: one pseudo-element the browser has never heard of drops the whole rule.
  `::target-text` is nine months older than `::highlight()`, so a list naming both would have
  taken the better-supported half down with the newer one in exactly the browsers that needed
  the fallback. `:is()` does not help — pseudo-elements cannot appear in it.
- **The system never intercepts `Ctrl`+`F`.** It is the obvious joke for a company called
  Control-F and it is the wrong thing to build: the browser's find is faster, works before any
  script has run, reads the whole page rather than one container, and is the one keystroke a
  reader can rely on everywhere. A site search field is an addition to it, not a replacement.

**In forced colours, `Mark` is a plate colour and not an ink colour** — one answer, applied to
all five rungs. `Mark` is yellow and `MarkText` black in *both* forced palettes; they are the
only pair in this drawing that does not flip, while `Canvas` and `CanvasText` do. So `MarkText`
holds only where it sits **on** the `Mark` plate, and everything the drawing puts outside that
plate takes `CanvasText`: the whole contour rung, which has no plate, and the ground line of the
light rung, which hangs below the plate on the page itself. That is the value the rest of the
system already means by *ink in this palette* — `.text-foil` takes it and `.rule` redraws itself
in it.

The rung that found this had been **absent, not faint**. Rendered rather than computed —
Chromium 149 and 151, `forced-colors: active`, `prefers-color-scheme` light and dark,
`foundations/found.html` served and screenshotted, pixels read back — the dark palette returned
one colour and 100 % `Canvas` for `.cf-mark`: the specimen sentence read *"Every match is the
______ alone"*, with the marked words gone from the page. `color: inherit` does not inherit
under forced colours; the mode re-forces the computed value, and for a `<mark>` Chromium forces
it to `MarkText` — black ink under a black ground line on a black `Canvas`. The declaration said
`color: inherit` and the computed value came back `rgb(0, 0, 0)`, which is why only a screenshot
could find it. The light palette was correct throughout, which is how it shipped.

**The backplate is painted over the element's own background**, which is the second half and the
one that arrived from a report that both element rungs were black blocks under the dark palette.
Chromium lays an opaque `Canvas`-coloured plate behind every run of text in this mode, and the
plate belongs to the *block container* that lays the text out, painted in that container's
background phase. An inline `<mark>` in a paragraph is not that container, so its yellow goes down
on top of the backplate and survives — which is why every match the system ships renders correctly
in both palettes, and why the report again named a rung that was not the one failing. Blockify the
mark and the container *is* the mark: measured in Chromium 151, a `.cf-mark--current` that is a
flex item, a grid item or `display: block` loses its plate in both palettes and, in the dark one,
loses everything. `forced-color-adjust: none` stops the backplate and does not leave the reader's
palette, since every value in those two rules is a system colour keyword; both element rungs carry
it now, the blockified cases arrive at the inline drawing in both palettes, and the inline cases do
not move by a pixel. The rung that was really failing is [today in the
calendar](#a-month-is-a-page-of-days) — a `<time>` that is a flex item — and it carries its own
copy.

Not `ButtonFace`/`ButtonText`, where the current-page marker in `components/pagination.html`
went for the neighbouring finding and did not stay: measured on the same run, `ButtonFace`
resolves to the *same value as* `Canvas` in both palettes, so a plate painted in it is not a
plate. That marker is the blockified case as well — an `inline-flex` slot — and it now takes
`Highlight`/`HighlightText` under this same escape, the pair the mode reserves for *the selected
one of a set*. One mechanic, two pairs: the escape decides whether a plate survives, the pair
decides what the plate says. And **the three
highlight pseudo-elements are not styleable in forced colours at all** — Chromium paints
`::target-text`, `::highlight(cf-found)` and `::highlight(cf-found-current)` with the UA's own
`Highlight`/`HighlightText` and discards every author declaration. Four candidates rendered
identically, the two rungs collapsing into one plate with no ground line; re-measured when the
escape went onto the element rungs — against the rules as they stand, against the same rules
carrying `forced-color-adjust: none` *inside* the pseudo, and against magenta and lime, colours no
palette contains — all three came back byte for byte identical in both schemes, `forced-color-adjust`
not being on the closed list of properties a highlight pseudo accepts. The single lever that
works is `forced-color-adjust: none` on the *originating element*, which would mean setting it
on the running text of the site — opting the page out of forced colours in order to keep a
drawing about accessibility. It is not taken; the escape on the element rungs is the opposite
trade and affordable because it lands on the word rather than the prose around it. Those three
rules are written as a conforming engine would paint them and are inert on Chromium today.

`::selection` is the one exception on the page and keeps its solid lime with no contour. Its
boundary against CF-Grau is the same 1.37:1 and that is documented rather than fixed: a drag is
transient, self-caused and under the reader's own hand, so the platform's convention wins over
the system's consistency. Every mark the reader did *not* make carries the ground line.

`hidden="until-found"` has no application in the system today, because the one place the site
collapses real prose is the accordion, which is `<details>` and already opens on a find. The
chapter documents it so the first thing that does need it does not reach for `display: none`.

**The chapter used to say nothing dynamic shipped here** — the same standing
[the field](#the-field) and the arrival ladder still have. That is no longer true, and the
next section is why.

## Contour here, light there

The found state settled what a match looks like and then had no page to be on: the system
could draw an answer and had nowhere to answer anything. `components/search.html` and
`patterns/suche.html` are that page — the surface the company is **named after**, and the last
major one the site was missing.

`.cf-result` is not a card. No box, no fill, no corner: a block of type standing on a rule,
which is the claim the found state already makes about a marked word one scale down — an
isometric object has no bounding box, what places it is the lattice edge under it. Every result
draws its own bottom rule, the **last one included**, so the register closes; the interior rules
are divisions and the closing one is an edge, which is both sanctioned uses in
[where a line may go](#where-a-line-may-go). It is the one place the system deliberately
does not follow `.cf-blog-card:last-child { border-bottom: 0 }` — that rule exists because the
blog grid's container already draws the bottom edge, and this list has no container.

**The decision the found chapter had left open is which match is lit.** Its two rungs are
contour for every match and light for the one the reader is *on* — exactly one, ever. On a
result page the reader is on none of them: they have not chosen, which is what the page is
for. So a result set is drawn **entirely in contour**, and the page's one lime moment goes
where it goes on every other listing, the call to action in the footer.

The light is not withheld, it is **deferred**. Every result link carries a `#:~:text=` fragment
quoting the phrase in its own excerpt, so following one lands on the destination page scrolled
to that phrase with it drawn in the lit rung by `::target-text` — which `base.css` has styled
since the found state shipped, and which the destination implements nothing at all for. The two
rungs turn out not to be two treatments of a word on one page. They are **the question and the
answer, one page apart**: the register of candidates is contour, and the thing you were looking
for lights up when you get there. That is the brand's own argument — data can be found in a
space rather than read off a sheet — running across a navigation rather than inside a paragraph.

Two things about the fragment, because both fail silently. A literal hyphen inside the quoted
phrase must be written `%2D`, since `-` is the delimiter of the `prefix-,start,end,-suffix`
form and a browser that misreads the phrase simply matches nothing. And the fragment matches
the **first** occurrence, so the quoted run has to be unique on the target page — four to six
words is the working band, and `textStart,textEnd` pins both ends where it cannot be.

**The main navigation does not carry the search, and that is a designer's call left standing.**
Both Figma mockups draw a six-item nav bar measured to `417 × 41`; a seventh item is a change
to the drawing, not to the code. `patterns/404.html` routes to it instead — first in the list,
because it is the only route on that page that does not guess what the reader was after.

## A month is a page of days

`components/calendar.html` is the second application of the found state, and the first thing in
the system that had to draw **time**. It is worth its own section for one reason: it introduces
no drawing. There is no new geometry in it, no new colour, no new token, and one custom
property that is a floor already written twice elsewhere. The whole component is three existing
components in an arrangement — which is the test a system passes or fails when something new is
asked of it.

| | |
|---|---|
| the frame | `.cf-table`'s. Ruled rows, nothing vertical, tabular figures, the caption as the accessible name, the scroll box with its three attributes. A month **is** tabular — the column is a weekday, the row is a week — so `<th scope>` does the work and no script has to. |
| the slot | `.cf-pagination__page`'s. 2.75 rem, a mono numeral centred in it, no contour at rest and the contour arriving on hover and focus, because at rest a number is type and under the pointer it is a target larger than its glyph. |
| the mark | the found state's, at numeral scale. A day something stands on is a numeral on its ground line; **today** is the same numeral with the light behind it. |

**The brand is named after finding a thing in a page, and a month is a page of days.** The day
the reader is standing on is the match they are standing on, so today is not a new state — it is
`::target-text` at the scale of a numeral, held to the same `--found-*` tokens rather than to a
shared selector, which is the mechanism `base.css` already states for the five rungs it declares
itself. It settles the lime budget the way [the found state](#the-found-state) does, and one step
harder: a month has exactly one today, so a calendar with four marked days composes one lit
numeral and three contoured ones *by arithmetic*. Nothing has to be kept.

Three absences, each a rule from somewhere else. **No weekend column** — it could only be a
vertical rule or a column fill, and a fill doing a hairline's job is the zebra stripe the table
refuses. **No days of the neighbouring month** — the only way to say a cell belongs to another
month is to grey it, and `--text-muted` on CF-Grau is 2.0:1, the one step this system does not
have; the cells before the first and after the last are empty, and the way out is a
`.cf-pagination` above or below the grid. **No entry titles in the cells** — a 44 px slot cannot
hold a sentence, so the grid is an *index* and what stands on a day is the register, which gains
its third consumer, `.cf-event`, beside `.cf-result` and `.cf-vacancy` for three words in seven
selector lists and not one declaration.

**Nothing dynamic ships here either.** `aria-current="date"` is a claim about the day the page is
*served*, so it is the server's to write, and the specimen fixes a month and lights one day in it
— the same standing [the presence ladder](#the-presence-ladder)'s states have and the news
archive's paging has.

One thing was measured, deferred, and has now been paid. Under forced colours today takes
`Mark`/`MarkText`, the pair `<mark>`, `::target-text` and both `::highlight()` names already take,
and for a while this component recorded that the pair does not paint under the dark theme and sent
the fix to `base.css` "to all five rungs at once". Re-measured in Chromium 151 in both schemes, the
found state's own inline rungs paint correctly in *both* palettes and always did; the lit day did
not. **The pair was never the fault; the box was.** Chromium lays an opaque `Canvas`-coloured
backplate behind each run of text in this mode, and it belongs to the *block container* that lays
the text out — so an inline `<mark>`'s plate goes down on top of it and survives, while this
`<time>`, a flex item of an inline-flex day, is its own block container and had the backplate land
on top of its plate: white in the light scheme, where the ink still read, black in the dark one,
where it did not. `forced-color-adjust: none` stops the backplate without leaving the reader's
palette, because every value in the rule is a system colour keyword and still resolves to the
theme. The lit day is now a yellow plate with a black numeral and a black rule in both schemes.
What was deferred to `base.css` was one declaration and not a change of pair — the two element
rungs there carry the same escape, where it changes nothing that ships today and covers the day a
match is blockified. `.cf-pagination__page[aria-current]` sits on the same mechanism and is the same
blockified case; it took the same escape and a different pair, `Highlight`/`HighlightText`, because
*currently selected* is not *currently matched*.


## The last route with nowhere to go

Every nav bar and every footer in the system links `/karriere`. `patterns/404.html` offers
it as one of four ways out, and `patterns/kontakt.html` sends applicants there in body copy
— *"Bewerbungen bitte über Karriere — dort steht, was wir für eine Bewerbung brauchen und
was nicht."* It was the one item in the primary navigation with no template behind it, and
the only promise on the site made to a page that did not exist. `patterns/karriere.html` is
that page, and its fourth section is that sentence, answered.

**The register it needed is not a new drawing.** `.cf-vacancy` is `.cf-result` — every rule
for the row, the sheen, the mono line, the title, the link and the excerpt names both, the
way `.cf-prose table` names itself alongside `.cf-table`. A job opening and a search hit are
the same object at the level the drawing works on: a mono line, a linked title, a couple of
sentences standing on a hairline. Writing that out twice would be two things to keep in step.

One part is genuinely new and it is the only thing declared on its own: `.cf-vacancy__facts`,
a `<dl>` of the four questions every candidate asks before reading a word of the description
— Standort, Anstellung, Umfang, Start. It is `.cf-contact`'s drawing, a mono term over its
value, turned along the row rather than down a column, because four facts stacked under every
opening make the register three times as long as its content. The column gap beats the row gap
by a factor of eight so a pair reads as a pair before the row reads as a row, and there are no
rules between them — a line there would be neither an edge nor a division nor a label rule.

**Structured data is the one thing this page deliberately does not carry.** Google's job
posting documentation is explicit that `JobPosting` markup belongs on a page describing exactly
one opening, one URL per opening, and that a careers page listing several must not carry it.
So the register stays plain HTML and links out; the JSON-LD goes on `/karriere/<rolle>`, where
every field in it has to match what the reader sees. That, the four placeholder postings and
the `jobs@control-f.de` mailbox are recorded under
[Before launch](#before-launch). → `components/vacancy.html`

## The two routes the law requires

`/datenschutz` and `/impressum` were the last two addresses in the system with no
template behind them, and they are not ordinary gaps. Every nav bar links neither and
every footer links both; between them the two were referenced 39 times, and the consent
layer — the one thing on the site that exists because a statute says so — sent readers
to `/datenschutz#cookies` nine times over. A banner that cannot legally be omitted was
pointing at a page that did not exist.

**Neither page needed a new drawing, and finding that out was most of the work.** A
privacy policy is a long document read in sections, which is what `.cf-article` already
is: the index rail, the sticky register, `.cf-prose` beside it. An Impressum is a set of
named facts, which is what `.cf-contact` already is — `/kontakt`'s contact column, the
same mono term over its value, only complete. The one decision either page makes on its
own is whether to carry an index at all, and `components/article.html` had already
written the rule: nothing under four sections, because a three-item index is furniture.
The policy has twelve and carries one; the Impressum has three and does not.

**The inventory moved rather than being copied.** `components/consent.html` used to
render the six entries itself, with a note giving the reason — copy that will be replaced
wholesale should exist once, and the page that should hold it did not exist. It does now,
so the component page states the shape of the table and links to the address the dialog
routes to, and there is still exactly one copy. The count in a caption and the count in
`.cf-consent__meta` still have to move together; that is unchanged and is the one piece
of arithmetic no script checks.

Two things the pages take from what the law currently is rather than from what most
German sites still say. **There is no ODR link.** The EU Commission's online dispute
platform stopped accepting complaints in March 2025 and was switched off on 20 July 2025;
the link that imprints have been required to carry since 2016 is now dead, and a dead
link to a dispute body is worse than none — what stays is the § 36 VSBG declaration.
And **there are no liability boilerplate paragraphs**. *Für die Inhalte externer Links
sind ausschließlich deren Betreiber verantwortlich* restates § 8 DDG and changes nothing;
the section says instead who owns the pictures and where to report a mistake.

The consent banner is on both pages, and on the policy page it is load-bearing twice:
`cf-consent.js` returns early when no banner element is in the document, so without that
block both the footer button and the *Einstellungen ändern* button inside section 05
would be dead controls — on the page the banner itself sends people to.

## Naming a part of a drawing

`components/annotation.html` is the chapter for the thing that sat between the two the
system already had. It could mark a found **word** — `foundations/found.html` — and it
could draw an **object** — `foundations/illustration.html`. It had nothing in between: no
way to say which *part* of an object you are looking at. Fifteen isometric objects ship
carrying `.cf-iso__node`, a black dot at a vertex, and not one of those dots said anything.

`.cf-annot` is the layer that gives them words, and it is the found state one scale up.
Two rungs, the same two: every annotation is drawn in **contour**, the one the figure is
about is **lit**. A drawing with six notes composes one lit anchor and five contoured ones,
so the one-lime-moment budget is satisfied by the drawing rather than waived for it — the
same argument the found state makes about a page with twelve matches.

**The leader is a lattice step, and that is the whole geometry.** Technical drawing has
required for a century that a leader run at neither horizontal nor vertical, so it can be
told from the object it points at; this brand sanctions four angles, two of them oblique.
The two rules land on the same drawing. So a leader is declared as a step — `--annot-mx`
across by `--annot-my` down — and its slope is **read off that step** rather than typed in:

| | |
|---|---|
| the angle | `atan2(--annot-my, --annot-mx)`. (2, 1) resolves to 26.565° and (1, 2) to 63.435°: the only two obliques the brand owns, and the only two a leader can be. A leader off the lattice is not expressible. |
| the length | `sqrt(mx² + my²) × u`, which is why both steps are the same length — they are the same diagonal. |
| left | a mirror, `scaleX(-1)` ahead of the rotation, not a second angle. Four directions cannot end up on three slopes. |
| the shoulder | the label's **own bottom rule**. Line and word are one mark, which is the third sanctioned use of a line — the label rule. Drafting asks for a level elbow at the note end for its own reasons and gets the same drawing. |

This is the first place the system states an isometric angle as the **ratio** it has always
been rather than as a rounded degree, and it is worth being exact about what that buys.
26.57° against 26.565° is 0.005° and no screenshot will ever show it. What it buys is that
the two cannot come apart: change the step and the slope follows, where before a leader
could be moved onto a different step and quietly keep the old angle. CSS trigonometry has
been Baseline since March 2023 and `sqrt()` since December 2023; both literals stay in
place as the fallback, because an angle is not a place to find out a browser is old.

**Below 28 rem of its own container the layer stops being a callout and becomes a legend.**
A note needs clear ground to point into and a 320 px drawing has none; overlapping two notes
is worse than not drawing the leaders at all. The set flows under the figure as a row of
marks and words, and the rule under each label goes with the leader — an underline with no
line running into it is not a label rule, it is decoration, and at that size it would be
taken for a link. The threshold is on the **figure**, never the viewport: what decides
whether a callout fits is the width of the drawing.

**Its first application is `patterns/404.html`,** which is the one page whose drawing is
already about something not being there. The empty socket is the figure's lit element, so
the note that names it — *Leerstelle* — is drawn in contour: the light is spent on the
object and the note points at it rather than competing with it. → `components/annotation.html`

## A mark drawn from a name

`components/signet.html` is the system's answer to an item that needs a face and has no
photograph. Nine plots of the isometric lattice, blocks standing on some of them, one face
carrying the light — **the object is the stack on `foundations/geometry.html#objects` and
not a new shape.** What the name decides is only where the blocks stand and how high, which
is the one degree of freedom that object already had: `01-discovery.svg` is three stacked
cuboids, and a signet is a nine-plot field of them.

**The alphabet is finite and its density is fixed.** The nine heights are a permutation of
one multiset — `0 0 0 1 1 2 2 3 3` — so every mark in the set has exactly three empty plots,
exactly two towers at full height, and exactly the same quantity of ink. That is
9! / (3! 2! 2! 2!) = **7560** arrangements, and it is the whole difference between this and
an identicon: the usual generator hashes into free parameters and its density swings from
nearly blank to nearly solid across the set, which is why identicons read as a family of
hashes rather than as a family of marks. Fixing the multiset moves the variation into
arrangement, where the construction system can still govern it. The number is computed from
the multiset by `CFSignet.count` rather than written down, so the documentation cannot drift
from the array.

**One lime moment, and the ink form is the default.** Of the two full-height towers the
light goes on the frontmost and never on both. But a wall of signets is the one place in
this system where an object could break the screen's lime budget twenty times over without
any single mark being wrong, so the generator emits `--ink` unless it is asked otherwise and
the light is opt-in, once. The lit face carries the family's ramp on the near rake, with the
19 % waypoint; its axis is the designer's own scaled by 0.15, which means **lime itself never
lands on the face** — what lands there is the leg just after it, falling to Glas by the
opposite corner. That is true of the designer's stack in the same proportion, and it is what
the manual means by light as a temporary effect rather than a fill.

**Determinism is the point, not a convenience.** FNV-1a into an xorshift32 into a
Fisher-Yates shuffle: no table, no storage, and the same answer in Python — which is what the
share plates will need on the day they are written by a build script. Seed it with something
stable and unique, a slug or a path; never with a title, because renaming a thing must not
redraw its mark.

**Where it is meant to go, and the one thing standing in front of it.** The site ships **no
Open Graph metadata at all** — no `og:title`, no `og:image`, no Twitter card, on any pattern
page in either edition — so every link to control-f.de posted into LinkedIn, Slack or Teams
renders as a bare address today. The signet is the plate for that, and the text half of the
metadata is not blocked by anything. The image half is: every consumer of `og:image` requires
a raster and this repository has no build dependencies, so the three routes and what each
costs are written out on the component page. → `components/signet.html#launch`

## The line of sight

`foundations/sight.html` is the chapter for the half of the brand's own model that the
implementation had never read. Two materials already answer to where the reader is — the
foil turns its rake as type travels up the screen, the field slides its pool of light down
a section as the reader passes — and both are built on the same claim: **you see the
material as drawn when you are square to it.** 116.57° is head-on, and the rake flattens
towards 90° as the sight line goes oblique.

A `view()` timeline supplies that obliquity for free on one axis. But it measures the
*element*, and the model is about the *reader*; vertically the two coincide, because an eye
at the middle of the screen is the only assumption a stylesheet can make, and horizontally
they come apart the moment a viewport is wider than a headline. On a 1920 frame a title at
the vertical centre and hard against the left margin was drawn perfectly head-on while the
reader sat a foot to its right. `assets/js/cf-sight.js` replaces that assumption with a
measurement.

**The two squarenesses multiply, and that is the whole safety argument.** Summing two
swings could leave the band; a product of two numbers in `[0, 1]` cannot, so the rake stays
inside 90°–116.57° by construction and every contrast figure the foil has been measured at
holds unchanged and unre-measured. It is also the physically true composition — a foil is
head-on only when you are square to it on *both* axes, and being level with a sheet you are
standing beside does not let you see it face on.

The swing is also now **derived rather than asserted**. The comment in `base.css` has always
said the 26.57° between the endpoints is the isometric angle itself; the keyframes said
`90deg` and `116.57deg` and left that a coincidence a later edit could break. It is written
as `--angle-square + --angle-b` now, so moving the isometric angle moves the foil with it.

**What may answer to sight is a closed list, and it is short.** The angle a gradient is
drawn at, and the position of a mask or a light. Not colour, not ink strength, not opacity,
not a composited specular, and not the position or size of anything — content that moves
away from a pointer cannot be clicked. The rule behind the list is that *the reader's
position must never be able to change how legible anything is*, which is what makes every
measured floor in this system a floor under every frame of this by construction rather than
by inspection. Interactive surfaces are excluded outright: `.cf-btn--solid` reads the static
foil from `:root` and is left alone, the same way it is left out of the vertical swing.

`--field-light-x` is the one property of the four declared `inherits: true`, and the
asymmetry is forced rather than chosen — the pool is painted by `.cf-ground::before`, and a
script cannot set a property on a pseudo-element. That is a subtree invalidation per write,
which is why the pool is quantised to whole percent where the rake is quantised to 1/64 of
its swing. Both are damped by `--duration-fast`, which is what turns a quantised value into
a material with weight rather than one that teleports between stops.

Every fallback lands on the designer's own still, and the script gates itself on
`CSS.supports('animation-timeline', 'view()')` — the same test `base.css` puts on the swing —
so the stylesheet and the file cannot disagree about whether the vertical half is running.
A finger does not get it at all: it has no position between taps, and reading a touch as a
light source makes the page flinch every time it is scrolled.

**The phone gets it from the other end.** On a desk the eye moves and the screen stays; in a
hand the screen moves and the eye stays, and the angle between the line of sight and the
plane of the screen is the same quantity read from either side. That angle is the one a
holographic foil is read by — a foil catalogue is photographed tilting — and for as long as
every coarse pointer rested, the surface most readers hold was the one surface on which the
brand's north star could not happen. `cf-sight.js` now has two sources and runs exactly one:
the pointer where there is a fine one, the **tilt of the device** where there is not and the
orientation sensor answers without being asked for. The reach is derived, not picked: a sight
line makes `--angle-b` with a plane tilted `--angle-a` from square, so the phone shows the
flat 90° rake at 63.43° of tilt exactly as a desk reader a half-viewport to the side does,
and the script reads the token rather than restating it. The still is wherever the hand
settles — the departure is measured against a baseline that follows the hand with a
two-second time constant, because nobody reads at a fixed angle to gravity and a reader in a
chair or in bed is not looking at the page obliquely. Where a browser gates the sensor behind
a permission prompt, the source is declined outright: a prompt for atmosphere is a cost the
reader never agreed to pay, and sight is the last layer. The two properties it writes, their
ranges, their rest values and the closed list of what may answer to them are unchanged, so
no contrast figure moved. → `foundations/sight.html#tilt`

## Vertical rhythm

Every section opens with a `cf-section-header`, and **the header owns the air beneath
it** — no page sets that distance locally. There are exactly two cases, both measured
off the mockups:

| | |
|---|---|
| **default** | Content sits `--section-header-gap` (80 px) below the hairline. For content that is not itself a ruled box: the logo wall, the team strip, a block of copy. |
| **`--flush`** | The content below *is* a ruled container — process card, accordion, blog grid — and its own top border is the header's rule. The header drops its border and its gap so one hairline does both jobs. This is how all three are drawn in the mockups. |

Before this rule the same relationship was set six different ways across the two pages
(24, 32, 48, 64 px, plus two container paddings). If a section needs a different
distance, change the token — not the page.

Between sections the air comes from `.section`'s own `padding-block`, and three classes
decide which token an edge gets. All three are documented on `foundations/layout.html`:

| | |
|---|---|
| `.section` | `--section-gap` on both edges — so 240 px *between* two sections at the reference frame. |
| `.section--tight` | `--section-gap-sm` on both. The first section under a `.cf-page-header` (→ `components/page-header.html`). |
| `.section--flush` | `--section-gap` top, nothing at the bottom. The last section on a page, paired with `.cf-footer--detached`, which supplies that bottom gap instead. |

Horizontal rhythm has one rule of the same shape. Most things sit in a `.container` and
inherit the content column for free; the few drawn against a full-bleed box — the hero's CTA
and pause switch, the values section's counter and progress bar — have to name their own
inset, and **that inset is `--column-inset`, never `--gutter`.** The gutter is the outer
margin only while the container is still growing; past `--container-max` the container
centres and the column moves inward while the gutter stays put. All four were on `--gutter`,
which is right to within 0.8 px at the 1440 frame the mockups were measured on and wrong by
160 px at 1920 and 480 at 2560 — the CTA walking away from the headline it belongs to, the
counter and progress bar sliding out from under the rule they restate, in opposite
directions. Where an element *can* be put in the container it should be, and the Über uns
header object is that case; the token is for the ones that cannot.
→ `foundations/layout.html#column-inset`

The last pair is a biconditional and used not to be checked as one, and it has now been broken
from both ends. `patterns/kontakt.html` carried `--detached` over a normal `.section` and stood
its footer off at 240 px where every other page measures 120. `patterns/expertise.html` broke
the other half: `--flush` on a section with two more sections under it and an ordinary footer at
the bottom, which is the class doing its job in the wrong place — the pinned Felder track gave
up its bottom edge to a neighbour that was not the footer, and the one section boundary on that
page measured 120 where every other boundary on the site measures 240. Nothing looked broken,
which is the point: half a gap reads as a slightly tighter page rather than as a fault. Measured
across all eight pattern pages, the rhythm is 240 between normal sections, 200 after a `--tight`
one, 120 above every footer, and 80 from every section header's hairline to its content.

## Navigating the site

A static site normally navigates the way paper does: the sheet is thrown away and another
one is put down. That is the one thing this brand is not, so **navigation is drawn rather
than swapped.** One edge at `--angle-a` crosses the viewport, the arriving page appears
behind it, and `--gradient-foil` shows through a `--stroke-2` gap between the two pages —
a lit contour, drawn before the surface it encloses. The foil is one gradient across the
whole viewport and only two pixels of it are visible at a time, so the line changes hue as
it travels. That is the brand's north star obtained the only way a real foil ever gives it
up: by moving past it.

The nav bar, the footer and the documentation sidebar carry a `view-transition-name`, which
lifts them out of the page snapshot and leaves them standing perfectly still. The page wash
is `background-attachment: fixed`, so it is pixel-identical between any two pages at any
scroll position and the edge cannot be seen crossing it. The room holds; the contents of the
room change.

No markup, no attribute, no script — it is `@view-transition` plus four rules in `base.css`,
inside `prefers-reduced-motion: no-preference`. Where the browser has no cross-document view
transitions (Firefox today) or the reader has asked for less motion, navigation is instant,
which is what this site did before. → `foundations/transitions.html`

## Outside the page

Every other section here is about something a stylesheet draws. Four declarations are not:
they are read by software this repository does not ship — the browser's own chrome, the
reader's launcher, the OS compositor — and **the site carried one of them across 138 pages.**
`rel="icon"`, and nothing else.

**The one with a live fault behind it is `color-scheme`.** Chrome for Android's Auto Dark
Theme re-tints any document that has not declared a scheme, and every colour on this site is
derived: `--wash-stops` opens at `#CFCFD2` and lands on white, the ramps are held to the
OKLab path, thirteen contrast ratios are recomputed from the tokens on every run. None of it
survives an automatic inversion and none of it can see one — a desktop browser ignores the
feature outright, so the responsive sweep, every capture under `docs/`, the contrast register
and the runtime console all agreed the page was fine. It is the same shape as the viewport
directive the mobile chapter found: a control the reader owns, taken away where nobody in the
review is standing. `only light` is the opt-out, and `only` is a promise as well — the day
this system wants a night it draws one; what the keyword forbids is shipping somebody else's.

The declaration also decides the surfaces the stylesheets deliberately leave native: the
scrollbar, the form controls, the spellcheck underline, the canvas behind the page. **And
`[data-theme="inverse"]` had inverted every token this system owns and none of the UA's** —
a native control inside the footer was drawn from the reader's OS preference, on black.

    html                    { color-scheme: only light; }
    [data-theme="inverse"]  { color-scheme: dark; }

**The other half is the tile.** The manual defines five frames for the signet and the web had
built two — the square frame is the nav plate, the transparent frame is the favicon. The
App-Icon is the third the web needs, and the gap was already written down in the favicon's own
header, which argues the black plate *off* the tab strip on the grounds that it "reads as an
app icon". That hands the plate somewhere, and nothing was standing there.

`scripts/build-app-icons.py` renders it out of the signet and the light family's ramp with the
stdlib rasteriser the share plates already own — no dependency, no second drawing of the mark
— plus the manifest that names it, whose two colours are read out of `tokens.css` on every
run. The artwork is full bleed and square: **the platform draws the manual's radius**, because
a maskable icon is masked by the launcher and a radius baked into the tile comes back a
thinner, wrong one. `check-outside-page.py` renders the 512 tile in memory and measures the
farthest non-ground pixel from the centre — 32.5 % against the 40 % the maskable contract
allows — so the safe zone is measured rather than asserted.
→ [`foundations/outside.html`](foundations/outside.html)

## Before launch

| | |
|---|---|
| **The browser's own surfaces** | **Shipped 2026-09-02.** All 138 pages declare `color-scheme: only light` and a `theme-color` at the wash's first stop; the 132 outside `prototypes/` also declare `apple-touch-icon` and the manifest. `check-outside-page.py` derives the colour from `tokens.css` rather than reading the pages' copies of it, and measures the maskable safe zone on a live render. Nothing here is blocked: the tile and the manifest are generated by `build-app-icons.py` and gitignored, like the share plates. → `foundations/outside.html` |
| **Publica Sans** | Commercial licence required. Drop `PublicaSans-Variable.woff2` into `assets/fonts/`. Until then `--font-display` falls back to Geist. |
| **Geist / Geist Mono** | OFL, free. Self-host the `.woff2` files in `assets/fonts/` — deliberately **not** the Google Fonts CDN (DSGVO). |
| **Process illustrations** | Done. Built from the designer's source vectors in `assets/source/illustrations/`. The four documented deviations are listed on `components/process-card.html`. |
| **Partner logos** | The logo wall renders text placeholders; drop in the real SVGs. |
| **Open Graph and Twitter cards** | **Shipped 2026-09-02.** Sixty-six pages across both editions carry a canonical link, `og:type`, `og:site_name`, `og:url`, `og:locale` and its alternate, `og:title`, `og:description`, `og:image` with its type, size and alt, and `twitter:card` — thirteen pattern pages as authored markup, the rest written by `build-news.py`, `build-articles.py` and `build-stellen.py`, all four out of `scripts/og_meta.py`. `og:image` is a 1200 × 630 raster per route, drawn from that route's own signet by `scripts/build-og-plates.py` — a rasteriser over `zlib` and nothing else, which is route 1 of the three that were costed. Which pages carry a card is the page's own rule — a description and no `noindex` — and `check-open-graph.py` holds it in both directions, re-deriving every field rather than looking for the tags. **`og:url` and the canonical link name the page's shipped address on `SITE_ORIGIN`**, derived from the pattern's name by `og_meta.address()`, so the domain cutover to control-f.io moves every generated card and canonical with one line of `wrangler.toml` (the thirteen authored pages are edited alongside it, and the check fails if one is missed) — and the copy a crawler still holds at the old GitHub Pages address points at the new one. → `foundations/share.html`, and README.md's *Domain cutover* |
| **Team photos** | Seven named portraits ship on Über uns, each filed under the person in it, and four of them now have a 144 px avatar derivative beside them (`simon-144.jpg` …) for the strip and the byline. The placeholder-era `portrait-01…04-144.jpg` are still in the folder but no page names a person over them any more; a derivative for Robin, Marie or Birk is made the same way — the 440 px square on the head, columns 100–540 and rows 60–500 of the 640 × 800 frame, at 144 px — the day a page needs one. No shipping page carries the strip itself. → `components/team.html#strip` |
| **Team layout on Über uns** | The mockup draws that block as a full-bleed strip of 294 px cells running past the right edge — 4.9 of them fit a 1440 frame — and the implementation renders a contained field that wraps instead. The wrapping grid is the better answer for ten people and it is what ships, but it is an improvement over the material rather than the material. A designer settles it. → `components/team.html#rules` |
| **Consent copy** | The three categories, their retention periods and the six entries in the inventory are placeholders. A lawyer signs off the wording, and a real cookie audit replaces the rows. The columns — name, kind of storage, purpose, recipient, retention — are what TDDDG § 25 and Art. 13 DSGVO ask for and should survive the replacement. The anchor the dialog links to now exists — `patterns/datenschutz.html#cookies` — and the counts in `.cf-consent__meta` have to keep matching the list there. |
| **Legal copy** | Every figure on `patterns/impressum.html` and `patterns/datenschutz.html` is a placeholder in a correct shape, and the shape is the deliverable — a lawyer replaces the values, not the structure. Specifically: `HRB 000000`, `DE000000000`, the Amtsgericht, the photography credit, the 7-day log retention, the hosting provider's name, and whether Matomo and the LinkedIn tags are what actually ships. `datenschutz@control-f.de` is a fourth placeholder mailbox alongside `info@`, `presse@` and `jobs@`. The § 38 BDSG argument for having no data protection officer holds at ten people and stops holding at twenty. |
| **Consent record** | `localStorage` proves nothing to a supervisory authority. The decision needs logging server-side before launch. |
| **Contact endpoint** | `patterns/kontakt.html` posts to `/kontakt` and expects the server to validate, re-render the form with the reader's values and an error summary, drop anything that filled the honeypot, and serve the whole thing over HTTPS. The phone number on the page is a placeholder. |
| **Search index** | `patterns/suche.html` is one query rendered flat. The server owns the index and the whole answer: `?q=…` selects it, the matches are wrapped in `<mark class="cf-mark">` as the response is rendered, and every result link is minted with a `#:~:text=` fragment quoting its own excerpt — hyphens as `%2D`, the run unique on the target page. The query is reader-supplied text echoed into three places (the input's `value`, the `<title>` and the header meta) and has to be escaped in all three. Zero hits renders `.cf-error--inline` at `200`; the page is `noindex, follow`. → `components/search.html` |
| **News listing** | `patterns/news.html` is page 1 of 11 rendered flat. The server owns the paging: `?seite=N` selects the slice, `?thema=…` filters it, and both are reflected in the counters, the status line and which slot carries `aria-current`. Out of range should 404 rather than render an empty grid; a `?thema=…` that matches nothing renders `.cf-error--inline` in place of the grid, at `200`, because an empty answer is not an error. → `components/error-state.html` |
| **Open positions** | `patterns/karriere.html` renders four placeholder postings and prints their count in the page header; both are the server's, out of one query, the same standing the consent dialog's entry counts have. Each entry links `/karriere/<rolle>` and none of those pages exists yet — that is where the `JobPosting` JSON-LD goes, with a `validThrough` on every one of them, or a filled position stays live in search results. `jobs@control-f.de` is a placeholder and is written on the page three times, one of them the screen's only lime moment. When nothing is open the whole register is replaced by `.cf-error--inline` at `200`, not rendered empty. → `components/vacancy.html#launch` |
| **Status codes** | `patterns/404.html` is the page; the response is the server's. A missing address answers `404`, one that is deliberately gone `410`, a failure `500`. Serving the template with `200 OK` is a soft 404 — the address stays indexed and keeps being crawled. |
| **Redirects** | The old topic pages (Maschinenbau, Energie, Dienstleistungen, Experten) are gone. They need 301s to the new structure — a redirect that is available always beats an error page that is polite. |

## Language

The documentation is English. The pattern pages carry German copy, because that is the
language the site ships in — translating it here would invent content that does not exist.
Landing Page and Über uns take theirs verbatim from the Figma mockups; News overview,
Blog article, Suche, Karriere, Kontakt, Datenschutz and Impressum have no mockup and
their copy is written placeholder in the same voice. On the two legal pages that
placeholder is a stronger claim than elsewhere — the structure is meant to survive review
and the values are not. Colour
names (Glas, Violett, CF-Grau, Schwarz, Weiß) stay German everywhere: they are the brand's
names for them.

## Decisions that differ from the source material

These were judgement calls, each documented on the relevant page:

- **The nav bar and the logo lockup were pills and are now 2 px plates.** This one is a
  correction, not a judgement call — the implementation was wrong. Counted off the Figma
  exports: 170 `<rect>` elements across both pages, ten with a radius, every one of them
  `rx="2"`. The nav bar is `417 × 41 rx="2"` where a pill would be `rx="20.5"`; the logo
  lockup is `152.09 × 35.25 rx="2"` where a pill would be `rx="17.6"`. At that height a
  2 px corner in a compressed mockup JPG is indistinguishable from a capsule, which is how
  it got in. `--radius-pill` has been deleted rather than left unused. Buttons moved the
  other way, from 0 to 2 px — all three CTAs are `rx="2"` too — as did team portraits.
  → `foundations/geometry.html`
- **The blog container is `rx="2"` in the export and square in the code.** It is drawn as
  `border-top` + `border-left` on the container with the other two edges on the cells, so
  its four corners belong to four different elements and there is no box to round.
  → `foundations/geometry.html`
- **The black button's label is the foil, not white.** The two page mockups have no black
  button in them to copy, so the precedent is the manual's app icon
  (`26-farben-anwendung`): a black plate whose *mark* is filled with the light ramp while
  the plate stays black. A black button is that object at UI scale. It takes the foil and
  not the lime ramp because lime is a moment — one element per screen — and there can be
  several black buttons on a page. Contrast floor 11.9:1 at rest, 9.3:1 on hover — the
  plate is black, so hover lifts to `grey-800` rather than deepening; there is nothing
  under black to go to.
  This also widens the foil's remit: `.text-foil` stays one headline per page, but the
  button's label is under no budget, because there the foil is the component's colour
  rather than an emphasis. → `components/buttons.html`, `foundations/colors.html`
- **Body copy is 14 px,** not the 11 px in the process-card Figma export. 11 px stays
  reserved for uppercase mono labels, where it is still legible.
  → `foundations/typography.html`
- **Running text in an article is 16 px and 66 ch wide,** not the system's 14 px and 56 ch.
  Copy that supports a layout and copy that is read for minutes are different problems; the
  readable band for the second is 45–90 characters. `.cf-value-row__body` already made this
  step silently, so `.cf-prose` only makes it explicit. → `components/article.html`
- **Muted labels never sit on CF-Grau.** `#919191` on `#CFCFCF` is 2.0:1 — unreadable.
  Every label that sits on the page wash — section-header counters, blog meta, the blog
  axis, benefit labels, stat labels, field hints — therefore uses `--text-secondary`
  (5.9:1 on CF-Grau), not `--text-muted`, even though the mockups paint them lighter.
  Decorative counters are also `aria-hidden`. → `foundations/colors.html`
- **Lime is light, not ink: no lime letterforms on a dark surface.** Not a headline, not a
  label, not a nav marker, not a syntax colour. Type on black is white at whatever ink
  strength the hierarchy needs, or the foil — which exists precisely so that colour can
  enter letterforms without spending the screen's one lime moment. Lime keeps every job it
  had that is not type: the lit icon contour, the plot cap, the focus ring, the banner
  edge. The rule is not a contrast failure — lime on black measures **18.5:1** and clears
  AA at any size. It is that `#E1FF00` sits at 87.5 % of white's luminance while carrying
  the palette's highest chroma, and near-white luminance at maximum chroma blooms on a
  dark ground; the same reason dark-theme guidance desaturates accents rather than
  carrying them over from the light theme. Desaturating lime is the one move not available
  here, because a dark-mode-safe lime would be neither the brand's light nor the brand's
  colour. The documentation sidebar was the loudest offender and now runs on three steps
  of one white — title, link, current-page plate — the same marker the site nav already
  used. → `foundations/colors.html`, `foundations/typography.html`
- **Every dark surface is Schwarz; the mockups' anthracite `#1B2022` is dropped.** The
  footer, logo plate, nav bar and consent banner are painted a near-black anthracite in the
  mockups, and that used to be an eighth token — `--cf-anthrazit` — on the grounds that it
  could not be mixed from the seven. It differs from black by 1.2:1, which is not a colour
  so much as an inconsistency waiting to be noticed: the solid button had anthracite at rest
  and black on hover, a state change of 1.2:1. `--surface-inverse` is now `--cf-schwarz`,
  the palette is exactly the seven the manual names, and a dark surface that needs a second
  value takes it from the neutral ramp like every other surface does.
  → `foundations/colors.html`
- **The pinned track re-times the build and used to drop the trace's lead with it.** A
  signal drawn as several strokes carries `--trace-lead` and `--trace-span` so that it
  arrives along its own direction of travel — the base assembly's own note measures what
  happens without them, card 03's arrow "growing outward from five different points, which
  reads as a sketch scribbling itself rather than as a signal arriving". `.cf-pin
  .cf-iso__trace` named **one** window for every stroke on the track, so both properties
  resolved to nothing on the one page that ships them. Measured on the landing page at
  1440 × 900 inside card 03's quarter: five strokes, five different authored leads, and all
  five at progress `0.061` and `stroke-dashoffset 0.79497` — the same number five times. The
  window is now mapped rather than replaced: the base window is the 27 points of `cover` the
  default `--trace-span` names and the quarter's is the 8 points between `+5 %` and `+13 %`,
  so a stroke takes the same fraction of the second that it took of the first. **Both ends of
  the default are preserved exactly** — a trace with no authored lead draws where it always
  did, card 02's two are byte-identical, and card 03's five become 5→11.22, 5.89→12.11 and
  6.78→13.00, the last still landing on 13 where the construction points open. The 27 is
  load-bearing on two timelines now for one number authored once, so `check-iso-motion.py`
  holds it — along with the `--stage` ceiling and the rule that a light is a filled element,
  both of which were stated in prose and read by nothing.
  → `foundations/motion.html#hold`, `foundations/motion.html#trace`
- **Card 04's orbits turn, and they turn by moving their dashes rather than by rotating.**
  They are the only geometry in the system drawn as motion, and they were the only thing on
  the page asserting circulation while holding perfectly still. A rotation would have been the
  obvious mechanic and is the wrong one: the three rings are stroked with `userSpaceOnUse`
  gradients, so rotating a ring rotates its fade with it and sweeps the solid half across the
  lime disc — the failure `components/process-card.html` already measures from the release in
  which that rotation was dropped as a no-op. `stroke-dashoffset` touches no paint server.
  Under `non-scaling-stroke` it is measured in screen pixels, so **the travel must be a whole
  multiple of the 5 px dash period or the ring settles off the phase the designer drew** — a
  drift no diff against `assets/source/` could ever show, because it lives in the rendered
  phase and not in the markup. Verified: the settled object is pixel-identical to the build
  with no animation at all. → `foundations/motion.html`
- **When they turn is two claims about other rules, and both were false.** "An orbit turns as
  the object assembles and settles when everything else does" is a relation between three rules
  in two stylesheets, so neither end could be seen from inside the rule that set it. The stacked
  path had the rings fading up over a *finished* sphere — measured at 375 px, first orbit ink at
  `cover` 20 % with the object's eleven forms already at mean opacity 0.444, and the plan's own
  `2–14 %` window standing empty because card 04's orbits are the only dashed geometry it has.
  The pinned path had the other end: the turn closed at `+12 %` of a quarter whose light opens at
  `+12.4 %`, so the ring stopped four tenths of a point before the lime under it began to come
  up. Both ends are now read rather than written — the plan's window and the construction points'
  window — and `check-iso-motion.py` re-derives all three, so moving either window moves what the
  orbit is judged against. The travel is untouched, so the settled ring is the same pixels.
  → `foundations/motion.html#orbit-plan`
- **The Über uns value-table wheel keeps its six teeth, and six is off the sanctioned
  angles.** Measured off `mockups/ueber-uns.jpg` by radial profile from the drawing's own
  centre, the teeth sit at 30°, 90°, 150°, 210°, 270° and 330° — 60° apart, of which only
  the vertical pair is one of the brand's four. Eight teeth at 45° would put every flank on
  a sanctioned angle and is the obvious correction; it is not made, because the material is
  the authority and the rule it bends is about *constructing space*. This wheel recedes
  nowhere — it is a face-on glyph, and the only spatial thing in it is the globe, which is
  one 2:1 ellipse drawn twice with the second turned 90°. What the same figure used to carry
  *was* a real violation and is gone: two dashed rings at `rotate(±30)`, the exact drawing
  `foundations/illustration.html` labels a *don't*, invented rather than drawn from anything.
  The other two figures in that table were wrong in the ordinary way — bodies drawn as
  circles where a disc on the ground plane is a 2:1 ellipse, and four chevrons leaning at
  38.66°, 31.26°, 31.26° and 25.46° where the designer drew three at 2:1.
  → `foundations/illustration.html#where`
- **The process illustrations correct four things in the Figma export:** the lime hex, three
  unsanctioned dash patterns, a second lime element on card 02, and a tangent that was
  0.4° off the brand angle. Figma's inner-shadow bevel on card 03 is dropped — it is not
  one of the six material layers. → `components/process-card.html`
- **The Über uns header object's dashes are mapped onto the four line types, and the source
  vector's are not one of them.** Every path in that drawing is the designer's vector
  verbatim — the viewBox is the source file's own coordinate window precisely so that
  nothing has to be retyped — and the dasharrays came over with the geometry: four shells
  and the axis at `1 2`, two tangent arcs at `3 1.5`. Those are the 1-2 and 2-1 **ratios**
  at units of 1 and 1.5, where the four types are realised at `4 2`, `2 4` and `1 4`. Under
  `.cf-iso`'s non-scaling stroke a dasharray is device pixels, so the drawing shipped three
  dash periods the system does not have, on one of the two designed pages, under a comment
  claiming the opposite. Same correction and the same precedent as the process cards, and
  the mapping is read off the presence ladder rather than snapped to the nearest value:
  shells and axis `--presence-absent` (1-4, reference geometry), tangent arcs
  `--presence-near` (2-1, a real intersection), the dome's back half `--presence-faint`
  (1-2, behind the body), everything else solid. The figure now uses all four types and
  they run down the ladder in the order the drawing reads. The mockup cannot settle it
  either way: at 1200 px for a 1440 frame those contours are sub-pixel, and measured off the
  JPG the axis reads a 1:4 dash and the shell crown a period of about 3.6 — a disagreement
  wider than the thing in dispute. → `patterns/ueber-uns.html`, `foundations/geometry.html#lines`
- **The footer title is filled with the foil; the mockup paints it solid near-white.**
  Sampled off `mockups/landing-page.jpg`, "Jetzt Projekt starten!" is a flat `#EDF1F2`.
  The system clips `--gradient-foil` into it instead — one foil moment per screen, on the
  surface where it clears AA comfortably. The fallback is the mockup's own value:
  `.cf-footer__title` sets no colour and inherits white, so any browser that cannot clip a
  background into text renders exactly what the designer drew.
  → `components/footer.html`, `foundations/colors.html`
- **The Über uns page title is filled with the foil's shadow half; the mockup paints it
  solid black.** `--gradient-foil` is light-on-dark and cannot be otherwise — every stop is
  above OKLab L 0.82, so on the page's own CF-Grau it lands at 1.1–1.5:1. That left both
  designed pages, which are a CF-Grau-to-white wash almost end to end, with no gradient type
  outside the black footer. `--gradient-foil-ink` is the same three hues moved into the
  800 band: 102.2° of hue travel across 0.115 of lightness, against the lit half's 104.5°
  across 0.090. Worst sample on the shipped header is 5.45:1. As above, the fallback is the
  designer's own value — the title inherits `--text-primary`.
  → `foundations/colors.html`
- **The foil's rake swings; the mockups draw it at one angle.** A foil that never moves is a
  photograph of a foil. `.text-foil` therefore opens and closes the angle its gradient is drawn
  at — 90° to 116.57°, both sanctioned, and the 26.57° between them is the isometric angle
  itself — scrubbed from the element's position in the viewport. 116.57° is what you see
  head-on, so the swing turns round at the middle of the screen and every path away from it
  (no `@property`, no scroll timeline, reduced motion, print, forced colours) lands on the
  designer's own value. Turning a gradient changes where its stops land and never which stops
  are present, so the measured contrast floor holds at every frame without re-measuring —
  which is why this is an angle rather than a specular band or a sliding ramp. Neither foil
  moment on the two designed pages can reach the middle of the screen, so both read between
  90° and 108°; that is documented rather than bent. The swing has a second axis now — see
  [the line of sight](#the-line-of-sight) — which multiplies into the same rake and can only
  take it further from head-on, so those two figures stay the ceiling.
  → `foundations/colors.html`, `foundations/motion.html`, `foundations/sight.html`
- **Inline SVG gradients carry an oklab waypoint the source vectors do not have.** Figma
  interpolates in sRGB, and SVG can only interpolate in sRGB or linearRGB, so the illustrations
  inherited the sRGB path. The CSS gradients interpolate in oklab. Same three colours, two
  visibly different curves on the lime→Glas leg (ΔE 0.044). Rather than give up oklab in CSS,
  each lime→Glas leg in an inline SVG gets one stop — `#DBFC60` at 19 % of the leg, measured from
  lime — which puts it back on the oklab path to within ΔE 0.0116. The source vectors in
  `assets/source/` are untouched. **`#DBFC60` appears in none of the four source vectors, so
  re-exporting a shipped illustration from its source drops the waypoint silently and reverts
  that leg to the sRGB path.** Nothing fails when this happens; the stop is simply gone. Every
  waypoint therefore carries a comment at the stop itself. Re-add it after any rebuild.
  → `foundations/colors.html`
- **The two foils and the spectrum carry a second kind of waypoint, and it is on the CSS
  side.** oklab draws a straight line, and between two stops of similar chroma and different
  hue that line is a **chord** — so chroma sags in the middle of every leg that turns: −17.9 %
  on Glas → Sky, −13.6 % on Glas 800 → Sky 800. A ramp whose whole claim is hue travel greys
  out exactly where it is turning. The right path is polar and `in oklch` is **not** used:
  measured in Chromium, a stop below about C 0.018 has its hue discarded and the neighbour's
  carried forward, and Glas 800 is C 0.0171 — so the ink foil would ship 39.7° of its 102.2°
  of hue travel. The arc is put into the ramp instead, one waypoint per chromatic leg at that
  leg's midpoint, which is the `#DBFC60` idiom one space out. Peak chroma is unchanged, the
  lightness path is unchanged by construction, and the three contrast figures come back
  identical to three decimals. A leg that ends in grey gets nothing — an achromatic stop has
  no hue, so there is no arc for a chord to fall short of. → `foundations/colors.html#the-arc`
- **The page wash carries hue; the mockups paint it neutral.** Sampled off both mockup
  JPGs the wash is a straight CF-Grau-to-white ramp with zero chroma, and it was the only
  gradient in the system belonging to no family. It now runs `--foil-stops` backwards —
  Violett, Sky, Glas, Weiss, positions subtracted from 100 % — at OKLab chroma 0.005, with
  every stop sitting on the neutral ramp's own lightness so the luminance path is unchanged
  by construction. Worst channel deviation is 4 of 255, under the grain already on the same
  surface, and both text contrasts come out marginally better. The reason it is worth doing
  at all is not decoration: a neutral ramp is quantization-bound — `#CFCFCF` to `#FFFFFF` is
  49 greys and there is no fiftieth, because R, G and B cross every 8-bit boundary in the
  same place. Sampled off rendered pixels in Chromium over 4,000 px, the wash goes from 51
  distinct colours to 130, and transitions that move all three channels at once fall from
  99.8 % to 23.6 %. **The three hexes are re-derived on every run** by
  `check-wash-derivation.py`, because they are literals that do not follow `--cf-grau` on
  their own and the gradient gate exempts this ramp from both of its rules.
  → `foundations/colors.html`
- **The subdivision grid is two implementations of one system.** The manual's *Teilungsraster*
  plate says the recursive system "kann als Konzept für interaktive UI-Elemente oder
  Menüstrukturen genutzt werden" — a use no plate illustrates, because a book cannot draw a
  layout that answers to a reader. `.subdivide` is the static half: a track set whose hierarchy
  is authored once, because which article is newest is a fact about the archive. `.cf-subdiv`
  is the moving half: the same halving series, with which cell stands at its head handed to
  whoever is looking. It is built on `flex-grow` rather than on tracks because a track list
  cannot interpolate and a unitless number can, and because the flex form is one declaration on
  the cell where the grid form would be one track list per head per depth — sixteen of them.
  Both draw the identical series at rest. The head rule is *the head takes rank 0 and everyone
  else keeps their place and continues the series*, not a rotation: under a rotation the
  hovered cell slides out from under the pointer that summoned it (measured, 1024 px, cell 4
  goes `[896,960]` → `[256,768]`), and under this one its box always contains the box it had.
  → `components/subdivision-field.html`
- **The plot is derived from the language, not measured off a plate.** The brand manual
  contains a statistics and diagram plate; the 22 plates in `assets/source/manual/` are not
  it. `.cf-plot` is therefore built only from parts that *are* documented — the lattice
  rhombus, the four angles, the 1-4 ghost line type, the light layer, and the cube from the
  icon set extruded past one unit. Check it against that plate when the full archive is to
  hand; if the two disagree, the plate wins. One thing the plate cannot overrule: the row of
  columns is **level**, not receding. Both isometric ground axes slope 26.57° on screen, and
  marching columns along either one subtracts a unit of drawn height per column — on five
  columns rising 31 → 100 the recession cancelled almost the whole climb and the tallest
  column was drawn *lower* than the shortest. The level row is still a lattice step:
  (2u, +u) + (2u, −u) = (4u, 0). → `components/plot.html`
- **A line is not a body, so it is not drawn in space.** `.cf-plot` names its own ceiling
  at five values and everything above it had no figure. `.cf-line` is that figure, and the
  first decision is what it is *not*: everything the manual draws in isometry is an object
  with faces and volume, while a trace encodes a position at each point of a domain and
  says nothing about extent. Drawing it in space would claim a body where there is none —
  and it would cost what the plot already measured, a unit of drawn height per step along
  either 26.57° ground axis, which over eleven points is more than the whole climb. So the
  line is a **section**: orthographic, 90°, the fourth of the four angles. The lattice
  stays — every point the figure is read at stands on a cell, the same 8 px rhombus
  `.cf-annot::before` cuts — and the trace between those cells is flat. Three consequences
  follow from the same distinction. The trace's **angle is the one angle in this system
  nobody chose**, because quantising a slope to the four brand angles would falsify the
  data rather than merely flatten the picture. The **frame's ratio is fixed at 2:1**, the
  tile's own, and is a document-level choice from the three the brand owns rather than a
  per-figure tuning, because steepness is what a reader takes off a line and two frames at
  two ratios in one document cannot be compared. And the **floor is not assumed to be
  zero** — a column stands on the ground and must start there, a trace stands on nothing —
  which is why `.cf-line__bounds` is required: a tight frame is not dishonest, an
  undeclared one is. A point is data by default and a mark only when asked, so the eye gets
  three numbers where the accessibility tree gets eleven. → `components/line.html`
- **The palette cannot make a categorical hairline set, and that is measured rather than
  assumed.** A second series is a rung of the presence ladder and not a tint, because grey
  fails at both ends at once and the accents fail at both ends too. Against CF-Grau, the
  wash's worst end: `--border-default` composites to 1.74:1, grey 500 to 1.78:1 and grey
  400 to 2.02:1 — every grey light enough to *read* as a second series is under the 3:1 a
  contour owes — while grey 700, the one that clears the wash at 5.87:1, is 2.30:1 from the
  black it is supposed to differ from and is `--text-secondary`, the label ink. The three
  brand accents split the same way: Glas/Sky/Violett **500** measure 1.21, 1.49 and 2.24:1
  on the wash, and the **800** steps that clear it are near-blacks 1.36:1 and 1.20:1 apart
  from *each other* — a 1 px stroke has no area to judge a hue on. So the four line types
  are the whole vocabulary a series has: four traces at the ceiling, three in practice, and
  the ladder is ordinal so the series have to be (measured, planned, forecast). Past that
  the move is not a fourth line type but four frames — `.tiles` with one `.cf-line` per
  cell, all on one stated scale. → `components/line.html`
- **A label is a fixed height and a frame is not, which is one bug and one rule.** The
  value that rides a point needs its own line plus the gap — `0.75rem × 1.3` over
  `--space-3`, about 27.6 px — and that is the same 27.6 px whether the frame is 320 px
  tall on a desktop or 136 px at a 320 px viewport, where it is a fifth of the whole
  range. Two things follow, both measured rather than reasoned. The *bug*: a value near
  the ceiling climbs out through it — 84 % sat 5.1 px over its own top hairline at 320 px
  wide and 0.8 px over at 375 — and `bottom: min(…)` now parks such a label flush under
  the ceiling and leaves its node where the data says. The *rule*: in a multi-series
  figure the space above a point usually belongs to another trace, and at 375 px the plan
  ran straight through the subject's opening value because 13 points of frame is 21 px
  there. So a figure with three traces goes `.cf-line__set--quiet` — keys and nodes paint,
  values do not, every value stays in the accessibility tree, and the numbers go in the
  caption, which has room for them. → `components/line.html`
- **The line chart is the one figure whose data is written twice, and a script holds the
  copy.** SVG cannot read a custom property off an `<li>`, and the CSS construction that
  would avoid the second copy — rotated hairlines sized with `hypot()` and turned with
  `atan2()` — draws nothing at all on an engine without CSS trigonometry, which breaks the
  component's first law that every fallback is the finished chart. So the polyline and the
  list are both authored, the mapping between them is the identity (`x == --t × 100`,
  `y == (1 − --v) × 100`), and `scripts/check-line-trace.py` proves point *i* is vertex *i*
  to 0.05 user units. It is the invisible class in its purest form: a label a few pixels
  off its own line looks like a label, and a trace drawn from last quarter's numbers under
  this quarter's printed values looks like a chart. → `components/line.html`
- **The pie is the plot's finding one dimension along.** Same missing plate, same method:
  `.cf-pie` is built only from measures the plot already carries — 6u across, the height of
  a full column; a 1u band, the unit cube's edge; a 4u hole, the column pitch. And the same
  refusal. Laying the disc on the 2:1 ground plane is the obvious move in this brand and is
  the one thing a chart of angles cannot survive: under `scaleY(0.5)` a ray at *t* is drawn
  at `atan(0.5·tan t)`, so two true 30° shares — the same 8.3 % of the whole — come out at
  16.10° and 49.11°, a factor of **3.05** decided by nothing but where on the ring they
  landed. So the pie stands up, a true circle. Three further things fell out of the language
  rather than being chosen: **no leaders**, because a share's mid-angle is a measurement and
  a leader off it lands on none of the four brand angles, which makes it decoration; **the
  bloom rather than the rake**, because the band is rotated to its share and a bloom centred
  on the ring is the only member of the light family that looks the same at every rotation;
  and **no glow**, because at 12 px it laid light on both sides of the outer contour and the
  hairline over the lit share went invisible — `.cf-iso__light`, every lit face in the
  system, has never carried one either. The hole is not empty: the whole goes in it, with
  its unit, which is the one number a pie has always failed to state.
  Two engine facts are load-bearing and both were measured rather than assumed. A dash
  under `vector-effect: non-scaling-stroke` is counted in SCREEN pixels while `pathLength`
  normalises in user units, so the two never meet: at `--pie-u: 32px` a full-circle dash on
  a non-scaling contour drew 0.625 of the ring — 120/192, the viewBox scale exactly. And
  `stroke-dashoffset` takes a number, but Firefox 153 accepts it only as a literal: every
  unitless `calc()` on that property is invalid at computed-value time and drops to 0,
  `calc(1 - 0.27)` included — which over `pathLength="1"` is the whole ring lit. Written as
  `calc((1 - var(--pie-arc)) * 1px)` all three engines compute 0.73px. Verified in Chromium
  151, Firefox 153 and WebKit 26.5: same ring, same cuts, same labels to the pixel.
  → `components/pie.html`
- **Hue on a face is legal where hue on a hairline is not, and that is what a second series
  costs.** `.cf-plot` names its own ceiling at one series and declines the second, because a
  row of columns stepped a cell back along a ground axis is occluded by exactly the thing it
  is being compared with. `.cf-block` is that figure in **section** — the same 90° the line
  took — where both screen axes are free: one carries the categories, the other the series.
  The palette measurement `.cf-line` made still holds and still forbids a categorical *stroke*
  set (Glas/Sky/Violett 500 at 1.21, 1.49 and 2.24:1 on the wash), and it is a measurement
  about **area**, not about hue: a block is nothing but face, the 3:1 is carried by the black
  contour round it, and the fill is free. Three consequences fell out rather than being
  chosen. **A series ramp is a falloff and not a turn** — source straight to CF-Grau, no Glas
  in the middle — because keeping the near rake's Glas stop makes the Violett → Glas leg owe
  its polar arc waypoint, and that colour is `#74C1E6`: Sky's own hue, at Sky's own chroma,
  drawn through the middle of the Violett series in a figure whose premise is that the two are
  different things. **The chart stands up**, because the subdivisions of a horizontal value
  axis are vertical rules and geometry.html calls a rule that carries no label at its end
  decoration — lying it down would cost it its scale; the same refusal the pie made about the
  ground plane. And **the legend is carried by position, not by colour**: the series run in
  the legend's order inside every group, so a forced palette, a photocopier and every colour
  vision deficiency take the hue away and leave the figure readable — which is also what lets
  one block still be lit. Two faults measured on the way: `flex: 1 1 0` turned into a column
  drew a stack in equal thirds regardless of its values, and a printed number crossed its own
  ceiling hairline by 4 px at 375 px — fixed with the line's clamp, over
  `100% / var(--block-hz)`, which is the frame's height expressed in the block's own units.
  → `components/block.html`
- **The found state is derived from the language, not measured off a plate.** No plate in
  `assets/source/manual/` draws a highlight and neither mockup carries one, so `.cf-mark`,
  `::target-text` and the two `::highlight()` names are built only from parts the manual does
  establish — the hairline, the lattice edge an object stands on, the light layer, the presence
  ladder. Two consequences the plate could not have ruled on either way. The fill is lime even
  though *lime is light, not a surface*: material layer 5 sits under layer 6, so a lime fill
  behind text is the light layer in its correct place, and a word's worth of it is not a plate.
  And a bare `<strong>` now sets its own weight — the UA default `bolder` against the body's
  300 resolves to 400, one step on a variable axis and no visible emphasis, which no component
  had noticed because every component that thought about emphasis set 500 or 600 itself.
  → `foundations/found.html`
- **The table is derived from the language, not measured off a plate.** No plate in
  `assets/source/manual/` shows a table and neither mockup carries one, so `.cf-table` is
  built only from parts the manual does establish: the hairline for the row rule, the mono
  uppercase label the section header already uses for the column head, tabular figures, and
  no vertical rules at all — a line between two columns would be neither an edge nor a
  division, which is the test in *Where a line may go*. Two consequences worth knowing.
  `.cf-prose table` is not a second drawing: every selector names both, so an article's
  tables and a standalone one cannot drift. And a row header is set in the body face rather
  than as a mono label, because a row header is the row's subject — content — and the mono
  face in this system marks the things that are not prose.
  → `components/table.html`
- **The breadcrumb's separator is drawn, not typed.** No plate in `assets/source/manual/`
  shows a breadcrumb and neither mockup carries one, so `.cf-breadcrumb` is built only from
  parts the manual does establish: the mono uppercase label, the hairline, and the four
  angles. The separator is where that pays: every other system sets a character — `/`, `›`,
  `»` — which is a glyph from the body face standing in a row of mono labels, leaning at
  whatever angle the typeface felt like (a solidus is about 70°, none of the sanctioned
  four), and which some screen readers announce, so the trail reads "News slash Analyse
  slash". `content: ""` on a box rotated to `--angle-a`, its 1 px drawn as a
  `border-inline-start`, has none of those problems: nothing to announce, nothing to
  suppress, and the line lands on the steep isometric. It is a border rather than a
  background because forced colours overrides `background-color` to `Canvas` and the first
  version lost every separator in Windows high contrast; border colours are mapped into the
  forced palette instead of erased. It is
  a **division** under *Where a line may go* — a crumb on each side of it — not the banned
  bar with nothing on its far side. The fold below 30 rem keeps the parent and the current
  page rather than collapsing the middle into an overflow menu, because a menu needs a
  script and puts a second interactive thing in a component whose job is one line of
  orientation. → `components/breadcrumb.html`
- **The radio's box is square, and the mark is what tells it from a checkbox.** No plate in
  `assets/source/manual/` draws a form control and neither mockup carries a choice group, so
  `.cf-choice` and `.cf-radio` are built only from parts the manual does establish — the mono
  label, the 20 px square box the checkbox already is, the lattice rhombus, and the presence
  ladder. Every other system draws a circle here and this one may not: corners are square and
  the three exceptions the manual grants are the logo, the nav bar and a round avatar, none of
  which is a control. So single choice and multiple choice are told apart by the mark *inside*
  the box rather than by the shape of the box — a tick at 45° for *and*, the lattice rhombus
  for *or*, the same cell every isometric object is cut from and the same mark `.cf-progress`
  fills with light at its head. Both marks are drawn out of **border** rather than fill,
  because forced-colours mode discards `background-color` and maps border colours into its own
  palette: the rhombus is a zero-sized box with a border on all four sides, turned 45°.
  Verified in forced colours — the foil fill goes and the mark stays.
  An invalid **group** is marked once, on the legend, and not with the obvious 2 px rule down
  the left of the list, which is the decoration [where a line may go](#where-a-line-may-go)
  bans by name. → `components/forms.html#choice`
- **The two states a field can be in without being wrong are two rungs of the presence
  ladder.** `--presence-near` (2-1) is described on `components/arrival.html` as *held for a
  state that is a claim about the object, not about the wait* — reserved, and never claimed by
  anything. A **disabled** field is exactly that claim: not late, not available. It is drawn as
  the same field one rung down, same box, same size, same place, with the line as a repeating
  gradient because CSS gives no control over the dash-to-gap ratio of `border-style: dashed`
  and the four types are ratios. **Read-only** is the opposite claim — the value is here and it
  submits — so it is not a control at all any more and loses the line entirely, becoming the
  mono-term-over-value drawing `.cf-contact` already is. It is the one field state that keeps
  the global focus ring, because it has no line left to thicken. Both are written as
  `[disabled]` / `[readonly]` rather than `:disabled` / `:read-only`: a disabled input matches
  `:read-only`, and a `<select>` matches it *always*, so the pseudo-class would have stripped
  the line off every select on the site. → `components/forms.html#states`
- **The hero carries a switch the mockups do not draw.** The loop runs 12 s and repeats
  forever behind the headline, which is exactly the content WCAG 2.2.2 *Pause, Stop, Hide*
  (level A) requires a reader-operable mechanism over. `prefers-reduced-motion` is not that
  mechanism — it is a sufficient technique for 2.3.3, a different criterion, and 2.2.2 does
  not mention it. The system had the preference and not the mechanism, so this was a level A
  failure on the one page carrying video. The fix is a checkbox and two sibling selectors:
  checked hides the loop and shows the still, which is the third of the criterion's own three
  verbs and the only one CSS can reach alone. **No script** — a scripted control is absent
  for exactly the readers most likely to need it. Under reduced motion the control is
  *removed*, not hidden: nothing is moving, so a switch that changes nothing is worse than
  none. → `foundations/motion.html#hero`
- **The hero headline broke in six lines and the mockup draws three.** A correction rather
  than a judgement call, and one the markup had been asking for the whole time: the `<h1>`
  carries two explicit `<br>`s, and `.cf-hero__body` was overruling them with
  `max-width: 44ch`. `ch` is font-relative to the element it is *declared on*, and that
  element is the 14 px wrapper, not the 64 px headline it was sizing — so the clamp landed
  at 342.59 px and stayed there at 768, 1024, 1280, 1440 and 1920 alike. Six headline lines
  instead of three, and a kicker on two lines that the plate sets on one. The column is now
  `width: fit-content`, which is the longest line the display face actually sets, so the
  breaks the markup declares are the breaks that ship and nothing in the stylesheet has to
  be kept in step with the copy. Swept the other six `ch` measures in `components.css`
  while here: all of them sit on the element carrying the text, so this was the one
  instance, not a pattern. The same trap is already written up at the prose track in
  `components.css` — it was sprung here in the opposite direction.

  Two consequences. **The rule under the headline is no longer an element.** On the plate
  it starts and ends on the same two x as the mono line beneath it — 42 → 463 in the
  1200 px render — while the headline overhangs both; an empty `<div>` fills whatever box
  it is given and so ended with the headline instead. It is the kicker's `border-top` now,
  which makes it the kicker's width by construction, at every viewport and in a language
  whose translation of that sentence is longer. Measured 518 px against the plate's 505.
  And **the hero scrim's derivation was re-measured**, because it was written against the
  44 ch column: wider and shorter moves the text block's far corner outward along the
  63.43° axis and downward off it at once, and on this artwork the second wins. Headline
  4.08–6.26:1 at 375 / 768 / 1280 / 1920 against a 3:1 floor, kicker 8.99–15.33:1 against
  4.5:1 — every figure equal to or better than the one it replaces. No token changed; the
  comment in `tokens.css` now carries the numbers that were actually measured.
- **The process card is contour on the wash; the code painted it an opaque plate.** This
  one is a correction rather than a judgement call, and `foundations/materials.html` had
  been describing the corrected version all along — it lists the process card among the
  panels that "sit on the page wash with nothing complex behind it, so it is drawn with a
  contour instead", while `.cf-process` declared `background: var(--surface-card)`, its copy
  column declared a second plate in the same colour, and its note block a grey one. Sampled
  down the Discovery plate in `mockups/landing-page.jpg`, the card's interior and the page
  margin beside it read within **0.2** of each other at every row. There is no plate under
  the figure. `--surface-card` is retired; it resolved to the same `grey-050` as
  `--surface-raised`, so wherever the two were stacked one of them painted nothing.
  **That sampling went down the figure half only, and the copy half disagrees with it.** The
  plate is divided at x = 600 by the card's own interior hairline; right of it, over the full
  interior height, every sampled pixel is a flat `#F8F8F8` while the margin beside it climbs
  219 → 226 — **+22 to +29, constant**, which the wash cannot be because the wash moves. So
  the designer drew a contour figure panel and an opaque light plate under the copy, and the
  implementation draws neither. **The copy half carried that plate for a while, as
  `--surface-lifted`, and it has come off again — the card is contour on both halves.** The
  veil was the honest form of the mockup's plate and the arithmetic behind it holds: an
  absolute grey inside the wash's range inverts, so the step *toward* the light is a veil of
  white; the objection that a light step "dies at the bottom of every screen" is silent about
  this panel, which sits in `.cf-pin__stage`, `position: sticky`, and holds viewport rows **54**
  and **785** identically across the whole 5,760 px pin range at 1280×900; and the value was
  mirrored rather than picked — 6 % black removes 12.42 at the wash's opening stop, a white
  veil has 48 there, `12.42 / 48 = 0.2588` → white 26 %, rendering +15 at the card's head and
  +4 at its foot. **What none of that answered is whether the card wants a surface there at
  all, and on the rendered card it does not.** The two halves are already divided, by the
  figure's `border-right` — one hairline, and the only cut the card was meant to have. A plate
  on one side of it divides them a second time along the same seam and more loudly: what reads
  at a glance is a light block filling the right half of a card whose left half is the page,
  rather than one card in two parts. So both halves are the wash, in both forms, and
  `--surface-lifted` is retired with the declaration — its one consumer — with the derivation
  kept beside the retirement note in `tokens.css`. The mockup's measurement stands; the mockup
  is not the thing that ships. → `foundations/materials.html#copy-panel-gap`
- **A step away from the page is a ratio, not a grey — so `--surface-sunken` is a veil.**
  The neutral steps were absolute values chosen against `--surface-base`, CF-Grau, and no
  page in the system is painted CF-Grau: every page carries `.page-wash`, which is
  `background-attachment: fixed` at `background-size: cover` and therefore spans the
  **viewport**, running the full CF-Grau-to-white down every screen without scrolling. So
  what is behind a panel depends on where that panel currently sits on screen. Measured on
  the landing page at 1280×900, walking the process card's note down the viewport:
  `#E7E7E7` reads **+21** at 14 % of viewport height, **0** at 65 % and **−10** at 86 % —
  raised, then invisible, then sunken, all in one scroll. 6 % black removes 6 % of whatever
  light is there, a constant 0.858 ratio in linear light, so the step is −12 to −15
  everywhere. The direction had to flip: the light theme's steps used to climb toward white
  and cannot, because the wash *ends* at white. Sunken now means sunken. Contrast floor is
  the CF-Grau end — `--text-secondary` 5.19:1, `--text-primary` 11.91:1.
  → `foundations/colors.html#a-step-is-a-ratio`
- **Isometric contours use `vector-effect: non-scaling-stroke`.** "1 px contour at every
  size" is a device pixel. A 640-unit drawing shown at 352 px would otherwise put its
  contours on screen at 0.55 px. The one exception is `.cf-iso__trace`: under
  `non-scaling-stroke` the dash is measured in screen px while `pathLength` normalises
  against user space, which makes the line-drawing finish at 45 % of its range instead of
  100 %. Traces are stroked in user units instead — **and a user-unit stroke lands on screen
  at `weight × render scale`, so the weight is a property of the frame rather than of the
  system.** One literal was serving five families at four scales, and measured across
  375 / 768 / 1280 / 1920 the shipped trace ran 0.38 → 1.71 CSS px: 71 % heavier than the
  object it arrives at on Expertise, and 2.5:1 against CF-Grau on the reference strip, under
  the 3:1 a contour is held to. `--trace-weight` is `viewBox width / rendered width`, declared
  beside the `max-width` or `calc()` it is the reciprocal of — the same reason `--iso-travel`
  is written next to its viewBox. Every frame pinned to a cap is 1.00 px, and so is the process
  card's fluid phone band, which a 2.4× ramp had kept at 0.45–1.06 behind a `34.625rem` container
  query: its weight is `tan(atan2(640px, min(…)))` over the three lengths the figure already
  declares, with `100cqw` standing for the card, and the query is gone because `min()` is the
  crossover it spelled out. The two fluid bands that remain, Expertise and the reference strip,
  keep a constant stated as a band.
  → `foundations/motion.html`

## Drawing an illustration

`foundations/illustration.html` is the chapter for this, and it is the one to read before
drawing anything isometric. It states the system the four process objects were built on —
the lattice and its three steps, the four `.cf-iso__*` layers and the order they stack in,
the one-light-per-object budget with the three rakes, the three face greys, the frame as a
crop rather than a bounding box — and closes with a checklist and a specimen object drawn
from nothing but those rules.

**There were five layers until 2026-08-28, and `.cf-iso__trace` — the signal arriving from
off-stage — is the retired one.** Nothing new is drawn with a trace: the chapter sets out
four, the checklist no longer asks about one, and `isolib`/`isonews` cannot emit one. The
`--trace-*` machinery below and in `components.css` is kept for the drawings that already
carry a trace, which are the landing page's statement figure and process cards 01 to 04.

Two things it settles that the source material does not:

- **The light is per object, not per brand.** Laid out together, the four shipped gradient
  axes disagree about which side the light comes from — card 01's lime end is up-left,
  card 03's is up-right — and agree only that it is *up*. So a new object picks the end that
  reads as its own high point rather than copying card 01's axis.
- **Which side face is the darker one.** The four cards fill both side faces `#CFCFCF` and
  duck it; `foundations/geometry.html` darkens the right face; the manual's *Isometrie-Raster*
  plate darkens the left. The chapter ties it to the object — the shaded face is the one away
  from that object's own lime end — because under a per-object light that is the only version
  that cannot contradict itself. Flagged there for a designer; it is three fill values, not a
  redraw.

### An object made of parts is assembled, not delivered

`.cf-iso--build` on the `<svg>` stops the scene travelling and lets the parts arrive
instead: each `.cf-iso__form` on a `--stage` you index, out of a direction you author as
`--build-dx` / `--build-dy` in viewBox units. The four objects in *Was wir machen* all use
it — the telescope telescopes, the plates slide down their rack, the sphere's meridians
swell out of its axis.

Two rules make it a system rather than four animations:

- **A part travels only along an axis the object already contains, and only as far as the
  drawing says.** The 98 and 238 on card 01 are the two extensions measured off the source
  vector, not a motion decision. Both properties default to `0`, so a part with nowhere to
  come from resolves in place — which is most parts of most objects.
- **`--stage` is construction order, not paint order.** Nothing is reordered to animate it,
  so occlusion, paint servers and the diff against `assets/source/illustrations/` are
  untouched. Nodes are never staged: construction points belong to a finished object.

Parts move with the `translate` property rather than `transform`, because half of them carry
a `transform` attribute that *is* their shape. Full account in `foundations/motion.html#build`.

On a wide screen the landing page pins the whole section and scrubs the same build off the
track's timeline — the third pinned track, and the one to copy when the copy is prose rather
than typed. See `foundations/motion.html#pinned`.

## Redrawing an illustration: five things that vanish quietly

All five bite when an object is rebuilt or re-exported from `assets/source/illustrations/`,
and none of them announces itself — the drawing still renders, it is simply no longer what
the designer drew.

**Four of the five are now checked**, by one script each, all run by CI on every push and
pull request — the travel by `scripts/check-iso-motion.py`, the waypoint by
`scripts/check-gradient-family.py`, which owns it because it recomputes the offset and the
colour from the oklab path rather than looking for a hex, the dash pattern by
`scripts/check-line-types.py`, and the dropped `transform` by
`scripts/check-illustration-source.py`. See [Check it](#check-it).

**The fourth was on the unchecked side of this list, and the argument for leaving it there
was wrong in an instructive way.** It ran: a `transform` on a `userSpaceOnUse` gradient is
sometimes exactly right — card 04's largest orbit carries `rotate(-90)` on purpose — so the
presence of one is a question, not a verdict. That is true when the only thing you have is
the markup. It stops being true the moment you compare the markup against
`assets/source/illustrations/`, because **the source vector is what says whether the
transform was there**, and the question this list is actually about is not "should this
element have a rotation" but "did a rebuild drop the one the designer drew". That second
question is decidable, and the general rule `components/process-card.html` states is what
decides it: a transform may go missing only where dropping it is provably a no-op — a
rotation about the element's own centre, on a circle, painted flat. Card 04's eight
construction points pass all three. Its orbit fails the third, which is the defect that was
shipped. Verified against a mutation of each rule rather than assumed.

**The fifth is genuinely not checkable here**, and the line is worth stating rather than
leaving as an accident of what was easy. Whether a trace runs off the edge of its crop is a
fact about *rendered* geometry, which needs a browser to answer; a checker that guessed at
it would train people to ignore it.

- **The oklab waypoint.** `#DBFC60` exists in no source vector, so a re-export drops it and
  that lime→Glas leg reverts to the sRGB path. Every waypoint carries a comment at the stop.
  See the bullet above.
- **The dash pattern the export brought with it.** A `stroke-dasharray` is a presentation
  attribute sitting next to the path data, so it comes over with the geometry and looks
  exactly as authored — and the designer's vectors are drawn at whatever unit the file was
  built at. `8 2`, `2 8`, `2 2`, `1 2` and `3 1.5` have all arrived that way. Under
  `.cf-iso`'s non-scaling stroke the number is device pixels, so a right ratio at a wrong
  unit is a dash period the system does not have, and it is invisible: 3 px and 5 px are the
  same picture at a glance. Map it onto the rung it means before the drawing lands.
  → `scripts/check-line-types.py`, `foundations/geometry.html#lines`
- **A `transform` on an element painted with a `userSpaceOnUse` gradient.** The paint server
  is resolved in the user space where it is referenced, so the element's own transform
  rotates its gradient too. On a circle the rotation looks like a no-op against the geometry
  and is not: card 04's largest orbit had lost `rotate(-90)` and was fading 90° off the
  designer's axis. Measured and fixed, and now held against the source vector rather than
  against a reading of the markup.
  → `scripts/check-illustration-source.py`, `components/process-card.html`
- **`--trace-from` / `--trace-to` on a trace the crop cuts, and `--trace-lead` /
  `--trace-span` on one of several.** All four are inline custom properties on the path, so a
  re-export drops them and the line-drawing goes back to being timed against its full length —
  including the half of it that is outside the frame, and including the four strokes that are
  not this one. The drawing is not wrong, it just spends most of its scroll range invisible or
  holding still. Each one carries a comment at the element. Two drawings are cut by their
  crop — card 02, at both ends, and card 04 — and one is drawn as several strokes and
  therefore led: card 03's five-stroke arrow. All eight authored traces are on the four
  process objects and nowhere else. This paragraph used to name a fifth drawing and a sixth
  stroke set on a "trace specimen" on `foundations/illustration.html`, which carries no
  trace and no longer mentions one: the trace was retired from the four documented material
  layers, the specimen went with it, and the sentence counting it did not. The count is the
  tree's rather than this file's — `check-iso-motion.py` reports how many traces it measured
  on every run.
  → `foundations/motion.html`
- **`--iso-travel` on a frame that has been recropped.** The arrival distance is a transform,
  so it is in viewBox units, and the rule is `viewBox width / 40` — the same 5 % of the
  drawing in every frame. Eight of the fourteen shipping figures are not on a 640 square, seven of them
  carry their own value, four of those as inline custom properties on the `svg`, and the
  eighth is the Über uns header, which is above the fold and travels nowhere. Nothing tied
  those literals to the viewBox they were derived from, so **recropping a drawing left its
  travel silently wrong.** It had already happened once: the four objects on
  `patterns/expertise.html` were recropped from 695.2 / 612 / 552.4 / 714.24 to
  732 / 776.8 / 732 / 790.24 within an hour of the values first being written, and nothing
  failed — the objects simply arrived from the wrong distance. `check-iso-motion.py` now
  re-derives every one of them from the frame it is written beside, so that half is held.
  **The prose is the half that was not, and it had been wrong since it was written.**
  `foundations/motion.html` taught the rule with a worked example — the statement figure at
  "480 units", overriding the token *down* to 12 — against a drawing that is 1200 units and a
  stylesheet that has shipped 30 the whole time. Both numbers were wrong, they agreed with
  each other, and the correction they demonstrated was inverted: a bigger frame on the same
  token travels a *smaller* fraction, so the example argued the opposite of the rule above
  it. A check reading only CSS cannot see that, because the sample is text and renders
  whatever it says. The samples are now read too: a selector-keyed `--iso-travel` in a
  docs-code block must equal what `components.css` declares for that same selector, and its
  `/* W / 40 */` derivation must name the frame of the drawings that rule actually governs.
  **`--trace-weight` is the same hazard read the other way round:** it is `viewBox width /
  rendered width`, so a recrop breaks it from the viewBox end and a change to the frame's
  `max-width` breaks it from the render end. Both leave a trace that still draws itself,
  correctly and linearly, at the wrong weight.
  → `foundations/motion.html#travel`
