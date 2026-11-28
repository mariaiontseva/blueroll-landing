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

EXTRA_CSS = """
td.read { text-align: center; padding: 0; font-family: 'Caveat', cursive; font-size: 14pt; color: #1d3a8a; white-space: nowrap; }
.circ { display: inline-block; border: 1.3px solid #1d3a8a; border-radius: 50%; padding: 0 1.2mm; line-height: 1.1; }
.ref { display: grid; grid-template-columns: 1fr 1fr; column-gap: 9mm; margin-top: 2mm; font-size: 8.5pt; }
.ref div { display: flex; justify-content: space-between; gap: 3mm; border-bottom: 1px solid #d9dedb; padding: 1.3mm 0; }
.ref b { font-weight: 600; }
"""

E, DAYS = B.E, B.DAYS
MINUS = "−"
M = MINUS


def weekly(title, lead, units, extra_rows, filled, top, notes, sign, rule_note, name, example, widths):
    th = (f'<tr><th style="width:{widths[0]}%">Unit</th><th style="width:{widths[1]}%">Target</th>' + B.day_heads() + '</tr>')
    rows = []
    for i, (unit, target) in enumerate(units + extra_rows):
        vals = (filled[i] + [""] * (7 - len(filled[i]))) if example else [""] * 7
        rows.append(f'<tr class="w"><td class="item">{unit}</td><td class="sub">{target}</td>'
                    + "".join(f'<td class="read v">{v}</td>' for v in vals) + '</tr>')
    table = f'<table><thead>{th}</thead><tbody>{"".join(rows)}</tbody></table>'
    return B.page(B.head(title, lead), top, B.grow(table), f'<p class="note">{rule_note}</p>', notes, sign, B.foot(name))


def circ(bad, good):
    return f'<span style="font-size:12.5pt"><span class="circ">{bad}</span> &rarr; {good}</span>'


# ---------------------------------------------------------------- UK (A4, C)

UK_NAME = "fridge temperature log"

UK_UNITS = [
    ("Fridge 1 &middot; AM", "5&deg;C or below"), ("Fridge 1 &middot; PM", "5&deg;C or below"),
    ("Fridge 2 &middot; AM", "5&deg;C or below"), ("Fridge 2 &middot; PM", "5&deg;C or below"),
    ("Fridge 3 &middot; AM", "5&deg;C or below"), ("Fridge 3 &middot; PM", "5&deg;C or below"),
    ("Display chiller &middot; AM", "5&deg;C or below"), ("Display chiller &middot; PM", "5&deg;C or below"),
    ("Cold room &middot; AM", "5&deg;C or below"), ("Cold room &middot; PM", "5&deg;C or below"),
    ("Freezer 1", f"{MINUS}18&deg;C or below"), ("Freezer 2", f"{MINUS}18&deg;C or below"),
]
UK_EXTRA = [("Probe check (ice water)", f"0&deg;C, {MINUS}1 to +1"), ("Initials &middot; AM", ""), ("Initials &middot; PM", "")]
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


def uk_weekly(example):
    if example:
        lead = ("Filled example from St James's Cafe, up to Thursday. "
                "The out-of-range reading is circled, put right and rechecked.")
        top = B.fields(("Week starting", "Mon 16 Nov 2026"), ("Business", "St James's Cafe"))
        notes = B.write("Out-of-range readings and what you did", 2,
                        "Wed 16:10 - Fridge 2 at 7.6&deg;C after the dairy delivery went in with the door propped open. "
                        "Door shut, food probed at 4.8&deg;C, rechecked 16:40: 4.2&deg;C - PK.")
        sign = B.fields(("Checked by (manager)", "SR"), ("Date", "Thu 19 Nov 2026"))
    else:
        lead = ("Read at opening and before close, from the display or a probe in water in the unit. "
                "Write the number, not a tick.")
        top = B.fields(("Week starting", ""), ("Business", ""))
        notes = B.write("Out-of-range readings and what you did", 2)
        sign = B.fields(("Checked by (manager)", ""), ("Date", ""))
    return weekly("Fridge temperature log", lead, UK_UNITS, UK_EXTRA, UK_FILLED, top, notes, sign, UK_RULE,
                  UK_NAME, example, (24, 15))


def probe_page(title, lead, cook_cols, cool_title, cool_cols, cool_rows, ref_title, ref, ref_note, name, labels):
    def heads(cols):
        return "<tr>" + "".join(
            f'<th class="{"v " if i else ""}{"c" if c else ""}"{f" style=width:{w}" if w else ""}>{t}</th>'
            for i, (t, w, c) in enumerate(cols)) + "</tr>"

    def blank(cols, cls=""):
        return f'<tr{cls}><td class="hand"></td>' + '<td class="hand v"></td>' * (len(cols) - 1) + '</tr>'

    cook = f'<table><thead>{heads(cook_cols)}</thead><tbody>{blank(cook_cols, " class=w")}</tbody></table>'
    cool = (f'<table><thead>{heads(cool_cols)}</thead><tbody>{blank(cool_cols) * cool_rows}</tbody></table>')
    refs = "".join(f'<div><span>{a}</span><b>{b}</b></div>' for a, b in ref)
    return B.page(B.head(title, lead), B.fields(*labels), B.grow(cook, extend=True),
                  f'<h2>{cool_title}</h2>', f'<div class="fixed" style="margin-top:2.5mm">{cool}</div>',
                  f'<h2>{ref_title}</h2>', f'<div class="ref">{refs}</div>',
                  f'<p class="note">{ref_note}</p>', B.foot(name))


