#!/usr/bin/env python3
"""The other half of the light family: the ANGLE every gradient is raked at.

scripts/check-gradient-family.py settles what a gradient is made of -- which
colours, in which order, with the arc waypoints and the oklab path. Nothing
settles which way it runs, and the brand states that law as squarely as it
states the ramp. foundations/geometry.html:

    Anything spatial is constructed in 2:1 isometry. The only sanctioned angles
    are 26.57, 45, 63.43 and 90 degrees.

A gradient is light crossing a surface, so it is spatial by the same definition
the drawings are, and the four angles close under mirroring into exactly eight
directions per half-turn. Every gradient in the system is on one of them today.
This is the thing that keeps them there.

WHY A GATE RATHER THAN A READING, and the answer is not "conventions drift"
this time. It is that A GRADIENT'S ANGLE IS NOT WRITTEN IN THE FILE THAT
DECLARES IT.

    <linearGradient id="cf-ex-01" x1="395.3" y1="357.52" x2="440.7" y2="322.08"
                    gradientUnits="userSpaceOnUse">
    ...
    <ellipse class="cf-iso__light" ... transform="rotate(127.98 418 339.8)"
             fill="url(#cf-ex-01)"/>

Read off its own coordinates that ramp runs at 52.02 deg, which is not a brand
angle and not near one. Painted, it runs at exactly 180 deg -- straight down --
because a userSpaceOnUse paint server resolves in the user space the REFERENCING
element's transform establishes, and that element is turned 127.98 deg. The
declaration and the paint are 128 degrees apart and both are correct.

That is not a hypothetical. scripts/expertise-objects/isolib.py records the same
mechanism shipping wrong, in the same place, in as many words:

    "A TRANSFORM IS NEVER A NO-OP ON A GRADIENT. [...] measured by rasterising
    the shipped ellipse and reading the pixels back, the lightest pixel of this
    object's light sat 68 % of the way DOWN the disc. The one rule the page
    states without qualification is that the light comes from above."

It was found by rasterising a page and reading pixels back, because there was
nothing else that could have found it. The fix was correct and nothing holds it:
change the disc's axis, add a wrapping <g transform>, re-anchor the span, and
the light silently lies down again. Every claim in this file is about the
RESOLVED angle -- the vector rotated by its referencing element's own transform
chain -- which is the only angle a reader ever sees.

THE TWO EXCEPTIONS ARE DERIVED, NOT LISTED. Process cards 01 and 03 paint at
118.74 and 49.96 deg, which are nobody's brand angles. They are the designer's:
01-discovery.svg and 03-weniger-ausfaelle.svg carry those vectors, and
assets/source/ is the authority this system implements against rather than
corrects. So this script reads the source vectors and accepts what it finds in
them, instead of carrying two hexes' worth of folklore. Move the source and the
exemption moves; delete the source and the exemption is gone.

WHAT IT CANNOT ANSWER, IT NAMES. Three classes are genuinely unreadable from a
file, and each is reported rather than passed over in silence -- a rule with a
quiet hole in it teaches people to stop reading it. All three fire today, on
three gradients:

  * A PAINT SERVER NAMED FROM A STYLESHEET. `.map__fill { fill: url(#map-ramp) }`
    means the element that paints with it, and therefore the transform its
    vector resolves in, is chosen by a selector in another file.
  * AN objectBoundingBox VECTOR THAT IS DIAGONAL. It renders at
    atan2(dx W, -dy H), and the box is a rendered quantity. An axis-aligned one
    is immune -- scaling a box never turns a horizontal or a vertical -- which
    is why the frame's six ramps and the four field lights all resolve.
  * A CUSTOM PROPERTY THAT IS NOT A BARE ANGLE. --foil-angle is the swing:
    calc(90deg + 26.57deg x --sight-v x --sight-h), whose value is decided by
    two @property numbers a scroll timeline drives. Both ends of it are brand
    angles -- 90 at rest either side and 116.57 at mid-travel -- but that is a
    fact about a keyframe block, not about a declaration, so it is stated in
    foundations/colors.html and named here rather than claimed.

    python3 scripts/check-gradient-angle.py       # check, exit 1 on drift
    python3 scripts/check-gradient-angle.py -v    # print every resolved angle

stdlib only, no build step. Same python3 that serves the pages.
"""

import argparse
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
SOURCE = DS / "assets" / "source" / "illustrations"

