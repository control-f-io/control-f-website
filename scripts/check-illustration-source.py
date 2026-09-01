#!/usr/bin/env python3
"""The four process objects still are the designer's vectors.

`design-system/assets/source/illustrations/` holds the designer's own exports of
the four "Was wir machen" objects. They are the authority: where the source and
the implementation disagree, the source wins unless there is a documented
reason. components/process-card.html states the relationship in prose —

    "The four objects are now built from the designer's source vectors, not
     approximated. Geometry, gradient stops and construction points are the
     exported ones; three things were changed on purpose"

— and, of card 04's orbit, makes the stronger claim outright:

    "Restored to the source verbatim, so a diff against
     assets/source/illustrations/ now shows no drift on this object."

Nothing performed that diff. The claim was true when it was written and had no
way of staying true: an object is 19 to 37 hand-written elements inside a page
of 2,278 lines, and a coordinate that moves by three units in a re-draw renders
as a picture that still looks entirely correct. That is the same failure mode
the README's own "four things that vanish quietly" is about, one level up — not
a token that goes missing from a drawing, but the drawing going missing from
the designer's drawing.

WHAT IS CHECKED. Every geometry element of every shipped process object must
appear in that object's source vector, coordinate for coordinate: tag, its
geometric attributes, and its transform. Numbers are compared at two decimals,
which is the precision the exports are written to. An element that matches
nothing in the source is drift and fails.

WHAT IS ALLOWED, AND WHY EACH ONE IS A RULE RATHER THAN A LIST. Four classes of
difference are sanctioned. Three of them are verified as rules — the script
re-derives the reason and fails if the reason does not hold — so a fifth
deviation cannot arrive by resembling one of them:

  1. DASH PATTERN. The exports carry 8-2, 2-8 and 2-2; the system holds four
     line types. A shipped dash may differ from its source freely, because
     check-line-types.py already owns the claim that every dash in the tree is
     one of the four, measured against --dash-* in px. Two scripts asserting one
     invariant to two standards is the drift this family exists to prevent, so
     this one asserts nothing about dashes at all and says where the rule lives.

  2. A DROPPED TRANSFORM, only where dropping it is provably a no-op. The source
     puts rotate(-90 ...) on construction points that are flat-filled circles,
     and components/process-card.html spends a section on why dropping it there
     is correct and why dropping the identical attribute from the orbit beside
     it was a defect: "never drop a transform from an element that is painted
     with a userSpaceOnUse gradient, however redundant it looks against the
     geometry". That is the rule, so that is what is checked — a transform may
     be dropped only when it is a rotation about the element's OWN centre, the
     element is a circle (rx == ry, so the rotation cannot move a point of it),
     AND every paint on it is a flat colour rather than a url(). Fail any one of
     the three and it is drift, which is exactly the orbit's defect.

  3. A TRACE SPLIT INTO ITS SUBPATHS. Card 03's incoming signal is one <path>
     of five subpaths in the export and five .cf-iso__trace elements in the
     implementation, because "a dash pattern restarts at every subpath while
     pathLength normalises the path as a whole" — the measured defect
     foundations/motion.html records at cover 26.8 % of a range running to 45 %.
     Checked as a partition: the shipped traces' subpaths must be exactly the
     source path's subpaths, as a multiset, each one either forwards or
     reversed. A stroke that moved, vanished or was added fails; only the
     bookkeeping of which element carries which stroke is free.

  4. THE ONE TRUED ANGLE. Card 04's trace leaves the sphere at 26.96 degrees in
     the export and the system sanctions four angles. It is trued to exactly
     26.57 — a 2:1 run over rise — and that is checked arithmetically rather
     than whitelisted: the shipped line must share its origin with the source
     line, must be exactly 2:1, and the source must NOT already be. A second
     endpoint edited for any other reason fails.

WHAT IS DELIBERATELY NOT CHECKED. Colour, gradient stops and the oklab waypoint:
scripts/check-gradient-family.py recomputes that waypoint from the oklab path,
which is strictly the stronger claim, and check-paint-register.py owns the
literals. Card 02's second lime plate dropping to Glas and lime being #E1FF00
rather than the export's #E0FF02 are both colour decisions and both live there.
The Figma inner-shadow filter on card 03 is not checked either: it is a <filter>
and not geometry, and foundations/illustration.html's six material layers are
what rule it out.

Usage:
    check-illustration-source.py       fail on drift
    check-illustration-source.py -v    print every element, matched or deviated
"""