def uk_probe():
    return probe_page(
        "Cooking, cooling and hot-holding log",
        "Probe the thickest part of the food. Write the temperature, the time, and what you did if it was not safe.",
        [("Date", "10%", False), ("Food", "22%", False), ("Check", "14%", False), ("Time", "", True),
         ("Temp &deg;C", "", True), ("OK?", "7%", True), ("If not OK, what you did", "23%", False),
         ("Initials", "", True)],
        "Cooling: cooked food going into the fridge",
        [("Date", "10%", False), ("Food", "28%", False), ("Out of the oven", "", True), ("Into the fridge", "", True),
         ("Temp going in", "", True), ("Initials", "", True)], 5,
        "Safe temperatures (UK)",
        [("Fridges", "5&deg;C or below (legal limit 8&deg;C)"), ("Freezers", f"{MINUS}18&deg;C or below"),
         ("Cooking (core)", "75&deg;C, or 70&deg;C for 2 min"), ("Hot holding", "63&deg;C or above"),
         ("Reheating", "75&deg;C (82&deg;C in Scotland)"), ("Cooling", "into the fridge within 90 min"),
         ("Probe check, ice water", f"0&deg;C ({MINUS}1 to +1)"), ("Probe check, boiling water", "100&deg;C (99 to 101)")],
        "Check is cook, hot hold or reheat. 8&deg;C for fridges is the legal limit in England, Wales and Northern Ireland. "
        "63&deg;C for hot holding is the legal minimum across the UK, and Scotland also requires reheating to 82&deg;C.",
        UK_NAME, (("Week starting", ""), ("Business", "")))


# ---------------------------------------------------------------- US (Letter, F)

US_NAME = "food temperature log"

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


def us_weekly(example):
    if example:
        lead = ("Filled example from Main Street Diner, a sample restaurant. "
                "The out-of-range reading is circled, fixed and rechecked.")
        top = B.fields(("Week of", "Mon, Nov 16, 2026"), ("Restaurant", "Main Street Diner"))
        notes = B.write("Out-of-range readings and what you did", 2,
                        "Wed 3:15 pm - prep-line cooler at 45&deg;F, lids left open through the lunch rush. Lids closed, "
                        "pans probed at 40&deg;F, rechecked 3:45 pm: 39&deg;F - JM.")
        sign = B.fields(("Manager sign-off", "DL"), ("Date", "Thu, Nov 19, 2026"))
    else:
        lead = "Take readings at opening and before close. Write the number, not a check mark."
        top = B.fields(("Week of", ""), ("Restaurant", ""))
        notes = B.write("Out-of-range readings and what you did", 2)
        sign = B.fields(("Manager sign-off", ""), ("Date", ""))
    return weekly("Cooler and freezer temperature log", lead, US_UNITS, US_EXTRA, US_FILLED, top, notes, sign,
                  US_RULE, US_NAME, example, (28, 14))


def us_probe():
    return probe_page(
        "Food temperature log",
        "Probe the thickest part of the food. Write the temperature, the time, and what you did if it was not safe.",
        [("Date", "10%", False), ("Food", "22%", False), ("Check", "14%", False), ("Time", "", True),
         ("Temp &deg;F", "", True), ("OK?", "7%", True), ("If not OK, what you did", "23%", False),
         ("Initials", "", True)],
        "Cooling log: 135&deg;F to 70&deg;F in 2 hours, to 41&deg;F within 6 hours total",
        [("Date", "10%", False), ("Food", "26%", False), ("Start time &amp; temp", "", True), ("2-hour check", "", True),
         ("6-hour check", "", True), ("Initials", "", True)], 5,
        "FDA Food Code temperatures",
        [("Poultry, stuffed foods", "165&deg;F, &lt;1 sec"), ("Ground beef and pork", "155&deg;F, 17 sec"),
         ("Steaks, chops, fish, eggs", "145&deg;F, 15 sec"), ("Reheating for hot holding", "165&deg;F, 15 sec, within 2 hrs"),
         ("Hot holding", "135&deg;F or above"), ("Cold holding", "41&deg;F or below"),
         ("Cooling", "135&rarr;70&deg;F in 2 hrs, 41&deg;F in 6"), ("Thermometer check", "32&deg;F ice water, &plusmn;2&deg;F")],
        "Check is cook, hot hold, reheat or cold hold. Your state or county may have adopted a different Food Code edition; "
        "your local health code comes first.",
        US_NAME, (("Week of", ""), ("Restaurant", "")))


def main():
    root = B.ROOT
    uk = root / "blueroll-fridge-temperature-log.pdf"
    B.render([uk_weekly(False), uk_weekly(True), uk_probe()], "A4", "210mm", "297mm", uk,
             "Fridge temperature log (UK) | Blueroll", extra_css=EXTRA_CSS)
    us = root / "blueroll-food-temperature-log.pdf"
    B.render([us_weekly(False), us_weekly(True), us_probe()], "letter", "8.5in", "11in", us,
             "Food temperature log (US) | Blueroll", lang="en-US", pad=B.US_PAD, extra_css=EXTRA_CSS)
    B.previews(uk, "temperature-uk-page")
    B.previews(us, "temperature-us-page")


if __name__ == "__main__":
    main()
