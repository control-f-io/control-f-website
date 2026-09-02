#!/usr/bin/env python3
"""The four declarations that decide what the brand looks like outside the page.

WHAT THIS IS FOR. Every other check in this directory reads something a
stylesheet draws. These four are read by software this repository does not
ship — the browser's own chrome, the reader's launcher, the OS compositor — and
each of them fails in a place no screenshot taken at a desk can reach.

  color-scheme    Chrome for Android's Auto Dark Theme re-tints any document
                  that has not declared a scheme. A desktop browser ignores
                  the feature outright, so the responsive sweep, the contrast
                  register and every screenshot in docs/ agree the page is
                  fine while a share of readers are looking at an inverted
                  one. `only light` is the documented opt-out.
  theme-color     the strip of browser chrome directly above the page. Left
                  undeclared it is the UA's grey, sitting on top of a wash
                  whose first stop this system derives. It is that stop.
  apple-touch-icon
                  the home screen. Undeclared, iOS keeps a thumbnail of a
                  screenshot, and the manual's App-Icon frame — one of the
                  five it defines — has never been drawn.
  manifest        the same on Android, plus the two colours a launcher uses.

WHAT IT CHECKS.

  the scheme is on every page   `<meta name="color-scheme" content="only
                  light">` and a `theme-color` on every .html under
                  design-system/, prototypes included. A scheme is a fact
                  about a rendered document and every one of these renders.
  the colour is derived, not typed   the theme-color on all of them, and both
                  colours in the manifest, equal the first stop of
                  --wash-stops read out of tokens.css. Nothing here carries a
                  hex of its own.
  the stylesheet says it too   base.css declares `color-scheme: only light` on
                  html and `color-scheme: dark` on [data-theme="inverse"]. The
                  meta is what the parser sees first; the property is what
                  cascades, and a subtree that inverts every token this system
                  owns has to invert the UA's too.
  the home screen is declared   every page that declares rel="icon" — the
                  register check-favicon-frame.py already holds, patterns and
                  documentation, prototypes excluded for the reason given
                  there — also declares apple-touch-icon and manifest, and
                  both resolve.
  the tiles are what they say   each icon named by the manifest exists, and
                  its IHDR width and height are the sizes the manifest
                  declares. Read out of the PNG header, not out of the
                  filename.
  THE MASKABLE SAFE ZONE IS MEASURED. A maskable icon is cropped by a shape
                  the launcher chooses and only the centre circle of 80 %
                  diameter is guaranteed to survive. This check renders the
                  512 tile in memory, finds every pixel that is not the
                  ground, and measures the farthest one from the centre. An
                  icon whose mark reaches past that circle loses a corner of
                  the signet on some launchers and no other check in this
                  repository — or any screenshot taken on the machine that
                  built it — would ever show which ones.

WHY THE SAFE ZONE IS RENDERED RATHER THAN READ OFF DISK. The generator's
--check already proves the file on disk is that render; measuring the render
instead of the file means this check holds the DRAWING, and it holds it on a
machine where the icons have never been built.

Proven failing on: the meta removed from one chapter, `light` in place of
`only light`, the theme-color moved one hex off the wash, the manifest's
theme_color typed rather than derived, the apple-touch-icon line removed from
one pattern page, a manifest icon renamed, a size row that disagrees with the
PNG header, MARK_WIDTH raised to 0.72 so the signet crosses the safe circle,
and the [data-theme="inverse"] rule deleted from base.css.
"""

import argparse
import importlib.util
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
TOKENS = DS / "assets/css/tokens.css"
BASE = DS / "assets/css/base.css"
ICON_DIR = DS / "assets/icon"

SCHEME = "only light"
# The maskable contract: content inside the centre circle of 80 % diameter, so
# 40 % of the edge as a radius. w3.org/TR/appmanifest/#icon-masks
SAFE_RADIUS = 0.40

