#!/usr/bin/env python3
"""The conditional glass tint must hold its contrast floor over the backdrop it
actually lands on.

The 156th check, the third whose subject is a contrast guarantee, and the first
that has to look at composited pixels to make one.

WHY THE OTHER TWO CANNOT SEE THIS. check-contrast.py recomputes every pair the
token file rests on, and it can do that because those pairs are arithmetic: a
tint, a backdrop, an ink, alpha composited and rounded. Its register carries
bearing glass and the guarantee that makes bearing glass safe anywhere —

    black type on bearing glass over a pure black frame        4.56:1

— which holds over ANY backdrop, because pure black is the worst one there is.
46 % white was chosen to make that true and tokens.css derives it in full.
check-hero-scrim.py is the second, and it decodes 360 video frames because a
figure over a loop is a figure over one frame unless somebody decodes all of
them.

--surface-glass-thin is neither shape. It is white at 30 %, and over a pure
black frame it composites to rgb(76,76,76), where black type reads 2.45:1. It
is not a floor and was never claimed to be one. tokens.css is explicit about
what it is instead:

    "The 46 % floor is universal because it assumes the worst backdrop there
     is. This one is not universal. Where the thing behind the glass is the
     system's own field, a lattice on the wash, the backdrop is one THAT
     surface says."

So the thin tint's permission is a measurement on a NAMED backdrop, and the
named backdrop is a drawing — an isometric lattice, a gradient, four generated
SVG objects — none of which is a colour any file states. There is no arithmetic
that produces the number. The only instrument that can is a browser that has
already painted it.

AND THE MEASUREMENT WAS MADE ONCE, BY HAND, IN PROSE. foundations/materials.html
carries it as a sentence — 6.73:1, on .cf-info-card__count, on the one stage
that card ships on — which is the exact failure shape check-contrast.py's own
header is written against: "a token is one number in one file, every claim about
it lives in prose somewhere else, and the page after the nudge renders
beautifully on every screen belonging to anyone who would review it." A routine
that restyles the lattice, darkens an object, moves a card to a different band
of the wash, or gives a copy card a new ink tier changes that figure and leaves
the sentence standing. Nothing in 155 checks reads it.

The same argument has already been made once inside this material and acted on.
The act rail's plate ran two ink tiers, muted rising to secondary; a sweep found
the darkest pixel the plate composites to is rgb(164,165,165) and secondary read
3.70:1 there, so the titles went black and the recession moved to marks. That
was found by a person sweeping by hand. This is that sweep, run by the gate.

  GLASS-FLOOR   an ink tier rendered on a translucent surface whose composited
                plate — tint over the blurred backdrop, as the browser paints
                it — puts that ink under its WCAG AA floor at some scroll
                position the surface actually occupies.

WHAT COUNTS AS A CONDITIONAL SURFACE IS READ OUT OF THE RENDER, NOT LISTED HERE.
Every element in the settled DOM whose computed background-color is translucent
and which declares a backdrop-filter is one, and its selectors are nobody's to
maintain — the same reason check-glass-budget.py derives its set from the
stylesheet rather than from a list, and check-gradient-family.py recomputes its
waypoint instead of comparing against a table of hexes. A fifth glass surface
added later enters this gate by existing. A surface at the 46 % bearing tint is
measured too and simply never fails, because its floor is universal; leaving it
in costs one screenshot and keeps the set derived.

THE MEASUREMENT IS THE BROWSER'S OWN COMPOSITE, NOT A MODEL OF IT. The element's
children are hidden and the element itself is screenshotted where it stands, so
what comes back through the lens is tint over blurred backdrop exactly as it is
painted — the real blur radius, the real saturate(), the real backdrop root, the
real stacking. Nothing here reimplements backdrop-filter, and that matters more
than it sounds: a gaussian written in this file would be a second material
wearing the first one's name, which is the fault check-glass-budget.py's second
claim exists to prevent one property over.

THE ARTEFACT THIS CLASS IS MOSTLY MADE OF, and the reason it is fifty lines
rather than ten. A screenshot of an element's box is a screenshot of a RECTANGLE
OF THE VIEWPORT, and everything painted ABOVE the glass lands in it — while
backdrop-filter samples only what is painted BELOW. The two sets are different
and the difference is not small. Measured while this check was being written, on
patterns/expertise.html, naive box capture:

    surface                       darkest px   ink        reads    verdict
    .ex-step__copy  @375           (0,0,0)     secondary  1.10:1   FAIL
    .ex-step__copy  @1280          (126,..)    secondary  3.93:1   FAIL
    .cf-btn--glass  @375           (169,..)    label     12.30:1   ok

Three of those numbers are wrong and none of them is a rendering fault. The
black at 375 is the opaque navigation bar and the consent banner, both painted
over the card and neither behind it. The (126,134,149) at 1280 is the same
navigation bar caught mid-sweep. A gate reporting those would have sent whoever
read it to change a contrast that was never failing — which is worse than no
gate, because it spends the one thing a check has, which is being believed.

SO THE SAMPLE SET IS HIT-TESTED RATHER THAN CROPPED. With the element's own
children hidden, document.elementFromPoint at a sample point returns the glass
element itself exactly when nothing is painted over that point, and returns the
navigation, the banner or the docs chrome when something is. Only points that
come back as the surface are read. It is general — it needs no list of overlays,
no z-index reasoning and no knowledge of which page it is on — and it is exact,
because it asks the same engine the same question the compositor answered.

A surface can therefore be fully covered at some scroll position and contribute
no sample there. That is correct and not a gap: an ink nobody can see cannot
fail a reader.

THE SWEEP IS THE ELEMENT'S OWN PASSAGE, not the document's. Each surface is
carried from "top edge at the bottom of the viewport" to "bottom edge at the
top" in SWEEP_STOPS positions, so every band of artwork it can ever stand on is
sampled. A single visit measures one frame of a moving relationship — which is
the fault check-hero-scrim.py names about video, and a page that scrolls has the
same shape for the same reason.

FLOORS ARE WCAG 2.x AA, and large text is 1.4.3's definition rather than a
guess: 24 px, or 18.66 px at weight 700 and above. Ink is taken from the
computed style of the leaf that carries the text, so a tier that only appears on
one page appears here on that page. Text painted with a gradient — the foil
headings, which set color to transparent and clip a background — is skipped and
said so at -v: its ink is not a colour, and foundations/typography.html carries
that pair's guarantee separately.

stdlib plus playwright, which is the dependency check-runtime.py already spends
and this gate shares a CI job with. The PNG that comes back from a screenshot is
decoded here rather than through Pillow: scripts/og-plate/png.py writes the
format over zlib and calls that the easy half, and this is the other half, at
about the same size.

    python3 scripts/check-glass-floor.py           # check, exit 1 on a finding
    python3 scripts/check-glass-floor.py -v        # every surface, not only hits
    python3 scripts/check-glass-floor.py --page patterns/expertise.html
"""

