import httpx

client = httpx.Client(timeout=30.0)

for key, ra, dec in [('wise0855', 133.79513, -7.24515), ('barnard', 269.45208, 4.69339)]:
    r_cut = client.get(f'http://127.0.0.1:8000/api/cutout?ra={ra}&dec={dec}&target={key}&fov=3.0&lod=1').json()
    r_scene = client.get(f'http://127.0.0.1:8000/api/scene?fov=3.0&target={key}&ra={ra}&dec={dec}').json()
    r_spec = client.get(f'http://127.0.0.1:8000/api/spectrum?ra={ra}&dec={dec}&target={key}').json()
    r_gaia = client.get(f'http://127.0.0.1:8000/api/gaia?ra={ra}&dec={dec}&fov=3.0').json()

    print(f"=== {key.upper()} ===")
    print("Cutout Status:", r_cut.get("status"), "| Target:", r_cut.get("target"))
    print("Transient Vector:", r_cut.get("motion_vector"))
    print("Scene Target:", r_scene["target"]["name"], "| Tier:", r_scene["target"]["evidence_tier"])
    print("Total PM:", r_scene["target"]["total_pm_arcsec_yr"], '"/yr | Teff:', r_scene["target"]["effective_temp_k"], "K")
    print("Spectrum Bands:", len(r_spec.get("bands", [])))
    print("Gaia Stars in Field:", len(r_gaia.get("sources", [])))
    if r_gaia.get("sources"):
        s0 = r_gaia["sources"][0]
        print(f"Nearest Gaia Star: G={s0.get('phot_g_mag')}, PM={s0.get('total_pm_mas_yr')} mas/yr")
    print()
