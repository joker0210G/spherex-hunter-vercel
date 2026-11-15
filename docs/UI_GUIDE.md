# SPHEREx Hunter - Observatory Frontend & UI Guide

> **NASA Space Apps Challenge 2026** | **Team:** RIP (Coimbatore, India)  
> **Challenge:** Planet X and SPHEREx  
> **Platform Version:** 2.0 (Deep Space Infrared Observatory)

---

## 🌌 Overview & Design Philosophy

SPHEREx Hunter is engineered with a **Dark Observatory Theme** (`#070a11` / `#0d111b` / `#131926` palette) providing optimal visual contrast (WCAG 2.2 AA compliant) for astronomical FITS cutouts, subtle difference-imaging residuals, and high proper-motion vector overlays.

The interface adheres to the core principle:  
**Simple by default, powerful on demand.**  
- **Beginner Mode:** Plain-language tooltips, automatic guided walk-throughs, and curated discovery presets.
- **Scientist Mode:** Exposes raw ZOGY $S_{\text{corr}}$ SNR thresholds, EPSF centroid astrometric errors, SkyCoord space-motion propagation offsets, and raw multi-epoch flux readouts ($\mu\text{Jy}$ and counts).

---

## 🖥️ Layout Hierarchy

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ TOP BAR (48px / h-12)                                                                  │
│ [SPHEREx Logo] [Blink | Diff | Spectra | Aladin]   [Ctrl+K Target Search]   [Coords]   │
│                                                     [Presets: WISE 0855...] [Fetch]    │
│                                                     [Mode: Beginner/Scientist] [...]   │
├─────────┬─────────────────────────────────────────────────────────┬────────────────────┤
│ LEFT    │ CENTER VIEWPORT                                         │ RIGHT INSPECTOR    │
│ RAIL    │                                                         │ (384px / w-96)     │
│ (56px)  │ ┌─ Top-Left HUD ────────┐   ┌─ Top-Right Shading ─────┐ │ ┌─ Tabs ─────────┐ │
│         │ │ WISE 0855-0714        │   │ Gray | Invert | Thermal │ │ │Layers | Target │ │
│ [Select]│ │ Frame 1: 2MASS (1999) │   └─────────────────────────┘ │ │Candidates | Photo│
│ [Pan]   │ └───────────────────────┘                               │ └────────────────┘ │
│ [Dist]  │                                                         │                    │
│ [Flip]  │ [Edge-to-Edge Pure Astronomical FITS Canvas]            │ Tab 1: Scene Layers│
│ [Gaia]  │                                                         │ Tab 2: Coordinates │
│ [Center]│ ┌─ Bottom-Left ─────────┐   ┌─ Bottom-Right Scale ────┐ │ Tab 3: Flagged Cand│
│ [1:1]   │ │ RA / Dec / Zoom / LOD │   │ Scale (1') | Compass ↑N │ │ Tab 4: 6-Array Phot│
│ [Walk]  │ └───────────────────────┘   └─────────────────────────┘ │                    │
│ [Full]  │                                                         │                    │
├─────────┴─────────────────────────────────────────────────────────┴────────────────────┤
│ BOTTOM DOCK (Collapsed: 36px / Expanded: 148px)                                        │
│ [Timeline (Flipbook)] [102-Band Spectrum] [Light Curve]         [Baseline: 26.2y] [⏷]  │
│ [|◀ ◀ ⏸ ▶ ▶|] Frame 1/4   [====== Progress Bar ======] Speed: 2.0 FPS               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⌨️ Keyboard Shortcuts Reference

| Key | Action | Description |
|---|---|---|
| **`B`** | **Blink Mode** | Multi-epoch flipbook comparator |
| **`D`** | **Difference Mode** | Numerical ZOGY subtraction ($I_2 - I_1$) |
| **`S`** | **Spectra Mode** | 102-band infrared spectroscopy panel |
| **`A`** | **Aladin Sky Mode** | Interactive CDS Strasbourg Aladin Lite |
| **`Space`** | **Play / Pause** | Toggles multi-epoch flipbook blinking |
| **`[`** / **`]`** | **Step Frame** | Jump to previous / next epoch frame |
| **`G`** | **Toggle Gaia** | Toggle ESA/NASA Gaia DR3 proper motion vectors |
| **`R`** | **Recenter** | Recenter telescope canvas on target coordinates |
| **`F`** | **Fullscreen** | Toggle fullscreen canvas mode |
| **`Ctrl + K`** | **Command Palette** | Quick search targets, coordinates, and modes |
| **`?`** | **Shortcuts Cheat Sheet**| Opens interactive keyboard shortcuts modal |
| **`Shift + \``** | **Walk Nav** | WASD 6DOF telescope slewing & flight mode |
| **`Esc`** | **Dismiss** | Closes any open modal, popover, or exits Walk Nav |

---

## 🗂️ Inspector Tabs Detail

### Tab 1: Layers (Scene Collection)
- Single source of truth: synchronized with `window.scene`.
- Filter search input for instantaneous layer and epoch filtering.
- Observation Epochs card tree with proper-motion alignment displacement metrics.
- Visual Layers with independent opacity sliders (0–100%), visibility toggles, and provenance info.

### Tab 2: Target
- Verified astronomical target metadata: Object Type, Spectral Class, ICRS RA/Dec.
- Proper motion in both `"/yr` and `mas/yr` with Astropy space-motion propagation.
- Distance (pc and light-years), Parallax (mas), and Effective Temperature ($T_{\text{eff}}$ in K) with literature citations.
- Direct external bridges: NASA WiseView flipbook verification and CADC NEOSSat asteroid archive search.

### Tab 3: Candidates
- Dynamic real-time list of citizen science discoveries and pipeline detections.
- Filterable by evidence tier:
  - 🔵 **Known Solar System** (MPC / SkyBoT)
  - 🟢 **Known Stellar / Brown Dwarf** (SIMBAD / Gaia)
  - 🟡 **Unknown Mover** (Candidate, not confirmed)
  - 🟣 **Slow IR-Excess Candidate** (Planet X Candidate)
  - 🔴 **Likely Artifact** (Starlight residual)
- Direct 1-click export to CSV (`/api/discoveries/export/csv`) and NASA/CSA discovery flagging modal.

### Tab 4: Photometry
- Responsive grid of all **6 SPHEREx Detector Arrays**:
  - Array 1 ($0.75\,\mu\text{m}$)
  - Array 2 ($1.20\,\mu\text{m}$)
  - Array 3 ($1.90\,\mu\text{m}$)
  - Array 4 ($2.42\,\mu\text{m}$)
  - Array 5 ($3.82\,\mu\text{m}$)
  - Array 6 ($4.42\,\mu\text{m}$)
- Counts, extracted flux ($\mu\text{Jy}$), co-added Signal-to-Noise Ratio (SNR).
- Archival coverage status for Canadian Space Agency NEOSSat.

---

## 🔗 Permalinks & Shareable State

Every target switch, mode change, or frame selection automatically updates the browser URL hash:
```
http://127.0.0.1:8000/app/index.html#target=wise0855&mode=blink&frame=1
```
Users can bookmark or share this link to immediately open the exact target, view mode, and frame.
