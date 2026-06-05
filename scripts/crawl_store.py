#!/usr/bin/env python3
"""Deprecated wrapper — use discover_store.py."""

import sys

if __name__ == "__main__":
    print("Use: python scripts/discover_store.py <url>", file=sys.stderr)
    from discover_store import main

    main()
