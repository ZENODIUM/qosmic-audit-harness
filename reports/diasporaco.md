# Diaspora Co. audit — cart and bundles are strong; waitlist-heavy hero SKUs leak cold traffic

## Executive summary

**Diaspora Co. is a mature Shopify DTC spice brand on this crawl.** All seven manifest surfaces returned 200, including `/cart` with a real Shopping Cart page (`artifacts/diasporaco/cart.md`; screenshot: `artifacts/diasporaco/screenshots/cart_full.png`). PDPs **Anamalai Cacao** and **Anamalai Nutmeg** both show add-to-cart in HTML (`artifacts/diasporaco/pdp_1.md`, `artifacts/diasporaco/pdp_2.md`) with matching screenshots — a working buy path with review-widget copy present.

**Merchandising depth—not checkout plumbing—is the story.** The homepage and gifts collection load (`artifacts/diasporaco/homepage.md`, `artifacts/diasporaco/collection.md`) with rich bundle, cookbook, and gifting modules in the static fetch. The journal hub loads (`artifacts/diasporaco/content_page.md`) as a content surface separate from the homepage. Static HTML notes widespread **Notify Me / waitlist** patterns on hero launches (e.g. Meyer Lemon Achaar collaboration), which can stall first-purchase momentum for cold traffic landing on promotional heroes. FAQs return 200 (`artifacts/diasporaco/faq_or_where_to_buy.md`) with farm-partner and wholesale detail — a trust asset that could carry stronger product handoffs.

**Technical baseline is mostly fine with Warns.** HTTPS, sitemap, and robots pass per `artifacts/diasporaco/tech_grounded.json`; SSL verification failed locally and both PSI calls timed out this run. Priority tests: sampler-first path for waitlist heroes, cart pack-threshold clarity, journal→tin modules, FAQ→gift bundle CTA, and mobile LCP on the homepage hero — all tied to URLs and screenshots from this run.

## Proposed experiments

### exp-d1a2b3c4 — Spice Sampler hero for cold traffic

**Pillar:** Conversion
**Affected surface:** Homepage
**URL:** https://diasporaco.com
**Evidence:** artifacts/diasporaco/homepage.md — ATC and review copy in HTML; hero modules include waitlist-style CTAs in live site content; screenshot: artifacts/diasporaco/screenshots/homepage_full.png
**Hypothesis:** Homepage→PDP CTR rises when cold visitors see an in-stock Spice Sampler or 6-pack bundle hero above limited waitlist SKUs.
**Primary change:** Default hero = Spice Sampler with “Start here” copy; Meyer Lemon Achaar waitlist module moves below fold for paid/new sessions.
**Primary KPI:** Homepage click-through rate to in-stock PDPs
**Decision rule:** Ship if homepage CTR rises by ≥9% over 21 days at 90% confidence.
**Expected lift:** +8–15%
**Confidence:** 76

### exp-d2b3c4d5 — Review summary above ATC on Anamalai Cacao

**Pillar:** Conversion
**Affected surface:** Anamalai Cacao PDP
**URL:** https://diasporaco.com/products/anamalai-cacao
**Evidence:** artifacts/diasporaco/pdp_1.md — add-to-cart and review widget copy in HTML; screenshot: artifacts/diasporaco/screenshots/pdp_1_full.png
**Hypothesis:** Add-to-cart rate on Anamalai Cacao improves when aggregated star rating and review count render directly above the primary ATC control.
**Primary change:** Move review summary block above ATC on top five SKUs by sessions, starting with Anamalai Cacao.
**Primary KPI:** Add-to-cart rate (Anamalai Cacao PDP)
**Decision rule:** Ship if ATC rises by ≥5% over 14 days without return rate up ≥2%.
**Expected lift:** +4–10%
**Confidence:** 78

### exp-d3c4d5e6 — Build Your Own Pack default at 6 tins

**Pillar:** AOV
**Affected surface:** Cart
**URL:** https://diasporaco.com/cart
**Evidence:** artifacts/diasporaco/cart.md — Shopping Cart 200; live cart copy references BYOP 3/6/9/12 packs and pack savings; screenshot: artifacts/diasporaco/screenshots/cart_full.png
**Hypothesis:** Units per order rise when empty or single-tin carts default-suggest a 6-tin BYOP pack with visible savings vs à la carte.
**Primary change:** Cart drawer highlights “Build a 6-pack — save $3.50” with one-click jump to BYOP builder when cart has 1–2 tins.
**Primary KPI:** Units per order
**Decision rule:** Ship if units per order rise by ≥0.2 over 21 days at 90% confidence.
**Expected lift:** +7–14%
**Confidence:** 74

