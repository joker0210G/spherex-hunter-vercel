# 📋 Frontend Contract Issues & Inconsistencies Log
> **SPHEREx Hunter Observatory** | Phase: Stage A Contract Audit
> **Document Purpose:** Strictly per instructions, any real frontend bug, hardcoding, or architectural mismatch found during the backend alignment is recorded here without silent patching of frontend science logic.

---

### 1. `CADC` Domain Typo in `loadSceneState`
* **File:** `frontend/index.html` (line 1484)
* **Code:** `https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.jp/en/search/?collection=NEOSSAT&target=...`
* **Issue:** Uses Japanese country code `.gc.jp` instead of the Canadian Astronomy Data Centre canonical `.gc.ca`.
* **Impact:** Clicking the CADC link in the layer manager provenance fails DNS resolution unless redirected.
* **Recommended Frontend Fix:** Update domain to `.gc.ca`.

---

### 2. Static Command Palette Catalog (`Ctrl+K`)
* **File:** `frontend/index.html` (lines 3253–3265)
* **Code:** Iterates over hardcoded local array `commandItems` containing only 5 static presets.
* **Issue:** Typing arbitrary astronomical names or coordinates does not query a backend search endpoint (`/api/v1/targets/search?q=...`) to dynamically resolve SIMBAD objects or parse sexagesimal coordinates.
* **Impact:** Users cannot discover candidates or external targets via keyboard search.
* **Recommended Frontend Fix:** Hook `input` event on `#commandPaletteInput` to `GET /api/v1/targets/search?q={query}` with debouncing.

---

### 3. Hardcoded Photometry Array Cards
* **File:** `frontend/index.html` (lines 683–718)
* **Code:** HTML contains hardcoded AB magnitudes and signal-to-noise ratios (`Array 1: 18.2 AB mag, S/N 6.8`, `Array 6: 20.1 AB mag, S/N 22.4`).
* **Issue:** Selecting different targets (e.g. Barnard's Star vs. WISE 0855) does not update the photometry cards; they remain static across all astronomical objects.
* **Impact:** Photometry tab shows non-truthful, uncalibrated flux values for non-default targets.
* **Recommended Frontend Fix:** Hook tab activation to `GET /api/v1/targets/{id}/photometry` and dynamically render array cards with verified flux values, units ($\mu\text{Jy}$ / AB mag), and uncertainties.

---

### 4. Timeline Dock Multi-Epoch Strip Disconnected from Public Exposures
* **File:** `frontend/index.html` (lines 755–780)
* **Code:** Timeline flipbook scrubber toggles only between Frame 1 and Frame 2.
* **Issue:** Does not fetch or display the real multi-epoch exposure sequence from the backend (`GET /api/v1/targets/{id}/exposures`), missing MJD timestamps, detector IDs, and passband indicators for real SPHEREx flight exposures.
* **Impact:** Citizen scientists and judges cannot see which specific SPHEREx or 2MASS exposures compose the observation baseline.
* **Recommended Frontend Fix:** Call `GET /api/v1/targets/{id}/exposures` and populate interactive timeline ticks.

---

### 5. Simulated Light Curve Canvas
* **File:** `frontend/index.html` (lines 2800–2840)
* **Code:** `initLightCurveChart()` generates synthetic historical points (2MASS 1999 -> SPHEREx 2025) with hardcoded random offsets.
* **Issue:** Photometric time series is not backed by authentic catalog forced photometry or IRSA time-series points.
* **Impact:** Violates scientific honesty rule if perceived by judges as real multi-epoch light curves.
* **Recommended Frontend Fix:** Query `GET /api/v1/targets/{id}/lightcurve` which returns per-exposure fluxes at like wavelengths with authentic uncertainties and timestamps.

---

### 6. Generic Error Toasts on Cutout Failures
* **File:** `frontend/index.html` (lines 2280–2295)
* **Code:** `showToast('Failed to load FITS cutout: ...')` catches generic HTTP exceptions without parsing RFC 7807 `problem+json` error types.
* **Issue:** Does not distinguish `NO_PUBLIC_DATA` (404) from upstream archive timeouts (504) or server errors (500).
* **Impact:** Users cannot tell whether a target simply has no coverage or if an external NASA server is experiencing downtime.
* **Recommended Frontend Fix:** Parse `detail.code` or RFC 7807 `title` from response and display tailored banners.