import glob
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, "design-system", "assets", "source", "illustrations")

# Every page in the tree, generated editions and prototypes included. A shipped
# object is identified by the id prefix its own <defs> declare — cf-01- to
# cf-04- — which is how the four are told apart wherever they stand.
PAGES = sorted(
    glob.glob(os.path.join(ROOT, "design-system", "**", "*.html"), recursive=True)
)

CARD_ID = re.compile(r'id="cf-(0[1-4])-')
SVG = re.compile(r'<svg\b[^>]*\bclass="cf-iso\b[^"]*"[^>]*>(.*?)</svg>', re.S)
DEFS = re.compile(r"<defs\b.*?</defs>", re.S)
ELEMENT = re.compile(r"<(path|circle|ellipse|line|rect|polygon|polyline)\b([^>]*?)/?>")
NUMBER = re.compile(r"-?\d+(?:\.\d+)?")

# The geometry of each shape — everything that decides where its ink lands.
GEOMETRY = {
    "path": ("d",),
    "circle": ("cx", "cy", "r"),
    "ellipse": ("cx", "cy", "rx", "ry"),
    "line": ("x1", "y1", "x2", "y2"),
    "rect": ("x", "y", "width", "height", "rx", "ry"),
    "polygon": ("points",),
    "polyline": ("points",),
}

# The exports write outlined text as <path>. Nothing drawn in this system comes
# near this length, and the alternative — classifying glyphs — is a judgement
# where this is a measurement.
GLYPH_LENGTH = 400


def rounded(text):
    """Numbers at two decimals, which is what the exports are written to."""
    return NUMBER.sub(lambda m: "%g" % round(float(m.group()), 2), text)


def tidy(text):
    return rounded(re.sub(r"[,\s]+", " ", text or "").strip())


def tidy_path(d):
    return tidy(re.sub(r"([A-Za-z])", r" \1 ", d or ""))


def attr(attrs, name):
    m = re.search(r'\b%s="([^"]*)"' % re.escape(name), attrs)
    return m.group(1) if m else ""


def parse(svg_body, drop_glyphs):
    """Geometry elements of one drawing, <defs> stripped.

    <defs> holds the clip rectangle and the paint servers. The clip is the frame
    rather than part of the object, and the paint servers are colour, which
    belongs to the two scripts named at the top of this file.
    """
    body = DEFS.sub("", svg_body)
    out = []
    for m in ELEMENT.finditer(body):
        tag, attrs = m.group(1), m.group(2)
        values = []
        for name in GEOMETRY[tag]:
            raw = attr(attrs, name)
            values.append(tidy_path(raw) if name in ("d", "points") else tidy(raw))
        if drop_glyphs and tag == "path" and len(values[0]) > GLYPH_LENGTH:
            continue
        out.append(
            {
                "tag": tag,
                "values": tuple(values),
                "key": (tag, tuple(values)),
                "transform": tidy(attr(attrs, "transform")),
                "classes": attr(attrs, "class").split(),
                "fill": attr(attrs, "fill"),
                "stroke": attr(attrs, "stroke"),
                "attrs": attrs,
                "raw": m.group(0),
            }
        )
    return out


# --------------------------------------------------------------------------
# Deviation 2 — a transform may be dropped only where dropping it is a no-op.

ROTATE = re.compile(r"^rotate\(\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s*\)$")


def centre(element):
    if element["tag"] == "circle":
        cx, cy, _ = element["values"]
        return cx, cy
    if element["tag"] == "ellipse":
        cx, cy, _, _ = element["values"]
        return cx, cy
    return None, None


def is_round(element):
    """A circle: no rotation about its own centre can move a point of it."""
    if element["tag"] == "circle":
        return True
    if element["tag"] == "ellipse":
        _, _, rx, ry = element["values"]
        return rx == ry
    return False


def flat_paint(element):
    """No url() anywhere. A paint server is resolved in the user space in force
    where it is referenced, which includes the element's own transform — so a
    transform is never redundant on an element that carries one."""
    for value in (element["fill"], element["stroke"]):
        if value.startswith("url("):
            return False
    return True


