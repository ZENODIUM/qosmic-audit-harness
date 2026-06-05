# Touchland audit — checkout works; scent discovery and mobile meta are the gaps

## Executive summary

**Note:** `touchlandusa.com` did not resolve on this crawl; the live DTC storefront is **touchland.com** (Touchland LLC, Miami). All seven manifest surfaces returned 200, including `/cart` with a working cart page (`artifacts/touchland/cart.md`; screenshot: `artifacts/touchland/screenshots/cart_full.png`). Hero PDPs **Applelicious Power Mist** and **Beach Coco Power Mist** both show add-to-cart in HTML (`artifacts/touchland/pdp_1.md`, `artifacts/touchland/pdp_2.md`) with matching screenshots and review-widget copy.

**Merchandising is bundle- and collab-heavy, not broken.** The homepage and `/collections/bundles` load (`artifacts/touchland/homepage.md`, `artifacts/touchland/collection.md`) with ATC present in static notes. The blog hub loads (`artifacts/touchland/content_page.md`) as a separate content surface. Live catalog patterns include sold-out special editions and mist+case sets — a scent-discovery and availability story more than a checkout-plumbing problem.

**Technical baseline is mixed.** SSL, HTTPS, sitemap, and robots pass per `artifacts/touchland/tech_grounded.json`; **meta title, description, and Open Graph were missing** in the homepage static fetch (likely JS-rendered). PageSpeed **68/100 desktop**; mobile PSI timed out this run. Priority tests: scent-quiz first purchase, case upsell on hero mists, bundle-led collection, blog→product modules, and mobile meta/LCP — tied to URLs and screenshots from this run.

## Proposed experiments

### exp-t1a2b3c4 — Scent quiz hero for cold traffic

**Pillar:** Conversion
**Affected surface:** Homepage
**URL:** https://touchland.com
**Evidence:** artifacts/touchland/homepage.md — ATC and review copy in HTML; screenshot: artifacts/touchland/screenshots/homepage_full.png
**Hypothesis:** Homepage→PDP CTR rises when cold visitors land on a 3-question scent quiz that recommends a Power Mist SKU instead of a generic hero carousel.
**Primary change:** Default hero = interactive scent quiz with direct add links to top three in-stock mists.
**Primary KPI:** Homepage click-through rate to PDP
**Decision rule:** Ship if homepage CTR rises by ≥10% over 21 days at 90% confidence.
**Expected lift:** +8–16%
**Confidence:** 77

### exp-t2b3c4d5 — Review summary above ATC on Applelicious

**Pillar:** Conversion
**Affected surface:** Applelicious Power Mist PDP
**URL:** https://touchland.com/products/applelicious-power-mist
**Evidence:** artifacts/touchland/pdp_1.md — add-to-cart and review widget in HTML; screenshot: artifacts/touchland/screenshots/pdp_1_full.png
**Hypothesis:** Add-to-cart rate improves when aggregated star rating and review count render directly above the primary ATC on Applelicious Power Mist.
**Primary change:** Move review summary block above ATC on top five Power Mist SKUs by sessions.
**Primary KPI:** Add-to-cart rate (Applelicious PDP)
**Decision rule:** Ship if ATC rises by ≥5% over 14 days without return rate up ≥2%.
**Expected lift:** +4–10%
**Confidence:** 79

### exp-t3c4d5e6 — Mist case upsell on Beach Coco PDP

**Pillar:** AOV
**Affected surface:** Beach Coco Power Mist PDP
**URL:** https://touchland.com/products/beach-coco-power-mist
**Evidence:** artifacts/touchland/pdp_2.md — Beach Coco PDP 200, ATC in HTML; screenshot: artifacts/touchland/screenshots/pdp_2_full.png
**Hypothesis:** AOV increases when single-mist buyers see a one-click “Add matching Mist Case” module with bundle savings on the PDP.
**Primary change:** Inline case upsell card below variant selector with compare-at pricing.
**Primary KPI:** AOV (Beach Coco PDP sessions)
**Decision rule:** Ship if AOV rises by ≥$4 over 28 days with sitewide CVR down ≤3%.
**Expected lift:** +9–15%
**Confidence:** 74

