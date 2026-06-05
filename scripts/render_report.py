#!/usr/bin/env python3
"""Render reports/{slug}.md to reports/{slug}.html using a static template (no LLM)."""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "report.html"

PILLAR_COLORS = {
    "Conversion": "#2563eb",
    "AOV": "#7c3aed",
    "Retention": "#059669",
    "Acquisition": "#d97706",
    "Performance": "#dc2626",
}

IMAGE_PATH_RE = re.compile(
    r"artifacts/[a-zA-Z0-9_./-]+\.(?:png|webp|jpe?g)",
    re.I,
)
SCREENSHOT_COLON_RE = re.compile(
    r"screenshot:\s*(artifacts/[a-zA-Z0-9_./-]+\.(?:png|webp|jpe?g))",
    re.I,
)
CONFIDENCE_RE = re.compile(r"^\s*(\d{1,3})\s*$")
LIFT_RE = re.compile(r"\+\s*(\d+)\s*[–\-—]\s*(\d+)\s*%", re.I)
PSI_RE = re.compile(r"(\d+)/100")


def escape(s: str) -> str:
    return html.escape(s, quote=True)


def md_bold_to_html(text: str) -> str:
    parts = []
    for para in text.strip().split("\n\n"):
        para = para.strip()
        if not para:
            continue
        para = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", para)
        parts.append(f"<p>{para}</p>")
    return "\n".join(parts) if parts else "<p></p>"


def parse_table_rows(lines: list[str]) -> list[list[str]]:
    rows = [ln for ln in lines if ln.strip().startswith("|") and "---" not in ln]
    if len(rows) <= 1:
        return []
    return [[c.strip() for c in row.strip("|").split("|")] for row in rows[1:]]


def parse_table_fixed(lines: list[str]) -> str:
    rows = [ln for ln in lines if ln.strip().startswith("|") and "---" not in ln]
    if not rows:
        return "<p>No table data.</p>"
    out = ["<table>"]
    for i, row in enumerate(rows):
        cells = [c.strip() for c in row.strip("|").split("|")]
        tag = "th" if i == 0 else "td"
        rendered = []
        for j, c in enumerate(cells):
            if i > 0 and j == 1 and c in ("Pass", "Warn", "Fail"):
                rendered.append(f'<span class="status-{c}">{escape(c)}</span>')
            else:
                rendered.append(escape(c))
        out.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in rendered) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def extract_image_paths(text: str) -> list[str]:
    paths = set(IMAGE_PATH_RE.findall(text))
    paths |= {m.group(1) for m in SCREENSHOT_COLON_RE.finditer(text)}
    return sorted(paths)


def format_field_value(key: str, value: str, slug: str, assets_dir: Path) -> str:
    if key.lower() != "evidence":
        return escape(value)
    paths = extract_image_paths(value)
    imgs: list[str] = []
    for rel in paths:
        src = ROOT / rel.replace("\\", "/")
        if not src.is_file():
            continue
        assets_dir.mkdir(parents=True, exist_ok=True)
        dest_name = src.name
        dest = assets_dir / dest_name
        shutil.copy2(src, dest)
        imgs.append(
            f'<img class="evidence-shot" src="assets/{slug}/{dest_name}" '
            f'alt="Evidence: {escape(src.name)}" loading="lazy" />'
        )
    body = escape(value)
    if imgs:
        body += '<div class="evidence-images">' + "".join(imgs) + "</div>"
    return body


