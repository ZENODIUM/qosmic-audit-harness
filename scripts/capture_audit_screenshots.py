#!/usr/bin/env python3
"""Capture full-page screenshots for every surface in artifacts/{slug}/manifest.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from screenshot_lib import capture_pages, capture_screenshot  # noqa: E402


def capture_for_slug(slug: str, artifacts_root: Path | None = None) -> list[str]:
    base = (artifacts_root or ROOT / "artifacts") / slug
    manifest_path = base / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    shots_dir = base / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)
    captured: list[str] = []

    batch: list[tuple[str, Path]] = []
    page_meta: list[tuple[dict, str, Path]] = []

    for page in manifest.get("pages", []):
        surface = page.get("surface", "unknown")
        url = page.get("url")
        if not url:
            continue
        rel = f"screenshots/{surface}_full.png"
        out = base / rel
        batch.append((url, out))
        page_meta.append((page, surface, out))

    try:
        capture_pages(batch, full_page=True)
        for page, surface, out in page_meta:
            rel = f"screenshots/{surface}_full.png"
            page["screenshot"] = rel
            captured.append(rel)
            print(f"screenshot {surface} -> {rel}")

            md_path = base / f"{surface}.md"
            if md_path.exists():
                text = md_path.read_text(encoding="utf-8")
                shot_line = f"- **Screenshot:** artifacts/{slug}/{rel}\n"
                if "**Screenshot:**" not in text:
                    text = text.rstrip() + "\n" + shot_line
                    md_path.write_text(text, encoding="utf-8")
    except Exception as e:
        print(f"WARN: batch capture failed ({e}); falling back to per-page", file=sys.stderr)
        captured.clear()
        for page, surface, out in page_meta:
            url = page.get("url")
            if not url:
                continue
            rel = f"screenshots/{surface}_full.png"
            try:
                capture_screenshot(url, out, full_page=True)
                page["screenshot"] = rel
                captured.append(rel)
                print(f"screenshot {surface} -> {rel}")

                md_path = base / f"{surface}.md"
                if md_path.exists():
                    text = md_path.read_text(encoding="utf-8")
                    shot_line = f"- **Screenshot:** artifacts/{slug}/{rel}\n"
                    if "**Screenshot:**" not in text:
                        text = text.rstrip() + "\n" + shot_line
                        md_path.write_text(text, encoding="utf-8")
            except Exception as err:
                print(f"WARN: screenshot failed for {surface} ({url}): {err}", file=sys.stderr)

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return captured


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture manifest surface screenshots.")
    parser.add_argument("slug", help="Store slug, e.g. zenrojas")
    args = parser.parse_args()
    captured = capture_for_slug(args.slug)
    if not captured:
        print("ERROR: no screenshots captured", file=sys.stderr)
        sys.exit(1)
    print(f"Captured {len(captured)} screenshots for {args.slug}")


if __name__ == "__main__":
    main()
