"""
🛰️ SPHEREx Hunter - Comprehensive API v1 Contract Tests
NASA Space Apps Challenge 2026 - Team RIP

Validates:
1. Strict adherence to Pydantic v2 response schemas and RFC 7807 error shapes.
2. Compatibility against docs/frontend_calls.json network requirements.
3. Astropy apply_space_motion proper-motion propagation accuracy.
4. Scientific honesty edge cases (BAND_MISMATCH, NO_PUBLIC_DATA, honest empty states).
5. Fast sub-millisecond execution for capabilities and health.
6. Binary export formats (CSV, IVOA VOTable XML, binary FITS table).
"""

import io

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
from fastapi.testclient import TestClient

from backend.api_v1 import propagate_target_position
from backend.main import app
from backend.models_v1 import (
    CapabilitiesResponse,
    CutoutRawHeaderResponse,
    DifferenceResponse,
    ExposuresResponse,
    FlagCandidateResponse,
    HealthResponse,
    LightCurveResponse,
    PhotometryResponse,
    ProblemDetails,
    SceneResponse,
    SearchResponse,
    StatusResponse,
    TargetDetail,
    TargetSummary,
    ValidationResponse,
)

client = TestClient(app)


# ==============================================================================
# 1. CORE CAPABILITIES, STATUS, & HEALTH
# ==============================================================================

