# 🛰️ SPHEREx Hunter - API Contract Specification (v1)
> **NASA Space Apps Challenge 2026** | **Team:** RIP (Coimbatore, India)  
> **API Version:** `v1` | **Deployment Environment:** Production / Local  
> **OpenAPI Schema:** [`docs/openapi.json`](file:///docs/openapi.json) | **Interactive Docs:** `/docs`

---

## 1. Architectural Principles & Conventions

The SPHEREx Hunter backend adheres to rigorous scientific and software engineering principles:

1. **Contract-First & Strictly Typed:** Every request and response schema is defined using Pydantic v2 models in [`backend/models_v1.py`](file:///backend/models_v1.py).
2. **Absolute Scientific Honesty:** No hardcoded probabilities, synthetic noise curves, or fabricated candidate detections. Missing public data returns structured, truthful empty states or RFC 7807 problem details.
3. **Physical Quantities Convention:** Every measured or derived physical quantity is represented as an explicit object:
   ```json
   {
     "value": 14.80,
     "unit": "uJy",
     "uncertainty": 0.35,
     "source": "circular_aperture_3.5pix"
   }
   ```
4. **Celestial Coordinate Conventions:**
   - Coordinates are provided in ICRS decimal degrees (`ra_deg`, `dec_deg`).
   - Standard sexagesimal string equivalents (`ra_sexagesimal`: `08:55:10.831`, `dec_sexagesimal`: `-07:14:42.54`) are included for human readability.
5. **Time Conventions:**
   - Dual time representation: Modified Julian Date (`mjd`, e.g. `60789.752254`) and ISO-8601 UTC (`utc`, e.g. `2025-04-20T18:03:14Z`).
6. **Standard HTTP Headers:**
   - `X-Request-Id`: Unique request tracing UUID (e.g. `spx-a1b2c3d4e5f6`).
   - `ETag`: SHA-256 content checksum for caching and 304 Not Modified responses.
   - `Cache-Control`: Granular caching directives (e.g. `public, max-age=3600`).
   - `X-Data-Source`: Provenance indicator (`live_archive`, `demo_cache`, `registry`, `system`).
7. **RFC 7807 Problem Details:** All client and server errors return `Content-Type: application/problem+json`:
   ```json
   {
     "type": "https://spherex-hunter.space/errors/band-mismatch",
     "title": "Wavelength Mismatch in Difference Pair",
     "status": 422,
     "detail": "Epoch A (1.20 μm) and Epoch B (4.42 μm) have mismatched wavelengths...",
     "instance": "http://127.0.0.1:8000/api/v1/difference?...",
     "request_id": "spx-9876543210ab",
     "retryable": false,
     "code": "BAND_MISMATCH"
   }
   ```

---

## 2. API v1 Endpoint Inventory

| Endpoint | Method | Response Model | Description |
| :--- | :--- | :--- | :--- |
| `/api/v1/capabilities` | `GET` | `CapabilitiesResponse` | Reports operational state and enabled features. |
| `/api/v1/status` | `GET` | `StatusResponse` | Readiness, archive reachability latencies, and cache metrics. |
| `/api/v1/health` | `GET` | `HealthResponse` | Zero-dependency liveness probe. |
| `/api/v1/targets` | `GET` | `List[TargetSummary]` | Benchmark targets catalog with coordinates and exposure counts. |
| `/api/v1/targets/{id}` | `GET` | `TargetDetail` | Detailed target metadata, Gaia DR3 space motion, and citations. |
| `/api/v1/targets/{id}/scene` | `GET` | `SceneResponse` | Astronomical scene graph, space-motion propagation, and layer tree. |
| `/api/v1/targets/{id}/exposures` | `GET` | `ExposuresResponse` | Public SPHEREx exposures covering the field (or honest 0-count reason). |
| `/api/v1/cutout` | `GET` | Visual Cutout Data | Calibrated visual preview cutout with ETag validation. |
| `/api/v1/cutout/raw` | `GET` | `application/octet-stream` | Raw uncompressed float32 ArrayBuffer for WebGL / client-side analysis. |
| `/api/v1/cutout/raw/header` | `GET` | `CutoutRawHeaderResponse` | WCS celestial projection and calibration metadata for raw binary. |
| `/api/v1/difference` | `GET` | `DifferenceResponse` | ZOGY optimal subtraction; rejects mismatched wavelengths (`BAND_MISMATCH`). |
| `/api/v1/validation` | `GET` | `ValidationResponse` | Dynamic pipeline audit metrics (clean FPR, veto efficiency, completeness). |
| `/api/v1/export/csv` | `GET` | `text/csv` | Candidate discoveries export in standard CSV. |
| `/api/v1/export/votable` | `GET` | `application/x-votable+xml` | Candidate discoveries export in IVOA VOTable XML. |
| `/api/v1/export/fits` | `GET` | `image/fits` | Candidate discoveries export in binary FITS table. |
| `/api/v1/targets/{id}/candidates` | `GET` | `CandidatesResponse` | Verified pipeline candidate detections for the target field. |
| `/api/v1/candidates/flag` | `POST` | `FlagCandidateResponse` | Citizen science candidate logging with spatial deduplication. |
| `/api/v1/targets/{id}/photometry` | `GET` | `PhotometryResponse` | Forced aperture/PSF fluxes per band with 1-sigma errors and SNR. |
| `/api/v1/targets/{id}/lightcurve` | `GET` | `LightCurveResponse` | Strictly like-wavelength photometric time series. |
| `/api/v1/targets/search` | `GET` | `SearchResponse` | Coordinate parser and CDS SIMBAD astronomical target resolver. |

---

## 3. Detailed Request & Response Schemas

### 3.1 Capabilities (`GET /api/v1/capabilities`)
Reports system capabilities:
```json
{
  "version": "6.0.0",
  "api_version": "v1",
  "git_hash": "71a9daaaa9d8b27d415c2d79d1be389da460baff",
  "environment": "production",
  "capabilities": {
    "live_archive": {"enabled": true, "reason": "IRSA TAP and SkyView reachability active."},
    "demo_cache": {"enabled": true, "reason": "Precomputed cutouts and photometry available for 6 targets."},
    "exports": {"enabled": true, "reason": "CSV, IVOA VOTable, and FITS table exports enabled."},
    "spectral_differencing": {"enabled": true, "reason": "ZOGY difference imaging restricted strictly to matched wavelengths."},
    "space_motion_propagation": {"enabled": true, "reason": "Astropy apply_space_motion with Gaia DR3 proper motions enabled."}
  }
}
```

### 3.2 Target Detail (`GET /api/v1/targets/wise0855`)
Includes high-precision proper motions, parallax, and peer-reviewed literature citations:
```json
{
  "id": "wise0855",
  "name": "WISE 0855-0714",
  "ra_deg": 133.79513,
  "dec_deg": -7.24515,
  "ra_sexagesimal": "08:55:10.831",
  "dec_sexagesimal": "-07:14:42.54",
  "target_type": "Y-Dwarf (Sub-stellar Brown Dwarf, T_eff ~ 250 K)",
  "description": "Coldest known sub-stellar brown dwarf outside Solar System; high proper motion (~8.2 arcsec/yr).",
  "public_exposures_count": 5,
  "has_demo_cache": true,
  "space_motion": {
    "pm_ra_cosdec_mas_yr": -8120.0,
    "pm_dec_mas_yr": 2690.0,
    "parallax_mas": 448.4,
    "radial_velocity_km_s": null,
    "epoch_ref": 2014.0,
    "source": "Luhman, K. L. (2014) ApJL, 786, L18; Kirkpatrick et al. (2021) ApJS, 253, 7"
  },
  "known_mag_ab": {"WISE_W2": 14.02, "Array_5_3.82um": 18.48},
  "citations": [
    "Luhman, K. L. (2014). Discovery of a ~250 K Brown Dwarf at 2 pc from the Sun. ApJL, 786, L18.",
    "Kirkpatrick, J. D. et al. (2021). The Field Substellar Mass Function. ApJS, 253, 7."
  ]
}
```

### 3.3 Difference Imaging (`GET /api/v1/difference`)
Validates wavelength matching. Returns `BAND_MISMATCH` if wavelengths differ:
```json
// Example: Valid matched pair (Detector 6, 4.42 μm)
{
  "valid": true,
  "status": "success",
  "method": "ZOGY (Zackay, Ofek, & Gal-Yam 2016)",
  "epoch_a": {
    "exposure_id": "SPHEREx_D6_60789_752254",
    "mjd": 60789.752254,
    "detector": 6,
    "band": "Band 6 (4.42 μm)",
    "wavelength_um": 4.42
  },
  "epoch_b": {
    "exposure_id": "SPHEREx_D6_60789_752458",
    "mjd": 60789.752458,
    "detector": 6,
    "band": "Band 6 (4.42 μm)",
    "wavelength_um": 4.42
  },
  "band_matched": true,
  "scorr_max": 24.85,
  "scorr_min": -4.12,
  "scorr_mean": 0.04,
  "scorr_std": 1.08,
  "provenance": {"source": "precomputed", "git_hash": "71a9daaaa9d8b27d415c2d79d1be389da460baff"}
}
```

### 3.4 Scientific Validation (`GET /api/v1/validation`)
Serves dynamic, auditable verification figures directly from `validation/` CSV data:
```json
{
  "pipeline_version": "6.0.0",
  "metrics": [
    {
      "name": "clean_fpr_5sigma_per_deg2",
      "value": 41.52,
      "unit": "candidates / deg^2",
      "status": "verified",
      "description": "Unvetoed candidates per deg^2 on 2.7 deg^2 field at 5.0 sigma. 95% Poisson CI: [34.21, 49.91]."
    },
    {
      "name": "veto_rejection_efficiency_5sigma_pct",
      "value": 88.4,
      "unit": "percent",
      "status": "verified",
      "description": "Percentage of raw detections successfully rejected by morphological and mask vetoes."
    },
    {
      "name": "depth_5sigma_ab_d6",
      "value": 18.06,
      "unit": "mag (AB)",
      "status": "verified",
      "description": "5-sigma point-source sensitivity in Detector 6 (4.42 μm) derived from propagated VARIANCE array."
    },
    {
      "name": "completeness_50pct_ab",
      "value": 17.30,
      "unit": "mag (AB)",
      "status": "verified",
      "description": "Empirical 50% completeness magnitude on difference imaging (sigma_diff = sqrt(2) * sigma_single)."
    },
    {
      "name": "star_mask_mover_loss_rate",
      "value": "Under Review",
      "unit": "percent",
      "status": "under_review",
      "description": "Measurement of real mover losses caused by bright star masking is undergoing Phase 2.9 re-calibration."
    }
  ],
  "audit_reports": [
    {"title": "Phase 2.8 Result Sanity Audit", "path": "docs/validation_audit.md"},
    {"title": "API Contract and Data Shape Audit", "path": "docs/API_CONTRACT_AUDIT.md"},
    {"title": "Scientific References & Catalogs", "path": "docs/references.md"}
  ],
  "last_updated": "2026-11-14T10:35:00Z"
}
```

---

## 4. Error Code Catalog (RFC 7807)

| Error Code | HTTP Status | Title | Trigger Condition |
| :--- | :--- | :--- | :--- |
| `TARGET_NOT_FOUND` | 404 | Target Not Found | Requested target slug does not exist in target registry. |
| `NO_PUBLIC_DATA` | 404 | No Public SPHEREx Data | Target has 0 public exposures in IRSA `spherex.obscore` (e.g. RW Aurigae). |
| `RAW_CUTOUT_NOT_FOUND` | 404 | Raw Cutout Not Found | Float32 raw binary array is not cached for the target. |
| `BAND_MISMATCH` | 422 | Wavelength Mismatch in Difference Pair | Epochs have different spectral bands/wavelengths without a spectral model. |
| `INVALID_COORDINATES`| 400 | Invalid Coordinates | Coordinates out of physical bounds `[0, 360)` or `[-90, +90]`. |
| `MISSING_PARAMETERS` | 400 | Missing Parameters | Required query parameters are missing. |
| `CUTOUT_ERROR` | 500 | Cutout Retrieval Error | Archive query failure or FITS processing error. |

---

## 5. Dual-Tier Deployment Architecture

SPHEREx Hunter supports two complementary execution environments:

### 5.1 Tier 1: Cloud Serverless Edge (Vercel)
* **Base URL:** `https://spherex-hunter-vercel.vercel.app/api`
* **Entrypoint:** `api/index.py` (FastAPI Serverless Function)
* **Design Philosophy:** Zero external compilation, zero-cost ($0 Hobby tier), ultra-low latency (<50ms).
* **Endpoints Supported:**
  - `GET /api/cutout?target={key}`: Instant calibrated multi-epoch cutouts with base64 PNGs from `api/demo_data/*.json`.
  - `GET /api/scene?target={key}`: Authentic scene graph, layer tree, and coordinate frames.
  - `GET /api/spectrum?target={key}`: 102-band infrared spectrophotometry.
  - `GET /api/gaia?target={key}`: Gaia DR3 astrometric catalogue.
  - `GET /api/targets` & `GET /api/benchmarks`: Target manifests.
  - `GET /api/health`: Deployment liveness check.

### 5.2 Tier 2: Local Scientific Compute Engine (FastAPI / Uvicorn)
* **Base URL:** `http://127.0.0.1:8000/api` and `http://127.0.0.1:8000/api/v1`
* **Entrypoint:** `backend/main.py`
* **Capabilities:**
  - Live TAP queries to NASA IRSA (`2MASS`, `DSS2`, `SPHEREx`) and ESA Gaia DR3 across arbitrary sky coordinates.
  - Astropy ZScale normalization, dynamic WCS reprojection, and ZOGY optimal difference imaging.
  - **OPT-1 Concurrent FITS Downloads:** Parallel download of multi-epoch FITS via `concurrent.futures.ThreadPoolExecutor`.
  - **OPT-2 Background Disk Pruning:** Asynchronous cache cleanup running on a daemon thread.
  - **OPT-3 Memory Circuit Breaker:** In-memory 5s TTL cache with `threading.RLock()` preventing re-entrant locks.
  - **OPT-5 Lazy Git Metadata:** Deferred `git rev-parse` evaluation avoiding cold-start import lag.

