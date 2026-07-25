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
├── components/             buttons, nav, section header, statement + value table,
│                           process card, accordion, blog grid, article + prose,
│                           team, forms, footer, consent
├── patterns/               full page templates — landing-page.html, ueber-uns.html,
│                           blog-artikel.html
├── prototypes/             scroll-animation studies — standalone, not yet system
├── reference.html          the designer's source material, next to what implements it
└── assets/
    ├── css/
    │   ├── tokens.css      every design decision as a custom property
    │   ├── base.css        fonts, reset, type classes, layout primitives, utilities
    │   ├── components.css  every component
    │   └── docs.css        this documentation site only — does not ship
    ├── js/
    │   ├── cf-consent.js   the consent banner + settings dialog. Ships.
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

One script ships, and only one:

```html
<script src="/design-system/assets/js/cf-consent.js"></script>
```

It drives the consent banner and the settings dialog, which the site cannot legally
do without (TDDDG § 25). It is dependency-free, creates no markup of its own, and if
it never runs, no non-essential script runs either. Everything else in the system is
HTML and CSS. → `components/consent.html`

## Animation prototypes

`prototypes/` holds scroll-animation studies. They are **not part of the system**: each
one carries its own styling and its own scroll engine, neither has been reconciled with
the tokens, and nothing in `components/` depends on them. They are in the sidebar so the
motion they propose can be reviewed against the pages it would land on.

| | |
|---|---|
| `werte-scroll.html` | The mark builds itself from its own isometric subdivision grid across six value stages, with the copy streaming in char by char. Scroll-scrubbed, so it un-builds on the way back up. |
| `services-scroll.html` | The four process cards assemble inside a pinned section — cubes telescoping up, layers sliding in, contours drawing themselves. 1.4 MB, almost all of it one inline Figma export. |

Both scrub from scroll position rather than playing on a timer, which is what the system
already commits to in `foundations/motion.html` — the animation tracks the reader's hand
and reverses when they scroll back.

**`werte-scroll.html` has shipped.** It is the *Unsere Werte* section of
`patterns/ueber-uns.html` now, rebuilt as `.cf-values`. What changed on the way in:

| | prototype | shipped |
|---|---|---|
| engine | ~120 lines of JS | a view timeline, no script |
| copy | typed char by char out of a JS array | six list items in the document |
| reduced motion | the 660 vh track and the gating both survive | stacked, readable, mark finished |
| no JS / no support / print | nothing to read | the same stacked state |
| below 820 px | pinned | stacked, so a phone gets no seven-viewport hijack |

The char-by-char typing did not survive, and that is the one thing the shipped version is
missing. A view timeline cannot type, and doing it properly needs either a second shipping
script or ~180 spans per paragraph. Each value now arrives as a whole instead. Worth
revisiting if the typing turns out to be the point rather than the flourish.

The prototype file stays where it is as the reference for that question.

`services-scroll.html` is still a prototype. Its reduced-motion path is already correct —
the scrub script returns early, the pinned section goes `static` and auto-height, and the
illustration renders in its authored, finished state, the same shape as the fix in #11.

## The system in one paragraph

The site sits on CF-Grau, not on white — a data space, not a sheet of paper, with a
slow vertical wash from `#CFCFCF` to white across the full page height. Everything is
drawn with 1 px contours rather than filled, and anything spatial is constructed in
2:1 isometry (26.57°). Corners are square; the only exceptions are the logo pill, the
nav pill and round avatars. Lime is light, not a surface: one element per screen.
Publica Sans sets display headlines, Geist sets everything readable, Geist Mono sets
labels and every number.

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

## Before launch

| | |
|---|---|
| **Publica Sans** | Commercial licence required. Drop `PublicaSans-Variable.woff2` into `assets/fonts/`. Until then `--font-display` falls back to Geist. |
| **Geist / Geist Mono** | OFL, free. Self-host the `.woff2` files in `assets/fonts/` — deliberately **not** the Google Fonts CDN (DSGVO). |
| **Process illustrations** | Done. Built from the designer's source vectors in `assets/source/illustrations/`. The four documented deviations are listed on `components/process-card.html`. |
| **Partner logos** | The logo wall renders text placeholders; drop in the real SVGs. |
| **Team photos** | Six placeholder portraits from the shoot. Real names, roles and the full set of ten still needed. |
| **Consent copy** | The three categories, their retention periods and the entry counts on `components/consent.html` are placeholders. A lawyer signs off the wording, and the real cookie inventory replaces the numbers. |
| **Consent record** | `localStorage` proves nothing to a supervisory authority. The decision needs logging server-side before launch. |
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
- **Running text in an article is 16 px and 66 ch wide,** not the system's 14 px and 56 ch.
  Copy that supports a layout and copy that is read for minutes are different problems; the
  readable band for the second is 45–90 characters. `.cf-value-row__body` already made this
  step silently, so `.cf-prose` only makes it explicit. → `components/article.html`
- **Muted labels never sit on CF-Grau.** `#919191` on `#CFCFCF` is 2.0:1 — unreadable.
  Every label that sits on the page wash — section-header counters, blog meta, the blog
  axis, benefit labels, stat labels, field hints — therefore uses `--text-secondary`
  (5.9:1 on CF-Grau), not `--text-muted`, even though the mockups paint them lighter.
  Decorative counters are also `aria-hidden`. → `foundations/colors.html`
- **Anthracite `#1B2022` exists as a token but is not a core colour.** It is the measured
  footer and logo-pill fill from the mockups and cannot be mixed from the seven, so it is
  declared once rather than hard-coded per component. → `foundations/colors.html`
- **The process illustrations correct four things in the Figma export:** the lime hex, three
  unsanctioned dash patterns, a second lime element on card 02, and a tangent that was
  0.4° off the brand angle. Figma's inner-shadow bevel on card 03 is dropped — it is not
  one of the six material layers. → `components/process-card.html`
- **The footer title is filled with the foil; the mockup paints it solid near-white.**
  Sampled off `mockups/landing-page.jpg`, "Jetzt Projekt starten!" is a flat `#EDF1F2`.
  The system clips `--gradient-foil` into it instead — one gradient headline per page, on
  the one surface where it clears AA comfortably. The fallback is the mockup's own value:
  `.cf-footer__title` sets no colour and inherits white, so any browser that cannot clip a
  background into text renders exactly what the designer drew.
  → `components/footer.html`, `foundations/colors.html`
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
- **Isometric contours use `vector-effect: non-scaling-stroke`.** "1 px contour at every
  size" is a device pixel. A 640-unit drawing shown at 352 px would otherwise put its
  contours on screen at 0.55 px. The one exception is `.cf-iso__trace`: under
  `non-scaling-stroke` the dash is measured in screen px while `pathLength` normalises
  against user space, which makes the line-drawing finish at 45 % of its range instead of
  100 %. Traces are stroked in user units at width 2 instead. → `foundations/motion.html`