### exp-t4d5e6f7 — Bundle-first row on bundles collection

**Pillar:** AOV
**Affected surface:** Bundles collection
**URL:** https://touchland.com/collections/bundles
**Evidence:** artifacts/touchland/collection.md — bundles grid 200, ATC in HTML; screenshot: artifacts/touchland/screenshots/collection_full.png
**Hypothesis:** Units per order rise when the bundles collection pins a “Best value” 3-mist set as the first row with explicit savings vs à la carte.
**Primary change:** Pinned first-row 3-mist bundle card with compare-at pricing and “Best value” label above the full grid.
**Primary KPI:** Units per order (bundles collection sessions)
**Decision rule:** Ship if units per order rise by ≥0.25 over 21 days at 90% confidence.
**Expected lift:** +7–14%
**Confidence:** 73

### exp-t5e6f7g8 — Subscribe & save on Power Mist refills

**Pillar:** Retention
**Affected surface:** Applelicious Power Mist PDP
**URL:** https://touchland.com/products/applelicious-power-mist
**Evidence:** artifacts/touchland/pdp_1.md — hero SKU PDP 200; screenshot: artifacts/touchland/screenshots/pdp_1_full.png
**Hypothesis:** Subscription attach rate rises when Power Mist PDPs default to subscribe & save with clear cadence and savings vs one-time purchase.
**Primary change:** Pre-select subscription on core Power Mist SKUs with one-click switch to one-time.
**Primary KPI:** Subscription attach rate
**Decision rule:** Ship if attach rate rises by ≥11% over 30 days without one-time CVR down ≥4%.
**Expected lift:** +9–17%
**Confidence:** 71

### exp-t6f7g8h9 — Reorder last scents module in cart

**Pillar:** Retention
**Affected surface:** Cart
**URL:** https://touchland.com/cart
**Evidence:** artifacts/touchland/cart.md — cart 200, ATC notes in HTML; screenshot: artifacts/touchland/screenshots/cart_full.png
**Hypothesis:** Repeat purchase rate improves when returning visitors see “Reorder your last mists” with one-click add for prior Power Mist SKUs.
**Primary change:** Personalized reorder strip above cart line items for recognized return sessions.
**Primary KPI:** 90-day repeat purchase rate
**Decision rule:** Ship if repeat rate rises by ≥6% over 60 days among exposed returning sessions.
**Expected lift:** +5–11%
**Confidence:** 69

### exp-t7g8h9i0 — Blog scent-education → shop modules

**Pillar:** Acquisition
**Affected surface:** Blog
**URL:** https://touchland.com/blogs/blogs
**Evidence:** artifacts/touchland/content_page.md — blog hub 200; screenshot: artifacts/touchland/screenshots/content_page_full.png
**Hypothesis:** Organic traffic from scent/wellness queries converts better when blog index cards link to paired Power Mist PDPs with one-click add.
**Primary change:** Shoppable module on top six blog cards with mist thumbnails and deep links.
**Primary KPI:** Blog landing conversion rate
**Decision rule:** Ship if blog CVR rises by ≥7% over 28 days at 90% confidence.
**Expected lift:** +6–12%
**Confidence:** 72

### exp-t8h9i0j1 — FAQ bundle CTA for first-time buyers

**Pillar:** Acquisition
**Affected surface:** FAQ
**URL:** https://touchland.com/pages/faq
**Evidence:** artifacts/touchland/faq_or_where_to_buy.md — FAQ 200; screenshot: artifacts/touchland/screenshots/faq_or_where_to_buy_full.png
**Hypothesis:** FAQ→purchase conversion rises when “Which scent is right for me?” answers include a shoppable bundles collection CTA.
**Primary change:** Inline bundle card below top FAQ accordion linking to `/collections/bundles`.
**Primary KPI:** FAQ page conversion rate
**Decision rule:** Ship if FAQ CVR rises by ≥5% over 28 days at 90% confidence.
**Expected lift:** +4–9%
**Confidence:** 70

