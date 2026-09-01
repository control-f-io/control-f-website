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
python3 scripts/check-gradient-family.py       # the light family, in every shipped SVG and stylesheet
python3 scripts/check-gradient-family.py -v    # list all 88 gradients, not only the failures
python3 scripts/check-iso-motion.py            # the isometric assembly's invariants
python3 scripts/check-glass-budget.py          # what backdrop-filter is allowed to cost
python3 scripts/check-glass-budget.py --fix    # rewrite the census in foundations/materials.html
python3 scripts/check-glass-budget.py -v       # list every page, not only the ones carrying glass
python3 scripts/check-grid-tracks.py           # every fr track has a floor
python3 scripts/check-grid-tracks.py -v        # list every track list, not only the failures
python3 scripts/check-breakpoints.py           # every threshold is in the register, in rem
python3 scripts/check-breakpoints.py -v        # list every threshold, not only the failures
python3 scripts/check-overflow-clip.py         # a crop is a crop, not a scroll container
python3 scripts/check-overflow-clip.py -v      # list every overflow declaration, not only the failures
python3 scripts/check-highlight-fill.py        # every highlight states its ink as a fill, so a clip cannot erase it
python3 scripts/check-highlight-fill.py -v     # list every highlight rule, not only the failures
python3 scripts/check-line-types.py            # every dash pattern is one of the four line types
python3 scripts/check-line-types.py -v         # list every dash pattern, not only the strays
python3 scripts/check-links.py                 # every reference resolves on the host that serves it
python3 scripts/check-job-posting.py           # the JobPosting block matches the posting the reader sees
python3 scripts/check-a11y.py                  # the accessibility facts that are arithmetic rather than judgement
python3 scripts/check-class-provenance.py      # every class in the markup is declared by something
python3 scripts/check-class-provenance.py --report  # the census: who declares what, and what is written twice
python3 scripts/check-viewport-zoom.py         # no page revokes the reader's pinch zoom
python3 scripts/check-local-thresholds.py      # every page-local threshold is registered, and in rem under patterns/
python3 scripts/check-local-thresholds.py -v   # print the register
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

The fifteen checks the system enforces rather than documents, run by CI on every push and
pull request — one job, because each is a few hundred milliseconds of stdlib python.
Stdlib only: they do not give the system a build step.

**The space scale** holds to two rules: `foundations/layout.html`'s table of who uses each
rung must match the shipping CSS, and spacing in the shipping CSS must be written as a
token rather than as a length. The table in that page is **generated** — run `--fix`
rather than editing a count by hand.

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
| **the arc** | Every opaque leg that *turns* carries one waypoint at its own OKLCh midpoint. A waypoint is recognised by **being** that midpoint rather than by appearing on a list, so `#B9E3EB`, `#B8CCF3`, `#33494E` and `#273650` are re-derived on every run — the same standing `#DBFC60` has. A leg that turns and carries nothing is a chord and fails. |
| **the path** | A ramp carrying a **lime** leg exists somewhere with `in oklab`. lime → Glas is ΔEok 0.0443 between the two paths where every other leg in the family is under 0.0015, which is why `--glass-edge` and `--sheen-panel` are left in sRGB by name and the lime legs are not. |

What the arc does *not* govern is where the second rule gets its scope. A leg touching lime,
CF-Grau or Weiss is a **falloff** — light's source and what it falls away to — and oklab's
straight line is already its correct path. Only what happens in the band between them turns.
The premise is not just "chromatic at both ends": lime at C 0.2201 against Glas at C 0.0414 is
a radial move, and the polar path through it bows out to `#A8FFB6`, a green in no palette at
three times the chroma of the stop it is travelling to.

The second rule had already been broken. `.cf-btn--glass` drew Glas into lime on the sRGB path
with no `@supports` branch — the only lime ramp in the system's CSS never put on the family's
path, at ΔEok 0.03866 composited over CF-Grau, seventy-nine times the divergence of the
`--glass-edge` layer directly above it that the family deliberately declines to correct. Its
stops are a custom property now and only the path changes.

**The isometric assembly** holds to six rules, all of which were already written down in
prose and none of which anything ran:

| | |
|---|---|
| `--iso-travel` | Every figure that assembles travels `viewBox width / 40` — 2.5 % of its own drawing — resolved the way the cascade does: inline styles, then the component-keyed rules in `components.css`, then the `:root` default. |
| `--iso-orbit-travel` | A whole multiple of the `--dash-1-4` period, or every orbit settles off the phase the source vector drew. |
| `pathLength="1"` | On every `.cf-iso__trace`, and `non-scaling-stroke` on none of them. The trace is a retired layer — this holds the ones already drawn. |
| `.cf-iso__orbit` | Always carries `.cf-iso__ghost` too — an orbit is a ghost that also turns, and the shared rule names the ghost. |
| one light | At most one `.cf-iso__light` per object. |
| `screen` | Every `animation-timeline` declaration sits inside a `@media` that names `screen`. |

Every one of the six is invisible in a screenshot and countable in a file, which is the
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

## Layout

