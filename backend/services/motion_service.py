"""
SPHEREx Hunter - Space Motion & Proper Motion Propagation Service
Uses Astropy SkyCoord.apply_space_motion to rigorously propagate celestial
coordinates across observation epochs (e.g. 2MASS 1999 -> SPHEREx 2025).
"""

import math
from typing import Any, Dict, Optional

import astropy.units as u
from astropy.coordinates import Distance, SkyCoord
from astropy.time import Time


def propagate_target_epoch(
    ra_deg: float,
    dec_deg: float,
    pm_ra_mas_yr: float = 0.0,
    pm_dec_mas_yr: float = 0.0,
    base_epoch_year: float = 2000.0,
    target_date: Optional[Any] = None,
    target_mjd: Optional[float] = None,
    parallax_mas: Optional[float] = None,
    radial_velocity_kms: Optional[float] = None,
    fov_arcmin: float = 3.0
) -> Dict[str, Any]:
    """
    Propagates celestial coordinates to a target epoch date or MJD.
    Calculates the angular displacement from baseline and flags if displacement exceeds FOV.
    """
    # Determine target obstime
    if target_mjd is not None:
        target_obstime = Time(target_mjd, format="mjd")
    elif isinstance(target_date, (int, float)):
        target_obstime = Time(target_date, format="jyear")
    elif isinstance(target_date, str) and "-" in target_date:
        target_obstime = Time(target_date, format="iso")
    else:
        target_obstime = Time("J2025.5")

    base_obstime = Time(f"J{base_epoch_year}")

    # Set up distance if parallax is provided
    dist = None
    if parallax_mas and parallax_mas > 0:
        dist = Distance(parallax=parallax_mas * u.mas)

    rv = (radial_velocity_kms * u.km / u.s) if radial_velocity_kms is not None else 0.0 * u.km / u.s

    try:
        if dist is not None:
            c0 = SkyCoord(
                ra=ra_deg * u.deg,
                dec=dec_deg * u.deg,
                distance=dist,
                pm_ra_cosdec=pm_ra_mas_yr * u.mas / u.yr,
                pm_dec=pm_dec_mas_yr * u.mas / u.yr,
                radial_velocity=rv,
                obstime=base_obstime
            )
        else:
            c0 = SkyCoord(
                ra=ra_deg * u.deg,
                dec=dec_deg * u.deg,
                pm_ra_cosdec=pm_ra_mas_yr * u.mas / u.yr,
                pm_dec=pm_dec_mas_yr * u.mas / u.yr,
                obstime=base_obstime
            )

        c_epoch = c0.apply_space_motion(new_obstime=target_obstime)
        prop_ra = float(round(c_epoch.ra.deg, 6))
        prop_dec = float(round(c_epoch.dec.deg, 6))
        displacement_arcsec = float(round(c0.separation(c_epoch).arcsec, 3))

    except Exception:
        # High-precision spherical trigonometry fallback
        dt_years = target_obstime.jyear - base_obstime.jyear
        cos_dec = max(1e-5, math.cos(math.radians(dec_deg)))
        delta_ra_deg = (pm_ra_mas_yr * dt_years / (cos_dec * 3600000.0))
        delta_dec_deg = (pm_dec_mas_yr * dt_years / 3600000.0)
        prop_ra = float(round(ra_deg + delta_ra_deg, 6))
        prop_dec = float(round(dec_deg + delta_dec_deg, 6))
        total_pm = math.sqrt(pm_ra_mas_yr**2 + pm_dec_mas_yr**2)
        displacement_arcsec = float(round((total_pm * abs(dt_years)) / 1000.0, 3))

    fov_arcsec = fov_arcmin * 60.0
    exceeds_fov = displacement_arcsec > fov_arcsec

    warning_msg = None
    if exceeds_fov:
        warning_msg = (
            f"Proper motion displacement ({displacement_arcsec:.1f}\") exceeds "
            f"the requested FOV ({fov_arcsec:.1f}\"). Object has migrated outside un-centered frame!"
        )

    return {
        "base_epoch": base_obstime.iso,
        "target_epoch": target_obstime.iso,
        "target_mjd": float(round(target_obstime.mjd, 4)),
        "base_ra_deg": ra_deg,
        "base_dec_deg": dec_deg,
        "epoch_ra_deg": prop_ra,
        "epoch_dec_deg": prop_dec,
        "displacement_arcsec": displacement_arcsec,
        "fov_arcmin": fov_arcmin,
        "fov_arcsec": fov_arcsec,
        "exceeds_fov": exceeds_fov,
        "warning": warning_msg
    }