# The same boundary check-gradient-family.py draws, for the same two reasons:
# assets/source/ is the authority rather than the subject, and prototypes/ is
# unshipped working material carrying raw Figma exports.
EXCLUDE = ("/assets/source/", "/prototypes/")

# The shipping stylesheets, verbatim from check-gradient-family.py's CSS tuple.
CSS = ("tokens.css", "base.css", "components.css", "acts.css")

# THE SANCTIONED SET, in CSS's own convention: 0 deg is up, clockwise. The
# manual names four angles; a gradient has a direction, so each of them is a
# direction in all four quadrants and the set closes at sixteen.
#
#   26.57 = atan(1/2)   the shallow isometric rake
#   45                  the neutral diagonal
#   63.43 = atan(2)     the steep isometric rake
#   90                  square
#
# Written as the generator rather than as a list of sixteen numbers, so it is
# the manual's four angles that are stated here and not a table derived from
# them by hand.
BRAND_QUADRANT = (0.0, 26.565051, 45.0, 63.434949)
BRAND = sorted({(q + 90.0 * k) % 360.0
                for q in BRAND_QUADRANT for k in range(4)})

# Half a hundredth of a degree past what three decimals of a coordinate can
# cost. The tightest pair in the set is 18.43 deg apart, so this cannot make
# two brand angles ambiguous.
TOL = 0.02

# --- geometry ---------------------------------------------------------------


def css_angle(dx, dy):
    """The CSS angle of a screen vector. SVG's y runs down, CSS's 0 deg is up
    and turns clockwise, so a vector (0, +1) -- straight down the screen -- is
    180 deg, and (+1, 0) is 90 deg."""
    return math.degrees(math.atan2(dx, -dy)) % 360.0


def is_brand(angle):
    return any(min((angle - b) % 360.0, (b - angle) % 360.0) <= TOL for b in BRAND)


def nearest_brand(angle):
    return min(BRAND, key=lambda b: min((angle - b) % 360.0, (b - angle) % 360.0))


# --- a very small SVG reader ------------------------------------------------
#
# Not an XML parser and not trying to be. It walks the tags inside each <svg>
# subtree keeping a stack, which is enough because SVG content is well-formed
# by construction: every element in these files either closes or self-closes.
# Scanning only inside <svg> is what keeps HTML's optional end tags out of it.

TAG = re.compile(r"<(/?)([A-Za-z][\w:-]*)((?:\"[^\"]*\"|'[^']*'|[^>\"'])*?)(/?)>")
ATTR = re.compile(r"([\w:-]+)\s*=\s*\"([^\"]*)\"")
NUM = r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"
ROTATE = re.compile(r"rotate\s*\(\s*(%s)" % NUM)
URLREF = re.compile(r"url\(#([\w:.-]+)\)")
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)


def svg_spans(text):
    """(start, end) of every top-level <svg> ... </svg> in a document."""
    out, depth, start = [], 0, None
    for m in TAG.finditer(text):
        closing, name, _, selfclose = m.groups()
        if name.lower() != "svg":
            continue
        if not closing:
            if depth == 0:
                start = m.start()
            if not selfclose:
                depth += 1
        else:
            depth -= 1
            if depth == 0 and start is not None:
                out.append((start, m.end()))
                start = None
    return out


UNSUPPORTED = re.compile(r"\b(matrix|skewX|skewY|rotate3d)\s*\(")
SCALE = re.compile(r"\bscale\s*\(\s*(%s)\s*[, ]\s*(%s)\s*\)" % (NUM, NUM))


def _turns(transform):
    """(rotation in degrees, names of terms this reader will not resolve).

    translate() moves a gradient's origin and never its direction, so it is
    correctly ignored. A UNIFORM scale is ignored for the same reason —
    including scale(-1,-1), a half-turn about the origin that leaves a
    gradient line's direction where it was — and a NON-UNIFORM one is not: it
    turns every direction that is not already an axis, which is the same fact
    that makes an objectBoundingBox diagonal unreadable. The icon sprite's
    scale(-1,1) is a non-uniform scale by that definition and is correctly
    named, though it holds no gradient."""
    hard = [m.group(1) for m in UNSUPPORTED.finditer(transform)]
    for m in SCALE.finditer(transform):
        if abs(abs(float(m.group(1))) - abs(float(m.group(2)))) > 1e-9 \
                or float(m.group(1)) * float(m.group(2)) < 0:
            hard.append("scale")
    return sum(float(a) for a in ROTATE.findall(transform)), hard


