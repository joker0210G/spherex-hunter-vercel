# 🇨🇦 CSA NEOSSAT_Tutorial Code & Algorithm Codex
> **Source Repository:** [https://github.com/asc-csa/NEOSSAT_Tutorial](https://github.com/asc-csa/NEOSSAT_Tutorial) (Branch: `main`)  
> **Author Organization:** Canadian Space Agency (CSA / ASC)  
> **Target Challenge:** NASA Space Apps Challenge (Near-Earth Objects & Asteroid Tracking)  
> **License:** Modified MIT License  
> **Vault Location:** `05 - Research & Resources/NEOSSAT_TUTORIAL_CODE_CODEX.md`

---

## 1. 🌐 The Complete Repository Architecture

```
github.com/asc-csa/NEOSSAT_Tutorial
│
├── 📄 LICENSE.txt (Modified MIT Open-Source License)
├── 📄 README.md (Bilingual French & English Tutorial Guide)
├── 🖼️ neossat.jpg (High-Resolution 3D Microsatellite Render)
│
└── 📁 code/
    ├── 📓 01_ Extracting Data and Visualization.ipynb (English)
    │   ├── Option 1: CSA FTP Server Direct Downloader (`ftp.asc-csa.gc.ca`)
    │   ├── Option 2: CADC CAOM-2 TAP Interface (`astroquery.cadc`)
    │   └── Astropy FITS Image Visualization (`astropy_mpl_style`)
    │
    ├── 📓 01_ Extraction de Données et Visualisation.ipynb (French)
    │
    ├── 📓 02_Pre Processing and Analysis.ipynb (English)
    │   ├── Section A: Programmatic CADC ADQL Query Constructor (MJD conversion)
    │   ├── Section B: Raw FITS Header & Coordinate Inspection
    │   ├── Section C: Image Calibration Pipeline:
    │   │   ├── 50-pixel overscan bias correction
    │   │   ├── Master dark frame median co-addition & subtraction
    │   │   └── Multi-image temporal median stacking (SNR boost)
    │   └── Section D: Detection & Analytics:
    │       ├── Line Segment Detector (LSD) streaklet detection
    │       ├── Temporal 3D difference cube analysis (`difference_cube > 3σ`)
    │       └── Animated GIF time-series exporter (`imageio`)
    │
    └── 📓 02_Prétraitement et Analyse.ipynb (French)
```

---

## 2. 📡 Data Ingestion Pipelines (Notebook 01)

### Option 1: Direct FTP Download from Canadian Space Agency
The CSA hosts public NEOSSat observations sorted by calendar year and day-of-year (DOY):
```python
from ftplib import FTP
import os

def download_fits_files(year, day_of_year, local_directory):
    ftp_host = 'ftp.asc-csa.gc.ca'
    ftp = FTP(ftp_host)
    ftp.login()  # Anonymous login

    ftp_directory = f'/users/OpenData_DonneesOuvertes/pub/NEOSSAT/ASTRO/{year}/{day_of_year}/'
    ftp.cwd(ftp_directory)

    # List and stream .fits files
    fits_files = [f for f in ftp.nlst() if f.endswith('.fits')]
    for filename in fits_files:
        local_path = os.path.join(local_directory, filename)
        with open(local_path, 'wb') as local_file:
            ftp.retrbinary(f'RETR {filename}', local_file.write)
    ftp.quit()
```

### Option 2: Programmatic Query via `astroquery.cadc`
```python
from astroquery.cadc import Cadc
from astropy.coordinates import SkyCoord
from astropy import units as u

cadc = Cadc()
coords = SkyCoord(240.0, -30.0, unit='deg')
radius = 2.0 * u.deg

# Query CADC for NEOSSAT collection
results = cadc.query_region(coords, radius=radius, collection='NEOSSAT')

# Filter by exposure time (> 60s)
filtered = results[results['time_exposure'] > 60.0]
image_urls = cadc.get_image_list(filtered, coords, radius)
```

---

## 3. 🔬 Calibration & Pre-Processing Pipeline (Notebook 02)

### A. Overscan Bias Subtraction
NEOSSat CCDs contain a 50-column unilluminated overscan region on the right edge. Computing the line-by-line median bias suppresses row-correlated readout noise:
```python
import numpy as np

def overscan_correction(science_data, overscan_region):
    # Compute median bias for each CCD row
    overscan_median = np.median(overscan_region, axis=1)
    # Subtract bias vector from active science pixels
    corrected_data = science_data - overscan_median[:, np.newaxis]
    return corrected_data
```

### B. Master Dark Frame Co-addition
Stacking multiple unilluminated dark frames via median rejects transient cosmic ray spikes and produces a pure thermal fixed-pattern noise map:
$$D_{\text{master}}(x, y) = \text{median}\left( \{ D_k(x, y) \}_{k=1}^K \right)$$
```python
def create_master_dark(dark_frames):
    corrected_darks = [overscan_correction(d[:, :start_col], d[:, start_col:]) for d in dark_frames]
    master_dark = np.median(np.array(corrected_darks), axis=0)
    return master_dark
```

### C. Temporal Median Stacking
Stacking calibrated exposures eliminates random photon noise while preserving stationary stellar baselines:
$$I_{\text{stacked}}(x, y) = \text{median}\left( \{ I_t(x, y) \}_{t=1}^N \right)$$

---

## 4. ☄️ Core Analytics: Asteroid Streaklet & Motion Detection

### A. Line Segment Detector (LSD) Streaklet Finding (`detect_streaklets`)
Fast-moving Near-Earth Asteroids (NEAs) leave linear streaklet trails across CCD exposures. The CSA pipeline uses Gaussian smoothing followed by the Line Segment Detector:
```python
from scipy.ndimage import gaussian_filter
from skimage.draw import line as draw_line
from skimage.morphology import binary_dilation, disk, remove_small_objects
from pylsd import lsd  # or cv2.createLineSegmentDetector()

def detect_streaklets(image_data, min_length=10):
    # 1. Smooth and normalize image to 8-bit unsigned integer
    smoothed = gaussian_filter(image_data, sigma=1.0)
    norm = (smoothed - np.min(smoothed)) / (np.max(smoothed) - np.min(smoothed))
    img_uint8 = (norm * 255).astype(np.uint8)

    # 2. Extract linear features
    lines = lsd(img_uint8)
    streaklet_mask = np.zeros_like(img_uint8, dtype=bool)

    # 3. Filter segments by Euclidean length
    for line in lines:
        x0, y0, x1, y1, width = line
        length = np.hypot(x1 - x0, y1 - y0)
        if length >= min_length:
            rr, cc = draw_line(int(y0), int(x0), int(y1), int(x1))
            rr = np.clip(rr, 0, img_uint8.shape[0] - 1)
            cc = np.clip(cc, 0, img_uint8.shape[1] - 1)
            streaklet_mask[rr, cc] = True

    # 4. Clean morphological noise
    streaklet_mask = binary_dilation(streaklet_mask, footprint=disk(1))
    streaklet_mask = remove_small_objects(streaklet_mask, min_size=50)
    return streaklet_mask
```

### B. Moving Object Detection via Temporal Difference Stacking
Constructs an $(N, H, W)$ observation cube, subtracts the static median reference, and flags pixels exceeding the $3\sigma$ threshold:
```python
from skimage.morphology import binary_opening, remove_small_objects

def detect_moving_objects(data_cube):
    # Compute static reference background
    median_image = np.median(data_cube, axis=0)
    difference_cube = data_cube - median_image

    # Flag pixels exceeding 3-sigma noise threshold
    threshold = np.std(difference_cube) * 3.0
    moving_mask = np.max(difference_cube > threshold, axis=0)

    # Morphological filtering
    moving_mask = binary_opening(moving_mask, footprint=np.ones((3, 3)))
    moving_mask = remove_small_objects(moving_mask, min_size=20)
    return moving_mask
```

---

## 5. 🎯 Integration with SPHEREx Hunter

1. **Automated Candidate Filtering (`/api/source_discovery`):**
   - Incorporates CSA's `detect_streaklets` logic to identify and label linear asteroid trails.
   - Prevents fast solar system asteroids from polluting our cold brown dwarf / Planet X candidate list.
2. **Median Difference Normalization:**
   - Adapts the `difference_cube = data_cube - median_image` concept into our multi-epoch Astropy comparator to produce clean dipole signatures centered at neutral 128 mid-gray.
