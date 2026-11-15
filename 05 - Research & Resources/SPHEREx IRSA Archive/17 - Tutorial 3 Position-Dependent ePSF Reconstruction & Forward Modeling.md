---
title: "Tutorial 3: Position-Dependent ePSF Reconstruction & Forward Modeling"
document_id: "SPHEREX-TUT-03"
source_url: "https://caltech-ipac.github.io/irsa-tutorials/spherex-psf/"
authors: "Vandana Desai, Jessica Krick, Andreas Faisst, Brigitta Sipőcz, Troy Raen (Caltech/IPAC-IRSA)"
updated: "2026-03-05"
tags:
  - spherex
  - caltech-ipac
  - epsf
  - psf-modeling
  - photutils
  - forward-modeling
  - tractor
  - sub-pixel-astrometry
  - tutorial
aliases:
  - SPHEREx PSF Tutorial
  - Caltech Tutorial 3
  - ePSF Reconstruction Guide
created: 2026-11-14
status: active
---

# 🎯 Tutorial 3: Position-Dependent ePSF Reconstruction & Forward Modeling
> **Official Caltech-IPAC Tutorial:** [Understanding and Extracting the ePSF Extension in a SPHEREx Cutout](https://caltech-ipac.github.io/irsa-tutorials/spherex-psf/)  
> **Authors:** Vandana Desai, Jessica Krick, Andreas Faisst, Brigitta Sipőcz, Troy Raen (Caltech/IPAC-IRSA)  
> **Target Coordinate in Guide:** Cygnus Field ($\alpha = 305.59875^\circ, \delta = +41.14889^\circ$), Detector `SPHEREx-D4` ($2.42 - 3.82\ \mu\text{m}$)  
> **MOC:** [[02 - IRSA SPHEREx Data Releases]] | [[12 - Explanatory Supplement Ch 4 Calibrations & Instrument Models]] | [[15 - Tutorial 1 Introduction to SPHEREx Spectral Images]] | [[16 - Tutorial 2 SPHEREx Spectral Image Cutouts & MEF Packaging]]

---

## 📌 1. Executive Summary & Physics of the SPHEREx ePSF
Because SPHEREx observes wide $3.5^\circ \times 11.3^\circ$ fields across broad optical passbands (0.75 – 5.0 μm) using Linear Variable Filters (LVFs), the Point Spread Function (PSF) varies strongly across the focal plane due to:
1. **Optical Wavefront Aberrations:** Field-dependent coma, astigmatism, and chromatic dispersion from off-axis telescope reflections.
2. **Spectral Variation with Position:** Because wavelength varies continuously along the dispersion axis ($y$ or $x$ depending on the detector), the diffraction limit $\theta \approx 1.22 \lambda / D$ expands as wavelength increases.
3. **Sub-Pixel Intra-Pixel Sensitivity:** SPHEREx's native $6.2''$ pixels critically under-sample the optical PSF in the SWIR bands (Detectors 1–3).

To resolve this without loss of information, SSDC provides an **Effective Point Spread Function (ePSF)** oversampled by a factor of $f = 5$ ($5 \times 5$ sub-pixels per physical detector pixel). In versions $\ge 7.0$ (QR3 and DR1), the ePSF is bundled directly into **HDU 5 (`EPSF`)** of every Level 2 image and cutout.

```
                    SPHEREx Cutout Coordinate Mapping & ePSF Extraction
┌────────────────────────────┐
│   Cutout Pixel (x, y)      │
│   e.g. (2.17, 2.34)        │
└─────────────┬──────────────┘
              │  Shift by cutout anchor: x_orig = 1 + x_cutout - CRPIX1A
              ▼
┌────────────────────────────┐
│ Parent Detector Coordinate │
│ e.g. (223.17, 2007.34)     │
└─────────────┬──────────────┘
              │  Find nearest zone: dist = min(sqrt((x - XCENTER)^2 + (y - YCENTER)^2))
              ▼
┌────────────────────────────┐
│ 21x21 Zone Grid (441 zones)│ ──► Row 422: BINX=2, BINY=20 (CWAVE=2.43 μm, N_eff=4.38)
└─────────────┬──────────────┘
              │  Extract 33x33 5x oversampled ePSF array (1089D)
              ▼
┌────────────────────────────┐
│  photutils.psf.ImagePSF    │ ──► Resample & integrate onto native 11x11 SPHEREx pixel stamp
└────────────────────────────┘
```

---

## 🗺️ 2. Step 1: Mapping Cutout Pixels to Parent Focal Plane Coordinates

When querying an IRSA sub-image cutout, the cutout header loses the global detector origin. To calculate which PSF zone applies, the user must transform local cutout coordinates $(x_{\text{cutout}}, y_{\text{cutout}})$ back to the parent $2048 \times 2048$ detector frame using the `CRPIX1A` and `CRPIX2A` keywords.

### Coordinate Transformation Formula:
$$x_{\text{orig}} = 1 + x_{\text{cutout}} - \text{CRPIX1A}$$
$$y_{\text{orig}} = 1 + y_{\text{cutout}} - \text{CRPIX2A}$$

```python
from astropy.wcs import WCS

# 1. Transform celestial coordinate to local cutout pixels
spatial_wcs = WCS(cutout_header)
xpix_cutout, ypix_cutout = spatial_wcs.world_to_pixel(coord)
# e.g., xpix_cutout = 2.168, ypix_cutout = 2.343

# 2. Shift to parent detector coordinates using anchor keywords
crpix1a = cutout_header["CRPIX1A"]
crpix2a = cutout_header["CRPIX2A"]

xpix_orig = 1 + xpix_cutout - crpix1a
ypix_orig = 1 + ypix_cutout - crpix2a
# Result: xpix_orig = 223.17, ypix_orig = 2007.34 on the parent focal plane!
```

---

## 🔍 3. Step 2: Binary Table Structure of HDU 5 (`EPSF`)

In DR1 and QR3 (Pipeline Version $\ge 7.0$), the `EPSF` HDU is stored as an efficient binary table (`BinTableHDU`) with 441 rows ($21 \times 21$ zones) for Detectors 1, 2, 4, 5, 6 (or $11 \times 41 = 451$ zones for Detector 3):

| Column | Type | Unit | Description |
| :--- | :---: | :---: | :--- |
| `BINX` | `int32` (`J`) | — | Discrete zone index along focal plane X axis ($0 \dots 20$). |
| `BINY` | `int32` (`J`) | — | Discrete zone index along focal plane Y axis ($0 \dots 20$). |
| `XCENTER` | `float32` (`E`) | `pixel` | Physical focal plane X coordinate of zone centroid. |
| `YCENTER` | `float32` (`E`) | `pixel` | Physical focal plane Y coordinate of zone centroid. |
| `XWIDTH` | `float32` (`E`) | `pixel` | Spatial width of this calibration zone ($~97\text{ px}$). |
| `YWIDTH` | `float32` (`E`) | `pixel` | Spatial height of this calibration zone ($~97\text{ px}$). |
| `NSTAR` | `int32` (`J`) | — | Number of empirical stars co-added to construct this ePSF. |
| `NEFF_MEAN`| `float32` (`E`)| — | Effective noise pixel area: $N_{\text{eff}} = \frac{1}{\sum p_i^2}$. |
| `CWAVE` | `float32` (`E`) | $\mu\text{m}$ | Central observing wavelength at this zone center. |
| `CBAND` | `float32` (`E`) | $\mu\text{m}$ | Effective spectral bandwidth ($\Delta \lambda$) of the LVF at this zone. |
| `EPSF` | `1089D` | — | **$33 \times 33$ double-precision array** storing the 2D ePSF. |

### Key Header Telemetry Cards:
- `OVSMPX = 5` & `OVSMPY = 5`: Oversampling factor ($5 \times$ in each axis).
- `TDIM11 = '(33, 33)'`: Dimensions of the oversampled array.
- `DETCOORD = 'sky'`: For Detectors 4, 5, 6 (MWIR), pixels are automatically flipped along X so coordinates match the SWIR sky view.

---

## 🎯 4. Step 3: Selecting the Optimal PSF Zone

To determine which ePSF describes the source, the user computes the Euclidean distance between the source's parent coordinates $(x_{\text{orig}}, y_{\text{orig}})$ and all zone centroids in the table:

```python
import numpy as np

# 1. Compute Euclidean distance across all 441 zones
distances = np.sqrt((xpix_orig - epsf_bintable["XCENTER"])**2 + 
                    (ypix_orig - epsf_bintable["YCENTER"])**2)

# 2. Locate closest zone
sel_zone = np.argmin(distances)
bin_x = epsf_bintable["BINX"][sel_zone]
bin_y = epsf_bintable["BINY"][sel_zone]

# 3. Extract 33x33 oversampled PSF and metadata
epsf_2d = epsf_bintable["EPSF"][sel_zone]  # shape: (33, 33)
n_eff = epsf_bintable["NEFF_MEAN"][sel_zone]
cwave = epsf_bintable["CWAVE"][sel_zone]

print(f"Optimal Zone: Row {sel_zone} (BINX={bin_x}, BINY={bin_y})")
print(f"Central Wavelength: {cwave:.4f} μm | N_eff: {n_eff:.2f} pixels")
```

---

## 🤖 5. Step 4: Native Resolution Integration for Forward Modeling (Tractor)

Standard forward-modeling and forced photometry tools (such as **The Tractor**, Lang et al., or Astropy `photutils`) cannot ingest oversampled PSFs directly because the pixel width and flux normalization will be wrong by a factor of $f^2 = 25\times$.

The oversampled ePSF must be:
1. Shifted to the exact continuous sub-pixel center $(x_0, y_0)$ of the source.
2. Integrated (downsampled) onto the native $6.2''$ SPHEREx detector pixel grid.
3. Normalized to unit flux ($\sum p_i = 1.0$).

### Production Implementation using `photutils.psf.ImagePSF`:

```python
from photutils.psf import ImagePSF

# 1. Construct Photutils continuous model with 5x oversampling
ovs = (int(epsf_header.get("OVSMPY", 5)), int(epsf_header.get("OVSMPX", 5)))
epsf_model = ImagePSF(data=epsf_2d, oversampling=ovs)

# 2. Render centered native stamp (e.g. 11x11 detector pixels)
def render_epsf_stamp_centered(epsf: ImagePSF, x0: float, y0: float, 
                               stamp_size: int = 11, unit_flux: bool = True):
    """
    Renders an oversampled ePSF into a native detector pixel stamp centered at (x0, y0).
    """
    x0, y0 = float(x0), float(y0)
    half = (stamp_size - 1) / 2.0
    
    # Lower-left pixel index in parent detector frame
    x_ll = int(np.floor(x0 - half))
    y_ll = int(np.floor(y0 - half))
    
    # Grid of native pixel center coordinates
    x_centers = x_ll + np.arange(stamp_size)
    y_centers = y_ll + np.arange(stamp_size)
    Y, X = np.meshgrid(y_centers, x_centers, indexing="ij")
    
    # Evaluate continuous model on discrete native pixel centers
    psf_stamp = epsf.evaluate(X, Y, flux=1.0, x_0=x0, y_0=y0)
    
    if unit_flux:
        s = psf_stamp.sum()
        if s > 0 and np.isfinite(s):
            psf_stamp /= s
            
    return psf_stamp, x_ll, y_ll

# 3. Generate native stamp for candidate point source
native_psf, x_ll, y_ll = render_epsf_stamp_centered(epsf_model, x0=xpix_orig, y0=ypix_orig, stamp_size=11)
print(f"Rendered native {native_psf.shape} PSF stamp centered at ({xpix_orig:.2f}, {ypix_orig:.2f})")
```

---

## 🔬 6. Diagnostic Physics: The $N_{\text{eff}}$ Metric
The tutorial details how the effective noise area $N_{\text{eff}}$ varies across the focal plane:
$$N_{\text{eff}} = \frac{1}{\sum_{i} p_i^2}$$
- In the detector center, optical focus is sharpest: $N_{\text{eff}} \approx 3.2\text{--}3.8\text{ pixels}$.
- At the extreme detector corners and edges, optical coma and astigmatism spread the starlight: $N_{\text{eff}} \approx 5.5\text{--}6.5\text{ pixels}$.
- As wavelength increases along the dispersion axis, diffraction scales as $\lambda / D$, broadening $N_{\text{eff}}$ proportionally.
- In aperture and PSF photometry, photometric variance scales directly with $N_{\text{eff}}$:
  $$\sigma_{\text{flux}}^2 \approx N_{\text{eff}} \cdot \sigma_{\text{background}}^2$$
  Sources falling in zones with low $N_{\text{eff}}$ yield substantially higher Signal-to-Noise Ratios (SNR)!

---

## 🚀 7. Key Takeaways for Team RIP (SPHEREx Hunter)

1. **Precision Point Source Fitting in `image_engine` (@iceodu):**  
   When iceodu runs PSF fitting to measure candidate brown dwarf flux in `cutout_engine.py`, we must use `render_epsf_stamp_centered` with `photutils.psf.ImagePSF` rather than a simplistic 2D Gaussian.
2. **Correct Coordinate Inversion:**  
   When a user clicks starlight in the SPHEREx Hunter frontend, our backend must compute $(x_{\text{orig}}, y_{\text{orig}})$ using `CRPIX1A` / `CRPIX2A` before retrieving the matching ePSF kernel.
3. **Artifact Rejection:**  
   Spurious noise spikes and single-pixel cosmic ray hits will have $N_{\text{eff}} \approx 1.0$. Real astronomical sources must have $N_{\text{eff}} \ge 3.0$ matching the local calibration zone. This provides an automated machine filter to eliminate false positive dipole candidates!

---

## 🔗 Related Notes in Obsidian Vault
- [[02 - IRSA SPHEREx Data Releases]] — PSF header erratum and DR1 calibration files.
- [[12 - Explanatory Supplement Ch 4 Calibrations & Instrument Models]] — Full mathematical derivation of SSDC ePSF models.
- [[15 - Tutorial 1 Introduction to SPHEREx Spectral Images]] — Multi-extension FITS loading.
- [[16 - Tutorial 2 SPHEREx Spectral Image Cutouts & MEF Packaging]] — Dynamic TAP queries and parallel cutout downloads.
- [[SPHEREX_DR1_SITEMAP]] — Master index of Caltech SPHEREx tutorials.
