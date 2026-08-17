"""SEO helpers: canonical URLs, meta overrides, JSON-LD, robots, sitemap."""
from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path

from program_copy import PROGRAM_COPY

SITE_ORIGIN = os.environ.get("SITE_ORIGIN", "https://aicareer.academy").rstrip("/")
BRAND = "AI Career Academy"
CONTACT_NAME = "Prerna"
PHONE_DISPLAY = "+91 83681 22877"
PHONE_E164 = "+918368122877"
WA_ME = f"https://wa.me/{PHONE_E164.lstrip('+')}"
EMAIL = os.environ.get("SITE_EMAIL", "hello@aicareer.academy")
ORG_ID = f"{SITE_ORIGIN}/#org"
PLACE_ID = f"{SITE_ORIGIN}/#studio"
GEO_LAT = 28.385278
GEO_LNG = 77.051389
STREET = "68 Avenue, Badshahpur, Sector 68"
POSTAL = "122101"
NAP_LINE = f"{STREET}, Gurugram, Haryana {POSTAL}"
MAPS_QUERY = f"{GEO_LAT},{GEO_LNG}"
MAPS_EMBED = (
    f"https://maps.google.com/maps?q={MAPS_QUERY}&ll={MAPS_QUERY}&z=16&hl=en&output=embed"
)
MAPS_PLACE = f"https://www.google.com/maps/search/?api=1&query={GEO_LAT}%2C{GEO_LNG}"
GURGAON_CANONICAL_PATH = "/ai-courses-in-gurgaon/"
DELHI_PATH = "/ai-courses-in-delhi/"
NOIDA_PATH = "/ai-courses-in-noida/"
GHAZIABAD_PATH = "/ai-courses-in-ghaziabad/"
# (source path without trailing slash, canonical destination)
LOCAL_REDIRECTS = [
    ("/ai-institute-in-gurgaon", GURGAON_CANONICAL_PATH),
    ("/ai-institute-in-gurugram", GURGAON_CANONICAL_PATH),
    ("/ai-courses-in-gurugram", GURGAON_CANONICAL_PATH),
    ("/ai-training-in-gurgaon", GURGAON_CANONICAL_PATH),
    ("/best-ai-institute-in-gurgaon", GURGAON_CANONICAL_PATH),
    ("/best-ai-institute-in-gurugram", GURGAON_CANONICAL_PATH),
    ("/best-ai-institute-in-gurgaon-with-fees", GURGAON_CANONICAL_PATH),
    ("/best-ai-institute-in-gurgaon-placement", GURGAON_CANONICAL_PATH),
    ("/ai-course-in-gurgaon-fees", GURGAON_CANONICAL_PATH),
    ("/ai-course-in-gurgaon-offline", GURGAON_CANONICAL_PATH),
    ("/ai-courses-in-gurgaon-sector-14", GURGAON_CANONICAL_PATH),
    ("/artificial-intelligence-course-in-gurgaon-for-freshers", GURGAON_CANONICAL_PATH),
    ("/generative-ai-course-in-gurgaon", GURGAON_CANONICAL_PATH),
    ("/ai-institute-in-delhi", DELHI_PATH),
    ("/best-ai-institute-in-delhi", DELHI_PATH),
    ("/best-ai-institute-in-delhi-with-fees", DELHI_PATH),
    ("/best-ai-institute-in-delhi-placement", DELHI_PATH),
    ("/ai-course-in-delhi-fees", DELHI_PATH),
    ("/ai-course-in-delhi-offline", DELHI_PATH),
    ("/generative-ai-course-in-delhi", DELHI_PATH),
    ("/artificial-intelligence-course-in-delhi-for-freshers", DELHI_PATH),
    ("/ai-institute-in-noida", NOIDA_PATH),
    ("/best-ai-institute-in-noida", NOIDA_PATH),
    ("/best-ai-institute-in-noida-with-fees", NOIDA_PATH),
    ("/best-ai-institute-in-noida-placement", NOIDA_PATH),
    ("/ai-course-in-noida-fees", NOIDA_PATH),
    ("/ai-course-in-noida-offline", NOIDA_PATH),
    ("/generative-ai-course-in-noida", NOIDA_PATH),
    ("/artificial-intelligence-course-in-noida-for-freshers", NOIDA_PATH),
    ("/ai-institute-in-ghaziabad", GHAZIABAD_PATH),
    ("/best-ai-institute-in-ghaziabad", GHAZIABAD_PATH),
    ("/best-ai-institute-in-ghaziabad-with-fees", GHAZIABAD_PATH),
    ("/best-ai-institute-in-ghaziabad-placement", GHAZIABAD_PATH),
    ("/ai-course-in-ghaziabad-fees", GHAZIABAD_PATH),
    ("/ai-course-in-ghaziabad-offline", GHAZIABAD_PATH),
    ("/generative-ai-course-in-ghaziabad", GHAZIABAD_PATH),
    ("/artificial-intelligence-course-in-ghaziabad-for-freshers", GHAZIABAD_PATH),
]

