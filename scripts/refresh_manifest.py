#!/usr/bin/env python3
"""Re-fetch statuses for manifest pages sequentially."""

import json
import sys
from pathlib import Path

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}


def main(slug: str) -> None:
    manifest_path = Path("artifacts") / slug / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    for page in data["pages"]:
        url = page["url"]
        try:
            r = requests.get(url, timeout=60, headers=UA)
            page["status"] = r.status_code
            print(page["surface"], r.status_code)
        except Exception as e:
            page["status"] = 0
            print(page["surface"], "ERR", e)
    manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "zenrojas")
