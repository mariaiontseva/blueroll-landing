#!/usr/bin/env python3
"""Build the free allergen matrix template (14 UK allergens) and its page images.

  blueroll-allergen-matrix-template.pdf    A4 landscape: blank matrix, filled example, how-to + change log
  blueroll-allergen-matrix-template.xlsx   the same matrix to fill in on screen (Excel, Google Sheets, Numbers)
  uploads/allergen-matrix-template-1.webp  page previews for allergen-matrix.html
  uploads/allergen-matrix-template-2.webp
  uploads/allergen-matrix-app.webp         the app's matrix screen, cropped to the content (no names)
  allergen-matrix-template-og.png          1200x630 share image

Same look as the cleaning and temperature sheets (shared CSS and helpers in
_build/build_cleaning_pdfs.py; filled example in handwriting). The 14 allergens and their examples are the FSA's
wording from "Allergen guidance for food businesses" (GOV.UK, updated 17 July 2026).
The example dishes are the FSA's own examples from "Allergen information for
non-prepacked foods: best practice" (24 February 2025), plus a coffee and chips.

Run from the repo root:

    python3 _build/build_allergen_matrix.py
"""
import html
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import build_cleaning_pdfs as B  # noqa: E402  shared look of the printable templates

ROOT = Path(__file__).resolve().parent.parent
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

NAME = "allergen matrix template"
PAD = "10mm 12mm 8mm"

EXTRA_CSS = """
.matrix th.al { padding: 1.8mm 0; }
.matrix th.al div { writing-mode: vertical-rl; transform: rotate(180deg); height: 26mm; margin: 0 auto;
                    font-size: 8.5pt; line-height: 1.12; text-align: left; white-space: normal; }
.matrix th.notes span { display: block; font-weight: 400; color: #454b53; margin-top: .8mm; }
.matrix td.cell { font-size: 15pt; }
.split { flex: 1 1 auto; min-height: 0; display: grid; grid-template-columns: 116mm 1fr; grid-template-rows: minmax(0, 1fr);
         column-gap: 10mm; margin-top: 5mm; }
.split .grow { margin-top: 0; }
.split .text { display: flex; flex-direction: column; gap: 4.2mm; }
.split .text ul.two { columns: 2; column-gap: 6mm; }
.split .text li { break-inside: avoid; }
.split .src { font-size: 8pt; color: #5c626b; margin-top: 1.4mm; }
"""


def fields(vals=("", "", "")) -> str:
    labels = ("Business", "Date reviewed", "Reviewed by (print and sign)")
    return B.fields(*zip(labels, vals))


def matrix_table(rows) -> str:
    # 273 mm wide: dish 58 mm, 14 x 11.4 mm, notes the rest
    cols = '<colgroup><col style="width:58mm">' + '<col style="width:11.4mm">' * 14 + '<col></colgroup>'
    th = ('<tr><th>Dish, drink, sauce or side</th>'
          + "".join(f'<th class="al v"><div>{E(n)}</div></th>' for n in NAMES)
          + '<th class="notes v">Notes<span>Which cereal or nut? Why may contain?</span></th></tr>')
    body = []
    for dish, marks, note in rows:
        cells = "".join(f'<td class="cell v">{E(marks.get(n, ""))}</td>' for n in NAMES)
        body.append(f'<tr class="w"><td class="hand">{E(dish)}</td>{cells}<td class="hand v">{E(note)}</td></tr>')
    return f'<table class="matrix">{cols}<thead>{th}</thead><tbody>{"".join(body)}</tbody></table>'


def sheet_blank() -> str:
    lead = ("One row per dish, drink, sauce or side. Tick &#10003; each allergen it contains, write M for may contain "
            "(cross-contact you cannot rule out), leave the rest blank.")
    return B.page(B.head("Allergen matrix", lead), fields(), B.grow(matrix_table([("", {}, "")]), extend=True),
                  B.foot(NAME))


