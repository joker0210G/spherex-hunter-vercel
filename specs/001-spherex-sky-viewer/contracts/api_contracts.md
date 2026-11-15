# API Contracts: SPHEREx Hunter Astronomical Backend

## Base URL: `http://localhost:8000/api`

---

### Endpoint 1: `/cutout`
Retrieves multi-epoch astronomical cutouts and difference imaging map.

- **Method:** `GET`
- **Parameters:**
  - `ra` (float, required): Right Ascension in decimal degrees (or sexagesimal parsed by backend).
  - `dec` (float, required): Declination in decimal degrees.
  - `fov` (float, optional, default: 3.0): Field of View in arcminutes.
  - `target` (string, optional): Benchmark key (`wise0855`, `barnard`, `epsindi`, `rwaur`, `rdraconis`).
- **Response Format (200 OK):**
```json
{
  "status": "success",
  "target": "WISE 0855-0714",
  "coordinates": {
    "ra_deg": 133.79513,
    "dec_deg": -7.24515,
    "fov_arcmin": 3.0
  },
  "archive_survey": "WISE 4.6 / SPHEREx",
  "epochs": [
    {
      "frame": 1,
      "label": "SPHEREx Pass 1 (May 2025)",
      "date": "2025-05-18",
      "image_data": "data:image/png;base64,..."
    },
    {
      "frame": 2,
      "label": "SPHEREx Pass 2 (Nov 2025)",
      "date": "2025-11-20",
      "image_data": "data:image/png;base64,..."
    }
  ],
  "difference_image": {
    "label": "Difference Map (I2 - I1)",
    "image_data": "data:image/png;base64,..."
  },
  "motion_vector": {
    "epoch1_pos": {"x": 182, "y": 206},
    "epoch2_pos": {"x": 200, "y": 212},
    "shift_arcsec": 8.12,
    "is_variable": false
  },
  "telemetry": {
    "proper_motion_mas_yr": 8554.0,
    "object_type": "Sub-stellar Cold Y-Dwarf",
    "estimated_temp_k": 250,
    "coadd_snr_boost": "4.12x (6 detector arrays)",
    "noise_filter": "Background sigma-clipped (CRT static suppressed)"
  }
}
```

---

### Endpoint 2: `/spectrum`
Returns the 102 near-infrared spectral bands (0.75 - 5.0 μm) with molecular detection metadata.

- **Method:** `GET`
- **Parameters:**
  - `ra` (float, required)
  - `dec` (float, required)
  - `target` (string, optional)
- **Response Format (200 OK):**
```json
{
  "wavelengths_microns": [0.75, 0.79, 0.83, ..., 5.00],
  "flux_microjanskys": [12.4, 15.8, ..., 3.2],
  "detector_arrays": {
    "Array_1": {"bands": "1-17", "range": "0.75 - 1.11 μm"},
    "Array_2": {"bands": "18-34", "range": "1.11 - 1.64 μm"},
    "Array_3": {"bands": "35-51", "range": "1.64 - 2.42 μm"},
    "Array_4": {"bands": "52-68", "range": "2.42 - 3.82 μm"},
    "Array_5": {"bands": "69-85", "range": "3.82 - 4.42 μm (Water/CO Ice)"},
    "Array_6": {"bands": "86-102", "range": "4.42 - 5.00 μm (CO2 Ice & Organics)"}
  },
  "detected_molecules": [
    {"molecule": "H2O Ice", "wavelength_um": 3.05, "confidence": "98.2%"},
    {"molecule": "CH4 Methane", "wavelength_um": 3.30, "confidence": "92.5%"},
    {"molecule": "CO2 Ice", "wavelength_um": 4.27, "confidence": "96.7%"}
  ]
}
```
