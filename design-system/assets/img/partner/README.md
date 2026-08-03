# Partner marks

The seven marks `.cf-logo-wall` paints on patterns/landing-page.html. Third-party
artwork, normalised — not drawn here, and not to be redrawn here.

## Why they are normalised at all

The wall paints every mark at ONE height (`components.css`, `.cf-logo-wall img`:
`height: 2.5rem; width: auto`). One height is the right contract — a wall whose
CSS carries a number per logo is a wall nobody can add an eighth mark to — but it
only works if the FILES are the thing that has been made equal.

They are not equal as shipped. A brand delivers its mark in its own box: Hetzner's
is an all-caps wordmark whose caps fill the box top to bottom, Databricks' is a
stacked lockup with the wordmark under the glyph, Azure's is a glyph with no type
at all. Set those three to the same height and the Hetzner caps render three times
the size of the Databricks wordmark. Measured on the shipped sources at a 200 px
box, the height of the letterforms ran 58 px (Kafka) to 149 px (Azure) — a 2.6x
spread inside a stylesheet that thinks it is drawing one size.

## The rule

**Every mark is scaled so the median column ink-extent is 0.29 of its box.**

The median column ink-extent is the measurable stand-in for x-height: render the
mark, take each column of pixels that has ink in it, measure top-to-bottom extent,
take the median. Most columns of a wordmark are letter stems, so the median lands
on x-height for a lowercase mark, on cap height for an all-caps one, and on the
glyph itself for a mark that is only a glyph — which is the right answer in all
three cases, because that is the height the eye compares along a row.

It is NOT equal ink area, which was tried first and is wrong: area conflates
weight with WIDTH, so a long wordmark is penalised for being long. Measured, the
equal-area rule wanted Kafka at 1.93x Kubernetes and Hetzner at 1.06x — Kafka
twice the size of everything because "kafka" is a short word.

0.29 is not chosen either. It is Kafka's own fraction, and Kafka is the mark that
sets it because its glyph column is the tallest thing on the wall relative to its
type. Every other mark is padded DOWN to it, so no mark is ever scaled past its
own box and nothing is clipped.

At the wall's 2.5rem box that puts every mark's x-height at 11.6 px — which is
`--text-xs`, 11 px, the size of the mono labels the marks replaced and of every
other label on the page. The box height follows from the rule; it is not a
separate taste.

## What was done to each file

1. **Trimmed to the tight bounding box**, measured in a renderer. An exported
   `viewBox` is an artboard, and an artboard carries whatever margin the designer
   left in it.
2. **Flattened to one ink** (`#000`). The wall is one tone, and the stylesheet's
   `grayscale(1)` maps each brand colour to its own luminance instead — Kafka's
   near-black against Spark's orange is two weights on one line. White is left
   alone where it is a KNOCKOUT (the helm inside the Kubernetes heptagon); STACKIT
   ships white-on-dark, so there white IS the ink and it flips. The wall's
   `opacity: .38` is what makes them grey.
3. **Re-boxed** so the artwork fills `k` of the box height, centred, with `k` from
   the rule above. The box is exactly the artwork's width, so `width: auto` gives
   the natural width.
4. **Stripped** of editor metadata (Inkscape/Illustrator namespaces, generator
   comments, `sodipodi:namedview`).

Databricks additionally had its horizontal lockup **composed from its own two
paths** — glyph left, wordmark right, centred on one axis, gap 0.31 of the glyph's
width. The only file published as SVG is the stacked lockup, and a stacked lockup
in a row renders its wordmark at a third of the line. Nothing was redrawn: both
paths are the brand's, moved.

| mark | k | box (units) | source | licence at source |
|---|---|---|---|---|
| databricks | 0.523 | 132.2 × 39.85 | Wikimedia Commons, `Databricks-logo.svg` | Public domain (trademark) |
| kafka | 1.000 | 112.0 × 52.00 | Wikimedia Commons, `Apache_kafka_wordtype.svg` | Apache-2.0 (trademark) |
| stackit | 0.505 | 112.6 × 25.79 | stackit.de, inline header mark | trademark, © Schwarz Digits |
| spark | 0.607 | 412.9 × 353.5 | Wikimedia Commons, `Apache_Spark_logo.svg` | Apache-2.0 (trademark) |
| kubernetes | 0.637 | 500.6 × 132.7 | Wikimedia Commons, `Kubernetes_logo.svg` | Public domain (trademark) |
| azure | 0.358 | 88.0 × 231.6 | Wikimedia Commons, `Microsoft_Azure.svg` | Public domain (trademark) |
| hetzner | 0.289 | 181.5 × 76.99 | hetzner.com, `hetzner-logo.svg` | trademark, © Hetzner Online GmbH |

Every one of these is a **trademark of its owner**, used nominatively to name a
partner or a technology. A licence marked "public domain" or "Apache-2.0" is the
licence on the FILE, not permission over the mark. Do not restyle them beyond the
one-ink-plus-opacity treatment above, do not put them on a coloured plate, and do
not use them to imply endorsement.

## Changing the set

Re-run the measurement, do not eyeball it. Add the mark, render every file at a
common box height, take the median column ink-extent of each, and re-derive `k`
for the whole set — a new mark with a taller glyph column than Kafka's becomes the
new reference and every other `k` moves with it.

Then **re-measure the wall's one-line width**, because it is the trip point for
the container query in `components.css` and it is not derivable from anything
else. Seven marks and six `--space-12` gaps are 988.52 px today, which is why the
query sits at the register's 64rem. With text stand-ins that width was a rendered
STRING and the register said no script could hold it; with marks it is a sum of
boxes, and any browser gives the same number.
