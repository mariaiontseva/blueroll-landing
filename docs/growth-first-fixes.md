# Direct app routes and conversion measurement

The marketing site's sign-in links sent returning customers to the app root. An unauthenticated visit to that route opens onboarding. The app already exposes `/login` and `/onboarding`, verified in the live browser on 20 November 2026.

The first fix directs 248 sign-in links to `/login` and 324 trial links to `/onboarding` across 128 pages. The solution-page generator uses the direct onboarding route; the other relevant generators copy navigation from the updated source pages. Product metadata and canonical URLs remain their existing destinations.

`geo-analytics.js` now keeps sending click events when session storage is unavailable. Previously, a denied storage read could exit the whole script before its click handler was registered. AI source persistence and browser-back attribution remain best-effort when storage is blocked.

Click events include `cta_location`. The homepage explicitly labels `header`, `mobile_menu`, `hero`, `pricing` and `final`. Other links use their containing region. In GA4, create an event-scoped custom dimension named `cta_location`, then compare unique users with `trial_start_click` by landing page, source, device and placement. A click is an intent signal; account creation and first payment require separate confirmed app/server events.

## Validation

- `node --test scripts/geo-analytics.test.mjs`: storage denial, AI attribution, login separation, placement fallback, modified clicks and one browser-back return.
- `node --check geo-analytics.js` and `git diff --check`.
- Static link checks for all modified anchors and all 113 sitemap entries; no sitemap, canonical or title changes.

## Next decisions

Use current Search Console and GA4 data before choosing which search landing pages to expand. The public site already has SFBB, templates, allergen matrix and competitor comparison pages; inspect their non-brand impressions, clicks and confirmed signups before adding more articles. The older onboarding plan in this repository describes a card step; the live onboarding currently shows seven steps and a no-card message, so revalidate the plan against current app events before implementing it.
