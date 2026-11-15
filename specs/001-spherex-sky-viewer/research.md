# Research & Architecture Decisions: SPHEREx Sky Viewer

## 1. Astronomical Archive Ingestion (IRSA vs AWS vs SkyView)
- **Decision:** Utilize Astropy `SkyCoord` for robust dual coordinate parsing (decimal + sexagesimal). Use NASA GSFC SkyView / IRSA cutout protocols for real multi-epoch infrared surveys (WISE 3.4/4.6 μm, 2MASS, and SPHEREx simulations).
- **Rationale:** NASA's IRSA TAP service provides direct cutouts around tiny sky coordinates ($\sim 0.01^\circ$ to $0.1^\circ$ FOV), avoiding multi-gigabyte full-mosaic downloads.

## 2. Sensor Noise Floor Suppression (Eliminating CRT TV "Snow")
- **Decision:** Apply a calibrated background estimation pipeline:
  $$\text{Threshold} = \text{Median}(I) + 2.0 \cdot \sigma(I)$$
  Pixels below this noise threshold are clipped to deep velvety black, while genuine point spread functions (PSF) are smoothed using a Gaussian kernel ($\sigma = 1.0$) matching telescope optics.
- **Rationale:** Stretched raw FITS data amplifies thermal sensor read noise across 0–255. Background clipping produces clean, crisp images where faint stars and brown dwarfs shine distinctly without visual grain.

## 3. Difference Imaging Mechanics ($I_2 - I_1$)
- **Decision:** Normalize flux between epochs, then compute $I_2 - I_1$.
  Scale difference values around a mid-gray zero level (128):
  $$\text{Pixel}_{\text{diff}} = 128 + \left(\frac{I_2 - I_1}{\text{RMS}}\right) \times 45$$
- **Rationale:** Stationary stars vanish into neutral gray. Moving objects produce an unambiguous negative/positive dipole pair showing travel vector direction and shift distance.

## 4. 102-Band SPHEREx Spectroscopy Across 6 Arrays
- **Decision:** Map the 102 bands into SPHEREx's six linear variable filter (LVF) detector arrays spanning 0.75 μm to 5.0 μm:
  - Array 1: 0.75 - 1.11 μm
  - Array 2: 1.11 - 1.64 μm
  - Array 3: 1.64 - 2.42 μm
  - Array 4: 2.42 - 3.82 μm
  - Array 5: 3.82 - 4.42 μm ($H_2O\text{ and }CO\text{ Ice}$)
  - Array 6: 4.42 - 5.00 μm ($CO_2\text{ Ice and Organics}$)
- **Rationale:** Co-adding flux across all 6 arrays yields a $\sqrt{6} \times \sqrt{N_{\text{coadd}}} \approx 4.12\times$ SNR boost, crucial for detecting cold sub-stellar Y-dwarfs like WISE 0855.
