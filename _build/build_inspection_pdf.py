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

EXTRA_CSS = """
td.yn { text-align: center; padding: 0; font-family: 'Caveat', cursive; font-size: 14pt; line-height: 1; color: #1d3a8a; }
td.num { color: #5c626b; font-size: 8pt; text-align: right; padding: 0 1.5mm 0 0; }
td.chk { font-size: 8.5pt; font-weight: 500; padding-top: .6mm; padding-bottom: .6mm; }
td.fix { font-family: 'Caveat', cursive; font-size: 11.5pt; line-height: 1; color: #1d3a8a; padding-top: .4mm; padding-bottom: .4mm; }
table.chkl td { height: 6.2mm; }
table.chkl tr.sec td { height: 6mm; }
.ref2 { margin-top: 2mm; font-size: 8.5pt; }
.ref2 div { display: grid; grid-template-columns: 38mm 1fr; gap: 3mm; border-bottom: 1px solid #d9dedb; padding: 1.3mm 0; }
.ref2 b { font-weight: 600; }
"""
NAME = "restaurant health inspection checklist"
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
    th = ('<tr><th style="width:4%"></th><th style="width:61%">Check</th><th class="c v" style="width:6%">Yes</th>'
          '<th class="c v" style="width:6%">No</th><th class="v">If no: fix, who, by when</th></tr>')
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
        rows.append(f'<tr class="w"><td class="num">{n}</td><td class="chk">{it[0]}</td>'
                    f'<td class="yn v">{yes}</td><td class="yn v">{no}</td><td class="fix v">{fix}</td></tr>')
    table = f'<table class="chkl"><thead>{th}</thead><tbody>{"".join(rows)}</tbody></table>'
    if example:
        lead = ("Filled example from Main Street Diner, a sample restaurant, at lunch. "
                "21 of 24 yes; each no has a fix, an owner and a date.")
        top = B.fields(("Date and time", "Thu, Nov 19, 2026, 12:40 pm"), ("Done by", "DL, manager"))
    else:
        lead = "Walk it as an inspector does: handwashing sink, coolers, hot line, prep, dish area, storage, restrooms."
        top = B.fields(("Date and time", ""), ("Done by", ""))
    score = ('<p class="note"><b>Score:</b> count the yes answers out of 24. Fix the first four sections first: they match '
             'the FDA&rsquo;s five risk factors for foodborne illness and usually cost the most points.</p>')
    return B.page(B.head("Restaurant self-inspection checklist", lead), top, B.grow(table), score, B.foot(NAME))


def log_page() -> str:
    th = ('<tr><th style="width:13%">Date</th><th class="v" style="width:29%">What was wrong</th>'
          '<th class="v" style="width:29%">What you did</th><th class="v">Who</th><th class="v">Checked</th></tr>')
    row = '<tr class="w"><td class="hand"></td>' + '<td class="hand v"></td>' * 4 + '</tr>'
    cities = [
        ("New York City", "Letter grade from violation points: A is 0-13, B is 14-27, C is 28 or more."),
        ("Los Angeles County", "Letter grade from a score out of 100: A is 90-100, B is 80-89, C is 70-79."),
        ("San Francisco", "A score out of 100."),
        ("Chicago", "Pass, Pass with Conditions, or Fail."),
        ("Seattle / King County", "Placard: Excellent, Good, Okay, or Needs to Improve."),
    ]
    ref = "".join(f'<div><b>{a}</b><span>{b}</span></div>' for a, b in cities)
    lead = "Everything a self-inspection or a real inspection found, what you did, and who checked that the fix held."
    return B.page(B.head("Corrective action log", lead), B.fields(("Month", ""), ("Restaurant", "")),
                  B.grow(f'<table><thead>{th}</thead><tbody>{row}</tbody></table>', extend=True),
                  '<h2>How your city scores</h2>', f'<div class="ref2">{ref}</div>',
                  '<p class="note">The FDA&rsquo;s five risk factors come first everywhere: food from unsafe sources, '
                  'inadequate cooking, improper holding temperatures, contaminated equipment and poor personal hygiene. '
                  'Your city or county code may add to the FDA Food Code.</p>',
                  B.foot(NAME))


def main():
    out = B.ROOT / "blueroll-restaurant-health-inspection-checklist.pdf"
    B.render([checklist(False), checklist(True), log_page()], "letter", "8.5in", "11in", out,
             "Restaurant health inspection checklist (US) | Blueroll", lang="en-US", pad=B.US_PAD, extra_css=EXTRA_CSS)
    B.previews(out, "inspection-us-page")


if __name__ == "__main__":
    main()
