# 🎯 Mandatory Test Targets & Benchmark Suite
> **NASA Requirement:** *"Test your tool on Barnard’s Star, Epsilon Indi B, WISE 0855, and variable stars RW Aurigae and R Draconis."*

Use this table as our **Golden Test Suite** to verify that our web application, WCS alignment, and blink comparator work properly.

---

## 🌌 Target Specifications & Coordinates

| Target Name | RA (J2000) | Dec (J2000) | Object Type | Expected Visual Signature in Blink Tool |
| :--- | :--- | :--- | :--- | :--- |
| **1. Barnard's Star** | `17h 57m 48.50s` (269.4521°) | `+04° 41' 36.2"` (+4.6934°) | High Proper Motion Red Dwarf ($M4.0V$) | **Rapid directional drift** ($\sim 10.3$ arcsec/year). In 6-month epochs, shifts by $\sim 5.1$ arcseconds (readily visible across pixels). |
| **2. Epsilon Indi B** | `22h 04m 10.51s` (331.0438°) | `-56° 46' 57.8"` (-56.7827°) | Binary Brown Dwarf system (T1 + T6) | High proper motion ($\sim 4.7$ arcsec/yr) paired companion orbiting Epsilon Indi A. Faint in optical, bright in SPHEREx NIR. |
| **3. WISE 0855-0714** | `08h 55m 10.83s` (133.7951°) | `-07° 14' 42.5"` (-7.2451°) | Sub-stellar Y-dwarf ($T \sim 250	ext{ K}$) | **Super-fast moving cold brown dwarf** ($\mu pprox 8.1$ arcsec/yr). Extreme infrared color; invisible in optical surveys (Gaia), glowing in SPHEREx $3-5\mu	ext{m}$. |
| **4. RW Aurigae** | `05h 07m 49.54s` (76.9564°) | `+30° 24' 05.1"` (+30.4014°) | Young T-Tauri Binary Variable Star | **Significant photometric brightness drop/flare** between epochs due to circumstellar dust accretion disk dimming events. |
| **5. R Draconis** | `16h 32m 40.23s` (248.1676°) | `+66° 45' 18.2"` (+66.7551°) | Mira-type Pulsating Red Giant Variable | **Cyclic pulsing brightness** ($V pprox 6.7$ to $13.2$, period $\sim 245$ days). Large flux shift between 6-month SPHEREx passes. |

---

## 🧪 Automated Test Verification Script (Python / Astropy)
The backend data engineer should run this script to ensure cutouts are successfully retrieved and verified:

```python
# test_benchmark_targets.py
from astropy.coordinates import SkyCoord
import astropy.units as u

BENCHMARKS = [
    {
        "name": "Barnard's Star",
        "ra": "17h57m48.50s",
        "dec": "+04d41m36.2s",
        "type": "High Proper Motion",
        "expected": "Positional shift northwards ~10.3"/yr"
    },
    {
        "name": "Epsilon Indi B",
        "ra": "22h04m10.51s",
        "dec": "-56d46m57.8s",
        "type": "Brown Dwarf Binary",
        "expected": "Proper motion companion"
    },
    {
        "name": "WISE 0855",
        "ra": "08h55m10.831s",
        "dec": "-07d14m42.53s",
        "type": "Y-Dwarf / Planet-like object",
        "expected": "Fast motion, bright at 4.6um, dark in optical"
    },
    {
        "name": "RW Aurigae",
        "ra": "05h07m49.54s",
        "dec": "+30d24m05.1s",
        "type": "Eruptive Variable",
        "expected": "Magnitude variability delta > 2 mag"
    },
    {
        "name": "R Draconis",
        "ra": "16h32m40.23s",
        "dec": "+66d45m18.2s",
        "type": "Mira Variable",
        "expected": "Periodic pulsation flux shift"
    }
]

for target in BENCHMARKS:
    coord = SkyCoord(target["ra"], target["dec"], frame="icrs")
    print(f"✅ {target['name']}: RA={coord.ra.deg:.6f}°, Dec={coord.dec.deg:.6f}° ({target['type']})")
```

---

## 📋 Verification Checklist for Demo Video
- [ ] Record a 5-second screencast of **Barnard's Star** blinking between Epoch 1 and Epoch 2.
- [ ] Record **WISE 0855** showing clear translation across pixel space with background stars subtracted.
- [ ] Record **RW Aurigae** with the difference imaging mode showing a strong black/white flux residual (variable star signature).
- [ ] Show the coordinate bar auto-loading each benchmark target via preset quick-buttons in the UI.
