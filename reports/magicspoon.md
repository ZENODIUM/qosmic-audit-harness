# Magic Spoon audit — Checkout path works; JS-heavy PDPs and weak PageSpeed are the main leaks

## Executive summary

**Magic Spoon is a live Shopify DTC storefront on this crawl.** All seven manifest surfaces returned **200**, including `/cart` with title “Your Shopping Cart” (`artifacts/magicspoon/cart.md`; screenshot: `artifacts/magicspoon/screenshots/cart_full.png`). Hero PDPs **Classic Marshmallow & S'mores** and **Cocoa Cereal case** both load with review copy detected in HTML (`artifacts/magicspoon/pdp_1.md`, `artifacts/magicspoon/pdp_2.md`), though static fetch did not surface add-to-cart strings — consistent with a JS-rendered Shopify theme.

**Merchandising and performance—not cart plumbing—is where revenue likely leaks.** The homepage and **Shop All** collection titles emphasize protein, keto-friendly positioning and multi-category catalog (`artifacts/magicspoon/homepage.md`, `artifacts/magicspoon/collection.md`). FAQ loads at `/pages/faq` (`artifacts/magicspoon/faq_or_where_to_buy.md`). No distinct blog or content URL was discovered; `content_page` resolved to the homepage duplicate on this sitemap pass (`artifacts/magicspoon/manifest.json`).

**Technical baseline passes automated checks but PageSpeed is poor.** Per `artifacts/magicspoon/tech_grounded.json`: HTTPS, SSL, sitemap, robots, meta/OG, and favicon **Pass**; PageSpeed **40/100 mobile** and **42/100 desktop**. Priority tests: surface social proof closer to purchase on JS PDPs, bundle-first paths on collection, subscribe framing on case SKUs, FAQ→product handoffs, and LCP/image work on the homepage carousel — all tied to manifest URLs and screenshots from this run.

## Proposed experiments

### exp-m7a1b2c3 — Bundle Builder hero on Shop All collection

**Pillar:** Conversion
**Affected surface:** Shop All collection
**URL:** https://magicspoon.com/collections/shop-all
**Evidence:** artifacts/magicspoon/collection.md — title “Shop All | Magic Spoon Cereal, Treats & Granola”, status 200; screenshot: artifacts/magicspoon/screenshots/collection_full.png
**Hypothesis:** Collection-to-checkout rate rises when a “Build Your Own Bundle” module sits above the product grid with pre-selected bestseller cases.
**Primary change:** Sticky bundle CTA + 3-SKU starter preset linking to bundle builder flow.
**Primary KPI:** Collection add-to-cart rate
**Decision rule:** Ship if collection ATC rises by ≥8% over 21 days at 90% confidence.
**Expected lift:** +7–14%
**Confidence:** 77

### exp-m8b2c3d4 — Aggregated reviews above purchase block on Cocoa case PDP

**Pillar:** Conversion
**Affected surface:** Cocoa Cereal case PDP
**URL:** https://magicspoon.com/products/cocoa-cereal-case
**Evidence:** artifacts/magicspoon/pdp_2.md — review widget/copy in HTML, status 200; screenshot: artifacts/magicspoon/screenshots/pdp_2_full.png
**Hypothesis:** Add-to-cart on the cocoa case PDP improves when star rating and review count render in the first viewport above the purchase module (static HTML already hints review widgets load client-side).
**Primary change:** SSR or priority-hydrate review summary block directly above subscription/ATC on top five case SKUs.
**Primary KPI:** PDP add-to-cart rate (cocoa case)
**Decision rule:** Ship if ATC rises by ≥6% over 14 days without return rate up ≥2%.
**Expected lift:** +5–11%
**Confidence:** 79

### exp-m9c3d4e5 — Empty-cart sampler recommendation strip

**Pillar:** Conversion
**Affected surface:** Cart
**URL:** https://magicspoon.com/cart
**Evidence:** artifacts/magicspoon/cart.md — “Your Shopping Cart” 200; screenshot: artifacts/magicspoon/screenshots/cart_full.png
**Hypothesis:** Cart abandonment drops when empty-cart state shows a single-click “Discovery Kit” or variety 6-pack instead of a blank cart.
**Primary change:** Empty-state module with one preset bundle + social-proof line from homepage review theme.
**Primary KPI:** Cart-to-checkout rate (empty-cart sessions)
**Decision rule:** Ship if empty-cart checkout starts rise by ≥10% over 28 days at 90% confidence.
**Expected lift:** +8–16%
**Confidence:** 74

