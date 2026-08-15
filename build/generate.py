#!/usr/bin/env python3
"""Generate static HTML site from scraped JSON and Jinja2 templates."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from curriculum import resolve_curriculum
from fee_display import prepare_fee_display
from fees import extract_city_fees, extract_fees
from salaries import extract_salaries, filter_sections, format_section_html
from seo import (
    BRAND,
    EMAIL,
    SITE_ORIGIN,
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

def _initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


MENTORS = [
    {"name": "Ankit", "role": "Lead AI Engineer", "tags": ["Generative AI", "Agentic AI", "LLM", "VLM", "AIOPS"], "focus": "Supports learners across analytics, structured problem-solving, and applied ML foundations."},
    {"name": "Prerna", "role": "Data Scientist", "tags": ["Machine Learning", "Computer Vision", "NLP", "GenAI", "Agentic AI"], "focus": "Guides project work and practical implementation across core AI workflows."},
    {"name": "Praveen", "role": "Applied AI Engineer", "tags": ["Generative AI", "Deep Learning", "Python", "ML Systems", "Agentic AI"], "focus": "Helps learners connect modern AI concepts with real engineering execution."},
    {"name": "Aayush", "role": "Senior AI Engineer", "tags": ["Machine Learning", "Computer Vision", "LLMOPS", "AIOPS", "GenAI"], "focus": "Focuses on helping learners build strong model-building intuition and debugging skills."},
    {"name": "Rahul Bhardwaj", "role": "ML Engineer", "tags": ["MLOps", "Data Engineering", "Python", "Cloud"], "focus": "Brings production ML deployment experience to mentor data pipeline and serving projects."},
    {"name": "Vaibhav Sharma", "role": "GenAI Specialist", "tags": ["RAG", "LLM Fine-tuning", "LangChain", "Agents"], "focus": "Specializes in RAG architecture and agentic workflow design for real-world applications."},
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


def setup_assets():
    assets = SITE / "assets"
    css_dir = assets / "css"
    js_dir = assets / "js"
    css_dir.mkdir(parents=True, exist_ok=True)
    js_dir.mkdir(parents=True, exist_ok=True)

    # Copy base CSS from existing styles.css
    src_css = ROOT / "styles.css"
    if src_css.exists():
        shutil.copy(src_css, css_dir / "base.css")

    # Write program.css and content.css
    (css_dir / "program.css").write_text(PROGRAM_CSS, encoding="utf-8")
    (css_dir / "content.css").write_text(CONTENT_CSS, encoding="utf-8")

    # Write JS files
    (js_dir / "nav.js").write_text(NAV_JS, encoding="utf-8")
    (js_dir / "courses.js").write_text(_courses_js(), encoding="utf-8")
    (js_dir / "register.js").write_text(REGISTER_JS, encoding="utf-8")
    (js_dir / "paths.js").write_text(PATHS_JS, encoding="utf-8")

    # Favicon + social preview
    (assets / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    og_src = BUILD / "og.png"
    if not og_src.exists():
        og_src = Path(r"C:\Users\Pc\.cursor\projects\d-personal-app\assets\og.png")
    if og_src.exists():
        shutil.copy(og_src, assets / "og.png")
        if not (BUILD / "og.png").exists():
            shutil.copy(og_src, BUILD / "og.png")


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
        if page["type"] == "courses-list":
            list_programs = enrich_programs_with_fees(programs, manifest)

        page_title = format_seo_title(data.get("title", ""), page)
        description = meta_description(data, page)
        canon = canonical_url(page)
        ctx = {
            "page_title": page_title,
            "meta_description": description,
            "canonical_url": canon,
            "og_type": og_type(page),
            "og_image": f"{SITE_ORIGIN}/assets/og.png",
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
            "programs": list_programs if page["type"] in ("courses-list", "register") else [],
            "paths": load_json(BUILD / "career-paths.json") if page["type"] == "home" else None,
            "mentors": MENTORS,
            "brand": BRAND,
            "email": EMAIL,
            "extra_css": _extra_css(page["type"], page.get("id", "")),
            "extra_js": _extra_js(page["type"]),
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
    )
    write_404(SITE, post_process_html(not_found))
    print(f"\nDone: {generated} pages generated, {skipped} skipped")


def _extra_css(page_type: str, page_id: str = "") -> list:
    if page_type == "register":
        return ["content.css"]
    if page_type == "program" or page_id.startswith("city-"):
        return ["program.css", "content.css"]
    if page_type in ("content", "comparison", "blog", "mentors", "home"):
        return ["content.css"]
    return []


def _extra_js(page_type: str) -> list:
    if page_type == "courses-list":
        return ["courses.js"]
    if page_type == "register":
        return ["register.js"]
    if page_type == "home":
        return ["paths.js"]
    return []


def post_process_html(html: str) -> str:
    """Sanitize leftover brand strings; add lazy loading to images."""
    html = sanitize_text(html)

    def add_lazy(match):
        tag = match.group(0)
        if "loading=" in tag.lower():
            return tag
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

    def repl_href(m):
        path = m.group(1)
        if path.startswith("http") or path.startswith("mailto:") or path.startswith("tel:") or path.startswith("#") or path.startswith("https://wa.me"):
            return m.group(0)
        if path == "/":
            return f'href="{base}index.html"'
        clean = path.strip("/")
        return f'href="{base}{clean}/index.html"'

    html = re.sub(r'href="(/[^"]*)"', repl_href, html)
    return html


PROGRAM_CSS = """
/* Program hero */
.prog-hero { padding: 56px 0 48px; background: var(--paper); border-bottom: 1px solid var(--line); }
.prog-hero-grid { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(200px, 0.7fr); gap: 32px; align-items: center; }
@media (max-width: 768px) { .prog-hero-grid { grid-template-columns: 1fr; } .prog-hero-art { display: none; } }
.prog-hero-art { justify-self: end; max-width: 280px; width: 100%; }
#fees, #salary, #curriculum, #faq { scroll-margin-top: calc(var(--header-h) + 56px); }

