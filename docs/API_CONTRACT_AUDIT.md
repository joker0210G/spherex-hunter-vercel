# 🔍 SPHEREx Hunter - Stage A: Comprehensive API Contract Audit
> **Document:** `docs/API_CONTRACT_AUDIT.md` | **Version:** 1.0.0
> **System Scope:** Backend FastAPI (`backend/`) Alignment with Redesigned Frontend (`frontend/index.html`)

---

## 1. Inventory of All Frontend Network Invocations

The production client application (`frontend/index.html`) performs 8 primary asynchronous HTTP requests. The contract audit details each method, endpoint, payload, consumer component, and parsed response keys below:

| # | Method | Endpoint / URL | Component | Request Parameters / Body | Exact Response Fields Read | Error Handling Behaviour |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `GET` | `/api/scene` | Inspector: Layers Tab (`#inspectorPanelLayers`) | Query: `fov` (float), `target` (opt str), `ra` (opt float), `dec` (opt float) | `status`, `target_key`, `target` (`name`, `ra_deg`, `dec_deg`, `object_type`, `spectral_type`, `total_pm_arcsec_yr`, `total_pm_mas_yr`, `effective_temp_k`, `evidence_tier`, `evidence_summary`, `confirmation_status`, `citations`), `epochs[]` (`id`, `name`, `survey`, `instrument`, `band`, `mjd`, `date`, `detector`, `wavelength_microns`, `pixel_scale_arcsec`, `status`, `target_coord.ra_deg`, `target_coord.dec_deg`, `target_coord.delta_theta_arcsec`, `target_coord.fov_warning`), `layers[]` (`id`, `name`, `type`, `visible`, `opacity`, `status`, `provenance`, `badge`, `band_matched`, `unmatched_reason`), `active_blink_pair`, `difference` (`valid`, `reason`) | Hides skeleton loader, unhides `#sceneError` banner with `#sceneErrorMessage` text |
| **2** | `GET` | `/api/cutout` | Main Astronomical Viewport (`#astroCanvas`, flipbook, difference) | Query: `ra` (float), `dec` (float), `fov` (float), `lod` (int 0..2), `target` (opt str) | `coordinates` (`ra_deg`, `dec_deg`, `fov_arcmin`), `epochs[0,1]` (`image_data`, `label`, `date`, `survey`, `band`), `difference_image` (`image_data`, `label`), `coverage_mask_image` (`image_data`), `transient_detection` (`status`, `offset_arcsec`, `snr`, `transient_type`, `source_ra`, `source_dec`, `notes`), `provenance` (`source`, `retrieved_at`) | Logs console error, shows dismissible floating toast alert |
| **3** | `GET` | `/api/gaia` | Viewport Reticle Overlay & Inspector Gaia DR3 Card | Query: `ra` (float), `dec` (float), `radius` (float arcmin) | `status`, `count`, `sources[]` (`source_id`, `ra`, `dec`, `phot_g_mean_mag`, `pmra`, `pmdec`, `total_pm_mas_yr`, `parallax`, `distance_pc`) | Logs console warning, defaults `gaiaSources` to empty array |
| **4** | `GET` | `/api/csa/neossat` | Target Inspector NEOSSat Card & Mission Codex Panel | Query: `ra` (float), `dec` (float), `radius` (float arcmin) | `status`, `verdict`, `verdict_text`, `known_solar_system_objects` (`count`, `objects[]`), `neossat_archive` (`count`), `cadc_search_url`, `links` | Logs console warning, silences failure |
| **5** | `GET` | `/api/spectrum` | Bottom Dock: 102-Band Spectrum Panel & Chart.js Canvas | Query: `ra` (float), `dec` (float), `target` (opt str) | `flux_microjanskys` (array 102 floats), `wavelengths_microns` (array 102 floats), `estimated_temp_k`, `detected_molecules`, `bands[]` (`flux_ujy`, `wavelength`) | Logs console warning, chart remains empty |
| **6** | `POST` | `/api/flag` | Citizen Science Candidate Flagging Modal (`#flagCandidateModal`) | Body (JSON): `ra`, `dec`, `candidate_name`, `motion_type`, `proper_motion_mas` | `status`, `message`, `candidate_id`, `candidate` | Alerts user via `alert()` dialog |
| **7** | `GET` | `/api/discoveries` | Inspector: Candidates Tab (`#candidatesListContainer`) | Query: None | Array of objects: `candidate_id`, `target_name`, `notes`, `ra`, `dec`, `object_type`, `evidence_tier`, `proper_motion_mas`, `created_at` | Renders inline error card inside candidates list container |
| **8** | `GET` | `/api/discoveries/export/csv` | Inspector Candidates Tab: CSV Export Button | Query: None | Streaming text/csv attachment (`SPHEREx_Discoveries_Export.csv`) | Native browser download dialog |

---

## 2. Complete Inventory of UI Features Requiring Backend Data

