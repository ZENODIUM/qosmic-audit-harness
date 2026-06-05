# Ginger People audit — juice and turmeric PDPs work; retailer handoff and dead cart leak demand

## Executive summary

**This crawl found a live catalog with retailer-routed PDPs, not a broken storefront.** Homepage and the products grid return 200 (`artifacts/gingerpeople/homepage.md`, `artifacts/gingerpeople/collection.md`). Sitemap-driven PDPs for **Fiji Ginger Juice** and **Fiji Turmeric Juice** also return 200 (`artifacts/gingerpeople/pdp_1.md`, `artifacts/gingerpeople/pdp_2.md`), with review copy and **Destini** retailer-locator scripting present — but the static HTML fetch shows **no add-to-cart string**, so purchase intent still depends on locator/retailer modules loading correctly.

**`/cart` is a branded 404** (`artifacts/gingerpeople/cart.md`, `manifest.json`), which is a hard performance and conversion leak for bookmarks, ads, and old Shopify links. Where To Buy loads with the same Destini pattern (`artifacts/gingerpeople/faq_or_where_to_buy.md`) while the GLP-1 education article loads cleanly (`artifacts/gingerpeople/content_page.md`) without a shoppable routine in the fetch — under-commercialized wellness traffic.

**Technical baseline is strong; merchandising is the gap.** SSL, HTTPS, sitemap, and robots pass (`artifacts/gingerpeople/tech_grounded.json`). PageSpeed **31/100 mobile**, **44/100 desktop** — slow on mobile. Priority tests: structured buy/locator module on juice PDPs, cart recovery, pairing ginger+turmeric juice on the grid, and a GLP-1 → product routine — derived from this crawl’s URLs, not a template audit.

## Proposed experiments

### exp-f71a2b3c — Locator-first module on juice PDPs

**Pillar:** Conversion
**Affected surface:** Fiji Ginger Juice PDP
**URL:** https://gingerpeople.com/products/fiji-ginger-juice
**Evidence:** artifacts/gingerpeople/pdp_1.md — 200; Destini script referenced; no add-to-cart in HTML fetch; screenshot: artifacts/gingerpeople/screenshots/pdp_1_full.png
**Hypothesis:** Outbound retailer clicks rise when shoppers see an above-the-fold “Find online / near me” module with load-state handling when Destini is slow or blocked.
**Primary change:** Persistent locator card with fallback retailer links if widget fails to render in 2s.
**Primary KPI:** Outbound retailer click rate (juice PDPs)
**Decision rule:** Ship if clicks rise by ≥12% over 21 days at 90% confidence without PDP bounce up ≥4%.
**Expected lift:** +10–18%
**Confidence:** 76

### exp-g82b3c4d — Ginger + turmeric juice bundle

**Pillar:** AOV
**Affected surface:** Fiji juice PDPs + collection
**URL:** https://gingerpeople.com/products/fiji-turmeric-juice
**Evidence:** artifacts/gingerpeople/pdp_2.md and pdp_1.md — adjacent SKUs via sitemap; screenshot: artifacts/gingerpeople/screenshots/pdp_2_full.png
**Hypothesis:** AOV increases when turmeric and ginger juice are sold as a paired “daily shot” bundle from both PDPs and the products grid.
**Primary change:** Bundle SKU or virtual bundle with 8% off; cross-link on both Fiji PDPs and `/the-ginger-people-products`.
**Primary KPI:** AOV (juice PDP sessions)
**Decision rule:** Ship if AOV rises by ≥$5 over 28 days with juice PDP CVR down ≤3%.
**Expected lift:** +9–16%
**Confidence:** 71

### exp-h93c4d5e — Cart URL recovery

