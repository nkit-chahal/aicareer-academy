"""Extract course fee amounts and payment plans from scraped page data."""

from __future__ import annotations

import re


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"&[#\w]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _normalize_html(text: str) -> str:
    text = text or ""
    text = text.replace("&#8377;", "₹").replace("&#x20b9;", "₹").replace("&rupee;", "₹")
    return text


def _valid_plan(text: str) -> bool:
    if len(text) < 12 or len(text) > 220:
        return False
    low = text.lower()
    if any(
        x in low
        for x in (
            "semibold",
            "class=",
            "max-w-",
            "text-[",
            "aria-",
            "button",
            "href=",
            "rounded",
            "shadow-md",
            "opacity",
            "academic as the",
            "contact us and our academic",
            "encouraging the dissemination",
            "they manage and scale data",
        )
    ):
        return False
    if ">" in text or '"' in text:
        return False
    return any(
        k in low
        for k in (
            "emi",
            "installment",
            "one-time",
            "one time",
            "hidden charge",
            "same fee",
            "payment",
            "post placement",
            "placement assurance",
            "pay in",
            "no hidden",
            "flexible",
            "part-payment",
            "counsellor",
        )
    )


def _collect_text_parts(data: dict) -> str:
    parts = []
    for section in data.get("sections", []):
        parts.append(section.get("heading", ""))
        parts.append(section.get("content", ""))
    for faq in data.get("faqs", []):
        parts.append(faq.get("question", ""))
        parts.append(faq.get("answer", ""))
    for lst in data.get("lists", []):
        for item in lst:
            parts.append(item)
    return "\n".join(parts)


def _find_amounts(text: str) -> tuple[list[str], list[str]]:
    amounts: list[str] = []
    amount_notes: list[str] = []
    for m in re.finditer(r"₹([\d,]+)", text):
        val = int(m.group(1).replace(",", ""))
        if val < 1000:
            continue
        amounts.append(f"₹{m.group(1)}")
        ctx = _clean(text[m.end() : m.end() + 40]).lower()
        if "one-time" in ctx or "one time" in ctx:
            amount_notes.append("One-time payment")
        if "post placement" in ctx:
            amount_notes.append("Post-placement payment")
    return list(dict.fromkeys(amounts)), list(dict.fromkeys(amount_notes))


def _find_fee_section_snippets(text: str) -> list[str]:
    notes: list[str] = []
    patterns = [
        r"(?i)the fee is ₹[\d,]+[^.<]{0,120}",
        r"(?i)(?:course|program|total)\s+fee[^.]{0,120}₹[\d,]+[^.]{0,80}",
        r"(?i)pay ₹[\d,]+[^.]{0,100}",
        r"(?i)₹[\d,]+\s*(?:\(one-time\)|one-time|all-inclusive)[^.]{0,80}",
        r"(?i)(?:duration|months?)\s*[·•|]\s*fee[^|]{0,40}₹[\d,]+",
        r"(?i)₹[\d,]+\s*\+\s*₹[\d,]+[^.]{0,80}",
        r"(?i)fees?(?:\s+are|\s+is|\s+for)?[^.]{0,40}₹[\d,]+[^.]{0,80}",
        r"(?i)₹[\d,]+\s+now\s+and\s+₹[\d,]+[^.]{0,80}",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text):
            note = _clean(m.group())
            if note and len(note) > 12 and "class=" not in note and "<" not in note:
                notes.append(note)
    return list(dict.fromkeys(notes))[:4]


def _find_plans(text: str) -> list[str]:
    plans: list[str] = []
    for item in text.split("\n"):
        item = _clean(item)
        if _valid_plan(item):
            plans.append(item)
    for m in re.finditer(
        r"(?i)(?:emi options|pay in \d+ installments|no hidden charges|flexible batches[^.]{0,80}|"
        r"one-time payment with placement assurance|post placement[^.]{0,80}|"
        r"flat ₹[\d,]+ off[^.]{0,80}|transparent fees[^.]{0,80})",
        text,
    ):
        plan = _clean(m.group())
        if plan and _valid_plan(plan):
            plans.append(plan)
    return list(dict.fromkeys(plans))[:4]


