#!/usr/bin/env python3
"""Build the two temperature-log landing pages (UK and US).

    fridge-temperature-log.html   UK, degrees C, source haccp-template:temperature:<placement> (gets the drip)
    food-temperature-log.html     US, degrees F, source us-template:temperature:<placement> (no British drip)

Same skeleton, layout and gate as the cleaning pages (_build/build_cleaning_pages.py).
PDFs and the preview images in uploads/ come from _build/build_temperature_pdfs.py.
Run from the repo root:

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
    "title": "Fridge Temperature Log Sheet: Free UK PDF (&deg;C) | Blueroll",
    "desc": "Free fridge and freezer temperature log sheet for UK kitchens, in &deg;C: a weekly log, a filled-in example, and a cooking, cooling and hot-holding log. A4 PDF.",
    "doc_name": "Fridge temperature log sheet (UK)",
    "crumb": "Fridge temperature log sheet",
    "h1": "Free fridge temperature log sheet",
    "lede": "A printable A4 weekly log in &deg;C for fridges, freezers, display chillers and the cold room, plus a filled-in example and a cooking, cooling and hot-holding log.",
    "button": "Get the free log",
    "note": "The PDF downloads straight away. We also email you our full 16-page HACCP pack, then two short follow-ups. Unsubscribe anytime.",
    "offer": True,
    "chip": ("Fridge 2 &middot; PK", "3.9&deg;C"),
    "bridge": "This same log fills itself in Blueroll",
    "alts": ["Blank weekly fridge and freezer temperature log in &deg;C, with the target temperature for each unit and a column for each day",
             "Filled-in fridge temperature log, with an out-of-range reading circled and what was done written below",
             "Blank cooking, cooling and hot-holding log with the UK safe temperatures"],
    "sections": [
        {"type": "split", "sheet": 2, "h2": "How to use the log", "blocks": [
            ("ol", ["Tape the sheet to the fridge door.",
                    "Read every unit when you open and before you close, from the display or a probe in water kept in the unit.",
                    "Write the number, the time and your initials, not a tick.",
                    "Circle a reading out of range, write down what you did, and recheck.",
                    "Check your probe thermometer in iced water and write down the result."]),
            ("p", 'The <a href="free-haccp-template.html">16-page HACCP pack</a>, the <a href="kitchen-cleaning-schedule-template.html">kitchen cleaning schedule</a> and our <a href="sfbb-guide.html">SFBB guide</a> cover the rest of the paperwork. Kitchens in Scotland can use the <a href="haccp-template-scotland.html">CookSafe HACCP template</a>.')]},
        {"type": "cards", "h2": "Safe temperatures in the UK", "intro": [
            ("p", "The numbers an inspector expects to see on your log and your probe.")],
         "cards": [("5&deg;C", "Fridges", "Set fridges and chilled display to 5&deg;C or below."),
                   ("8&deg;C", "Chilled food, at most", "The law in England, Wales and Northern Ireland, and the recommendation in Scotland."),
                   (f"{M}18&deg;C", "Freezers", "Keep frozen food at &minus;18&deg;C or below."),
                   ("70&deg;C", "Cooking", "A core temperature of 70&deg;C for 2 minutes, or 75&deg;C for 30 seconds."),
                   ("63&deg;C", "Hot holding", "Keep hot food at 63&deg;C or above."),
                   ("82&deg;C", "Reheating in Scotland", "Elsewhere, reheat until steaming hot all the way through, and only once.")],
         "after": [("p", f"A probe should read between {M}1&deg;C and 1&deg;C in iced water, and between 99&deg;C and 101&deg;C in boiling water.")]},
        {"type": "split", "sheet": 3, "h2": "What the law expects", "blocks": [
            ("p", "Chilled food must be kept at 8&deg;C or below in England, Wales and Northern Ireland. The Food Standards Agency recommends setting fridges to 5&deg;C or below to keep that margin through door openings and deliveries."),
            ("p", "Safer Food, Better Business asks you to check fridges and chilled display at least once a day, starting with your opening checks. In England, holding food above 8&deg;C, or hot food below 63&deg;C, is an offence, with time-limited exceptions for service and display."),
            ("p", "The third sheet records core temperatures for cooking, cooling, reheating and hot holding.")]},
        {"type": "split", "shot": "checklists", "h2": "How Blueroll does it", "blocks": [
            ("p", 'In Blueroll the same checks are on your team&rsquo;s phones. Every check has a safe range, so a reading outside it is flagged the moment it is logged, the manager is notified, and the corrective action is recorded on the same entry. See <a href="haccp-checklists.html">how the checklists work</a>.'),
            ("p", 'It costs &pound;24.99 per site per month after a 14-day free trial, with no card needed, and we set it up for you, free. <a href="https://app.blueroll.app/">Start the free trial</a>.')]},
    ],
    "faq": [
        ("How often should I record fridge temperatures?",
         "At least once a day, and better twice: once when you open and once before you close. Record more often for a fridge that is opened all through service or has given trouble. Write the actual number each time, not a tick."),
        ("What temperature should a commercial fridge be in the UK?",
         f"5&deg;C or below. The legal maximum for chilled food in England, Wales and Northern Ireland is 8&deg;C, so 5&deg;C leaves a margin for door openings and deliveries. Freezers should be at {M}18&deg;C or below."),
        ("What should I do when a fridge reading is too high?",
         "Check again with a probe, in the food or in water kept in the unit, and look for the cause: a door left open, a delivery just loaded, a blocked fan. If the unit stays above 5&deg;C, move the food to another fridge and call an engineer. If you cannot show the food stayed safe, throw it away, and write down the reading, the time, what you did and the recheck."),
        ("Is this template really free?",
         "Yes. No charge, no account and no watermark. Enter your email, the PDF downloads, and you can print it for as long as paper works for you."),
    ],
    "end_h2": "Get the free fridge temperature log",
    "sources": [
        ("Food hygiene for businesses: chilling and freezing", "https://www.gov.uk/food-hygiene-businesses/chilling-and-freezing", "Food Standards Agency, GOV.UK"),
        ("Food hygiene for businesses: cooking food safely", "https://www.gov.uk/food-hygiene-businesses/cooking", "Food Standards Agency, GOV.UK"),
        ("Safer food, better business for caterers", "https://www.gov.uk/government/publications/safer-food-better-business-for-caterers", "Food Standards Agency, GOV.UK"),
        ("The Food Safety and Hygiene (England) Regulations 2013, Schedule 4", "https://www.legislation.gov.uk/uksi/2013/2996/schedule/4", "legislation.gov.uk"),
        ("The Food Hygiene (Scotland) Regulations 2006, Schedule 4", "https://www.legislation.gov.uk/ssi/2006/3/schedule/4", "legislation.gov.uk"),
    ],
    "exit_h2": "Take the log with you",
    "exit_p": "Three printable sheets: the weekly fridge log, a filled-in example, and the cooking and cooling log, straight to your Downloads.",
}

US = {
    "file": "food-temperature-log.html", "url": US_URL, "uk_url": UK_URL, "us_url": US_URL, "lang": "en-US",
    "slug": "us-temperature", "source": "us-template:temperature", "subject": "New food temperature log download (US)",
    "pdf": "blueroll-food-temperature-log.pdf", "img": "temperature-us-page",
    "title": "Food Temperature Log Sheet: Free Printable PDF | Blueroll",
    "desc": "Free food temperature log sheets in &deg;F: a cooler and freezer log, a filled-in example, and a cooking, hot-holding and cooling log based on the FDA Food Code.",
    "doc_name": "Food temperature log sheet (US)",
    "crumb": "Food temperature log sheet",
    "h1": "Free food temperature log sheet",
    "lede": "A printable weekly log in &deg;F for the walk-in, reach-ins, prep-line cooler and freezers, plus a filled-in example and a cooking, hot-holding and cooling log with Food Code temperatures.",
    "button": "Get the free log",
    "note": "The PDF downloads right away. We don&rsquo;t share your email.",
    "chip": ("Walk-in cooler &middot; DL", "37&deg;F"),
    "bridge": "This same log fills itself in Blueroll",
    "alts": ["Blank weekly cooler and freezer temperature log in &deg;F, with the target temperature for each unit and a column for each day",
             "Filled-in cooler and freezer temperature log, with an out-of-range reading circled and what was done written below",
             "Food temperature log for cooking, hot holding and cooling, with FDA Food Code temperatures"],
    "sections": [
        {"type": "split", "sheet": 2, "h2": "How to use the log", "blocks": [
            ("ol", ["Tape the sheet to the walk-in door.",
                    "Read every cooler and freezer at opening and before close.",
                    "Write the number, the time and your initials, not a check mark.",
                    "Circle a reading out of range, write down what you did, and recheck.",
                    "Use the third sheet for final cooking temperatures, hot holding and cooling."]),
            ("p", 'The <a href="restaurant-cleaning-checklist.html">restaurant cleaning checklist</a> and the <a href="restaurant-health-inspection-checklist.html">restaurant health inspection checklist</a> are free too.')]},
        {"type": "cards", "h2": "FDA Food Code temperatures", "intro": [
            ("p", "Your state or county may have adopted a different edition of the Food Code, and its rules come first.")],
         "cards": [("41&deg;F", "Cold holding", "Coolers, reach-ins and the prep line. Freezers are usually kept at 0&deg;F or below."),
                   ("135&deg;F", "Hot holding", "Hot-held food stays at 135&deg;F or above."),
                   ("165&deg;F", "Poultry and reheating", "Poultry and stuffed foods for under a second. Food reheated for hot holding for 15 seconds, within 2 hours."),
                   ("155&deg;F", "Ground beef and pork", "For 17 seconds."),
                   ("145&deg;F", "Steaks, fish and eggs", "Steaks, chops, fish and eggs for immediate service, for 15 seconds."),
                   ("6 hours", "Cooling", "From 135&deg;F to 70&deg;F within 2 hours, then to 41&deg;F within 6 hours in total.")]},
        {"type": "split", "sheet": 3, "h2": "What the Food Code expects", "blocks": [
            ("p", "Inspectors check cold holding, hot holding and cooling early: improper holding temperatures are one of the five foodborne illness risk factors the FDA Food Code is built to control."),
            ("p", f"Your log should show a real reading for every unit, who took it, and what you did when a reading was out of range. How inspections are scored in {P.CITY_LINKS}.")]},
        {"type": "split", "shot": "checklists", "h2": "How Blueroll does it", "blocks": [
            ("p", 'In Blueroll the same checks are on your team&rsquo;s phones. Every check has a safe range, so a reading outside it is flagged the moment it is logged, the manager is notified, and the corrective action is recorded on the same entry. See <a href="haccp-checklists.html">how the checklists work</a>.'),
            ("p", 'Try it free for 14 days, no card needed. <a href="https://app.blueroll.app/">Start the free trial</a>.')]},
    ],
    "faq": [
        ("What temperature should a walk-in cooler be?",
         "41&deg;F or below for cold holding under the FDA Food Code. Many kitchens set the walk-in at 36-38&deg;F to leave a margin for door openings and deliveries. A walk-in freezer is usually kept at 0&deg;F or below."),
        ("How often should I check and log food temperatures?",
         "Coolers and freezers at least at opening and before close; hot-held food every 2 to 4 hours; cooling food at the 2-hour and 6-hour marks. Write the actual number each time, not a check mark."),
        ("What should I do when a cooler reading is too high?",
         "Check again with a calibrated probe thermometer in the food itself, and find the cause: a door left open, lids off the prep-line cooler, a delivery just loaded, a blocked condenser. Move the food to a unit that is holding temperature and call for service if the unit does not recover. Decide what happens to the food using your local code&rsquo;s time limits; when in doubt, throw it out. Write down the reading, the time, what you did and the recheck."),
        ("Is this log free?",
         "Yes. No charge, no account and no watermark. Enter your email, the PDF downloads, and you can print as many copies as you need."),
    ],
    "end_h2": "Get the free food temperature log",
    "sources": [P.FOOD_CODE],
    "exit_h2": "Take the log with you",
    "exit_p": "Three printable sheets: the cooler and freezer log, a filled-in example, and the cooking, hot-holding and cooling log.",
}


def main():
    P.build((UK, US))


if __name__ == "__main__":
    main()
