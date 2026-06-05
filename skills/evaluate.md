# Evaluate Phase (automatic)

Run **immediately after** `reports/{slug}.md` is written. Same session as crawl → reason → grounded → write.

## Command

From repo root:

```bash
python scripts/post_audit.py {slug}
```

`{slug}` = hostname without `www` (e.g. `zenrojas`, `gingerpeople`).

## What it does

1. `eval/eval.py` → `eval/scores/{slug}.json`
2. `eval/cross_audit.py` if both `reports/gingerpeople.md` and `reports/zenrojas.md` exist
3. `scripts/render_report.py` → `reports/{slug}.html` (template, no LLM)
4. `eval/render_dashboard.py` → `reports/index.html` when both stores exist

## Agent instructions

- Execute the command in the terminal; do not ask the user to run it unless the command fails.
- Read the JSON output and summarize: overall score, `flags[]`, and cross-audit interpretation if run.
- If `flags` is non-empty, fix the report and re-run `post_audit.py` until structural eval is clean (or document unfixable grounded Warns like PSI 429).

## Done when

- [ ] `eval/scores/{slug}.json` exists
- [ ] `reports/{slug}.html` exists
- [ ] User sees a short eval summary in chat

---

## Self-improvement loop (manual trigger)

When the user asks for **pattern tracker**, **full eval**, or **rubric calibration**:

| Request | Run |
|---------|-----|
| Full eval for a store | `python eval/run_full_eval.py {slug}` |
| Recurring flags | `python eval/pattern_tracker.py` |
| Rubric calibration | Edit `eval/outcomes/*.json`, then `python eval/calibrate_rubric.py` |

After judge + challenger JSON exist, re-run `run_full_eval.py` to produce `{slug}_verdict.json` (gap ≥2 → human review).

---

## Optional: Qualitative judge (eval-only)

Use only when the user asks for qualitative scoring — **not** part of the default audit flow.

**Inputs:** `reports/{slug}.md`, `eval/rubric.md`

### Pass 1 — Judge

Score each dimension 1–10. Write `eval/scores/{slug}_judge.json`:

```json
{
  "store": "gingerpeople",
  "dimensions": {
    "evidence_specificity": 8,
    "hypothesis_falsifiability": 7,
    "decision_rule_completeness": 8,
    "executive_summary_quality": 8,
    "competitor_depth": 7,
    "pillar_diversity_quality": 9
  },
  "experiment_scores": [
    {"exp_id": "exp-a1b2c3d4", "score": 8, "note": "..."}
  ],
  "flags": [],
  "overall": 7.8
}
```

### Pass 2 — Challenger

For any experiment score **> 7** or dimension **> 7**, re-read the cited evidence and argue why it deserves **≤ 5**.

Write `eval/scores/{slug}_debate.json`:

```json
{
  "disagreements": [
    {
      "item": "exp-a1b2c3d4",
      "judge_score": 8,
      "challenger_score": 4,
      "challenger_argument": "...",
      "human_review": true
    }
  ]
}
```

If judge and challenger agree (both ≤7 or within 2 points), set `human_review: false`.

### Judge done when

- [ ] `{slug}_judge.json` written
- [ ] `{slug}_debate.json` written
- [ ] Structural eval already ran via `post_audit.py`
- [ ] Optional: `python eval/run_full_eval.py {slug}` for verdict JSON
