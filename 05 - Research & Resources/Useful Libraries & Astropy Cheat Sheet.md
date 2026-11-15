# 🧰 Useful Libraries & Astropy Cheat Sheet

---

## 1. Essential Python Packages
```bash
pip install astropy astroquery reproject numpy scipy pillow fastapi uvicorn
```

---

## 2. Astropy Coordinates & WCS Quick Reference

```python
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.io import fits
from astropy.wcs import WCS

# 1. Parse any coordinate string (sexagesimal or decimal)
c1 = SkyCoord("08h55m10.831s", "-07d14m42.53s", frame="icrs")
print(f"RA in deg: {c1.ra.deg}, Dec in deg: {c1.dec.deg}")

# 2. Compute angular separation between two detections
c2 = SkyCoord(ra=133.7955 * u.deg, dec=-7.2450 * u.deg, frame="icrs")
separation_arcsec = c1.separation(c2).arcsec
print(f"Shift: {separation_arcsec:.2f} arcsec")

# 3. Read WCS and pixel coordinates from FITS
hdu = fits.open("cutout.fits")[0]
w = WCS(hdu.header)
px, py = w.world_to_pixel(c1)
print(f"Pixel location on detector: X={px:.1f}, Y={py:.1f}")
```

---

## 3. JavaScript / Aladin Lite Integration
To embed the official CDS Strasbourg Aladin Lite v3 viewer in React:
```html
<!-- index.html -->
<script type="text/javascript" src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
```
```javascript
// Inside React Component
const aladin = A.aladin('#aladin-div', {
  survey: 'P/WISE/color',
  fov: 0.1,
  target: '08 55 10.83 -07 14 42.5'
});
```
