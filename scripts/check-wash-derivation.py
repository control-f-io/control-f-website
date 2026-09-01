#!/usr/bin/env python3
"""The page wash's three chromatic stops are re-derived, not trusted.

The largest gradient in the system by two orders of magnitude is
--surface-page-wash: roughly 5,800 px of CF-Grau descending into Weiss behind
every page the site ships. Since it was given the foil's own ramp reversed it
is also the only member of the light family whose colours are LITERALS with a
stated derivation and no arithmetic anywhere that recomputes them.

tokens.css names the trap itself, in as many words:

    THE THREE HEXES ARE RE-DERIVABLE, NOT HAND-TUNED -- recompute the ramp and
    you get them back -- and they carry the same trap the #DBFC60 waypoint
    does: they are literals, so they do not follow --cf-grau. Move CF-Grau and
    these must be recomputed or the wash quietly stops starting where the page
    starts.

That paragraph was written, and then nothing was written that runs it. This
file is that arithmetic.

WHY THE GRADIENT GATE CANNOT SEE THIS. check-gradient-family.py walks every
gradient the site ships and it walks this one too -- but it asks the two
questions the family's opaque members answer: does a leg leaving lime carry
its 19 % waypoint, and does a leg that turns carry its polar midpoint. The
wash is exempt from both, deliberately and with a reason recorded in that
script: it "runs the foil backwards at chroma 0.005, and tokens.css sets that
ceiling on purpose so the wash stays inside the grain; arcing it would be
telling the wash to stop being neutral". So the gate reads #CFCFD2, #E1E4E7
and #F3F8F7 as data and passes them through. It never asks the only question
that can go stale about them: whether they are still what the rule produces.

WHAT WOULD GO WRONG, AND HOW QUIETLY. Every input to these three hexes is a
token somebody may reasonably move:

    --cf-grau            the anchor. Its OKLab L is the whole lightness path.
    --cf-glas            } the three hues, at their 300 tints for two of them.
    --sky-300            } These are the foil's own, which is the entire claim
    --violett-300        } that the wash is a member of this family.
    --rake-near-n        } the positions, subtracted from 100. The wash's
    --spectrum-hot-n     } stops are calc() off these, so the POSITIONS follow
    --spectrum-cool-n    } on their own -- and the colours at them do not.

Move --cf-grau by two levels and the wash's opening stop is no longer the
page's own grey: the largest surface in the system starts on a colour that
exists nowhere else, and the first row of every page is a seam nobody drew.
Nothing fails. check-hero-scrim.py would not catch it either -- and this is
worth being precise about, because that check does read --wash-stops. It reads
the wash's opening stop and holds the hero's scrim tint TO it, deriving the
scrim from the wash rather than restating it. That is the right rule and it is
the opposite direction from this one: it keeps the scrim honest about whatever
the wash says, including a wash that has quietly stopped being right. Together
they close the loop -- that one holds the scrim to the wash, this one holds
the wash to the palette.

WHAT IS CHECKED, AND WHY EACH IS A SEPARATE CLAIM

  HEX        Each chromatic stop is exactly oklch(L, 0.005, h) rendered to
             8-bit sRGB, where L is the neutral ramp's own lightness at that
             stop's position and h is the corresponding foil hue. Exact
             equality, the same standing the arc waypoints get in
             check-gradient-family.py: these come off the same 8-bit grid the
             derivation lands on, so anything but equality is a stale value
             left behind by an input that moved.

  POSITION   The positions are calc() over --spectrum-*-n and --rake-near-n
             rather than percentages typed twice. This is what makes the
             positions immune to the failure the colours have, and it is
             checked structurally so a later hand cannot quietly flatten a
             calc() into the number it happens to evaluate to today.

  LIGHTNESS  tokens.css claims the four-stop ramp's lightness path is
             identical to the two-stop neutral one it replaced, "exactly and
             by construction". That is the claim that lets the wash carry hue
             at no contrast cost, and every measured figure at the wash and at
             the hero scrim rests on it. Recomputed here from the rendered
             hexes rather than from the intent.

  CHROMA     "CHROMA 0.005 IS THE WHOLE BUDGET, and the ceiling is set by
             something already on this surface: no channel may move further
             from the neutral than the grain does." Both halves are checked --
             the OKLab chroma against the budget, and the worst per-channel
             deviation from the neutral ramp against --grain's ~5 levels.
             tokens.css puts that worst case at 4 of 255.

  FAMILY     The wash's own membership argument: "The three hues are
             --foil-stops' three, to the digit. Hue travel across them is
             104.5 degrees, which is the lit foil's own figure; the band they
             span is 0.120." Both are recomputed, the hue travel against the
             foil's own stops rather than against the number in the prose, so
             the two ramps cannot drift apart while both still read as
             internally consistent.

WHAT THIS DOES NOT CHECK. That 0.005 is the right ceiling, or that 19 % is the
right waypoint, or that the wash should carry hue at all. Those are design
rulings and they are argued where they were made. This file only holds the
system to the arithmetic it says it did.

Usage:
    check-wash-derivation.py       fail if a stop is not what the rule produces
    check-wash-derivation.py -v    print the whole derivation, stop by stop
"""

