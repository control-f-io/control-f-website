#!/usr/bin/env python3
"""One-time migration: replace all cf-footer--v2 blocks in German + English patterns
with <!-- CF:FOOTER --> and update build-site.py to inject design-system/partials/footer.html.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "design-system" / "patterns"

PLACEHOLDER = "<!-- CF:FOOTER -->"

# Matches <!-- Footer --> comment (optional), then <footer ... id="abschluss"...>...</footer>
# Anchored on cf-footer--v2 so we only touch the new footer, not v1 or detached.
FOOTER_RE = re.compile(
    r'(?:[ \t]*<!-- (?:Footer|id="abschluss"[^-]*) -->\n)?'
    r'<footer class="cf-footer cf-footer--v2"[^>]*>.*?</footer>\n?',
    re.DOTALL
)

def patch(path):
    text = path.read_text(encoding="utf-8")
    new_text, count = FOOTER_RE.subn(PLACEHOLDER + "\n", text)
    if count == 0:
        return False
    path.write_text(new_text, encoding="utf-8")
    print(f"  patched ({count}x): {path.relative_to(ROOT)}")
    return True

def main():
    total = 0
    print("Patching German patterns...")
    for p in sorted(PATTERNS.glob("*.html")):
        if patch(p):
            total += 1

    print("\nPatching English patterns...")
    for p in sorted((PATTERNS / "en").glob("*.html")):
        if patch(p):
            total += 1

    print(f"\nDone — {total} files patched.")

if __name__ == "__main__":
    main()
