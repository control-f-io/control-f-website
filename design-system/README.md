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

## Check it

```bash
python3 scripts/check-spacing-scale.py         # from the repo root
python3 scripts/check-spacing-scale.py --fix   # rewrite the table in foundations/layout.html
```

The one check the system enforces rather than documents, run by CI on every push and
pull request. It holds the space scale to two rules: `foundations/layout.html`'s table of
who uses each rung must match the shipping CSS, and spacing in the shipping CSS must be
written as a token rather than as a length. Stdlib only — it does not give the system a
build step.

The table in that page is **generated**. Run `--fix` rather than editing a count by hand.

## Layout

```
design-system/
├── index.html              overview + how to include the CSS
├── foundations/            colour, type, layout, geometry, iconography, materials,
│                           illustration, logo, photo, motion, mobile
├── components/             buttons, nav, section header, statement + value table,
│                           plot, process card, accordion, blog grid, subdivision
│                           field, pagination, article + prose, team, forms,
│                           footer, consent
├── patterns/               full page templates — landing-page.html, ueber-uns.html,
│                           news.html, blog-artikel.html, kontakt.html
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
    │   ├── cf-values.js    types the values copy. Ships, optional — see below.
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

Two scripts ship. One is required, one is not:

```html
<script src="/design-system/assets/js/cf-consent.js"></script>
<script src="/design-system/assets/js/cf-values.js" defer></script>
```

`cf-consent.js` drives the consent banner and the settings dialog, which the site
cannot legally do without (TDDDG § 25). It is dependency-free, creates no markup of
its own, and if it never runs, no non-essential script runs either.
→ `components/consent.html`

`cf-values.js` is **optional and additive**. The values section is complete without it
— the copy is real markup and a view timeline does the pinning, the scrubbing and the
mark. All it adds is the copy arriving character by character rather than whole, which
is the one thing a view timeline cannot do because there is no per-character unit to
animate. It refuses to run unless the pinned layout is actually active, and it keeps
the full sentence in a `.visually-hidden` twin so assistive technology never gets a
half-written value. Delete the tag and the section still works.

Everything else in the system is HTML and CSS.

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
| copy | typed char by char out of a JS array | six list items, typed by an optional script |
| reduced motion | the 660 vh track and the gating both survive | stacked, readable, mark finished |
| no JS / no support / print | nothing to read | every value readable, whole |
| below 820 px | pinned | stacked, so a phone gets no seven-viewport hijack |

The typing does survive, but only as an enhancement on top: `assets/js/cf-values.js`,
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

The last pair is a biconditional and used not to be checked as one: `patterns/kontakt.html`
carried `--detached` over a normal `.section` and stood its footer off at 240 px where every
other page measures 120. Measured across all five pattern pages, the rhythm is now 240 between
normal sections, 200 after a `--tight` one, 120 above every footer, and 80 from every section
header's hairline to its content.

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
| **Contact endpoint** | `patterns/kontakt.html` posts to `/kontakt` and expects the server to validate, re-render the form with the reader's values and an error summary, drop anything that filled the honeypot, and serve the whole thing over HTTPS. The phone number on the page is a placeholder. |
| **News listing** | `patterns/news.html` is page 1 of 11 rendered flat. The server owns the paging: `?seite=N` selects the slice, `?thema=…` filters it, and both are reflected in the counters, the status line and which slot carries `aria-current`. Out of range should 404 rather than render an empty grid. |
| **Redirects** | The old topic pages (Maschinenbau, Energie, Dienstleistungen, Experten) are gone. They need 301s to the new structure. |

## Language

The documentation is English. The pattern pages carry German copy, because that is the
language the site ships in — translating it here would invent content that does not exist.
Landing Page and Über uns take theirs verbatim from the Figma mockups; News overview,
Blog article and Kontakt have no mockup and their copy is written placeholder in the
same voice. Colour
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
- **The process illustrations correct four things in the Figma export:** the lime hex, three
  unsanctioned dash patterns, a second lime element on card 02, and a tangent that was
  0.4° off the brand angle. Figma's inner-shadow bevel on card 03 is dropped — it is not
  one of the six material layers. → `components/process-card.html`
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
  90° and 108°; that is documented rather than bent.
  → `foundations/colors.html`, `foundations/motion.html`
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
- **Isometric contours use `vector-effect: non-scaling-stroke`.** "1 px contour at every
  size" is a device pixel. A 640-unit drawing shown at 352 px would otherwise put its
  contours on screen at 0.55 px. The one exception is `.cf-iso__trace`: under
  `non-scaling-stroke` the dash is measured in screen px while `pathLength` normalises
  against user space, which makes the line-drawing finish at 45 % of its range instead of
  100 %. Traces are stroked in user units at width 2 instead. → `foundations/motion.html`

## Drawing an illustration

`foundations/illustration.html` is the chapter for this, and it is the one to read before
drawing anything isometric. It states the system the four process objects were built on —
the lattice and its three steps, the five `.cf-iso__*` layers and the order they stack in,
the one-light-per-object budget with the three rakes, the three face greys, the frame as a
crop rather than a bounding box — and closes with a checklist and a specimen object drawn
from nothing but those rules.

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

## Redrawing an illustration: three things that vanish quietly

All three bite when an object is rebuilt or re-exported from `assets/source/illustrations/`,
and none of them announces itself — the drawing still renders, it is simply no longer what
the designer drew.

- **The oklab waypoint.** `#DBFC60` exists in no source vector, so a re-export drops it and
  that lime→Glas leg reverts to the sRGB path. Every waypoint carries a comment at the stop.
  See the bullet above.
- **A `transform` on an element painted with a `userSpaceOnUse` gradient.** The paint server
  is resolved in the user space where it is referenced, so the element's own transform
  rotates its gradient too. On a circle the rotation looks like a no-op against the geometry
  and is not: card 04's largest orbit had lost `rotate(-90)` and was fading 90° off the
  designer's axis. Measured and fixed. → `components/process-card.html`
- **`--trace-from` / `--trace-to` on a trace the crop cuts.** They are inline custom
  properties on the path, so a re-export drops them and the line-drawing goes back to being
  timed against its full length — including the half of it that is outside the frame. The
  drawing is not wrong, it just spends most of its scroll range invisible. Each one carries a
  comment at the element, and there are three: two on card 02, one on card 04.
  → `foundations/motion.html`
