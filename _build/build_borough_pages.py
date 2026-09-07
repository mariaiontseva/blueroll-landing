#!/usr/bin/env python3
"""Generate the 33 London borough rating pages + hub from FSA data.

Reads _build/borough_template.html and _build/data/borough_data.json,
writes food-hygiene-ratings/<slug>.html and food-hygiene-ratings/index.html,
and maintains marker-fenced blocks in sitemap.xml and llms.txt. Run after
fetch_borough_data.py, from the repo root:

    python3 _build/build_borough_pages.py
"""
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from borough_config import BOROUGHS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "food-hygiene-ratings"
OUT.mkdir(exist_ok=True)
TEMPLATE = (Path(__file__).parent / "borough_template.html").read_text()
DATA = json.loads((Path(__file__).parent / "data" / "borough_data.json").read_text())

m = re.search(r"var ANON = '(eyJ[^']+)'", (ROOT / "free-haccp-template.html").read_text())
assert m, "anon key not found on the template page"
ANON = m.group(1)

UPDATED = date.today().strftime("%-d %B %Y")


def fmt_n(n: int) -> str:
    return f"{n:,}"


def fmt_d(iso: str) -> str:
    if not iso:
        return "?"
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%b %Y")


def link_name(slug: str) -> str:
    n = BOROUGHS[slug]["name"]
    return n[4:].strip() if n.startswith("the ") else n


def esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def strip_tags(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def movers_html(b: dict, name: str, prev_date) -> str:
    if prev_date and (b["movers_up"] or b["movers_down"]):
        def rows(items, arrow):
            return "".join(
                f'<li><span class="who">{esc(e["name"])}</span>'
                f'<span class="chg">{e["was"]} {arrow} {e["r"]}</span></li>'
                for e in items) or '<li><span class="who">No changes this week</span></li>'
        return (f'<div class="mv">'
                f'<div class="mvcard up"><h3>Climbed since last week</h3><ul>{rows(b["movers_up"], "&rarr;")}</ul></div>'
                f'<div class="mvcard down"><h3>Dropped since last week</h3><ul>{rows(b["movers_down"], "&rarr;")}</ul></div>'
                f'</div>')
    low_rows = "".join(
        f'<li><span class="who">{esc(e["name"])}</span><span class="chg">&rarr; {e["r"]} &middot; {fmt_d(e["d"])}</span></li>'
        for e in b["recent_low"]) or '<li><span class="who">None. A clean month.</span></li>'
    return (f'<div class="mv">'
            f'<div class="mvcard up"><h3>Inspections in the last month</h3>'
            f'<ul><li><span class="who">Kitchens inspected and rated</span><span class="chg">{b["recent_count"]}</span></li>'
            f'<li><span class="who">Walked away with a 5</span><span class="chg">{b["recent_new5"]}</span></li></ul></div>'
            f'<div class="mvcard down"><h3>Recent ratings of 2 or below</h3><ul>{low_rows}</ul></div>'
            f'</div>')


def build_page(slug: str) -> str:
    cfg, b = BOROUGHS[slug], DATA["boroughs"][slug]
    name, council = cfg["name"], cfg["council"]
    rated = b["rated"]
    counts = b["counts"]
    widths = {r: (round(100 * counts[r] / rated, 1) if rated else 0) for r in counts}
    for r, w in widths.items():
        if counts[r] and w < 0.5:
            widths[r] = 0.5

    title = f"Food Hygiene Ratings in {name}: {fmt_n(rated)} Kitchens Rated 0&ndash;5 | Blueroll"
    og_title = f"Food Hygiene Ratings in {name}"
    desc = (f"Every rated food business in {name}: {b['pct5']}% hold a 5 and {b['low']} need improvement. "
            f"Live map, this month's changes and the full 0-1 list. Updated weekly.")
    assert len(strip_tags(desc)) < 175, f"{slug}: description too long"

    worst = b["worst"]
    worst_rows = "".join(
        f'<tr><td>{esc(e["name"])}</td><td>{esc(e["type"])}</td>'
        f'<td>{esc(", ".join(x for x in [e["addr"], e["pc"]] if x))}</td>'
        f'<td class="r r{e["r"]}">{e["r"]}</td><td>{fmt_d(e["d"])}</td></tr>'
        for e in worst) or '<tr><td colspan="5">Nothing rated 0 or 1 right now. Well done, ' + esc(name) + '.</td></tr>'
    n01 = counts["0"] + counts["1"]
    worst_note = (f"All {n01} businesses rated 0 or 1, from the FSA register." if n01 <= 15
                  else f"The 15 longest-standing of {n01} businesses rated 0 or 1, from the FSA register.")

    exempt = b["total"] - rated
    exempt_note = (f"{fmt_n(exempt)} further establishments are exempt or awaiting their first inspection."
                   if exempt > 0 else "Every registered establishment currently holds a rating.")

    nearby = " &middot; ".join(
        f'<a href="/food-hygiene-ratings/{n}.html">{esc(link_name(n))}</a>' for n in cfg["neighbours"])

    faqs = [
        (f"Who inspects food businesses in {name}?",
         f"Environmental health officers from {council}. Visits are unannounced, and the new rating is published on the FSA register within a few weeks of the inspection."),
        (f"My kitchen in {name} got a low rating. How do I get re-inspected?",
         f"Fix the issues, then request a re-rating visit through {council}. Officers look hardest at your daily records; our guide to improving your food hygiene rating covers the fastest route back to a 5."),
        ("Is a 0 rating illegal?",
         "No. It means urgent improvement is necessary, but the business may keep trading unless the council issues a hygiene emergency prohibition notice."),
        ("How current is this page?",
         f"The numbers are rebuilt every week from the FSA's open register, and the map and search query it live. A rating changes only when {council} re-inspects."),
    ]
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
        ensure_ascii=False)
    breadcrumb_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Blueroll", "item": "https://blueroll.app/"},
        {"@type": "ListItem", "position": 2, "name": "Food hygiene ratings", "item": "https://blueroll.app/food-hygiene-ratings/"},
        {"@type": "ListItem", "position": 3, "name": f"Food hygiene ratings in {name}"}]}, ensure_ascii=False)
    dataset_ld = json.dumps({"@context": "https://schema.org", "@type": "Dataset",
        "name": f"Food hygiene ratings in {name}",
        "description": f"Weekly aggregate of FHRS food hygiene ratings for {name}, London.",
        "license": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "creator": {"@type": "Organization", "name": "Food Standards Agency"},
        "dateModified": DATA["fetched"]}, ensure_ascii=False)

    s = TEMPLATE
    subs = {
        "{{TITLE}}": title, "{{OG_TITLE}}": og_title, "{{DESC}}": esc(desc).replace("&amp;", "&"),
        "{{SLUG}}": slug, "{{SLUG_U}}": slug.replace("-", "_"), "{{NAME}}": name, "{{COUNCIL}}": council,
        "{{UPDATED}}": UPDATED, "{{TOTAL}}": fmt_n(b["total"]), "{{RATED}}": fmt_n(rated),
        "{{PCT5}}": str(b["pct5"]), "{{LOW}}": fmt_n(b["low"]),
        "{{EXEMPT_NOTE}}": exempt_note, "{{MOVERS_HTML}}": movers_html(b, name, DATA.get("prev_date")),
        "{{WORST_ROWS}}": worst_rows, "{{WORST_NOTE}}": worst_note,
        "{{NEARBY_LINKS}}": nearby, "{{LAID}}": str(cfg["id"]), "{{ANON}}": ANON,
        "{{BBOX}}": json.dumps(b["bbox"]),
        "{{BREADCRUMB_LD}}": breadcrumb_ld, "{{FAQ_LD}}": faq_ld, "{{DATASET_LD}}": dataset_ld,
    }
    for r in "012345":
        subs[f"{{{{C{r}}}}}"] = fmt_n(counts[r])
        subs[f"{{{{W{r}}}}}"] = str(widths[r])
    for k, v in subs.items():
        assert k in s, f"{slug}: placeholder {k} missing from template"
        s = s.replace(k, v)
    assert "{{" not in s, f"{slug}: unfilled placeholder remains: {s[s.index('{{'):s.index('{{')+30]}"
    return s


