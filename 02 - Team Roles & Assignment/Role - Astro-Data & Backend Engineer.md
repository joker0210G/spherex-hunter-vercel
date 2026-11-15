# 🔭 Role: Astro-Data & Backend Engineer
> **Mission:** Harness Python, Astropy, and astronomical APIs to fetch, align, and serve multi-epoch image cutouts and 102-band spectra.

---

## 🎯 Key Deliverables
1. **Cutout Ingestion API:**
   - FastAPI endpoint `GET /api/cutout?ra={ra}&dec={dec}&fov={arcsec}`.
   - Queries astronomical archives (SPHEREx mock/public release, WISE/NEOWISE via IRSA, and Gaia DR3).
   - Reprojects images onto an identical WCS grid using `reproject.reproject_interp`.
2. **Band Co-addition & FITS Processing:**
   - Group the 102 SPHEREx channels into 6 detector arrays to increase Signal-to-Noise Ratio (SNR).
   - Convert FITS 32-bit floating point arrays to normalized 8-bit PNGs using Astropy's `ZScaleInterval` or `AsinhStretch`.
3. **Synthetic Spectra Generator:**
   - Endpoint `GET /api/spectrum?ra={ra}&dec={dec}`.
   - Extracts flux values across all 102 wavelengths ($0.75 - 5.0\ \mu	ext{m}$) at the queried coordinate.
   - Identifies molecular absorption fingerprints ($H_2O, CO, CO_2, CH_4$).

---

## 🛠️ Recommended Tech Stack
- **Framework:** Python 3.10+ / FastAPI + Uvicorn.
- **Astronomy Libraries:**
  - `astropy` (WCS, coordinates, units, FITS I/O, visualization stretch)
  - `astroquery` (Querying IRSA, CDS Aladin, Gaia, SkyView)
  - `reproject` (Astronomical image spatial alignment)
  - `numpy`, `scipy`, `pillow`

---

## 🧪 Starter Code Snippet: Astropy Cutout Engine
```python
# app/services/cutout_service.py
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.visualization import AsinhStretch, ZScaleInterval
from astroquery.skyview import SkyView
import numpy as np

def fetch_and_stretch(ra: float, dec: float, survey: str = "WISE 4.6", radius_arcmin: float = 3.0):
    coord = SkyCoord(ra=ra, dec=dec, unit="deg", frame="icrs")
    images = SkyView.get_images(position=coord, survey=[survey], radius=radius_arcmin * u.arcmin)
    
    if not images:
        return None
        
    hdu = images[0][0]
    data = np.nan_to_num(hdu.data)
    
    # Astronomical stretch for human perception
    transform = ZScaleInterval()
    vmin, vmax = transform.get_limits(data)
    stretched = np.clip((data - vmin) / (vmax - vmin), 0, 1)
    return (stretched * 255).astype(np.uint8)
```

---

## 🔗 Cross-Links
- Benchmark Targets: [[02 - Mandatory Test Targets & Benchmark Suite]]
- Instrument Primer: [[03 - SPHEREx Instrument & Data Primer]]
- API Spec: [[04 - API & URL Deep-Linking Specification]]
