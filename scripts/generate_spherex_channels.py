#!/usr/bin/env python3
"""
🛰️ SPHEREx 102-Spectral-Channel Table Generator (NASA Space Apps Challenge 2026)
Source: Official NASA IRSA SPHEREx DR1 all-sky data cube properties & Explanatory Supplement:
https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube/properties
https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf

Produces: frontend/src/data/spherex_102_channels.json
"""

import json
from pathlib import Path

# Official 102 channel central wavelengths (microns) extracted from IRSA data_cube_crval3_arr
IRSA_CRVAL3_STR = (
    "0.753 0.771 0.790 0.809 0.828 0.848 0.868 0.889 0.910 0.932 0.955 0.978 1.001 1.025 1.050 1.075 1.102 "
    "1.113 1.139 1.167 1.195 1.224 1.254 1.284 1.315 1.346 1.378 1.412 1.446 1.481 1.517 1.554 1.592 1.631 "
    "1.656 1.695 1.735 1.775 1.818 1.861 1.905 1.949 1.995 2.041 2.089 2.139 2.189 2.240 2.292 2.345 2.399 "
    "2.445 2.506 2.575 2.646 2.719 2.794 2.871 2.951 3.033 3.118 3.204 3.293 3.383 3.476 3.570 3.667 3.768 "
    "3.833 3.867 3.901 3.935 3.970 4.005 4.040 4.076 4.112 4.148 4.184 4.220 4.257 4.294 4.331 4.368 4.405 "
    "4.435 4.467 4.500 4.533 4.566 4.600 4.635 4.669 4.704 4.739 4.773 4.808 4.843 4.879 4.915 4.951 4.988"
)

# Band definitions matching NASA SPHEREx instrument specs
BAND_SPECS = [
    {"band": 1, "array_id": "A1", "name": "Array 1 (0.75-1.11 µm)", "resolving_power": 41, "science": "Stellar continuum & proper motion"},
    {"band": 2, "array_id": "A2", "name": "Array 2 (1.11-1.64 µm)", "resolving_power": 41, "science": "2MASS J/H overlap, stellar photospheres"},
    {"band": 3, "array_id": "A3", "name": "Array 3 (1.64-2.42 µm)", "resolving_power": 41, "science": "2MASS Ks overlap, warm circumstellar dust"},
    {"band": 4, "array_id": "A4", "name": "Array 4 (2.42-3.82 µm)", "resolving_power": 35, "science": "H₂O Ice (3.05 µm), CH₄ Methane (3.30 µm)"},
    {"band": 5, "array_id": "A5", "name": "Array 5 (3.82-4.42 µm)", "resolving_power": 112, "science": "CO₂ Ice (4.27 µm), Brown Dwarf thermal peak"},
    {"band": 6, "array_id": "A6", "name": "Array 6 (4.42-5.00 µm)", "resolving_power": 128, "science": "CO Carbon Monoxide (4.67 µm), Organics"}
]

# Key astrophysical feature annotations (literature citations)
MOLECULAR_FEATURES = [
    {"name": "H2O Ice (1.4 µm)", "wavelength_um": 1.412, "citation": "Aikawa et al. 2012"},
    {"name": "H2O Ice (1.9 µm)", "wavelength_um": 1.949, "citation": "Boogert et al. 2015"},
    {"name": "H2O Ice (3.05 µm)", "wavelength_um": 3.033, "citation": "Gibb et al. 2004"},
    {"name": "PAH / Organics (3.3 µm)", "wavelength_um": 3.293, "citation": "Tielens 2008"},
    {"name": "CO2 Ice (4.27 µm)", "wavelength_um": 4.257, "citation": "Pontoppidan et al. 2008"},
    {"name": "CO Gas / Ice (4.67 µm)", "wavelength_um": 4.669, "citation": "Boogert et al. 2002"}
]

def generate_channels():
    wavelengths = [float(w) for w in IRSA_CRVAL3_STR.split()]
    assert len(wavelengths) == 102, f"Expected 102 wavelengths, got {len(wavelengths)}"

    channels = []
    for idx, wl in enumerate(wavelengths):
        channel_id = idx + 1
        band_num = (idx // 17) + 1
        sub_channel = (idx % 17) + 1
        spec = BAND_SPECS[band_num - 1]
        r = spec["resolving_power"]

        # Channel bandwidth estimate: delta_lambda = lambda / R
        delta_lambda = round(wl / r, 4)

        # Check for molecular line alignment within delta_lambda
        matched_feature = None
        for mf in MOLECULAR_FEATURES:
            if abs(wl - mf["wavelength_um"]) <= (delta_lambda * 0.75):
                matched_feature = mf
                break

        # Note: Frames 50 and 51 (band 3 channel 17, band 4 channel 1) are dichroic boundaries
        is_dichroic_boundary = (channel_id in [50, 51])

        channels.append({
            "channel_id": channel_id,
            "band": band_num,
            "sub_channel": sub_channel,
            "array_id": spec["array_id"],
            "lambda_center_um": wl,
            "delta_lambda_um": delta_lambda,
            "resolving_power": r,
            "is_dichroic_boundary": is_dichroic_boundary,
            "molecular_feature": matched_feature["name"] if matched_feature else None,
            "citation": matched_feature["citation"] if matched_feature else "NASA/JPL-Caltech/IPAC SPHEREx DR1"
        })

    payload = {
        "metadata_source": "NASA/JPL-Caltech/IPAC SPHEREx DR1 all-sky cube properties",
        "documentation_url": "https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube/properties",
        "explanatory_supplement": "https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf",
        "total_channels": len(channels),
        "total_bands": 6,
        "channels_per_band": 17,
        "band_specifications": BAND_SPECS,
        "channels": channels
    }

    out_dir = Path("frontend/src/data")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "spherex_102_channels.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"✅ Generated {len(channels)} channels into {out_file}")
    return payload

if __name__ == "__main__":
    generate_channels()
