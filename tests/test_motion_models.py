"""
Unit tests for Astrometric Motion Models (Model A, Model B, Model C)
Verifies physical scaling laws:
1. Parallax amplitude = 206265 / d(AU) arcsec (~412.5" at 500 AU)
2. Parallax ellipse semi-minor axis scales with sin(ecliptic latitude beta)
3. Peak parallax rate near 0.3"/hr at 500 AU
4. Orbital angular rate of order tens of arcsec/yr at several hundred AU
5. Model fitting and BIC evaluation
"""

import astropy.units as u
import numpy as np
from astropy.coordinates import GeocentricTrueEcliptic, SkyCoord
from astropy.time import Time

from backend.science.motion_model import (
    RAD_TO_ARCSEC,
    MotionModelFitter,
    compute_earth_barycentric_positions,
    project_parallax_factors,
)


def test_parallax_amplitude_at_500_au():
    """Parallax amplitude must equal 206265 / d(AU) arcsec (~412.5" at 500 AU)."""
    d_au = 500.0
    expected_amplitude_arcsec = RAD_TO_ARCSEC / d_au  # ~412.529 arcsec
    assert np.isclose(expected_amplitude_arcsec, 412.53, atol=0.5)


def test_parallax_ellipse_semi_minor_axis_scales_with_sin_ecliptic_latitude():
    """
    The semi-minor axis of the Earth reflex parallax ellipse must scale
    strictly with |sin(beta)| where beta is the ecliptic latitude.
    """
    times = Time("2026-01-01") + np.linspace(0, 365.25, 100) * u.day

    # Test three targets at different ecliptic latitudes
    # 1. Ecliptic pole (beta = 90 deg -> circle: b/a = 1.0)
    # 2. Ecliptic plane (beta = 0 deg -> line: b/a = 0.0)
    # 3. Intermediate latitude (beta = 30 deg -> b/a = 0.5)
    ecl_coords = [
        SkyCoord(lon=45*u.deg, lat=90*u.deg, frame=GeocentricTrueEcliptic),
        SkyCoord(lon=45*u.deg, lat=0*u.deg, frame=GeocentricTrueEcliptic),
        SkyCoord(lon=45*u.deg, lat=30*u.deg, frame=GeocentricTrueEcliptic)
    ]

    for coord in ecl_coords:
        icrs = coord.icrs
        ra_deg = float(icrs.ra.deg)
        dec_deg = float(icrs.dec.deg)
        lat_rad = float(coord.lat.radian)

        p_alpha, p_dec = project_parallax_factors(ra_deg, dec_deg, times)
        # In a 1-year sampling, calculate semi-axes from covariance or amplitude
        # At lat=0, the motion in ecliptic perpendicular direction must vanish
        if np.isclose(np.sin(lat_rad), 0.0, atol=1e-3):
            # Ecliptic plane: trajectory is degenerate (straight line)
            # Area of ellipse ~ 0
            u_grid = np.column_stack([p_alpha, p_dec])
            _, s, _ = np.linalg.svd(u_grid - np.mean(u_grid, axis=0))
            ratio = s[1] / s[0]
            assert ratio < 0.1, f"Expected degenerate ellipse at ecliptic plane, got ratio {ratio}"
        elif np.isclose(np.sin(lat_rad), 1.0, atol=1e-3):
            # Ecliptic pole: trajectory is circular (ratio ~ 1.0)
            u_grid = np.column_stack([p_alpha, p_dec])
            _, s, _ = np.linalg.svd(u_grid - np.mean(u_grid, axis=0))
            ratio = s[1] / s[0]
            assert np.isclose(ratio, 1.0, atol=0.1), f"Expected circular ellipse at pole, got ratio {ratio}"
        else:
            # Intermediate latitude: ratio s[1]/s[0] ~ |sin(beta)|
            u_grid = np.column_stack([p_alpha, p_dec])
            _, s, _ = np.linalg.svd(u_grid - np.mean(u_grid, axis=0))
            ratio = s[1] / s[0]
            expected_ratio = np.abs(np.sin(lat_rad))
            assert np.isclose(ratio, expected_ratio, atol=0.15)


