# Crawl Phase

Visit the storefront and capture artifacts before reasoning or writing the report.

## Slug

From input URL hostname, strip `www.` → e.g. `gingerpeople.com` → folder `artifacts/gingerpeople/`.

## Required surfaces

Visit each surface and record HTTP status. Minimum set:

| `surface` key | What to visit |
|---------------|---------------|
| `homepage` | Store root URL |
| `pdp_1` | First product page linked from homepage or /products |
| `pdp_2` | Second distinct PDP |
| `collection` | A collection or category listing |
| `cart` | `{origin}/cart` |
| `faq_or_where_to_buy` | FAQ, Where To Buy, or store-locator page (whichever exists) |
| `content_page` | One blog post or educational content page |

## Crawl command (required — includes screenshots)

**Every audit** starts with discovery + screenshot capture in one step:

```bash
python scripts/discover_store.py https://{store}
python scripts/refresh_manifest.py {slug}    # if statuses need refresh
```

`discover_store.py` automatically:
1. Writes `manifest.json` + seven `{surface}.md` files
2. Captures **full-page PNGs** for every surface → `artifacts/{slug}/screenshots/{surface}_full.png`
3. Updates each `.md` and manifest with `screenshot` paths

Requires Playwright: `pip install playwright && playwright install chromium`

If discovery succeeded but screenshots failed, re-run only screenshots:

```bash
python scripts/capture_audit_screenshots.py {slug}
```

## How to fetch (Cursor built-in — no Firecrawl)

**You do not need Firecrawl or any paid crawl API.** Terminal scripts handle text + pixels; use WebFetch/browser only if scripts fail.

| Tool | When to use |
|------|-------------|
| **`discover_store.py`** | **Default** — always run first |
| **WebFetch / Browser** | Fallback if scripts rate-limit; still run `capture_audit_screenshots.py` after |
| **Terminal curl** | Status checks only |

Do **not** use store-specific URL lists in skills or scripts. `crawl_store.py` is deprecated.

For each page, `{surface}.md` must contain:

- Full URL, HTTP status, title/H1, CRO notes
- **Screenshot line** (added automatically): `artifacts/{slug}/screenshots/{surface}_full.png`

Optional extra crops (PDP add-to-cart, etc.):

```bash
python scripts/capture_screenshot.py --url https://{store}/products/example --out artifacts/{slug}/screenshots/pdp_1_atc.png --selector "text=Add to cart"
```

## manifest.json (required schema)

```json
{
  "store": "gingerpeople.com",
  "crawled_at": "2026-06-04T12:00:00Z",
  "pages": [
    {"surface": "homepage", "url": "https://gingerpeople.com", "status": 200, "screenshot": "screenshots/homepage_full.png"},
    {"surface": "cart", "url": "https://gingerpeople.com/cart", "status": 404, "screenshot": "screenshots/cart_full.png"}
  ]
}
```

- `screenshot` (required after crawl): path **relative to** `artifacts/{slug}/`

A 404 on `cart` is valid evidence — record it, do not omit it.

## Grounded checks (not during crawl)

**Required before write:** `eval/grounded.py` → `artifacts/{slug}/tech_grounded.json` per [`skills/write.md`](write.md).

## Done when

- [ ] All 7 surfaces in `manifest.json` with `screenshot` on each page
- [ ] Seven PNGs in `artifacts/{slug}/screenshots/`
- [ ] Matching `{surface}.md` files exist
- [ ] No surface skipped without a documented reason
