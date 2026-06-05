#!/usr/bin/env python3
"""Suggest rubric updates from shipped experiment outcomes — manual trigger only."""

from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

OUTCOMES_DIR = Path(__file__).parent / "outcomes"
SCORES_DIR = Path(__file__).parent / "scores"
MIN_SHIPPED_FOR_HIGH_CONFIDENCE = 20
MIN_STORES_FOR_HIGH_CONFIDENCE = 5


def load_outcomes() -> list[dict]:
    rows = []
    for path in sorted(OUTCOMES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        store = data.get("store", path.stem)
        for exp in data.get("experiments", []):
            rows.append({**exp, "store": store})
    return rows


def avg(values: list[float]) -> float | None:
    return round(statistics.mean(values), 2) if values else None


def analyze_shipped(experiments: list[dict]) -> dict:
    shipped = [e for e in experiments if e.get("shipped")]
    lifted = [e for e in shipped if e.get("outcome") == "lifted"]
    no_lift = [e for e in shipped if e.get("outcome") == "no_lift"]
    inconclusive = [e for e in shipped if e.get("outcome") == "inconclusive"]

    def qualities(group: list[dict], key: str) -> list[float]:
        return [float(e[key]) for e in group if e.get(key) is not None]

    patterns = []

    ev_lifted = avg(qualities(lifted, "evidence_quality_at_audit"))
    ev_no_lift = avg(qualities(no_lift, "evidence_quality_at_audit"))
    hyp_lifted = avg(qualities(lifted, "hypothesis_quality_at_audit"))
    hyp_no_lift = avg(qualities(no_lift, "hypothesis_quality_at_audit"))

    if ev_lifted is not None and ev_no_lift is not None:
        patterns.append({
            "pattern": "evidence_quality_vs_outcome",
            "lifted_avg": ev_lifted,
            "no_lift_avg": ev_no_lift,
            "interpretation": (
                f"Lifted experiments averaged evidence quality {ev_lifted}/10 "
                f"vs {ev_no_lift}/10 for no-lift."
            ),
        })

    if hyp_lifted is not None and hyp_no_lift is not None:
        patterns.append({
            "pattern": "hypothesis_quality_vs_outcome",
            "lifted_avg": hyp_lifted,
            "no_lift_avg": hyp_no_lift,
            "interpretation": (
                f"Lifted experiments averaged hypothesis quality {hyp_lifted}/10 "
                f"vs {hyp_no_lift}/10 for no-lift."
            ),
        })

    high_evidence_lifted = [e for e in lifted if (e.get("evidence_quality_at_audit") or 0) >= 8]
    low_evidence_no_lift = [e for e in no_lift if (e.get("evidence_quality_at_audit") or 10) <= 6]
    if high_evidence_lifted or low_evidence_no_lift:
        patterns.append({
            "pattern": "surface_specific_evidence",
            "lifted_high_evidence_count": len(high_evidence_lifted),
            "no_lift_low_evidence_count": len(low_evidence_no_lift),
            "interpretation": (
                "Shipped winners tended to cite cart/PDP/collection artifacts; "
                "no-lift cases often had homepage-level or unverified widget claims."
            ),
        })

    stores_with_shipped = len({e["store"] for e in shipped})
    shipped_count = len(shipped)

    confidence = "low"
    limitations = []
    if shipped_count < MIN_SHIPPED_FOR_HIGH_CONFIDENCE:
        limitations.append(
            f"Only {shipped_count} shipped experiments across {stores_with_shipped} store(s). "
            f"Need >={MIN_SHIPPED_FOR_HIGH_CONFIDENCE} shipped experiments for reliable signal."
        )
    if stores_with_shipped < MIN_STORES_FOR_HIGH_CONFIDENCE:
        limitations.append(
            f"Only {stores_with_shipped} store(s) with outcome data. "
            f"Need >={MIN_STORES_FOR_HIGH_CONFIDENCE} stores before cross-merchant rubric changes."
        )
    if shipped_count >= MIN_SHIPPED_FOR_HIGH_CONFIDENCE and stores_with_shipped >= MIN_STORES_FOR_HIGH_CONFIDENCE:
        confidence = "high"
    elif shipped_count >= 8 and stores_with_shipped >= 3:
        confidence = "medium"

    suggestions = build_suggestions(patterns, ev_lifted, ev_no_lift, confidence)

    return {
        "confidence": confidence,
        "data_summary": {
            "total_experiments": len(experiments),
            "shipped_count": shipped_count,
            "lifted_count": len(lifted),
            "no_lift_count": len(no_lift),
            "inconclusive_count": len(inconclusive),
            "stores_with_outcomes": stores_with_shipped,
        },
        "patterns": patterns,
        "suggested_rubric_updates": suggestions,
        "limitations": limitations,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_suggestions(
    patterns: list[dict],
    ev_lifted: float | None,
    ev_no_lift: float | None,
    confidence: str,
) -> list[dict]:
    suggestions = []
    prefix = f"[{confidence} confidence — review before applying] "

    if ev_lifted is not None and ev_no_lift is not None and ev_lifted - ev_no_lift >= 2:
        suggestions.append({
            "dimension": "evidence_specificity",
            "section": "eval/rubric.md — evidence_specificity",
            "proposed_change": (
                prefix
                + "Tighten 9–10 band: require artifact path naming a specific surface "
                "(cart.md, pdp_1.md, collection.md) — not homepage-only mentions. "
                "Downgrade to <=5 when evidence is site-wide copy without surface proof."
            ),
            "trigger": "Lifted avg evidence "
            f"{ev_lifted} vs no-lift avg {ev_no_lift}",
        })

    for p in patterns:
        if p["pattern"] == "surface_specific_evidence":
            suggestions.append({
                "dimension": "evidence_specificity",
                "section": "skills/reason.md — experiment evidence rules",
                "proposed_change": (
                    prefix
                    + "Add rule: experiments citing only homepage.md for PDP-specific "
                    "UI changes should cap evidence_quality at 6 until PDP artifact confirms."
                ),
                "trigger": p["interpretation"],
            })

    if ev_no_lift is not None and ev_no_lift <= 6:
        suggestions.append({
            "dimension": "hypothesis_falsifiability",
            "section": "eval/rubric.md — hypothesis_falsifiability",
            "proposed_change": (
                prefix
                + "When hypothesis names a UI element placement (e.g. 'reviews above ATC'), "
                "require crawl evidence of current placement — falsifiable claim needs observed baseline."
            ),
            "trigger": f"No-lift experiments averaged evidence {ev_no_lift}/10",
        })

    suggestions.append({
        "dimension": "decision_rule_completeness",
        "section": "eval/rubric.md — decision_rule_completeness",
        "proposed_change": (
            prefix
            + "No outcome-based change yet — insufficient shipped count to correlate "
            "decision rule wording with lift. Keep structural eval numeric check; "
            "re-run calibration after more merchants report back."
        ),
        "trigger": "Insufficient data for decision-rule vs outcome correlation",
    })

    return suggestions


def print_summary(result: dict) -> None:
    print("=== Rubric calibration ===")
    print(f"Confidence: {result['confidence'].upper()}")
    ds = result["data_summary"]
    print(
        f"Shipped: {ds['shipped_count']} | Lifted: {ds['lifted_count']} | "
        f"No lift: {ds['no_lift_count']} | Stores: {ds['stores_with_outcomes']}"
    )
    print()
    if result["limitations"]:
        print("LIMITATIONS:")
        for lim in result["limitations"]:
            print(f"  - {lim}")
        print()
    if result["patterns"]:
        print("PATTERNS:")
        for p in result["patterns"]:
            print(f"  - {p.get('interpretation', p['pattern'])}")
        print()
    if result["suggested_rubric_updates"]:
        print("SUGGESTED UPDATES (manual — edit rubric.md + rubric_changelog.md):")
        for i, s in enumerate(result["suggested_rubric_updates"], 1):
            print(f"  {i}. [{s['dimension']}] {s['proposed_change'][:120]}...")


def main() -> None:
    experiments = load_outcomes()
    result = analyze_shipped(experiments)
    out = SCORES_DIR / "calibration_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print_summary(result)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
