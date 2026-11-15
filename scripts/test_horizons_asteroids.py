from astropy.time import Time
from astroquery.jplhorizons import Horizons

mjd = 60789.750762
t = Time(mjd, format='mjd')

for target in ['1', '2', '4', '433', '10', '15', '29', '52']:
    try:
        obj = Horizons(id=target, location='500@399', epochs=t.jd)
        eph = obj.ephemerides()
        ra = eph["RA"][0]
        dec = eph["DEC"][0]
        v = eph["V"][0]
        print(f"Asteroid {target}: RA={ra:.3f}, Dec={dec:.3f}, V={v:.2f}")
    except Exception as e:
        print(f"Error {target}: {e}")