COMMENT = re.compile(r"<!--.*?-->", re.S)
META = re.compile(r"<meta\b[^>]*\bname=\"([^\"]+)\"[^>]*\bcontent=\"([^\"]*)\"[^>]*>", re.I)
LINK = re.compile(r"<link\b[^>]*\brel=\"([^\"]+)\"[^>]*>", re.I)
HREF = re.compile(r"\bhref=\"([^\"]+)\"")
WASH_HEAD = re.compile(r"--wash-stops:\s*(#[0-9A-Fa-f]{6})")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def theme_colour():
    m = WASH_HEAD.search(TOKENS.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit("check-outside-page: tokens.css --wash-stops "
                         "does not open with a hex.")
    return m.group(1).upper()


def rels(text):
    """{rel token: href} for every <link> outside a comment."""
    out = {}
    for m in LINK.finditer(COMMENT.sub("", text)):
        href = HREF.search(m.group(0))
        for token in m.group(1).lower().split():
            out.setdefault(token, href.group(1) if href else "")
    return out


def audit_pages(theme):
    findings, pages, homed = [], 0, 0
    for path in sorted(DS.rglob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        metas = {m.group(1).lower(): m.group(2)
                 for m in META.finditer(COMMENT.sub("", text))}
        pages += 1

        got = metas.get("color-scheme")
        if got is None:
            findings.append((rel, "no color-scheme meta: this document is a "
                                  "light page a browser may decide to re-tint"))
        elif got.strip() != SCHEME:
            findings.append((rel, "color-scheme is %r, not %r — without `only` "
                                  "the automatic dark rendering still applies"
                             % (got, SCHEME)))

        got = metas.get("theme-color")
        if got is None:
            findings.append((rel, "no theme-color: the chrome above the page "
                                  "is the UA's grey"))
        elif got.strip().upper() != theme:
            findings.append((rel, "theme-color is %s; the wash opens at %s"
                             % (got, theme)))

        # THE REGISTER IS check-favicon-frame.py's, INCLUDING ITS EXCLUSION.
        # That check holds every page outside prototypes/ to declaring
        # rel="icon", and leaves the six labs out because they are the
        # designer's raw material and unshipped. The home screen follows the
        # same line: two of those six declare an icon anyway — which is one
        # word off what that check's own docstring says about them — and a lab
        # nobody can navigate to is not a page anybody adds to a home screen.
        if path.relative_to(DS).parts[0] == "prototypes":
            continue
        link = rels(text)
        if "icon" not in link:
            continue
        homed += 1
        for token, want in (("apple-touch-icon", "assets/icon/cf-app-icon-180.png"),
                            ("manifest", "assets/icon/site.webmanifest")):
            href = link.get(token)
            if href is None:
                findings.append((rel, "declares rel=\"icon\" and not "
                                      "rel=\"%s\": a page that answers the tab "
                                      "and not the home screen" % token))
            elif not href.endswith(want):
                findings.append((rel, "rel=\"%s\" points at %s, not %s"
                                 % (token, href, want)))
            elif not (path.parent / href).resolve().exists():
                findings.append((rel, "rel=\"%s\" href %s does not resolve — "
                                      "run `python3 scripts/build-app-icons.py`"
                                 % (token, href)))
    return findings, pages, homed


def audit_stylesheet():
    src = COMMENT.sub("", BASE.read_text(encoding="utf-8"))
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    findings = []
    if not re.search(r"\bhtml\s*\{[^}]*color-scheme:\s*only\s+light\s*;", src, re.S):
        findings.append(("design-system/assets/css/base.css",
                         "html does not declare `color-scheme: only light`; the "
                         "meta is what the parser sees and this is what cascades"))
    if not re.search(r"\[data-theme=\"inverse\"\][^{]*\{[^}]*color-scheme:\s*dark\s*;",
                     src, re.S):
        findings.append(("design-system/assets/css/base.css",
                         "[data-theme=\"inverse\"] does not declare "
                         "`color-scheme: dark`; the inverse theme flips every "
                         "token this system owns and none of the UA's"))
    return findings


def png_size(path):
    """(width, height) out of the IHDR, without decoding the image."""
    head = path.read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise ValueError("%s is not a PNG" % path.name)
    return struct.unpack(">II", head[16:24])


def audit_manifest(theme):
    import json
    findings = []
    path = ICON_DIR / "site.webmanifest"
    if not path.exists():
        return [("design-system/assets/icon/site.webmanifest",
                 "missing — run `python3 scripts/build-app-icons.py`")], 0
    doc = json.loads(path.read_text(encoding="utf-8"))
    rel = "design-system/assets/icon/site.webmanifest"
    for key in ("theme_color", "background_color"):
        if doc.get(key, "").upper() != theme:
            findings.append((rel, "%s is %s; the wash opens at %s"
                             % (key, doc.get(key), theme)))
    for key in ("start_url", "scope"):
        if doc.get(key, "").startswith("/"):
            findings.append((rel, "%s is absolute; the Pages deploy serves this "
                                  "site from a subpath and would resolve it to "
                                  "another site's root" % key))
    icons = doc.get("icons", [])
    for entry in icons:
        src = ICON_DIR / entry["src"]
        if not src.exists():
            findings.append((rel, "icons names %s, which does not exist"
                             % entry["src"]))
            continue
        w, h = png_size(src)
        if "%dx%d" % (w, h) != entry["sizes"]:
            findings.append((rel, "%s is declared %s and its header says %dx%d"
                             % (entry["src"], entry["sizes"], w, h)))
    if not any("maskable" in e.get("purpose", "") for e in icons):
        findings.append((rel, "no maskable icon: a launcher that masks gets a "
                              "tile it has to guess the safe area of"))
    return findings, len(icons)


def audit_safe_zone():
    """Render the 512 tile and measure how far the mark reaches from centre."""
    gen = load("cf_build_app_icons", ROOT / "scripts" / "build-app-icons.py")
    size = 512
    cv = gen.render(size)
    ground = gen.raster.hex_rgb(gen.GROUND)
    px, worst = cv.px, 0.0
    cx = cy = size / 2.0
    # A pixel counts as mark where it differs from the ground by more than one
    # 8-bit step, so the antialiased fringe of the outline is not read as art.
    for y in range(size):
        base = y * size * 3
        dy = (y + 0.5) - cy
        for x in range(size):
            o = base + x * 3
            if (abs(px[o] - ground[0]) <= 1 and abs(px[o + 1] - ground[1]) <= 1
                    and abs(px[o + 2] - ground[2]) <= 1):
                continue
            dx = (x + 0.5) - cx
            d = (dx * dx + dy * dy) ** 0.5
            if d > worst:
                worst = d
    reach = worst / size
    findings = []
    if reach > SAFE_RADIUS:
        findings.append(("scripts/build-app-icons.py",
                         "the mark reaches %.1f %% of the tile from its centre "
                         "and the maskable safe circle is %.0f %%: a launcher "
                         "that masks cuts the signet"
                         % (reach * 100, SAFE_RADIUS * 100)))
    return findings, reach


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print the numbers behind the pass")
    args = ap.parse_args()

    theme = theme_colour()
    findings, pages, homed = audit_pages(theme)
    findings += audit_stylesheet()
    manifest_findings, icons = audit_manifest(theme)
    findings += manifest_findings
    zone_findings, reach = audit_safe_zone()
    findings += zone_findings

    if findings:
        print("outside the page: %d finding(s)\n" % len(findings))
        for where, what in findings:
            print("  %s\n      %s" % (where, what))
        return 1

    print("outside the page: %d pages declare the scheme at %s, %d of them the "
          "home screen; %d manifest icons, mark reaches %.1f %% of %.0f %%."
          % (pages, theme, homed, icons, reach * 100, SAFE_RADIUS * 100))
    if args.verbose:
        print("  color-scheme  only light on html, dark on [data-theme=inverse]")
        print("  theme-color   %s, the first stop of --wash-stops" % theme)
        print("  safe zone     %.1f %% reach against a %.0f %% radius, measured "
              "on the 512 render" % (reach * 100, SAFE_RADIUS * 100))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
