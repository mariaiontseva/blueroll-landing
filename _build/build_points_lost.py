#!/usr/bin/env python3
"""Build food-hygiene-ratings/where-points-are-lost.html from computed FSA council stats.

Every figure on the page comes from two files made by ~/blueroll-log/fsa/council_stats.py
(FSA FHRS API v2, open data). Nothing on the page is typed by hand.

    food-hygiene-ratings/council-stats-<as_of>.csv   per-council table, also the public download
    _build/data/fsa-national-<as_of>.json            national totals and by_type

Usage, from the repo root:
    python3 _build/build_points_lost.py                       # build from the copies in the repo
    python3 _build/build_points_lost.py --from ~/blueroll-log/fsa   # copy the newest pair in first

Site chrome (nav + footer) is lifted from a live article page, like build_owner_pages.py.
"""
import csv
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "food-hygiene-ratings"
DATA_DIR = ROOT / "_build" / "data"
PAGE = "where-points-are-lost.html"
SITE = "https://blueroll.app"
URL = f"{SITE}/food-hygiene-ratings/{PAGE}"
PUBLISHED = "2026-11-19"  # first publication of the page; dateModified follows the data
FSA_OPEN_DATA = "https://ratings.food.gov.uk/open-data"
OGL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"

# FSA business type -> label on the page, in the order the page shows them.
TYPES = [
    ("Restaurant/Cafe/Canteen", "Restaurants, cafes and canteens"),
    ("Takeaway/sandwich shop", "Takeaways and sandwich shops"),
    ("Pub/bar/nightclub", "Pubs, bars and nightclubs"),
    ("Mobile caterer", "Mobile caterers"),
    ("Hotel/bed & breakfast/guest house", "Hotels, B&Bs and guest houses"),
    ("Other catering premises", "Other catering premises"),
]
# Inspection areas: key, name on the page, column in the data.
AREAS = [
    ("management", "Confidence in management", "below5_management_10plus_pct"),
    ("structure", "Structure and cleaning", "below5_structure_10plus_pct"),
    ("hygiene", "Hygienic food handling", "below5_hygiene_10plus_pct"),
]
AREA_NAME = {k: n for k, n, _ in AREAS}
AREA_COL = {k: c for k, _, c in AREAS}


# ---------------------------------------------------------------- data

def copy_in(src: Path) -> None:
    """Copy the newest council-stats-<d>.csv / national-<d>.json pair from src into the repo."""
    dates = sorted(p.stem.split("national-")[1] for p in src.glob("national-*.json"))
    assert dates, f"no national-*.json in {src}"
    d = dates[-1]
    shutil.copyfile(src / f"council-stats-{d}.csv", OUT_DIR / f"council-stats-{d}.csv")
    DATA_DIR.mkdir(exist_ok=True)
    shutil.copyfile(src / f"national-{d}.json", DATA_DIR / f"fsa-national-{d}.json")
    print("copied data for", d)


def load():
    js = sorted(DATA_DIR.glob("fsa-national-*.json"))
    assert js, "no _build/data/fsa-national-*.json; run with --from first"
    nat = json.loads(js[-1].read_text())
    as_of = nat["as_of"]
    csv_path = OUT_DIR / f"council-stats-{as_of}.csv"
    with csv_path.open(newline="") as f:
        rows = list(csv.DictReader(f))

    def num(v, kind):
        return None if v == "" else kind(v)

    councils = []
    for r in rows:
        councils.append({
            "council": r["council"],
            "rated": int(r["rated"]),
            "at_5_pct": float(r["at_5_pct"]),
            "below_5": int(r["below_5"]),
            "below_5_pct": float(r["below_5_pct"]),
            "management": num(r["below5_management_10plus_pct"], float),
            "structure": num(r["below5_structure_10plus_pct"], float),
            "hygiene": num(r["below5_hygiene_10plus_pct"], float),
            "median_days": int(r["median_days_since_inspection"]),
        })
    # The two files must describe the same counts.
    assert len(councils) == nat["councils"], "council count differs between CSV and JSON"
    assert sum(c["rated"] for c in councils) == nat["national"]["rated"], "rated total differs"
    assert sum(c["below_5"] for c in councils) == nat["national"]["below_5"], "below-5 total differs"
    assert set(nat["by_type"]) == {t for t, _ in TYPES}, f"unexpected business types: {sorted(nat['by_type'])}"
    assert sum(v["rated"] for v in nat["by_type"].values()) == nat["national"]["rated"], "type totals differ"
    return as_of, csv_path, nat, councils


