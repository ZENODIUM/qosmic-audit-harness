#!/usr/bin/env python3
"""Verify artifact and screenshot paths cited in a report exist on disk."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARTIFACT_RE = re.compile(
    r"artifacts/[a-zA-Z0-9_./-]+\.(?:md|json|png|webp|jpe?g)",
    re.I,
)
SCREENSHOT_IN_EVIDENCE_RE = re.compile(
    r"screenshot:\s*(artifacts/[a-zA-Z0-9_./-]+\.(?:png|webp|jpe?g))",
    re.I,
)


def cited_paths(text: str) -> set[str]:
    paths = set(ARTIFACT_RE.findall(text))
    paths |= {m.group(1) for m in SCREENSHOT_IN_EVIDENCE_RE.finditer(text)}
    return paths


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_evidence.py reports/<slug>.md", file=sys.stderr)
        sys.exit(1)
    md_path = Path(sys.argv[1])
    if not md_path.is_absolute():
        md_path = ROOT / md_path
    text = md_path.read_text(encoding="utf-8")
    cites = cited_paths(text)
    missing_files = []
    for cite in sorted(cites):
        path = ROOT / cite.replace("\\", "/")
        if not path.exists():
            missing_files.append(cite)

    has_md = any(c.endswith(".md") for c in cites)
    has_image = any(re.search(r"\.(png|webp|jpe?g)$", c, re.I) for c in cites)
    report_errors = []
    if has_md and not has_image:
        report_errors.append(
            "No screenshot paths cited — required: screenshot: artifacts/{slug}/screenshots/..."
        )

    if report_errors:
        print("Errors:")
        for e in report_errors:
            print(f"  - {e}")

    if missing_files:
        print("Missing evidence paths:")
        for m in missing_files:
            print(f"  - {m}")

    if missing_files or report_errors:
        sys.exit(1)
    print(f"OK: {len(cites)} artifact/screenshot paths exist")
    sys.exit(0)


if __name__ == "__main__":
    main()
