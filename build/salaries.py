"""Extract and format salary / pay band data from scraped page data."""

from __future__ import annotations

import html
import re

from bs4 import BeautifulSoup

EXP_TIER_RE = re.compile(
    r"(?P<exp>\d[+–\-]?\d*\+?\s*yrs?)\s+(?P<range>\d+\s*[–\-]\s*\d+(?:\+)?)\s*(?:₹\s*)?LPA",
    re.I,
)
BADGE_TIER_RE = re.compile(
    r"₹([\d]+[–\-][\d]+(?:\+)?)\s*LPA\s*\(([^)]+)\)",
    re.I,
)
SALARY_HEADING_RE = re.compile(
    r"salary|LPA|pay band|compensation|indicative salary",
    re.I,
)


def _text(el) -> str:
    if el is None:
        return ""
    return re.sub(r"\s+", " ", el.get_text(separator=" ", strip=True)).strip()


def _parse_tiers(text: str) -> list[dict]:
    tiers: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for m in EXP_TIER_RE.finditer(text or ""):
        exp = m.group("exp").replace("-", "–")
        rng = re.sub(r"\s+", " ", m.group("range"))
        key = (exp, rng)
        if key not in seen:
            seen.add(key)
            tiers.append({"experience": exp, "india_lpa": rng})
    return tiers


def _parse_badge_tiers(text: str) -> list[dict]:
    tiers: list[dict] = []
    for m in BADGE_TIER_RE.finditer(text or ""):
        tiers.append({"experience": m.group(2).strip(), "india_lpa": m.group(1).strip()})
    return tiers


def _find_salary_section(soup: BeautifulSoup):
    for sec in soup.find_all("section"):
        label = sec.get("aria-label", "")
        if re.search(r"salari", label, re.I):
            return sec
    for h2 in soup.find_all(["h2", "h3"]):
        if SALARY_HEADING_RE.search(_text(h2)):
            parent = h2.find_parent("section")
            if parent:
                return parent
            block = h2.find_parent("div", class_=True) or h2.parent
            if block and _parse_tiers(_text(block)):
                return block
    return None


def _extract_roles(section) -> list[dict]:
    roles: list[dict] = []
    skip_titles = {"salary by experience", "how to reach the top band (fast)"}

    cards = section.find_all("button")
    if not cards:
        for grid in section.find_all("div", class_=re.compile(r"grid")):
            cards = [
                child
                for child in grid.find_all("div", recursive=False)
                if child.find("h4") and _parse_tiers(_text(child))
            ]
            if cards:
                break

    for card in cards:
        h4 = card.find("h4")
        if not h4:
            continue
        name = _text(h4)
        if name.lower() in skip_titles:
            continue
        tiers = _parse_tiers(_text(card))
        if not tiers:
            continue
        note = ""
        for p in card.find_all("p"):
            t = _text(p)
            if t and len(t) < 120 and "LPA" not in t:
                note = t
                break
        roles.append({"name": name, "tiers": tiers, "note": note})

    seen: set[str] = set()
    unique: list[dict] = []
    for role in roles:
        if role["name"] not in seen:
            seen.add(role["name"])
            unique.append(role)
    return unique


def _extract_from_html(html: str) -> dict | None:
    if not html:
        return None
    soup = BeautifulSoup(html, "lxml")
    section = _find_salary_section(soup)
    if not section:
        # Badge-style bands (e.g. ML course spans)
        for h3 in soup.find_all(["h2", "h3", "h4"]):
            if not SALARY_HEADING_RE.search(_text(h3)):
                continue
            block = h3.find_parent("div") or h3.parent
            tiers = _parse_badge_tiers(_text(block))
            if tiers:
                return {
                    "title": _text(h3),
                    "subtitle": "",
                    "intro": "",
                    "roles": [],
                    "experience_table": tiers,
                    "footnote": "",
                    "tips_heading": "",
                    "tips": [],
                }
        return None

    result: dict = {
        "title": "",
        "subtitle": "",
        "intro": "",
        "roles": [],
        "experience_table": [],
        "footnote": "",
        "tips_heading": "",
        "tips": [],
    }

    h2 = section.find("h2")
    if h2:
        result["title"] = _text(h2)
    for h3 in section.find_all("h3"):
        t = _text(h3)
        if t and t != result["title"]:
            result["subtitle"] = t
            break
    for p in section.find_all("p"):
        t = _text(p)
        if len(t) > 40 and "LPA" not in t and "Source:" not in t:
            result["intro"] = t
            break

    result["roles"] = _extract_roles(section)

    for h4 in section.find_all("h4"):
        label = _text(h4).lower()
        if "salary by experience" in label:
            container = h4.find_parent("div") or h4.parent
            result["experience_table"] = _parse_tiers(_text(container))
            for fp in container.find_all("p"):
                ft = _text(fp)
                if "vary" in ft.lower() or "company" in ft.lower():
                    result["footnote"] = ft
        elif "how to reach" in label:
            result["tips_heading"] = _text(h4)
            ul = h4.find_next("ul")
            if ul:
                result["tips"] = [_text(li) for li in ul.find_all("li") if _text(li)]

    if not result["roles"] and not result["experience_table"]:
        tiers = _parse_tiers(_text(section))
        if tiers:
            result["experience_table"] = tiers
            if not result["title"]:
                result["title"] = "Salary by experience"

    if not result["roles"] and not result["experience_table"]:
        return None
    return result


