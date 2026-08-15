"""Resolve nested Course Curriculum trees for program and roadmap pages.

Scraped JSON is mostly flat (marketing lists + heading/paragraph sections).
This module:
  1. Tries to parse nested modules from raw_html (details, h2/h3, lists).
  2. Prefers authored trees in curricula.json keyed by slug.
  3. Falls back to program topics + usable list items.
"""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

BUILD = Path(__file__).parent
AUTHORED_PATH = BUILD / "curricula.json"

SKIP_HEADINGS = {
    "frequently asked questions",
    "faq",
    "ready to start",
    "have questions",
    "what you'll learn",
    "why learners",
    "job assistance",
}

SKIP_LIST_RE = re.compile(
    r"job assistance|placement program|mentor-led|we don.?t|contact us|register now",
    re.I,
)


class _OutlineParser(HTMLParser):
    """Collect h2/h3, details/summary, and list items in document order."""

    def __init__(self):
        super().__init__()
        self.events: list[tuple] = []
        self._tag_stack: list[str] = []
        self._capture = ""
        self._in_capture = False
        self._details_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self._tag_stack.append(tag)
        if tag == "details":
            self.events.append(("details_open", self._details_depth))
            self._details_depth += 1
        if tag in ("h2", "h3", "summary", "li"):
            self._in_capture = True
            self._capture = ""

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ("h2", "h3", "summary", "li") and self._in_capture:
            text = _clean(self._capture)
            if text:
                self.events.append((tag, text))
            self._in_capture = False
            self._capture = ""
        if tag == "details":
            self._details_depth = max(0, self._details_depth - 1)
            self.events.append(("details_close", self._details_depth))
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
        elif tag in self._tag_stack:
            self._tag_stack.reverse()
            self._tag_stack.remove(tag)
            self._tag_stack.reverse()

    def handle_data(self, data):
        if self._in_capture:
            self._capture += data


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    text = text.replace("\u00a0", " ")
    return text


def _skip_heading(text: str) -> bool:
    low = text.lower().strip()
    if len(low) < 3 or len(low) > 120:
        return True
    return any(s in low for s in SKIP_HEADINGS)


def parse_html_curriculum(raw_html: str) -> dict | None:
    if not raw_html or len(raw_html) < 80:
        return None
    parser = _OutlineParser()
    try:
        parser.feed(raw_html)
    except Exception:
        return None

    levels: list[dict] = []
    current_level: dict | None = None
    current_module: dict | None = None
    details_stack: list[str] = []

    def flush_module():
        nonlocal current_module, current_level
        if current_module and current_level is not None:
            if current_module.get("topics") or current_module.get("modules"):
                current_level.setdefault("modules", []).append(current_module)
        current_module = None

    def flush_level():
        nonlocal current_level
        flush_module()
        if current_level and (current_level.get("modules") or current_level.get("topics")):
            levels.append(current_level)
        current_level = None

    for kind, payload in parser.events:
        if kind == "h2":
            if _skip_heading(payload):
                continue
            flush_level()
            current_level = {"title": payload, "modules": []}
        elif kind == "h3":
            if _skip_heading(payload):
                continue
            if current_level is None:
                current_level = {"title": "Curriculum", "modules": []}
            flush_module()
            current_module = {"title": payload, "topics": []}
        elif kind == "summary":
            if _skip_heading(payload):
                continue
            details_stack.append(payload)
            if current_level is None:
                current_level = {"title": payload, "modules": []}
            elif current_module is None:
                current_module = {"title": payload, "topics": []}
        elif kind == "details_close":
            if details_stack:
                details_stack.pop()
            if payload == 0:
                flush_level()
            else:
                flush_module()
        elif kind == "li":
            if SKIP_LIST_RE.search(payload) or len(payload) > 180:
                continue
            if current_module is not None:
                current_module.setdefault("topics", []).append(payload)
            elif current_level is not None:
                if current_level.get("modules"):
                    last = current_level["modules"][-1]
                    last.setdefault("topics", []).append(payload)
                else:
                    current_level.setdefault("topics", []).append(payload)

    flush_level()
    levels = [lv for lv in levels if _level_weight(lv) >= 2]
    if not levels:
        return None
    return {"title": "Course Curriculum", "levels": levels[:12], "source": "html"}


def parse_roadmap_cards(raw_html: str) -> dict | None:
    """Roadmap pages encode modules as font-semibold titles + comma topic lines."""
    if not raw_html:
        return None
    stages = re.findall(
        r"<h3[^>]*>([^<]+)</h3>",
        raw_html,
        flags=re.I,
    )
    modules = re.findall(
        r'text-sm font-semibold[^>]*>([^<]+)</div>\s*<p[^>]*>([^<]+)</p>',
        raw_html,
        flags=re.I,
    )
    if len(modules) < 3:
        return None

    seen = set()
    unique_modules: list[tuple[str, str]] = []
    for title, topics in modules:
        title = _clean(title)
        topics = _clean(topics)
        if not title or title in seen or len(title) > 80:
            continue
        seen.add(title)
        unique_modules.append((title, topics))

    stage_titles = []
    for s in stages:
        s = _clean(s)
        if s and s.lower() not in {t.lower() for t in stage_titles} and not _skip_heading(s):
            stage_titles.append(s)

    if not unique_modules:
        return None

    levels = []
    if stage_titles:
        chunk = max(1, round(len(unique_modules) / max(len(stage_titles), 1)))
        idx = 0
        for i, st in enumerate(stage_titles[:10]):
            take = unique_modules[idx : idx + chunk]
            if i == len(stage_titles) - 1:
                take = unique_modules[idx:]
            idx += chunk
            if not take:
                continue
            levels.append({
                "title": st,
                "modules": [
                    {
                        "title": t,
                        "topics": [p.strip() for p in topics.split(",") if p.strip()][:8],
                    }
                    for t, topics in take
                ],
            })
    else:
        levels.append({
            "title": "Full roadmap",
            "modules": [
                {
                    "title": t,
                    "topics": [p.strip() for p in topics.split(",") if p.strip()][:8],
                }
                for t, topics in unique_modules
            ],
        })

    if _tree_weight({"levels": levels}) < 4:
        return None
    return {"title": "Full roadmap", "levels": levels, "source": "html"}


