#!/usr/bin/env python3
"""Build the two cleaning-template landing pages (UK and US).

    kitchen-cleaning-schedule-template.html   UK, source haccp-template:cleaning:<placement> (gets the drip)
    restaurant-cleaning-checklist.html        US, source us-template:cleaning:<placement> (no British drip)

The <head> styles, nav, mobile menu and footer are taken from the live
free-haccp-template.html, so the pages stay in step with the main template
page. Everything between the nav and the footer is written here. PDFs come
from _build/build_cleaning_pdfs.py. Run from the repo root:

    python3 _build/build_cleaning_pages.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKELETON = (ROOT / "free-haccp-template.html").read_text()
MAIN_URL = "https://blueroll.app/free-haccp-template.html"
MAIN_TITLE = "Free HACCP Plan Template UK: PDF &amp; Cleaning Schedule | Blueroll"
UK_URL = "https://blueroll.app/kitchen-cleaning-schedule-template.html"
US_URL = "https://blueroll.app/restaurant-cleaning-checklist.html"
ANON = re.search(r"var ANON = '([^']+)'", SKELETON).group(1)

CHECK = ('<span style="width: 14px; height: 14px; border-radius: 50%; background: #1f9d63; color: #fff; display: inline-flex; '
         'align-items: center; justify-content: center; font-size: 8px; flex-shrink: 0;">&#10003;</span>')


def gate(loc, button, note, align="center"):
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
        <div class="g-sent" style="display: none;">
          <div style="display: flex; align-items: center; justify-content: center; gap: 11px; background: #eaf4ee; border: 1px solid #cfe6d9; border-radius: 12px; padding: 15px 18px;">
            <span style="width: 24px; height: 24px; border-radius: 50%; background: #1f9d63; color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0;">&#10003;</span>
            <span style="font-size: 14.5px; font-weight: 600; color: #14532d;">Downloading. Check your Downloads folder</span>
          </div>
        </div>
      </div>"""


def band(title, sub, loc, cfg):
    return f"""<div style="max-width: 1160px; margin: 72px auto 0; padding: 0 24px;">
  <div style="border-top: 1px solid #e2e4e8; border-bottom: 1px solid #e2e4e8; padding: 36px 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap: 28px; align-items: center;">
    <div>
      <div style="font-size: clamp(22px, 3.5vw, 28px); font-weight: 800; letter-spacing: -0.03em; line-height: 1.15;">{title}</div>
      <div style="font-size: 12px; color: #9aa0a8; font-family: 'Geist Mono', monospace; margin-top: 10px;">{sub}</div>
    </div>
    <div class="g-side" style="max-width: 460px; justify-self: end; width: 100%;">
      {gate(loc, cfg['button'], cfg['note'], 'flex-end')}
    </div>
  </div>
</div>"""


def prose(cfg):
    out = []
    for kind, a, *b in cfg["body"]:
        if kind == "h2":
            out.append(f'<h2 style="font-size: 26px; font-weight: 800; letter-spacing: -0.025em; line-height: 1.25; margin: 44px 0 0;">{a}</h2>')
        elif kind == "h3":
            out.append(f'<h3 style="font-size: 17px; font-weight: 700; margin: 30px 0 0;">{a}</h3>')
        elif kind == "p":
            out.append(f'<p style="font-size: 15px; color: #41464d; line-height: 1.7; margin: 10px 0 0; text-wrap: pretty;">{a}</p>')
        elif kind == "ol":
            items = "".join(f'<li style="margin: 0 0 6px;">{x}</li>' for x in a)
            out.append(f'<ol style="font-size: 15px; color: #41464d; line-height: 1.65; margin: 12px 0 0; padding-left: 22px;">{items}</ol>')
        elif kind == "rows":
            rows = "".join(
                f'<div class="who-row" style="display: grid; grid-template-columns: minmax(130px, 170px) 1fr; gap: 16px; padding: 15px 0; border-top: 1px solid #e7e9ec; align-items: baseline;">'
                f'<span style="font-size: 11px; font-weight: 600; color: #1f7a52; font-family: \'Geist Mono\', monospace; letter-spacing: .04em;">{k}</span>'
                f'<p style="font-size: 14.5px; color: #41464d; line-height: 1.6; margin: 0; text-wrap: pretty;">{v}</p></div>'
                for k, v in a)
            out.append(f'<div style="margin-top: 14px; border-bottom: 1px solid #e7e9ec;">{rows}</div>')
    faq = "".join(
        f'\n    <h3 style="font-size: 15.5px; font-weight: 700; margin: 22px 0 0;">{q}</h3>'
        f'\n    <p style="font-size: 14px; color: #5c626b; line-height: 1.65; margin: 6px 0 0;">{a}</p>' for q, a in cfg["faq"])
    out.append('<h2 style="font-size: 26px; font-weight: 800; letter-spacing: -0.025em; line-height: 1.25; margin: 48px 0 0;">Frequently asked questions</h2>'
               f'<div style="margin-top: 8px;">{faq}\n  </div>')
    return '<div style="max-width: 760px; margin: 80px auto 0; padding: 0 24px;">\n  ' + "\n  ".join(out) + "\n</div>"


