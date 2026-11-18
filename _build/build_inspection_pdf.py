#!/usr/bin/env python3
"""Build the free US restaurant health inspection checklist PDF and its previews.

  blueroll-restaurant-health-inspection-checklist.pdf  US Letter: 24-point self-inspection,
  filled example, corrective action log with how five cities score.

Same look and helpers as _build/build_cleaning_pdfs.py. Run from the repo root:

    python3 _build/build_inspection_pdf.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_cleaning_pdfs as B  # noqa: E402

B.CSS += """
td.yn { border-left: 1px solid #e3e6e4; text-align: center; width: 9mm; font-family: 'Caveat', cursive; font-size: 13pt; color: #1d3a8a; padding: 0; }
td.num { color: #9aa0a8; font-size: 6.8pt; width: 6mm; text-align: right; padding-right: 1mm; }
.ref2 div { display: grid; grid-template-columns: 34mm 1fr; gap: 3mm; border-bottom: 1px dotted #c9d6ce; padding: 1mm 0; }
.ref2 b { color: #16181d; }
"""
E = B.E

ITEMS = [
    ("sec", "Food temperatures"),
    ("Cold-held TCS food at 41&deg;F or below (probe 3 items in each cooler)",),
    ("Hot-held food at 135&deg;F or above",),
    ("Cooling log in use: 135&deg;F to 70&deg;F in 2 hrs, 41&deg;F within 6",),
    ("Probe thermometer on hand and checked this week in ice water (32&deg;F)",),
    ("sec", "Handwashing and staff"),
    ("Handwashing sinks stocked, not blocked, used only for handwashing",),
    ("No bare-hand contact with ready-to-eat food (gloves, tongs, deli paper)",),
    ("Staff know to report vomiting, diarrhea or jaundice; ill-worker policy signed",),
    ("Hair restraints on; staff drinks covered and away from prep areas",),
    ("sec", "Storage and sources"),
    ("Raw meat stored below ready-to-eat food, poultry on the lowest shelf",),
    ("Ready-to-eat TCS food kept over 24 hrs is date-marked, used within 7 days",),
    ("Food from approved suppliers; invoices kept; shellfish tags kept 90 days",),
    ("Food covered, labeled and stored at least 6 inches off the floor",),
    ("sec", "Cleaning and sanitizing"),
    ("Sanitizer at the right strength in buckets and the dish machine (test strips)",),
    ("Wiping cloths kept in sanitizer between uses",),
    ("Food-contact surfaces cleaned and sanitized at least every 4 hrs in use",),
    ("Ice machine and soda nozzles clean, no mold or slime",),
    ("sec", "Pests and facility"),
    ("No signs of pests; latest pest control report on file",),
    ("Outer doors close tight; door sweeps and screens intact",),
    ("Trash lids closed; dumpster area clean",),
    ("Restrooms clean and stocked; doors self-closing",),
    ("sec", "Paperwork and allergens"),
    ("Certified Food Protection Manager on staff; certificate on site",),
    ("Health permit and latest grade or placard posted where guests can see it",),
    ("Consumer advisory on the menu for raw or undercooked items",),
    ("Staff trained in food allergy awareness; allergens known for every dish",),
]

# Main Street Diner, Thu Nov 19, 2026. Three "no" answers with fixes.
FILLED_NO = {
    4: "Calibrated 2:10 pm, reads 32&deg;F - JM",
    10: "2 rice pans undated, labeled now - DL",
    18: "Back door sweep worn, fit by Mon - RC",
}


def checklist(example: bool) -> str:
    th = ('<tr><th style="width:5%"></th><th style="width:55%">Check</th><th class="c">Yes</th><th class="c">No</th>'
          '<th style="width:28%">If no: fix, who, by when</th></tr>')
    rows, n = [], 0
    for it in ITEMS:
        if it[0] == "sec":
            rows.append(f'<tr class="sec"><td colspan="5">{it[1]}</td></tr>')
            continue
        n += 1
        yes = no = fix = ""
        if example:
            if n in FILLED_NO:
                no, fix = "&#10007;", FILLED_NO[n]
            else:
                yes = "&#10003;"
        rows.append(f'<tr><td class="num">{n}</td><td class="item" style="font-weight:500">{it[0]}</td>'
                    f'<td class="yn">{yes}</td><td class="yn">{no}</td>'
                    f'<td class="hand" style="font-size:10.5pt;white-space:nowrap">{fix}</td></tr>')
    if example:
        intro = ("Main Street Diner (a sample restaurant), self-inspection on Thursday, November 19, 2026, during lunch. "
                 "21 of 24 yes. Each no has a fix, an owner and a date.")
        top = B.fields("Date and time", "Thu, Nov 19, 2026, 12:40 pm", "Done by", "Dana L., manager")
    else:
        intro = ("Walk the kitchen in the order an inspector does: handwashing sink, coolers, hot line, prep, dish area, "
                 "storage, restrooms. Mark every line yes or no; for every no, write the fix.")
        top = B.fields("Date and time", "", "Done by", "")
    return ('<section class="page">' + B.head("Restaurant self-inspection checklist", "Sheet 2" if example else "Sheet 1", example)
            + f'<p class="intro">{intro}</p>' + top
            + f'<table><thead>{th}</thead><tbody>{"".join(rows)}</tbody></table>'
            + '<p class="note"><b>Score:</b> count the yes answers out of 24. Fix the first four sections first: they match '
              'the FDA&rsquo;s five risk factors for foodborne illness and usually cost the most points.</p>'
            + B.foot("Blueroll &middot; Free restaurant health inspection checklist &middot; US",
                     "This checklist fills itself in Blueroll &middot; blueroll.app")
            + '</section>')


def log_page() -> str:
    th = ('<tr><th style="width:10%">Date</th><th style="width:30%">What was wrong</th><th style="width:30%">What you did</th>'
          '<th class="c">Who</th><th class="c">Checked</th></tr>')
    rows = "".join("<tr>" + '<td class="hand"></td>' * 5 + "</tr>" for _ in range(11))
    cities = [
        ("New York City", "Letter grade from violation points: A is 0-13, B is 14-27, C is 28 or more."),
        ("Los Angeles County", "Letter grade from a score out of 100: A is 90-100, B is 80-89, C is 70-79."),
        ("San Francisco", "A score out of 100."),
        ("Chicago", "Pass, Pass with Conditions, or Fail."),
        ("Seattle / King County", "Placard: Excellent, Good, Okay, or Needs to Improve."),
    ]
    ref = "".join(f'<div><b>{a}</b><span>{b}</span></div>' for a, b in cities)
    return ('<section class="page">' + B.head("Corrective action log", "Sheet 3")
            + '<p class="intro">Everything your self-inspection or a real inspection found, what you did about it, '
              'and who checked that the fix held. Inspectors read a log like this as proof you act on problems.</p>'
            + B.fields("Month", "", "Restaurant", "")
            + f'<table><thead>{th}</thead><tbody>{rows}</tbody></table>'
            + f'<div class="card"><h4>How your city scores</h4><div class="ref2">{ref}</div>'
            + '<p style="margin:2mm 0 0;">The FDA&rsquo;s five risk factors come first everywhere: food from unsafe sources, '
              'inadequate cooking, improper holding temperatures, contaminated equipment and poor personal hygiene. '
              'Your city or county code may add to the FDA Food Code.</p></div>'
            + B.foot("Blueroll &middot; Free restaurant health inspection checklist &middot; US",
                     "Based on the FDA Food Code. Your local health code may add to it.")
            + '</section>')


def main():
    out = B.ROOT / "blueroll-restaurant-health-inspection-checklist.pdf"
    B.render([checklist(False), checklist(True), log_page()], "letter", "8.5in", "11in", "6.5mm", out,
             "Restaurant health inspection checklist (US) | Blueroll")
    B.previews(out, "inspection-us-page")


if __name__ == "__main__":
    main()
