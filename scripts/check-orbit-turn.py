#!/usr/bin/env python3
"""An orbit turns by a share of its own ring, and one arc is not one share.

WHAT AN ORBIT IS. `.cf-iso__orbit` is a dashed ring that circulates as its
object assembles and then settles. It turns by travelling its dashes —
`stroke-dashoffset` from `--iso-orbit-travel` to 0 — rather than by taking a
rotation, because all of these rings are stroked with `userSpaceOnUse`
gradients and rotating an element rotates its paint server with it. That
argument is components.css's and foundations/motion.html's; this file is about
HOW FAR the dashes go.

WHAT WENT WRONG, AND WHY NOTHING REPORTED IT. `--iso-orbit-travel` is 60 px and
it was measured on card 04, whose three rings are the largest drawn anywhere:
1 520.53 units round the great circle, 1 171.37 round each of the two 2:1
orbits. One arc for every ring is a deliberate decision — it makes an object's
inner ring turn through more of itself than its outer one, which is what stops
concentric rings reading as a rigid body being spun — and it holds only while
the rings are of a size. They are not. The other six orbits, on Expertise and
its prototype, measure 103.04, 139.83 and 323.90 units, and 60 px of dash is
0.58, 0.43 and 0.19 of those rings. Four of the nine went round MORE THAN ONCE
while their object assembled.

The settled drawing was correct throughout, which is exactly why this needed a
script. Both ends of the animation sit on a whole number of dashes, so the ring
a reader actually reads is the phase the source vector draws whatever the
travel is; the defect lives entirely in the motion, and a lap and a tenth of a
turn end in the same picture.

THE TWO RULES.

  WHOLE DASHES  Every orbit's travel is a positive whole multiple of its own
                dash period — the sum of its `stroke-dasharray`, 1 + 4 = 5 for
                every ring in the tree today. This is what puts both ends of
                the turn, and the `both` fill held before the range opens, on
                the phase the drawing was exported in. A travel of 63 would
                leave the ring three fifths of a dash out for good, and a diff
                against assets/source/illustrations/ could never show it
                because the drift is in the rendered phase, not the markup.

  SHARE         No orbit travels more than SHARE_MAX of its own circumference.
                An orbit that would declares its own `--iso-orbit-travel`
                inline, the way a part of a built object declares its own
                `--build-dx`.

WHERE SHARE_MAX COMES FROM, AND WHY IT IS NOT A CONSTANT THIS FILE REMEMBERS.
The ceiling is card 04's own tightest share — 60 px of 1 171.37 units, one part
in 19.52 — so the bound is read off the drawing rather than chosen. Written
down and left there it would be a number nobody could check, and the failure it
guards against is precisely a small ring being left on the default: that ring
would take a larger share, and the ceiling derived from the defaulting rings
would silently rise to meet it. So the ceiling is recomputed on every run as
the largest share among the orbits that STILL RUN THE DEFAULT, and it is that
recomputation which is compared against the recorded 19.52. A small ring left
on the default therefore fails here rather than moving the bar.

The share is taken in the DRAWING's units, not the render's. What the eye
judges is the rendered ring, and the travel is in screen pixels while the ring
is in viewBox units, so the rendered share moves with the drawing's scale —
which is a thing no check without a browser can see. A share of the drawing is
the scale-free form of the same rule, and the two agree because these drawings
render between 0.29 and 0.63 of their viewBox: one part in 19.52 of the drawing
is 8.1 % to 17.7 % of a rendered turn, card 04's own measured band.

SCOPE. Every .html under design-system/, prototypes included — the same
boundary check-iso-motion.py draws, and for the same reason: a prototype is a
motion study, and a motion study that studies the wrong motion is worse than
none. Generated editions under patterns/en/ are built from the German pages and
are checked too when they exist, so a build that dropped an inline style would
be caught.
"""

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
TOKENS = DS / "assets" / "css" / "tokens.css"