def walk(text, span):
    """Yield (attrs, rotation, unresolved, line) for every element in one <svg>
    subtree, with rotation and unresolved terms accumulated from every ancestor
    — because a paint server resolves in the user space the whole chain
    establishes, not the one its own transform does."""
    lo, hi = span
    stack = []
    for m in TAG.finditer(text, lo, hi):
        closing, name, raw, selfclose = m.groups()
        if closing:
            if stack:
                stack.pop()
            continue
        attrs = dict(ATTR.findall(raw))
        turn, hard = _turns(attrs.get("transform", ""))
        up_turn, up_hard = stack[-1] if stack else (0.0, ())
        total = (up_turn + turn, tuple(up_hard) + tuple(hard))
        yield attrs, total[0], total[1], text[:m.start()].count("\n") + 1
        if not selfclose:
            stack.append(total)


# walk() drops the tag name, because the only thing that needs it is the
# gradient lookup below and re-scanning for one tag is a regex over a string
# already in memory. A gradient that declares no coordinates inherits them
# through href; one that inherits nothing takes SVG's own default, (0,0) to
# (100%,0) -- left to right, which is 90 deg in CSS's convention.
GRAD_TAG = re.compile(r"<linearGradient((?:\"[^\"]*\"|'[^']*'|[^>\"'])*?)/?>")


def linear_gradients(text, span):
    """id -> (attrs, line) for every <linearGradient> in one subtree."""
    lo, hi = span
    out = {}
    for m in GRAD_TAG.finditer(text, lo, hi):
        attrs = dict(ATTR.findall(m.group(1)))
        if "id" in attrs:
            out[attrs["id"]] = (attrs, text[:m.start()].count("\n") + 1)
    return out


def resolve_vector(gid, defs, seen=()):
    """(dx, dy, units) for a gradient, following href for coordinates it does
    not declare itself. Returns None on a reference that goes nowhere."""
    if gid in seen or gid not in defs:
        return None
    attrs = defs[gid][0]
    units = attrs.get("gradientUnits", "objectBoundingBox")
    if {"x1", "y1", "x2", "y2"} & set(attrs):
        try:
            x1 = _len(attrs.get("x1", "0%"))
            y1 = _len(attrs.get("y1", "0%"))
            x2 = _len(attrs.get("x2", "100%"))
            y2 = _len(attrs.get("y2", "0%"))
        except ValueError:
            return None
        return x2 - x1, y2 - y1, units
    href = attrs.get("href") or attrs.get("xlink:href", "")
    if href.startswith("#"):
        inherited = resolve_vector(href[1:], defs, seen + (gid,))
        if inherited:
            # Units are the referring gradient's own; only the geometry is
            # inherited, and only when it declares none of its own.
            return inherited[0], inherited[1], units
        return None
    return 1.0, 0.0, units          # SVG's default: left to right


def _len(v):
    v = v.strip()
    return float(v[:-1]) / 100.0 if v.endswith("%") else float(v)


# --- the designer's own angles ----------------------------------------------


def source_angles():
    """Every angle painted by a gradient in assets/source/illustrations/.

    Derived rather than listed, so the exemption is the material and not a
    memory of it. The source vectors carry no transforms on their lit elements;
    if one ever does, it turns up here as a different number and the drawing
    that copies it has to move with it."""
    out = {}
    for f in sorted(SOURCE.glob("*.svg")):
        text = f.read_text(encoding="utf-8")
        for span in svg_spans(text):
            defs = linear_gradients(text, span)
            turns = {}
            for attrs, turn, _hard, _line in walk(text, span):
                for ref in URLREF.findall(attrs.get("fill", "")
                                          + " " + attrs.get("stroke", "")):
                    turns.setdefault(ref, turn)
            for gid in defs:
                vec = resolve_vector(gid, defs)
                if not vec or vec[2] != "userSpaceOnUse":
                    continue
                ang = (css_angle(vec[0], vec[1]) + turns.get(gid, 0.0)) % 360.0
                out.setdefault(round(ang, 4), []).append("%s#%s" % (f.name, gid))
    return out


# --- the CSS half -----------------------------------------------------------

