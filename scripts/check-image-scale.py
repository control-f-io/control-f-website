#!/usr/bin/env python3
"""Hold a raster file's pixel count to the fixed box the stylesheet paints it in.

THE SHAPE. Most images on this site are sized by their container and there is
no number to check them against. A few are not: a rule states BOTH width and
height as a fixed length, and from then on the file's own dimensions have
nothing to do with what is drawn.

    .cf-team-strip__avatar { width: 3.5rem; height: 3.5rem; object-fit: cover; }
    .cf-article__avatar    { width: 3rem;   height: 3rem;   object-fit: cover; }

Those two rules are the whole register, and the register is DERIVED and not
listed: the script reads the three shipping stylesheets and takes every rule
that pins both axes to a fixed length, then keeps the ones whose class is worn
by an <img> pointing at a raster file. Nothing here is kept by hand, so nothing
here can be caught short.

WHAT IT COST. Every one of them was being handed the 640 x 800 studio portrait:

    patterns/landing-page.html   .cf-team-strip__avatar x4   210,928 bytes
    components/team.html         .cf-team-strip__avatar x4   210,928 bytes
    patterns/blog-artikel.html   .cf-article__avatar   x1     49,142 bytes
    components/article.html      .cf-article__avatar   x1     49,142 bytes

On the landing page that was 10.1 % of the 2,098,207 bytes the page transfers —
second only to the hero loop — to paint four 56 px circles covering 0.6 % of its
drawn area. 512,000 source pixels each for 3,136 painted ones, and 163 x the
area a 1 x screen can use.

WHY NOTHING CAUGHT IT. It renders correctly. The browser downsamples, the
circles are sharp, no check failed and no screenshot differs. A cost that is
invisible in the picture and countable in the file is exactly what a script is
for — the same argument foundations/materials.html makes for the glass budget.

THE INVARIANT, in device pixels, per axis:

    2 x box  <=  file  <=  3 x box

The ceiling is the densest mainstream screen: at dpr 3 a 56 px box paints 168
device pixels, and a file larger than that ships bytes no display can resolve.
The floor is the other failure — a file under 2 x is upscaled on the ordinary
retina screen, which is the one most readers have.

The window is per component, and the two overlap: the 3.5rem box wants 112 to
168, the 3rem box wants 96 to 144, and 112 to 144 satisfies both. That is why
one 144 px derivative serves both boxes on all four pages, and why none of them
needs a srcset — inside a window this narrow there is no second candidate for a
browser to choose between.

ALSO CHECKED, because both are silent and both break the arithmetic above:
  - width/height attributes, where present, must be the file's real dimensions.
    They are the aspect-ratio box; a stale pair reserves the wrong space.
  - srcset `w` descriptors, where present, must be the candidate's real width.
    A descriptor is a promise the browser cannot verify, and selection is done
    entirely on the promise.

SCOPE is design-system/ and nothing above it: the three shipping stylesheets
for the register, and every .html under design-system/ for the uses. The root
generation is deliberately out — it carries its own assets/css/, so its boxes
are not these boxes and pairing a root page against this register would be
measuring against the wrong stylesheet. SVG sources are skipped: they have no
pixel budget to blow. docs.css is documentation chrome and is not read, for the
same reason the letterbox check does not read it.
"""
import argparse
import os
import re
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = [
    "design-system/assets/css/tokens.css",
    "design-system/assets/css/base.css",
    "design-system/assets/css/components.css",
]
REM_PX = 16.0          # nothing in the shipping sheets moves the root font-size
DPR_MAX = 3            # ceiling: the densest mainstream screen
DPR_MIN = 2            # floor: the ordinary retina screen must not be upscaled

FIXED_LEN = re.compile(r"^\s*([\d.]+)\s*(rem|px)\s*$")
RASTER = (".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif")


def blank(m):
    """Replace a span with spaces, keeping its newlines so line numbers hold."""
    return "".join(c if c == "\n" else " " for c in m.group())


