#!/usr/bin/env python3
"""Verify all internal links in generated static site resolve to existing files."""

import re
from pathlib import Path
from urllib.parse import urlparse

SITE = Path(__file__).parent.parent / "site"
HREF_RE = re.compile(r'href="([^"]+)"')


def is_internal(href: str) -> bool:
    if not href or href.startswith(("#", "mailto:", "tel:", "https://wa.me", "http://", "https://")):
        return False
    return True


def resolve_link(source: Path, href: str) -> Path | None:
    path = urlparse(href).path
    if path.startswith("/"):
        target = SITE / path.lstrip("/")
    else:
        target = (source.parent / path).resolve()
    if target.is_dir():
        target = target / "index.html"
    return target


def audit():
    broken = []
    noncanonical = []
    checked = 0
    html_files = [
        path
        for path in SITE.rglob("*.html")
        if "experiments" not in path.relative_to(SITE).parts
    ]

    for html_file in html_files:
        content = html_file.read_text(encoding="utf-8", errors="ignore")
        for href in HREF_RE.findall(content):
            if not is_internal(href):
                continue
            checked += 1
            parsed = urlparse(href)
            if parsed.path.endswith("index.html"):
                noncanonical.append((str(html_file.relative_to(SITE)), href))
            target = resolve_link(html_file, href)
            if target is None or not target.exists():
                broken.append((str(html_file.relative_to(SITE)), href, str(target)))

    print(f"Checked {checked} internal links across {len(html_files)} pages")
    if broken:
        print(f"BROKEN: {len(broken)}")
        for src, href, target in broken[:30]:
            print(f"  {src} -> {href} (expected {target})")
        return 1
    if noncanonical:
        print(f"NONCANONICAL: {len(noncanonical)} internal index.html links")
        for src, href in noncanonical[:30]:
            print(f"  {src} -> {href}")
        return 1
    print("All internal links OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(audit())
