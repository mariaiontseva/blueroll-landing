#!/usr/bin/env python3
"""Build Blueroll solution pages and keep the shared Solutions menu in sync."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAMP = "20260720-solutions-v1"


DESKTOP_MENU = """<!-- SOLUTIONS_MENU_START -->
    <div class="bx-dd bx-solutions-dd">
      <button aria-haspopup="true">Solutions <svg class="bx-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5"/></svg></button>
      <div class="bx-menu bx-solutions-menu">
        <div class="bx-solutions-grid">
          <section class="bx-solutions-col">
            <p class="bx-solutions-label">Solutions for</p>
            <div class="bx-business-list">
              <a class="bx-solution-card" href="/independent-restaurant-food-safety.html">
                <span class="bx-solution-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="/solutions-icons.svg#solution-independent"></use></svg></span>
                <span class="bx-solution-copy"><strong>Independent restaurants</strong><small>One site, complete food-safety control</small></span><span class="bx-solution-arrow">›</span>
              </a>
              <a class="bx-solution-card is-featured" href="/multi-site-food-safety.html">
                <span class="bx-solution-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="/solutions-icons.svg#solution-multisite"></use></svg></span>
                <span class="bx-solution-copy"><strong>Multi-site groups <span class="bx-solution-tag">New</span></strong><small>See every location in one view</small></span><span class="bx-solution-arrow">›</span>
              </a>
              <a class="bx-solution-card" href="/franchise-food-safety.html">
                <span class="bx-solution-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="/solutions-icons.svg#solution-franchise"></use></svg></span>
                <span class="bx-solution-copy"><strong>Franchises</strong><small>Shared standards, local accountability</small></span><span class="bx-solution-arrow">›</span>
              </a>
              <a class="bx-solution-card" href="/hospitality-group-food-safety.html">
                <span class="bx-solution-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="/solutions-icons.svg#solution-hospitality"></use></svg></span>
                <span class="bx-solution-copy"><strong>Hospitality groups</strong><small>Hotels, pubs, cafés and catering</small></span><span class="bx-solution-arrow">›</span>
              </a>
            </div>
          </section>
          <section class="bx-solutions-col">
            <p class="bx-solutions-label">Benefits</p>
            <div class="bx-benefits-list">
              <a class="bx-solution-card" href="/inspection-ready-compliance.html">
                <span class="bx-solution-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="/solutions-icons.svg#benefit-compliance"></use></svg></span>
                <span class="bx-solution-copy"><strong>Inspection-ready compliance</strong><small>Complete records when an EHO arrives</small></span><span class="bx-solution-arrow">›</span>
              </a>
              <a class="bx-solution-card" href="/food-safety-consistency.html">
                <span class="bx-solution-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="/solutions-icons.svg#benefit-consistency"></use></svg></span>
                <span class="bx-solution-copy"><strong>Consistency across sites</strong><small>The same standards at every location</small></span><span class="bx-solution-arrow">›</span>
              </a>
              <a class="bx-solution-card" href="/team-accountability.html">
                <span class="bx-solution-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="/solutions-icons.svg#benefit-accountability"></use></svg></span>
                <span class="bx-solution-copy"><strong>Team accountability</strong><small>Know what was done, where and by whom</small></span><span class="bx-solution-arrow">›</span>
              </a>
              <a class="bx-solution-card" href="/paperless-food-safety.html">
                <span class="bx-solution-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="/solutions-icons.svg#benefit-savings"></use></svg></span>
                <span class="bx-solution-copy"><strong>Time &amp; paper savings</strong><small>Less admin, no missing folders</small></span><span class="bx-solution-arrow">›</span>
              </a>
            </div>
          </section>
        </div>
        <div class="bx-solutions-foot">
          <a class="bx-solutions-compare" href="/best-food-safety-apps-uk.html">Compare Blueroll with other food-safety apps →</a>
          <a class="bx-solutions-demo" href="mailto:hello@blueroll.app?subject=Multi-site%20Blueroll%20demo"><span>Managing 5+ sites?</span> Book a demo →</a>
        </div>
      </div>
    </div>
<!-- SOLUTIONS_MENU_END -->
    """


MOBILE_MENU = """<!-- SOLUTIONS_MOBILE_START -->
  <h4>Solutions for</h4>
  <a href="/independent-restaurant-food-safety.html">Independent restaurants</a>
  <a href="/multi-site-food-safety.html" class="bx-mobile-featured">Multi-site groups <small>New</small></a>
  <a href="/franchise-food-safety.html">Franchises</a>
  <a href="/hospitality-group-food-safety.html">Hospitality groups</a>
  <h4>Benefits</h4>
  <a href="/inspection-ready-compliance.html">Inspection-ready compliance</a>
  <a href="/food-safety-consistency.html">Consistency across sites</a>
  <a href="/team-accountability.html">Team accountability</a>
  <a href="/paperless-food-safety.html">Time &amp; paper savings</a>
  <a href="/best-food-safety-apps-uk.html">Compare food-safety apps</a>