def parse_experiments(block: str, slug: str, assets_dir: Path) -> tuple[str, list[dict]]:
    chunks = re.split(r"(?=^### exp-)", block, flags=re.M)
    cards = []
    meta: list[dict] = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk.startswith("###"):
            continue
        m = re.match(r"^### (exp-[a-zA-Z0-9]+)\s*[—\-]\s*(.+)$", chunk, re.M)
        if not m:
            continue
        exp_id, title = m.group(1), m.group(2).strip()
        fields = dict(re.findall(r"^\*\*([^*]+):\*\*\s*(.+)$", chunk, re.M))
        pillar = fields.get("Pillar", "").strip()
        conf = fields.get("Confidence", "")
        lift = fields.get("Expected lift", "")
        conf_val = None
        cm = CONFIDENCE_RE.match(conf.strip()) if conf else None
        if cm:
            conf_val = int(cm.group(1))
        lift_mid = None
        lm = LIFT_RE.search(lift) if lift else None
        if lm:
            lift_mid = (int(lm.group(1)) + int(lm.group(2))) // 2

        meta.append({"pillar": pillar, "confidence": conf_val, "lift_mid": lift_mid})

        pills = []
        if conf_val is not None:
            pills.append(f'<span class="pill">{conf_val}% conf</span>')
        if lift_mid is not None:
            pills.append(f'<span class="pill pill-lift">+{lift_mid}% est</span>')

        badge_cls = f"badge-{pillar.replace(' ', '')}" if pillar else "badge"
        cards.append(
            f'<div class="card">'
            f'<div class="card-head">'
            f'<span class="badge {badge_cls}">{escape(pillar)}</span>'
            + "".join(pills)
            + f"</div>"
            f"<h3>{escape(exp_id)} — {escape(title)}</h3><dl>"
            + "".join(
                f"<dt>{escape(k)}</dt><dd>{format_field_value(k, v, slug, assets_dir)}</dd>"
                for k, v in fields.items()
                if k != "Pillar"
            )
            + "</dl></div>"
        )
    html_out = "\n".join(cards) if cards else "<p>No experiments parsed.</p>"
    return html_out, meta


def load_eval_score(slug: str) -> float | None:
    path = ROOT / "eval" / "scores" / f"{slug}.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("scores", {}).get("overall")
    except Exception:
        return None


def tech_status_counts(tech_rows: list[list[str]]) -> Counter:
    counts: Counter = Counter()
    for row in tech_rows:
        if len(row) >= 2 and row[1] in ("Pass", "Warn", "Fail"):
            counts[row[1]] += 1
    return counts


def psi_scores(tech_rows: list[list[str]]) -> list[int]:
    scores = []
    for row in tech_rows:
        if len(row) >= 3 and "Page Speed" in row[0]:
            m = PSI_RE.search(row[2])
            if m:
                scores.append(int(m.group(1)))
    return scores


def build_pillar_chart(pillar_counts: Counter) -> str:
    if not pillar_counts:
        return "<p class='kpi-sub'>No pillar data</p>"
    max_c = max(pillar_counts.values()) or 1
    rows = []
    for pillar in ("Conversion", "AOV", "Retention", "Acquisition", "Performance"):
        n = pillar_counts.get(pillar, 0)
        if n == 0:
            continue
        pct = int(n / max_c * 100)
        color = PILLAR_COLORS.get(pillar, "#78716c")
        rows.append(
            f'<div class="bar-row">'
            f'<span class="bar-label">{escape(pillar)}</span>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>'
            f'<span class="bar-count">{n}</span></div>'
        )
    return "\n".join(rows)


