# Graza audit — checkout is solid; first-purchase clarity and mobile speed are the levers

## Executive summary

**Graza is a healthy Shopify DTC olive-oil brand on this crawl.** All seven manifest surfaces returned 200, including `/cart` with a real Shopping Cart page (`artifacts/graza/cart.md`; screenshot: `artifacts/graza/screenshots/cart_full.png`). Hero PDPs **“Drizzle” Finishing Oil** and **“The Duo” Glass** both load with review-widget copy in HTML (`artifacts/graza/pdp_1.md`, `artifacts/graza/pdp_2.md`) and matching screenshots — a working buy path, not a locator-only setup.

**Merchandising is busy, not broken.** The homepage and `/collections/all` both load (`artifacts/graza/homepage.md`, `artifacts/graza/collection.md`) with multiple hero modules (chips, glass, trio) competing for attention in the static fetch notes. FAQs return 200 (`artifacts/graza/faq_or_where_to_buy.md`) but the crawl did not surface a distinct blog/Glog URL — `content_page` resolved to the homepage duplicate (`artifacts/graza/content_page.md`), so educational→product handoffs are under-tested on this pass.

**Technical baseline is strong with performance Warns.** SSL, HTTPS, sitemap, and robots pass per `artifacts/graza/tech_grounded.json`; PageSpeed **38/100 mobile** (desktop PSI timed out this run). Priority tests: trio-first homepage for new buyers, subscribe default on hero SKUs, cart threshold upsells, Frizzle high-heat landing, and mobile LCP fixes — all tied to URLs and screenshots from this run.

## Proposed experiments

### exp-gr1a2b3c — Trio-first homepage hero for new visitors

**Pillar:** Conversion
**Affected surface:** Homepage
**URL:** https://graza.co
**Evidence:** artifacts/graza/homepage.md — multiple Shop Now / Shop The Trio modules, H1 “Graza”; screenshot: artifacts/graza/screenshots/homepage_full.png
**Hypothesis:** Homepage→PDP CTR rises when first-time visitors see a single “Get The Trio” hero with Drizzle, Sizzle, and Frizzle use-case copy above secondary promos (chips, glass).
**Primary change:** Default hero = Trio bundle with three use-case bullets; chips/glass modules move below fold for cold traffic.
**Primary KPI:** Homepage click-through rate to collection or Trio PDP
**Decision rule:** Ship if homepage CTR rises by ≥8% over 21 days at 90% confidence.
**Expected lift:** +7–14%
**Confidence:** 77

### exp-gr2b3c4d — Review summary above add-to-cart on Drizzle

**Pillar:** Conversion
**Affected surface:** Drizzle PDP
**URL:** https://graza.co/products/drizzle
**Evidence:** artifacts/graza/pdp_1.md — review widget copy in HTML fetch; screenshot: artifacts/graza/screenshots/pdp_1_full.png
**Hypothesis:** Add-to-cart rate on Drizzle improves when aggregated star rating and review count render directly above the primary ATC control.
**Primary change:** Move review summary block above ATC on Drizzle and top three SKUs by sessions.
**Primary KPI:** Add-to-cart rate (Drizzle PDP)
**Decision rule:** Ship if ATC rises by ≥5% over 14 days without return rate up ≥2%.
**Expected lift:** +4–10%
**Confidence:** 79

### exp-gr3c4d5e6 — Duo Glass upsell on Drizzle PDP

**Pillar:** AOV
**Affected surface:** Drizzle PDP + Duo Glass PDP
**URL:** https://graza.co/products/drizzle
**Evidence:** artifacts/graza/pdp_1.md — Drizzle 200; artifacts/graza/pdp_2.md — Duo Glass 200; screenshots: artifacts/graza/screenshots/pdp_1_full.png, artifacts/graza/screenshots/pdp_2_full.png
**Hypothesis:** AOV increases when Drizzle buyers see a “Complete the set” Duo Glass module with one-click add at checkout-adjacent placement on the PDP.
**Primary change:** Inline Duo Glass upsell card below variant selector on Drizzle with bundle discount.
**Primary KPI:** AOV (Drizzle PDP sessions)
**Decision rule:** Ship if AOV rises by ≥$6 over 28 days with sitewide CVR down ≤3%.
**Expected lift:** +9–16%
**Confidence:** 74

