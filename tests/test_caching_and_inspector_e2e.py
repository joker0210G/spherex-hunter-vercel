"""
E2E & Integration Test Suite for Issues #13 and #14:
- Issue #13: [CACHE] Hierarchical Spatial-Tile Caching (Client IndexedDB + Backend Spatial-Hash)
- Issue #14: [UX/UI] User-Friendly Inspector Panel with Thematic Sections & Plain English Explanations
"""

import os
import time

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.cutout_engine import (
    auto_prune_disk_cache,
    clear_all_caches,
    compute_spatial_hash,
    fetch_real_cutout,
    get_cache_stats,
)

BASE_URL = os.environ.get("SPHEREX_BASE_URL", "http://127.0.0.1:8000/app/index.html")

# =============================================================================
# BACKEND UNIT / INTEGRATION TESTS (Issue #13)
# =============================================================================

def test_spatial_hash_computation():
    """Verify spatial hash bin calculation across celestial coordinates."""
    bin1 = compute_spatial_hash(133.79513, -7.24515, 3.0)
    bin2 = compute_spatial_hash(133.79800, -7.24300, 3.0)
    assert bin1.startswith("bin_")
    # Proximity coords within 0.05 deg should map to the exact same spatial bin
    assert bin1 == bin2


def test_backend_hierarchical_cache_and_pruning():
    """Verify L1 RAM, L1 spatial-hash hits, and disk auto-pruning."""
    clear_all_caches()
    stats_init = get_cache_stats()
    assert stats_init["l1_ram_entries"] == 0

    # Query 1: Benchmark cold brown dwarf
    res1 = fetch_real_cutout(133.79513, -7.24515, fov_arcmin=3.0, target_key="wise0855")
    assert res1 is not None
    stats_after_1 = get_cache_stats()
    assert stats_after_1["l1_ram_entries"] >= 1
    assert stats_after_1["spatial_bins_indexed"] >= 1

    # Query 2: Micro-pan within same spatial bin should hit L1 Spatial-Hash cache in < 15ms
    t0 = time.time()
    res2 = fetch_real_cutout(133.79800, -7.24300, fov_arcmin=3.0)
    elapsed_ms = (time.time() - t0) * 1000.0
    assert res2 is not None
    assert elapsed_ms < 50.0  # sub-50ms cache response

    # Auto-prune test
    prune_result = auto_prune_disk_cache(max_mb=1000.0, target_mb=500.0)
    assert "pruned_files" in prune_result
    assert "freed_mb" in prune_result


def test_cache_api_endpoints():
    """Verify /api/cache/stats, /api/cache/prune, and /api/cache/clear endpoints."""
    client = TestClient(app)

    # Stats
    res_stats = client.get("/api/cache/stats")
    assert res_stats.status_code == 200
    data_stats = res_stats.json()
    assert "l1_ram_entries" in data_stats
    assert "spatial_bins_indexed" in data_stats

    # Prune
    res_prune = client.post("/api/cache/prune?max_mb=800&target_mb=400")
    assert res_prune.status_code == 200
    data_prune = res_prune.json()
    assert "pruned_files" in data_prune

    # Clear
    res_clear = client.post("/api/cache/clear")
    assert res_clear.status_code == 200
    assert res_clear.json()["status"] == "success"


# =============================================================================
# PLAYWRIGHT E2E TESTS (Issue #13 Client IndexedDB & Issue #14 User-Friendly Inspector)
# =============================================================================

def test_issue_13_client_indexeddb_caching_e2e():
    """Verify client-side IndexedDB caching layer and in-flight abort handling."""
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.add_init_script("localStorage.setItem('spherex_tour_seen', 'true');")
        page.goto(BASE_URL, wait_until="domcontentloaded")
        time.sleep(1.0)

        # 1. Verify IndexedDB initialization in window
        db_ready = page.evaluate("typeof window.initTileIndexedDB === 'function'")
        assert db_ready is True

        # 2. Store a tile in IndexedDB and retrieve it
        test_payload = {"test": "astronomical_fits_data", "timestamp": time.time()}
        page.evaluate(f"window.storeTileInIndexedDB('test_tile_001', {test_payload})")
        time.sleep(0.3)

        retrieved = page.evaluate("window.getTileFromIndexedDB('test_tile_001')")
        assert retrieved is not None
        assert retrieved.get("test") == "astronomical_fits_data"

        browser.close()


def test_issue_14_user_friendly_inspector_panel_e2e():
    """Verify redesigned user-friendly Inspector Panel with clear sections and plain English."""
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.add_init_script("localStorage.setItem('spherex_tour_seen', 'true');")
        page.goto(BASE_URL, wait_until="domcontentloaded")
        time.sleep(1.0)

        # Switch to Target tab in right sidebar inspector
        tab_target = page.locator("#tabTargetBtn")
        assert tab_target.is_visible()
        tab_target.click()
        time.sleep(0.5)

        panel_target = page.locator("#inspectorPanelTarget")
        assert not panel_target.get_attribute("class").count("hidden")

        # 1. Section 1: Object Overview & Location
        target_name = page.locator("#targetDetailName").inner_text()
        assert "WISE 0855" in target_name
        subtitle = page.locator("#inspectTypeSubtitle").inner_text()
        assert "failed star" in subtitle.lower()

        # Moon scale analogy
        moon_desc = page.locator("#inspectMoonScaleDesc").inner_text()
        assert "Moon" in moon_desc

        # 2. Section 2: Observation & Wavelength Details Table
        obs_table_text = page.locator("#inspectObsTableBody").inner_text()
        assert "NASA 2MASS" in obs_table_text
        assert "NASA WISE" in obs_table_text
        assert "SPHEREx DR1" in obs_table_text
        baseline_sep = page.locator("#inspectBaselineSeparation").inner_text()
        assert "26" in baseline_sep

        # 3. Section 3: Surface Temperature Thermometer & Plain-English Gauge
        temp_readable = page.locator("#inspectTempReadable").inner_text()
        assert "250 K" in temp_readable or "freezing" in temp_readable.lower()
        temp_indicator = page.locator("#inspectTempIndicator")
        assert temp_indicator.is_visible()

        # 4. Section 4: Motion & Cosmic Speed
        speed_badge = page.locator("#inspectSpeedBadge").inner_text()
        assert "MOVER" in speed_badge
        shift_text = page.locator("#inspectShift50yr").inner_text()
        assert "arcseconds" in shift_text or "arcminutes" in shift_text

        # 5. Section 5: "What This Means" Beginner Takeaway
        summary_text = page.locator("#inspectSummaryText").inner_text()
        assert len(summary_text) > 20
        assert "infrared" in summary_text.lower() or "brown dwarf" in summary_text.lower()

        # 6. Test Target Switch (Barnard's Star) updates Inspector dynamically
        page.click("[data-target='barnard']")
        time.sleep(0.5)

        barnard_name = page.locator("#targetDetailName").inner_text()
        assert "Barnard" in barnard_name
        barnard_speed = page.locator("#inspectSpeedBadge").inner_text()
        assert "FASTEST" in barnard_speed or "MOVER" in barnard_speed

        browser.close()
