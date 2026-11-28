# Measurement plan: web trial onboarding

Updated: 4 November 2026

**Feature:** the path from a "Start trial" link on blueroll.app, through the `app.blueroll.app/onboarding` wizard, to account creation, card capture and the first paid invoice.
**Tool:** GA4 only. Property `530219605`, web stream "Blueroll Landing", tag `G-ZFY0GPZYYQ`. The app joins the same property and stream.
**Owner:** Blueroll. Prepared by aictrl.dev.

## 0. Current state

| Area | What exists on 4 November 2026 |
|---|---|
| Marketing site | The gtag snippet is on 115 of 142 pages. `geo-analytics.js` is on 70 pages and sends `trial_start_click`, which is the property's only key event (57 events from 26 users in the 28 days to 3 November). |
| Untracked links | 48 pages link to the app without loading `geo-analytics.js`: 46 borough pages built from `_build/borough_template.html`, `audit/` and `bobo-eho-guide.html`. Clicks from these pages are not counted. |
| Sign-in clicks counted as trials | 228 of about 515 app links are "Sign in" links (`nav-signin`, `mm-link`). They use the same URL as "Start for free", so returning customers send `trial_start_click` and inflate the key event. Until this is fixed, historical `trial_start_click` figures overstate trial intent. |
| Links with campaign tags | 8 pages add `utm_source=blueroll.app&utm_medium=referral` to their app links. Once the app is tagged, these tags will replace each visitor's real source (for example `google / organic` or `chatgpt.com`) with `blueroll.app / referral`. |
| App | The app has no GA4 and no other analytics. It loads only Sentry and Stripe. |
| Visitor ID across sites | The gtag snippet uses its default cookie domain, so it sets the `_ga` cookie on `blueroll.app`. The app on `app.blueroll.app` can read the same cookie and will see the same visitor ID. No link decoration is needed, but GA4 must be told that both hostnames are Blueroll's (see §4b). |
| Wizard | The wizard is one URL, `/onboarding`, and React state switches the steps. The address never changes, so the browser's back button leaves the wizard and loses everything entered. The wizard's own ← Back button calls `goBack` and stays inside. |

The wizard has three routes (`flow`), read from the production bundle:

| `flow` | Steps |
|---|---|
| `single_site` | name → choice → setup → postcode → select → rating → signup → card |
| `multi_site` | name → choice → setup → sites → invites → signup → card → done |
| `invite` | name → choice → invite → signup |

## 1. Goal

> Analyse **the web trial onboarding flow** for the purpose of **improving** it with respect to its **step completion, back-navigation and source-to-paid conversion** from the viewpoint of **Blueroll's founders**, in the context of **web sign-ups from blueroll.app in each account's first 30 days, excluding native iOS and Android installs**.

## 2. Learning objectives

### Feature impact
- **Q1:** At which wizard step do the most people stop? Does this differ by `flow`?
- **Q2:** Where do people use the wizard's ← Back button? Which step do they leave and which do they return to? Do they then finish, or abandon?
- **Q3:** How often does the browser's back button take people out of the wizard, and from which step?
- **Q4:** Of the people who click "Start trial", what share create an account, and what share then add a card?

### Business performance
- **Q5:** Which sources and landing pages produce trials with a card and paying accounts, not only clicks?
- **Q6 (guard rail):** Does GA4 count every trial? Does adding tracking or a consent banner reduce the number of people who reach step 1? How much of the traffic is bots?

## 3. Metrics

All metrics count users, not events, unless stated otherwise. The segments are `flow`, first-user source/medium, landing page, `ai_source`, device category and week.