import argparse
import os
import struct
import sys
import threading
import zlib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "design-system"

# Same candidates check-runtime.py carries, for the same reason: the remote
# sessions this repository is groomed from pre-install a Chromium and export its
# path, and CF_BROWSER overrides everything.
BROWSER_CANDIDATES = [
    os.environ.get("CF_BROWSER"),
    "/opt/pw-browsers/chromium",
]

# The widths the rest of this system is held at. A conditional tint is a
# statement about artwork, and this artwork reflows.
WIDTHS = [375, 768, 1280, 1920]
VIEWPORT_H = 900

SWEEP_STOPS = 7          # positions of the surface's own passage through the viewport
SAMPLE_STEP = 6          # px between hit-tested sample points, both axes
SETTLE_MS = 450
MIN_BOX = 8              # a surface smaller than this has nothing to measure

AA_TEXT = 4.5
AA_LARGE = 3.0


# --------------------------------------------------------------------------
# The other half of scripts/og-plate/png.py.
#
# Chromium hands back an 8-bit non-interlaced PNG, colour type 2 (RGB) or 6
# (RGBA). Everything else raises rather than guessing, because a silent wrong
# read here would produce contrast figures that look entirely reasonable.
# --------------------------------------------------------------------------
def png_pixels(data):
    """Decode a PNG into (width, height, [(r,g,b), ...]) in row-major order."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos, idat, meta = 8, [], None
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            w, h, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 8 or colour not in (2, 6) or interlace:
                raise ValueError("unsupported PNG: depth=%d colour=%d interlace=%d"
                                 % (depth, colour, interlace))
            meta = (w, h, 4 if colour == 6 else 3)
        elif kind == b"IDAT":
            idat.append(body)
        elif kind == b"IEND":
            break
        pos += 12 + length
    if meta is None:
        raise ValueError("PNG carried no IHDR")
    w, h, chan = meta
    raw = zlib.decompress(b"".join(idat))
    stride = w * chan
    out = []
    prev = bytearray(stride)
    pos = 0
    for _ in range(h):
        filt = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        if filt == 1:
            for i in range(chan, stride):
                line[i] = (line[i] + line[i - chan]) & 0xFF
        elif filt == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif filt == 3:
            for i in range(stride):
                left = line[i - chan] if i >= chan else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif filt == 4:
            for i in range(stride):
                a = line[i - chan] if i >= chan else 0
                b = prev[i]
                c = prev[i - chan] if i >= chan else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 0xFF
        elif filt != 0:
            raise ValueError("unknown PNG filter %d" % filt)
        out.extend((line[i], line[i + 1], line[i + 2]) for i in range(0, stride, chan))
        prev = line
    return w, h, out


# --------------------------------------------------------------------------
# WCAG 2.x relative luminance and contrast, on integers, the way a browser
# paints them — check-contrast.py's note applies here too: the composite is
# already quantised by the time it reaches the screenshot.
# --------------------------------------------------------------------------
def _channel(value):
    c = value / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    return (0.2126 * _channel(rgb[0])
            + 0.7152 * _channel(rgb[1])
            + 0.0722 * _channel(rgb[2]))


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def parse_rgb(text):
    """'rgb(1, 2, 3)' / 'rgba(1, 2, 3, 0.4)' -> (r, g, b, a). None if not a colour."""
    text = (text or "").strip()
    if not text.startswith(("rgb(", "rgba(")):
        return None
    body = text[text.index("(") + 1:text.rindex(")")].replace("/", " ").replace(",", " ")
    try:
        parts = [float(p) for p in body.split()]
    except ValueError:
        return None
    if len(parts) == 3:
        parts.append(1.0)
    return tuple(parts[:4]) if len(parts) >= 4 else None


# --------------------------------------------------------------------------
# In the page.
# --------------------------------------------------------------------------

# Derived, not listed — and derived from the STYLESHEET rather than from the
# computed value, which is the difference between catching the real case and
# missing it.
#
# The obvious rule is "translucent background plus a live backdrop-filter", and
# it has a hole the size of the page this check was written for. Inside the
# pinned gate on patterns/expertise.html, `.ex-step .cf-info-card` sets
# `backdrop-filter: none` on all four copy cards — the plate behind them is the
# material there, and spending four more blurred layers on top of it is what the
# glass budget exists to prevent. The cards keep the 30 % tint. So at 1280 they
# are translucent, they bear four ink tiers, they composite over whatever the
# plate composites over — and a computed-value rule walks straight past them,
# because the one property it looks at was deliberately switched off.
#
# A surface with its blur turned off is not less exposed than one with it on. It
# is MORE: a blur is a low-pass filter, so it pulls the darkest pixel of a busy
# backdrop UP towards the local mean, and switching it off hands the ink the raw
# artwork. The tint is what the guarantee rests on either way, and the tint is
# still there.
#
# So membership is a question about the CSS, not about one element's computed
# style: every selector in the loaded stylesheets that declares a backdrop-filter
# names a glass surface, and an element matching one of them with a translucent
# background is measured wherever it lands and whatever this page did to its
# blur. Same derivation check-glass-budget.py makes over the shipping files, made
# here over the CSSOM so it covers exactly what this page actually loaded.
FIND_SURFACES = """
() => {
  // Every selector that declares a backdrop-filter, at any nesting depth.
  const selectors = new Set();
  const walk = rules => {
    for (const rule of rules) {
      if (rule.cssRules) walk(rule.cssRules);
      if (!rule.style || !rule.selectorText) continue;
      const bf = rule.style.getPropertyValue('backdrop-filter')
              || rule.style.getPropertyValue('-webkit-backdrop-filter');
      if (!bf || bf.trim() === 'none') continue;
      for (const part of rule.selectorText.split(',')) {
        // A rule on ::before names the surface it is the edge of, so the
        // pseudo-element is stripped and the originating element measured.
        const bare = part.trim().replace(/::?(before|after|backdrop|first-line|marker)\\b/g, '').trim();
        if (bare) selectors.add(bare);
      }
    }
  };
  for (const sheet of document.styleSheets) {
    try { walk(sheet.cssRules); } catch (e) { /* cross-origin: none here */ }
  }
  const candidates = new Set();
  for (const sel of selectors) {
    try { for (const el of document.querySelectorAll(sel)) candidates.add(el); }
    catch (e) { /* a selector querySelectorAll cannot parse names no element */ }
  }
  const out = [];
  let n = 0;
  for (const el of document.querySelectorAll('*')) {   // document order
    if (!candidates.has(el)) continue;
    const cs = getComputedStyle(el);
    const bg = cs.backgroundColor || '';
    const m = bg.match(/^rgba\\(([^)]+)\\)$/);
    if (!m) continue;                       // opaque rgb() — nothing composites through
    const a = parseFloat(m[1].split(',')[3]);
    if (!(a > 0 && a < 1)) continue;        // fully clear or fully opaque
    const r = el.getBoundingClientRect();
    if (r.width < 8 || r.height < 8) continue;
    const bf = cs.backdropFilter || cs.webkitBackdropFilter;
    el.dataset.cfGlassProbe = String(n);
    out.push({ probe: n, tint: bg, filter: (bf && bf !== 'none') ? bf : 'none (blur off here)',
               name: (el.tagName.toLowerCase()
                      + (el.id ? '#' + el.id : '')
                      + (el.className && typeof el.className === 'string'
                         ? '.' + el.className.trim().split(/\\s+/).join('.') : '')).slice(0, 110) });
    n += 1;
  }
  return out;
}
"""

# Every distinct ink tier the surface actually renders, taken from the leaf that
# carries the text. A leaf whose colour is transparent is painting through a
# clipped background — the foil headings — and is reported rather than measured.
INKS = """
(probe) => {
  const el = document.querySelector('[data-cf-glass-probe="' + probe + '"]');
  if (!el) return [];
  const seen = Object.create(null);
  // THE SURFACE ITSELF IS A LEAF WHEN IT CARRIES ITS OWN TEXT, and leaving it
  // out skipped the one control this whole material exists for. .cf-btn--glass
  // is an <a> whose label is a direct text node, so a walk of descendants alone
  // reported "no ink" on the site's primary call to action at every width — the
  // single surface most worth measuring, silently unmeasured.
  for (const n of [el].concat(Array.from(el.querySelectorAll('*')))) {
    if (!n.textContent || !n.textContent.trim()) continue;
    const own = Array.from(n.childNodes).some(c => c.nodeType === 3 && c.textContent.trim());
    if (!own) continue;
    const cs = getComputedStyle(n);
    if (cs.visibility === 'hidden' || cs.display === 'none' || cs.opacity === '0') continue;
    // INK ON AN OPAQUE OBJECT STANDING ON THE GLASS IS NOT INK ON THE GLASS,
    // and this is the material's own layer order rather than an exemption
    // written for it. foundations/materials.html: "Put opaque objects ON the
    // glass; that is what the layer order means" — the navigation is the
    // shipping case, an opaque logo plate and an opaque link pill standing on
    // the veil, and the label inside them sits on black at 21:1 no matter what
    // the sheet beneath is composited over. Measuring those against the sheet
    // would report the backdrop of a surface the type cannot see.
    let opaque = false;
    for (let a = n; a && a !== el; a = a.parentElement) {
      const bg = getComputedStyle(a).backgroundColor || '';
      const m2 = bg.match(/^rgba?\\(([^)]+)\\)$/);
      if (!m2) continue;
      const parts = m2[1].split(',');
      if (parts.length < 4 || parseFloat(parts[3]) === 1) { opaque = true; break; }
    }
    if (opaque) continue;
    const size = parseFloat(cs.fontSize) || 16;
    const weight = parseInt(cs.fontWeight, 10) || 400;
    const key = cs.color + '|' + size + '|' + weight;
    if (seen[key]) continue;
    seen[key] = { color: cs.color, size: size, weight: weight,
                  large: size >= 24 || (size >= 18.66 && weight >= 700),
                  where: (n.className && typeof n.className === 'string'
                          ? '.' + n.className.trim().split(/\\s+/).join('.')
                          : n.tagName.toLowerCase()).slice(0, 60),
                  sample: n.textContent.trim().slice(0, 30) };
  }
  return Object.values(seen);
}
"""

# Hide the surface's own content so the screenshot is the plate and nothing else,
# then hand back the box and the hit-tested sample points inside it. A point is
# accepted only when the topmost painted element there IS the surface: anything
# else means something is drawn OVER it, and what is drawn over a sheet never
# enters its blur. Coordinates come back viewport-relative and are converted to
# clip-relative by the caller.
MASK_AND_POINTS = """
(args) => {
  const el = document.querySelector('[data-cf-glass-probe="' + args.probe + '"]');
  if (!el) return null;
  // HIDING THE CHILDREN IS NOT HIDING THE CONTENT. .cf-btn--glass carries its
  // label as a direct TEXT NODE, which has no style of its own to hide, so a
  // walk of element children left the glyphs painted and the darkest pixel of
  // the "plate" came back rgb(0,0,0) — the label. The button then failed its own
  // gate at 1.00:1 against ink identical to itself, at every width. Clearing the
  // element's own text colour is what covers a text node; -webkit-text-fill-color
  // is cleared with it because it outranks `color` where it is set, which is
  // exactly where the foil headings set it.
  for (const n of el.children) { n.style.visibility = 'hidden'; }
  el.style.setProperty('color', 'transparent', 'important');
  el.style.setProperty('-webkit-text-fill-color', 'transparent', 'important');
  el.style.setProperty('text-shadow', 'none', 'important');
  const r = el.getBoundingClientRect();
  const x0 = Math.max(0, Math.ceil(r.left)), y0 = Math.max(0, Math.ceil(r.top));
  const x1 = Math.min(window.innerWidth, Math.floor(r.right));
  const y1 = Math.min(window.innerHeight, Math.floor(r.bottom));
  if (x1 - x0 < 2 || y1 - y0 < 2) return { box: null, points: [] };
  const pts = [];
  for (let y = y0 + 1; y < y1 - 1; y += args.step) {
    for (let x = x0 + 1; x < x1 - 1; x += args.step) {
      if (document.elementFromPoint(x, y) === el) pts.push([x, y]);
    }
  }
  return { box: { x: x0, y: y0, w: x1 - x0, h: y1 - y0 }, points: pts };
}
"""

UNMASK = """
(probe) => {
  const el = document.querySelector('[data-cf-glass-probe="' + probe + '"]');
  if (!el) return;
  for (const n of el.children) { n.style.visibility = ''; }
  el.style.removeProperty('color');
  el.style.removeProperty('-webkit-text-fill-color');
  el.style.removeProperty('text-shadow');
}
"""

# Put the surface's own passage through the viewport at stop `i` of `n`, from
# "top edge at the bottom of the viewport" to "bottom edge at the top".
PLACE = """
(args) => {
  const el = document.querySelector('[data-cf-glass-probe="' + args.probe + '"]');
  if (!el) return null;
  const doc = document.scrollingElement || document.documentElement;
  const top = el.getBoundingClientRect().top + doc.scrollTop;
  const h = el.getBoundingClientRect().height;
  const from = top - window.innerHeight;
  const to = top + h;
  const y = from + (to - from) * (args.n <= 1 ? 0.5 : args.i / (args.n - 1));
  window.scrollTo({ top: Math.max(0, Math.round(y)), left: 0, behavior: 'instant' });
  return Math.round(doc.scrollTop);
}
"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def launch(playwright_ctx):
    """A browser, or None — the house idiom the other three browser gates carry:
    a machine without a Chromium is not a failing branch, it is an unguarded
    one, and CF_REQUIRE_BROWSER is what turns the difference into an exit code."""
    for candidate in BROWSER_CANDIDATES:
        if not candidate:
            continue
        try:
            return playwright_ctx.chromium.launch(executable_path=candidate)
        except Exception:
            continue
    try:
        return playwright_ctx.chromium.launch()
    except Exception:
        return None