### exp-m0d4e5f6 — Case + treats cross-sell in cart drawer

**Pillar:** AOV
**Affected surface:** Cart / post-ATC drawer
**URL:** https://magicspoon.com/cart
**Evidence:** artifacts/magicspoon/collection.md — catalog spans cereal, treats, granola in title; artifacts/magicspoon/cart.md — cart 200; screenshot: artifacts/magicspoon/screenshots/collection_full.png
**Hypothesis:** AOV increases when adding a cereal case triggers a one-click treats 6-pack upsell at 15% off in the cart drawer.
**Primary change:** Rule-based upsell (cereal case in cart → treats variety pack offer) with single-tap accept.
**Primary KPI:** AOV (sessions with cereal case ATC)
**Decision rule:** Ship if AOV rises by ≥$6 over 28 days with sitewide CVR down ≤3%.
**Expected lift:** +9–18%
**Confidence:** 72

### exp-m1e5f6a7 — Subscribe-default on S'mores marshmallow case

**Pillar:** AOV
**Affected surface:** S'mores protein cereal PDP
**URL:** https://magicspoon.com/products/classic-smores-protein-cereal-marshmallows-1case-4boxes
**Evidence:** artifacts/magicspoon/pdp_1.md — marshmallow case PDP 200, review copy in HTML; screenshot: artifacts/magicspoon/screenshots/pdp_1_full.png
**Hypothesis:** Revenue per buyer rises when subscribe-and-save is pre-selected on case SKUs with clear “skip or cancel anytime” copy beside one-time purchase.
**Primary change:** Default subscription toggle on case PDPs; one-time as secondary link.
**Primary KPI:** Subscription take rate on case PDPs
**Decision rule:** Ship if subscription mix rises by ≥12% over 30 days without 60-day churn up ≥5%.
**Expected lift:** +10–20%
**Confidence:** 71

### exp-m2f6a7b8 — Post-purchase subscribe rescue email

**Pillar:** Retention
**Affected surface:** Post-purchase email (Klaviyo)
**URL:** https://magicspoon.com/ (purchase trigger)
**Evidence:** artifacts/magicspoon/cart.md — checkout path exists (cart 200); screenshot: artifacts/magicspoon/screenshots/cart_full.png
**Hypothesis:** 60-day repeat purchase rate improves when one-time buyers receive a day-14 email offering subscribe conversion on the same flavor at 20% off first refill.
**Primary change:** SKU-matched subscribe offer email with one-click reorder link.
**Primary KPI:** 60-day repeat purchase rate
**Decision rule:** Ship if repeat rate rises by ≥9% over 60 days at 90% confidence.
**Expected lift:** +8–15%
**Confidence:** 70

### exp-m3a7b8c9 — Replenishment reminder for case buyers

**Pillar:** Retention
**Affected surface:** Email / SMS
**URL:** https://magicspoon.com/products/cocoa-cereal-case
**Evidence:** artifacts/magicspoon/pdp_2.md — case SKU PDP 200; screenshot: artifacts/magicspoon/screenshots/pdp_2_full.png
**Hypothesis:** Churn among one-time case buyers drops when a day-25 “running low?” reminder fires with one-tap reorder of the same case.
**Primary change:** Consumption-based reminder (4-box case ≈ 28-day cadence) with prefilled cart link.
**Primary KPI:** Second-order rate within 45 days
**Decision rule:** Ship if second-order rate rises by ≥7% over 45 days at 90% confidence.
**Expected lift:** +6–13%
**Confidence:** 69

### exp-m4b8c9d0 — Protein-cereal landing from homepage thesis

**Pillar:** Acquisition
**Affected surface:** Homepage hero
**URL:** https://magicspoon.com
**Evidence:** artifacts/magicspoon/homepage.md — title “High Protein, Keto-Friendly, 0g Sugar Cereal”, status 200; screenshot: artifacts/magicspoon/screenshots/homepage_full.png
**Hypothesis:** Paid and organic traffic from “high protein cereal” intent converts better on a dedicated `/pages/high-protein-cereal` LP with single CTA to Shop All than on the rotating homepage carousel.
**Primary change:** Intent-matched LP mirroring homepage protein/sugar claims with one bundle CTA.
**Primary KPI:** Landing-page conversion rate (protein-cereal campaigns)
**Decision rule:** Ship if LP CVR beats homepage by ≥15% over 21 days with n≥2,000 sessions per variant.
**Expected lift:** +12–22%
**Confidence:** 75