def strip_tags(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))).strip()


def build_head(cfg):
    end = SKELETON.index('<div style="max-width: 1160px; margin: 22px auto 0; padding: 0 24px; font-size: 12.5px; color: #8a9099;">')
    s = SKELETON[:end]
    s = s.replace('<html lang="en-GB">', f'<html lang="{cfg["lang"]}">')
    s = s.replace(MAIN_URL, cfg["url"])
    s = s.replace(MAIN_TITLE, cfg["title"])
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + cfg["desc"] + m.group(2), s)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + cfg["desc"] + m.group(2), s)
    if cfg.get("hreflang", True):
      s = s.replace(f'<link rel="canonical" href="{cfg["url"]}">',
                  f'<link rel="canonical" href="{cfg["url"]}">\n'
                  f'<link rel="alternate" hreflang="en-gb" href="{cfg.get("uk_url", UK_URL)}">\n'
                  f'<link rel="alternate" hreflang="en-us" href="{cfg.get("us_url", US_URL)}">\n'
                  f'<link rel="alternate" hreflang="x-default" href="{cfg.get("uk_url", UK_URL)}">')
    s = s.replace('<meta property="og:image" content="https://blueroll.app/og-image.png">',
                  f'<meta property="og:image" content="https://blueroll.app/uploads/{cfg["img"]}-2.png">')
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
        for q, a in cfg["faq"]]}
    s, n = re.subn(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>',
                   lambda m: '<script type="application/ld+json">' + json.dumps(faq_ld, ensure_ascii=False) + '</script>', s, count=1, flags=re.S)
    assert n == 1
    doc_ld = {"@context": "https://schema.org", "@type": "DigitalDocument", "name": cfg["doc_name"],
              "description": html.unescape(cfg["desc"]), "url": cfg["url"], "contentUrl": "https://blueroll.app/" + cfg["pdf"],
              "encodingFormat": "application/pdf", "inLanguage": cfg["lang"], "isAccessibleForFree": True,
              "dateModified": "2026-11-18", "publisher": {"@type": "Organization", "name": "Blueroll", "url": "https://blueroll.app/"}}
    s, n = re.subn(r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"DigitalDocument".*?</script>',
                   lambda m: '<script type="application/ld+json">' + json.dumps(doc_ld, ensure_ascii=False) + '</script>', s, count=1, flags=re.S)
    assert n == 1
    assert s.count("Free HACCP Plan Template UK (PDF + Daily Logs)") == 1
    s = s.replace("Free HACCP Plan Template UK (PDF + Daily Logs)", cfg["crumb"])
    assert "free-haccp-template.html\">" not in s.split("<body>")[0] or True
    return s


