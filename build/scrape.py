#!/usr/bin/env python3
"""Scrape schoolofcoreai.com pages into structured JSON cache."""

import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Comment

from fees import extract_city_fees, extract_fees

ROOT = Path(__file__).parent.parent
BUILD = ROOT / "build"
DATA_DIR = BUILD / "data"
IMAGES_DIR = ROOT / "site" / "assets" / "images"
BASE_URL = "https://schoolofcoreai.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

SKIP_TAGS = {"script", "style", "noscript", "svg", "iframe"}


def load_manifest():
    with open(BUILD / "pages.json", encoding="utf-8") as f:
        return json.load(f)


def fetch(url: str) -> str:
    full = urljoin(BASE_URL, url)
    print(f"  Fetching {full}")
    resp = requests.get(full, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def clean_soup(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(SKIP_TAGS):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()
    return soup


def text_of(el) -> str:
    if el is None:
        return ""
    return re.sub(r"\s+", " ", el.get_text(separator=" ", strip=True)).strip()


def download_image(src: str, page_id: str) -> str:
    if not src or src.startswith("data:"):
        return src
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    full_url = urljoin(BASE_URL, src)
    parsed = urlparse(full_url)
    ext = Path(parsed.path).suffix or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"):
        ext = ".jpg"
    name_hash = hashlib.md5(full_url.encode()).hexdigest()[:12]
    filename = f"{page_id}-{name_hash}{ext}"
    dest = IMAGES_DIR / filename
    if not dest.exists():
        try:
            r = requests.get(full_url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                dest.write_bytes(r.content)
        except Exception as e:
            print(f"    Image skip: {full_url} ({e})")
            return src
    return f"/assets/images/{filename}"


def rewrite_links(html: str) -> str:
    """Rewrite internal links to local paths."""
    patterns = [
        (r'href="https?://(?:www\.)?schoolofcoreai\.com([^"]*)"', r'href="\1"'),
        (r"href='https?://(?:www\.)?schoolofcoreai\.com([^']*)'", r"href='\1'"),
    ]
    for pat, repl in patterns:
        html = re.sub(pat, repl, html)
    # Normalize trailing slashes for folder-style paths
    html = re.sub(r'href="(/[^"]*[^/])"', r'href="\1/"', html)
    html = re.sub(r"href='(/[^']*[^/])'", r"href='\1/'", html)
    return html


def extract_sections(soup: BeautifulSoup) -> list:
    sections = []
    main = soup.find("main") or soup.find("article") or soup.body
    if not main:
        return sections

    for h2 in main.find_all(["h2", "h3"]):
        heading = text_of(h2)
        if not heading or len(heading) < 3:
            continue
        content_parts = []
        for sib in h2.find_next_siblings():
            if sib.name in ("h2", "h3"):
                break
            if sib.name in SKIP_TAGS:
                continue
            t = text_of(sib)
            if t:
                content_parts.append(t)
            elif sib.name == "ul":
                items = [text_of(li) for li in sib.find_all("li", recursive=False)]
                content_parts.extend([f"• {i}" for i in items if i])
        if content_parts:
            sections.append({"heading": heading, "content": "\n\n".join(content_parts[:8])})
    return sections[:20]


def extract_faqs(soup: BeautifulSoup) -> list:
    faqs = []
    main = soup.find("main") or soup.body
    if not main:
        return faqs
    text = main.get_text()
    # Look for FAQ-like patterns in headings
    for h in main.find_all(["h2", "h3", "h4"]):
        q = text_of(h)
        if "?" in q or q.lower().startswith(("what", "how", "why", "who", "when", "is ", "can ", "do ")):
            answer_parts = []
            for sib in h.find_next_siblings():
                if sib.name in ("h2", "h3", "h4"):
                    break
                t = text_of(sib)
                if t:
                    answer_parts.append(t)
            if answer_parts:
                faqs.append({"question": q, "answer": " ".join(answer_parts)[:800]})
    return faqs[:15]


def extract_lists(soup: BeautifulSoup) -> list:
    lists = []
    main = soup.find("main") or soup.body
    if not main:
        return lists
    for ul in main.find_all("ul")[:10]:
        items = [text_of(li) for li in ul.find_all("li", recursive=False)]
        items = [i for i in items if i and len(i) > 5]
        if len(items) >= 2:
            lists.append(items[:12])
    return lists


def extract_images(soup: BeautifulSoup, page_id: str) -> list:
    images = []
    for img in soup.find_all("img")[:15]:
        src = img.get("src") or img.get("data-src") or ""
        if not src or "facebook.com" in src or "pixel" in src:
            continue
        alt = img.get("alt", "")
        local = download_image(src, page_id)
        images.append({"src": local, "alt": alt, "width": img.get("width"), "height": img.get("height")})
    return images


def extract_page(page: dict, html: str) -> dict:
    soup = clean_soup(html)
    title_tag = soup.find("title")
    title = text_of(title_tag) if title_tag else page["id"]
    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = meta_desc.get("content", "") if meta_desc else ""

    h1 = soup.find("h1")
    hero_title = text_of(h1) if h1 else title.split("|")[0].strip()

    # Hero subtitle: first substantial paragraph after h1
    hero_sub = ""
    if h1:
        for sib in h1.find_next_siblings():
            if sib.name == "p":
                hero_sub = text_of(sib)
                if len(hero_sub) > 30:
                    break

    sections = extract_sections(soup)
    faqs = extract_faqs(soup)
    lists = extract_lists(soup)
    images = extract_images(soup, page["id"])

    # Raw main content as simplified HTML for content pages
    main = soup.find("main") or soup.find("article")
    raw_html = ""
    full_html = ""
    if main:
        full_html = str(main)
        full_html = rewrite_links(full_html)
        full_html = re.sub(r'\s(on\w+)="[^"]*"', "", full_html)
        raw_html = full_html[:50000] if full_html else ""

    scrape_data = {
        "id": page["id"],
        "source": page["source"],
        "output": page["output"],
        "type": page["type"],
        "nav": page.get("nav", ""),
        "title": title,
        "description": description,
        "hero_title": hero_title,
        "hero_sub": hero_sub,
        "sections": sections,
        "faqs": faqs,
        "lists": lists,
        "images": images,
        "raw_html": raw_html,
    }

    if page["type"] == "program" and full_html:
        scrape_data["fees"] = extract_fees({**scrape_data, "_full_html": full_html})
    elif page["id"].startswith("city-") and full_html:
        scrape_data["fees"] = extract_city_fees({**scrape_data, "_full_html": full_html})

    return scrape_data


def scrape_all(force: bool = False, only_ids: set[str] | None = None):
    manifest = load_manifest()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    ok, skip, fail = 0, 0, 0
    for page in manifest["pages"]:
        if only_ids and page["id"] not in only_ids:
            continue
        out_file = DATA_DIR / f"{page['id']}.json"
        if out_file.exists() and not force:
            print(f"  Cached: {page['id']}")
            skip += 1
            continue
        try:
            html = fetch(page["source"])
            data = extract_page(page, html)
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            ok += 1
            time.sleep(1)
        except Exception as e:
            print(f"  FAIL {page['id']}: {e}")
            fail += 1

    print(f"\nDone: {ok} scraped, {skip} cached, {fail} failed")


if __name__ == "__main__":
    import sys

    force = "--force" in sys.argv
    only_ids = None
    for arg in sys.argv[1:]:
        if arg.startswith("--ids="):
            only_ids = {x.strip() for x in arg.split("=", 1)[1].split(",") if x.strip()}
    scrape_all(force=force, only_ids=only_ids)
