"""
Re-run obscore exposure queries against DR1 holdings using spatial-containment query:
CONTAINS(POINT('ICRS', ra, dec), s_region) = 1
Compare new exposure counts with cached counts and analyze cross-survey pairs.
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

try:
    with open("data_samples/irsa_obscore_cache.json") as f:
        old_cache = json.load(f)
except Exception:
    old_cache = {}

results = {}
comparison = {}

for k, v in targets.items():
    ra, dec = v["ra"], v["dec"]
    adql = f"""
    SELECT
        obs_id, obs_collection, s_ra, s_dec, t_min, t_max, t_exptime,
        energy_bandpassname, em_min, em_max, em_res_power,
        instrument_name, facility_name, calib_level, access_url, s_region
    FROM spherex.obscore
    WHERE CONTAINS(POINT('ICRS', {ra:.5f}, {dec:.5f}), s_region) = 1
    """
    print(f"Querying {v['name']} ({k})...", flush=True)
    try:
        qr = service.run_sync(adql)
        rows = []
        for r in qr:
            rows.append({
                "obs_id": str(r["obs_id"]),
                "obs_collection": str(r["obs_collection"]) if r["obs_collection"] else "spherex_dr1",
                "s_ra": float(r["s_ra"]),
                "s_dec": float(r["s_dec"]),
                "t_min": float(r["t_min"]) if r["t_min"] is not None else None,
                "t_max": float(r["t_max"]) if r["t_max"] is not None else None,
                "t_exptime": float(r["t_exptime"]) if r["t_exptime"] is not None else None,
                "band": str(r["energy_bandpassname"]),
                "em_min_m": float(r["em_min"]) if r["em_min"] is not None else None,
                "em_max_m": float(r["em_max"]) if r["em_max"] is not None else None,
                "em_res_power": float(r["em_res_power"]) if r["em_res_power"] is not None else None,
                "access_url": str(r["access_url"]) if r["access_url"] is not None else None,
                "s_region": str(r["s_region"]) if r["s_region"] is not None else None
            })
        rows.sort(key=lambda x: (x["t_min"] if x["t_min"] is not None else 0))
        old_count = old_cache.get(k, {}).get("count", old_cache.get(k, {}).get("total_exposures", 0))
        results[k] = {
            "target": v["name"],
            "count": len(rows),
            "data_release": "DR1",
            "exposures": rows
        }
        comparison[k] = {
            "target": v["name"],
            "old_cone_count": old_count,
            "new_spatial_containment_count": len(rows),
            "delta": len(rows) - old_count
        }
        print(f"-> {v['name']}: old={old_count}, new={len(rows)} (delta={len(rows)-old_count})", flush=True)
    except Exception as e:
        print(f"-> {v['name']} error: {e}", flush=True)
        results[k] = {"target": v["name"], "error": str(e), "count": 0}

with open("data_samples/irsa_obscore_dr1_cache.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n--- Summary of Comparison ---", flush=True)
for k, v in comparison.items():
    print(f"{v['target']}: Old={v['old_cone_count']} -> New(DR1)={v['new_spatial_containment_count']} (Delta={v['delta']})", flush=True)