.prog-jump {
  position: sticky;
  top: var(--header-h);
  z-index: 40;
  background: rgba(248, 250, 252, 0.94);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
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
  border-radius: 999px;
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
.prog-hero-title { font-size: clamp(1.8rem, 4vw, 2.8rem); font-weight: 700; letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 16px; color: var(--ink); }
.prog-hero-sub { font-size: 17px; color: var(--ink-3); line-height: 1.7; max-width: 680px; margin-bottom: 24px; }
.prog-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.prog-cta-row { display: flex; gap: 12px; flex-wrap: wrap; }

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
.prog-fee-save { display: inline-flex; align-items: center; padding: 6px 12px; font-family: var(--font-mono); font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #fff; background: var(--accent); border-radius: 999px; white-space: nowrap; }
.prog-fee-save .prog-fee-symbol, .prog-fee-save .prog-fee-num { font-size: 11px; font-weight: 700; letter-spacing: 0.06em; color: #fff; }
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
.curr-level { border: 1px solid var(--line); border-radius: 12px; background: var(--card); overflow: hidden; }
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
.curr-module { border: 1px solid #BFDBFE; border-radius: 10px; margin: 8px 0; background: #fff; }
.curr-module > summary { font-size: 14px; font-weight: 600; }
.curr-topics { list-style: none; margin: 0 16px 12px 28px; padding: 4px 0 8px; border-left: 2px solid #BFDBFE; }
.curr-topics li { position: relative; padding: 8px 0 8px 20px; font-size: 14px; color: var(--ink-2); line-height: 1.45; }
.curr-topics li::before {
  content: ""; position: absolute; left: -5px; top: 14px; width: 8px; height: 8px;
  border-radius: 50%; background: var(--accent); border: 2px solid #fff; box-shadow: 0 0 0 1px #BFDBFE;
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
  width: 56px; height: 56px; border-radius: 50%; margin-bottom: 14px;
  background: var(--accent-dark); color: #fff; font-weight: 700; font-size: 16px; letter-spacing: 0.04em;
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
.curr-level { border: 1px solid var(--line); border-radius: 12px; background: var(--card); overflow: hidden; }
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
.curr-module { border: 1px solid #BFDBFE; border-radius: 10px; margin: 8px 0; background: #fff; }
.curr-module > summary { font-size: 14px; font-weight: 600; }
.curr-topics { list-style: none; margin: 0 16px 12px 28px; padding: 4px 0 8px; border-left: 2px solid #BFDBFE; }
.curr-topics li { position: relative; padding: 8px 0 8px 20px; font-size: 14px; color: var(--ink-2); line-height: 1.45; }
.curr-topics li::before {
  content: ""; position: absolute; left: -5px; top: 14px; width: 8px; height: 8px;
  border-radius: 50%; background: var(--accent); border: 2px solid #fff; box-shadow: 0 0 0 1px #BFDBFE;
}
.register-section { padding: 48px 0 72px; background: var(--paper); }
.inquiry-form { max-width: 640px; margin: 0 auto; background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 32px; box-shadow: 0 8px 24px rgba(20, 18, 16, 0.04); }
@media (max-width: 600px) { .inquiry-form { padding: 24px 20px; } }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 600px) { .form-grid { grid-template-columns: 1fr; } }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group-full { grid-column: 1 / -1; }
.form-group label { font-size: 14px; font-weight: 700; color: var(--ink); }
.form-group .required { color: var(--accent); }
.form-group .optional { font-weight: 400; color: var(--ink-3); font-size: 13px; }
.form-group input, .form-group select, .form-group textarea { font-family: var(--font-sans); font-size: 15px; color: var(--ink); background: var(--paper); border: 1px solid var(--line-2); border-radius: var(--radius-sm); padding: 11px 14px; transition: border-color 0.15s; width: 100%; }
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
  var nav = document.getElementById('nav');
  var header = document.getElementById('header');
  var year = document.getElementById('year');
  var explore = document.getElementById('navExplore');
  var exploreBtn = document.getElementById('exploreToggle');
  if (year) year.textContent = new Date().getFullYear();
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        if (explore) {
          explore.classList.remove('open');
          if (exploreBtn) exploreBtn.setAttribute('aria-expanded', 'false');
        }
      });
    });
  }
  if (explore && exploreBtn) {
    exploreBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = explore.classList.toggle('open');
      exploreBtn.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', function (e) {
      if (!explore.contains(e.target)) {
        explore.classList.remove('open');
        exploreBtn.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        explore.classList.remove('open');
        exploreBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }
  if (header) {
    window.addEventListener('scroll', function () {
      header.classList.toggle('scrolled', window.scrollY > 8);
    }, { passive: true });
  }
})();
"""

def _courses_js() -> str:
    return """const TOTAL = 17;

function applyFilter(filter) {
  var cards = document.querySelectorAll('.card');
  var visible = 0;
  cards.forEach(function(card) {
    var tags = card.dataset.tags.split(',');
    var show = filter === 'all' || tags.indexOf(filter) !== -1;
    card.classList.toggle('hidden', !show);
    if (show) visible++;
  });
  ['featuredSection', 'moreSection'].forEach(function(id) {
    var grid = document.getElementById(id).querySelector('.grid');
    var visibleInSection = grid.querySelectorAll('.card:not(.hidden)').length;
    var existing = grid.querySelector('.empty-state');
    if (visibleInSection === 0) {
      if (!existing) {
        var tpl = document.getElementById('emptyTpl');
        grid.appendChild(tpl.content.cloneNode(true));
      }
    } else if (existing) {
      existing.remove();
    }
  });
  document.getElementById('showingCount').textContent =
    filter === 'all' ? 'Showing all ' + TOTAL + ' programs' : 'Showing ' + visible + ' of ' + TOTAL + ' programs';
}

document.querySelectorAll('.filter-pill').forEach(function(pill) {
  pill.addEventListener('click', function() {
    document.querySelectorAll('.filter-pill').forEach(function(p) {
      p.classList.remove('active');
      p.setAttribute('aria-selected', 'false');
    });
    pill.classList.add('active');
    pill.setAttribute('aria-selected', 'true');
    applyFilter(pill.dataset.filter);
  });
});
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

    var lines = [
      "Hi, I'd like to book a career call.",
      'Name: ' + name,
      'Phone: ' + phone,
      'Email: ' + email,
      'Experience: ' + experience,
      'Course: ' + courseLabel()
    ];
    if (message) lines.push('Message: ' + message);

    var url = 'https://wa.me/918708752385?text=' + encodeURIComponent(lines.join('\\n'));
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

FAVICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#1E3A8A"/><text x="16" y="22" font-family="Arial" font-size="16" font-weight="bold" fill="#EFF6FF" text-anchor="middle">A</text></svg>'


if __name__ == "__main__":
    generate()