# Card 04's tightest ring at the token's own speed: 60 px of 1 171.37 units.
# Recomputed below from the rings that still run the default and compared with
# this, rather than trusted. Written as the denominator because that is how the
# chapter and the stylesheets say it out loud: "one part in 19.52".
SHARE_MAX_DENOMINATOR = 19.52
# The rings are exported to two decimals and Ramanujan is exact to far more
# than that, so the derived denominator has to agree to about a hundredth.
DENOMINATOR_TOLERANCE = 0.01

ELEMENT = re.compile(r"<(circle|ellipse)\b([^>]*)>", re.I)
ATTR = re.compile(r"([:\w-]+)\s*=\s*\"([^\"]*)\"")
COMMENT = re.compile(r"<!--.*?-->", re.S)
DECLARED = re.compile(r"--iso-orbit-travel\s*:\s*([0-9.]+)px")


def ring_length(tag, attrs):
    """Circumference in the drawing's own units.

    A circle is 2 pi r. An ellipse has no closed form, so this is Ramanujan's
    second approximation, whose error on a 2:1 ellipse is under one part in ten
    million — four orders of magnitude tighter than the two decimals the source
    vectors are exported to. A `transform` on the element cannot change its
    length: every transform in the tree is a rotation about the ellipse's own
    centre, and the check below refuses anything else so that stays true.
    """
    if tag.lower() == "circle":
        return 2 * math.pi * float(attrs.get("r", 0))
    a = float(attrs.get("rx", 0))
    b = float(attrs.get("ry", 0))
    h = ((a - b) ** 2) / ((a + b) ** 2) if (a + b) else 0.0
    return math.pi * (a + b) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))


def token_default():
    text = TOKENS.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    m = re.search(r"--iso-orbit-travel\s*:\s*([0-9.]+)px", text)
    if not m:
        raise SystemExit("orbit turn: tokens.css declares no --iso-orbit-travel")
    return float(m.group(1))


def dash_period(value):
    """The sum of the dash pattern, which is the distance a dash repeats over."""
    numbers = [float(n) for n in re.findall(r"[0-9.]+", value)]
    if not numbers:
        return None
    # An odd-length pattern repeats doubled, and its period is doubled with it.
    if len(numbers) % 2:
        numbers = numbers * 2
    return sum(numbers)


def collect():
    """Every orbit in the tree, with its ring, its travel and where it came from."""
    orbits, problems = [], []
    for path in sorted(DS.rglob("*.html")):
        text = COMMENT.sub("", path.read_text(encoding="utf-8"))
        for m in ELEMENT.finditer(text):
            attrs = dict(ATTR.findall(m.group(2)))
            classes = attrs.get("class", "").split()
            if "cf-iso__orbit" not in classes:
                continue
            rel = path.relative_to(ROOT)
            line = text.count("\n", 0, m.start()) + 1
            where = "%s:%d" % (rel, line)

            transform = attrs.get("transform", "").strip()
            if transform and not transform.startswith("rotate("):
                problems.append(
                    "%s carries transform=%r. Only a rotation about the ring's own\n"
                    "    centre leaves its circumference alone, and this check measures\n"
                    "    circumference. A scale or a matrix here needs this script taught\n"
                    "    to read it before the ring can ship." % (where, transform)
                )
                continue

            dashes = attrs.get("stroke-dasharray", "")
            period = dash_period(dashes)
            if period is None:
                problems.append(
                    "%s has no stroke-dasharray. An orbit turns by moving its\n"
                    "    dashes; a solid ring has nothing to move and no phase to settle\n"
                    "    on." % where
                )
                continue

            declared = DECLARED.search(attrs.get("style", ""))
            orbits.append({
                "where": where,
                "length": ring_length(m.group(1), attrs),
                "period": period,
                "travel": float(declared.group(1)) if declared else None,
            })
    return orbits, problems


