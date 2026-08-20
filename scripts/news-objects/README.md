# The news title plates

Ten isometric drawings, one per published post in the Notion news database, in
the language `design-system/foundations/illustration.html` sets out: an object
is a lattice, a contour and one light.

```bash
python3 scripts/news-objects/objects.py           # draw them, and export the PNGs
python3 scripts/news-objects/objects.py --check   # fail if a drawing has drifted
python3 scripts/check-news-objects.py             # hold them to the projection
```

The vector is the **source**, in `svg/`. What **ships** is a 2016 px PNG in
`design-system/assets/img/news/`, and that split is not a preference: Notion does
not render an SVG in a Files property, so the Titelbild came out broken in the
database and the person choosing the picture could not see the picture. A format
the CMS cannot display is not a format this pipeline can use. `illustration.html`
is written about drawings *inline* in a page, where `vector-effect:
non-scaling-stroke` buys a 1 px contour at every size; it buys nothing through an
`<img>` the author cannot preview.

Two consequences worth knowing:

- **The export carries a heavier stroke than the source** (1.4 user units against
  1). A raster has no non-scaling-stroke: it is downscaled by whatever the card
  is — 2016 → 380 in the grid, 2016 → 568 in the lead cell — so a contour needs
  about 5 px in the file to arrive at 1 on screen. At 2016 px from a 572-unit
  viewBox the scale is 3.52, which puts that at 1.4.
- **Every export leaves through Pillow.** librsvg's PNG writer and Pillow's
  differ in filter choice and zlib settings, and one of the ten came out of
  librsvg as a byte stream Notion's edge refused — HTTP 403 from Cloudflare, on
  the content and not the request: the same upload slot took a different picture
  at 200, and the same picture failed a fresh slot twice. Re-encoded to identical
  pixels it uploads first time. A pipeline that produces an unpublishable file
  occasionally is worse than one that produces one always, so all ten go through
  the same encoder.

## What they replaced

The archive's ten `Titelbild`s were stock and generated photographs — fibre-optic
renders, wind farms at golden hour, and one plate that was the word "AI" set
white on black. That last one breaks three separate rules of the chapter above on
its own: **no text inside a drawing, no colour outside grey and the one lime ramp,
no raster.**

## Draw the proposition, not the plant

The first replacement was correct in every rule the checks can measure and wrong
in register: a battery container with cell-bay doors, a marking press with
uprights and a ram, a substation with cross-arms and insulator sheds. Technical
illustration of real equipment, done carefully, in the wrong language.

The four objects that ship are named in the chapter's own table by their **form**:

| | | |
|---|---|---|
| 01 | Discovery | stacked cuboids telescoping out of frame |
| 02 | Datenfundament | overlapping 63.43° plates, each finer than the last |
| 03 | Weniger Ausfälle | a solid of revolution read on its axis |
| 04 | Mehr Leistung | a sphere cut by its equator, three orbits |

None of the four is a thing you could buy. *"The brand's pictures are technical
drawings of objects that do not exist"* is not a licence to invent plausible
plant; it is the instruction to draw the **proposition** — a stack, a
subdivision, a body on its axis, a boundary, a detour — and let the copy name the
subject. A louvre is a detail about a cabinet. A trace that stops on a surface is
an argument about a boundary, and it is the same drawing whether the boundary is
a rack or a jurisdiction.

So these ten are stacks, plates, solids of revolution, orbits, subdivisions, the
lattice and the trace. Nothing in them has a supplier.

**Three greys, no more.** `#919191` and `#484848` are the *dense* register's
accent and aperture — the values that let a 95-to-145-element Expertise object
keep its contours. A news plate carries a dozen or two faces and runs in the
register the chapter states first, so the slots and sight glasses the first pass
spent them on went with the equipment that justified them.

**No arrows.** The trace is a sanctioned layer and these ten do not use it. What
a trace is for is the signal arriving, and in a set where several drawings are
*about* the connection — a detour round a constraint, a region joined by links, a
feeder that is there and not carrying — making the connection the one element
that is not part of the object put the subject outside the drawing. They are
members now: risers, spans, beams, each on a lattice axis. A hub with three arms
drawn and a fourth in ghost says what three arrows and a dashed one said, and it
says it in the object.

**Nothing is cut.** `fit()` takes the crop *after* the drawing, from the points
every primitive registered, pads them and widens the result to 3:2. The rule that
a frame is a crop and not a bounding box is a rule about composition, and
`scripts/expertise-objects/objects.py` records what it cost applied literally:
three passes on object 01, each fixing the cut that was reported, each read back
as the same sentence, *"the image is cut off"*. The four Expertise objects are
cropped to their own extent plus a pad, and so are these. The lattice is exempt —
it is a field, and a field is entitled to run off the edge.

