# Process plant illustration references

Inspected on 2026-09-07. These manufacturer photographs ground silhouettes and
construction details in `anlagen()` in `objects.py`. The SVG combines equipment
types into a compact illustration; it does not identify a model, reproduce an
installation, or specify a process flow.

## Tower and pipe rack — Sulzer

- Page: https://www.sulzer.com/en/shared/products/distillation
- Inspected image: https://www.sulzer.com/-/media/images/products/separation-technology/06912534_production_plant_distillation_columns_1920x1280.jpg?hash=EBA899AC0EE9C96BED0C8267C2CEE972&la=en&mw=720
- Observed: slender vertical shells with horizontal courses, reduced/rounded
  crowns, access ladders and projecting manways; substantial overhead pipe runs
  descend beside the vessels and rest on structural racks.
- Applied: shouldered tower crown and shallow flanged lid, shell courses,
  attached ladder and manway, supported header with a routed drop outside the
  rack beam. The ladder cage, platforms and most plant piping are omitted to
  preserve legibility at the page's illustration size.

## Heat exchangers — Alfa Laval

- Page: https://www.alfalaval.com/en-GB/products/heat-transfer/tubular-heat-exchangers/shell-and-tube-heat-exchanger/
- Inspected image: https://www.alfalaval.co.uk/globalassets/images/industries/marine-and-transportation/marine/alfa-laval-shell-and-tube-heat-exchanger-aalborg-mx-right-view.jpg
- Observed: a horizontal cylindrical shell held by two ring saddle brackets with
  flat mounting feet; an enlarged bolted removable end head; upright flanged
  nozzles at separated positions; a small end connection.
- Applied: identical parallel units with true contacting saddles, saddle straps,
  larger channel heads, six equally spaced bolts on each end flange, paired top
  nozzles and small end connections. One common feed joins the units visibly.

## Motor and pump — KSB

- Page: https://www.ksb.com/en-th/applications/industry-technology/ksb-eta-family
- Inspected image: https://acszigalen.cloudimg.io/v7/https%3A%2F%2Flive-resources-e2e-sales.ksb.com%2Fresource%2Fimage%2F1231420%2Flandscape_ratio16x9%2F3300%2F1856%2F1d5ab389a434c499c1830118e4de081c%2FF5B7A46F3BC4C2B0C1B970AD982A56B4%2Fpic-product-details-etanorm.jpg?ci_url_encoded=1&force_format=webp&height=675&q=60&width=1200
- Observed: ribbed electric motor, top controller/terminal housing, narrower
  coupling guard, rounded centrifugal pump casing, axial flanged inlet and
  vertical discharge. Motor and pump have separate feet on a shared baseplate.
- Applied: those distinct connected volumes, longitudinal motor fins, feet,
  flanges and a small controller face. The discharge connects to the shared feed.

## Vertical storage vessel — Paul Mueller Company

- Page: https://nl.paulmueller.com/voedselverwerkende-apparatuur/silos/standaard-silo/
- Inspected image: https://www.paulmueller.com/hubfs/Food-Processing/Products/Silos/Standard-Silo/Stainless-steel-silos.jpg
- Observed: cylindrical tanks sit on concrete bases; their shells have horizontal
  courses, shallow roofs, access ladders and lower service connections. The
  photographed installation includes connecting overhead pipes and platforms.
- Applied: a ring foundation, shallow roof, top connection flange, low manway,
  attached ladder and a continuous branch from the rack header. Proportions are
  composed for the illustration rather than copied from the pictured silos.

## Shared drawing constraints

- Retain the repository's near-white directional face tokens and contour style.
- Use a single gradient on the tower's flanged lid and four equal nodes placed
  at the exact symmetric extrema of that projected circle.
- Preserve the original concrete-pad footprint and four depth stages.
- Keep the exchanger pair identical and use computed circular bolt placement.
