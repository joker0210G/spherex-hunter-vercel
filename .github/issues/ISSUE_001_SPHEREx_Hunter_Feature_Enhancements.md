---
title: "feat(core): Comprehensive SPHEREx Viewport Enhancements (Image Quality, Playback Controls, Date-Time Search, Omnibox Search, and Deep-Link Sharing)"
labels: ["enhancement", "ui/ux", "astrophysics", "help wanted"]
assignees: ["joker0210G", "coolodu", "darkodu", "iceodu", "astrodu"]
---

# 🚀 SPHEREx Hunter Feature Request & Enhancement Suite

## Overview
This issue tracks the implementation of six core enhancements to the SPHEREx Hunter application to elevate image clarity, user interaction, temporal search, astronomical catalog lookup, and citizen science collaboration.

---

### 1. Improve Image Clarity and Quality
- [x] **Sub-pixel object clarity:** High-precision rendering for selected astronomical sources.
- [x] **Zoom fidelity:** Maintain image quality across all magnification tiers with high-quality bilinear canvas smoothing (`imageSmoothingQuality = 'high'`).
- [x] **Lossless fidelity:** Preserve uncompressed FITS dynamic range using Astropy `ZScaleInterval` and `AsinhStretch`.
- [x] **Photometric adjustments:** Add interactive **Brightness** and **Contrast** controls with a single-click Reset option.
- [x] **Native Resolution:** Stream full-resolution original SPHEREx and NASA IRSA archive matrices at hero zoom levels.

---

### 2. Improve Animation and Frame Rate
- [x] **Smooth 60 FPS playback:** Seamless observation animation utilizing `requestAnimationFrame`.
- [x] **Adjustable speed:** Fine-grained playback speed control ($0.5 - 6.0\text{ FPS}$).
- [x] **Full transport controls:** Dedicated **Play**, **Pause**, and **Stop** (reset to Frame 1) controls.
- [x] **Observation stepping:** One-click forward and backward navigation between observation epochs.
- [x] **Zero-latency blinking:** In-memory double-buffered preloading preventing stutters between frames.

---

### 3. Improve Date and Time Display
- [x] **Standard Date Format:** Display observation dates in `DD-MM-YYYY` format (e.g. `16-06-1991`).
- [x] **UTC Time Stamping:** Explicitly label observation time in Universal Coordinated Time (e.g., `07:48:00 UTC`).
- [x] **Real-time updates:** Dynamically update the HUD date/time badge whenever the frame changes.
- [x] **Chronological ordering:** Observations strictly ordered from earliest to latest epoch.

---

### 4. Add Date and Time Search
- [x] **Date Range Pickers:** Start-date and end-date input fields.
- [x] **Temporal filtering:** Query observations falling within the user's selected date range.
- [x] **Empty state feedback:** Clear alert message when no observations exist within the selected window.

---

### 5. Add a Search Bar
- [x] **Global Omnibox:** Search bar at the top of the viewport.
- [x] **Object Name Lookup:** Resolves astronomical names (e.g., *Vega*, *Barnard's Star*, *WISE 0855*, *Sirius*, *Betelgeuse*) to celestial coordinates via CDS Sesame and local benchmarks.
- [x] **Coordinate support:** Accepts decimal degrees (`133.795, -7.245`) and sexagesimal notation (`08h55m10.8s, -07d14m42.5s`).
- [x] **Quick clear:** Clear (`✕`) button to quickly reset and perform another search.
- [x] **Genuine data query:** Triggers authenticated NASA IRSA / SPHEREx cutout queries.

---

### 6. Add a Share Option
- [x] **Share Button:** Convenient Share action in the header and properties sidebar.
- [x] **Clipboard Summary:** Copies formatted telemetry (target name, RA/Dec coordinates, date, and deep-link URL).
- [x] **Deep-link Generator:** Generates shareable URL with query parameters (`?ra=...&dec=...&fov=...&target=...`).
- [x] **State Persistence:** Automatically loads the shared celestial coordinates and FOV when a shared URL is opened.

---

## Technical Architecture & Impacted Files
* `frontend/index.html`: UI controls, search bar, date range picker, brightness/contrast sliders, share modal, and transport controls.
* `backend/main.py`: Celestial object name resolution endpoint (`/api/resolve`), date range filtering, and DD-MM-YYYY UTC formatting.
* `backend/services/cutout_engine.py`: Multi-epoch date handling and authentic NASA FITS ingestion.
