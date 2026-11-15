"""
Queries NASA IRSA TAP spherex.obscore for all benchmark demo targets,
computes observation dates, wavelengths, and evaluates pair feasibility.
"""

import json

import pyvo as vo

service = vo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")

targets = {
    "wise0855": {"name": "WISE 0855-0714", "ra": 133.79513, "dec": -7.24515},
    "barnard": {"name": "Barnard's Star", "ra": 269.45208, "dec": 4.69339},
    "epsindi": {"name": "Epsilon Indi B", "ra": 330.84042, "dec": -56.78778},
    "rwaur": {"name": "RW Aurigae", "ra": 77.10667, "dec": 30.40111},
    "rdraconis": {"name": "R Draconis", "ra": 248.33750, "dec": 66.70278},
    "sample_leo": {"name": "Leo Minor Sample Locus", "ra": 160.61524, "dec": 30.66908}
}

results = {}
for k, v in targets.items():
    ra, dec = v["ra"], v["dec"]
    # 0.5 deg cone search
    adql = f"""
    SELECT TOP 50
        obs_id, s_ra, s_dec, t_min, t_max, t_exptime,
        energy_bandpassname, em_min, em_max, em_res_power,
        instrument_name, facility_name, calib_level, access_url
    FROM spherex.obscore
    WHERE CONTAINS(POINT('ICRS', s_ra, s_dec), CIRCLE('ICRS', {ra:.5f}, {dec:.5f}, 0.5)) = 1
    ORDER BY t_min ASC
    """
    try:
        qr = service.run_sync(adql)
        rows = []
        for r in qr:
            rows.append({
                "obs_id": str(r["obs_id"]),
                "s_ra": float(r["s_ra"]),
                "s_dec": float(r["s_dec"]),
                "t_min": float(r["t_min"]) if r["t_min"] is not None else None,
                "t_max": float(r["t_max"]) if r["t_max"] is not None else None,
                "t_exptime": float(r["t_exptime"]) if r["t_exptime"] is not None else None,
                "band": str(r["energy_bandpassname"]),
                "em_min_m": float(r["em_min"]) if r["em_min"] is not None else None,
                "em_max_m": float(r["em_max"]) if r["em_max"] is not None else None,
                "em_res_power": float(r["em_res_power"]) if r["em_res_power"] is not None else None,
                "access_url": str(r["access_url"]) if r["access_url"] is not None else None
            })
        results[k] = {"target": v["name"], "count": len(rows), "exposures": rows}
        print(f"{v['name']}: {len(rows)} SPHEREx exposures found in IRSA ObsCore")
    except Exception as e:
        print(f"{v['name']} error: {e}")
        results[k] = {"target": v["name"], "error": str(e), "count": 0}

with open("data_samples/irsa_obscore_cache.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved data_samples/irsa_obscore_cache.json")

