#!/usr/bin/env python3
"""The still a reader is handed instead of the loop may not be the worst copy of it.

The hero carries a 12-second H.264 loop and one JPEG standing in for it. That
JPEG is not a placeholder in any sense the reader would recognise:

  - it is what every browser paints before the first frame decodes, so it is
    the landing page's largest paint and usually its LCP element;
  - it is the ONLY artwork a `prefers-reduced-motion` reader is ever shown, by
    the gate check-hero-video.py exists to hold — the loop is not merely hidden
    from them, it is never requested;
  - it is what the pause switch (foundations/motion.html, WCAG 2.2.2) leaves on
    the screen for as long as the reader wants it there.

Three of the site's own audiences see the still and not the loop, and the still
was the least carefully encoded file in the hero.

WHAT WAS MEASURED, on the artwork that shipped 2026-08-03. Decode the loop's
frame 0 and compare the shipped poster against it — the frame it stands for:

    shipped hero-poster.jpg        83,847 bytes   4:2:0   38.26 dB
    frame 0 vs frame 1 of the loop         --       --    42.34 dB

The poster's own error was LARGER than a whole frame of the animation. Handed
that still, the reader is not looking at the moment the video begins on; they
are looking at something further from it than the next frame is.

And it was not a budget: re-cutting the same frame at the same byte count is
better than what shipped, because the bytes were being spent on a 4:2:0 chroma
plane the artwork cannot afford — it is grey planes separated by lime and blue
EDGES, and 4:2:0 keeps one chroma sample per 2 x 2 pixels of exactly those.

    same frame, q76 4:2:0          83,010 bytes   4:2:0   41.98 dB   (+3.7)
    same frame, q85 4:4:4         146,447 bytes   4:4:4   46.37 dB   (+8.1)

What ships now is the second line: 46.37 dB is comfortably inside one frame of
the loop's own motion, so the still and the first painted frame agree, and the
handover from poster to video is not a visible correction. It costs 62,600
bytes on a page that transfers 4.8 MB, and for the reduced-motion reader — the
one who sees nothing else — it is the whole of the artwork budget, against the
3,328,598 bytes of loop the gate spares them.

WHY A SCRIPT. Nothing about a re-compressed poster is visible in a diff, in a
screenshot at review size, or in any check that existed: the page renders, the
image is the right picture at the right dimensions, and check-image-scale.py —
the only other check that opens a raster — reads dimensions and is right to,
because a pixel count is what its own invariant is about. The failure here is
one level down, in how those pixels were quantised, and the first tool that
re-saves this file will default to 4:2:0 at whatever quality it likes and no
number anywhere will move.

WHAT IT CHECKS, on every poster referenced by a <video> under design-system/:

  4:4:4          every component's sampling factors are 1 x 1. A subsampled
                 chroma plane is a decision about coloured edges, and this
                 artwork is coloured edges.
  quantisation   the mean of each quantisation table is not ABOVE the value
                 the file ships at. Larger entries are coarser steps, so this
                 is a ceiling on how much can be thrown away, not a target.
                 The mean rather than the table itself, because two encoders
                 at the same quality write different tables and only the
                 severity is comparable.
  the still      the <img> that stands in when the video is display:none
                 points at the same file as the poster attribute. Two files
                 would be two encodes and one of them would drift.

WHAT IT CANNOT CHECK, and this is the reason the numbers above are recorded in
prose. The invariant that matters is "the poster is frame 0 of the loop", and
verifying it costs an H.264 decoder. Chromium in this CI ships none (see
check-hero-scrim.py, which gave up the same way), so what runs every commit is
the ENCODER SETTINGS the measurement was taken under. To regenerate the file:

    ffmpeg -i design-system/assets/video/hero-abstract-art.mp4 \\
           -vf "select=eq(n\\,0)" -vframes 1 -pix_fmt rgb24 frame0.png
    # Pillow: save(quality=85, subsampling=0, optimize=True, progressive=True)

SCOPE is design-system/ and nothing above it. The root generation carries the
same file — there is one copy of every image in the repository, and
build-site.py rewrites the path and not the asset — so checking it twice would
be checking it twice.

    python3 scripts/check-hero-poster.py       # check, exit 1 on a failure
    python3 scripts/check-hero-poster.py -v    # print every poster's figures
"""

import argparse
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCOPE = ROOT / "design-system"

# The ceiling, per quantisation table index, as the file ships. Luma is table
# 0 and chroma table 1 in every baseline and progressive JPEG this repository
# has; an encoder that writes more tables than that is caught by the loop
# rather than by a number listed here.
QUANT_CEILING = {0: 17.33, 1: 26.03}