def main():
    default = token_default()
    orbits, problems = collect()

    if not orbits:
        raise SystemExit("orbit turn: no .cf-iso__orbit found — has the class been renamed?")

    # Nothing may redeclare the token in a stylesheet: this check models the
    # value as "the token, or an inline style", and a rule in a stylesheet would
    # be a third source it cannot see.
    for sheet in sorted((DS / "assets" / "css").glob("*.css")):
        if sheet.name == "tokens.css":
            continue
        body = re.sub(r"/\*.*?\*/", "", sheet.read_text(encoding="utf-8"), flags=re.S)
        if "--iso-orbit-travel:" in body:
            problems.append(
                "assets/css/%s declares --iso-orbit-travel. The travel is the token\n"
                "    or an inline style on the ring itself, because the ceiling is a share\n"
                "    of THAT ring and a selector does not know which ring it caught."
                % sheet.name
            )

    # THE CEILING, RE-DERIVED. The largest share among the rings still running
    # the default is what the recorded denominator has to be.
    defaulting = [o for o in orbits if o["travel"] is None]
    if not defaulting:
        problems.append(
            "every orbit declares its own travel, so the ceiling has nothing left to be\n"
            "    derived from. --iso-orbit-travel is meant to be the default that card 04's\n"
            "    rings run; if it no longer is, this check and the token both need rewriting."
        )
        derived = None
    else:
        tightest = min(defaulting, key=lambda o: o["length"])
        derived = tightest["length"] / default
        if abs(derived - SHARE_MAX_DENOMINATOR) > DENOMINATOR_TOLERANCE:
            problems.append(
                "the ceiling has moved. It is derived as the largest share any orbit takes\n"
                "    at the token's %g px — one part in %.2f, on the %.2f-unit ring at %s —\n"
                "    and this script records one part in %.2f. Either card 04's geometry\n"
                "    changed, or a ring too small for the default was left on it. A ring that\n"
                "    small must declare its own travel; it may not raise the bar it is judged\n"
                "    against."
                % (default, derived, tightest["length"], tightest["where"],
                   SHARE_MAX_DENOMINATOR)
            )

    share_max = 1.0 / SHARE_MAX_DENOMINATOR
    for o in orbits:
        travel = default if o["travel"] is None else o["travel"]
        if travel <= 0:
            problems.append("%s travels %g px. An orbit that does not turn is not an orbit."
                            % (o["where"], travel))
            continue
        periods = travel / o["period"]
        if abs(periods - round(periods)) > 1e-9:
            problems.append(
                "%s travels %g px on a %g px dash period — %.3f dashes, not a whole\n"
                "    number. It would settle that fraction of a dash off the phase the source\n"
                "    vector draws, for good, and nothing renders it wrong."
                % (o["where"], travel, o["period"], periods)
            )
        share = travel / o["length"]
        if share > share_max + 1e-9:
            allowed = int((o["length"] * share_max) // o["period"]) * o["period"]
            problems.append(
                "%s travels %g px round a %.2f-unit ring — one part in %.2f, past the\n"
                "    ceiling of one part in %.2f. %s Declare\n"
                "    style=\"--iso-orbit-travel:%gpx\" on it: %d whole dash%s, the most that\n"
                "    stays inside."
                % (o["where"], travel, o["length"], 1 / share, SHARE_MAX_DENOMINATOR,
                   "That is past a whole lap — the dashes go round and land back where they"
                   "\n    started." if share > 1 else "A turn that big reads as a spin, not a settle.",
                   allowed, int(allowed / o["period"]),
                   "" if allowed == o["period"] else "es")
            )

    if problems:
        print("orbit turn: %d finding(s)\n" % len(problems))
        for p in problems:
            print("  - %s\n" % p)
        return 1

    print("orbit turn: %d orbit(s), ceiling one part in %.2f (derived %.2f). "
          "Every travel a whole number of dashes and inside the ceiling."
          % (len(orbits), SHARE_MAX_DENOMINATOR, derived))
    return 0


if __name__ == "__main__":
    sys.exit(main())
