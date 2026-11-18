#!/usr/bin/env python3
"""Build the two free temperature-log PDFs and their page previews.

  blueroll-fridge-temperature-log.pdf  UK, A4, degrees C: weekly fridge/freezer log, filled example, cooking/cooling log
  blueroll-food-temperature-log.pdf    US, Letter, degrees F: weekly cooler/freezer log, filled example, cooking/cooling log

Same look and helpers as _build/build_cleaning_pdfs.py. Run from the repo root:

    python3 _build/build_temperature_pdfs.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_cleaning_pdfs as B  # noqa: E402

B.CSS += """
td.read { border-left: 1px solid #e3e6e4; text-align: center; font-family: 'Caveat', cursive; font-size: 12.5pt; color: #1d3a8a; padding: 0; white-space: nowrap; }
td.tgt { color: #1f5e40; font-size: 6.8pt; font-weight: 600; }
.circ { display: inline-block; border: 1.3px solid #1d3a8a; border-radius: 50%%; padding: 0 1.2mm; line-height: 1.1; }
.ref { display: grid; grid-template-columns: 1fr 1fr; gap: 1mm 6mm; }
.ref div { display: flex; justify-content: space-between; gap: 3mm; border-bottom: 1px dotted #c9d6ce; padding: .9mm 0; }
.ref b { color: #16181d; }
table.wk { table-layout: fixed; }
h3.tt { font-size: 6.2pt; letter-spacing: .16em; color: #1f7a52; text-transform: uppercase; margin: 5mm 0 0; font-weight: 700; border-bottom: 1px solid #1f9d63; padding-bottom: 1.4mm; }
"""

E, DAYS = B.E, B.DAYS
MINUS = "−"


def weekly(title, units, extra_rows, filled, intro, top, notes, sign, rule_note, foot_l, foot_r, example):
    th = ('<tr><th style="width:24%">Unit</th><th style="width:12%">Target</th>'
          + "".join(f'<th class="c">{d}</th>' for d in DAYS) + '</tr>')
    rows = []
    for i, (unit, target) in enumerate(units + extra_rows):
        vals = (filled[i] + [""] * (7 - len(filled[i]))) if example else [""] * 7
        rows.append(f'<tr><td class="item">{unit}</td><td class="tgt">{target}</td>'
                    + "".join(f'<td class="read">{v}</td>' for v in vals) + '</tr>')
    return ('<section class="page">' + B.head(title, "Sheet 2" if example else "Sheet 1", example)
            + f'<p class="intro">{intro}</p>' + top
            + f'<table class="wk"><thead>{th}</thead><tbody>{"".join(rows)}</tbody></table>'
            + f'<p class="note">{rule_note}</p>' + notes + sign + B.foot(foot_l, foot_r) + '</section>')


def circ(bad, good):
    return f'<span style="font-size:10.5pt"><span class="circ">{bad}</span> &rarr; {good}</span>'


# ---------------------------------------------------------------- UK (A4, C)

UK_UNITS = [
    ("Fridge 1 &middot; AM", "5&deg;C or below"), ("Fridge 1 &middot; PM", "5&deg;C or below"),
    ("Fridge 2 &middot; AM", "5&deg;C or below"), ("Fridge 2 &middot; PM", "5&deg;C or below"),
    ("Fridge 3 &middot; AM", "5&deg;C or below"), ("Fridge 3 &middot; PM", "5&deg;C or below"),
    ("Display chiller &middot; AM", "5&deg;C or below"), ("Display chiller &middot; PM", "5&deg;C or below"),
    ("Cold room &middot; AM", "5&deg;C or below"), ("Cold room &middot; PM", "5&deg;C or below"),
    ("Freezer 1", f"{MINUS}18&deg;C or below"), ("Freezer 2", f"{MINUS}18&deg;C or below"),
]
UK_EXTRA = [("Probe check (ice water)", f"0&deg;C, {MINUS}1 to +1"), ("Initials &middot; AM", ""), ("Initials &middot; PM", "")]
M = MINUS
UK_FILLED = [
    ["3.2", "3.4", "3.1", "3.3"], ["3.9", "4.1", "3.8", "4.0"],
    ["4.0", "4.2", "3.9", "4.1"], ["4.4", "4.3", circ("7.6", "4.2"), "4.5"],
    ["2.8", "3.0", "2.9", "3.1"], ["3.5", "3.6", "3.4", "3.7"],
    ["4.1", "4.3", "4.0", "4.2"], ["4.8", "4.6", "4.7", "4.9"],
    ["2.9", "3.1", "3.0", "3.2"], ["3.6", "3.8", "3.5", "3.9"],
    [f"{M}18.4", f"{M}18.6", f"{M}18.2", f"{M}18.5"], [f"{M}19.0", f"{M}18.8", f"{M}19.1", f"{M}18.9"],
    ["0.2 &#10003;"], ["TA", "PK", "TA", "SR"], ["SR", "SR", "PK", "TA"],
]
UK_RULE = ("<b>Fridges:</b> 5&deg;C or below is the target; 8&deg;C is the legal limit in England, Wales and Northern Ireland. "
           f"<b>Freezers:</b> {MINUS}18&deg;C or below. Circle any reading out of range, write what you did below, and recheck.")
UK_FOOT = ("Blueroll &middot; Free fridge temperature log &middot; UK", "This log fills itself in Blueroll &middot; blueroll.app")


def uk_weekly(example):
    if example:
        intro = ("St James's Cafe, week of Monday 16 November 2026, filled in up to Thursday. The out-of-range reading "
                 "is circled, put right and rechecked, not hidden.")
        top = B.fields("Week starting", "Mon 16 Nov 2026", "Business", "St James's Cafe")
        notes = ('<div class="box"><h4>Out-of-range readings and what you did</h4><div class="hand">'
                 'Wed 16:10 - Fridge 2 at 7.6&deg;C after the dairy delivery went in with the door propped open. '
                 'Door shut, food probed at 4.8&deg;C, rechecked 16:40: 4.2&deg;C - PK.</div></div>')
        sign = B.fields("Checked by (manager)", "Sam R.", "Date", "Thu 19 Nov 2026")
    else:
        intro = ("Take readings at opening and before close, from the display or a probe in a glass of water kept in the unit. "
                 "Write the number, not a tick. Rename the units to match your kitchen.")
        top = B.fields("Week starting", "", "Business", "")
        notes = ('<div class="box"><h4>Out-of-range readings and what you did</h4>'
                 '<div class="rule"></div><div class="rule"></div></div>')
        sign = B.fields("Checked by (manager)", "", "Date", "")
    return weekly("Fridge temperature log", UK_UNITS, UK_EXTRA, UK_FILLED, intro, top, notes, sign, UK_RULE,
                  *UK_FOOT, example)


def probe_page(title, intro, cook_cols, cook_rows, cool_title, cool_cols, cool_rows, ref_title, ref, ref_note, foot,
               labels=("Week starting", "", "Business", "")):
    th = "<tr>" + "".join(f'<th{" class=c" if c else ""}{f" style=width:{w}" if w else ""}>{t}</th>' for t, w, c in cook_cols) + "</tr>"
    body = "".join("<tr>" + '<td class="hand"></td>' * len(cook_cols) + "</tr>" for _ in range(cook_rows))
    th2 = "<tr>" + "".join(f'<th{" class=c" if c else ""}{f" style=width:{w}" if w else ""}>{t}</th>' for t, w, c in cool_cols) + "</tr>"
    body2 = "".join("<tr>" + '<td class="hand"></td>' * len(cool_cols) + "</tr>" for _ in range(cool_rows))
    refs = "".join(f'<div><span>{a}</span><b>{b}</b></div>' for a, b in ref)
    return ('<section class="page">' + B.head(title, "Sheet 3")
            + f'<p class="intro">{intro}</p>' + B.fields(*labels)
            + f'<table><thead>{th}</thead><tbody>{body}</tbody></table>'
            + f'<h3 class="tt">{cool_title}</h3>'
            + f'<table style="margin-top:2.5mm"><thead>{th2}</thead><tbody>{body2}</tbody></table>'
            + f'<div class="card"><h4>{ref_title}</h4><div class="ref">{refs}</div>'
            + f'<p style="margin:2mm 0 0;">{ref_note}</p></div>'
            + B.foot(*foot) + '</section>')


def uk_probe():
    return probe_page(
        "Cooking, cooling &amp; hot-holding log".replace("&amp;", "&"),
        "Probe the thickest part of the food. Write the temperature you read, the time, and what you did if it was not safe.",
        [("Date", "9%", False), ("Food", "24%", False), ("Check", "15%", False), ("Time", "", True), ("Temp &deg;C", "", True),
         ("OK?", "", True), ("If not OK, what you did", "24%", False), ("Initials", "", True)], 11,
        "Cooling: cooked food going into the fridge",
        [("Date", "9%", False), ("Food", "27%", False), ("Out of the oven", "", True), ("Into the fridge", "", True),
         ("Temp going in", "", True), ("Initials", "", True)], 5,
        "Safe temperatures (UK)",
        [("Fridges", "5&deg;C or below (legal limit 8&deg;C)"), ("Freezers", f"{MINUS}18&deg;C or below"),
         ("Cooking (core)", "75&deg;C, or 70&deg;C for 2 min"), ("Hot holding", "63&deg;C or above"),
         ("Reheating", "75&deg;C (82&deg;C in Scotland)"), ("Cooling", "into the fridge within 90 min"),
         ("Probe check, ice water", f"0&deg;C ({MINUS}1 to +1)"), ("Probe check, boiling water", "100&deg;C (99 to 101)")],
        "Check is cook, hot hold or reheat. 8&deg;C for fridges is the legal limit in England, Wales and Northern Ireland. "
        "63&deg;C for hot holding is the legal minimum across the UK, and Scotland also requires reheating to 82&deg;C.",
        UK_FOOT)


# ---------------------------------------------------------------- US (Letter, F)

US_UNITS = [
    ("Walk-in cooler &middot; AM", "41&deg;F or below"), ("Walk-in cooler &middot; PM", "41&deg;F or below"),
    ("Reach-in 1 &middot; AM", "41&deg;F or below"), ("Reach-in 1 &middot; PM", "41&deg;F or below"),
    ("Reach-in 2 &middot; AM", "41&deg;F or below"), ("Reach-in 2 &middot; PM", "41&deg;F or below"),
    ("Prep-line cooler &middot; AM", "41&deg;F or below"), ("Prep-line cooler &middot; PM", "41&deg;F or below"),
    ("Walk-in freezer &middot; AM", "0&deg;F or below"), ("Walk-in freezer &middot; PM", "0&deg;F or below"),
    ("Reach-in freezer", "0&deg;F or below"),
]
US_EXTRA = [("Thermometer check (ice water)", "32&deg;F, &plusmn;2"), ("Initials &middot; AM", ""), ("Initials &middot; PM", "")]
US_FILLED = [
    ["37", "38", "36", "37"], ["39", "40", "38", "39"],
    ["36", "37", "37", "36"], ["38", "39", "38", "38"],
    ["35", "36", "35", "36"], ["37", "38", "37", "37"],
    ["38", "38", "37", "38"], ["40", "39", circ("45", "39"), "40"],
    [f"{M}2", f"{M}1", f"{M}3", f"{M}2"], [f"{M}1", "0", f"{M}2", f"{M}1"],
    [f"{M}1", f"{M}2", "0", f"{M}1"],
    ["32 &#10003;"], ["DL", "JM", "DL", "RC"], ["JM", "RC", "JM", "JM"],
]
US_RULE = ("<b>Cold holding:</b> 41&deg;F or below (FDA Food Code). <b>Freezers:</b> 0&deg;F or below is the usual target. "
           "Circle any reading out of range, write what you did below, and recheck.")
US_FOOT = ("Blueroll &middot; Free food temperature log &middot; US", "Based on the FDA Food Code. Your local health code may add to it.")


def us_weekly(example):
    if example:
        intro = ("Main Street Diner (a sample restaurant), week of Monday, November 16, 2026, filled in up to Thursday. "
                 "The out-of-range reading is circled, fixed and rechecked, not hidden.")
        top = B.fields("Week of", "Mon, Nov 16, 2026", "Restaurant", "Main Street Diner")
        notes = ('<div class="box"><h4>Out-of-range readings and what you did</h4><div class="hand">'
                 'Wed 3:15 pm - prep-line cooler at 45&deg;F, lids left open through the lunch rush. Lids closed, '
                 'pans probed at 40&deg;F, rechecked 3:45 pm: 39&deg;F - JM.</div></div>')
        sign = B.fields("Manager sign-off", "Dana L.", "Date", "Thu, Nov 19, 2026")
    else:
        intro = ("Take readings at opening and before close. Write the number, not a check mark. "
                 "Rename the units to match your kitchen.")
        top = B.fields("Week of", "", "Restaurant", "")
        notes = ('<div class="box"><h4>Out-of-range readings and what you did</h4>'
                 '<div class="rule"></div><div class="rule"></div></div>')
        sign = B.fields("Manager sign-off", "", "Date", "")
    return weekly("Cooler &amp; freezer temperature log".replace("&amp;", "&"), US_UNITS, US_EXTRA, US_FILLED,
                  intro, top, notes, sign, US_RULE, "Blueroll &middot; Free food temperature log &middot; US",
                  "This log fills itself in Blueroll &middot; blueroll.app", example)


def us_probe():
    return probe_page(
        "Food temperature log",
        "Probe the thickest part of the food. Write the temperature you read, the time, and what you did if it was not safe.",
        [("Date", "9%", False), ("Food", "24%", False), ("Check", "15%", False), ("Time", "", True), ("Temp &deg;F", "", True),
         ("OK?", "", True), ("If not OK, what you did", "24%", False), ("Initials", "", True)], 10,
        "Cooling log: 135&deg;F to 70&deg;F in 2 hours, to 41&deg;F within 6 hours total",
        [("Date", "9%", False), ("Food", "25%", False), ("Start time &amp; temp", "", True), ("2-hour check", "", True),
         ("6-hour check", "", True), ("Initials", "", True)], 5,
        "FDA Food Code temperatures",
        [("Poultry, stuffed foods", "165&deg;F, &lt;1 sec"), ("Ground beef and pork", "155&deg;F, 17 sec"),
         ("Steaks, chops, fish, eggs", "145&deg;F, 15 sec"), ("Reheating for hot holding", "165&deg;F, 15 sec, within 2 hrs"),
         ("Hot holding", "135&deg;F or above"), ("Cold holding", "41&deg;F or below"),
         ("Cooling", "135&rarr;70&deg;F in 2 hrs, 41&deg;F in 6"), ("Thermometer check", "32&deg;F ice water, &plusmn;2&deg;F")],
        "Check is cook, hot hold, reheat or cold hold. Your state or county may have adopted a different Food Code edition; "
        "your local health code comes first.",
        US_FOOT, ("Week of", "", "Restaurant", ""))


def main():
    root = B.ROOT
    uk = root / "blueroll-fridge-temperature-log.pdf"
    B.render([uk_weekly(False), uk_weekly(True), uk_probe()], "A4", "210mm", "297mm", "8.4mm", uk,
             "Fridge temperature log (UK) | Blueroll")
    us = root / "blueroll-food-temperature-log.pdf"
    B.render([us_weekly(False), us_weekly(True), us_probe()], "letter", "8.5in", "11in", "8.2mm", us,
             "Food temperature log (US) | Blueroll")
    B.previews(uk, "temperature-uk-page")
    B.previews(us, "temperature-us-page")


if __name__ == "__main__":
    main()
