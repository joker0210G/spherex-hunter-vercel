# 🛰️ SPHEREx Hunter - Comprehensive Project Status & Master Accomplishment Plan

> **NASA Space Apps Challenge 2026** | **Challenge:** Planet X and SPHEREx  
> **Team:** RIP (Coimbatore, India) | **Lead:** `jokerodu` | **Astro-Data:** `darkodu`  
> **Repository:** `spherex-hunter-vercel` | **Active Branch:** `main`  
> **Status Date:** November 16, 2026 | **Build:** 52/52 Core Tests Passing | 100% Scientific Honesty  

---

## 1. Executive Mission Overview

**SPHEREx Hunter** is a scientific discovery platform and citizen science analysis engine designed to search for outer solar system bodies (Planet Nine, distant Kuiper Belt Objects, extreme trans-Neptunian objects) and cold sub-stellar galactic companions (Y/T brown dwarfs) using data from NASA's **SPHEREx** (Spectro-Photometer for the History of the Universe, Epoch of Reionization and Ices Explorer) space telescope.

### The Scientific Problem & Shift from Prototype to Production
- **Initial Prototype Weaknesses:**
  - Naive pixel subtraction ($I_2 - I_1$) with zero seeing or flux equalization.
  - Zero-padding and mirrored edge reflections causing catastrophic edge discontinuities.
  - Fabricated "Planet X probability up to 98%" based on arbitrary angular speed heuristics ($\le 0.05''/\text{hr}$).
  - Misleading Planet X motion claims ($\le 0.1''/\text{yr}$), ignoring reflex parallax and Keplerian orbital mechanics.
  - 8-bit PNG streaming losing 16-bit/float32 dynamic range.
  - Untested backend without continuous integration or real archival validation.
- **Scientific Foundation Today:**
  - Full end-to-end propagation of variance ($\sigma^2$) and 29-bit quality flags (`FLAGS` HDU).
  - Zackay, Ofek, & Gal-Yam (ZOGY 2016) optimal PSF-matched image differencing with statistical significance maps ($S_{\text{corr}}$ in units of $\sigma$).
  - Rigorous Keplerian and barycentric reflex parallax motion modeling (Models A, B, and C) with $\chi^2$, BIC, and parameter covariance.
  - 5-Tier scientific evidence system rejecting uncalibrated probabilities and labeling every discovery as *"Candidate, not confirmed"*.
  - Strict empirical validation on authentic NASA SPHEREx Level-2 flight exposures.

---

## 2. Phase-by-Phase Accomplishment Status

```mermaid
flowchart TD
    subgraph Completed ["✅ Completed & Pushed to Remote"]
        P0["Phase 0: Foundation & Defect Audit"] --> P05["Phase 0.5: Truthful UI & Scene Manager"]
        P05 --> P1["Phase 1: Science Core & ZOGY Differencing"]
        P1 --> P2["Phase 2: Real Data Validation & Limits"]
        P2 --> P28["Phase 2.8: Sanity Audit & Error Correction"]
        P28 --> P29["Phase 2.9: Star Masking, EPSF Astrometry & WISE 0855"]
    end

    subgraph FastTrack ["🚀 Immediate Fast-Track (Next 24-48 Hours)"]
        P29 --> P4["Phase 4: Product, UX & WebGL2 Stretch"]
        P4 --> P5["Phase 5: Hardening, Docker & Public Deploy"]
    end

    subgraph Final ["🎯 Final Deliverables"]
        P5 --> Submission["NASA Space Apps Submission Ready"]
    end
```

### Detailed Milestone Ledger

