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

THE ADDRESS IS IN THE BLOCK TOO, TWICE, AND FOR THE MOVE OFF WIX. `og:url`
and `<link rel="canonical">` both name the page's address on the canonical
host, SITE_ORIGIN again, and both are here for the same reason: two public
copies of this site are live (GitHub Pages, and the Worker that answers the
form), and the domain cutover will make it three for a while — the old Pages
address redirects, but a crawler that already indexed it needs telling where
the page now lives. A canonical link is that telling, on every copy, in the
same commit that moves SITE_ORIGIN. Where the address comes from:

  address()       the page's SHIPPED name, asked of build-site.py's SHIP and
                  FOLDER tables — landing-page.html is "/", beitrag-x.html is
                  blog/x.html, and an English page sits under en/. A pattern's
                  file name is not its address, and this is the one place the
                  difference is resolved for the head.

WHAT IS NOT IN THE BLOCK.

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
    """SITE_ORIGIN from wrangler.toml: the canonical host, without a trailing slash.

    It is GitHub Pages' subdirectory today and becomes https://www.control-f.io
    at the domain cutover — one line in wrangler.toml, and og:image, og:url,
    the canonical link, the sitemap and the redirect stubs all move with it.
    A missing SITE_ORIGIN is a build that stops rather than a card that
    silently points at nothing: see the cutover notes in that file.
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


def _site():
    """build-site.py, loaded by path — its name is not an identifier."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cf_build_site", os.path.join(ROOT, "scripts", "build-site.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_SITE = None


def address(name, edition="de"):
    """The shipped address of a pattern page, relative to the origin.

    `name` is the pattern's file name — landing-page.html, expertise.html,
    beitrag-<slug>.html — and the answer is where build-site.py ships it:
    SHIP for the named pages, FOLDER for the generated families, and the
    English edition under en/. A directory index is named by its directory,
    because that is the address a reader has and the one a crawler should
    keep: "" for the German landing page, "en/" for the English one.

    Asked of build-site.py's tables rather than copied from them, so a page
    moved there moves here without this file changing. The generated page's
    pattern may not exist yet when its head is being written, which is why
    this applies the rules rather than reading ship()'s result.
    """
    global _SITE
    if _SITE is None:
        _SITE = _site()
    key = name if edition == "de" else "en/" + name
    if key in _SITE.SHIP:
        shipped = _SITE.SHIP[key]
    else:
        shipped = key
        for prefix, folder in _SITE.FOLDER:
            if name.startswith(prefix):
                shipped = ("" if edition == "de" else "en/") + folder + name[len(prefix):]
                break
    if shipped.endswith("index.html"):
        shipped = shipped[:-len("index.html")]
    return shipped


def page_url(name, edition="de"):
    return "%s/%s" % (origin(), address(name, edition))


def esc(value):
    """Attribute-safe. The two that matter in a `content="..."` are the quote
    and the ampersand; the generators hand over text that is already entity-
    encoded for the page, so this must not double-encode one."""
    return value.replace('"', "&quot;")


def block(title, desc, seed, edition="de", name=None):
    """The share card for one page, as a list of lines with no indent.

    `name` is the pattern's file name and decides og:url and the canonical
    link through address(). It is required: a card without its address is
    the state this site was in until the domain move was prepared, and no
    caller is allowed back into it by forgetting an argument.
    """
    if name is None:
        raise SystemExit("og_meta.block: the page's pattern name is required — "
                         "og:url and the canonical link are derived from it.")
    own, other = LOCALE[edition]
    url = page_url(name, edition)
    return list(NOTE) + [
        '<link rel="canonical" href="%s">' % url,
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Control-F">',
        '<meta property="og:url" content="%s">' % url,
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