<!-- SOLUTIONS_MOBILE_END -->
  """


HEADER = f"""<input type="checkbox" id="bx-burger-cb" class="bx-burger-cb">
<header class="bx-nav">
  <a href="/" class="bx-logo"><img src="/blueroll-logo.svg" alt="Blueroll"><b>Blueroll</b></a>
  <div class="bx-right">
    {DESKTOP_MENU.strip()}
    <div class="bx-dd">
      <button aria-haspopup="true">Product <svg class="bx-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5"/></svg></button>
      <div class="bx-menu">
        <a href="/haccp-checklists.html">HACCP Checklists<small>Daily checks &amp; temperature logs</small></a>
        <a href="/allergen-matrix.html">Allergen Matrix<small>All 14 allergens, auto-generated</small></a>
        <a href="/ai-recipe-import.html">AI Recipe Import<small>Any recipe in seconds</small></a>
        <a href="/compliance-reports.html">Compliance Reports<small>One-tap EHO-ready PDFs</small></a>
        <a href="/deliveries.html">Deliveries<small>Log temperature &amp; evidence</small></a>
        <a href="/document-management.html">Documents<small>Certificates &amp; reminders</small></a>
        <a href="/team-management.html">Team Management<small>Roles, access and tracking</small></a>
      </div>
    </div>
    <div class="bx-dd">
      <button aria-haspopup="true">Free Tools <svg class="bx-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5"/></svg></button>
      <div class="bx-menu">
        <a href="/audit/">Free Self-Audit<small>Score your kitchen</small></a>
        <a href="/check-food-hygiene-rating.html">Check a Hygiene Rating<small>Look up any UK venue</small></a>
        <a href="https://chatgpt.com/g/g-6a0c75c897108191956d8c9f3223abb4-blueroll-uk-food-safety-coach" target="_blank" rel="noopener">GPT Food Safety Coach<small>Ask our AI coach</small></a>
        <a href="/london-food-hygiene-map.html">London Hygiene Map<small>Every London venue</small></a>
        <a href="/nyc-restaurant-map.html">NYC Restaurant Map<small>US health grades</small></a>
        <a href="/sf-restaurant-map.html">SF Restaurant Map<small>US health grades</small></a>
        <div class="bx-sep"></div><a href="/tools.html">See all free tools →</a>
      </div>
    </div>
    <a href="/#pricing">Pricing</a>
    <a href="mailto:hello@blueroll.app?subject=Blueroll%20demo">Book a Demo</a>
    <a href="https://app.blueroll.app/" class="bx-btn">Start for Free</a>
  </div>
  <label for="bx-burger-cb" class="bx-burger" aria-label="Menu"><span></span><span></span><span></span></label>
</header>
<div class="bx-mobile">
  {MOBILE_MENU.strip()}
  <h4>Product</h4>
  <a href="/haccp-checklists.html">HACCP Checklists</a><a href="/allergen-matrix.html">Allergen Matrix</a><a href="/ai-recipe-import.html">AI Recipe Import</a><a href="/compliance-reports.html">Compliance Reports</a><a href="/deliveries.html">Deliveries</a><a href="/document-management.html">Documents</a><a href="/team-management.html">Team Management</a>
  <h4>Free Tools</h4>
  <a href="/audit/">Free Self-Audit</a><a href="/check-food-hygiene-rating.html">Check a Hygiene Rating</a><a href="/tools.html">See all free tools</a>
  <h4>&nbsp;</h4><a href="/#pricing">Pricing</a><a href="mailto:hello@blueroll.app?subject=Blueroll%20demo">Book a Demo</a><a href="https://app.blueroll.app/" class="bx-m-cta">Start for Free</a>
