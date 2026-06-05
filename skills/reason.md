# Reason Phase

Analyze crawl artifacts and design the audit content before writing the final report.

**Do not open or copy from `target_report.md`.** That file is a post-hoc quality bar for reviewers, not crawl input. Experiments must be driven by what you observed in `artifacts/{slug}/` for **this** store URL — not by reusing another audit's experiment titles or IDs.

## Inputs

- `artifacts/{slug}/manifest.json`
- All `artifacts/{slug}/*.md` page notes
- `artifacts/{slug}/screenshots/*.png` (when captured during crawl)
- `artifacts/{slug}/tech_grounded.json` (from required `eval/grounded.py` run before write)

## Five pillars

| Pillar | Look for |
|--------|----------|
| **Conversion** | Friction in buy path, weak CTAs, missing social proof, confusing navigation |
| **AOV** | No bundles, upsells, cross-sells, samplers, or kits |
| **Retention** | No subscriptions, routines, reorder flows, post-purchase hooks |
| **Acquisition** | Weak landing pages for intents (symptom, use-case, campaign) |
| **Performance** | 404s, slow pages, heavy images, broken critical URLs |

## Experiments (draft 10)

For each experiment, draft:

- `exp-{8char}` id (hex or alphanumeric, e.g. `exp-a1b2c3d4`)
- **Pillar** (one of five above)
- **Affected surface** + **URL** (live URL from manifest)
- **Evidence** — required: `artifacts/{slug}/{surface}.md` + `screenshot: artifacts/{slug}/screenshots/...` from manifest
- **Hypothesis** — falsifiable: what changes for whom and why
- **Primary change** — concrete control → variant
- **Primary KPI** — one metric
- **Decision rule** — must include a **number** (e.g. ≥5% lift, 14 days, 90% confidence)
- **Expected lift** — range like `+8–14%`
- **Confidence** — integer `0–100`

**Coverage:** at least 2 experiments on Conversion; at least 1 each for AOV, Retention, Acquisition, Performance.

## Competitors (3–4)

Pick real competitors for **this store's category** from your knowledge and quick web search — not names hardcoded in skills.

For each: positioning, what they make easier, this store's edge, pattern to adapt.

## Technical findings

From manifest status codes and `eval/grounded.py` output, note:

- Broken critical URLs (e.g. cart 404)
- PSI mobile/desktop scores
- SSL, sitemap, robots results

## Done when

- [ ] 10 experiment drafts with evidence tied to artifacts
- [ ] All 5 pillars represented
- [ ] 3–4 competitors identified with differentiation
- [ ] Technical issues list ready for write phase
