#!/usr/bin/env python3
"""Generate the HACCP template satellite pages from the live main page.

The main page (free-haccp-template.html) is the skeleton: gates, gallery,
bands, exit modal, tracking and mobile CSS are reused byte-for-byte. Only the
SEO surface (title, description, canonical/OG, breadcrumb, keyword H1, sub),
the who-downloads rows, the FAQ (visible + FAQPage JSON-LD) and the capture
source tag change per segment. Run from the repo root:

    python3 _build/build_template_satellites.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from template_satellites_config import SEGMENTS, PAGES_COUNT  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SKELETON = (ROOT / "free-haccp-template.html").read_text()

MAIN_URL = "https://blueroll.app/free-haccp-template.html"
MAIN_TITLE = "Free HACCP Plan Template UK: PDF &amp; Cleaning Schedule | Blueroll"
MAIN_DESC_RE = re.compile(r'(<meta name="description" content=")[^"]*(")')
MAIN_OG_DESC_RE = re.compile(r'(<meta property="og:description" content=")[^"]*(")')
MAIN_H1_RE = re.compile(r"(<h1 style=\"font-size: 17px;[^\"]*\">)[^<]*(</h1>)")
MAIN_SUB_RE = re.compile(r'(<p class="hero-sub"[^>]*>).*?(</p>)', re.S)
BREADCRUMB_LABEL = "Free HACCP Plan Template UK (PDF + Daily Logs)"
WHO_ROW_RE = re.compile(r'(<div class="who-row"[^>]*>\s*<span[^>]*>).*?(</span>\s*<p[^>]*>).*?(</p>\s*</div>)', re.S)
FAQ_BLOCK_RE = re.compile(
    r'(<h2[^>]*>Frequently asked questions</h2>\s*<div style="margin-top: 8px;">).*?(</div>)', re.S)
FAQPAGE_LD_RE = re.compile(r'<script type="application/ld\+json">\s*\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>', re.S)


def strip_tags(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def build(slug: str, cfg: dict) -> str:
    s = SKELETON
    url = f"https://blueroll.app/{cfg['file']}"

    s = s.replace(MAIN_URL, url)                      # canonical, og:url, JSON-LD urls
    s = s.replace(MAIN_TITLE, cfg["title"])           # <title> and og:title
    s = MAIN_DESC_RE.sub(lambda m: m.group(1) + cfg["desc"] + m.group(2), s)
    s = MAIN_OG_DESC_RE.sub(lambda m: m.group(1) + cfg["desc"] + m.group(2), s)
    s = s.replace(BREADCRUMB_LABEL, cfg["breadcrumb"])  # visible crumb + BreadcrumbList LD
    s = MAIN_H1_RE.sub(lambda m: m.group(1) + cfg["h1"] + m.group(2), s, count=1)
    s = MAIN_SUB_RE.sub(lambda m: m.group(1) + cfg["sub"] + m.group(2), s, count=1)

    rows = list(cfg["who_rows"])
    assert len(rows) == 3, slug
    def row_sub(m, _rows=iter(rows)):
        label, text = next(_rows)
        return m.group(1) + label + m.group(2) + text + m.group(3)
    s, n = WHO_ROW_RE.subn(row_sub, s)
    assert n == 3, f"{slug}: who rows replaced {n}"

    faq_html = "".join(
        f'\n    <h3 style="font-size: 15.5px; font-weight: 700; margin: 22px 0 0;">{q}</h3>'
        f'\n    <p style="font-size: 14px; color: #5c626b; line-height: 1.65; margin: 6px 0 0;">{a}</p>'
        for q, a in cfg["faq"])
    s, n = FAQ_BLOCK_RE.subn(lambda m: m.group(1) + faq_html + "\n  " + m.group(2), s, count=1)
    assert n == 1, f"{slug}: faq block"

    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip_tags(q),
         "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
        for q, a in cfg["faq"]]}
    s, n = FAQPAGE_LD_RE.subn(
        lambda m: '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False) + "\n</script>", s, count=1)
    assert n == 1, f"{slug}: faq ld"

    s = s.replace("source: 'haccp-template:' + placement", f"source: 'haccp-template:{slug}:' + placement")
    assert f"haccp-template:{slug}:" in s

    assert f"{PAGES_COUNT}-page" in s, f"{slug}: page count marker"
    return s


def main() -> None:
    for slug, cfg in SEGMENTS.items():
        out = ROOT / cfg["file"]
        out.write_text(build(slug, cfg))
        print(f"built {cfg['file']}")


if __name__ == "__main__":
    main()
