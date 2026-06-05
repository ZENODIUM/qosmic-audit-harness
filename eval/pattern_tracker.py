#!/usr/bin/env python3
"""Find recurring eval flags across stores — systemic harness problems vs one-offs."""

from __future__ import annotations

import fnmatch
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCORES_DIR = Path(__file__).parent / "scores"
THRESHOLD_PCT = 50

SKIP_FILES = {
    "cross_audit.json",
    "recurring_patterns.json",
    "calibration_report.json",
}

SKIP_SUFFIXES = ("_judge.json", "_debate.json", "_verdict.json")

EXP_FLAG_RE = re.compile(r"^exp-[a-zA-Z0-9]+:")

SKILL_MAP: list[tuple[str, str]] = [
    ("executive_summary_*", "skills/write.md"),
    ("exp:missing_*", "skills/write.md"),
    ("exp:*decision_rule*", "skills/write.md"),
    ("exp:*confidence*", "skills/write.md"),
    ("exp:*hypothesis*", "skills/write.md"),
    ("exp:*expected_lift*", "skills/write.md"),
    ("missing_pillars:*", "skills/reason.md"),
    ("competitor_rows:*", "skills/reason.md"),
    ("technical_rows:*", "skills/write.md"),
    ("experiment_count:*", "skills/reason.md"),
    ("psi_mismatch_*", "skills/write.md"),
    ("grounded_*", "skills/write.md"),
    ("eval_generalization_gap:*", "eval/rubric.md"),
]


def normalize_flag(flag: str) -> str:
    return EXP_FLAG_RE.sub("exp:", flag)


def suggest_skill(flag: str) -> str:
    for pattern, skill in SKILL_MAP:
        if fnmatch.fnmatch(flag, pattern):
            return skill
    if flag.startswith("exp:"):
        return "skills/write.md"
    return "skills/reason.md"


def is_store_score_file(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return False
    if any(path.name.endswith(s) for s in SKIP_SUFFIXES):
        return False
    return path.suffix == ".json"


def load_store_scores() -> dict[str, list[str]]:
    stores: dict[str, list[str]] = {}
    for path in sorted(SCORES_DIR.glob("*.json")):
        if not is_store_score_file(path):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if "scores" not in data or "flags" not in data:
            continue
        stores[path.stem] = [normalize_flag(f) for f in data.get("flags", [])]
    return stores


def analyze(stores: dict[str, list[str]]) -> dict:
    store_count = len(stores)
    if store_count == 0:
        return {
            "scored_stores": [],
            "store_count": 0,
            "threshold_pct": THRESHOLD_PCT,
            "recurring": [],
            "one_off": [],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    flag_stores: dict[str, list[str]] = {}
    for store, flags in stores.items():
        for flag in flags:
            flag_stores.setdefault(flag, [])
            if store not in flag_stores[flag]:
                flag_stores[flag].append(store)

    recurring = []
    one_off = []
    for flag, store_list in sorted(flag_stores.items()):
        rate = round(100 * len(store_list) / store_count, 1)
        entry = {
            "flag": flag,
            "stores": sorted(store_list),
            "rate_pct": rate,
            "suggested_skill": suggest_skill(flag),
        }
        if rate > THRESHOLD_PCT:
            recurring.append(entry)
        else:
            one_off.append(entry)

    return {
        "scored_stores": sorted(stores.keys()),
        "store_count": store_count,
        "threshold_pct": THRESHOLD_PCT,
        "recurring": recurring,
        "one_off": one_off,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def print_summary(result: dict) -> None:
    print("=== Pattern tracker ===")
    print(f"Stores scored: {result['store_count']} ({', '.join(result['scored_stores']) or 'none'})")
    print(f"Threshold: >{result['threshold_pct']}% of stores = recurring (harness problem)\n")

    if result["recurring"]:
        print("RECURRING (systemic — edit suggested skill):")
        for item in result["recurring"]:
            print(f"  [{item['rate_pct']}%] {item['flag']}")
            print(f"         stores: {', '.join(item['stores'])}")
            print(f"         -> {item['suggested_skill']}")
    else:
        print("RECURRING: none")

    print()
    if result["one_off"]:
        print("ONE-OFF (store-specific):")
        for item in result["one_off"]:
            print(f"  [{item['rate_pct']}%] {item['flag']} - {', '.join(item['stores'])}")
    else:
        print("ONE-OFF: none")


def main() -> None:
    stores = load_store_scores()
    result = analyze(stores)
    out = SCORES_DIR / "recurring_patterns.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print_summary(result)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
