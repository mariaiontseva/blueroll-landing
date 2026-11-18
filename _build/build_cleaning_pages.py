#!/usr/bin/env python3
"""Build the two cleaning-template landing pages (UK and US).

    kitchen-cleaning-schedule-template.html   UK, source haccp-template:cleaning:<placement> (gets the drip)
    restaurant-cleaning-checklist.html        US, source us-template:cleaning:<placement> (no British drip)

The tracking scripts at the top of <head>, the nav, the mobile menu and the
footer are taken from the live free-haccp-template.html, so the pages stay in
step with the main template page. The rest of <head> (meta, JSON-LD, CSS) and
everything between the nav and the footer is written here.

Layout (design pass 18.11.2026, shared with fridge-temperature-log.html,
food-temperature-log.html, restaurant-health-inspection-checklist.html and
allergen-matrix.html): breadcrumb, then a two-column hero with the H1, one
sentence, one CTA and the first sheet shown big. Below it, bands that alternate
white and grey, each with a visual anchor: how to use it beside the filled-in
sheet, a frequency scale or cards for real sets, what the law expects beside
the third sheet, the app screenshot for how Blueroll does it; then the FAQ,
one closing CTA and the sources.
The email gate and its script are unchanged: hero and bottom CTAs plus the
desktop exit-intent modal. On the UK pages ("offer": True) the state after
the download is the free-setup offer with one sign-up button.

PDFs and the preview images in uploads/ come from _build/build_cleaning_pdfs.py.
Run from the repo root:

    python3 _build/build_cleaning_pages.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKELETON = (ROOT / "free-haccp-template.html").read_text()
UK_URL = "https://blueroll.app/kitchen-cleaning-schedule-template.html"
US_URL = "https://blueroll.app/restaurant-cleaning-checklist.html"
ANON = re.search(r"var ANON = '([^']+)'", SKELETON).group(1)
IMG_V = "20261118b"
# Pixel size of the preview images in uploads/ (A4 and US Letter at 150 dpi). Only the ratio matters.
SIZE = {"en-GB": (1240, 1755), "en-US": (1240, 1605)}

CHECK = ('<span style="width: 14px; height: 14px; border-radius: 50%; background: #1f9d63; color: #fff; display: inline-flex; '
         'align-items: center; justify-content: center; font-size: 8px; flex-shrink: 0;">&#10003;</span>')


def _between(s, start, end_re):
    i = s.index(start)
    m = re.search(end_re, s[i:], flags=re.S)
    assert m, end_re
    return s[i:i + m.end()]


# Tracking scripts (Contentsquare, GA, geo-analytics), copied as they are.
TRACKING = SKELETON[SKELETON.index("<head>") + len("<head>"):SKELETON.index('<link rel="canonical"')].strip("\n")
assert "gtag('config', 'G-ZFY0GPZYYQ')" in TRACKING and "<title>" not in TRACKING
NAV = _between(SKELETON, "<!-- ============ NAV ============ -->", r'mm-cta">Start for free</a>\s*</div>')
_f = SKELETON.index("<!-- ============ FOOTER ============ -->")
FOOTER = SKELETON[_f:SKELETON.index("<!-- ============ FOOTER ============ -->", _f + 10) + len("<!-- ============ FOOTER ============ -->")]
# Same nav text as allergen-matrix.html (no em dashes), and a footer Pricing link that works off the home page.
for a, b in [("One kitchen, one folder — fully digital", "One kitchen, one folder, fully digital"),
             ("Printable pack — logs, schedules, checks", "Printable pack: logs, schedules, checks"),
             ("London, NYC &amp; SF — live inspection data", "London, NYC &amp; SF, live inspection data")]:
    NAV = NAV.replace(a, b)
FOOTER = FOOTER.replace('<a href="#pricing" class="foot-link">', '<a href="/#pricing" class="foot-link">')

BASE_CSS = """<style>
/* ============ base ============ */
* { box-sizing: border-box; }
body { margin: 0; background: #f6f7f8; color: #16181d; font-family: 'Geist', -apple-system, sans-serif; -webkit-font-smoothing: antialiased; }
a { color: #1f7a52; text-decoration: none; }
a:hover { color: #1f9d63; }
img { max-width: 100%; }

/* ============ nav and footer ============ */
.navlink { color: #41464d; display: flex; align-items: center; gap: 5px; white-space: nowrap; }
.navlink:hover { color: #16181d; }
.dd { position: relative; height: 100%; display: flex; align-items: center; }
.dd-menu { display: none; position: absolute; top: 50px; left: -8px; background: #fff; border: 1px solid #e7e9ec; border-radius: 14px; box-shadow: 0 16px 40px -20px rgba(16,24,40,.3); padding: 8px; cursor: default; z-index: 60; }
.dd:hover .dd-menu, .dd:focus-within .dd-menu { display: block; }
.dd-menu.dd-grid { width: 596px; display: none; }
.dd:hover .dd-menu.dd-grid, .dd:focus-within .dd-menu.dd-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px; }
.dd-item { display: flex; align-items: flex-start; gap: 11px; padding: 9px 10px; border-radius: 10px; }
.dd-item:hover { background: #f4f8f5; }
.dd-icon { width: 32px; height: 32px; border-radius: 9px; background: #eef6f1; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.dd-title { display: block; font-size: 13.5px; font-weight: 600; color: #16181d; }
.dd-sub { display: block; font-size: 12px; color: #7c828b; line-height: 1.4; margin-top: 1px; }
.tag-new { background: #eaf4ee; color: #1f7a52; font-size: 9.5px; font-weight: 700; border-radius: 20px; padding: 1px 6px; font-family: 'Geist Mono', monospace; }
.btn-green { background: #1f9d63; color: #fff; font-weight: 600; border-radius: 8px; white-space: nowrap; }
.btn-green:hover { background: #1c8e5a; color: #fff; }
.foot-link { color: #9aa0a8; }
.foot-link:hover { color: #fff; }
.gh0:hover { background: #24ab6d; color: #fff; }
.nav-burger { display: none; background: none; border: none; padding: 8px; margin-left: auto; cursor: pointer; color: #16181d; }
.mobile-menu { display: none; position: fixed; top: 64px; left: 0; right: 0; bottom: 0; background: #fff; z-index: 49; overflow-y: auto; padding: 8px 24px 40px; }
.mobile-menu.open { display: block; }
.mm-group { border-bottom: 1px solid #eef0f2; padding: 14px 0; }
.mm-label { font-size: 11px; font-weight: 700; letter-spacing: .08em; color: #8a9099; text-transform: uppercase; margin-bottom: 6px; }
.mm-link { display: flex; align-items: center; gap: 8px; padding: 9px 0; font-size: 15px; font-weight: 600; color: #16181d; }
.mm-cta { display: block; text-align: center; margin-top: 18px; padding: 13px; font-size: 15px; }
body.mm-lock { overflow: hidden; }
@media (max-width: 960px) {
  .nav-links { display: none !important; }
  .nav-signin { display: none !important; }
  .nav-burger { display: inline-flex; }
  .footer-grid { grid-template-columns: 1fr 1fr !important; }
  html, body { overflow-x: clip; }
  input, select, textarea { font-size: 16px !important; }
  .foot-link { display: inline-block; padding: 8px 0; }
  div[style*="margin: 22px auto 0"] a { display: inline-block; padding: 8px 2px; }
  div[style*="background: #14161b"] a { display: inline-block; padding: 6px 0; }
}
</style>"""

# Shared by the template pages. allergen-matrix.html carries a copy of this block: keep them in step.
TEMPLATE_CSS = """<style>
/* ============ template page (same block in allergen-matrix.html) ============ */
.tp-wrap { max-width: 1160px; margin: 0 auto; padding: 0 24px; }
.tp-hero { max-width: 1160px; margin: 32px auto 0; padding: 0 24px 104px; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 460px); gap: 72px; align-items: center; }
.tp-hero.tp-wide { grid-template-columns: minmax(0, 1fr) minmax(0, 620px); gap: 56px; }
.tp-hero h1 { font-size: 50px; line-height: 1.06; font-weight: 800; letter-spacing: -0.035em; color: #16181d; margin: 0; text-wrap: balance; }
.tp-lede { font-size: 18px; line-height: 1.6; color: #41464d; margin: 20px 0 0; max-width: 520px; text-wrap: pretty; }
.tp-cta { margin-top: 32px; max-width: 460px; }
.tp-sheet { margin: 0; }
.tp-sheet img { display: block; width: 100%; height: auto; background: #fff; border: 1px solid #e7e9ec; border-radius: 4px; box-shadow: 0 24px 48px -28px rgba(16,24,40,.35); }
.tp-shot { margin: 0; border: 1px solid #e7e9ec; border-radius: 14px; overflow: hidden; background: #f6f7f8; box-shadow: 0 32px 64px -40px rgba(16,24,40,.3); }
.tp-shot img { display: block; width: 100%; height: auto; }
.tp-band { padding: 104px 0; }
.tp-band.tp-white { background: #fff; border-top: 1px solid #eef0f2; border-bottom: 1px solid #eef0f2; }
.tp-band h2 { font-size: 32px; line-height: 1.18; font-weight: 800; letter-spacing: -0.03em; color: #16181d; margin: 0; text-wrap: balance; }
.tp-band h3 { font-size: 20px; line-height: 1.35; font-weight: 700; letter-spacing: -0.01em; color: #16181d; margin: 32px 0 0; }
.tp-band p, .tp-band li { font-size: 18px; line-height: 1.6; color: #41464d; text-wrap: pretty; }
.tp-band p { margin: 16px 0 0; }
.tp-band ol, .tp-band ul { margin: 18px 0 0; padding-left: 26px; }
.tp-band li { margin: 0 0 10px; padding-left: 4px; }
.tp-band b { color: #16181d; font-weight: 600; }
.tp-split { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 80px; align-items: center; }
.tp-split.tp-portrait { grid-template-columns: minmax(0, 1fr) minmax(0, 440px); }
.tp-split.tp-portrait.tp-left { grid-template-columns: minmax(0, 440px) minmax(0, 1fr); }
.tp-split.tp-left .tp-media { order: -1; }
.tp-text { max-width: 560px; }
.tp-head { max-width: 720px; }
.tp-narrow { max-width: 720px; }
.tp-cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; margin-top: 40px; }
.tp-cards.tp-c4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.tp-cards.tp-c5 { grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px; }
.tp-card { background: #fff; border: 1px solid #e7e9ec; border-radius: 16px; padding: 24px; }
.tp-white .tp-card { background: #f6f7f8; border-color: #eef0f2; }
.tp-card.tp-on { background: #eaf4ee; border-color: #cfe6d9; }
.tp-card .tp-big { font-size: 40px; line-height: 1; font-weight: 800; letter-spacing: -0.035em; color: #16181d; font-variant-numeric: tabular-nums; white-space: nowrap; }
.tp-band .tp-card h3 { font-size: 18px; margin: 0; }
.tp-band .tp-card .tp-big + h3 { margin-top: 14px; }
.tp-band .tp-card p { font-size: 16px; line-height: 1.55; color: #5c626b; margin: 8px 0 0; }
.tp-c5 .tp-card { padding: 20px; }
.tp-stack { display: grid; gap: 16px; }
.tp-cards.tp-small .tp-card { padding: 18px 20px; }
.tp-band .tp-small .tp-card p { font-size: 15px; margin-top: 4px; }
.tp-scale { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 40px; margin-top: 48px; position: relative; }
.tp-scale::before { content: ""; position: absolute; left: 8px; right: 0; top: 8px; height: 2px; background: #cfe6d9; }
.tp-stop { position: relative; }
.tp-stop::before { content: ""; display: block; width: 18px; height: 18px; border-radius: 50%; border: 2px solid #1f9d63; background: #1f9d63; position: relative; }
.tp-stop:nth-child(2)::before { background: #cfe6d9; }
.tp-stop:nth-child(3)::before { background: #fff; }
.tp-band .tp-stop h3 { margin-top: 22px; }
.tp-band .tp-stop ul { list-style: none; padding: 0; margin: 12px 0 0; }
.tp-band .tp-stop li { font-size: 16px; line-height: 1.45; padding: 10px 0; margin: 0; border-bottom: 1px solid #e7e9ec; }
.tp-table { margin: 24px 0 0; overflow-x: auto; -webkit-overflow-scrolling: touch; }
.tp-table table { width: 100%; border-collapse: collapse; }
.tp-table th, .tp-table td { font-size: 16px; line-height: 1.5; text-align: left; vertical-align: top; padding: 12px 20px 12px 0; border-bottom: 1px solid #e7e9ec; }
.tp-table th { font-weight: 700; color: #16181d; border-bottom-color: #c9ced4; }
.tp-table td { color: #41464d; }
.tp-table td:first-child { width: 32%; font-weight: 600; color: #16181d; }
.tp-table th:last-child, .tp-table td:last-child { padding-right: 0; }
.tp-faq { display: grid; grid-template-columns: minmax(0, 320px) minmax(0, 1fr); gap: 80px; }
.tp-faq .tp-qa h3:first-child { margin-top: 0; }
.tp-faq .tp-qa h3 { margin-top: 36px; }
.tp-faq .tp-qa p { margin-top: 10px; }
.tp-end { text-align: center; }
.tp-end .tp-cta { margin: 28px auto 0; }
.tp-sources { max-width: 720px; margin: 88px 0 0; padding-top: 40px; border-top: 1px solid #e2e4e8; }
.tp-band .tp-sources h2 { font-size: 28px; }
.tp-band ul.tp-src { list-style: none; padding-left: 0; }
.tp-band .tp-src li, .tp-band p.tp-note { font-size: 15px; line-height: 1.55; color: #5c626b; padding-left: 0; }
.tp-band .tp-src li { margin: 0 0 14px; }
.tp-src a { display: block; }
.tp-src span { display: block; font-size: 14px; color: #7c828b; }
@media (max-width: 960px) {
  .tp-hero, .tp-hero.tp-wide { grid-template-columns: minmax(0, 1fr); gap: 40px; padding-bottom: 72px; }
  .tp-hero h1 { font-size: 40px; }
  .tp-sheet { max-width: 520px; }
  .tp-band { padding: 72px 0; }
  .tp-split, .tp-split.tp-portrait, .tp-split.tp-portrait.tp-left { grid-template-columns: minmax(0, 1fr); gap: 40px; }
  .tp-split.tp-left .tp-media { order: 0; }
  .tp-cards, .tp-cards.tp-c4, .tp-cards.tp-c5 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .tp-faq { grid-template-columns: minmax(0, 1fr); gap: 28px; }
  .g-row { flex-direction: column; }
  .g-row .g-email, .g-row .g-send { flex: 0 0 auto !important; width: 100%; }
  .g-row .g-email { font-size: 16px; padding: 12px !important; }
  .g-row .g-send { padding: 14px !important; font-size: 15px !important; }
}
@media (max-width: 600px) {
  .tp-hero { margin-top: 16px; padding-bottom: 56px; }
  .tp-hero h1 { font-size: 34px; }
  .tp-lede { font-size: 17px; }
  .tp-cta { margin-top: 26px; }
  .tp-band { padding: 56px 0; }
  .tp-band h2 { font-size: 28px; }
  .tp-band h3 { font-size: 19px; }
  .tp-band p, .tp-band li { font-size: 17px; }
  .tp-cards, .tp-cards.tp-c4, .tp-cards.tp-c5 { grid-template-columns: minmax(0, 1fr); gap: 12px; margin-top: 28px; }
  .tp-card { padding: 20px; }
  .tp-nums .tp-card { display: grid; grid-template-columns: 104px minmax(0, 1fr); column-gap: 14px; align-items: start; }
  .tp-card .tp-big { font-size: 28px; }
  .tp-nums .tp-card .tp-big { grid-row: span 2; }
  .tp-band .tp-nums .tp-card .tp-big + h3 { margin-top: 0; }
  .tp-scale { grid-template-columns: minmax(0, 1fr); gap: 32px; margin-top: 32px; }
  .tp-scale::before { display: none; }
  .tp-table th, .tp-table td { font-size: 15px; padding-right: 14px; }
  .tp-sources { margin-top: 64px; }
  .tp-src a { padding: 11px 0 10px; }
}
</style>"""


# What a UK visitor sees after the download starts: one offer, one button (18.11.2026). The sign-up page has no
# parameter that preselects "Set it up for me"; that choice is the first screen after sign-up.
SETUP_URL = "https://app.blueroll.app/onboarding"
SETUP_OFFER = ("Send us a photo of your paper sheets and we&rsquo;ll set up your checks on your team&rsquo;s phones "
               "for free, ready by 10:00 the next working day.")
SETUP_BUTTON = "Start 14 days free, no card"
SENT = """<div class="g-sent" style="display: none;">
          <div style="display: flex; align-items: center; justify-content: center; gap: 11px; background: #eaf4ee; border: 1px solid #cfe6d9; border-radius: 12px; padding: 15px 18px;">
            <span style="width: 24px; height: 24px; border-radius: 50%; background: #1f9d63; color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0;">&#10003;</span>
            <span style="font-size: 14.5px; font-weight: 600; color: #14532d;">Downloading. Check your Downloads folder</span>
          </div>
        </div>"""
SENT_OFFER = f"""<div class="g-sent" style="display: none;">
          <div style="background: #fff; border: 1px solid #e2e4e8; border-radius: 12px; padding: 18px 20px; box-shadow: 0 20px 44px -28px rgba(16,24,40,.35); text-align: left;">
            <div style="font-size: 12.5px; font-weight: 600; color: #1f7a52;">&#10003; Your PDF is downloading.</div>
            <div style="font-size: 15px; font-weight: 600; line-height: 1.45; color: #16181d; margin: 8px 0 14px; text-wrap: pretty;">{SETUP_OFFER}</div>
            <a class="g-setup btn-green" href="{SETUP_URL}" style="display: inline-block; font-size: 14.5px; font-weight: 700; padding: 12px 20px;">{SETUP_BUTTON}</a>
          </div>
        </div>"""
SETUP_JS = """
    var setup = g.querySelector('.g-setup');
    if (setup) setup.addEventListener('click', function () { track('template_setup_cta', { placement: '%(slug)s:' + loc, lead_source: SOURCE + ':' + loc, transport_type: 'beacon' }); });"""


def gate(loc, button, note, align="flex-start", offer=False):
    return f"""<div data-gate="{loc}">
        <div class="g-idle" style="display: flex; justify-content: {align};">
          <button class="g-open gh0" style="background: #1f9d63; color: #fff; font-family: 'Geist', sans-serif; font-size: 15.5px; font-weight: 700; padding: 15px 32px; border: none; border-radius: 8px; cursor: pointer; box-shadow: 0 12px 32px -14px rgba(31,157,99,.8); width: 100%; max-width: 340px;">{button}</button>
        </div>
        <div class="g-form" style="display: none;">
          <div class="g-row" style="display: flex; flex-wrap: wrap; gap: 8px; background: #fff; border: 1px solid #e2e4e8; border-radius: 12px; padding: 8px; box-shadow: 0 20px 44px -28px rgba(16,24,40,.35); text-align: left;">
            <input class="g-email" type="email" placeholder="Your work email" autocomplete="email" style="flex: 1 1 180px; min-width: 0; font-family: 'Geist', sans-serif; font-size: 16px; padding: 10px 12px; border: none; border-radius: 8px; background: transparent; color: #16181d; outline: none; box-shadow: inset 0 0 0 1.5px #e2e4e8;">
            <button class="g-send" style="flex: 1 1 auto; background: #1f9d63; color: #fff; font-family: 'Geist', sans-serif; font-size: 14.5px; font-weight: 700; padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; white-space: nowrap;">Send me the PDF</button>
          </div>
          <div style="font-size: 12px; color: #8a9099; line-height: 1.5; margin-top: 10px; text-align: left;">{note}</div>
        </div>
        {SENT_OFFER if offer else SENT}
      </div>"""


def strip_tags(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))).strip()


def render(blocks):
    out = []
    for b in blocks:
        kind = b[0]
        if kind == "h3":
            out.append(f"<h3>{b[1]}</h3>")
        elif kind == "p":
            out.append(f"<p>{b[1]}</p>")
        elif kind in ("ol", "ul"):
            items = "".join(f"\n          <li>{x}</li>" for x in b[1])
            out.append(f"<{kind}>{items}\n        </{kind}>")
        elif kind == "table":
            head = "".join(f"<th>{h}</th>" for h in b[1])
            rows = "".join("\n            <tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in b[2])
            out.append(f'<div class="tp-table"><table>\n          <thead><tr>{head}</tr></thead>\n          <tbody>{rows}\n          </tbody>\n        </table></div>')
        else:
            raise ValueError(kind)
    return "\n        ".join(out)


# App screenshot, cropped in CSS to the checklist itself: no top bar (business and user names) and no sidebar.
SHOTS = {
    "checklists": {"src": "/uploads/shot-checklists.png?v=20260813", "w": 3024, "h": 1720, "crop": (760, 150, 2730, 1668),
                   "alt": "Today&rsquo;s checklists in Blueroll: opening checks, fridge and freezer temperatures, probe calibration and hot-hold temperatures, each marked done"},
}


def shot_html(key):
    s = SHOTS[key]
    x0, y0, x1, y1 = s["crop"]
    cw, ch = x1 - x0, y1 - y0
    style = (f"width: {100 * s['w'] / cw:.3f}%; max-width: none; "
             f"margin: {-100 * y0 / cw:.3f}% 0 0 {-100 * x0 / cw:.3f}%;")
    return (f'<figure class="tp-shot" style="aspect-ratio: {cw} / {ch};">'
            f'<img src="{s["src"]}" width="{s["w"]}" height="{s["h"]}" alt="{s["alt"]}" loading="lazy" style="{style}"></figure>')


def sheet_html(src, w, h, alt, eager=False):
    extra = ' fetchpriority="high"' if eager else ' loading="lazy"'
    return f'<figure class="tp-sheet"><img src="{src}" width="{w}" height="{h}" alt="{alt}"{extra}></figure>'


def section_html(sec, white, media_left, sheet):
    """One band. sheet(i) returns the <figure> for sheet i of this template."""
    band = "tp-band tp-white" if white else "tp-band"
    sid = f' id="{sec["id"]}"' if sec.get("id") else ""
    kind = sec["type"]
    if kind == "split":
        if "sheet" in sec:
            media, shape = sheet(sec["sheet"]), sec.get("shape", "tp-portrait")
        elif "shot" in sec:
            media, shape = shot_html(sec["shot"]), ""
        else:
            media, shape = sec["media"], sec.get("shape", "")
        cls = " ".join(x for x in ("tp-split", shape, "tp-left" if media_left else "") if x)
        return f"""
<section class="{band}"{sid}>
  <div class="tp-wrap">
    <div class="{cls}">
      <div class="tp-text">
        <h2>{sec['h2']}</h2>
        {render(sec['blocks'])}
      </div>
      <div class="tp-media">{media}</div>
    </div>
  </div>
</section>"""
    head = f"<h2>{sec['h2']}</h2>" + ("\n      " + render(sec["intro"]) if sec.get("intro") else "")
    after = f'\n    <div class="tp-head">\n      {render(sec["after"])}\n    </div>' if sec.get("after") else ""
    if kind == "cards":
        cards = []
        for c in sec["cards"]:
            big, title, text = c[:3]
            on = " tp-on" if len(c) > 3 and c[3] else ""
            cards.append(f'\n      <div class="tp-card{on}">' + (f'<div class="tp-big">{big}</div>' if big else "")
                         + f"<h3>{title}</h3>" + (f"<p>{text}</p>" if text else "") + "</div>")
        cls = " ".join(x for x in ("tp-cards", sec.get("cols", ""), "tp-nums" if any(c[0] for c in sec["cards"]) else "") if x)
        body = f'<div class="{cls}">{"".join(cards)}\n    </div>'
    elif kind == "scale":
        stops = "".join(f'\n      <div class="tp-stop"><h3>{t}</h3><ul>' + "".join(f"<li>{x}</li>" for x in items) + "</ul></div>"
                        for t, items in sec["stops"])
        body = f'<div class="tp-scale">{stops}\n    </div>'
    else:
        raise ValueError(kind)
    return f"""
<section class="{band}"{sid}>
  <div class="tp-wrap">
    <div class="tp-head">
      {head}
    </div>
    {body}{after}
  </div>
</section>"""


def sections_html(sections, sheet, first_white=True):
    """Bands alternate white and grey; split sections alternate the image left and right (the hero has it right)."""
    out, white, left = [], first_white, True
    for sec in sections:
        out.append(section_html(sec, white, left, sheet))
        white = not white
        if sec["type"] == "split":
            left = not left
    return "".join(out), white


def faq_html(faq, white):
    qa = "".join(f"\n        <h3>{q}</h3>\n        <p>{a}</p>" for q, a in faq)
    return f"""
<section class="tp-band{' tp-white' if white else ''}">
  <div class="tp-wrap">
    <div class="tp-faq">
      <h2>Frequently asked questions</h2>
      <div class="tp-qa">{qa}
      </div>
    </div>
  </div>
</section>"""


def end_html(h2, gate_html, sources, white, note=""):
    src = "".join(f'\n          <li><a href="{u}">{t}</a><span>{p}</span></li>' for t, u, p in sources)
    note_html = f'\n        <p class="tp-note">{note}</p>' if note else ""
    return f"""
<section class="tp-band{' tp-white' if white else ''}">
  <div class="tp-wrap">
    <div class="tp-end">
      <h2>{h2}</h2>
      <div class="tp-cta">
      {gate_html}
      </div>
    </div>
    <div class="tp-sources">
        <h2>Sources</h2>
        <ul class="tp-src">{src}
        </ul>{note_html}
    </div>
  </div>
</section>
"""


def build_head(cfg):
    title = cfg["title"]
    og_title = title.replace(" | Blueroll", "")
    desc = cfg["desc"]
    img = f'https://blueroll.app/uploads/{cfg["img"]}-{cfg.get("og_page", 2)}.png'
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
        for q, a in cfg["faq"]]}
    doc_ld = {"@context": "https://schema.org", "@type": "DigitalDocument", "name": cfg["doc_name"],
              "description": html.unescape(desc), "url": cfg["url"], "contentUrl": "https://blueroll.app/" + cfg["pdf"],
              "encodingFormat": "application/pdf", "inLanguage": cfg["lang"], "isAccessibleForFree": True,
              "dateModified": "2026-11-18", "publisher": {"@type": "Organization", "name": "Blueroll", "url": "https://blueroll.app/"}}
    crumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Blueroll", "item": "https://blueroll.app/"},
        {"@type": "ListItem", "position": 2, "name": "Free Tools", "item": "https://blueroll.app/tools.html"},
        {"@type": "ListItem", "position": 3, "name": strip_tags(cfg["crumb"]), "item": cfg["url"]}]}
    ld = "\n".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + "</script>"
                   for x in (faq_ld, doc_ld, crumb_ld))
    # UK/US pairs point at each other; x-default is the UK page. A page with no pair sets "hreflang": False.
    alternates = ""
    if cfg.get("hreflang", True):
        uk, us = cfg.get("uk_url", UK_URL), cfg.get("us_url", US_URL)
        alternates = (f'\n<link rel="alternate" hreflang="en-GB" href="{uk}">'
                      f'\n<link rel="alternate" hreflang="en-US" href="{us}">'
                      f'\n<link rel="alternate" hreflang="x-default" href="{uk}">')
    return f"""<!DOCTYPE html>
<html lang="{cfg['lang']}">
<head>
{TRACKING}
<link rel="canonical" href="{cfg['url']}">{alternates}
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Blueroll">
<meta property="og:url" content="{cfg['url']}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
{ld}
{BASE_CSS}
<link rel="stylesheet" href="/site-footer.css?v=20260813">
{TEMPLATE_CSS}
</head>
<body>
{NAV}
"""


def build_body(cfg):
    w, h = SIZE[cfg["lang"]]
    alts = cfg["alts"]

    def sheet(i, eager=False):
        return sheet_html(f'/uploads/{cfg["img"]}-{i}.png?v={IMG_V}', w, h, alts[i - 1], eager)

    bands, white = sections_html(cfg["sections"], sheet)
    offer = cfg.get("offer", False)
    # UK pages show the free-setup offer inside the gate instead; the US pages keep the small bridge.
    bridge = "" if offer else f"""
      <div class="g-bridge" style="display: none; flex-wrap: wrap; align-items: center; gap: 14px; background: #fff; border: 1px solid #e7e9ec; border-radius: 14px; padding: 14px 16px; margin-top: 12px; text-align: left;">
        <div style="display: flex; align-items: center; gap: 8px; background: #f6f7f8; border: 1px solid #eef0f2; border-radius: 9px; padding: 8px 11px; font-size: 11.5px; white-space: nowrap; flex-shrink: 0;">{CHECK}<span style="font-weight: 600;">{cfg['chip'][0]}</span><span style="color: #1f7a52; font-weight: 700; font-variant-numeric: tabular-nums; padding-left: 8px;">{cfg['chip'][1]}</span></div>
        <div style="flex: 1 1 170px; min-width: 0;">
          <div style="font-size: 13px; font-weight: 600; line-height: 1.4;">{cfg['bridge']}</div>
          <a href="/haccp-checklists.html" style="font-size: 12.5px; font-weight: 700;">See how, 2 min tour &rarr;</a>
        </div>
      </div>"""
    return f"""
<div style="max-width: 1160px; margin: 22px auto 0; padding: 0 24px; font-size: 12.5px; color: #8a9099;"><a href="/">Blueroll</a> <span style="color: #c6cad0;">›</span> <a href="/tools.html">Free Tools</a> <span style="color: #c6cad0;">›</span> <span style="color: #5c626b; font-weight: 600;">{cfg['crumb']}</span></div>

<!-- hero -->
<div class="tp-hero">
  <div>
    <h1>{cfg['h1']}</h1>
    <p class="tp-lede">{cfg['lede']}</p>
    <div class="tp-cta">
      {gate('hero', cfg['button'], cfg['note'], offer=offer)}{bridge}
    </div>
  </div>
  {sheet(1, eager=True)}
</div>
{bands}
{faq_html(cfg['faq'], white)}
{end_html(cfg['end_h2'], gate('bottom', cfg['button'], cfg['note'], 'center', offer=offer), cfg['sources'], not white)}"""



def build_tail(cfg):
    modal = f"""<!-- exit-intent modal (desktop) -->
<div id="tpl-exit" style="display: none; position: fixed; inset: 0; z-index: 100; background: rgba(10,20,15,.45); backdrop-filter: blur(3px); align-items: center; justify-content: center; padding: 24px;">
  <div style="position: relative; background: #fff; border-radius: 20px; padding: 36px; width: 100%; max-width: 460px; box-shadow: 0 40px 80px -30px rgba(16,24,40,.5);">
    <button id="tpl-exit-close" aria-label="Close" style="position: absolute; top: 14px; right: 14px; width: 36px; height: 36px; border: none; border-radius: 50%; background: #f2f3f5; color: #41464d; font-size: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; font-family: 'Geist', sans-serif;">&#10005;</button>
    <h2 style="font-size: 26px; font-weight: 800; letter-spacing: -0.03em; line-height: 1.15; margin: 0; padding-right: 36px;">{cfg['exit_h2']}</h2>
    <p style="font-size: 14px; color: #5c626b; line-height: 1.6; margin: 10px 0 16px;">{cfg['exit_p']}</p>
    {gate('exit', cfg['button'], cfg['note'], 'center', offer=cfg.get('offer', False))}
  </div>
</div>
"""
    script = """
<script>
(function () {
  var SB = 'https://rszrggreuarvodcqeqrj.supabase.co';
  var ANON = '%(anon)s';
  var PDF = '/%(pdf)s';
  var SOURCE = '%(source)s';
  var downloaded = false;
  try { downloaded = !!localStorage.getItem('br-tpl-downloaded'); } catch (e) {}

  function track(name, params) { if (typeof gtag === 'function') gtag('event', name, params || {}); }
  function download() {
    var a = document.createElement('a');
    a.href = PDF; a.download = PDF.slice(1);
    document.body.appendChild(a); a.click(); a.remove();
  }

  function deliver(email, placement) {
    try { localStorage.setItem('br-tpl-downloaded', '1'); } catch (e) {}
    downloaded = true;
    fetch(SB + '/rest/v1/template_leads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'apikey': ANON, 'Authorization': 'Bearer ' + ANON, 'Prefer': 'return=minimal' },
      body: JSON.stringify({ email: email, source: SOURCE + ':' + placement, page: window.location.pathname, user_agent: navigator.userAgent.slice(0, 250) })
    }).catch(function () {});
    fetch('https://formsubmit.co/ajax/hello@blueroll.app', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ email: email, _subject: '%(subject)s: ' + email, source: SOURCE, placement: placement, page: window.location.href })
    }).catch(function () {});
    track('haccp_template_download', { placement: '%(slug)s:' + placement, email_domain: email.split('@')[1] });
    download();
  }

  document.querySelectorAll('[data-gate]').forEach(function (g) {
    var loc = g.getAttribute('data-gate');
    var idle = g.querySelector('.g-idle'), form = g.querySelector('.g-form'), sent = g.querySelector('.g-sent');
    var input = g.querySelector('.g-email'), send = g.querySelector('.g-send'), open = g.querySelector('.g-open');
    function showForm() {
      idle.style.display = 'none'; form.style.display = 'block';
      track('haccp_form_open', { placement: '%(slug)s:' + loc });
      setTimeout(function () { input.focus(); }, 30);
    }
    function submit() {
      var email = (input.value || '').trim();
      if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) {
        input.style.boxShadow = 'inset 0 0 0 1.5px #d64545'; input.focus(); return;
      }
      form.style.display = 'none'; sent.style.display = 'block';
      var bridge = document.querySelector('.g-bridge');
      if (loc === 'hero' && bridge) bridge.style.display = 'flex';
      deliver(email, loc);
    }
    open.addEventListener('click', showForm);
    send.addEventListener('click', submit);
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); submit(); } });
    input.addEventListener('input', function () { input.style.boxShadow = 'inset 0 0 0 1.5px #e2e4e8'; });%(setup_js)s
  });

  // Links in emails can land here with ?dl=1: start the download and log the click.
  if (/[?&]dl=1/.test(location.search)) { track('haccp_email_pdf_click', { placement: '%(slug)s' }); download(); }

  // Exit intent: desktop, once per session, never after a download.
  var modal = document.getElementById('tpl-exit');
  if (modal) {
    var close = function () { modal.style.display = 'none'; };
    document.getElementById('tpl-exit-close').addEventListener('click', close);
    modal.addEventListener('click', function (e) { if (e.target === modal) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
    document.addEventListener('mouseout', function (e) {
      if (e.relatedTarget || e.clientY > 8) return;
      if (window.innerWidth < 900 || downloaded) return;
      try { if (sessionStorage.getItem('br-exit-shown')) return; sessionStorage.setItem('br-exit-shown', '1'); } catch (err) {}
      modal.style.display = 'flex';
      track('haccp_exit_intent_shown', { placement: '%(slug)s' });
      var f = modal.querySelector('.g-idle'); if (f && f.style.display !== 'none') modal.querySelector('.g-open').click();
    });
  }
})();
</script>
</body>
</html>
""" % {"anon": ANON, "pdf": cfg["pdf"], "source": cfg["source"], "subject": cfg["subject"], "slug": cfg["slug"],
       "setup_js": (SETUP_JS % {"slug": cfg["slug"]}) if cfg.get("offer") else ""}
    return FOOTER + "\n\n" + modal + script


def check(cfg, page):
    """Fail loudly on the things the design pass asks for."""
    title = html.unescape(re.search(r"<title>(.*?)</title>", page).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', page).group(1))
    assert 50 <= len(title) <= 60 and title.endswith("| Blueroll"), (cfg["file"], len(title), title)
    assert 140 <= len(desc) <= 158, (cfg["file"], len(desc), desc)
    assert page.count("<h1") == 1, cfg["file"]
    assert page.count('data-gate="') == 3, cfg["file"]
    assert "—" not in page and "&mdash;" not in page, cfg["file"]
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', page, flags=re.S):
        json.loads(m.group(1))
    return title, desc


def build(configs):
    for cfg in configs:
        page = build_head(cfg) + build_body(cfg) + "\n" + build_tail(cfg)
        title, desc = check(cfg, page)
        (ROOT / cfg["file"]).write_text(page)
        print(f"built {cfg['file']}\n  title ({len(title)}): {title}\n  desc ({len(desc)}): {desc}")


UK = {
    "file": "kitchen-cleaning-schedule-template.html", "url": UK_URL, "uk_url": UK_URL, "us_url": US_URL, "lang": "en-GB",
    "slug": "cleaning", "source": "haccp-template:cleaning", "subject": "New cleaning schedule download (UK)",
    "pdf": "blueroll-kitchen-cleaning-schedule.pdf", "img": "cleaning-uk-page",
    "title": "Kitchen Cleaning Schedule Template UK: Free PDF | Blueroll",
    "desc": "Free kitchen cleaning schedule template for UK food businesses: a weekly schedule, a filled-in example and a monthly deep-clean log. Printable A4 PDF.",
    "doc_name": "Kitchen cleaning schedule template (UK)",
    "crumb": "Kitchen cleaning schedule template",
    "h1": "Free kitchen cleaning schedule template",
    "lede": "A printable A4 weekly cleaning schedule for UK kitchens, with the jobs, methods and frequencies already written in, plus a filled-in example and a monthly deep-clean log.",
    "button": "Get the free schedule",
    "note": "The PDF downloads straight away. We also email you our full 16-page HACCP pack, then two short follow-ups. Unsubscribe anytime.",
    "offer": True,
    "chip": ("Floors &middot; SR", "21:40"),
    "bridge": "This same schedule ticks itself off in Blueroll",
    "alts": ["Blank weekly kitchen cleaning schedule: each job with how often and how to clean it, and a column for each day of the week",
             "Filled-in kitchen cleaning schedule, with initials against each job",
             "Blank monthly and deep-clean log"],
    "sections": [
        {"type": "split", "sheet": 2, "h2": "How to use the schedule", "blocks": [
            ("ol", ["Pin the weekly sheet up where the cleaning is done.",
                    "Cross out what you do not have, add your own equipment and set the frequencies to how busy you are.",
                    "Initial each job when it is done, at the time it is done.",
                    "At the end of the week, a manager checks the sheet, signs it and files it."]),
            ("p", 'It fits the Cleaning section of <a href="sfbb-guide.html">Safer Food, Better Business</a>. The <a href="free-haccp-template.html">16-page HACCP pack</a>, the <a href="fridge-temperature-log.html">fridge temperature log</a> and the <a href="eho-inspection-checklist.html">EHO inspection checklist</a> are free too.')]},
        {"type": "scale", "h2": "How often each job comes round", "intro": [
            ("p", "The schedule already lists these jobs. Move them to suit how busy you are.")],
         "stops": [("After use and daily", ["Work surfaces and chopping boards", "Handles, taps and the till", "Handwash basins and sinks",
                                            "Hobs, fryer and microwave", "Fridge seals", "Floors and bins"]),
                   ("Weekly", ["Fridge interiors and shelves", "Extractor hood and filters", "Walls and splashbacks",
                               "Dry store shelves", "Dishwasher"]),
                   ("Monthly or less often", ["Defrosting freezers", "Behind and under equipment", "Drains",
                                              "Light fittings and fly screens", "Whole-kitchen deep clean",
                                              "Extraction ductwork, on your insurer&rsquo;s TR19 schedule"])]},
        {"type": "split", "sheet": 3, "h2": "What the law expects", "blocks": [
            ("p", "UK food hygiene law requires premises to be kept clean, and equipment that touches food to be cleaned and, where necessary, disinfected. The Food Standards Agency asks for a cleaning schedule that says what gets cleaned, how often and with which products."),
            ("h3", "Clean, then disinfect"),
            ("ol", ["Scrape off food and debris.", "Wash with hot water and detergent, then rinse.",
                    "Apply a disinfectant or sanitiser and leave it for the contact time on the label.",
                    "Rinse if the label says so, then air-dry or use a single-use towel."]),
            ("p", "Disinfectants and sanitisers should meet BS EN 1276 or BS EN 13697.")]},
        {"type": "cards", "h2": "What an inspector scores", "intro": [
            ("p", "A food hygiene rating comes from three scores. Cleaning and your records count towards two of them.")],
         "cards": [(None, "Food handling", "How food is prepared, cooked, reheated, cooled and stored."),
                   (None, "Condition of the premises", "Cleanliness, layout, lighting, ventilation and pest control. A clean kitchen scores here.", True),
                   (None, "Confidence in management", "Your food safety system and records. A signed cleaning schedule scores here.", True)],
         "after": [("p", 'A schedule nobody signs, a week initialled in one pen, sanitiser mixed by guesswork and one cloth for raw and ready-to-eat areas all lose marks. <a href="food-hygiene-ratings-explained.html">Food hygiene ratings explained</a> shows how the scores add up.')]},
        {"type": "split", "shot": "checklists", "h2": "How Blueroll does it", "blocks": [
            ("p", 'Blueroll puts the same schedule on your team&rsquo;s phones. Each job is ticked with a name and a time, a manager signs off the finished list, and the record files itself, ready for an inspection. See <a href="haccp-checklists.html">how the checklists work</a>.'),
            ("p", 'It costs &pound;24.99 per site per month after a 14-day free trial, with no card needed, and we set it up for you, free. <a href="https://app.blueroll.app/">Start the free trial</a>.')]},
    ],
    "faq": [
        ("How often should a commercial kitchen be cleaned?",
         "Food-contact surfaces after every use, the rest of the kitchen every day, and fridges, extractor filters and walls every week. Deeper jobs such as defrosting freezers and cleaning behind equipment usually go monthly, and extraction ductwork follows your insurer's TR19 schedule. The template lists all of these, so you only adjust the frequencies to how busy you are."),
        ("Is a paper cleaning schedule enough for an EHO?",
         'Yes, as long as each job is signed when it is done, by the person who did it, and a manager checks the sheet. Inspectors question a week filled in with one pen at the end. When paper gets tedious, <a href="haccp-checklists.html">digital checklists</a> keep the same record with the time and the name on every tick.'),
        ("Which disinfectant should I use?",
         "One that meets BS EN 1276 or BS EN 13697, used at the dilution and for the contact time on the label. Inspectors check the bottle, so keep the product name on the schedule."),
        ("Is this template really free?",
         "Yes. No charge, no account and no watermark. Enter your email, the PDF downloads, and you can print it for as long as paper works for you."),
    ],
    "end_h2": "Get the free cleaning schedule",
    "sources": [
        ("Food hygiene for businesses: cleaning", "https://www.gov.uk/food-hygiene-businesses/cleaning", "Food Standards Agency, GOV.UK"),
        ("Safer food, better business for caterers", "https://www.gov.uk/government/publications/safer-food-better-business-for-caterers", "Food Standards Agency, GOV.UK"),
        ("Regulation (EC) No 852/2004 on the hygiene of foodstuffs, Annex II", "https://www.legislation.gov.uk/eur/2004/852/annex/II", "legislation.gov.uk"),
        ("Food hygiene rating scheme: guidance for businesses", "https://www.gov.uk/government/publications/food-hygiene-rating-scheme-fhrs-guidance-for-businesses/food-hygiene-rating-scheme-fhrs-guidance-for-businesses", "Food Standards Agency, GOV.UK"),
    ],
    "exit_h2": "Take the schedule with you",
    "exit_p": "Three printable sheets: the weekly schedule, a filled-in example and the monthly deep-clean log, straight to your Downloads.",
}

CITY_LINKS = ('<a href="nyc-restaurant-grade.html">New York City</a>, <a href="la-restaurant-grade.html">Los Angeles</a>, '
              '<a href="sf-restaurant-inspection.html">San Francisco</a>, <a href="chicago-restaurant-inspection.html">Chicago</a> '
              'and <a href="seattle-restaurant-inspection.html">Seattle</a>')
FOOD_CODE = ("FDA Food Code 2026", "https://www.fda.gov/food/fda-food-code/food-code-2026", "U.S. Food and Drug Administration")

US = {
    "file": "restaurant-cleaning-checklist.html", "url": US_URL, "uk_url": UK_URL, "us_url": US_URL, "lang": "en-US",
    "slug": "us-cleaning", "source": "us-template:cleaning", "subject": "New restaurant cleaning checklist download (US)",
    "pdf": "blueroll-restaurant-cleaning-checklist.pdf", "img": "cleaning-us-page",
    "title": "Restaurant Cleaning Checklist: Free Printable PDF | Blueroll",
    "desc": "Free restaurant cleaning checklist: daily kitchen, front-of-house and restroom tasks, weekly and monthly jobs and a sanitizer log, based on the FDA Food Code.",
    "doc_name": "Restaurant cleaning checklist (US)",
    "crumb": "Restaurant cleaning checklist",
    "h1": "Free restaurant cleaning checklist",
    "lede": "A printable daily cleaning checklist for the kitchen, front of house and restrooms, plus a filled-in example and a weekly, monthly and sanitizer log, built on the FDA Food Code.",
    "button": "Get the free checklist",
    "note": "The PDF downloads right away. We don&rsquo;t share your email.",
    "chip": ("Prep tables &middot; JM", "2:05 pm"),
    "bridge": "This same checklist ticks itself off in Blueroll",
    "alts": ["Blank daily restaurant cleaning checklist: kitchen, front-of-house and restroom tasks with when and how, and a column for each day",
             "Filled-in daily restaurant cleaning checklist, with initials against each task",
             "Blank weekly and monthly cleaning log with a sanitizer test-strip log"],
    "sections": [
        {"type": "split", "sheet": 2, "h2": "How to use the checklist", "blocks": [
            ("ol", ["Post the daily checklist by the dish pit.",
                    "Cross off tasks you don&rsquo;t have and add your own equipment.",
                    "Initial each task when it&rsquo;s done, at the time it&rsquo;s done.",
                    "Test every new sanitizer bucket and write the reading on the sanitizer log.",
                    "Have a manager check the sheets and keep them on file for your inspector."]),
            ("p", 'The <a href="food-temperature-log.html">food temperature log</a> and the <a href="restaurant-health-inspection-checklist.html">restaurant health inspection checklist</a> are free too.')]},
        {"type": "scale", "h2": "How often each task comes round", "intro": [
            ("p", "The checklist already lists these tasks. Move them to suit your volume and your equipment.")],
         "stops": [("Every shift and daily", ["Prep tables and food-contact surfaces", "Cutting boards and utensils", "Sanitizer buckets",
                                              "Handwashing sinks", "Flat-top, grill and fryer", "Reach-in handles and gaskets",
                                              "Dish machine", "Floors, drains and trash", "Dining room, drink station and restrooms"]),
                   ("Weekly", ["Walk-in shelves, floor and door gasket", "Hood filters", "Oven interiors",
                               "Walls behind the line", "Coffee equipment"]),
                   ("Monthly or less often", ["Ice machine", "Freezers", "Behind and under equipment",
                                              "Grease trap, on your hauler&rsquo;s schedule",
                                              "Hood and ducts, on the NFPA 96 schedule for your cooking volume"])]},
        {"type": "split", "sheet": 3, "h2": "What the Food Code expects", "blocks": [
            ("p", "Inspectors check that food-contact surfaces are clean and sanitized, that sanitizer is at the right strength, and that handwashing sinks are stocked and used only for handwashing. Most state and local codes are based on the FDA Food Code, and your local code is the one that applies."),
            ("h3", "Clean, rinse, sanitize"),
            ("ol", ["Scrape off food and debris.", "Wash with detergent and warm water.", "Rinse with clean water.",
                    "Sanitize at the right strength for the contact time on the label.", "Let it air-dry."]),
            ("p", "Surfaces in constant use with TCS food need this at least every 4 hours (Food Code 4-602.11).")]},
        {"type": "cards", "cols": "tp-c4", "h2": "What costs points at an inspection", "intro": [
            ("p", f"In cities with letter grades and scores, these show up as violations that lower your grade. How inspections are scored in {CITY_LINKS}.")],
         "cards": [(None, "Sanitizer at the wrong strength", "Test every bucket with the matching strips and write the reading down."),
                   (None, "Wiping cloths left out", "Keep them in sanitizer between uses, not on the counter."),
                   (None, "A blocked handwashing sink", "Stocked with soap and towels, and used only for handwashing."),
                   (None, "No record of cleaning", "Initials on every task show it happens every day, not only on inspection day.")]},
        {"type": "split", "shot": "checklists", "h2": "How Blueroll does it", "blocks": [
            ("p", 'Blueroll puts the same checklist on your team&rsquo;s phones. Every task is ticked with a name and a time, a manager signs off the finished list, and the record is ready to show your health inspector. See <a href="haccp-checklists.html">how the checklists work</a>.'),
            ("p", 'Try it free for 14 days, no card needed. <a href="https://app.blueroll.app/">Start the free trial</a>.')]},
    ],
    "faq": [
        ("How often should a restaurant be cleaned?",
         "Food-contact surfaces after each task and at least every 4 hours while in use; the line, floors, restrooms and dining room every day; walk-ins, hood filters and ovens every week; freezers, ice machines and behind equipment every month. Hoods and ducts follow the NFPA 96 schedule for your cooking volume."),
        ("What sanitizer concentration should I use?",
         "Follow the product label and your local health code. As a guide, chlorine bleach solutions are usually 50 to 100 ppm and quaternary ammonium (quat) solutions often 200 to 400 ppm. Test every new bucket with the matching strips and write the reading on the sanitizer log."),
        ("Is this checklist free?",
         "Yes. No charge, no account and no watermark. Enter your email, the PDF downloads, and you can print as many copies as you need."),
    ],
    "end_h2": "Get the free cleaning checklist",
    "sources": [
        FOOD_CODE,
        ("NFPA 96, Standard for Ventilation Control and Fire Protection of Commercial Cooking Operations", "https://www.nfpa.org/codes-and-standards/nfpa-96-standard-development/96", "National Fire Protection Association"),
    ],
    "exit_h2": "Take the checklist with you",
    "exit_p": "Three printable sheets: the daily checklist, a filled-in example, and the weekly, monthly and sanitizer log.",
}


def main():
    build((UK, US))


if __name__ == "__main__":
    main()
