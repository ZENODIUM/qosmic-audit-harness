"""Shared crawl helpers for discover_store / refresh_manifest."""

from __future__ import annotations

import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def slug_from_url(url: str) -> str:
    url = url.replace("https://", "").replace("http://", "").strip("/")
    return url.split("/")[0].replace("www.", "")


def fetch_page(full_url: str) -> tuple[int, str, str, list[str]]:
    r = requests.get(full_url, timeout=45, headers=UA, allow_redirects=True)
    html = r.text[:120_000]
    title = ""
    m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
    if m:
        title = m.group(1).strip()
    h1 = ""
    m = re.search(r"<h1[^>]*>([^<]+)</h1>", html, re.I)
    if m:
        h1 = m.group(1).strip()
    notes: list[str] = []
    low = html.lower()
    if r.status_code == 404 or "page not found" in title.lower():
        notes.append("branded 404 page")
    if "add to cart" in low or "add-to-cart" in low:
        notes.append("add-to-cart in HTML")
    else:
        notes.append("no add-to-cart string in HTML fetch")
    if "review" in low or "judge.me" in low or "stamped" in low:
        notes.append("review widget or review copy in HTML")
    if "destini" in low or "where to buy" in low or "where-to-buy" in low:
        notes.append("retailer/locator copy present")
    if "destini" in low:
        notes.append("Destini locator script referenced")
    # pull a few short text snippets for evidence
    for phrase in ("america's #1", "10% fresh ginger", "86 reviews", "buy online or find"):
        if phrase in low:
            notes.append(f"found phrase: {phrase!r}")
    return r.status_code, title, h1, notes
