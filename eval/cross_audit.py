#!/usr/bin/env python3
"""Compare structural eval scores across calibration and generalization audits."""

from __future__ import annotations

import json
from pathlib import Path

SCORES_DIR = Path(__file__).parent / "scores"
CALIBRATION = "gingerpeople"
GENERALIZATION = "zenrojas"
GAP_THRESHOLD = 3.0  # points difference triggers flag


def load_scores(slug: str) -> dict | None:
    path = SCORES_DIR / f"{slug}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    cal = load_scores(CALIBRATION)
    gen = load_scores(GENERALIZATION)
    flags = []
    if not cal:
        flags.append(f"missing_scores:{CALIBRATION}.json")
    if not gen:
        flags.append(f"missing_scores:{GENERALIZATION}.json")

    comparison = {}
    if cal and gen:
        for key in ("structural", "field_quality", "overall"):
            c = cal["scores"].get(key, 0)
            g = gen["scores"].get(key, 0)
            delta = round(c - g, 2)
            comparison[key] = {"calibration": c, "generalization": g, "delta": delta}
            if abs(delta) >= GAP_THRESHOLD:
                flags.append(f"eval_generalization_gap:{key}:delta={delta}")

        cal_flags = len(cal.get("flags", []))
        gen_flags = len(gen.get("flags", []))
        if cal_flags <= 2 and gen_flags >= 8:
            flags.append("eval_generalization_gap:generalization_has_many_more_flags")

    result = {
        "calibration_store": CALIBRATION,
        "generalization_store": GENERALIZATION,
        "comparison": comparison,
        "flags": flags,
        "interpretation": (
            "Large score deltas suggest rubric or harness drift — review rubric.md, not just rewrite one report."
            if flags
            else "Structural eval scores are consistent across stores."
        ),
    }
    out = SCORES_DIR / "cross_audit.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
