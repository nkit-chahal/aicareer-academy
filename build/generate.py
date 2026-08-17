#!/usr/bin/env python3
"""Generate static HTML site from scraped JSON and Jinja2 templates."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from jinja2 import Environment, FileSystemLoader, select_autoescape

from curriculum import resolve_curriculum
from fee_display import prepare_fee_display
from fees import extract_city_fees, extract_fees
from salaries import extract_salaries, filter_sections, format_section_html
from seo import (
    BRAND,
    CONTACT_NAME,
    EMAIL,
    GEO_LAT,
    GEO_LNG,
    MAPS_EMBED,
    MAPS_PLACE,
    PHONE_DISPLAY,
    PHONE_E164,
    SITE_ORIGIN,
    WA_ME,
    apply_overrides,
    canonical_url,
    is_noindex,
    json_ld,
    meta_description,
    og_type,
    sanitize_text,
    sanitize_tree,
    write_404,
    write_robots_and_sitemap,
    _format_title as format_seo_title,
)

ROOT = Path(__file__).parent.parent
BUILD = ROOT / "build"
DATA_DIR = BUILD / "data"
SITE = ROOT / "site"
TEMPLATES = BUILD / "templates"

# Studio wordmarks — not official logos.
EMPLOYERS = [
    ("amazon", "Amazon"),
    ("microsoft", "Microsoft"),
    ("google", "Google"),
    ("flipkart", "Flipkart"),
    ("infosys", "Infosys"),
    ("tcs", "TCS"),
    ("accenture", "Accenture"),
    ("deloitte", "Deloitte"),
    ("wipro", "Wipro"),
    ("ibm", "IBM"),
    ("nvidia", "NVIDIA"),
    ("salesforce", "Salesforce"),
    ("swiggy", "Swiggy"),
    ("razorpay", "Razorpay"),
    ("zoho", "Zoho"),
    ("paytm", "Paytm"),
]

def _initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


MENTORS = [
    {"name": "Ankit", "role": "Lead AI Engineer", "tags": ["Generative AI", "Agentic AI", "LLM", "VLM", "AIOPS"], "focus": "Supports learners across analytics, structured problem-solving, and applied ML foundations."},
    {"name": "Prerna", "role": "Sales Head", "tags": ["Career calls", "Program fit", "Enrolment"], "focus": "First desk for a 15-minute call — which sequence fits, or that none does yet."},
    {"name": "Praveen", "role": "Applied AI Engineer", "tags": ["Generative AI", "Deep Learning", "Python", "ML Systems", "Agentic AI"], "focus": "Helps learners connect modern AI concepts with real engineering execution."},
    {"name": "Aayush", "role": "Senior AI Engineer", "tags": ["Machine Learning", "Computer Vision", "LLMOPS", "AIOPS", "GenAI"], "focus": "Focuses on helping learners build strong model-building intuition and debugging skills."},
    {"name": "Rahul Bhardwaj", "role": "ML Engineer", "tags": ["MLOps", "Data Engineering", "Python", "Cloud"], "focus": "Brings production ML deployment experience to mentor data pipeline and serving projects."},
    {"name": "Vaibhav Sharma", "role": "GenAI Specialist", "tags": ["RAG", "LLM Fine-tuning", "LangChain", "Agents"], "focus": "Specializes in RAG architecture and agentic workflow design for real-world applications."},
    {"name": "Deepak Rohilla", "role": "Senior Frontend Engineer", "tags": ["HTML", "CSS", "JavaScript", "React", "Accessibility"], "focus": "Mentors the three-month Frontend program — UI that ships, not a tutorial dump."},
]
for _m in MENTORS:
    _m["initials"] = _initials(_m["name"])

TEMPLATE_MAP = {
    "home": "home.html",
    "courses-list": "courses-list.html",
    "program": "program-detail.html",
    "content": "content-page.html",
    "comparison": "comparison.html",
    "blog": "blog-post.html",
    "mentors": "mentors.html",
    "register": "register.html",
}

NAV_MAP = {
    "home": "home",
    "courses": "courses",
    "hire": "hire",
    "contact": "contact",
    "about": "about",
    "enterprise": "enterprise",
    "mentors": "mentors",
    "legal": "",
    "register": "register",
}


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute_base(output_path: str) -> str:
    """Return relative path prefix to site root."""
    parts = Path(output_path).parts
    depth = len(parts) - 1  # exclude filename
    return "../" * depth if depth > 0 else ""


def load_programs():
    return load_json(BUILD / "programs.json")


def find_program_by_source(programs, source: str):
    slug = source.strip("/").split("/")[-1]
    for p in programs:
        if p["slug"] == slug:
            return p
    return None


def card_fee_label(fees: dict | None) -> str | None:
    """Short fee chip for course cards. None when we have no real amount."""
    if not fees or not fees.get("display"):
        return None
    d = fees["display"]
    mode = d.get("mode")
    if mode == "single":
        return f"{d['current']['symbol']}{d['current']['value']}"
    if mode == "discount":
        return f"{d['current']['symbol']}{d['current']['value']}"
    if mode == "dual_tier":
        return f"{d['tier_a']['symbol']}{d['tier_a']['value']}"
    if mode == "dual_plan":
        return f"{d['upfront']['symbol']}{d['upfront']['value']}"
    if mode == "multi" and d.get("amounts"):
        a = d["amounts"][0]
        return f"{a['symbol']}{a['value']}"
    return None


def enrich_programs_with_fees(programs: list, manifest: dict) -> list:
    id_by_slug = {}
    for page in manifest["pages"]:
        if page["type"] == "program":
            slug = page["source"].strip("/").split("/")[-1]
            id_by_slug[slug] = page["id"]
    enriched = []
    for p in programs:
        item = dict(p)
        pid = id_by_slug.get(p["slug"])
        if pid:
            data_file = DATA_DIR / f"{pid}.json"
            if data_file.exists():
                data = load_json(data_file)
                raw = data.get("fees") or extract_fees(data)
                prepared = prepare_fee_display(raw) if raw else None
                label = card_fee_label(prepared)
                if label:
                    item["fee_label"] = label
        enriched.append(item)
    return enriched


def resolve_active_nav(page: dict) -> str:
    mapped = NAV_MAP.get(page.get("nav", ""), "")
    if mapped:
        return mapped
    out = page.get("output", "")
    if out.startswith("comparisons") or out.startswith("roadmaps") or out.startswith("blogs"):
        return "explore"
    return mapped


def build_jump_nav(fees, salaries, data: dict, curriculum=None) -> list:
    items = []
    if fees:
        items.append({"id": "fees", "label": "Fees"})
    if curriculum or data.get("lists"):
        items.append({"id": "curriculum", "label": "Curriculum"})
    if salaries:
        items.append({"id": "salary", "label": "Salary"})
    if data.get("faqs"):
        items.append({"id": "faq", "label": "FAQ"})
    return items


def resolve_fees(data: dict, page: dict):
    """Use scrape-time fees when present; otherwise extract from cached fields."""
    if data.get("fees"):
        return data["fees"]
    if page["type"] == "program":
        return extract_fees(data)
    if page["id"].startswith("city-"):
        return extract_city_fees(data)
    return None


def resolve_salaries(data: dict, page: dict):
    """Extract structured salary tables from raw HTML or flattened section text."""
    if page["type"] != "program":
        return None
    if data.get("skip_extracted_salaries"):
        return None
    if data.get("salaries"):
        return data["salaries"]
    return extract_salaries(data)


def prepare_sections(data: dict, salaries) -> list:
    """Return sections with salary blobs converted to HTML where possible."""
    sections = filter_sections(data.get("sections", []), salaries)
    prepared = []
    for section in sections:
        item = dict(section)
        if not salaries:
            formatted = format_section_html(item.get("content", ""))
            if formatted:
                item["content_html"] = formatted
                item["content"] = ""
        prepared.append(item)
    return prepared


def compress_offer_images(src_img: Path, img_dir: Path) -> None:
    """Resize offer PNGs to display size and emit WebP (cuts ~8MB homepage payload)."""
    try:
        from PIL import Image
    except ImportError:
        print("  Skip WebP (Pillow not installed)")
        return
    names = (
        "offer-live.png",
        "offer-whatsapp.png",
        "offer-curriculum.png",
        "offer-projects.png",
        "offer-career.png",
    )
    img_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        src = src_img / name
        if not src.exists():
            src = img_dir / name
        if not src.exists():
            continue
        dest = img_dir / (src.stem + ".webp")
        im = Image.open(src)
        if im.mode in ("RGBA", "P"):
            rgba = im.convert("RGBA")
            bg = Image.new("RGB", rgba.size, (247, 241, 228))
            bg.paste(rgba, mask=rgba.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
        im.thumbnail((800, 600), Image.Resampling.LANCZOS)
        im.save(dest, "WEBP", quality=78, method=6)
        png_out = img_dir / name
        if png_out.exists() and png_out.stat().st_size > 200_000:
            png_out.unlink()
        print(f"  WebP: {dest.name} ({dest.stat().st_size // 1024} KiB)")


def setup_assets():
    assets = SITE / "assets"
    css_dir = assets / "css"
    js_dir = assets / "js"
    css_dir.mkdir(parents=True, exist_ok=True)
    js_dir.mkdir(parents=True, exist_ok=True)

    src_css = ROOT / "styles.css"
    css_text = src_css.read_text(encoding="utf-8") if src_css.exists() else ""
    v5_css = ROOT / "site" / "experiments" / "v5" / "styles.css"
    if v5_css.exists():
        raw = v5_css.read_text(encoding="utf-8")
        cut = raw.find(".ticker {")
        if cut >= 0:
            css_text += "\n\n/* === v5 chrome + home story === */\n" + raw[cut:]
    css_text += V5_INNER_CSS
    (css_dir / "base.css").write_text(css_text, encoding="utf-8")

    # Write program.css and content.css
    (css_dir / "program.css").write_text(PROGRAM_CSS, encoding="utf-8")
    (css_dir / "content.css").write_text(CONTENT_CSS, encoding="utf-8")

    # Write JS files
    (js_dir / "nav.js").write_text(NAV_JS, encoding="utf-8")
    (js_dir / "courses.js").write_text(_courses_js(), encoding="utf-8")
    (js_dir / "register.js").write_text(REGISTER_JS, encoding="utf-8")
    (js_dir / "home.js").write_text(HOME_JS, encoding="utf-8")
    static = BUILD / "static"
    if (static / "studio.css").exists():
        shutil.copy(static / "studio.css", css_dir / "studio.css")
    if (static / "studio.js").exists():
        shutil.copy(static / "studio.js", js_dir / "studio.js")
    if (static / "grid.js").exists():
        shutil.copy(static / "grid.js", js_dir / "grid.js")

    (assets / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    img_dir = assets / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    people_src = BUILD / "assets" / "people"
    people_dst = img_dir / "people"
    if people_src.exists():
        people_dst.mkdir(parents=True, exist_ok=True)
        for img in people_src.iterdir():
            if img.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                shutil.copy(img, people_dst / img.name)
    src_img = BUILD / "assets"
    cursor_assets = Path(r"C:\Users\Pc\.cursor\projects\d-personal-app\assets")
    src_img.mkdir(parents=True, exist_ok=True)
    for extra in ("og-search.png", "logo-aca.png", "og-programs.png", "og-gurugram.png"):
        if (cursor_assets / extra).exists():
            shutil.copy(cursor_assets / extra, src_img / extra)
    if (src_img / "og-search.png").exists():
        shutil.copy(src_img / "og-search.png", src_img / "og.png")
    for name in (
        "og.png",
        "home-figure.png",
        "poster-data-analytics.png",
        "poster-data-science.png",
        "poster-genai-devs.png",
        "poster-genai-spec.png",
        "poster-mlops.png",
        "poster-llmops.png",
        "poster-java.png",
        "poster-devops.png",
        "poster-frontend.png",
        "offer-live.png",
        "offer-whatsapp.png",
        "offer-curriculum.png",
        "offer-projects.png",
        "offer-career.png",
        "logo-aca.png",
        "og-programs.png",
        "og-gurugram.png",
        "og-search.png",
    ):
        src = src_img / name
        if not src.exists() and (cursor_assets / name).exists():
            src_img.mkdir(parents=True, exist_ok=True)
            shutil.copy(cursor_assets / name, src_img / name)
            src = src_img / name
        if not src.exists() and name == "og.png":
            src = cursor_assets / "og.png"
        if src.exists():
            shutil.copy(src, img_dir / name)
            if name == "og.png":
                shutil.copy(src, assets / "og.png")
                shutil.copy(src, BUILD / "og.png")
    write_employer_stamps(img_dir / "stamps")
    compress_offer_images(src_img, img_dir)
    for verify in src_img.glob("google*.html"):
        shutil.copy(verify, SITE / verify.name)


def generate():
    manifest = load_json(BUILD / "pages.json")
    programs = load_programs()
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    setup_assets()
    generated = 0
    skipped = 0

    for page in manifest["pages"]:
        data_file = DATA_DIR / f"{page['id']}.json"
        if not data_file.exists() and page["type"] not in ("mentors", "home"):
            print(f"  Skip (no data): {page['id']}")
            skipped += 1
            continue

        data = load_json(data_file) if data_file.exists() else {}
        data = apply_overrides(page, data)
        data = sanitize_tree(data)
        template_name = TEMPLATE_MAP.get(page["type"], "content-page.html")
        template = env.get_template(template_name)

        base = compute_base(page["output"])
        program = find_program_by_source(programs, page["source"]) if page["type"] == "program" else None
        course_slug = None
        if page["type"] == "program":
            course_slug = program["slug"] if program else page["source"].strip("/").split("/")[-1]
        raw_fees = resolve_fees(data, page) if page["type"] in ("program",) or page["id"].startswith("city-") else None
        fees = prepare_fee_display(raw_fees) if raw_fees else None
        salaries = resolve_salaries(data, page)
        display_sections = prepare_sections(data, salaries)
        wants_curriculum = page["type"] == "program" or str(page.get("id", "")).startswith("roadmap")
        curriculum = resolve_curriculum(page, data, program) if wants_curriculum else None
        list_programs = programs
        if page["type"] in ("courses-list", "home"):
            list_programs = enrich_programs_with_fees(programs, manifest)

        page_title = format_seo_title(data.get("title", ""), page)
        description = meta_description(data, page)
        canon = canonical_url(page)
        og_image = f"{SITE_ORIGIN}/assets/og.png"
        if page.get("id") in ("ncr", "gurgaon", "delhi", "noida", "ghaziabad"):
            og_image = f"{SITE_ORIGIN}/assets/img/og-gurugram.png"
        ctx = {
            "page_title": page_title,
            "meta_description": description,
            "canonical_url": canon,
            "og_type": og_type(page),
            "og_image": og_image,
            "noindex": is_noindex(page),
            "json_ld": json_ld(page, data, fees),
            "base": base,
            "active_nav": resolve_active_nav(page),
            "data": data,
            "display_sections": display_sections,
            "program": program,
            "course_slug": course_slug,
            "fees": fees,
            "salaries": salaries,
            "curriculum": curriculum,
            "jump_nav": build_jump_nav(fees, salaries, data, curriculum) if page["type"] == "program" else [],
            "page_id": page.get("id", ""),
            "programs": list_programs if page["type"] in ("courses-list", "register", "home") else [],
            "paths": load_json(BUILD / "career-paths.json") if page["type"] == "home" else None,
            "mentors": MENTORS,
            "brand": BRAND,
            "email": EMAIL,
            "contact_name": CONTACT_NAME,
            "phone_display": PHONE_DISPLAY,
            "phone_e164": PHONE_E164,
            "wa_url": WA_ME,
            "geo_lat": GEO_LAT,
            "geo_lng": GEO_LNG,
            "maps_embed": MAPS_EMBED,
            "maps_place": MAPS_PLACE,
            "extra_css": _extra_css(page["type"], page.get("id", "")),
            "extra_js": _extra_js(page["type"], page.get("id", "")),
            "employers": EMPLOYERS,
        }

        html = template.render(**ctx)
        html = rewrite_internal_links(html, base)
        html = post_process_html(html)

        out_path = SITE / page["output"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        generated += 1
        print(f"  Generated: {page['output']}")

    write_robots_and_sitemap(SITE, manifest["pages"])
    prune_unpublished_courses(manifest)
    not_found = env.get_template("404.html").render(
        page_title=f"Page not found — {BRAND}",
        meta_description=f"That page is not on {BRAND}. Browse programs or book a career call.",
        canonical_url=f"{SITE_ORIGIN}/404.html",
        og_type="website",
        og_image=f"{SITE_ORIGIN}/assets/og.png",
        noindex=True,
        json_ld=[],
        base="",
        active_nav="",
        extra_css=["content.css"],
        extra_js=[],
        brand=BRAND,
        email=EMAIL,
        contact_name=CONTACT_NAME,
        phone_display=PHONE_DISPLAY,
        phone_e164=PHONE_E164,
        wa_url=WA_ME,
        geo_lat=GEO_LAT,
        geo_lng=GEO_LNG,
        maps_embed=MAPS_EMBED,
        maps_place=MAPS_PLACE,
    )
    write_404(SITE, post_process_html(not_found))
    print(f"\nDone: {generated} pages generated, {skipped} skipped")


def prune_unpublished_courses(manifest: dict):
    """Remove generated course folders that are no longer in pages.json."""
    keep = {
        page["source"].strip("/").split("/")[-1]
        for page in manifest.get("pages", [])
        if page.get("type") == "program"
    }
    courses_root = SITE / "courses"
    if not courses_root.exists():
        return
    for child in courses_root.iterdir():
        if child.is_dir() and child.name not in keep:
            shutil.rmtree(child)
            print(f"  Removed unpublished: courses/{child.name}")


def _extra_css(page_type: str, page_id: str = "") -> list:
    if page_type == "home":
        return []
    if page_type == "register":
        return ["content.css"]
    if page_type == "program" or page_id.startswith("city-"):
        return ["program.css", "content.css"]
    if page_type in ("content", "comparison", "blog", "mentors"):
        return ["content.css"]
    return []


def write_employer_stamps(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    bars = ("#1a3d6e", "#e23b2b", "#f5c400", "#2e7d32", "#1565c0", "#6a1b9a")
    for i, (slug, name) in enumerate(EMPLOYERS):
        bar = bars[i % len(bars)]
        label = xml_escape(name.upper())
        size = 34 if len(name) < 10 else 26 if len(name) < 14 else 22
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="280" height="110" viewBox="0 0 280 110" role="img" aria-label="{xml_escape(name)}">
  <rect width="280" height="110" fill="#fff8e8"/>
  <rect x="4" y="4" width="272" height="102" fill="#fffdf7" stroke="#111" stroke-width="5"/>
  <path d="M4 4h272" stroke="{bar}" stroke-width="12"/>
  <g stroke="#c8c4b8" stroke-width="1.2">
    <path d="M28 0v110M56 0v110M84 0v110M112 0v110M140 0v110M168 0v110M196 0v110M224 0v110M252 0v110"/>
    <path d="M0 28h280M0 55h280M0 82h280"/>
  </g>
  <rect x="4" y="4" width="272" height="102" fill="none" stroke="#111" stroke-width="5"/>
  <text x="140" y="68" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="800" fill="#111">{label}</text>
</svg>
'''
        (dest / f"{slug}.svg").write_text(svg, encoding="utf-8")


def _extra_js(page_type: str, page_id: str = "") -> list:
    if page_type == "courses-list":
        return ["courses.js"]
    if page_type == "register":
        return ["register.js"]
    if page_type == "home":
        return ["grid.js", "home.js"]
    if page_id == "contact-us":
        return ["grid.js"]
    return []


def post_process_html(html: str) -> str:
    """Sanitize leftover brand strings; add lazy loading to images."""
    html = sanitize_text(html)

    def add_lazy(match):
        tag = match.group(0)
        if "loading=" in tag.lower():
            return tag
        if tag.rstrip().endswith("/>"):
            return tag[:-2].rstrip() + ' loading="lazy" decoding="async" />'
        return tag[:-1] + ' loading="lazy" decoding="async">'

    html = re.sub(
        r'<script(?![^>]*(?:src=["\'][^"\']*assets/|type=["\']application/ld\+json))[^>]*>.*?</script>',
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html = re.sub(r"<img[^>]*>", add_lazy, html, flags=re.IGNORECASE)
    return html


def rewrite_internal_links(html: str, base: str) -> str:
    """Fix absolute paths to work as static files."""
    live = {p["slug"] for p in load_programs()}

    def repl_href(m):
        path = m.group(1)
        if path.startswith("http") or path.startswith("mailto:") or path.startswith("tel:") or path.startswith("#") or path.startswith("https://wa.me"):
            return m.group(0)
        if path == "/":
            return f'href="{base}index.html"'
        clean = path.strip("/")
        parts = [p for p in clean.split("/") if p]
        if len(parts) >= 2 and parts[0] == "courses" and parts[1] not in live:
            return f'href="{base}courses/index.html"'
        return f'href="{base}{clean}/index.html"'

    html = re.sub(r'href="(/[^"]*)"', repl_href, html)
    return html


V5_INNER_CSS = """
.site-foot .footer-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr 1.2fr;
  gap: 28px;
  margin-bottom: 24px;
  text-align: left;
}
.site-foot .footer-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.site-foot .footer-col h4 {
  margin: 0 0 4px;
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.site-foot .footer-brand p {
  margin: 8px 0 0;
  max-width: 28rem;
  color: var(--muted);
}
.explore-card,
.prog-salary-card,
.mentor-card,
.faq-item,
.curriculum-list li {
  border-radius: 0 !important;
  border-width: 3px;
}
.explore-card:hover {
  background: var(--accent);
  color: var(--accent-ink);
  transform: none;
  box-shadow: none;
}
.card {
  padding: 0;
  overflow: hidden;
}
.card-cover {
  display: block;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  border-bottom: 3px solid var(--fg);
  background: #09090B;
}
.card-cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-body { padding: 22px 22px 18px; }
.card-footer { padding: 0 22px 22px; }
.home-figure {
  display: block;
  width: 100%;
  max-width: 36rem;
  max-height: 220px;
  object-fit: cover;
  border: 3px solid var(--accent);
  margin: 0 0 28px;
  background: #09090B;
}
.prog-thumb-spacer {
  width: 56px;
  height: 42px;
  display: block;
}
.prog {
  grid-template-columns: 56px 64px 1fr auto !important;
}
.ticker {
  width: 100%;
}
@media (max-width: 1099px) {
  .honest {
    grid-template-columns: 1fr !important;
  }
  .honest .no {
    border-left: 0 !important;
    border-top: var(--border) solid var(--fg);
  }
}
.prog .prog-thumb {
  width: 56px;
  height: 42px;
  object-fit: cover;
  border: 2px solid var(--line);
}
@media (max-width: 900px) {
  .site-foot .footer-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 640px) {
  .site-foot .footer-grid { grid-template-columns: 1fr; }
}

/* Hero: rem-capped type so browser zoom-out reveals more page (vw-only type stays viewport-tall). */
.is-home .hero h1 {
  padding: clamp(1.25rem, 3vh, 2.25rem) 1.5rem 1rem;
  font-size: clamp(1.85rem, 8vw, 4.25rem);
  line-height: 0.86;
}
.is-home .hero-stamp {
  width: min(110px, 22vw);
  height: min(110px, 22vw);
  top: 20px;
  right: 4%;
}
.is-home .hero-copy,
.is-home .hero-act {
  padding: 20px 24px;
  min-width: 0;
}
.is-home .hero-act .cta,
.is-home .hero-act .ghost {
  white-space: normal;
  text-align: center;
  width: 100%;
}
.is-home .demand .chart-stage {
  min-height: 0;
}
"""

PROGRAM_CSS = """
/* Program hero — rem-capped so 175% zoom / short viewports still show fees below */
.prog-hero { padding: clamp(1.25rem, 4vh, 2.75rem) 0 clamp(1rem, 3.5vh, 2.25rem); background: var(--paper); border-bottom: 1px solid var(--line); }
.prog-hero-grid { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(180px, 0.65fr); gap: 28px; align-items: center; }
.prog-hero-art { justify-self: end; max-width: min(380px, 34vw); width: 100%; }
@media (max-width: 1024px) {
  .prog-hero-grid { grid-template-columns: 1fr; gap: 18px; }
  .prog-hero-art { justify-self: start; max-width: min(420px, 100%); }
}
.prog-hero-art img {
  display: block;
  width: 100%;
  height: auto;
  max-height: min(280px, 38vh);
  object-fit: cover;
  object-position: center top;
  border: 3px solid var(--accent);
  background: #09090B;
}
#fees, #salary, #curriculum, #faq { scroll-margin-top: calc(var(--header-h) + 56px); }

.prog-jump {
  position: sticky;
  top: var(--header-h);
  z-index: 40;
  background: var(--bg);
  border-bottom: var(--border) solid var(--fg);
}
.prog-jump-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  min-height: 48px;
  padding-top: 8px;
  padding-bottom: 8px;
}
.prog-jump-label {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ink-3);
  margin-right: 4px;
}
.prog-jump a {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 6px 12px;
  border-radius: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-2);
  border: 1px solid var(--line);
  background: var(--card);
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}
.prog-jump a:hover { color: var(--accent); border-color: var(--accent-line); background: var(--accent-soft); }
.breadcrumb { font-family: var(--font-mono); font-size: 12px; margin-bottom: 16px; display: flex; gap: 8px; align-items: center; color: var(--ink-3); }
.breadcrumb a:hover { color: var(--accent); text-decoration: underline; }
.prog-hero-title { font-size: clamp(1.65rem, 2.4vw + 1rem, 2.6rem); font-weight: 700; letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 12px; color: var(--ink); }
.prog-hero-sub { font-size: 1rem; color: var(--ink-3); line-height: 1.6; max-width: 42rem; margin-bottom: 20px; }
.prog-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.prog-cta-row { display: flex; gap: 12px; flex-wrap: wrap; }
.prog-cta-row .btn-lg { padding: 12px 22px; font-size: 0.9rem; }
@media (max-height: 720px) {
  .prog-hero-art img { max-height: 28vh; }
  .prog-hero-sub { margin-bottom: 14px; }
}