</div>"""


FEATURES = [
    ("✓", "HACCP checklists", "Opening, closing, cleaning and temperature records.", "/haccp-checklists.html"),
    ("H", "HACCP Pack", "A structured food-safety system connected to your records.", "/haccp-pack.html"),
    ("14", "Allergen matrix", "Recipes and all 14 regulated allergens in one view.", "/allergen-matrix.html"),
    ("PDF", "Compliance reports", "Export the date range an inspector asks to see.", "/compliance-reports.html"),
    ("R", "Roles & team", "Give each person the right access and responsibilities.", "/team-management.html"),
    ("D", "Documents", "Keep certificates together and track expiry dates.", "/document-management.html"),
]


PAGES = [
    {
        "slug": "independent-restaurant-food-safety.html",
        "title": "Food Safety Software for Independent Restaurants | Blueroll",
        "description": "Replace paper SFBB folders with digital HACCP checks, allergens, recipes and inspection-ready records built for independent restaurants.",
        "crumb": "Independent restaurants",
        "eyebrow": "For independent restaurants",
        "h1": "A complete food safety system. <em>Without enterprise overhead.</em>",
        "h1_plain": "A complete food safety system without enterprise overhead",
        "lede": "Run daily checks, recipes, allergens, deliveries and inspection records from one straightforward app. Your team gets the routine; you keep the oversight.",
        "secondary": ("See pricing", "/#pricing"),
        "proof": ["£24.99 per site / month", "Unlimited team members", "14-day free trial"],
        "demo": ("Today at your restaurant", "On track", [("12/14", "checks complete"), ("0", "overdue documents"), ("14", "allergens tracked")], [("ok", "Opening checks", "Completed by Kitchen", "Done"), ("warn", "Fridge 2 temperature", "Corrective action recorded", "Reviewed"), ("ok", "Closing checks", "Assigned to Manager", "Due 22:30")]),
        "section_kicker": "Everything in one place",
        "section_title": "Built around the way an independent kitchen actually works.",
        "section_intro": "No implementation project and no per-seat maths. Start with the records you need today, then add detail as the team settles in.",
        "cards": [("Daily control", "Keep the daily record together", "Checks, temperatures, deliveries and incidents live in the same system instead of separate folders and chats."), ("Safer answers", "Connect menu and allergens", "Recipes feed the allergen view so front and back of house can check the same structured information."), ("Clear evidence", "Find the record quickly", "Filter the period you need and export a clean report instead of searching through weeks of paper.")],
        "band_title": "Start simple. Keep room to grow.",
        "band_text": "Blueroll is focused enough for one busy restaurant, while the same account can support a second or third site when the business expands.",
        "band_items": ["Use ready-made food-safety checks, then adapt the workflow to your operation.", "Invite the whole team without paying for a seat every time somebody joins.", "Add another location later and move between a single-site view and the group view."],
        "workflow_title": "From paper folder to a live routine.",
        "steps": [("Set up the site", "Add your business details, food-safety pack and the checks your kitchen runs."), ("Invite the team", "Give managers, chefs, kitchen staff and front of house the right role."), ("Run one shift", "Complete opening, temperature and closing records on phone, tablet or web."), ("Review the trail", "See what is complete and retrieve the evidence when you need it.")],
        "faqs": [("Is Blueroll only for restaurant groups?", "No. It is designed to work for a single independent venue as well as a growing group. You pay per site and can invite unlimited team members."), ("Do I need to rebuild every checklist myself?", "No. Blueroll includes food-safety checklist templates, and you can adapt the working routine to your operation."), ("Can staff use their own phones?", "Yes. Blueroll works on the web and is available on iOS and Android, so teams can use the device that fits the shift."), ("What happens when I open a second location?", "Add the new site to the same group, assign its team and use the All sites view for oversight while each location keeps its own records.")],
        "cta_title": "Replace the folder before the next inspection.",
        "cta_text": "Start with one site and bring the team onto the daily routine during the free trial.",
    },
    {
        "slug": "multi-site-food-safety.html",
        "title": "Multi-Site Food Safety Management for Restaurant Groups | Blueroll",
        "description": "Manage HACCP, teams, site records and compliance across multiple restaurant locations from one Blueroll group dashboard.",
        "crumb": "Multi-site groups",
        "eyebrow": "New · Multi-site management",
        "h1": "Every site on standard. <em>One view for head office.</em>",
        "h1_plain": "Every site on standard with one view for head office",
        "lede": "Move from the whole group to a single location without losing context. See completion, missed checks and HACCP status across the estate, then open the site that needs attention.",
        "secondary": ("Book a multi-site demo", "mailto:hello@blueroll.app?subject=Multi-site%20Blueroll%20demo"),
        "proof": ["All sites dashboard", "Site-level access", "Unlimited team members"],
        "demo": ("All sites", "Group view", [("4", "active sites"), ("93%", "checks complete"), ("1", "needs attention")], [("ok", "Shoreditch", "All scheduled checks complete", "On track"), ("warn", "Stratford", "2 missed checks", "Review"), ("ok", "Clapham", "HACCP sign-off current", "On track")]),
        "section_kicker": "Group visibility",
        "section_title": "See the estate. Keep the record local.",
        "section_intro": "Head office gets a useful overview without flattening every kitchen into one undifferentiated list. Local teams stay focused on the site they run.",
        "cards": [("One view", "Spot the site that needs attention", "Use the All sites scope to compare progress and missed checks before opening the location-level detail."), ("Clear ownership", "Give people the right site access", "Assign members and roles so local teams see their work while group leaders retain oversight."), ("Consistent system", "Keep HACCP organised by location", "Each site keeps its operational evidence, while the group view shows where reviews or sign-off need attention.")],
        "band_title": "The answer to: “Which site do I need to look at?”",
        "band_text": "Multi-site management should reduce the hunt for information. Blueroll brings the exception to the surface, then lets you move into the exact location and record.",
        "band_items": ["Switch between All sites and a single location from the same workspace.", "Review group completion, missed checks and site-level HACCP status.", "Manage locations, members, roles and permissions from one group account."],
        "workflow_title": "Add sites without multiplying admin.",
        "steps": [("Create a location", "Add the site inside the existing Blueroll group and start it with the group standard."), ("Assign local leads", "Invite the manager and team with access matched to their responsibilities."), ("Run locally", "Each kitchen completes its checks, records and sign-off in its own site view."), ("Review as a group", "Use All sites to find exceptions, then open the location that needs follow-up.")],
        "faqs": [("What counts as multi-site in Blueroll?", "Any Blueroll group with two or more locations can use site switching and the All sites view."), ("Can a manager be limited to one site?", "Yes. Site membership and role-based permissions are designed so people can be given access that matches the locations and work they own."), ("Is pricing per user or per location?", "Pricing is £24.99 per site per month with unlimited team members. For five or more sites, book a demo so we can walk through the group setup."), ("Do all sites lose their individual records?", "No. Operational records remain tied to the relevant site. The group view provides oversight and a route into the site-level detail.")],
        "cta_title": "Put every location in the same operating view.",
        "cta_text": "Start a group trial or book a walkthrough for your current site structure.",
    },
    {
        "slug": "franchise-food-safety.html",
        "title": "Food Safety Software for Restaurant Franchises | Blueroll",
        "description": "Keep food-safety standards consistent across franchise locations with shared checklists, site roles and location-level evidence.",
        "crumb": "Franchises",
        "eyebrow": "For franchise operations",
        "h1": "Protect the brand. <em>Let every location own the shift.</em>",
        "h1_plain": "Protect the brand while every location owns the shift",
        "lede": "Give locations a clear food-safety standard, local responsibility and records that can be reviewed from the group level — without asking head office to run every kitchen.",
        "secondary": ("Talk through your structure", "mailto:hello@blueroll.app?subject=Franchise%20food-safety%20demo"),
        "proof": ["Group standards", "Local site records", "Roles & permissions"],
        "demo": ("Franchise overview", "4 locations", [("4/4", "sites reporting"), ("2", "local managers"), ("1", "follow-up")], [("ok", "Location A", "Opening and temperatures complete", "Signed off"), ("ok", "Location B", "HACCP review current", "Current"), ("warn", "Location C", "Document expires in 12 days", "Follow up")]),
        "section_kicker": "Central standard, local proof",
        "section_title": "Consistency without constant chasing.",
        "section_intro": "A franchise food-safety system needs to make the standard easy to follow and the evidence easy to find at each location.",
        "cards": [("Brand standard", "Start from the same operating baseline", "New sites can begin with the group's standard checklists and shared HACCP structure."), ("Local action", "Make responsibility visible", "Give each location's manager and team the roles they need to complete and review the daily record."), ("Group assurance", "Review exceptions across locations", "Use group visibility to find missed work or approaching document expiry without calling every site.")],
        "band_title": "One standard should create many local records — not one central bottleneck.",
        "band_text": "Blueroll separates the group view from the site view so the brand can set direction while the people on shift create the evidence.",
        "band_items": ["Organise locations inside one Blueroll group and switch scope as needed.", "Use roles and site access to separate head-office, manager and kitchen responsibilities.", "Keep checks, allergens, deliveries, documents and reports connected to the location."],
        "workflow_title": "A repeatable opening path for each location.",
        "steps": [("Define the baseline", "Choose the checks, HACCP information and menu records the group expects."), ("Create the site", "Add the location with the group's starting structure."), ("Name the owners", "Assign local managers and the team responsible for completing the work."), ("Review the exceptions", "Use group visibility for follow-up while the full evidence stays at site level.")],
        "faqs": [("Is Blueroll a full franchise management platform?", "No. Blueroll is focused on restaurant food safety, HACCP, allergens and the operational evidence around them. It does not claim to replace finance, royalty or franchise sales systems."), ("Can each location have its own manager?", "Yes. Members can be assigned roles and site access that match local responsibility."), ("Can locations keep different details?", "Yes. Records are tied to the relevant site, while the group account provides the shared structure and oversight."), ("What if franchisees are separate legal owners?", "Blueroll's group model is best when locations operate inside one managed workspace. For more complex ownership or data separation, book a demo so the structure can be checked before rollout.")],
        "cta_title": "Make the standard visible at every location.",
        "cta_text": "Show us how your franchise is structured and we will map the right Blueroll setup.",
    },
    {
        "slug": "hospitality-group-food-safety.html",
        "title": "Food Safety Software for Hospitality Groups | Blueroll",
        "description": "Coordinate food-safety records across hotel kitchens, pubs, cafés, catering teams and mixed hospitality locations.",
        "crumb": "Hospitality groups",
        "eyebrow": "For mixed hospitality operations",
        "h1": "One food-safety view across <em>kitchens, bars and venues.</em>",
        "h1_plain": "One food-safety view across kitchens, bars and venues",
        "lede": "Bring different locations and teams into one food-safety system while keeping the daily checks, documents and evidence relevant to each site.",
        "secondary": ("Book a group demo", "mailto:hello@blueroll.app?subject=Hospitality%20group%20demo"),
        "proof": ["Mixed venue groups", "Site-specific records", "Shared oversight"],
        "demo": ("Hospitality group", "All sites", [("5", "locations"), ("28", "team members"), ("96%", "checks complete")], [("ok", "Hotel kitchen", "Breakfast checks complete", "On track"), ("ok", "Ground-floor bar", "Closing record signed", "On track"), ("warn", "Events kitchen", "Delivery evidence incomplete", "Review")]),
        "section_kicker": "Different venues, one standard",
        "section_title": "Keep complexity in the structure — not in the team's day.",
        "section_intro": "A hotel kitchen, pub and catering operation may run different routines. They still need clear ownership and a reliable evidence trail.",
        "cards": [("Relevant routine", "Keep work tied to the location", "Teams enter the site they are working in and see the checks and records that belong there."), ("Group control", "Move between venue and estate views", "Leaders can review the whole group, then open the kitchen or venue behind an exception."), ("Shared knowledge", "Keep recipes, allergens and documents findable", "Structured records reduce the need to ask one person where the current information lives.")],
        "band_title": "A group view that respects local operations.",
        "band_text": "Blueroll gives head office a consistent food-safety lens while each venue keeps the people, records and day-to-day detail it needs.",
        "band_items": ["Organise hotel kitchens, pubs, cafés or catering locations inside one group.", "Assign members to the locations and roles they actually work in.", "Review checks, HACCP status and supporting evidence from the right scope."],
        "workflow_title": "Bring a mixed estate into one system.",
        "steps": [("Map the locations", "List the kitchens and venues that need their own operational record."), ("Set responsibilities", "Assign group leaders, site managers and local teams with the right access."), ("Run each routine", "Keep checks and evidence relevant to the venue rather than forcing one giant list."), ("Review centrally", "Use the group view to find gaps and move into the site that needs action.")],
        "faqs": [("Can Blueroll handle different venue types in one group?", "Yes. Locations can represent the kitchens or venues you need to manage, with records and teams scoped to the relevant site."), ("Is this an enterprise hotel management system?", "No. Blueroll is a focused food-safety product. It does not replace property management, rota, procurement or broad facilities platforms."), ("Can staff work across more than one location?", "The multi-site model supports members and site access inside the same group, so the setup can reflect people who work across locations."), ("Can we see the whole group and one venue?", "Yes. The scope switcher is designed for moving between All sites and an individual location.")],
        "cta_title": "Give every venue a clear food-safety home.",
        "cta_text": "Book a walkthrough and map your kitchens, venues and team responsibilities.",
    },
    {
        "slug": "inspection-ready-compliance.html",
        "title": "Inspection-Ready Food Safety Compliance Software | Blueroll",
        "description": "Keep HACCP checks, corrective actions, documents and date-range reports ready for a food hygiene inspection.",
        "crumb": "Inspection-ready compliance",
        "eyebrow": "Benefit · Compliance",
        "h1": "Be ready <em>before the inspector walks in.</em>",
        "h1_plain": "Be ready before the inspector walks in",
        "lede": "Inspection readiness is the result of a complete daily record. Blueroll keeps checks, corrective actions, documents and reports together so evidence is available when it is asked for.",
        "secondary": ("See compliance reports", "/compliance-reports.html"),
        "proof": ["Date-range reports", "Corrective-action record", "Document reminders"],
        "demo": ("Inspection record", "Ready to export", [("31", "days selected"), ("184", "records"), ("3", "actions resolved")], [("ok", "Daily checks", "Opening, closing and cleaning", "Included"), ("ok", "Temperature records", "With corrective actions", "Included"), ("ok", "Documents", "Certificates and policies", "Current")]),
        "section_kicker": "Build the evidence daily",
        "section_title": "Inspection day should be retrieval, not reconstruction.",
        "section_intro": "The useful record is the one your team creates during normal shifts and can explain later — not a folder completed in a rush.",
        "cards": [("Complete", "Capture the routine as it happens", "Record checks, readings, deliveries and incidents close to the work rather than recreating them later."), ("Explain", "Keep exceptions with the response", "When something falls outside the safe range, record the corrective action alongside the result."), ("Retrieve", "Export the period requested", "Choose a date range and produce a readable report for review or inspection.")],
        "band_title": "Compliance is a record trail, not a panic button.",
        "band_text": "Blueroll helps the responsible team maintain and retrieve its own food-safety evidence. It does not replace professional advice or the judgment of the food business operator.",
        "band_items": ["Use structured daily and periodic checks instead of loose notes.", "Keep timestamps, completion detail and corrective actions together.", "Store supporting documents and see approaching expiry dates."],
        "workflow_title": "A calmer inspection starts weeks earlier.",
        "steps": [("Run the checks", "Complete the scheduled routine during each shift."), ("Record the exception", "Add the reading, context and corrective action when something is wrong."), ("Manager reviews", "Follow up missed work and sign-off from the relevant site view."), ("Export evidence", "Select the period and retrieve the inspection record in a clean report.")],
        "faqs": [("Does Blueroll guarantee a hygiene rating?", "No. A software product cannot guarantee an inspection outcome. Blueroll helps organise the records your business creates and makes gaps easier to see."), ("Can I export a specific date range?", "Yes. Compliance reports are designed around selecting the period you need and producing a PDF record."), ("What happens to a failed temperature?", "The result can be kept with the corrective-action information so the record shows what happened and how the team responded."), ("Does Blueroll replace my food-safety adviser?", "No. The food business operator remains responsible for the system and should use the relevant authority or qualified adviser for decisions that need professional judgment.")],
        "cta_title": "Make inspection readiness part of the daily routine.",
        "cta_text": "Start recording the work now so the evidence is already there when it is needed.",
    },
    {
        "slug": "food-safety-consistency.html",
        "title": "Consistent Food Safety Standards Across Multiple Sites | Blueroll",
        "description": "Keep restaurant food-safety standards consistent across sites with shared structure, local records and group oversight.",
        "crumb": "Consistency across sites",
        "eyebrow": "Benefit · Consistency",
        "h1": "The same standard at every site. <em>Proven in the record.</em>",
        "h1_plain": "The same standard at every site, proven in the record",
        "lede": "Turn the group standard into a routine each location can run, then use the All sites view to see where execution is consistent and where support is needed.",
        "secondary": ("Explore multi-site", "/multi-site-food-safety.html"),
        "proof": ["Group baseline", "Local execution", "All sites review"],
        "demo": ("Standards overview", "This week", [("4/4", "sites active"), ("18", "shared checks"), ("92%", "completion")], [("ok", "Opening routine", "Used across all sites", "Consistent"), ("ok", "Cooling record", "Used across all sites", "Consistent"), ("warn", "Document review", "1 site overdue", "Follow up")]),
        "section_kicker": "Standardise the system",
        "section_title": "Consistency is shared structure plus visible local action.",
        "section_intro": "A policy document alone cannot show whether the standard reached the shift. The daily record connects what the group expects with what each site completed.",
        "cards": [("Baseline", "Start sites from a recognisable standard", "Use a common group structure for the checks and HACCP information that should not be reinvented at every opening."), ("Context", "Keep local records local", "Each venue still records its own temperatures, deliveries, incidents, documents and sign-off."), ("Oversight", "Compare without flattening the detail", "Review the estate from All sites, then move into the location behind a gap or exception.")],
        "band_title": "Make the standard easy to follow — and hard to lose.",
        "band_text": "Blueroll gives teams one place for the current food-safety routine, reducing the drift that appears when templates, messages and folders live in different places.",
        "band_items": ["Keep recurring checks in a structured schedule rather than local memory.", "Connect recipes, allergens and HACCP information to the working record.", "Use one group account to review location-level progress and follow-up."],
        "workflow_title": "From group expectation to site evidence.",
        "steps": [("Set the baseline", "Agree the food-safety routine the group expects locations to run."), ("Assign locally", "Give the work to the roles and people who own it at each site."), ("Record the shift", "Teams complete the routine and capture exceptions where they happen."), ("Compare and improve", "Review the group, support the outlier and keep the site record intact.")],
        "faqs": [("Do all sites need identical checklists?", "Not necessarily. A group can keep a recognisable baseline while location records reflect the work that applies to that site."), ("How do I see a problem at one location?", "The All sites scope surfaces group progress and missed work; from there you can open the relevant site for the underlying record."), ("Can new locations start from the group setup?", "The current multi-site flow is designed to create a location with the group's standard checklists and shared HACCP structure as a starting point."), ("Does consistency mean head office completes everything?", "No. The model is built for local completion and responsibility with group oversight.")],
        "cta_title": "Give every site the same clear starting point.",
        "cta_text": "Use Blueroll to connect the group standard to the record each kitchen creates.",
    },
    {
        "slug": "team-accountability.html",
        "title": "Restaurant Team Accountability & Food Safety Records | Blueroll",
        "description": "Assign food-safety work by role and keep a clear record of what was completed, where and by whom across restaurant sites.",
        "crumb": "Team accountability",
        "eyebrow": "Benefit · Accountability",
        "h1": "Know what was done, <em>where and by whom.</em>",
        "h1_plain": "Know what was done, where and by whom",
        "lede": "Give each person the right work and access, keep completion attached to the record, and let managers follow up on exceptions without chasing every routine task.",
        "secondary": ("See team management", "/team-management.html"),
        "proof": ["Role-based permissions", "Site membership", "Completion trail"],
        "demo": ("Team activity", "Live record", [("24", "checks today"), ("7", "team active"), ("1", "needs sign-off")], [("ok", "Opening checks", "Completed by Kitchen Staff · Site A", "08:12"), ("ok", "Delivery record", "Completed by Chef · Site A", "11:46"), ("warn", "Closing review", "Assigned to Manager · Site B", "Pending")]),
        "section_kicker": "Clarity without micromanagement",
        "section_title": "Responsibility should be visible before something is missed.",
        "section_intro": "Blueroll connects the work to a role, location and completion record so the team knows what it owns and managers know where follow-up is needed.",
        "cards": [("Right access", "Match permissions to responsibility", "Use roles to control what owners, managers, chefs, kitchen staff and other team members can see or change."), ("Right place", "Keep people scoped to their sites", "Site membership helps prevent a local team from working in the wrong location while group leaders retain wider access."), ("Clear trail", "Keep completion attached to the record", "Managers can review completed and missed work with the relevant person, time and site context.")],
        "band_title": "Give the team a clear lane. Give managers the exception.",
        "band_text": "Good accountability is not more notifications. It is a routine where people can see their responsibility and the manager can see the gap.",
        "band_items": ["Assign checklist work to the roles responsible for carrying it out.", "Create or adapt roles and permissions for the way the group operates.", "Review team activity from a site or across the group, depending on access."],
        "workflow_title": "Set ownership once, make it visible every shift.",
        "steps": [("Define roles", "Start with the core team roles and adjust capabilities where the operation needs it."), ("Add site access", "Connect each member to the locations they actually work in."), ("Assign the routine", "Make scheduled checks available to the roles responsible for completing them."), ("Review exceptions", "Follow up missed work and sign-off without interrupting every completed task.")],
        "faqs": [("Can I create custom roles?", "The new roles and permissions system supports role presets and custom roles with capabilities matched to the business."), ("Can a person work at multiple sites?", "The group model supports site membership so access can reflect people who work in one or several locations."), ("Can I see who completed a record?", "Completion information is kept with the operational record so managers can review who completed the work and when."), ("Are team members charged per seat?", "No. Blueroll includes unlimited team members and charges per site.")],
        "cta_title": "Make ownership clear across every shift.",
        "cta_text": "Invite the team, set the roles and let the record show where follow-up is needed.",
    },
    {
        "slug": "paperless-food-safety.html",
        "title": "Paperless Food Safety Records for Restaurants | Blueroll",
        "description": "Replace paper food-safety folders with digital checks, searchable records, documents and reports for restaurant teams.",
        "crumb": "Time & paper savings",
        "eyebrow": "Benefit · Less admin",
        "h1": "Spend less time <em>chasing paper.</em>",
        "h1_plain": "Spend less time chasing paper",
        "lede": "Put the daily food-safety routine on the devices your team already uses. Records become easier to complete, review and retrieve — without inventing a spreadsheet around the folder.",
        "secondary": ("See how checks work", "/haccp-checklists.html"),
        "proof": ["Works on any device", "Searchable records", "One-tap PDF reports"],
        "demo": ("Digital record", "No paper folder", [("1", "shared system"), ("0", "missing pages"), ("3", "devices supported")], [("ok", "Complete on shift", "Phone, tablet or browser", "Record"), ("ok", "Manager review", "Filter by site and date", "Review"), ("ok", "Inspection request", "Export a PDF report", "Share")]),
        "section_kicker": "Less handling, better retrieval",
        "section_title": "Digitising the record should remove work, not move it around.",
        "section_intro": "Blueroll replaces the cycle of printing, filing, photographing and re-keying paper with a record that starts digital and stays connected.",
        "cards": [("Complete once", "Record the work where it happens", "Teams use phone, tablet or browser during the shift instead of completing paper for somebody else to enter later."), ("Find quickly", "Filter instead of searching a shelf", "Use site, date and record context to get to the relevant evidence without opening multiple folders."), ("Share cleanly", "Create a readable report", "Export the requested period as a PDF rather than scanning or photographing pages.")],
        "band_title": "The saving is not a marketing calculator. It is fewer manual steps.",
        "band_text": "We do not publish an invented return-on-investment number. The practical gain is removing repeated handling from completion, review and retrieval.",
        "band_items": ["No printing a new checklist pack every time the template changes.", "No separate spreadsheet just to see which site sent its folder back.", "No last-minute scanning exercise when somebody requests a date range."],
        "workflow_title": "One digital trail from shift to report.",
        "steps": [("Open the task", "The team sees the food-safety work for the relevant role and site."), ("Complete the record", "Add the result and any required context on the device at hand."), ("Review the exception", "Managers focus on missing work or corrective actions rather than every page."), ("Retrieve and share", "Filter the period and create a clear report when it is requested.")],
        "faqs": [("Do we need special hardware?", "No. Blueroll works in a web browser and on iOS and Android, so teams can use existing phones, tablets or computers."), ("Can we keep printed backups?", "Your business can decide what backup process it needs. Blueroll is designed to make the working record digital and exportable."), ("Will digital records automatically make us compliant?", "No. The business remains responsible for having an appropriate food-safety system and for completing accurate records. Blueroll helps organise that work."), ("How much paper or time will we save?", "That depends on your current process, number of sites and how often records are handled. We avoid a universal savings claim; the trial is the best way to measure the difference in your own routine.")],
        "cta_title": "Run one shift without the folder.",
        "cta_text": "Use the free trial to compare completion, review and retrieval with your current paper process.",
    },
]


def render_demo(data: tuple) -> str:
    title, badge, stats, rows = data
    stat_html = "".join(f'<div class="sp-demo-stat"><b>{value}</b><small>{label}</small></div>' for value, label in stats)
    row_html = "".join(
        f'<div class="sp-demo-row"><span class="sp-dot {"warn" if state == "warn" else "muted" if state == "muted" else ""}"></span><span><b>{name}</b><small>{detail}</small></span><span>{value}</span></div>'
        for state, name, detail, value in rows
    )
    return f'<div class="sp-demo" aria-label="Illustrative Blueroll interface preview"><div class="sp-demo-top"><strong>{title}</strong><span>{badge}</span></div><div class="sp-demo-summary">{stat_html}</div><div class="sp-demo-list">{row_html}</div></div>'


def render_page(page: dict) -> str:
    canonical = f'https://blueroll.app/{page["slug"]}'
    structured = [
        {"@context": "https://schema.org", "@type": "WebPage", "name": page["h1_plain"], "description": page["description"], "url": canonical, "dateModified": "2026-07-20", "publisher": {"@id": "https://blueroll.app/#organization"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Blueroll", "item": "https://blueroll.app/"}, {"@type": "ListItem", "position": 2, "name": page["crumb"], "item": canonical}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in page["faqs"]]},
    ]
    proof = "".join(f"<span>{item}</span>" for item in page["proof"])
    cards = "".join(f'<article class="sp-card"><div class="sp-card-num">0{i}</div><h3>{title}</h3><p>{copy}</p></article>' for i, (_, title, copy) in enumerate(page["cards"], 1))
    band_items = "".join(f"<li>{item}</li>" for item in page["band_items"])
    steps = "".join(f'<article class="sp-step"><h3>{title}</h3><p>{copy}</p></article>' for title, copy in page["steps"])
    features = "".join(f'<a class="sp-feature" href="{href}"><span class="sp-feature-icon">{icon}</span><div><h3>{title}</h3><p>{copy}</p></div></a>' for icon, title, copy, href in FEATURES)
    faqs = "".join(f"<details><summary>{question}</summary><p>{answer}</p></details>" for question, answer in page["faqs"])
    secondary_label, secondary_href = page["secondary"]
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{page['title']}</title>
<meta name="description" content="{page['description']}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="en-gb" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:url" content="{canonical}"><meta property="og:title" content="{page['title']}"><meta property="og:description" content="{page['description']}"><meta property="og:image" content="https://blueroll.app/og-image.png">
<link rel="icon" href="/favicon.ico"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/site-chrome.css?v={STAMP}"><link rel="stylesheet" href="/solution-pages.css?v={STAMP}">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-ZFY0GPZYYQ"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-ZFY0GPZYYQ');</script>
<script type="application/ld+json">{json.dumps(structured, ensure_ascii=False, separators=(',', ':'))}</script>
</head>
<body class="bx-has-nav">
{HEADER}
<main>
  <header class="sp-hero"><div class="sp-shell">
    <nav class="sp-breadcrumb" aria-label="Breadcrumb"><ol><li><a href="/">Blueroll</a></li><li>›</li><li aria-current="page">{page['crumb']}</li></ol></nav>
    <div class="sp-hero-grid"><div><div class="sp-eyebrow">{page['eyebrow']}</div><h1>{page['h1']}</h1><p class="sp-lede">{page['lede']}</p><div class="sp-actions"><a class="sp-btn sp-btn-primary" href="https://app.blueroll.app/">Start free for 14 days</a><a class="sp-btn" href="{secondary_href}">{secondary_label}</a></div><div class="sp-proof">{proof}</div></div>{render_demo(page['demo'])}</div>
  </div></header>
  <section class="sp-section"><div class="sp-shell"><div class="sp-heading"><div class="sp-kicker">{page['section_kicker']}</div><h2>{page['section_title']}</h2><p>{page['section_intro']}</p></div><div class="sp-card-grid">{cards}</div></div></section>
  <section class="sp-band"><div class="sp-shell sp-band-grid"><div><h2>{page['band_title']}</h2><p>{page['band_text']}</p></div><ul class="sp-band-list">{band_items}</ul></div></section>
  <section class="sp-section sp-section-soft"><div class="sp-shell"><div class="sp-heading"><div class="sp-kicker">How it works</div><h2>{page['workflow_title']}</h2></div><div class="sp-steps">{steps}</div></div></section>
  <section class="sp-section"><div class="sp-shell"><div class="sp-heading"><div class="sp-kicker">Connected product</div><h2>One record across the food-safety workflow.</h2><p>Use the parts you need now. The value grows when checks, people, recipes, allergens, documents and reports stay connected.</p></div><div class="sp-feature-grid">{features}</div></div></section>
  <section class="sp-section sp-section-soft"><div class="sp-shell sp-faq"><div><div class="sp-kicker">FAQ</div><h2>Questions before you switch.</h2></div><div class="sp-faq-list">{faqs}</div></div></section>
  <section class="sp-section"><div class="sp-shell"><div class="sp-final"><h2>{page['cta_title']}</h2><p>{page['cta_text']}</p><div class="sp-actions"><a class="sp-btn sp-btn-primary" href="https://app.blueroll.app/">Start free for 14 days</a><a class="sp-btn" href="mailto:hello@blueroll.app?subject=Blueroll%20demo">Book a demo</a></div></div></div></section>
</main>
{render_footer()}
</body>
</html>
"""


