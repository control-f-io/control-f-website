#!/usr/bin/env python3
"""Keep illustration ink slim without changing logos, UI or draw-on geometry.

Check the shared .7 CSS px token, overrides on semantic illustration rules,
inline shape styles that outrank those rules, and both generated SVG families.
Presentation attributes in designer exports are allowed: shape-level CSS
intentionally adapts their inherited weights. Normalized paths, gradient light
strokes, and the map's forced-colour data emphasis retain separate measures.

stdlib only. --self-test also proves representative thick overrides are caught.
"""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / 'design-system'
TOKEN = '--illustration-stroke'
WEIGHT = .7
SHAPES = {'path', 'line', 'circle', 'ellipse', 'rect', 'polygon', 'polyline'}
ROOTS = {'cf-iso', 'cf-illustration', 'cf-plot__draw', 'cf-line__draw',
         'cf-line__sample', 'cf-pie__ink', 'cf-arrive__object', 'lp-flow', 'sp-field'}
EXEMPT = {'cf-iso__trace', 'cf-illustration__trace', 'cf-illustration__light', 'lp-flow__light',
          'lp-flow__leaf', 'map__land--market'}
DIRECT = {'cf-line__trace', 'cf-pie__contour', 'cf-pie__cut', 'cf-arrive__object',
          'cf-construct__work', 'lp-flow__seg', 'lp-flow__orb',
          'cf-stmt-sensor__bead', 'map__land'}


def number(value):
    match = re.fullmatch(r'\s*(\d*\.?\d+)\s*(?:px)?\s*', value or '')
    return float(match[1]) if match else None


def allowed(value):
    return value.strip() == 'var(%s)' % TOKEN or number(value) == WEIGHT


def css_rules(source):
    clean = re.sub(r'/\*.*?\*/', '', source, flags=re.S)
    return re.finditer(r'([^{}]+)\{([^{}]*)\}', clean)


def protected(selector):
    # Classes in :not() exclude shapes; they do not turn the whole rule into
    # an exception. :is() is deliberately retained to cover every branch.
    positive = re.sub(r':not\([^)]*\)', '', selector)
    classes = set(re.findall(r'\.([\w-]+)', positive))
    return not classes & EXEMPT and any(
        c in DIRECT or c in {'cf-iso', 'cf-illustration'} or
        c.startswith(('cf-iso__', 'cf-illustration__', 'cf-plot__'))
        for c in classes)


def css_findings(source):
    findings = []
    for rule in css_rules(source):
        value = re.search(r'(?<![\w-])stroke-width\s*:\s*([^;}]+)', rule[2])
        if value and protected(rule[1]) and not allowed(value[1]):
            findings.append('%s uses stroke-width: %s' %
                            (' '.join(rule[1].split()), value[1].strip()))
    return findings


class InlineContours(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.active = False
        self.findings = []
        self.figures = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set(a.get('class', '').split())
        if tag == 'svg':
            if self.depth == 0:
                self.active = bool(classes & ROOTS)
                self.figures += self.active
            self.depth += 1
        if not self.active or tag not in SHAPES:
            return
        if classes & EXEMPT or 'pathlength' in a:
            return
        value = re.search(r'(?<![\w-])stroke-width\s*:\s*([^;]+)', a.get('style', ''))
        if value and not allowed(value[1]):
            self.findings.append('line %d <%s> has an inline contour override: %s' %
                                 (self.getpos()[0], tag, value[1]))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'svg':
            self.depth = max(0, self.depth - 1)
            if not self.depth:
                self.active = False


def generated_findings(path):
    root = ET.parse(path).getroot()
    styles = '\n'.join(e.text or '' for e in root.iter() if e.tag.endswith('}style'))
    widths = re.findall(r'stroke-width\s*:\s*([^;}]+)', styles)
    local = any(allowed(w) or re.fullmatch(
        r'var\(--illustration-stroke,\s*\.7px\)', w.strip()) for w in widths)
    scenes = [e for e in root.iter() if 'cf-iso__scene' in e.get('class', '').split()]
    if not scenes:
        return ['missing cf-iso__scene']
    if not local and any(number(e.get('stroke-width')) != WEIGHT for e in scenes):
        return ['scene needs a .7 stroke or equivalent embedded contour rule']
    if 'news-objects' in path.parts and (not local or 'non-scaling-stroke' not in styles):
        return ['standalone news SVG must carry its .7 fallback and non-scaling stroke']
    return []


def self_test():
    assert css_findings('.cf-iso path { stroke-width: 2px; }')
    assert css_findings('.cf-iso__form { stroke-width: 1; }')
    assert not css_findings('.cf-iso__trace { stroke-width: var(--trace-weight); }')
    assert not css_findings('.cf-icon { stroke-width: 2px; }')
    probe = InlineContours()
    probe.feed('<svg class="cf-iso"><path style="stroke-width:2px"/></svg>')
    assert probe.findings
    probe = InlineContours()
    probe.feed('<svg class="cf-iso"><path class="cf-iso__trace" '
               'pathLength="1" style="stroke-width:2px"/></svg>')
    assert not probe.findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    findings = []
    tokens = (DESIGN / 'assets/css/tokens.css').read_text()
    value = re.search(re.escape(TOKEN) + r'\s*:\s*([^;]+)', tokens)
    if not value or number(value[1]) != WEIGHT:
        findings.append('tokens.css must define --illustration-stroke: .7px')
    css = DESIGN / 'assets/css'
    components = (css / 'components.css').read_text()
    contour_rules = [m for m in css_rules(components)
                     if '.cf-iso :is(' in m[1] and 'stroke-width' in m[2]]
    if not contour_rules or not all('var(%s)' % TOKEN in m[2] and
                                   'non-scaling-stroke' in m[2] for m in contour_rules):
        findings.append('components.css must apply the token and non-scaling stroke to isometric shapes')
    for path in css.glob('*.css'):
        findings.extend('%s: %s' % (path.relative_to(ROOT), f)
                        for f in css_findings(path.read_text()))
    figures = 0
    for path in DESIGN.rglob('*.html'):
        if 'source' in path.parts:
            continue
        source = path.read_text()
        probe = InlineContours()
        probe.feed(source)
        figures += probe.figures
        findings.extend('%s: %s' % (path.relative_to(ROOT), f) for f in probe.findings)
        for style in re.findall(r'<style[^>]*>(.*?)</style>', source, re.S):
            findings.extend('%s: %s' % (path.relative_to(ROOT), f) for f in css_findings(style))
    assets = list((ROOT / 'scripts/expertise-objects').glob('*.svg'))
    assets += list((ROOT / 'scripts/news-objects/svg').glob('*.svg'))
    for path in assets:
        findings.extend('%s: %s' % (path.relative_to(ROOT), f) for f in generated_findings(path))
    raster = (ROOT / 'scripts/news-objects/objects.py').read_text()
    export = re.search(r'^EXPORT_STROKE\s*=\s*([\d.]+)', raster, re.M)
    if not export or abs(float(export[1]) - WEIGHT * 1.4) > 1e-9:
        findings.append('news raster export must retain 1.4 scale compensation × .7 contour')
    if findings:
        print('\n'.join(findings))
        return 1
    print('illustration contours: .7 CSS px; %d SVG figures, %d generated assets; '
          'no thick contour overrides.' % (figures, len(assets)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
