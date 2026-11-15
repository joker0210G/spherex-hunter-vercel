"""
E2E Playwright test suite for Issues #9, #10, and #12:
- Issue #9: [WEB] Command Palette Ctrl+K for Rapid Discovery & Scientific Triage
- Issue #10: [VIEWPORT] Continuous Raytracing-like Sky Tiling & Adaptive LOD Zoom Engine
- Issue #12: [WEB] Universal Sky Region Share Modal & Deep-Link Parameter Hub
"""

import os
import time

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("SPHEREX_BASE_URL", "http://127.0.0.1:8000/app/index.html")

def test_issue_9_command_palette_ctrl_k():
    """Verify Command Palette indexing, categories, natural-language aliases, and keyboard navigation."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.add_init_script("localStorage.setItem('spherex_tour_seen', 'true');")
        page.goto(BASE_URL, wait_until="domcontentloaded")
        time.sleep(1.0)

        # 1. Header trigger button
        btn_palette = page.locator("#btnOpenCommandPalette")
        assert btn_palette.is_visible()
        btn_palette.click()
        time.sleep(0.3)

        modal = page.locator("#commandPaletteModal")
        assert not modal.get_attribute("class").count("hidden")

        # 2. Check that at least 20 items are indexed across groups
        item_count = page.evaluate("document.querySelectorAll('#commandPaletteList .palette-item').length")
        assert item_count >= 20, f"Expected >= 20 indexed commands, got {item_count}"

        # 3. Natural language alias search: 'cold brown dwarf' -> WISE 0855
        input_palette = page.locator("#commandPaletteInput")
        input_palette.fill("cold brown dwarf")
        time.sleep(0.2)
        filtered_text = page.locator("#commandPaletteList").inner_text()
        assert "WISE 0855-0714" in filtered_text

        # 4. Keyboard Arrow Down + Enter navigation
        input_palette.press("ArrowDown")
        input_palette.press("Enter")
        time.sleep(0.5)
        # Modal should be closed
        assert modal.get_attribute("class").count("hidden")

        # 5. Open via Ctrl+K keyboard shortcut
        page.keyboard.press("Control+k")
        time.sleep(0.3)
        assert not modal.get_attribute("class").count("hidden")

        # 6. Search view mode alias: 'subtraction' -> Difference
        input_palette.fill("subtraction")
        time.sleep(0.2)
        filtered_diff = page.locator("#commandPaletteList").inner_text()
        assert "Difference Imaging" in filtered_diff

        # Execute difference view
        input_palette.press("Enter")
        time.sleep(0.5)
        assert modal.get_attribute("class").count("hidden")

        # Verify difference button is active
        ws_diff = page.locator("#wsDiff")
        assert "blender-btn-active" in ws_diff.get_attribute("class")

        browser.close()


def test_issue_10_frustum_raycasting_and_bounds():
    """Verify frustum raycasting engine (canvasToSkyCoordinates and getVisibleFrustumSkyBounds)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.add_init_script("localStorage.setItem('spherex_tour_seen', 'true');")
        page.goto(BASE_URL, wait_until="domcontentloaded")
        time.sleep(1.0)

        # 1. Test canvasToSkyCoordinates
        coords_center = page.evaluate("window.canvasToSkyCoordinates(400, 300)")
        assert "ra" in coords_center and "dec" in coords_center
        assert 0.0 <= coords_center["ra"] <= 360.0
        assert -90.0 <= coords_center["dec"] <= 90.0

        # 2. Test getVisibleFrustumSkyBounds
        bounds = page.evaluate("window.getVisibleFrustumSkyBounds()")
        assert "minRA" in bounds and "maxRA" in bounds
        assert "minDec" in bounds and "maxDec" in bounds
        assert "arcsecPerPixel" in bounds
        assert bounds["arcsecPerPixel"] > 0
        assert bounds["minRA"] <= bounds["maxRA"]
        assert bounds["minDec"] <= bounds["maxDec"]

        browser.close()


def test_issue_12_universal_share_modal_and_hydration():
    """Verify universal share modal, clipboard copy, telemetry brief, and URL parameter hydration."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.add_init_script("localStorage.setItem('spherex_tour_seen', 'true');")
        page.goto(BASE_URL, wait_until="domcontentloaded")
        time.sleep(1.0)

        # 1. Header Share button
        btn_share = page.locator("#btnShareModal")
        assert btn_share.is_visible()
        btn_share.click()
        time.sleep(0.3)

        share_modal = page.locator("#shareModal")
        assert not share_modal.get_attribute("class").count("hidden")

        # 2. Check modal fields
        ra_text = page.locator("#shareRA").inner_text()
        dec_text = page.locator("#shareDec").inner_text()
        url_val = page.locator("#shareUrlInput").input_value()
        telemetry_val = page.locator("#shareTelemetryText").input_value()

        assert "°" in ra_text
        assert "°" in dec_text
        assert "ra=" in url_val and "dec=" in url_val and "fov=" in url_val
        assert "SPHEREx Hunter Astrophysical Target Brief" in telemetry_val
        assert "102 NASA SPHEREx LVF Bands" in telemetry_val

        # 3. Test Copy Buttons
        page.locator("#btnCopyShareUrl").click()
        page.locator("#btnCopyTelemetrySnippet").click()
        time.sleep(0.2)

        # 4. Close Share modal
        page.locator("#closeShareModalBtn").click()
        time.sleep(0.3)
        assert share_modal.get_attribute("class").count("hidden")

        # 5. Test Deep-Link Hydration
        deep_link = f"{BASE_URL}?ra=269.45208&dec=4.69339&fov=5.0&mode=diff&target=barnard&gaia=false"
        page.goto(deep_link, wait_until="domcontentloaded")
        time.sleep(1.0)

        # Verify difference mode hydrated
        ws_diff = page.locator("#wsDiff")
        assert "blender-btn-active" in ws_diff.get_attribute("class")

        # Verify coordinates / target loaded
        ra_input_val = page.locator("#inputRA").input_value()
        assert "269" in ra_input_val or "Barnard" in page.locator("#propTarget").inner_text()

        browser.close()