def render_footer() -> str:
    return """<footer class="sp-footer"><div class="sp-footer-grid"><div><div class="sp-footer-brand"><img src="/blueroll-logo.svg" alt="">Blueroll</div><p>Food safety management for independent restaurants and growing hospitality groups.</p></div><div><h3>Solutions</h3><a href="/independent-restaurant-food-safety.html">Independent restaurants</a><a href="/multi-site-food-safety.html">Multi-site groups</a><a href="/franchise-food-safety.html">Franchises</a><a href="/hospitality-group-food-safety.html">Hospitality groups</a></div><div><h3>Benefits</h3><a href="/inspection-ready-compliance.html">Inspection-ready</a><a href="/food-safety-consistency.html">Consistency</a><a href="/team-accountability.html">Accountability</a><a href="/paperless-food-safety.html">Time &amp; paper</a></div><div><h3>Company</h3><a href="/best-food-safety-apps-uk.html">Compare apps</a><a href="/about.html">About</a><a href="/security.html">Security</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></div></div><div class="sp-footer-bottom">© 2026 Blueroll. London, United Kingdom.</div></footer>"""


def replace_between(text: str, start_tokens: tuple[str, ...], end_token: str, replacement: str) -> str:
    starts = [text.find(token) for token in start_tokens]
    starts = [value for value in starts if value >= 0]
    if not starts:
        return text
    start = min(starts)
    end = text.find(end_token, start)
    if end < 0:
        return text
    return text[:start] + replacement + text[end:]