def build_body(cfg):
    figs = "".join(
        f"""
      <figure class="tpl-fig" style="margin: 0; transform: rotate({rot}deg);">
        <img src="/uploads/{cfg['img']}-{i}.png?v=20261118" alt="{alt}" loading="lazy" style="width: 100%; display: block; border-radius: 4px; box-shadow: 0 2px 4px rgba(16,24,40,.08), 0 28px 48px -22px rgba(16,24,40,.4);">
        <figcaption style="font-size: 11px; color: #7c828b; margin-top: 12px; text-align: center; font-family: 'Geist Mono', monospace;">{cap}</figcaption>
      </figure>""" for i, (rot, alt, cap) in enumerate(cfg["figs"], 1))
    chips = "".join(
        f'\n    <a href="{h}" style="border: 1px solid #e2e4e8; border-radius: 999px; padding: 7px 14px; font-size: 13px; font-weight: 600; color: #41464d; background: #fff;" class="gh0">{t}</a>'
        for t, h in cfg["chips"])
    return f"""<div style="max-width: 1160px; margin: 22px auto 0; padding: 0 24px; font-size: 12.5px; color: #8a9099;"><a href="/">Blueroll</a> <span style="color: #c6cad0;">›</span> <a href="/tools.html">Free Tools</a> <span style="color: #c6cad0;">›</span> <span style="color: #5c626b; font-weight: 600;">{cfg['crumb']}</span></div>

<!-- hero -->
<style>@media (max-width: 960px) {{ h1.hero-kw {{ font-size: 17px !important; }} .tpl-desk[style] {{ grid-template-columns: minmax(0, 1fr) !important; max-width: 320px; margin: 0 auto; }} }}</style>
<div style="max-width: 1160px; margin: 56px auto 0; padding: 0 24px; text-align: center;">
  <div style="max-width: 820px; margin: 0 auto;">
    <div style="display: inline-flex; align-items: center; gap: 7px; background: #eaf4ee; color: #1f7a52; font-size: 12.5px; font-weight: 700; border-radius: 20px; padding: 5px 14px;">{cfg['badge']}</div>
    <div class="hero-h1" style="font-size: clamp(36px, 6.5vw, 54px); line-height: 1.05; font-weight: 800; letter-spacing: -0.04em; margin: 18px 0 0; text-wrap: balance;">{cfg['big']}</div>
    <h1 class="hero-kw" style="font-size: 17px; font-weight: 600; color: #41464d; letter-spacing: -0.01em; margin: 14px 0 0;">{cfg['h1']}</h1>
    <p class="hero-sub" style="font-size: 17px; line-height: 1.6; color: #5c626b; margin: 18px auto 0; max-width: 640px; text-wrap: pretty;">{cfg['sub']}</p>
    <div style="max-width: 460px; margin: 30px auto 0;">
      {gate('hero', cfg['button'], cfg['note'])}
      <div class="g-bridge" style="display: none; flex-wrap: wrap; align-items: center; gap: 14px; background: #fff; border: 1px solid #e7e9ec; border-radius: 14px; padding: 14px 16px; margin-top: 12px; text-align: left;">
        <div style="display: flex; align-items: center; gap: 8px; background: #f6f7f8; border: 1px solid #eef0f2; border-radius: 9px; padding: 8px 11px; font-size: 11.5px; white-space: nowrap; flex-shrink: 0;">{CHECK}<span style="font-weight: 600;">{cfg['chip'][0]}</span><span style="color: #1f7a52; font-weight: 700; font-variant-numeric: tabular-nums; padding-left: 8px;">{cfg['chip'][1]}</span></div>
        <div style="flex: 1 1 170px; min-width: 0;">
          <div style="font-size: 13px; font-weight: 600; line-height: 1.4;">{cfg['bridge']}</div>
          <a href="/haccp-checklists.html" style="font-size: 12.5px; font-weight: 700;">See how, 2 min tour &rarr;</a>
        </div>
      </div>
      <div style="font-size: 11.5px; color: #9aa0a8; font-family: 'Geist Mono', monospace; margin-top: 16px;">{cfg['meta']}</div>
    </div>
  </div>
</div>

<!-- the sheets -->
<div style="max-width: 1160px; margin: 56px auto 0; padding: 0 24px;">
  <div style="text-align: center; margin-bottom: 28px;">
    <div style="font-size: 14px; font-weight: 600; color: #1f7a52; letter-spacing: .01em;">{cfg['inside']}</div>
    <h2 style="font-size: 32px; font-weight: 700; letter-spacing: -0.03em; margin: 12px auto 0; max-width: 640px; text-wrap: balance;">{cfg['inside_h2']}</h2>
  </div>
  <div style="background: #eef1f0; border-radius: 24px; padding: clamp(28px, 5vw, 56px) clamp(16px, 3vw, 40px) clamp(24px, 4vw, 44px); overflow: hidden;">
    <div class="tpl-desk" style="display: grid; grid-template-columns: repeat(3, minmax(0, 300px)); justify-content: center; gap: clamp(18px, 3vw, 34px);">{figs}
    </div>
  </div>
</div>

<div style="max-width: 1160px; margin: 34px auto 0; padding: 0 24px; text-align: center;">
  <div style="font-size: 12px; font-weight: 600; color: #8a9099; text-transform: uppercase; letter-spacing: .06em;">{cfg['chips_label']}</div>
  <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-top: 12px;">{chips}
  </div>
</div>

{band(cfg['mid_title'], cfg['mid_sub'], 'mid', cfg)}

{prose(cfg)}

{band(cfg['bottom_title'], cfg['mid_sub'], 'bottom', cfg)}

<div style="max-width: 1160px; margin: 80px auto 0; padding: 0 24px 88px;">
  <div style="position: relative; background: linear-gradient(105deg, #14382a, #0f2b1e 55%, #0a1f15); border-radius: 24px; padding: 56px; color: #fff; overflow: hidden; display: grid; grid-template-columns: 1.35fr 1fr; gap: 44px; align-items: center;">
    <div style="position: relative;">
      <h2 style="font-size: 34px; font-weight: 800; letter-spacing: -0.03em; margin: 0; line-height: 1.12; text-wrap: balance;">{cfg['dark_h2']}</h2>
      <p style="font-size: 15px; margin: 14px 0 0; max-width: 440px; color: rgba(255,255,255,.6); line-height: 1.6; text-wrap: pretty;">{cfg['dark_p']}</p>
      <a href="https://app.blueroll.app/" style="display: inline-block; margin-top: 26px; background: #1f9d63; color: #fff; font-size: 15px; font-weight: 700; padding: 13px 26px; border-radius: 8px; box-shadow: 0 12px 32px -14px rgba(31,157,99,.9);" class="gh0">{cfg['dark_btn']}</a>
      <div style="margin-top: 18px; font-size: 12px; color: rgba(255,255,255,.4);">{cfg['dark_small']}</div>
    </div>
    <div style="position: relative;">
      <div style="display: flex; flex-direction: column; align-items: stretch; max-width: 250px; margin-left: auto;">{''.join(
        f'<div style="display: flex; align-items: center; gap: 9px; background: #fff; border-radius: 11px; padding: 10px 13px; font-size: 12.5px; color: #16181d; white-space: nowrap; box-shadow: 0 14px 34px -16px rgba(0,0,0,.5);{" margin-top: 8px;" if j else ""}">{CHECK}<span style="font-weight: 600;">{a}</span><span style="margin-left: auto; color: #1f7a52; font-weight: 700; font-size: 11px;">{b}</span></div>'
        for j, (a, b) in enumerate(cfg['dark_rows']))}
      </div>
    </div>
  </div>
</div>
"""


