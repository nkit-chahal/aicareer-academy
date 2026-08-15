"""SEO helpers: canonical URLs, meta overrides, JSON-LD, robots, sitemap."""
from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path

SITE_ORIGIN = os.environ.get("SITE_ORIGIN", "https://aicareer.academy").rstrip("/")
BRAND = "AI Career Academy"
PHONE_DISPLAY = "+91 87087 52385"
PHONE_E164 = "+918708752385"
EMAIL = os.environ.get("SITE_EMAIL", "hello@aicareer.academy")
ORG_ID = f"{SITE_ORIGIN}/#org"

SEO_OVERRIDES = {
    "home": {
        "title": f"{BRAND} — Pick the job. Get the sequence.",
        "description": f"Choose an AI role and get the learning sequence: live programs, curriculum, published fees, and mentor-led projects. {BRAND}, Gurugram.",
    },
    "courses": {
        "title": f"AI and data programs — {BRAND}",
        "description": "Live instructor-led programs in data analytics, data science, machine learning, GenAI, MLOps, and agentic AI. Curriculum, fees, and career-call booking.",
    },
    "about-us": {
        "title": f"About {BRAND}",
        "description": f"{BRAND} is an engineering-first studio in Gurugram that maps AI careers to a learning sequence — live cohorts, projects, and practitioner mentors.",
    },
    "hire-from-us": {
        "title": f"Hire from {BRAND}",
        "description": f"Talk to {BRAND} about hiring learners trained on RAG, MLOps, and agentic workflows. Portfolios and practitioner-led projects — not a placement guarantee.",
    },
    "contact-us": {
        "title": f"Contact {BRAND}",
        "description": f"Reach {BRAND} in Gurugram: {PHONE_DISPLAY}, {EMAIL}, or WhatsApp. Mon–Sat, 10am–7pm IST.",
    },
    "enterprise": {
        "title": f"Enterprise AI upskilling — {BRAND}",
        "description": f"Role-based GenAI, LLM, agentic AI, and MLOps upskilling for teams. Talk to {BRAND} about cohort format and scope.",
    },
    "privacy": {
        "title": f"Privacy policy — {BRAND}",
        "description": f"How {BRAND} collects, uses, and stores enquiry and learning data. Contact {EMAIL} for requests.",
        "hero_title": "Privacy policy",
        "hero_sub": "What we collect when you enquire or learn with us, and how to reach us about it.",
    },
    "terms": {
        "title": f"Terms of service — {BRAND}",
        "description": f"Enrollment, payments, and use of {BRAND} programs and this website.",
        "hero_title": "Terms of service",
        "hero_sub": "How enrollment, fees, and use of this site work.",
    },
    "refund": {
        "title": f"Refund policy — {BRAND}",
        "description": "Fees are generally non-refundable after enrollment. Course transfer windows and what happens if we cancel a batch.",
        "hero_title": "Refund policy",
        "hero_sub": "Read this before you pay. Course fees are generally not refundable.",
    },
    "register": {
        "title": f"Book a career call — {BRAND}",
        "description": "Book a 15-minute career call on WhatsApp. Tell us your background and the role you want; we will map a sequence.",
    },
    "mentors": {
        "title": f"Mentors — {BRAND}",
        "description": f"Practitioner mentors at {BRAND}: Ankit, Prerna, Praveen, Aayush, Rahul Bhardwaj, and Vaibhav Sharma.",
    },
    "blogs": {
        "title": f"Blog — {BRAND}",
        "description": f"Short notes on AI career sequences, tools, and role maps from {BRAND}.",
        "hero_title": "Notes on AI careers",
        "hero_sub": "Role maps and tool stacks — written to help you choose a sequence, not to rank for ‘best institute’.",
    },
    "prog-data-science": {
        "title": f"Data Science course — {BRAND}",
        "description": "Live data science program: Python, SQL, statistics, ML, projects, and interview prep. See curriculum and fees on this page.",
    },
}

