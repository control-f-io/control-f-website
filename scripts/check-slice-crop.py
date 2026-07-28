#!/usr/bin/env python3
"""Hold a `slice` crop to the part of the drawing the crop exists to show.

THE SHAPE, and why nothing else in this directory catches it.

`preserveAspectRatio="… slice"` fills the box and throws the surplus axis away.
Every check here that touches a figure asks whether the drawing FITS — see
check-figure-letterbox.py, whose whole subject is dead space around an object
that stopped growing. A slice crop has the opposite failure: it never leaves
dead space, never overflows, never clips anything a browser will report, and
renders perfectly at every width. What it can do is show the wrong 58 % of the
picture, and there is no measurement of the box that says so.

Worse, it does it CONSTANTLY. A box whose height comes from `width x ratio`
crops the same fraction at every width, because both ratios are fixed:

    window width in viewBox units = viewBox height x box ratio

is a number with no viewport in it. So a bad crop is not a bug at one width
that a ladder sweep finds; it is the same wrong picture at 320 and at 1000, and
a ladder finds it at all ten stops or at none of them. The only thing that
decides which units survive is the ALIGN KEYWORD — xMin, xMid, xMax — a token
typed once next to the viewBox, defaulted more often than chosen, and invisible
in every screenshot unless you already know what the drawing is supposed to say.

WHAT IT COST. patterns/landing-page.html's statement band is 1200 x 420 and
carries `xMinYMid slice` against a 5/3 stacked box. The visible window was
[0, 700] — at every width below the 56rem fold, which is every phone and every
tablet in portrait. The drawing's field is masked out at x 648, so x 648–1200
is the void, 552 units, 46 % of the drawing, and the void is the subject: the
claim set on the band says the sensors produce data and no answers. The crop
kept 52 of those 552 units. The reader got a lattice running edge to edge and
thinning slightly at the right, over a sentence about there being nothing there
— the picture arguing against its own caption, on the flagship page, at ten of
the ten widths on the ladder.

WHAT THIS CHECKS, and all of it is re-derived rather than compared to itself.

  1. THE SUBJECT'S SHARE OF THE FRAME. Each registered crop names an interval
     of the viewBox as its subject and where that interval comes from — here,
     the last stop of the mask gradient that ends the field, read out of the
     markup, not typed here. The check computes the visible window in each box
     ratio the shipping stylesheet gives the figure, and requires the subject's
     share of the frame to stay within TOLERANCE points of its share in the
     WIDEST window — the mode the composition was drawn in. A crop is allowed
     to be a crop; it is not allowed to change what the drawing is about.

  2. NO REGISTERED OBJECT CUT BY THE FRAME. The drawing's solid objects are
     re-derived from their own arc paths — a ring drawn as four quarter arcs
     gives its centre as the mean of the endpoints and its radius from the arc
     command — and must lie inside every window. This is the constraint that
     picks the ratio once the align keyword has fixed the share, and it is the
     rule the statement's own #cf-stmt-halo note already states in prose: "an
     extent of its own instead of four edges cut by the frame".

  3. ONE ALIGN KEYWORD PER DRAWING. The statement band exists three times in
     this tree — the pattern, the component specimen, and the escaped code
     sample beside the specimen — which is the arrangement the breakpoint
     register was caught short by four times. Two copies of a decision is the
     shape of a fork. Every occurrence of a slice crop in design-system/ must
     be registered, and every occurrence belonging to one drawing must carry
     the same keyword.

WHAT IT DOES NOT CHECK, deliberately

  Whether the subject is the right subject. The register below says what a
  drawing is about; the check holds the crop to it. Naming a different subject
  is a design decision and it goes in this file, in the same commit, the way a
  threshold goes in the breakpoint register.

  `meet` crops nothing and is out of scope. prototypes/ is out of scope — the
  same boundary tokens.css draws around its register.

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css" / "components.css"
PAGES = ROOT / "design-system"

# Out by the boundary every register in this system draws.
SKIP_DIRS = ("prototypes",)

# How far the subject's share of the frame may drift from the share the
# uncropped mode gives it, in percentage points. Five is wide enough that the
# ratio can be chosen for the objects and narrow enough that an anchor on the
# wrong end of the drawing — 7.4 % against 46.0 % — cannot pass.
TOLERANCE = 5.0

# THE REGISTER. One entry per drawing that carries a slice crop.
#
#   selector  the rule in components.css whose aspect-ratio declarations set
#             the box. Every declaration for this exact selector is read, so a
#             ratio added inside a container query is picked up with the base.
#   subject   (name, derivation) — the interval of the viewBox the crop must
#             keep a fair share of. The derivation is a callable given the SVG
#             source, so the numbers come from the drawing.
#   objects   (name, derivation) — intervals no window may cut.
CROPS = {
    ".cf-statement__figure .cf-iso": {
        "what": "the statement band",
        "files": ("patterns/landing-page.html", "components/statement.html"),
        "subject": "the void",
        "objects": "the ring and its nucleus",
    },
}


def ratios_for(selector, css):
    """Every aspect-ratio the shipping sheet gives one selector, as floats."""
    out = []
    for m in re.finditer(re.escape(selector) + r"\s*\{([^}]*)\}", css):
        for a in re.finditer(r"aspect-ratio\s*:\s*([\d.]+)\s*/\s*([\d.]+)", m.group(1)):
            w, h = float(a.group(1)), float(a.group(2))
            out.append((a.group(1) + " / " + a.group(2), w / h))
    return out


def svg_of(text, selector):
    """The <svg …> element carrying the slice crop, and its viewBox."""
    m = re.search(r"<svg\b[^>]*preserveAspectRatio\s*=\s*\"(x\w+ slice)\"[^>]*>", text)
    if not m:
        return None
    align = m.group(1).split("Y")[0]
    vb = re.search(r'viewBox\s*=\s*"([\d.\-\s]+)"', m.group(0))
    if not vb:
        return None
    x0, y0, w, h = (float(n) for n in vb.group(1).split())
    end = text.find("</svg>", m.end())
    return {"align": align, "vb": (x0, y0, w, h),
            "body": text[m.end():end if end > 0 else len(text)]}


def void_from_reach(body):
    """Where the field stops: the last zero-opacity stop of the reach ramp.

    The gradient is userSpaceOnUse over x1..x2, so an offset is an x directly.
    Read rather than typed — the drawing is allowed to move its own edge, and
    when it does this check follows it instead of contradicting it.
    """
    g = re.search(r'<linearGradient id="[^"]*reach"[^>]*x1="([\d.]+)"[^>]*x2="([\d.]+)"'
                  r'[^>]*>(.*?)</linearGradient>', body, re.S)
    if not g:
        return None
    x1, x2 = float(g.group(1)), float(g.group(2))
    zeros = [float(s.group(1)) for s in
             re.finditer(r'<stop offset="([\d.]+)"[^>]*stop-opacity="0"', g.group(3))]
    if not zeros:
        return None
    return x1 + max(zeros) * (x2 - x1)


def rings(body):
    """Circle extents re-derived from quarter-arc paths, grouped by radius.

    Four quarters of one circle put their eight endpoints symmetrically about
    the centre, so the mean of the endpoints IS the centre — no arc maths, and
    it stays right if the split angles ever change.
    """
    by_r = {}
    for p in re.finditer(r'\bd="M([\d.]+) ([\d.]+)A([\d.]+) [\d.]+ 0 0 1 ([\d.]+) ([\d.]+)"', body):
        x1, y1, r, x2, y2 = (float(p.group(i)) for i in (1, 2, 3, 4, 5))
        by_r.setdefault(r, []).extend([x1, x2])
    return {r: (sum(xs) / len(xs) - r, sum(xs) / len(xs) + r) for r, xs in by_r.items()}


def window(vb, ratio, align):
    """The viewBox interval a `slice` box of this ratio shows."""
    x0, _, w, h = vb
    span = min(h * ratio, w)          # wider than the drawing and the crop goes vertical
    if align == "xMin":
        left = x0
    elif align == "xMax":
        left = x0 + w - span
    else:
        left = x0 + (w - span) / 2
    return left, left + span


def overlap(a, b):
    return max(0.0, min(a[1], b[1]) - max(a[0], b[0]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every window, not only the failures")
    args = ap.parse_args()

    css = CSS.read_text()
    findings = []
    rows = []

    # Every slice crop in the tree, so an unregistered one is a finding rather
    # than a silence. The escaped code sample has no parseable <svg>, and that
    # is the point of counting keywords rather than elements.
    seen = {}
    for f in sorted(PAGES.rglob("*.html")):
        if f.relative_to(PAGES).parts[0] in SKIP_DIRS:
            continue
        text = f.read_text()
        for m in re.finditer(r"\b(x(?:Min|Mid|Max))Y(?:Min|Mid|Max) slice\b", text):
            seen.setdefault(str(f.relative_to(ROOT)), []).append(m.group(1))

    for selector, entry in CROPS.items():
        ratios = ratios_for(selector, css)
        if not ratios:
            findings.append("%s: registered here and carries no aspect-ratio in "
                            "components.css." % selector)
            continue

        aligns = set()
        for rel in entry["files"]:
            path = PAGES / rel
            keys = seen.pop(str(path.relative_to(ROOT)), [])
            aligns.update(keys)

        if len(aligns) != 1:
            findings.append(
                "%s (%s): the crop is written %d different ways across its copies "
                "— %s. One drawing, one anchor; two copies of a decision is the "
                "shape of a fork."
                % (selector, entry["what"], len(aligns), ", ".join(sorted(aligns))))
            continue
        align = aligns.pop()

        svg = svg_of((PAGES / entry["files"][0]).read_text(), selector)
        if not svg:
            findings.append("%s: no <svg> with a slice crop in %s."
                            % (selector, entry["files"][0]))
            continue
        vb = svg["vb"]

        subject = void_from_reach(svg["body"])
        if subject is None:
            findings.append("%s: could not read %s out of the drawing."
                            % (selector, entry["subject"]))
            continue
        subject = (subject, vb[0] + vb[2])
        objects = rings(svg["body"])

        # The widest window is the mode the composition was drawn in.
        wins = [(label, ratio, window(vb, ratio, align)) for label, ratio in ratios]
        wins.sort(key=lambda r: r[2][1] - r[2][0])
        ref = wins[-1]
        ref_share = 100 * overlap(ref[2], subject) / (ref[2][1] - ref[2][0])

        for label, ratio, win in wins:
            span = win[1] - win[0]
            share = 100 * overlap(win, subject) / span
            rows.append((selector, label, win, share, ref_share))
            if abs(share - ref_share) > TOLERANCE:
                findings.append(
                    "%s (%s): at aspect-ratio %s the %s crop shows viewBox "
                    "x %g–%g, and %s takes %.1f %% of the frame against %.1f %% "
                    "at %s — %.1f points, past the %.1f the register allows.\n"
                    "      The window is %g units wide at EVERY viewport, so this "
                    "is the same picture at 320 px and at 1000. Move the anchor "
                    "before the ratio: the anchor decides which units survive, "
                    "the ratio only decides how many."
                    % (selector, entry["what"], label, align, win[0], win[1],
                       entry["subject"], share, ref_share, ref[0],
                       abs(share - ref_share), TOLERANCE, span))
            for r, ext in sorted(objects.items()):
                if ext[0] < win[0] - 1e-6 or ext[1] > win[1] + 1e-6:
                    findings.append(
                        "%s (%s): at aspect-ratio %s the window x %g–%g cuts %s "
                        "— the r=%g circle spans x %g–%g. A frame through a solid "
                        "object is the thing this drawing's own halo exists to "
                        "avoid; widen the ratio until the rim clears the edge."
                        % (selector, entry["what"], label, win[0], win[1],
                           entry["objects"], r, ext[0], ext[1]))

    for path, keys in sorted(seen.items()):
        findings.append("%s: carries a slice crop (%s) that no entry in this "
                        "register claims. Add it, or the next anchor nobody "
                        "chose is invisible again." % (path, ", ".join(sorted(set(keys)))))

    if args.verbose:
        print("slice crops, as read out of the markup and the shipping sheet:\n")
        for sel, label, win, share, ref in rows:
            print("  %-34s %-12s window x %7.1f–%-7.1f subject %5.1f %% "
                  "(reference %.1f %%)" % (sel[:34], label, win[0], win[1], share, ref))
        print()

    if findings:
        print("slice crop: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  " + f + "\n")
        return 1

    print("slice crop: %d registered drawing(s), %d window(s) read, every subject "
          "within %.1f points of the uncropped composition and no object cut."
          % (len(CROPS), len(rows), TOLERANCE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
