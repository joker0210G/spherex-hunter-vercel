"""
Finds real SPHEREx exposures matching known asteroids (Ceres, Vesta, Pallas, Iris)
using JPL Horizons ephemerides and cross-matching against spherex.obscore.
"""

import json

import pyvo as vo
from astropy.time import Time

service = vo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")

# Check 4 major asteroids: Ceres (1), Pallas (2), Vesta (4), Iris (7)
asteroid_targets = ["1", "2", "4", "7"]
recovered_asteroids = []

print("🔭 Checking JPL Horizons ephemerides for major asteroids during SPHEREx 2025 mission...")

try:
    from astroquery.jplhorizons import Horizons
    for ast_id in asteroid_targets:
        # Check mid-2025 epochs
        epochs = ["2025-04-15", "2025-06-15", "2025-08-15", "2025-10-15"]
        for ep_str in epochs:
            t = Time(ep_str)
            obj = Horizons(id=ast_id, location="500@0", epochs=t.jd)
            eph = obj.ephemerides()
            if len(eph) > 0:
                ra_deg = float(eph["RA"][0])
                dec_deg = float(eph["DEC"][0])
                v_mag = float(eph["V"][0]) if "V" in eph.colnames else None
                ast_name = str(eph["targetname"][0])

                # Check if SPHEREx has observations in spherex.obscore near this position
                adql = f"""
                SELECT TOP 5
                    obs_id, s_ra, s_dec, t_min, t_max, energy_bandpassname
                FROM spherex.obscore
                WHERE CONTAINS(POINT('ICRS', s_ra, s_dec), CIRCLE('ICRS', {ra_deg:.4f}, {dec_deg:.4f}, 0.5)) = 1
                """
                res = service.run_sync(adql)
                if len(res) > 0:
                    print(f"🎯 MATCH FOUND! {ast_name} at ({ra_deg:.2f}, {dec_deg:.2f}) has {len(res)} SPHEREx exposures in IRSA!")
                    recovered_asteroids.append({
                        "name": ast_name,
                        "asteroid_id": ast_id,
                        "epoch": ep_str,
                        "ra_deg": ra_deg,
                        "dec_deg": dec_deg,
                        "v_mag": v_mag,
                        "spherex_exposures_count": len(res),
                        "sample_obs_id": str(res[0]["obs_id"])
                    })
                    break
except Exception as e:
    print("Horizons query note:", e)

with open("data_samples/known_asteroids_recovered.json", "w") as f:
    json.dump(recovered_asteroids, f, indent=2)

print(f"Total known asteroids matched to SPHEREx coverage: {len(recovered_asteroids)}")