LEGAL_SECTIONS = {
    "privacy": [
        {
            "heading": "Who we are",
            "content": f"{BRAND} operates this website and the enquiry forms on it. For privacy requests email {EMAIL} or call {PHONE_DISPLAY}. Office: 68 Avenue, Badshahpur, Sector 68, Gurugram, Haryana 122101.",
        },
        {
            "heading": "What we collect",
            "content": "When you book a career call we collect the name, phone, email, experience level, and program interest you submit. WhatsApp then holds that conversation under Meta’s terms. We do not run a student login or store card numbers on this static site.",
        },
        {
            "heading": "How we use it",
            "content": "We use enquiry details to reply about programs, schedules, and fees. We do not sell your data. We may keep messages as long as needed to finish an enrolment conversation or to meet tax and dispute records.",
        },
        {
            "heading": "Your requests",
            "content": f"Email {EMAIL} to ask what we hold, to correct it, or to ask us to delete an enquiry we no longer need. We will say if the law requires us to keep a record.",
        },
    ],
    "refund": [
        {
            "heading": "Fees after enrollment",
            "content": "Any amount paid for a course, program, or service is not refundable. Read the program page (duration, curriculum, and fee) and talk to us before you pay.",
        },
        {
            "heading": "Installments",
            "content": "If you pay in installments, missed payments may pause access until the balance is cleared.",
        },
        {
            "heading": "Transfer to another course",
            "content": "Ask within 7 days of the batch start if you want to move to a different program. Transfers depend on seat availability and any fee difference.",
        },
        {
            "heading": "If we cancel or reschedule",
            "content": f"If {BRAND} cancels or moves a batch, you may transfer to another batch or course at no extra fee, or take credit toward a later program. We do not offer cash refunds in that case.",
        },
        {
            "heading": "Questions",
            "content": f"Write to {EMAIL} or call {PHONE_DISPLAY} before you pay if anything on a program page is unclear.",
        },
    ],
}


def pretty_path(output: str) -> str:
    if output == "index.html":
        return "/"
    if output.endswith("/index.html"):
        return "/" + output[: -len("/index.html")].strip("/") + "/"
    if output.endswith(".html"):
        return "/" + output
    return "/" + output.strip("/") + "/"


def canonical_url(page: dict) -> str:
    return SITE_ORIGIN + pretty_path(page["output"])


def is_noindex(page: dict) -> bool:
    return str(page.get("id", "")).startswith("city-") or page.get("noindex") is True


def sanitize_text(value: str) -> str:
    s = value
    s = s.replace("School of Core AI", BRAND)
    s = s.replace("Resonance AI", BRAND)
    s = re.sub(r"\bSCAI\b", BRAND, s)
    s = s.replace("hello@schoolofcoreai.com", EMAIL)
    s = s.replace("info@schoolofcoreai.com", EMAIL)
    s = s.replace("hello@resonanceai.com", EMAIL)
    s = s.replace("https://wa.me/9196914 40998", f"https://wa.me/{PHONE_E164.lstrip('+')}")
    s = s.replace("https://wa.me/919691440998", f"https://wa.me/{PHONE_E164.lstrip('+')}")
    s = s.replace("+91 96914 40998", PHONE_DISPLAY)
    s = s.replace("+919691440998", PHONE_E164)
    s = s.replace("96914 40998", "87087 52385")
    s = s.replace("9691440998", "8708752385")
    s = re.sub(r"\b100%\s+placement support\b", "placement support", s, flags=re.I)
    s = re.sub(r"\b100%\s+placement\b", "placement support", s, flags=re.I)
    s = re.sub(
        r"India['’]s (?:best|top-rated|top|most trusted|leading)(?: AI institute| institute)?",
        "an AI training studio",
        s,
        flags=re.I,
    )
    return s


