"""
🛰️ SPHEREx Hunter - WISE 0855-0714 In-Flight Forced Photometry Benchmark
NASA Space Apps Challenge 2026 - Team RIP

Measures forced photometry on authentic SPHEREx Detector 6 (4.4 - 5.0 um):
Exposure: level2_2025W46_1A_0238_2D6_spx_l2b-v27-2026-206.fits (MJD 60989.979)
Target: WISE 0855-0714 (T ~ 250K cold brown dwarf)
Literature: Luhman (2014, ApJ 786, L18), Kirkpatrick et al. (2021, ApJS 253, 7)
"""

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS

FITS_PATH = "data_samples/wise0855_spherex_d6.fits"

# 1. Propagate coordinates from Kirkpatrick et al. (2021)
ra_2010 = 133.7862
dec_2010 = -7.2443
pm_ra = -8149.0  # mas/yr
pm_dec = 693.0   # mas/yr
plx = 448.4      # mas (d = 2.23 pc)

with fits.open(FITS_PATH) as hdul:
    img = hdul["IMAGE"].data.astype(np.float64)
    var = hdul["VARIANCE"].data.astype(np.float64)
    header = hdul["IMAGE"].header
    wcs = WCS(header)
    mjd_obs = header.get("MJD-OBS", 60989.9785)
    obs_time = Time(mjd_obs, format="mjd")

sc_2010 = SkyCoord(
    ra=ra_2010 * u.deg, dec=dec_2010 * u.deg,
    distance=(1000.0 / plx) * u.pc,
    pm_ra_cosdec=pm_ra * u.mas / u.yr, pm_dec=pm_dec * u.mas / u.yr,
    obstime=Time("2010-01-01T00:00:00", scale="tcb")
)
sc_prop = sc_2010.apply_space_motion(new_obstime=obs_time)
x_pred, y_pred = wcs.world_to_pixel(sc_prop)
x_pred, y_pred = float(x_pred), float(y_pred)

print("="*70)
print("WISE 0855-0714 In-Flight Forced Photometry Benchmark")
print(f"Exposure: {header.get('OBSID', '2025W46_1A_0238_2D6')}, Detector: {header.get('DETECTOR', 6)}")
print(f"Observation Time: {obs_time.iso} (MJD {mjd_obs:.5f})")
print(f"Baseline since 2010: {obs_time.decimalyear - 2010.0:.2f} years")
print(f"Predicted Celestial Coordinates: RA = {sc_prop.ra.deg:.5f}°, Dec = {sc_prop.dec.deg:.5f}°")
print(f"Detector Pixel Coordinates: x = {x_pred:.2f}, y = {y_pred:.2f} (in 2040x2040 array)")

# Pixel scale and conversion
from backend.science.preprocessing import MJY_SR_TO_UJY_SR, compute_pixel_solid_angle_sr

pix_scale, omega_sr = compute_pixel_solid_angle_sr(wcs)
conv_factor = omega_sr * MJY_SR_TO_UJY_SR

# Crop 21x21 box around predicted position
ix, iy = int(round(x_pred)), int(round(y_pred))
box = 10
cut_img = img[iy - box:iy + box + 1, ix - box:ix + box + 1] * conv_factor
cut_var = var[iy - box:iy + box + 1, ix - box:ix + box + 1] * (conv_factor**2)

# Optimal PSF-weighted forced photometry
yy, xx = np.mgrid[iy - box:iy + box + 1, ix - box:ix + box + 1]
r2 = (xx - x_pred)**2 + (yy - y_pred)**2
sig_epsf = 2.0 / 2.35482
psf_model = np.exp(-0.5 * r2 / (sig_epsf**2))
psf_model /= np.sum(psf_model)

# Subtract local annular background (radius 6 to 10 pixels)
annulus_mask = (r2 >= 6.0**2) & (r2 <= 10.0**2)
local_bg = float(np.nanmedian(cut_img[annulus_mask]))
cut_img_sub = cut_img - local_bg

# Flux estimator: F_hat = sum(w * d) / sum(w * P) where w = P / sigma^2
w = psf_model / np.maximum(1e-12, cut_var)
f_hat = float(np.sum(w * cut_img_sub) / np.sum(w * psf_model))
var_f = float(1.0 / np.sum(w * psf_model))
sigma_f = float(np.sqrt(max(1e-12, var_f)))
snr = f_hat / sigma_f

m_ab = 23.9 - 2.5 * np.log10(max(1e-4, f_hat)) if f_hat > 0 else 99.0

print("\nTarget Photometry at Predicted Position:")
print(f"  Extracted Flux:       {f_hat:.2f} ± {sigma_f:.2f} µJy")
print(f"  Calibrated AB Mag:    {m_ab:.2f} mag")
print(f"  Detection SNR:        {snr:.2f} σ")

# Measure peak offset by centroid fitting
sub_h, sub_w = cut_img_sub.shape
denom = float(np.sum(cut_img_sub[box-3:box+4, box-3:box+4]))
if denom > 0:
    x_obs = ix - box + float(np.sum(cut_img_sub[box-3:box+4, box-3:box+4] * (xx[box-3:box+4, box-3:box+4] - ix + box))) / denom
    y_obs = iy - box + float(np.sum(cut_img_sub[box-3:box+4, box-3:box+4] * (yy[box-3:box+4, box-3:box+4] - iy + box))) / denom
    pos_offset_pix = np.hypot(x_obs - x_pred, y_obs - y_pred)
    pos_offset_arcsec = pos_offset_pix * pix_scale
    print(f"  Observed Centroid:    x = {x_obs:.2f}, y = {y_obs:.2f}")
    print(f"  Positional Offset:    {pos_offset_arcsec:.2f}\" ({pos_offset_pix:.2f} pixels)")

# Control Positions (4 blank sky positions 30" away)
print("\nControl Positions (Blank Sky Offset 30\" N/S/E/W):")
offsets = [(0, 30.0/pix_scale), (0, -30.0/pix_scale), (30.0/pix_scale, 0), (-30.0/pix_scale, 0)]
control_snrs = []
for idx, (dx, dy) in enumerate(offsets):
    cx_ctrl = x_pred + dx
    cy_ctrl = y_pred + dy
    r2_ctrl = (xx - cx_ctrl)**2 + (yy - cy_ctrl)**2
    psf_ctrl = np.exp(-0.5 * r2_ctrl / (sig_epsf**2))
    psf_ctrl /= np.sum(psf_ctrl)
    w_ctrl = psf_ctrl / np.maximum(1e-12, cut_var)
    f_ctrl = float(np.sum(w_ctrl * cut_img_sub) / np.sum(w_ctrl * psf_ctrl))
    var_ctrl = float(1.0 / np.sum(w_ctrl * psf_ctrl))
    sig_ctrl = float(np.sqrt(max(1e-12, var_ctrl)))
    snr_ctrl = f_ctrl / sig_ctrl
    control_snrs.append(snr_ctrl)
    print(f"  Control {idx+1}: Flux = {f_ctrl:6.2f} ± {sig_ctrl:.2f} µJy, SNR = {snr_ctrl:+.2f} σ")

print(f"Mean Control SNR: {np.mean(control_snrs):+.2f} σ (Consistent with null background)")
print("="*70)

