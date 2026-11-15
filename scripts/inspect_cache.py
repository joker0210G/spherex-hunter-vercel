import json

with open("data_samples/irsa_obscore_cache.json") as f:
    data = json.load(f)

for k, val in data.items():
    print(f"=== {val['target']} ({val['count']} exposures) ===")
    for exp in val.get("exposures", [])[:4]:
        em_min_um = exp["em_min_m"] * 1e6 if exp["em_min_m"] else 0.0
        em_max_um = exp["em_max_m"] * 1e6 if exp["em_max_m"] else 0.0
        print(f"  ID: {exp['obs_id'][:30]} | Band: {exp['band']} | Range: {em_min_um:.2f}-{em_max_um:.2f} um | MJD: {exp['t_min']}")

