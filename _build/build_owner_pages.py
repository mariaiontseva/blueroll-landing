"""Build the owner pages (how to get a 5, re-rating) from _build/owner_pages/.

Site chrome (nav + footer) is lifted from a live article page at build time, the same way
build_borough_pages.py does it, so these pages never drift from the rest of the site.
Usage: python3 _build/build_owner_pages.py   (writes the pages into the repo root)
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "_build" / "owner_pages"
PAGES = ["how-to-get-a-5-food-hygiene-rating.html", "food-hygiene-re-rating.html"]

m = re.search(r"var ANON = '(eyJ[^']+)'", (ROOT / "free-haccp-template.html").read_text())
assert m, "anon key not found on the template page"
ANON = m.group(1)

_SRC = (ROOT / "food-hygiene-ratings-explained.html").read_text()
_NAV_END = _SRC.index('<div style="max-width: 1160px; margin: 22px auto 0;')
CHROME_NAV = _SRC[_SRC.index("<!-- ============ NAV ============ -->"):_NAV_END].rstrip()
CHROME_FOOTER = _SRC[_SRC.rindex("<!-- ============ FOOTER ============ -->"):_SRC.rindex("</body>")].rstrip()
assert "nav-burger" in CHROME_NAV and "mobile-menu" in CHROME_NAV, "nav extraction broke"
assert "footer-grid" in CHROME_FOOTER and "getElementById('nav-burger')" in CHROME_FOOTER, "footer extraction broke"

CSS = (SRC_DIR / "owner.css").read_text().rstrip()
UPDATED = date.today().strftime("%B %Y")

# Free HACCP pack capture: same pipeline as the template and borough pages
# (template_leads -> drip letters), source haccp-template:owner:<page>-inline.
PACK_JS = """
(function () {
  var SB = 'https://rszrggreuarvodcqeqrj.supabase.co', ANON = '__ANON__', PLACE = '__PLACE__';
  var g = document.querySelector('[data-gate="inline"]'); if (!g) return;
  var form = g.querySelector('.g-form'), sent = g.querySelector('.g-sent'), input = g.querySelector('.g-email'), send = g.querySelector('.g-send');
  function track(n, p) { if (window.gtag) gtag('event', n, p || {}); }
  function submit() {
    var email = (input.value || '').trim();
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) { input.style.boxShadow = 'inset 0 0 0 2px #d64545'; input.focus(); return; }
    form.hidden = true; sent.hidden = false;
    try { localStorage.setItem('br-tpl-downloaded', '1'); } catch (e) {}
    fetch(SB + '/rest/v1/template_leads', { method: 'POST',
      headers: { 'Content-Type': 'application/json', 'apikey': ANON, 'Authorization': 'Bearer ' + ANON, 'Prefer': 'return=minimal' },
      body: JSON.stringify({ email: email, source: 'haccp-template:owner:' + PLACE + '-inline', page: location.pathname, user_agent: navigator.userAgent.slice(0, 250) })
    }).catch(function () {});
    track('haccp_template_download', { placement: 'owner:' + PLACE, email_domain: email.split('@')[1] });
    var a = document.createElement('a'); a.href = '/blueroll-haccp-template.pdf'; a.download = 'blueroll-haccp-template.pdf';
    document.body.appendChild(a); a.click(); a.remove();
  }
  send.addEventListener('click', submit);
  input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); submit(); } });
  input.addEventListener('input', function () { input.style.boxShadow = ''; });
  document.querySelectorAll('[data-cta]').forEach(function (a) { a.addEventListener('click', function () { track('trial_start_click', { placement: a.getAttribute('data-cta') }); }); });
})();
"""


SITE = "https://blueroll.app"
META = {
    "how-to-get-a-5-food-hygiene-rating.html": {
        "title": "How to Get a 5 Food Hygiene Rating + Calculator | Blueroll",
        "desc": "A 5 needs all three inspection scores at 5 or better. Enter your inspector's scores to see your rating, what caps it and what to fix first.",
        "og_title": "How to get a 5 food hygiene rating",
        "og_desc": "Enter the inspector's three scores, see your rating, what caps it and what to fix first.",
        "crumb": "How to get a 5", "published": "2026-11-10",
        "howto": "How to prepare for a 5 food hygiene rating",
    },
    "food-hygiene-re-rating.html": {
        "title": "Food Hygiene Re-rating: Fees, Timing & Free Letter | Blueroll",
        "desc": "Got a 1, 2 or 3? Ask your council for a re-rating visit. Fees in England, Wales and NI, how long it takes, and a free request letter.",
        "og_title": "Got a 1, 2 or 3? How to get re-rated",
        "og_desc": "Re-rating fees by council and nation, timing, and a free request letter you can send today.",
        "crumb": "Re-rating", "published": "2026-11-10",
        "howto": "How to get a food hygiene re-rating",
    },
}


def _text(fragment: str) -> str:
    t = re.sub(r"<[^>]+>", "", fragment)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def head(name: str) -> str:
    m = META[name]
    url = f"{SITE}/{name}"
    assert len(m["title"]) <= 62, f"title too long: {len(m['title'])}"
    assert 110 <= len(m["desc"]) <= 158, f"description length {len(m['desc'])}"
    esc = lambda s: s.replace("&", "&amp;").replace('"', "&quot;")
    return f"""<title>{esc(m['title'])}</title>
