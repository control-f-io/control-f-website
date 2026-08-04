# Website of control-f

The website is the 2026 brand: the pages under [`design-system/patterns/`](design-system/patterns/),
served from the repository root. Sixteen pages — landing page, Expertise, Über uns,
News and a topic and an article, Suche and its empty state, Karriere and a posting and
its empty state, Kontakt and its confirmation, Datenschutz, Impressum, 404 — each in two
languages, German at the root and English under `/en/`.

The generation before it — nine hand-written pages against `assets/css/main.css` — has
been removed.

## The root is generated

Every `.html` file at the root is written by [`scripts/build-site.py`](scripts/build-site.py)
out of the matching page in `design-system/patterns/`. **Do not edit them.** Edit the
pattern and rebuild:

```bash
python3 scripts/build-site.py            # write the root pages
python3 scripts/build-site.py --check    # fail if any is stale, missing or hand-written
```

The patterns cannot simply live at the root: seventy-five `scripts/check-*.py` read them
from `design-system/patterns/`, several keyed on that path by string, and the routines run
against it. So the pattern stays where it is checked and the root holds its shipped form,
which differs by four edits and nothing else — asset paths, the landing page's name, and
the two pieces of preview chrome that never ship. The script's own header lists them.

`design-system.yml` runs `--check` on every push, and `deploy.yml` rebuilds before it
uploads, so a forgotten rebuild is caught in CI and cannot reach production either way.

There is one copy of every stylesheet, script, font and image, in
`design-system/assets/`. The shipped pages and the documentation load the same files.

## So is the English edition

`/en/` is the same sixteen pages with the words changed, and it is generated one step
earlier in the same chain by [`scripts/build-i18n.py`](scripts/build-i18n.py):
`design-system/patterns/en/` is built from the German pattern beside it, and
`build-site.py` then ships that directory the way it ships the German one.

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
in the middle of it, which is the failure nobody reviews — and five scheduled routines
write new sentences into the landing pattern every hour. Add the copy in German, run
`--extract`, translate what it prints, rebuild.

The two editions point at each other from the nav — the `EN` / `DE` plate at the top
right — and from a `<link rel="alternate" hreflang>` pair in the head. Both are written
by the generator, so they cannot disagree about where the other edition is.

The eighty-two `scripts/check-*.py` do not read `patterns/en/`. Every fact they keep is
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

## Automation

Most commits on `main` are written by scheduled cloud agents that merge their own
pull requests, with no human review gate. What they are, what they have been told,
and the standing orders that outrank their briefs: [.github/ROUTINES.md](.github/ROUTINES.md).

## Deployment

Every merge to `main` publishes the repo root to GitHub Pages via
`.github/workflows/deploy.yml`.

- Website: https://control-f-io.github.io/control-f-website/
- Design system: https://control-f-io.github.io/control-f-website/design-system/

Because the site is served from a subpath, links and asset references must stay
**relative** (`design-system/assets/css/tokens.css`, `expertise.html`) — a leading `/`
would resolve against `control-f-io.github.io` and 404. `scripts/check-links.py` holds
that rule for the design system; the generator carries it to the root.

## Fragen

- contact email: info@control-f.io? The pages currently write `info@control-f.de`,
  plus `jobs@`, `presse@` and `datenschutz@` on the same domain.
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