| ID | Metric | Definition | Answers | Type | Granularity |
|----|--------|-----------|---------|------|-------------|
| M1 | Step reach | Users with `onboarding_step_view` at `step_number = n` ÷ users at `step_number = 1`, per `flow` | Q1 | funnel | weekly |
| M2 | Step error rate | Users with `onboarding_error` at `step` ÷ users with `onboarding_step_view` at `step` | Q1 | rate | weekly |
| M3 | Back-button rate | Users with `onboarding_step_back` (`method = button`) from `from_step` ÷ users who viewed that step | Q2 | rate | weekly |
| M4 | Recovery after back | Users with `onboarding_step_back` who later send `sign_up` in the same session ÷ users with `onboarding_step_back` | Q2 | rate | weekly |
| M5 | Browser exit rate | **Now:** users with `onboarding_back_return` ÷ users with `trial_start_click`. **After the app change:** users with `onboarding_step_back` (`method = browser`) from `from_step` ÷ users who viewed that step | Q3 | rate | weekly |
| M6 | Click to sign-up | Users with `sign_up` ÷ users with `trial_start_click` | Q4 | funnel | weekly |
| M7 | Sign-up to card | Users with `trial_start` ÷ users with `sign_up` | Q4 | funnel | weekly |
| M8 | Trial to paid | Users with `purchase` ÷ users with `trial_start`, counting only cohorts whose trial started 15 or more days ago | Q5 | rate | monthly |
| M9 | Trials and paying accounts by source | Count of users with `trial_start` and with `purchase`, by first-user source/medium, first landing page and `ai_source` | Q5 | counter | monthly |
| M10 | GA4 coverage (guard rail) | `trial_start` events in GA4 ÷ new trialing subscriptions in Stripe, same week | Q6 | ratio | weekly |
| M11 | Wizard reach (guard rail) | Users with `onboarding_step_view` at `step_number = 1` ÷ users with `trial_start_click`, compared before and after each tracking or consent change | Q6 | rate | weekly |
| M12 | Unengaged traffic by country (guard rail) | Sessions without `user_engagement` ÷ all sessions, by country. Investigate Singapore first: 130 of 495 active users in the last 28 days | Q6 | rate | weekly |

## 4. Implementation

The plan uses 8 events: 5 in the app, 1 sent by the server and 2 on the marketing site. Parameter names are short and shared across events. Use `step`, not `onboarding_step`.

### 4a. GA4 events

#### App (`app.blueroll.app`): needs the app codebase

Load GA4 once, in the root layout, with the same tag ID. For Next.js, use `GoogleAnalytics` from `@next/third-parties/google`, then send events with `sendGAEvent`.

| Event | Trigger | Parameters | Metric |
|-------|---------|------------|--------|
| `onboarding_step_view` | Each time the wizard's current step changes, including the first render | `step` (`name`, `choice`, …), `step_number` (1-based), `total_steps`, `flow` | M1–M5, M11 |
| `onboarding_step_back` | The ← Back button (`method = button`) or the browser's back button inside the wizard (`method = browser`, see below) | `from_step`, `to_step`, `step_number` (of `from_step`), `flow`, `method` | M3–M5 |
| `onboarding_error` | Any error shown in the wizard: sign-up failure, card declined, "Session expired" | `step`, `flow`, `error` (short code such as `card_declined`, never the raw message) | M2 |
| `sign_up` (GA4 recommended event) | `supabase.auth.signUp` succeeds | `method: "email"`, `flow` | M4, M6, M7 |
| `trial_start` | Stripe confirms the card in the `card` step, which starts the 14-day trial | `flow`, `sites` (number of sites, if known) | M7–M10 |

**Browser back inside the wizard.** On each step change, call `window.history.pushState({ step: next }, "")`. Listen for `popstate`. On `popstate`, send `onboarding_step_back` with `method: "browser"` and show `event.state.step`. This keeps the person inside the wizard instead of discarding their input, and it measures M5 per step. The change fixes a UX defect and also collects the data.

**User ID.** After `sign_up`, set the Supabase user ID as `user_id` with `gtag('config', 'G-ZFY0GPZYYQ', { user_id })`. Never send an email address or a name.

**Visitor ID for the server.** After `sign_up`, read the GA4 visitor ID with `gtag('get', 'G-ZFY0GPZYYQ', 'client_id', …)` and save it on the user's profile row as `ga_client_id`. §4c needs it.

#### Marketing site (`blueroll.app`): this repo

| Change | Detail | Metric |
|-------|--------|--------|
| Load `geo-analytics.js` on the 48 untracked pages | Add it to `_build/borough_template.html` (the scheduled borough rebuild otherwise overwrites edits to the HTML) and to `audit/` and `bobo-eho-guide.html`. Extend `scripts/add-geo-analytics.mjs` so it reports pages that are still missing. | M5, M6, M9 |
| Remove `utm_*` from links to the app | 8 pages, listed by `grep -rl "app.blueroll.app/?utm_" --include=*.html .`. `trial_start_click` already records `landing_page`, which carries the same information. | M9 |
| Separate sign-in clicks | In `geo-analytics.js`, app links whose text is "Sign in" send `sign_in_click` instead of `trial_start_click`. | M5, M6, M11 |
| New event `onboarding_back_return` | In `geo-analytics.js`: when `trial_start_click` fires, store the time and page in `sessionStorage`. On `pageshow`, if `event.persisted` is true or `performance.getEntriesByType('navigation')[0].type === 'back_forward'`, and the stored value exists, send the event and clear the value. Parameters: `landing_page`, `seconds` (time since the click). All app links open in the same tab, so the back button returns here. | M5 |

