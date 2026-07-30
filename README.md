# Website of control-f

The website is the 2026 brand: the pages under [`design-system/patterns/`](design-system/patterns/),
served from the repository root. Fourteen pages — landing page, Expertise, Über uns,
News and an article, Suche and its empty state, Karriere and a posting, Kontakt and its
confirmation, Datenschutz, Impressum, 404.

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

## Development

```bash
python3 -m http.server 8000    # repo root
```

- Website: <http://localhost:8000/>
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
- Add english variants (do this at the very end)
- Redirects for the outgoing URLs (`experten.html`, `dienstleistungen.html`,
  `energie.html`, `maschinenbau.html`, `blog/`) if any of them are linked from outside
