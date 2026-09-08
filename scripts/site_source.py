"""Read pattern documents as rendered previews, with shared partials and routes.

Used by static checks and the development server. Unknown root URLs stay unknown
so link checks still reject them. Fragments are never treated as full documents.
"""
from functools import lru_cache
import importlib.util
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / 'design-system'
PATTERNS = DS / 'patterns'
PARTIALS = DS / 'partials'
MARKER = '<!-- CF:FOOTER -->'


def is_partial(path):
    return Path(path).resolve().is_relative_to(PARTIALS)


@lru_cache(maxsize=1)
def route_sources():
    spec = importlib.util.spec_from_file_location('site_build_routes', ROOT / 'scripts/build-site.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = {}
    for source, destination in module.ship().items():
        path = PATTERNS / source
        result['/' + destination] = path
        result['/' + destination.removesuffix('.html')] = path
        if destination.endswith('index.html'):
            result['/' + destination[:-len('index.html')]] = path
    return result


def footer_for(path):
    """The same footer and current-section markers for build and preview."""
    path = Path(path)
    edition = 'en/' if path.parent.name == 'en' else ''
    text = (PARTIALS / edition / 'footer.html').read_text(encoding='utf-8')
    name = path.name
    section = ('news' if name.startswith(('beitrag-', 'news-thema')) else
               'karriere' if name.startswith(('stelle-', 'karriere-')) else
               'suche' if name == 'suche-leer.html' else
               'kontakt' if name == 'kontakt-danke.html' else None)
    def mark(m):
        href = m[1]
        target = href.rstrip('/').split('/')[-1]
        current = 'page' if target + '.html' == name else 'true' if target == section else None
        return '<li><a href="' + href + '"' + (f' aria-current="{current}"' if current else '') + '>'
    return re.sub(r'<li><a href="([^"]+)">', mark, text)


def read_source(path):
    path = Path(path).resolve()
    text = path.read_text(encoding='utf-8')
    if MARKER in text:
        if text.count(MARKER) != 1 or not path.is_relative_to(PATTERNS):
            raise ValueError(f'{path}: invalid footer include')
        text = text.replace(MARKER, footer_for(path))
    # Resolve production routes relative to this preview document. The source
    # for each route comes from the builder's own table, never a second list.
    def link(m):
        value = m[3]
        bits = urlsplit(value)
        if bits.netloc:
            return m[0]
        target = route_sources().get(bits.path)
        if target is None:
            return m[0]
        value = os.path.relpath(target, path.parent).replace(os.sep, '/')
        if bits.query: value += '?' + bits.query
        if bits.fragment: value += '#' + bits.fragment
        return m[1] + m[2] + value + m[2]
    return re.sub(r'(\b(?:href|action)=)(["\'])(/[^"\']*)\2', link, text)


from http.server import SimpleHTTPRequestHandler
from io import BytesIO


class PreviewHandler(SimpleHTTPRequestHandler):
    """Serve the same expanded source checked above, including clean routes."""
    def translate_path(self, path):
        target = super().translate_path(path)
        if not Path(target).exists() and Path(target + '.html').is_file():
            return target + '.html'
        return target

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if path.suffix == '.html' and path.is_file() and path.resolve().is_relative_to(PATTERNS):
            data = read_source(path).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            return BytesIO(data)
        return super().send_head()