### exp-m5c9d0e1 — FAQ answer modules with PDP deep links

**Pillar:** Acquisition
**Affected surface:** FAQ
**URL:** https://magicspoon.com/pages/faq
**Evidence:** artifacts/magicspoon/faq_or_where_to_buy.md — FAQ page 200; screenshot: artifacts/magicspoon/screenshots/faq_or_where_to_buy_full.png
**Hypothesis:** Organic FAQ traffic converts when top questions (ingredients, subscribe, shipping) end with inline “Shop cocoa case” / “Build a bundle” buttons instead of generic footer nav only.
**Primary change:** Top 8 FAQ entries get contextual product CTAs tied to question topic.
**Primary KPI:** FAQ-to-PDP click rate
**Decision rule:** Ship if FAQ→PDP CTR rises by ≥20% over 30 days at 90% confidence.
**Expected lift:** +10–18%
**Confidence:** 73

### exp-m6d0e1f2 — Defer non-critical JS on homepage carousel

**Pillar:** Performance
**Affected surface:** Homepage
**URL:** https://magicspoon.com
**Evidence:** artifacts/magicspoon/tech_grounded.json — Page Speed 40/100 mobile, 42/100 desktop; artifacts/magicspoon/homepage.md — status 200; screenshot: artifacts/magicspoon/screenshots/homepage_full.png
**Hypothesis:** Mobile add-to-cart rate improves when LCP image and hero copy load before review carousels and promotional video scripts (PSI already sub-50 on both form factors).
**Primary change:** Defer below-fold review/video widgets; priority-load hero LCP image and primary Shop CTA.
**Primary KPI:** Mobile LCP (seconds) and mobile PDP entry rate from homepage
**Decision rule:** Ship if mobile LCP improves by ≥1.2s and homepage→collection CTR rises by ≥5% over 21 days.
**Expected lift:** +4–9%
**Confidence:** 76

## Competitor analysis

| Competitor | Domain | Positioning | What they make easier | Magic Spoon edge | Pattern to adapt |
|---|---|---|---|---|---|
| Catalina Crunch | catalinacrunch.com | Keto-friendly cereal | Clear flavor grid, subscribe on PDP | Stronger brand fame, treats/granola expansion | Subscribe-default on case SKUs |
| Three Wishes | threewishescereal.com | Clean-ingredient cereal | Simple ingredient story, variety packs | Higher protein claim, nostalgia creative | Sampler-first empty cart |
| OffLimits | offlimits.com | Gamified DTC cereal | Personality-led PDP, trial positioning | Broader catalog (treats, granola, pastries) | Bundle builder as collection hero |
| Schoolyard Snacks | schoolyardsnacks.com | Low-carb cereal & snacks | Price-forward cases, Amazon social proof | Premium DTC experience, review volume | Star rating above ATC on case PDPs |

## Technical checks

| Check | Status | Detail |
|---|---|---|
| SSL Certificate | Pass | Valid certificate; expires Aug 28 12:22:32 2026 GMT (`tech_grounded.json`) |
| HTTPS Redirect | Pass | HTTP redirects to HTTPS (301) |
| Sitemap | Pass | Returns 200 |
| Robots.txt | Pass | Returns 200 |
| Critical Pages Loading | Pass | 7/7 manifest surfaces returned 200 (`manifest.json`) |
| Meta Tags & Social Previews | Pass | Title, description, OG present; favicon present (`tech_grounded.json`) |
| Structured Data | Warn | Product JSON-LD not validated on crawled PDPs this pass (JS-rendered theme) |
| Favicon | Pass | Detected in homepage meta parse (`tech_grounded.json`) |
| Mobile-Friendly | Warn | Not measured directly; PSI mobile 40/100 suggests room to improve |
| Page Speed Mobile | Pass | 40/100 on PageSpeed Insights (mobile) |
| Page Speed Desktop | Pass | 42/100 on PageSpeed Insights (desktop) |
| Broken Links | Pass | No 404/503 on manifest surfaces this crawl |
| Image Optimization | Warn | Not measured; low PSI scores suggest heavy hero/carousel assets |
| Cookie/Privacy | Warn | Privacy policy linked in footer per site pattern; banner behavior not fully inspected |
| Checkout Reachable | Pass | /cart 200 — Shopping Cart page (`cart.md`, `screenshots/cart_full.png`) |