def _extract_from_sections(sections: list) -> dict | None:
    title = ""
    intro = ""
    experience_table: list[dict] = []
    footnote = ""
    tips_heading = ""
    tips: list[str] = []

    for sec in sections:
        heading = sec.get("heading", "")
        content = sec.get("content", "")
        if not SALARY_HEADING_RE.search(heading) and not _parse_tiers(content):
            continue
        tiers = _parse_tiers(content)
        if tiers and len(tiers) >= 2:
            if SALARY_HEADING_RE.search(heading):
                title = heading
            experience_table = tiers
            rest = EXP_TIER_RE.sub("", content)
            if "vary" in rest.lower():
                footnote = rest.strip()[:300]
        elif "India (₹ LPA)" in content:
            intro = content.split("India (₹ LPA)")[0].strip()
            if SALARY_HEADING_RE.search(heading):
                title = heading.replace("plus ", "").strip()

    if not experience_table:
        return None
    return {
        "title": title or "Salary by experience",
        "subtitle": "",
        "intro": intro,
        "roles": [],
        "experience_table": experience_table,
        "footnote": footnote,
        "tips_heading": tips_heading,
        "tips": tips,
    }


def extract_salaries(data: dict) -> dict | None:
    """Return structured salary data from scraped page fields."""
    html = data.get("_full_html") or data.get("raw_html", "")
    if html:
        result = _extract_from_html(html)
        if result:
            return result
    return _extract_from_sections(data.get("sections", []))


def is_salary_section(heading: str, content: str) -> bool:
    """True when a flat section should be rendered by the salary block instead."""
    if SALARY_HEADING_RE.search(heading or ""):
        return True
    if "India (₹ LPA)" in (content or "") and "Global ($ /yr)" in (content or ""):
        return True
    if len(_parse_tiers(content or "")) >= 2:
        return True
    return False


def filter_sections(sections: list, salaries: dict | None) -> list:
    """Remove sections superseded by structured salary rendering."""
    if not salaries:
        return sections
    return [
        s
        for s in sections
        if not is_salary_section(s.get("heading", ""), s.get("content", ""))
    ]


def format_section_html(content: str) -> str | None:
    """Convert inline salary tier blobs into a table."""
    tiers = _parse_tiers(content)
    if len(tiers) < 2:
        return None
    remainder = EXP_TIER_RE.sub("", content).strip()
    remainder = re.sub(r"Salary by Experience\s*", "", remainder, flags=re.I).strip()
    parts = [render_tier_table(tiers, caption="Salary by experience")]
    if remainder:
        parts.append(f'<p class="prog-salary-footnote">{html.escape(remainder)}</p>')
    return "\n".join(parts)


def render_tier_table(tiers: list[dict], caption: str = "", global_col: bool = False) -> str:
    cols = ["Experience", "India (₹ LPA)"]
    if global_col:
        cols.append("Global ($/yr)")
    rows = []
    for i, tier in enumerate(tiers):
        cls = "prog-salary-row-alt" if i % 2 else ""
        cells = [
            f'<td class="prog-salary-exp">{html.escape(tier["experience"])}</td>',
            f'<td class="prog-salary-amt">{html.escape(tier.get("india_lpa", "—"))}</td>',
        ]
        if global_col:
            cells.append(
                f'<td class="prog-salary-amt">{html.escape(tier.get("global_usd", "—"))}</td>'
            )
        rows.append(f'<tr class="{cls}">{"".join(cells)}</tr>')
    cap = f'<caption class="prog-salary-caption">{html.escape(caption)}</caption>' if caption else ""
    thead = "".join(f"<th scope=\"col\">{html.escape(c)}</th>" for c in cols)
    return (
        f'<div class="prog-salary-table-wrap"><table class="prog-salary-table">{cap}'
        f"<thead><tr>{thead}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def render_role_cards(roles: list[dict]) -> str:
    cards = []
    for role in roles:
        tier_rows = "".join(
            f'<div class="prog-salary-card-tier">'
            f'<span class="prog-salary-exp">{html.escape(t["experience"])}</span>'
            f'<span class="prog-salary-amt">{html.escape(t["india_lpa"])} ₹ LPA</span>'
            f"</div>"
            for t in role.get("tiers", [])
        )
        note = (
            f'<p class="prog-salary-card-note">{html.escape(role["note"])}</p>'
            if role.get("note")
            else ""
        )
        cards.append(
            f'<article class="prog-salary-card">'
            f'<h3 class="prog-salary-card-title">{html.escape(role["name"])}</h3>'
            f'{tier_rows}{note}</article>'
        )
    return f'<div class="prog-salary-cards">{"".join(cards)}</div>'
