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

Every merge to `main` publishes the repo root to GitHub Pages via
`.github/workflows/deploy.yml`.

`deploy-worker.yml` publishes the same pages to Cloudflare with the Worker in front of
them. It runs only when the `CLOUDFLARE_ENABLED` variable is set, so it is inert until
someone turns it on, and **both deploys run in parallel** — the cutover is a DNS change,
not a merge. Cloudflare serves `dist/`, which `scripts/stage-site.py` fills with the
sixteen generated pages and `design-system/` and nothing else in the repository.

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
  address `presse@control-f.io`; the phone number is Simon's, `+49 176 44478596`
  — the `+49 7531 123456-0` on the pages was a placeholder. `jobs@` and
  `datenschutz@` were not named and still write `control-f.de`.
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