def strip_comments(src):
    return re.sub(r"/\*.*?\*/", blank, src, flags=re.S)


def to_px(value):
    m = FIXED_LEN.match(value)
    if not m:
        return None
    n, unit = float(m.group(1)), m.group(2)
    return n * REM_PX if unit == "rem" else n


def fixed_boxes():
    """Every class the shipping sheets pin to a fixed width AND height."""
    boxes = {}
    for rel in CSS:
        path = os.path.join(ROOT, rel)
        src = strip_comments(open(path, encoding="utf-8").read())
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", src):
            sel, body = m.group(1).strip(), m.group(2)
            if "@" in sel or "::" in sel or ":" in sel:
                continue
            decls = {}
            for d in body.split(";"):
                if ":" in d:
                    k, v = d.split(":", 1)
                    decls[k.strip()] = v.strip()
            w, h = to_px(decls.get("width", "")), to_px(decls.get("height", ""))
            if w is None or h is None:
                continue
            for cls in re.findall(r"\.([A-Za-z0-9_-]+)\s*$", sel):
                line = src[: m.start()].count("\n") + 1
                boxes[cls] = (w, h, os.path.basename(rel), line,
                              decls.get("width"), decls.get("height"))
    return boxes


def intrinsic(path):
    """Pixel dimensions from the file header. No decoder, no dependency."""
    with open(path, "rb") as fh:
        d = fh.read()
    if d[:2] == b"\xff\xd8":                                    # JPEG
        i = 2
        while i < len(d) - 9:
            if d[i] != 0xFF:
                i += 1
                continue
            mk = d[i + 1]
            if mk in (0xD8, 0xD9) or 0xD0 <= mk <= 0xD7 or mk == 0xFF:
                i += 2
                continue
            if 0xC0 <= mk <= 0xCF and mk not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", d[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", d[i + 2:i + 4])[0]
        return None
    if d[:8] == b"\x89PNG\r\n\x1a\n":                           # PNG
        return struct.unpack(">II", d[16:24])
    if d[:4] == b"RIFF" and d[8:12] == b"WEBP":                 # WebP (VP8/VP8L/VP8X)
        if d[12:16] == b"VP8X":
            return (int.from_bytes(d[24:27], "little") + 1,
                    int.from_bytes(d[27:30], "little") + 1)
        if d[12:16] == b"VP8 ":
            return (struct.unpack("<H", d[26:28])[0] & 0x3FFF,
                    struct.unpack("<H", d[28:30])[0] & 0x3FFF)
        if d[12:16] == b"VP8L":
            b0 = int.from_bytes(d[21:25], "little")
            return ((b0 & 0x3FFF) + 1, ((b0 >> 14) & 0x3FFF) + 1)
    if d[:6] in (b"GIF87a", b"GIF89a"):                         # GIF
        return struct.unpack("<HH", d[6:10])
    return None


def pages():
    """Every page that is styled by the register's own stylesheets."""
    out = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "design-system")):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "assets")]
        out += [os.path.join(dirpath, fn) for fn in filenames if fn.endswith(".html")]
    return sorted(out)