/* Fee block */
.prog-fees { padding: 48px 0; background: var(--chip); border-bottom: 1px solid var(--line); }
.prog-fees-inner { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 40px 56px; align-items: start; }
@media (max-width: 720px) { .prog-fees-inner { grid-template-columns: 1fr; gap: 32px; } }
.prog-fees-col-main { min-width: 0; }
.prog-fees-label { font-family: var(--font-mono); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--ink-3); margin: 0 0 12px; }
.prog-fee-display { margin: 0; }
.prog-fee-amt { font-variant-numeric: tabular-nums; display: inline-flex; align-items: baseline; gap: 0.15em; line-height: 1.1; color: var(--ink); }
.prog-fee-symbol { font-size: 0.7em; font-weight: 700; opacity: 0.85; }
.prog-fee-num { font-size: clamp(2rem, 4vw, 2.75rem); font-weight: 700; letter-spacing: -0.03em; }
.prog-fee-display--discount .prog-fee-primary { display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px 18px; }
.prog-fee-display { min-width: 0; }
.prog-fee-amt { flex-wrap: wrap; }
.prog-fee-amt-wrap--original .prog-fee-num { font-size: clamp(1.1rem, 2vw, 1.4rem); font-weight: 500; text-decoration: line-through; color: var(--ink-3); opacity: 0.75; }
.prog-fee-amt-wrap--original .prog-fee-symbol { font-size: 0.85em; opacity: 0.75; }
.prog-fee-save { display: inline-flex; align-items: center; padding: 6px 12px; font-family: var(--font-mono); font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--accent-ink); background: var(--accent); border-radius: 0; white-space: nowrap; }
.prog-fee-save .prog-fee-symbol, .prog-fee-save .prog-fee-num { font-size: 11px; font-weight: 700; letter-spacing: 0.06em; color: var(--accent-ink); }
.prog-fee-display--tier { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 14px; }
.prog-fee-sep { font-family: var(--font-mono); font-size: 12px; font-weight: 600; color: var(--ink-3); align-self: center; padding: 0 2px; }
.prog-fee-display--plan { display: flex; flex-direction: column; gap: 10px; }
.prog-fee-plan-row { display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 14px; }
.prog-fee-plan-label { font-family: var(--font-mono); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink-3); min-width: 108px; flex-shrink: 0; }
.prog-fee-plan-row--secondary .prog-fee-num { font-size: clamp(1.35rem, 2.5vw, 1.75rem); }
.prog-fees-notes { margin-top: 14px; }
.prog-fees-note { font-size: 14px; line-height: 1.65; margin: 0 0 6px; max-width: 520px; color: var(--ink-2); }
.prog-fees-note:last-child { margin-bottom: 0; }
.prog-fees-note--muted { font-size: 13px; color: var(--ink-3); }
.prog-fees-plans { min-width: 0; }
.prog-fees-plan-list { list-style: none; margin: 0; padding: 0; }
.prog-fees-plan-list li { font-size: 15px; color: var(--ink-2); line-height: 1.55; padding: 12px 0; display: flex; align-items: flex-start; gap: 10px; border-bottom: 1px solid var(--line); }
.prog-fees-plan-list li::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--accent); margin-top: 0.55em; flex-shrink: 0; }
.prog-fees-plan-list li:last-child { border-bottom: none; padding-bottom: 0; }

