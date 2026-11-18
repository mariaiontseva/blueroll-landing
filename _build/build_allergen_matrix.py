#!/usr/bin/env python3
"""Build the free allergen matrix template (14 UK allergens) and its page images.

  blueroll-allergen-matrix-template.pdf    A4 landscape: blank matrix, filled example, how-to + change log
  blueroll-allergen-matrix-template.xlsx   the same matrix to fill in on screen (Excel, Google Sheets, Numbers)
  uploads/allergen-matrix-template-1.webp  page previews for allergen-matrix.html
  uploads/allergen-matrix-template-2.webp
  uploads/allergen-matrix-app.webp         the app's matrix screen, cropped to the content (no names)
  allergen-matrix-template-og.png          1200x630 share image

Same look as the 16-page HACCP pack and the cleaning sheets (dark green table heads,
filled example in handwriting). The 14 allergens and their examples are the FSA's
wording from "Allergen guidance for food businesses" (GOV.UK, updated 17 July 2026).
The example dishes are the FSA's own examples from "Allergen information for
non-prepacked foods: best practice" (24 February 2025), plus a coffee and chips.

Run from the repo root:

    python3 _build/build_allergen_matrix.py
"""
import html
import subprocess
import tempfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PDF = ROOT / "blueroll-allergen-matrix-template.pdf"
XLSX = ROOT / "blueroll-allergen-matrix-template.xlsx"

FSA_GUIDANCE = "https://www.gov.uk/government/publications/allergen-guidance-for-food-businesses/allergen-guidance-for-food-businesses"
FSA_BEST_PRACTICE = ("https://www.gov.uk/government/publications/allergen-information-for-non-prepacked-foods-best-practice/"
                     "allergen-information-for-non-prepacked-foods-best-practice")

# The FSA list, in the FSA's order. (column heading, example text from the FSA list)
ALLERGENS = [
    ("Celery", ""),
    ("Cereals containing gluten", "such as wheat, rye, barley and oats"),
    ("Crustaceans", "such as prawns, crabs and lobsters"),
    ("Eggs", ""),
    ("Fish", ""),
    ("Lupin", ""),
    ("Milk", ""),
    ("Molluscs", "such as mussels and oysters"),
    ("Mustard", ""),
    ("Peanuts", ""),
    ("Sesame", ""),
    ("Soybeans", ""),
    ("Sulphur dioxide and sulphites", "if the sulphur dioxide and sulphites are at a concentration of more than ten parts per million"),
    ("Tree nuts", "such as almonds, hazelnuts, walnuts, brazil nuts, cashews, pecans, pistachios and macadamia nuts"),
]
NAMES = [a for a, _ in ALLERGENS]

C, M = "✓", "M"  # contains / may contain

# Example dishes. Allergens as in the FSA's examples (best practice guidance 11.1, 11.2, 11.4 and annex B);
# chips from the FSA's shared-fryer example; flat white is milk, oat milk adds oats.
EXAMPLE = [
    ("Chicken salad", {"Eggs": C, "Milk": C, "Mustard": C}, ""),
    ("Chicken tikka masala", {"Milk": C, "Tree nuts": C}, "Almond"),
    ("BBQ chicken burger and coleslaw",
     {"Celery": C, "Cereals containing gluten": C, "Eggs": C, "Fish": C, "Mustard": C, "Sesame": C},
     "Wheat. Mustard: coleslaw only"),
    ("Fish, bean and rice bowl", {"Celery": C, "Fish": C, "Milk": C}, ""),
    ("Seafood and chorizo paella", {"Crustaceans": C, "Molluscs": C, "Sulphur dioxide and sulphites": C},
     "Prawns, clams"),
    ("Avocado and cos salad", {"Peanuts": C, "Sesame": C, "Soybeans": C, "Tree nuts": C}, "Cashew"),
    ("Chips", {"Cereals containing gluten": M, "Fish": M}, "Same fryer as battered fish"),
    ("Flat white", {"Milk": C}, "Oat milk swap adds oats"),
]

E = html.escape

# ---------------------------------------------------------------- PDF (HTML printed by headless Chrome)