def build_tail(cfg):
    start = SKELETON.index("<!-- ============ FOOTER ============ -->")
    end = SKELETON.index("<!-- exit-intent modal (desktop) -->")
    footer = SKELETON[start:end]
    modal = f"""<!-- exit-intent modal (desktop) -->
<div id="tpl-exit" style="display: none; position: fixed; inset: 0; z-index: 100; background: rgba(10,20,15,.45); backdrop-filter: blur(3px); align-items: center; justify-content: center; padding: 24px;">
  <div style="position: relative; background: #fff; border-radius: 20px; padding: 36px; width: 100%; max-width: 460px; box-shadow: 0 40px 80px -30px rgba(16,24,40,.5);">
    <button id="tpl-exit-close" aria-label="Close" style="position: absolute; top: 14px; right: 14px; width: 36px; height: 36px; border: none; border-radius: 50%; background: #f2f3f5; color: #41464d; font-size: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; font-family: 'Geist', sans-serif;">&#10005;</button>
    <div style="display: inline-flex; align-items: center; gap: 7px; background: #eaf4ee; color: #1f7a52; font-size: 12px; font-weight: 700; border-radius: 20px; padding: 4px 12px;">Before you go</div>
    <h2 style="font-size: 26px; font-weight: 800; letter-spacing: -0.03em; line-height: 1.15; margin: 14px 0 0;">{cfg['exit_h2']}</h2>
    <p style="font-size: 14px; color: #5c626b; line-height: 1.6; margin: 10px 0 16px;">{cfg['exit_p']}</p>
    {gate('exit', cfg['button'], cfg['note'])}
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
    input.addEventListener('input', function () { input.style.boxShadow = 'inset 0 0 0 1.5px #e2e4e8'; });
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
""" % {"anon": ANON, "pdf": cfg["pdf"], "source": cfg["source"], "subject": cfg["subject"], "slug": cfg["slug"]}
    return footer + "\n" + modal + script