def dismiss_consent(page):
    """The banner is opaque and covers the foot of the first screen. It is not an
    overlay the hit test needs help with — elementFromPoint already rejects every
    point under it — but a reader who has answered it is the state the rest of the
    page is measured in, and leaving it up costs the surfaces beneath it their
    samples."""
    for name in ("Alle akzeptieren", "Accept all", "Nur notwendige", "Necessary only"):
        try:
            button = page.get_by_role("button", name=name)
            if button.count():
                button.first.click(timeout=2000)
                page.wait_for_timeout(250)
                return True
        except Exception:
            continue
    return False


def measure_surface(page, probe, width):
    """Darkest composited plate pixel over the surface's whole passage.

    Returns (rgb, scroll_y, samples) or None when the surface was never visible
    with a single uncovered point — which is a fact about the page, not a fault.
    """
    worst = None
    for i in range(SWEEP_STOPS):
        scroll_y = page.evaluate(PLACE, {"probe": probe, "i": i, "n": SWEEP_STOPS})
        if scroll_y is None:
            continue
        page.wait_for_timeout(90)
        got = page.evaluate(MASK_AND_POINTS, {"probe": probe, "step": SAMPLE_STEP})
        if not got or not got.get("box") or not got["points"]:
            page.evaluate(UNMASK, probe)
            continue
        box = got["box"]
        try:
            shot = page.screenshot(clip={"x": box["x"], "y": box["y"],
                                         "width": box["w"], "height": box["h"]})
        finally:
            page.evaluate(UNMASK, probe)
        img_w, img_h, pixels = png_pixels(shot)
        # device_scale_factor is 1, so the clip maps one-to-one; guard anyway.
        sx = img_w / float(box["w"])
        sy = img_h / float(box["h"])
        for px, py in got["points"]:
            ix = int((px - box["x"]) * sx)
            iy = int((py - box["y"]) * sy)
            if 0 <= ix < img_w and 0 <= iy < img_h:
                rgb = pixels[iy * img_w + ix]
                if worst is None or luminance(rgb) < luminance(worst[0]):
                    worst = (rgb, scroll_y, len(got["points"]))
    return worst