/* Content sections */
.prog-sections { padding: 56px 0; background: var(--paper-alt); }
.prog-section { margin-bottom: 32px; padding-bottom: 32px; border-bottom: 1px solid var(--line); }
.prog-section:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.prog-section-title { font-size: 22px; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 14px; color: var(--ink); }
.prog-section-body { font-size: 15px; color: var(--ink-2); line-height: 1.75; white-space: pre-line; }

/* Salary tables */
.prog-salaries { padding: 56px 0; background: var(--paper-alt); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.prog-salary-header { max-width: 720px; margin-bottom: 32px; }
.prog-salary-title { font-size: clamp(1.4rem, 3vw, 1.9rem); font-weight: 700; letter-spacing: -0.02em; color: var(--ink); margin-bottom: 8px; }
.prog-salary-subtitle { font-size: 16px; font-weight: 600; color: var(--ink-2); margin-bottom: 12px; }
.prog-salary-intro { font-size: 15px; color: var(--ink-3); line-height: 1.7; margin-bottom: 0; }
.prog-salary-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; margin-bottom: 32px; }
.prog-salary-card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 20px; }
.prog-salary-card-title { font-size: 16px; font-weight: 700; color: var(--ink); margin-bottom: 14px; padding-bottom: 10px; border-bottom: 2px solid var(--accent); }
.prog-salary-card-tier { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--line); font-size: 14px; }
.prog-salary-card-tier:last-of-type { border-bottom: none; }
.prog-salary-card-note { font-size: 12px; color: var(--ink-3); margin-top: 12px; line-height: 1.5; }
.prog-salary-table-wrap { overflow-x: auto; margin: 20px 0; border: 1px solid var(--line); border-radius: var(--radius); background: var(--card); }
.prog-salary-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.prog-salary-caption { caption-side: top; text-align: left; font-weight: 700; font-size: 15px; color: var(--ink); padding: 16px 16px 8px; }
.prog-salary-table thead { background: var(--paper-alt); border-bottom: 2px solid var(--line); }
.prog-salary-table th { text-align: left; padding: 12px 16px; font-family: var(--font-mono); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink); }
.prog-salary-table td { padding: 12px 16px; border-bottom: 1px solid var(--line); color: var(--ink-2); }
.prog-salary-table tbody tr:hover { background: var(--accent-soft); }
.prog-salary-table tbody tr:last-child td { border-bottom: none; }
.prog-salary-row-alt { background: var(--paper); }
.prog-salary-exp { font-weight: 600; color: var(--ink); }
.prog-salary-amt { font-family: var(--font-mono); font-variant-numeric: tabular-nums; font-weight: 700; color: var(--accent); text-align: right; white-space: nowrap; }
.prog-salary-footnote { font-size: 13px; color: var(--ink-3); margin-top: 12px; line-height: 1.6; }
.prog-salary-tips { margin-top: 28px; padding: 24px; background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: var(--radius); }
.prog-salary-tips-title { font-size: 16px; font-weight: 700; color: var(--ink); margin-bottom: 12px; }
.prog-salary-tips-list { margin: 0; padding-left: 20px; }
.prog-salary-tips-list li { font-size: 14px; color: var(--ink-2); line-height: 1.65; margin-bottom: 8px; }

