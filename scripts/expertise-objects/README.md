# The four Expertise objects

`python3 objects.py` re-emits `0{1..4}-*.svg` in this directory. Those four files are
inlined verbatim into `design-system/patterns/expertise.html` and
`design-system/prototypes/expertise-scroll.html` — they are the source the pages were
built from, kept here because a drawing of 95 to 145 elements is not something anyone
should have to edit by hand a second time.

- `isolib.py` — the projection and the primitives. `+x` is 26.57° down-right, `+y`
  26.57° down-left, `+z` vertical, and every vertex comes from a lattice coordinate, so
  every edge lands on a brand angle by construction. Circles are computed rather than
  eyeballed: `_ell()` takes the singular values of the projection restricted to a lattice
  plane, which is what makes every drum, hoop, wheel, flange and rotor exact, and what
  gives `cyl()` the tangent points where a cylinder's silhouette leaves its end caps.
- `objects.py` — the four drawings.

Two conventions in here are load-bearing and are documented on
`design-system/foundations/illustration.html`:

**Stages are depth bands, back to front.** Each `.cf-iso__form` group carries
`data-stage`, and the page's build animation brings them up in that order. A stage is a
`<g>`, so everything in stage 2 paints over everything in stage 1 regardless of the order
it was written in — ordering the stages by depth is therefore the only assignment that is
correct as a drawing *and* as a build.

**Nothing pierces the plate.** Anything standing on a foundation stands on it: a mast is a
slender box, not a line, and a line that would run into the plate is not drawn. Hairlines
ending inside the plate are exactly what read as brittle at stage size.

The generator also writes `--vb-w` and `--iso-travel` into each `<svg>`, both derived from
the same number that produced the crop, so a re-crop cannot leave the arrival distance
behind. See `foundations/motion.html#travel`.

## The landing page's root

`python3 gen-flow-root.py` prints the geometry of `.lp-flow` — the drawing that carries
the reader from the statement's void down into the frame the four process cards are built
in — as paths and nodes ready to paste into `design-system/patterns/landing-page.html`.
It shares this directory's premise and not its library: the flow is 2-D and is not a
`.cf-iso` drawing, so it computes in the page's own 1200 × 620 units rather than on the
isometric lattice, in exact rational arithmetic.

It is here because a self-similar form is not something anyone types by hand and keeps on
the five brand angles, and because a construction may not be random at runtime — the same
paths come out every run. Three of its terminals are pinned rather than grown: flow
x 0, 600 and 1200 are frame x 0, 500 and 1000, so the three taproots must land exactly on
the frame's three verticals, two of them in its top corners.

`scripts/check-flow-terminals.py` holds the result — every terminal on the rail, the void
or another branch; every segment on a brand angle; every node on a junction — against the
*markup*, which is where a hand edit would land.
