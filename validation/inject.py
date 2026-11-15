"""
🛰️ SPHEREx Hunter - Comprehensive Injection-Recovery Validation Engine
NASA Space Apps Challenge 2026 - Team RIP

Phase 2.9 Enhancements:
1. "Appearing Source" Benchmark:
   - Evaluates point sources with no counterpart in reference image.
   - Computes empirical completeness vs AB magnitude (16.0 to 19.5 mag, 50 trials/bin).
   - Overplots exact analytical Gaussian matched-filter completeness curve.
2. "Moving Dipole Tracklet" Benchmark:
   - Injects true mover present in BOTH epochs (+F in Ep2, +F in Ep1 displaced by Δr).
   - Tests displacements Δr = 1, 2, and 5 PSF widths (2.0, 4.0, 10.0 pixels).
   - Measures recovery of both positive lobe and negative well.
   - Evaluates tracklet linking success rate via flux conservation and velocity filtering.
"""

import csv
import os

import matplotlib
import numpy as np
from scipy import special, stats
from scipy.ndimage import map_coordinates

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.io import fits

from backend.science.differencing import construct_gaussian_psf, detect_and_veto_candidates, zogy_subtraction
from backend.science.preprocessing import preprocess_spherex_hdu
from backend.science.tracklet_linking import detect_negative_wells, link_dipole_tracklets

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data_samples")
FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "figures")
FITS_1_PATH = os.path.join(DATA_DIR, "spherex_level2_sample.fits")
FITS_2_PATH = os.path.join(DATA_DIR, "spherex_level2_pair_epoch2.fits")
RESULTS_CSV_PATH = os.path.join(os.path.dirname(__file__), "injection_results.csv")
os.makedirs(FIG_DIR, exist_ok=True)


