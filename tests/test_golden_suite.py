"""
NASA Space Apps Challenge 2026 - Golden Verification Suite
Validates the 5 NASA Benchmark Targets, WCS Astrometry, Difference Imaging,
and 102-Band Infrared Spectrophotometry against the Spec-Kit requirements.
"""
import os
import time

try:
    import pytest
except ImportError:
    class _DummyMark:
        @staticmethod
        def parametrize(*args, **kwargs):
            def decorator(fn): return fn
            return decorator
    class pytest:  # noqa: N801
        mark = _DummyMark()
from astropy.coordinates import SkyCoord

from backend.services.catalog_engine import (
    _CIRCUIT_STATE_PATH,
    _load_circuit_state,
    _save_circuit_state,
    is_esa_gaia_available,
    is_irsa_tap_available,
    trip_esa_gaia_circuit,
    trip_irsa_tap_circuit,
)
from backend.services.cutout_engine import fetch_real_cutout, get_102_band_spectrum

BENCHMARKS = [
    ("wise0855", 133.79513, -7.24515, "WISE 0855-0714"),
    ("barnard", 269.4521, 4.6934, "Barnard's Star"),
    ("epsindi", 331.0438, -56.7827, "Epsilon Indi B"),
    ("rwaur", 76.9564, 30.4014, "RW Aurigae"),
    ("rdraconis", 248.1676, 66.7551, "R Draconis"),
]

@pytest.mark.parametrize("target_key,ra,dec,expected_name", BENCHMARKS)
def test_nasa_benchmark_cutouts(target_key, ra, dec, expected_name):
    bundle = fetch_real_cutout(ra=ra, dec=dec, target_key=target_key)
    assert bundle["status"] == "success"
    assert expected_name in bundle["target"]
    assert len(bundle["epochs"]) == 2
    assert "image_data" in bundle["difference_image"]
    assert len(bundle["difference_image"]["image_data"]) > 100

def test_sexagesimal_and_decimal_parsing():
    # Decimal
    bundle_dec = fetch_real_cutout(ra=133.79513, dec=-7.24515)
    assert bundle_dec["status"] == "success"
    assert abs(bundle_dec["coordinates"]["ra_deg"] - 133.79513) < 0.001

    # Sexagesimal parse via Astropy
    coord = SkyCoord("08h55m10.831s", "-07d14m42.53s", frame="icrs")
    bundle_sex = fetch_real_cutout(ra=coord.ra.deg, dec=coord.dec.deg)
    assert bundle_sex["status"] == "success"
    assert abs(bundle_sex["coordinates"]["ra_deg"] - 133.79513) < 0.001

def test_102_band_spectroscopy():
    spec = get_102_band_spectrum(133.79513, -7.24515, "wise0855")
    assert len(spec["wavelengths_microns"]) == 102
    assert len(spec["flux_microjanskys"]) == 102
    assert len(spec["detector_arrays"]) == 6
    assert len(spec["detected_molecules"]) >= 3
    # Verify range 0.75 um to 5.00 um
    assert spec["wavelengths_microns"][0] == 0.75
    assert spec["wavelengths_microns"][-1] == 5.00

def test_gaia_dr3_astrometry():
    from backend.services.gaia_service import query_gaia_dr3
    res = query_gaia_dr3(269.45208, 4.69339, radius_arcmin=3.0)
    assert res["status"] == "success"
    assert res["catalog"] == "Gaia Data Release 3 (Gaia DR3)"
    assert res["matched_count"] > 0
    # Barnard's Star is the brightest/fastest source with PM > 10,000 mas/yr
    fast_stars = [s for s in res["sources"] if s["total_pm_mas_yr"] and s["total_pm_mas_yr"] > 10000.0]
    assert len(fast_stars) >= 1
    assert abs(fast_stars[0]["total_pm_mas_yr"] - 10393.3) < 20.0

def test_wiseview_verification_bridge():
    from backend.services.verification_service import run_wiseview_verification
    res = run_wiseview_verification(133.79513, -7.24515, fov_arcmin=3.0, target_key="wise0855")
    assert res["status"] == "success"
    assert res["verdict"] == "PLANET_X_CANDIDATE"
    assert len(res["checklist"]) == 5
    assert "byw.tools/wiseview" in res["wiseview_url"]

def test_neossat_and_cadc_tracking():
    from backend.services.neossat_service import build_neossat_tracking_report
    res = build_neossat_tracking_report(133.79513, -7.24515, fov_arcmin=3.0, include_cadc=False)
    assert res["status"] == "success"
    assert res["verdict"] in ("NO_KNOWN_SSO_MATCH", "SSO_CHECK_UNAVAILABLE")
    assert "cadc_neossat_search" in res["links"]

