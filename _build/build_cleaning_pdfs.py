#!/usr/bin/env python3
"""Build the two free cleaning PDFs and their page previews.

  blueroll-kitchen-cleaning-schedule.pdf    UK, A4: weekly schedule, filled example, monthly + deep-clean log
  blueroll-restaurant-cleaning-checklist.pdf US, Letter: daily checklist, filled example, weekly/monthly + sanitizer log

This file also holds the shared look of the printable templates (cleaning, temperature
logs, allergen matrix): small logo top-left, large title, one short line under it,
a light header row, tall writing rows that fill the page, one quiet footer line.
Black text on white, so the sheets print well in black and white. The filled
examples are written in a handwriting font. HTML is printed with headless Chrome,
previews come from pdftoppm. Run from the repo root:

    python3 _build/build_cleaning_pdfs.py
"""
import html
import re
import subprocess
import tempfile
from pathlib import Path
from string import Template

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

E = html.escape

# ---------------------------------------------------------------- shared look

INK, SOFT, QUIET = "#16181d", "#454b53", "#8a9099"
HAND = "#1d3a8a"

CSS = Template("""
@page { size: $size; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; }
body { font-family: 'Geist', -apple-system, sans-serif; color: #16181d; font-size: 9pt; line-height: 1.35;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: $w; height: $h; padding: $pad; display: flex; flex-direction: column; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.brand { display: flex; align-items: center; gap: 1.5mm; font-size: 10pt; font-weight: 700; letter-spacing: -0.01em; flex: none; }
.brand svg { height: 5mm; width: auto; display: block; }
h1 { font-size: 24pt; font-weight: 700; letter-spacing: -0.025em; line-height: 1.05; margin: 5mm 0 0; flex: none; }
.lead { font-size: 9.5pt; color: #454b53; margin: 2mm 0 0; flex: none; white-space: nowrap; }
.fields { display: flex; gap: 9mm; margin-top: 4.5mm; flex: none; }
.field { flex: 1; display: flex; align-items: flex-end; gap: 2.2mm; min-width: 0; }
.field > span { font-size: 9pt; font-weight: 600; white-space: nowrap; padding-bottom: 1.1mm; }
.field .line { flex: 1; min-width: 0; border-bottom: 1px solid #8a9099; height: 8mm; padding-left: 1.5mm;
               font-family: 'Caveat', cursive; font-size: 15pt; line-height: 9.2mm; color: #1d3a8a; white-space: nowrap; }
.grow { flex: 1 1 auto; min-height: 0; margin-top: 5mm; }
.fixed { flex: none; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; }
th { background: #f1f4f2; color: #16181d; font-size: 8.5pt; font-weight: 700; text-align: left; line-height: 1.2;
     padding: 2.2mm 2mm; vertical-align: bottom; border-bottom: 1px solid #9aa19d; }
th.c { text-align: center; padding-left: .5mm; padding-right: .5mm; }
td { height: 9mm; padding: 0 2mm; border-bottom: 1px solid #c9cfcb; vertical-align: middle; line-height: 1.25; }
th.v, td.v { border-left: 1px solid #d9dedb; }
td.item { font-weight: 500; }
td.sub { color: #454b53; font-size: 8.5pt; }
td.cell { text-align: center; padding: 0; font-family: 'Caveat', cursive; font-size: 14pt; color: #1d3a8a; white-space: nowrap; }
td.hand { font-family: 'Caveat', cursive; font-size: 13.5pt; color: #1d3a8a; white-space: nowrap; overflow: hidden; }
tr.sec td { height: 6.5mm; font-size: 8.5pt; font-weight: 700; vertical-align: bottom; padding-bottom: 1.3mm; }
.note { font-size: 8.5pt; color: #454b53; margin: 2mm 0 0; flex: none; }
.note b { color: #16181d; font-weight: 600; }
h2 { font-size: 10.5pt; font-weight: 700; letter-spacing: -0.01em; margin: 6mm 0 0; flex: none; }
.write { margin-top: 4mm; flex: none; }
.write > span { font-size: 9pt; font-weight: 600; }
.ruled { position: relative; }
.ruled .r { height: 8.6mm; border-bottom: 1px solid #c9cfcb; }
.ruled .hand { position: absolute; left: 1.5mm; right: 0; top: 2.1mm; font-family: 'Caveat', cursive; font-size: 13.5pt;
               line-height: 8.6mm; color: #1d3a8a; }
.text { font-size: 8.5pt; color: #2e333a; line-height: 1.45; }
.text h3 { font-size: 9pt; font-weight: 700; color: #16181d; margin: 0 0 1.4mm; }
.text ol, .text ul { margin: 0; padding-left: 4.4mm; }
.text li { margin: 0 0 .8mm; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 9mm; margin-top: 5mm; flex: none; }
.foot { margin-top: 4mm; font-size: 8pt; color: #8a9099; flex: none; }
""")

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700'
         '&family=Caveat:wght@500&display=block" rel="stylesheet">')

