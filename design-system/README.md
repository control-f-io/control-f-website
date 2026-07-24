# Control-F Design System

The implementation of the 2026 brand for the web. Static HTML + CSS, no build step,
no dependencies.

Source material: [`control_f_website_new_design/`](../../control_f_website_new_design/)
— brand manual, logo files, Figma mockups of the Landing Page and Über uns.

## Run it

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/design-system/>. It also works by opening
`index.html` directly from disk.

## Layout

```
design-system/
├── index.html              overview + how to include the CSS
├── foundations/            colour, type, layout, geometry, iconography, materials,
│                           logo, photo, motion
├── components/             buttons, nav, section header, process card, accordion,
│                           blog grid, team, forms, footer
├── patterns/               full page templates — landing-page.html, ueber-uns.html
├── reference.html          the designer's source material, next to what implements it
└── assets/
    ├── css/
    │   ├── tokens.css      every design decision as a custom property
    │   ├── base.css        fonts, reset, type classes, layout primitives, utilities
    │   ├── components.css  every component
    │   └── docs.css        this documentation site only — does not ship
    ├── js/
    │   ├── cf-icons.js     the icon set — the one place a glyph is drawn. Ships.
    │   └── docs.js         sidebar, swatch copy, arrow sprite — documentation only
    ├── fonts/              (empty — see below)
    ├── img/                logo SVGs, icons, hero poster, team photos
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

## The system in one paragraph

The site sits on CF-Grau, not on white — a data space, not a sheet of paper, with a
slow vertical wash from `#CFCFCF` to white across the full page height. Everything is
drawn with 1 px contours rather than filled, and anything spatial is constructed in
2:1 isometry (26.57°). Corners are square; the only exceptions are the logo pill, the
nav pill and round avatars. Lime is light, not a surface: one element per screen.
Publica Sans sets display headlines, Geist sets everything readable, Geist Mono sets
labels and every number.

## Before launch

| | |
|---|---|
| **Publica Sans** | Commercial licence required. Drop `PublicaSans-Variable.woff2` into `assets/fonts/`. Until then `--font-display` falls back to Geist. |
| **Geist / Geist Mono** | OFL, free. Self-host the `.woff2` files in `assets/fonts/` — deliberately **not** the Google Fonts CDN (DSGVO). |
| **Process illustrations** | The four isometric objects are systems-correct approximations, not final assets. |
| **Partner logos** | The logo wall renders text placeholders; drop in the real SVGs. |
| **Team photos** | Six placeholder portraits from the shoot. Real names, roles and the full set of ten still needed. |
| **Redirects** | The old topic pages (Maschinenbau, Energie, Dienstleistungen, Experten) are gone. They need 301s to the new structure. |

## Language

The documentation is English. The two pattern pages carry the real German marketing copy
from the Figma mockups, because that is the language the site ships in — translating it
here would invent content that does not exist. Colour names (Glas, Violett, CF-Grau,
Schwarz, Weiß) stay German everywhere: they are the brand's names for them.

## Decisions that differ from the source material

These were judgement calls, each documented on the relevant page:

- **Body copy is 14 px,** not the 11 px in the process-card Figma export. 11 px stays
  reserved for uppercase mono labels, where it is still legible.
  → `foundations/typography.html`
- **Muted labels never sit on CF-Grau.** `#919191` on `#CFCFCF` is 1.9:1 — unreadable.
  Decorative counters are also `aria-hidden`. → `foundations/colors.html`
- **Anthracite `#1B2022` exists as a token but is not a core colour.** It is the measured
  footer and logo-pill fill from the mockups and cannot be mixed from the seven, so it is
  declared once rather than hard-coded per component. → `foundations/colors.html`