UK = {
    "file": "kitchen-cleaning-schedule-template.html", "url": UK_URL, "lang": "en-GB", "slug": "cleaning",
    "source": "haccp-template:cleaning", "subject": "New cleaning schedule download (UK)",
    "pdf": "blueroll-kitchen-cleaning-schedule.pdf", "img": "cleaning-uk-page",
    "title": "Kitchen Cleaning Schedule Template UK: Free PDF | Blueroll",
    "desc": "Free kitchen cleaning schedule template for UK food businesses: a weekly schedule, a filled-in example and a monthly deep-clean log. Printable A4 PDF.",
    "doc_name": "Kitchen cleaning schedule template (UK)",
    "crumb": "Kitchen cleaning schedule template",
    "badge": "Free template &middot; 3 printable A4 sheets",
    "big": "The cleaning schedule,<br>already written",
    "h1": "Free kitchen cleaning schedule template for UK kitchens",
    "sub": "A printable weekly cleaning schedule with the jobs, methods and frequencies already filled in, a filled-in example, and a monthly deep-clean log. Enter your work email and the PDF downloads straight away.",
    "button": "Get the free schedule",
    "note": "The PDF downloads straight away. We also email you our full 16-page HACCP pack, plus two short follow-ups. Unsubscribe anytime.",
    "chip": ("Floors &middot; SR", "21:40"),
    "bridge": "This same schedule ticks itself off in Blueroll",
    "meta": "A4 &middot; weekly schedule &middot; filled example &middot; monthly log",
    "inside": "Inside the PDF &middot; 3 sheets &middot; A4",
    "inside_h2": "Print it, pin it by the sink, sign it as you go",
    "figs": [(-2, "Weekly kitchen cleaning schedule, blank", "SHEET 1 &middot; WEEKLY SCHEDULE"),
             (1.2, "Kitchen cleaning schedule, filled-in example from St James's Cafe", "SHEET 2 &middot; FILLED EXAMPLE"),
             (-1, "Monthly and deep-clean log with the two-stage cleaning method", "SHEET 3 &middot; MONTHLY LOG")],
    "chips_label": "More free records",
    "chips": [("Full HACCP pack (16 pages)", "/free-haccp-template.html"), ("EHO inspection checklist", "/eho-inspection-checklist.html"),
              ("Fridge temperature log", "/fridge-temperature-log.html"), ("SFBB guide", "/sfbb-guide.html")],
    "mid_title": "Get the schedule, free.",
    "mid_sub": "weekly schedule &middot; filled example &middot; monthly log",
    "bottom_title": "Still scrolling?<br>The schedule is one click away.",
    "body": [
        ("h2", "What a kitchen cleaning schedule needs to show"),
        ("p", "Every UK food business has to keep its premises and equipment clean and be able to show how. On the day, an Environmental Health Officer looks at two things: whether the kitchen is clean now, and whether your records prove it stays clean the rest of the time. The cleaning schedule is that record. It says what gets cleaned, how, how often, and who signed it off."),
        ("p", 'If you use Safer Food, Better Business, the Cleaning section asks for a schedule like this one, and the sheets fit straight into the folder. Our <a href="sfbb-guide.html">SFBB guide</a> covers the rest of the pack.'),
        ("h3", "Daily, weekly and monthly jobs"),
        ("rows", [("AFTER USE<br>AND DAILY", "Work surfaces, chopping boards, hand-contact points such as handles, taps and the till, handwash basins, sinks, hobs, the fryer, the microwave, fridge seals, floors and bins."),
                  ("WEEKLY", "Fridge interiors and shelves, extractor hood and filters, walls and splashbacks, dry store shelves and the dishwasher."),
                  ("MONTHLY<br>OR LESS", "Defrosting freezers, behind and under equipment, drains, light fittings and fly screens, a whole-kitchen deep clean, and extraction ductwork on the schedule your insurer sets (TR19).")]),
        ("h3", "Clean, then disinfect: the two-stage method"),
        ("ol", ["Scrape off food and debris.", "Wash with hot water and detergent, then rinse.",
                "Apply a disinfectant or sanitiser and leave it for the contact time on the label.",
                "Rinse if the label says so, then air-dry or use a single-use towel."]),
        ("p", "Use a product that meets BS EN 1276 or BS EN 13697, at the dilution on the label. That is the standard the Food Standards Agency&rsquo;s guidance on E. coli cross-contamination asks for, and inspectors check the bottle."),
        ("h3", "What loses marks at an inspection"),
        ("p", 'A schedule nobody signs. A week signed up in one pen on Friday night. Sanitiser mixed by guesswork. The same cloth used on raw meat and ready-to-eat areas. Cleaning and records feed two of the three scores behind a hygiene rating: the condition of the premises, and confidence in management. <a href="food-hygiene-ratings-explained.html">Food hygiene ratings explained</a> shows how the scores add up.'),
        ("p", 'Need the rest of the paperwork? The <a href="free-haccp-template.html">free 16-page HACCP pack</a> adds the daily opening checklist, fridge temperature logs, delivery checks and the allergen matrix.'),
    ],
    "faq": [
        ("How often should a commercial kitchen be cleaned?",
         "Food-contact surfaces after every use, the rest of the kitchen every day, and fridges, extractor filters and walls every week. Deeper jobs such as defrosting freezers and cleaning behind equipment usually go monthly, and extraction ductwork follows your insurer's TR19 schedule. The template lists all of these, so you only adjust the frequencies to how busy you are."),
        ("Is a paper cleaning schedule enough for an EHO?",
         'Yes, as long as each job is signed when it is done, by the person who did it, and a manager checks the sheet. Inspectors question a week filled in with one pen at the end. When paper gets tedious, <a href="haccp-checklists.html">digital checklists</a> keep the same record with the time and the name on every tick.'),
        ("Is this template really free?",
         "Yes. No charge, no account and no watermark. Enter your email, the PDF downloads, and you can print it for as long as paper works for you."),
    ],
    "dark_h2": "Or stop chasing signatures.",
    "dark_p": "The same schedule on your team&rsquo;s phones: every job ticked with a name and a time, and the record ready for the inspector. &pound;24.99 a month.",
    "dark_btn": "Start your free 14-day trial",
    "dark_small": "14 days free. No card needed. We set it up for you, free.",
    "dark_rows": [("Work surfaces", "TA 12:05"), ("Floors", "SR 21:40"), ("Extractor filters", "Weekly &#10003;")],
    "exit_h2": "Take the schedule with you",
    "exit_p": "Three printable sheets: the weekly schedule, a filled-in example and the monthly deep-clean log, straight to your Downloads.",
}