# After the fonts load, each .grow block is filled: tables marked data-extend get
# more blank rows while a whole row still fits, then the space left over is shared
# between the writing rows (tr.w), so the table always reaches the footer.
# A red outline marks a table that does not fit, so it shows in the check renders.
FILL_JS = """<script>
document.fonts.ready.then(function () {
  document.querySelectorAll('.lead').forEach(function (l) {
    if (l.scrollWidth > l.clientWidth + 1) { l.style.outline = '3px solid red'; l.setAttribute('data-extra', 'lead too long'); }
  });
  document.querySelectorAll('.grow').forEach(function (g) {
    var t = g.querySelector('table'), b = t.tBodies[0];
    var avail = g.getBoundingClientRect().height - 1;
    var th = function () { return t.getBoundingClientRect().height; };
    if (g.hasAttribute('data-extend')) {
      var last = b.rows[b.rows.length - 1], h = last.getBoundingClientRect().height;
      while (avail - th() >= h) b.appendChild(last.cloneNode(true));
    }
    var rows = b.querySelectorAll('tr.w'), extra = avail - th();
    g.setAttribute('data-extra', extra.toFixed(1));
    if (extra < -1) { g.style.outline = '3px solid red'; return; }
    var hs = Array.prototype.map.call(rows, function (r) { return r.getBoundingClientRect().height; });
    rows.forEach(function (r, i) { r.style.height = (hs[i] + extra / rows.length) + 'px'; });
  });
});
</script>"""


def _logo_path() -> str:
    svg = (ROOT / "blueroll-logo.svg").read_text()
    return re.search(r' d="([^"]+)"', svg).group(1)


LOGO = ('<svg viewBox="154 97 261 360" xmlns="http://www.w3.org/2000/svg">'
        '<defs><linearGradient id="lg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#006A4C"/><stop offset="1" stop-color="#003526"/></linearGradient></defs>'
        f'<path d="{_logo_path()}" fill="url(#lg)"/></svg>')


def head(title: str, lead: str = "") -> str:
    """Logo, title, and at most one short line under it. `title` is HTML."""
    out = f'<div class="brand">{LOGO}<span>Blueroll</span></div><h1>{title}</h1>'
    return out + (f'<p class="lead">{lead}</p>' if lead else "")


def fields(*pairs) -> str:
    """Write-in fields on one line: fields(("Week starting", ""), ("Business", "")). Values are plain text."""
    return '<div class="fields">' + "".join(
        f'<div class="field"><span>{E(label)}</span><div class="line">{E(val)}</div></div>'
        for label, val in pairs) + '</div>'


def write(label: str, lines: int = 2, text: str = "") -> str:
    """A label and ruled lines to write on. `text` (HTML) is the filled-in example, in handwriting."""
    hand = f'<div class="hand">{text}</div>' if text else ""
    return (f'<div class="write"><span>{E(label)}</span><div class="ruled">'
            + '<div class="r"></div>' * lines + hand + '</div></div>')


def grow(table: str, extend: bool = False) -> str:
    return f'<div class="grow"{" data-extend" if extend else ""}>{table}</div>'


def foot(name: str) -> str:
    return f'<div class="foot">blueroll.app &middot; Free {name}</div>'


def page(*parts: str) -> str:
    return '<section class="page">' + "".join(parts) + '</section>'


def render(pages, size, w, h, out_pdf: Path, title: str, lang: str = "en-GB",
           pad: str = "10mm 13mm 8mm", extra_css: str = "") -> None:
    css = CSS.substitute(size=size, w=w, h=h, pad=pad) + extra_css
    doc = (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{E(title)}</title>{FONTS}'
           f'<style>{css}</style></head><body>{"".join(pages)}{FILL_JS}</body></html>')
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "doc.html"
        src.write_text(doc, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--virtual-time-budget=10000", f"--print-to-pdf={out_pdf}", src.as_uri()],
                       check=True, capture_output=True)
    print("built", out_pdf.name)


def page_images(pdf: Path, width: int, first: int = 1, last: int = 0):
    """Each page of the PDF as an RGB image `width` px wide (sharp on 2x screens)."""
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["pdftoppm", "-png", "-scale-to-x", str(width), "-scale-to-y", "-1", "-f", str(first)]
        if last:
            cmd += ["-l", str(last)]
        subprocess.run(cmd + [str(pdf), f"{tmp}/p"], check=True)
        return [Image.open(p).convert("RGB") for p in sorted(Path(tmp).glob("p-*.png"))]


