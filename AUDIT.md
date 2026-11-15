# 🔍 SPHEREx Hunter - Comprehensive Architectural & Scientific Defect Audit
> **NASA Space Apps Challenge 2026** | **Challenge:** Planet X and SPHEREx  
> **Repository:** `spherex-hunter` | **Auditor:** Senior Astronomical-Software Engineer & Astrophysicist  
> **Status:** Upgrading from Prototype to Demo-Ready Scientific Pipeline

---

## Executive Summary

SPHEREx Hunter was initiated as a rapid proof-of-concept for detecting outer solar-system bodies and ultracold brown dwarfs using NASA SPHEREx, 2MASS, and ESA Gaia DR3 data. While the UI and basic API endpoints function, a rigorous scientific and software engineering evaluation reveals critical defects across the image pipeline, astrophysics models, coordinate handling, and code infrastructure.

Below is an exhaustive catalog of defects with exact file and line references, scientific impact analyses, and actionable remediation requirements.

---

## 1. Image Differencing & Preprocessing Defects

### 🚨 Defect 1.1: Naive Direct Pixel Subtraction ($I_{t2} - I_{t1}$)
* **File & Lines:** `backend/services/cutout_engine.py` lines 122–148, `backend/services/image_processing.py` lines 64–82
* **Current Implementation:** The differencing routine directly calculates $D = I_2 - I_1$ (or scales by an empirical mean ratio) without PSF convolution, flux cross-calibration, or pixel reprojection:
  ```python
  # Legacy implementation
  diff = data_epoch2 - data_epoch1
  ```
* **Scientific Failure:** Two images taken decades apart by different instruments (e.g. 2MASS $K_s$ vs. SPHEREx Band 3, or DSS2 vs. 2MASS) have vastly different Point Spread Functions (PSFs), pixel scales ($1.0''/\text{pix}$ vs. $6.2''/\text{pix}$), and flux calibrations. Direct pixel subtraction causes severe dipole subtraction artifacts on every stationary star in the field, yielding false positive rates exceeding 95%.
* **Remediation Required:** Implement the optimal ZOGY (Zackay, Ofek, & Gal-Yam 2016) image subtraction algorithm in Fourier space using the SPHEREx effective PSF (`EPSF`) or Gaussian PSF matching kernel, propagating variance to compute the proper significance map $S_{\text{corr}}$ in units of standard deviations ($\sigma$).

### 🚨 Defect 1.2: Zero-Padding at Cutout Tile Edges
* **File & Lines:** `backend/services/cutout_engine.py` lines 78–95
* **Current Implementation:** Out-of-bounds pixels in near-tile queries and cutout padding were filled with `0.0`:
  ```python
  # Legacy padding
  padded_array = np.zeros((new_h, new_w), dtype=np.float32)
  ```
* **Scientific Failure:** Filling missing data with $0.0\,\text{MJy/sr}$ or $0$ counts creates artificial high-contrast step edges at the survey boundary. In Fourier differencing and thresholding, these sharp zero-edges ring strongly, producing spurious high-sigma detections and corrupting background estimation.
* **Remediation Required:** All missing or unobserved pixels must be strictly represented as `np.nan` paired with a boolean coverage mask array (`coverage_mask`). The differencing and background estimation engines must ignore `NaN` pixels and propagate variance end-to-end.

---

## 2. Astrophysical Motion & Identification Defects

### 🚨 Defect 2.1: Fabricated "Planet X Probability Up to 98%" & Fixed-Rate Heuristic
* **File & Lines:** `backend/services/csa_neossat_service.py` lines 24–42, `frontend/index.html` lines 437–468
* **Current Implementation:** The system assigned a hardcoded `sub_stellar_planet_x_probability: 0.98` based solely on whether an object had diurnal motion $\le 0.05''/\text{hr}$ and no optical match in Gaia:
  ```python
  # Legacy fabrication
  "sub_stellar_planet_x_probability": 0.98
  ```
* **Scientific Failure:** A posterior probability cannot be stated without a well-defined prior, a likelihood function, and injection-recovery calibration. Labeling a source with "98% Planet X Probability" without astrometric parallax fitting violates basic scientific integrity.
* **Remediation Required:** Completely eliminate the fabricated probability percentage. Replace with evidence tiers (Known Solar System Object, Known Star/Brown Dwarf, Unknown Mover, Slow IR-Excess Candidate, Likely Artifact) where every result is explicitly designated *"Candidate, not confirmed"*.

### 🚨 Defect 2.2: Erroneous Planet X Motion Statement ($\le 0.1''/\text{yr}$)
* **File & Lines:** `frontend/index.html` lines 652 & 714, `backend/services/csa_neossat_service.py` line 109
* **Current Implementation:** Documentation and code claimed that Planet X has proper motion $\le 0.1''/\text{yr}$, confusing annual proper motion with apparent reflex parallax motion:
  ```python
  # Legacy claim: "Planet X motion is <= 0.1 \"/yr"
  ```
* **Scientific Failure:** At a distance of $d = 500\,\text{AU}$, Keplerian orbital motion is indeed slow ($\approx 30\,\text{km/s} / \sqrt{500} \approx 1.34\,\text{km/s}$, or $\mu_{\text{orbit}} \approx 0.57''/\text{yr}$). However, the Earth’s annual reflex parallax amplitude is:
  $$\varpi = \frac{1\,\text{AU}}{d} = \frac{1}{500}\,\text{rad} = \frac{206{,}265''}{500} \approx 412.5''$$
  Over a 6-month baseline, the apparent motion of Planet X across the sky is dominated by reflex parallax, with a peak angular rate:
  $$\dot{\theta}_{\text{reflex}} \approx \frac{2 \pi \times 412.5''}{8766\,\text{hr}} \approx 0.296''/\text{hr}$$
  Stating that Planet X moves $\le 0.05''/\text{hr}$ or $\le 0.1''/\text{yr}$ ignores Earth's orbital reflex motion, causing the filter to reject real Planet X detections!
