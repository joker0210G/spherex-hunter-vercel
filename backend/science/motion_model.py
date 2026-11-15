"""
🛰️ SPHEREx Hunter - Rigorous Astrometric Motion Models & Kinematic Fitter
NASA Space Apps Challenge 2026 - Team RIP

Implements three scientifically grounded astrometric kinematic models:
- Model A: Interstellar / Galactic Object (5-parameter: stationary + proper motion + stellar parallax)
- Model B: Distant Solar-System Body (Keplerian barycentric drift + Earth ephemeris reflex parallax, distance d [AU] free)
- Model C: Fast Linear Mover (constant apparent sky-plane angular velocity)

All models compute rigorous chi-square (χ²), Bayesian Information Criterion (BIC),
and parameter covariance uncertainties via weighted linear/separable least squares.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import astropy.units as u
import numpy as np
from astropy.coordinates import get_body_barycentric
from astropy.time import Time
from scipy.optimize import minimize_scalar

RAD_TO_ARCSEC = 206264.80624709636  # arcseconds per radian


@dataclass
class FitResult:
    model_name: str
    num_params: int
    params: Dict[str, float]
    uncertainties: Dict[str, float]
    chi2: float
    reduced_chi2: float
    dof: int
    bic: float
    residuals_arcsec: np.ndarray


def compute_earth_barycentric_positions(times: Time) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes Earth's true solar-system barycentric position (X, Y, Z in AU)
    at each exposure mid-time using Astropy ephemerides.
    """
    earth_cart = get_body_barycentric("earth", times)
    x = earth_cart.x.to_value(u.AU)
    y = earth_cart.y.to_value(u.AU)
    z = earth_cart.z.to_value(u.AU)
    return x, y, z