SEO_OVERRIDES = {
    "home": {
        "title": f"AI institute in Gurugram (Gurgaon) — {BRAND} | live online",
        "description": (
            f"{BRAND} is an AI training studio in Gurugram: desk at {NAP_LINE}. "
            "Nine live online programs — Analytics, Data Science, GenAI, MLOps, LLMOps, Java, DevOps, Frontend. "
            f"Walk-in counselling Mon–Sat 10am–7pm. Call {CONTACT_NAME} on {PHONE_DISPLAY}."
        ),
    },
    "courses": {
        "title": f"AI and data programs — {BRAND}",
        "description": "Nine live programs: Data Analytics with AI, Data Science Gen AI, Gen AI for Developers, Gen AI Specialization, MLOps, LLMOps, Java, DevOps, and Frontend. Placement support, certification, internships. Curriculum, fees, and career-call booking.",
    },
    "about-us": {
        "title": f"About {BRAND}",
        "description": f"{BRAND} is an engineering-first studio that maps AI careers to a learning sequence — live online cohorts, projects, and practitioner mentors.",
    },
    "hire-from-us": {
        "title": f"Hire from {BRAND}",
        "description": f"Talk to {BRAND} about hiring learners trained on RAG, MLOps, and agentic workflows. Portfolios, practitioner-led projects, and internship pipelines.",
    },
    "contact-us": {
        "title": f"Contact {BRAND} | Gurugram Sector 68 desk",
        "description": (
            f"Visit {BRAND} at {NAP_LINE}. {CONTACT_NAME}: {PHONE_DISPLAY}, {EMAIL}, WhatsApp. "
            "Mon–Sat, 10am–7pm IST. Career call and walk-in counselling. Classes are live online."
        ),
        "hero_title": "Gurugram desk — Sector 68",
        "hero_sub": f"{NAP_LINE}. Counselling here. Live cohorts on a screen. Mon–Sat, 10am–7pm IST.",
    },
    "ncr": {
        "title": f"AI courses in Delhi NCR (live online) — {BRAND}, Gurugram",
        "description": (
            f"Live online AI, data, Java, DevOps, and frontend programs for Delhi NCR. "
            f"Desk at {NAP_LINE}. Same published fees as the catalog. "
            f"Talk to {CONTACT_NAME} on {PHONE_DISPLAY}."
        ),
        "hero_title": "AI courses in Delhi NCR — live online",
        "hero_sub": "The classroom is a screen. The desk is in Gurugram. Learners across Delhi, Gurugram, Noida, Faridabad, and Ghaziabad join the same live cohort.",
    },
    "gurgaon": {
        "title": f"AI institute in Gurgaon (Gurugram) — {BRAND} | Sector 68",
        "description": (
            f"AI Career Academy is an AI institute in Gurgaon: {NAP_LINE}. "
            "Live online AI, Data Science, GenAI, MLOps, Java, DevOps, and Frontend. "
            f"Walk-in counselling Mon–Sat 10am–7pm. {CONTACT_NAME} {PHONE_DISPLAY}."
        ),
        "hero_title": "AI institute in Gurgaon — Sector 68 desk, live online classes",
        "hero_sub": (
            "Searchers looking for an AI institute in Gurugram / Gurgaon land here. "
            "The studio desk is on Sohna Road (Badshahpur, Sector 68). Batches are live online. "
            "Come in for a career call; join class from home."
        ),
    },
    "delhi": {
        "title": f"AI institute in Delhi — fees, GenAI, placement support | {BRAND}",
        "description": (
            f"AI and GenAI courses for Delhi learners. Published fees from ₹35,000. "
            f"Live online cohorts; counselling desk at {NAP_LINE}. Freshers welcome. "
            f"{CONTACT_NAME} {PHONE_DISPLAY}."
        ),
        "hero_title": "AI courses in Delhi — live online, Gurugram desk",
        "hero_sub": (
            "Same catalog as Gurgaon: published fees, GenAI tracks, placement support. "
            "You join from Delhi. Walk-in counselling is Sector 68, Gurugram — not a Connaught Place classroom."
        ),
    },
    "noida": {
        "title": f"AI institute in Noida — fees, GenAI, placement support | {BRAND}",
        "description": (
            f"AI and GenAI courses for Noida and Greater Noida. Fees on the page. "
            f"Live online; desk at {NAP_LINE}. Freshers welcome. {CONTACT_NAME} {PHONE_DISPLAY}."
        ),
        "hero_title": "AI courses in Noida — live online, Gurugram desk",
        "hero_sub": (
            "Sector 62 / 18 / 137 searchers join the same live cohort. "
            "The pin is Sector 68 Gurugram for counselling — classes are not a Noida classroom batch."
        ),
    },
    "ghaziabad": {
        "title": f"AI institute in Ghaziabad — fees, GenAI, placement support | {BRAND}",
        "description": (
            f"AI and GenAI courses for Ghaziabad (Vaishali, Indirapuram, Raj Nagar). "
            f"Published fees, live online, placement support. Desk: {NAP_LINE}. {CONTACT_NAME} {PHONE_DISPLAY}."
        ),
        "hero_title": "AI courses in Ghaziabad — live online, Gurugram desk",
        "hero_sub": (
            "Join from Vaishali, Indirapuram, or Kaushambi. "
            "Counselling is at the Gurugram Sector 68 desk. Batches are live online, same fees as the catalog."
        ),
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
        "description": f"Book a 15-minute career call with {CONTACT_NAME} on WhatsApp. Tell us your background and the role you want; we will map a sequence.",
    },
    "mentors": {
        "title": f"Mentors — {BRAND}",
        "description": f"Practitioner mentors at {BRAND}: Ankit, Praveen, Aayush, Rahul Bhardwaj, Vaibhav Sharma, and Deepak Rohilla (senior frontend engineer). Sales Head: Prerna.",
    },
    "blogs": {
        "title": f"Blog — {BRAND}",
        "description": f"Short notes on AI career sequences, tools, and role maps from {BRAND}.",
        "hero_title": "Notes on AI careers",
        "hero_sub": "Role maps and tool stacks — written to help you choose a sequence, not to rank for ‘best institute’.",
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
    "terms": [
        {
            "heading": "Using this site",
            "content": f"This website is a catalog for {BRAND}. Published fees, durations, and curricula are the offer. Marketing pages do not create a placement guarantee.",
        },
        {
            "heading": "Enrollment",
            "content": "A seat is confirmed after we accept your enquiry and you pay the published fee (or the installment plan we write down). We may refuse a batch if the sequence does not fit your background — that is the point of the career call.",
        },
        {
            "heading": "Live online format",
            "content": "Cohorts are live online. The Gurugram address is the studio office, not a classroom you must attend.",
        },
        {
            "heading": "Conduct",
            "content": "Do not share session recordings, assignments, or other learners’ work outside the cohort without permission.",
        },
        {
            "heading": "Contact",
            "content": f"{EMAIL} · {PHONE_DISPLAY} · 68 Avenue, Badshahpur, Sector 68, Gurugram, Haryana 122101.",
        },
    ],
    "enterprise": [
        {
            "heading": "What we will scope",
            "content": "Role-based live cohorts for teams: GenAI for developers, RAG/eval habits, MLOps, or LLMOps. We start from the job your people already do — not a generic tool dump.",
        },
        {
            "heading": "What we will not claim",
            "content": "We do not sell a placement percentage for your employees, and we do not put your logo on this site unless you ask in writing.",
        },
        {
            "heading": "Talk to the desk",
            "content": f"WhatsApp {CONTACT_NAME} or email {EMAIL} with team size, stack, and the role you want people to grow into.",
        },
    ],
}

ABOUT_SECTIONS = [
    {
        "heading": "What this studio is",
        "content": f"{BRAND} maps a job to a live online sequence. Nine published programs, practitioner mentors, and a 15-minute career call before you pay. The office is in Gurugram; the classroom is a screen.",
    },
    {
        "heading": "How we work",
        "content": "Curriculum and fees sit on each program page. Every live program includes placement support, a course certificate, and internship opportunities — not an invented pass rate.",
    },
    {
        "heading": "What we will not do",
        "content": "We will not paste another institute’s recruiter wall as ours. We will not invent Indian salary tables. We will not call a recorded dump a live cohort.",
    },
    {
        "heading": "Talk to us",
        "content": f"Book a career call with {CONTACT_NAME}, WhatsApp {PHONE_DISPLAY}, or write {EMAIL}. If the sequence does not fit, we will say so.",
    },
]

PROGRAM_HREFS = [
    {"href": "courses/data-analytics-course-with-placement/index.html", "title": "Data Analytics with AI — 5 months — ₹40,000"},
    {"href": "courses/data-science-course/index.html", "title": "Data Science Gen AI — 6 months — ₹55,000"},
    {"href": "courses/ai-developers-course/index.html", "title": "Gen AI for Developers — 3 months — ₹40,000"},
    {"href": "courses/generative-ai-course/index.html", "title": "Generative AI Specialization — 5 months — ₹64,999"},
    {"href": "courses/mlops-course/index.html", "title": "MLOps — 6 months — ₹60,000"},
    {"href": "courses/llmops-course/index.html", "title": "LLMOps — 3 months — ₹35,000"},
    {"href": "courses/java-course/index.html", "title": "Java — 3 months — ₹40,000"},
    {"href": "courses/devops-course/index.html", "title": "DevOps — 6 months — ₹60,000"},
    {"href": "courses/frontend-course/index.html", "title": "Frontend — 3 months — ₹40,000"},
]

FEE_LINES = [
    "Data Analytics with AI — 5 months — ₹40,000",
    "Data Science Gen AI — 6 months — ₹55,000 (₹65,000 listed, ₹10,000 off)",
    "Gen AI for Developers — 3 months — ₹40,000",
    "Generative AI Specialization — 5 months — ₹64,999",
    "MLOps — 6 months — ₹60,000",
    "LLMOps — 3 months — ₹35,000",
    "Java — 3 months — ₹40,000",
    "DevOps — 6 months — ₹60,000",
    "Frontend — 3 months — ₹40,000",
]

NCR_PAGE = {
    "sections": [
        {
            "heading": "Where you actually sit",
            "content": (
                f"{BRAND} is based at 68 Avenue, Badshahpur, Sector 68, Gurugram, Haryana 122101. "
                "That is the studio desk — for career calls with Prerna and for anyone who needs to visit. "
                "Batches are live online. You do not have to move to Gurugram, and we do not run a separate classroom in Connaught Place, Noida Sector 18, or Dwarka."
            ),
        },
        {
            "heading": "Who this page is for",
            "content": (
                "Working professionals and graduates in Delhi, Gurugram, Noida, Greater Noida, Faridabad, and Ghaziabad who want a published sequence — Data Analytics, Data Science, GenAI, MLOps, LLMOps, Java, DevOps, or Frontend — without a mystery PDF after they pay. "
                "Evening and weekend-shaped batches are listed on the program pages; confirm the current slot on the call."
            ),
        },
        {
            "heading": "What NCR hiring actually looks like here",
            "content": (
                "Product firms, IT services, banks, and captives across NCR hire analysts, developers, and ops engineers. "
                "That is a labour-market fact, not a list of companies that hired our alumni, and not a placement percentage. "
                "We map your background to one catalog program, or we say none fits yet."
            ),
        },
        {
            "heading": "Fees",
            "content": (
                "The number on each program page is the number. Placement support, a course certificate, and internship opportunities are included. "
                "We do not publish a fake “Delhi NCR average CTC” table."
            ),
        },
        {
            "heading": "Next step",
            "content": (
                f"Open a program below, or WhatsApp {CONTACT_NAME} on {PHONE_DISPLAY} for a 15-minute career call. "
                "Mon–Sat, 10am–7pm IST."
            ),
        },
    ],
    "faqs": [
        {
            "question": "Is this a classroom course in Delhi?",
            "answer": "No. Cohorts are live online. The Gurugram Sector 68 address is the office, not a daily classroom you must attend.",
        },
        {
            "question": "I live in Noida or Faridabad. Can I join?",
            "answer": "Yes. You join the same live online cohort as learners anywhere else. If you need to visit the desk, it is in Gurugram Sector 68.",
        },
        {
            "question": "Which programs can Delhi NCR learners take?",
            "answer": "All nine published programs: Data Analytics with AI, Data Science Gen AI, Gen AI for Developers, Gen AI Specialization, MLOps, LLMOps, Java, DevOps, and Frontend. Fees and modules are on each program page.",
        },
        {
            "question": "Do you guarantee a job in Gurgaon or Noida?",
            "answer": "No. We offer placement support, a certificate, and internship opportunities. We do not invent a placement rate.",
        },
    ],
    "page_links": [
        {"href": "courses/data-analytics-course-with-placement/index.html", "title": "Data Analytics with AI"},
        {"href": "courses/data-science-course/index.html", "title": "Data Science Gen AI"},
        {"href": "courses/ai-developers-course/index.html", "title": "Gen AI for Developers"},
        {"href": "courses/generative-ai-course/index.html", "title": "Gen AI Specialization"},
        {"href": "courses/mlops-course/index.html", "title": "MLOps"},
        {"href": "courses/llmops-course/index.html", "title": "LLMOps"},
        {"href": "courses/java-course/index.html", "title": "Java"},
        {"href": "courses/devops-course/index.html", "title": "DevOps"},
        {"href": "courses/frontend-course/index.html", "title": "Frontend"},
        {"href": "ai-courses-in-gurgaon/index.html", "title": "AI institute in Gurgaon (Gurugram desk)"},
        {"href": "ai-courses-in-delhi/index.html", "title": "AI courses in Delhi"},
        {"href": "ai-courses-in-noida/index.html", "title": "AI courses in Noida"},
        {"href": "ai-courses-in-ghaziabad/index.html", "title": "AI courses in Ghaziabad"},
        {"href": "contact-us/index.html", "title": "Gurugram desk + map"},
        {"href": "register/index.html", "title": "Book a career call"},
    ],
}

GURGAON_PAGE = {
    "sections": [
        {
            "heading": "Best AI institute in Gurgaon — how to judge, not a slogan",
            "content": (
                f"{BRAND} is an AI institute in Gurgaon at {NAP_LINE}. "
                "“Best” on Google is a search phrase, not a trophy we print. Judge us on published fees, live cohorts, and a career call that can say no. "
                "We do not buy review counts or paste another centre’s placement wall."
            ),
        },
        {
            "heading": "AI course in Gurgaon fees",
            "content": (
                "Fees are on each program page before WhatsApp. Current catalog: Analytics ₹40,000 · Data Science ₹55,000 · "
                "Gen AI for Developers ₹40,000 · Generative AI Specialization ₹64,999 · MLOps ₹60,000 · LLMOps ₹35,000 · "
                "Java ₹40,000 · DevOps ₹60,000 · Frontend ₹40,000. Same number for Delhi, Noida, and Ghaziabad learners."
            ),
        },
        {
            "heading": "Placement support — not a Gurgaon job guarantee",
            "content": (
                "Searches for “best AI institute in Gurgaon placement” usually want a percentage. We do not invent one. "
                "Every live program includes placement support, a course certificate, and internship opportunities. "
                "Cyber City hiring is a labour market, not our alumni list."
            ),
        },
        {
            "heading": "Artificial Intelligence course in Gurgaon for freshers",
            "content": (
                "Freshers and career-switchers take the same live online batches. The 15-minute call maps background to Analytics, "
                "Data Science, GenAI, Java, DevOps, or Frontend — or says wait. There is no separate “fresher dump.”"
            ),
        },
        {
            "heading": "Generative AI course in Gurgaon",
            "content": (
                "Two GenAI tracks: Gen AI for Developers (₹40,000, 3 months — APIs, RAG, agents, FastAPI) and "
                "Generative AI Specialization (₹64,999, 5 months — architectures, fine-tuning, multimodal). "
                "Neither is a recorded ChatGPT tutorial."
            ),
        },
        {
            "heading": "AI course in Gurgaon offline vs Sector 14",
            "content": (
                "Classes are live online. Walk-in counselling is Sector 68 (Sohna Road / Badshahpur), Mon–Sat 10am–7pm. "
                "We are not an Old DLF Sector 14 classroom and we are not DataMites. If a map pin says Sector 14, that is another institute."
            ),
        },
        {
            "heading": "How to visit",
            "content": (
                f"Address: {NAP_LINE}. Phone {PHONE_DISPLAY}. WhatsApp {CONTACT_NAME}. "
                "Bring 20 minutes: background plus the role you want."
            ),
        },
    ],
    "faqs": [
        {
            "question": "Which is the best AI institute in Gurgaon?",
            "answer": (
                f"Compare published fees, whether class is actually live, and whether placement is a method or a percentage. "
                f"{BRAND} is at {NAP_LINE}: live online cohorts, fees on the page, placement support without a fabricated rate."
            ),
        },
        {
            "question": "What are AI course fees in Gurgaon at AI Career Academy?",
            "answer": "₹35,000–₹64,999 depending on program. LLMOps ₹35,000; Analytics, Gen AI for Developers, Java, Frontend ₹40,000; Data Science ₹55,000; MLOps and DevOps ₹60,000; Gen AI Specialization ₹64,999.",
        },
        {
            "question": "Do you offer placement after an AI course in Gurgaon?",
            "answer": "Placement support, a certificate, and internships are included. We do not guarantee a Cyber City job or publish a placement percentage.",
        },
        {
            "question": "Is there an AI course in Gurgaon for freshers?",
            "answer": "Yes. Freshers join the same live online catalog. The career call decides which sequence fits — Analytics, Data Science, GenAI, or a software track.",
        },
        {
            "question": "Is the AI course in Gurgaon offline?",
            "answer": "Counselling is on-site at Sector 68. Batches are live online. There is no daily classroom in Sector 14 or Cyber Hub.",
        },
        {
            "question": "Do you run AI courses in Gurgaon Sector 14?",
            "answer": "No. The desk is 68 Avenue, Sector 68, Badshahpur — not Old DLF Sector 14. Searchers comparing Sector 14 centres should check the pin before travelling.",
        },
        {
            "question": "Do you teach a Generative AI course in Gurgaon?",
            "answer": "Yes. Gen AI for Developers (₹40,000, 3 months) and Generative AI Specialization (₹64,999, 5 months). Links are on this page.",
        },
        {
            "question": "Are you DataMites Gurgaon?",
            "answer": "No. AI Career Academy is a separate studio at Sector 68. Do not treat another brand’s reviews or fees as ours.",
        },
    ],
    "lists": [FEE_LINES],
    "page_links": PROGRAM_HREFS
    + [
        {"href": "ai-courses-in-delhi/index.html", "title": "AI courses in Delhi"},
        {"href": "ai-courses-in-noida/index.html", "title": "AI courses in Noida"},
        {"href": "ai-courses-in-ghaziabad/index.html", "title": "AI courses in Ghaziabad"},
        {"href": "ai-courses-in-delhi-ncr/index.html", "title": "AI courses in Delhi NCR"},
        {"href": "contact-us/index.html", "title": "Map, phone, walk-in hours"},
        {"href": "register/index.html", "title": "Book a career call"},
    ],
}


def ncr_city_hub(city: str, areas: str, commute: str) -> dict:
    """Indexed landing page for a city that shares the Gurugram desk + live online catalog."""
    return {
        "sections": [
            {
                "heading": f"Best AI institute in {city} — same catalog, honest pin",
                "content": (
                    f"People searching “best AI institute in {city}” want fees, placement, and whether they must sit in a classroom. "
                    f"{BRAND} teaches live online. The walk-in desk is {NAP_LINE}. {areas} "
                    f"{commute}"
                ),
            },
            {
                "heading": f"AI course in {city} fees",
                "content": (
                    "Same published fees as Gurgaon — not a city surcharge. "
                    "Analytics ₹40,000 · Data Science ₹55,000 · Gen AI for Developers ₹40,000 · "
                    "Generative AI Specialization ₹64,999 · MLOps ₹60,000 · LLMOps ₹35,000 · Java ₹40,000 · DevOps ₹60,000 · Frontend ₹40,000."
                ),
            },
            {
                "heading": f"Placement after an AI course in {city}",
                "content": (
                    "Placement support, certificate, internships — included. No invented “100% placement in NCR” line. "
                    "NCR product, IT services, and captives hire these roles; that is labour-market context, not our alumni wall."
                ),
            },
            {
                "heading": f"Artificial Intelligence course in {city} for freshers",
                "content": (
                    f"Freshers in {city} join the same live batches. A 15-minute call with {CONTACT_NAME} maps a sequence or says none fits yet."
                ),
            },
            {
                "heading": f"Generative AI course in {city}",
                "content": (
                    "Gen AI for Developers (₹40,000, 3 months) and Generative AI Specialization (₹64,999, 5 months). "
                    "Live instructor-led, not a recorded prompt course."
                ),
            },
            {
                "heading": f"AI course in {city} offline",
                "content": (
                    f"There is no {city} classroom campus. Offline means you can visit the Gurugram Sector 68 desk for counselling. "
                    "Class itself is live online from {city}."
                ),
            },
        ],
        "faqs": [
            {
                "question": f"Which is the best AI institute in {city}?",
                "answer": (
                    f"Use fees on the page, live vs recorded, and placement method. {BRAND} is live online with a Gurugram desk at {NAP_LINE}. "
                    f"{city} learners join the same cohort."
                ),
            },
            {
                "question": f"What are AI course fees in {city}?",
                "answer": f"₹35,000–₹64,999. Exact number is on each program page. No different {city} price list.",
            },
            {
                "question": f"Do you offer placement after an AI course in {city}?",
                "answer": "Placement support, certificate, internships. No job guarantee and no fabricated percentage.",
            },
            {
                "question": f"Is there an AI course in {city} for freshers?",
                "answer": f"Yes. Freshers in {city} take the live online catalog after a career call.",
            },
            {
                "question": f"Is the AI course in {city} offline?",
                "answer": f"Class is live online. Visit Sector 68 Gurugram if you want an in-person counselling slot.",
            },
            {
                "question": f"Do you teach a Generative AI course in {city}?",
                "answer": "Yes — Gen AI for Developers and Generative AI Specialization. Same fees as the Gurgaon catalog.",
            },
        ],
        "lists": [FEE_LINES],
        "page_links": PROGRAM_HREFS
        + [
            {"href": "ai-courses-in-gurgaon/index.html", "title": "AI institute in Gurgaon (the desk)"},
            {"href": "ai-courses-in-delhi-ncr/index.html", "title": "Delhi NCR overview"},
            {"href": "contact-us/index.html", "title": "Map and walk-in hours"},
            {"href": "register/index.html", "title": "Book a career call"},
        ],
    }


CITY_PAGES = {
    "delhi": ncr_city_hub(
        "Delhi",
        "South Delhi, Dwarka, Rohini, and East Delhi learners are in the same batch.",
        "Do not expect a Connaught Place classroom; expect a screen plus a Gurugram desk if you want to visit.",
    ),
    "noida": ncr_city_hub(
        "Noida",
        "Sector 18, 62, 137, and Greater Noida learners join from home or office.",
        "The Noida Expressway commute is for a counselling visit, not a daily lecture.",
    ),
    "ghaziabad": ncr_city_hub(
        "Ghaziabad",
        "Vaishali, Indirapuram, Kaushambi, and Raj Nagar Extension are in range for a weekend desk visit.",
        "Weekday class is live online so you are not stuck on NH-9 for a 7pm lecture.",
    ),
}


def city_body(city: str) -> dict:
    return {
        "title": f"Data Science course for {city} learners — live online — {BRAND}",
        "description": (
            f"Live online Data Science Gen AI for people in {city}. Same published curriculum and fee as the national program. "
            "Placement support, certificate, internships — not a local hiring-partner claim."
        ),
        "hero_title": f"Data Science for {city} — live online",
        "hero_sub": (
            f"You join the same live online cohort as everyone else. Gurugram is the studio address, not a {city} classroom. "
            f"This page is here so searchers in {city} can find the catalog."
        ),
        "sections": [
            {
                "heading": "Same program, your city in the search box",
                "content": (
                    f"The Data Science Gen AI sequence is Python, SQL, statistics, machine learning, and a first RAG. "
                    f"Learners in {city} attend live online. We do not run a separate {city} campus batch."
                ),
            },
            {
                "heading": "Fees and support",
                "content": "The fee on the program page is the fee. Placement support, a certificate, and internship opportunities are included — without a made-up percentage or a named hiring-partner list.",
            },
            {
                "heading": "Next step",
                "content": "Open the Data Science program, or book a 15-minute career call if you are unsure this is the role.",
            },
        ],
        "faqs": [
            {
                "question": f"Do I have to move to Gurugram from {city}?",
                "answer": "No. Cohorts are live online. The Sector 68 address is the office.",
            },
            {
                "question": "Is this a different syllabus for each city?",
                "answer": "No. City pages point at the same Data Science Gen AI catalog.",
            },
        ],
        "lists": [],
    }


ROADMAP_BODIES = {
    "roadmap-ds": {
        "hero_title": "Data science roadmap",
        "hero_sub": "Excel/SQL → Python → ML → a first RAG. Matches the Data Science Gen AI program — not a placement promise.",
    },
    "roadmap-ai-dev": {
        "hero_title": "AI developer roadmap",
        "hero_sub": "Software engineering plus LLM APIs, RAG, and a deployed service. Matches Gen AI for Developers.",
    },
    "roadmap-ai-eng": {
        "hero_title": "AI engineer roadmap",
        "hero_sub": "Build, evaluate, and ship model-backed features. Deeper than a prompt-only track.",
    },
    "roadmap-ml-eng": {
        "hero_title": "ML engineer roadmap",
        "hero_sub": "Train, version, and serve models. Neighbours the MLOps program, not a dashboard course.",
    },
    "roadmap-genai": {
        "hero_title": "Generative AI roadmap",
        "hero_sub": "Transformers, RAG, adapters, serving. Matches Gen AI Specialization.",
    },
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
    s = s.replace("https://wa.me/9196914 40998", WA_ME)
    s = s.replace("https://wa.me/919691440998", WA_ME)
    s = s.replace("https://wa.me/918708752385", WA_ME)
    s = s.replace("+91 96914 40998", PHONE_DISPLAY)
    s = s.replace("+91 87087 52385", PHONE_DISPLAY)
    s = s.replace("+919691440998", PHONE_E164)
    s = s.replace("+918708752385", PHONE_E164)
    s = s.replace("96914 40998", "83681 22877")
    s = s.replace("87087 52385", "83681 22877")
    s = s.replace("9691440998", "8368122877")
    s = s.replace("8708752385", "8368122877")
    s = re.sub(r"\b100%\s+placement support\b", "placement support", s, flags=re.I)
    s = re.sub(r"\b100%\s+placement\b", "placement support", s, flags=re.I)
    s = re.sub(
        r"India['’]s (?:best|top-rated|top|most trusted|leading)(?: AI institute| institute)?",
        "an AI training studio",
        s,
        flags=re.I,
    )
    s = re.sub(r"hiring partners?", "typical employers of these roles", s, flags=re.I)
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
    extra = dict(SEO_OVERRIDES.get(page["id"], {}))
    extra.update(PROGRAM_COPY.get(page["id"], {}))
    for key in ("title", "description", "hero_title", "hero_sub"):
        if key in extra:
            data[key] = extra[key]
    if page["id"] in PROGRAM_COPY:
        copy = PROGRAM_COPY[page["id"]]
        data["sections"] = copy["sections"]
        data["raw_html"] = ""
        data["skip_extracted_salaries"] = True
        data["faqs"] = copy.get("faqs") or []
        data["lists"] = []
        data["related"] = copy.get("related") or []
    if page["id"] in LEGAL_SECTIONS:
        data["sections"] = LEGAL_SECTIONS[page["id"]]
        data["raw_html"] = ""
        data["faqs"] = []
        data["lists"] = []
    if page["id"] == "about-us":
        data["hero_title"] = f"About {BRAND}"
        data["hero_sub"] = "An engineering-first studio. Live online cohorts. A desk in Gurugram."
        data["sections"] = ABOUT_SECTIONS
        data["raw_html"] = ""
        data["faqs"] = []
        data["lists"] = []
        data["images"] = []
    if page["id"] == "ncr":
        data["sections"] = NCR_PAGE["sections"]
        data["faqs"] = NCR_PAGE["faqs"]
        data["page_links"] = NCR_PAGE["page_links"]
        data["raw_html"] = ""
        data["lists"] = []
        data["images"] = []
    if page["id"] == "gurgaon":
        data["sections"] = GURGAON_PAGE["sections"]
        data["faqs"] = GURGAON_PAGE["faqs"]
        data["page_links"] = GURGAON_PAGE["page_links"]
        data["lists"] = GURGAON_PAGE.get("lists") or []
        data["raw_html"] = ""
        data["images"] = []
    if page["id"] in CITY_PAGES:
        hub = CITY_PAGES[page["id"]]
        data["sections"] = hub["sections"]
        data["faqs"] = hub["faqs"]
        data["page_links"] = hub["page_links"]
        data["lists"] = hub.get("lists") or []
        data["raw_html"] = ""
        data["images"] = []
    if page["id"] == "contact-us":
        data["page_links"] = [
            {"href": "ai-courses-in-gurgaon/index.html", "title": "AI institute in Gurgaon — full local page"},
            {"href": "ai-courses-in-delhi/index.html", "title": "AI courses in Delhi"},
            {"href": "ai-courses-in-noida/index.html", "title": "AI courses in Noida"},
            {"href": "ai-courses-in-ghaziabad/index.html", "title": "AI courses in Ghaziabad"},
            {"href": "ai-courses-in-delhi-ncr/index.html", "title": "AI courses in Delhi NCR"},
            {"href": "register/index.html", "title": "Book a career call"},
        ]
        data["raw_html"] = ""
        data["sections"] = [
            {
                "heading": "Walk in",
                "content": f"{NAP_LINE}. Mon–Sat, 10am–7pm IST. Ask for {BRAND}. Counselling and paperwork here; class is live online.",
            },
            {
                "heading": "Call or WhatsApp",
                "content": f"{CONTACT_NAME} · {PHONE_DISPLAY} · {EMAIL}. Book a 15-minute career call if you cannot visit today.",
            },
        ]
        data["faqs"] = [
            {
                "question": "Where is the Gurgaon office?",
                "answer": f"{NAP_LINE}. Pin on the map on this page.",
            },
            {
                "question": "Can I visit without an appointment?",
                "answer": "Yes during desk hours. WhatsApp first if you want a reserved slot.",
            },
        ]
        data["lists"] = []
    if str(page["id"]).startswith("city-"):
        city = {
            "city-delhi": "Delhi NCR",
            "city-bangalore": "Bengaluru",
            "city-hyderabad": "Hyderabad",
            "city-pune": "Pune",
        }.get(page["id"], "your city")
        body = city_body(city)
        data.update(body)
        data["raw_html"] = ""
        data["images"] = []
        if page["id"] == "city-delhi":
            data["page_links"] = [
                {
                    "href": "ai-courses-in-gurgaon/index.html",
                    "title": "AI institute in Gurgaon (Gurugram desk)",
                },
                {
                    "href": "ai-courses-in-delhi-ncr/index.html",
                    "title": "AI courses in Delhi NCR (live online)",
                },
            ]
    if page["id"] in ROADMAP_BODIES:
        data.update(ROADMAP_BODIES[page["id"]])
        data["raw_html"] = ""
        if not data.get("sections"):
            data["sections"] = [
                {
                    "heading": "How to use this page",
                    "content": "The tree below is a sequence, not a job offer. Pick the matching live program if the role is the one you want.",
                }
            ]
    if page.get("type") == "comparison":
        data["raw_html"] = ""
        intro = {
            "heading": "How to read this",
            "content": "Role and tool comparisons for choosing a sequence. Not salary tables, not a ranking of institutes, not a claim about who hires our alumni.",
        }
        existing = [s for s in (data.get("sections") or []) if s.get("heading") != intro["heading"]]
        data["sections"] = [intro] + existing
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
        data["raw_html"] = ""
    if page["id"] == "comparisons":
        data["hero_title"] = "Comparisons"
        data["hero_sub"] = "Pick a role or tool pair. These pages help you choose a sequence — not an institute ranking."
        data["raw_html"] = ""
        data["page_links"] = [
            {"href": "comparisons/ai-developer-vs-data-scientist/index.html", "title": "AI Developer vs Data Scientist"},
            {"href": "comparisons/ai-developer-vs-ai-engineer/index.html", "title": "AI Developer vs AI Engineer"},
            {"href": "comparisons/ai-engineer-vs-ml-engineer/index.html", "title": "AI Engineer vs ML Engineer"},
            {"href": "comparisons/genai-vs-ai-developer-vs-agentic-ai/index.html", "title": "GenAI vs AI Developer vs Agentic AI"},
            {"href": "comparisons/mlops-vs-llmops-vs-aiops/index.html", "title": "MLOps vs LLMOps vs AIOps"},
            {"href": "comparisons/prompt-engineer-vs-ai-developer/index.html", "title": "Prompt Engineer vs AI Developer"},
            {"href": "comparisons/mlops-engineer-vs-ml-engineer/index.html", "title": "MLOps Engineer vs ML Engineer"},
            {"href": "comparisons/rag-vs-fine-tuning/index.html", "title": "RAG vs Fine-Tuning"},
            {"href": "comparisons/rag-vs-agentic-rag/index.html", "title": "RAG vs Agentic RAG"},
            {"href": "comparisons/langchain-vs-langgraph/index.html", "title": "LangChain vs LangGraph"},
            {"href": "comparisons/crewai-vs-autogen-vs-langgraph/index.html", "title": "CrewAI vs AutoGen vs LangGraph"},
            {"href": "comparisons/mcp-vs-acp/index.html", "title": "MCP vs ACP"},
        ]
    return data


def _format_title(raw: str, page: dict) -> str:
    if page.get("id") in PROGRAM_COPY and PROGRAM_COPY[page["id"]].get("title"):
        return PROGRAM_COPY[page["id"]]["title"]
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
        desc = f"{sanitize_text(str(title).split('|')[0].strip())}. Live online programs and career sequences from {BRAND}."
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


def _postal_address() -> dict:
    return {
        "@type": "PostalAddress",
        "streetAddress": STREET,
        "addressLocality": "Gurugram",
        "addressRegion": "Haryana",
        "postalCode": POSTAL,
        "addressCountry": "IN",
    }


def json_ld(page: dict, data: dict, fees=None) -> list:
    org = {
        "@type": ["EducationalOrganization"],
        "@id": ORG_ID,
        "name": BRAND,
        "alternateName": [
            "AI Career Academy Gurgaon",
            "AI Career Academy Gurugram",
            "ACA Gurugram",
        ],
        "url": SITE_ORIGIN + "/",
        "email": EMAIL,
        "telephone": PHONE_E164,
        "logo": f"{SITE_ORIGIN}/assets/img/logo-aca.png",
        "image": [
            f"{SITE_ORIGIN}/assets/og.png",
            f"{SITE_ORIGIN}/assets/img/logo-aca.png",
            f"{SITE_ORIGIN}/assets/img/og-programs.png",
            f"{SITE_ORIGIN}/assets/img/og-gurugram.png",
        ],
        "address": _postal_address(),
        "geo": {"@type": "GeoCoordinates", "latitude": GEO_LAT, "longitude": GEO_LNG},
        "hasMap": MAPS_PLACE,
        "location": {"@id": PLACE_ID},
        "areaServed": [
            {"@type": "City", "name": "Gurugram"},
            {"@type": "City", "name": "Gurgaon"},
            {"@type": "AdministrativeArea", "name": "Delhi NCR"},
        ],
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ],
                "opens": "10:00",
                "closes": "19:00",
            }
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": PHONE_E164,
            "contactType": "admissions",
            "areaServed": "IN",
            "availableLanguage": ["en", "hi"],
        },
    }
    graph = [
        org,
        {
            "@type": ["Place", "LocalBusiness"],
            "@id": PLACE_ID,
            "name": f"{BRAND} Gurugram",
            "alternateName": "AI Career Academy Gurgaon",
            "url": f"{SITE_ORIGIN}{GURGAON_CANONICAL_PATH}",
            "telephone": PHONE_E164,
            "image": f"{SITE_ORIGIN}/assets/img/og-gurugram.png",
            "address": _postal_address(),
            "geo": {"@type": "GeoCoordinates", "latitude": GEO_LAT, "longitude": GEO_LNG},
            "hasMap": MAPS_PLACE,
            "parentOrganization": {"@id": ORG_ID},
            "openingHoursSpecification": org["openingHoursSpecification"],
            "priceRange": "₹₹",
        },
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
    if page.get("id") == "ncr":
        graph.append(
            {
                "@type": "WebPage",
                "name": data.get("hero_title") or "AI courses in Delhi NCR",
                "url": canonical_url(page),
                "about": {"@id": ORG_ID},
                "areaServed": [
                    {"@type": "City", "name": "Gurugram"},
                    {"@type": "City", "name": "New Delhi"},
                    {"@type": "City", "name": "Noida"},
                    {"@type": "City", "name": "Faridabad"},
                    {"@type": "City", "name": "Ghaziabad"},
                ],
            }
        )
    if page.get("id") in ("gurgaon", "delhi", "noida", "ghaziabad"):
        served = {
            "gurgaon": [{"@type": "City", "name": "Gurugram"}, {"@type": "City", "name": "Gurgaon"}],
            "delhi": [{"@type": "City", "name": "New Delhi"}, {"@type": "City", "name": "Delhi"}],
            "noida": [{"@type": "City", "name": "Noida"}, {"@type": "City", "name": "Greater Noida"}],
            "ghaziabad": [{"@type": "City", "name": "Ghaziabad"}],
        }[page["id"]]
        graph.append(
            {
                "@type": "WebPage",
                "@id": canonical_url(page) + "#webpage",
                "name": data.get("hero_title") or page["id"],
                "url": canonical_url(page),
                "about": {"@id": PLACE_ID},
                "primaryImageOfPage": f"{SITE_ORIGIN}/assets/img/og-gurugram.png",
                "areaServed": served,
                "speakable": {
                    "@type": "SpeakableSpecification",
                    "cssSelector": ["h1", ".center-copy"],
                },
            }
        )
    faqs = data.get("faqs") or []
    if faqs and (
        page.get("type") in ("program", "comparison", "blog")
        or page.get("id") in ("ncr", "gurgaon", "delhi", "noida", "ghaziabad", "contact-us")
    ):
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


def _local_redirect_rules() -> list[dict]:
    rules = []
    for src, dest in LOCAL_REDIRECTS:
        rules.append({"source": src, "destination": dest, "permanent": True})
        if not src.endswith("/"):
            rules.append({"source": src + "/", "destination": dest, "permanent": True})
    return rules


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
        pid = page.get("id", "")
        priority = (
            "1.0"
            if pid in ("home", "gurgaon")
            else "0.9"
            if pid in ("delhi", "noida", "ghaziabad", "ncr")
            else "0.8"
            if pid in ("courses", "contact-us")
            else "0.6"
        )
        urls.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (site / "sitemap.xml").write_text(xml, encoding="utf-8")
    host = SITE_ORIGIN.replace("https://", "").replace("http://", "")
    netlify_lines = [f"https://www.{host}/* https://{host}/:splat 301"]
    for src, dest in LOCAL_REDIRECTS:
        netlify_lines.append(f"{src} {dest} 301")
        if not src.endswith("/"):
            netlify_lines.append(f"{src}/ {dest} 301")
    (site / "_redirects").write_text("\n".join(netlify_lines) + "\n", encoding="utf-8")
    (site / "_headers").write_text(
        "/*\n"
        "  X-Frame-Options: DENY\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n",
        encoding="utf-8",
    )
    vercel = {
        "trailingSlash": True,
        "cleanUrls": False,
        "redirects": _local_redirect_rules(),
        "rewrites": [
            {
                "source": "/google114699eecbb71cd9.html/",
                "destination": "/google114699eecbb71cd9.html",
            },
            {
                "source": "/llms.txt/",
                "destination": "/llms.txt",
            },
        ],
        "headers": [
            {
                "source": "/(.*)",
                "headers": [
                    {"key": "X-Frame-Options", "value": "DENY"},
                    {"key": "X-Content-Type-Options", "value": "nosniff"},
                    {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                ],
            }
        ],
    }
    (site / "vercel.json").write_text(json.dumps(vercel, indent=2) + "\n", encoding="utf-8")
    (site / "llms.txt").write_text(
        "\n".join(
            [
                f"# {BRAND}",
                "",
                f"> Live online AI, data, and engineering programs. Desk at {NAP_LINE}. Counselling Mon–Sat 10:00–19:00 IST. Classes are live online.",
                "",
                f"- [Home]({SITE_ORIGIN}/)",
                f"- [AI institute in Gurgaon]({SITE_ORIGIN}{GURGAON_CANONICAL_PATH})",
                f"- [AI courses in Delhi]({SITE_ORIGIN}{DELHI_PATH})",
                f"- [AI courses in Noida]({SITE_ORIGIN}{NOIDA_PATH})",
                f"- [AI courses in Ghaziabad]({SITE_ORIGIN}{GHAZIABAD_PATH})",
                f"- [AI courses in Delhi NCR]({SITE_ORIGIN}/ai-courses-in-delhi-ncr/)",
                f"- [Programs]({SITE_ORIGIN}/courses/)",
                f"- [Book a career call]({SITE_ORIGIN}/register/)",
                f"- [Contact]({SITE_ORIGIN}/contact-us/)",
                f"- [WhatsApp {CONTACT_NAME}]({WA_ME})",
                "",
                f"Admissions: {CONTACT_NAME}, {PHONE_DISPLAY}, {EMAIL}.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_404(site: Path, html: str) -> None:
    (site / "404.html").write_text(html, encoding="utf-8")
