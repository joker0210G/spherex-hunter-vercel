"""
🛰️ SPHEREx Hunter - Exposure Wavelength Pairing & Feasibility Analyzer
NASA Space Apps Challenge 2026 - Team RIP

Analyzes SPHEREx survey coverage and Linear Variable Filter (LVF) dispersion
at target celestial positions to determine epoch differencing feasibility:
1. Wavelength-matched pairs (same detector array, |lambda1 - lambda2| <= delta_lambda)
   -> Qualified for ZOGY PSF-matched optimal image differencing.
2. Unmatched exposures (differing wavelengths or multi-survey 2MASS/WISE/SPHEREx)
   -> Forward-model residuals via catalog SED cross-calibration.
3. Uncovered regions -> Flagged as unfeasible for differencing.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ExposureRecord:
    exposure_id: str
    survey: str
    instrument: str
    detector: str
    mjd_obs: float
    wavelength_um: float
    channel_fwhm_um: float
    pixel_scale_arcsec: float


def compute_spherex_channel_fwhm(wavelength_um: float, band: int) -> float:
    """
    Computes SPHEREx spectral resolving power R = lambda / delta_lambda:
    - Bands 1-3 (0.75 - 2.42 um): R ~ 41 -> delta_lambda = lambda / 41
    - Bands 4-6 (2.42 - 5.00 um): R ~ 135 -> delta_lambda = lambda / 135
    """
    if band <= 3:
        resolving_power = 41.4
    else:
        resolving_power = 135.0
    return float(wavelength_um / resolving_power)


def evaluate_epoch_pairing_feasibility(
    target_name: str,
    exposures: List[ExposureRecord]
) -> Dict[str, Any]:
    """
    Evaluates epoch pairing feasibility for a list of exposures over a celestial coordinate.
    """
    n_exp = len(exposures)
    matched_pairs = []
    unmatched_pairs = []

    for i in range(n_exp):
        for j in range(i + 1, n_exp):
            exp_a = exposures[i]
            exp_b = exposures[j]

            # Condition 1: Same survey & detector
            same_detector = (exp_a.survey == exp_b.survey) and (exp_a.detector == exp_b.detector)
            # Condition 2: Wavelength match within channel width
            mean_fwhm = 0.5 * (exp_a.channel_fwhm_um + exp_b.channel_fwhm_um)
            delta_wave = abs(exp_a.wavelength_um - exp_b.wavelength_um)
            is_wave_matched = same_detector and (delta_wave <= mean_fwhm)

            pair_info = {
                "pair": (exp_a.exposure_id, exp_b.exposure_id),
                "det_a": exp_a.detector,
                "det_b": exp_b.detector,
                "mjd_a": exp_a.mjd_obs,
                "mjd_b": exp_b.mjd_obs,
                "dt_days": round(abs(exp_b.mjd_obs - exp_a.mjd_obs), 2),
                "wave_a_um": exp_a.wavelength_um,
                "wave_b_um": exp_b.wavelength_um,
                "delta_wave_um": round(delta_wave, 4),
                "channel_fwhm_um": round(mean_fwhm, 4),
                "is_matched": is_wave_matched,
                "recommended_method": "ZOGY_SUBTRACTION" if is_wave_matched else "FORWARD_MODEL_RESIDUALS"
            }

            if is_wave_matched:
                matched_pairs.append(pair_info)
            else:
                unmatched_pairs.append(pair_info)

    status = "FEASIBLE_ZOGY" if len(matched_pairs) > 0 else (
        "FEASIBLE_FORWARD_MODEL" if len(unmatched_pairs) > 0 else "UNFEASIBLE_NO_PAIRS"
    )

    return {
        "target": target_name,
        "num_exposures": n_exp,
        "num_matched_pairs": len(matched_pairs),
        "num_unmatched_pairs": len(unmatched_pairs),
        "status": status,
        "matched_pairs": matched_pairs,
        "unmatched_pairs": unmatched_pairs
    }

