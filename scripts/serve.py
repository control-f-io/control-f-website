#!/usr/bin/env python3
"""Local development server supporting clean URLs (without .html extension).

Usage:
    python3 scripts/serve.py [port]
    Default port: 8000
"""

import http.server
import socketserver
import os
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        raw_path = urllib.parse.urlsplit(self.path).path
        
        # If someone visits a page with a trailing slash (e.g. /en/news/ or /expertise/),
        # redirect to the canonical clean URL (/en/news or /expertise) without trailing slash,
        # so the browser calculates relative asset paths (../design-system/...) at the correct depth.
        if raw_path.endswith("/") and len(raw_path) > 1 and raw_path != "/en/":
            stripped = raw_path.rstrip("/")
            candidate = os.path.join(ROOT, stripped.lstrip("/") + ".html")
            if os.path.isfile(candidate):
                parts = urllib.parse.urlsplit(self.path)
                new_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, stripped, parts.query, parts.fragment))
                self.send_response(302)
                self.send_header("Location", new_url)
                self.end_headers()
                return

        return super().do_GET()

    def translate_path(self, path):
        path = urllib.parse.urlsplit(path).path
        clean_path = super().translate_path(path)
        
        # Check if clean_path + '.html' exists
        html_candidate = clean_path.rstrip("/\\") + ".html"
        if os.path.isfile(html_candidate):
            return html_candidate
            
        return clean_path

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            raw_path = urllib.parse.urlsplit(self.path).path
            is_en = raw_path.startswith("/en/") or raw_path == "/en"
            custom_404 = ROOT / ("en/404.html" if is_en else "404.html")
            if custom_404.is_file():
                try:
                    content = custom_404.read_bytes()
                    self.send_response(404)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception:
                    pass
        super().send_error(code, message, explain)

if __name__ == "__main__":
    os.chdir(ROOT)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    class ThreadedHTTPServer(http.server.ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    with ThreadedHTTPServer(("", port), CleanURLHandler) as httpd:
        print(f"Serving Control-F at http://localhost:{port}/ (clean URLs enabled, multi-threaded)")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