def test_resources_codex():
    from backend.main import get_resources_codex
    res = get_resources_codex("133.79513", "-7.24515", 3.0)
    assert res["status"] == "success"
    assert len(res["portals"]) == 7

def test_observation_timeline_temporal_search():
    """Verify Issue #11: Observation Date & Time Search and Temporal Range Filtering."""
    from backend.services.cutout_engine import query_observation_timeline

    # 1. Full baseline
    all_obs = query_observation_timeline(133.79513, -7.24515)
    assert all_obs["status"] == "success"
    assert all_obs["count"] >= 4
    for o in all_obs["observations"]:
        assert "date_obs" in o
        assert "mjd" in o
        assert "survey" in o

    # 2. Filtered 2MASS window (1998-2002)
    filtered = query_observation_timeline(133.79513, -7.24515, start_date="1998-01-01", end_date="2002-01-01")
    assert filtered["status"] == "success"
    assert filtered["count"] == 1
    assert filtered["observations"][0]["survey"] == "2MASS"

    # 3. Empty historical window (1800-1850) -> honest no-observations state
    empty = query_observation_timeline(133.79513, -7.24515, start_date="1800-01-01", end_date="1850-01-01")
    assert empty["status"] == "no_observations"
    assert empty["count"] == 0
    assert "nearest_available_epoch" in empty

def test_multi_coordinate_sky_tiling_raycaster():
    """Verify Issue #10: Continuous sky tiling multi-coordinate off-center tile queries."""
    from backend.services.cutout_engine import fetch_real_cutout
    # Query slightly offset tiles around WISE 0855
    res_center = fetch_real_cutout(133.79513, -7.24515, fov_arcmin=3.0, lod=1)
    res_east = fetch_real_cutout(133.74513, -7.24515, fov_arcmin=3.0, lod=1)
    res_north = fetch_real_cutout(133.79513, -7.19515, fov_arcmin=3.0, lod=1)
    assert res_center["status"] == "success"
    assert res_east["status"] == "success"
    assert res_north["status"] == "success"
    assert res_center["difference_image"]["image_data"].startswith("data:image/png;base64,")


def test_observation_timeline_timestamps():
    """Verify Issue #11: cut-out epochs, 102-band observation_dates, and timeline timestamps."""
    from backend.services.cutout_engine import fetch_real_cutout, get_102_band_spectrum, query_observation_timeline

    cutout = fetch_real_cutout(133.79513, -7.24515, target_key="wise0855")
    assert cutout["status"] == "success"
    for ep in cutout["epochs"]:
        assert "date_obs" in ep and ep["date_obs"]
        assert "mjd" in ep and isinstance(ep["mjd"], (int, float))

    spec = get_102_band_spectrum(133.79513, -7.24515, "wise0855")
    assert "observation_dates" in spec
    assert len(spec["observation_dates"]) == 102
    assert "simultaneity_notice" in spec

    obs = query_observation_timeline(133.79513, -7.24515)
    assert obs["status"] == "success"
    assert obs["total_matched_observations"] == obs["count"]
    assert obs["count"] >= 4


def test_temporal_filter_valid_range():
    """Verify Issue #11: temporal filtering by date range and exact_date."""
    from backend.services.cutout_engine import query_observation_timeline

    res_range = query_observation_timeline(133.79513, -7.24515, start_date="2024-01-01", end_date="2026-12-31")
    assert res_range["status"] == "success"
    assert res_range["total_matched_observations"] >= 1
    assert any(o["date_obs"] >= "2024-01-01" for o in res_range["observations"])

    res_exact = query_observation_timeline(133.79513, -7.24515, exact_date="1999-02-14")
    assert res_exact["status"] == "success"
    assert res_exact["total_matched_observations"] == 1
    assert res_exact["observations"][0]["survey"] == "2MASS"


def test_temporal_filter_empty_range():
    """Verify Issue #11: empty temporal range returns honest no_observations + nearest_available_epoch."""
    from backend.services.cutout_engine import query_observation_timeline

    empty = query_observation_timeline(133.79513, -7.24515, start_date="1910-01-01", end_date="1920-01-01")
    assert empty["status"] == "no_observations"
    assert empty["total_matched_observations"] == 0
    assert empty["count"] == 0
    assert "nearest_available_epoch" in empty
    assert "date" in empty["nearest_available_epoch"]