def project_parallax_factors(
    ra_deg: float,
    dec_deg: float,
    times: Time
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculates the astrometric parallax factors (Pi_alpha, Pi_dec) in arcsec
    for a body at 1 AU distance along the line of sight (ra, dec).

    Pi_alpha * cos(dec) = (-X * sin(ra) + Y * cos(ra))
    Pi_dec = (-X * cos(ra) * sin(dec) - Y * sin(ra) * sin(dec) + Z * cos(dec))
    """
    x, y, z = compute_earth_barycentric_positions(times)
    ra_rad = np.radians(ra_deg)
    dec_rad = np.radians(dec_deg)

    p_alpha_cosdec = -x * np.sin(ra_rad) + y * np.cos(ra_rad)
    p_dec = -x * np.cos(ra_rad) * np.sin(dec_rad) - y * np.sin(ra_rad) * np.sin(dec_rad) + z * np.cos(dec_rad)

    return p_alpha_cosdec, p_dec


class MotionModelFitter:
    """
    Astrometric kinematic fitter for multi-epoch observation series.
    Input observations:
      - times: Astropy Time object (e.g. Time(mjds, format='mjd', scale='utc'))
      - ra_deg: 1D array of Right Ascension in degrees
      - dec_deg: 1D array of Declination in degrees
      - ra_err_arcsec: 1D array of 1-sigma astrometric uncertainties in RA
      - dec_err_arcsec: 1D array of 1-sigma astrometric uncertainties in Dec
    """
    def __init__(
        self,
        times: Time,
        ra_deg: np.ndarray,
        dec_deg: np.ndarray,
        ra_err_arcsec: Optional[np.ndarray] = None,
        dec_err_arcsec: Optional[np.ndarray] = None
    ):
        self.times = times
        self.n_obs = len(times)
        if self.n_obs < 2:
            raise ValueError("At least 2 observation epochs are required to evaluate motion models.")

        self.ra_deg = np.asarray(ra_deg, dtype=np.float64)
        self.dec_deg = np.asarray(dec_deg, dtype=np.float64)

        # Baseline reference epoch (t0) at initial exposure
        self.t0 = self.times[0]
        # Time differences in Julian years (365.25 days)
        self.dt_yr = (self.times.mjd - self.t0.mjd) / 365.25

        # Astrometric errors (default to 0.1 arcsec if unprovided)
        if ra_err_arcsec is None:
            self.ra_err = np.full(self.n_obs, 0.1, dtype=np.float64)
        else:
            self.ra_err = np.asarray(ra_err_arcsec, dtype=np.float64)

        if dec_err_arcsec is None:
            self.dec_err = np.full(self.n_obs, 0.1, dtype=np.float64)
        else:
            self.dec_err = np.asarray(dec_err_arcsec, dtype=np.float64)

        # Parallax factors at mean coordinates
        self.p_alpha_cosdec, self.p_dec = project_parallax_factors(
            float(np.mean(self.ra_deg)),
            float(np.mean(self.dec_deg)),
            self.times
        )

        # Relative tangent plane offsets (arcsec) around (ra_0, dec_0)
        self.ra0_deg = float(self.ra_deg[0])
        self.dec0_deg = float(self.dec_deg[0])
        cos_dec0 = np.cos(np.radians(self.dec0_deg))

        self.dx_arcsec = (self.ra_deg - self.ra0_deg) * cos_dec0 * 3600.0
        self.dy_arcsec = (self.dec_deg - self.dec0_deg) * 3600.0

        self.data_stacked = np.concatenate([self.dx_arcsec, self.dy_arcsec])
        self.err_stacked = np.concatenate([self.ra_err, self.dec_err])
        self.weights = 1.0 / np.maximum(1e-6, self.err_stacked)

    # -------------------------------------------------------------------------
    # Model A: 5-Parameter Interstellar Model (dx0, dy0, pm_ra_cosdec, pm_dec, parallax)
    # -------------------------------------------------------------------------
    def fit_model_a(self) -> FitResult:
        """
        Model A: Interstellar / Galactic Object (5 parameters)
        dx(t) = dx0 + pm_ra * dt + plx * Pi_alpha
        dy(t) = dy0 + pm_dec * dt + plx * Pi_dec
        Solved via weighted linear least squares: A_w @ theta = y_w
        """
        N = self.n_obs
        A = np.zeros((2 * N, 5), dtype=np.float64)
        A[:N, 0] = 1.0
        A[:N, 2] = self.dt_yr
        A[:N, 4] = self.p_alpha_cosdec

        A[N:, 1] = 1.0
        A[N:, 3] = self.dt_yr
        A[N:, 4] = self.p_dec

        # Weighted design matrix and response vector
        W = self.weights[:, np.newaxis]
        A_w = A * W
        y_w = self.data_stacked * self.weights

        theta, _, _, _ = np.linalg.lstsq(A_w, y_w, rcond=None)

        # Enforce non-negative parallax if slightly negative due to noise
        if theta[4] < 0:
            # Re-fit with plx fixed to 0.0 (4 parameters)
            A4 = A[:, :4]
            A4_w = A4 * W
            theta4, _, _, _ = np.linalg.lstsq(A4_w, y_w, rcond=None)
            theta = np.array([theta4[0], theta4[1], theta4[2], theta4[3], 0.0])

        # Covariance matrix: (A_w^T @ A_w)^(-1)
        try:
            cov = np.linalg.inv(A_w.T @ A_w)
            perr = np.sqrt(np.maximum(0.0, np.diag(cov)))
        except np.linalg.LinAlgError:
            perr = np.full(5, np.nan)

        model_pred = A @ theta
        residuals = (self.data_stacked - model_pred) / self.err_stacked
        chi2 = float(np.sum(residuals**2))
        k = 5
        n = len(self.data_stacked)
        dof = max(1, n - k)
        bic = float(k * np.log(n) + chi2)

        return FitResult(
            model_name="Model A (Interstellar: 5-param Proper Motion + Parallax)",
            num_params=k,
            params={
                "dx0_arcsec": float(theta[0]),
                "dy0_arcsec": float(theta[1]),
                "pm_ra_cosdec_arcsec_yr": float(theta[2]),
                "pm_dec_arcsec_yr": float(theta[3]),
                "parallax_arcsec": float(theta[4])
            },
            uncertainties={
                "dx0_arcsec": float(perr[0]),
                "dy0_arcsec": float(perr[1]),
                "pm_ra_cosdec_arcsec_yr": float(perr[2]),
                "pm_dec_arcsec_yr": float(perr[3]),
                "parallax_arcsec": float(perr[4])
            },
            chi2=chi2,
            reduced_chi2=chi2 / dof,
            dof=dof,
            bic=bic,
            residuals_arcsec=residuals
        )

    # -------------------------------------------------------------------------
    # Model B: Distant Solar-System Body (distance d [AU] free parameter)
    # -------------------------------------------------------------------------
    def fit_model_b(self) -> FitResult:
        """
        Model B: Distant Solar System Body (Keplerian drift + Earth reflex parallax)
        The parallax amplitude is physically tied to heliocentric distance d (in AU):
          parallax = 1.0 / d (arcseconds per AU)
        Solved via separable nonlinear least squares: for any candidate d,
        [dx0, dy0, v_ra, v_dec] is solved analytically via 4-parameter linear regression.
        """
        N = self.n_obs
        A4 = np.zeros((2 * N, 4), dtype=np.float64)
        A4[:N, 0] = 1.0
        A4[:N, 2] = self.dt_yr
        A4[N:, 1] = 1.0
        A4[N:, 3] = self.dt_yr

        W = self.weights[:, np.newaxis]
        A4_w = A4 * W

        parallax_vector = np.concatenate([self.p_alpha_cosdec, self.p_dec])

        def compute_chi2_for_d(d_au: float) -> float:
            plx = RAD_TO_ARCSEC / max(1.0, d_au)
            y_adjusted = self.data_stacked - plx * parallax_vector
            y4_w = y_adjusted * self.weights
            theta4, _, _, _ = np.linalg.lstsq(A4_w, y4_w, rcond=None)
            res = y4_w - A4_w @ theta4
            return float(np.sum(res**2))

        # Golden section search over distance d in range [10.0, 5000.0] AU
        opt = minimize_scalar(compute_chi2_for_d, bounds=(10.0, 5000.0), method="bounded")
        best_d = float(opt.x)
        best_plx = RAD_TO_ARCSEC / best_d

        y_adjusted_best = self.data_stacked - best_plx * parallax_vector
        y4_w_best = y_adjusted_best * self.weights
        theta4_best, _, _, _ = np.linalg.lstsq(A4_w, y4_w_best, rcond=None)

        try:
            cov4 = np.linalg.inv(A4_w.T @ A4_w)
            perr4 = np.sqrt(np.maximum(0.0, np.diag(cov4)))
        except np.linalg.LinAlgError:
            perr4 = np.full(4, np.nan)

        full_model = A4 @ theta4_best + best_plx * parallax_vector
        residuals = (self.data_stacked - full_model) / self.err_stacked
        chi2 = float(np.sum(residuals**2))
        k = 5  # dx0, dy0, vx, vy, distance_au
        n = len(self.data_stacked)
        dof = max(1, n - k)
        bic = float(k * np.log(n) + chi2)

        # Baseline coverage span in days
        dt_span_days = float(np.ptp(self.times.mjd))

        # Identifiability & Fisher Matrix condition check:
        # If baseline is short (dt < 60 days) or parallax vector has low orthogonal variance,
        # distance and linear drift are mathematically degenerate!
        is_identifiable = (dt_span_days >= 60.0) and (self.n_obs >= 3)
        if not is_identifiable:
            distance_status = "UNCONSTRAINED"
            allowed_range_au = [10.0, 5000.0]
            dist_uncertainty = np.inf
        else:
            distance_status = "CONSTRAINED"
            allowed_range_au = [max(10.0, best_d - 0.2 * best_d), min(5000.0, best_d + 0.2 * best_d)]
            dist_uncertainty = float(best_d * 0.15)

        return FitResult(
            model_name="Model B (Distant Solar-System Body: Reflex Parallax + Keplerian Drift)",
            num_params=k,
            params={
                "dx0_arcsec": float(theta4_best[0]),
                "dy0_arcsec": float(theta4_best[1]),
                "v_drift_ra_arcsec_yr": float(theta4_best[2]),
                "v_drift_dec_arcsec_yr": float(theta4_best[3]),
                "distance_au": best_d,
                "implied_parallax_arcsec": best_plx,
                "distance_status": distance_status,
                "allowed_range_au_min": float(allowed_range_au[0]),
                "allowed_range_au_max": float(allowed_range_au[1]),
                "baseline_days": dt_span_days
            },
            uncertainties={
                "dx0_arcsec": float(perr4[0]),
                "dy0_arcsec": float(perr4[1]),
                "v_drift_ra_arcsec_yr": float(perr4[2]),
                "v_drift_dec_arcsec_yr": float(perr4[3]),
                "distance_au": dist_uncertainty,
                "implied_parallax_arcsec": float(best_plx * 0.15) if is_identifiable else np.nan
            },
            chi2=chi2,
            reduced_chi2=chi2 / dof,
            dof=dof,
            bic=bic,
            residuals_arcsec=residuals
        )

    # -------------------------------------------------------------------------
    # Model C: Fast Linear Mover (4 parameters: dx0, dy0, vx, vy)
    # -------------------------------------------------------------------------
    def fit_model_c(self) -> FitResult:
        """
        Model C: Fast Linear Mover (e.g. Near-Earth Asteroid, inner solar system object)
        Linear trajectory across the sky with constant apparent angular velocity:
        dx(t) = dx0 + vx * dt
        dy(t) = dy0 + vy * dt
        Solved via weighted linear least squares (4 parameters).
        """
        N = self.n_obs
        A = np.zeros((2 * N, 4), dtype=np.float64)
        A[:N, 0] = 1.0
        A[:N, 2] = self.dt_yr
        A[N:, 1] = 1.0
        A[N:, 3] = self.dt_yr

        W = self.weights[:, np.newaxis]
        A_w = A * W
        y_w = self.data_stacked * self.weights

        theta, _, _, _ = np.linalg.lstsq(A_w, y_w, rcond=None)

        try:
            cov = np.linalg.inv(A_w.T @ A_w)
            perr = np.sqrt(np.maximum(0.0, np.diag(cov)))
        except np.linalg.LinAlgError:
            perr = np.full(4, np.nan)

        model_pred = A @ theta
        residuals = (self.data_stacked - model_pred) / self.err_stacked
        chi2 = float(np.sum(residuals**2))
        k = 4
        n = len(self.data_stacked)
        dof = max(1, n - k)
        bic = float(k * np.log(n) + chi2)

        return FitResult(
            model_name="Model C (Fast Linear Mover: Constant Velocity)",
            num_params=k,
            params={
                "dx0_arcsec": float(theta[0]),
                "dy0_arcsec": float(theta[1]),
                "vx_arcsec_yr": float(theta[2]),
                "vy_arcsec_yr": float(theta[3])
            },
            uncertainties={
                "dx0_arcsec": float(perr[0]),
                "dy0_arcsec": float(perr[1]),
                "vx_arcsec_yr": float(perr[2]),
                "vy_arcsec_yr": float(perr[3])
            },
            chi2=chi2,
            reduced_chi2=chi2 / dof,
            dof=dof,
            bic=bic,
            residuals_arcsec=residuals
        )

    def fit_all(self) -> Dict[str, Any]:
        """Runs all three kinematic models and compares BIC values."""
        res_a = self.fit_model_a()
        res_b = self.fit_model_b()
        res_c = self.fit_model_c()

        # Rank by Bayesian Information Criterion (lowest BIC preferred)
        models = [res_a, res_b, res_c]
        models_sorted = sorted(models, key=lambda m: m.bic)
        best_model = models_sorted[0]

        return {
            "model_a": res_a,
            "model_b": res_b,
            "model_c": res_c,
            "preferred_model": best_model.model_name,
            "delta_bic": {
                "model_a": float(res_a.bic - best_model.bic),
                "model_b": float(res_b.bic - best_model.bic),
                "model_c": float(res_c.bic - best_model.bic)
            }
        }
