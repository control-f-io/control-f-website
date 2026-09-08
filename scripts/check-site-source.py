#!/usr/bin/env python3
"""Check footer expansion and production-route parity in the source preview.

These are behavioral regressions for the shared renderer: partials must become
complete pages, known routes must resolve, and unknown or external links must
remain available to link validation instead of being silently repaired.
"""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.request import urlopen

import site_source as source


class SourcePreviewTests(unittest.TestCase):
    def test_routes_follow_the_shipping_table(self):
        routes = source.route_sources()
        self.assertEqual(routes['/'], source.PATTERNS / 'landing-page.html')
        self.assertEqual(routes['/en/'], source.PATTERNS / 'en/landing-page.html')
        self.assertEqual(routes['/expertise'], routes['/expertise.html'])
        for route, target in routes.items():
            self.assertTrue(target.is_file(), (route, target))
        self.assertNotIn('/this-route-does-not-exist', routes)

    def test_footer_edition_and_current_section(self):
        for edition in ('', 'en/'):
            footer = source.footer_for(source.PATTERNS / edition / 'news.html')
            self.assertIn(f'href="/{edition}news" aria-current="page"', footer)
            child = source.footer_for(source.PATTERNS / edition / 'beitrag-example.html')
            self.assertIn(f'href="/{edition}news" aria-current="true"', child)
        self.assertNotEqual(source.footer_for(source.PATTERNS / 'news.html'),
                            source.footer_for(source.PATTERNS / 'en/news.html'))

    def test_includes_and_links_without_masking_bad_urls(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            page = root / 'news.html'
            page.write_text(source.MARKER + '\n<a href="/expertise?from=test#felder">Known</a>'
                            '\n<a href="/this-route-does-not-exist">Missing</a>'
                            '\n<a href="//example.org/expertise">External</a>')
            with patch.object(source, 'PATTERNS', root):
                result = source.read_source(page)
                self.assertNotIn(source.MARKER, result)
                self.assertEqual(result.count('<footer '), 1)
                self.assertIn('expertise.html?from=test#felder', result)
                self.assertIn('href="/this-route-does-not-exist"', result)
                self.assertIn('href="//example.org/expertise"', result)
                page.write_text(source.MARKER * 2)
                with self.assertRaises(ValueError):
                    source.read_source(page)
            page.write_text(source.MARKER)
            with self.assertRaises(ValueError):
                source.read_source(page)

    def test_pattern_previews_have_one_footer(self):
        for page in source.PATTERNS.rglob('*.html'):
            rendered = source.read_source(page)
            self.assertEqual(rendered.count('<footer '), 1, page)
            self.assertNotIn(source.MARKER, rendered, page)
        self.assertTrue(source.is_partial(source.PARTIALS / 'footer.html'))
        self.assertFalse(source.is_partial(source.PATTERNS / 'news.html'))

    def test_http_preview_expands_includes_on_clean_routes(self):
        class Quiet(source.PreviewHandler):
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(source.ROOT)))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for edition in ('', 'en/'):
                path = f'design-system/patterns/{edition}landing-page'
                with urlopen(f'http://127.0.0.1:{server.server_port}/{path}') as response:
                    text = response.read().decode()
                self.assertEqual(text, source.read_source(source.ROOT / (path + '.html')))
                self.assertEqual(text.count('<footer '), 1)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
