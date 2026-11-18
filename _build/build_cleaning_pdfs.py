#!/usr/bin/env python3
"""Build the two free cleaning PDFs and their page previews.

  blueroll-kitchen-cleaning-schedule.pdf    UK, A4: weekly schedule, filled example, monthly + deep-clean log
  blueroll-restaurant-cleaning-checklist.pdf US, Letter: daily checklist, filled example, weekly/monthly + sanitizer log

Same look as the 16-page HACCP pack (dark green table heads, filled example in
handwriting). HTML is rendered with headless Chrome, previews with pdftoppm.
Run from the repo root:

    python3 _build/build_cleaning_pdfs.py
"""
import html
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: %(size)s; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; }
body { font-family: 'Geist', -apple-system, sans-serif; color: #16181d; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: %(w)s; height: %(h)s; padding: 14mm 14mm 10mm; display: flex; flex-direction: column; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.head { display: flex; align-items: flex-end; justify-content: space-between; border-bottom: 1.4px solid #16181d; padding-bottom: 3mm; }
.head h1 { font-size: 21pt; font-weight: 800; letter-spacing: -0.03em; margin: 0; line-height: 1; }
.head .r { display: flex; align-items: center; gap: 3mm; }
.tag { background: #1f9d63; color: #fff; font-size: 6.5pt; font-weight: 700; letter-spacing: .14em; border-radius: 20px; padding: 1.4mm 3.6mm; text-transform: uppercase; }
.pno { font-size: 6.5pt; color: #9aa0a8; letter-spacing: .16em; font-weight: 600; text-transform: uppercase; }
.intro { font-size: 8pt; color: #5c626b; line-height: 1.5; margin: 2.6mm 0 0; }
.fields { display: grid; grid-template-columns: 1fr 1fr; gap: 9mm; margin-top: 4mm; }
.field label { display: block; font-size: 6pt; letter-spacing: .16em; color: #8a9099; font-weight: 700; text-transform: uppercase; }
.field .line { border-bottom: 1px solid #c9cfd6; height: 7.5mm; font-family: 'Caveat', cursive; font-size: 14pt; color: #1d3a8a; padding-left: 1mm; line-height: 8.5mm; }
table { width: 100%%; border-collapse: separate; border-spacing: 0; margin-top: 4mm; font-size: 7.6pt; }
thead th { background: #123227; color: #fff; font-size: 6pt; letter-spacing: .12em; text-transform: uppercase; font-weight: 700; text-align: left; padding: 2.6mm 2.2mm; line-height: 1.25; }
thead th:first-child { border-top-left-radius: 2.4mm; }
thead th:last-child { border-top-right-radius: 2.4mm; }
thead th.c { text-align: center; }
tbody td { border-bottom: 1px solid #e3e6e4; padding: 0 2.2mm; height: %(rowh)s; line-height: 1.25; }
tbody td.item { font-weight: 600; }
tbody td.sub { color: #5c626b; font-size: 7pt; }
tbody td.cell { border-left: 1px solid #e3e6e4; text-align: center; font-family: 'Caveat', cursive; font-size: 13pt; color: #1d3a8a; padding: 0; }
tbody td.hand { font-family: 'Caveat', cursive; font-size: 12.5pt; color: #1d3a8a; border-left: 1px solid #e3e6e4; }
tbody tr.sec td { background: #eef4f0; color: #1f5e40; font-size: 6pt; letter-spacing: .14em; text-transform: uppercase; font-weight: 700; height: 6mm; }
.note { font-size: 7.2pt; color: #5c626b; margin-top: 2.6mm; line-height: 1.5; }
.note b { color: #16181d; }
.box { border: 1px solid #dfe3e1; border-radius: 3mm; padding: 3mm 4mm; margin-top: 3.5mm; }
.box h4 { font-size: 6pt; letter-spacing: .16em; color: #8a9099; text-transform: uppercase; margin: 0 0 1.6mm; font-weight: 700; }
.box .hand { font-family: 'Caveat', cursive; font-size: 13pt; color: #1d3a8a; line-height: 1.35; }
.box .rule { border-bottom: 1px solid #e3e6e4; height: 7mm; }
.sign { display: grid; grid-template-columns: 1.4fr 1fr; gap: 9mm; margin-top: 3.5mm; }
.card { background: #f1f6f3; border-radius: 3mm; padding: 3.6mm 4.2mm; margin-top: 4mm; font-size: 7.4pt; line-height: 1.5; color: #33403a; }
.card h4 { font-size: 8.5pt; margin: 0 0 1.6mm; color: #16181d; letter-spacing: -0.01em; }
.card ol, .card ul { margin: 0; padding-left: 4.2mm; }
.card li { margin: 0 0 .8mm; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.foot { margin-top: auto; border-top: 1px solid #e3e6e4; padding-top: 2.6mm; display: flex; justify-content: space-between; font-size: 6.5pt; color: #8a9099; }
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;600;700;800&family=Caveat:wght@500&display=block" rel="stylesheet">')

E = html.escape


def head(title, pno, example=False):
    tag = '<span class="tag">Filled example</span>' if example else ''
    return f'<div class="head"><h1>{E(title)}</h1><div class="r">{tag}<span class="pno">{E(pno)}</span></div></div>'


def fields(a_label, a_val, b_label, b_val):
    return ('<div class="fields">'
            f'<div class="field"><label>{E(a_label)}</label><div class="line">{E(a_val)}</div></div>'
            f'<div class="field"><label>{E(b_label)}</label><div class="line">{E(b_val)}</div></div>'
            '</div>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


# ---------------------------------------------------------------- UK (A4)

UK_ROWS = [
    ("Work surfaces &amp; prep tables", "After use", "Detergent, then sanitiser"),
    ("Chopping boards &amp; knives", "After use", "Dishwasher, or wash then sanitise"),
    ("Hand-contact points", "Daily", "Sanitiser: handles, taps, switches, till"),
    ("Handwash basins", "Daily", "Clean, sanitise, refill soap and towels"),
    ("Sinks &amp; draining boards", "Daily", "Detergent, then sanitiser"),
    ("Hobs, ovens &amp; grill", "Daily", "Degreaser"),
    ("Fryer &amp; surround", "Daily", "Degreaser"),
    ("Microwave", "Daily", "Detergent, then sanitiser"),
    ("Fridge seals &amp; handles", "Daily", "Sanitiser"),
    ("Floors", "Daily", "Sweep, then mop with detergent"),
    ("Bins", "Daily", "Empty, wash, sanitise lids"),
    ("Fridge interiors &amp; shelves", "Weekly", "Empty, detergent, sanitiser"),
    ("Extractor hood &amp; filters", "Weekly", "Degreaser or dishwasher"),
    ("Walls &amp; splashbacks", "Weekly", "Detergent"),
    ("Dry store shelves", "Weekly", "Detergent; look for pest signs"),
    ("Dishwasher", "Weekly", "Clean filters and arms; descale"),
    ("", "", ""),
    ("", "", ""),
]

# St James's Cafe, week of Mon 16 Nov 2026, as of Thursday. Mon..Thu filled.
UK_FILLED = [
    ["TA", "PK", "TA", "SR"], ["PK", "PK", "SR", "TA"], ["SR", "SR", "TA", "SR"], ["SR", "PK", "SR", "SR"],
    ["TA", "TA", "PK", "SR"], ["SR", "TA", "SR", "TA"], ["SR", "SR", "TA", "TA"], ["PK", "PK", "SR", "PK"],
    ["TA", "SR", "TA", "SR"], ["SR", "SR", "SR", "SR"], ["SR", "SR", "TA", "SR"],
    ["", "", "PK", ""], ["", "PK", "", ""], ["", "", "", ""], ["TA", "", "", ""], ["", "", "", "SR"],
    ["", "", "", ""], ["", "", "", ""],
]

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def uk_weekly(example: bool) -> str:
    th = ('<tr><th style="width:30%">Item / area</th><th style="width:9%">Freq.</th>'
          '<th style="width:27%">Method / chemical</th>' + "".join(f'<th class="c">{d}</th>' for d in DAYS) + '</tr>')
    rows = []
    for i, (item, freq, method) in enumerate(UK_ROWS):
        marks = (UK_FILLED[i] + ["", "", ""]) if example else [""] * 7
        rows.append(f'<tr><td class="item">{item}</td><td class="sub">{freq}</td><td class="sub">{method}</td>'
                    + "".join(f'<td class="cell">{E(m)}</td>' for m in marks) + '</tr>')
    if example:
        intro = ("St James's Cafe, week of Monday 16 November 2026, as of Thursday. Blank cells mean "
                 "&ldquo;not due that day&rdquo;, not &ldquo;forgotten&rdquo;. Weekly jobs show the day they were done.")
        top = fields("Week starting", "Mon 16 Nov 2026", "Business", "St James's Cafe")
        notes = ('<div class="box"><h4>Deep clean notes / problems found</h4><div class="hand">'
                 'Extractor filters through the dishwasher Tue PM - PK. Fridge 2 door seal split, new seal ordered Wed, '
                 'wiped down every service until it is fitted - SR. Walls and splashbacks due Fri.</div></div>')
        sign = fields("Checked by (manager)", "Sam R.", "Date", "Thu 19 Nov 2026")
    else:
        intro = ("Initial each cell when the job is done, at the time it is done. Leave a cell blank if the job "
                 "is not due that day. Add your own equipment in the empty rows.")
        top = fields("Week starting", "", "Business", "")
        notes = ('<div class="box"><h4>Deep clean notes / problems found</h4>'
                 '<div class="rule"></div><div class="rule"></div></div>')
        sign = fields("Checked by (manager)", "", "Date", "")
    return ('<section class="page">'
            + head("Kitchen cleaning schedule", "Sheet 2" if example else "Sheet 1", example)
            + f'<p class="intro">{intro}</p>' + top
            + f'<table><thead>{th}</thead><tbody>{"".join(rows)}</tbody></table>'
            + '<p class="note"><b>Two-stage clean:</b> remove debris, wash with hot water and detergent, rinse, '
              'then apply sanitiser for the contact time on the label. Sanitiser should meet BS EN 1276 or BS EN 13697.</p>'
            + notes + sign
            + foot("Blueroll &middot; Free kitchen cleaning schedule &middot; UK", "This schedule fills itself in Blueroll &middot; blueroll.app")
            + '</section>')


UK_MONTHLY = [
    ("Freezers: defrost and clean", "Monthly, or when ice builds up"),
    ("Behind and under equipment", "Monthly"),
    ("Cold room or walk-in: shelves and floor", "Monthly"),
    ("Ice machine", "Monthly, or as the maker says"),
    ("Coffee machine: descale", "As the maker says"),
    ("Drains and gullies", "Monthly"),
    ("Light fittings, vents, fly screens", "Every 3 months"),
    ("Whole-kitchen deep clean", "Every 3 months"),
    ("Extract ductwork (contractor)", "As your insurer requires (TR19)"),
    ("Pest control visit", "As your contract says"),
    ("", ""),
    ("", ""),
]


def uk_monthly() -> str:
    th = ('<tr><th style="width:31%">Job</th><th style="width:22%">Suggested frequency</th><th class="c">Date done</th>'
          '<th class="c">Done by</th><th class="c">Checked by</th><th style="width:16%">Notes</th></tr>')
    rows = "".join(
        f'<tr><td class="item">{job}</td><td class="sub">{freq}</td><td class="cell"></td><td class="cell"></td>'
        f'<td class="cell"></td><td class="cell"></td></tr>' for job, freq in UK_MONTHLY)
    card = ('<div class="grid2">'
            '<div class="card"><h4>Clean, then disinfect</h4><ol>'
            '<li>Scrape off food and debris.</li>'
            '<li>Wash with hot water and detergent, then rinse.</li>'
            '<li>Apply sanitiser and leave it for the contact time on the label.</li>'
            '<li>Rinse if the label says so. Air-dry or use a single-use towel.</li></ol></div>'
            '<div class="card"><h4>What an inspector looks for</h4><ul>'
            '<li>A schedule that says what is cleaned, how, how often and by whom.</li>'
            '<li>Sign-offs made at the time, not a week filled in with one pen.</li>'
            '<li>Sanitiser to BS EN 1276 or BS EN 13697, used at the right dilution.</li>'
            '<li>Disposable cloths, or cloths washed on a hot cycle; separate cloths for raw-food areas.</li></ul></div>'
            '</div>')
    return ('<section class="page">' + head("Monthly and deep-clean log", "Sheet 3")
            + '<p class="intro">For jobs that are not on the weekly sheet. Frequencies are a starting point: '
              'set your own from how busy the kitchen is and what your equipment maker says.</p>'
            + fields("Year", "", "Business", "")
            + f'<table><thead>{th}</thead><tbody>{rows}</tbody></table>' + card
            + foot("Blueroll &middot; Free kitchen cleaning schedule &middot; UK", "This log fills itself in Blueroll &middot; blueroll.app")
            + '</section>')


# ---------------------------------------------------------------- US (Letter)

US_ROWS = [
    ("sec", "Kitchen"),
    ("Prep tables &amp; food-contact surfaces", "Every 4 hrs in use", "Wash, rinse, sanitize"),
    ("Cutting boards &amp; utensils", "After each task", "Wash, rinse, sanitize"),
    ("Sanitizer buckets &amp; wiping cloths", "Every shift", "Fresh solution; test strip"),
    ("Handwashing sinks", "Every shift", "Clean; soap and towels stocked"),
    ("Flat-top, grill &amp; fryer", "At close", "Scrape, degrease"),
    ("Reach-ins: handles &amp; gaskets", "At close", "Wash, sanitize"),
    ("Dish machine", "At close", "Drain, clean screens and arms"),
    ("Floors &amp; floor drains", "At close", "Sweep, mop, clear drains"),
    ("Trash &amp; recycling", "At close", "Empty, wash cans"),
    ("sec", "Front of house"),
    ("Tables, chairs &amp; booths", "Each turn", "Clean, sanitize"),
    ("Menus &amp; condiment caddies", "At close", "Wipe, sanitize"),
    ("Drink station &amp; soda nozzles", "At close", "Soak nozzles, wipe down"),
    ("Door handles, host stand, POS", "At close", "Sanitize"),
    ("sec", "Restrooms"),
    ("Toilets, sinks &amp; mirrors", "Every shift", "Clean, disinfect"),
    ("Soap, paper towels, tissue", "Every shift", "Restock"),
]

US_FILLED = [
    None,
    ["JM", "JM", "DL", "JM"], ["DL", "JM", "DL", "RC"], ["RC", "RC", "DL", "RC"], ["JM", "DL", "DL", "JM"],
    ["DL", "DL", "JM", "DL"], ["JM", "RC", "JM", "JM"], ["RC", "RC", "RC", "DL"], ["DL", "JM", "RC", "RC"],
    ["RC", "RC", "DL", "RC"],
    None,
    ["AV", "AV", "KT", "AV"], ["KT", "AV", "KT", "KT"], ["AV", "KT", "AV", "AV"], ["KT", "KT", "AV", "KT"],
    None,
    ["AV", "KT", "AV", "KT"], ["AV", "KT", "AV", "AV"],
]


def us_daily(example: bool) -> str:
    th = ('<tr><th style="width:31%">Task</th><th style="width:13%">When</th>'
          '<th style="width:22%">How</th>' + "".join(f'<th class="c">{d}</th>' for d in DAYS) + '</tr>')
    rows = []
    for i, r in enumerate(US_ROWS):
        if r[0] == "sec":
            rows.append(f'<tr class="sec"><td colspan="10">{r[1]}</td></tr>')
            continue
        task, when, how = r
        marks = (US_FILLED[i] + ["", "", ""]) if example else [""] * 7
        rows.append(f'<tr><td class="item">{task}</td><td class="sub">{when}</td><td class="sub">{how}</td>'
                    + "".join(f'<td class="cell">{E(m)}</td>' for m in marks) + '</tr>')
    if example:
        intro = ("Main Street Diner (a sample restaurant), week of Monday, November 16, 2026, as of Thursday. "
                 "Each cell is initialed by the person who did the job, when they did it.")
        top = fields("Week of", "Mon, Nov 16, 2026", "Restaurant", "Main Street Diner")
        notes = ('<div class="box"><h4>Problems found / follow-up</h4><div class="hand">'
                 'Wed: dish machine sanitizer read low at close, changed the bucket and called the chemical rep - RC. '
                 'Thu: men\'s room out of paper towels at 2 pm, restocked, added a 1 pm check - AV.</div></div>')
        sign = fields("Manager sign-off", "Dana L.", "Date", "Thu, Nov 19, 2026")
    else:
        intro = ("Initial each box when the job is done, at the time it is done. Add tasks for your own "
                 "equipment. Keep completed sheets on file for your health inspector.")
        top = fields("Week of", "", "Restaurant", "")
        notes = ('<div class="box"><h4>Problems found / follow-up</h4>'
                 '<div class="rule"></div><div class="rule"></div></div>')
        sign = fields("Manager sign-off", "", "Date", "")
    return ('<section class="page">' + head("Daily restaurant cleaning checklist", "Sheet 2" if example else "Sheet 1", example)
            + f'<p class="intro">{intro}</p>' + top
            + f'<table><thead>{th}</thead><tbody>{"".join(rows)}</tbody></table>'
            + '<p class="note"><b>Clean, rinse, sanitize:</b> food-contact surfaces in constant use with TCS food '
              'get cleaned and sanitized at least every 4 hours (FDA Food Code 4-602.11). Keep wiping cloths in sanitizer between uses.</p>'
            + notes + sign
            + foot("Blueroll &middot; Free restaurant cleaning checklist &middot; US",
                   "This checklist fills itself in Blueroll &middot; blueroll.app")
            + '</section>')


US_PERIODIC = [
    ("Walk-in cooler: shelves, floor, door gasket", "Weekly"),
    ("Hood filters", "Weekly"),
    ("Ovens: inside", "Weekly"),
    ("Walls and surfaces behind the line", "Weekly"),
    ("Coffee and beverage equipment: deep clean", "Weekly"),
    ("Ice machine: clean and sanitize", "Monthly, or per manufacturer"),
    ("Freezers: defrost and clean", "Monthly"),
    ("Behind and under equipment", "Monthly"),
    ("Grease trap", "Per your hauler's schedule"),
    ("Hood and duct system (contractor)", "Per NFPA 96 / fire marshal"),
    ("Pest control service", "Per your contract"),
]


def us_periodic() -> str:
    th = ('<tr><th style="width:42%">Task</th><th style="width:24%">How often</th><th class="c">Date done</th>'
          '<th class="c">By</th><th class="c">Checked</th></tr>')
    rows = "".join(
        f'<tr><td class="item">{t}</td><td class="sub">{f}</td><td class="cell"></td><td class="cell"></td>'
        f'<td class="cell"></td></tr>' for t, f in US_PERIODIC)
    th2 = ('<tr><th>Date</th><th>Time</th><th>Station</th><th>Sanitizer</th><th class="c">Reading (ppm)</th>'
           '<th class="c">OK?</th><th style="width:28%">If not OK, what you did</th><th class="c">Initials</th></tr>')
    rows2 = "".join('<tr>' + '<td class="hand"></td>' * 8 + '</tr>' for _ in range(7))
    return ('<section class="page">' + head("Weekly, monthly &amp; sanitizer log".replace("&amp;", "&"), "Sheet 3")
            + '<p class="intro">Deeper jobs that are not on the daily sheet, and a log of sanitizer test-strip readings. '
              'Frequencies are a starting point: set your own from your volume and your equipment manuals.</p>'
            + fields("Month", "", "Restaurant", "")
            + f'<table><thead>{th}</thead><tbody>{rows}</tbody></table>'
            + '<table style="margin-top:5mm"><thead>' + th2 + '</thead><tbody>' + rows2 + '</tbody></table>'
            + '<p class="note"><b>Test strip targets:</b> chlorine (bleach) usually 50-100 ppm; quaternary ammonium '
              'at the strength on the product label, often 200-400 ppm. The label and your city or county health code come first.</p>'
            + foot("Blueroll &middot; Free restaurant cleaning checklist &middot; US",
                   "Based on the FDA Food Code. Your local health code may add to it.")
            + '</section>')


def render(pages, size, w, h, rowh, out_pdf: Path, title: str) -> None:
    css = CSS % {"size": size, "w": w, "h": h, "rowh": rowh}
    doc = (f'<!doctype html><html><head><meta charset="utf-8"><title>{E(title)}</title>{FONTS}'
           f'<style>{css}</style></head><body>{"".join(pages)}</body></html>')
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "doc.html"
        src.write_text(doc)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--virtual-time-budget=8000", f"--print-to-pdf={out_pdf}", src.as_uri()],
                       check=True, capture_output=True)
    print("built", out_pdf.name)


def previews(pdf: Path, stem: str) -> None:
    out = ROOT / "uploads"
    subprocess.run(["pdftoppm", "-r", "80", "-png", str(pdf), str(out / stem)], check=True)
    for p in sorted(out.glob(f"{stem}-*.png")):
        n = int(p.stem.rsplit("-", 1)[1])
        p.rename(out / f"{stem}-{n}.png")
    print("previews", stem)


def main() -> None:
    uk = ROOT / "blueroll-kitchen-cleaning-schedule.pdf"
    render([uk_weekly(False), uk_weekly(True), uk_monthly()], "A4", "210mm", "297mm", "8.6mm", uk,
           "Kitchen cleaning schedule (UK) | Blueroll")
    us = ROOT / "blueroll-restaurant-cleaning-checklist.pdf"
    render([us_daily(False), us_daily(True), us_periodic()], "letter", "8.5in", "11in", "7.6mm", us,
           "Restaurant cleaning checklist (US) | Blueroll")
    previews(uk, "cleaning-uk-page")
    previews(us, "cleaning-us-page")


if __name__ == "__main__":
    main()
