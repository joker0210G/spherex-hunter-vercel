# ⚡ Sprint Phase 2: Core Engine & Blink Comparator (Hours 12 – 24)
> **Goal:** Smooth animated blink player, difference imaging toggle, and user-adjustable FOV.

---

## 📋 Phase 2 Action Items

### 1. Blink Engine & Player Controls (Hours 12 – 18)
- [ ] Create alternating timer loop in React/Canvas switching between `Epoch 1` and `Epoch 2`.
- [ ] Implement playback controls:
  - Play / Pause button
  - Speed slider (0.5 FPS to 10 FPS)
  - Previous / Next epoch step buttons
- [ ] Add visual indicator showing currently active epoch badge (`Pass 1 - May 2025` vs `Pass 2 - Nov 2025`).

### 2. Image Arithmetic & Difference Imaging (Hours 14 – 22)
- [ ] Implement Python difference imaging algorithm ($I_{	ext{diff}} = I_{	ext{epoch } 2} - I_{	ext{epoch } 1}$).
- [ ] Align images to identical WCS grid using `reproject.reproject_interp`.
- [ ] Add "Difference Mode" toggle in frontend viewer.
- [ ] Verify dipole signature is visible on WISE 0855 and Barnard's Star.

### 3. User-Selectable Field of View (FOV) (Hours 18 – 24)
- [ ] Add FOV dropdown / slider:
  - `1 arcmin` (Ultra-narrow / Deep zoom)
  - `3 arcmin` (Standard Target View)
  - `10 arcmin` (Wide Search Field)
- [ ] Connect FOV parameter to cutout query backend.
- [ ] Implement URL deep-linking so query params reflect current view (`?ra=...&dec=...&fov=...`).