def sync_existing_menus() -> None:
    generated = {page["slug"] for page in PAGES}
    for path in ROOT.rglob("*.html"):
        if path.name in generated:
            continue
        text = path.read_text(encoding="utf-8")
        if "bx-solutions-dd" not in text:
            continue
        updated = replace_between(
            text,
            ("<!-- SOLUTIONS_MENU_START -->", '<div class="bx-dd bx-solutions-dd">'),
            '<div class="bx-dd">',
            DESKTOP_MENU,
        )
        updated = replace_between(
            updated,
            ("<!-- SOLUTIONS_MOBILE_START -->", "<h4>Solutions</h4>", "<h4>Solutions for</h4>"),
            "<h4>Product</h4>",
            MOBILE_MENU,
        )
        updated = re.sub(r"site-chrome\.css\?v=[^\"']+", f"site-chrome.css?v={STAMP}", updated)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def upgrade_trust_pages() -> None:
    for filename in ("about.html", "evidence.html", "security.html", "best-food-safety-apps-uk.html"):
        path = ROOT / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "site-chrome.css" not in text:
            text = text.replace(
                '<link rel="stylesheet" href="trust-pages.css?v=20260720">',
                f'<link rel="stylesheet" href="trust-pages.css?v=20260720"><link rel="stylesheet" href="site-chrome.css?v={STAMP}">',
            )
        text = text.replace("<body>", '<body class="bx-has-nav">', 1)
        if "trust-nav" in text:
            text = re.sub(r'<nav class="trust-nav".*?</nav>', HEADER, text, count=1, flags=re.S)
        path.write_text(text, encoding="utf-8")


def main() -> None:
    for page in PAGES:
        (ROOT / page["slug"]).write_text(render_page(page), encoding="utf-8")
    sync_existing_menus()
    upgrade_trust_pages()
    print(f"Built {len(PAGES)} solution pages and synced the Solutions menu.")


if __name__ == "__main__":
    main()