CSS = """
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; }
body { font-family: 'Geist', -apple-system, sans-serif; color: #16181d; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 297mm; height: 210mm; padding: 10mm 12mm 7mm; display: flex; flex-direction: column; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.head { display: flex; align-items: flex-end; justify-content: space-between; border-bottom: 1.4px solid #16181d; padding-bottom: 2.6mm; }
.head h1 { font-size: 20pt; font-weight: 800; letter-spacing: -0.03em; margin: 0; line-height: 1; }
.head .r { display: flex; align-items: center; gap: 3mm; }
.tag { background: #1f9d63; color: #fff; font-size: 6.5pt; font-weight: 700; letter-spacing: .14em; border-radius: 20px; padding: 1.4mm 3.6mm; text-transform: uppercase; }
.pno { font-size: 6.5pt; color: #9aa0a8; letter-spacing: .16em; font-weight: 600; text-transform: uppercase; }
.intro { font-size: 7.8pt; color: #5c626b; line-height: 1.45; margin: 2.2mm 0 0; }
.intro b { color: #16181d; }
.fields { display: grid; grid-template-columns: 1.3fr 1fr 1fr; gap: 9mm; margin-top: 2.6mm; }
.field label { display: block; font-size: 6pt; letter-spacing: .16em; color: #8a9099; font-weight: 700; text-transform: uppercase; }
.field .line { border-bottom: 1px solid #c9cfd6; height: 7mm; font-family: 'Caveat', cursive; font-size: 14pt; color: #1d3a8a; padding-left: 1mm; line-height: 8mm; }
table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 3.4mm; font-size: 7.6pt; table-layout: fixed; }
thead th { background: #123227; color: #fff; font-weight: 700; padding: 2mm 1.4mm; vertical-align: bottom; text-align: left; }
thead th.lab { font-size: 6pt; letter-spacing: .12em; text-transform: uppercase; line-height: 1.3; }
thead th:first-child { border-top-left-radius: 2.4mm; }
thead th:last-child { border-top-right-radius: 2.4mm; }
thead th.al { padding: 2mm 0 2.2mm; border-left: 1px solid rgba(255,255,255,.14); }
thead th.al div { writing-mode: vertical-rl; transform: rotate(180deg); height: 29mm; margin: 0 auto; font-size: 7pt; line-height: 1.15; letter-spacing: 0; text-align: left; }
tbody td { border-bottom: 1px solid #e3e6e4; padding: 0 2mm; height: 7.1mm; line-height: 1.2; overflow: hidden; }
tbody td.cell { border-left: 1px solid #e3e6e4; text-align: center; padding: 0; font-family: 'Caveat', cursive; font-size: 14pt; color: #1d3a8a; }
tbody td.cell.alt { background: #f7f9f8; }
tbody td.hand { font-family: 'Caveat', cursive; font-size: 12.5pt; color: #1d3a8a; }
tbody td.notes { border-left: 1px solid #e3e6e4; }
.key { display: flex; flex-wrap: wrap; gap: 1.2mm 6mm; font-size: 7.2pt; color: #5c626b; margin-top: 2.4mm; line-height: 1.45; }
.key b { color: #16181d; }
.grid2 { display: grid; grid-template-columns: 112mm 1fr; gap: 7mm; margin-top: 3.6mm; flex: 1; min-height: 0; }
.card { background: #f1f6f3; border-radius: 3mm; padding: 3.2mm 4mm; font-size: 7.3pt; line-height: 1.45; color: #33403a; margin-bottom: 3mm; }
.card h4 { font-size: 8.4pt; margin: 0 0 1.4mm; color: #16181d; letter-spacing: -0.01em; }
.card ol, .card ul { margin: 0; padding-left: 4.2mm; }
.card li { margin: 0 0 .7mm; }
.card .src { font-size: 6.4pt; color: #6b756f; margin-top: 1.6mm; }
.log td { height: 8.6mm; }
.log td + td { border-left: 1px solid #e3e6e4; }
.foot { margin-top: auto; border-top: 1px solid #e3e6e4; padding-top: 2.2mm; display: flex; justify-content: space-between; font-size: 6.5pt; color: #8a9099; }
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;600;700;800&family=Caveat:wght@500&display=block" rel="stylesheet">')

FOOT = ('<div class="foot"><span>Blueroll &middot; Free allergen matrix template &middot; 14 UK allergens</span>'
        '<span>In Blueroll the matrix comes from your recipes &middot; blueroll.app/allergen-matrix.html</span></div>')


def head(title: str, pno: str, example: bool = False) -> str:
    tag = '<span class="tag">Filled example</span>' if example else ''
    return f'<div class="head"><h1>{E(title)}</h1><div class="r">{tag}<span class="pno">{E(pno)}</span></div></div>'


def fields(vals=("", "", "")) -> str:
    labels = ("Business", "Date reviewed", "Reviewed by (print and sign)")
    return '<div class="fields">' + "".join(
        f'<div class="field"><label>{E(lab)}</label><div class="line">{E(v)}</div></div>'
        for lab, v in zip(labels, vals)) + '</div>'


def matrix_table(rows) -> str:
    # 273 mm wide: dish 58 mm, 14 x 11.4 mm, notes the rest
    cols = '<colgroup><col style="width:58mm">' + '<col style="width:11.4mm">' * 14 + '<col></colgroup>'
    th = ('<tr><th class="lab">Dish, drink, sauce or side</th>'
          + "".join(f'<th class="al"><div>{E(n)}</div></th>' for n in NAMES)
          + '<th class="lab">Notes<br>Which cereal or nut? Why may contain?</th></tr>')
    body = []
    for dish, marks, note in rows:
        cells = "".join(
            f'<td class="cell{" alt" if i % 2 else ""}">{E(marks.get(n, ""))}</td>' for i, n in enumerate(NAMES))
        body.append(f'<tr><td class="hand">{E(dish)}</td>{cells}<td class="hand notes">{E(note)}</td></tr>')
    return f'<table>{cols}<thead>{th}</thead><tbody>{"".join(body)}</tbody></table>'


KEY = ('<div class="key"><span><b>&#10003; = contains</b> (it is an ingredient, or in one)</span>'
       '<span><b>M = may contain</b> (cross-contact you cannot rule out)</span>'
       '<span><b>Blank = not in the dish</b></span>'
       '<span>The 14 allergens are the ones UK food law says you must declare (FSA list).</span></div>')


def sheet_blank() -> str:
    intro = ('<b>How to use:</b> list every dish, drink, sauce and side. Work from recipes and ingredient labels, not memory. '
             'Tick each allergen it contains; write M only for real cross-contact; for cereals and tree nuts, write which one in Notes. '
             'Re-check after any recipe, ingredient or supplier change, then re-date and sign the sheet.')
    rows = [("", {}, "")] * 15
    return ('<section class="page">' + head("Allergen matrix", "Sheet 1")
            + f'<p class="intro">{intro}</p>' + fields() + matrix_table(rows) + KEY + FOOT + '</section>')


def sheet_example() -> str:
    intro = ('An example cafe menu. The first six dishes and their allergens are the FSA&rsquo;s own examples; your recipes '
             'and ingredient labels decide what goes in your boxes. Note the chips: no allergen in the recipe, but they share '
             'a fryer with battered fish, so they get an M.')
    rows = EXAMPLE + [("", {}, "")] * 7
    return ('<section class="page">' + head("Allergen matrix", "Sheet 2", example=True)
            + f'<p class="intro">{intro}</p>' + fields(("Example cafe", "16 / 11 / 26", "Head chef"))
            + matrix_table(rows) + KEY + FOOT + '</section>')


def sheet_howto() -> str:
    allergens = "".join(f'<li><b>{E(n)}</b>{" (" + E(x) + ")" if x else ""}</li>' for n, x in ALLERGENS)
    left = ('<div>'
            '<div class="card"><h4>The 14 allergens, as the FSA lists them</h4>'
            f'<ul style="columns: 2; column-gap: 6mm;">{allergens}</ul>'
            '<div class="src">Source: FSA, Allergen guidance for food businesses, updated 17 July 2026 (GOV.UK). '
            'This also applies to additives, processing aids and other substances in the final dish.</div></div>'
            '<div class="card"><h4>Fill it in</h4><ol>'
            '<li>List every dish and drink, plus sauces, dressings, garnishes and sides served on their own.</li>'
            '<li>Check every ingredient against its label or spec sheet. Compound items (stocks, sauces, bread) count.</li>'
            '<li>Tick &#10003; each allergen present. For cereals and tree nuts, name which one in Notes.</li>'
            '<li>Write M only where cross-contact is real and you cannot control it, such as a shared fryer.</li>'
            '<li>Date and sign it. Keep one copy at the pass and one front of house, and make sure staff know where it is.</li>'
            '</ol></div>'
            '<div class="card"><h4>Re-check the matrix when</h4><ul>'
            '<li>a recipe changes, or a new dish or special goes on;</li>'
            '<li>you change supplier or brand, or a delivery comes with a substitute;</li>'
            '<li>a supplier tells you an ingredient has changed;</li>'
            '<li>you make a last-minute swap during service.</li></ul></div>'
            '</div>')
    th = ('<tr><th class="lab" style="width:17mm">Date</th><th class="lab">Dish or ingredient</th>'
          '<th class="lab">What changed</th><th class="lab">Allergens added or removed</th>'
          '<th class="lab" style="width:24mm">Matrix updated by</th><th class="lab" style="width:20mm">Checked by</th></tr>')
    rows = "".join('<tr>' + '<td></td>' * 6 + '</tr>' for _ in range(15))
    right = ('<div><div style="font-size:8.4pt;font-weight:700;letter-spacing:-0.01em">Change log</div>'
             '<div style="font-size:7.2pt;color:#5c626b;margin-top:1mm;line-height:1.45">One line for every change that '
             'could move a tick. It shows when the matrix was last checked, and why.</div>'
             f'<table class="log" style="margin-top:2.6mm"><thead>{th}</thead><tbody>{rows}</tbody></table></div>')
    return ('<section class="page">' + head("How to use it, and keep it right", "Sheet 3")
            + f'<div class="grid2">{left}{right}</div>' + FOOT + '</section>')


def build_pdf() -> None:
    doc = (f'<!doctype html><html lang="en-GB"><head><meta charset="utf-8">'
           f'<title>Allergen matrix template (14 UK allergens) | Blueroll</title>{FONTS}'
           f'<style>{CSS}</style></head><body>{sheet_blank()}{sheet_example()}{sheet_howto()}</body></html>')
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "doc.html"
        src.write_text(doc, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--virtual-time-budget=8000", f"--print-to-pdf={PDF}", src.as_uri()],
                       check=True, capture_output=True)
    print("built", PDF.name)


# ---------------------------------------------------------------- XLSX

GREEN = "123227"
THIN = Side(style="thin", color="D9DEDB")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD_FILL = PatternFill("solid", fgColor=GREEN)
HEAD_FONT = Font(name="Arial", bold=True, color="FFFFFF", size=10)
BODY = Font(name="Arial", size=10)
MUTED = Font(name="Arial", size=9, color="5C626B")
FIRST, LAST = 2, 15             # allergen columns B..O
NOTES, CONTAINS = 16, 17        # P, Q
HEADER_ROW = 7


def contains_formula(r: int) -> str:
    parts = "&".join(
        f'IF(OR({get_column_letter(c)}{r}="{C}",{get_column_letter(c)}{r}="Y"),{get_column_letter(c)}${HEADER_ROW}&", ","")'
        for c in range(FIRST, LAST + 1))
    return f'=IFERROR(LEFT({parts},LEN({parts})-2),"")'


def matrix_sheet(ws, title: str, rows, filled: bool) -> None:
    ws.sheet_view.showGridLines = False
    ws["A1"] = title
    ws["A1"].font = Font(name="Arial", bold=True, size=18)
    ws["A2"] = ("How to use: one row per dish, drink, sauce or side. Pick ✓ (contains) or M (may contain) from the "
                "drop-down in each allergen column, or type Y for contains. Name the cereal or nut in Notes. Re-check after "
                "every recipe, ingredient or supplier change, then update the date below.")
    ws["A2"].font = MUTED
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=CONTAINS)
    ws.row_dimensions[2].height = 28
    # (label, label from, label to, value from, value to)
    labels = [("Business", "A", "A", "B", "F"), ("Date reviewed", "G", "J", "K", "L"),
              ("Reviewed by", "M", "O", "P", "Q")]
    vals = ("Example cafe", "16/11/2026", "Head chef") if filled else ("", "", "")
    for (lab, l1, l2, v1, v2), v in zip(labels, vals):
        if l1 != l2:
            ws.merge_cells(f"{l1}4:{l2}4")
        ws[f"{l1}4"] = lab
        ws[f"{l1}4"].font = Font(name="Arial", bold=True, size=9, color="8A9099")
        ws[f"{l1}4"].alignment = Alignment(horizontal="right" if l1 != "A" else "left", vertical="bottom")
        ws.merge_cells(f"{v1}4:{v2}4")
        ws[f"{v1}4"] = v
        ws[f"{v1}4"].font = BODY
        for col in range(ws[f"{v1}4"].column, ws[f"{v2}4"].column + 1):
            ws.cell(row=4, column=col).border = Border(bottom=Side(style="thin", color="9AA0A8"))
    ws["A5"] = ("✓ = contains   M = may contain (cross-contact you cannot rule out)   blank = not in the dish. "
                "The 14 allergens are the FSA list of allergens UK food law says you must declare.")
    ws["A5"].font = MUTED
    ws.merge_cells(start_row=5, start_column=1, end_row=5, end_column=CONTAINS)

    heads = ["Dish, drink, sauce or side"] + NAMES + ["Notes (which cereal or nut, why may contain)",
                                                      "Contains (for your menu)"]
    for i, h in enumerate(heads, start=1):
        cell = ws.cell(row=HEADER_ROW, column=i, value=h)
        cell.fill, cell.font, cell.border = HEAD_FILL, HEAD_FONT, BOX
        if FIRST <= i <= LAST:
            cell.alignment = Alignment(text_rotation=90, horizontal="center", vertical="bottom", wrap_text=True)
        else:
            cell.alignment = Alignment(vertical="bottom", wrap_text=True)
    ws.row_dimensions[HEADER_ROW].height = 118

    widths = {1: 34, NOTES: 30, CONTAINS: 44}
    for c in range(1, CONTAINS + 1):
        ws.column_dimensions[get_column_letter(c)].width = widths.get(c, 5.6)

    n_rows = 50
    first, last = HEADER_ROW + 1, HEADER_ROW + n_rows
    for k in range(n_rows):
        r = first + k
        dish, marks, note = rows[k] if k < len(rows) else ("", {}, "")
        ws.cell(row=r, column=1, value=dish or None)
        for c in range(FIRST, LAST + 1):
            v = marks.get(NAMES[c - FIRST], "")
            ws.cell(row=r, column=c, value=v or None).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=r, column=NOTES, value=note or None)
        if filled:
            # static text, so it shows even in apps that do not recalculate on open
            ws.cell(row=r, column=CONTAINS, value=", ".join(n for n in NAMES if marks.get(n) == C) or None)
        else:
            ws.cell(row=r, column=CONTAINS, value=contains_formula(r))
        for c in range(1, CONTAINS + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BOX
            if c in (1, NOTES, CONTAINS):
                cell.font = BODY if c != CONTAINS else MUTED
                cell.alignment = Alignment(vertical="center", wrap_text=True)
            else:
                cell.font = Font(name="Arial", size=11, bold=True, color="1D3A8A")
        ws.row_dimensions[r].height = 20

    rng = f"{get_column_letter(FIRST)}{first}:{get_column_letter(LAST)}{last}"
    dv = DataValidation(type="list", formula1=f'"{C},M"', allow_blank=True, showErrorMessage=False)
    dv.add(rng)
    ws.add_data_validation(dv)
    tl = f"{get_column_letter(FIRST)}{first}"
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR({tl}="{C}",{tl}="Y")'],
                                                   fill=PatternFill("solid", fgColor="FBE3C0")))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{tl}="M"'], fill=PatternFill("solid", fgColor="FFF4CC")))

    ws.freeze_panes = ws.cell(row=first, column=FIRST)
    ws.print_title_rows = f"{HEADER_ROW}:{HEADER_ROW}"
    ws.print_area = f"A1:{get_column_letter(CONTAINS)}{last}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = ws.page_margins.bottom = 0.5
    ws.oddFooter.left.text = "Blueroll free allergen matrix template, blueroll.app/allergen-matrix.html"
    ws.oddFooter.right.text = "Page &P of &N"


def howto_sheet(ws) -> None:
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 95
    r = 1
    ws.cell(row=r, column=1, value="How to use this allergen matrix").font = Font(name="Arial", bold=True, size=16)
    r += 2
    steps = [
        "List every dish and drink, plus sauces, dressings, garnishes and sides served on their own.",
        "Check every ingredient against its label or spec sheet. Compound items (stocks, sauces, bread) count.",
        "Tick each allergen present (✓ or Y). For cereals and tree nuts, name which one in Notes.",
        "Write M only where cross-contact is real and you cannot control it, such as a shared fryer.",
        "Fill in the date and who reviewed it. Print a copy for the pass and one for front of house.",
        "Re-check when a recipe changes, a new dish goes on, you change supplier or brand, a delivery comes with a "
        "substitute, or a supplier tells you an ingredient changed. Log each change on the Change log sheet.",
    ]
    for i, s in enumerate(steps, start=1):
        lab = ws.cell(row=r, column=1, value=f"Step {i}")
        lab.font, lab.alignment = Font(name="Arial", bold=True, size=10), Alignment(vertical="top")
        c = ws.cell(row=r, column=2, value=s)
        c.font, c.alignment = BODY, Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 28 if len(s) > 95 else 16
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="The 14 allergens (FSA list)").font = Font(name="Arial", bold=True, size=12)
    r += 1
    for n, x in ALLERGENS:
        ws.cell(row=r, column=1, value=n).font = Font(name="Arial", bold=True, size=10)
        c = ws.cell(row=r, column=2, value=x or None)
        c.font, c.alignment = BODY, Alignment(wrap_text=True)
        r += 1
    r += 1
    notes = [
        ("Also counts", "Additives, processing aids and any other substances present in the final dish (FSA)."),
        ("Source", FSA_GUIDANCE),
        ("Best practice", FSA_BEST_PRACTICE),
        ("Checked", "18 November 2026. This template is a record-keeping aid, not legal advice."),
        ("Keep it in the app", "In Blueroll the matrix comes from your recipes: blueroll.app/allergen-matrix.html"),
    ]
    for a, b in notes:
        ws.cell(row=r, column=1, value=a).font = Font(name="Arial", bold=True, size=10)
        c = ws.cell(row=r, column=2, value=b)
        c.font, c.alignment = BODY, Alignment(wrap_text=True)
        if b.startswith("https://"):
            c.hyperlink = b
            c.font = Font(name="Arial", size=10, color="1F7A52", underline="single")
        r += 1
    ws.page_setup.orientation = "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def log_sheet(ws) -> None:
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Change log"
    ws["A1"].font = Font(name="Arial", bold=True, size=16)
    ws["A2"] = "One line for every change that could move a tick. It shows when the matrix was last checked, and why."
    ws["A2"].font = MUTED
    heads = ["Date", "Dish or ingredient", "What changed", "Allergens added or removed", "Matrix updated by", "Checked by"]
    widths = [13, 30, 40, 30, 20, 18]
    for i, (h, w) in enumerate(zip(heads, widths), start=1):
        c = ws.cell(row=4, column=i, value=h)
        c.fill, c.font, c.border = HEAD_FILL, HEAD_FONT, BOX
        ws.column_dimensions[get_column_letter(i)].width = w
    for r in range(5, 45):
        for i in range(1, 7):
            c = ws.cell(row=r, column=i)
            c.border, c.font = BOX, BODY
        ws.row_dimensions[r].height = 20
    ws.freeze_panes = "A5"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def build_xlsx() -> None:
    wb = Workbook()
    matrix_sheet(wb.active, "Allergen matrix", [], filled=False)
    wb.active.title = "Allergen matrix"
    matrix_sheet(wb.create_sheet("Filled example"), "Allergen matrix: filled example", EXAMPLE, filled=True)
    howto_sheet(wb.create_sheet("How to use"))
    log_sheet(wb.create_sheet("Change log"))
    wb.properties.creator = "Blueroll"
    wb.properties.lastModifiedBy = "Blueroll"
    wb.properties.title = "Allergen matrix template (14 UK allergens)"
    wb.save(XLSX)
    print("built", XLSX.name)


# ---------------------------------------------------------------- images

def previews() -> None:
    out = ROOT / "uploads"
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "110", "-png", "-f", "1", "-l", "2", str(PDF), f"{tmp}/p"], check=True)
        pages = sorted(Path(tmp).glob("p-*.png"))
        for i, p in enumerate(pages, start=1):
            im = Image.open(p).convert("RGB")
            im.save(out / f"allergen-matrix-template-{i}.webp", "WEBP", quality=86, method=6)
            if i == 2:
                og(im)
    print("previews", len(pages))


def og(page: Image.Image) -> None:
    """1200x630: the filled example's top-left corner on the site's background."""
    w, h = page.size
    crop = page.crop((0, 0, w, int(w * 630 / 1200)))
    crop = crop.resize((1200, 630), Image.LANCZOS)
    crop.save(ROOT / "allergen-matrix-template-og.png", optimize=True)


def app_shot() -> None:
    """The app's matrix screen without the top bar (user name) and side bar."""
    src = Image.open(ROOT / "uploads" / "shot-allergen-matrix.png").convert("RGB")
    w, h = src.size  # 3024 x 1720
    crop = src.crop((470, 124, w, h))
    crop.thumbnail((1600, 1600), Image.LANCZOS)
    crop.save(ROOT / "uploads" / "allergen-matrix-app.webp", "WEBP", quality=86, method=6)
    print("app shot", crop.size)


def main() -> None:
    build_pdf()
    build_xlsx()
    previews()
    app_shot()


if __name__ == "__main__":
    main()
