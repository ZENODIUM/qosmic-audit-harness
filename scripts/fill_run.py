#!/usr/bin/env python3
"""Create or update runs/{slug}/run.json for manual token / timing notes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    p = argparse.ArgumentParser(description="Update runs/{slug}/run.json")
    p.add_argument("slug", help="e.g. zenrojas")
    p.add_argument("--store", help="hostname e.g. zenrojas.com")
    p.add_argument("--tokens-in", type=int, default=None)
    p.add_argument("--tokens-out", type=int, default=None)
    p.add_argument("--notes", default="")
    p.add_argument("--started", help="ISO8601 start time")
    p.add_argument("--completed", help="ISO8601 end time")
    p.add_argument(
        "--refresh-html",
        action="store_true",
        help="Re-render reports/{slug}.html after updating run.json",
    )
    args = p.parse_args()

    out_dir = ROOT / "runs" / args.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "run.json"
    data = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    data.setdefault("store", args.store or f"{args.slug}.com")
    if args.started:
        data["started_at"] = args.started
    elif "started_at" not in data:
        data["started_at"] = now
    if args.completed:
        data["completed_at"] = args.completed
    else:
        data["completed_at"] = now
    if args.tokens_in is not None:
        data["cursor_tokens_input"] = args.tokens_in
    if args.tokens_out is not None:
        data["cursor_tokens_output"] = args.tokens_out
    if args.notes:
        data["notes"] = args.notes
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")

    if args.refresh_html:
        report = ROOT / "reports" / f"{args.slug}.md"
        if not report.exists():
            print(f"Missing report: {report}", file=sys.stderr)
            sys.exit(1)
        rc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "render_report.py"), str(report)],
            cwd=ROOT,
        )
        sys.exit(rc.returncode)


if __name__ == "__main__":
    main()