def build_hub() -> str:
    head, rest = TEMPLATE.split('<div class="wrap">', 1)
    _, footer_on = rest.split("<!-- FOOTER -->", 1)
    footer = "<!-- FOOTER -->" + footer_on.split("<script", 1)[0]

    tot = sum(b["total"] for b in DATA["boroughs"].values())
    rated = sum(b["rated"] for b in DATA["boroughs"].values())
    fives = sum(b["counts"]["5"] for b in DATA["boroughs"].values())
    low = sum(b["low"] for b in DATA["boroughs"].values())
    rows = "".join(
        f'<tr><td><a href="/food-hygiene-ratings/{slug}.html">{esc(link_name(slug))}</a></td>'
        f'<td style="text-align:right">{fmt_n(b["total"])}</td>'
        f'<td style="text-align:right">{b["pct5"]}%</td>'
        f'<td style="text-align:right">{fmt_n(b["low"])}</td></tr>'
        for slug, b in sorted(DATA["boroughs"].items(), key=lambda kv: link_name(kv[0])))

    title = "Food Hygiene Ratings by London Borough: All 33 Compared | Blueroll"
    desc = (f"Food hygiene ratings for all {fmt_n(tot)} registered London food businesses, borough by borough: "
            f"share of 5s, kitchens needing improvement, live maps and weekly updates.")
    head = head.replace("{{TITLE}}", title).replace("{{OG_TITLE}}", "Food Hygiene Ratings by London Borough")
    head = head.replace("{{DESC}}", desc)
    head = head.replace('<link rel="canonical" href="https://blueroll.app/food-hygiene-ratings/{{SLUG}}.html">',
                        '<link rel="canonical" href="https://blueroll.app/food-hygiene-ratings/">')
    head = head.replace('<meta property="og:url" content="https://blueroll.app/food-hygiene-ratings/{{SLUG}}.html">',
                        '<meta property="og:url" content="https://blueroll.app/food-hygiene-ratings/">')
    head = head.replace("{{BREADCRUMB_LD}}", json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Blueroll", "item": "https://blueroll.app/"},
        {"@type": "ListItem", "position": 2, "name": "Food hygiene ratings by London borough"}]}, ensure_ascii=False))
    head = head.replace('<script type="application/ld+json">{{FAQ_LD}}</script>\n', "")
    head = head.replace('<script type="application/ld+json">{{DATASET_LD}}</script>\n', "")
    head = head.replace('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">\n', "")
    head = head.replace('{{SLUG_U}}', 'hub')
    assert "{{" not in head, "hub head has unfilled placeholders"

    body = f'''<div class="wrap">
  <div class="crumbs"><a href="/">Blueroll</a> › Food hygiene ratings</div>
  <div class="label">London · FHRS data</div>
  <h1>Food hygiene ratings by <em>London borough</em></h1>
  <p class="sub">All {fmt_n(tot)} registered food businesses across the 33 boroughs, scored 0 to 5 by council environmental health officers. Pick your borough for the full picture: the numbers, the map, this month's changes and every kitchen rated 0 or 1.</p>
  <div class="updated">Updated {UPDATED} · rebuilt weekly from the FSA register</div>
  <div class="stats">
    <div class="stat"><b>{fmt_n(rated)}</b><span>rated food businesses</span></div>
    <div class="stat"><b>{round(100*fives/rated, 1)}%</b><span>hold the top rating of 5</span></div>
    <div class="stat"><b>{fmt_n(low)}</b><span>rated 0&ndash;2: improvement needed</span></div>
  </div>
  <h2>Pick your borough</h2>
  <div class="tscroll">
  <table class="wt">
    <tr><th>Borough</th><th style="text-align:right">Registered</th><th style="text-align:right">Rated 5</th><th style="text-align:right">Rated 0&ndash;2</th></tr>
    {rows}
  </table>
  </div>
  <p class="note">Share of 5s is calculated over rated establishments only. Exempt and awaiting-inspection businesses are counted in the register totals.</p>
  <div class="rel">
    <strong style="font-size:15px;">More on food hygiene ratings</strong>
    <ul>
      <li><a href="/london-food-hygiene-map.html">Live London food hygiene map: search any restaurant</a></li>
      <li><a href="/food-hygiene-ratings-explained.html">Food hygiene ratings explained: EHO scoring and how to get a 5</a></li>
      <li><a href="/how-to-improve-food-hygiene-rating.html">How to improve your food hygiene rating</a></li>
      <li><a href="/free-haccp-template.html">Free 16-page HACCP pack for UK kitchens</a></li>
    </ul>
  </div>
</div>
'''
    return head + body + footer + "</body>\n</html>\n"