def sanitize_tree(obj):
    if isinstance(obj, str):
        return sanitize_text(obj)
    if isinstance(obj, list):
        return [sanitize_tree(x) for x in obj]
    if isinstance(obj, dict):
        return {k: sanitize_tree(v) for k, v in obj.items()}
    return obj


def apply_overrides(page: dict, data: dict) -> dict:
    data = dict(data)
    extra = SEO_OVERRIDES.get(page["id"], {})
    for key in ("title", "description", "hero_title", "hero_sub"):
        if key in extra:
            data[key] = extra[key]
    if page["id"] in LEGAL_SECTIONS:
        data["sections"] = LEGAL_SECTIONS[page["id"]]
        data["raw_html"] = ""
    if page["id"] == "blogs":
        data["page_links"] = [
            {
                "href": "blogs/blog/ai-engineer-roadmap-2026/index.html",
                "title": "AI Engineer roadmap 2026: four paths",
            },
            {
                "href": "blogs/blog/data-science-tools-for-2026/index.html",
                "title": "Data science tools shaping 2026",
            },
        ]
    if page["id"] == "about-us":
        sections = []
        for section in data.get("sections") or []:
            item = dict(section)
            if item.get("heading") == "Numbers that reflect real outcomes":
                item["heading"] = "How we work"
                item["content"] = (
                    "We publish program curriculum and fees on each course page. "
                    "We do not list student counts or placement percentages we cannot show."
                )
            sections.append(item)
        data["sections"] = sections
    return data


def _format_title(raw: str, page: dict) -> str:
    if page.get("id") in SEO_OVERRIDES and SEO_OVERRIDES[page["id"]].get("title"):
        return SEO_OVERRIDES[page["id"]]["title"]
    if page.get("type") == "home":
        return SEO_OVERRIDES["home"]["title"]
    if not raw:
        return BRAND
    title = sanitize_text(raw.split("|")[0].strip())
    low = title.lower()
    if low in ("resonance ai", "the ai career institute", "ai career academy"):
        return BRAND
    if "ai career academy" not in low and "resonance ai" not in low:
        title += f" — {BRAND}"
    return title


def meta_description(data: dict, page: dict) -> str:
    desc = (data.get("description") or "").strip()
    desc = sanitize_text(desc)
    if not desc or desc.startswith("An engineering-first AI institution"):
        title = data.get("hero_title") or data.get("title") or BRAND
        desc = f"{sanitize_text(str(title).split('|')[0].strip())}. Live programs and career sequences from {BRAND}, Gurugram."
    return desc[:300]


def og_type(page: dict) -> str:
    if page.get("type") == "blog":
        return "article"
    return "website"


def breadcrumb_items(page: dict, data: dict) -> list[dict]:
    items = [{"name": "Home", "url": SITE_ORIGIN + "/"}]
    out = page.get("output", "")
    if out.startswith("courses/") and out != "courses/index.html":
        items.append({"name": "Programs", "url": SITE_ORIGIN + "/courses/"})
        items.append({"name": data.get("hero_title") or "Program", "url": canonical_url(page)})
    elif out.startswith("comparisons/") and out != "comparisons/index.html":
        items.append({"name": "Comparisons", "url": SITE_ORIGIN + "/comparisons/"})
        items.append({"name": data.get("hero_title") or "Comparison", "url": canonical_url(page)})
    elif out.startswith("roadmaps/"):
        items.append({"name": "Roadmaps", "url": SITE_ORIGIN + "/roadmaps/data-science-roadmap/"})
        items.append({"name": data.get("hero_title") or "Roadmap", "url": canonical_url(page)})
    elif out.startswith("blogs/") and out != "blogs/index.html":
        items.append({"name": "Blog", "url": SITE_ORIGIN + "/blogs/"})
        items.append({"name": data.get("hero_title") or "Article", "url": canonical_url(page)})
    elif page.get("type") != "home":
        items.append({"name": data.get("hero_title") or _format_title(data.get("title", ""), page), "url": canonical_url(page)})
    return items


