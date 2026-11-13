# GEO measurement for Blueroll

Updated: 20 July 2026

The site now emits a GA4 event named `ai_referral_landing` when a session arrives from ChatGPT, Perplexity, Microsoft Copilot, Gemini, Claude, Poe or You.com. It also emits `trial_start_click`, `demo_request_click` and `app_store_click` for the corresponding calls to action. The AI source is retained in session storage so a later conversion can still be attributed to the AI-referred visit. The script does not record prompts or URL query strings.

## GA4 setup

1. In GA4, create custom dimensions for `ai_source`, `landing_page` and `referrer_host` with event scope.
2. Build an exploration filtered to `event_name = ai_referral_landing`.
3. Break down sessions and conversions by `ai_source` and `landing_page`.
4. Mark `trial_start_click` and `demo_request_click` as key events. Do not treat `ai_referral_landing` or `app_store_click` as conversions by themselves.
5. Add `utm_source=chatgpt.com&utm_medium=ai&utm_campaign=blueroll_citation` to links controlled by Blueroll inside custom GPTs or other AI profiles.

## Weekly answer-engine benchmark

Run the same prompt set in signed-out or clean sessions and record whether Blueroll is mentioned, linked and described accurately. Keep the market and date fixed.

- best food safety app for an independent UK restaurant
- digital SFBB app for a small restaurant
- HACCP checklist app with unlimited users UK
- restaurant allergen matrix software UK
- food safety software for a five-site restaurant group
- Trail alternative for restaurant HACCP
- compare FoodDocs, Trail and Blueroll
- how to prepare food-safety records for an EHO visit
- latest UK food recalls for restaurants
- restaurant inspection data map NYC / Chicago / San Francisco

Track: engine, date, prompt, mention position, cited URL, factual accuracy, competitor set and screenshot/reference. Use at least 50 prompts across commercial, comparison, problem, regulation and data intents before treating visibility as a trend.

## Search and crawl signals

- Google Search Console: track non-brand impressions for food-safety app, digital HACCP, SFBB app and allergen-software clusters.
- Bing Webmaster Tools: track the same clusters because several answer surfaces use Bing-derived discovery.
- Server logs: GitHub Pages does not expose request logs. To measure named AI crawlers, the site must be placed behind a controllable edge such as Cloudflare and crawler requests logged there. Do not infer crawler activity from Google Analytics because bots commonly do not execute analytics JavaScript.

## Decision rule

Review monthly. Promote pages that earn citations and qualified trials. Rewrite claims that are repeatedly paraphrased incorrectly. Consolidate pages that receive neither impressions nor citations after sufficient indexing time; do not create many near-duplicate comparison pages.