SM_START = "<!-- borough-pages:start -->"
SM_END = "<!-- borough-pages:end -->"


def update_sitemap() -> None:
    p = ROOT / "sitemap.xml"
    s = p.read_text()
    today = date.today().isoformat()
    urls = [f'  <url><loc>https://blueroll.app/food-hygiene-ratings/</loc><lastmod>{today}</lastmod></url>'] + [
        f'  <url><loc>https://blueroll.app/food-hygiene-ratings/{slug}.html</loc><lastmod>{today}</lastmod></url>'
        for slug in sorted(BOROUGHS)]
    block = f"  {SM_START}\n" + "\n".join(urls) + f"\n  {SM_END}"
    if SM_START in s:
        s = re.sub(re.escape("  " + SM_START) + r"[\s\S]*?" + re.escape(SM_END), block, s)
    else:
        s = s.replace("</urlset>", block + "\n</urlset>")
    p.write_text(s)


LLMS_HEADER = "## London borough food hygiene ratings"


def update_llms() -> None:
    p = ROOT / "llms.txt"
    if not p.exists():
        return
    s = p.read_text()
    lines = [f"- [Food hygiene ratings in {BOROUGHS[slug]['name']}](https://blueroll.app/food-hygiene-ratings/{slug}.html)"
             for slug in sorted(BOROUGHS)]
    block = (LLMS_HEADER + "\n"
             + "- [Food hygiene ratings by London borough](https://blueroll.app/food-hygiene-ratings/)\n"
             + "\n".join(lines) + "\n")
    if LLMS_HEADER in s:
        s = re.sub(re.escape(LLMS_HEADER) + r"[\s\S]*?(?=\n## |\Z)", block, s)
    else:
        s = s.rstrip() + "\n\n" + block
    p.write_text(s)


def main() -> None:
    for slug in BOROUGHS:
        (OUT / f"{slug}.html").write_text(build_page(slug))
    (OUT / "index.html").write_text(build_hub())
    update_sitemap()
    update_llms()
    print(f"built {len(BOROUGHS)} borough pages + hub, sitemap and llms.txt updated")


if __name__ == "__main__":
    main()