### 4b. GA4 admin settings (no code)

1. **Data stream → Configure tag settings → Configure your domains:** add `blueroll.app` and `app.blueroll.app`. GA4 then stops treating the step from the site into the app as a referral that starts a new session.
2. **Custom definitions → event-scoped dimensions:** `step`, `flow`, `from_step`, `to_step`, `method`, `error`, `landing_page`. **Custom metrics:** `step_number`, `seconds`.
3. **Key events:** mark `sign_up`, `trial_start` and `purchase`. Keep `trial_start_click` as a key event until `trial_start` has a month of data, then unmark it.
4. **Data stream → Measurement Protocol API secrets:** create one secret for §4c.
5. **Explorations:** one funnel exploration per `flow`, with these steps: `trial_start_click` → `onboarding_step_view` for `step_number` 1 to 8 → `trial_start`. GA4 allows at most 10 funnel steps, so build a separate funnel for each flow. Add a free-form table for back-navigation: rows `from_step`, columns `to_step`, values = users, filtered to `onboarding_step_back`.

### 4c. Server event: first paid invoice

| Event | Source | Fields | Metric |
|-------|--------|--------|--------|
| `purchase` (GA4 recommended event) | Stripe webhook `invoice.paid`, sent only for the first invoice with `amount_paid > 0` | `client_id` (= `ga_client_id` from the profile), `user_id`, `transaction_id` (invoice ID), `value`, `currency: "GBP"` | M8, M9 |

Send it to `https://www.google-analytics.com/mp/collect?measurement_id=G-ZFY0GPZYYQ&api_secret=…` from the existing Stripe webhook handler. Use `transaction_id` so that Stripe's webhook retries do not double-count.

### 4d. Warehouse

None is needed for the first version. GA4 explorations answer Q1–Q6. If M8 and M9 later need joins at user level with Stripe or Supabase, link GA4 to BigQuery (the daily export is free) and join on `user_id`.

## 5. Validation

- [ ] Every metric maps to a question, and every question maps to the goal.
- [ ] GA4 DebugView (load the app with `?debug_mode=true`, or use Tag Assistant) shows `onboarding_step_view` at every step of all three flows, with the correct `step_number` and `total_steps`.
- [ ] The ← Back button and the browser's back button each send `onboarding_step_back` with the correct `method`. The browser's back button no longer leaves the wizard.
- [ ] On the marketing site, clicking "Start trial" and then pressing the browser's back button sends `onboarding_back_return` exactly once.
- [ ] A test sign-up sends `sign_up` with `user_id`, and the profile row has `ga_client_id`.
- [ ] A Stripe test-mode invoice sends a `purchase` that appears in GA4 with the same `client_id`.
- [ ] Pages viewed on `app.blueroll.app` show session source `google / organic` (or the visitor's real source), not `blueroll.app / referral`.
- [ ] M10 (GA4 coverage) is at least 90% in the first full week.

### Review schedule
- **Week 1 after release:** check that data is arriving, fix gaps in instrumentation and check M10.
- **Week 4:** first review of M1–M7: the step with the largest drop and the back-navigation hotspots.
- **Week 12:** first M8 and M9 cohorts (trials started 15 or more days earlier) and the paid-by-source review.

## 6. Delivery

| Change | Where | Status |
|---|---|---|
| This plan | `blueroll-landing` | PR: `docs/onboarding-measurement-plan` |
| `geo-analytics.js` on the borough pages, through the template | `blueroll-landing` | PR: `fix/geo-analytics-borough-pages` |
| Remove `utm_*` from links to the app | `blueroll-landing` | PR: `fix/remove-internal-utm-app-links` |
| `sign_in_click` and `onboarding_back_return` | `blueroll-landing` | PR: `feat/onboarding-back-return-event` |
| GA4 admin settings (§4b) | GA4 | Blueroll applies them |
| App events, browser-back handling, `ga_client_id` (§4a) | App codebase | Blueroll's team, or aictrl.dev with repository access |
| Stripe webhook to Measurement Protocol (§4c) | App codebase | Blueroll's team, or aictrl.dev with repository access |

Apply the GA4 domain setting in §4b before the app sends its first event.

## 7. Decisions for Blueroll

1. **Consent.** The site sets analytics cookies without asking. Before the app adds more tracking, decide whether to use a consent banner with Google Consent Mode v2 (`analytics_storage` denied by default). Check the current ICO guidance on analytics cookies after the Data (Use and Access) Act 2025. M10 and M11 show how much measured data a banner removes.
2. **Card step.** Card capture before the trial is the most likely large drop. Measure M7 for at least four weeks before changing the step.
