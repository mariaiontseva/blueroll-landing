# Template Funnel Scale Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Multiply the already-converting HACCP template funnel (7% download→register before any nurture) with five segment satellite pages, a Scotland edition, per-segment analytics, and a "2026 edition" relaunch trigger.

**Architecture:** One Python builder in the repo generates all satellite pages from a single config, reusing the proven v2 page skeleton (two-step gates, tracked capture into `template_leads`, drip letter 1 fires automatically because capture source stays `haccp-template:*`). Copy, FAQ, schema and examples vary per segment; the PDF stays one file so the 2026-edition swap is a single-URL replace.

**Tech Stack:** Static HTML on GitHub Pages (gh-pages branch), Python 3 builder committed to `_build/`, Supabase `template_leads` + `drip` edge function (already live), GA4 events already wired in the skeleton.

## Global Constraints

- Every capture must POST to `template_leads` with `source = 'haccp-template:<segment>:<placement>'` so the existing drip picks it up unchanged and the portal shows the segment.
- SEO floors: unique `<title>`, meta description, canonical (self), H1 with the page's exact-match keyword, FAQPage + BreadcrumbList JSON-LD, breadcrumb visible, page in `sitemap.xml` and `llms.txt`. Never touch the main page's existing URL or its copy except the cross-links block.
- The pack is 8 pages until the 2026 edition ships; the page count lives ONLY in the builder config (one place).
- No em dashes in any copy. UK English. Honest claims only (Scotland page says the pack "sits alongside CookSafe", it does not claim to BE CookSafe).
- Mobile: no horizontal scroll at 390px and 340px, inputs 16px, gallery 2×2 (skeleton already handles this; verify per page).

---

### Task 1: Builder + skeleton extraction

**Files:**
- Create: `_build/build_template_satellites.py`
- Create: `_build/template_satellites_config.py`
- Read: `free-haccp-template.html` (the skeleton source)

**Interfaces:**
- Produces: `python3 _build/build_template_satellites.py` writes every configured satellite HTML into the repo root; config exposes `SEGMENTS: dict[slug, dict]` with keys `title, desc, h1, badge, sub, steps[3], who_rows[3], faq[3] (q, a_html), extra_seo_html, source_tag, breadcrumb_label`.

- [ ] **Step 1:** Write the builder: load `free-haccp-template.html` as the skeleton, parameterise via string replacement of the hero block (badge/H1/keyword-H1/sub), the three numbered steps, the who-downloads rows, the FAQ block, `<title>`, meta description, canonical URL, breadcrumb label, FAQPage JSON-LD (regenerate from config q/a), and the capture `source` string (`'haccp-template'` → `'haccp-template:' + slug`). Keep gates, gallery, bands, exit modal, dark CTA byte-identical.
- [ ] **Step 2:** Add a `PAGES_COUNT = 8` constant in config used everywhere the number appears.
- [ ] **Step 3:** Build with one placeholder segment, diff against the main page to confirm only the intended blocks changed.
- [ ] **Step 4:** Commit `_build/` (builder + config, no generated pages yet).

### Task 2: Segment copy (four English segments)

**Files:**
- Modify: `_build/template_satellites_config.py`
- Create (generated): `haccp-template-cafe.html`, `haccp-template-takeaway.html`, `haccp-template-bakery.html`, `haccp-template-food-truck.html`

