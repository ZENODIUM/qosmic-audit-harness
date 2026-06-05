# Zen Rojas audit — DTC checkout works; FAQ outage and first-purchase guidance are the gaps

## Executive summary

**Zen Rojas is a functional Shopify DTC tea shop on this crawl.** Six of seven manifest surfaces returned 200, including `/cart` with a real Shopping Cart page (`artifacts/zenrojas/cart.md`; screenshot: `artifacts/zenrojas/screenshots/cart_full.png`). Hero PDPs **Organic Black Tea** and **Bodyguard Organic Tea** both show add-to-cart in HTML (`artifacts/zenrojas/pdp_1.md`, `artifacts/zenrojas/pdp_2.md`) with matching screenshots — unlike retailer-routed brands where cart and ATC are absent.

**Merchandising and reliability—not checkout plumbing—is the main leak.** The teas collection and homepage load (`artifacts/zenrojas/collection.md`, `artifacts/zenrojas/homepage.md`) but the crawl notes no sampler-first hero or guided first-purchase path. **`/pages/faqs` returned 503** this run (`artifacts/zenrojas/faq_or_where_to_buy.md`; screenshot shows Shopify error page), which hurts trust and blocks FAQ→product handoffs. The weekly blog hub loads (`artifacts/zenrojas/content_page.md`) without an obvious shoppable module in static notes.

**Technical baseline is mostly fine with Warns.** HTTPS, sitemap, and robots pass per `artifacts/zenrojas/tech_grounded.json`; SSL verification failed locally; PageSpeed **66/100 mobile**, **78/100 desktop**. Priority tests: fix FAQ availability, sampler-led collection, subscription on hero SKUs, cart threshold merchandising, and blog→product modules — all tied to URLs and screenshots from this run.

## Proposed experiments

### exp-z7a1b2c3 — Sampler hero on teas collection

**Pillar:** Conversion
**Affected surface:** Teas collection
**URL:** https://zenrojas.com/collections/teas
**Evidence:** artifacts/zenrojas/collection.md — Teas H1, grid 200; screenshot: artifacts/zenrojas/screenshots/collection_full.png
**Hypothesis:** Collection-to-PDP CTR rises when tea-bag and loose-leaf sampler SKUs sit in a hero row above the full grid.
**Primary change:** Hero with two sampler products and “New to Zen Rojas?” copy linking to a working FAQ or quiz page.
**Primary KPI:** Collection click-through rate
**Decision rule:** Ship if CTR rises by ≥9% over 21 days at 90% confidence.
**Expected lift:** +8–15%
**Confidence:** 76

### exp-z8b2c3d4 — Star rating above add-to-cart on black tea

**Pillar:** Conversion
**Affected surface:** Organic Black Tea PDP
**URL:** https://zenrojas.com/products/blacktea
**Evidence:** artifacts/zenrojas/pdp_1.md — ATC and review copy in HTML; screenshot: artifacts/zenrojas/screenshots/pdp_1_full.png
**Hypothesis:** Add-to-cart rate on the black tea PDP improves when aggregated stars render directly above the ATC button.
**Primary change:** Review summary block moved above ATC on top five SKUs by sessions.
**Primary KPI:** Add-to-cart rate (black tea PDP)
**Decision rule:** Ship if ATC rises by ≥5% over 14 days without return rate up ≥2%.
**Expected lift:** +4–9%
**Confidence:** 78

### exp-z9c3d4e5 — Immunity duo bundle (black + bodyguard)

**Pillar:** AOV
**Affected surface:** Bodyguard PDP + cart upsell
**URL:** https://zenrojas.com/products/bodyguardtea
**Evidence:** artifacts/zenrojas/pdp_2.md — Bodyguard PDP 200; screenshot: artifacts/zenrojas/screenshots/pdp_2_full.png; paired with pdp_1 from sitemap
**Hypothesis:** AOV increases when “Daily Defense Duo” bundles black tea and Bodyguard at 10% off with one-click add from either PDP.
**Primary change:** Bundle SKU + cart-drawer upsell after either SKU added.
**Primary KPI:** AOV (bundle-exposed sessions)
**Decision rule:** Ship if AOV rises by ≥$5 over 28 days with sitewide CVR down ≤3%.
**Expected lift:** +10–17%
**Confidence:** 73