```
design-system/
├── index.html              overview + how to include the CSS
├── foundations/            colour, type, layout, geometry, iconography, materials,
│                           illustration, logo, photo, motion, mobile,
│                           page transitions, field, found state, line of sight
├── components/             buttons, nav, breadcrumb, section header, statement +
│                           value table, plot, gantt, annotation, process card,
│                           accordion, blog grid,
│                           subdivision field, search + results, vacancy,
│                           pagination, error + empty state, arrival + progress,
│                           article + prose, table, team, forms, footer, consent
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

Three exceptions, each technical rather than aesthetic: the palette swatch on
`foundations/colors.html` (a swatch of a colour has to be the colour), the **found state**
(`background-image` is ignored on a highlight pseudo-element, so no ramp of this family can
be painted into `::selection`, `::target-text` or `::highlight()` — see below), and any
**stroke, outline or focus ring** (not a fill — the rule is about area). The flat lime cube on
`foundations/illustration.html` is a labelled *don't*, drawn wrong on purpose.

→ `foundations/colors.html#lime-is-never-flat`

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
Coarse pointers do not get it at all: a finger has no position between taps, and reading a
touch as a light source makes the page flinch every time it is scrolled.

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
| `.section--tight` | `--section-gap-sm` on both. The first section under a `.cf-page-header`. |
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

## Before launch

| | |
|---|---|
| **Publica Sans** | Commercial licence required. Drop `PublicaSans-Variable.woff2` into `assets/fonts/`. Until then `--font-display` falls back to Geist. |
| **Geist / Geist Mono** | OFL, free. Self-host the `.woff2` files in `assets/fonts/` — deliberately **not** the Google Fonts CDN (DSGVO). |
| **Process illustrations** | Done. Built from the designer's source vectors in `assets/source/illustrations/`. The four documented deviations are listed on `components/process-card.html`. |
| **Partner logos** | The logo wall renders text placeholders; drop in the real SVGs. |
| **Team photos** | Six placeholder portraits from the shoot. Real names, roles and the full set of ten still needed. |
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
  99.8 % to 23.6 %. → `foundations/colors.html`
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
  implementation draws neither. Left standing rather than half-restored: the same argument
  that retired the card's plate applies to this one — an absolute grey inside the wash's range
  inverts as the reader scrolls, and the honest form of a step *toward* the light is a veil of
  white, which the materials family does not have a value for yet. A designer settles it.
  → `foundations/materials.html#copy-panel-gap`
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
  is written next to its viewBox. Every frame pinned to a cap is 1.00 px now; the fluid bands
  keep the old constant and are stated as a band, because a 2.4× ramp has no constant.
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

**Three of the five are now checked**, by one script each, all run by CI on every push and
pull request — the travel by `scripts/check-iso-motion.py`, the waypoint by
`scripts/check-gradient-family.py`, which owns it because it recomputes the offset and the
colour from the oklab path rather than looking for a hex, and the dash pattern by
`scripts/check-line-types.py`. See [Check it](#check-it).
The other two are not, and the line between them is worth stating rather than leaving
as an accident of what was easy. A missing waypoint, a travel that disagrees with its
viewBox and a dash period that is on no rung are **facts about the markup**, so a script
can settle them. The other two are not: a `transform` on a `userSpaceOnUse` gradient is sometimes exactly right — card 04's
largest orbit carries `rotate(-90)` on purpose — so the presence of one is a question, not
a verdict; and whether a trace runs off the edge of its crop is a fact about rendered
geometry, which needs a browser to answer. A checker that guessed at either would train
people to ignore it.

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
  designer's axis. Measured and fixed. → `components/process-card.html`
- **`--trace-from` / `--trace-to` on a trace the crop cuts, and `--trace-lead` /
  `--trace-span` on one of several.** All four are inline custom properties on the path, so a
  re-export drops them and the line-drawing goes back to being timed against its full length —
  including the half of it that is outside the frame, and including the four strokes that are
  not this one. The drawing is not wrong, it just spends most of its scroll range invisible or
  holding still. Each one carries a comment at the element. Three drawings are cut by their
  crop — card 02 (both ends), card 04, and the trace specimen on
  `foundations/illustration.html` — and two are drawn as several strokes and therefore led:
  card 03's five-stroke arrow and that same specimen's three.
  → `foundations/motion.html`
- **`--iso-travel` on a frame that has been recropped.** The arrival distance is a transform,
  so it is in viewBox units, and the rule is `viewBox width / 40` — the same 5 % of the
  drawing in every frame. Seven of the fifteen shipping objects are not on a 640 square and
  carry their own value, four of them as inline custom properties on the `svg`. Nothing ties
  those literals to the viewBox they were derived from, so **recropping a drawing leaves its
  travel silently wrong.** It has already happened once: the four objects on
  `patterns/expertise.html` were recropped from 695.2 / 612 / 552.4 / 714.24 to
  732 / 776.8 / 732 / 790.24 within an hour of the values first being written, and nothing
  failed — the objects simply arrived from the wrong distance. Re-measure after any recrop.
  **`--trace-weight` is the same hazard read the other way round:** it is `viewBox width /
  rendered width`, so a recrop breaks it from the viewBox end and a change to the frame's
  `max-width` breaks it from the render end. Both leave a trace that still draws itself,
  correctly and linearly, at the wrong weight.
  → `foundations/motion.html#travel`