Segments and exact-match keywords (title/H1):
- cafe → "HACCP template for cafes & coffee shops (free UK PDF)"; examples: espresso machine cleaning, milk fridge temps, allergen labels on counter cakes.
- takeaway → "HACCP template for takeaways (free UK PDF)"; examples: hot hold, delivery driver handover times, reheating temps.
- bakery → "HACCP template for bakeries & home bakers (free UK PDF)"; examples: PPDS labels (Natasha's Law), egg storage, cooling logs; who-rows reference our real downloaders (a bake-box club, a gelateria that went digital after this pack).
- food-truck → "HACCP template for food trucks & street food (free UK PDF)"; examples: gas + water checks, event-day opening checks, NCASS mention.

- [ ] **Step 1:** Fill config for the four segments: each gets its own sub-paragraph (keyword in first sentence), 3 steps rewritten with segment examples, 3 who-rows, 3 FAQs (one always "Is this enough for my EHO inspection?", one segment-specific, one "Is it really free?"), meta description under 155 chars.
- [ ] **Step 2:** Build, open each page locally (launch config `landing-repo`, port 8792), submit a test email on ONE page, verify the row lands as `haccp-template:cafe:hero`, then delete the test row.
- [ ] **Step 3:** Check 390px and 340px: no horizontal scroll, 2×2 gallery, full-width band buttons.
- [ ] **Step 4:** Commit generated pages.

### Task 3: Scotland edition

**Files:**
- Create (generated): `haccp-template-scotland.html` via config segment `scotland`

Scotland differs: regulator is Food Standards Scotland, scheme is the Food Hygiene Information Scheme ("Pass" / "Improvement Required", not 0-5 stars), the FSA pack equivalent is CookSafe (REHIS training). Copy must use those words and never mention SFBB as the local scheme.
- Title/H1: "HACCP template for Scottish kitchens (CookSafe-friendly, free PDF)".
- Sub: the pack's daily records (temps, cleaning, deliveries, corrective actions) are what an EHO checks under FHIS; it files alongside a CookSafe house rules folder.
- FAQ: "Does this work with CookSafe?" (honest: same daily records, keep your CookSafe house rules section), "What does 'Pass' depend on?", "Is it really free?".

- [ ] **Step 1:** Fill the scotland segment config with the copy above.
- [ ] **Step 2:** Build, verify locally as in Task 2 Step 2-3.
- [ ] **Step 3:** Commit.

### Task 4: Interlinking + discovery

**Files:**
- Modify: `free-haccp-template.html` (add "Made for your kitchen" block after the gallery: 5 pill links to the satellites)
- Modify: `tools.html` (satellite links under the template card)
- Modify: `sitemap.xml` (5 URLs, lastmod today), `llms.txt` (5 lines)

- [ ] **Step 1:** Add the cross-link block to the main page (pills, no layout change elsewhere).
- [ ] **Step 2:** Add links in `tools.html`, entries in `sitemap.xml` and `llms.txt`.
- [ ] **Step 3:** Build all, run the internal link check: every satellite links back to the main page (breadcrumb) and to two sibling satellites in its FAQ answers.
- [ ] **Step 4:** Commit, push gh-pages, wait for 200 on all five live URLs, spot-check one live form submit end to end (row + drip letter 1 arrives), delete the test row and its log.

### Task 5: Per-segment numbers in the portal

**Files:**
- Modify: `internal/template-leads.html`

- [ ] **Step 1:** In the stats row, add a compact "by page" breakdown: count leads grouped by the segment parsed from `source` (`haccp-template:cafe` → "cafe"), rendered as small badges with counts.
- [ ] **Step 2:** Push, verify live with existing data (all current rows show as "main").

### Task 6: 2026 edition relaunch (BLOCKED until the designer's PDF lands)

**Files:**
- Replace: `blueroll-haccp-template.pdf` (same URL, same filename)
- Modify: `_build/template_satellites_config.py` (`PAGES_COUNT`), rebuild all pages
- Modify: `supabase/functions/drip/templates/*` in blueroll-web (page count), redeploy `drip`

- [ ] **Step 1:** Verify the new PDF page count with pypdf; set `PAGES_COUNT`, rebuild satellites + main page badge/sub, push.
- [ ] **Step 2:** Update the three drip templates' page count, regenerate `templates.ts`, redeploy the function.
- [ ] **Step 3:** Relaunch email to every non-unsubscribed lead: subject "The 2026 edition of your HACCP pack", body: what's new (filled-in examples, EHO questions page, allergen matrix), tracked download link. Send via the drip function as a one-off letter (add letter 4 template) after Maria approves the text.
- [ ] **Step 4:** Watch portal opens/clicks for a week; report.

### Task 7: Distribution seeding (manual, Maria's list)

No files. One-line tasks to hand out: pin the four preview images to Pinterest linking to the matching satellite; answer the standing "where do I get a HACCP template" threads on r/KitchenConfidential and UK hospitality Facebook groups with the segment link; offer NCASS the food-truck page for their member resources; ask the 533-consultant list (when partner outreach starts) to link "free template" to us.

---

## Self-Review Notes

- Spec coverage: satellites (T1-2), Scotland (T3), interlinking/SEO (T4), measurement (T5), 2026 relaunch (T6), distribution (T7). Covered.
- The drip needs zero changes for satellites: `source=like.haccp-template*` already matches `haccp-template:cafe:hero`.
- Placeholder scan: copy directions are concrete; final sentence-level copy is written at execution time inside the config (single place), constraints pinned in Global Constraints.
