#!/usr/bin/env python3
"""Discover URLs from homepage + sitemap and crawl representative surfaces."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

from crawl_lib import fetch_page, slug_from_url, UA

sys.path.insert(0, str(Path(__file__).resolve().parent))


def links_from_html(origin: str, html: str) -> set[str]:
    host = urlparse(origin).netloc.replace("www.", "")
    paths = set(re.findall(r'href=["\'](/[^"\']+)["\']', html))
    paths |= set(re.findall(r'href=["\'](https?://[^"\']+)["\']', html))
    out = set()
    for p in paths:
        u = p if p.startswith("http") else urljoin(origin, p)
        if urlparse(u).netloc.replace("www.", "") == host:
            out.add(u.split("#")[0].rstrip("/") or u)
    return out


def links_from_sitemap(origin: str) -> set[str]:
    urls = set()
    for path in ("/sitemap.xml", "/sitemap_products_1.xml"):
        try:
            r = requests.get(urljoin(origin, path), timeout=30, headers=UA)
            if r.status_code != 200:
                continue
            urls |= set(re.findall(r"<loc>([^<]+)</loc>", r.text))
        except Exception:
            pass
    host = urlparse(origin).netloc.replace("www.", "")
    return {u for u in urls if urlparse(u).netloc.replace("www.", "") == host}


def discover(origin: str, html: str) -> dict[str, str]:
    full = links_from_html(origin, html) | links_from_sitemap(origin)

    def pick(pred):
        for u in sorted(full, key=len):
            if pred(u):
                return u
        return None

    pdps = sorted(u for u in full if "/products/" in u)
    # prefer gingerpeople known patterns only as sort key, not filter — longer path first
    pdps = sorted(pdps, key=lambda u: ("/products/" not in u, u))

    collection = pick(lambda u: "/the-ginger-people-products" in u) or pick(
        lambda u: "/collections/" in u and "all" not in u
    ) or pick(lambda u: "/collections/" in u)

    wtb = pick(lambda u: "where-to-buy" in u.lower()) or pick(
        lambda u: any(x in u.lower() for x in ("faq", "where-to-buy", "/pages/"))
    )

    blog = pick(lambda u: "/boost-your-glp" in u or "/blogs/" in u) or pick(
        lambda u: "/blog" in u
    )

    return {
        "homepage": origin.rstrip("/"),
        "pdp_1": pdps[0] if pdps else urljoin(origin, "/products/"),
        "pdp_2": pdps[1] if len(pdps) > 1 else (pdps[0] if pdps else urljoin(origin, "/products/")),
        "collection": collection or urljoin(origin, "/collections/all"),
        "cart": urljoin(origin, "/cart"),
        "faq_or_where_to_buy": wtb or urljoin(origin, "/pages/faqs"),
        "content_page": blog or origin,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    origin = args.url.rstrip("/")
    if not origin.startswith("http"):
        origin = f"https://{origin}"
    slug = slug_from_url(origin).split(".")[0]
    out_dir = Path("artifacts") / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    r = requests.get(origin, timeout=45, headers=UA)
    urls = discover(origin, r.text)

    pages = []
    for surface, full in urls.items():
        try:
            status, title, h1, notes = fetch_page(full)
        except Exception as e:
            status, title, h1, notes = 0, "", "", [str(e)]
        pages.append({"surface": surface, "url": full, "status": status})
        note_str = "; ".join(notes)
        (out_dir / f"{surface}.md").write_text(
            f"# {surface}\n\n- **URL:** {full}\n- **Status:** {status}\n"
            f"- **Title:** {title}\n- **H1:** {h1}\n- **Notes:** {note_str}\n",
            encoding="utf-8",
        )
        print(surface, status, full[:75])

    manifest = {
        "store": urlparse(origin).netloc.replace("www.", ""),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "pages": pages,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("=== screenshots (required) ===")
    try:
        from capture_audit_screenshots import capture_for_slug

        captured = capture_for_slug(slug, Path("artifacts"))
        print(f"Captured {len(captured)} screenshots")
    except Exception as e:
        print(f"Screenshot capture failed: {e}", file=sys.stderr)
        print("Run: pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
