#!/usr/bin/env python3
"""Capture viewport or element screenshots via Playwright."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from screenshot_lib import capture_screenshot  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Save a PNG screenshot of a URL (full page or element)."
    )
    parser.add_argument("--url", required=True, help="Page URL to open")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument(
        "--selector",
        help='Playwright selector, e.g. "text=Add to cart"',
    )
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page")
    parser.add_argument("--wait-ms", type=int, default=2000, help="Ms after navigation (default 2000)")
    args = parser.parse_args()

    try:
        capture_screenshot(
            args.url,
            Path(args.out),
            selector=args.selector,
            full_page=args.full_page,
            wait_ms=args.wait_ms,
        )
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