/* Curriculum */
.prog-curriculum { padding: 48px 0; background: var(--paper); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.curriculum-list { list-style: none; margin: 20px 0; }
.curriculum-list li { padding: 14px 16px; border: 1px solid var(--line); border-radius: var(--radius-sm); margin-bottom: 8px; font-size: 15px; color: var(--ink-2); background: var(--card); }
.curriculum-tree { margin-top: 24px; display: flex; flex-direction: column; gap: 12px; max-width: 760px; }
.curr-level { border: var(--border) solid var(--line); border-radius: 0; background: var(--card); overflow: hidden; }
.curr-level > summary, .curr-module > summary {
  list-style: none; cursor: pointer; display: flex; align-items: center; gap: 12px;
  padding: 16px 18px; font-weight: 700; font-size: 15px; color: var(--ink);
}
.curr-level > summary::-webkit-details-marker,
.curr-module > summary::-webkit-details-marker { display: none; }
.curr-level > summary::after, .curr-module > summary::after {
  content: ""; margin-left: auto; width: 8px; height: 8px; flex-shrink: 0;
  border-right: 2px solid var(--accent); border-bottom: 2px solid var(--accent);
  transform: rotate(45deg); transition: transform 0.15s;
}
.curr-level[open] > summary::after, .curr-module[open] > summary::after { transform: rotate(225deg); translate: 0 3px; }
.curr-level > summary { background: var(--chip); }
.curr-level-body { padding: 8px 12px 14px; }
.curr-module { border: var(--border) solid var(--line); border-radius: 0; margin: 8px 0; background: var(--card); }
.curr-module > summary { font-size: 14px; font-weight: 600; }
.curr-topics { list-style: none; margin: 0 16px 12px 28px; padding: 4px 0 8px; border-left: 2px solid var(--line); }
.curr-topics li { position: relative; padding: 8px 0 8px 20px; font-size: 14px; color: var(--ink-2); line-height: 1.45; }
.curr-topics li::before {
  content: ""; position: absolute; left: -5px; top: 14px; width: 8px; height: 8px;
  border-radius: 0; background: var(--accent); border: 2px solid var(--bg); box-shadow: 0 0 0 1px var(--line);
}

/* FAQ */
.prog-faq { padding: 56px 0; background: var(--paper-alt); }
.faq-list { margin-top: 24px; }
.faq-item { border: 1px solid var(--line); border-radius: var(--radius-sm); margin-bottom: 8px; background: var(--card); }
.faq-item summary { padding: 16px 20px; font-weight: 700; font-size: 15px; cursor: pointer; list-style: none; color: var(--ink); }
.faq-item summary::-webkit-details-marker { display: none; }
.faq-item p { padding: 0 20px 16px; font-size: 14px; color: var(--ink-2); line-height: 1.7; }
"""

CONTENT_CSS = """
.page-hero { padding: 56px 0 48px; background: var(--paper); border-bottom: 1px solid var(--line); }
.prog-curriculum { padding: 48px 0; background: var(--paper); border-bottom: 1px solid var(--line); }
.explore-path { padding: 40px 0 48px; background: var(--paper-alt); border-bottom: 1px solid var(--line); }
.explore-path .section-title { margin-bottom: 8px; white-space: normal; }
.explore-path-lead { font-size: 15px; color: var(--ink-3); margin-bottom: 24px; max-width: 520px; }
.explore-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.explore-card {
  display: flex; flex-direction: column; gap: 6px;
  padding: 20px; min-height: 120px;
  background: var(--card); border: 1px solid var(--line); border-radius: var(--radius);
  color: var(--ink); transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
}
.explore-card:hover { border-color: var(--accent-line); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(20, 18, 16, 0.06); color: var(--ink); }
.explore-card strong { font-size: 16px; font-weight: 700; letter-spacing: -0.02em; }
.explore-card span { font-size: 13px; color: var(--ink-3); line-height: 1.5; }
.page-content table, .scraped-content table { width: 100%; border-collapse: collapse; font-size: 14px; margin: 16px 0; background: var(--card); }
.page-content th, .scraped-content th { text-align: left; padding: 10px 12px; background: var(--paper-alt); border-bottom: 2px solid var(--line); color: var(--ink); font-size: 12px; }
.page-content td, .scraped-content td { padding: 10px 12px; border-bottom: 1px solid var(--line); color: var(--ink-2); }
.page-hero-title { font-size: clamp(1.8rem, 4vw, 2.6rem); font-weight: 700; letter-spacing: -0.03em; line-height: 1.12; margin-bottom: 16px; color: var(--ink); }
.page-hero-sub { font-size: 17px; line-height: 1.7; max-width: 640px; color: var(--ink-3); }
.page-content { padding: 56px 0 72px; background: var(--paper); }
.content-body { max-width: 760px; }
.content-section { margin-bottom: 36px; }
.content-section h2 { font-size: 20px; font-weight: 700; margin-bottom: 12px; letter-spacing: -0.02em; color: var(--ink); }
.content-section p { font-size: 15px; color: var(--ink-2); line-height: 1.75; white-space: pre-line; }
.content-list { list-style: none; margin: 16px 0 24px; }
.content-list li { font-size: 15px; color: var(--ink-2); margin-bottom: 0; line-height: 1.6; padding: 12px 0; border-bottom: 1px solid var(--line); }
.content-list li:last-child { border-bottom: none; }
.scraped-content { font-size: 15px; color: var(--ink-2); line-height: 1.75; }
.scraped-content h2, .scraped-content h3 { color: var(--ink); font-weight: 700; margin: 32px 0 12px; }
.scraped-content p { margin-bottom: 14px; }
.scraped-content ul { margin: 12px 0 12px 20px; }
.scraped-content li { margin-bottom: 6px; }
.scraped-content img { margin: 16px 0; max-width: 100%; height: auto; border-radius: var(--radius-sm); }
.mentors-grid-section { padding: 56px 0; background: var(--paper); }
.mentors-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.mentor-card { padding: 28px; border: 1px solid var(--line); border-radius: var(--radius); background: var(--card); }
.mentor-avatar {
  width: 56px; height: 56px; border-radius: 0; margin-bottom: 14px;
  background: var(--accent); color: var(--accent-ink); font-weight: 700; font-size: 16px; letter-spacing: 0.04em;
  display: flex; align-items: center; justify-content: center;
}
.mentor-name { font-size: 18px; font-weight: 700; margin-bottom: 4px; color: var(--ink); }
.mentor-role { font-size: 14px; color: var(--ink-3); margin-bottom: 14px; }
.mentor-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
.mentor-focus { font-size: 14px; color: var(--ink-2); line-height: 1.65; }
.faq-list { margin-top: 24px; }
.faq-item { border: 1px solid var(--line); border-radius: var(--radius-sm); margin-bottom: 8px; background: var(--card); }
.faq-item summary { padding: 16px 20px; font-weight: 700; font-size: 15px; cursor: pointer; list-style: none; color: var(--ink); }
.faq-item summary::-webkit-details-marker { display: none; }
.faq-item p { padding: 0 20px 16px; font-size: 14px; color: var(--ink-2); line-height: 1.7; }
.curriculum-tree { margin-top: 24px; display: flex; flex-direction: column; gap: 12px; max-width: 760px; }
.curr-level { border: var(--border) solid var(--line); border-radius: 0; background: var(--card); overflow: hidden; }
.curr-level > summary, .curr-module > summary {
  list-style: none; cursor: pointer; display: flex; align-items: center; gap: 12px;
  padding: 16px 18px; font-weight: 700; font-size: 15px; color: var(--ink);
}
.curr-level > summary::-webkit-details-marker,
.curr-module > summary::-webkit-details-marker { display: none; }
.curr-level > summary::after, .curr-module > summary::after {
  content: ""; margin-left: auto; width: 8px; height: 8px; flex-shrink: 0;
  border-right: 2px solid var(--accent); border-bottom: 2px solid var(--accent);
  transform: rotate(45deg); transition: transform 0.15s;
}
.curr-level[open] > summary::after, .curr-module[open] > summary::after { transform: rotate(225deg); translate: 0 3px; }
.curr-level > summary { background: var(--chip); }
.curr-level-body { padding: 8px 12px 14px; }
.curr-module { border: var(--border) solid var(--line); border-radius: 0; margin: 8px 0; background: var(--card); }
.curr-module > summary { font-size: 14px; font-weight: 600; }
.curr-topics { list-style: none; margin: 0 16px 12px 28px; padding: 4px 0 8px; border-left: 2px solid var(--line); }
.curr-topics li { position: relative; padding: 8px 0 8px 20px; font-size: 14px; color: var(--ink-2); line-height: 1.45; }
.curr-topics li::before {
  content: ""; position: absolute; left: -5px; top: 14px; width: 8px; height: 8px;
  border-radius: 0; background: var(--accent); border: 2px solid var(--bg); box-shadow: 0 0 0 1px var(--line);
}
.register-section { padding: 48px 0 72px; background: var(--paper); }
.inquiry-form { max-width: 640px; margin: 0 auto; background: var(--card); border: var(--border) solid var(--fg); border-radius: 0; padding: 32px; }
@media (max-width: 600px) { .inquiry-form { padding: 24px 20px; } }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 600px) { .form-grid { grid-template-columns: 1fr; } }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group-full { grid-column: 1 / -1; }
.form-group label { font-size: 14px; font-weight: 700; color: var(--ink); }
.form-group .required { color: var(--accent); }
.form-group .optional { font-weight: 400; color: var(--ink-3); font-size: 13px; }
.form-group input, .form-group select, .form-group textarea { font-family: var(--font-display); font-size: 15px; color: var(--ink); background: var(--bg); border: var(--border) solid var(--line); border-radius: 0; padding: 11px 14px; transition: border-color 0.15s; width: 100%; }
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
.form-group input.invalid, .form-group select.invalid { border-color: var(--accent); }
.form-group textarea { resize: vertical; min-height: 96px; }
.form-error { font-size: 13px; color: var(--accent); margin: 0; min-height: 0; }
.form-error:empty { display: none; }
.form-actions { margin-top: 28px; }
.form-actions .btn { width: 100%; justify-content: center; gap: 8px; }
.btn-icon { width: 18px; height: 18px; flex-shrink: 0; }
.form-alt-contact { margin-top: 28px; padding-top: 24px; border-top: 1px solid var(--line); text-align: center; }
.form-alt-contact > p { font-size: 14px; color: var(--ink-3); margin-bottom: 12px; }
.form-alt-links { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px 20px; }
.form-alt-link { display: inline-flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; color: var(--accent); text-decoration: none; }
.form-alt-link svg { width: 16px; height: 16px; flex-shrink: 0; }
.form-alt-link:hover { text-decoration: underline; text-underline-offset: 3px; }
"""

NAV_JS = """
(function () {
  var toggle = document.getElementById('navToggle');
  var menu = document.getElementById('menu');
  var closeBtn = document.getElementById('menuClose');
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
  if (!toggle || !menu) return;

  function setOpen(open) {
    menu.classList.toggle('is-open', open);
    menu.setAttribute('aria-hidden', open ? 'false' : 'true');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) {
      if (closeBtn) closeBtn.focus();
      return;
    }
    if (closeBtn) closeBtn.blur();
    if (document.activeElement && menu.contains(document.activeElement)) {
      document.activeElement.blur();
    }
    if (window.getSelection) {
      var sel = window.getSelection();
      if (sel && sel.removeAllRanges) sel.removeAllRanges();
    }
    toggle.focus();
  }

  toggle.addEventListener('click', function () {
    setOpen(!menu.classList.contains('is-open'));
  });
  if (closeBtn) {
    closeBtn.addEventListener('click', function () { setOpen(false); });
  }
  menu.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') setOpen(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menu.classList.contains('is-open')) setOpen(false);
  });
})();
"""

HOME_JS = """
(function () {
  var stage = document.querySelector('.chart-stage');
  var towers = Array.prototype.slice.call(document.querySelectorAll('.lane'));
  var readoutTitle = document.getElementById('readoutTitle');
  var readoutBody = document.getElementById('readoutBody');
  if (!towers.length) return;

  var facts = {
    ds: {
      title: 'Data scientists · U.S. BLS +33.5%',
      body: 'U.S. BLS (not MoSPI/PLFS, not Indian CTC) projects data scientist employment to grow 33.5% from 2024 to 2034 — among the fastest of all occupations, versus 3.1% for all jobs. We show it as a published international benchmark because India has no matching official occupation series. Not a placement promise. If this is the job you want, we map Excel/SQL/Python into a live program.'
    },
    sec: {
      title: 'Information security analysts · U.S. BLS +28.5%',
      body: 'U.S. BLS: +28.5% employment change, 2024–34 — an international benchmark, not an Indian official occupation rate. Security is not our core catalog, but production AI work still needs people who can think about access, logs, and failure. A career call will say so if another path fits better.'
    },
    rs: {
      title: 'Computer & information research scientists · U.S. BLS +19.7%',
      body: 'U.S. BLS: +19.7%, 2024–34. Not Indian CTC and not a placement rate. Research-scientist titles usually want a deeper academic track than a 3–6 month cohort. We still teach the engineering stack used next to that work — models, evaluation, shipping.'
    },
    sw: {
      title: 'Software developers · U.S. BLS +16%',
      body: 'U.S. BLS: software developers +16% (2024–34); the broader developers / QA / testers group is +15%. This is a U.S. labour forecast shown for Indian learners as a published benchmark, not an Indian salary table. Developers who can work with data, APIs, and LLMs are the people companies actually interview. That is the sequence we teach.'
    },
    all: {
      title: 'All occupations · U.S. BLS +3.1%',
      body: 'The short bar is the U.S. BLS all-occupations average. AI-adjacent roles sit far above it in this table. India does not publish an equivalent official occupation-level series — so we refuse to invent one. Book a call if you want a role map, not a slogan.'
    }
  };

  function selectTower(btn, focus) {
    towers.forEach(function (t) {
      t.classList.toggle('is-on', t === btn);
      t.setAttribute('aria-pressed', t === btn ? 'true' : 'false');
    });
    var fact = facts[btn.getAttribute('data-id')];
    if (fact && readoutTitle && readoutBody) {
      readoutTitle.textContent = fact.title;
      readoutBody.textContent = fact.body;
    }
    if (focus) btn.focus();
  }

  towers.forEach(function (btn, i) {
    btn.addEventListener('click', function () { selectTower(btn, false); });
    btn.addEventListener('keydown', function (e) {
      var next = i;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = (i + 1) % towers.length;
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = (i - 1 + towers.length) % towers.length;
      else return;
      e.preventDefault();
      selectTower(towers[next], true);
    });
  });

  function draw() {
    if (stage) stage.classList.add('is-drawn');
  }

  if (!stage) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    draw();
    return;
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          draw();
          io.disconnect();
        }
      });
    }, { threshold: 0.25 });
    io.observe(stage);
  } else {
    draw();
  }
})();