def check_page(browser, url, rel, width, verbose):
    findings = []
    context = browser.new_context(viewport={"width": width, "height": VIEWPORT_H},
                                  device_scale_factor=1)
    page = context.new_page()
    try:
        page.goto(url, wait_until="load", timeout=30000)
        page.wait_for_timeout(SETTLE_MS)
        dismiss_consent(page)
        surfaces = page.evaluate(FIND_SURFACES)
        for surface in surfaces:
            probe = surface["probe"]
            inks = page.evaluate(INKS, probe)
            if not inks:
                if verbose:
                    print("    %-52s %-26s no ink" % (surface["name"][:52], surface["tint"]))
                continue
            worst = measure_surface(page, probe, width)
            if worst is None:
                if verbose:
                    print("    %-52s %-26s never uncovered" % (surface["name"][:52], surface["tint"]))
                continue
            plate, scroll_y, samples = worst
            if verbose:
                print("    %-52s %-26s plate=rgb%s @y=%d (%d pts)"
                      % (surface["name"][:52], surface["tint"], plate, scroll_y, samples))
            for ink in inks:
                colour = parse_rgb(ink["color"])
                if colour is None or colour[3] == 0:
                    if verbose:
                        print("        %-22s %s  (no ink colour — painted through a clip)"
                              % (ink["color"], ink["where"]))
                    continue
                ratio = contrast(colour[:3], plate)
                floor = AA_LARGE if ink["large"] else AA_TEXT
                if verbose:
                    print("        %-22s %5.1fpx w%-3d %6.2f:1  need %.1f  %s"
                          % (ink["color"], ink["size"], ink["weight"], ratio, floor,
                             "ok" if ratio >= floor else "FAIL"))
                if ratio < floor:
                    findings.append(
                        "GLASS-FLOOR: %s @%dpx\n"
                        "    surface : %s\n"
                        "    tint    : %s over its own blurred backdrop\n"
                        "    plate   : rgb%s — the darkest uncovered pixel of the composite,\n"
                        "              at scrollY %d of the surface's passage (%d points sampled)\n"
                        "    ink     : %s at %gpx weight %d on %s — %r\n"
                        "    reads   : %.2f:1 against a %.1f:1 floor (WCAG 1.4.3, %s text)"
                        % (rel, width, surface["name"], surface["tint"], plate,
                           scroll_y, samples, ink["color"], ink["size"], ink["weight"],
                           ink["where"], ink["sample"], ratio, floor,
                           "large" if ink["large"] else "body"))
    except Exception as exc:
        findings.append("GLASS-FLOOR: %s @%dpx — the visit itself failed: %s" % (rel, width, exc))
    finally:
        context.close()
    return findings


