#!/usr/bin/env python3
"""Run full eval loop for one store — manual trigger."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = Path(__file__).resolve().parent
SCORES_DIR = EVAL_DIR / "scores"
REPORTS = ROOT / "reports"
GAP_THRESHOLD = 2


def run_step(label: str, cmd: list[str]) -> int:
    print(f"\n=== {label} ===")
    r = subprocess.run(cmd, cwd=ROOT)
    return r.returncode


def store_url_from_report(report_path: Path) -> str:
    text = report_path.read_text(encoding="utf-8")
    m = re.search(r"https?://[^\s\)|]+", text)
    if m:
        return m.group(0).rstrip(".,)")
    slug = report_path.stem
    return f"https://{slug}.com"


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def compare_judge_debate(judge: dict, debate: dict | None) -> dict:
    disagreements = debate.get("disagreements", []) if debate else []
    debate_by_item = {d["item"]: d for d in disagreements}

    agreed = []
    human_review = []
    pending_challenger = []

    for dim, score in judge.get("dimensions", {}).items():
        item_key = dim
        if item_key in debate_by_item:
            d = debate_by_item[item_key]
            gap = abs(d.get("judge_score", score) - d.get("challenger_score", score))
            entry = {
                "item": item_key,
                "type": "dimension",
                "judge_score": d.get("judge_score", score),
                "challenger_score": d.get("challenger_score"),
                "gap": gap,
                "argument": d.get("challenger_argument", ""),
            }
            if gap >= GAP_THRESHOLD or d.get("human_review"):
                entry["human_review"] = True
                human_review.append(entry)
            else:
                agreed.append(entry)
        elif score >= 7:
            pending_challenger.append({
                "item": item_key,
                "type": "dimension",
                "judge_score": score,
                "reason": "Judge scored >=7 but no challenger entry in debate JSON",
            })
        else:
            agreed.append({
                "item": item_key,
                "type": "dimension",
                "judge_score": score,
                "note": "Both sides would likely agree (score <=7)",
            })

    for exp in judge.get("experiment_scores", []):
        exp_id = exp["exp_id"]
        score = exp["score"]
        if exp_id in debate_by_item:
            d = debate_by_item[exp_id]
            gap = abs(d.get("judge_score", score) - d.get("challenger_score", score))
            entry = {
                "item": exp_id,
                "type": "experiment",
                "judge_score": d.get("judge_score", score),
                "challenger_score": d.get("challenger_score"),
                "gap": gap,
                "argument": d.get("challenger_argument", ""),
                "note": exp.get("note", ""),
            }
            if gap >= GAP_THRESHOLD or d.get("human_review"):
                entry["human_review"] = True
                human_review.append(entry)
            else:
                agreed.append(entry)
        elif score >= 7:
            pending_challenger.append({
                "item": exp_id,
                "type": "experiment",
                "judge_score": score,
                "reason": "Judge scored >=7 but no challenger entry in debate JSON",
                "note": exp.get("note", ""),
            })
        else:
            agreed.append({
                "item": exp_id,
                "type": "experiment",
                "judge_score": score,
            })

    return {
        "agreed": agreed,
        "human_review": human_review,
        "pending_challenger_review": pending_challenger,
    }


def print_judge_instructions(slug: str) -> None:
    print("\n=== Judge + challenger (manual — run in Cursor Agent) ===")
    print(
        f"Read eval/rubric.md and skills/evaluate.md (Optional: Qualitative judge).\n"
        f"Judge then challenger reports/{slug}.md\n"
        f"Write: eval/scores/{slug}_judge.json and eval/scores/{slug}_debate.json\n"
        f"Re-run: python eval/run_full_eval.py {slug}"
    )


def print_final_summary(slug: str, verdict: dict) -> None:
    print("\n" + "=" * 60)
    print(f"FULL EVAL SUMMARY - {slug}")
    print("=" * 60)

    struct = verdict.get("structural_scores", {})
    if struct:
        print(f"Structural: {struct.get('structural')} | Field: {struct.get('field_quality')} | Overall: {struct.get('overall')}")
        flags = struct.get("flags", [])
        if flags:
            print(f"Flags ({len(flags)}): {', '.join(flags[:5])}{'...' if len(flags) > 5 else ''}")
        else:
            print("Flags: none")

    grounded_warns = verdict.get("grounded_warns", [])
    if grounded_warns:
        print(f"Grounded Warns: {', '.join(grounded_warns)}")
    else:
        print("Grounded Warns: none")

    cross = verdict.get("cross_audit")
    if cross:
        comp = cross.get("comparison", {})
        if comp:
            o = comp.get("overall", {})
            print(f"Cross-audit overall delta (cal - gen): {o.get('delta', 'n/a')}")
        if cross.get("flags"):
            print(f"Cross-audit flags: {', '.join(cross['flags'])}")

    recurring = verdict.get("recurring_patterns", [])
    if recurring:
        print(f"Recurring patterns: {len(recurring)}")
        for p in recurring:
            print(f"  - {p['flag']} -> {p.get('suggested_skill', '?')}")
    else:
        print("Recurring patterns: none")

    judge_v = verdict.get("judge_verdict") or {}
    hr = judge_v.get("human_review", [])
    pending = judge_v.get("pending_challenger_review", [])
    if hr:
        print(f"\nHUMAN REVIEW ({len(hr)} items, gap >={GAP_THRESHOLD}):")
        for item in hr:
            print(f"  - {item['item']} ({item['type']}): judge={item['judge_score']} challenger={item['challenger_score']}")
    elif pending:
        print(f"\nPending challenger review: {len(pending)} items (judge >=7, no debate entry)")
    else:
        if judge_v:
            print("\nJudge/challenger: all reviewed items within gap threshold")
        else:
            print("\nJudge/challenger: not run yet (see instructions above)")

    print(f"\nVerdict saved: eval/scores/{slug}_verdict.json")
    print("=" * 60)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python eval/run_full_eval.py <slug>", file=sys.stderr)
        sys.exit(1)

    slug = sys.argv[1].replace(".md", "")
    report = REPORTS / f"{slug}.md"
    if not report.exists():
        print(f"Missing report: {report}", file=sys.stderr)
        sys.exit(1)

    py = sys.executable

    # 1. Structural eval
    rc = run_step("Structural eval", [py, str(EVAL_DIR / "eval.py"), str(report)])
    if rc != 0:
        print("(structural eval reported issues — continuing)")

    # 2. Grounded checks
    url = store_url_from_report(report)
    grounded_out = ROOT / "artifacts" / slug / "tech_grounded.json"
    run_step(
        "Grounded checks",
        [py, str(EVAL_DIR / "grounded.py"), "--url", url, "--out", str(grounded_out)],
    )

    # 3. Pattern tracker
    run_step("Pattern tracker", [py, str(EVAL_DIR / "pattern_tracker.py")])

    # 4. Cross-audit
    gp = REPORTS / "gingerpeople.md"
    zr = REPORTS / "zenrojas.md"
    cross_data = None
    if gp.exists() and zr.exists():
        run_step("Cross-audit", [py, str(EVAL_DIR / "cross_audit.py")])
        cross_data = load_json(SCORES_DIR / "cross_audit.json")
    else:
        print("\n=== Cross-audit ===\n(skipped — need both gingerpeople.md and zenrojas.md)")

    # 5. Judge instructions
    print_judge_instructions(slug)

    # 6. Compare judge vs debate if present
    judge = load_json(SCORES_DIR / f"{slug}_judge.json")
    debate = load_json(SCORES_DIR / f"{slug}_debate.json")
    judge_verdict = None
    if judge:
        judge_verdict = compare_judge_debate(judge, debate)
    elif debate:
        judge_verdict = {"error": "debate.json exists but judge.json missing"}

    # Load scores for verdict
    struct_data = load_json(SCORES_DIR / f"{slug}.json")
    recurring_data = load_json(SCORES_DIR / "recurring_patterns.json")

    grounded_warns = []
    if grounded_out.exists():
        g = json.loads(grounded_out.read_text(encoding="utf-8"))
        for name, check in g.get("checks", {}).items():
            if check.get("status") == "Warn":
                grounded_warns.append(name)

    verdict = {
        "store": slug,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "structural_scores": {
            "structural": struct_data["scores"]["structural"] if struct_data else None,
            "field_quality": struct_data["scores"]["field_quality"] if struct_data else None,
            "overall": struct_data["scores"]["overall"] if struct_data else None,
            "flags": struct_data.get("flags", []) if struct_data else [],
        },
        "grounded_warns": grounded_warns,
        "cross_audit": cross_data,
        "recurring_patterns": recurring_data.get("recurring", []) if recurring_data else [],
        "judge_verdict": judge_verdict,
        "gap_threshold": GAP_THRESHOLD,
    }

    verdict_path = SCORES_DIR / f"{slug}_verdict.json"
    verdict_path.write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")

    print_final_summary(slug, verdict)


if __name__ == "__main__":
    main()