def previews(pdf: Path, stem: str, width: int = 1240) -> None:
    """uploads/<stem>-1.png, -2.png, ... A palette PNG keeps the files small."""
    out = ROOT / "uploads"
    for n, im in enumerate(page_images(pdf, width), start=1):
        im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(
            out / f"{stem}-{n}.png", optimize=True)
    print("previews", stem)


DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def day_heads() -> str:
    return "".join(f'<th class="c v">{d}</th>' for d in DAYS)


# ---------------------------------------------------------------- UK (A4)

UK_NAME = "kitchen cleaning schedule"

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

UK_TWO_STAGE = ('<p class="note"><b>Two-stage clean:</b> remove debris, wash with hot water and detergent, rinse, '
                'then apply sanitiser for the contact time on the label. Sanitiser should meet BS EN 1276 or BS EN 13697.</p>')


def uk_weekly(example: bool) -> str:
    th = ('<tr><th style="width:26%">Item or area</th><th style="width:11%">How often</th>'
          '<th style="width:30%">Method and chemical</th>' + day_heads() + '</tr>')
    rows = []
    for i, (item, freq, method) in enumerate(UK_ROWS):
        marks = (UK_FILLED[i] + ["", "", ""]) if example else [""] * 7
        rows.append(f'<tr class="w"><td class="item">{item}</td><td class="sub">{freq}</td><td class="sub">{method}</td>'
                    + "".join(f'<td class="cell v">{E(m)}</td>' for m in marks) + '</tr>')
    table = f'<table><thead>{th}</thead><tbody>{"".join(rows)}</tbody></table>'
    if example:
        lead = ("Filled example from St James's Cafe, up to Thursday. "
                "A blank cell means not due that day, not forgotten.")
        top = fields(("Week starting", "Mon 16 Nov 2026"), ("Business", "St James's Cafe"))
        notes = write("Deep clean notes and problems found", 2,
                      "Extractor filters through the dishwasher Tue PM - PK. Fridge 2 door seal split, new seal ordered "
                      "Wed, wiped down every service until it is fitted - SR. Walls and splashbacks due Fri.")
        sign = fields(("Checked by (manager)", "SR"), ("Date", "Thu 19 Nov 2026"))
    else:
        lead = ("Initial each cell when the job is done, at the time it is done. "
                "Leave it blank if the job is not due that day.")
        top = fields(("Week starting", ""), ("Business", ""))
        notes = write("Deep clean notes and problems found", 2)
        sign = fields(("Checked by (manager)", ""), ("Date", ""))
    return page(head("Kitchen cleaning schedule", lead), top, grow(table), UK_TWO_STAGE, notes, sign, foot(UK_NAME))


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
]


def uk_monthly() -> str:
    th = ('<tr><th style="width:30%">Job</th><th style="width:21%">Suggested frequency</th>'
          '<th class="v" style="width:12%">Date done</th><th class="v" style="width:11%">Done by</th>'
          '<th class="v" style="width:12%">Checked by</th><th class="v">Notes</th></tr>')
    rows = "".join(
        f'<tr class="w"><td class="item">{job}</td><td class="sub">{freq}</td>' + '<td class="hand v"></td>' * 4 + '</tr>'
        for job, freq in UK_MONTHLY)
    table = f'<table><thead>{th}</thead><tbody>{rows}</tbody></table>'
    text = ('<div class="cols">'
            '<div class="text"><h3>Clean, then disinfect</h3><ol>'
            '<li>Scrape off food and debris.</li>'
            '<li>Wash with hot water and detergent, then rinse.</li>'
            '<li>Apply sanitiser and leave it for the contact time on the label.</li>'
            '<li>Rinse if the label says so. Air-dry or use a single-use towel.</li></ol></div>'
            '<div class="text"><h3>What an inspector looks for</h3><ul>'
            '<li>A schedule that says what is cleaned, how, how often and by whom.</li>'
            '<li>Sign-offs made at the time, not a week filled in with one pen.</li>'
            '<li>Sanitiser to BS EN 1276 or BS EN 13697, used at the right dilution.</li>'
            '<li>Disposable cloths, or cloths washed on a hot cycle; separate cloths for raw-food areas.</li></ul></div>'
            '</div>')
    lead = "For jobs not on the weekly sheet. Set frequencies from how busy you are and what the equipment maker says."
    return page(head("Monthly and deep-clean log", lead), fields(("Year", ""), ("Business", "")),
                grow(table, extend=True), text, foot(UK_NAME))


# ---------------------------------------------------------------- US (Letter)

