#!/usr/bin/env python3
"""Check rendered footers against the shared DE/EN partials and live specimen.

The V2 footer is a build include. Comparing an unexpanded marker to the former
inline footer reported every page as missing its footer. The partial is now the
source of truth; an inline fork, missing include, duplicate footer, broken route
or edition mismatch still fails. Current-page markers are checked separately by
check-a11y.py and check-links.py using the same expanded document.
"""
from pathlib import Path
import re
import sys
from site_source import ROOT, PATTERNS, PARTIALS, read_source

FOOTER = re.compile(r'<footer\b.*?</footer>', re.S)
COMMENT = re.compile(r'<!--.*?-->', re.S)
COMPONENT = ROOT / 'design-system/components/footer.html'


def normalized(text, path):
    text = COMMENT.sub('', text)
    text = re.sub(r'\s+(?:aria-current|id)="[^"]*"', '', text)
    def href(m):
        value = m[2]
        if value.startswith(('#', 'https:', 'mailto:', 'tel:')):
            return m[0]
        target, _, fragment = value.partition('#')
        return m[1] + '="' + str((path.parent / target).resolve()) + ('#'+fragment if fragment else '') + '"'
    text = re.sub(r'\b(href|src)="([^"]*)"', href, text)
    return re.sub(r'>\s+<', '><', re.sub(r'\s+', ' ', text)).strip()


def main():
    findings = []
    pages = sorted(PATTERNS.rglob('*.html')) + [COMPONENT]
    for path in pages:
        text = read_source(path)
        footers = FOOTER.findall(text)
        if len(footers) != 1:
            findings.append(f'{path.relative_to(ROOT)}: expected one rendered footer, got {len(footers)}')
            continue
        partial = PARTIALS / ('en/footer.html' if path.parent.name == 'en' else 'footer.html')
        expected = FOOTER.findall(read_source(partial))[0]
        if normalized(footers[0], path) != normalized(expected, partial):
            findings.append(f'{path.relative_to(ROOT)}: footer differs from {partial.relative_to(ROOT)}')
        if any(scheme in footers[0] for scheme in ('mailto:', 'tel:')):
            findings.append(f'{path.relative_to(ROOT)}: direct contact channel bypasses the contact form')
    if findings:
        print('\n'.join(findings), file=sys.stderr)
        return 1
    print(f'footer parity: {len(pages)} rendered footers match their edition and live component.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