def droppable(shipped, source):
    """Why the source's transform may be absent here, or None if it may not."""
    m = ROTATE.match(source["transform"])
    if not m:
        return None
    _, cx, cy = m.groups()
    ecx, ecy = centre(source)
    if ecx is None or (rounded(cx), rounded(cy)) != (ecx, ecy):
        return None
    if not is_round(source):
        return None
    if not flat_paint(shipped):
        return None
    return "rotation about the centre of a flat-painted circle"


# --------------------------------------------------------------------------
# Deviation 3 — one source path of several subpaths, shipped as several traces.

COMMAND = re.compile(r"([MmLlHhVvZz])|(-?\d+(?:\.\d+)?)")


def points_of(d):
    """The points of a straight-line subpath, or None if it is not one.

    Traces are drawn with M, L, H and V only. Anything with a curve in it is
    returned as None and compared as a string instead, which is strictly safe:
    it can only refuse a match, never invent one.
    """
    tokens = [(m.group(1), m.group(2)) for m in COMMAND.finditer(d)]
    points, command, buf, x, y = [], None, [], 0.0, 0.0
    for letter, number in tokens:
        if letter:
            if letter in "Zz":
                return None
            command, buf = letter, []
            continue
        if command is None:
            return None
        buf.append(float(number))
        if command in "MmLl" and len(buf) == 2:
            dx, dy = buf
            x, y = (dx, dy) if command in "ML" else (x + dx, y + dy)
            points.append((round(x, 2), round(y, 2)))
            buf = []
            if command == "M":
                command = "L"
            elif command == "m":
                command = "l"
        elif command in "HhVv" and len(buf) == 1:
            d0 = buf[0]
            if command == "H":
                x = d0
            elif command == "h":
                x += d0
            elif command == "V":
                y = d0
            else:
                y += d0
            points.append((round(x, 2), round(y, 2)))
            buf = []
    return points or None


def subpaths(d):
    """Split on every moveto. A dash pattern restarts at each of these."""
    parts = re.split(r"(?=[Mm])", d.strip())
    return [p.strip() for p in parts if p.strip()]


def stroke_key(d):
    """A stroke, direction-insensitive. A stroke's direction is invisible at
    rest and is the whole of the draw, so a trace may be written backwards."""
    points = points_of(d)
    if points is None:
        return ("raw", tidy_path(d))
    return ("points", min(tuple(points), tuple(reversed(points))))


# --------------------------------------------------------------------------
# Deviation 4 — the one trued angle, checked rather than whitelisted.

SANCTIONED_RUN_OVER_RISE = 2.0  # 26.57 degrees, the brand's isometry


def trued_tangent(shipped, source):
    """The shipped line is the source line with its far end trued onto 26.57.

    Verified, not asserted: same origin, exactly 2:1, and a source that is not
    already 2:1 — so an endpoint moved for any other reason still fails.
    """
    if shipped["tag"] != "line" or source["tag"] != "line":
        return None
    sx1, sy1, sx2, sy2 = (float(v) for v in shipped["values"])
    ox1, oy1, ox2, oy2 = (float(v) for v in source["values"])
    if (round(sx1, 2), round(sy1, 2)) != (round(ox1, 2), round(oy1, 2)):
        return None
    if round(sx2, 2) != round(ox2, 2):
        return None  # only the rise may move
    run, rise = abs(sx2 - sx1), abs(sy2 - sy1)
    source_run, source_rise = abs(ox2 - ox1), abs(oy2 - oy1)
    if rise == 0 or source_rise == 0:
        return None
    if round(run / rise, 4) != SANCTIONED_RUN_OVER_RISE:
        return None
    if round(source_run / source_rise, 4) == SANCTIONED_RUN_OVER_RISE:
        return None  # nothing to true; the source was already on the angle
    return "trued from %.2f to %.2f degrees" % (
        math.degrees(math.atan2(source_rise, source_run)),
        math.degrees(math.atan2(rise, run)),
    )


# --------------------------------------------------------------------------


def load_sources():
    sources = {}
    for path in sorted(glob.glob(os.path.join(SOURCE_DIR, "0*.svg"))):
        card = os.path.basename(path)[:2]
        sources[card] = parse(open(path, encoding="utf-8").read(), drop_glyphs=True)
    return sources