# PARENTHESES ARE BALANCED BY HAND AND NOT BY A REGEX, and the reason is a bug
# this had before it did. `linear-gradient(var(--foil-rake), var(--foil-stops))`
# stops a non-greedy [^;]*? at the FIRST close paren — the one belonging to
# var(--foil-rake — so the first argument came back as an unclosed var(), fell
# through to the "no angle stated" branch, and every ramp raked by a token
# resolved to CSS's default 180 deg. Four of the eight gradients in tokens.css
# read that way, --gradient-foil and --gradient-foil-ink among them: the check
# passed them, and it would have gone on passing them at any angle at all.
GRAD_OPEN = re.compile(r"\b(repeating-)?(linear|radial|conic)-gradient\s*\(")


def gradient_calls(text):
    """(prefix, kind, first argument, line) for every gradient function call,
    with the argument taken at paren depth zero."""
    for m in GRAD_OPEN.finditer(text):
        depth, i, head_end = 1, m.end(), None
        while i < len(text) and depth:
            c = text[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == "," and depth == 1 and head_end is None:
                head_end = i
            i += 1
        if depth:
            continue                       # unterminated; nothing to claim
        close = i - 1
        yield (m.group(1) or "", m.group(2),
               text[m.end():head_end if head_end is not None else close],
               text[:m.start()].count("\n") + 1)
ANGLE = re.compile(r"^\s*(%s)deg\b" % NUM)
VAR = re.compile(r"^\s*var\(\s*(--[\w-]+)\s*\)")
KEYWORD = {"to top": 0.0, "to right": 90.0, "to bottom": 180.0, "to left": 270.0,
           "to top right": None, "to bottom right": None,
           "to bottom left": None, "to top left": None}
# NOT ANCHORED TO THE START OF A LINE, and the two declarations that taught it
# so are both modifiers written inline: `.material-rake--mirror { --rake-angle:
# calc(...) }` and `.material-rake--grazing { --rake-angle: 239.25deg }`. A
# line-anchored pattern saw neither, so --rake-angle resolved to the one value
# it holds at rest and the two angles the modifiers exist to supply — a
# half-turn and the designer's second measured rake — went unchecked.
DECL = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+)[;}]")


CALC_SUM = re.compile(
    r"^calc\(\s*(var\(\s*--[\w-]+\s*\)|%s\s*deg)\s*([-+])\s*"
    r"(var\(\s*--[\w-]+\s*\)|%s\s*deg)\s*\)$" % (NUM, NUM))


def angle_tokens(texts):
    """Every angle a custom property is ever declared as.

    EVERY declaration and not the first, because a modifier that swaps the rake
    is exactly the thing worth checking: .material-rake--mirror turns the ramp
    by a half-turn and .material-rake--grazing writes the designer's second
    measured angle, and both reach the same gradient through the same var().
    Taking the first value would make this a check on the rest state of a
    family whose whole point is that the angle moves.

    Resolved: a bare angle, a var() naming one, and calc(A +/- B) where both
    terms are one of those. Anything else is returned as a name with no value,
    and main() names it rather than guessing."""
    values, pending = {}, []
    for t in texts:
        for name, value in DECL.findall(CSS_COMMENT.sub(" ", t)):
            pending.append((name, value.strip()))

    def resolve(v, depth=0):
        if depth > 4:
            return None
        m = ANGLE.match(v)
        if m and v.rstrip().endswith("deg"):
            return float(m.group(1)) % 360.0
        m = VAR.match(v)
        if m and v == m.group(0).strip():
            got = values.get(m.group(1))
            return next(iter(got)) if got and len(got) == 1 else None
        m = CALC_SUM.match(v.replace("\n", " "))
        if m:
            a, op = resolve(m.group(1), depth + 1), m.group(2)
            b = resolve(m.group(3), depth + 1)
            if a is not None and b is not None:
                return (a + b) % 360.0 if op == "+" else (a - b) % 360.0
        return None

    # Two passes: the second resolves aliases whose target was declared later
    # in the file than they were, which is how --field-rake reads --angle-b.
    for _ in range(2):
        for name, v in pending:
            got = resolve(v)
            if got is not None:
                values.setdefault(name, set()).add(round(got, 4))
    unresolved = {}
    for name, v in pending:
        if resolve(v) is None:
            unresolved.setdefault(name, []).append(v)
    return values, unresolved


