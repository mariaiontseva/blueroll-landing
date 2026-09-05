# Segment config for the HACCP template satellite pages.
# The pack's page count lives HERE and nowhere else.
PAGES_COUNT = 16

FREE_FAQ = (
    "Is this template really free?",
    'Yes, there is no charge, account or watermark. Enter your email to download the PDF, then print it and use it for as long as paper works for you.',
)

SEGMENTS = {
    "cafe": {
        "file": "haccp-template-cafe.html",
        "title": "HACCP Template for Cafes &amp; Coffee Shops: Free UK PDF | Blueroll",
        "desc": "Free HACCP plan template for UK cafes and coffee shops. Fridge and milk temperature logs, cleaning schedule, allergen reference. Free 16-page PDF.",
        "h1": "Free HACCP template for cafes &amp; coffee shops",
        "breadcrumb": "HACCP template for cafes",
        "sub": "This free HACCP plan template fits a UK cafe or coffee shop out of the box: fridge and milk temperature logs, a cleaning schedule that covers the espresso machine, delivery checks and corrective actions. Enter your work email for instant access to the 16-page pack.",
        "who_rows": [
            ("GELATERIA<br>LONDON", "Downloaded this pack in spring, ran it on paper, now runs the same checks digitally."),
            ("COFFEE VAN<br>DEVON", "Prints the daily sheet, clips it by the grinder, files it weekly."),
            ("TAPROOM<br>CORNWALL", "Downloaded the day after opening. Rated 5 a week later."),
        ],
        "faq": [
            ("Is this enough for a cafe EHO inspection?",
             'Yes, as your daily records. The sheets cover what an EHO asks a cafe for first: fridge and milk temperatures, cleaning, deliveries and corrective actions. Fill them in daily, sign them and file by week. When paper gets tedious, <a href="haccp-checklists.html">digital HACCP checklists</a> run the same checks on your team\'s phones.'),
            ("Does it cover allergens for counter cakes and sandwiches?",
             'The quick reference card lists all 14 UK allergens to pin by the counter. If you sell items packed on site, PPDS labelling under Natasha\'s Law also applies; our <a href="14-allergens-uk.html">14 allergens guide</a> and the <a href="haccp-template-bakery.html">bakery version of this template</a> cover it in more depth.'),
            FREE_FAQ,
        ],
    },
    "takeaway": {
        "file": "haccp-template-takeaway.html",
        "title": "HACCP Template for Takeaways: Free UK PDF | Blueroll",
        "desc": "Free HACCP plan template for UK takeaways. Hot-holding and reheating logs, opening checks, cleaning schedule, delivery checks. Free 16-page PDF.",
        "h1": "Free HACCP template for takeaways",
        "breadcrumb": "HACCP template for takeaways",
        "sub": "This free HACCP plan template is built for takeaway reality: opening checks before the rush, hot-holding and reheating temperatures, cleaning, delivery checks and corrective actions. Enter your work email for instant access to the 16-page pack.",
        "who_rows": [
            ("GRILL TAKEAWAY<br>LONDON", "Downloaded the pack in August; opening checks done before the doors open."),
            ("MOMO'S CAFE", "Runs the daily sheet through service, files it by week."),
            ("SCHOOL KITCHEN<br>LONDON", "Same sheets at the pass, filed weekly."),
        ],
        "faq": [
            ("Will this help my hygiene rating for Just Eat or Deliveroo?",
             'Indirectly, yes. Delivery platforms require a minimum food hygiene rating, and complete daily records are a big part of the "confidence in management" score an EHO gives. The sheets here are those records; our guide to <a href="food-hygiene-ratings-explained.html">food hygiene ratings</a> explains how the score is built.'),
            ("What temperatures matter most in a takeaway?",
             'Hot holding at 63&deg;C or above, reheating to 82&deg;C in Scotland (75&deg;C elsewhere in the UK), fridges below 5&deg;C. The quick reference card in the pack has the full list to pin by the fryer, and the weekly log gives you a place to record them; <a href="haccp-template-food-truck.html">street food traders</a> use the same sheets.'),
            FREE_FAQ,
        ],
    },
    "bakery": {
        "file": "haccp-template-bakery.html",
        "title": "HACCP Template for Bakeries &amp; Home Bakers: Free UK PDF | Blueroll",
        "desc": "Free HACCP plan template for UK bakeries and registered home bakers. Cooling logs, cleaning schedule, PPDS allergen reference. Free 16-page PDF.",
        "h1": "Free HACCP template for bakeries &amp; home bakers",
        "breadcrumb": "HACCP template for bakeries",
        "sub": "This free HACCP plan template works for a high-street bakery and a registered home baker alike: fridge and cooling temperature logs, a cleaning schedule, delivery checks for ingredient drops and corrective actions. Enter your work email for instant access to the 16-page pack.",
        "who_rows": [
            ("BAKE-BOX CLUB<br>YORKSHIRE", "Uses the delivery check form for ingredient drops and the cleaning schedule weekly."),
            ("GELATERIA<br>LONDON", "Started on this paper pack, now runs the same checks digitally."),
            ("HOME BAKERY<br>UK", "Keeps the signed daily sheets ready for the council's first visit."),
        ],
        "faq": [
            ("Do home bakers really get inspected?",
             "Yes. Registering your home kitchen with the council is the law once you sell food, and an EHO can visit like any other food business. Signed, dated daily records are exactly what turns that first visit into a good rating."),
            ("What about Natasha's Law and my labels?",
             'If you pack items before sale (PPDS), every label needs a full ingredient list with the 14 allergens emphasised. The pack\'s reference card lists the allergens; our <a href="natashas-law-2026.html">Natasha\'s Law guide</a> covers the labelling rules, and the <a href="haccp-template-cafe.html">cafe version</a> of this template handles counter sales.'),
            FREE_FAQ,
        ],
    },
    "food-truck": {
        "file": "haccp-template-food-truck.html",
        "title": "HACCP Template for Food Trucks &amp; Street Food: Free UK PDF | Blueroll",
        "desc": "Free HACCP plan template for UK food trucks, trailers and street food traders. Event-day opening checks, temperature logs, cleaning. Free 16-page PDF.",
        "h1": "Free HACCP template for food trucks &amp; street food",
        "breadcrumb": "HACCP template for food trucks",
        "sub": "This free HACCP plan template suits a truck, trailer or market stall: opening checks for the unit (water, gas, power), fridge and hot-hold temperature logs, cleaning, stock deliveries and corrective actions. Enter your work email for instant access to the 16-page pack.",
        "who_rows": [
            ("COFFEE VAN<br>DEVON", "Runs the daily sheet on the hatch shelf, files it after each pitch."),
            ("TAPROOM<br>CORNWALL", "Downloaded the day after opening. Rated 5 a week later."),
            ("GRILL TAKEAWAY<br>LONDON", "Same sheets, busier Fridays."),
        ],
        "faq": [
            ("Do I need HACCP for a food truck or market stall?",
             "Yes. Any registered food business needs a food safety management system based on HACCP principles, mobile or not. The unit gets inspected and rated like a restaurant, and the day's signed records are the first thing asked for."),
            ("What will an EHO check at an event?",
             'Water supply, hand-wash facilities, fridge and hot-hold temperatures, allergen information and your records for the day. Many traders keep an NCASS due-diligence folder; these sheets are the daily evidence that goes in it. The <a href="haccp-template-takeaway.html">takeaway version</a> covers fixed premises.'),
            FREE_FAQ,
        ],
    },
    "scotland": {
        "file": "haccp-template-scotland.html",
        "title": "HACCP Template for Scottish Kitchens (CookSafe-friendly): Free PDF | Blueroll",
        "desc": "Free HACCP plan template for kitchens in Scotland. Daily records that sit alongside CookSafe: temperature logs, cleaning, deliveries. Free 16-page PDF.",
        "h1": "Free HACCP template for Scottish kitchens",
        "breadcrumb": "HACCP template for Scotland",
        "sub": "This free HACCP plan template fits Scottish kitchens: the daily records Food Standards Scotland inspections look at, filed alongside your CookSafe house rules. Fridge and hot-hold temperature logs, cleaning schedule, delivery checks and corrective actions. Enter your work email for the 16-page pack.",
        "who_rows": [
            ("EH OFFICER<br>SCOTTISH COUNCIL", "An environmental health officer downloaded this pack. The same records inspectors ask to see."),
            ("TAPROOM<br>CORNWALL", "Downloaded the day after opening. Rated 5 a week later."),
            ("SCHOOL KITCHEN<br>LONDON", "Runs the daily sheets at the pass, files them by week."),
        ],
        "faq": [
            ("Does this work with CookSafe?",
             "Yes. CookSafe is the house-rules manual; these sheets are the daily evidence that you follow it: temperatures, cleaning, deliveries, corrective actions. Keep your CookSafe folder as is and file these records with it."),
            ("What does a Pass depend on under the Food Hygiene Information Scheme?",
             'Scotland rates premises Pass or Improvement Required rather than 0 to 5. Complete, signed day-by-day records are the strongest evidence of control an officer sees. When paper gets tedious, <a href="haccp-checklists.html">digital checklists</a> keep the same records on your team\'s phones. Sorting out training too? See our <a href="food-hygiene-certificate-scotland-a-2026-guide-to-business-compliance.html">guide to food hygiene certificates in Scotland</a>.'),
            FREE_FAQ,
        ],
    },
}
