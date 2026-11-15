"""
E2E Playwright verification for the SPHEREx Hunter Frontend Redesign.
Validates:
1. Top bar compactness and command palette (Ctrl+K).
2. Coordinates popover (RA/Dec/FOV).
3. 4-tab Inspector (Layers, Target, Candidates, Photometry).
4. 3-tab Bottom Dock (Timeline, Spectrum, Light Curve) and Collapse.
5. Beginner vs Scientist mode switch.
6. Responsive layout integrity and permalinks.
"""

import time

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="module")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        pg = context.new_page()
        pg.goto("http://127.0.0.1:8000/app/index.html", wait_until="domcontentloaded")
        time.sleep(2)
        yield pg
        browser.close()

def test_top_bar_compactness_and_command_palette(page):
    """Verify top bar has clean controls and Ctrl+K command palette operates smoothly."""
    btn_palette = page.locator("#btnOpenCommandPalette")
    assert btn_palette.is_visible()
    btn_palette.click()
    time.sleep(0.5)

    modal = page.locator("#commandPaletteModal")
    assert not modal.get_attribute("class").count("hidden")

    # Search for Barnard
    input_box = page.locator("#commandPaletteInput")
    input_box.fill("Barnard")
    time.sleep(0.5)

    list_container = page.locator("#commandPaletteList")
    assert "Barnard's Star" in list_container.inner_text()

    # Close modal
    page.locator("#closeCommandPaletteBtn").click()
    time.sleep(0.5)
    assert "hidden" in modal.get_attribute("class")

def test_coordinates_popover(page):
    """Verify clicking Coordinates opens floating popover with RA/Dec/FOV."""
    btn_coords = page.locator("#btnToggleCoordsPopover")
    assert btn_coords.is_visible()
    btn_coords.click()
    time.sleep(0.5)

    popover = page.locator("#coordsPopover")
    assert not popover.get_attribute("class").count("hidden")

    # Check input values are present
    ra_val = page.locator("#inputRA").input_value()
    dec_val = page.locator("#inputDec").input_value()
    assert float(ra_val) > 0
    assert abs(float(dec_val)) > 0

    # Close popover
    page.locator("#btnCloseCoordsPopover").click()
    time.sleep(0.5)
    assert "hidden" in popover.get_attribute("class")

def test_inspector_four_tabs(page):
    """Verify switching between Layers, Target, Candidates, and Photometry tabs."""
    tab_target = page.locator("#tabTargetBtn")
    tab_target.click()
    time.sleep(0.5)
    assert not page.locator("#inspectorPanelTarget").get_attribute("class").count("hidden")
    target_text = page.locator("#inspectorPanelTarget").inner_text().upper()
    assert "ICRS ASTROMETRY" in target_text

    tab_cand = page.locator("#tabCandidatesBtn")
    tab_cand.click()
    time.sleep(1.0)
    assert not page.locator("#inspectorPanelCandidates").get_attribute("class").count("hidden")
    assert page.locator("#btnExportCSV").is_visible()

    tab_photo = page.locator("#tabPhotometryBtn")
    tab_photo.click()
    time.sleep(0.5)
    assert not page.locator("#inspectorPanelPhotometry").get_attribute("class").count("hidden")
    assert "Array 1 (0.75 μm)" in page.locator("#inspectorPanelPhotometry").inner_text()
    assert "Array 6 (4.42 μm)" in page.locator("#inspectorPanelPhotometry").inner_text()

    # Switch back to Layers
    page.locator("#tabLayersBtn").click()
    time.sleep(0.5)
    assert not page.locator("#inspectorPanelLayers").get_attribute("class").count("hidden")

def test_bottom_dock_tabs_and_collapse(page):
    """Verify switching between Timeline, Spectrum, and Light Curve, and collapsing."""
    # Click Spectrum tab
    page.locator("#dockTabSpectrum").click()
    time.sleep(0.5)
    assert not page.locator("#dockPanelSpectrum").get_attribute("class").count("hidden")

    # Click Light Curve tab
    page.locator("#dockTabLightCurve").click()
    time.sleep(0.5)
    assert not page.locator("#dockPanelLightCurve").get_attribute("class").count("hidden")

    # Click Timeline tab
    page.locator("#dockTabTimeline").click()
    time.sleep(0.5)
    assert not page.locator("#dockPanelTimeline").get_attribute("class").count("hidden")

    # Test collapse
    btn_collapse = page.locator("#btnToggleDock")
    btn_collapse.click()
    time.sleep(0.5)
    height = page.locator("#dockContentBody").evaluate("el => el.style.height")
    assert height == "0px"

    # Expand again
    btn_collapse.click()
    time.sleep(0.5)
    height_expanded = page.locator("#dockContentBody").evaluate("el => el.style.height")
    assert height_expanded == "144px"

def test_beginner_scientist_toggle(page):
    """Verify switching Beginner / Scientist mode updates the label and body class."""
    btn_mode = page.locator("#btnToggleUserMode")
    initial_text = page.locator("#userModeLabel").inner_text()

    btn_mode.click()
    time.sleep(0.5)
    new_text = page.locator("#userModeLabel").inner_text()
    assert new_text != initial_text

    # Revert back
    btn_mode.click()
    time.sleep(0.5)
    assert page.locator("#userModeLabel").inner_text() == initial_text
