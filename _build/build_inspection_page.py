#!/usr/bin/env python3
"""Build the US restaurant health inspection checklist page and the inline forms on the five US city pages.

    restaurant-health-inspection-checklist.html   source us-template:inspection:<placement> (no British drip)
    nyc / la / sf / chicago / seattle pages        source us-template:inspection:<city>-inline

The page reuses the cleaning-page skeleton (_build/build_cleaning_pages.py); the PDF comes
from _build/build_inspection_pdf.py. The city forms are inserted once, at the top of
<div class="content">, and skipped if already there. Run from the repo root:

    python3 _build/build_inspection_page.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_cleaning_pages as P  # noqa: E402

URL = "https://blueroll.app/restaurant-health-inspection-checklist.html"
PDF = "blueroll-restaurant-health-inspection-checklist.pdf"

CITY_LINKS = [("New York City", "/nyc-restaurant-grade.html"), ("Los Angeles", "/la-restaurant-grade.html"),
              ("San Francisco", "/sf-restaurant-inspection.html"), ("Chicago", "/chicago-restaurant-inspection.html"),
              ("Seattle", "/seattle-restaurant-inspection.html")]

PAGE = {
    "file": "restaurant-health-inspection-checklist.html", "url": URL, "lang": "en-US", "hreflang": False,
    "slug": "us-inspection", "source": "us-template:inspection", "subject": "New inspection checklist download (US)",
    "pdf": PDF, "img": "inspection-us-page",
    "title": "Restaurant Health Inspection Checklist: Free PDF Self-Inspection | Blueroll",
    "desc": "Free restaurant health inspection checklist: a 24-point self-inspection built on the FDA Food Code, a filled-in example and a corrective action log. Printable PDF.",
    "doc_name": "Restaurant health inspection checklist (US)",
    "crumb": "Restaurant health inspection checklist",
    "badge": "Free download &middot; 3 printable sheets",
    "big": "Inspect yourself<br>before they do",
    "h1": "Free restaurant health inspection checklist (PDF)",
    "sub": "A 24-point self-inspection built on the FDA Food Code: temperatures, handwashing, storage, sanitizing, pests and paperwork. With a filled-in example and a corrective action log. Enter your work email and the PDF downloads right away.",
    "button": "Get the free checklist",
    "note": "The PDF downloads right away. We don&rsquo;t share your email.",
    "chip": ("Self-inspection &middot; DL", "21/24"),
    "bridge": "This same checklist ticks itself off in Blueroll",
    "meta": "US Letter &middot; 24-point checklist &middot; filled example &middot; corrective action log",
    "inside": "Inside the PDF &middot; 3 sheets &middot; US Letter",
    "inside_h2": "Walk the kitchen once a week, the way an inspector does",
    "figs": [(-2, "24-point restaurant self-inspection checklist, blank", "SHEET 1 &middot; SELF-INSPECTION"),
             (1.2, "Self-inspection checklist, filled-in example with three fixes", "SHEET 2 &middot; FILLED EXAMPLE"),
             (-1, "Corrective action log with how five US cities score", "SHEET 3 &middot; CORRECTIVE ACTIONS")],
    "chips_label": "More free templates and city guides",
    "chips": [("Restaurant cleaning checklist", "/restaurant-cleaning-checklist.html"),
              ("Food temperature log", "/food-temperature-log.html")] + CITY_LINKS,
    "mid_title": "Get the checklist, free.",
    "mid_sub": "24-point checklist &middot; filled example &middot; corrective action log",
    "bottom_title": "Still scrolling?<br>The checklist is one click away.",
    "body": [
        ("h2", "What a health inspector checks first"),
        ("p", "Inspectors start with the FDA&rsquo;s five risk factors for foodborne illness: food from unsafe sources, inadequate cooking, improper holding temperatures, contaminated equipment and poor personal hygiene. Violations in these areas usually cost the most points. Walk your kitchen with the same list once a week and fix what you find before the inspector does."),
        ("h3", "How to run a self-inspection"),
        ("ol", ["Pick a busy time, not a quiet afternoon. Problems show up during service.",
                "Walk the kitchen in the inspector&rsquo;s order: handwashing sink, coolers, hot line, prep, dish area, storage, restrooms.",
                "Probe three items in every cooler and on the hot line, and write the numbers down.",
                "Mark each line yes or no. For every no, write the fix, who owns it and by when.",
                "Do it weekly and keep the sheets with your corrective action log."]),
        ("h3", "How your city scores"),
        ("rows", [("NEW YORK CITY", 'Letter grade from violation points: A is 0-13, B is 14-27, C is 28 or more. <a href="nyc-restaurant-grade.html">How to get an A in NYC</a>.'),
                  ("LOS ANGELES", 'Letter grade from a score out of 100: A is 90-100, B is 80-89, C is 70-79. <a href="la-restaurant-grade.html">How to get an A in LA</a>.'),
                  ("SAN FRANCISCO", 'A score out of 100. <a href="sf-restaurant-inspection.html">How to score 90 or above</a>.'),
                  ("CHICAGO", 'Pass, Pass with Conditions, or Fail. <a href="chicago-restaurant-inspection.html">How to pass in Chicago</a>.'),
                  ("SEATTLE", 'A placard: Excellent, Good, Okay or Needs to Improve. <a href="seattle-restaurant-inspection.html">How to pass in Seattle</a>.')]),
        ("p", 'Your state or county may have adopted a different edition of the Food Code, and its rules come first. The <a href="food-temperature-log.html">food temperature log</a> and the <a href="restaurant-cleaning-checklist.html">cleaning checklist</a> are the daily records behind most of these checks.'),
    ],
    "faq": [
        ("What do health inspectors look for in a restaurant?",
         "Food temperatures, handwashing and bare-hand contact with ready-to-eat food, how food is stored and labeled, whether sanitizer is at the right strength, signs of pests, and paperwork such as your permit and a Certified Food Protection Manager. The checklist covers each of these."),
        ("How often should I do a self-inspection?",
         "Weekly works for most restaurants, plus one more when an inspection is due. Keep the completed sheets with your corrective action log."),
        ("Is this checklist free?",
         "Yes. No charge, no account and no watermark. Enter your email, the PDF downloads, and you can print as many copies as you need."),
    ],
    "dark_h2": "Or put the checks on your team&rsquo;s phones.",
    "dark_p": "Every check ticked with a name and a time, ready to show your health inspector.",
    "dark_btn": "Try Blueroll free for 14 days",
    "dark_small": "14 days free. No card needed.",
    "dark_rows": [("Self-inspection", "21/24"), ("Walk-in cooler", "37&deg;F"), ("Sanitizer bucket", "200 ppm")],
    "exit_h2": "Take the checklist with you",
    "exit_p": "Three printable sheets: the 24-point self-inspection, a filled-in example and the corrective action log.",
}

CITIES = {
    "nyc-restaurant-grade.html": ("nyc", "New York City", "the NYC Health Department"),
    "la-restaurant-grade.html": ("la", "Los Angeles", "the LA County inspector"),
    "sf-restaurant-inspection.html": ("sf", "San Francisco", "the SF health inspector"),
    "chicago-restaurant-inspection.html": ("chicago", "Chicago", "the CDPH inspector"),
    "seattle-restaurant-inspection.html": ("seattle", "Seattle", "the King County inspector"),
}


def city_gate(slug, city, who):
    return f"""
