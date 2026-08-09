#!/bin/sh
# Every generator, in the one order they work in.
#
# The order is not a preference. build-news.py writes the archive into the
# German pattern page and the titles into the catalogue; build-i18n.py reads
# that page and that catalogue to write the English edition; build-articles.py
# splices each post's text into BOTH editions of blog-artikel.html, so it needs
# the English one to exist first; build-site.py reads everything to write the
# pages that actually ship at the root. Run them the other way round and you
# publish yesterday's archive in English.
#
# CI runs each one's --check rather than this script, so a page that was edited
# instead of generated fails rather than being silently rebuilt.
set -e
cd "$(dirname "$0")/.."
python3 scripts/build-news.py
python3 scripts/build-jobs.py
python3 scripts/build-i18n.py
python3 scripts/build-articles.py
python3 scripts/build-stellen.py
python3 scripts/build-site.py
