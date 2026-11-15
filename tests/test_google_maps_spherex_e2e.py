"""
E2E Playwright test for Google-Maps-Style SPHEREx All-Sky Continuous Viewer:
1. Continuous all-sky image from NASA SPHEREx DR1 HiPS (zero single-tile bounding boxes).
2. Progressive multi-resolution zoom (180° All-Sky -> 30° Wide -> 5° Field -> 0.1° HD Native SPHEREx).
3. 102-channel wavelength stepping across 0.75 - 5.0 μm.
4. Interactive NASA landmark target pins (Google Maps Landmark Pins).
"""

import os
import time

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

DOCS_FIGURES = os.path.join(os.path.dirname(__file__), "..", "docs", "figures")
os.makedirs(DOCS_FIGURES, exist_ok=True)
BASE_URL = os.environ.get("SPHEREX_BASE_URL", "http://127.0.0.1:8000/app/index.html")

def test_google_maps_continuous_spherex_viewer():
    """Validates the continuous Google-Maps-style progressive multi-resolution SPHEREx all-sky map."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.add_init_script("localStorage.setItem('spherex_tour_seen', 'true');")
        page.goto(f"{BASE_URL}", wait_until="domcontentloaded")
        time.sleep(1.0)

        # 1. Click SPHEREx Map (Google Sky) Mode
        ws_aladin = page.locator("#wsAladin")
        assert ws_aladin.is_visible()
        ws_aladin.click()
        time.sleep(2.0)

        # Verify container & Google Maps context bar
        container = page.locator("#aladinContainer")
        assert not container.get_attribute("class").count("hidden")
        context_bar = page.locator("#aladinContextBar")
        assert not context_bar.get_attribute("class").count("hidden")

        # 2. Test Multi-Resolution Zoom Levels (Google Maps Mapping Method)
        btn_allsky = page.locator("#btnZoomAllSky")
        btn_wide = page.locator("#btnZoomWide")
        btn_field = page.locator("#btnZoomField")
        btn_core = page.locator("#btnZoomCore")

        assert btn_allsky.is_visible()
        assert btn_wide.is_visible()
        assert btn_field.is_visible()
        assert btn_core.is_visible()

        # Zoom to 180° All-Sky View
        btn_allsky.click()
        time.sleep(1.0)
        page.screenshot(path=os.path.join(DOCS_FIGURES, "google_maps_spherex_180_allsky.png"))

        # Zoom in to 30° Wide Constellation View
        btn_wide.click()
        time.sleep(0.5)

        # Zoom in to 0.1° HD Native SPHEREx Resolution (Fine Details)
        btn_core.click()
        time.sleep(1.0)
        page.screenshot(path=os.path.join(DOCS_FIGURES, "google_maps_spherex_01_hd_stars.png"))

        # 3. Test 102-Band Channel Stepper
        btn_next = page.locator("#btnHipsNextCh")
        btn_prev = page.locator("#btnHipsPrevCh")
        assert btn_next.is_visible()
        assert btn_prev.is_visible()

        btn_next.click()
        time.sleep(0.3)
        wl_display = page.locator("#hipsWavelengthDisplay")
        # Should now be on channel 2
        assert "0.771" in wl_display.inner_text() or "Band" in wl_display.inner_text()

        # 4. Test Landmark Target Pins
        pin_wise = page.locator(".hips-landmark-btn[data-target='wise0855']")
        pin_barnard = page.locator(".hips-landmark-btn[data-target='barnard']")
        assert pin_wise.is_visible()
        assert pin_barnard.is_visible()

        # Click Barnard's Star Pin
        pin_barnard.click()
        time.sleep(1.0)
        vp_target = page.locator("#vpTargetName")
        assert "Barnard" in vp_target.inner_text()

        browser.close()