<!-- Free inspection checklist capture (source: us-template:inspection:{slug}-inline, no British drip) -->
<div data-gate="inline" style="max-width:820px;margin:0 auto 44px;padding:26px 28px;background:#f0f7f3;border:1px solid #cfe3d6;border-radius:14px;">
  <div style="font-size:11.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#047857;">Free download</div>
  <h3 style="font-size:20px;font-weight:800;letter-spacing:-.02em;margin:8px 0 6px;color:#1a1d21;">Inspect your kitchen before {who} does</h3>
  <p style="font-size:14.5px;color:#5c626b;line-height:1.65;margin:0 0 16px;">A free 24-point self-inspection checklist built on the FDA Food Code, with a filled-in example and a corrective action log. Print it and walk your {city} kitchen once a week.</p>
  <div class="g-idle">
    <button class="g-open" style="background:#047857;color:#fff;font-family:inherit;font-size:15px;font-weight:700;padding:13px 26px;border:none;border-radius:8px;cursor:pointer;">Get the free checklist</button>
  </div>
  <div class="g-form" style="display:none;">
    <div style="display:flex;flex-wrap:wrap;gap:8px;background:#fff;border:1px solid #dbe3dd;border-radius:12px;padding:8px;max-width:520px;">
      <input class="g-email" type="email" placeholder="Your work email" autocomplete="email" style="flex:1 1 180px;min-width:0;font-family:inherit;font-size:16px;padding:10px 12px;border:none;border-radius:8px;background:transparent;color:#1a1d21;outline:none;box-shadow:inset 0 0 0 1.5px #e2e4e8;">
      <button class="g-send" style="flex:1 1 auto;background:#047857;color:#fff;font-family:inherit;font-size:14.5px;font-weight:700;padding:12px 20px;border:none;border-radius:8px;cursor:pointer;white-space:nowrap;">Send me the PDF</button>
    </div>
    <div style="font-size:12px;color:#8a9099;line-height:1.5;margin-top:10px;">The PDF downloads right away. We don&rsquo;t share your email.</div>
  </div>
  <div class="g-sent" style="display:none;">
    <div style="display:flex;align-items:center;gap:11px;background:#eaf4ee;border:1px solid #cfe6d9;border-radius:12px;padding:15px 18px;max-width:520px;">
      <span style="width:24px;height:24px;border-radius:50%;background:#047857;color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0;">&#10003;</span>
      <span style="font-size:14.5px;font-weight:600;color:#14532d;">Downloading. Check your Downloads folder</span>
    </div>
  </div>