<meta name="description" content="{esc(m['desc'])}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en-gb" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Blueroll">
<meta property="og:locale" content="en_GB">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(m['og_title'])}">
<meta property="og:description" content="{esc(m['og_desc'])}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="article:published_time" content="{m['published']}">
<meta property="article:modified_time" content="{date.today().isoformat()}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(m['og_title'])}">
<meta name="twitter:description" content="{esc(m['og_desc'])}">
<meta name="twitter:image" content="{SITE}/og-image.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>"""


def structured_data(name: str, html: str) -> str:
    """Article + breadcrumbs + FAQ + HowTo, all taken from what the page shows, so they never drift."""
    m = META[name]
    url = f"{SITE}/{name}"
    h1 = _text(re.search(r"<h1>(.*?)</h1>", html, re.S).group(1))
    faq = [{"@type": "Question", "name": _text(q), "acceptedAnswer": {"@type": "Answer", "text": _text(a)}}
           for q, a in re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", html, re.S)]
    steps_html = re.search(r'<ol class="steps">(.*?)</ol>', html, re.S).group(1)
    steps = [{"@type": "HowToStep", "position": i + 1, "name": _text(b), "text": _text(sp)}
             for i, (b, sp) in enumerate(re.findall(r"<b>(.*?)</b><span>(.*?)</span>", steps_html, re.S))]
    assert faq and steps, f"no FAQ or steps parsed in {name}"
    org = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Blueroll", "url": f"{SITE}/",
           "logo": {"@type": "ImageObject", "url": f"{SITE}/app_icon.png"}}
    graph = [
        org,
        {"@type": "Article", "headline": h1, "description": m["desc"], "image": f"{SITE}/og-image.png",
         "datePublished": m["published"], "dateModified": date.today().isoformat(), "inLanguage": "en-GB",
         "author": {"@id": f"{SITE}/#org"}, "publisher": {"@id": f"{SITE}/#org"},
         "mainEntityOfPage": {"@type": "WebPage", "@id": url}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Blueroll", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Food hygiene ratings", "item": f"{SITE}/food-hygiene-ratings/"},
            {"@type": "ListItem", "position": 3, "name": m["crumb"], "item": url}]},
        {"@type": "FAQPage", "mainEntity": faq},
        {"@type": "HowTo", "name": m["howto"], "step": steps},
    ]
    return ('<script type="application/ld+json">\n'
            + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
            + "\n</script>")


def build(name: str) -> None:
    html = (SRC_DIR / name).read_text()
    place = name.replace(".html", "")
    out = (html.replace("{{HEAD}}", head(name)).replace("{{LD}}", structured_data(name, html))
               .replace("{{CSS}}", CSS).replace("{{CHROME_NAV}}", CHROME_NAV).replace("{{CHROME_FOOTER}}", CHROME_FOOTER)
               .replace("{{UPDATED}}", UPDATED)
               .replace("{{PACK_JS}}", PACK_JS.replace("__ANON__", ANON).replace("__PLACE__", place)))
    assert "{{" not in out, f"unfilled placeholder in {name}"
    (ROOT / name).write_text(out)
    print("built", name, len(out))


if __name__ == "__main__":
    for p in PAGES:
        build(p)
