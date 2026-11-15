"""
🛰️ SPHEREx Hunter - 102-Band Spectroscopy & Structural Metadata Tests
Validates GitHub Issue #7: 6-Array Selector, 17-Wavelength Stepper & SED Visualizer
"""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_bands_endpoint_structural_metadata():
    """Validates that GET /api/bands returns 102 channels across 6 arrays (A1-A6)."""
    resp = client.get("/api/bands")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["total_bands"] == 102
    assert len(data["arrays"]) == 6
    assert len(data["bands"]) == 102

    array_ids = [a["array_id"] for a in data["arrays"]]
    assert array_ids == ["A1", "A2", "A3", "A4", "A5", "A6"]

    # Verify first and last channel wavelengths
    assert data["bands"][0]["band_id"] == 1
    assert data["bands"][0]["array_id"] == "A1"
    assert data["bands"][0]["wavelength_um"] == 0.750

    assert data["bands"][-1]["band_id"] == 102
    assert data["bands"][-1]["array_id"] == "A6"
    assert data["bands"][-1]["wavelength_um"] == 5.000

    # Verify molecular flags present
    flagged = [b for b in data["bands"] if b.get("molecular_flag")]
    assert len(flagged) >= 4
    flags = {b["molecular_flag"] for b in flagged}
    assert "H2O" in flags
    assert "CH4" in flags
    assert "CO2_ICE" in flags
    assert "CO" in flags

def test_spectrum_endpoint_with_bands_and_summary():
    """Validates that GET /api/spectrum returns 102 bands and A1-A6 array_summary."""
    resp = client.get("/api/spectrum?ra=133.79513&dec=-7.24515&target=wise0855")
    assert resp.status_code == 200
    data = resp.json()

    assert data["available"] is True
    assert len(data["bands"]) == 102
    assert "array_summary" in data

    summary = data["array_summary"]
    for arr_id in ["A1", "A2", "A3", "A4", "A5", "A6"]:
        assert arr_id in summary
        assert "avg_flux_ujy" in summary[arr_id]
        assert "total_counts" in summary[arr_id]
        assert "band_range" in summary[arr_id]

    # Verify individual band schema
    first_band = data["bands"][0]
    assert first_band["band_id"] == 1
    assert first_band["array_id"] == "A1"
    assert "flux_ujy" in first_band
    assert "wavelength_um" in first_band
    assert "measured_photometry_points" in data
    assert "wise_counterpart" in data
    assert "spherex_coverage" in data


def test_wise_and_spherex_catalog_endpoints():
    """Validates /api/catalog/wise, /api/catalog/spherex, and unified /api/catalog/crossmatch."""
    # 1. AllWISE + NEOWISE endpoint on Barnard's Star
    r_wise = client.get("/api/catalog/wise?ra=269.45208&dec=4.69339&radius=3.0")
    assert r_wise.status_code == 200
    d_wise = r_wise.json()
    assert d_wise["survey"] == "NASA AllWISE + NEOWISE-R"
    assert d_wise["status"] in ("success", "unavailable")
    if d_wise["status"] == "success":
        assert len(d_wise["sources"]) > 0
        s0 = d_wise["sources"][0]
        assert "w1_mag" in s0 and "w1_flux_ujy" in s0 and "w1_w2_color" in s0

    # 2. SPHEREx DR1 ObsCore endpoint
    r_spx = client.get("/api/catalog/spherex?ra=133.79513&dec=-7.24515&radius=15.0")
    assert r_spx.status_code == 200
    d_spx = r_spx.json()
    assert "NASA SPHEREx" in d_spx["survey"]
    assert d_spx["coverage_type"] in ("DIRECT_FIELD_HIT", "DR1_REFERENCE_PLANES", "ARCHIVE_UNAVAILABLE")
    assert isinstance(d_spx["planes"], list)

    # 3. Unified Cross-Match on WISE 0855-0714 (including moving-target IR photometry synthesis)
    r_xm = client.get("/api/catalog/crossmatch?ra=133.79513&dec=-7.24515&radius=3.0")
    assert r_xm.status_code == 200
    d_xm = r_xm.json()
    assert d_xm["status"] == "success"
    assert "wise_counterpart" in d_xm
    assert d_xm["wise_counterpart"]["w2_mag"] is not None
    assert "wise_w1_minus_w2" in d_xm["color_diagnostics"]
    assert d_xm["color_diagnostics"]["is_ultracold_candidate"] is True
    assert len(d_xm["multi_survey_sed_points"]) >= 2
    assert len(d_xm["multi_epoch_lightcurve"]) >= 2


if __name__ == "__main__":
    test_bands_endpoint_structural_metadata()
    test_spectrum_endpoint_with_bands_and_summary()
    test_wise_and_spherex_catalog_endpoints()
    print("ALL BANDS, SPECTRUM & MULTI-SURVEY CATALOG TESTS PASSED!")
