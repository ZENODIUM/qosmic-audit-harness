# Qosmic Audit Quality Rubric

Store-agnostic. Score any `reports/*.md` report. Used by the optional judge + challenger pass (`skills/evaluate.md`).

---

## Dimensions (1–10 each)

### evidence_specificity

**9–10:** Every experiment cites a specific artifact path **and** (when available) a matching screenshot under `artifacts/{slug}/screenshots/` for the UI region observed — not just the homepage.

- *High example:* `artifacts/gingerpeople/cart.md` + `screenshot: artifacts/gingerpeople/screenshots/cart_404.png` on exp-h93c4d5e.
- *High example:* `artifacts/zenrojas/collection.md — sampler CTA below fold` on exp-z7a1b2c3.

**5–6:** Mix of specific PDP/cart citations and vague homepage references.

- *Mid example:* Hypothesis about PDP widget placement but evidence only cites `homepage.md` review language.

**1–2:** Generic or missing evidence; no artifact path; "the site could improve conversion."

---

### hypothesis_falsifiability

**9–10:** Clear if/then, named metric, plausible mechanism, observable baseline from crawl.

- *High example:* "If we add a locator module above retailer links on juice PDPs, juice SKU add-to-cart rate will rise because buyers currently bounce to external retailers without a structured path."

**5–6:** Directionally right but mushy mechanism or unnamed metric.

- *Mid example:* "Adding reviews will help trust" without stating which KPI or baseline observation.

**1–2:** "This will help conversion" with no testable claim or metric.

---

### decision_rule_completeness

**9–10:** Decision rule includes numeric lift threshold, time window, and statistical confidence (or explicit sample-size rule).

- *High example:* "Ship if add-to-cart rate improves by ≥8% over 14 days at 90% confidence."
- *High example:* "Ship if sampler AOV rises ≥$4 per order over 21 days with n≥500 sessions per variant."

**5–6:** Has a number but missing time window or confidence; or vague "monitor for improvement."

- *Mid example:* "Ship if conversion improves by 10%" (no duration or confidence).

**1–2:** No numbers; "evaluate qualitatively" or missing decision rule field entirely.

---

### executive_summary_quality

**9–10:** 2–3 prose paragraphs; consultant tone; names the main revenue leak, technical baseline, and top priority tests.

- *High example:* Opens with bold thesis on cart/merchandising gap, cites grounded checks, prioritizes 2–3 experiments by pillar impact.

**5–6:** Too short, bullet-heavy, or generic store praise without a leak.

**1–2:** Missing section or checklist-only bullets with no narrative.

---

### competitor_depth

**9–10:** 3–4 real category competitors with positioning, what they make easier, this store's edge, and an actionable pattern to adapt.

- *High example:* Row comparing Rishi, Yogi, and Traditional Medicinals with specific UX patterns (quiz, subscription, sampler) tied to zenrojas gaps.

**5–6:** Thin rows; correct names but generic "better UX" cells.

**1–2:** Missing table, wrong category, or obviously fabricated competitors.

---

### pillar_diversity_quality

**9–10:** Ten experiments meaningfully spread across Conversion, AOV, Retention, Acquisition, and Performance — each pillar has distinct intent.

**5–6:** Pillar labels present but ideas cluster on one theme (e.g. eight conversion tweaks, one token AOV row).

**1–2:** Missing pillars or duplicate themes with different labels.

---

## Experiment-level scoring (optional but recommended)

Score individual experiments 1–10 in `experiment_scores[]` when evidence quality varies within a report. Use the same evidence_specificity and hypothesis_falsifiability criteria at experiment granularity.

---

## Challenger instructions (required)

After the judge pass, act as **challenger**. Do not agree by default.

1. Re-read **every dimension** the judge scored **≥7**.
2. Re-read **every experiment** the judge scored **≥7**.
3. For each, argue specifically why it deserves **≤5** — cite the exact gap (e.g. missing PDP artifact, homepage-only evidence, decision rule without confidence level).
4. Name the exact **exp_id** (e.g. `exp-z8b2c3d4`) or section (e.g. `## Executive summary`).
5. Write disagreements to `{slug}_debate.json`. Set `human_review: true` when judge and challenger differ by **≥2 points** or when you believe the judge was over-lenient on evidence.

The challenger is not a rubber stamp — its job is to catch rubric drift and over-scoring before humans read every audit.

---

## Judge JSON schema

Write `eval/scores/{slug}_judge.json`:

```json
{
  "store": "gingerpeople",
  "dimensions": {
    "evidence_specificity": 8,
    "hypothesis_falsifiability": 8,
    "decision_rule_completeness": 7,
    "executive_summary_quality": 9,
    "competitor_depth": 8,
    "pillar_diversity_quality": 9
  },
  "experiment_scores": [
    {"exp_id": "exp-h93c4d5e", "score": 9, "note": "manifest 404 + cart.md — strong grounded evidence"},
    {"exp_id": "exp-m48b9c0d", "score": 5, "note": "homepage-only review mention for PDP widget test"}
  ],
  "flags": [],
  "overall": 8.2
}
```

- `overall`: mean of dimension scores (and experiment scores if present), rounded to 1 decimal.
- `flags`: optional free-text notes for the human (not structural eval flags).

---

## Challenger JSON schema

Write `eval/scores/{slug}_debate.json`:

```json
{
  "disagreements": [
    {
      "item": "exp-m48b9c0d",
      "judge_score": 7,
      "challenger_score": 4,
      "challenger_argument": "Judge credited PDP widget hypothesis but evidence only cites homepage.md review language — no pdp_1.md proof of widget absence above ATC.",
      "human_review": true
    },
    {
      "item": "evidence_specificity",
      "judge_score": 8,
      "challenger_score": 6,
      "challenger_argument": "Three experiments use homepage-only citations for surface-specific UI changes.",
      "human_review": false
    }
  ]
}
```

- `item`: dimension key (e.g. `evidence_specificity`) or `exp_id`.
- `human_review`: `true` when gap ≥2 or challenger believes item needs human eyes.

After both files exist, run `python eval/run_full_eval.py {slug}` to produce `{slug}_verdict.json` with agreed vs human-review items.

---

## Rubric versioning

`eval/rubric.md` lives in git. Human corrections that change scoring criteria should be logged in `eval/rubric_changelog.md` and committed, e.g. `rubric: tighten evidence — homepage-only URLs scored too high`. **Git history + changelog is the eval system's learning history.**

Outcome-driven updates: edit `eval/outcomes/*.json` when merchants report back, then run `python eval/calibrate_rubric.py` for suggested patches (manual apply only).