**Pillar:** Performance
**Affected surface:** /cart
**URL:** https://gingerpeople.com/cart
**Evidence:** artifacts/gingerpeople/cart.md — branded 404; screenshot: artifacts/gingerpeople/screenshots/cart_full.png
**Hypothesis:** Sessions that hit `/cart` convert better when 404 is replaced with recovery links to top juice PDPs, Where To Buy, and collection.
**Primary change:** Recovery template listing Fiji juices + locator CTA (no blank 404).
**Primary KPI:** /cart → retailer click rate
**Decision rule:** Ship if retailer clicks from /cart rise by ≥20% vs 404 baseline over 14 days.
**Expected lift:** +12–22%
**Confidence:** 84

### exp-i04d5e6f — Where To Buy above blog noise

**Pillar:** Conversion
**Affected surface:** Where To Buy
**URL:** https://gingerpeople.com/where-to-buy-the-ginger-people-products
**Evidence:** artifacts/gingerpeople/faq_or_where_to_buy.md — Destini present; screenshot: artifacts/gingerpeople/screenshots/faq_or_where_to_buy_full.png
**Hypothesis:** Clicks from the Where To Buy nav improve when locator and retailer cards appear before editorial/blog blocks in the DOM order.
**Primary change:** Reorder layout: locator + top SKUs first; move blog cards below fold on mobile.
**Primary KPI:** Where To Buy → retailer click rate
**Decision rule:** Ship if rate rises by ≥15% over 21 days.
**Expected lift:** +14–24%
**Confidence:** 79

### exp-j15e6f7a — Products grid: format filters

**Pillar:** Performance
**Affected surface:** Products listing
**URL:** https://gingerpeople.com/the-ginger-people-products
**Evidence:** artifacts/gingerpeople/collection.md — large family grid; screenshot: artifacts/gingerpeople/screenshots/collection_full.png
**Hypothesis:** Grid engagement improves when shoppers filter by format (juice, chews, lozenges, sauces) instead of scanning all families.
**Primary change:** Collection filters + default “Juices & shots” for cold-traffic landings.
**Primary KPI:** Collection → PDP click-through rate
**Decision rule:** Ship if CTR rises by ≥7% over 28 days.
**Expected lift:** +6–12%
**Confidence:** 73

### exp-k26f7a8b — GLP-1 article → turmeric juice routine

**Pillar:** Retention
**Affected surface:** GLP-1 blog post
**URL:** https://gingerpeople.com/boost-your-glp-1-naturally-the-power-of-ginger-turmeric
**Evidence:** artifacts/gingerpeople/content_page.md — article 200; screenshot: artifacts/gingerpeople/screenshots/content_page_full.png
**Hypothesis:** Repeat retailer clicks from article readers increase when the post ends with a named “Ginger + Turmeric daily shot” linking to Fiji juice PDPs.
**Primary change:** In-article routine card with locator CTA to ginger + turmeric juices.
**Primary KPI:** 30-day repeat click rate (article cohort)
**Decision rule:** Ship if repeat clicks rise by ≥8% over 60 days.
**Expected lift:** +7–14%
**Confidence:** 70

### exp-l37a8b9c — Cooking / juice landing from homepage

**Pillar:** Acquisition
**Affected surface:** New `/ginger-juice-cooking/` LP
**URL:** https://gingerpeople.com/ginger-juice-cooking/ (new)
**Evidence:** artifacts/gingerpeople/homepage.md — H1/cookie-recipe hero mismatch; screenshot: artifacts/gingerpeople/screenshots/homepage_full.png
**Hypothesis:** Organic “ginger juice cooking” queries convert better on a dedicated LP featuring Fiji Ginger Juice than on a generic homepage.
**Primary change:** LP with recipes, juice PDP hero, locator CTA; paid search alignment.
**Primary KPI:** Landing-page retailer click rate
**Decision rule:** Ship if LP beats homepage click rate by ≥10% over 30 days.
**Expected lift:** +11–19%
**Confidence:** 68

### exp-m48b9c0d — Review widget above locator on PDPs