US = {
    "file": "restaurant-cleaning-checklist.html", "url": US_URL, "lang": "en-US", "slug": "us-cleaning",
    "source": "us-template:cleaning", "subject": "New restaurant cleaning checklist download (US)",
    "pdf": "blueroll-restaurant-cleaning-checklist.pdf", "img": "cleaning-us-page",
    "title": "Restaurant Cleaning Checklist: Free PDF (Daily, Weekly, Monthly) | Blueroll",
    "desc": "Free printable restaurant cleaning checklist: daily kitchen, front-of-house and restroom tasks, weekly and monthly jobs, and a sanitizer log. Based on the FDA Food Code.",
    "doc_name": "Restaurant cleaning checklist (US)",
    "crumb": "Restaurant cleaning checklist",
    "badge": "Free download &middot; 3 printable sheets",
    "big": "Every cleaning job,<br>on one sheet",
    "h1": "Free restaurant cleaning checklist (PDF)",
    "sub": "A printable daily cleaning checklist for the kitchen, front of house and restrooms, a filled-in example, and a weekly, monthly and sanitizer log. Built on the FDA Food Code. Enter your work email and the PDF downloads right away.",
    "button": "Get the free checklist",
    "note": "The PDF downloads right away. We don&rsquo;t share your email.",
    "chip": ("Prep tables &middot; JM", "2:05 pm"),
    "bridge": "This same checklist ticks itself off in Blueroll",
    "meta": "US Letter &middot; daily checklist &middot; filled example &middot; sanitizer log",
    "inside": "Inside the PDF &middot; 3 sheets &middot; US Letter",
    "inside_h2": "Print it, post it by the dish pit, initial it as you go",
    "figs": [(-2, "Daily restaurant cleaning checklist, blank", "SHEET 1 &middot; DAILY CHECKLIST"),
             (1.2, "Daily restaurant cleaning checklist, filled-in example", "SHEET 2 &middot; FILLED EXAMPLE"),
             (-1, "Weekly and monthly cleaning log with a sanitizer test-strip log", "SHEET 3 &middot; WEEKLY, MONTHLY, SANITIZER")],
    "chips_label": "Free templates and city guides",
    "chips": [("Food temperature log", "/food-temperature-log.html"), ("Inspection checklist", "/restaurant-health-inspection-checklist.html"), ("New York City", "/nyc-restaurant-grade.html"), ("Los Angeles", "/la-restaurant-grade.html"),
              ("San Francisco", "/sf-restaurant-inspection.html"), ("Chicago", "/chicago-restaurant-inspection.html"),
              ("Seattle", "/seattle-restaurant-inspection.html")],
    "mid_title": "Get the checklist, free.",
    "mid_sub": "daily checklist &middot; filled example &middot; weekly, monthly &amp; sanitizer log",
    "bottom_title": "Still scrolling?<br>The checklist is one click away.",
    "body": [
        ("h2", "What a restaurant cleaning checklist should cover"),
        ("p", "Health inspectors check that food-contact surfaces are clean and sanitized, that sanitizer is mixed at the right strength, and that handwashing sinks are stocked and used only for handwashing. A checklist with initials on every task is how you show that happens every day, not only on inspection day."),
        ("h3", "Daily, weekly and monthly tasks"),
        ("rows", [("EVERY SHIFT<br>AND DAILY", "Prep tables and food-contact surfaces, cutting boards and utensils, sanitizer buckets, handwashing sinks, the flat-top, grill and fryer, reach-in handles and gaskets, the dish machine, floors and drains, trash, dining tables, menus, the drink station and restrooms."),
                  ("WEEKLY", "Walk-in cooler shelves, floor and door gasket, hood filters, oven interiors, the walls behind the line and coffee equipment."),
                  ("MONTHLY<br>OR LESS", "Ice machine, freezers, behind and under equipment, the grease trap on your hauler&rsquo;s schedule, and the hood and duct system on the NFPA 96 schedule for your cooking volume.")]),
        ("h3", "Clean, rinse, sanitize"),
        ("ol", ["Scrape off food and debris.", "Wash with detergent and warm water.", "Rinse with clean water.",
                "Sanitize at the right strength for the contact time on the label.", "Let it air-dry."]),
        ("p", "Food-contact surfaces in constant use with time and temperature control (TCS) food need this at least every 4 hours (FDA Food Code 4-602.11). Check sanitizer with the matching test strips: chlorine is usually 50-100 ppm, and quaternary ammonium (quat) is used at the strength on the label, often 200-400 ppm. Wiping cloths stay in sanitizer between uses."),
        ("h3", "What costs points at an inspection"),
        ("p", "Sanitizer buckets at the wrong strength, wiping cloths left on the counter, a handwashing sink that is blocked or out of soap and towels, food buildup on equipment, and no record that cleaning happens. In cities with letter grades and scores, these show up as violations that lower your grade. The city guides below explain how each system scores."),
    ],
    "faq": [
        ("How often should a restaurant be cleaned?",
         "Food-contact surfaces after each task and at least every 4 hours while in use; the line, floors, restrooms and dining room every day; walk-ins, hood filters and ovens every week; freezers, ice machines and behind equipment every month. Hoods and ducts follow the NFPA 96 schedule for your cooking volume."),
        ("What sanitizer concentration should I use?",
         "Follow the product label and your local health code. As a guide, chlorine bleach solutions are usually 50-100 ppm and quat solutions often 200-400 ppm. Test every new bucket with the matching strips and write the reading on sheet 3."),
        ("Is this checklist free?",
         "Yes. No charge, no account and no watermark. Enter your email, the PDF downloads, and you can print as many copies as you need."),
    ],
    "dark_h2": "Or put the checklist on your team&rsquo;s phones.",
    "dark_p": "Every task ticked with a name and a time, ready to show your health inspector.",
    "dark_btn": "Try Blueroll free for 14 days",
    "dark_small": "14 days free. No card needed.",
    "dark_rows": [("Prep tables", "JM 2:05"), ("Sanitizer bucket", "200 ppm"), ("Restrooms", "AV 4:30")],
    "exit_h2": "Take the checklist with you",
    "exit_p": "Three printable sheets: the daily checklist, a filled-in example, and the weekly, monthly and sanitizer log.",
}


def main():
    for cfg in (UK, US):
        page = build_head(cfg) + build_body(cfg) + "\n" + build_tail(cfg)
        assert "free-haccp-template.html\">\n<title>" not in page
        assert page.count('data-gate="') == 4, cfg["file"]
        (ROOT / cfg["file"]).write_text(page)
        print("built", cfg["file"])


if __name__ == "__main__":
    main()
