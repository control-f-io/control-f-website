"""The share card's markup, written once and read by everything that emits it.

WHO EMITS IT. Three places, and there is no fourth:

  the pattern pages   thirteen of them carry the block in their <head> as
                      authored markup, because that is what a pattern page is
  build-news.py       the topic pages, whose title and description it writes
  build-articles.py   the reading page of every post, in both editions

A block written out by hand in three places is three places to forget a field.
So the block is written HERE, the two generators call it, and
scripts/check-open-graph.py re-derives what every authored page should say and
compares it line for line — which makes the authored copies provably the same
markup as the generated ones rather than merely similar to them.

THE ORIGIN IS READ, NOT TYPED. `og:image` has to be absolute: LinkedIn and
several other consumers do not resolve a relative one, and a share plate that
does not load is a link with no card at all. The one place this repository
already records where the site lives is `SITE_ORIGIN` in wrangler.toml —
scripts/stage-site.py reads it for the same reason — so it is read from there
and the cutover moves one line rather than fourteen files.

WHAT IS NOT IN THE BLOCK.

  og:url          Two public copies of this site are live while the domain move
                  is pending. An og:url names ONE of them and would name it on
                  both, and every consumer falls back to the address it
                  actually fetched — which is the right answer on either copy.
                  This is the one field the cutover unblocks.
  twitter:title   X reads Open Graph as its fallback for every field except the
  twitter:image   card type, so repeating them would be the same three strings
  twitter:*       maintained twice. `twitter:card` alone is deliberate.
  og:video        There is a hero video and it is decoration, not the subject
                  of any page.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRANGLER = os.path.join(ROOT, "wrangler.toml")

# The plates, and where they are served from once design-system/ ships whole.
PLATE_DIR = "design-system/assets/og"
WIDTH, HEIGHT = 1200, 630

# One sentence for every plate, because every plate is the same drawing with a
# different arrangement in it. It describes what the picture IS — a reader who
# cannot see it is owed that, and is not owed the seed.
ALT = {
    "de": ("Control-F: das Signet dieser Seite — ein isometrisches Objekt aus "
           "neun Feldern, eine Fläche im Lime-Verlauf."),
    "en": ("Control-F: this page's signet — an isometric object of nine plots, "
           "one face carrying the lime ramp."),
}

LOCALE = {"de": ("de_DE", "en_GB"), "en": ("en_GB", "de_DE")}

NOTE = (
    "<!-- Open Graph — the share plate for this route. → foundations/share.html,",
    "     and landing-page.html for why each of these lines is here. -->",
)

CARD_NOTE = (
    "<!-- X falls back to Open Graph for every field but this one, which is why it is",
    "     the only twitter:* tag here. Without it a large embed degrades to an",
    "     80 x 80 thumbnail on Discord and to the small card on X. -->",
)


def origin(path=WRANGLER):
    """SITE_ORIGIN from wrangler.toml.

    Absent, it means the cutover has happened and this deployment IS the site —
    at which point og:image can be relative to the origin, and og:url can
    finally be written. Until somebody has decided what that domain is, a
    missing SITE_ORIGIN is a build that stops rather than a card that silently
    points at nothing.
    """
    src = open(path, "r", encoding="utf-8").read()
    m = re.search(r'^SITE_ORIGIN = "([^"]+)"', src, re.M)
    if not m:
        raise SystemExit(
            "og_meta: SITE_ORIGIN is gone from wrangler.toml, so nothing here "
            "knows what to make og:image absolute against. See the cutover "
            "notes in that file and in design-system/foundations/share.html.")
    return m.group(1).rstrip("/")


def image_url(seed):
    return "%s/%s/%s.png" % (origin(), PLATE_DIR, seed)


def esc(value):
    """Attribute-safe. The two that matter in a `content="..."` are the quote
    and the ampersand; the generators hand over text that is already entity-
    encoded for the page, so this must not double-encode one."""
    return value.replace('"', "&quot;")


def block(title, desc, seed, edition="de"):
    """The share card for one page, as a list of lines with no indent."""
    own, other = LOCALE[edition]
    return list(NOTE) + [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Control-F">',
        '<meta property="og:locale" content="%s">' % own,
        '<meta property="og:locale:alternate" content="%s">' % other,
        '<meta property="og:title" content="%s">' % esc(title),
        '<meta property="og:description" content="%s">' % esc(desc),
        '<meta property="og:image" content="%s">' % image_url(seed),
        '<meta property="og:image:type" content="image/png">',
        '<meta property="og:image:width" content="%d">' % WIDTH,
        '<meta property="og:image:height" content="%d">' % HEIGHT,
        '<meta property="og:image:alt" content="%s">' % esc(ALT[edition]),
    ] + list(CARD_NOTE) + [
        '<meta name="twitter:card" content="summary_large_image">',
    ]