def shipped_objects():
    for page in PAGES:
        text = open(page, encoding="utf-8").read()
        for body in SVG.findall(text):
            m = CARD_ID.search(body)
            if m:
                yield os.path.relpath(page, ROOT), m.group(1), body


def check_traces(shipped, source_elements, failures, notes, where):
    """The split, as a partition of the source path's subpaths."""
    traces = [e for e in shipped if "cf-iso__trace" in e["classes"]]
    if not traces:
        return set()
    want = {}
    for element in source_elements:
        if element["tag"] != "path":
            continue
        parts = subpaths(element["values"][0])
        if len(parts) > 1:
            want[element["key"]] = [stroke_key(p) for p in parts]
    if not want:
        return set()
    # Every multi-subpath source path this card has, against every trace that
    # did not already match the source outright.
    unmatched = [t for t in traces if t["key"] not in {e["key"] for e in source_elements}]
    got = sorted(stroke_key(t["values"][0]) for t in unmatched)
    for key, strokes in want.items():
        if sorted(strokes) == got:
            notes.append(
                "%s: %d traces are the %d subpaths of one source path"
                % (where, len(unmatched), len(strokes))
            )
            return {id(t) for t in unmatched}
    failures.append(
        "%s: the traces are not the source path's subpaths.\n"
        "    shipped %d stroke(s), source path has %d"
        % (where, len(got), len(next(iter(want.values()))))
    )
    return {id(t) for t in unmatched}


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    sources = load_sources()
    if not sources:
        print("no source vectors under %s" % SOURCE_DIR)
        return 1

    failures, notes, checked = [], [], 0
    for page, card, body in shipped_objects():
        where = "%s card %s" % (page, card)
        source_elements = sources.get(card)
        if source_elements is None:
            failures.append("%s: no source vector for card %s" % (where, card))
            continue
        shipped = parse(body, drop_glyphs=False)
        by_key = {}
        for element in source_elements:
            by_key.setdefault(element["key"], []).append(element)

        excused = check_traces(shipped, source_elements, failures, notes, where)

        for element in shipped:
            checked += 1
            if id(element) in excused:
                continue
            candidates = by_key.get(element["key"])
            if not candidates:
                failures.append(
                    "%s: element is in no source vector —\n    %s"
                    % (where, element["raw"].strip())
                )
                continue
            if any(c["transform"] == element["transform"] for c in candidates):
                if verbose:
                    notes.append("%s: %s matches the source" % (where, element["tag"]))
                continue
            if not element["transform"]:
                reasons = [droppable(element, c) for c in candidates]
                reason = next((r for r in reasons if r), None)
                if reason:
                    notes.append(
                        "%s: %s drops its source transform — %s"
                        % (where, element["tag"], reason)
                    )
                    continue
            failures.append(
                '%s: transform differs from the source. shipped "%s", source %s —\n    %s'
                % (
                    where,
                    element["transform"],
                    " / ".join('"%s"' % c["transform"] for c in candidates),
                    element["raw"].strip(),
                )
            )

        # Anything still unaccounted for may be the one trued angle.
        for failure in list(failures):
            if not failure.startswith("%s: element is in no source vector" % where):
                continue
            raw = failure.split("\n")[-1].strip()
            element = next((e for e in shipped if e["raw"].strip() == raw), None)
            if element is None:
                continue
            for candidate in source_elements:
                reason = trued_tangent(element, candidate)
                if reason:
                    failures.remove(failure)
                    notes.append("%s: %s %s" % (where, element["tag"], reason))
                    break

    if verbose:
        for note in notes:
            print("  %s" % note)
    elif notes:
        for note in notes:
            if "matches the source" not in note:
                print("  %s" % note)

    if failures:
        print("\nthe shipped objects have drifted from the designer's vectors:\n")
        for failure in failures:
            print("  %s" % failure)
        print(
            "\n%d element(s) drifted. The source vectors under\n"
            "design-system/assets/source/illustrations/ are the authority: move the\n"
            "implementation back, or add the deviation to this script with its reason."
            % len(failures)
        )
        return 1

    print(
        "%d elements across %d shipped objects, all of them the designer's"
        % (checked, len(list(shipped_objects())))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