US_NAME = "restaurant cleaning checklist"
US_PAD = "9mm 13mm 7mm"  # Letter is 18 mm shorter than A4

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
    th = ('<tr><th style="width:31%">Task</th><th style="width:15%">When</th>'
          '<th style="width:24%">How</th>' + day_heads() + '</tr>')
    rows = []
    for i, r in enumerate(US_ROWS):
        if r[0] == "sec":
            rows.append(f'<tr class="sec"><td colspan="10">{r[1]}</td></tr>')
            continue
        task, when, how = r
        marks = (US_FILLED[i] + ["", "", ""]) if example else [""] * 7
        rows.append(f'<tr class="w"><td class="item">{task}</td><td class="sub">{when}</td><td class="sub">{how}</td>'
                    + "".join(f'<td class="cell v">{E(m)}</td>' for m in marks) + '</tr>')
    table = f'<table><thead>{th}</thead><tbody>{"".join(rows)}</tbody></table>'
    if example:
        lead = ("Filled example from Main Street Diner, a sample restaurant, up to Thursday. "
                "Each box is initialed when the job is done.")
        top = fields(("Week of", "Mon, Nov 16, 2026"), ("Restaurant", "Main Street Diner"))
        notes = write("Problems found and follow-up", 2,
                      "Wed: dish machine sanitizer read low at close, changed the bucket and called the chemical rep - RC. "
                      "Thu: men's room out of paper towels at 2 pm, restocked, added a 1 pm check - AV.")
        sign = fields(("Manager sign-off", "DL"), ("Date", "Thu, Nov 19, 2026"))
    else:
        lead = ("Initial each box when the job is done, at the time it is done. "
                "Keep completed sheets on file for your inspector.")
        top = fields(("Week of", ""), ("Restaurant", ""))
        notes = write("Problems found and follow-up", 2)
        sign = fields(("Manager sign-off", ""), ("Date", ""))
    rule = ('<p class="note"><b>Clean, rinse, sanitize:</b> food-contact surfaces in constant use with TCS food '
            'get cleaned and sanitized at least every 4 hours (FDA Food Code 4-602.11). '
            'Keep wiping cloths in sanitizer between uses.</p>')
    return page(head("Daily restaurant cleaning checklist", lead), top, grow(table), rule, notes, sign, foot(US_NAME))


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
    th = ('<tr><th style="width:41%">Task</th><th style="width:23%">How often</th><th class="v">Date done</th>'
          '<th class="v">By</th><th class="v">Checked</th></tr>')
    rows = "".join(
        f'<tr><td class="item">{t}</td><td class="sub">{f}</td>' + '<td class="hand v"></td>' * 3 + '</tr>'
        for t, f in US_PERIODIC)
    th2 = ('<tr><th style="width:11%">Date</th><th class="v" style="width:9%">Time</th><th class="v">Station</th>'
           '<th class="v">Sanitizer</th><th class="v c" style="width:11%">Reading (ppm)</th>'
           '<th class="v c" style="width:7%">OK?</th><th class="v" style="width:25%">If not OK, what you did</th>'
           '<th class="v c" style="width:9%">Initials</th></tr>')
    rows2 = '<tr class="w"><td class="hand"></td>' + '<td class="hand v"></td>' * 7 + '</tr>'
    lead = "Deeper jobs that are not on the daily sheet, and sanitizer test-strip readings."
    return page(head("Weekly, monthly and sanitizer log", lead), fields(("Month", ""), ("Restaurant", "")),
                f'<div class="fixed" style="margin-top:5mm"><table><thead>{th}</thead><tbody>{rows}</tbody></table></div>',
                '<p class="note">Frequencies are a starting point: set your own from your volume and your equipment manuals.</p>',
                '<h2>Sanitizer test strips</h2>',
                grow(f'<table><thead>{th2}</thead><tbody>{rows2}</tbody></table>', extend=True),
                '<p class="note"><b>Test strip targets:</b> chlorine (bleach) usually 50-100 ppm; quaternary ammonium '
                'at the strength on the product label, often 200-400 ppm. The label and your city or county health code '
                'come first.</p>',
                foot(US_NAME))


def main() -> None:
    uk = ROOT / "blueroll-kitchen-cleaning-schedule.pdf"
    render([uk_weekly(False), uk_weekly(True), uk_monthly()], "A4", "210mm", "297mm", uk,
           "Kitchen cleaning schedule (UK) | Blueroll")
    us = ROOT / "blueroll-restaurant-cleaning-checklist.pdf"
    render([us_daily(False), us_daily(True), us_periodic()], "letter", "8.5in", "11in", us,
           "Restaurant cleaning checklist (US) | Blueroll", lang="en-US", pad=US_PAD)
    previews(uk, "cleaning-uk-page")
    previews(us, "cleaning-us-page")


if __name__ == "__main__":
    main()
