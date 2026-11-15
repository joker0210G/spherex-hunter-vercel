---
title: "Tutorial 6: SPHEREx HiPS All-Sky Mosaic Cubes & HEALPix Geometry"
document_id: "SPHEREX-TUT-06"
source_url: "https://caltech-ipac.github.io/irsa-tutorials/spherex-hipscube/"
authors: "Andreas Faisst, Vandana Desai, Troy Raen, Brigitta Sipőcz (Caltech/IPAC-IRSA)"
updated: "2026-05-08"
tags:
  - spherex
  - caltech-ipac
  - hips-cubes
  - healpix
  - hpgeom
  - all-sky-survey
  - firefly
  - aladin
  - tutorial
aliases:
  - SPHEREx HiPS Tutorial
  - Caltech Tutorial 6
  - HiPS All-Sky Cube Guide
created: 2026-11-14
status: active
---

# 🌐 Tutorial 6: SPHEREx HiPS All-Sky Mosaic Cubes & HEALPix Geometry
> **Official Caltech-IPAC Tutorial:** [Using SPHEREx HiPS All-Sky Mosaic Cubes](https://caltech-ipac.github.io/irsa-tutorials/spherex-hipscube/)  
> **Authors:** Andreas Faisst, Vandana Desai, Troy Raen, Brigitta Sipőcz (Caltech/IPAC-IRSA)  
> **Benchmark Coordinates:** Perseus Field ($\alpha = 60.81100^\circ, \delta = +51.34040^\circ$) $\to$ **HEALPix Order 5 Pixel 445**  
> **MOC:** [[02 - IRSA SPHEREx Data Releases]] | [[03 - SPHEREx Science Data Products & Calibration]] | [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] | [[19 - Tutorial 5 SPHEREx Mosaic Cubes & Multi-Wavelength Overlays]]

---

## 📌 1. Executive Summary & Physics of All-Sky HiPS Cubes
To enable instant worldwide streaming of the 0.75 – 5.0 μm all-sky hyperspectral dataset, the SPHEREx Science Data Center (SSDC) generates **Hierarchical Progressive Survey (HiPS) Cubes** mapped onto the celestial sphere using the **HEALPix** (Hierarchical Equal Area isoLatitude Pixelation) tessellation.

### Core Architecture Highlights:
1. **Dual Access Modalities:**
   - **Interactive Web Client HiPS Service (`hips_url`):** Renders multi-resolution tiles for IPAC Firefly and Aladin Lite across all 102 bands.
   - **Direct On-Premises IBE FITS Repository (`hips_data_url`):** Houses the 12,288 individual Order 5 3D FITS data cubes $(102, 512, 512)$ ready for direct HTTP range streaming or download.
2. **HEALPix Order 5 Tessellation:**
   - Divides the entire $4\pi$ steradian sky into exactly $12 \times 4^5 = \mathbf{12,288\text{ pixels}}$ using the **Nested** indexing convention (`nest=True`).
   - Each Order 5 cell spans $\sim 1.83^\circ \times 1.83^\circ$ containing a $512 \times 512 \times 102$ voxel cube with an angular pixel scale of $\sim 12.8''\text{/px}$.
3. **Dynamic Wavelength Channel Dispatching:**
   - Translates desired observing wavelengths ($\lambda \in [0.75, 5.0]\ \mu\text{m}$) into zero-based discrete cube indices (`cubeIdx`), dynamically dispatching channel changes to the client viewport.
4. **Local Astrometric Distortion Correction (`local_pixel_scale`):**
   - Accounts for the non-conformal nature of the HPX spherical projection to compute accurate solid angles $\Omega_{\text{pixel}}$ for surface brightness ($\text{MJy/sr}$) to flux density ($\text{mJy}$) conversion.

```
                  SPHEREx All-Sky HiPS Cube Infrastructure
                                  Entire Sky (4π sr)
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         HiPS Tile Visualizer                            Direct IBE FITS Cubes
   https://irsa.ipac.caltech.edu/                  https://irsa.ipac.caltech.edu/ibe/
   data/hips/SPHEREx/spherex_allsky_cube           data/spherex/dr1/hips5_cube/hips_20261026
                  │                                               │
                  ├───────────────────────────────┐               │
                  ▼                               ▼               ▼
      Aladin Lite / Firefly Viewport      HEALPix Nested Math (Order 5)
      fc.dispatch(ChangeHiPS, cubeIdx)    N_side = 32 -> ipix = 445 -> Dir0
                                                  │
                                                  ▼
                                      12,288 Individual FITS Cubes
                                      Npix{ipix}_cube.fits (102 x 512 x 512)
                                      ├── IMAGE (Science flux: MJy/sr)
                                      ├── NHITS (Input coverage depth)
                                      ├── FLAGS (22-bit quality OR masks)
                                      ├── SPECTRAL_CHANNELS (102 channels)
                                      └── WCS-WAVE (Lookup wavelength arrays)
```

---

## 🌐 2. Step 1: Querying HiPS Metadata & Properties

The HiPS standard publishes its configuration through a simple key-value `properties` endpoint:

```python
import requests
from astropy.table import Table
import numpy as np
import astropy.units as u

hips_url = "https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube"
response = requests.get(f"{hips_url}/properties")
response.raise_for_status()

# Parse key-value properties
properties = {}
for line in response.text.splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        properties[k.strip()] = v.strip()

print(f"Mission Description: {properties['obs_description']}")
print(f"Cube Depth: {properties['hips_cube_depth']} spectral channels")
print(f"Spatial Scales: Order {properties['hips_order_min']} to Order {properties['hips_order']}")
# Returns: hips_cube_depth = 102, hips_order_min = 0 (12 tiles), hips_order = 5 (12,288 tiles)
```

### Building the 102-Band Wavelength Lookup Table:
The central wavelengths for each of the 102 layers are encoded inside the `data_cube_crval3_arr` property:

```python
# Construct zero-based wavelength lookup table
wavelengths = np.array(properties["data_cube_crval3_arr"].split(), dtype=float) * u.micrometer
layer_ids = np.arange(int(properties["hips_cube_depth"]))

wavetab = Table([wavelengths, layer_ids], names=["lambda_um", "layer_id"])
# Allows instant matching: idx = np.argmin(np.abs(wavetab["lambda_um"] - target_wl))
```

---

## 🖥️ 3. Step 2: Interactive Visualization & Firefly Dispatching

To navigate through the all-sky hyperspectral cube in real time, the tutorial connects via `FireflyClient` and dispatches state mutations:

```python
from firefly_client import FireflyClient

# 1. Connect to IRSA Firefly service
fc = FireflyClient.make_client(url="https://irsa.ipac.caltech.edu/irsaviewer")

# 2. Open All-Sky HiPS Viewport centered on RA/Dec
ra, dec = 60.8109955 * u.deg, 51.3404038 * u.deg
hips_plot_id = 'spherex_cube'

fc.show_hips(
    plot_id=hips_plot_id,
    hips_root_url=hips_url,
    Title='SPHEREx All-Sky HiPS Cube',
    WorldPt=f'{ra.value};{dec.value};EQ_J2000',
    SizeInDeg=10.0
)

# 3. Dynamically switch active viewing channel to PAH 3.3 μm (Layer 62)
target_wl = 3.3 * u.micrometer
layer_idx = int(wavetab["layer_id"][np.argmin(np.abs(wavetab["lambda_um"] - target_wl))])

fc.dispatch(
    action_type='ImagePlotCntlr.ChangeHiPS',
    payload={'plotId': hips_plot_id, 'cubeIdx': layer_idx}
)
```

> [!NOTE]
> **Striping Artifacts in Early Releases:**  
> Users will observe diagonal parallel striping across certain all-sky planes. As explained in the SPHEREx Explanatory Supplement, this striping is an expected optical consequence of early single-visit sky coverage and zodiacal light subtraction boundaries. The stripes diminish as multiple surveys are co-added into DR2 and DR3.

---

## 🧮 4. Step 3: Calculating Direct HEALPix FITS Cube URLs

When high-precision numerical analysis or forced photometry is required, the underlying Order 5 FITS cubes can be retrieved directly from IRSA's IBE repository without downloading the entire all-sky dataset.

### The Nested Indexing Math:
SPHEREx tiles are indexed using HEALPix **Nested Scheme** at **Order 5**:
$$N_{\text{side}} = 2^{N_{\text{order}}} = 2^5 = 32$$
$$N_{\text{pix}} = 12 \times N_{\text{side}}^2 = 12 \times 1024 = 12,288\text{ total sky tiles}$$

```python
import hpgeom as hp
import posixpath

Norder = 5
nside = 2**Norder  # 32

# 1. Convert celestial RA, Dec to nested HEALPix pixel ID
ipix = hp.angle_to_pixel(nside, ra.to_value(u.degree), dec.to_value(u.degree), 
                         nest=True, lonlat=True)
# Result for (60.811°, +51.340°): ipix = 445

# 2. Calculate directory bucket ID (chunks of 10,000 pixels)
dirid = (ipix // 10000) * 10000  # Dir0

# 3. Synthesize exact FITS cube URL
hips_data_url = "https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/hips5_cube/hips_20261026"
cube_url = posixpath.join(hips_data_url, f"Norder{Norder}", f"Dir{dirid}", f"Npix{ipix}_cube.fits")
print(f"Target FITS Cube URL: {cube_url}")
# Returns: https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/hips5_cube/hips_20261026/Norder5/Dir0/Npix445_cube.fits
```

---

## 📦 5. Step 4: Inspecting and Drilling Through the HiPS FITS Cube

Opening `Npix445_cube.fits` reveals a full $512 \times 512 \times 102$ voxel hyperspectral volume:

```python
from astropy.io import fits
from astropy.wcs import WCS

with fits.open(cube_url, cache=False) as hdul:
    hdul.info()
    img_cube = hdul["IMAGE"].data    # shape: (102, 512, 512) float32
    hits_cube = hdul["NHITS"].data   # shape: (102, 512, 512) int32
    flags_cube = hdul["FLAGS"].data  # shape: (102, 512, 512) int32
    wcs_3d = WCS(hdul["IMAGE"].header, fobj=hdul)
    spec_tab = Table.read(hdul["SPECTRAL_CHANNELS"])
```

### Local Angular Pixel Scale Computation:
Because the HEALPix projection (`HPX`) is equal-area on the sphere but exhibits local shear in the Cartesian pixel plane, the effective angular scale must be derived dynamically from local world coordinate deltas:

```python
def local_pixel_scale(wcs_cel, x, y):
    """
    Computes true angular pixel scale (arcsec/pixel) on the sky at coordinate (x, y).
    """
    c0, c1, c2 = wcs_cel.pixel_to_world([x, x + 1, x], [y, y, y + 1])
    dlon1, dlat1 = c0.spherical_offsets_to(c1)
    dlon2, dlat2 = c0.spherical_offsets_to(c2)
    area_sr = np.abs(dlon1 * dlat2 - dlat1 * dlon2).to(u.sr)
    return np.sqrt(area_sr.to(u.arcsec**2)) / u.pixel

def aperture_sum_to_mjy(aperture_sum, pixscale, bunit=u.MJy / u.sr):
    """
    Converts summed pixel counts into flux density in mJy.
    """
    pix_sr = ((pixscale * u.pixel)**2).to(u.sr)
    return (np.asarray(aperture_sum) * u.Unit(bunit) * pix_sr).to(u.mJy)
```

---

## 🚀 6. Full Integration in SPHEREx Hunter

The findings from this notebook directly empower the core features of Team RIP's platform:

1. **Aladin Lite All-Sky HiPS Integration (`frontend/index.html`):**  
   Our "CDS Aladin" tab connects directly to `https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube`. Users can zoom from all-sky HEALPix overview down to arcsecond sub-fields seamlessly.
2. **Dynamic 1-Click Tile Ingestion:**  
   When a user slews to a target (e.g. WISE 0855), our backend dynamically evaluates `hpgeom.angle_to_pixel(32, ra, dec, nest=True)` to identify the exact Order 5 tile (`Npix{ipix}_cube.fits`) and streams cutouts instantaneously.
3. **Multi-Channel Slider:**  
   Our topbar channel scrubber ($0 \dots 101$) maps directly to `ChangeHiPS` dispatch calls, allowing instant time-resolved and wavelength-resolved flipbook comparison!

---

## 🏆 Summary of the Completed 6-Part Caltech-IPAC Tutorial Series
With this note, **all 6 official Caltech-IPAC SPHEREx tutorials are now 100% indexed, synthesized, and cross-linked in the Obsidian vault**:
- **[[15 - Tutorial 1 Introduction to SPHEREx Spectral Images]]** — 6-extension Level 2 MEF structure, Spectral WCS, and bitmasks.
- **[[16 - Tutorial 2 SPHEREx Spectral Image Cutouts & MEF Packaging]]** — Dynamic TAP queries, 10x parallel downloading, and master science MEFs.
- **[[17 - Tutorial 3 Position-Dependent ePSF Reconstruction & Forward Modeling]]** — $21 \times 21$ calibration grids, $5\times$ oversampled ePSF, and Photutils forward modeling.
- **[[18 - Tutorial 4 SPHEREx Source Discovery Tool & Spectral Extraction]]** — Spectral difference imaging ($I_{\text{D2}} - I_{\text{D4}}$) and 19-flag aperture photometry.
- **[[19 - Tutorial 5 SPHEREx Mosaic Cubes & Multi-Wavelength Overlays]]** — 3D mosaic cube analysis, PAH $3.3\ \mu\text{m}$ mapping, and GALEX FUV overlays.
- **[[20 - Tutorial 6 SPHEREx HiPS All-Sky Mosaic Cubes & HEALPix Geometry]]** — 12,288 Order 5 tiles, Firefly dispatching, and all-sky streaming.

---

## 🔗 Related Notes in Obsidian Vault
- [[02 - IRSA SPHEREx Data Releases]] — DR1 and QR3 data products.
- [[03 - SPHEREx Science Data Products & Calibration]] — Full HEALPix Order 5 cube specifications.
- [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] — All-sky cube spatial-spectral entanglement.
- [[SPHEREX_DR1_SITEMAP]] — Master catalog of all 6 Caltech tutorials.