### exp-z0d4e5f6 — Subscribe-and-save on hero SKUs

**Pillar:** Retention
**Affected surface:** Black tea and Bodyguard PDPs
**URL:** https://zenrojas.com/products/blacktea
**Evidence:** artifacts/zenrojas/pdp_1.md — standard ATC present; screenshot: artifacts/zenrojas/screenshots/pdp_1_full.png; no subscription option in HTML notes
**Hypothesis:** 60-day repeat purchase rate improves when Subscribe & Save (10% off, skip anytime) is enabled on the two crawled hero teas.
**Primary change:** Shopify subscription widget on blacktea and bodyguardtea PDPs.
**Primary KPI:** 60-day repeat purchase rate
**Decision rule:** Ship if repeat rate rises by ≥7% over 90 days with churn refunds up ≤1%.
**Expected lift:** +6–13%
**Confidence:** 71

### exp-z1e5f6a7 — Tea finder quiz landing

**Pillar:** Acquisition
**Affected surface:** New `/find-your-tea/` page
**URL:** https://zenrojas.com/pages/find-your-tea (new)
**Evidence:** artifacts/zenrojas/collection.md — many SKUs without guided path; screenshot: artifacts/zenrojas/screenshots/collection_full.png
**Hypothesis:** Paid and organic landing CVR beats `/collections/teas` when a four-question quiz routes to black tea, bodyguard, or samplers.
**Primary change:** Quiz (caffeine, flavor, format, gift vs self) with deep links to discovered PDPs.
**Primary KPI:** Landing-page purchase conversion rate
**Decision rule:** Ship if LP CVR beats collection baseline by ≥11% over 30 days.
**Expected lift:** +11–19%
**Confidence:** 75

### exp-z2f6a7b8 — Weekly blog shoppable footer

**Pillar:** Acquisition
**Affected surface:** Weekly blog hub
**URL:** https://zenrojas.com/blogs/weekly-blog
**Evidence:** artifacts/zenrojas/content_page.md — blog index 200; screenshot: artifacts/zenrojas/screenshots/content_page_full.png
**Hypothesis:** Blog-session purchase rate rises when each featured post ends with one “brew this week” product card.
**Primary change:** Standard blog footer module linking to black tea or rotating sampler.
**Primary KPI:** Blog session conversion rate
**Decision rule:** Ship if blog CVR rises by ≥8% over 45 days.
**Expected lift:** +8–14%
**Confidence:** 70

### exp-z3a7b8c9 — Cart free-shipping progress bar

**Pillar:** AOV
**Affected surface:** Cart
**URL:** https://zenrojas.com/cart
**Evidence:** artifacts/zenrojas/cart.md — Shopping Cart H1, status 200; screenshot: artifacts/zenrojas/screenshots/cart_full.png
**Hypothesis:** AOV rises when a dynamic “Add $X for free shipping” bar suggests a low-cost tea add-on before checkout.
**Primary change:** Progress bar + one-click sampler add in cart template.
**Primary KPI:** AOV
**Decision rule:** Ship if AOV rises by ≥$4 over 21 days with abandonment up ≤2%.
**Expected lift:** +7–12%
**Confidence:** 77

### exp-z4b8c9d0 — Restore FAQs and add sampler strip

**Pillar:** Conversion
**Affected surface:** FAQs
**URL:** https://zenrojas.com/pages/faqs
**Evidence:** artifacts/zenrojas/faq_or_where_to_buy.md — 503 error page this crawl; screenshot: artifacts/zenrojas/screenshots/faq_or_where_to_buy_full.png
**Hypothesis:** FAQ→purchase rate improves when `/pages/faqs` loads reliably and a persistent “Still deciding? Start with the sampler” strip appears after brewing questions.
**Primary change:** Fix 503 root cause; sticky CTA to sampler collection or PDP on working FAQ template.
**Primary KPI:** FAQ page load success rate + FAQ → add-to-cart rate
**Decision rule:** Ship if FAQ 503 rate is 0% for 14 days and FAQ ATC rises by ≥10% over 28 days after fix.
**Expected lift:** +6–11%
**Confidence:** 72