def css_angle_of(head, tokens):
    """(every angle a gradient's first argument can state, how it states it).

    An empty first argument is 180 deg — CSS's own default, and the page wash's
    actual rake. A var() is every angle that property is ever declared as, so a
    ramp reached by three modifiers is checked three times."""
    head = head.strip()
    if not head:
        return {180.0}, "default"
    m = ANGLE.match(head)
    if m:
        return {float(m.group(1)) % 360.0}, "literal"
    m = VAR.match(head)
    if m:
        return tokens.get(m.group(1)) or None, m.group(1)
    for kw, val in KEYWORD.items():
        if head.startswith(kw):
            return ({val} if val is not None else None), kw
    return {180.0}, "default"


def css_gradients(text, tokens):
    """(function, angle, how, line) for every gradient in a stylesheet.

    A radial or conic gradient's first argument is a shape, a size or a
    position rather than a rake, so only the linear ones carry an angle to
    check -- which is the same division tokens.css makes when it gives the
    blooms a shape and the rakes an angle."""
    for rep, kind, head, line in gradient_calls(text):
        if kind != "linear":
            yield rep + kind + "-gradient", None, "not an angle", line
            continue
        head = re.sub(r"\bin\s+(oklab|oklch|srgb|hsl|lab|lch)\b.*$", "", head)
        angles, how = css_angle_of(head, tokens)
        yield rep + kind + "-gradient", angles, how, line