**One size for the set.** `common_size()` measures every drawing and gives them
all the largest frame any of them needs, so the ten render at one scale in the
same 380 px card. Sized individually each fills its own frame and the archive
becomes ten drawings that happen to be adjacent — which is the failure
`illustration.html`'s "one size per set" exists to prevent.

**And lime is a moment, not a surface.** The first abstract pass put the ramp on
whatever the object's largest face happened to be — a 2.9 × 2.9 top, a full drum
end — which is 40 % of a frame in the one value the system spends most carefully.
The light goes on the element the eye should land on, and that is usually a small
one: a gate on a skin, a hub on an axis, a 0.16-deep course under four of them.
`lit_x` exists because such a course has no visible top face at all — what it
shows is its flank, and a flank is a flat face, so the ramp climbs it.

## Where the drawing lives, and where the file goes

`objects.py` is the source. It writes into
`design-system/assets/img/news/` **under the name the sync would give the
file** — `<stem>-<sha1[:8]>.svg`, the digest being of the bytes stored, which is
how `scripts/sync-news-notion.py` stops an hourly job rewriting the same
pictures every run. Because the name is a function of the bytes, the file this
writes and the file the sync downloads from Notion after the same drawing is
uploaded there **are the same file**. Regenerate, upload the result to the post's
`Titelbild`, and the next sync is a no-op rather than a churn.

Notion is still the source of truth for *which* picture a post carries. This
generator is the source of truth for *what the picture is*.

## The two things a standalone file has to carry itself

Every other illustration in this repository is inline SVG under `.cf-iso` and
inherits from `components.css` the two declarations that make a 1 px contour
survive being scaled. A file referenced by an `img` element inherits nothing, so
`isonews.py` inlines both in a `<style>` the file carries — without it a
600-unit drawing in a 300 px card puts its contours on screen at half a pixel.

The trace takes `non-scaling-stroke` here, and that is a departure from the
shipping class with its reason attached: `illustration.html` makes the trace the
one exception *because* the dash would otherwise be measured in screen px while
`pathLength` normalises against user space, ending the draw-on at 45 % of its
range. There is no draw-on in a file loaded through `img` — it cannot see a view
timeline, and the system's own rule is that the finished state is the authored
state. The exception's cause is absent, so the exception is too.

## Geometry

`isonews.py` sits on `scripts/expertise-objects/isolib.py`, so every vertex is a
lattice point by construction. What it changes is the register: the Expertise
objects carry 95–145 elements each and run near-white, a news plate is the
dozen-or-two-faces object the same chapter states first — `#DADADA` / `#CFCFCF`
/ `#C4C4C4` on CF-Grau, which is the value of its own shaded face.

The frame is 3:2 for all ten, because `.cf-blog-card__image` is
`aspect-ratio: 3 / 2; object-fit: cover` — authored at any other ratio and the
card crops the drawing with no say from here. One size for the set, so the
archive reads as one system rather than as ten drawings that happen to be
adjacent.

## What the gate measures

`scripts/check-news-objects.py` runs in CI beside the other 119. Two of its tests
are for things that are invisible:

- **Every straight edge is on a brand angle** — 26.57°, 63.43°, 45°, 90° or the
  level step's 0°. The chapter's own demonstration is a cube in textbook 30°
  isometry next to a correct one, five units wrong in the top face and barely
  different to look at: *"nothing about a wrong angle announces itself, it just
  stops registering with everything else on the page."* One mistyped coordinate
  puts a segment off the grid and no screenshot reports it. Arc commands are
  skipped — a solid of revolution has no vertices to snap, and what is on the
  lattice there is its axis, which is a straight segment like any other.
- **Nothing is outside the frame** — every drawn coordinate inside the viewBox,
  with the lattice group excluded.

Plus the absolutes: one lit element, no `<text>`, nothing outside the three greys
and the ramp, and the oklab waypoint at 19 % of each lime leg.

## The import path is untouched

An earlier pass opened `sync-news-notion.py` up to carry SVG — it had named the
format as its own example of what is refused — and taught
`check-image-scale.py` to read a size out of one. All of that is reverted. The
capability was never usable end to end: the import could accept a vector the CMS
could not display, which puts the broken preview one step earlier rather than
fixing it. What ships is a PNG at 2016 px and under 800 kB, which is what the
existing gates were already written for.
