"""
Benchmark Astrometry using 2D EPSF fitting vs Center-of-Mass on real SPHEREx data.
Checks dependence on detector radius and wavelength across the LVF.
"""

import astropy.units as u
import numpy as np
import pyvo as vo
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS
from scipy.optimize import minimize

with fits.open("data_samples/spherex_level2_sample.fits") as h:
    img = h["IMAGE"].data.astype(np.float64)
    wcs = WCS(h["IMAGE"].header)
    mjd = h["IMAGE"].header["MJD-OBS"]
    obs_time = Time(mjd, format="mjd")

with fits.open("data_samples/spectral_wcs_sample.fits") as h_swcs:
    cwave_map = h_swcs["CWAVE"].data.astype(np.float64)

center_coord = wcs.pixel_to_world(1020, 1020)
tap = vo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")
q = f"""
SELECT TOP 50 source_id, ra, dec, pmra, pmdec, phot_g_mean_mag
FROM gaia_dr3_source
WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {center_coord.ra.deg}, {center_coord.dec.deg}, 0.3))
  AND phot_g_mean_mag BETWEEN 11.0 AND 14.0
  AND pmra IS NOT NULL AND pmdec IS NOT NULL
ORDER BY phot_g_mean_mag ASC
"""
res = tap.search(q).to_table()

# 2D Gaussian EPSF model function (FWHM = 2.0 pix, sigma = 0.8493)
sig_epsf = 2.0 / 2.35482

def fit_epsf_centroid(patch: np.ndarray) -> tuple[float, float]:
    """Fits 2D Gaussian EPSF model (flux, x0, y0, background) by minimizing least squares."""
    h_p, w_p = patch.shape
    cy, cx = h_p / 2.0, w_p / 2.0
    yy, xx = np.mgrid[0:h_p, 0:w_p]

    # Initial guess
    bg0 = np.percentile(patch, 15)
    amp0 = max(0.1, np.max(patch) - bg0)

    def loss(p):
        amp, x0, y0, bg = p
        r2 = (xx - x0)**2 + (yy - y0)**2
        model = bg + amp * np.exp(-0.5 * r2 / (sig_epsf**2))
        return np.sum((patch - model)**2)

    res_fit = minimize(loss, [amp0, cx, cy, bg0], bounds=[(0, None), (1, w_p-2), (1, h_p-2), (None, None)], method="L-BFGS-B")
    return float(res_fit.x[1]), float(res_fit.x[2])

com_diffs = []
epsf_diffs = []
det_radii = []
wavelengths = []

for star in res:
    sc = SkyCoord(
        ra=float(star["ra"]) * u.deg,
        dec=float(star["dec"]) * u.deg,
        pm_ra_cosdec=float(star["pmra"]) * u.mas / u.yr,
        pm_dec=float(star["pmdec"]) * u.mas / u.yr,
        obstime=Time("2016-01-01T00:00:00", scale="tcb")
    )
    sc_prop = sc.apply_space_motion(new_obstime=obs_time)
    x_exp, y_exp = wcs.world_to_pixel(sc_prop)
    x_exp, y_exp = float(x_exp), float(y_exp)

    if 60 < x_exp < 1980 and 60 < y_exp < 1980:
        ix, iy = int(round(x_exp)), int(round(y_exp))
        patch = img[iy - 5:iy + 6, ix - 5:ix + 6]
        if np.all(np.isfinite(patch)) and np.max(patch) > 0.3:
            # 1. Center of mass
            denom = float(np.sum(patch))
            if denom > 0:
                x_com = ix - 5 + float(np.sum(patch * np.arange(11)[None, :])) / denom
                y_com = iy - 5 + float(np.sum(patch * np.arange(11)[:, None])) / denom
                coord_com = wcs.pixel_to_world(x_com, y_com)
                dtot_com = coord_com.separation(sc_prop).arcsec

                # 2. EPSF model fit
                dx_epsf, dy_epsf = fit_epsf_centroid(patch)
                x_fit = ix - 5 + dx_epsf
                y_fit = iy - 5 + dy_epsf
                coord_epsf = wcs.pixel_to_world(x_fit, y_fit)
                dtot_epsf = coord_epsf.separation(sc_prop).arcsec

                if dtot_epsf < 5.0:
                    com_diffs.append(dtot_com)
                    epsf_diffs.append(dtot_epsf)
                    r_det = np.hypot(x_fit - 1020, y_fit - 1020)
                    det_radii.append(r_det)
                    cwave = cwave_map[int(round(y_fit)), int(round(x_fit))]
                    wavelengths.append(cwave)

print("="*60)
print(f"Sample: N = {len(epsf_diffs)} isolated Gaia DR3 stars (G=11-14 mag)")
print(f"Center-of-Mass: Median = {np.median(com_diffs):.3f}\", RMS = {np.sqrt(np.mean(np.array(com_diffs)**2)):.3f}\"")
print(f"2D EPSF Fitting: Median = {np.median(epsf_diffs):.3f}\", RMS = {np.sqrt(np.mean(np.array(epsf_diffs)**2)):.3f}\" ({np.sqrt(np.mean(np.array(epsf_diffs)**2))/6.155:.3f} pix)")

# Dependence on detector radius
corr_radius = np.corrcoef(det_radii, epsf_diffs)[0, 1]
print(f"Correlation with Detector Radius (FOV dist): r = {corr_radius:.3f}")

# Dependence on wavelength
corr_wave = np.corrcoef(wavelengths, epsf_diffs)[0, 1]
print(f"Correlation with Wavelength (LVF gradient): r = {corr_wave:.3f}")
print("="*60)