def test_spatial_hash_cache_hit():
    """Verify Issue #13: L1 spatial-hash proximity cache returns sub-arcmin neighbor hit."""
    from backend.services.cutout_engine import (
        _L1_MEMORY_CACHE,
        _SPATIAL_HASH_CACHE,
        fetch_real_cutout,
        get_spatial_cell_id,
    )

    _L1_MEMORY_CACHE.clear()
    _SPATIAL_HASH_CACHE.clear()
    base_ra, base_dec = 133.79513, -7.24515
    first = fetch_real_cutout(base_ra, base_dec, fov_arcmin=3.0, target_key="wise0855", lod=1)
    assert first["status"] == "success"

    # Neighbor 0.06 arcmin away (< 0.35 arcmin tolerance, same 0.05 deg spatial cell)
    second = fetch_real_cutout(base_ra + 0.001, base_dec + 0.0005, fov_arcmin=3.0, target_key="wise0855", lod=1)
    assert second["status"] == "success"
    assert second.get("cache_tier") == "L1_SPATIAL_HASH"
    assert second.get("spatial_cell_id") == get_spatial_cell_id(base_ra, base_dec)


def test_sub_matrix_wcs_crop():
    """Verify Issue #13: Astropy WCS sub-matrix crop from wider on-disk master FITS."""
    from backend.services.cutout_engine import crop_submatrix_from_master_fits

    crop = crop_submatrix_from_master_fits(133.79513, -7.24515, fov_arcmin=1.5, dim=360)
    assert crop["status"] == "success"
    assert crop["shape"] == [360, 360]
    assert len(crop["peak_pixel"]) == 2
    assert isinstance(crop["spatial_cell_id"], int)


def test_auto_prune_disk_cache():
    """Verify Issue #13: smart disk auto-pruning evicts unpinned files while preserving benchmarks."""
    import os
    import tempfile

    from backend.services.cutout_engine import auto_prune_disk_cache

    with tempfile.TemporaryDirectory() as tmpdir:
        pinned_path = os.path.join(tmpdir, "wise0855_pinned.fits")
        old_sky_1 = os.path.join(tmpdir, "sky_10.0000_20.0000_3.0_2mass.fits")
        old_sky_2 = os.path.join(tmpdir, "sky_12.0000_22.0000_3.0_dss2.fits")
        with open(pinned_path, "wb") as f:
            f.write(b"A" * 600_000)
        with open(old_sky_1, "wb") as f:
            f.write(b"B" * 600_000)
        with open(old_sky_2, "wb") as f:
            f.write(b"C" * 600_000)
        os.utime(old_sky_1, (1000, 1000))
        os.utime(old_sky_2, (2000, 2000))

        # Limit 1.0 MB, target 0.8 MB -> should prune unpinned old files, keeping wise0855 pinned
        result = auto_prune_disk_cache(max_mb=1.0, target_mb=0.8, cache_dirs=[tmpdir])
        assert result["status"] == "ok"
        assert result["pinned_count"] == 1
        assert result["pruned_count"] >= 2
        assert os.path.exists(pinned_path)
        assert not os.path.exists(old_sky_1)


def test_ai_copilot_analyze_and_ask():
    """Verifies Integrated AI Co-Pilot endpoints synthesize real telemetry with zero fabricated scores."""
    from fastapi.testclient import TestClient

    from backend.main import app
    client = TestClient(app)
    r_analyze = client.get("/api/ai/analyze?ra=133.79513&dec=-7.24515&fov=3.0&target=wise0855")
    assert r_analyze.status_code == 200
    data = r_analyze.json()
    assert data["status"] == "success"
    assert "score" not in data
    assert "WISE" in data["target_name"] and "0855" in data["target_name"]
    assert "plain_english_summary" in data and len(data["plain_english_summary"]) > 20
    assert "scientist_technical_summary" in data and "ICRS" in data["scientist_technical_summary"]
    assert isinstance(data["key_insights"], list) and len(data["key_insights"]) == 3
    assert isinstance(data["checklist"], list) and len(data["checklist"]) >= 4

    r_ask = client.post("/api/ai/ask", json={
        "ra": "133.79513",
        "dec": "-7.24515",
        "fov": 3.0,
        "target": "wise0855",
        "question": "Explain 102-band molecular absorption dips"
    })
    assert r_ask.status_code == 200
    ask_data = r_ask.json()
    assert ask_data["status"] == "success"
    assert ask_data["topic"] == "102-Band Infrared Spectroscopy"
    assert any(tok in ask_data["answer"] for tok in ("CH4", "H2O", "CH₄", "H₂O"))


