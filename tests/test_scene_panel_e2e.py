"""
SPHEREx Hunter - Playwright End-to-End Tests for Scene Collection Layer Manager
Tests:
1. Switching presets dynamically updates target metadata, evidence tier, and proper motion.
2. Selecting an epoch updates the active blink frame and canvas state.
3. Layer visibility toggles update state and trigger canvas re-renders.
4. Layer opacity slider dynamically adjusts opacity.
5. No hardcoded or static placeholder strings remain in the DOM.
"""

import time

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="module")
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto("http://127.0.0.1:8000/app/index.html", wait_until="domcontentloaded")
        time.sleep(3)
        yield page
        browser.close()


def test_no_hardcoded_placeholder_values(browser_page):
    """Verify that old static placeholders and bogus values do not exist in the DOM."""
    content = browser_page.locator("#propertiesSidebar").inner_text()

    # Old hardcoded/contradictory strings that must NOT exist
    assert "98% (Sub-stellar)" not in content
    assert "Planet X Prob" not in content
    assert "14160.00 \"/yr" not in content
    assert "10393.40 \"/yr" not in content

    # Must have single source of truth rendered content
    assert "Evidence Tier:" in content
    assert "OBSERVATION EPOCHS" in content
    assert "LAYERS" in content


def test_switching_presets_updates_panel(browser_page):
    """Verify clicking presets updates target metadata, PM, and evidence tier without reload."""
    # 1. Click Barnard's Star
    btn_barnard = browser_page.locator("button.target-btn[data-target='barnard']")
    btn_barnard.click()
    time.sleep(2)

    sidebar_text = browser_page.locator("#sceneContent").inner_text()
    assert "BARNARD" in sidebar_text.upper()
    assert "10.359" in sidebar_text or "10.36" in sidebar_text
    assert "10359 mas/yr" in sidebar_text or "10358" in sidebar_text
    assert "3134 K" in sidebar_text
    assert "M4.0V" in sidebar_text

    # 2. Click Epsilon Indi B
    btn_epsindi = browser_page.locator("button.target-btn[data-target='epsindi']")
    btn_epsindi.click()
    time.sleep(2)

    sidebar_text2 = browser_page.locator("#sceneContent").inner_text()
    assert "EPSILON INDI" in sidebar_text2.upper()
    assert "4.705" in sidebar_text2 or "4.70" in sidebar_text2
    assert "1300 K" in sidebar_text2
    assert "T1 + T6" in sidebar_text2


def test_selecting_epoch_updates_frame(browser_page):
    """Verify clicking an epoch card selects it and highlights the active row."""
    # Click WISE 0855 preset to reset
    browser_page.locator("button.target-btn[data-target='wise0855']").click()
    time.sleep(2)

    # Find epoch cards
    cards = browser_page.locator(".epoch-card")
    assert cards.count() >= 4

    # Click Epoch 2 (unWISE W1)
    card_w1 = cards.nth(1)
    card_w1.click()
    time.sleep(1)

    # Verify card border is highlighted with active class
    border_class = card_w1.get_attribute("class")
    assert "border-blender-orange" in border_class


def test_layer_visibility_toggle(browser_page):
    """Verify clicking a layer's visibility toggle updates the state."""
    # Find Gaia overlay toggle button
    btn_gaia_toggle = browser_page.locator("button[onclick=\"toggleLayerVisibility('gaia_overlay')\"]")
    assert btn_gaia_toggle.count() > 0

    # Initial state should be visible
    icon_before = btn_gaia_toggle.locator("svg").get_attribute("class")
    assert "text-blender-orange" in icon_before

    # Click to toggle off
    btn_gaia_toggle.click()
    time.sleep(1)

    # Verify icon updated to eye-off / gray
    icon_after = btn_gaia_toggle.locator("svg").get_attribute("class")
    assert "text-gray-500" in icon_after

    # Click to toggle back on
    btn_gaia_toggle.click()
    time.sleep(1)
    icon_restored = btn_gaia_toggle.locator("svg").get_attribute("class")
    assert "text-blender-orange" in icon_restored


def test_layer_opacity_slider(browser_page):
    """Verify adjusting the layer opacity slider updates the live readout label."""
    # Find Gaia overlay opacity slider
    slider = browser_page.locator("input[oninput*=\"'gaia_overlay'\"]")
    assert slider.count() > 0

    # Fill with 45%
    slider.fill("45")
    time.sleep(0.5)

    label = browser_page.locator("#opacityLabel_gaia_overlay").inner_text()
    assert label == "45%"

    # Reset back to 85%
    slider.fill("85")
    time.sleep(0.5)
    assert browser_page.locator("#opacityLabel_gaia_overlay").inner_text() == "85%"


def test_validation_modal_tab(browser_page):
    """Verify that clicking the top Validation button opens the Phase 2 Validation tab."""
    btn_val = browser_page.locator("#btnOpenValidation")
    assert btn_val.count() > 0
    btn_val.click()
    time.sleep(1)

    modal = browser_page.locator("#missionCodexModal")
    assert not modal.get_attribute("class").count("hidden")

    panel_val = browser_page.locator("#codexPanelValidation")
    assert not panel_val.get_attribute("class").count("hidden")

    text_content = panel_val.inner_text()
    assert "Detection Completeness Benchmark" in text_content
    assert "False-Positive Rate" in text_content
    assert "Known Astronomical Bodies" in text_content or "Known Solar System Bodies" in text_content

    # Close modal
    browser_page.locator("#closeCodexBtn").click()
    time.sleep(0.5)
    assert "hidden" in modal.get_attribute("class")
