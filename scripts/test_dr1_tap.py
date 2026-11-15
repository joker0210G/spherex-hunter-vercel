import pyvo as vo

service = vo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")

ra, dec = 133.79513, -7.24515

q = f"""
SELECT TOP 10
    obs_id, obs_collection, s_ra, s_dec, t_min, t_max, t_exptime,
    energy_bandpassname, em_min, em_max, s_region, access_url
FROM spherex.obscore
WHERE CONTAINS(POINT('ICRS', {ra:.5f}, {dec:.5f}), s_region) = 1
ORDER BY t_min ASC
"""

res = service.run_sync(q)
print(f"Results with CONTAINS(POINT, s_region): {len(res)} rows")
for r in res:
    print(dict(r))