### exp-d4d5e6f7 — Cookbook + 6-pack bundle on gifts collection

**Pillar:** AOV
**Affected surface:** Gifts collection
**URL:** https://diasporaco.com/collections/gifts
**Evidence:** artifacts/diasporaco/collection.md — gift-set collection 200, ATC in HTML; screenshot: artifacts/diasporaco/screenshots/collection_full.png
**Hypothesis:** AOV on gifts collection sessions increases when Cookbook + Spice 6-pack bundle is pinned as the first row with explicit savings callout.
**Primary change:** Pinned bundle card at top of gifts grid with compare-at pricing and gift-note prompt.
**Primary KPI:** AOV (gifts collection sessions)
**Decision rule:** Ship if AOV rises by ≥$8 over 28 days with collection CVR down ≤3%.
**Expected lift:** +9–16%
**Confidence:** 72

### exp-d5e6f7g8 — Rewards enrollment at cart checkout

**Pillar:** Retention
**Affected surface:** Cart
**URL:** https://diasporaco.com/cart
**Evidence:** artifacts/diasporaco/cart.md — cart 200; homepage/nav references Rewards program; screenshot: artifacts/diasporaco/screenshots/cart_full.png
**Hypothesis:** Repeat purchase rate improves when cart shows one-click Rewards signup with points estimate on the current order subtotal.
**Primary change:** Cart sidebar module: “Earn X points on this order — join Rewards” with email capture pre-checkout.
**Primary KPI:** 90-day repeat purchase rate
**Decision rule:** Ship if repeat rate rises by ≥6% over 60 days among exposed sessions.
**Expected lift:** +5–11%
**Confidence:** 70

### exp-d6f7g8h9 — Reorder last tins module in cart

**Pillar:** Retention
**Affected surface:** Cart
**URL:** https://diasporaco.com/cart
**Evidence:** artifacts/diasporaco/cart.md — cart 200; tin-based catalog in collection/homepage notes; screenshot: artifacts/diasporaco/screenshots/cart_full.png
**Hypothesis:** Returning customers add more units when cart surfaces “Reorder your last tins” for recognized logged-in or cookie-return sessions.
**Primary change:** Personalized reorder strip above cart line items with one-click add for last 3 purchased SKUs.
**Primary KPI:** Repeat purchase rate (30-day)
**Decision rule:** Ship if 30-day repeat rate rises by ≥7% among returning visitors over 45 days.
**Expected lift:** +6–12%
**Confidence:** 68

### exp-d7g8h9i0 — Journal recipe cards with shoppable tins

**Pillar:** Acquisition
**Affected surface:** Journal
**URL:** https://diasporaco.com/blogs/journal
**Evidence:** artifacts/diasporaco/content_page.md — blog/journal 200; homepage promotes community recipes; screenshot: artifacts/diasporaco/screenshots/content_page_full.png
**Hypothesis:** Organic and social traffic from recipe intent converts better when journal index cards show linked spice tins and one-click add below each featured recipe.
**Primary change:** Shoppable module on top 6 journal cards with spice tin thumbnails and deep links to paired PDPs.
**Primary KPI:** Journal landing conversion rate
**Decision rule:** Ship if journal CVR rises by ≥8% over 28 days at 90% confidence.
**Expected lift:** +6–13%
**Confidence:** 73

### exp-d8h9i0j1 — FAQ gift-guide CTA for first-time buyers

**Pillar:** Acquisition
**Affected surface:** FAQ
**URL:** https://diasporaco.com/pages/faq
**Evidence:** artifacts/diasporaco/faq_or_where_to_buy.md — FAQ 200; farm-partner and wholesale content in live site; screenshot: artifacts/diasporaco/screenshots/faq_or_where_to_buy_full.png
**Hypothesis:** FAQ→purchase conversion rises when “What makes Diaspora different?” answers include a shoppable Spice Sampler or gifts collection CTA for branded-search visitors.
**Primary change:** Inline gift-guide card below top FAQ accordion with link to `/collections/gifts`.
**Primary KPI:** FAQ page conversion rate
**Decision rule:** Ship if FAQ CVR rises by ≥5% over 28 days at 90% confidence.
**Expected lift:** +4–9%
**Confidence:** 71

