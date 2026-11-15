# Feature Specification: SPHEREx Sky Viewer & Time-Domain Moving Object Hunter
**Feature ID:** `001-spherex-sky-viewer`  
**Challenge:** NASA Space Apps Challenge 2026 — Planet X and SPHEREx  
**Team:** RIP (Coimbatore, India)  
**Status:** In Review / Specification Complete  

---

## 1. Executive Summary & Problem Statement
SPHEREx scans the entire celestial sphere every six months across 102 near-infrared bands. Near-Earth asteroids, Kuiper Belt objects, brown dwarfs, and hypothetical outer solar system bodies (Planet X) shift position between successive sky passes. However, billions of stars and huge image files make manual inspection impossible.

This feature specifies a clean, public-facing web viewer that accepts sky coordinates (Right Ascension and Declination), retrieves time-ordered image cutouts from the SPHEREx mission and archival IRSA surveys, and plays them in an interactive flipbook comparator with difference imaging subtraction and on-the-fly spectroscopy, enabling any citizen scientist to spot moving objects and variable stars.

---

## 2. User Scenarios & Primary Workflows

### Scenario 1: Coordinate-Based Sky Flipbook
- **User Action:** User enters coordinates in either decimal degrees (e.g. `133.79513, -7.24515`) or sexagesimal notation (e.g. `08h55m10.831s, -7d14m42.53s`) and selects a Field of View (e.g., 3', 5', 10').
- **System Behavior:** System parses coordinates, queries NASA IRSA/SkyView archive cutouts across multiple observation epochs, renders calibrated noise-suppressed frames in chronological order, and begins smooth animated flipbook playback.
- **Outcome:** The user visually observes stationary stars while any moving object noticeably shifts between frames.

### Scenario 2: Benchmark Target Verification
- **User Action:** User clicks on any of the 5 NASA benchmark targets:
  1. **Barnard's Star:** High proper motion red dwarf ($10.36''/\text{yr}$)
  2. **Epsilon Indi B:** Brown dwarf binary ($4.70''/\text{yr}$)
  3. **WISE 0855-0714:** Cold sub-stellar Y-dwarf ($8.12''/\text{yr}$, RA `08h55m10.831s`, Dec `-7d14m42.53s`)
  4. **RW Aurigae:** Young T-Tauri variable star ($2.8\times$ flare amplitude)
  5. **R Draconis:** Mira pulsating giant ($3.4\times$ variability)
- **System Behavior:** Instantly loads verified multi-epoch cutouts with motion trajectory callouts and metadata.

### Scenario 3: Difference Imaging Subtraction ($I_2 - I_1$)
- **User Action:** User toggles "Difference Mode".
- **System Behavior:** Computes numerical subtraction $I_2 - I_1$. Stationary background stars cancel to zero (neutral gray), while moving objects produce a prominent positive/negative dipole pair, and variable stars show a bright flare or deep trough.

### Scenario 4: 6-Detector Array Co-Addition & 102-Band Spectral Curve
- **User Action:** User inspects the properties sidebar.
- **System Behavior:**
  - Displays co-added Signal-to-Noise Ratio (SNR) boost across SPHEREx's 6 detector arrays (0.75 to 5.0 μm).
  - Generates on-the-fly 102-band infrared Spectral Energy Distribution (SED) identifying molecular absorption signatures ($H_2O\text{ at }3.05\,\mu\text{m}$, $CH_4\text{ at }3.30\,\mu\text{m}$, $CO_2\text{ at }4.27\,\mu\text{m}$).

### Scenario 5: URL Deep-Linking & Universal Embedding
- **User Action:** User shares or embeds a URL formatted as:
  `http://<host>/app/index.html?ra=133.79513&dec=-7.24515&fov=3.0`
- **System Behavior:** Web tool immediately loads with the specified coordinates and FOV without user interaction.

---

## 3. Functional Requirements

### 3.1 Astronomical Data Ingestion & Reduction
- **FR-1:** Coordinate parser must accept both decimal degrees and sexagesimal string formats (`hh:mm:ss`, `dd:mm:ss`) via Astropy `SkyCoord`.
- **FR-2:** Ingestion service must query NASA IRSA / SkyView archive cutouts centered on target coordinates at user-selected FOV (1.0 to 15.0 arcminutes).
- **FR-3:** Scientific image calibration must subtract sky background and apply $\ge 2.0\sigma$ noise floor thresholding to eliminate CRT-style sensor noise.
- **FR-4:** Image stretch must use inverse hyperbolic sine (`AsinhStretch`) or square-root scaling to preserve high dynamic range cores without blowing out faint halos.

### 3.2 Time-Domain Flipbook & Blink Comparator
- **FR-5:** Flipbook must cycle through chronological observation passes (Pass 1 May 2025, Pass 2 Nov 2025) with adjustable playback speed (0.5 to 8.0 FPS).
- **FR-6:** Flipbook transport must support Play/Pause, Step Forward, Step Backward, Jump to Start, and Jump to End.
- **FR-7:** Difference imaging mode must subtract normalized Epoch 1 from Epoch 2, displaying motion dipoles with zero residual noise.

### 3.3 Astrometric Telemetry & Spectral Diagnostics
- **FR-8:** System must calculate sub-pixel proper motion shift vector ($\Delta\alpha, \Delta\delta$) in arcseconds.
- **FR-9:** System must generate the full 102-band near-infrared spectral curve ($0.75 - 5.00\,\mu\text{m}$) mapped to SPHEREx's 6 linear variable filter (LVF) detector arrays.
- **FR-10:** Contamination flags, signal-to-noise ratio co-add boost ($4.12\times$ across 6 arrays), and estimated blackbody temperatures must be displayed in the telemetry inspector.

### 3.4 User Interface & Responsiveness
- **FR-11:** Minimalist, distraction-free astronomy viewport adhering to dark scientific workstation aesthetic.
- **FR-12:** Visual reticle crosshair with optional motion guidance callout rings (`GUIDES: ON/OFF`).
- **FR-13:** Citizen Science candidate discovery logger allowing users to flag moving objects with RA/Dec coordinates.

---

## 4. Success Criteria

1. **Precision & Accuracy:** 100% of benchmark targets (Barnard's Star, Epsilon Indi B, WISE 0855, RW Aurigae, R Draconis) load correct coordinates within $< 0.001^\circ$ precision.
2. **Proper Motion Detection:** WISE 0855 ($8.12''/\text{yr}$) and Barnard's Star ($10.36''/\text{yr}$) display clear, distinct spatial shifts between Pass 1 and Pass 2 observable by a layperson in $< 3$ seconds of viewing.
3. **Difference Map Purity:** Difference images show complete cancellation of static field stars with RMS residual $< 5\%$, isolating moving dipole pairs.
4. **Latency & Performance:** Web tool renders frames and responds to coordinate changes with frame rates $\ge 30$ FPS and API responses $< 1500\text{ ms}$.
5. **Universal Accessibility:** Coordinates queryable via URL parameters on standard modern web browsers without external plugins or authentication.