### exp-z5c9d0e1 — Caffeine and format filters on collection

**Pillar:** Performance
**Affected surface:** Teas collection UX
**URL:** https://zenrojas.com/collections/teas
**Evidence:** artifacts/zenrojas/collection.md — single grid, no filter chips in notes; screenshot: artifacts/zenrojas/screenshots/collection_full.png
**Hypothesis:** Collection bounce drops when shoppers filter by caffeine level, bag vs loose, and organic certification.
**Primary change:** Shopify collection filters + default sort “Best for beginners.”
**Primary KPI:** Collection bounce rate
**Decision rule:** Ship if bounce falls by ≥5% over 21 days without hurting pages per session.
**Expected lift:** +5–10%
**Confidence:** 74

### exp-z6d0e1f2 — Post-purchase brewing email series

**Pillar:** Retention
**Affected surface:** Post-purchase email (Klaviyo)
**URL:** https://zenrojas.com/ (onsite purchase trigger)
**Evidence:** artifacts/zenrojas/cart.md — checkout path exists (200); screenshot: artifacts/zenrojas/screenshots/cart_full.png
**Hypothesis:** 45-day repeat purchase rate improves with a three-email series (brew guide → complementary SKU → subscribe offer) keyed to first SKU purchased.
**Primary change:** Flow for black tea vs herbal (bodyguard) purchasers with SKU-specific content.
**Primary KPI:** 45-day repeat purchase rate
**Decision rule:** Ship if repeat rate rises by ≥8% over 60 days at 90% confidence.
**Expected lift:** +8–15%
**Confidence:** 68

## Competitor analysis

| Competitor | Domain | Positioning | What they make easier | Zen Rojas edge | Pattern to adapt |
|---|---|---|---|---|---|
| Harney & Sons | harney.com | Premium tea discovery | Samplers, gift sets, caffeine labels | Boutique organic story | Sampler-first collection |
| Art of Tea | artoftea.com | Specialty loose leaf | Subscription and education | Direct founder brand | Subscribe on hero PDPs |
| Rishi Tea | rishi-tea.com | Organic specialty tea | Origin stories per SKU | Bodyguard immunity positioning | PDP storytelling + bundle |
| Adagio Teas | adagio.com | Custom blends and samplers | Flavor search and trial sets | Curated organic catalog | Quiz landing for first purchase |

## Technical checks

| Check | Status | Detail |
|---|---|---|
| SSL Certificate | Warn | Could not verify — local SSL trust error (`tech_grounded.json`) |
| HTTPS Redirect | Pass | HTTP redirects to HTTPS (301) |
| Sitemap | Pass | Returns 200 |
| Robots.txt | Pass | Returns 200 |
| Critical Pages Loading | Warn | 6/7 manifest surfaces 200; `/pages/faqs` returned 503 (`faq_or_where_to_buy.md`) |
| Meta Tags & Social Previews | Pass | Title, description, OG present; favicon not found |
| Structured Data | Warn | Product JSON-LD not validated on crawled PDPs this pass |
| Favicon | Warn | Not detected in homepage meta parse |
| Mobile-Friendly | Warn | Not measured this run |
| Page Speed Mobile | Pass | 66/100 on PageSpeed Insights (mobile) |
| Page Speed Desktop | Pass | 78/100 on PageSpeed Insights (desktop) |
| Broken Links | Warn | FAQ page 503 on manifest URL |
| Image Optimization | Warn | Not measured |
| Cookie/Privacy | Warn | Not fully inspected |
| Checkout Reachable | Pass | /cart 200 — Shopping Cart page (`cart.md`, `screenshots/cart_full.png`) |
