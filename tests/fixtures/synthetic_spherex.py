"""
Synthetic SPHEREx Level-2 FITS Generator for CI/CD and Unit Testing
Creates lightweight (64x64) Multi-Extension FITS files conforming to the
official SPHEREx Level-2 format without requiring 65 MB download files.
"""

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS


def create_synthetic_spherex_fits(
    ra_center: float = 133.79513,
    dec_center: float = -7.24515,
    size: int = 64,
    mjd_obs: float = 60789.75076,
    wavelength_um: float = 2.45
) -> fits.HDUList:
    """
    Constructs a 7-HDU SPHEREx Level-2 synthetic FITS product:
    0: PRIMARY
    1: IMAGE (MJy/sr)
    2: FLAGS (int32 quality bitmask)
    3: VARIANCE (MJy2/sr2)
    4: ZODI (MJy/sr)
    5: EPSF (Empirical PSF table)
    6: WCS-WAVE (Tabular wavelength lookup)
    """
    # 1. Primary HDU
    primary_hdr = fits.Header()
    primary_hdr["TELESCOP"] = "SPHEREx"
    primary_hdr["INSTRUME"] = "SPHEREx"
    primary_hdr["OBSID"] = "SYNTH_SPHEREx_TEST"
    primary_hdr["TIMESYS"] = "UTC"
    primary_hdr["MJD-OBS"] = mjd_obs
    primary_hdr["MJD-AVG"] = mjd_obs + 0.00066
    primary_hdr["MJD-END"] = mjd_obs + 0.00133
    primary_hdu = fits.PrimaryHDU(header=primary_hdr)

    # WCS setup (6.2 arcsec / pixel = ~0.001722 deg/pix)
    pix_scale_deg = 6.2 / 3600.0
    w = WCS(naxis=2)
    w.wcs.crpix = [size / 2.0 + 0.5, size / 2.0 + 0.5]
    w.wcs.cdelt = [-pix_scale_deg, pix_scale_deg]
    w.wcs.crval = [ra_center, dec_center]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]

    image_hdr = w.to_header()
    image_hdr["EXTNAME"] = "IMAGE"
    image_hdr["BUNIT"] = "MJy / sr"
    image_hdr["CWAVE"] = wavelength_um
    image_hdr["CBAND"] = 3

    # Generate sky background (zodi + noise)
    rng = np.random.default_rng(42)
    zodi_bg = 15.0  # MJy/sr
    read_noise_std = 0.5
    image_data = rng.normal(loc=zodi_bg, scale=read_noise_std, size=(size, size)).astype(np.float32)

    # Inject a central point source
    cy, cx = size // 2, size // 2
    yy, xx = np.mgrid[0:size, 0:size]
    r2 = (xx - cx)**2 + (yy - cy)**2
    psf_sigma = 1.0
    flux_peak = 50.0  # MJy/sr
    image_data += (flux_peak * np.exp(-0.5 * r2 / psf_sigma**2)).astype(np.float32)

    image_hdu = fits.ImageHDU(data=image_data, header=image_hdr, name="IMAGE")

    # 2. FLAGS HDU
    flags_data = np.zeros((size, size), dtype=np.int32)
    # Inject bad pixels: transient at (5, 5), hot pixel at (10, 10), source at center
    flags_data[5, 5] = 1 << 0   # TRANSIENT (1)
    flags_data[10, 10] = 1 << 10  # HOT (1024)
    flags_data[cy-1:cy+2, cx-1:cx+2] |= (1 << 21)  # SOURCE (2097152)
    flags_data[2, 2] = 1 << 6   # NONFUNC (64)
    flags_data[3, 3] = 1 << 11  # COLD (2048)
    flags_data[4, 4] = 1 << 19  # OUTLIER (524288)

    flags_hdr = w.to_header()
    flags_hdr["EXTNAME"] = "FLAGS"
    flags_hdr["EXTTYPE"] = "MASK"
    flags_hdr["MSKN0000"] = "TRANSIENT"
    flags_hdr["MSKM0000"] = 1
    flags_hdr["MSKN0001"] = "OVERFLOW"
    flags_hdr["MSKM0001"] = 2
    flags_hdr["MSKN0006"] = "NONFUNC"
    flags_hdr["MSKM0006"] = 64
    flags_hdr["MSKN0010"] = "HOT"
    flags_hdr["MSKM0010"] = 1024
    flags_hdr["MSKN0011"] = "COLD"
    flags_hdr["MSKM0011"] = 2048
    flags_hdr["MSKN0019"] = "OUTLIER"
    flags_hdr["MSKM0019"] = 524288
    flags_hdr["MSKN0021"] = "SOURCE"
    flags_hdr["MSKM0021"] = 2097152

    flags_hdu = fits.CompImageHDU(data=flags_data, header=flags_hdr, name="FLAGS")

    # 3. VARIANCE HDU
    variance_data = np.full((size, size), fill_value=read_noise_std**2, dtype=np.float32)
    var_hdr = w.to_header()
    var_hdr["EXTNAME"] = "VARIANCE"
    var_hdr["BUNIT"] = "MJy2 / sr2"
    var_hdu = fits.ImageHDU(data=variance_data, header=var_hdr, name="VARIANCE")

    # 4. ZODI HDU
    zodi_data = np.full((size, size), fill_value=zodi_bg, dtype=np.float32)
    zodi_hdr = w.to_header()
    zodi_hdr["EXTNAME"] = "ZODI"
    zodi_hdr["BUNIT"] = "MJy / sr"
    zodi_hdu = fits.ImageHDU(data=zodi_data, header=zodi_hdr, name="ZODI")

    # 5. EPSF HDU (33x33 normalized PSF grid)
    psf_size = 33
    py, px = np.mgrid[-(psf_size//2):(psf_size//2)+1, -(psf_size//2):(psf_size//2)+1]
    psf_kernel = np.exp(-0.5 * (px**2 + py**2) / (1.2**2)).astype(np.float64)
    psf_kernel /= np.sum(psf_kernel)

    epsf_col1 = fits.Column(name="BINX", format="J", array=np.array([0]))
    epsf_col2 = fits.Column(name="BINY", format="J", array=np.array([0]))
    epsf_col3 = fits.Column(name="CWAVE", format="E", unit="um", array=np.array([wavelength_um]))
    epsf_col4 = fits.Column(name="CBAND", format="E", unit="um", array=np.array([3.0]))
    epsf_col5 = fits.Column(name="EPSF", format="1089D", dim="(33,33)", array=np.array([psf_kernel]))

    epsf_hdu = fits.BinTableHDU.from_columns(
        [epsf_col1, epsf_col2, epsf_col3, epsf_col4, epsf_col5],
        name="EPSF"
    )

    # 6. WCS-WAVE HDU
    wave_col1 = fits.Column(name="X", format="9J", array=np.arange(9, dtype=np.int32).reshape(1, 9))
    wave_col2 = fits.Column(name="Y", format="9J", array=np.arange(9, dtype=np.int32).reshape(1, 9))
    wave_col3 = fits.Column(name="VALUES", format="162E", dim="(2,9,9)", array=np.full((1, 2, 9, 9), wavelength_um, dtype=np.float32))
    wcs_wave_hdu = fits.BinTableHDU.from_columns([wave_col1, wave_col2, wave_col3], name="WCS-WAVE")

    return fits.HDUList([primary_hdu, image_hdu, flags_hdu, var_hdu, zodi_hdu, epsf_hdu, wcs_wave_hdu])

