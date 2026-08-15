#!/usr/bin/env python3
"""Post-scrape fee audit report."""
import json
import re
from pathlib import Path

from fees import extract_fees

BUILD = Path(__file__).parent
pages = json.load(open(BUILD / "pages.json", encoding="utf-8"))
programs = [p for p in pages["pages"] if p["type"] == "program"]
lines = ["| Program slug | Fees in JSON | Amounts | Notes |", "|---|---|---|---|"]
with_fees = 0
for p in sorted(programs, key=lambda x: x["source"]):
    slug = p["source"].split("/")[-1]
    data = json.load(open(BUILD / "data" / f"{p['id']}.json", encoding="utf-8"))
    fees = data.get("fees") or extract_fees(data)
    if fees and (fees.get("amounts") or fees.get("notes")):
        with_fees += 1
        status = "YES"
    elif fees and fees.get("plans"):
        status = "PARTIAL"
    else:
        status = "NO"
    amts = ", ".join(fees.get("amounts", [])) if fees else "-"
    notes = (fees.get("notes") or [""])[0][:60] if fees else "-"
    lines.append(f"| {slug} | {status} | {amts} | {notes} |")

lines.append("")
lines.append(f"Summary: {with_fees}/{len(programs)} programs with fee amounts or notes")
lines.append("")
lines.append("City pages:")
for p in pages["pages"]:
    if not p["id"].startswith("city-"):
        continue
    data = json.load(open(BUILD / "data" / f"{p['id']}.json", encoding="utf-8"))
    fees = data.get("fees")
    amts = fees.get("amounts", []) if fees else []
    lines.append(f"- {p['id']}: {amts or 'MISSING'}")

report = "\n".join(lines)
(BUILD / "fee_audit_after_rescrape.txt").write_text(report, encoding="utf-8")
print(f"Wrote fee_audit_after_rescrape.txt ({with_fees}/{len(programs)} programs with fees)")
