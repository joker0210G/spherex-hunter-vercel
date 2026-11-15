# Implementation Plan: SPHEREx Sky Viewer

**Feature:** `001-spherex-sky-viewer`  
**Constitution Ref:** [.specify/memory/constitution.md](../../.specify/memory/constitution.md)  
**Spec Ref:** [spec.md](spec.md)  

---

## Technical Context

- **Backend Architecture:** Python 3.11+ / FastAPI (`backend/main.py`), Astropy 8.0+, Astroquery, PyVO, NumPy, SciPy, Pillow.
- **Frontend Architecture:** Vanilla HTML5, Canvas 2D, Tailwind CSS, Lucide icons, Chart.js. Mounted under FastAPI at `/app` for same-origin PNA compliance.
- **Data Flow:**
  1. Client sends coordinates (`RA, Dec, FOV`).
  2. Backend parses coordinates via Astropy `SkyCoord` (supports both decimal and sexagesimal).
  3. NASA IRSA / SkyView archive queried for multi-epoch FITS images.
  4. Sigma-clipped background noise suppression ($2.0\sigma$) + PSF Airy Gaussian smoothing.
  5. Multi-epoch difference imaging computation ($I_2 - I_1$).
  6. Return Base64 PNG frames, motion vector shift, 6-array co-add boost telemetry, and 102-band spectrum.
  7. Client Canvas renders animated flipbook with difference overlay, reticle callouts, and timeline transport.

---

## Constitution Compliance Check

| Principle | Check | Status |
| :--- | :--- | :--- |
| **1. Scientific Integrity (Real Data First)** | Uses Astropy SkyCoord and calibrated FITS reduction. No fake video games. | ✅ Compliant |
| **2. Layman Accessibility** | Animated flipbook + difference dipole highlights + clean black background. | ✅ Compliant |
| **3. Multi-Epoch Synergy** | Compares Pass 1 (May) vs Pass 2 (Nov) with archival WISE 3.4/4.6 baseline. | ✅ Compliant |
| **4. 102-Band Spectroscopy** | Generates full 102-channel SED with molecular absorption features. | ✅ Compliant |
| **5. Universal Embeddability** | Deep-linkable via URL query params (`?ra=...&dec=...&fov=...`). | ✅ Compliant |

---

## Phased Implementation Roadmap

- **Phase 0:** Research & Mathematical Calibration (Noise floor sigma-clipping, difference imaging formula).
- **Phase 1:** Core Data Engine (`backend/services/cutout_engine.py`) with sexagesimal parsing, 5 benchmark targets, and 102-band spectrum API.
- **Phase 2:** High-Performance Frontend Viewport (`frontend/index.html`) with interactive timeline, FPS control, difference mode toggle, and coordinate inputs.
- **Phase 3:** Verification on 5 NASA Targets (Barnard's Star, Epsilon Indi B, WISE 0855, RW Aurigae, R Draconis) and live browser devtools proof.