# ---------------------------------------------------------------- formatting

def n(v: int) -> str:
    return f"{v:,}"


def pc(v) -> str:
    return f"{v:.1f}%"


def long_date(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%-d %B %Y")


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def text_of(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def join_and(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


# ---------------------------------------------------------------- chrome

_SRC = (ROOT / "food-hygiene-ratings-explained.html").read_text()
_NAV_END = _SRC.index('<div style="max-width: 1160px; margin: 22px auto 0;')
CHROME_NAV = _SRC[_SRC.index("<!-- ============ NAV ============ -->"):_NAV_END].rstrip()
CHROME_FOOTER = _SRC[_SRC.rindex("<!-- ============ FOOTER ============ -->"):_SRC.rindex("</body>")].rstrip()
assert "nav-burger" in CHROME_NAV and "mobile-menu" in CHROME_NAV, "nav extraction broke"
assert "footer-grid" in CHROME_FOOTER and "getElementById('nav-burger')" in CHROME_FOOTER, "footer extraction broke"

CSS = """
  /* same system as eho-inspection-checklist.html (design pass 18.11.2026) */
  :root { --ink:#16181d; --text:#2c3036; --muted:#5c626b; --soft:#8a9099; --line:#e5e7e4; --line-strong:#cfd4cf;
          --green:#047857; --green-btn:#1f9d63; --band:#f6f7f8; --mint:#eef6f1; --amber:#c2410c; }
  * { box-sizing:border-box; }
  body { margin:0; background:#fff; color:var(--ink); font:16px/1.6 "Geist",-apple-system,'Segoe UI',Arial,sans-serif; -webkit-font-smoothing:antialiased; }
  html { scroll-behavior:smooth; }
  a { text-decoration:none; }
  img { max-width:100%; }

  main { font-size:17px; line-height:1.6; color:var(--text); overflow-x:clip; }
  main a { color:var(--green); }
  main p a, main li a, main dd a { text-decoration:underline; text-underline-offset:3px; text-decoration-color:rgba(4,120,87,.35); }
  main p a:hover, main li a:hover, main dd a:hover { text-decoration-color:currentColor; }

  .band { padding:96px 0; }
  .band.alt { background:var(--band); }
  .inner { max-width:1160px; margin:0 auto; padding:0 24px; }

  h1 { font-size:50px; line-height:1.06; letter-spacing:-.03em; font-weight:800; color:var(--ink); margin:0 0 22px; text-wrap:balance; }
  h2 { font-size:32px; line-height:1.18; letter-spacing:-.02em; font-weight:800; color:var(--ink); margin:0 0 14px; text-wrap:balance; scroll-margin-top:84px; }
  p { margin:0 0 18px; }
  b, strong { color:var(--ink); font-weight:600; }
  .intro { font-size:18px; line-height:1.55; color:var(--muted); max-width:700px; margin:0 0 36px; }
  .shot { display:block; width:100%; height:auto; border-radius:16px; border:1px solid var(--line); background:#fff; box-shadow:0 1px 2px rgba(16,24,40,.05), 0 16px 40px rgba(16,24,40,.08); }

  /* first screen */
  .hero { background:var(--band); padding:0 0 88px; }
  .crumbs { font-size:13px; color:var(--soft); padding-top:12px; }
  .crumbs a { display:inline-block; padding:12px 0; color:var(--soft); }
  .crumbs a:hover { color:var(--green); }
  .hero-grid { display:grid; grid-template-columns:minmax(0,5fr) minmax(0,6fr); gap:64px; align-items:center; margin-top:36px; }
  .lede { font-size:19px; line-height:1.55; color:var(--muted); margin:0; text-wrap:pretty; }
  .lede b { color:var(--ink); }
  .src { font-size:15px; color:var(--muted); margin:24px 0 0; }
  .kpis { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }
  .kpi { background:#fff; border:1px solid var(--line); border-radius:16px; padding:24px 24px 22px; }
  .kpi b { display:block; font-size:50px; font-weight:800; letter-spacing:-.035em; line-height:1; color:var(--ink); font-variant-numeric:tabular-nums; white-space:nowrap; }
  .kpi span { display:block; margin-top:10px; font-size:15.5px; line-height:1.4; color:var(--muted); }
  .meter { height:8px; border-radius:4px; background:var(--line); margin-top:16px; overflow:hidden; }
  .meter i { display:block; height:100%; border-radius:4px; background:var(--green-btn); }
  .kpi-h { grid-column:1 / -1; margin:14px 0 0; font-size:16px; line-height:1.45; font-weight:600; color:var(--ink); }
  .areas { grid-column:1 / -1; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }
  .areas .kpi { padding:20px 20px 20px; }
  .areas .kpi b { font-size:38px; }
  .areas .kpi span { font-size:15px; }
  .areas .meter i { background:var(--amber); }

  /* tables */
  .tscroll { overflow-x:auto; -webkit-overflow-scrolling:touch; }
  table.t { width:100%; border-collapse:separate; border-spacing:0; font-size:15.5px; line-height:1.45; }
  .t th { text-align:right; font-weight:700; color:var(--ink); padding:10px 0 10px 18px; border-bottom:1px solid var(--line-strong); vertical-align:bottom; background:#fff; white-space:nowrap; }
  .t thead th:last-child { white-space:normal; min-width:132px; }
  .tbox .t thead th:last-child { min-width:190px; }
  .t td { text-align:right; padding:12px 0 12px 18px; border-bottom:1px solid var(--line); color:var(--text); font-variant-numeric:tabular-nums; white-space:nowrap; background:#fff; }
  .t th:first-child, .t td:first-child { text-align:left; padding-left:0; padding-right:8px; white-space:normal; }
  .t tbody th { font-weight:600; }
  .t tr.all td, .t tr.all th { font-weight:700; color:var(--ink); border-bottom:0; border-top:1px solid var(--line-strong); }
  .t-types th:first-child { width:28%; min-width:180px; }
  .t .na { color:var(--soft); }

  /* all councils */
  .ctools { margin:0 0 16px; }
  .ctools input { width:100%; max-width:360px; min-height:48px; padding:0 16px; border:1px solid var(--line-strong); border-radius:10px; background:#fff; color:var(--ink); font:inherit; font-size:16px; }
  .ctools input:focus { outline:2px solid var(--green-btn); outline-offset:1px; }
  .tbox { overflow:auto; -webkit-overflow-scrolling:touch; max-height:min(720px, 78vh); border:1px solid var(--line); border-radius:14px; background:#fff; }
  .tbox table.t { font-size:15px; }
  .tbox .t th { position:sticky; top:0; z-index:2; padding:12px 16px; }
  .tbox .t td { padding:11px 16px; }
  .tbox .t th:first-child, .tbox .t td:first-child { position:sticky; left:0; z-index:1; padding-left:20px; min-width:190px; }
  .tbox .t thead th:first-child { z-index:3; }
  .tbox .t th:last-child, .tbox .t td:last-child { padding-right:20px; }
  .tbox .t tbody tr:last-child td { border-bottom:0; }
  .t th .sort { all:unset; cursor:pointer; display:inline; font:inherit; color:inherit; }
  .t th .sort:focus-visible { outline:2px solid var(--green-btn); outline-offset:2px; }
  .t th[aria-sort="ascending"] .sort::after { content:" \\2191"; color:var(--green); }
  .t th[aria-sort="descending"] .sort::after { content:" \\2193"; color:var(--green); }
  .cnone { margin:14px 0 0; color:var(--muted); }

  /* owner */
  .feat { display:grid; grid-template-columns:minmax(0,6fr) minmax(0,5fr); gap:72px; align-items:center; }
  .feat-text p { font-size:18px; }
  .feat-text p:last-child { margin-bottom:0; }
  .feat-media { display:flex; justify-content:center; }
  .feat-media .shot { width:auto; max-width:300px; border-radius:24px; }

  /* method */
  .defs { display:grid; grid-template-columns:220px minmax(0,1fr); margin:8px 0 0; border-top:1px solid var(--line-strong); max-width:980px; }
  .defs dt, .defs dd { margin:0; padding:16px 0; border-bottom:1px solid var(--line); }
  .defs dt { font-weight:700; color:var(--ink); padding-right:24px; }
  .defs dd { font-size:16.5px; overflow-wrap:anywhere; }

  button:focus-visible, input:focus-visible, a:focus-visible { outline:2px solid var(--green-btn); outline-offset:2px; }

  @media (max-width:1000px) {
    .hero-grid, .feat { gap:48px; }
    .kpi b { font-size:44px; }
  }
  @media (max-width:860px) {
    .hero-grid, .feat { grid-template-columns:minmax(0,1fr); }
  }
  @media (max-width:760px) {
    .inner { padding:0 16px; }
    .band { padding:72px 0; }
    .hero { padding-bottom:72px; }
    .hero-grid { margin-top:20px; gap:36px; }
    h1 { font-size:34px; }
    h2 { font-size:28px; }
    .lede { font-size:18px; }
    .intro { font-size:17px; margin-bottom:28px; }
    .kpis { gap:10px; }
    .kpi { padding:18px 16px 16px; border-radius:14px; }
    .kpi b { font-size:34px; }
    .kpi span { font-size:14.5px; margin-top:8px; }
    .areas { gap:10px; }
    .areas .kpi { padding:16px 14px; }
    .areas .kpi b { font-size:27px; }
    .areas .kpi span { font-size:13.5px; }
    .meter { margin-top:12px; height:6px; }
    .feat { gap:36px; }
    .feat-text p { font-size:17px; }
    .feat-media .shot { max-width:260px; }
    .tbox .t th:first-child, .tbox .t td:first-child { min-width:150px; padding-left:14px; }
    .tbox .t th, .tbox .t td { padding-left:12px; padding-right:12px; }
    .defs { grid-template-columns:minmax(0,1fr); }
    .defs dt { border-bottom:0; padding-bottom:4px; }
    .defs dd { padding-top:0; }
    .footer-grid { grid-template-columns:1fr 1fr !important; }
    .footer-grid > div:first-child { grid-column:1 / -1; }
  }
  @media (prefers-reduced-motion:reduce) { * { transition:none !important; animation:none !important; } html { scroll-behavior:auto; } }
"""

JS = """
(function () {
  var t = document.getElementById('councils'); if (!t) return;
  var tb = t.tBodies[0], rows = Array.prototype.slice.call(tb.rows);
  var tools = document.getElementById('ctools'), q = document.getElementById('cq'), none = document.getElementById('cnone');
  tools.hidden = false;
  q.addEventListener('input', function () {
    var s = q.value.trim().toLowerCase(), shown = 0;
    rows.forEach(function (r) {
      var m = !s || r.cells[0].textContent.toLowerCase().indexOf(s) > -1;
      r.hidden = !m; if (m) shown++;
    });
    none.hidden = shown > 0;
  });
  var ths = t.tHead.rows[0].cells;
  Array.prototype.forEach.call(ths, function (th, i) {
    var b = document.createElement('button'); b.type = 'button'; b.className = 'sort';
    while (th.firstChild) b.appendChild(th.firstChild);
    th.appendChild(b);
    b.addEventListener('click', function () {
      var cur = th.getAttribute('aria-sort');
      var dir = cur === 'ascending' ? 'descending' : cur === 'descending' ? 'ascending' : (i === 0 ? 'ascending' : 'descending');
      Array.prototype.forEach.call(ths, function (h) { h.removeAttribute('aria-sort'); });
      th.setAttribute('aria-sort', dir);
      var k = dir === 'ascending' ? 1 : -1;
      rows.sort(function (a, b) {
        if (i === 0) return k * a.cells[0].textContent.localeCompare(b.cells[0].textContent, 'en-GB');
        var x = a.cells[i].getAttribute('data-v'), y = b.cells[i].getAttribute('data-v');
        if (x === y) return 0; if (x === '') return 1; if (y === '') return -1;
        return k * (parseFloat(x) - parseFloat(y));
      });
      rows.forEach(function (r) { tb.appendChild(r); });
    });
  });
  var dl = document.getElementById('csv-dl');
  if (dl) dl.addEventListener('click', function () { if (typeof gtag === 'function') gtag('event', 'fsa_data_csv_download', {}); });
})();
"""


# ---------------------------------------------------------------- page

def build(as_of, csv_path, nat, councils) -> str:
    N = nat["national"]
    T = nat["by_type"]
    day = long_date(as_of)
    n_councils = len(councils)
    csv_name = csv_path.name
    csv_url = f"{SITE}/food-hygiene-ratings/{csv_name}"

    # Areas ranked by how often they hold a business below 5, nationally.
    ranked = sorted(AREAS, key=lambda a: -N[a[2]])
    # The owner section talks about management first and structure second; stop if the data says otherwise.
    assert [a[0] for a in ranked][:2] == ["management", "structure"], f"area order changed: {[a[0] for a in ranked]}"

    title = "Why Food Businesses Miss a 5: Scores by Council | Blueroll"
    h1 = "Why food businesses miss a 5: hygiene scores council by council"
    desc = (f"Of {n(N['rated'])} rated hospitality businesses in England, Wales and NI, {pc(N['at_5_pct'])} hold a 5. "
            f"See which inspection score keeps the rest below it, in all {n_councils} councils.")
    og_desc = (f"{pc(N['at_5_pct'])} of rated hospitality businesses hold a 5. Which of the three inspection scores "
               f"keeps the rest below it, for every council in England, Wales and Northern Ireland.")
    assert 50 <= len(title) <= 60, f"title length {len(title)}"
    assert 140 <= len(desc) <= 158, f"description length {len(desc)}: {desc}"

    # ---- first screen
    first, rest = ranked[0], ranked[1:]
    area_clause = (f"{pc(N[first[2]])} scored 10 or more for {first[1].lower()}, "
                   + join_and(f"{pc(N[c])} for {name.lower()}" for _, name, c in rest))
    lede = (f"Of <b>{n(N['rated'])}</b> hospitality businesses rated 0 to 5 in England, Wales and Northern Ireland, "
            f"<b>{pc(N['at_5_pct'])}</b> hold a 5. Of the {n(N['below_5'])} below a 5, {area_clause}. "
            f"A 5 needs every score at 5 or less, so a single score of 10 or more is enough to miss it.")
    area_cards = "".join(
        f'<div class="kpi"><b>{pc(N[c])}</b><span>{name}</span>'
        f'<div class="meter" aria-hidden="true"><i style="width:{N[c]}%"></i></div></div>'
        for _, name, c in ranked)
    kpis = f"""<div class="kpis">
          <div class="kpi"><b>{n(N['rated'])}</b><span>hospitality businesses rated</span></div>
          <div class="kpi"><b>{pc(N['at_5_pct'])}</b><span>hold a 5</span><div class="meter" aria-hidden="true"><i style="width:{N['at_5_pct']}%"></i></div></div>
          <p class="kpi-h">Of the {n(N['below_5'])} below a 5, the share that scored 10 or more in each area</p>
          <div class="areas">{area_cards}</div>
        </div>"""

    # ---- by type
    lab = dict(TYPES)
    lo = min(T, key=lambda t: T[t]["at_5_pct"])
    hi = max(T, key=lambda t: T[t]["at_5_pct"])
    top_area = {t: max(AREAS, key=lambda a: T[t][a[2]])[0] for t in T}
    common = max(set(top_area.values()), key=lambda k: sum(1 for v in top_area.values() if v == k))
    odd = [t for t, _ in TYPES if top_area[t] != common]
    type_intro = (f"{lab[lo]} have the lowest share at 5 ({pc(T[lo]['at_5_pct'])}) and "
                  f"{lab[hi].lower()} the highest ({pc(T[hi]['at_5_pct'])}). ")
    if not odd:
        type_intro += f"{AREA_NAME[common]} is the score most often at 10 or more in every type."
    else:
        type_intro += (f"{AREA_NAME[common]} is the score most often at 10 or more in every type except "
                       + join_and(f"{lab[t].lower()}, where it is {AREA_NAME[top_area[t]].lower()}" for t in odd) + ".")

    def score_cells(d):
        return "".join(f"<td>{pc(d[AREA_COL[k]])}</td>" for k in ("management", "structure", "hygiene"))

    type_rows = "".join(
        f"<tr><th scope=\"row\">{esc(label)}</th><td>{n(T[t]['rated'])}</td><td>{pc(T[t]['at_5_pct'])}</td>"
        f"<td>{pc(T[t]['below_5_pct'])}</td>{score_cells(T[t])}<td>{n(T[t]['median_days_since_inspection'])}</td></tr>"
        for t, label in TYPES)
    type_rows += (f"<tr class=\"all\"><th scope=\"row\">All six types</th><td>{n(N['rated'])}</td><td>{pc(N['at_5_pct'])}</td>"
                  f"<td>{pc(N['below_5_pct'])}</td>{score_cells(N)}<td>{n(N['median_days_since_inspection'])}</td></tr>")
    head_cells = ("<th>Rated</th><th>At&nbsp;5</th><th>Below&nbsp;5</th><th>Management 10+</th>"
                  "<th>Structure 10+</th><th>Hygiene 10+</th><th>Median days since inspection</th>")

    # ---- all councils
    def cell(v, shown):
        if v is None:
            return '<td data-v=""><span class="na">n/a</span></td>'
        return f'<td data-v="{v}">{shown}</td>'

    council_rows = "\n".join(
        "<tr><td>" + esc(c["council"]) + "</td>"
        + cell(c["rated"], n(c["rated"])) + cell(c["at_5_pct"], pc(c["at_5_pct"]))
        + cell(c["below_5_pct"], pc(c["below_5_pct"]))
        + "".join(cell(c[k], None if c[k] is None else pc(c[k])) for k in ("management", "structure", "hygiene"))
        + cell(c["median_days"], n(c["median_days"])) + "</tr>"
        for c in councils)

    # ---- method
    smallest = min(councils, key=lambda c: c["rated"])
    type_list = join_and(t for t, _ in TYPES)

    page_body = f"""
<main>
  <section class="hero">
    <div class="inner">
      <div class="crumbs"><a href="/">Blueroll</a> › <a href="/food-hygiene-ratings/">Food hygiene ratings</a> › Where points are lost</div>
      <div class="hero-grid">
        <div>
          <h1>{h1}</h1>
          <p class="lede">{lede}</p>
          <p class="src">Data: Food Standards Agency, ratings published as of {day}</p>
        </div>
        {kpis}
      </div>
    </div>
  </section>

  <section class="band">
    <div class="inner">
      <h2 id="by-type">By type of business</h2>
      <p class="intro">{esc(type_intro)}</p>
      <div class="tscroll">
        <table class="t t-types">
          <thead><tr><th>Business type</th>{head_cells}</tr></thead>
          <tbody>{type_rows}</tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="band alt">
    <div class="inner">
      <div class="feat">
        <div class="feat-text">
          <h2 id="owners">What it means for an owner</h2>
          <p>{AREA_NAME['management']} is the score most often at 10 or more, ahead of {AREA_NAME['structure'].lower()}. It is mostly about your food safety management system and the records that show you follow it: your Safer Food, Better Business pack or HACCP plan, daily checks, temperatures, cleaning and training.</p>
          <p><a href="/how-to-get-a-5-food-hygiene-rating.html">How to get a 5</a> shows how the three scores set your rating, and the <a href="/eho-inspection-checklist.html">EHO inspection checklist</a> covers what the officer looks at. For the records, start with the <a href="/free-haccp-template.html">free HACCP template</a> and a <a href="/kitchen-cleaning-schedule-template.html">kitchen cleaning schedule</a>.</p>
          <p><a href="/">Blueroll</a> keeps those records on the team's phones, each check saved with the time and who did it.</p>
        </div>
        <div class="feat-media"><img class="shot" src="/uploads/eho-phone.webp" width="780" height="1128" loading="lazy" alt="Blueroll on a phone: opening checks, fridge and freezer temperatures, probe calibration, deliveries, hot-hold temperatures, allergen labels and the weekly deep clean ticked off"></div>
      </div>
    </div>
  </section>

  <section class="band">
    <div class="inner">
      <h2 id="councils-h">All {n_councils} councils</h2>
      <p class="intro">The score columns show the share of businesses below a 5 that scored 10 or more in that area.</p>
      <div class="ctools" id="ctools" hidden><input id="cq" type="search" placeholder="Search for a council" aria-label="Search for a council" autocomplete="off"></div>
      <div class="tbox">
        <table class="t" id="councils">
          <thead><tr><th aria-sort="ascending">Council</th>{head_cells}</tr></thead>
          <tbody>
{council_rows}
          </tbody>
        </table>
      </div>
      <p class="cnone" id="cnone" hidden>No council matches that search.</p>
    </div>
  </section>

  <section class="band alt">
    <div class="inner">
      <h2 id="method">Method</h2>
      <dl class="defs">
        <dt>Source</dt>
        <dd>Food Standards Agency, <a href="{FSA_OPEN_DATA}">Food Hygiene Rating Scheme open data</a>, read through the FHRS API (version 2) on {day}.</dd>
        <dt>Councils</dt>
        <dd>All {n_councils} local authorities on the 0 to 5 scheme in England, Wales and Northern Ireland, port health authorities included. Scotland is left out because its scheme, FHIS, gives a pass or improvement required rather than a score from 0 to 5.</dd>
        <dt>Business types</dt>
        <dd>{esc(type_list)}, as the FSA classifies them. Other types, such as retailers, manufacturers, schools and care premises, are not counted.</dd>
        <dt>Rated</dt>
        <dd>Businesses with a published rating from 0 to 5, all three inspection scores and a rating date. Exempt businesses, those awaiting inspection or publication, and records missing a score or the date are left out.</dd>
        <dt>Scores</dt>
        <dd>Points against, so 0 is best. Hygienic food handling and structure and cleaning each run from 0 to 25; confidence in management runs from 0 to 30. A 5 needs every score at 5 or less, so a score of 10 or more in an area is what keeps a business below 5.</dd>
        <dt>Percentages</dt>
        <dd>At 5 and below 5 are shares of rated businesses. The three score columns are shares of businesses below 5; one business can count in more than one, so they do not add up to 100%. Figures are rounded to one decimal place, and n/a means no business in that council is below 5.</dd>
        <dt>Days since inspection</dt>
        <dd>The median number of days from the rating date in each FSA record to {day}.</dd>
        <dt>Limitations</dt>
        <dd>These are the ratings on the register now, and some are years old: nationally the median is {n(N['median_days_since_inspection'])} days, and {pc(N['inspected_over_2y_ago_pct'])} of ratings are more than 730 days old. A new inspection appears only once the council publishes it. Small councils rest on few businesses: {esc(smallest['council'])} has {n(smallest['rated'])} rated.</dd>
        <dt>Licence</dt>
        <dd>Contains Food Standards Agency data licensed under the <a href="{OGL}">Open Government Licence v3.0</a>.</dd>
        <dt>Download</dt>
        <dd><a id="csv-dl" href="/food-hygiene-ratings/{csv_name}" download>{csv_name}</a>: the council table, plus the number below 5, the share rated 0 to 2 and the share with a rating more than 730 days old.</dd>
      </dl>
    </div>
  </section>
</main>
"""

    org = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Blueroll", "url": f"{SITE}/",
           "logo": {"@type": "ImageObject", "url": f"{SITE}/app_icon.png"}}
    dataset_desc = (f"Food hygiene ratings and inspection scores for hospitality businesses in all {n_councils} councils "
                    f"on the 0 to 5 scheme in England, Wales and Northern Ireland, from the Food Standards Agency's "
                    f"open data as published on {day}. For each council: businesses rated, share at 5 and below 5, "
                    f"and, among businesses below 5, the share scoring 10 or more for confidence in management, "
                    f"structure and cleaning, and hygienic food handling, with the median days since the rating date.")
    graph = [
        org,
        {"@type": "Dataset", "@id": f"{URL}#dataset",
         "name": "Food hygiene scores by council: where hospitality businesses lose points",
         "description": dataset_desc, "url": URL,
         "creator": {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Blueroll", "url": f"{SITE}/"},
         "isBasedOn": FSA_OPEN_DATA,
         "license": OGL, "isAccessibleForFree": True,
         "temporalCoverage": as_of, "dateModified": as_of, "datePublished": PUBLISHED,
         "spatialCoverage": [{"@type": "Place", "name": p} for p in ("England", "Wales", "Northern Ireland")],
         "variableMeasured": ["Rated businesses", "Share at 5", "Share below 5",
                              "Below 5: share with confidence in management score 10 or more",
                              "Below 5: share with structure and cleaning score 10 or more",
                              "Below 5: share with hygienic food handling score 10 or more",
                              "Median days since inspection"],
         "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": csv_url}]},
        {"@type": "Article", "headline": h1, "description": desc, "image": f"{SITE}/og-image.png",
         "datePublished": PUBLISHED, "dateModified": as_of, "inLanguage": "en-GB",
         "author": {"@id": f"{SITE}/#org"}, "publisher": {"@id": f"{SITE}/#org"},
         "mainEntityOfPage": {"@type": "WebPage", "@id": URL}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Blueroll", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Food hygiene ratings", "item": f"{SITE}/food-hygiene-ratings/"},
            {"@type": "ListItem", "position": 3, "name": "Where points are lost", "item": URL}]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)

    head = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{URL}">