(function () {
  var boards = Array.prototype.slice.call(document.querySelectorAll('#market-shift .js-reveal'));
  if (!boards.length) return;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function formatCount(el, value) {
    var suf = el.getAttribute('data-suf') || '';
    var pre = el.getAttribute('data-pre') || '';
    var decimals = String(el.getAttribute('data-to') || '').indexOf('.') >= 0 ? 1 : 0;
    el.textContent = pre + value.toFixed(decimals) + suf;
  }

  function countUp(el) {
    if (el.getAttribute('data-done') === '1') return;
    el.setAttribute('data-done', '1');
    var to = parseFloat(el.getAttribute('data-to') || '0');
    if (reduce) {
      formatCount(el, to);
      return;
    }
    var start = performance.now();
    var dur = 900;
    function tick(now) {
      var t = Math.min(1, (now - start) / dur);
      var eased = 1 - Math.pow(1 - t, 3);
      formatCount(el, to * eased);
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function activate(board) {
    if (board.classList.contains('is-in')) return;
    board.classList.add('is-in');
    Array.prototype.forEach.call(board.querySelectorAll('.js-count'), countUp);
  }

  if (reduce || !('IntersectionObserver' in window)) {
    boards.forEach(activate);
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        activate(entry.target);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.28, rootMargin: '0px 0px -8% 0px' });
  boards.forEach(function (b) { io.observe(b); });
})();
"""

def _courses_js() -> str:
    total = len(load_programs())
    return f"""const TOTAL = {total};

function applyFilter(filter) {{
  var cards = document.querySelectorAll('.card');
  var visible = 0;
  cards.forEach(function(card) {{
    var tags = card.dataset.tags.split(',');
    var show = filter === 'all' || tags.indexOf(filter) !== -1;
    card.classList.toggle('hidden', !show);
    if (show) visible++;
  }});
  ['featuredSection', 'moreSection'].forEach(function(id) {{
    var section = document.getElementById(id);
    if (!section) return;
    var grid = section.querySelector('.grid');
    if (!grid) return;
    var visibleInSection = grid.querySelectorAll('.card:not(.hidden)').length;
    var existing = grid.querySelector('.empty-state');
    if (visibleInSection === 0) {{
      if (!existing) {{
        var tpl = document.getElementById('emptyTpl');
        grid.appendChild(tpl.content.cloneNode(true));
      }}
    }} else if (existing) {{
      existing.remove();
    }}
  }});
  document.getElementById('showingCount').textContent =
    filter === 'all' ? 'Showing all ' + TOTAL + ' programs' : 'Showing ' + visible + ' of ' + TOTAL + ' programs';
}}

document.querySelectorAll('.filter-pill').forEach(function(pill) {{
  pill.addEventListener('click', function() {{
    document.querySelectorAll('.filter-pill').forEach(function(p) {{
      p.classList.remove('active');
      p.setAttribute('aria-pressed', 'false');
    }});
    pill.classList.add('active');
    pill.setAttribute('aria-pressed', 'true');
    applyFilter(pill.dataset.filter);
  }});
}});
"""

REGISTER_JS = """
(function () {
  var form = document.getElementById('inquiryForm');
  if (!form) return;

  var courseSelect = document.getElementById('course');
  var params = new URLSearchParams(window.location.search);
  var courseParam = params.get('course');
  if (courseParam && courseSelect) {
    for (var i = 0; i < courseSelect.options.length; i++) {
      if (courseSelect.options[i].value === courseParam) {
        courseSelect.selectedIndex = i;
        break;
      }
    }
  }

  var fields = {
    name: { el: document.getElementById('name'), err: document.getElementById('nameError'), msg: 'Please enter your name.' },
    phone: { el: document.getElementById('phone'), err: document.getElementById('phoneError'), msg: 'Please enter a valid phone number.' },
    email: { el: document.getElementById('email'), err: document.getElementById('emailError'), msg: 'Please enter a valid email address.' },
    experience: { el: document.getElementById('experience'), err: document.getElementById('experienceError'), msg: 'Please select your experience level.' },
    course: { el: courseSelect, err: document.getElementById('courseError'), msg: 'Please select a program.' }
  };

  function clearErrors() {
    Object.keys(fields).forEach(function (key) {
      var f = fields[key];
      if (f.err) f.err.textContent = '';
      if (f.el) f.el.classList.remove('invalid');
    });
  }

  function showError(key, message) {
    var f = fields[key];
    if (f.err) f.err.textContent = message || f.msg;
    if (f.el) f.el.classList.add('invalid');
  }

  function isValidPhone(val) {
    var digits = val.replace(/\\D/g, '');
    return digits.length >= 10;
  }

  function isValidEmail(val) {
    return /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(val);
  }

  function courseLabel() {
    if (!courseSelect || courseSelect.selectedIndex < 0) return '';
    return courseSelect.options[courseSelect.selectedIndex].text;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    clearErrors();

    var name = fields.name.el.value.trim();
    var phone = fields.phone.el.value.trim();
    var email = fields.email.el.value.trim();
    var experience = fields.experience.el.value;
    var course = fields.course.el.value;
    var message = document.getElementById('message').value.trim();
    var valid = true;

    if (!name) { showError('name'); valid = false; }
    if (!phone || !isValidPhone(phone)) { showError('phone'); valid = false; }
    if (!email || !isValidEmail(email)) { showError('email'); valid = false; }
    if (!experience) { showError('experience'); valid = false; }
    if (!course) { showError('course'); valid = false; }
    if (!valid) {
      var firstInvalid = form.querySelector('.invalid');
      if (firstInvalid) firstInvalid.focus();
      return;
    }

    var cityEl = document.getElementById('cityField');
    var lines = [
      "Hi Prerna, I'd like to book a career call.",
      'Name: ' + name,
      'Phone: ' + phone,
      'Email: ' + email,
      'Experience: ' + experience,
      'Course: ' + courseLabel()
    ];
    if (cityEl && cityEl.value.trim()) lines.push('City: ' + cityEl.value.trim());
    if (message) lines.push('Message: ' + message);
    lines.push('Page: ' + window.location.href);

    var url = 'https://wa.me/918368122877?text=' + encodeURIComponent(lines.join('\\n'));
    window.open(url, '_blank');
  });
})();
"""

PATHS_JS = """
(function () {
  var tabs = document.querySelectorAll('.path-tab');
  var panels = document.querySelectorAll('.path-panel');
  var picks = document.querySelectorAll('.path-pick');
  var hubs = document.querySelectorAll('.hub-node');
  if (!tabs.length) return;

  function activate(id, updateHash, scroll) {
    tabs.forEach(function (tab) {
      var on = tab.getAttribute('data-path') === id;
      tab.classList.toggle('is-active', on);
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    panels.forEach(function (panel) {
      var on = panel.getAttribute('data-path') === id;
      panel.classList.toggle('is-active', on);
      if (on) {
        panel.removeAttribute('hidden');
        panel.classList.remove('is-enter');
        void panel.offsetWidth;
        panel.classList.add('is-enter');
      } else {
        panel.setAttribute('hidden', '');
        panel.classList.remove('is-enter');
      }
    });
    picks.forEach(function (el) {
      el.classList.toggle('is-active', el.getAttribute('data-path') === id);
    });
    hubs.forEach(function (el) {
      el.classList.toggle('is-active', el.getAttribute('data-path') === id);
    });
    if (updateHash) {
      history.replaceState(null, '', '#path=' + id);
    }
    if (scroll) {
      var detail = document.getElementById('path-detail');
      if (detail) detail.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function bind(nodes, shouldScroll) {
    nodes.forEach(function (el) {
      el.addEventListener('click', function () {
        activate(el.getAttribute('data-path'), true, shouldScroll);
      });
    });
  }

  bind(tabs, false);
  bind(picks, true);
  bind(hubs, true);

  var hash = window.location.hash || '';
  var match = hash.match(/path=([a-z0-9-]+)/);
  if (match) {
    var exists = Array.prototype.some.call(tabs, function (t) {
      return t.getAttribute('data-path') === match[1];
    });
    if (exists) activate(match[1], false, false);
  }
})();
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" fill="#DFE104"/>
  <path fill="#09090B" d="M6 26V6h8.4c4.6 0 7.4 2.5 7.4 6.6 0 2.7-1.4 4.8-3.8 5.7L22 26h-5.1l-3.6-7.1H11V26H6zm5-11.2h3.1c2.1 0 3.3-1.1 3.3-2.8S16.2 9.2 14.1 9.2H11v5.6z"/>
</svg>"""


if __name__ == "__main__":
    generate()
