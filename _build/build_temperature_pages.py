#!/usr/bin/env python3
"""Build the two temperature-log landing pages (UK and US).

    fridge-temperature-log.html   UK, degrees C, source haccp-template:temperature:<placement> (gets the drip)
    food-temperature-log.html     US, degrees F, source us-template:temperature:<placement> (no British drip)

Same skeleton and gate as the cleaning pages (_build/build_cleaning_pages.py).
PDFs come from _build/build_temperature_pdfs.py. Run from the repo root:

    python3 _build/build_temperature_pages.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_cleaning_pages as P  # noqa: E402

UK_URL = "https://blueroll.app/fridge-temperature-log.html"
US_URL = "https://blueroll.app/food-temperature-log.html"
M = "&minus;"

UK = {
    "file": "fridge-temperature-log.html", "url": UK_URL, "uk_url": UK_URL, "us_url": US_URL, "lang": "en-GB",
    "slug": "temperature", "source": "haccp-template:temperature", "subject": "New fridge temperature log download (UK)",
    "pdf": "blueroll-fridge-temperature-log.pdf", "img": "temperature-uk-page",
    "title": "Fridge Temperature Log Sheet: Free UK PDF | Blueroll",
    "desc": "Free fridge and freezer temperature log sheet for UK kitchens, in &deg;C: a weekly log, a filled-in example, and a cooking, cooling and hot-holding log. Printable A4 PDF.",
    "doc_name": "Fridge temperature log sheet (UK)",
    "crumb": "Fridge temperature log sheet",
    "badge": "Free template &middot; 3 printable A4 sheets",
    "big": "The temperature log,<br>ready for the fridge door",
    "h1": "Free fridge temperature log sheet for UK kitchens (&deg;C)",
    "sub": "A printable weekly log for fridges, freezers, display chillers and the cold room, a filled-in example, and a cooking, cooling and hot-holding log with the safe temperatures printed on it. Enter your work email and the PDF downloads straight away.",
    "button": "Get the free log",
    "note": "The PDF downloads straight away. We also email you our full 16-page HACCP pack, plus two short follow-ups. Unsubscribe anytime.",
    "chip": ("Fridge 2 &middot; PK", "3.9&deg;C"),
    "bridge": "This same log fills itself in Blueroll",
    "meta": "A4 &middot; weekly fridge log &middot; filled example &middot; cooking and cooling log",
    "inside": "Inside the PDF &middot; 3 sheets &middot; A4",
    "inside_h2": "Tape it to the fridge door, fill it in twice a day",
    "figs": [(-2, "Weekly fridge and freezer temperature log, blank", "SHEET 1 &middot; WEEKLY FRIDGE LOG"),
             (1.2, "Fridge temperature log, filled-in example from St James's Cafe", "SHEET 2 &middot; FILLED EXAMPLE"),
             (-1, "Cooking, cooling and hot-holding log with UK safe temperatures", "SHEET 3 &middot; COOKING AND COOLING")],
    "chips_label": "More free records",
    "chips": [("Full HACCP pack (16 pages)", "/free-haccp-template.html"), ("Kitchen cleaning schedule", "/kitchen-cleaning-schedule-template.html"),
              ("SFBB guide", "/sfbb-guide.html"), ("Scotland (CookSafe)", "/haccp-template-scotland.html")],
    "mid_title": "Get the log, free.",
    "mid_sub": "weekly fridge log &middot; filled example &middot; cooking and cooling log",
    "bottom_title": "Still scrolling?<br>The log is one click away.",
    "body": [
        ("h2", "What a fridge temperature log needs to show"),
        ("p", "An Environmental Health Officer will look at your fridge thermometer, then at your log. The log should show a real reading for every unit each day, the time, the initials of whoever took it, and what you did when a reading was out of range. A column of ticks, or a week written up in one pen, tells the inspector the checks were not done."),
        ("h3", "Safe temperatures in the UK"),
        ("rows", [("FRIDGES", "5&deg;C or below, as the Food Standards Agency recommends. 8&deg;C is the legal maximum for chilled food in England, Wales and Northern Ireland; in Scotland chilled food must be kept in a fridge or a cool place."),
                  ("FREEZERS", f"{M}18&deg;C or below."),
                  ("HOT FOOD", "Cook to a core of 75&deg;C, or an equivalent such as 70&deg;C for 2 minutes. Hold hot food at 63&deg;C or above. Reheat to 75&deg;C, or 82&deg;C in Scotland."),
                  ("COOLING", "Get cooked food into the fridge as quickly as possible, ideally within 90 minutes.")]),
        ("h3", "When a reading is out of range"),
        ("ol", ["Check again with a probe thermometer, in the food or in a glass of water kept in the unit.",
                "Look for the cause: a door left open, a delivery just loaded, a hot tray put in, a blocked fan.",
                "Move the food to another fridge if the unit stays above 5&deg;C, and call an engineer if it does not recover.",
                "Decide what happens to the food. If you cannot show it stayed safe, throw it away.",
                "Write it down: the reading, the time, what you did and the recheck."]),
        ("p", "A circled reading with a note beside it is good evidence: it shows a kitchen that checks and acts. The filled-in example in the PDF shows how to record one."),
        ("h3", "Probe thermometer checks"),
        ("p", f"Check your probe regularly. In iced water it should read between {M}1&deg;C and +1&deg;C, and in boiling water between 99&deg;C and 101&deg;C. The weekly sheet has a row for the result."),
        ("p", 'Need the rest of the paperwork? The <a href="free-haccp-template.html">free 16-page HACCP pack</a> adds the daily opening checklist, delivery checks and the allergen matrix, and the <a href="kitchen-cleaning-schedule-template.html">kitchen cleaning schedule</a> covers cleaning.'),
    ],
    "faq": [
        ("How often should I record fridge temperatures?",
         "At least once a day, and better twice: once when you open and once before you close. Record more often for a fridge that is opened all through service or has given trouble. Write the actual number each time, not a tick."),
        ("What temperature should a commercial fridge be in the UK?",
         f"5&deg;C or below. The legal maximum for chilled food in England, Wales and Northern Ireland is 8&deg;C, so 5&deg;C leaves a margin for door openings and deliveries. Freezers should be at {M}18&deg;C or below."),
        ("Is this template really free?",
         "Yes. No charge, no account and no watermark. Enter your email, the PDF downloads, and you can print it for as long as paper works for you."),
    ],
    "dark_h2": "Or stop chasing the clipboard.",
    "dark_p": "The same checks on your team&rsquo;s phones: every reading with a name and a time, temperatures that flag themselves, and the log ready for the inspector. &pound;24.99 a month.",
    "dark_btn": "Start your free 14-day trial",
    "dark_small": "14 days free. No card needed. We set it up for you, free.",
    "dark_rows": [("Fridge 1", "3.2&deg;C"), ("Fridge 2", "3.9&deg;C"), ("Freezer", f"{M}18.4&deg;C")],
    "exit_h2": "Take the log with you",
    "exit_p": "Three printable sheets: the weekly fridge log, a filled-in example, and the cooking and cooling log, straight to your Downloads.",
}

US = {
    "file": "food-temperature-log.html", "url": US_URL, "uk_url": UK_URL, "us_url": US_URL, "lang": "en-US",
    "slug": "us-temperature", "source": "us-template:temperature", "subject": "New food temperature log download (US)",
    "pdf": "blueroll-food-temperature-log.pdf", "img": "temperature-us-page",
    "title": "Food Temperature Log Sheet: Free Printable PDF for Restaurants | Blueroll",
    "desc": "Free food temperature log sheets in &deg;F: a walk-in cooler and freezer log, a filled-in example, and a cooking, hot-holding and cooling log. Based on the FDA Food Code.",
    "doc_name": "Food temperature log sheet (US)",
    "crumb": "Food temperature log sheet",
    "badge": "Free download &middot; 3 printable sheets",
    "big": "Write the number,<br>not a check mark",
    "h1": "Free food temperature log sheet (PDF, &deg;F)",
    "sub": "A printable weekly log for the walk-in cooler, reach-ins, prep-line cooler and freezers, a filled-in example, and a cooking, hot-holding and cooling log with FDA Food Code temperatures printed on it. Enter your work email and the PDF downloads right away.",
    "button": "Get the free log",
    "note": "The PDF downloads right away. We don&rsquo;t share your email.",
    "chip": ("Walk-in cooler &middot; DL", "37&deg;F"),
    "bridge": "This same log fills itself in Blueroll",
    "meta": "US Letter &middot; cooler and freezer log &middot; filled example &middot; cooking and cooling log",
    "inside": "Inside the PDF &middot; 3 sheets &middot; US Letter",
    "inside_h2": "Tape it to the walk-in door, fill it in twice a day",
    "figs": [(-2, "Weekly cooler and freezer temperature log, blank", "SHEET 1 &middot; COOLER AND FREEZER LOG"),
             (1.2, "Cooler and freezer temperature log, filled-in example", "SHEET 2 &middot; FILLED EXAMPLE"),
             (-1, "Food temperature log with a cooling log and FDA Food Code temperatures", "SHEET 3 &middot; COOKING AND COOLING")],
    "chips_label": "Cleaning checklist and city guides",
    "chips": [("Restaurant cleaning checklist", "/restaurant-cleaning-checklist.html"), ("New York City", "/nyc-restaurant-grade.html"),
              ("Los Angeles", "/la-restaurant-grade.html"), ("San Francisco", "/sf-restaurant-inspection.html"),
              ("Chicago", "/chicago-restaurant-inspection.html"), ("Seattle", "/seattle-restaurant-inspection.html")],
    "mid_title": "Get the log, free.",
    "mid_sub": "cooler and freezer log &middot; filled example &middot; cooking and cooling log",
    "bottom_title": "Still scrolling?<br>The log is one click away.",
    "body": [
        ("h2", "What a food temperature log should show"),
        ("p", "Health inspectors check cold holding, hot holding and cooling early, because improper holding temperatures are one of the FDA&rsquo;s five main risk factors for foodborne illness. Your log should show a real reading for every unit, ideally at opening and before close, who took it, and what you did when a reading was out of range."),
        ("h3", "FDA Food Code temperatures"),
        ("rows", [("HOLDING", "Cold holding at 41&deg;F or below. Hot holding at 135&deg;F or above. Freezers are usually kept at 0&deg;F or below."),
                  ("COOKING", "Poultry and stuffed foods 165&deg;F for under a second. Ground beef and pork 155&deg;F for 17 seconds. Steaks, chops, fish and eggs for immediate service 145&deg;F for 15 seconds."),
                  ("COOLING", "From 135&deg;F to 70&deg;F within 2 hours, then to 41&deg;F within 6 hours in total."),
                  ("REHEATING", "Food reheated for hot holding reaches 165&deg;F for 15 seconds within 2 hours.")]),
        ("h3", "When a reading is out of range"),
        ("ol", ["Check again with a calibrated probe thermometer, in the food itself.",
                "Find the cause: a door left open, lids off the prep-line cooler, a delivery just loaded, a blocked condenser.",
                "Move the food to a unit that is holding temperature, and call for service if the unit does not recover.",
                "Decide what happens to the food using your local code&rsquo;s time limits. When in doubt, throw it out.",
                "Write down the reading, the time, what you did and the recheck."]),
        ("p", "Your state or county may have adopted a different edition of the Food Code, and its rules come first. The city guides below explain how each inspection system scores."),
    ],
    "faq": [
        ("What temperature should a walk-in cooler be?",
         "41&deg;F or below for cold holding under the FDA Food Code. Many kitchens set the walk-in at 36-38&deg;F to leave a margin for door openings and deliveries. A walk-in freezer is usually kept at 0&deg;F or below."),
        ("How often should I check and log food temperatures?",
         "Coolers and freezers at least at opening and before close; hot-held food every 2 to 4 hours; cooling food at the 2-hour and 6-hour marks. Write the actual number each time, not a check mark."),
        ("Is this log free?",
         "Yes. No charge, no account and no watermark. Enter your email, the PDF downloads, and you can print as many copies as you need."),
    ],
    "dark_h2": "Or put the log on your team&rsquo;s phones.",
    "dark_p": "Every reading with a name and a time, ready to show your health inspector.",
    "dark_btn": "Try Blueroll free for 14 days",
    "dark_small": "14 days free. No card needed.",
    "dark_rows": [("Walk-in cooler", "37&deg;F"), ("Prep-line cooler", "39&deg;F"), ("Walk-in freezer", f"{M}2&deg;F")],
    "exit_h2": "Take the log with you",
    "exit_p": "Three printable sheets: the cooler and freezer log, a filled-in example, and the cooking, hot-holding and cooling log.",
}


def main():
    for cfg in (UK, US):
        page = P.build_head(cfg) + P.build_body(cfg) + "\n" + P.build_tail(cfg)
        assert page.count('data-gate="') == 4, cfg["file"]
        (P.ROOT / cfg["file"]).write_text(page)
        print("built", cfg["file"])


if __name__ == "__main__":
    main()