def test_issue_23_scientific_cache_lifecycle_and_headers():
    """Verifies Issue #23: X-Cache headers, cached_at provenance, quota telemetry, and refresh=true bypass."""
    from unittest.mock import patch

    from fastapi.testclient import TestClient

    from backend.main import app
    from backend.services.cutout_engine import clear_all_caches

    client = TestClient(app)
    clear_all_caches()

    # Warm WISE 0855 from benchmark disk cache -> L2 hit, then L1 RAM hit
    r1 = client.get("/api/cutout?target=wise0855&ra=133.79513&dec=-7.24515&lod=1")
    assert r1.status_code == 200
    assert r1.headers.get("X-Cache") in ("HIT", "MISS")
    assert r1.headers.get("X-Cached-At")
    d1 = r1.json()
    assert d1.get("cached_at")
    assert d1.get("is_stale") is False

    r2 = client.get("/api/cutout?target=wise0855&ra=133.79513&dec=-7.24515&lod=1")
    assert r2.status_code == 200
    assert r2.headers.get("X-Cache") == "HIT"
    assert r2.json().get("cache_hit") is True

    # refresh=true bypasses L1/L2 caches and reports X-Cache: MISS
    with patch("backend.services.cutout_engine.fetch_live_irsa_fits", return_value=None):
        r_ref = client.get("/api/cutout?target=wise0855&ra=133.79513&dec=-7.24515&lod=1&refresh=true")
        assert r_ref.status_code == 200
        assert r_ref.headers.get("X-Cache") == "MISS"
        assert r_ref.json().get("cache_hit") is False

    stats_resp = client.get("/api/cache/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert "quota_mb" in stats and stats["quota_mb"] == 500.0
    assert "ttl_seconds" in stats and stats["ttl_seconds"] > 0
    assert "spatial_bins_indexed" in stats

    prune_resp = client.post("/api/cache/prune?max_mb=800&target_mb=400")
    assert prune_resp.status_code == 200
    prune_data = prune_resp.json()
    assert prune_data.get("status") == "ok"
    assert "pruned_files" in prune_data and "freed_mb" in prune_data


def test_issue_28_resilient_cutout_fallback_on_irsa_502():
    """Verifies Issue #28: graceful WCS + Gaia DR3 degraded fallback when upstream IRSA fails."""
    from unittest.mock import patch

    from fastapi.testclient import TestClient

    from backend.main import app

    sample_gaia = {
        "status": "success",
        "sources": [
            {
                "source_id": "test_180_15",
                "ra": 180.0,
                "dec": 15.0,
                "pmra_mas_yr": 15.0,
                "pmdec_mas_yr": -10.0,
                "phot_g_mean_mag": 12.4,
            }
        ],
    }
    client = TestClient(app)
    with patch("backend.services.cutout_engine.fetch_live_irsa_fits", return_value=None), \
         patch("backend.services.gaia_service.query_gaia_dr3", return_value=sample_gaia):
        resp = client.get("/api/cutout?ra=180.0&dec=15.0&refresh=true")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "fallback_simulated"
        assert data["archive_reachability"] == "degraded"
        assert data["is_authentic_fits"] is False
        assert resp.headers.get("X-Archive-Reachability") == "degraded"
        assert len(data["epochs"]) == 2
        assert data["epochs"][0]["image_data"].startswith("data:image/png;base64,")
        assert data["difference_image"]["image_data"].startswith("data:image/png;base64,")


def test_persistent_circuit_breakers_and_single_flight():
    """Verify that IRSA and Gaia circuit breakers persist to disk and single-flight lock works."""
    # Trip circuits
    trip_irsa_tap_circuit(90.0)
    trip_esa_gaia_circuit(90.0)

    assert os.path.exists(_CIRCUIT_STATE_PATH)
    state = _load_circuit_state()
    assert state["irsa_tap_cooldown"] > time.time()
    assert state["esa_gaia_cooldown"] > time.time()
    assert is_irsa_tap_available() is False
    assert is_esa_gaia_available() is False

    # Reset circuit
    _save_circuit_state({"irsa_tap_cooldown": 0.0, "esa_gaia_cooldown": 0.0})


if __name__ == "__main__":
    for b in BENCHMARKS:
        test_nasa_benchmark_cutouts(*b)
    test_sexagesimal_and_decimal_parsing()
    test_102_band_spectroscopy()
    test_gaia_dr3_astrometry()
    test_wiseview_verification_bridge()
    test_neossat_and_cadc_tracking()
    test_resources_codex()
    test_ai_copilot_analyze_and_ask()
    print("ALL GOLDEN SUITE TESTS PASSED!")
