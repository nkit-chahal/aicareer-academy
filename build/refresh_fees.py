#!/usr/bin/env python3
"""Refresh fee fields in cached JSON — re-fetch live HTML or apply verified manifest."""

import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from fees import extract_city_fees, extract_fees

BUILD = Path(__file__).parent
DATA_DIR = BUILD / "data"
BASE_URL = "https://schoolofcoreai.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html",
}

# Verified from live schoolofcoreai.com (Jul 2026) when scrape network unavailable
VERIFIED_FEES = {
    "prog-ai-developers": {
        "amounts": ["₹40,000"],
        "plans": ["No hidden charges. Batch timings confirmed on call."],
        "notes": ["One-time payment for 3 months live ILT with capstone and certificate."],
        "amount_notes": ["One-time payment"],
    },
    "prog-mlops": {
        "amounts": ["₹60,000"],
        "plans": ["One-time payment for 5-month live instructor-led program."],
        "notes": ["MLOps course fees are ₹60,000 for live instructor-led training with capstone and certificate."],
        "amount_notes": ["One-time payment"],
    },
    "prog-data-science": {
        "amounts": ["₹55,000", "₹65,000"],
        "plans": ["Flat ₹10,000 OFF — Pay ₹55,000 all-inclusive. No hidden charges.", "EMI options available"],
        "notes": ["Limited-time discount: course fee ₹65,000 minus ₹10,000; you pay ₹55,000."],
        "amount_notes": ["One-time payment"],
    },
    "prog-ds-ml": {
        "amounts": ["₹39,999"],
        "plans": ["One-time payment with placement assurance."],
        "notes": [],
        "amount_notes": ["One-time payment"],
    },
    "prog-ds-dl": {
        "amounts": ["₹49,999", "₹44,999"],
        "plans": ["Pay ₹49,999 now and ₹44,999 once you secure a job."],
        "notes": ["Dual-plan fee structure with post-placement component."],
        "amount_notes": ["Post-placement payment"],
    },
    "prog-dl-spec": {
        "amounts": ["₹74,999"],
        "plans": ["One-time payment with placement assurance."],
        "notes": [],
        "amount_notes": ["One-time payment"],
    },
    "prog-cv": {
        "amounts": ["₹74,999"],
        "plans": ["One-time payment with placement assurance."],
        "notes": [],
        "amount_notes": ["One-time payment"],
    },
    "prog-nlp": {
        "amounts": ["₹64,999"],
        "plans": ["One-time payment with placement assurance."],
        "notes": ["NLP course one-time fee with refund assurance if placement not achieved."],
        "amount_notes": ["One-time payment"],
    },
    "prog-full-stack-ds": {
        "amounts": ["₹89,999", "₹54,999"],
        "plans": ["Pay ₹89,999 now and ₹54,999 once you secure a job."],
        "notes": ["Dual-plan full stack data science fee structure."],
        "amount_notes": ["Post-placement payment"],
    },
    "prog-ai-engineering": {
        "amounts": [],
        "plans": [],
        "notes": ["No standalone fee on source site — detailed syllabus and fees are on the Generative AI Course page (₹64,999)."],
        "amount_notes": [],
    },
    "prog-fde": {
        "amounts": [],
        "plans": [],
        "notes": ["No published fee on source site — 6-month program; contact admissions for pricing."],
        "amount_notes": [],
    },
    "prog-data-analytics": {
        "amounts": ["₹40,000"],
        "plans": [
            "Flexible batches: classroom or live virtual (same fee)",
            "EMI options available • Pay in 2 installments • No hidden charges",
        ],
        "notes": ["One-time fee inclusive of training, projects, certification and placement support."],
        "amount_notes": ["One-time payment"],
    },
    "city-bangalore": {
        "amounts": ["₹55,000"],
        "plans": ["EMI and part-payment options available with counsellor."],
        "notes": ["Data Science Course Fees in Bangalore: total course fee ₹55,000; final fee and EMI confirmed by counsellor."],
        "amount_notes": [],
    },
    "city-pune": {
        "amounts": ["₹55,000"],
        "plans": ["EMI and part-payment options available with counsellor."],
        "notes": ["City page references transparent fee and EMI plans; main course fee aligns with Data Science Course (₹55,000)."],
        "amount_notes": [],
    },
    "city-delhi": {
        "amounts": ["₹55,000"],
        "plans": ["EMI and part-payment options available with counsellor."],
        "notes": ["Data Science Course Fee in Delhi: total course fee ₹55,000; final fee and EMI confirmed by counsellor."],
        "amount_notes": [],
    },
    "city-hyderabad": {
        "amounts": ["₹55,000"],
        "plans": ["EMI and part-payment options available with counsellor."],
        "notes": ["Data Science city page fee aligns with main Data Science Course (₹55,000); EMI confirmed by counsellor."],
        "amount_notes": [],
    },
}


def fetch_html(source: str) -> str | None:
    url = BASE_URL + source
    try:
        resp = requests.get(url, headers=HEADERS, timeout=45)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  fetch failed {source}: {e}")
        return None


def main(use_manifest_only: bool = False):
    pages = json.load(open(BUILD / "pages.json", encoding="utf-8"))
    targets = [
        p for p in pages["pages"]
        if p["type"] == "program" or p["id"].startswith("city-")
    ]
    updated = 0
    for page in targets:
        pid = page["id"]
        path = DATA_DIR / f"{pid}.json"
        if not path.exists():
            continue
        data = json.load(open(path, encoding="utf-8"))
        fees = None

        if not use_manifest_only:
            html = fetch_html(page["source"])
            if html:
                soup = BeautifulSoup(html, "lxml")
                main = soup.find("main") or soup.find("article")
                if main:
                    full_html = str(main)
                    payload = {**data, "_full_html": full_html, "raw_html": full_html[:50000]}
                    fees = extract_city_fees(payload) if pid.startswith("city-") else extract_fees(payload)
            time.sleep(0.5)

        if not fees or not (fees.get("amounts") or fees.get("notes")):
            # Try improved extraction on existing cached fields
            fees = extract_city_fees(data) if pid.startswith("city-") else extract_fees(data)

        if not fees or not (fees.get("amounts") or fees.get("notes")):
            fees = VERIFIED_FEES.get(pid) or fees

        if fees and (fees.get("amounts") or fees.get("notes") or fees.get("plans")):
            data["fees"] = fees
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            updated += 1
            print(f"  updated {pid}: amounts={len(fees.get('amounts', []))}")
        else:
            print(f"  no fees {pid}")

    print(f"\nUpdated {updated} pages")


if __name__ == "__main__":
    import sys
    main(use_manifest_only="--manifest-only" in sys.argv)
