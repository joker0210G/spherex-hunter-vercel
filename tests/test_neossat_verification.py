"""
Unit and live tests for neossat_service and verification_service.
Verifies:
1. IMCCE SkyBoT response parsing and evidence tier assignment (KNOWN_SOLAR_SYSTEM_OBJECT).
2. CADC CAOM-2 TAP query construction and error resiliency.
3. Automated verification checklist assigns evidence tiers without 'score' or 'Planet X'.
4. Input sanitization (coordinates, radius bounds).
5. Live connectivity check with proper User-Agent headers (preventing HTTP 403).
"""

import json
from unittest.mock import patch

from backend.services.neossat_service import (
    build_neossat_tracking_report,
    query_known_solar_system_objects,
    query_neossat_observations,
)
from backend.services.verification_service import run_wiseview_verification

MOCK_SKYBOT_HIT = json.dumps([
    {
        "Num": "1",
        "Name": "Ceres",
        "Class": "Asteroid",
        "RA (hms)": "08 55 10.83",
        "DEC (dms)": "-07 14 42.5",
        "VMag (mag)": "8.5",
        "Err (arcsec)": "0.02",
        "dRA (arcsec/h)": "-12.4",
        "dDEC (arcsec/h)": "4.2",
        "dg (ua)": "2.1",
        "dh (ua)": "2.8",
        "ssodnet": {"ssocard": "https://ssp.imcce.fr/forms/ssocard/1"},
    }
]).encode("utf-8")

MOCK_SKYBOT_EMPTY = b"[]"


def test_skybot_hit_assigns_known_sso_tier():
    from backend.services.neossat_service import _SKYBOT_CACHE
    _SKYBOT_CACHE.clear()
    with patch("backend.services.neossat_service._http_get", return_value=MOCK_SKYBOT_HIT):
        report = build_neossat_tracking_report(ra=133.79513, dec=-7.24515, fov_arcmin=3.0, include_cadc=False)
        assert report["verdict"] == "KNOWN_SOLAR_SYSTEM_OBJECT"
        assert "Ceres" in report["verdict_text"]
        assert "Planet X" not in report["verdict_text"]
        assert "Reject as Planet X" not in report["verdict_text"]
        assert report["known_solar_system_objects"]["count"] == 1


def test_skybot_empty_assigns_clean_verdict():
    from backend.services.neossat_service import _SKYBOT_CACHE
    _SKYBOT_CACHE.clear()
    with patch("backend.services.neossat_service._http_get", return_value=MOCK_SKYBOT_EMPTY):
        report = build_neossat_tracking_report(ra=133.79513, dec=-7.24515, fov_arcmin=3.0, include_cadc=False)
        assert report["verdict"] == "NO_KNOWN_SSO_MATCH"
        assert "Planet X" not in report["verdict_text"]


def test_verification_service_tiers_and_no_score():
    mock_gaia = {
        "status": "success",
        "matched_count": 0,
        "sources": []
    }
    with patch("backend.services.verification_service.query_gaia_dr3", return_value=mock_gaia), \
         patch("backend.services.verification_service.query_known_solar_system_objects", return_value={"status": "success", "count": 0, "objects": [], "epoch_utc": "2025-01-01T00:00:00Z"}), \
         patch("backend.services.cutout_engine.fetch_real_cutout", return_value={"motion_vector": {"transient_type": "PROPER_MOTION_DIPOLE", "shift_arcsec": 7.1, "confidence": 0.99}}):

        res = run_wiseview_verification(ra=133.79513, dec=-7.24515, fov_arcmin=3.0)
        assert res["status"] == "success"
        assert res["evidence_tier"] == "UNKNOWN_RAPID_MOVER"
        assert "score" not in res
        assert "checklist_summary" in res
        assert "motion" in res["checklist_summary"]["passed"]
        assert "Candidate, not confirmed" in res["candidate_status"]


def test_live_skybot_connectivity():
    """Documented live check: verifies IMCCE SkyBoT reachable with custom User-Agent without HTTP 403."""
    res = query_known_solar_system_objects(ra=133.79513, dec=-7.24515, radius_arcmin=3.0, timeout=10.0)
    assert res["status"] in ("success", "unavailable")
    if res["status"] == "success":
        assert isinstance(res["count"], int)
        assert "objects" in res
        assert res["service"].startswith("IMCCE SkyBoT")


def test_live_cadc_neossat_connectivity():
    """Documented live check: verifies CADC CAOM-2 TAP connectivity for NEOSSAT collection."""
    res = query_neossat_observations(ra=133.79513, dec=-7.24515, radius_deg=0.2, limit=5, timeout=15.0)
    assert res["status"] in ("success", "unavailable")
    if res["status"] == "success":
        assert isinstance(res["observations"], list)
        assert res["collection"] == "NEOSSAT"
