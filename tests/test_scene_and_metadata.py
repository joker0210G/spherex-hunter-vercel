"""
SPHEREx Hunter - Unit Tests for Metadata Schema & Space Motion Propagation
Verifies:
1. Pydantic schema validation rejects physical impossibilities (e.g. Y-dwarf Teff > 600K).
2. Astropy space motion propagation calculates exact epoch displacements and FOV exceedance.
3. Scene API returns truthful metadata, evidence tiers, and proper units.
"""

import pytest
from pydantic import ValidationError

from backend.services.metadata_schema import VERIFIED_PRESETS, AstronomicalTargetMetadata, EvidenceTier
from backend.services.motion_service import propagate_target_epoch
from backend.services.scene_service import get_target_scene


def test_schema_validation_valid_preset():
    """Verify standard benchmark preset metadata passes schema validation."""
    meta = VERIFIED_PRESETS["wise0855"]
    assert meta.name == "WISE J085510.83-071442.5"
    assert meta.effective_temp_k == 250.0
    assert meta.total_pm_arcsec_yr > 8.0
    assert meta.evidence_tier == EvidenceTier.KNOWN_STELLAR_OR_BROWN_DWARF
    assert len(meta.citations) >= 2


def test_schema_validation_rejects_implausible_y_dwarf_temp():
    """Verify physical impossibility check: Y-dwarf Teff cannot exceed 600 K."""
    with pytest.raises(ValidationError) as exc_info:
        AstronomicalTargetMetadata(
            name="Fake Y-Dwarf",
            ra_deg=100.0,
            dec_deg=10.0,
            object_type="Substellar Y-Dwarf",
            spectral_type="Y2",
            effective_temp_k=5200.0,  # Physical impossibility!
            evidence_tier=EvidenceTier.KNOWN_STELLAR_OR_BROWN_DWARF,
            evidence_summary="Fake test",
            confirmation_status="NOT_CONFIRMED"
        )
    assert "Physical plausibility violation" in str(exc_info.value)
    assert "cannot exceed 600 K" in str(exc_info.value)


def test_schema_validation_rejects_extreme_proper_motion():
    """Verify extreme proper motion check (> 25 arcsec/yr)."""
    with pytest.raises(ValidationError) as exc_info:
        AstronomicalTargetMetadata(
            name="Extreme Mover",
            ra_deg=100.0,
            dec_deg=10.0,
            object_type="Star",
            total_pm_arcsec_yr=40.0,  # Impossible stellar proper motion
            evidence_tier=EvidenceTier.UNKNOWN_MOVER,
            evidence_summary="Extreme PM test",
            confirmation_status="NOT_CONFIRMED"
        )
    assert "Extreme proper motion alert" in str(exc_info.value)


def test_astropy_space_motion_propagation_barnard():
    """Verify Astropy apply_space_motion computes displacement and FOV exceedance for Barnard's Star."""
    # Barnard's Star: ~10.36 "/yr
    res = propagate_target_epoch(
        ra_deg=269.45208,
        dec_deg=4.69339,
        pm_ra_mas_yr=-798.58,
        pm_dec_mas_yr=10328.12,
        base_epoch_year=2000.0,
        target_date="2025-06-01",
        fov_arcmin=3.0  # 180 arcsec
    )
    # Displacement over 25.4 years should be ~263 arcsec
    assert 250.0 < res["displacement_arcsec"] < 280.0
    assert res["exceeds_fov"] is True
    assert "exceeds the requested FOV" in res["warning"]


def test_astropy_space_motion_propagation_low_pm():
    """Verify targets with low proper motion stay within FOV."""
    res = propagate_target_epoch(
        ra_deg=77.10875,
        dec_deg=30.40139,
        pm_ra_mas_yr=1.2,
        pm_dec_mas_yr=-22.4,
        base_epoch_year=2000.0,
        target_date="2025-06-01",
        fov_arcmin=3.0
    )
    assert res["displacement_arcsec"] < 1.0
    assert res["exceeds_fov"] is False
    assert res["warning"] is None


def test_scene_state_engine_truthful_values():
    """Verify get_target_scene returns verified temperatures and evidence tiers."""
    scene = get_target_scene("wise0855", fov_arcmin=3.0)
    assert scene["status"] == "success"
    assert scene["target"]["effective_temp_k"] == 250.0  # Must NEVER be 5200 K
    assert scene["target"]["total_pm_arcsec_yr"] == pytest.approx(8.1493, rel=1e-2)
    assert scene["target"]["evidence_tier"] == "KNOWN_STELLAR_OR_BROWN_DWARF"
    assert "sub_stellar_planet_x_probability" not in scene["target"]  # Sensationalized prob removed

    # Verify epochs structure
    assert len(scene["epochs"]) >= 4
    for ep in scene["epochs"]:
        assert "cutout_center" in ep
        assert "displacement_arcsec" in ep
        assert "pixel_scale_arcsec" in ep
        assert "units" in ep

    # Verify layers structure
    layers = {l["id"]: l for l in scene["layers"]}
    assert "base_epoch_a" in layers
    assert "base_epoch_b" in layers
    assert "diff_image" in layers
    assert "coverage_mask" in layers
    assert "gaia_overlay" in layers

    # Bandpass matching check for WISE 0855 (AllWISE W2 4.6um + SPHEREx Stack 4.6um are matched)
    assert layers["diff_image"]["valid_bands"] is True
    assert layers["diff_image"]["status"] == "ready"

    # Band mismatch check on 2MASS (1.25um) vs SPHEREx (2.1um) using standard preset (e.g. Barnard)
    scene_barnard = get_target_scene("barnard", fov_arcmin=3.0)
    layers_barnard = {l["id"]: l for l in scene_barnard["layers"]}
    assert layers_barnard["diff_image"]["valid_bands"] is False
    assert "Band Mismatch" in layers_barnard["diff_image"]["tooltip"]