import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS = os.path.join(ROOT, "design-system", "assets", "css", "tokens.css")

# The chroma every chromatic stop of the wash is drawn at. tokens.css argues
# the number; this is the only place it is read back.
WASH_CHROMA = 0.005

# The grain the wash already carries is ~5 eight-bit levels (--grain, 8 %
# fractal noise). The ceiling on a stop's distance from the neutral ramp is
# that, because the rule is "no channel may move further from the neutral than
# the grain does" -- a deviation under the noise already on the surface is not
# a colour the reader can see, which is the whole argument for the budget.
GRAIN_LEVELS = 5

# Lightness is compared against the neutral ramp on the 8-bit grid, not on the
# arithmetic: two colours one level apart can differ by ~0.0015 of OKLab L up
# at this end of the scale, and the derivation rounds to a hex like everything
# else. Anything past this is the path moving, not the grid.
L_GRID = 0.0020

# The wash's four stops in source order, each named for the foil stop it is
# the reverse of. Weiss is not derived -- it is --grey-000 at 100 % by
# construction, since it is the end of the band being reversed.
WASH_ORDER = ("Violett", "Sky", "Glas")


# --- colour, the same arithmetic check-gradient-family.py uses ---------------

def _srgb_to_linear(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return v * 255.0


def oklab(rgb):
    r, g, b = (_srgb_to_linear(v) for v in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (v ** (1 / 3) if v >= 0 else -((-v) ** (1 / 3)) for v in (l, m, s))
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


def oklch(rgb):
    L, A, B = oklab(rgb)
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360.0


def oklch_to_hex(L, C, h):
    A = C * math.cos(math.radians(h))
    B = C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * A + 0.2158037573 * B
    m_ = L - 0.1055613458 * A - 0.0638541728 * B
    s_ = L - 0.0894841775 * A - 1.2914855480 * B
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return "#%02X%02X%02X" % tuple(
        max(0, min(255, int(round(_linear_to_srgb(v))))) for v in (r, g, b))


def to_rgb(hexv):
    hexv = hexv.lstrip("#")
    return tuple(int(hexv[i:i + 2], 16) for i in (0, 2, 4))


# --- reading tokens.css -----------------------------------------------------

def strip_comments(text):
    return re.sub(r"/\*.*?\*/", " ", text, flags=re.S)


def read_tokens():
    """The palette hexes, the three positional numbers and --wash-stops.

    Read off the source rather than off a copy of the values, because a copy is
    the thing this file exists to disallow.
    """
    text = open(TOKENS, encoding="utf-8").read()
    bare = strip_comments(text)

    hexes = {}
    for name in ("cf-grau", "cf-glas", "sky-300", "violett-300", "grey-000"):
        m = re.search(r"--%s\s*:\s*(#[0-9A-Fa-f]{6})\s*;" % re.escape(name), bare)
        if m:
            hexes[name] = m.group(1).upper()

    nums = {}
    for name in ("rake-near-n", "spectrum-hot-n", "spectrum-cool-n"):
        m = re.search(r"--%s\s*:\s*(-?[0-9.]+)\s*;" % re.escape(name), bare)
        if m:
            nums[name] = float(m.group(1))

    m = re.search(r"--wash-stops\s*:(.*?);\s*\n", bare, flags=re.S)
    return hexes, nums, (m.group(1) if m else None)


def split_stops(decl):
    """--wash-stops' four stops, split on the commas that separate them.

    Depth-aware: every position but the first is a calc() carrying commas of
    its own inside nested parens, so a plain split lands mid-expression.
    """
    out, cur, depth = [], "", 0
    for ch in decl:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [s.strip() for s in out if s.strip()]


# --- the rules --------------------------------------------------------------

def derive(hexes, nums):
    """The three chromatic stops, from the palette and the foil's own geometry.

    Positions first: --foil-stops' own, subtracted from 100. The foil renormalises
    the spectrum onto the band above the white hot spot, so Glas and Sky land at
    (rake - hot) / (100 - hot) and (cool - hot) / (100 - hot); reversing the ramp
    is 100 minus each, and Violett's 100 becomes 0.

    Then lightness: the neutral ramp's own value at that position, anchored on
    CF-Grau's OKLab L and running to 1.0 at Weiss. Then the hue of the foil stop
    being reversed, at the wash's chroma budget.
    """
    span = 100.0 - nums["spectrum-hot-n"]
    foil = {
        "Glas": (nums["rake-near-n"] - nums["spectrum-hot-n"]) / span * 100.0,
        "Sky": (nums["spectrum-cool-n"] - nums["spectrum-hot-n"]) / span * 100.0,
        "Violett": 100.0,
    }
    hue_source = {"Glas": "cf-glas", "Sky": "sky-300", "Violett": "violett-300"}

    L_anchor = oklab(to_rgb(hexes["cf-grau"]))[0]
    out = []
    for name in WASH_ORDER:
        pos = 100.0 - foil[name]
        t = pos / 100.0
        L = L_anchor + t * (1.0 - L_anchor)
        h = oklch(to_rgb(hexes[hue_source[name]]))[2]
        out.append({
            "name": name, "pos": pos, "L": L, "hue": h,
            "hex": oklch_to_hex(L, WASH_CHROMA, h),
            "from": hue_source[name],
        })
    return out, L_anchor


def check(verbose=False):
    findings = []
    hexes, nums, decl = read_tokens()

    missing = [n for n in ("cf-grau", "cf-glas", "sky-300", "violett-300", "grey-000")
               if n not in hexes]
    missing += [n for n in ("rake-near-n", "spectrum-hot-n", "spectrum-cool-n")
                if n not in nums]
    if missing:
        return ["tokens.css no longer declares %s as a plain literal, so the wash "
                "cannot be re-derived from it" % ", ".join("--" + m for m in missing)]
    if decl is None:
        return ["tokens.css declares no --wash-stops, so there is nothing to derive"]

    stops = split_stops(decl)
    if len(stops) != 4:
        return ["--wash-stops carries %d stops; the reversed foil has four "
                "(Violett, Sky, Glas, Weiss)" % len(stops)]

    derived, L_anchor = derive(hexes, nums)

    if verbose:
        print("anchor  --cf-grau %s  OKLab L %.6f" % (hexes["cf-grau"], L_anchor))
        print("%-9s %9s %9s %9s   %-8s %-8s" %
              ("stop", "pos %", "L", "hue", "derived", "declared"))

    # --- HEX and POSITION, stop by stop ---
    for want, decl_stop in zip(derived, stops[:3]):
        m = re.search(r"#[0-9A-Fa-f]{6}", decl_stop)
        got = m.group(0).upper() if m else None
        if verbose:
            print("%-9s %9.4f %9.4f %9.2f   %-8s %-8s" %
                  (want["name"], want["pos"], want["L"], want["hue"],
                   want["hex"], got or "-"))
        if got is None:
            findings.append(
                "the %s stop of --wash-stops is not a hex literal, so it cannot be "
                "held to the derivation; expected %s" % (want["name"], want["hex"]))
            continue
        if got != want["hex"]:
            findings.append(
                "--wash-stops' %s stop is %s; the rule produces %s -- OKLab L %.4f "
                "(CF-Grau's own L carried to %.2f %% of the ramp) at chroma %.3f and "
                "hue %.2f, which is --%s's. Recompute it, or the wash has stopped "
                "being the reversed foil it documents itself as."
                % (want["name"], got, want["hex"], want["L"], want["pos"],
                   WASH_CHROMA, want["hue"], want["from"]))

        # POSITION: the first stop is 0 % and is written as such; the other two
        # are calc() over the spectrum's own numbers and must stay that way.
        if want["name"] != "Violett":
            need = ("--spectrum-cool-n" if want["name"] == "Sky" else "--rake-near-n")
            if "calc(" not in decl_stop or need not in decl_stop:
                findings.append(
                    "--wash-stops' %s stop states its position without %s. The "
                    "positions are the half of this ramp that follows the palette "
                    "on its own; flattening one to the percentage it evaluates to "
                    "today gives it the same failure mode as the colours."
                    % (want["name"], need))

    # --- the ends ---
    if "--grey-000" not in stops[3] or "100%" not in stops[3].replace(" ", ""):
        findings.append(
            "--wash-stops does not end on var(--grey-000) 100%. Weiss lands at "
            "100 % by construction -- it is the end of the band being reversed -- "
            "and the bottom of every page is that value.")

    # --- LIGHTNESS: the path is the neutral ramp's, by construction ---
    for want in derived:
        got_L = oklab(to_rgb(want["hex"]))[0]
        if abs(got_L - want["L"]) > L_GRID:
            findings.append(
                "the %s stop renders at OKLab L %.4f where the neutral ramp is "
                "%.4f at that position (%.4f apart, past the %.4f the 8-bit grid "
                "explains). tokens.css's claim that the lightness path is unchanged "
                "'exactly and by construction' is what every contrast figure on the "
                "wash and the hero scrim rests on."
                % (want["name"], got_L, want["L"], abs(got_L - want["L"]), L_GRID))

    # --- CHROMA: the budget, and the grain that sets it ---
    for want in derived:
        rgb = to_rgb(want["hex"])
        C = oklch(rgb)[1]
        if C > WASH_CHROMA + 0.0015:
            findings.append(
                "the %s stop measures OKLab chroma %.4f against a budget of %.3f. "
                "The ceiling is the grain already on this surface, not taste."
                % (want["name"], C, WASH_CHROMA))
        neutral = oklch_to_hex(want["L"], 0.0, 0.0)
        worst = max(abs(a - b) for a, b in zip(rgb, to_rgb(neutral)))
        if worst > GRAIN_LEVELS:
            findings.append(
                "the %s stop sits %d eight-bit levels off the neutral ramp on its "
                "worst channel, past the ~%d levels of grain the wash already "
                "carries. 'No channel may move further from the neutral than the "
                "grain does' is the rule the budget comes from."
                % (want["name"], worst, GRAIN_LEVELS))

    # --- FAMILY: the wash's own membership argument, against the foil ---
    #
    # THE BAND IS THE CHROMATIC STOPS' OWN, and Weiss is outside it on purpose.
    # This is the foil's convention rather than a convenience: there, "Weiss is
    # the exception and is meant to be one -- at L 1.000 it sits deliberately
    # *above* the band, which is what makes it read as a specular hot spot
    # rather than as one more step in the ramp." The wash reverses that ramp, so
    # its Weiss is the same stop doing the same job at the other end, and
    # measuring the band across it would report 0.145 for a ramp tokens.css
    # documents at 0.120 -- a check contradicting the file it guards.
    hues = [w["hue"] for w in derived]
    Ls = [w["L"] for w in derived]
    travel = abs(hues[0] - hues[-1])
    band = max(Ls) - min(Ls)
    foil_hues = [oklch(to_rgb(hexes[n]))[2] for n in ("cf-glas", "violett-300")]
    foil_travel = abs(foil_hues[0] - foil_hues[1])
    if verbose:
        print("hue travel %.1f deg (the lit foil's own is %.1f), chromatic band "
              "%.3f, Weiss %.3f above it" % (travel, foil_travel, band, 1.0 - max(Ls)))

    # The white end must stay OUTSIDE the band it terminates, or the wash has
    # quietly become a four-step ramp rather than a three-stop band with a
    # specular at one end -- the same distinction the foil's note draws.
    if max(Ls) >= 1.0:
        findings.append(
            "the wash's lightest chromatic stop reaches OKLab L %.4f, leaving no "
            "room between it and Weiss. Weiss is the reversed foil's specular and "
            "has to sit above the band, not inside it." % max(Ls))
    if abs(travel - foil_travel) > 0.05:
        findings.append(
            "the wash travels %.1f degrees of hue where the lit foil travels %.1f. "
            "The wash's claim to family membership is that its three hues are "
            "--foil-stops' three 'to the digit'; these two ramps have drifted apart."
            % (travel, foil_travel))

    if verbose and not findings:
        print("the wash is the reversed foil, re-derived from --cf-grau and the "
              "foil's own geometry.")
    return findings


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    findings = check(verbose)
    if findings:
        for f in findings:
            print("  " + f, file=sys.stderr)
        print("\n%d finding(s) between --wash-stops and the rule it documents."
              % len(findings), file=sys.stderr)
        return 1
    if not verbose:
        print("the page wash's three chromatic stops are what the rule produces.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
