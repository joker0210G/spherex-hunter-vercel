# 🔬 Sprint Phase 3: Advanced Features & Astropy Magic (Hours 24 – 36)
> **Goal:** 102-band infrared spectra on click, Gaia/WISE overlays, and candidate discovery workflow.

---

## 📋 Phase 3 Action Items

### 1. 102-Band Spectral Energy Distribution (SED) Viewer (Hours 24 – 30)
- [ ] Group the 102 SPHEREx bands across the 6 detector arrays.
- [ ] Create interactive click listener on the canvas: clicking any pixel requests `/api/spectrum?ra={ra}&dec={dec}`.
- [ ] Render interactive Recharts curve showing flux vs. wavelength ($0.75 - 5.0\ \mu	ext{m}$).
- [ ] Add visual badges highlighting molecular absorption dips:
  - $H_2O$ Ice ($3.05\ \mu	ext{m}$)
  - $CO_2$ Ice ($4.27\ \mu	ext{m}$)
  - $CO$ ($4.67\ \mu	ext{m}$)
  - $CH_4$ ($3.3\ \mu	ext{m}$)

### 2. Multi-Survey Overlay (Hours 28 – 34)
- [ ] Add toggle to overlay **Gaia DR3** proper motion vector arrows onto the canvas.
- [ ] Add toggle to compare SPHEREx NIR with archival **WISE** or optical images.

### 3. Citizen Science Discovery & Flagging (Hours 30 – 36)
- [ ] Build "Flag Moving Object" discovery modal:
  - User marks candidate coordinates.
  - User selects classification: `Asteroid`, `Brown Dwarf`, `Variable Star`, `Planet X Candidate`.
  - Saves to local storage or community discoveries list.
