#!/usr/bin/env python3
"""Run structural eval after an audit report is written."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
EVAL = ROOT / "eval" / "eval.py"
CROSS = ROOT / "eval" / "cross_audit.py"
RENDER = ROOT / "scripts" / "render_report.py"
DASHBOARD = ROOT / "eval" / "render_dashboard.py"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/post_audit.py <slug>", file=sys.stderr)
        print("Example: python scripts/post_audit.py zenrojas", file=sys.stderr)
        sys.exit(1)
    slug = sys.argv[1].replace(".md", "")
    report = REPORTS / f"{slug}.md"
    if not report.exists():
        print(f"Missing report: {report}", file=sys.stderr)
        sys.exit(1)

    print(f"=== eval: {report.name} ===")
    r1 = subprocess.run([sys.executable, str(EVAL), str(report)], cwd=ROOT)
    if r1.returncode != 0:
        sys.exit(r1.returncode)

    gp = REPORTS / "gingerpeople.md"
    zr = REPORTS / "zenrojas.md"
    if gp.exists() and zr.exists():
        print("=== cross_audit ===")
        r2 = subprocess.run([sys.executable, str(CROSS)], cwd=ROOT)
        if r2.returncode != 0:
            sys.exit(r2.returncode)
    else:
        print("(cross_audit skipped until both gingerpeople.md and zenrojas.md exist)")

    print("=== render HTML ===")
    r3 = subprocess.run(
        [sys.executable, str(RENDER), str(report)], cwd=ROOT
    )
    if r3.returncode != 0:
        sys.exit(r3.returncode)

    if gp.exists() and zr.exists():
        print("=== dashboard ===")
        subprocess.run([sys.executable, str(DASHBOARD)], cwd=ROOT)

    print("=== done ===")


if __name__ == "__main__":
    main()