### exp-d9i0j1k2 — Mobile homepage LCP pass

**Pillar:** Performance
**Affected surface:** Homepage
**URL:** https://diasporaco.com
**Evidence:** artifacts/diasporaco/tech_grounded.json — Page Speed Mobile and Desktop timed out (90s); artifacts/diasporaco/homepage.md — heavy hero and product grid; screenshot: artifacts/diasporaco/screenshots/homepage_full.png
**Hypothesis:** Mobile bounce rate drops when above-the-fold hero media is compressed and deferred below-fold modules load lazily.
**Primary change:** WebP hero with fetchpriority=high; defer Ocado/interstitial and secondary carousels below first viewport.
**Primary KPI:** Mobile bounce rate
**Decision rule:** Ship if bounce falls by ≥5% and mobile PSI completes with score ≥45 over 21 days.
**Expected lift:** +4–10%
**Confidence:** 74

### exp-d0j1k2l3 — Nutmeg→cacao pairing on PDP cross-sell

**Pillar:** Conversion
**Affected surface:** Anamalai Nutmeg PDP
**URL:** https://diasporaco.com/products/anamalai-nutmeg
**Evidence:** artifacts/diasporaco/pdp_2.md — Nutmeg PDP 200, ATC in HTML; paired with pdp_1 cacao from same farm line; screenshot: artifacts/diasporaco/screenshots/pdp_2_full.png
**Hypothesis:** Attach rate rises when Anamalai Nutmeg PDP shows a “Complete the Anamalai set” cross-sell to Anamalai Cacao with bundle discount.
**Primary change:** Inline cross-sell module below variant selector on Nutmeg with one-click add of Cacao at 10% off.
**Primary KPI:** Attach rate (Nutmeg PDP sessions)
**Decision rule:** Ship if attach rate rises by ≥8% over 21 days at 90% confidence.
**Expected lift:** +5–12%
**Confidence:** 75

## Competitor analysis

| Competitor | Domain | Positioning | What they make easier | Diaspora edge | Pattern to adapt |
|---|---|---|---|---|---|
| Burlap & Barrel | burlapandbarrel.com | Single-origin spices, direct sourcing | Pantry-staple discovery | South Asia farm narrative + tin design | Origin story on every PDP |
| Spicewalla | spicewallabros.com | Chef-led blends and kits | Recipe-driven trial | Heirloom single-origin + cookbook | Bundle + recipe landing pairs |
| Oaktown Spice Shop | oaktownspices.com | Bay Area fresh-ground spices | Local freshness | National DTC + farm wages story | Sample sizes for first purchase |
| Penzeys | penzeys.com | Mass-premium spice catalog | Variety and gift sets | Premium ethical sourcing POV | Gift collection as default landing |

## Technical checks

| Check | Status | Detail |
|---|---|---|
| SSL Certificate | Warn | Could not verify — local SSL trust error (`tech_grounded.json`) |
| HTTPS Redirect | Pass | HTTP 301 to HTTPS |
| Sitemap | Pass | /sitemap.xml returns 200 |
| Robots.txt | Pass | Returns 200 |
| Critical Pages Loading | Pass | 7/7 manifest surfaces 200 including journal and FAQ |
| Meta Tags & Social Previews | Pass | Title, description, OG, favicon present |
| Structured Data | Warn | Product JSON-LD not validated on crawled PDPs this pass |
| Favicon | Pass | Present per homepage meta parse |
| Mobile-Friendly | Warn | Not run via Google mobile-friendly test |
| Page Speed Mobile | Warn | Could not verify — PSI read timed out (90s) |
| Page Speed Desktop | Warn | Could not verify — PSI read timed out (90s) |
| Broken Links | Pass | No manifest 404s on critical surfaces |
| Image Optimization | Warn | PSI timeout suggests heavy homepage; not fully measured |
| Cookie/Privacy | Warn | Not fully inspected |
| Checkout Reachable | Pass | /cart 200 — Shopping Cart page (`cart.md`, `screenshots/cart_full.png`) |
