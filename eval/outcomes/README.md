# Experiment outcomes (manual human input)

This is the **only folder in the harness where humans manually enter data**.

When a merchant ships an experiment from a Qosmic audit and reports results back, add or update a row in `{store}.json` here. The eval system uses this as **market truth** — it outranks judge scores and rubric opinions in the long run.

## When to update

1. Merchant confirms an experiment was **shipped** (or explicitly declined).
2. You have outcome data: lifted, no lift, or inconclusive after the test window.
3. Record actual lift vs the predicted range from the audit report.

## Schema

Each store file:

```json
{
  "store": "gingerpeople",
  "updated_at": "2026-06-04",
  "experiments": [
    {
      "exp_id": "exp-h93c4d5e",
      "title": "Cart URL recovery",
      "shipped": true,
      "shipped_at": "2026-03-01",
      "outcome": "lifted",
      "actual_lift_pct": 11.2,
      "predicted_lift_range": "+8–14%",
      "hypothesis_quality_at_audit": 9,
      "evidence_quality_at_audit": 9,
      "notes": "Optional free text"
    }
  ]
}
```

| Field | Values |
|-------|--------|
| `outcome` | `lifted`, `no_lift`, `inconclusive`, `not_shipped` |
| `shipped` | `true` / `false` |
| `*_quality_at_audit` | 1–10 scores you would have given at audit time (for calibration) |

## After editing

Run rubric calibration (manual trigger):

```bash
python eval/calibrate_rubric.py
```

Review `eval/scores/calibration_report.json`. If you accept a suggestion, edit `eval/rubric.md` and log the change in `eval/rubric_changelog.md`.

## Sample data

`gingerpeople.json` and `zenrojas.json` contain **realistic fake examples** to demonstrate the schema. Replace with real merchant data as it arrives.
