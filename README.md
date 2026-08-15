# Resonance AI — Static Site

A fast, fully static mirror of [schoolofcoreai.com](https://schoolofcoreai.com) with no backend or database.

## Deploy

Upload the **`site/`** folder to any static host (Netlify, GitHub Pages, S3, nginx, etc.).

## Preview locally

**Important:** Serve from the `site/` folder, not the project root.

```bash
# Easiest — double-click or run:
start.bat

# Or manually:
cd site
python -m http.server 8080
```

Open **http://localhost:8080** (not `/site/` — the server root IS the site).

- Home: http://localhost:8080/index.html
- Programs: http://localhost:8080/courses/index.html
- Example detail: http://localhost:8080/courses/generative-ai-course/index.html

Click **View program** on any card to open the full course page.

## Rebuild from source

```bash
# Install deps (one time)
pip install -r build/requirements.txt

# Scrape + generate + link audit
build.bat          # Windows
# or manually:
python build/scrape.py
python build/generate.py
python build/link_audit.py
```

## Structure

```
scai-clone/
  site/              ← deploy this
    index.html       ← homepage
    courses/         ← program listing + 19 detail pages
    hire-from-us/
    contact-us/
    mentors/
    roadmaps/
    comparisons/
    blogs/
    assets/css/      ← base.css, program.css, content.css
    assets/js/       ← nav.js, courses.js
  build/             ← scrape + generate scripts (not deployed)
    scrape.py
    generate.py
    pages.json       ← URL manifest (55 pages)
    data/            ← scraped JSON cache
    templates/       ← Jinja2 HTML templates
```

## Pages included (55)

- Home, courses listing, 17 program detail pages (+ 2 extras)
- Hire from us, contact, about, enterprise, mentors
- Privacy, terms, refund, register
- 5 roadmaps, 11 comparisons, 2 blog posts
- 4 city SEO landing pages

## Contact

Phone: **+91 87087 52385**  
WhatsApp: https://wa.me/918708752385