def clopper_pearson_interval(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Computes exact Clopper-Pearson binomial confidence interval."""
    if n == 0:
        return 0.0, 1.0
    alpha = 1.0 - confidence
    low = stats.beta.ppf(alpha / 2.0, k, n - k + 1) if k > 0 else 0.0
    high = stats.beta.ppf(1.0 - alpha / 2.0, k + 1, n - k) if k < n else 1.0
    return float(low), float(high)


def ab_mag_to_flux_ujy(ab_mag: float) -> float:
    return float(10.0**((23.9 - ab_mag) / 2.5))


def run_injection_suite():
    print("🔬 Loading authentic SPHEREx Level 2 consecutive exposure pair...")
    assert os.path.exists(FITS_1_PATH), f"Missing {FITS_1_PATH}"
    assert os.path.exists(FITS_2_PATH), f"Missing {FITS_2_PATH}"

    with fits.open(FITS_1_PATH) as h1, fits.open(FITS_2_PATH) as h2:
        prep1 = preprocess_spherex_hdu(h1)
        prep2 = preprocess_spherex_hdu(h2)

    w1 = prep1.wcs
    w2 = prep2.wcs

    cy, cx = 1020, 1020
    size = 512
    y0, y1 = cy - size // 2, cy + size // 2
    x0, x1 = cx - size // 2, cx + size // 2

    patch1_flux = prep1.flux_ujy[y0:y1, x0:x1].copy()
    patch1_var = prep1.variance_ujy2[y0:y1, x0:x1].copy()

    yy, xx = np.mgrid[y0:y1, x0:x1]
    sky_coords = w1.pixel_to_world(xx, yy)
    x2_grid, y2_grid = w2.world_to_pixel(sky_coords)

    patch2_flux = map_coordinates(prep2.flux_ujy, [y2_grid, x2_grid], order=1, cval=np.nan).astype(np.float32)
    patch2_var = map_coordinates(prep2.variance_ujy2, [y2_grid, x2_grid], order=1, cval=np.nan).astype(np.float32)

    patch1_flux[~np.isfinite(patch1_flux)] = np.nanmedian(patch1_flux)
    patch2_flux[~np.isfinite(patch2_flux)] = np.nanmedian(patch2_flux)
    patch1_var[~np.isfinite(patch1_var)] = np.nanmedian(patch1_var)
    patch2_var[~np.isfinite(patch2_var)] = np.nanmedian(patch2_var)

    psf_template = construct_gaussian_psf(25, fwhm_pix=2.0)
    mag_bins = [16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5]
    n_per_bin = 50
    rate_pix_values = [1.5, 3.0, 5.0, 8.0]

    rng = np.random.default_rng(2026)
    bright_mask = patch1_flux > (np.median(patch1_flux) + 150.0)
    bright_y, bright_x = np.where(bright_mask)

    print(f"🚀 Running Part 1: Appearing Source Benchmark ({len(mag_bins)*n_per_bin} trials)...")
    results = []
    trial_idx = 0

    for mag in mag_bins:
        flux_ujy = ab_mag_to_flux_ujy(mag)
        recovered_in_bin = 0

        for trial in range(n_per_bin):
            trial_idx += 1
            rate_pix = rate_pix_values[trial % len(rate_pix_values)]

            strategy = trial % 10
            if strategy < 2 and len(bright_x) > 0:
                s_idx = rng.integers(0, len(bright_x))
                ix = float(np.clip(bright_x[s_idx] + rng.uniform(-4.0, 4.0), 20.0, size - 20.0))
                iy = float(np.clip(bright_y[s_idx] + rng.uniform(-4.0, 4.0), 20.0, size - 20.0))
                env = "crowded_bright_star"
            elif strategy == 2:
                ix = float(rng.choice([rng.uniform(8.0, 16.0), rng.uniform(size - 16.0, size - 8.0)]))
                iy = float(rng.uniform(8.0, size - 8.0))
                env = "detector_edge"
            else:
                ix = float(rng.uniform(25.0, size - 25.0))
                iy = float(rng.uniform(25.0, size - 25.0))
                env = "general_field"

            theta = rng.uniform(0, 2 * np.pi)
            ix2 = ix + rate_pix * np.cos(theta)
            iy2 = iy + rate_pix * np.sin(theta)

            mod_flux2 = patch2_flux.copy()
            mod_var2 = patch2_var.copy()

            p_rad = 12
            y_min = max(0, int(round(iy2)) - p_rad)
            y_max = min(size, int(round(iy2)) + p_rad + 1)
            x_min = max(0, int(round(ix2)) - p_rad)
            x_max = min(size, int(round(ix2)) + p_rad + 1)

            yy_sub, xx_sub = np.mgrid[y_min:y_max, x_min:x_max]
            r2 = (xx_sub - ix2)**2 + (yy_sub - iy2)**2
            sub_kernel = np.exp(-0.5 * r2 / (0.976**2))
            sub_kernel /= np.sum(sub_kernel)

            injected_patch = (flux_ujy * sub_kernel).astype(np.float32)
            mod_flux2[y_min:y_max, x_min:x_max] += injected_patch
            mod_var2[y_min:y_max, x_min:x_max] += np.maximum(0.0, injected_patch)

            diff, s_corr, _ = zogy_subtraction(
                mod_flux2, mod_var2, psf_template, patch1_flux, patch1_var, psf_template
            )
            candidates, _ = detect_and_veto_candidates(diff, s_corr, snr_threshold=5.0, edge_margin_pix=6)

            matched = None
            min_dist = 999.0
            for cand in candidates:
                d = np.hypot(cand.x_pix - ix2, cand.y_pix - iy2)
                if d < 3.0:
                    if d < min_dist:
                        min_dist = d
                        matched = cand

            is_recovered = False
            veto_reason = "UNDETECTED"
            if matched is not None:
                if matched.passed_vetoes:
                    is_recovered = True
                    recovered_in_bin += 1
                else:
                    veto_reason = matched.veto_reason

            results.append({
                "trial": trial_idx,
                "type": "appearing_source",
                "mag_ab": round(mag, 2),
                "flux_ujy": round(flux_ujy, 2),
                "rate_pix": round(rate_pix, 2),
                "environment": env,
                "recovered": int(is_recovered),
                "veto_reason": veto_reason,
                "dist_pix": round(min_dist, 2) if matched else None
            })

    # Save to CSV
    with open(RESULTS_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    # Completeness stats
    mag_stats = []
    for mag in mag_bins:
        b = [r for r in results if r["mag_ab"] == mag]
        k = sum(r["recovered"] for r in b)
        n = len(b)
        low, high = clopper_pearson_interval(k, n)
        mag_stats.append({"mag": mag, "comp": k / n, "low": low, "high": high})

    # Analytical completeness curve
    # sigma_diff_eff for Gaussian FWHM=2.0 pix is F_5sigma ~ 345 uJy -> m_5sigma = 17.56 mag
    m_dense = np.linspace(16.0, 19.5, 100)
    f_dense = 10**((23.9 - m_dense) / 2.5)
    # sigma_psf_diff = 345.14 / 5.0 = 69.03 uJy
    snr_dense = f_dense / 69.03
    # P(snr + noise >= 5.0) where noise ~ N(0, 1)
    analytical_comp = 0.5 * (1.0 + special.erf((snr_dense - 5.0) / np.sqrt(2.0)))

    plt.figure(figsize=(8, 5.5), dpi=200)
    mags = [s["mag"] for s in mag_stats]
    comps = [s["comp"] for s in mag_stats]
    err_l = [s["comp"] - s["low"] for s in mag_stats]
    err_h = [s["high"] - s["comp"] for s in mag_stats]

    plt.errorbar(
        mags, comps, yerr=[err_l, err_h], fmt="o", color="#00bcd4",
        ecolor="#00e5ff", elinewidth=2, capsize=4, label="Appearing Source Empirical (N=400, 95% CI)"
    )
    plt.plot(m_dense, analytical_comp, "--", color="#ff7043", linewidth=2, label="Analytical Gaussian Noise Curve (FWHM=2.0 pix, 5.0σ)")
    plt.axvline(17.56, color="#ff9800", linestyle=":", label="Analytical 5σ Limit (17.56 mag)")
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.xlabel("Source Brightness (AB Magnitude)", fontsize=11, fontweight="bold")
    plt.ylabel("Recovery Completeness Fraction", fontsize=11, fontweight="bold")
    plt.title("SPHEREx Hunter - Appearing Source Completeness vs AB Magnitude\n(Empirical vs Analytical Gaussian 5.0σ Threshold Dropoff)", fontsize=10)
    plt.ylim(-0.05, 1.05)
    plt.gca().invert_xaxis()
    plt.legend(loc="lower left", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "completeness_vs_mag.png"))
    plt.close()

    # Part 2: Moving Dipole & Tracklet Linking Benchmark
    print("🚀 Running Part 2: Moving Dipole Tracklet Benchmark (Displacements Δr = 1, 2, 5 FWHM)...")
    displacements_fwhm = [1.0, 2.0, 5.0]  # in units of FWHM (2.0 pix) -> 2.0, 4.0, 10.0 pixels
    mover_mag = 16.5  # Bright mover well above noise
    mover_flux = ab_mag_to_flux_ujy(mover_mag)
    n_mover_trials = 30

    dipole_results = []
    for d_fwhm in displacements_fwhm:
        d_pix = d_fwhm * 2.0
        n_pos_rec = 0
        n_neg_rec = 0
        n_linked = 0

        for trial in range(n_mover_trials):
            ix1 = float(rng.uniform(40.0, size - 40.0))
            iy1 = float(rng.uniform(40.0, size - 40.0))
            angle = rng.uniform(0, 2 * np.pi)
            ix2 = ix1 + d_pix * np.cos(angle)
            iy2 = iy1 + d_pix * np.sin(angle)

            # Injected patches
            p_rad = 10
            # Epoch 1: +flux at (ix1, iy1)
            f1_mod = patch1_flux.copy()
            v1_mod = patch1_var.copy()
            yy1, xx1 = np.mgrid[int(iy1)-p_rad:int(iy1)+p_rad+1, int(ix1)-p_rad:int(ix1)+p_rad+1]
            k1 = np.exp(-0.5 * ((xx1 - ix1)**2 + (yy1 - iy1)**2) / (0.85**2))
            k1 /= np.sum(k1)
            f1_mod[int(iy1)-p_rad:int(iy1)+p_rad+1, int(ix1)-p_rad:int(ix1)+p_rad+1] += (mover_flux * k1).astype(np.float32)

            # Epoch 2: +flux at (ix2, iy2)
            f2_mod = patch2_flux.copy()
            v2_mod = patch2_var.copy()
            yy2, xx2 = np.mgrid[int(iy2)-p_rad:int(iy2)+p_rad+1, int(ix2)-p_rad:int(ix2)+p_rad+1]
            k2 = np.exp(-0.5 * ((xx2 - ix2)**2 + (yy2 - iy2)**2) / (0.85**2))
            k2 /= np.sum(k2)
            f2_mod[int(iy2)-p_rad:int(iy2)+p_rad+1, int(ix2)-p_rad:int(ix2)+p_rad+1] += (mover_flux * k2).astype(np.float32)

            # ZOGY
            diff_m, sc_m, _ = zogy_subtraction(f2_mod, v2_mod, psf_template, f1_mod, v1_mod, psf_template)
            pos_cands, _ = detect_and_veto_candidates(diff_m, sc_m, snr_threshold=4.5, edge_margin_pix=6)
            neg_wells = detect_negative_wells(diff_m, sc_m, snr_threshold=4.5, edge_margin_pix=6)

            # Check positive lobe at (ix2, iy2)
            pos_found = any(np.hypot(c.x_pix - ix2, c.y_pix - iy2) < 2.5 for c in pos_cands)
            # Check negative well at (ix1, iy1)
            neg_found = any(np.hypot(w[0] - ix1, w[1] - iy1) < 2.5 for w in neg_wells)

            if pos_found:
                n_pos_rec += 1
            if neg_found:
                n_neg_rec += 1

            # Run tracklet linking
            tracklets = link_dipole_tracklets(
                positive_candidates=pos_cands,
                negative_wells=neg_wells,
                dt_hours=128.9 / 3600.0,
                pixel_scale_arcsec=6.155,
                max_rate_arcsec_hr=2000.0,
                min_separation_pix=1.2
            )
            # Check if injected pair was linked
            is_linked = False
            for t in tracklets:
                if np.hypot(t.x2_pix - ix2, t.y2_pix - iy2) < 3.0 and np.hypot(t.x1_pix - ix1, t.y1_pix - iy1) < 3.0:
                    is_linked = True
                    break
            if is_linked:
                n_linked += 1

        p_rate = n_pos_rec / n_mover_trials
        n_rate = n_neg_rec / n_mover_trials
        l_rate = n_linked / n_mover_trials
        dipole_results.append({
            "sep_fwhm": d_fwhm,
            "sep_pix": d_pix,
            "pos_recovery": p_rate,
            "neg_recovery": n_rate,
            "linking_success": l_rate
        })
        print(f"Separation {d_fwhm:.1f} FWHM ({d_pix:.1f} pix): Pos Lobe = {p_rate*100:.1f}%, Neg Well = {n_rate*100:.1f}%, Tracklet Linked = {l_rate*100:.1f}%")

    print("✅ Completed injection suite rerun.")
    return dipole_results


if __name__ == "__main__":
    run_injection_suite()
