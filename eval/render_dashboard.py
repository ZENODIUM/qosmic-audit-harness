#!/usr/bin/env python3
"""Build reports/index.html from eval/scores/*.json (no LLM)."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORES = ROOT / "eval" / "scores"
REPORTS = ROOT / "reports"

SKIP_FILES = {
    "cross_audit.json",
    "recurring_patterns.json",
    "calibration_report.json",
}
SKIP_SUFFIXES = ("_judge.json", "_debate.json", "_verdict.json")


def is_store_score_file(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return False
    if any(path.name.endswith(s) for s in SKIP_SUFFIXES):
        return False
    return path.suffix == ".json"


def main() -> None:
    rows = []
    for path in sorted(SCORES.glob("*.json")):
        if not is_store_score_file(path):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if "scores" not in data or "flags" not in data:
            continue
        slug = data.get("store", path.stem)
        scores = data.get("scores", {})
        flags = data.get("flags", [])
        md = REPORTS / f"{slug}.md"
        ht = REPORTS / f"{slug}.html"
        ht_cell = f'<td><a href="{slug}.html">View</a></td>' if ht.exists() else "<td>—</td>"
        overall = scores.get("overall", "—")
        rows.append(
            "<tr>"
            f"<td><strong>{html.escape(slug)}</strong></td>"
            f"<td>{'yes' if md.exists() else '—'}</td>"
            f"{ht_cell}"
            f'<td><span class="score">{overall}</span></td>'
            f"<td>{scores.get('structural', '—')}</td>"
            f"<td>{scores.get('field_quality', '—')}</td>"
            f"<td>{html.escape(', '.join(flags) if flags else 'none')}</td>"
            "</tr>"
        )

    cross = ""
    cross_path = SCORES / "cross_audit.json"
    if cross_path.exists():
        c = json.loads(cross_path.read_text(encoding="utf-8"))
        cross = f'<p class="note">{html.escape(c.get("interpretation", ""))}</p>'

    body = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Qosmic Eval Dashboard</title>
<style>
:root {{ --bg:#f7f6f3; --surface:#fff; --border:#e8e4dc; --text:#1c1917; --muted:#78716c; --accent:#2563eb; }}
* {{ box-sizing:border-box; }}
body {{ font-family:"Segoe UI",system-ui,sans-serif; background:var(--bg); color:var(--text); margin:0; padding:2rem 1.5rem; line-height:1.5; }}
.wrap {{ max-width:900px; margin:0 auto; }}
h1 {{ font-size:1.5rem; font-weight:650; margin:0 0 0.25rem; letter-spacing:-0.02em; }}
.sub {{ color:var(--muted); font-size:0.9rem; margin:0 0 1.5rem; }}
.note {{ background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:0.75rem 1rem; font-size:0.88rem; color:#1e40af; margin-bottom:1.25rem; }}
.table-wrap {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; overflow:hidden; box-shadow:0 1px 2px rgba(28,25,23,0.04); }}
table {{ border-collapse:collapse; width:100%; font-size:0.88rem; }}
th, td {{ padding:0.65rem 0.9rem; text-align:left; border-bottom:1px solid var(--border); }}
tr:last-child td {{ border-bottom:none; }}
th {{ background:#fafaf9; color:var(--muted); font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; font-weight:650; }}
tr:hover td {{ background:#fafaf9; }}
a {{ color:var(--accent); text-decoration:none; font-weight:600; }}
a:hover {{ text-decoration:underline; }}
.score {{ font-weight:700; font-size:1.05rem; color:var(--accent); }}
</style></head><body>
<div class="wrap">
<h1>Qosmic eval dashboard</h1>
<p class="sub">Structural scores across audited stores</p>
{cross}
<div class="table-wrap">
<table><thead><tr>
<th>Store</th><th>Report</th><th>HTML</th><th>Overall</th><th>Structural</th><th>Field</th><th>Flags</th>
</tr></thead><tbody>{''.join(rows)}</tbody></table>
</div>
</div>
</body></html>"""

    out = REPORTS / "index.html"
    out.write_text(body, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
