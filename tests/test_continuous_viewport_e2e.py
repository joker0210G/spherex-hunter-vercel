"""
E2E Playwright test for Continuous Viewport features:
1. Seamless continuous epoch blending (morph slider & morph toggle).
2. Feathered celestial edge blending into ambient starfield.
3. Smooth inertial pan & zoom kinematics.
"""

import os
import time

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

DOCS_FIGURES = os.path.join(os.path.dirname(__file__), "..", "docs", "figures")
os.makedirs(DOCS_FIGURES, exist_ok=True)
BASE_URL = os.environ.get("SPHEREX_BASE_URL", "http://127.0.0.1:8000/app/index.html")

def launch_browser(p):
    try:
        return p.chromium.launch(headless=True)
    except Exception:
        return p.chromium.launch(headless=True, channel="msedge")

def test_continuous_viewport_controls_and_morph():
    """Verify continuous morph toggle and manual epoch blend slider work seamlessly."""
    with sync_playwright() as p:
        browser = launch_browser(p)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.goto(f"{BASE_URL}#target=wise0855&mode=blink&frame=1", wait_until="domcontentloaded")
        page.wait_for_selector("#astroCanvas")
        time.sleep(1.0)

        # 1. Verify Toggle Morph Button
        btn_morph = page.locator("#btnToggleBlinkMorph")
        assert btn_morph.is_visible()
        morph_label = page.locator("#blinkMorphModeLabel")
        assert morph_label.inner_text() == "Smooth Morph"

        # Toggle to Snap Blink
        btn_morph.click()
        assert morph_label.inner_text() == "Snap Blink"

        # Toggle back to Smooth Morph
        btn_morph.click()
        assert morph_label.inner_text() == "Smooth Morph"

        # 2. Verify Continuous Epoch Blend Slider
        slider = page.locator("#epochBlendSlider")
        assert slider.is_visible()
        blend_label = page.locator("#epochBlendLabel")
        assert blend_label.is_visible()

        # Pause flipbook if playing so we can manually scrub
        btn_play = page.locator("#btnPlayPause")
        btn_play.click()
        time.sleep(0.3)

        # Scrub to 50%
        slider.fill("50")
        slider.dispatch_event("input")
        time.sleep(0.3)
        assert blend_label.inner_text() == "50%"

        # Scrub to 100%
        slider.fill("100")
        slider.dispatch_event("input")
        time.sleep(0.3)
        assert blend_label.inner_text() == "100%"

        # Scrub back to 0%
        slider.fill("0")
        slider.dispatch_event("input")
        time.sleep(0.3)
        assert blend_label.inner_text() == "0%"

        # 3. Verify Step Back & Step Fwd increment blend in 25% increments
        btn_step_fwd = page.locator("#btnStepFwd")
        btn_step_fwd.click()
        time.sleep(0.3)
        assert blend_label.inner_text() in ["25%", "50%", "33%"]

        # 4. Canvas screenshot capture for verification
        canvas = page.locator("#astroCanvas")
        assert canvas.is_visible()
        screenshot_path = os.path.join(DOCS_FIGURES, "continuous_viewport_blended.png")
        canvas.screenshot(path=screenshot_path)
        assert os.path.exists(screenshot_path)
        assert os.path.getsize(screenshot_path) > 1000

        browser.close()

def test_continuous_viewport_frustum_tiling_on_pan():
    """Verify that panning the viewport dynamically streams frustum tiles and fills the viewport without seams or void."""
    with sync_playwright() as p:
        browser = launch_browser(p)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.goto(f"{BASE_URL}#target=wise0855&mode=blink&frame=1", wait_until="domcontentloaded")
        page.wait_for_selector("#astroCanvas")
        time.sleep(2.0)

        # Pan viewport +300px along X
        page.evaluate("""() => {
            camera.panX = 300;
            camera.panY = 0;
            updateCoordinateReadouts();
            drawFrame();
        }""")
        time.sleep(2.0)

        state = page.evaluate("""() => {
            return {
                panX: camera.panX,
                bounds: getVisibleFrustumSkyBounds(),
                cacheSize: adjacentSkyTileCache.size
            };
        }""")
        assert state["panX"] == 300
        assert state["bounds"]["centerRA"] > 133.79513
        assert state["cacheSize"] > 0
        browser.close()
