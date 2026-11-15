import numpy as np
from astropy.time import Time
from astroquery.jplhorizons import Horizons

mjd = 60789.750762
t = Time(mjd, format='mjd')

# Field center: RA=160.615, Dec=30.669, radius=2.5 deg
ra_target = 160.615
dec_target = 30.669

print(f"Searching for asteroids near RA={ra_target}, Dec={dec_target} at MJD={mjd}...")
found = []
for ast_id in range(1, 201):
    try:
        obj = Horizons(id=str(ast_id), location='500@399', epochs=t.jd)
        eph = obj.ephemerides()
        ra = float(eph["RA"][0])
        dec = float(eph["DEC"][0])
        dra = (ra - ra_target) * np.cos(np.radians(dec_target))
        ddec = dec - dec_target
        sep = np.hypot(dra, ddec)
        if sep < 5.0:  # within 5 degrees
            v = float(eph["V"][0]) if eph["V"][0] is not None else 99.0
            print(f"Hit! Asteroid {ast_id}: separation = {sep:.2f} deg, V = {v:.2f}")
            found.append((ast_id, sep, v, ra, dec))
    except Exception:
        pass

print(f"Done. Found {len(found)} asteroids within 5 degrees.")

