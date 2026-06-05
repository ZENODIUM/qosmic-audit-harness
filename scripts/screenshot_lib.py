#!/usr/bin/env python3
"""Shared Playwright screenshot capture."""

from __future__ import annotations

from pathlib import Path


def _ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright

        return sync_playwright
    except ImportError as e:
        raise RuntimeError(
            "Playwright not installed. Run: pip install playwright && playwright install chromium"
        ) from e


def _screenshot_page(
    page,
    out: Path,
    *,
    selector: str | None = None,
    full_page: bool = False,
) -> None:
    if selector:
        loc = page.locator(selector).first
        loc.wait_for(state="visible", timeout=15_000)
        loc.scroll_into_view_if_needed()
        loc.screenshot(path=str(out))
    elif full_page:
        page.screenshot(path=str(out), full_page=True)
    else:
        page.screenshot(path=str(out))


def _is_blank_png(path: Path, min_bytes: int = 5000) -> bool:
    if not path.is_file():
        return True
    return path.stat().st_size < min_bytes


def _goto_and_shot(
    page,
    url: str,
    out: Path,
    *,
    wait_until: str,
    wait_ms: int,
    full_page: bool,
    selector: str | None,
    timeout: int,
) -> None:
    page.goto(url, wait_until=wait_until, timeout=timeout)
    page.wait_for_timeout(wait_ms)
    _screenshot_page(page, out, selector=selector, full_page=full_page)


def capture_screenshot(
    url: str,
    out: Path,
    *,
    selector: str | None = None,
    full_page: bool = False,
    wait_ms: int = 2000,
    wait_until: str = "domcontentloaded",
) -> None:
    sync_playwright = _ensure_playwright()
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        try:
            _goto_and_shot(
                page,
                url,
                out,
                wait_until=wait_until,
                wait_ms=wait_ms,
                full_page=full_page,
                selector=selector,
                timeout=90_000,
            )
            if full_page and not selector and _is_blank_png(out):
                _goto_and_shot(
                    page,
                    url,
                    out,
                    wait_until="load",
                    wait_ms=wait_ms,
                    full_page=full_page,
                    selector=selector,
                    timeout=90_000,
                )
        finally:
            browser.close()


def capture_pages(
    pages: list[tuple[str, Path]],
    *,
    full_page: bool = True,
    wait_ms: int = 2000,
    wait_until: str = "domcontentloaded",
) -> list[Path]:
    """Capture multiple URLs in one browser session."""
    if not pages:
        return []

    sync_playwright = _ensure_playwright()
    captured: list[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        try:
            for url, out in pages:
                out = Path(out)
                out.parent.mkdir(parents=True, exist_ok=True)
                _goto_and_shot(
                    page,
                    url,
                    out,
                    wait_until=wait_until,
                    wait_ms=wait_ms,
                    full_page=full_page,
                    selector=None,
                    timeout=90_000,
                )
                if full_page and _is_blank_png(out):
                    _goto_and_shot(
                        page,
                        url,
                        out,
                        wait_until="load",
                        wait_ms=wait_ms,
                        full_page=full_page,
                        selector=None,
                        timeout=90_000,
                    )
                captured.append(out)
        finally:
            browser.close()

    return captured
