# Qosmic Runtime Audit Harness

Agent-native harness that turns any coding agent into a Qosmic storefront audit agent.

**Start here:** open [`index.html`](index.html) in a browser for the project overview (workflow, architecture, links).

> Assignment deliverable folder is named `reports/` (assignment text says `sample_output/`; same role).

## Architecture

```mermaid
flowchart LR
  url[Store_URL] --> agent[Cursor_Agent]
  agent --> crawl[Crawl]
  crawl --> artifacts[artifacts/slug]
  artifacts --> reason[Reason]
  reason --> write[Write]
  write --> md[reports/slug.md]
  md --> post[post_audit.py]
  post --> eval[eval.json]
  post --> html[reports/slug.html]
  post --> dash[reports/index.html]
```

## Quick start

1. Open this repo in **Cursor Agent** mode.
2. One prompt runs crawl → report → eval → HTML:

   ```
   Qosmic audit: https://zenrojas.com
   ```

   Crawl runs `discover_store.py` (text + **required screenshots** for all 7 surfaces). Agent completes Reason → grounded → Write → `post_audit.py`. Do not read `target_report.md`.

3. Outputs:
   - `artifacts/{store}/` + `manifest.json`
   - `reports/{store}.md` (canonical)
   - `reports/{store}.html` (from template, no LLM tokens)
   - `eval/scores/{store}.json`
   - `reports/index.html` when both stores are audited

## Crawl helpers

```bash
pip install -r requirements.txt
python scripts/discover_store.py https://gingerpeople.com
python scripts/refresh_manifest.py gingerpeople
```

## PageSpeed Insights API key

Grounded checks call the PSI API for mobile/desktop scores. Without a key you get ~1 request per 5 seconds and often **429 rate limited**.

1. Copy `.env.example` → `.env`
2. Set `PAGESPEED_API_KEY` (or `GOOGLE_PSI_API_KEY`) from [Google Cloud Console](https://console.cloud.google.com/apis/credentials) with PageSpeed Insights API enabled
3. `.env` is gitignored — never commit the key

```bash
python eval/grounded.py --url https://zenrojas.com --out artifacts/zenrojas/tech_grounded.json
```

## Expected runtime

| Phase | Typical time |
|---|---|
| Crawl + screenshots (`discover_store.py`) | ~1–2 min |
| Grounded checks (`grounded.py`, PSI mobile + desktop in parallel) | ~1–2 min |
| Agent reason + write report | ~5–15+ min (varies) |
| Post-audit (`post_audit.py`) | ~10s |

PSI mobile and desktop run in parallel. Screenshots use one browser session with `domcontentloaded` (falls back to `load` if blank).

## Post-audit (automatic in harness)

```bash
python scripts/post_audit.py zenrojas
```

Runs structural eval, cross-audit (if both reports exist), HTML render, and dashboard.

## Other scripts

| Script | Purpose |
|--------|---------|
| `scripts/render_report.py` | MD → HTML (no LLM) |
| `scripts/check_evidence.py` | Verify artifact + screenshot paths in report |
| `scripts/capture_screenshot.py` | Playwright PNG capture (full page or element selector) |
| `eval/render_dashboard.py` | `reports/index.html` scoreboard |
| `eval/run_full_eval.py` | Full eval loop + verdict (manual) |
| `eval/pattern_tracker.py` | Recurring vs one-off flags (manual) |
| `eval/calibrate_rubric.py` | Rubric suggestions from outcomes (manual) |

## Self-improvement (manual)

After audits, `post_audit.py` runs automatically. The **learning loop** is manual — run when you want it:

```bash
python eval/run_full_eval.py gingerpeople    # full loop + verdict JSON
python eval/pattern_tracker.py                 # systemic vs store-specific flags
python eval/calibrate_rubric.py                # after editing eval/outcomes/*.json
```

Log accepted rubric changes in `eval/rubric_changelog.md`. See `EVAL_LOOP.md` and `eval/outcomes/README.md`.

## Screenshot evidence (required — part of every audit)

`discover_store.py` captures full-page PNGs for all 7 surfaces under `artifacts/{slug}/screenshots/`. Reports must cite them in every experiment **Evidence** line. HTML embeds them via `render_report.py`.

Re-capture only:

```bash
python scripts/capture_audit_screenshots.py zenrojas
```

See `skills/crawl.md`.

## Layout

- `AGENTS.md` — entry contract
- `skills/` — crawl, reason, write, evaluate (includes optional judge)
- `reports/` — final audits (.md + .html)
- `artifacts/` — crawl outputs
- `eval/` — scorer, grounded checks, cross-audit, self-improvement scripts
- `eval/outcomes/` — **human-entered** merchant experiment results
- `EVAL_LOOP.md` — autonomy plan

## Test URLs

- Calibration: https://gingerpeople.com
- Generalization: https://zenrojas.com

**Rule #1:** **Do not read `target_report.md` during audits** — human calibration for gingerpeople only; recruiters check for copy-paste.

## Qualitative judge (optional)

```
Read eval/rubric.md and skills/evaluate.md (Optional: Qualitative judge). Judge then challenger reports/gingerpeople.md
```