def build_kpi_dashboard(
    slug: str,
    exp_meta: list[dict],
    tech_rows: list[list[str]],
) -> dict[str, str]:
    eval_score = load_eval_score(slug)
    exp_count = len(exp_meta)
    confidences = [e["confidence"] for e in exp_meta if e.get("confidence") is not None]
    avg_conf = round(sum(confidences) / len(confidences)) if confidences else None
    lifts = [e["lift_mid"] for e in exp_meta if e.get("lift_mid") is not None]
    avg_lift = round(sum(lifts) / len(lifts)) if lifts else None

    pillar_counts = Counter(e["pillar"] for e in exp_meta if e.get("pillar"))
    tech = tech_status_counts(tech_rows)
    total_tech = sum(tech.values()) or 1
    pass_n, warn_n, fail_n = tech.get("Pass", 0), tech.get("Warn", 0), tech.get("Fail", 0)
    pass_deg = pass_n / total_tech * 360
    warn_end_deg = (pass_n + warn_n) / total_tech * 360

    psi = psi_scores(tech_rows)
    if len(psi) >= 2:
        psi_label = f"{min(psi)}/{max(psi)}"
        psi_sub = "mobile & desktop"
    elif psi:
        psi_label = f"{psi[0]}/100"
        psi_sub = "PageSpeed"
    else:
        psi_label = "—"
        psi_sub = "not measured"

    eval_display = f"{eval_score:.1f}" if eval_score is not None else "—"
    conf_display = f"{avg_conf}<small>%</small>" if avg_conf is not None else "—"
    lift_display = f"+{avg_lift}<small>%</small>" if avg_lift is not None else "—"
    pass_rate = f"{pass_n}<small>/{total_tech}</small>"

    kpi_html = f"""
    <div class="kpi-grid">
      <div class="kpi">
        <div class="kpi-label">Eval score</div>
        <div class="kpi-value">{eval_display}</div>
        <div class="kpi-sub">Structural + field quality</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Experiments</div>
        <div class="kpi-value">{exp_count}</div>
        <div class="kpi-sub">Across 5 pillars</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Avg confidence</div>
        <div class="kpi-value">{conf_display}</div>
        <div class="kpi-sub">Experiment median belief</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Avg expected lift</div>
        <div class="kpi-value">{lift_display}</div>
        <div class="kpi-sub">Midpoint of ranges</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">PageSpeed</div>
        <div class="kpi-value">{escape(psi_label)}</div>
        <div class="kpi-sub">{escape(psi_sub)}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Tech pass rate</div>
        <div class="kpi-value">{pass_rate}</div>
        <div class="kpi-sub">{pass_n} pass · {warn_n} warn · {fail_n} fail</div>
      </div>
    </div>
    <div class="charts">
      <div class="chart-card">
        <div class="chart-title">Experiments by pillar</div>
        {build_pillar_chart(pillar_counts)}
      </div>
      <div class="chart-card">
        <div class="chart-title">Technical checks</div>
        <div class="donut-wrap">
          <div class="donut"></div>
          <div class="donut-legend">
            <div class="legend-item"><span class="dot" style="background:var(--pass)"></span> Pass · {pass_n}</div>
            <div class="legend-item"><span class="dot" style="background:var(--warn)"></span> Warn · {warn_n}</div>
            <div class="legend-item"><span class="dot" style="background:var(--fail)"></span> Fail · {fail_n}</div>
          </div>
        </div>
      </div>
    </div>"""

    return {
        "KPI_DASHBOARD": kpi_html,
        "STORE_SLUG": slug,
        "TECH_PASS_DEG": f"{pass_deg:.1f}",
        "TECH_WARN_END_DEG": f"{warn_end_deg:.1f}",
    }


def parse_report(md: str, slug: str, assets_dir: Path) -> dict[str, str]:
    title_m = re.match(r"^#\s+(.+)$", md, re.M)
    title = title_m.group(1).strip() if title_m else "Audit report"

    sections: dict[str, str] = {}
    for m in re.finditer(r"^## (.+)$", md, re.M):
        name = m.group(1).strip().lower()
        start = m.end()
        nxt = re.search(r"^## ", md[start:], re.M)
        end = start + nxt.start() if nxt else len(md)
        sections[name] = md[start:end].strip()

    exec_body = sections.get("executive summary", "")
    exp_body = sections.get("proposed experiments", "")
    comp_body = sections.get("competitor analysis", "")
    tech_body = sections.get("technical checks", "")

    experiments_html, exp_meta = parse_experiments(exp_body, slug, assets_dir)
    tech_rows = parse_table_rows(tech_body.splitlines())
    kpi = build_kpi_dashboard(slug, exp_meta, tech_rows)

    result = {
        "TITLE": title,
        "EXECUTIVE_SUMMARY": md_bold_to_html(exec_body),
        "EXPERIMENTS": experiments_html,
        "COMPETITORS": parse_table_fixed(comp_body.splitlines()),
        "TECHNICAL": parse_table_fixed(tech_body.splitlines()),
    }
    result.update(kpi)
    return result


def render(md_path: Path, out_path: Path | None = None) -> Path:
    md = md_path.read_text(encoding="utf-8")
    slug = md_path.stem
    assets_dir = ROOT / "reports" / "assets" / slug
    data = parse_report(md, slug, assets_dir)
    data["GENERATED_AT"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    tpl = TEMPLATE.read_text(encoding="utf-8")
    for key, val in data.items():
        tpl = tpl.replace("{{" + key + "}}", val)
    out = out_path or md_path.with_suffix(".html")
    out.write_text(tpl, encoding="utf-8")
    return out


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/render_report.py reports/<slug>.md", file=sys.stderr)
        sys.exit(1)
    md_path = Path(sys.argv[1])
    if not md_path.is_absolute():
        md_path = ROOT / md_path
    if not md_path.exists():
        print(f"Not found: {md_path}", file=sys.stderr)
        sys.exit(1)
    out = render(md_path)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
