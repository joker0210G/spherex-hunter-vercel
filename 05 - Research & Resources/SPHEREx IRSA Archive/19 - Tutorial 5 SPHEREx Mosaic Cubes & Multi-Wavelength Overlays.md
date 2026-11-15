---
title: "Tutorial 5: SPHEREx Mosaic Cubes & Multi-Wavelength Overlays"
document_id: "SPHEREX-TUT-05"
source_url: "https://caltech-ipac.github.io/irsa-tutorials/spherex-mosaic/"
authors: "Andreas Faisst, Jessica Krick, Brigitta Sipőcz, Troy Raen, Vandana Desai (Caltech/IPAC-IRSA)"
updated: "2026-05-08"
tags:
  - spherex
  - caltech-ipac
  - mosaic-cubes
  - hyperspectral
  - aperture-photometry
  - pah-emission
  - galex-fuv
  - reproject
  - tutorial
aliases:
  - SPHEREx Mosaic Cubes
  - Caltech Tutorial 5
  - PAH 3.3um Emission Line Mapping
created: 2026-11-14
status: active
---

# 🧊 Tutorial 5: SPHEREx Mosaic Cubes & Multi-Wavelength Overlays
> **Official Caltech-IPAC Tutorial:** [Understanding and Analyzing SPHEREx Mosaic Cubes](https://caltech-ipac.github.io/irsa-tutorials/spherex-mosaic/)  
> **Authors:** Andreas Faisst, Jessica Krick, Brigitta Sipőcz, Troy Raen, Vandana Desai (Caltech/IPAC-IRSA)  
> **Benchmark Target:** Pinwheel Galaxy (M101: $\alpha = 210.80227^\circ, \delta = +54.34895^\circ$, $z \approx 0.0$)  
> **MOC:** [[02 - IRSA SPHEREx Data Releases]] | [[03 - SPHEREx Science Data Products & Calibration]] | [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] | [[18 - Tutorial 4 SPHEREx Source Discovery Tool & Spectral Extraction]]

---

## 📌 1. Executive Summary & Physics of Mosaic Cubes
While Level 2 products are individual $2048 \times 2048$ detector exposures with varying spectral dispersion along the sky, **SPHEREx Mosaic Cubes** are rectified 3D spatial-spectral data structures $(x, y, \lambda)$ where every spatial pixel shares the same set of 102 calibrated wavelength channels.

### Key Capabilities Demonstrated in this Guide:
1. **Multi-Plane FITS Cube Architecture:** Inspecting the 5-HDU structure (`IMAGE`, `NHITS`, `FLAGS`, `SPECTRAL_CHANNELS`, `WCS-WAVE`).
2. **Surface Brightness to Absolute Flux Conversion:** Converting native $\text{MJy/sr}$ to millijanskys ($\text{mJy}$) using pixel scale geometry:
   $$[\text{mJy}] = [\text{MJy/sr}] \times 23.5045 \times (\text{pixel scale in arcsec/px})^2 / 1000$$
3. **Hyperspectral Aperture Photometry with Local Annulus Background Subtraction:** Extracting full 102-band spectra using `photutils.aperture.CircularAperture` and sigma-clipped background annuli.
4. **Continuum-Subtracted Emission Line Mapping:** Isolating the **PAH $3.3\ \mu\text{m}$** (Polycyclic Aromatic Hydrocarbon) star-formation emission feature and subtracting adjacent continuum channels.
5. **Multi-Wavelength Cross-Correlation with GALEX FUV:** Querying Far-Ultraviolet ($153\text{ nm}$) space imagery from IRSA (`spitzer_lvl`), converting flux, reprojecting via `reproject_exact`, and overlaying SPHEREx infrared contours over UV young star-forming clusters.

```
                  SPHEREx 3D Mosaic Cube Architecture (267 x 267 x 102)
   ┌─────────────────────────────────────────────────────────────┐
  ╱                                                             ╱│
 ┌─────────────────────────────────────────────────────────────┐ │
 │                                                             │ │
 │                     λ = 5.00 μm (Plane 102)                 │ │
 │                                                             │ │
 │       ...                                                   │ │
 │                     λ = 3.30 μm (Plane 63: PAH 3.3 μm)      │ │
 │                                                             │ │
 │       ...                                                   │ │
 │                     λ = 0.75 μm (Plane 1)                   │ │
 │                                                             │╱
 └─────────────────────────────────────────────────────────────┘
  ◄────────────────────── Spatial X (RA) ─────────────────────►
```

---

## 🏗️ 2. Step 1: Multi-Extension Structure of SPHEREx Mosaic Cubes

When opening a mosaic cube produced by the IRSA SPHEREx Mosaic Tool (`M101_irsa.fits`), Astropy reports 6 primary extensions:

```python
from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
import numpy as np

fn_spherex = "https://irsa.ipac.caltech.edu/data/demos/notebooks/spherex/M101_irsa.fits"
with fits.open(fn_spherex) as hdul:
    hdul.info()
```

### HDU Summary Table:
| HDU # | Name | Type | Dimensions | Description |
| :---: | :--- | :---: | :---: | :--- |
| `0` | `PRIMARY` | `PrimaryHDU` | `()` | Global mission header. |
| `1` | `IMAGE` | `ImageHDU` | `(267, 267, 102)` | 3D array: spatial $x, y$ by 102 spectral channels. |
| `2` | `NHITS` | `ImageHDU` | `(267, 267, 102)` | Hit-count coverage depth per pixel per plane. |
| `3` | `FLAGS` | `ImageHDU` | `(267, 267, 102)` | 22-bit quality and transient flags per voxel. |
| `4` | `SPECTRAL_CHANNELS`| `BinTableHDU` | `102R x 8C` | Central $\lambda$, bandwidth, and detector index. |
| `5` | `WCS-WAVE` | `BinTableHDU` | `1R x 3C` | Direct 102-element arrays of plane numbers, $\lambda$, and $\Delta \lambda$. |

### Surface Brightness to Flux Density Conversion:
SPHEREx mosaic cubes are delivered in surface brightness ($\text{MJy/sr}$). To convert to physical flux per pixel:
$$\text{Pixel Scale} = |\text{CDELT1}| \times 3600'' = 9.0''/\text{px}$$
$$I_{\text{mJy}} = I_{\text{MJy/sr}} \times 23.5045 \times \frac{(\text{Pixel Scale})^2}{1000}$$

```python
cube_hdr = hdul["IMAGE"].header
pixscale = np.abs(cube_hdr["CDELT1"] * 3600)  # 9.0 arcsec/pixel
cube_img = hdul["IMAGE"].data * 23.5045 * (pixscale**2) / 1e3
cube_hdr['BUNIT'] = "mJy"

# Extract 2D celestial spatial WCS (dropping spectral 3rd axis)
cube_wcs = WCS(cube_hdr, fobj=hdul).celestial
```

---

## 📈 3. Step 2: Quick-Look Aperture Photometry Across the Cube

Tutorial 5 extracts a complete 102-band spectrum of the galaxy nucleus using `photutils` circular apertures and concentric background annuli:

```python
from astropy.stats import SigmaClip
from photutils.aperture import CircularAperture, CircularAnnulus, ApertureStats, aperture_photometry

def measure_aperture_photometry_cube(cube, r_ap=20, r_in=60, r_out=100):
    """
    Computes aperture photometry with local sigma-clipped background subtraction
    across all 102 planes of the SPHEREx mosaic cube.
    """
    pos = (cube.shape[1] // 2, cube.shape[2] // 2)
    aperture = CircularAperture(pos, r=r_ap)
    annulus = CircularAnnulus(pos, r_in=r_in, r_out=r_out)
    sigclip = SigmaClip(sigma=3.0, maxiters=10)
    
    phot_results = []
    for i in range(cube.shape[0]):
        plane = cube[i, :, :]
        # Background estimation from annulus
        stats = ApertureStats(plane, annulus, sigma_clip=sigclip)
        total_bkg = stats.mean * aperture.area_overlap(plane)
        
        # Raw aperture sum minus local background
        phot = aperture_photometry(plane, aperture)
        bkg_sub = phot["aperture_sum"][0] - total_bkg
        phot_results.append(bkg_sub)
        
    return np.array(phot_results)
```

### Diagnostic Infrared Spectral Features Detected:
By plotting the extracted flux across the 102 channels, several key astrophysical features appear:
- **$\text{Pa-}\beta$ ($1.28\ \mu\text{m}$):** Paschen hydrogen recombination line.
- **$1.60\ \mu\text{m}$ Stellar Bump:** Minimum in $\text{H}^-$ opacity in cool star photospheres.
- **$\text{Pa-}\alpha$ ($1.87\ \mu\text{m}$):** Primary NIR hydrogen star-formation tracer.
- **$\text{Br-}\beta$ ($2.36\ \mu\text{m}$):** Brackett series hydrogen emission.
- **PAH $3.30\ \mu\text{m}$:** Strong aromatic hydrocarbon vibrational emission.
- **$\text{Br-}\alpha$ ($4.05\ \mu\text{m}$):** Mid-infrared hydrogen line.

---

## 🎨 4. Step 3: Continuum-Subtracted PAH $3.3\ \mu\text{m}$ Emission Line Map

To isolate the distribution of interstellar dust and starburst regions in M101, the tutorial builds a pure line map by subtracting adjacent continuum planes:

### Redshift-Dependent Plane Selection:
$$\lambda_{\text{obs}} = 3.3\ \mu\text{m} \times (1 + z)$$
For M101 ($z \approx 0.0$):
- **Feature Plane:** Plane 63 ($\lambda = 3.293\ \mu\text{m}$)
- **Continuum Planes:** Planes 61, 62 ($3.21\text{--}3.25\ \mu\text{m}$) and Planes 64, 65 ($3.33\text{--}3.37\ \mu\text{m}$)

```python
def make_emission_map(cube, feature_planes=[63], continuum_planes=[61, 62, 64, 65]):
    """
    Creates a continuum-subtracted 2D emission line map.
    """
    # Sum feature channels minus median continuum
    feat = np.nansum(cube[np.array(feature_planes) - 1, :, :], axis=0)
    cont = np.nanmedian(cube[np.array(continuum_planes) - 1, :, :], axis=0)
    return feat - cont

pah_map = make_emission_map(cube_img, [63], [61, 62, 64, 65])
```

---

## 🛰️ 5. Step 4: Multi-Wavelength Cross-Correlation with GALEX FUV

To confirm whether PAH $3.3\ \mu\text{m}$ emission traces active star formation, the notebook queries the **GALEX Far-Ultraviolet (FUV: $153\text{ nm}$)** science image from the Spitzer Local Volume Legacy (`spitzer_lvl`) archive:

```python
from astroquery.ipac.irsa import Irsa
from astropy.nddata import Cutout2D
from reproject import reproject_exact

# 1. Query IRSA for GALEX FUV science image at M101 coordinates
pos = SkyCoord(ra=210.80227 * u.deg, dec=54.34895 * u.deg)
im_table = Irsa.query_sia(pos=(pos, 1 * u.arcsec), collection='spitzer_lvl')
sel = (im_table["dataproduct_subtype"] == "science") & (im_table["instrument_name"] == "GALEX") & (im_table["energy_bandpassname"] == "FUV")
galex_url = im_table[sel]["access_url"][0]

# 2. Open GALEX image and convert AB magnitudes to mJy
with fits.open(galex_url) as hdul_galex:
    galex_cutout = Cutout2D(hdul_galex[0].data, position=pos, size=(40*u.arcmin, 40*u.arcmin), wcs=WCS(hdul_galex[0].header), mode="partial")
    img_galex = galex_cutout.data
    # AB magnitude conversion (GALEX FUV Zero Point = 18.82)
    img_galex_ab = -2.5 * np.log10(img_galex) + 18.82
    img_galex_mjy = 10**(-0.4 * (img_galex_ab - 23.9)) / 1e3

# 3. Exact flux-conserving reprojection onto SPHEREx Mosaic WCS
galex_reprojected, _ = reproject_exact(
    input_data=(img_galex_mjy, galex_cutout.wcs.to_header()), 
    output_projection=cube_wcs
)
```

### Observational Result:
When SPHEREx PAH $3.3\ \mu\text{m}$ red contour lines are plotted over the blue GALEX FUV image, the polycyclic aromatic hydrocarbon emission perfectly aligns with the bright UV clusters along M101's spiral arms, confirming that young OB associations heat and excite the surrounding aromatic dust!

---

## 🚀 6. Architectural Lessons for Team RIP (SPHEREx Hunter)

1. **3D Cube Streaming in Backend (`backend/api/`):**  
   SPHEREx mosaic cubes ($267 \times 267 \times 102$) can be sliced along the spectral dimension on demand. When a user in the frontend selects a specific emission line (e.g. `H2O Ice 3.03 μm`, `CO2 Ice 4.29 μm`, or `PAH 3.3 μm`), the backend can return the continuum-subtracted slice dynamically.
2. **Multi-Wavelength Overlay Contours in Three.js / Canvas:**  
   In our frontend viewer, we can offer an **"Overlay Contours"** toggle allowing citizen scientists to superimpose SPHEREx spectral feature contours directly over optical Legacy Survey or unWISE infrared images.
3. **Exact Flux Calibration Formula:**  
   We will store the calibrated conversion constant ($23.5045 \times \text{pixscale}^2 / 1000$) in `backend/config.py` for all IRSA mosaic products.

---

## 🔗 Related Notes in Obsidian Vault
- [[02 - IRSA SPHEREx Data Releases]] — Overview of DR1 all-sky cubes and DOIs.
- [[03 - SPHEREx Science Data Products & Calibration]] — Detailed MEF and HEALPix cube specifications.
- [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] — All-sky cube spatial-spectral entanglement caveats.
- [[18 - Tutorial 4 SPHEREx Source Discovery Tool & Spectral Extraction]] — Source detection and spectral extraction.
- [[SPHEREX_DR1_SITEMAP]] — Master catalog of all 6 Caltech tutorials.