def pages(only):
    if only:
        target = DESIGN / only
        if not target.exists():
            raise SystemExit("no such page: %s" % target)
        return [target]
    found = sorted((DESIGN / "patterns").glob("*.html"))
    found += sorted((DESIGN / "foundations").glob("*.html"))
    found += sorted((DESIGN / "components").glob("*.html"))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="every surface and every ink tier, not only the findings")
    ap.add_argument("--page", help="one page, relative to design-system/")
    ap.add_argument("--width", type=int, action="append",
                    help="one width instead of %s (repeatable)" % WIDTHS)
    args = ap.parse_args()

    required = bool(os.environ.get("CF_REQUIRE_BROWSER"))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        msg = "glass floor: SKIPPED — playwright is not installed (pip install playwright)."
        if required:
            print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.", file=sys.stderr)
            return 1
        print(msg + " The conditional tint is unguarded on this machine; CI still gates it.")
        return 0

    widths = args.width or WIDTHS
    targets = pages(args.page)
    server = serve()
    port = server.server_address[1]
    findings = []
    try:
        with sync_playwright() as ctx:
            browser = launch(ctx)
            if browser is None:
                msg = ("glass floor: SKIPPED — no Chromium found "
                       "(playwright install chromium, or CF_BROWSER).")
                if required:
                    print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.", file=sys.stderr)
                    return 1
                print(msg + " The conditional tint is unguarded on this machine; CI still gates it.")
                return 0
            try:
                for path in targets:
                    rel = path.relative_to(DESIGN).as_posix()
                    url = "http://127.0.0.1:%d/%s" % (port, path.relative_to(ROOT).as_posix())
                    for width in widths:
                        if args.verbose:
                            print("  %s @%dpx" % (rel, width))
                        findings.extend(check_page(browser, url, rel, width, args.verbose))
            finally:
                browser.close()
    finally:
        server.shutdown()

    if findings:
        print("check-glass-floor: %d finding(s).\n" % len(findings))
        for finding in findings:
            print("  " + finding.replace("\n", "\n  "))
            print()
        print("A conditional tint is a promise about ONE backdrop. Either the ink tier")
        print("moves up, or the surface takes --surface-glass, whose 46 % floor holds")
        print("over any backdrop there is. See foundations/materials.html.")
        return 1
    print("glass floor: every ink tier on every conditional glass surface clears WCAG AA "
          "over the darkest backdrop it lands on, at %s px."
          % "/".join(str(w) for w in widths))
    return 0


if __name__ == "__main__":
    sys.exit(main())
