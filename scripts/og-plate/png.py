"""A PNG writer in the standard library, and nothing else.

WHY THIS FILE EXISTS. Every consumer of `og:image` — LinkedIn, Slack, iMessage,
WhatsApp, Discord, Teams — requires a raster. None of them accepts SVG. The
repository has no build dependencies and the house rule is that it stays that
way, so the share plate either gets a rasteriser written here or it does not
get made. `components/signet.html#launch` costed three routes out of that and
this module is the first half of route 1: "zlib is in the standard library, so
writing the PNG is the easy half".

This is the easy half. A PNG is a signature, an IHDR, one or more IDATs and an
IEND; each chunk is a length, a four-byte type, its payload and a CRC-32, and
both `zlib.compress` and `zlib.crc32` are in the standard library. The image
data is the scanlines with a filter byte in front of each.

THE FILTER IS PER-ROW AND CHOSEN, NOT FIXED. A share plate is a vertical wash
with a drawing on it: along a row the colour barely moves, down a column it
moves steadily. Filter 1 (Sub, the pixel to the left) turns the wash's rows
into runs of zeroes and is what makes a 1200 x 630 plate compress to tens of
kilobytes rather than hundreds — which matters, because WhatsApp soft-caps
around 300 KB and silently downgrades anything larger. Rows carrying the
drawing pick up whichever of None/Sub/Up/Average/Paeth gives the smallest sum
of absolute differences, which is the heuristic the PNG specification itself
recommends and costs one pass over five candidates.

COLOUR TYPE 2, EIGHT BITS, NO ALPHA. The plate is opaque by construction — it
stands on the page wash and a transparent share plate renders on whatever
background the consumer happens to have, which for the brand's own ground is
the one thing that must not happen.
"""

import struct
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload +
            struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _filtered(row, prev, bpp):
    """The five candidate filterings of one scanline, best first by SAD.

    Returns the winning `bytes`, filter byte included. `prev` is the
    already-unfiltered previous row, which is what every PNG filter is defined
    against — not the filtered bytes that were written for it.
    """
    n = len(row)
    cands = []

    cands.append((0, bytes(row)))

    sub = bytearray(n)
    for i in range(n):
        sub[i] = (row[i] - (row[i - bpp] if i >= bpp else 0)) & 0xFF
    cands.append((1, bytes(sub)))

    up = bytearray(n)
    for i in range(n):
        up[i] = (row[i] - prev[i]) & 0xFF
    cands.append((2, bytes(up)))

    avg = bytearray(n)
    for i in range(n):
        left = row[i - bpp] if i >= bpp else 0
        avg[i] = (row[i] - ((left + prev[i]) >> 1)) & 0xFF
    cands.append((3, bytes(avg)))

    pae = bytearray(n)
    for i in range(n):
        left = row[i - bpp] if i >= bpp else 0
        upleft = prev[i - bpp] if i >= bpp else 0
        pae[i] = (row[i] - _paeth(left, prev[i], upleft)) & 0xFF
    cands.append((4, bytes(pae)))

    # The specification's own heuristic: treat each filtered byte as a signed
    # value and take the filter whose absolute sum is smallest. It is a
    # proxy for entropy and it is the one every encoder uses.
    def sad(b):
        return sum(v if v < 128 else 256 - v for v in b)

    kind, data = min(cands, key=lambda kv: sad(kv[1]))
    return bytes([kind]) + data


def write_rgb(path, width, height, pixels):
    """Write an 8-bit RGB PNG. `pixels` is one flat bytearray, 3 bytes a pixel."""
    stride = width * 3
    prev = bytes(stride)
    raw = bytearray()
    for y in range(height):
        row = pixels[y * stride:(y + 1) * stride]
        raw += _filtered(row, prev, 3)
        prev = row

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    body = SIGNATURE + _chunk(b"IHDR", ihdr)
    body += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    body += _chunk(b"IEND", b"")

    with open(path, "wb") as fh:
        fh.write(body)
    return len(body)
