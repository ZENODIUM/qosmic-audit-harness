"""Grounded storefront checks — required before the write phase.

Run: python eval/grounded.py --url https://{store} --out artifacts/{slug}/tech_grounded.json

Every check fails gracefully (never crash caller). PSI 429 → Warn with rate-limited detail.
Never invent Pass in the report when grounded could not verify."""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import requests

TIMEOUT = 30
PSI_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
USER_AGENT = "QosmicAuditHarness/1.0"


def _load_dotenv() -> None:
    """Load repo-root `.env` into os.environ (keys already set are not overwritten)."""
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _psi_api_key() -> str | None:
    _load_dotenv()
    return os.environ.get("PAGESPEED_API_KEY") or os.environ.get("GOOGLE_PSI_API_KEY") or None


def _warn(msg: str) -> dict[str, Any]:
    return {"status": "Warn", "detail": f"Could not verify — {msg}"}


def _pass(detail: str) -> dict[str, Any]:
    return {"status": "Pass", "detail": detail}


def _fail(detail: str) -> dict[str, Any]:
    return {"status": "Fail", "detail": detail}


def normalize_store_url(url: str) -> str:
    url = url.strip()
    if not url.startswith("http"):
        url = f"https://{url}"
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def check_ssl(host: str) -> dict[str, Any]:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        exp = cert.get("notAfter", "unknown")
        return _pass(f"Valid certificate; expires {exp}")
    except Exception as e:
        return _warn(str(e))


def check_https_redirect(origin: str) -> dict[str, Any]:
    try:
        http_url = origin.replace("https://", "http://", 1)
        r = requests.get(http_url, allow_redirects=False, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
        if r.status_code in (301, 302, 307, 308) and "https" in (r.headers.get("Location") or "").lower():
            return _pass(f"HTTP redirects to HTTPS ({r.status_code})")
        if r.status_code == 200 and origin.startswith("https"):
            return _warn("HTTP returned 200 without redirect to HTTPS")
        return _fail(f"Unexpected HTTP response: {r.status_code}")
    except Exception as e:
        return _warn(str(e))


def check_url_exists(url: str) -> dict[str, Any]:
    try:
        r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
        if r.status_code == 200:
            return _pass(f"Returns {r.status_code}")
        if r.status_code in (301, 302):
            return _pass(f"Redirects ({r.status_code})")
        return _fail(f"Returns {r.status_code}")
    except Exception as e:
        return _warn(str(e))


def fetch_psi(url: str, strategy: str) -> dict[str, Any]:
    api_key = _psi_api_key()
    params: dict[str, str] = {"url": url, "strategy": strategy}
    if api_key:
        params["key"] = api_key
    try:
        r = requests.get(
            PSI_URL,
            params=params,
            timeout=90,
            headers={"User-Agent": USER_AGENT},
        )
        if r.status_code == 429:
            detail = "rate limited"
            if not api_key:
                detail += " (set PAGESPEED_API_KEY in .env for higher quota)"
            return _warn(detail)
        r.raise_for_status()
        data = r.json()
        score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score")
        if score is None:
            return _warn("PSI response missing performance score")
        return _pass(f"{int(score * 100)}/100 on PageSpeed Insights ({strategy})")
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            return _warn("rate limited")
        return _warn(str(e))
    except Exception as e:
        if "429" in str(e):
            return _warn("rate limited")
        return _warn(str(e))


def parse_homepage_meta(origin: str) -> dict[str, Any]:
    try:
        r = requests.get(origin, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
        html = r.text[:100_000]
        title = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
        desc = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', html, re.I)
        og = re.search(r'<meta[^>]+property=["\']og:', html, re.I)
        favicon = re.search(r'<link[^>]+rel=["\'](?:shortcut )?icon', html, re.I)
        parts = []
        if title:
            parts.append("title present")
        else:
            parts.append("title missing")
        if desc:
            parts.append("meta description present")
        else:
            parts.append("meta description missing")
        if og:
            parts.append("Open Graph tags present")
        else:
            parts.append("Open Graph missing")
        if favicon:
            parts.append("favicon present")
        else:
            parts.append("favicon not found")
        status = "Pass" if title and desc else "Warn"
        return {"status": status, "detail": "; ".join(parts)}
    except Exception as e:
        return _warn(str(e))


def _run_parallel(checks: dict[str, Callable[[], dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=len(checks)) as executor:
        futures = {executor.submit(fn): name for name, fn in checks.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = _warn(str(e))
    return results


def run_grounded(url: str) -> dict[str, Any]:
    origin = normalize_store_url(url)
    parsed = urlparse(origin)
    host = parsed.hostname or ""

    fast_checks = _run_parallel(
        {
            "SSL Certificate": lambda: check_ssl(host),
            "HTTPS Redirect": lambda: check_https_redirect(origin),
            "Sitemap": lambda: check_url_exists(f"{origin}/sitemap.xml"),
            "Robots.txt": lambda: check_url_exists(f"{origin}/robots.txt"),
            "Meta Tags & Social Previews": lambda: parse_homepage_meta(origin),
        }
    )

    psi_checks = _run_parallel(
        {
            "Page Speed Mobile": lambda: fetch_psi(origin, "mobile"),
            "Page Speed Desktop": lambda: fetch_psi(origin, "desktop"),
        }
    )

    checks = {**fast_checks, **psi_checks}
    return {
        "url": origin,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Required before write phase. Saves JSON with --out."
    )
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", help="Write full result JSON (e.g. artifacts/{slug}/tech_grounded.json)")
    parser.add_argument("--psi-only", action="store_true")
    args = parser.parse_args()
    result = run_grounded(args.url)
    if args.psi_only:
        result = {
            "url": result["url"],
            "checked_at": result["checked_at"],
            "checks": {
                k: v
                for k, v in result["checks"].items()
                if k.startswith("Page Speed")
            },
        }
    text = json.dumps(result, indent=2)
    if args.out:
        from pathlib import Path

        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