def sheet_example() -> str:
    lead = ("Filled example. The first six dishes and their allergens are the FSA&rsquo;s own examples. "
            "The chips share a fryer with battered fish, so they get an M.")
    return B.page(B.head("Allergen matrix", lead), fields(("Example cafe", "16 / 11 / 26", "Head chef")),
                  B.grow(matrix_table(EXAMPLE + [("", {}, "")]), extend=True), B.foot(NAME))


def sheet_log() -> str:
    allergens = "".join(f'<li><b>{E(n)}</b>{" (" + E(x) + ")" if x else ""}</li>' for n, x in ALLERGENS)
    left = ('<div class="text">'
            '<div><h3>The 14 allergens, as the FSA lists them</h3>'
            f'<ul class="two">{allergens}</ul>'
            '<div class="src">Source: FSA, Allergen guidance for food businesses, updated 17 July 2026 (GOV.UK). '
            'This also applies to additives, processing aids and other substances in the final dish.</div></div>'
            '<div><h3>Fill it in</h3><ol>'
            '<li>List every dish and drink, plus sauces, dressings, garnishes and sides served on their own.</li>'
            '<li>Check every ingredient against its label or spec sheet. Compound items (stocks, sauces, bread) count.</li>'
            '<li>Tick &#10003; each allergen present. For cereals and tree nuts, name which one in Notes.</li>'
            '<li>Write M only where cross-contact is real and you cannot control it, such as a shared fryer.</li>'
            '<li>Date and sign it. Keep one copy at the pass and one front of house, and make sure staff know where it is.</li>'
            '</ol></div>'
            '<div><h3>Re-check the matrix when</h3><ul>'
            '<li>a recipe changes, or a new dish or special goes on;</li>'
            '<li>you change supplier or brand, or a delivery comes with a substitute;</li>'
            '<li>a supplier tells you an ingredient has changed;</li>'
            '<li>you make a last-minute swap during service.</li></ul></div>'
            '</div>')
    th = ('<tr><th style="width:17mm">Date</th><th class="v">Dish or ingredient</th>'
          '<th class="v">What changed</th><th class="v" style="width:31mm">Allergens added or removed</th>'
          '<th class="v" style="width:22mm">Updated by</th><th class="v" style="width:22mm">Checked by</th></tr>')
    row = '<tr class="w"><td class="hand"></td>' + '<td class="hand v"></td>' * 5 + '</tr>'
    log = B.grow(f'<table><thead>{th}</thead><tbody>{row}</tbody></table>', extend=True)
    lead = "One line for every change that could move a tick. It shows when the matrix was last checked, and why."
    return B.page(B.head("Allergen change log", lead), f'<div class="split">{left}{log}</div>', B.foot(NAME))


def build_pdf() -> None:
    B.render([sheet_blank(), sheet_example(), sheet_log()], "A4 landscape", "297mm", "210mm", PDF,
             "Allergen matrix template (14 UK allergens) | Blueroll", pad=PAD, extra_css=EXTRA_CSS)


# ---------------------------------------------------------------- XLSX

THIN = Side(style="thin", color="D9DEDB")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD_FILL = PatternFill("solid", fgColor="F1F4F2")
HEAD_FONT = Font(name="Arial", bold=True, color="16181D", size=10)
HEAD_BOX = Border(left=THIN, right=THIN, top=THIN, bottom=Side(style="thin", color="9AA19D"))
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
        cell.fill, cell.font, cell.border = HEAD_FILL, HEAD_FONT, HEAD_BOX
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
        c.fill, c.font, c.border = HEAD_FILL, HEAD_FONT, HEAD_BOX
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

def previews() -> Image.Image:
    """uploads/allergen-matrix-template-1.webp and -2.webp. Returns the filled example page (for og())."""
    pages = B.page_images(PDF, 1754, 1, 2)
    for i, im in enumerate(pages, start=1):
        im.save(ROOT / "uploads" / f"allergen-matrix-template-{i}.webp", "WEBP", quality=86, method=6)
    print("previews", len(pages))
    return pages[1]


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
    og(previews())
    app_shot()


if __name__ == "__main__":
    main()