def _level_weight(level: dict) -> int:
    n = len(level.get("topics") or [])
    for m in level.get("modules") or []:
        n += 1 + len(m.get("topics") or [])
    return n


def _tree_weight(tree: dict | None) -> int:
    if not tree:
        return 0
    return sum(_level_weight(lv) for lv in tree.get("levels") or [])


def load_authored() -> dict:
    if not AUTHORED_PATH.exists():
        return {}
    with open(AUTHORED_PATH, encoding="utf-8") as f:
        return json.load(f)


def fallback_from_program(program: dict | None, data: dict) -> dict | None:
    topics = list((program or {}).get("topics") or [])
    extra = []
    for lst in (data.get("lists") or [])[:2]:
        for item in lst:
            item = _clean(item)
            if not item or SKIP_LIST_RE.search(item) or len(item) > 120:
                continue
            extra.append(item)
    items = topics + [e for e in extra if e not in topics]
    if len(items) < 3:
        return None

    slug = (program or {}).get("slug", "") or ""
    pythonish = any(
        k in slug
        for k in (
            "data-science",
            "data-analytics",
            "machine-learning",
            "full-stack",
            "ai-course-with-placement",
        )
    )
    if pythonish:
        basics = items[: max(3, len(items) // 2)]
        rest = items[len(basics) :]
        levels = [
            {
                "title": "Python Basics",
                "modules": [
                    {"title": "Module 1: Language foundations", "topics": basics[:4] or basics},
                    {
                        "title": "Module 7: Time and Space Complexity",
                        "topics": [
                            "Understanding Algorithm Efficiency",
                            "Time Complexity",
                            "Space Complexity",
                        ],
                    },
                ],
            },
            {
                "title": "Python Advanced",
                "modules": [
                    {"title": "Applied Python for this program", "topics": rest[:6] or basics},
                ],
            },
        ]
        if "analytics" in slug:
            levels.append({
                "title": "Introduction to Excel",
                "modules": [
                    {
                        "title": "Spreadsheets for analysis",
                        "topics": ["Formulas and references", "Pivot tables", "Charts and dashboards"],
                    }
                ],
            })
        return {"title": "Course Curriculum", "levels": levels, "source": "fallback"}

    # Generic: one level per topic cluster
    mid = max(2, (len(items) + 1) // 2)
    clusters = [items[:mid], items[mid:]]
    levels = []
    for i, cluster in enumerate(clusters, 1):
        if not cluster:
            continue
        modules = []
        for j, topic in enumerate(cluster, 1):
            modules.append({"title": f"Module {j}: {topic}", "topics": [topic]})
        levels.append({"title": f"Part {i}", "modules": modules})
    return {"title": "Course Curriculum", "levels": levels, "source": "fallback"}


def fallback_from_roadmap_sections(data: dict) -> dict | None:
    sections = data.get("sections") or []
    stage_like = []
    for sec in sections:
        heading = _clean(sec.get("heading") or "")
        content = _clean(sec.get("content") or "")
        if not heading or _skip_heading(heading):
            continue
        if re.match(r"^\d", content) or "week" in content.lower() or len(content) < 40:
            stage_like.append((heading, content))
    if len(stage_like) < 3:
        return None
    levels = []
    for heading, content in stage_like:
        levels.append({
            "title": heading,
            "modules": [
                {
                    "title": heading,
                    "topics": [t.strip() for t in re.split(r"[.;]", content) if t.strip() and len(t.strip()) > 8][:6]
                    or [content],
                }
            ],
        })
    return {"title": "Full roadmap", "levels": levels, "source": "fallback"}


def page_slug(page: dict) -> str:
    source = (page.get("source") or "").strip("/")
    return source.split("/")[-1] if source else page.get("id", "")


def resolve_curriculum(page: dict, data: dict, program: dict | None = None) -> dict | None:
    authored = load_authored()
    slug = page_slug(page)
    if program and program.get("slug"):
        slug = program["slug"]

    html_tree = None
    raw = data.get("raw_html") or ""
    if page.get("id", "").startswith("roadmap") or "roadmap" in slug:
        html_tree = parse_roadmap_cards(raw) or parse_html_curriculum(raw)
    else:
        html_tree = parse_html_curriculum(raw)

    authored_tree = authored.get(slug)
    if authored_tree:
        tree = dict(authored_tree)
        tree.setdefault("title", "Course Curriculum")
        tree["source"] = "authored"
        return tree

    if html_tree and _tree_weight(html_tree) >= 4:
        return html_tree

    if page.get("type") == "program" or (program is not None):
        return fallback_from_program(program, data)

    if page.get("id", "").startswith("roadmap") or "roadmap" in slug:
        return fallback_from_roadmap_sections(data) or html_tree

    return html_tree