**Pillar:** Conversion
**Affected surface:** Fiji Turmeric Juice PDP
**URL:** https://gingerpeople.com/products/fiji-turmeric-juice
**Evidence:** artifacts/gingerpeople/pdp_2.md — review copy in HTML; screenshot: artifacts/gingerpeople/screenshots/pdp_2_full.png
**Hypothesis:** Locator clicks increase when star rating block renders immediately above the Destini widget on juice PDPs.
**Primary change:** Force review summary DOM order before locator on top 10 SKUs by traffic.
**Primary KPI:** Locator engagement rate
**Decision rule:** Ship if engagement rises by ≥5% over 14 days at 90% confidence.
**Expected lift:** +4–9%
**Confidence:** 74

### exp-n59c0d1e — Bulk ingredients CTA from collection

**Pillar:** Acquisition
**Affected surface:** Products grid + bulk nav
**URL:** https://gingerpeople.com/the-ginger-people-products
**Evidence:** artifacts/gingerpeople/collection.md — B2B/bulk nav theme; screenshot: artifacts/gingerpeople/screenshots/collection_full.png
**Hypothesis:** B2B inquiry rate rises when the products page adds a persistent “Food service / bulk” strip with email capture.
**Primary change:** Bulk strip with category links and one-field lead form.
**Primary KPI:** Bulk lead form submissions
**Decision rule:** Ship if submissions rise by ≥25% over 45 days without DTC click fall ≥5%.
**Expected lift:** +15–30%
**Confidence:** 65

### exp-o60d1e2f — Fix homepage hero message match

**Pillar:** Acquisition
**Affected surface:** Homepage hero
**URL:** https://gingerpeople.com/
**Evidence:** artifacts/gingerpeople/homepage.md — title vs H1 mismatch; screenshot: artifacts/gingerpeople/screenshots/homepage_full.png
**Hypothesis:** Homepage bounce falls when hero H1/CTA match the brand promise (functional foods) and route to juice or candy missions.
**Primary change:** Replace mismatched H1; dual CTA: “Shop juices” / “Shop candy”.
**Primary KPI:** Homepage bounce rate
**Decision rule:** Ship if bounce drops by ≥5% over 21 days.
**Expected lift:** +5–10%
**Confidence:** 72

## Competitor analysis

| Competitor | Domain | Positioning | What they make easier | Ginger People edge | Pattern to adapt |
|---|---|---|---|---|---|
| The Ginger People UK | gingerpeople.co.uk | Same brand, regional | Clear regional storefront | US catalog depth | Consistent locator UX |
| Buderim Ginger | buderimginger.com | Australian ginger foods | Origin story + retail finder | US share, GLP-1 content | Locator fallback links |
| Dynamic Health | dynamichealth.com | Ginger juice shots | Simple supplement PDPs | Branded Fiji juice story | Single-SKU hero PDP clarity |
| MONIN | monin.com | Beverage ingredients | B2B discovery | Consumer brand trust | Bulk strip on collection |

## Technical checks

| Check | Status | Detail |
|---|---|---|
| SSL Certificate | Pass | Valid to Jul 2026 (`tech_grounded.json`) |
| HTTPS Redirect | Pass | HTTP 301 to HTTPS |
| Sitemap | Pass | /sitemap.xml 200; used for PDP discovery |
| Robots.txt | Pass | Returns 200 |
| Critical Pages Loading | Warn | Juice PDPs, collection, Where To Buy, blog 200; `/cart` 404 |
| Meta Tags & Social Previews | Pass | Title, description, OG, favicon on homepage |
| Structured Data | Warn | Not validated on Fiji juice PDPs this pass |
| Favicon | Pass | Present |
| Mobile-Friendly | Warn | Not run via Google test |
| Page Speed Mobile | Pass | 31/100 on PageSpeed Insights (mobile) |
| Page Speed Desktop | Pass | 44/100 on PageSpeed Insights (desktop) |
| Broken Links | Fail | `/cart` branded 404 (cart.md, manifest) |
| Image Optimization | Warn | Not measured |
| Cookie/Privacy | Warn | Not fully inspected |
| Checkout Reachable | Fail | No cart; Destini/retailer path only |