</div>
<script>
(function () {{
  var SB = 'https://rszrggreuarvodcqeqrj.supabase.co';
  var ANON = '{P.ANON}';
  function track(n, p) {{ if (typeof gtag === 'function') gtag('event', n, p || {{}}); }}
  var g = document.querySelector('[data-gate="inline"]');
  if (!g) return;
  var idle = g.querySelector('.g-idle'), form = g.querySelector('.g-form'), sent = g.querySelector('.g-sent');
  var input = g.querySelector('.g-email'), send = g.querySelector('.g-send'), open = g.querySelector('.g-open');
  open.addEventListener('click', function () {{
    idle.style.display = 'none'; form.style.display = 'block';
    track('haccp_form_open', {{ placement: 'us-inspection:{slug}-inline' }});
    setTimeout(function () {{ input.focus(); }}, 30);
  }});
  function submit() {{
    var email = (input.value || '').trim();
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) {{
      input.style.boxShadow = 'inset 0 0 0 1.5px #d64545'; input.focus(); return;
    }}
    form.style.display = 'none'; sent.style.display = 'block';
    try {{ localStorage.setItem('br-tpl-downloaded', '1'); }} catch (e) {{}}
    fetch(SB + '/rest/v1/template_leads', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'apikey': ANON, 'Authorization': 'Bearer ' + ANON, 'Prefer': 'return=minimal' }},
      body: JSON.stringify({{ email: email, source: 'us-template:inspection:{slug}-inline', page: window.location.pathname, user_agent: navigator.userAgent.slice(0, 250) }})
    }}).catch(function () {{}});
    fetch('https://formsubmit.co/ajax/hello@blueroll.app', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'Accept': 'application/json' }},
      body: JSON.stringify({{ email: email, _subject: 'New inspection checklist download (US, {city}): ' + email, source: 'us-template:inspection', placement: '{slug}-inline', page: window.location.href }})
    }}).catch(function () {{}});
    track('haccp_template_download', {{ placement: 'us-inspection:{slug}-inline', email_domain: email.split('@')[1] }});
    var a = document.createElement('a');
    a.href = '/{PDF}'; a.download = '{PDF}';
    document.body.appendChild(a); a.click(); a.remove();
  }}
  send.addEventListener('click', submit);
  input.addEventListener('keydown', function (e) {{ if (e.key === 'Enter') {{ e.preventDefault(); submit(); }} }});
  input.addEventListener('input', function () {{ input.style.boxShadow = 'inset 0 0 0 1.5px #e2e4e8'; }});
}})();
</script>
"""


def main():
    page = P.build_head(PAGE) + P.build_body(PAGE) + "\n" + P.build_tail(PAGE)
    assert page.count('data-gate="') == 4
    assert 'hreflang' not in page.split("</head>")[0]
    (P.ROOT / PAGE["file"]).write_text(page)
    print("built", PAGE["file"])
    for f, (slug, city, who) in CITIES.items():
        path = P.ROOT / f
        s = path.read_text()
        if f"us-template:inspection:{slug}-inline" in s:
            print("gate already on", f)
            continue
        assert 'data-gate="' not in s, f
        anchor = '<div class="content">\n'
        assert s.count(anchor) == 1, f
        path.write_text(s.replace(anchor, anchor + city_gate(slug, city, who)))
        print("gate added to", f)


if __name__ == "__main__":
    main()