<link rel="alternate" hreflang="en-gb" href="{URL}">
<link rel="alternate" hreflang="x-default" href="{URL}">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Blueroll">
<meta property="og:locale" content="en_GB">
<meta property="og:url" content="{URL}">
<meta property="og:title" content="{esc(h1)}">
<meta property="og:description" content="{esc(og_desc)}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="article:published_time" content="{PUBLISHED}">
<meta property="article:modified_time" content="{as_of}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(h1)}">
<meta name="twitter:description" content="{esc(og_desc)}">
<meta name="twitter:image" content="{SITE}/og-image.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="/site-chrome.css?v=20260720-solutions-v1">
<link rel="stylesheet" href="/site-chrome-v2.css?v=20260812">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-ZFY0GPZYYQ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-ZFY0GPZYYQ');</script>
<script type="application/ld+json">
{ld}
</script>
<style>{CSS}</style>
<script src="/geo-analytics.js" defer></script>
</head>
<body>
"""
    out = head + CHROME_NAV + "\n" + page_body + "\n" + CHROME_FOOTER + f"\n<script>{JS}</script>\n</body>\n</html>\n"

    # Guards: one h1, no em dashes, no unfilled braces, every council present.
    assert out.count("<h1") == 1
    assert "—" not in out, "em dash on the page"
    assert "{" not in text_of(page_body), "unfilled placeholder"
    assert out.count("<tr><td>") == n_councils
    return out


def main(argv):
    if len(argv) >= 2 and argv[0] == "--from":
        copy_in(Path(argv[1]).expanduser())
    as_of, csv_path, nat, councils = load()
    out = build(as_of, csv_path, nat, councils)
    (OUT_DIR / PAGE).write_text(out)
    print(f"built food-hygiene-ratings/{PAGE} ({len(out):,} bytes) from {csv_path.name}, as of {as_of}")


if __name__ == "__main__":
    main(sys.argv[1:])
