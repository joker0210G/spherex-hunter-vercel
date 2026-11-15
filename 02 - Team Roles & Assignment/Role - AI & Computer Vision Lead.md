# 🧠 Role: AI & Computer Vision Lead
> **Mission:** Implement difference imaging, transient candidate detection, and automated motion tracking between epochs.

---

## 🎯 Key Deliverables
1. **Difference Imaging Engine:**
   - Compute normalized image difference:
     $$\Delta I = I_{	ext{epoch } 2} - I_{	ext{epoch } 1}$$
   - Apply Gaussian smoothing to reduce sensor shot noise.
   - Moving objects and variable stars create distinct **dipole signatures** (a bright positive spot adjacent to a dark negative depression).
2. **Transient & Motion Scorer:**
   - Detect connected components above threshold ($3\sigma$ above background RMS).
   - Match detections across epochs to calculate apparent proper motion speed ($	ext{arcsec}/	ext{year}$).
   - Flag objects with high motion for the user with an intuitive bounding box / crosshair.
3. **Artifact & Contamination Filter:**
   - Distinguish real astronomical shifts from single-epoch artifacts (cosmic ray strikes, diffraction spikes, bad pixels).

---

## 🧪 Difference Imaging Algorithm (Python / OpenCV / SciPy)
```python
import numpy as np
from scipy.ndimage import gaussian_filter

def compute_difference_map(img1: np.ndarray, img2: np.ndarray, sigma: float = 1.0):
    """
    Compute normalized difference image with sub-pixel aligned epochs.
    """
    # Normalize flux levels to account for slight exposure/background variations
    norm1 = (img1 - np.median(img1)) / (np.std(img1) + 1e-6)
    norm2 = (img2 - np.median(img2)) / (np.std(img2) + 1e-6)
    
    # Difference
    diff = norm2 - norm1
    
    # Smooth high-frequency shot noise
    diff_smooth = gaussian_filter(diff, sigma=sigma)
    
    # Rescale to 0-255 for visualization
    diff_vis = np.clip(128 + diff_smooth * 30, 0, 255).astype(np.uint8)
    return diff_vis
```

---

## 🔗 Cross-Links
- Image Processing Spec: [[03 - Image Processing & Blink Comparator Spec]]
- Architecture: [[01 - Architecture Overview]]