Beyond the 8 current network calls, the full frontend feature matrix requires structured backend telemetry:

1. **Layers / Epoch Tree (`#inspectorPanelLayers`)**: Needs per-epoch MJD, observation dates, instrument/survey, WCS wavelength at pixel center, space-motion displacement ($\Delta \theta$), and passband difference eligibility.
2. **Target Astrometry Tab (`#inspectorPanelTarget`)**: Needs ICRS astrometry ($\alpha, \delta$), total proper motion $\mu$ (both in $''/\text{yr}$ and $\text{mas/yr}$), parallax $\varpi$, physical distance ($d$ in $\text{pc}$ and $\text{ly}$), effective temperature $T_{\text{eff}}$, SIMBAD/Gaia citations, and evidence tier badge.
3. **Candidates Discovery Tab (`#inspectorPanelCandidates`)**: Needs synchronized candidate coordinates, S/N, evidence JSON, motion model summary ("UNCONSTRAINED" for baselines $<60\text{d}$), cross-match verifications, and deletion support.
4. **Photometry Cards (`#inspectorPanelPhotometry`)**: Needs live 6-detector SPHEREx array forced photometry ($0.75\,\mu\text{m}$ to $4.42\,\mu\text{m}$) in $\mu\text{Jy}$ and AB magnitudes with 1-sigma uncertainties and aperture method.
5. **Timeline Epoch Strip (`#dockPanelTimeline`)**: Needs public exposure list (`GET /api/v1/targets/{id}/exposures`) showing MJD timestamps, detector IDs, and wavelength coverage markers for each flight exposure.
6. **Spectrum Dock Tab (`#dockPanelSpectrum`)**: Needs 102-band flux vector ($\mu\text{Jy}$), wavelength vector ($\mu\text{m}$), and molecular absorption markers ($H_2O, CH_4, CO_2, CO$).
7. **Light Curve Dock Tab (`#dockPanelLightCurve`)**: Needs multi-epoch photometric time-series at matched wavelengths with authentic error bars and observation timestamps.
8. **Astronomical Canvas Viewport (`#astroCanvas`)**: Needs 8-bit PNG preview tiles, float32 raw data buffer (`/cutout/raw`), Bramich difference map, and transparent NaN coverage masks for out-of-bounds pixels.
9. **Difference Pair Validation**: Needs explicit reason codes (`BAND_MISMATCH`, `NO_OVERLAP`, `DIFFERENT_DETECTOR`) when differencing is disabled.
10. **Mission Codex / Phase 2 Validation Modal**: Needs live benchmark summaries (`GET /api/v1/validation`), including 50% completeness limit ($17.3\,\text{AB mag}$), FPR rate ($29.02\,\text{deg}^{-2}$), SkyBoT recoveries (54 objects), and static validation plots.
11. **Command Palette Search (`Ctrl+K`)**: Needs live coordinate parsing and astronomical target search (`GET /api/v1/targets/search?q=...`) to resolve SIMBAD targets on the fly.
12. **Capabilities & System Health**: Needs `GET /api/v1/capabilities` and `GET /api/v1/status` reporting live archive reachability, demo_cache status, and latency.
13. **Permalinks (`#target=...&mode=...&frame=...`)**: Needs stable target and candidate IDs that survive page reloads.

---

## 3. Gap Analysis: Frontend UI Needs vs. Current Backend Endpoints

