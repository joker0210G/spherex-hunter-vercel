"""
SPHEREx Hunter - Playwright E2E Tests for SPHEREx DR1 HiPS Context Layer.
Tests:
1. Aladin Lite viewer switch and DR1 HiPS context layer appearance.
2. 102-channel selector population and channel switching.
3. Graceful failure fallback and offline mode handling.
4. UI honesty in spectroscopy: non-simultaneous observation caveat and dates.
5. Coordinate click and search position scene loading.
"""

import os
import time

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

FIGURES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


@pytest.fixture(scope="module")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        pg = context.new_page()
        pg.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        pg.goto("http://127.0.0.1:8000/app/index.html", wait_until="domcontentloaded")
        time.sleep(3)
        yield pg
        browser.close()


def test_aladin_hips_layer_appears(page):
    """Verify switching to Aladin mode displays DR1 HiPS context bar and mandatory disclaimer."""
    ws_aladin = page.locator("#wsAladin")
    assert ws_aladin.is_visible()
    ws_aladin.click()
    time.sleep(2)

    # Verify containers are visible
    aladin_container = page.locator("#aladinContainer")
    assert not aladin_container.get_attribute("class").count("hidden")

    context_bar = page.locator("#aladinContextBar")
    assert not context_bar.get_attribute("class").count("hidden")

    # Verify mandatory honesty disclaimer label
    notice = page.locator("#aladinContextNotice")
    assert "DR1 all-sky mosaic: context only, not used for detection" in notice.inner_text()

    # Capture screenshot
    page.screenshot(path=os.path.join(FIGURES_DIR, "aladin_dr1_hips.png"))


def test_hips_channel_selector_102_channels(page):
    """Verify 102 channels are loaded and channel switching dynamically updates slice and label."""
    channel_select = page.locator("#hipsChannelSelect")
    assert channel_select.is_visible()

    # Verify exactly 102 options exist
    options = channel_select.locator("option")
    assert options.count() == 102

    # Verify first option (Ch 1) and mid option (Ch 86)
    assert "0.753" in options.nth(0).inner_text()
    assert "4.435" in options.nth(85).inner_text()

    # Switch to Channel 86 (Band 6, 4.435 um)
    channel_select.select_option("86")
    time.sleep(1)

    wl_display = page.locator("#hipsWavelengthDisplay")
    assert "4.435" in wl_display.inner_text()
    assert "Band 6" in wl_display.inner_text()

    # Capture screenshot
    page.screenshot(path=os.path.join(FIGURES_DIR, "aladin_dr1_channel_switch.png"))


def test_hips_failure_fallback_and_offline(page):
    """Verify graceful fallback handling when HiPS service is offline or unreachable."""
    # Trigger fallback function in the page context
    page.evaluate("applyHiPSFallback('Simulated offline test')")
    time.sleep(0.5)

    status_badge = page.locator("#aladinLayerStatus")
    assert "Fallback" in status_badge.inner_text()

    alert_box = page.locator("#aladinFallbackAlert")
    assert not alert_box.get_attribute("class").count("hidden")
    assert "fallback active" in page.locator("#aladinFallbackMsg").inner_text()

    # Capture screenshot
    page.screenshot(path=os.path.join(FIGURES_DIR, "aladin_dr1_fallback.png"))


def test_spectrum_ui_honesty_and_caveat(page):
    """Verify UI honesty: non-simultaneous observation caveat and honest spectrum states."""
    ws_spec = page.locator("#wsSpec")
    ws_spec.click()
    time.sleep(1)

    # Open bottom spectrum dock tab
    dock_spec_tab = page.locator("#dockTabSpectrum")
    if dock_spec_tab.is_visible():
        dock_spec_tab.click()
        time.sleep(0.5)

    # Check non-simultaneous notice
    notice = page.locator("#spectrumNonSimultaneousNotice")
    assert notice.is_visible()
    text = notice.inner_text()
    assert "not simultaneous for variable stars" in text
    assert "RW Aurigae" in text or "R Draconis" in text

    # Capture screenshot
    page.screenshot(path=os.path.join(FIGURES_DIR, "spectrum_honesty_notice.png"))


def test_click_and_search_position_loads_scene(page):
    """Verify loading scene by coordinates correctly updates camera and target state."""
    # Switch to Barnard's Star coordinates via JS loadSceneForPosition
    page.evaluate("loadSceneForPosition(269.45208, 4.69339)")
    time.sleep(2)

    # Verify coordinate readout updated to Barnard's Star
    ra_readout = page.locator("#vpRA").inner_text()
    assert "269.45" in ra_readout