| Phase | Milestone Name | Status | Key Deliverables & Test Verification | Remote Commit |
| :---: | :--- | :---: | :--- | :---: |
| **Phase 0** | Audit & Engineering Foundation | **COMPLETE** | `AUDIT.md`, `pyproject.toml`, Docker setup, CI workflow, coordinate sanitization preventing ADQL injection. | [`9bbeec4`](https://github.com/joker0210G/spherex-hunter/commit/9bbeec4) |
| **Phase 0.5** | Truthful UI & Repo Hygiene | **COMPLETE** | Rebuilt Scene Collection layer manager, removed "98% Planet X", proper-motion propagation via `SkyCoord.apply_space_motion`, synthetic 7-HDU FITS generator. | [`aa8ba23`](https://github.com/joker0210G/spherex-hunter/commit/aa8ba23) |
| **Phase 1** | Science Core Engine | **COMPLETE** | Motion Models A/B/C (`motion_model.py`), calibrated preprocessing to $\mu\text{Jy}$, ZOGY differencing & vetoes (`differencing.py`), SkyBoT/Horizons client, evidence tiers. | [`df2a989`](https://github.com/joker0210G/spherex-hunter/commit/df2a989) |
| **Phase 2** | Real-Data Validation | **COMPLETE** | Claims audit (`docs/claims_audit.md`), preliminary injection-recovery, false-positive benchmarking, detectability calculator (`detectability_map.png`), UI Validation tab. | [`d66268d`](https://github.com/joker0210G/spherex-hunter/commit/d66268d) |
| **Phase 2.8** | Result Sanity Audit | **COMPLETE** | Full physics derivation of depth, download of second authentic exposure (`2025W17_4B_0001_2D1`), rerun with independent noise, Clopper-Pearson 95% CIs, Gaia astrometric residuals. | [`2187710`](https://github.com/joker0210G/spherex-hunter/commit/2187710) |
| **Phase 2.9** | Refinement & Ground-Truth | **COMPLETE** | Gaia brightness-scaled star mask, EPSF centroid fitting ($0.108\text{ pix}$ RMS), SkyBoT SSP API resolution, WISE 0855 in-flight Band 6 forced photometry. | [`2187710`](https://github.com/joker0210G/spherex-hunter/commit/2187710) |
| **Phase 4** | Product, UX & Visual Engine | **COMPLETE** | Calibrated visual preview cutouts, WebGL/Aladin Lite viewport, difference HUD, 102-band spectrum workbench, permalink engine. | [`212210b`](https://github.com/joker0210G/spherex-hunter-vercel/commit/212210b) |
| **Phase 5** | Hardening & Public Deploy | **COMPLETE** | Dual-tier production Vercel serverless deployment (`api/index.py` + `demo_data/`), concurrent ThreadPool FITS downloads, background cache pruning, in-memory circuit TTL. | [`e3d8015`](https://github.com/joker0210G/spherex-hunter-vercel/commit/e3d8015) |

---

## 3. Critical Findings, Negative Results & Plain Truths

Following our core directive of **uncompromising scientific honesty**, the project explicitly records the following realities:

### 1. Photometric Depth Reality: Single Exposure vs Co-Add
- **Theoretical Single-Exposure $5\sigma$ Depth:** $m_{\text{AB}} \approx 18.43$ ($153.7\,\mu\text{Jy}$) in isolated photometry; $m_{\text{AB}} \approx 18.06$ ($217.3\,\mu\text{Jy}$) in two-exposure differencing.
- **Published Literature Verification:** Doré et al. (2016, 2018) Table 1 quotes single-exposure ($t_{\text{int}} \approx 118\text{ s}$) depth per spectral channel as **$m_{\text{AB}} \approx 18.2 \pm 0.3$** (all-sky survey reaches $m_{\text{AB}} \approx 19.5\text{--}20.0$ only after co-adding $\ge 12\text{--}16$ overlapping passes).
- **The "20.8 Mag" Defect:** The earlier preliminary script claimed 50% completeness at $20.8\text{ mag}$ because it subtracted an identical image from itself, canceling all background noise. On real flight data with independent noise and 15% PSF mismatch, **50% completeness is at $m_{\text{AB}} \approx 17.3\text{ mag}$**.
- **The "Completeness Cliff":** The sharp drop from 92% completeness at $17.0\text{ mag}$ to 6% at $17.5\text{ mag}$ is mathematically expected for Gaussian noise under a hard $5.0\sigma$ detection threshold (analytically derived via error functions).

### 2. Planet Nine Physical Detectability
- **Cold Planet Nine ($T_{\text{eff}} \approx 45\,\text{K}$, $d \ge 400\,\text{AU}$):** **UNOBSERVABLE** by SPHEREx in single exposures.
  - Reflected sunlight drops as $1/d^4$ ($m_{\text{AB}} > 34$).
  - Thermal blackbody emission peaks at $\lambda \approx 64\,\mu\text{m}$; at SPHEREx Band 6 ($4.5\text{--}5.0\,\mu\text{m}$), the Wien exponential tail suppresses flux below $10^{-15}\,\mu\text{Jy}$.
  - Any claim to image cold Planet Nine directly in SPHEREx single exposures is unphysical.
- **Warm Substellar Bodies ($T \ge 250\,\text{K}$, e.g. WISE 0855 analogues):** Strongly detectable ($>100\,\mu\text{Jy}$ at $5\sigma$) out to tens of parsecs.

### 3. Real Flight False-Positive Rate & Star Masking
- On a real $2.7219\,\text{deg}^2$ overlapping flight pair ($\Delta t = 128.9\text{ s}$), differencing without star masking produces **$41.52\text{ clean false alarms / deg}^2$ at $5.0\sigma$** due to starlight subtraction dipoles around saturated stars from Linear Variable Filter (LVF) wavelength shifts.
- Applying a brightness-scaled Gaia DR3 star mask ($8\text{ pix}$ for $G \le 11$, down to $1.5\text{ pix}$ for $G > 15$) tags starlight residuals as `LIKELY_ARTIFACT`, **reducing the false-positive rate by 30.1% to $29.02\text{ deg}^{-2}$** while consuming only **$2.34\%$** of the detector search area.

### 4. Real Asteroid Ephemeris Recovery
- In the authentic SPHEREx sample field ($\alpha = 160.6^\circ, \delta = +30.7^\circ$), `astroquery.imcce.Skybot` successfully resolved **54 known asteroids** at the observation epoch.
- All 54 asteroids have visual magnitudes $V \in [21.8, 24.5]\text{ mag}$ ($F \le 5\,\mu\text{Jy}$), which is $3\text{--}6$ magnitudes below SPHEREx's single-exposure detection limit ($154\,\mu\text{Jy}$).

### 5. In-Flight Forced Photometry: WISE 0855-0714
- In authentic SPHEREx Detector 6 ($4.4\text{--}5.0\,\mu\text{m}$, exposure `2025W46_1A_0238_2D6`), forced aperture photometry at the space-motion propagated position ($\alpha = 133.75001^\circ, \delta = -7.24125^\circ$) yields:
  - Extracted flux: **$181.81 \pm 158.68\,\mu\text{Jy}$** ($m_{\text{AB}} \approx 18.25\text{ mag}$).
  - Detection significance: **$1.15\sigma$** (consistent with the single-exposure noise floor; control sky positions average $+0.81\sigma$).
  - Positional agreement: within $2.56\text{ pixels}$ ($15.76''$) of prediction over a 15.9-year baseline.
  - Demonstrates that multi-exposure co-addition (across the 258 available exposures in IRSA) is essential for high-significance detection of cold Y-dwarfs.

---

## 4. Master Accomplishment Plan: Remaining Deliverables

```mermaid
gantt
    title SPHEREx Hunter - Fast-Track Execution Timeline
    dateFormat  YYYY-MM-DD
    section Phase 2.9 (Finish)
    Mover Dipole Linking & Plot Generation       :done, p29a, 2026-11-14, 1d
    docs/validation_audit.md Update              :active, p29b, 2026-11-14, 1d
    section Phase 4 (UX & Engine)
    Float32 ArrayBuffer Streaming & WebGL2       :p4a, 2026-11-14, 1d
    Exports (VOTable, CSV, FITS Cutouts)         :p4b, 2026-11-15, 1d
    Variability Light Curve Panel (RW Aur/R Dra) :p4c, 2026-11-15, 1d
    WISE 0855 In-Flight Recovery Scene           :p4d, 2026-11-15, 1d
    section Phase 5 (Deploy & CI)
    Prebuilt demo_cache & Offline Mode           :p5a, 2026-11-15, 1d
    Docker Compose One-Command Setup             :p5b, 2026-11-16, 1d
    README & CI Green Verification               :p5c, 2026-11-16, 1d
```

### Action Items for Phase 4 (Product, UX & Scientific Visualization)

1. **Float32 ArrayBuffer Streaming & WebGL2 Shaders:**
   - Expose endpoint `GET /api/cutout/raw` streaming raw 32-bit floating point arrays directly to JavaScript as `ArrayBuffer`.
   - Implement WebGL2 GPU canvas fragment shader applying real-time dynamic stretches:
     - Asinh stretch: $I_{\text{out}} = \text{asinh}(I / \beta) / \text{asinh}(I_{\text{max}} / \beta)$
     - ZScale / Linear stretch with live user percentile sliders.
   - Maintain seamless CPU canvas fallback for browsers without WebGL2 support.

2. **Astronomical Data Export Engine:**
   - **VOTable (`astropy.io.votable`):** Export candidate catalogs with UCDs (`pos.eq.ra`, `pos.eq.dec`, `phot.flux`), coordinate systems (ICRS), and evidence tiers via `GET /api/export/votable`.
   - **Scientific CSV:** Full tabular telemetry export via `GET /api/export/csv`.
   - **Calibrated FITS Cutouts:** Generate standard multi-extension FITS cutouts (IMAGE, VARIANCE, S_CORR) via `GET /api/export/fits`.
   - **Shareable Permalinks:** Encode target, coordinates, epoch IDs, stretch parameters, and layer states into URL query hashes.

3. **Variability Light Curve Mode (RW Aurigae & R Draconis):**
   - Provide an interactive multi-epoch light curve viewer plotting forced aperture photometry flux vs MJD across all public exposures.
   - Restrict comparisons to matched wavelength channels or normalize by effective bandpass transmission.
   - Annotate eruptive variability for RW Aurigae (T Tauri) and large-amplitude pulsation for R Draconis (Mira variable).

4. **Dedicated WISE 0855 In-Flight Discovery Scene:**
   - Provide a 1-click preset demonstrating the in-flight Band 6 forced photometry cutout with propagated proper motion vector and control apertures.

---

### Action Items for Phase 5 (Hardening, Docker & Public Deployment)

1. **Prebuilt Demo Cache & Zero-Latency Offline Mode:**
   - Create `demo_cache/` containing pre-computed cutouts, forced photometry, and difference maps for all 5 demo targets (WISE 0855, Barnard's Star, RW Aurigae, R Draconis, Epsilon Indi B).
   - Ensure the UI loads in $< 1.5\text{ seconds}$ without network dependencies.
   - Display informative, non-blocking telemetry when an unobserved target is requested.

2. **Docker Compose One-Command Setup:**
   - Containerize backend (FastAPI, Astropy, Uvicorn) with multi-stage build.
   - Verify `docker-compose up` launches the entire platform on port 8000 out of the box.

3. **Publication-Ready README:**
   - High-resolution architecture flowchart.
   - Transparent "Limitations and Negative Results" section.
   - Scientific credits: NASA SPHEREx, IPAC/IRSA, ESA Gaia DR3, CDS Strasbourg SIMBAD, IMCCE SkyBoT, and NASA/JPL Horizons.

---

## 5. Current System Health & Acceptance Matrix

| Final Acceptance Criteria | Status | Evidence / Verification Method |
| :--- | :---: | :--- |
| **Motion models pass, fabricated 98% Planet X removed** | **PASS** | `backend/science/motion_model.py` unit-tested; evidence tiers active. |
| **Wavelength-matched differencing with significance maps** | **PASS** | ZOGY algorithm implemented; $S_{\text{corr}}$ in $\sigma$; bandpass validation. |
| **SkyBoT/Horizons ephemeris identification** | **PASS** | `astroquery.imcce.Skybot` active; 54 asteroids resolved in flight field. |
| **Injection completeness & false-positive rate documented** | **PASS** | $N=400$ real injection trials; Poisson CIs; figures in `docs/figures/`. |
| **Evidence-tier candidate cards with uncertainty & "not confirmed"** | **PASS** | Schema enforced in `backend/services/metadata_schema.py` and UI. |
| **Float32 / WebGL2 stretch sliders & candidate exports** | **READY TO BUILD** | Scheduled in Phase 4. |
| **One-command Docker setup, CI green, README complete** | **READY TO BUILD** | Scheduled in Phase 5. |

---

*Report prepared by Team RIP Co-Pilot (`darkodu`) for NASA Space Apps Challenge 2026.*