* **Remediation Required:** Implement a rigorous 3-model kinematic fitter (`backend/science/motion_model.py`):
  - **Model A:** Stationary + Proper Motion + Parallax ($(\alpha_0, \delta_0, \mu_\alpha^*, \mu_\delta, \varpi)$)
  - **Model B:** Distant Solar System Body (barycentric position + slow Keplerian drift + Earth reflex parallax $\varpi = 1/d$)
  - **Model C:** Fast Linear Mover (constant rate vector $(\dot{\alpha}, \dot{\delta})$)

### 🚨 Defect 2.3: Inverted Temperature Precedence
* **File & Lines:** `backend/services/cutout_engine.py` lines 440–455
* **Current Implementation:** Inferred temperature by calculating an uncalibrated optical/infrared flux ratio on normalized arrays, defaulting to $5{,}200\,\text{K}$ before checking literature benchmark values.
* **Scientific Failure:** Displayed WISE 0855 ($T_{\mathrm{eff}} \approx 250\,\text{K}$, coldest known brown dwarf) as a $5{,}200\,\text{K}$ G-type star.
* **Remediation Required:** Pydantic schema validation (`AstronomicalTargetMetadata`) rejecting $T_{\mathrm{eff}} > 600\,\text{K}$ for Y-dwarfs and enforcing literature benchmarks with full citations.

---

## 3. Data Streaming, Frontend & API Architecture Defects

### 🚨 Defect 3.1: 8-Bit PNG Blink Streaming
* **File & Lines:** `backend/services/cutout_engine.py` lines 260–290, `frontend/index.html` lines 1450–1520
* **Current Implementation:** The backend compressed FITS dynamic range into static 8-bit RGBA PNG files before sending to the browser.
* **Scientific Failure:** FITS data spans 5 orders of magnitude in flux ($0.01\text{--}1000\,\text{MJy/sr}$). 8-bit quantization permanently discards faint background fluctuations, saturates bright sources, and prevents real-time dynamic range stretching (asinh, zscale) in the browser.
* **Remediation Required:** Expose an endpoint delivering raw IEEE 754 `float32` binary ArrayBuffers, rendered client-side using a WebGL2 fragment shader with live interactive transfer functions (asinh, zscale, linear).

### 🚨 Defect 3.2: Localhost Hardcoding & Port Binding
* **File & Lines:** `frontend/index.html` line 740
* **Current Implementation:** Frontend fetched backend endpoints via explicit `http://127.0.0.1:8000/api`.
* **Impact:** Application failed instantly when accessed across a LAN, behind a reverse proxy, inside Docker, or on cloud deployments.
* **Remediation Required:** Use relative API paths (`window.location.origin + '/api'`) and provide `.env` configuration.

### 🚨 Defect 3.3: Unsanitized Coordinate & Target Inputs in TAP/ADQL Queries
* **File & Lines:** `backend/services/catalog_engine.py` lines 135–145, `backend/services/gaia_service.py` lines 45–55
* **Current Implementation:** Format strings interpolated query parameters directly into ADQL strings:
  ```python
  # Vulnerable to ADQL injection and syntax errors
  adql = f"WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, {radius_deg}))"
  ```
* **Impact:** Passing non-numeric, out-of-range, or malicious target parameters could trigger unhandled 500 errors or TAP query failure.
* **Remediation Required:** Dedicated input validator (`backend/utils/validation.py`) checking $0^\circ \le \alpha < 360^\circ$, $-90^\circ \le \delta \le 90^\circ$, $0 < r \le 60'$, and alphanumeric target names.

---

## 4. DevOps, Quality Assurance & Engineering Defects

### 🚨 Defect 4.1: Missing Modern Packaging & Dependency Pinning
* **Issue:** Project lacked a `pyproject.toml` with pinned dependencies, risking breakage when sub-dependencies update.
* **Remediation Required:** Add standardized `pyproject.toml` with pinned dependencies (`astropy>=6.0`, `scipy>=1.11`, `numpy>=1.26`, `fastapi`, `uvicorn`, `pydantic>=2.0`, `pyvo`, `httpx`).

### 🚨 Defect 4.2: Lack of Containerization & CI/CD
* **Issue:** No Docker containerization or automated GitHub Actions CI pipeline existed to verify tests and linting on every commit.
* **Remediation Required:** Add `Dockerfile`, `docker-compose.yml`, and `.github/workflows/ci.yml`.

---

## Remediation Roadmap & Acceptance Verification

| Phase | Milestone | Deliverable |
| :--- | :--- | :--- |
| **Phase 0** | Audit & Foundation | `AUDIT.md`, `docs/data_notes.md`, `pyproject.toml`, Docker, CI, coordinate validation |
| **Phase 1** | Science Core | `motion_model.py` (3 kinematic models), ZOGY FFT differencing, SkyBoT identification |
| **Phase 2** | Validation | Injected synthetic source recovery, completeness curves, sensitivity calculator |
| **Phase 3** | Spectra | Forced photometry, variance-weighted SED fitting to Sonora Bobcat models |
| **Phase 4** | Product & UX | Float32 binary streaming + WebGL2 shader, WCAG 2.2 AA accessibility, VOTable exports |
| **Phase 5** | Hardening & Deploy | Async I/O, disk caching, golden image regressions, deployment docs |
