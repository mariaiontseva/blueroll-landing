"""Build the owner pages (how to get a 5, re-rating) from _build/owner_pages/.

Site chrome (nav + footer) is lifted from a live article page at build time, the same way
build_borough_pages.py does it, so these pages never drift from the rest of the site.
Usage: python3 _build/build_owner_pages.py   (writes the pages into the repo root)
"""
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


def build(name: str) -> None:
    html = (SRC_DIR / name).read_text()
    place = name.replace(".html", "")
    out = (html.replace("{{CSS}}", CSS).replace("{{CHROME_NAV}}", CHROME_NAV).replace("{{CHROME_FOOTER}}", CHROME_FOOTER)
               .replace("{{UPDATED}}", UPDATED)
               .replace("{{PACK_JS}}", PACK_JS.replace("__ANON__", ANON).replace("__PLACE__", place)))
    assert "{{" not in out, f"unfilled placeholder in {name}"
    (ROOT / name).write_text(out)
    print("built", name, len(out))


if __name__ == "__main__":
    for p in PAGES:
        build(p)
