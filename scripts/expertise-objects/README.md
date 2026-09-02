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

The four are drawn in the three-grey register — `#DADADA` / `#CFCFCF` / `#C4C4C4`, the
same values as every other object in the system — after shipping for a while in a
near-white register of their own; `isolib.py`'s header has the argument, and
`foundations/illustration.html` retired the second register with them. Each lights one
top face, runs the whole ramp inside it, and carries exactly two nodes, on that face's
back and right corners: `light_nodes_quad()` / `light_nodes_disc()` take the points off
the lit element, so they cannot be placed anywhere else.

Regenerating is deterministic to the byte. It was not: a half-turn arc's large-arc flag
was `span > pi` on a value that is pi to the last ulp, and two of the four files came back
from another machine's libm with eleven flags flipped and nothing changed on screen.
`_arc()` now carries the tolerance. After `python3 objects.py`, the four `<svg>` blocks in
the two pages are replaced with the files verbatim, at the pages' own indentation — so
anything a page needs on one of these elements has to come out of the generator. An
orbit's `--iso-orbit-travel` is the case in point: `scripts/check-orbit-turn.py` holds
every ring to a whole number of dashes inside one part in 19.52 of its circumference,
the declarations were once added to the pages by hand, and the next regeneration wiped
them. `isolib.orbit()` derives and writes the value itself now.

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

It also prints the six **values** that ride the routes, and those are generated for a
second reason: they have to add up. At any labelled point the value equals the sum of the
labelled values immediately downstream of it — 3 840 + 3 200 + 5 440 is the 12 480 that
left the void, and 1 360 + 4 080 is the 5 440 the right taproot carried. A point with
nothing labelled below it asserts nothing; unquantified is not the same as wrong.
`scripts/check-flow-values.py` holds that on the markup, together with the two facts a
number in a drawing cannot be trusted for on inspection: that its point lies exactly *on*
a segment, and that it carries `.t-label` rather than a page-local restatement of the mono
ramp. A number is the one kind of content that looks equally right whatever it says.

Which side of its own line a value sits on is computed, not chosen. A numeral is a
horizontal box on a sloped line, so eight pixels of clearance *at the point* is none at
all across the label: on the 26.57° runs the line drops 34 px over six digits and walks
back through them. A value on a line heading down-right therefore sits above it, one
heading down-left below it — the side the line is leaving — and the clearance grows across
the label instead of closing.
