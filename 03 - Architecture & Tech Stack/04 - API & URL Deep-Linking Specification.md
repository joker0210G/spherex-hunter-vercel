# 🌐 API & URL Deep-Linking Specification

---

## 1. REST API Endpoints (Backend)

### `GET /api/targets`
Returns the list of NASA benchmark presets.
```json
[
  {
    "id": "barnard",
    "name": "Barnard's Star",
    "ra": 269.45208,
    "dec": 4.69339,
    "fov": 180,
    "description": "High proper motion nearby red dwarf"
  },
  {
    "id": "wise0855",
    "name": "WISE 0855-0714",
    "ra": 133.79513,
    "dec": -7.24515,
    "fov": 120,
    "description": "Sub-stellar ultra-cool brown dwarf moving at 8 arcsec/yr"
  }
]
```

### `GET /api/cutouts`
Fetch multi-epoch imagery for a sky patch.
- **Query Params:**
  - `ra` (float, required): Right ascension in decimal degrees.
  - `dec` (float, required): Declination in decimal degrees.
  - `fov` (float, default `180`): Field of view in arcseconds.
  - `coadd` (bool, default `true`): Whether to co-add detector arrays.
- **Response:**
```json
{
  "coordinates": { "ra": 133.79513, "dec": -7.24515 },
  "fov_arcsec": 120,
  "epochs": [
    {
      "epoch_id": "SPHEREx_Pass_1",
      "date": "2025-06-15",
      "image_url": "/static/cutouts/wise0855_ep1.png"
    },
    {
      "epoch_id": "SPHEREx_Pass_2",
      "date": "2025-12-18",
      "image_url": "/static/cutouts/wise0855_ep2.png"
    }
  ],
  "difference_image_url": "/static/cutouts/wise0855_diff.png",
  "contamination_flags": {
    "cosmic_ray": false,
    "stray_light": false,
    "quality_score": 0.98
  }
}
```

### `GET /api/spectrum`
Returns the 102-band flux distribution at the specified pixel/coordinate.
- **Query Params:** `ra`, `dec`
- **Response:**
```json
{
  "wavelengths_microns": [0.75, 0.77, "...", 4.98, 5.00],
  "flux_microjanskys": [12.4, 12.8, "...", 85.3, 89.1],
  "detected_features": ["H2O Ice (3.05 μm)", "CO2 Ice (4.27 μm)"]
}
```

---

## 2. URL Query Parameter Specification (Deep-Linking)
NASA specifically highlights deep-linking as a key consideration so researchers can embed links into papers or share discoveries.

### URL Format:
`https://spherex-hunter.app/?ra={ra}&dec={dec}&fov={fov}&speed={speed}&mode={mode}`

### Parameter Definitions:
- `ra`: Decimal degrees or sexagesimal string (e.g. `133.7951` or `08h55m10.8s`).
- `dec`: Decimal degrees or sexagesimal string (e.g. `-7.2451` or `-07d14m42.5s`).
- `fov`: Field of view in arcseconds (e.g. `60`, `180`, `600`).
- `speed`: Playback speed in frames per second (e.g. `1`, `2`, `5`).
- `mode`: View mode (`blink`, `diff`, `split`).
- `survey`: Overlay survey (`none`, `gaia`, `wise`).

### Example Links:
- **Direct Link to WISE 0855 Blink:**
  `https://spherex-hunter.app/?ra=133.7951&dec=-7.2451&fov=120&speed=3&mode=blink`
- **Direct Link to RW Aurigae Difference Map:**
  `https://spherex-hunter.app/?ra=76.9564&dec=30.4014&fov=180&mode=diff`