| UI Feature / Need | Current Backend Endpoint | Gap Analysis (Shape / Units / Data / Speed) | Planned Fix in Stage B/C |
| :--- | :--- | :--- | :--- |
| **Unified Scene Layer Tree** | `GET /api/scene` | Legacy unversioned route. Does not return explicit physical units dictionary `{value, unit, uncertainty}`. | Implement `GET /api/v1/targets/{id}/scene` with strict Pydantic v2 schema, explicit physical units, and RFC 7807 error envelopes. Alias `/api/scene` for backward compatibility. |
| **Astronomical Cutout Viewport** | `GET /api/cutout` | Returns 8-bit Base64 PNGs. Lacks raw 32-bit floating-point scientific pixel arrays for precision photometric measurements; missing HTTP ETags. | Implement `GET /api/v1/cutout` (with Base64 preview) and `GET /api/v1/cutout/raw` (streaming IEEE 754 float32 ArrayBuffer + JSON WCS header), ETags, and Cache-Control. |
| **Difference Map & Validation** | Embedded in `/api/cutout` | No dedicated standalone endpoint for arbitrary epoch-pair differencing; mismatch rejection reasons are unstructured strings. | Implement `GET /api/v1/difference` accepting `epoch_a` and `epoch_b` with formal ZOGY $S_{\text{corr}}$ scoring and structured `BAND_MISMATCH` rejection codes. |
| **Target Presets & Metadata** | `GET /api/targets` | Simple JSON dictionary without citations, physical units, or pagination. | Implement `GET /api/v1/targets` and `GET /api/v1/targets/{id}` with complete SIMBAD/Gaia provenance, bibliography, and physical schema. |
| **Target Quick Search (`Ctrl+K`)** | None (client-side static list) | Frontend searches 5 local items; cannot resolve SIMBAD queries, coordinates, or new candidate IDs. | Implement `GET /api/v1/targets/search?q={query}` supporting SIMBAD query resolution, coordinate parsing, sanitization, and rate-limiting. |
| **Public Exposures List** | None (missing) | Timeline epoch dock only toggles 2 hardcoded frames; cannot show real multi-epoch flight coverage. | Implement `GET /api/v1/targets/{id}/exposures` with spatial containment queries on `spherex.obscore`, MJD, detector, and matched pairs. |
| **Candidates List & Filtering** | `GET /api/discoveries` | Flat unpaginated JSON array; lacks S/N filtering, evidence tier filtering, and starlight residual toggling. | Implement `GET /api/v1/targets/{id}/candidates` and `GET /api/v1/candidates` with sorting, tier filters, pagination, and `include_known_star_residuals=false` default. |
| **Candidate Flagging** | `POST /api/flag` | Basic SQLite logging; lacks duplicate coordinate collision checks and rate-limiting. | Implement `POST /api/v1/candidates/flag` with coordinate deduplication ($\le 2''$), input sanitization, and rate-limiting. |
| **Photometry Array Cards** | None (hardcoded in HTML) | HTML displays static values for Array 1..6; no dynamic calculation across different targets. | Implement `GET /api/v1/targets/{id}/photometry` returning forced aperture/PSF fluxes in $\mu\text{Jy}$ and AB magnitudes with uncertainties. |
| **Light Curve Dock Tab** | None (simulated in JS) | Client renders random mock curves; no connection to authentic multi-epoch flux data. | Implement `GET /api/v1/targets/{id}/lightcurve` returning epoch-by-epoch calibrated photometry at matching wavelengths. |
| **Gaia DR3 Cross-Match** | `GET /api/gaia` | Calls live ESA TAP without structured "unavailable" fallback when ESA is unreachable; no RFC 7807 problem json. | Implement `GET /api/v1/catalog/gaia` with structured status fallback, caching, and rate limiting. |
| **NEOSSat / Asteroid Tracking** | `GET /api/csa/neossat` | Functional, but lives on unversioned route; uses legacy CADC endpoint format. | Adopt `coolodu`'s `backend/services/neossat_service.py` under versioned endpoint `GET /api/v1/services/neossat` with SkyBoT + CADC integration. |
| **Validation Benchmark Data** | Static HTML in `#codexPanelValidation` | Benchmark metrics are static HTML strings; figures are not served via a versioned API. | Implement `GET /api/v1/validation` serving real benchmark numbers from Phase 2 runs, with figure routing under `/api/v1/validation/figures/{name}`. |
| **Capabilities & Health Readiness** | `GET /api/health` | Simple `{"status": "ok"}`; does not report upstream archive availability, demo cache status, or offline reasons. | Implement `GET /api/v1/capabilities` and `GET /api/v1/status` returning detailed component readiness, latency, and demo mode flags. |
| **Data Exports** | `GET /api/discoveries/export/csv` | Only exports basic CSV; lacks VOTable (IVOA standard) and multi-extension FITS exports. | Implement `GET /api/v1/export/csv`, `GET /api/v1/export/votable`, and `GET /api/v1/export/fits` with proper MIME types and UCD headers. |

---

## 4. Contract Governance & Architectural Decisions

1. **Versioned Route Prefix:** All new endpoints reside strictly under `/api/v1/`. Legacy routes (`/api/cutout`, `/api/scene`, `/api/spectrum`, etc.) are retained as deprecated proxies that forward transparently to `/api/v1/` until the frontend is migrated.
2. **Physical Unit Enforcement:** Every physical quantity is returned as a structured sub-object:
   ```json
   {
     "value": 8.149,
     "unit": "arcsec / yr",
     "uncertainty": 0.015,
     "source": "Gaia DR3 / SIMBAD"
   }
   ```
3. **Standard RFC 7807 Error Envelope:** Every failure uses `application/problem+json`:
   ```json
   {
     "type": "https://spherex-hunter.nasa.gov/errors/no-public-data",
     "title": "No Public Data Available",
     "status": 404,
     "code": "NO_PUBLIC_DATA",
     "detail": "Target RW Aurigae has 0 public SPHEREx flight exposures in IRSA archive.",
     "request_id": "spx-req-7f8a9b2c",
     "retryable": false
   }
   ```
4. **Authentic Provenance:** Every response payload carries `provenance`:
   ```json
   {
     "source": "demo_cache",
     "retrieved_at": "2026-11-14T15:30:00Z",
     "cache_version": "v1.0.0",
     "product_ids": ["SPHEREx_D6_60789_752254"]
   }
   ```