IMG = re.compile(r"<img\b[^>]*>", re.S)
ATTR = re.compile(r'([A-Za-z_:-][\w:.-]*)\s*=\s*"([^"]*)"', re.S)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    boxes = fixed_boxes()
    findings, seen = [], []

    for page in pages():
        rel = os.path.relpath(page, ROOT)
        src = open(page, encoding="utf-8").read()
        body = strip_comments(src)
        body = re.sub(r"<!--.*?-->", blank, body, flags=re.S)
        for m in IMG.finditer(body):
            attrs = dict(ATTR.findall(m.group()))
            classes = attrs.get("class", "").split()
            hit = next((c for c in classes if c in boxes), None)
            if not hit:
                continue
            src_attr = attrs.get("src", "")
            if not src_attr.lower().endswith(RASTER):
                continue
            bw, bh, css_file, css_line, raw_w, raw_h = boxes[hit]
            line = body[: m.start()].count("\n") + 1

            candidates = [(src_attr, None)]
            for part in filter(None, (p.strip() for p in attrs.get("srcset", "").split(","))):
                bits = part.split()
                candidates.append((bits[0], bits[1] if len(bits) > 1 else None))

            for url, descriptor in candidates:
                fpath = os.path.normpath(os.path.join(os.path.dirname(page), url))
                if not os.path.exists(fpath):
                    findings.append(f"{rel}:{line}  .{hit}\n"
                                    f"    {url} does not exist.")
                    continue
                dims = intrinsic(fpath)
                if not dims:
                    continue
                fw, fh = dims
                lo_w, hi_w = bw * DPR_MIN, bw * DPR_MAX
                lo_h, hi_h = bh * DPR_MIN, bh * DPR_MAX
                where = (f"{rel}:{line}  .{hit}  {os.path.basename(url)}\n"
                         f"    box is {bw:.0f} x {bh:.0f} px "
                         f"({css_file}:{css_line}, width: {raw_w}; height: {raw_h}) — "
                         f"the window is {lo_w:.0f}-{hi_w:.0f} x {lo_h:.0f}-{hi_h:.0f}.")
                if fw > hi_w or fh > hi_h:
                    over = (fw * fh) / max(1.0, hi_w * hi_h)
                    findings.append(
                        f"{where}\n"
                        f"    File is {fw} x {fh} — {over:.1f}x the area a {DPR_MAX}x screen "
                        f"can resolve, {os.path.getsize(fpath):,} bytes of it.")
                elif fw < lo_w or fh < lo_h:
                    findings.append(
                        f"{where}\n"
                        f"    File is {fw} x {fh} — upscaled on a {DPR_MIN}x screen.")
                else:
                    seen.append((rel, line, hit, os.path.basename(url), fw, fh, bw, bh,
                                 os.path.getsize(fpath)))

                if descriptor and descriptor.endswith("w"):
                    claimed = int(descriptor[:-1])
                    if claimed != fw:
                        findings.append(
                            f"{rel}:{line}  .{hit}\n"
                            f"    srcset says {os.path.basename(url)} is {claimed}w; "
                            f"the file is {fw} px wide. Selection is done on the descriptor.")

            if attrs.get("srcset") and "w" in attrs.get("srcset", "") and "sizes" not in attrs:
                findings.append(f"{rel}:{line}  .{hit}\n"
                                f"    srcset carries w descriptors and there is no sizes; "
                                f"the browser assumes 100vw and takes the largest candidate.")

            aw, ah = attrs.get("width"), attrs.get("height")
            if aw and ah:
                fpath = os.path.normpath(os.path.join(os.path.dirname(page), src_attr))
                dims = intrinsic(fpath) if os.path.exists(fpath) else None
                if dims and (int(aw), int(ah)) != dims:
                    findings.append(
                        f"{rel}:{line}  .{hit}\n"
                        f'    width="{aw}" height="{ah}" against a file that is '
                        f"{dims[0]} x {dims[1]}. Those attributes are the aspect-ratio box.")

    if args.verbose or not findings:
        for rel, line, cls, fn, fw, fh, bw, bh, size in seen:
            print(f"{rel}:{line}  .{cls}\n"
                  f"    {fn} {fw} x {fh} in a {bw:.0f} x {bh:.0f} box "
                  f"({fw / bw:.2f}x), {size:,} bytes")

    if findings:
        print(f"image scale: {len(findings)} finding(s)\n")
        for f in findings:
            print("  - " + f + "\n")
        return 1

    if not boxes:
        print("image scale: no fixed image box found in the shipping sheets — "
              "the register derives from them and came back empty.")
        return 1

    used = sorted({s[2] for s in seen})
    print(f"image scale: {len(seen)} raster source(s) across {len(used)} fixed box rule(s) "
          f"({', '.join('.' + u for u in used)}), every one inside its window.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
