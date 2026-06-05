#!/usr/bin/env python3
"""Structural and field-quality eval for Qosmic audit reports."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Allow running as script from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent))
from grounded import normalize_store_url, run_grounded  # noqa: E402

PILLARS = {"Conversion", "AOV", "Retention", "Acquisition", "Performance"}
REQUIRED_EXP_FIELDS = [
    "Pillar",
    "URL",
    "Evidence",
    "Hypothesis",
    "Primary change",
    "Primary KPI",
    "Decision rule",
    "Expected lift",
    "Confidence",
]
LIFT_RE = re.compile(r"\+\s*\d+\s*[–\-—]\s*\d+\s*%", re.I)
CONFIDENCE_RE = re.compile(r"^\s*(\d{1,3})\s*%?\s*$")
DIGIT_RE = re.compile(r"\d")


def read_report(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_experiments(text: str) -> list[tuple[str, str]]:
    """Return list of (exp_id, block_text)."""
    pattern = re.compile(r"^###\s+(exp-[a-zA-Z0-9]+)\s*[—\-]\s*(.+)$", re.M)
    matches = list(pattern.finditer(text))
    if not matches:
        return []
    blocks = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks.append((m.group(1), text[start:end]))
    return blocks


def extract_field(block: str, field: str) -> str | None:
    m = re.search(rf"\*\*{re.escape(field)}:\*\*\s*(.+)", block, re.I)
    return m.group(1).strip() if m else None


def validate_executive_summary(text: str) -> tuple[bool, list[str]]:
    flags = []
    m = re.search(r"## Executive summary\s*(.+?)(?=\n## |\Z)", text, re.S | re.I)
    if not m:
        return False, ["missing_executive_summary"]
    body = m.group(1).strip()
    bullets = len(re.findall(r"^\s*[-*•]", body, re.M))
    paragraphs = [p for p in re.split(r"\n\s*\n", body) if p.strip() and not p.strip().startswith("-")]
    if bullets > 4:
        flags.append("executive_summary_too_bullet_heavy")
    if len(paragraphs) < 2:
        flags.append("executive_summary_needs_2_3_paragraphs")
    return len(flags) == 0, flags


def validate_experiment(exp_id: str, block: str) -> list[str]:
    flags = []
    for field in REQUIRED_EXP_FIELDS:
        if not extract_field(block, field):
            flags.append(f"{exp_id}:missing_{field.lower().replace(' ', '_')}")

    pillar = extract_field(block, "Pillar")
    if pillar and pillar.split()[0] not in PILLARS:
        flags.append(f"{exp_id}:invalid_pillar")

    conf = extract_field(block, "Confidence")
    if conf:
        cm = CONFIDENCE_RE.match(conf)
        if not cm or not (0 <= int(cm.group(1)) <= 100):
            flags.append(f"{exp_id}:confidence_not_0_100_integer")

    lift = extract_field(block, "Expected lift")
    if lift and not LIFT_RE.search(lift):
        flags.append(f"{exp_id}:expected_lift_not_range_format")

    rule = extract_field(block, "Decision rule")
    if rule and not DIGIT_RE.search(rule):
        flags.append(f"{exp_id}:decision_rule_has_no_number")

    hyp = extract_field(block, "Hypothesis")
    if hyp and len(hyp) < 40:
        flags.append(f"{exp_id}:hypothesis_too_short")

    return flags


def count_table_rows(text: str, section: str) -> int:
    m = re.search(rf"## {section}\s*(.+?)(?=\n## |\Z)", text, re.S | re.I)
    if not m:
        return 0
    lines = [ln for ln in m.group(1).splitlines() if ln.strip().startswith("|") and "---" not in ln]
    return max(0, len(lines) - 1)  # minus header row


def compare_psi_to_report(text: str, grounded: dict) -> list[str]:
    flags = []
    for label, key in [("Page Speed Mobile", "mobile"), ("Page Speed Desktop", "desktop")]:
        g = grounded.get("checks", {}).get(label, {})
        if g.get("status") != "Pass":
            continue
        gm = re.search(r"(\d+)/100", g.get("detail", ""))
        if not gm:
            continue
        gscore = int(gm.group(1))
        # find in technical checks table
        row = re.search(
            rf"\|\s*{re.escape(label)}[^|]*\|[^|]*\|\s*(\d+)/100",
            text,
            re.I,
        )
        if row:
            rscore = int(row.group(1))
            if abs(rscore - gscore) > 10:
                flags.append(f"psi_mismatch_{key}:report={rscore} grounded={gscore}")
    return flags


def load_grounded(slug: str, store_url: str | None) -> dict:
    """Prefer saved tech_grounded.json; re-run only if missing."""
    grounded_path = Path(__file__).resolve().parent.parent / "artifacts" / slug / "tech_grounded.json"
    if grounded_path.is_file():
        return json.loads(grounded_path.read_text(encoding="utf-8"))
    if store_url:
        return run_grounded(store_url)
    return {}


def eval_report(path: Path) -> dict:
    text = read_report(path)
    slug = path.stem
    flags: list[str] = []
    experiments = split_experiments(text)

    if len(experiments) != 10:
        flags.append(f"experiment_count:{len(experiments)}_expected_10")

    pillars_found = set()
    for exp_id, block in experiments:
        flags.extend(validate_experiment(exp_id, block))
        p = extract_field(block, "Pillar")
        if p:
            for pillar in PILLARS:
                if pillar.lower() in p.lower():
                    pillars_found.add(pillar)
    missing_pillars = PILLARS - pillars_found
    if missing_pillars:
        flags.append(f"missing_pillars:{','.join(sorted(missing_pillars))}")

    ok_exec, exec_flags = validate_executive_summary(text)
    flags.extend(exec_flags)

    comp_rows = count_table_rows(text, "Competitor analysis")
    if comp_rows < 3:
        flags.append(f"competitor_rows:{comp_rows}_expected_3_plus")

    tech_rows = count_table_rows(text, "Technical checks")
    if tech_rows < 12:
        flags.append(f"technical_rows:{tech_rows}_expected_~15")

    # Grounded cross-check (graceful)
    store_url = None
    um = re.search(r"https?://[^\s\)|]+", text)
    if um:
        store_url = um.group(0)
    grounded = {}
    grounded_flags = []
    if store_url:
        try:
            grounded = load_grounded(slug, store_url)
            grounded_flags = compare_psi_to_report(text, grounded)
            flags.extend(grounded_flags)
        except Exception as e:
            flags.append(f"grounded_run_failed:{e}")

    # Scores
    structural = 10.0
    if len(experiments) != 10:
        structural -= 3
    if missing_pillars:
        structural -= len(missing_pillars) * 1.5
    if comp_rows < 3:
        structural -= 2
    if tech_rows < 12:
        structural -= 1
    structural = max(0, min(10, structural))

    field_penalty = min(10, len([f for f in flags if ":" in f and "exp-" in f]) * 0.5)
    field_quality = max(0, 10 - field_penalty)

    overall = round((structural + field_quality) / 2, 2)

    return {
        "store": slug,
        "report_path": str(path),
        "scores": {
            "structural": round(structural, 2),
            "field_quality": round(field_quality, 2),
            "overall": overall,
        },
        "counts": {
            "experiments": len(experiments),
            "pillars": sorted(pillars_found),
            "competitor_rows": comp_rows,
            "technical_rows": tech_rows,
        },
        "flags": flags,
        "grounded": grounded.get("checks", {}) if grounded else {},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("-o", "--output", type=Path, help="Write JSON scores path")
    args = parser.parse_args()
    result = eval_report(args.report)
    out = args.output or Path(__file__).parent / "scores" / f"{result['store']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["scores"]["overall"] >= 6 else 1)


if __name__ == "__main__":
    main()