def _offer(fees) -> dict | None:
    if not fees or not fees.get("display"):
        return None
    d = fees["display"]
    amount = None
    if d.get("mode") == "single":
        amount = d.get("current", {}).get("value")
    elif d.get("mode") == "discount":
        amount = d.get("current", {}).get("value")
    elif d.get("mode") == "dual_tier":
        amount = d.get("tier_a", {}).get("value")
    elif d.get("mode") == "dual_plan":
        amount = d.get("upfront", {}).get("value")
    if amount is None:
        return None
    numeric = re.sub(r"[^\d.]", "", str(amount))
    if not numeric:
        return None
    return {
        "@type": "Offer",
        "price": numeric,
        "priceCurrency": "INR",
        "availability": "https://schema.org/InStock",
        "url": None,
    }


def json_ld(page: dict, data: dict, fees=None) -> list:
    org = {
        "@type": "EducationalOrganization",
        "@id": ORG_ID,
        "name": BRAND,
        "url": SITE_ORIGIN + "/",
        "email": EMAIL,
        "telephone": PHONE_E164,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "68 Avenue, Badshahpur, Sector 68",
            "addressLocality": "Gurugram",
            "addressRegion": "Haryana",
            "postalCode": "122101",
            "addressCountry": "IN",
        },
    }
    graph = [
        org,
        {
            "@type": "WebSite",
            "@id": f"{SITE_ORIGIN}/#website",
            "url": SITE_ORIGIN + "/",
            "name": BRAND,
            "publisher": {"@id": ORG_ID},
        },
    ]
    crumbs = breadcrumb_items(page, data)
    if len(crumbs) >= 2:
        graph.append(
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": c["name"], "item": c["url"]}
                    for i, c in enumerate(crumbs)
                ],
            }
        )
    if page.get("type") == "program":
        course = {
            "@type": "Course",
            "name": data.get("hero_title") or data.get("title"),
            "description": meta_description(data, page),
            "provider": {"@id": ORG_ID},
            "url": canonical_url(page),
        }
        offer = _offer(fees)
        if offer:
            offer["url"] = canonical_url(page)
            course["offers"] = offer
        graph.append(course)
    faqs = data.get("faqs") or []
    if faqs and page.get("type") in ("program", "comparison", "blog"):
        graph.append(
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f.get("question", ""),
                        "acceptedAnswer": {"@type": "Answer", "text": f.get("answer", "")},
                    }
                    for f in faqs
                    if f.get("question") and f.get("answer")
                ],
            }
        )
    return {"@context": "https://schema.org", "@graph": graph}


def write_robots_and_sitemap(site: Path, pages: list[dict]) -> None:
    sitemap_url = f"{SITE_ORIGIN}/sitemap.xml"
    (site / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n",
        encoding="utf-8",
    )
    today = date.today().isoformat()
    urls = []
    for page in pages:
        if is_noindex(page):
            continue
        loc = canonical_url(page)
        urls.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>\n  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (site / "sitemap.xml").write_text(xml, encoding="utf-8")
    host = SITE_ORIGIN.replace("https://", "").replace("http://", "")
    (site / "_redirects").write_text(
        f"https://www.{host}/* https://{host}/:splat 301\n",
        encoding="utf-8",
    )
    (site / "_headers").write_text(
        "/*\n"
        "  X-Frame-Options: DENY\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n",
        encoding="utf-8",
    )
    (site / "vercel.json").write_text(
        '{\n'
        '  "trailingSlash": true,\n'
        '  "cleanUrls": false,\n'
        '  "headers": [\n'
        '    {\n'
        '      "source": "/(.*)",\n'
        '      "headers": [\n'
        '        { "key": "X-Frame-Options", "value": "DENY" },\n'
        '        { "key": "X-Content-Type-Options", "value": "nosniff" },\n'
        '        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        '}\n',
        encoding="utf-8",
    )


def write_404(site: Path, html: str) -> None:
    (site / "404.html").write_text(html, encoding="utf-8")
