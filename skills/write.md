# Write Phase

Produce the final audit at `reports/{slug}.md`.

## Format

Follow this **section structure** (same as assignment / production audits):

**Do not paraphrase or copy `target_report.md`.** Match format and depth only. Wording, experiment ideas, and competitors must come from your Reason phase and artifacts.

1. `# {Store name} audit — {one-line thesis}`
2. `## Executive summary` — **2–3 paragraphs of prose** (bold lead-ins allowed; not a bullet list)
3. `## Proposed experiments` — 10 subsections `### exp-{id} — {title}`
4. `## Competitor analysis` — markdown table
5. `## Technical checks` — markdown table ~15 rows

## Experiment block template

```markdown
### exp-a1b2c3d4 — {Title}

**Pillar:** Conversion
**Affected surface:** {name}
**URL:** https://...
**Evidence:** artifacts/{slug}/cart.md — /cart returns 404; screenshot: artifacts/{slug}/screenshots/cart_404.png
**Hypothesis:** ...
**Primary change:** ...
**Primary KPI:** ...
**Decision rule:** Ship if {metric} improves by ≥X% over 14 days at 90% confidence.
**Expected lift:** +8–14%
**Confidence:** 75
```

- **Confidence** must be integer 0–100 (no `%` sign).
- **Expected lift** must look like `+X–Y%`.
- **Decision rule** must contain at least one digit.

**Evidence line rules (required):**

- Always cite `{surface}.md` + observation + **`screenshot: artifacts/{slug}/screenshots/{surface}_full.png`** (use the manifest `screenshot` path; add extra crops if captured).
- **URL** field stays the live page URL from manifest.

## Competitor table columns

| Competitor | Domain | Positioning | What they make easier | {Store} edge | Pattern to adapt |

## Technical checks table (grounded — required)

**Required:** run grounded checks **before** writing this section (after Reason, before final report):

```bash
python eval/grounded.py --url https://{store} --out artifacts/{slug}/tech_grounded.json
```

Read `artifacts/{slug}/tech_grounded.json` and map each automated check to the table. Supplement remaining rows (Critical Pages Loading, Structured Data, etc.) from `manifest.json` and page artifacts — still no guessing.

| Rule | Behavior |
|------|----------|
| **Required** | Run `grounded.py` before write; cite `tech_grounded.json` in Page Speed / SSL / sitemap rows |
| **Fallback** | PSI returns **429** → **Warn** with detail `Warn — rate limited` (or `Could not verify — rate limited`) |
| **Never** | Guess or fake a **Pass** when grounded did not verify |

Columns: `Check | Status | Detail`

Required checks (match assignment):

SSL Certificate, HTTPS Redirect, Sitemap, Robots.txt, Critical Pages Loading, Meta Tags & Social Previews, Structured Data, Favicon, Mobile-Friendly, Page Speed Mobile, Page Speed Desktop, Broken Links, Image Optimization, Cookie/Privacy, Checkout Reachable

Use **Pass**, **Warn**, or **Fail**. Other failures to verify → **Warn** with `Could not verify — {reason}`.

## Done when

- [ ] `artifacts/{slug}/tech_grounded.json` exists (from required `grounded.py` run)
- [ ] File written to `reports/{slug}.md`
- [ ] Exactly 10 experiments, 5 pillars covered
- [ ] Executive summary is prose paragraphs
- [ ] Every experiment Evidence line cites `.md` + `screenshot:` path
- [ ] Proceed to **Evaluate** → [`skills/evaluate.md`](evaluate.md) (`python scripts/post_audit.py {slug}`)
