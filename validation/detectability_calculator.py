"""
🛰️ SPHEREx Hunter - Planet X Detectability & Sensitivity Calculator
NASA Space Apps Challenge 2026 - Team RIP

Computes realistic point-source flux (reflected sunlight + thermal emission)
for hypothetical outer Solar System bodies vs distance (50 - 1000 AU) and effective temperature,
and benchmarks directly against SPHEREx's empirical 5-sigma detection limits.
Outputs publication-ready sensitivity plot: docs/figures/detectability_map.png
"""

import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Constants
H_PLANCK = 6.62607015e-34    # J s
C_LIGHT = 2.99792458e8       # m / s
K_BOLTZ = 1.380649e-23       # J / K
AU_METERS = 1.495978707e11   # m
R_EARTH_METERS = 6.371e6     # m
SOLAR_CONSTANT_1AU = 1361.0  # W / m^2


def planck_b_lambda(wavelength_m: float, temp_k: float) -> float:
    """Computes Planck spectral radiance B_lambda in W / (m^2 sr m)."""
    if temp_k <= 0:
        return 0.0
    x = (H_PLANCK * C_LIGHT) / (wavelength_m * K_BOLTZ * temp_k)
    if x > 100.0:  # Avoid overflow on Wien tail
        return 0.0
    num = 2.0 * H_PLANCK * (C_LIGHT**2) / (wavelength_m**5)
    denom = np.expm1(x)
    return float(num / denom)


def compute_outer_planet_flux_ujy(
    distance_au: float,
    radius_earth_radii: float = 3.0,
    geometric_albedo: float = 0.4,
    effective_temp_k: float = 45.0,
    wavelength_um: float = 4.5
) -> dict:
    """
    Computes total point source flux in uJy at wavelength_um for an outer body:
    F_total = F_reflected + F_thermal
    """
    r_body_m = radius_earth_radii * R_EARTH_METERS
    d_m = distance_au * AU_METERS
    wave_m = wavelength_um * 1.0e-6

    # 1. Reflected solar flux (uJy)
    # Solar spectral flux density at 1 AU ~ 2.0 W/m^2/um at 4.5 um
    # F_refl = F_sun(1AU) / d^2 * p * (R/d)^2
    f_sun_at_wave_w_m2_m = 0.5e6  # ~0.5 W/m^2/micron = 0.5e6 W/m^2/m at 4.5 um
    f_refl_w_m2_m = f_sun_at_wave_w_m2_m * geometric_albedo * (r_body_m**2) / (distance_au**2 * d_m**2)
    # Convert W/m^2/m to W/m^2/Hz: dnu = c / lambda^2 * dlambda -> F_nu = F_lambda * lambda^2 / c
    f_refl_nu_w_m2_hz = f_refl_w_m2_m * (wave_m**2) / C_LIGHT
    # 1 Jy = 10^-26 W/m^2/Hz -> 1 uJy = 10^-32 W/m^2/Hz
    flux_refl_ujy = float(f_refl_nu_w_m2_hz * 1e32)

    # 2. Thermal emission (uJy)
    b_lambda = planck_b_lambda(wave_m, effective_temp_k)
    # Surface flux = pi * B_lambda, received flux at distance d = pi * B_lambda * (R / d)^2
    f_therm_w_m2_m = np.pi * b_lambda * (r_body_m / d_m)**2
    f_therm_nu = f_therm_w_m2_m * (wave_m**2) / C_LIGHT
    flux_therm_ujy = float(f_therm_nu * 1e32)

    return {
        "distance_au": distance_au,
        "flux_refl_ujy": flux_refl_ujy,
        "flux_therm_ujy": flux_therm_ujy,
        "flux_total_ujy": flux_refl_ujy + flux_therm_ujy
    }


def generate_detectability_plot():
    """Generates publication-ready sensitivity comparison curve."""
    distances = np.linspace(50.0, 1000.0, 50)

    # Scenarios
    # 1. Standard cold Planet Nine: M ~ 5 M_earth, R ~ 3.0 R_earth, T_eff = 45 K (Fortney et al.)
    fluxes_p9_cold = [compute_outer_planet_flux_ujy(d, 3.0, 0.4, 45.0, 4.5)["flux_total_ujy"] for d in distances]
    # 2. Warm sub-stellar brown dwarf: T_eff = 250 K (WISE 0855 analogue)
    fluxes_warm_bd = [compute_outer_planet_flux_ujy(d, 11.2, 0.2, 250.0, 4.5)["flux_total_ujy"] for d in distances]
    # 3. Intermediate body: T_eff = 120 K
    fluxes_inter = [compute_outer_planet_flux_ujy(d, 4.0, 0.5, 120.0, 4.5)["flux_total_ujy"] for d in distances]

    # SPHEREx measured 5-sigma detection limit
    # Single exposure (Band 6 ~4.5 um): ~16 uJy
    # All-sky co-add (Survey 1-4 stack): ~3.5 uJy
    spherex_5sigma_single = 16.0  # uJy
    spherex_5sigma_stack = 3.5    # uJy

    plt.figure(figsize=(8, 5.5))
    plt.semilogy(distances, np.maximum(1e-6, fluxes_warm_bd), "r-", lw=2.5, label=r"Warm Sub-Stellar Brown Dwarf ($T=250\,\mathrm{K}$, $R=1\,R_{\mathrm{Jup}}$)")
    plt.semilogy(distances, np.maximum(1e-6, fluxes_inter), "m--", lw=2, label=r"Warm Gas Giant / KBO ($T=120\,\mathrm{K}$, $R=4\,R_\oplus$)")
    plt.semilogy(distances, np.maximum(1e-6, fluxes_p9_cold), "c:", lw=2, label=r"Cold Planet Nine ($T=45\,\mathrm{K}$, $R=3\,R_\oplus$, Fortney+16)")

    plt.axhline(spherex_5sigma_single, color="blue", ls="--", lw=1.5, label=r"SPHEREx Single-Exposure 5σ Limit ($16\,\mu\mathrm{Jy}$)")
    plt.axhline(spherex_5sigma_stack, color="navy", ls="-.", lw=1.5, label=r"SPHEREx Full-Survey Co-Add 5σ Limit ($3.5\,\mu\mathrm{Jy}$)")

    plt.xlim(50, 1000)
    plt.ylim(1e-5, 1e4)
    plt.xlabel("Heliocentric Distance (AU)", fontsize=11)
    plt.ylabel("Predicted Flux Density at 4.5 µm (µJy)", fontsize=11)
    plt.title("SPHEREx Hunter - Detectability Calculator at $\\lambda = 4.5\\,\\mu\\mathrm{m}$\n(Reflected Sunlight + Thermal Emission vs Empirical Limits)", fontsize=11)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(loc="upper right", fontsize=9)
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, "detectability_map.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"📊 Saved detectability map to {out_path}")


if __name__ == "__main__":
    generate_detectability_plot()