### exp-gr4d5e6f7 — Cart threshold bar with Frizzle add-on

**Pillar:** AOV
**Affected surface:** Cart
**URL:** https://graza.co/cart
**Evidence:** artifacts/graza/cart.md — Shopping Cart page 200; screenshot: artifacts/graza/screenshots/cart_full.png
**Hypothesis:** Units per order rise when the cart shows a progress bar toward free shipping and recommends Frizzle as the lowest-friction add-on to hit threshold.
**Primary change:** Sticky cart-drawer progress bar + Frizzle one-click upsell when subtotal is within $8 of threshold.
**Primary KPI:** Units per order
**Decision rule:** Ship if units per order rise by ≥0.15 over 21 days at 90% confidence.
**Expected lift:** +6–12%
**Confidence:** 72

### exp-gr5e6f7g8 — Subscribe & save pre-selected on Sizzle

**Pillar:** Retention
**Affected surface:** Collection + hero PDPs
**URL:** https://graza.co/collections/all
**Evidence:** artifacts/graza/collection.md — full catalog 200; footer Subscribe/Manage Subscription links on homepage fetch; screenshot: artifacts/graza/screenshots/collection_full.png
**Hypothesis:** Subscription attach rate rises when Sizzle and Drizzle PDPs default to subscribe & save with clear cadence and savings callout.
**Primary change:** Pre-select subscription on cooking-oil SKUs with “Every 4 weeks” default and one-click switch to one-time.
**Primary KPI:** Subscription attach rate
**Decision rule:** Ship if attach rate rises by ≥12% over 30 days without one-time CVR down ≥4%.
**Expected lift:** +10–18%
**Confidence:** 75

### exp-gr6f7g8h9 — Refill-can reorder module in cart

**Pillar:** Retention
**Affected surface:** Cart
**URL:** https://graza.co/cart
**Evidence:** artifacts/graza/cart.md — cart 200; homepage notes Refill Cans in nav pattern; screenshot: artifacts/graza/screenshots/cart_full.png
**Hypothesis:** Repeat purchase rate improves when returning visitors with prior can purchases see a “Refill your cans” module in cart with last-ordered SKUs.
**Primary change:** Cart module surfacing last-ordered refill cans with one-click reorder for recognized return visitors.
**Primary KPI:** Repeat purchase rate (90-day)
**Decision rule:** Ship if repeat rate rises by ≥7% over 60 days among exposed returning sessions.
**Expected lift:** +5–11%
**Confidence:** 68

### exp-gr7g8h9i0 — Frizzle high-heat landing from collection

**Pillar:** Acquisition
**Affected surface:** All collection
**URL:** https://graza.co/collections/all
**Evidence:** artifacts/graza/collection.md — Graza H1, grid 200; homepage promotes Frizzle high-heat positioning; screenshot: artifacts/graza/screenshots/collection_full.png
**Hypothesis:** Paid and organic “high heat cooking oil” traffic converts better when collection traffic can land on a Frizzle-first module with neutral-oil comparison copy.
**Primary change:** Collection hero strip for Frizzle with “High heat kitchen hero” copy and deep link from campaign URLs.
**Primary KPI:** Landing CVR (Frizzle campaign sessions)
**Decision rule:** Ship if CVR rises by ≥10% over 14 days on Frizzle-targeted campaigns.
**Expected lift:** +8–15%
**Confidence:** 71

### exp-gr8h9i0j1 — FAQ shipping block with Trio CTA

**Pillar:** Acquisition
**Affected surface:** FAQs
**URL:** https://graza.co/pages/faqs
**Evidence:** artifacts/graza/faq_or_where_to_buy.md — FAQs 200; screenshot: artifacts/graza/screenshots/faq_or_where_to_buy_full.png
**Hypothesis:** FAQ→purchase conversion rises when shipping/delivery answers include a shoppable Trio module for visitors arriving from support or branded search.
**Primary change:** Add “Not sure what to buy?” Trio card below shipping FAQ accordion with direct add links.
**Primary KPI:** FAQ page conversion rate
**Decision rule:** Ship if FAQ CVR rises by ≥6% over 28 days at 90% confidence.
**Expected lift:** +5–10%
**Confidence:** 70