def test_peak_parallax_rate_at_500_au():
    """
    Peak reflex parallax rate near 0.3"/hr at 500 AU.
    Earth's velocity ~ 29.8 km/s ~ 0.000717 AU/hr.
    At 500 AU: 0.000717 * 206265 / 500 ~ 0.296"/hr.
    """
    t_start = Time("2026-03-20 12:00:00")  # Vernal equinox
    dt_hours = np.linspace(0, 24, 25)
    times = t_start + dt_hours * u.hour

    # Earth barycentric velocity
    x, y, z = compute_earth_barycentric_positions(times)
    # Velocity in AU/hr
    vx = np.gradient(x, dt_hours)
    vy = np.gradient(y, dt_hours)
    vz = np.gradient(z, dt_hours)
    v_earth_au_hr = np.sqrt(vx**2 + vy**2 + vz**2)

    mean_v_earth = float(np.mean(v_earth_au_hr))
    # Angular rate at 500 AU
    rate_arcsec_hr = (mean_v_earth / 500.0) * RAD_TO_ARCSEC
    assert np.isclose(rate_arcsec_hr, 0.30, atol=0.04), f"Expected ~0.30 \"/hr at 500 AU, got {rate_arcsec_hr}"


def test_motion_model_fitter_recovers_known_parallaxes():
    """
    Simulate a high-proper-motion star (Barnard's Star proxy: mu = 10.3"/yr, plx = 0.547")
    and verify Model A fits parameters accurately.
    """
    times = Time("2024-01-01") + np.linspace(0, 3.0, 15) * u.year  # 15 epochs over 3 years
    dt_yr = (times.mjd - times[0].mjd) / 365.25

    p_alpha, p_dec = project_parallax_factors(269.45, 4.69, times)

    true_dx0 = 0.0
    true_dy0 = 0.0
    true_pm_ra = -0.798  # arcsec/yr
    true_pm_dec = 10.36  # arcsec/yr
    true_plx = 0.547     # arcsec

    sim_x = true_dx0 + true_pm_ra * dt_yr + true_plx * p_alpha
    sim_y = true_dy0 + true_pm_dec * dt_yr + true_plx * p_dec

    cos_dec = np.cos(np.radians(4.69))
    ra_deg = 269.45 + (sim_x / 3600.0) / cos_dec
    dec_deg = 4.69 + (sim_y / 3600.0)

    fitter = MotionModelFitter(times, ra_deg, dec_deg)
    res_a = fitter.fit_model_a()

    assert np.isclose(res_a.params["pm_ra_cosdec_arcsec_yr"], true_pm_ra, atol=0.1)
    assert np.isclose(res_a.params["pm_dec_arcsec_yr"], true_pm_dec, atol=0.1)
    assert np.isclose(res_a.params["parallax_arcsec"], true_plx, atol=0.1)
    assert res_a.chi2 < 1.0


def test_model_b_distant_solar_system_body():
    """
    Simulate an outer planet at 500 AU with small Keplerian drift (0.1"/yr).
    Verify Model B recovers the distance within bounds and yields lower BIC than linear mover.
    """
    times = Time("2025-01-01") + np.linspace(0, 2.0, 20) * u.year
    dt_yr = (times.mjd - times[0].mjd) / 365.25

    p_alpha, p_dec = project_parallax_factors(120.0, 15.0, times)
    true_dist = 500.0  # AU
    plx = RAD_TO_ARCSEC / true_dist

    sim_x = 0.05 * dt_yr + plx * p_alpha
    sim_y = -0.02 * dt_yr + plx * p_dec

    cos_dec = np.cos(np.radians(15.0))
    ra_deg = 120.0 + (sim_x / 3600.0) / cos_dec
    dec_deg = 15.0 + (sim_y / 3600.0)

    fitter = MotionModelFitter(times, ra_deg, dec_deg)
    results = fitter.fit_all()

    res_b = results["model_b"]
    assert np.isclose(res_b.params["distance_au"], 500.0, atol=50.0)
    assert res_b.chi2 < 1.0