# Markers that carry a frame header. SOF0 is baseline, SOF2 progressive, and
# the poster is progressive — the same set check-image-scale.py reads.
SOF = tuple(m for m in range(0xC0, 0xD0) if m not in (0xC4, 0xC8, 0xCC))

VIDEO = re.compile(r"<video\b[^>]*>", re.S)
IMG = re.compile(r"<img\b[^>]*>", re.S)
ATTR = re.compile(r'(\w[\w:-]*)\s*=\s*"([^"]*)"')


def segments(data):
    """Yield (marker, payload) for every JPEG segment, entropy data aside."""
    i = 2
    while i < len(data) - 3:
        if data[i] != 0xFF:
            i += 1
            continue
        mk = data[i + 1]
        if mk in (0xD8, 0xD9) or 0xD0 <= mk <= 0xD7 or mk == 0xFF:
            i += 2
            continue
        size = struct.unpack(">H", data[i + 2:i + 4])[0]
        yield mk, data[i + 4:i + 2 + size]
        if mk == 0xDA:                      # scan — the rest is entropy coded
            return
        i += 2 + size


def jpeg_facts(path):
    """Sampling factors and quantisation table means, without a decoder."""
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        return None
    sampling, tables = [], {}
    for mk, payload in segments(data):
        if mk == 0xDB:                      # DQT, one or more tables
            j = 0
            while j < len(payload):
                pq, tq = payload[j] >> 4, payload[j] & 0x0F
                j += 1
                if pq:                      # 16-bit table
                    vals = struct.unpack(">64H", payload[j:j + 128])
                    j += 128
                else:
                    vals = tuple(payload[j:j + 64])
                    j += 64
                tables[tq] = sum(vals) / 64.0
        elif mk in SOF:
            n = payload[5]
            for c in range(n):
                b = payload[6 + c * 3 + 1]
                sampling.append((b >> 4, b & 0x0F))
    return sampling, tables


def posters():
    """Every (page, poster path, still src) the hero contract produces."""
    out = []
    for page in sorted(SCOPE.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        for tag in VIDEO.finditer(text):
            attrs = dict(ATTR.findall(tag.group(0)))
            if "poster" not in attrs:
                continue                    # check-hero-video.py owns that
            line = text.count("\n", 0, tag.start()) + 1
            after = text[tag.end():tag.end() + 2000]
            still = next((dict(ATTR.findall(m.group(0))).get("src")
                          for m in IMG.finditer(after)), None)
            out.append((page, line, attrs["poster"], still))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    findings, seen = [], []
    for page, line, poster, still in posters():
        rel = page.relative_to(ROOT)
        path = (page.parent / poster).resolve()
        if not path.exists():
            findings.append((rel, line, "poster %s does not exist" % poster))
            continue
        if still != poster:
            findings.append((rel, line,
                             "the still <img> loads %r and the poster attribute "
                             "%r — one file or they drift apart" % (still, poster)))
        facts = jpeg_facts(path)
        if facts is None:
            continue                        # not a JPEG; nothing here applies
        sampling, tables = facts
        if any(f != (1, 1) for f in sampling):
            findings.append((rel, line,
                             "%s is chroma-subsampled %s — the artwork is grey "
                             "planes separated by lime and blue edges, and a "
                             "shared chroma sample is one edge in four"
                             % (poster, sampling)))
        for tq, mean in sorted(tables.items()):
            ceiling = QUANT_CEILING.get(tq)
            if ceiling is None:
                findings.append((rel, line,
                                 "%s carries an unexpected quantisation table %d; "
                                 "add its ceiling to QUANT_CEILING or re-encode"
                                 % (poster, tq)))
            elif mean > ceiling + 0.01:
                findings.append((rel, line,
                                 "%s quantisation table %d averages %.2f, above "
                                 "the %.2f this file ships at — it has been "
                                 "re-saved at a lower quality"
                                 % (poster, tq, mean, ceiling)))
        seen.append((rel, line, poster, path.stat().st_size, sampling, tables))

    if args.verbose:
        for rel, line, poster, size, sampling, tables in seen:
            print("%s:%d %s  %d bytes  sampling %s  tables %s"
                  % (rel, line, poster, size, sampling,
                     {k: round(v, 2) for k, v in sorted(tables.items())}))

    if findings:
        for rel, line, msg in findings:
            print("%s:%d: %s" % (rel, line, msg))
        print("\n%d finding%s." % (len(findings), "" if len(findings) == 1 else "s"))
        return 1
    print("hero posters: %d checked, 4:4:4 and no coarser than they ship."
          % len(seen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