def _amounts_near_fee_headings(html: str) -> list[str]:
    """Find ₹ amounts in HTML blocks headed by fee/pricing labels."""
    amounts: list[str] = []
    html = _normalize_html(html)
    for m in re.finditer(
        r"(?is)(?:course\s+fees?|fee\s+structure|program\s+fee|total\s+course\s+fee|pricing)[^<]{0,800}",
        html,
    ):
        block = m.group()
        for amt in re.findall(r"₹([\d,]+)", block):
            val = int(amt.replace(",", ""))
            if val >= 1000:
                amounts.append(f"₹{amt}")
        # Numbers without rupee symbol near fee headings (e.g. "49,999 + ₹44,999")
        if not re.search(r"₹", block):
            for amt in re.findall(r"(?<![\d])([\d]{2,3},[\d]{3})(?![\d])", block):
                val = int(amt.replace(",", ""))
                if val >= 5000:
                    amounts.append(f"₹{amt}")
    return list(dict.fromkeys(amounts))


def _amounts_from_tables(html: str) -> list[str]:
    amounts: list[str] = []
    html = _normalize_html(html)
    for m in re.finditer(r"(?i)duration[^|]{0,20}fee[^|]{0,40}₹[\d,]+", _clean(html)):
        for amt in re.findall(r"₹([\d,]+)", m.group()):
            amounts.append(f"₹{amt}")
    return list(dict.fromkeys(amounts))


def extract_fees(data: dict) -> dict | None:
    """Pull course fee amounts and payment plans from structured scrape or raw_html."""
    combined = _collect_text_parts(data)
    raw = _normalize_html(data.get("raw_html", ""))
    full_html = _normalize_html(data.get("_full_html", "")) or raw

    texts = [combined, raw, full_html]
    amounts: list[str] = []
    amount_notes: list[str] = []
    notes: list[str] = []
    plans: list[str] = []

    for text in texts:
        a, n = _find_amounts(text)
        amounts.extend(a)
        amount_notes.extend(n)
        notes.extend(_find_fee_section_snippets(text))
        plans.extend(_find_plans(text))

    amounts.extend(_amounts_near_fee_headings(full_html))
    amounts.extend(_amounts_from_tables(full_html))

    amounts = list(dict.fromkeys(amounts))
    amount_notes = list(dict.fromkeys(amount_notes))
    notes = list(dict.fromkeys(notes))
    plans = list(dict.fromkeys(plans))[:4]

    # Filter salary-range false positives (keep course-scale fees)
    if amounts:
        filtered = []
        for amt in amounts:
            val = int(amt.replace("₹", "").replace(",", ""))
            if val <= 200000:
                filtered.append(amt)
        amounts = filtered or amounts

    if not amounts and not notes:
        if plans and any(k in p.lower() for p in plans for k in ("emi", "installment", "hidden charge", "same fee")):
            return {"amounts": [], "plans": plans, "notes": [], "amount_notes": amount_notes}
        return None

    return {"amounts": amounts, "plans": plans, "notes": notes, "amount_notes": amount_notes}


def extract_city_fees(data: dict) -> dict | None:
    """Extract fee block from city landing pages."""
    raw = _normalize_html(data.get("raw_html", ""))
    full = _normalize_html(data.get("_full_html", "")) or raw
    fees = extract_fees({**data, "raw_html": full, "_full_html": full})
    if fees and (fees.get("amounts") or fees.get("notes")):
        return fees

    for html in (full, raw):
        m = re.search(
            r"(?is)(?:data science course fees[^<]{0,120}|fee and emi plans[^<]{0,120}).{0,1200}",
            html,
        )
        if m:
            block = _clean(m.group())
            amounts, amount_notes = _find_amounts(block)
            notes = _find_fee_section_snippets(block)
            if amounts or notes:
                return {
                    "amounts": amounts,
                    "plans": _find_plans(block),
                    "notes": notes or [block[:240]],
                    "amount_notes": amount_notes,
                }
    return fees