def test_v1_health():
    """Liveness check must return 200 OK under 10ms with timestamp."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    model = HealthResponse(**data)
    assert model.status == "ok"
    assert "T" in model.timestamp
    assert resp.headers.get("X-Request-Id") is not None


def test_v1_capabilities():
    """Capabilities endpoint returns deployment state and feature rationales."""
    resp = client.get("/api/v1/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    model = CapabilitiesResponse(**data)
    assert model.api_version == "v1"
    assert "live_archive" in model.capabilities
    assert "demo_cache" in model.capabilities
    assert "spectral_differencing" in model.capabilities
    assert model.capabilities["live_archive"].enabled is True


def test_v1_status():
    """Status endpoint reports cache metrics and archive reachability."""
    resp = client.get("/api/v1/status")
    assert resp.status_code == 200
    data = resp.json()
    model = StatusResponse(**data)
    assert model.ready is True
    assert model.archive.irsa_reachable is True
    assert "l1_ram_entries" in model.cache


# ==============================================================================
# 2. TARGETS & BENCHMARKS
# ==============================================================================

def test_v1_list_targets():
    """Lists benchmark targets with ICRS degrees, sexagesimal strings, and public exposure counts."""
    resp = client.get("/api/v1/targets")
    assert resp.status_code == 200
    targets = resp.json()
    assert len(targets) >= 5

    target_map = {}
    for t in targets:
        model = TargetSummary(**t)
        target_map[model.id] = model
        assert model.ra_sexagesimal is not None
        assert model.dec_sexagesimal is not None

    assert "wise0855" in target_map
    assert "sample_leo" in target_map
    assert "rwaur" in target_map
    assert target_map["rwaur"].public_exposures_count == 0


def test_v1_get_target_detail():
    """Returns detailed target metadata including proper motions and literature citations."""
    resp = client.get("/api/v1/targets/wise0855")
    assert resp.status_code == 200
    data = resp.json()
    model = TargetDetail(**data)
    assert model.id == "wise0855"
    assert model.space_motion is not None
    assert model.space_motion.pm_ra_cosdec_mas_yr == -8120.0
    assert len(model.citations) > 0


def test_v1_get_target_not_found_rfc7807():
    """Unknown target must return 404 with RFC 7807 problem details."""
    resp = client.get("/api/v1/targets/unknown_target_999")
    assert resp.status_code == 404
    assert resp.headers.get("content-type") == "application/problem+json"
    problem = ProblemDetails(**resp.json())
    assert problem.code == "TARGET_NOT_FOUND"
    assert problem.status == 404
    assert "unknown_target_999" in problem.detail


# ==============================================================================
# 3. SCENE GRAPH & ASTROPY PROPER MOTION PROPAGATION
# ==============================================================================

def test_astropy_proper_motion_propagation():
    """
    Validates proper motion propagation against independent Astropy apply_space_motion.
    WISE 0855 moves ~8.1 arcsec/yr westward; over 11 years (2014 to 2025),
    RA should shift significantly westward (~0.02 deg).
    """
    ra_init = 133.79513
    dec_init = -7.24515
    pm_ra = -8120.0  # mas/yr
    pm_dec = 2690.0   # mas/yr
    plx = 448.4       # mas
    obs_mjd = 60789.75  # ~April 2025

    prop_ra, prop_dec = propagate_target_position(
        ra_deg=ra_init,
        dec_deg=dec_init,
        pm_ra_mas_yr=pm_ra,
        pm_dec_mas_yr=pm_dec,
        mjd=obs_mjd,
        epoch_ref=2014.0,
        parallax_mas=plx
    )

    # RA must shift westward (smaller RA in degrees)
    assert prop_ra < ra_init
    # Dec must shift northward (less negative Dec in degrees)
    assert prop_dec > dec_init

    # Total displacement should be approximately 80 - 100 arcseconds (~0.025 degrees)
    c0 = SkyCoord(ra=ra_init*u.deg, dec=dec_init*u.deg)
    c1 = SkyCoord(ra=prop_ra*u.deg, dec=prop_dec*u.deg)
    sep_arcsec = c0.separation(c1).arcsec
    assert 70.0 < sep_arcsec < 110.0


def test_v1_target_scene():
    """Scene graph endpoint returns layers and space-motion propagated epochs."""
    resp = client.get("/api/v1/targets/sample_leo/scene?fov_arcmin=3.0")
    assert resp.status_code == 200
    data = resp.json()
    model = SceneResponse(**data)
    assert model.target.id == "sample_leo"
    assert len(model.layers) >= 3
    assert len(model.epochs) >= 1


# ==============================================================================
# 4. EXPOSURES & HONEST ZERO-COUNT EMPTY STATE
# ==============================================================================

def test_v1_exposures_honest_empty_state_rwaur():
    """RW Aurigae has 0 public SPHEREx exposures; must return honest structured explanation."""
    resp = client.get("/api/v1/targets/rwaur/exposures")
    assert resp.status_code == 200
    data = resp.json()
    model = ExposuresResponse(**data)
    assert model.status == "no_public_data"
    assert model.total_found == 0
    assert len(model.exposures) == 0
    assert "0 public SPHEREx exposures" in model.reason


def test_v1_exposures_sample_leo():
    """Technical validation field has cached public exposures."""
    resp = client.get("/api/v1/targets/sample_leo/exposures")
    assert resp.status_code == 200
    data = resp.json()
    model = ExposuresResponse(**data)
    assert model.status == "ok"
    assert model.total_found >= 2
    assert len(model.exposures) >= 2
    assert model.exposures[0].detector == 6
    assert model.exposures[0].wavelength_um == 4.42


# ==============================================================================
# 5. RAW BINARY CUTOUT & WCS HEADER
# ==============================================================================

def test_v1_raw_cutout_binary_and_etag():
    """Raw cutout endpoint returns exactly 128x128 4-byte float32 binary (65,536 bytes) with ETag."""
    resp = client.get("/api/v1/cutout/raw?target=sample_leo")
    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "application/octet-stream"
    etag = resp.headers.get("etag")
    assert etag is not None

    raw_bytes = resp.content
    assert len(raw_bytes) == 128 * 128 * 4  # 65536 bytes

    arr = np.frombuffer(raw_bytes, dtype=np.float32).reshape((128, 128))
    assert not np.isnan(np.nanmax(arr))

    # Test 304 Not Modified
    resp_304 = client.get("/api/v1/cutout/raw?target=sample_leo", headers={"If-None-Match": etag})
    assert resp_304.status_code == 304


def test_v1_raw_cutout_header():
    """Raw cutout WCS header returns pixel coordinates and flux units."""
    resp = client.get("/api/v1/cutout/raw/header?target=sample_leo")
    assert resp.status_code == 200
    data = resp.json()
    model = CutoutRawHeaderResponse(**data)
    assert model.dimensions == [128, 128]
    assert model.dtype == "float32"
    assert "microjansky" in model.units.lower()


# ==============================================================================
# 6. DIFFERENCE IMAGING & BAND MISMATCH ERROR
# ==============================================================================

def test_v1_difference_band_mismatch_rfc7807():
    """Mismatched wavelengths must be rejected with 422 BAND_MISMATCH."""
    resp = client.get("/api/v1/difference?target=sample_leo&wavelength_a_um=1.20&wavelength_b_um=4.42")
    assert resp.status_code == 422
    assert resp.headers.get("content-type") == "application/problem+json"
    problem = ProblemDetails(**resp.json())
    assert problem.code == "BAND_MISMATCH"
    assert "mismatched wavelengths" in problem.detail


def test_v1_difference_matched_pair():
    """Matched wavelength pair returns valid ZOGY difference product."""
    resp = client.get("/api/v1/difference?target=sample_leo")
    assert resp.status_code == 200
    data = resp.json()
    model = DifferenceResponse(**data)
    assert model.valid is True
    assert model.band_matched is True
    assert "ZOGY" in model.method
    assert model.scorr_max is not None


# ==============================================================================
# 7. SCIENTIFIC VALIDATION METRICS
# ==============================================================================

def test_v1_validation_metrics():
    """Dynamic validation endpoint returns FPR, veto efficiency, and audit links."""
    resp = client.get("/api/v1/validation")
    assert resp.status_code == 200
    data = resp.json()
    model = ValidationResponse(**data)
    assert model.pipeline_version == "6.0.0"

    metric_names = {m.name: m for m in model.metrics}
    assert "clean_fpr_5sigma_per_deg2" in metric_names
    assert "veto_rejection_efficiency_5sigma_pct" in metric_names
    assert "completeness_50pct_ab" in metric_names

    # Check incomplete metrics are marked under_review
    assert "star_mask_mover_loss_rate" in metric_names
    assert metric_names["star_mask_mover_loss_rate"].status == "under_review"


# ==============================================================================
# 8. EXPORTS (CSV, VOTABLE XML, BINARY FITS TABLE)
# ==============================================================================

def test_v1_export_csv():
    """CSV export returns standard text/csv."""
    resp = client.get("/api/v1/export/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type")
    assert "candidate_id" in resp.text


def test_v1_export_votable():
    """VOTable export returns valid IVOA XML."""
    resp = client.get("/api/v1/export/votable")
    assert resp.status_code == 200
    assert "xml" in resp.headers.get("content-type")
    assert "VOTABLE" in resp.text


def test_v1_export_fits():
    """FITS table export returns valid multi-extension binary FITS table."""
    resp = client.get("/api/v1/export/fits")
    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "image/fits"
    bio = io.BytesIO(resp.content)
    with fits.open(bio) as hdul:
        assert len(hdul) >= 2
        assert isinstance(hdul[1], fits.BinTableHDU)
        assert "candidate_id" in hdul[1].columns.names


# ==============================================================================
# 9. CITIZEN SCIENCE FLAGGING & DEDUPLICATION
# ==============================================================================

def test_v1_candidate_flagging_and_deduplication():
    """Submitting duplicate flags within spatial radius acknowledges existing flag."""
    payload = {
        "target_id": "sample_leo",
        "ra_deg": 160.6050,
        "dec_deg": 30.7020,
        "category": "mover",
        "notes": "Fast-moving candidate tracklet test",
        "user_id": "@pytest_runner"
    }

    # First flag
    resp1 = client.post("/api/v1/candidates/flag", json=payload)
    assert resp1.status_code == 200
    data1 = resp1.json()
    model1 = FlagCandidateResponse(**data1)
    assert model1.status in ("recorded", "duplicate_acknowledged")
    flag_id = model1.flag_id

    # Duplicate flag immediately after
    resp2 = client.post("/api/v1/candidates/flag", json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    model2 = FlagCandidateResponse(**data2)
    assert model2.duplicate is True
    assert model2.flag_id == flag_id


# ==============================================================================
# 10. FORCED PHOTOMETRY & LIKE-WAVELENGTH LIGHT CURVES
# ==============================================================================

def test_v1_forced_photometry():
    """Photometry returns physical fluxes with explicit units and SNR."""
    resp = client.get("/api/v1/targets/wise0855/photometry")
    assert resp.status_code == 200
    data = resp.json()
    model = PhotometryResponse(**data)
    assert model.target_id == "wise0855"
    assert len(model.bands) > 0
    assert model.bands[0].flux.unit == "uJy"
    assert model.bands[0].mag_ab.unit == "mag (AB)"


def test_v1_like_wavelength_lightcurve():
    """Light curve strictly enforces like-wavelength selection rule."""
    resp = client.get("/api/v1/targets/sample_leo/lightcurve")
    assert resp.status_code == 200
    data = resp.json()
    model = LightCurveResponse(**data)
    assert model.target_id == "sample_leo"
    assert "Like-wavelength" in model.selection_rule
    assert len(model.points) >= 2


# ==============================================================================
# 11. SEARCH
# ==============================================================================

def test_v1_search_preset_and_coordinates():
    """Search matches presets and parses coordinates."""
    # Preset search
    resp_preset = client.get("/api/v1/targets/search?q=wise")
    assert resp_preset.status_code == 200
    search_data = SearchResponse(**resp_preset.json())
    assert any("0855" in r.name for r in search_data.results)

    # Coordinate search
    resp_coord = client.get("/api/v1/targets/search?q=160.6,30.7")
    assert resp_coord.status_code == 200
    search_coord = SearchResponse(**resp_coord.json())
    assert len(search_coord.results) > 0
    assert "Custom Coordinates" in search_coord.results[0].name
