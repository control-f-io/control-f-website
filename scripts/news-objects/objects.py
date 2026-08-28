"""Ten news title plates, one per published post in the Notion news archive.

WHAT THEY REPLACED. The archive's ten Titelbilder were stock and generated
photographs — fibre-optic renders, wind farms at golden hour, and one plate that
was the word "AI" set white on black. Three rules of
foundations/illustration.html are against that last one alone: no text inside a
drawing, no colour outside grey and the one lime ramp, no raster.

AND THE FIRST REPLACEMENT WAS TOO LITERAL, which is the more interesting fault
and the reason this file reads the way it does. It drew a battery container with
cell-bay doors, a marking press with uprights and a ram, a substation with
cross-arms and insulator sheds — technical illustration of real equipment, done
correctly and in the wrong language. The four objects that ship are named in the
chapter's own table by their FORM and not by any machine:

    01  Discovery         stacked cuboids telescoping out of frame
    02  Datenfundament    overlapping 63.43 deg plates, each finer than the last
    03  Weniger Ausfälle  a solid of revolution read on its axis
    04  Mehr Leistung     a sphere cut by its equator, three orbits

None of the four is a thing you could buy. "The brand's pictures are technical
drawings of objects that do not exist" is not a licence to invent plausible
plant; it is the instruction to draw the PROPOSITION — a stack, a subdivision, a
body on its axis, a boundary, a detour — and let the copy name the subject. A
louvre is a detail about a cabinet. A trace that stops on a surface is an
argument about a boundary, and it is the same drawing whether the boundary is a
rack or a jurisdiction.

So: stacks, plates, solids of revolution, orbits, subdivisions, the lattice, and
the trace. Nothing that has a supplier.

THREE GREYS, NO MORE. #919191 and #484848 are the dense register's accent and
aperture — the values that let a 95-to-145-element Expertise object keep its
contours. A news plate carries a dozen or two faces and runs in the register the
chapter states first, so the slots and sight glasses the first pass spent them on
are gone with the equipment that justified them.

ONE LIT ELEMENT EACH, and it is the element the eye is meant to land on. The
rake follows what is lit: `near` for a flat face, `mid` for a body turning away,
`far` for a rim.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from isonews import (  # noqa: E402
    iso, P, p_, f, poly, line, face, box, quad_t, quad_x, quad_y, seams,
    disc, hoop, cyl, drum, taper, orbit, node, reset,
    TOP, LIT, SHADE, light_def, lit, lit_top, lit_x, lattice, emit, fit,
    common_size,
)

# The level step. Both ground axes slope 26.57 deg on screen, so a row marched
# along either one loses a unit of drawn height per step — the trap the plot
# fell into, where five columns rising 31 to 100 came out with the tallest drawn
# lower than the shortest. e1 - e2 is (+1, -1): still a lattice move, and the
# only way to go sideways without descending.
LEVEL = (1.0, -1.0)


def stack(x, y, z, base, dz, n, inset, taper_z=1.0):
    """Cuboids on one axis, each inset from the one below. The whole vocabulary
    of object 01 and half of object 02, and the shape a proposition about
    refinement or accumulation takes before it takes any other."""
    out = []
    for i in range(n):
        s = base - 2 * inset * i
        h = dz * (taper_z ** i)
        out += box(x + inset * i, y + inset * i, z, s, s, h, TOP, SHADE, LIT)
        z += h
    return out


def plates(x, y, z, base, th, gap, n, inset):
    """Overlapping plates, each finer than the last — object 02's form. The
    inset is what carries "finer"; the gap is what stops it reading as a solid."""
    out = []
    for i in range(n):
        s = base - 2 * inset * i
        out += box(x + inset * i, y + inset * i, z + i * (th + gap),
                   s, s, th, TOP, SHADE, LIT)
    return out


def beam(x, y, z, axis_, length, s=0.28):
    """A member on one lattice axis. Every link in this set is one of these
    rather than a trace: with the arrows gone, what connects two bodies has to
    be a thing, and a thing on a lattice axis is the only kind this projection
    draws."""
    dx, dy, dz = (length, s, s) if axis_ == 'x' else \
                 ((s, length, s) if axis_ == 'y' else (s, s, length))
    return box(x, y, z, dx, dy, dz, TOP, SHADE, LIT)


# TWO RULES HOLD THIS SET TOGETHER, AND BOTH ARE ARITHMETIC.
#
# EVERY EDGE ON A MULTIPLE OF TWO. lattice() draws its two families at constant
# x and constant y in steps of 2, so a body whose faces sit on even coordinates
# stands on the drawn grid and one that does not floats a half-cell off it. The
# lattice is the only thing in the frame a reader can measure the object
# against; agreeing with it is most of what "aligned" means here.
#
# EVERY OBJECT SYMMETRIC UNDER x <-> y. Screen x is (x - y), so swapping the two
# ground axes mirrors the drawing about the vertical through its centre: a form
# that survives the swap is bilaterally symmetric on the plate, and one that
# does not leans. A body centred on the diagonal survives it alone; anything
# else has to come in a pair, one on each ground axis. That is why the members
# below are always two, never one.
#
# FOUR NODES ON THE LIT FACE, WHICH IS THE SAME RULE AGAIN. The specimen on
# foundations/illustration.html puts r = 3 on all four corners of the face it
# lights. Three of the four is not a lighter version of that: it is an
# asymmetry, and on a square read at 380 px the eye finds the missing corner
# before it finds the object. Nothing steps down below the lit face here —
# a plate has one subject and no third stage to mark.


# ==================================================================== 01
def offshore():
    """WindSeeG: two decades resting on a seven-day window.

    Three concentric slabs, each standing on the one below, and the smallest is
    lit."""
    reset()
    forms = box(0.0, 0.0, 0.0, 12.0, 12.0, 1.0, TOP, SHADE, LIT)
    forms += box(2.0, 2.0, 1.0, 8.0, 8.0, 3.0, TOP, SHADE, LIT)
    forms += box(4.0, 4.0, 4.0, 4.0, 4.0, 3.0, TOP, SHADE, LIT)
    la, lb, light = lit_top('n01', 4.0, 4.0, 7.0, 4.0, 4.0)
    nd = [node(4.0, 4.0, 7.0, 3), node(8.0, 4.0, 7.0, 3),
          node(8.0, 8.0, 7.0, 3), node(4.0, 8.0, 7.0, 3)]
    return light_def('n01', 'near', la, lb), forms, light, (), (), nd


# ==================================================================== 02
def labelling():
    """The AI Act's labelling duty: the mark is on the thing, or it is nowhere.

    One body, one square set in the centre of its face, and the square is what
    is lit."""
    reset()
    forms = box(0.0, 0.0, 0.0, 12.0, 12.0, 5.0, TOP, SHADE, LIT)
    forms += box(4.0, 4.0, 5.0, 4.0, 4.0, 1.0, TOP, SHADE, LIT)
    la, lb, light = lit_top('n02', 4.0, 4.0, 6.0, 4.0, 4.0)
    nd = [node(4.0, 4.0, 6.0, 3), node(8.0, 4.0, 6.0, 3),
          node(8.0, 8.0, 6.0, 3), node(4.0, 8.0, 6.0, 3)]
    return light_def('n02', 'near', la, lb), forms, light, (), (), nd


# ==================================================================== 03
def redispatch():
    """Redispatch: the direct way is closed and the cost is the way round.

    A centre held between two equal masses, and what is lit is the centre — the
    money is spent in the middle, on the detour, not at either end.

    The centre is drawn FIRST: depth here is x + y, and at (4, 4) it stands
    behind both masses."""
    reset()
    forms = box(4.0, 4.0, 0.0, 2.0, 2.0, 8.0, TOP, SHADE, LIT)
    forms += box(0.0, 6.0, 0.0, 4.0, 4.0, 6.0, TOP, SHADE, LIT)
    forms += box(6.0, 0.0, 0.0, 4.0, 4.0, 6.0, TOP, SHADE, LIT)
    la, lb, light = lit_top('n03', 4.0, 4.0, 8.0, 2.0, 2.0)
    nd = [node(4.0, 4.0, 8.0, 3), node(6.0, 4.0, 8.0, 3),
          node(6.0, 6.0, 8.0, 3), node(4.0, 6.0, 8.0, 3)]
    return light_def('n03', 'near', la, lb), forms, light, (), (), nd


# ==================================================================== 04
def electrolyser():
    """Hydrogen under a controller: separation, drawn as plates.

    Three concentric plates with air between them. The finest is lit."""
    reset()
    forms = box(0.0, 0.0, 0.0, 12.0, 12.0, 1.0, TOP, SHADE, LIT)
    forms += box(2.0, 2.0, 3.0, 8.0, 8.0, 1.0, TOP, SHADE, LIT)
    forms += box(4.0, 4.0, 6.0, 4.0, 4.0, 1.0, TOP, SHADE, LIT)
    la, lb, light = lit_top('n04', 4.0, 4.0, 7.0, 4.0, 4.0)
    nd = [node(4.0, 4.0, 7.0, 3), node(8.0, 4.0, 7.0, 3),
          node(8.0, 8.0, 7.0, 3), node(4.0, 8.0, 7.0, 3)]
    return light_def('n04', 'near', la, lb), forms, light, (), (), nd


# ==================================================================== 05
def cluster():
    """An on-premise cluster, drawn as the boundary it is bought for.

    A closed ring and the one thing inside it, which is what is lit.

    BACK TO FRONT, AND THE RING IS WHY. The two walls at low x and low y are
    behind what they enclose, the other two are in front of it. Painted in any
    other order the body inside cuts into the near wall and the boundary stops
    being closed."""
    reset()
    forms = box(0.0, 0.0, 0.0, 12.0, 2.0, 4.0, TOP, SHADE, LIT)
    forms += box(0.0, 2.0, 0.0, 2.0, 10.0, 4.0, TOP, SHADE, LIT)
    forms += box(4.0, 4.0, 0.0, 4.0, 4.0, 2.0, TOP, SHADE, LIT)
    forms += box(2.0, 10.0, 0.0, 10.0, 2.0, 4.0, TOP, SHADE, LIT)
    forms += box(10.0, 2.0, 0.0, 2.0, 8.0, 4.0, TOP, SHADE, LIT)
    la, lb, light = lit_top('n05', 4.0, 4.0, 2.0, 4.0, 4.0)
    nd = [node(4.0, 4.0, 2.0, 3), node(8.0, 4.0, 2.0, 3),
          node(8.0, 8.0, 2.0, 3), node(4.0, 8.0, 2.0, 3)]
    return light_def('n05', 'near', la, lb), forms, light, (), (), nd


# ==================================================================== 06
def storage():
    """Storage as a flexibility asset: flat arrivals, one body that holds.

    Two plates on the two ground axes, and the mass they run into is lit."""
    reset()
    forms = box(0.0, 4.0, 0.0, 4.0, 4.0, 1.0, TOP, SHADE, LIT)
    forms += box(4.0, 0.0, 0.0, 4.0, 4.0, 1.0, TOP, SHADE, LIT)
    forms += box(4.0, 4.0, 0.0, 6.0, 6.0, 6.0, TOP, SHADE, LIT)
    la, lb, light = lit_top('n06', 4.0, 4.0, 6.0, 6.0, 6.0)
    nd = [node(4.0, 4.0, 6.0, 3), node(10.0, 4.0, 6.0, 3),
          node(10.0, 10.0, 6.0, 3), node(4.0, 10.0, 6.0, 3)]
    return light_def('n06', 'near', la, lb), forms, light, (), (), nd


# ==================================================================== 07
def verteilnetz():
    """The distribution grid: a hub and what leaves it.

    A cross on the lattice's own ground axes, four arms of one length, and the
    hub is lit. The two near arms are painted after the hub they leave."""
    reset()
    forms = box(0.0, 4.0, 0.0, 4.0, 4.0, 2.0, TOP, SHADE, LIT)
    forms += box(4.0, 0.0, 0.0, 4.0, 4.0, 2.0, TOP, SHADE, LIT)
    forms += box(4.0, 4.0, 0.0, 4.0, 4.0, 4.0, TOP, SHADE, LIT)
    forms += box(8.0, 4.0, 0.0, 4.0, 4.0, 2.0, TOP, SHADE, LIT)
    forms += box(4.0, 8.0, 0.0, 4.0, 4.0, 2.0, TOP, SHADE, LIT)
    la, lb, light = lit_top('n07', 4.0, 4.0, 4.0, 4.0, 4.0)
    nd = [node(4.0, 4.0, 4.0, 3), node(8.0, 4.0, 4.0, 3),
          node(8.0, 8.0, 4.0, 3), node(4.0, 8.0, 4.0, 3)]
    return light_def('n07', 'near', la, lb), forms, light, (), (), nd


# ==================================================================== 08
def platforms():
    """Two data platforms, drawn as two ways of building one volume.

    Layers you can count and a body you cannot, the same height at mirrored
    places on the grid. What is lit is the stack."""
    reset()
    forms = plates(0.0, 6.0, 0.0, 4.0, 1.0, 0.5, 4, 0.0)
    forms += drum(8.0, 2.0, 0.0, 2.0, 5.5, top=TOP, side=LIT)
    la, lb, light = lit_top('n08', 0.0, 6.0, 5.5, 4.0, 4.0)
    nd = [node(0.0, 6.0, 5.5, 3), node(4.0, 6.0, 5.5, 3),
          node(4.0, 10.0, 5.5, 3), node(0.0, 10.0, 5.5, 3)]
    return light_def('n08', 'near', la, lb), forms, light, (), (), nd


# ==================================================================== 09
def maintenance():
    """Predictive maintenance: a body read on its axis.

    A solid of revolution and the hub the axis runs through, which is lit. The
    four nodes are the hub's own cardinal points — a disc has no corners, and
    the rule is four marks, not four corners."""
    reset()
    forms = drum(6.0, 6.0, 0.0, 4.0, 5.0, top=TOP, side=LIT)
    forms += drum(6.0, 6.0, 5.0, 2.0, 1.0, top=None, side=LIT)
    # The span is in user units, not radii: at 2.6 across a hub of radius 2 the
    # ramp never leaves lime and the light stops being a moment. Five radii is
    # what the rest of the set spends.
    la, lb = iso.lime_span_disc(6.0, 6.0, 6.0, 2.0, axis='z', span=10.0)
    light = iso.light_disc('n09', 6.0, 6.0, 6.0, 2.0, axis='z')
    nd = [node(4.0, 6.0, 6.0, 3), node(8.0, 6.0, 6.0, 3),
          node(6.0, 4.0, 6.0, 3), node(6.0, 8.0, 6.0, 3)]
    return light_def('n09', 'far', la, lb), forms, light, (), (), nd


# ==================================================================== 10
def region():
    """A region of connected platforms: what is between them is the subject.

    A centre and two sites, one on each ground axis, joined by two members of
    one length. The centre is lit, and it is nearest, so it is painted last."""
    reset()
    forms = box(0.0, 4.0, 0.0, 4.0, 4.0, 3.0, TOP, SHADE, LIT)
    forms += box(4.0, 0.0, 0.0, 4.0, 4.0, 3.0, TOP, SHADE, LIT)
    forms += box(4.0, 8.0, 2.0, 4.0, 2.0, 1.0, TOP, SHADE, LIT)
    forms += box(8.0, 4.0, 2.0, 2.0, 4.0, 1.0, TOP, SHADE, LIT)
    forms += box(8.0, 8.0, 0.0, 4.0, 4.0, 6.0, TOP, SHADE, LIT)
    la, lb, light = lit_top('n10', 8.0, 8.0, 6.0, 4.0, 4.0)
    nd = [node(8.0, 8.0, 6.0, 3), node(12.0, 8.0, 6.0, 3),
          node(12.0, 12.0, 6.0, 3), node(8.0, 12.0, 6.0, 3)]
    return light_def('n10', 'near', la, lb), forms, light, (), (), nd


OBJECTS = {
    'sieben-tage-fuer-zwei-jahrzehnte-was-die': (offshore, 'Ein teleskopierender Stapel auf einer einzigen dünnen Platte'),
    'ki-kennzeichnung-was-der-ai-act-jetzt-ve': (labelling, 'Ein Körper mit einer kleineren Marke, in seine Fläche eingesetzt'),
    'drei-milliarden-fuer-ein-netz-das-es-so': (redispatch, 'Eine verstellte Achse und der Umweg darüber'),
    'gastbeitrag-ki-ist-notwendigkeit-fuer-di': (electrolyser, 'Übereinanderliegende Platten, jede feiner als die vorige'),
    'ki-im-netzbetrieb-wie-llm-cluster-gegen': (cluster, 'Ein geschlossener Körper; die Signale enden auf seiner Haut'),
    'batteriespeicher-als-flexibilitaets-asse': (storage, 'Eine ebene Reihe, die in einen einzelnen speichernden Körper läuft'),
    'wie-wir-mit-digitalisierung-im-verteilne': (verteilnetz, 'Ein Knoten mit vier Armen; einer ist da und trägt nichts'),
    'databricks-vs-snowflake-welche-datenplat': (platforms, 'Zwei Bauweisen über einem geteilten Grundriss'),
    'predictive-maintenance-fuer-kommunale-en': (maintenance, 'Ein Rotationskörper auf seiner Achse, mit Orbit und künftigem Profil'),
    'wie-die-bodenseeregion-von-vernetzten-da': (region, 'Drei Körper auf einem Gitter, über Gitterachsen verbunden'),
}


def build(fn, title, size=None):
    """THE CROP IS TAKEN AFTER THE DRAWING, not before it. fit() reads the
    points every primitive registered, pads them and widens the result to 3:2,
    so no part of an object can end up outside its own frame. The lattice is
    generated from that crop afterwards and registers nothing: it is a field,
    and a field is entitled to run off the edge."""
    defs, forms, light, ghost, orbits, nd = fn()
    crop = fit(size=size)
    return emit(title, crop, defs, [forms], light, ghost, orbits, (), nd,
                underlay=lattice(crop))


# WHAT SHIPS IS A PNG, AND THE VECTOR IS THE SOURCE IT IS MADE FROM.
#
# These were SVG in the store for two rounds, on illustration.html's own
# instruction — "SVG, always ... no raster export" — and the import path was
# opened up to carry them. What that missed is that the archive's editor is
# Notion, and Notion does not render an SVG in a Files property: the Titelbild
# came out broken in the database, so the person choosing the picture could not
# see the picture. A format the CMS cannot display is not a format this pipeline
# can use, whatever the chapter says about contours — and the chapter is written
# about drawings INLINE in a page, where the rule buys a 1 px contour at every
# size. It buys nothing through an <img> the author cannot preview.
#
# So the vector stays the source, under scripts/news-objects/svg/ with a stable
# name, and the export is a 2016 px PNG — two plates wide, which is the ceiling
# check-content-images.py allows and what a dpr-2 screen resolves across the
# 1008 px plate.
#
# THE EXPORT CARRIES A HEAVIER STROKE THAN THE SOURCE, and that is arithmetic
# rather than taste. In a browser the source draws its contours at 1 CSS px at
# any size, because .cf-iso sets vector-effect: non-scaling-stroke. A raster has
# no such thing: it is downscaled by whatever the card is, 2016 -> 380 in the
# grid and 2016 -> 568 in the lead cell, so a contour needs to be about 5 px in
# the file to arrive at 1. At 2016 px from a 572-unit viewBox the scale is 3.52,
# which puts that at 1.4 user units.
#
# NOTHING HERE RUNS BY ITSELF, AND THE EXPORT DOES NOT GO INTO THE SITE.
#
# This file used to write its PNGs straight into
# design-system/assets/img/news/ under the name the sync would give them, so
# that a picture uploaded to Notion afterwards came back to the same path. Two
# stores then claimed the same pictures, and the archive was emptied twice
# working out which one was in charge: once when the sync swept plates the
# generator had just committed, and once when an upload to Notion failed
# quietly and the sync read the missing picture as an editorial decision.
#
# NOTION IS THE ONE PLACE A PICTURE COMES FROM. This is a drawing tool that is
# run when somebody asks for it, by hand; the export lands in png/ next to the
# sources, and a person uploads what they want from there into the post's
# Titelbild. What the site ships is whatever Notion holds — downloaded, named
# and swept by scripts/sync-news-notion.py, which is the only writer that image
# folder has. png/ is not committed for the same reason: a copy in the
# repository is a second answer to a question that now has one.

SVG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'svg')
PNG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'png')

EXPORT_W = 2016          # two plates; check-content-images.py's ceiling
EXPORT_STROKE = 1.4      # see the note above


def for_raster(svg):
    """The source, prepared for a rasteriser: the <style> block dropped and one
    stroke width set on the scene.

    The block is exactly the two declarations a standalone file carries because
    it inherits no stylesheet, and both are wrong for an export. non-scaling-
    stroke would pin every contour to one device pixel of a 2016 px image, which
    is a quarter of a CSS pixel by the time a card has finished with it."""
    out = re.sub(r'<style>.*?</style>', '', svg, flags=re.S)
    return out.replace('<g class="cf-iso__scene" stroke="#000"',
                       '<g class="cf-iso__scene" stroke-width="%s" stroke="#000"'
                       % EXPORT_STROKE)


def rasterise(svg, stem):
    """The source through rsvg-convert, then re-encoded by Pillow.

    THE RE-ENCODE IS NOT AN OPTIMISATION. librsvg's PNG writer and Pillow's
    differ in filter choice and zlib settings, and one of the ten drawings came
    out of librsvg as a byte stream that Notion's edge refused: HTTP 403 from
    Cloudflare, on the file's content and not on the request — the same slot took
    a different picture at 200, and the same picture failed a fresh slot twice.
    Re-encoded to identical pixels it uploads first time.

    A picture the CMS will not accept is a picture that cannot be published, and
    a pipeline that produces one occasionally is worse than one that produces one
    always: this way every export leaves through the same encoder, so a drawing
    either uploads or none of them do. Pillow is already this repository's one
    dependency — scripts/sync-news-notion.py pins it for fit_to_plate.
    """
    import io
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, stem + '.svg')
        with open(src, 'w', encoding='utf-8') as fh:
            fh.write(for_raster(svg))
        try:
            out = subprocess.run(
                ['rsvg-convert', '-w', str(EXPORT_W), src],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        except FileNotFoundError:
            raise SystemExit(
                "news-objects: the PNG export needs rsvg-convert.\n"
                "    brew install librsvg\n"
                "    --check does not need it: it compares the SVG sources.")
    from PIL import Image
    im = Image.open(io.BytesIO(out))
    im.load()
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def emit_all(check=False):
    bad = 0
    size = common_size([fn for fn, _ in OBJECTS.values()])
    os.makedirs(SVG_DIR, exist_ok=True)
    for stem, (fn, title) in OBJECTS.items():
        svg = build(fn, title, size).encode('utf-8')
        src = os.path.join(SVG_DIR, stem + '.svg')
        same = os.path.exists(src) and open(src, 'rb').read() == svg
        if check:
            bad += not same
            print(("ok   " if same else "DRIFT") + "  " + stem + '.svg')
            continue
        if not same:
            with open(src, 'wb') as fh:
                fh.write(svg)
        png = rasterise(svg.decode('utf-8'), stem)
        name = stem + '.png'
        path = os.path.join(PNG_DIR, name)
        os.makedirs(PNG_DIR, exist_ok=True)
        if not os.path.exists(path) or open(path, 'rb').read() != png:
            with open(path, 'wb') as fh:
                fh.write(png)
        print("%7d B  %s" % (len(png), name))
    return bad


if __name__ == '__main__':
    check = '--check' in sys.argv
    drift = emit_all(check)
    if check and drift:
        print("\n%d drawing(s) differ from what objects.py produces." % drift)
        sys.exit(1)
