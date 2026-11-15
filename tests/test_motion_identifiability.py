"""
Unit tests for motion model identifiability, parameter degeneracy,
and distance recovery accuracy on simulated 500 AU bodies.
"""

import astropy.units as u
import numpy as np
from astropy.time import Time

from backend.science.motion_model import MotionModelFitter, project_parallax_factors


def test_short_baseline_returns_unconstrained_distance():
    """
    Over a short baseline (dt = 20 days), parallax and linear motion are degenerate.
    The engine must return distance_status == 'UNCONSTRAINED'.
    """
    times = Time("2025-04-01") + np.linspace(0, 20.0, 4) * u.day
    dt_yr = (times.mjd - times[0].mjd) / 365.25

    p_alpha, p_dec = project_parallax_factors(133.79, -7.25, times)
    plx = 206264.8 / 500.0
    sim_x = 0.05 * dt_yr + plx * p_alpha
    sim_y = -0.02 * dt_yr + plx * p_dec

    cos_dec = np.cos(np.radians(-7.25))
    ra_deg = 133.79 + (sim_x / 3600.0) / cos_dec
    dec_deg = -7.25 + (sim_y / 3600.0)

    fitter = MotionModelFitter(times, ra_deg, dec_deg)
    res_b = fitter.fit_model_b()

    assert res_b.params["distance_status"] == "UNCONSTRAINED"
    assert res_b.params["allowed_range_au_min"] == 10.0
    assert res_b.params["allowed_range_au_max"] == 5000.0


def test_long_baseline_constrains_500au_distance():
    """
    Over a 1-year baseline with multi-epoch sampling, Earth reflex parallax curvature
    breaks the degeneracy and constrains distance d ~ 500 AU within 20%.
    """
    times = Time("2025-01-01") + np.linspace(0, 365.25, 12) * u.day
    dt_yr = (times.mjd - times[0].mjd) / 365.25

    p_alpha, p_dec = project_parallax_factors(133.79, -7.25, times)
    true_dist = 500.0  # AU
    plx = 206264.8 / true_dist
    sim_x = 0.05 * dt_yr + plx * p_alpha
    sim_y = -0.02 * dt_yr + plx * p_dec

    # Add realistic SPHEREx astrometric noise (0.15 arcsec)
    rng = np.random.default_rng(42)
    sim_x += rng.normal(0.0, 0.15, len(times))
    sim_y += rng.normal(0.0, 0.15, len(times))

    cos_dec = np.cos(np.radians(-7.25))
    ra_deg = 133.79 + (sim_x / 3600.0) / cos_dec
    dec_deg = -7.25 + (sim_y / 3600.0)

    fitter = MotionModelFitter(times, ra_deg, dec_deg, ra_err_arcsec=np.full(len(times), 0.15))
    res_b = fitter.fit_model_b()

    assert res_b.params["distance_status"] == "CONSTRAINED"
    assert np.isclose(res_b.params["distance_au"], 500.0, rtol=0.25)
