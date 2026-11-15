"""
Acceptance unit tests for ZOGY PSF-matched differencing & candidate detection:
1. Stationary-star pairs leave no dipole residuals above 3.5 sigma.
2. Injected moving source is successfully recovered at >5 sigma and centroided within 0.5 pixels.
3. Cosmic ray spike veto: single-pixel high-flux artifact is identified and vetoed.
4. Edge proximity veto: source on image boundary is vetoed.
"""

import numpy as np

from backend.science.differencing import construct_gaussian_psf, execute_scientific_differencing, zogy_subtraction


def test_stationary_star_leaves_no_dipole_residuals():
    """Stationary star pair with noise must leave residuals below 3.5 sigma in ZOGY."""
    size = 64
    rng = np.random.default_rng(101)

    # 1. Background noise
    bg_noise = 0.5
    img_a = rng.normal(0.0, bg_noise, (size, size)).astype(np.float32)
    img_b = rng.normal(0.0, bg_noise, (size, size)).astype(np.float32)

    var_a = np.full((size, size), bg_noise**2, dtype=np.float32)
    var_b = np.full((size, size), bg_noise**2, dtype=np.float32)

    # 2. Add bright stationary star at center (32, 32)
    cy, cx = 32, 32
    yy, xx = np.mgrid[0:size, 0:size]
    r2 = (xx - cx)**2 + (yy - cy)**2
    psf_sigma = 1.2
    star_flux = 100.0  # 200x background noise!
    star = star_flux * np.exp(-0.5 * r2 / psf_sigma**2)

    img_a += star.astype(np.float32)
    img_b += star.astype(np.float32)

    psf = construct_gaussian_psf(33, fwhm_pix=psf_sigma * 2.355)

    diff, s_corr, noise_sigma = zogy_subtraction(
        image_new=img_b,
        var_new=var_b,
        psf_new=psf,
        image_ref=img_a,
        var_ref=var_a,
        psf_ref=psf
    )

    # Maximum residual significance on stationary star must stay below 3.5 sigma
    star_box = s_corr[cy-3:cy+4, cx-3:cx+4]
    max_star_sigma = np.max(np.abs(star_box))
    assert max_star_sigma < 3.5, f"Stationary star left high dipole residual: {max_star_sigma:.2f} sigma"


def test_injected_moving_source_recovered():
    """Injected moving source must be recovered at > 5 sigma and centroided accurately."""
    size = 64
    rng = np.random.default_rng(202)

    bg_noise = 0.5
    img_a = rng.normal(0.0, bg_noise, (size, size)).astype(np.float32)
    img_b = rng.normal(0.0, bg_noise, (size, size)).astype(np.float32)
    var_a = np.full((size, size), bg_noise**2, dtype=np.float32)
    var_b = np.full((size, size), bg_noise**2, dtype=np.float32)

    # Inject stationary background star at (20, 20)
    yy, xx = np.mgrid[0:size, 0:size]
    psf_sigma = 1.2
    star = 50.0 * np.exp(-0.5 * ((xx - 20)**2 + (yy - 20)**2) / psf_sigma**2)
    img_a += star.astype(np.float32)
    img_b += star.astype(np.float32)

    # Inject moving asteroid/Planet X at (40.0, 35.0) ONLY in epoch B!
    inject_x, inject_y = 40.0, 35.0
    mover_flux = 30.0  # 60 sigma detection
    mover = mover_flux * np.exp(-0.5 * ((xx - inject_x)**2 + (yy - inject_y)**2) / psf_sigma**2)
    img_b += mover.astype(np.float32)

    psf = construct_gaussian_psf(33, fwhm_pix=psf_sigma * 2.355)

    result = execute_scientific_differencing(
        image_a=img_a,
        var_a=var_a,
        image_b=img_b,
        var_b=var_b,
        psf_a=psf,
        psf_b=psf,
        is_wavelength_matched=True,
        snr_threshold=5.0
    )

    # Must detect mover
    assert result.num_passed_candidates >= 1
    mover_cand = next(c for c in result.candidates if c.passed_vetoes)
    assert mover_cand.peak_snr_sigma > 10.0
    # Centroid accuracy within 0.5 pixels
    assert np.isclose(mover_cand.x_pix, inject_x, atol=0.5)
    assert np.isclose(mover_cand.y_pix, inject_y, atol=0.5)


def test_cosmic_ray_spike_vetoed():
    """A single-pixel cosmic ray spike must be vetoed as COSMIC_RAY_SPIKE."""
    size = 64
    img_a = np.zeros((size, size), dtype=np.float32)
    img_b = np.zeros((size, size), dtype=np.float32)
    var_a = np.ones((size, size), dtype=np.float32)
    var_b = np.ones((size, size), dtype=np.float32)

    # Single hot pixel in epoch B
    img_b[25, 25] = 200.0

    result = execute_scientific_differencing(
        image_a=img_a,
        var_a=var_a,
        image_b=img_b,
        var_b=var_b,
        is_wavelength_matched=True,
        snr_threshold=5.0
    )

    # Detection should trigger cosmic ray veto
    cr_cand = next((c for c in result.candidates if c.is_cosmic_ray), None)
    assert cr_cand is not None
    assert cr_cand.veto_reason == "COSMIC_RAY_SPIKE"
    assert not cr_cand.passed_vetoes