### exp-t9i0j1k2 — Mobile meta tags and LCP pass

**Pillar:** Performance
**Affected surface:** Homepage
**URL:** https://touchland.com
**Evidence:** artifacts/touchland/tech_grounded.json — meta title/description/OG missing in static fetch; desktop PSI 68/100, mobile timed out; screenshot: artifacts/touchland/screenshots/homepage_full.png
**Hypothesis:** Mobile bounce and social CTR improve when server-rendered title, meta description, OG tags exist and hero LCP image is compressed/preloaded.
**Primary change:** SSR meta tags + WebP hero with fetchpriority=high; defer below-fold collab carousels.
**Primary KPI:** Mobile bounce rate
**Decision rule:** Ship if bounce falls by ≥5% and social link CTR rises by ≥8% over 21 days.
**Expected lift:** +5–11%
**Confidence:** 76

### exp-t0j1k2l3 — Cross-sell Beach Coco on Applelicious cart add

**Pillar:** Conversion
**Affected surface:** Cart drawer / Applelicious PDP
**URL:** https://touchland.com/products/applelicious-power-mist
**Evidence:** artifacts/touchland/pdp_1.md and artifacts/touchland/pdp_2.md — paired hero mists from crawl; screenshot: artifacts/touchland/screenshots/pdp_1_full.png
**Hypothesis:** Attach rate rises when adding Applelicious triggers a cart-drawer cross-sell to Beach Coco at bundle discount (“Build your duo”).
**Primary change:** Post-add cart drawer module recommending Beach Coco with one-click add.
**Primary KPI:** Attach rate (Applelicious add-to-cart sessions)
**Decision rule:** Ship if attach rate rises by ≥9% over 21 days at 90% confidence.
**Expected lift:** +6–13%
**Confidence:** 75

## Competitor analysis

| Competitor | Domain | Positioning | What they make easier | Touchland edge | Pattern to adapt |
|---|---|---|---|---|---|
| Bath & Body Works | bathandbodyworks.com | Mass fragrance + sanitizer | Variety and gift sets | Premium mist format + collabs | Scent families as collection landing |
| Merci Handy | mercihandy.com | Design-led hand sanitizer | Playful packaging | US DTC scale + Disney/Hello Kitty | Limited-edition hero rotation |
| Grown Alchemist | grownalchemist.com | Premium personal care | Spa-like upsell | On-the-go mist form factor | PDP cross-sell to cases/bundles |
| Byredo | byredo.com | Luxury scent | Brand prestige | Accessible price + function | Sample/mini first-purchase sets |

## Technical checks

| Check | Status | Detail |
|---|---|---|
| SSL Certificate | Pass | Valid to Aug 2026 (`tech_grounded.json`) |
| HTTPS Redirect | Pass | HTTP 301 to HTTPS |
| Sitemap | Pass | /sitemap.xml returns 200 |
| Robots.txt | Pass | Returns 200 |
| Critical Pages Loading | Pass | 7/7 manifest surfaces 200 (audited touchland.com; touchlandusa.com did not resolve) |
| Meta Tags & Social Previews | Warn | Title, description, OG missing in static homepage fetch; favicon not found |
| Structured Data | Warn | Product JSON-LD not validated on crawled PDPs this pass |
| Favicon | Warn | Not detected in homepage meta parse |
| Mobile-Friendly | Warn | Not run via Google mobile-friendly test |
| Page Speed Mobile | Warn | Could not verify — PSI read timed out (90s) |
| Page Speed Desktop | Pass | 68/100 on PageSpeed Insights (desktop) |
| Broken Links | Pass | No manifest 404s on critical surfaces |
| Image Optimization | Warn | Desktop PSI 68; mobile not measured this run |
| Cookie/Privacy | Warn | Not fully inspected |
| Checkout Reachable | Pass | /cart 200 (`cart.md`, `screenshots/cart_full.png`) |