# --- main -------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every gradient and the angle it resolves to")
    args = ap.parse_args()

    allowed_source = source_angles()
    failures, notes = [], []
    svg_seen = 0

    # A PAINT SERVER CAN BE NAMED FROM A STYLESHEET, and the one that is, is the
    # one whose angle is least visible from anywhere. acts.css says
    # `.map__fill { fill: url(#map-ramp) }`, so the element that paints with it
    # — and therefore the transform its vector resolves in — is decided by a
    # selector, in another file, against markup this reader would have to match
    # by hand. Collected here so that reference is named below rather than read
    # as an unused def.
    css_text = {name: (DS / "assets" / "css" / name).read_text(encoding="utf-8")
                for name in CSS}
    # Comments are stripped first, and blanked rather than removed so every
    # line number below still counts. acts.css names three paint servers inside
    # one comment explaining what forced colours does to them; read as
    # declarations they would each raise a note about a gradient nothing paints
    # that way.
    css_painted = {}
    for name, t in css_text.items():
        t = CSS_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), t)
        for m in URLREF.finditer(t):
            css_painted.setdefault(m.group(1), "assets/css/%s:%d"
                                   % (name, t[:m.start()].count("\n") + 1))

    files = [f for f in sorted(DS.rglob("*.html"))
             if not any(x in "/" + str(f.relative_to(DS)) for x in EXCLUDE)]

    for f in files:
        rel = str(f.relative_to(DS))
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "<linearGradient" not in text:
            continue
        # DEFS AND PAINTERS ARE COLLECTED PER DOCUMENT, NOT PER <svg>, because a
        # url(#id) reference is document-scoped and this system uses that: the
        # landing page declares the frame's six ramps in one hidden sprite at
        # line 1306 and paints with them in a different <svg> four hundred lines
        # later. Scoped per subtree, every one of those reads as a def nobody
        # uses and a painter pointing at nothing. The transform stack stays per
        # subtree, which is correct — an svg root starts a new user space.
        defs, painters = {}, {}
        for span in svg_spans(text):
            defs.update(linear_gradients(text, span))
            for attrs, turn, hard, line in walk(text, span):
                paint = " ".join((attrs.get("fill", ""), attrs.get("stroke", ""),
                                  attrs.get("style", "")))
                for ref in URLREF.findall(paint):
                    painters.setdefault(ref, []).append((turn, hard, line))
        for gid, (_attrs, gline) in sorted(defs.items()):
            if gid not in painters:
                if gid in css_painted:
                    notes.append(
                        "%s:%d  %s is painted by a rule (%s), so which element "
                        "carries it — and therefore the transform its vector "
                        "resolves in — is decided by a selector. No claim is "
                        "made about its angle."
                        % (rel, gline, gid, css_painted[gid]))
                continue        # otherwise a stop-only template; heirs carry the rake
            vec = resolve_vector(gid, defs)
            if vec is None:
                failures.append("%s:%d  %s: no readable geometry, and nothing "
                                "it inherits from has any" % (rel, gline, gid))
                continue
            dx, dy, units = vec
            if units != "userSpaceOnUse" and dx != 0 and dy != 0:
                notes.append(
                    "%s:%d  %s: an objectBoundingBox vector of (%g, %g) renders "
                    "at atan2(dx W, -dy H) — the referencing element's box, which "
                    "is a rendered quantity. No claim is made about its angle."
                    % (rel, gline, gid, dx, dy))
                continue
            for turn, hard, pline in painters[gid]:
                if hard:
                    notes.append(
                        "%s:%d  %s is painted through a %s() transform, which turns "
                        "a direction by an amount this reader does not resolve. No "
                        "claim is made about its angle."
                        % (rel, pline, gid, hard[0]))
                    continue
                svg_seen += 1
                ang = (css_angle(dx, dy) + turn) % 360.0
                ok = is_brand(ang) or any(
                    abs((ang - s + 180) % 360 - 180) <= TOL for s in allowed_source)
                if args.verbose:
                    why = ""
                    if not is_brand(ang):
                        for s, names in allowed_source.items():
                            if abs((ang - s + 180) % 360 - 180) <= TOL:
                                why = "  = " + names[0]
                    print("%s %-40s svg %-16s %8.2f%s%s" % (
                        "ok  " if ok else "FAIL", rel, gid, ang,
                        "  (turned %g)" % turn if turn else "", why))
                if not ok:
                    failures.append(
                        "%s:%d  %s paints at %.2f deg — not a brand angle "
                        "(nearest is %.2f) and not one the designer's source "
                        "vectors carry.%s"
                        % (rel, pline, gid, ang, nearest_brand(ang),
                           "  Its own coordinates read %.2f; the element painting "
                           "with it is turned %g deg." % (css_angle(dx, dy), turn)
                           if turn else ""))

    # --- the CSS half
    css = [(name, (DS / "assets" / "css" / name).read_text(encoding="utf-8"))
           for name in CSS]
    tokens, unreadable = angle_tokens([t for _, t in css])
    css_seen = 0
    for name, text in css:
        for fn, angles, how, line in css_gradients(text, tokens):
            if angles is None and how == "not an angle":
                continue
            css_seen += 1
            if angles is None:
                notes.append(
                    "assets/css/%s:%d  %s is raked by %s, which these four files "
                    "never declare as a bare angle. No claim is made about it."
                    % (name, line, fn, how))
                continue
            for angle in sorted(angles):
                ok = is_brand(angle) or angle in DESIGNER_CSS
                if args.verbose:
                    print("%s %-40s css %-16s %8.2f  (%s)" % (
                        "ok  " if ok else "FAIL", "assets/css/" + name, fn, angle, how))
                if not ok:
                    failures.append(
                        "assets/css/%s:%d  %s is raked at %.2f deg — not a brand "
                        "angle (nearest is %.2f) and not one of the designer's two "
                        "measured rakes." % (name, line, fn, angle, nearest_brand(angle)))
            # A property that is a readable angle in one declaration and
            # something else in another is the case worth naming: the readable
            # half passes above and the other half is a rake nothing has looked
            # at. --foil-angle is exactly that, and its other half is the swing.
            for decl in unreadable.get(how, []):
                notes.append("assets/css/%s:%d  %s also takes %s: `%s`, which is not "
                             "a bare angle. No claim is made about that value."
                             % (name, line, fn, how, " ".join(decl.split())))

    if failures:
        print("\nThe light family is raked off-axis in %d place%s:\n"
              % (len(failures), "" if len(failures) == 1 else "s"), file=sys.stderr)
        for x in failures:
            print("  " + x, file=sys.stderr)
        print("\nSee foundations/colors.html#the-rake-register and "
              "foundations/geometry.html.", file=sys.stderr)
        return 1

    print("%d painted SVG gradients and %d CSS gradients, %d sanctioned directions."
          % (svg_seen, css_seen, len(BRAND)))
    # Named rather than passed over in silence, the way check-gradient-family.py
    # names a stop it cannot resolve: a rule with a quiet hole in it teaches
    # people to stop reading it.
    for n in notes:
        print("  " + n)
    return 0


# The designer's own two rakes, in CSS. They are literals here and not derived
# the way the SVG exemptions are, because their authority is the Figma dump --
# assets/source/illustrations/figma-process-card-spec.css.txt, which is a text
# file of declarations rather than a drawing this can resolve a vector out of.
# tokens.css states both and says of the first: "132.36 deg is 2.6 deg off the
# sanctioned 135 -- the material wins, but see foundations/geometry.html before
# deriving new angles from it."
DESIGNER_CSS = {132.36, 239.25}

if __name__ == "__main__":
    sys.exit(main())