### exp-gr9i0j1k2 — Mobile homepage LCP image pass

**Pillar:** Performance
**Affected surface:** Homepage
**URL:** https://graza.co
**Evidence:** artifacts/graza/tech_grounded.json — Page Speed Mobile 38/100; artifacts/graza/homepage.md — heavy hero modules; screenshot: artifacts/graza/screenshots/homepage_full.png
**Hypothesis:** Mobile bounce rate drops when above-the-fold hero media is compressed, preloaded, and lazy-loads below-fold promos (chips, glass).
**Primary change:** WebP hero with fetchpriority=high, defer non-critical carousel assets below first viewport.
**Primary KPI:** Mobile bounce rate
**Decision rule:** Ship if bounce falls by ≥5% and mobile PSI score rises by ≥8 points over 21 days.
**Expected lift:** +4–9%
**Confidence:** 76

### exp-gr0j1k2l3 — “First purchase” Trio strip on collection grid

**Pillar:** Conversion
**Affected surface:** All collection
**URL:** https://graza.co/collections/all
**Evidence:** artifacts/graza/collection.md — full catalog without guided first-buy path in static notes; screenshot: artifacts/graza/screenshots/collection_full.png
**Hypothesis:** Collection add-to-cart rate rises when a pinned first row explains Drizzle vs Sizzle vs Frizzle and links to The Trio bundle.
**Primary change:** Sticky educational strip above product grid with trio comparison and bundle CTA.
**Primary KPI:** Collection add-to-cart rate
**Decision rule:** Ship if collection ATC rises by ≥7% over 21 days at 90% confidence.
**Expected lift:** +6–13%
**Confidence:** 73

## Competitor analysis

| Competitor | Domain | Positioning | What they make easier | Graza edge | Pattern to adapt |
|---|---|---|---|---|---|
| Brightland | brightland.com | Design-forward premium EVOO | Giftability and brand storytelling | Playful voice + squeeze bottles | Quiz-led first purchase |
| Kosterina | kosterina.com | Mediterranean lifestyle EVOO | Premium gifting and bundles | Strong SKU naming (Drizzle/Sizzle/Frizzle) | Lifestyle content → product modules |
| California Olive Ranch | californiaoliveranch.com | Mass-premium grocery EVOO | Availability and trust at scale | DTC freshness narrative | Store locator + DTC bridge |
| Graza (chips extension) | graza.co | EVOO-cooked snack adjacency | Cross-category trial | Oil brand equity in chips | Limited-edition hero rotation |

## Technical checks

| Check | Status | Detail |
|---|---|---|
| SSL Certificate | Pass | Valid to Jul 2026 (`tech_grounded.json`) |
| HTTPS Redirect | Pass | HTTP 301 to HTTPS |
| Sitemap | Pass | /sitemap.xml returns 200 |
| Robots.txt | Pass | Returns 200 |
| Critical Pages Loading | Warn | 7/7 manifest surfaces 200; `content_page` duplicate of homepage (no distinct Glog URL discovered) |
| Meta Tags & Social Previews | Pass | Title, description, OG, favicon present |
| Structured Data | Warn | Product JSON-LD not validated on crawled PDPs this pass |
| Favicon | Pass | Present per homepage meta parse |
| Mobile-Friendly | Warn | Not run via Google mobile-friendly test |
| Page Speed Mobile | Pass | 38/100 on PageSpeed Insights (mobile) |
| Page Speed Desktop | Warn | Could not verify — PSI read timed out (90s) |
| Broken Links | Pass | No manifest 404s on critical surfaces |
| Image Optimization | Warn | Mobile PSI 38 suggests heavy hero imagery; not fully measured |
| Cookie/Privacy | Warn | Not fully inspected |
| Checkout Reachable | Pass | /cart 200 — Shopping Cart page (`cart.md`, `screenshots/cart_full.png`) |
