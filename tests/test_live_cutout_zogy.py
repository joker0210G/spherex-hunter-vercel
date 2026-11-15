"""
🛰️ SPHEREx Hunter - Live Cutout Pipeline & ZOGY Differencing Tests
Addresses GitHub Issue #2: Wiring ZOGY Differencing & Float32 Preprocessing into Live /api/cutout

Validates:
1. Live GET /api/cutout returns authentic ZOGY S_corr significance metrics (units: sigma).
2. ZOGY S_corr peak >= 5.0 sigma on WISE 0855 and Barnard's Star.
3. GET /api/cutout/raw returns streaming Float32 binary buffer (65,536 bytes) with ETag.
4. GET /api/cutout/raw/header returns accurate WCS celestial projection metadata.
"""

import numpy as np
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_live_cutout_zogy_wise0855():
    """Verify that /api/cutout on WISE 0855 returns ZOGY S_corr significance peak >= 5.0 sigma."""
    resp = client.get("/api/cutout?target=wise0855&ra=133.79513&dec=-7.24515&lod=1")
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "success"
    assert "WISE 0855" in data["target"]

    # Check ZOGY significance fields
    assert "zogy_significance" in data
    zogy = data["zogy_significance"]
    assert zogy["units"] == "sigma"
    assert "ZOGY" in zogy["method"]
    assert zogy["peak_sigma"] >= 5.0
    assert zogy["is_significant"] is True

    # Check difference image payload
    diff_img = data["difference_image"]
    assert "image_data" in diff_img
    assert diff_img.get("units") == "sigma"
    assert diff_img.get("scorr_max") >= 5.0


def test_live_cutout_zogy_barnard():
    """Verify that /api/cutout on Barnard's Star returns ZOGY S_corr significance peak >= 5.0 sigma."""
    resp = client.get("/api/cutout?target=barnard&ra=269.45208&dec=4.69339&lod=1")
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "success"
    assert "Barnard" in data["target"]

    assert "zogy_significance" in data
    zogy = data["zogy_significance"]
    assert zogy["units"] == "sigma"
    assert zogy["peak_sigma"] >= 5.0
    assert zogy["is_significant"] is True
    assert data["difference_image"].get("scorr_max") >= 5.0


def test_raw_cutout_float32_streaming():
    """Verify that GET /api/cutout/raw streams raw Float32 ArrayBuffer for WebGL client."""
    resp = client.get("/api/cutout/raw?target=sample_leo")
    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "application/octet-stream"
    assert resp.headers.get("etag") is not None

    raw_bytes = resp.content
    assert len(raw_bytes) == 128 * 128 * 4  # 65536 bytes
    arr = np.frombuffer(raw_bytes, dtype=np.float32).reshape((128, 128))
    assert not np.isnan(np.nanmax(arr))


def test_raw_cutout_wcs_header():
    """Verify that GET /api/cutout/raw/header returns WCS celestial projection metadata."""
    resp = client.get("/api/cutout/raw/header?target=sample_leo")
    assert resp.status_code == 200
    data = resp.json()
    assert data["dimensions"] == [128, 128]
    assert data["dtype"] == "float32"
    assert "microjansky" in data["units"].lower()
    assert len(data["crpix"]) == 2
    assert len(data["crval"]) == 2
