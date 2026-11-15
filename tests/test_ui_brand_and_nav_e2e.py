import os

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright

DOCS_FIGURES = os.path.join(os.path.dirname(__file__), "..", "docs", "figures")
os.makedirs(DOCS_FIGURES, exist_ok=True)

def test_brand_logo_and_mission_explainer():
    """Validates Issue #5: Custom SVG Logo, Branding, and Mission Explainer Badge."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        # Set localStorage to prevent auto-popping modal during initial load
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.goto("http://127.0.0.1:8000/app/", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        # 1. Logo image in brand link
        logo_img = page.locator("#brandLogoLink img")
        assert logo_img.is_visible()
        src = logo_img.get_attribute("src")
        assert "logo.svg" in src

        # 2. Mission Explainer badge
        mission_btn = page.locator("#btnMissionExplainer")
        title = mission_btn.get_attribute("title")
        assert "Planet Nine" in title
        assert "SPHEREx" in title

        # Screenshot header branding
        page.locator("header").screenshot(path=os.path.join(DOCS_FIGURES, "topbar_brand_logo.png"))
        browser.close()

def test_onboarding_modal_interactive_tour():
    """Validates Issue #5: 5-Step Interactive Guided Tour, Step Navigation, and Persistence."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto("http://127.0.0.1:8000/app/", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        # 1. Onboarding modal can be opened via Tour button
        modal = page.locator("#onboardingModal")
        if not modal.is_visible():
            tour_btn = page.locator("#btnOpenOnboarding, #btnOpenOnboardingTour").first
            tour_btn.click()
            page.wait_for_timeout(300)

        assert modal.is_visible()
        badge = page.locator("#onboardingStepBadge")
        assert "Step 1 of 3" in badge.inner_text()
        assert page.locator("#btnTourQuickStart").is_visible()

        # Screenshot Step 1
        modal.screenshot(path=os.path.join(DOCS_FIGURES, "onboarding_step1_mission.png"))

        # Step 2: Click Next
        page.locator("#btnTourNext").click()
        page.wait_for_timeout(200)
        assert "Step 2 of 3" in badge.inner_text()
        assert page.locator(".tour-slide[data-step='2']").is_visible()

        # Step 3: Click Next
        page.locator("#btnTourNext").click()
        page.wait_for_timeout(200)
        assert "Step 3 of 3" in badge.inner_text()
        assert page.locator(".tour-slide[data-step='3']").is_visible()
        modal.screenshot(path=os.path.join(DOCS_FIGURES, "onboarding_step3_discoveries.png"))

        # Previous button
        page.locator("#btnTourPrev").click()
        page.wait_for_timeout(200)
        assert "Step 2 of 3" in badge.inner_text()

        # Close modal
        page.locator("#btnCloseOnboardingModal").click()
        page.wait_for_timeout(300)
        assert not modal.is_visible()

        browser.close()

def test_sky_helper_and_celestial_landmarks():
    """Validates Issue #6: Sky Helper popover, coordinate format guide, and landmark selection."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.goto("http://127.0.0.1:8000/app/", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        # 1. Open Sky Helper Popover
        sky_btn = page.locator("#btnSkyHelper")
        sky_btn.click()
        page.wait_for_timeout(300)

        helper = page.locator("#skyHelperPopover")
        assert helper.is_visible()
        assert "Accepted Coordinate Formats" in helper.inner_text()

        # Capture screenshot of Sky Helper Popover
        helper.screenshot(path=os.path.join(DOCS_FIGURES, "sky_helper_popover.png"))

        # 2. Click Barnard's Star landmark in helper
        barnard_landmark = page.locator(".landmark-btn[data-ra='269.45208']")
        barnard_landmark.click()
        page.wait_for_timeout(500)

        # Popover should close and coordinates should update
        assert not helper.is_visible()
        input_ra = page.locator("#inputRA").input_value()
        assert "269.452" in input_ra

        browser.close()

def test_coordinate_validation_and_fov_scale():
    """Validates Issue #6: Dynamic coordinate validation, hints, and celestial scale FOV options."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.goto("http://127.0.0.1:8000/app/", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        # 1. Open Coordinates Popover
        page.locator("#btnToggleCoordsPopover").click()
        page.wait_for_timeout(300)

        coords_pop = page.locator("#coordsPopover")
        assert coords_pop.is_visible()

        # 2. Check FOV scale options
        fov_select = page.locator("#selectFOV")
        fov_options = fov_select.locator("option").all_inner_texts()
        assert any("1/10th Moon" in opt for opt in fov_options)
        assert any("Micro-Arcsec Dipoles" in opt for opt in fov_options)
        assert any("Half Moon Width" in opt for opt in fov_options)

        # 3. Test RA Validation (Out of bounds)
        input_ra = page.locator("#inputRA")
        input_ra.fill("450.0")
        page.wait_for_timeout(150)
        ra_hint = page.locator("#raValidationHint").inner_text()
        assert "Must be 0° to 360°" in ra_hint

        # Test RA Validation (Valid)
        input_ra.fill("133.795")
        page.wait_for_timeout(150)
        ra_hint_valid = page.locator("#raValidationHint").inner_text()
        assert "Valid" in ra_hint_valid

        # 4. Test Dec Validation (Out of bounds)
        input_dec = page.locator("#inputDec")
        input_dec.fill("-95.5")
        page.wait_for_timeout(150)
        dec_hint = page.locator("#decValidationHint").inner_text()
        assert "Must be -90° to +90°" in dec_hint

        # Test Dec Validation (Valid)
        input_dec.fill("-7.245")
        page.wait_for_timeout(150)
        dec_hint_valid = page.locator("#decValidationHint").inner_text()
        assert "Valid" in dec_hint_valid

        # Screenshot of coordinates card with validation
        coords_pop.screenshot(path=os.path.join(DOCS_FIGURES, "coords_popover_validation.png"))

        browser.close()
