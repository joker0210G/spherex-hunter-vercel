import json
from collections import defaultdict

with open("data_samples/irsa_obscore_dr1_cache.json") as f:
    data = json.load(f)

print("=== SPHEREx DR1 Cross-Survey Wavelength-Matched Pair Analysis ===")

SIX_MONTHS_DAYS = 182.6
MIN_SEPARATION = 130.0  # ~4.5 months
MAX_SEPARATION = 230.0  # ~7.5 months

results = {}

for target_id, target_data in data.items():
    target_name = target_data["target"]
    exposures = target_data["exposures"]

    # Group by band / detector
    by_band = defaultdict(list)
    for exp in exposures:
        band = exp["band"]
        by_band[band].append(exp)

    pairs = []
    # Check for matched pairs within each band
    for band, exps in by_band.items():
        exps.sort(key=lambda x: x["t_min"])
        for i in range(len(exps)):
            for j in range(i + 1, len(exps)):
                dt = exps[j]["t_min"] - exps[i]["t_min"]
                if MIN_SEPARATION <= dt <= MAX_SEPARATION:
                    # check wavelength match
                    w1_min, w1_max = exps[i]["em_min_m"], exps[i]["em_max_m"]
                    w2_min, w2_max = exps[j]["em_min_m"], exps[j]["em_max_m"]
                    # If same band and wavelength bounds match within 5%
                    if abs(w1_min - w2_min) / w1_min < 0.05 and abs(w1_max - w2_max) / w1_max < 0.05:
                        pairs.append({
                            "band": band,
                            "exp1": exps[i]["obs_id"],
                            "exp2": exps[j]["obs_id"],
                            "mjd1": exps[i]["t_min"],
                            "mjd2": exps[j]["t_min"],
                            "delta_days": round(dt, 2),
                            "em_min_um": round(w1_min * 1e6, 3),
                            "em_max_um": round(w1_max * 1e6, 3)
                        })

    # Also check short-baseline pairs (< 45 days)
    short_pairs = []
    for band, exps in by_band.items():
        for i in range(len(exps)):
            for j in range(i + 1, len(exps)):
                dt = exps[j]["t_min"] - exps[i]["t_min"]
                if 2.0 <= dt <= 45.0:
                    short_pairs.append({
                        "band": band,
                        "dt": round(dt, 2)
                    })

    mjd_min = min((e["t_min"] for e in exposures), default=0)
    mjd_max = max((e["t_min"] for e in exposures), default=0)
    total_span = round(mjd_max - mjd_min, 1)

    results[target_id] = {
        "target": target_name,
        "total_exposures": len(exposures),
        "mjd_span": total_span,
        "mjd_min": round(mjd_min, 2),
        "mjd_max": round(mjd_max, 2),
        "cross_survey_6mo_pairs_count": len(pairs),
        "short_baseline_pairs_count": len(short_pairs),
        "sample_6mo_pairs": pairs[:5]
    }
    print(f"\nTarget: {target_name} ({target_id})")
    print(f"  Total Exposures: {len(exposures)}")
    print(f"  Observation Baseline: {total_span} days (MJD {mjd_min:.1f} to {mjd_max:.1f})")
    print(f"  Cross-Survey ~6-Month Pairs (130-230 d): {len(pairs)}")
    print(f"  Short-Baseline Pairs (2-45 d): {len(short_pairs)}")
    if pairs:
        print("  Sample 6-month pairs:")
        for p in pairs[:3]:
            print(f"    - Band {p['band']}: {p['exp1']} (MJD {p['mjd1']:.1f}) <-> {p['exp2']} (MJD {p['mjd2']:.1f}), dt={p['delta_days']} d")

with open("data_samples/cross_survey_pairs_summary.json", "w") as f:
    json.dump(results, f, indent=2)
