# 🛰️ SPHEREx Level-2 Spectral-Image Data Product Notes
> **Source:** NASA/IPAC Infrared Science Archive (IRSA) / SPHEREx Mission Data Release  
> **Inspection Date:** 2026-11-14  
> **Reference Files:** `data_samples/spherex_level2_sample.fits`, `data_samples/spectral_wcs_sample.fits`

---

## 1. File Structure & HDU Architecture

Inspection of the primary Level-2 spectral image product (`spherex_level2_sample.fits`, $2040 \times 2040$ pixels, ~65.4 MB) reveals a 7-extension multi-extension FITS (MEF) layout:

| HDU # | Extension Name | Extension Type | Dimensions | Data Type | Units (`BUNIT`) | Description |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | `PRIMARY` | `PrimaryHDU` | () | - | - | Metadata header with observation-level planning keywords |
| **1** | `IMAGE` | `ImageHDU` | $(2040, 2040)$ | `float32` | `MJy / sr` | Calibrated surface brightness image |
| **2** | `FLAGS` | `CompImageHDU` | $(2040, 2040)$ | `int32` | dimensionless | 29-bit pixel quality and mask flags (RICE-compressed) |
| **3** | `VARIANCE` | `ImageHDU` | $(2040, 2040)$ | `float32` | `MJy2 / sr2` | Pixel flux variance $\sigma_i^2$ for error propagation |
| **4** | `ZODI` | `ImageHDU` | $(2040, 2040)$ | `float32` | `MJy / sr` | 2D modeled zodiacal light emission map |
| **5** | `EPSF` | `BinTableHDU` | 441 rows $\times$ 11 cols | Table | - | Grid of empirical Point Spread Functions ($33 \times 33$ double) |
| **6** | `WCS-WAVE` | `BinTableHDU` | 1 row $\times$ 3 cols | Table | - | Tabular wavelength WCS (`-TAB`) lookup coordinates |

---

## 2. Essential Header Keywords & Coordinate Reference

From `HDU 1 (IMAGE)`:
- `TELESCOP`: `SPHEREx`
- `INSTRUME`: `SPHEREx`
- `TIMESYS`: `UTC`
- `MJD-OBS`: `60789.750762072` (Observation start time in MJD, UTC)
- `MJD-AVG`: `60789.751428261` (Effective mid-exposure time in MJD, UTC)
- `MJD-END`: `60789.75209445` (Observation end time in MJD, UTC)
- `OBSID`: `2025W17_4B_0001_1`
- `BUNIT`: `MJy / sr` (MegaJanskys per steradian)
- `WCSAXES`: `2`
- `CTYPE1`: `RA---TAN-SIP` (Gnomonic projection with Simple Imaging Polynomial distortion)
- `CTYPE2`: `DEC--TAN-SIP`
- `CRVAL1`: `160.615237739` (Reference Right Ascension in degrees, ICRS)
- `CRVAL2`: `30.6690774567` (Reference Declination in degrees, ICRS)
- `CRPIX1`: `1020.5`
- `CRPIX2`: `1020.5`

From `spectral_wcs_sample.fits`:
- `CWAVE` (`HDU 1`): $(2040, 2040)$ `float32` array specifying the exact central wavelength $\lambda_{\text{eff}}(x, y)$ in microns ($\mu\text{m}$) for every individual pixel across the linear variable filter (LVF).
- `CBAND` (`HDU 2`): $(2040, 2040)$ `float32` array mapping each pixel to its respective instrument band/channel ($1\text{--}6$).

---

## 3. Pixel Quality Bitmask Flag Definitions (`HDU 2: FLAGS`)

The flag plane `FLAGS` contains a 32-bit integer per pixel. The mask plane definitions are documented in `HDU 2` header cards `MSKN0000` through `MSKN0028` with corresponding bitmasks `MSKM00xx = (1 << xx)`:

| Plane $n$ | Bitmask Value (`1 << n`) | Flag Name | Definition / Scientific Significance | Processing Action in Pipeline |
| :---: | :---: | :--- | :--- | :--- |
| **0** | `1` ($2^0$) | `TRANSIENT` | Radiation hit or unconfirmed transient spike | **Mask as NaN** |
| **1** | `2` ($2^1$) | `OVERFLOW` | Detector charge well overflow / saturation | **Mask as NaN** |
| **2** | `4` ($2^2$) | `SUR_ERROR` | Sample-up-the-ramp fit slope error | **Mask as NaN** |
| **6** | `64` ($2^6$) | `NONFUNC` | Non-functional or dead pixel | **Mask as NaN** |
| **7** | `128` ($2^7$) | `DICHROIC` | Low throughput / filter edge degradation | Use with elevated variance |
| **9** | `512` ($2^9$) | `MISSING_DATA` | Telemetry dropped or unobserved pixel | **Mask as NaN** |
| **10** | `1024` ($2^{10}$) | `HOT` | Known warm/hot pixel | **Mask as NaN** |
| **11** | `2048` ($2^{11}$) | `COLD` | Known cold/unresponsive pixel | **Mask as NaN** |
| **12** | `4096` ($2^{12}$) | `FULLSAMPLE` | Saturated on first Fowler read | **Mask as NaN** |
| **14** | `16384` ($2^{14}$) | `PHANMISS` | Phantom missing read | **Mask as NaN** |
| **15** | `32768` ($2^{15}$) | `NONLINEAR` | Non-linear regime response | De-weight in chi-square fits |
| **17** | `131072` ($2^{17}$) | `PERSIST` | Residual charge from preceding bright exposure | Flag candidate if static |
| **19** | `524288` ($2^{19}$) | `OUTLIER` | Temporal or spatial sigma-clip outlier | **Mask as NaN** |
| **20** | `1048576` ($2^{20}$) | `CROSSTALK` | Electronic crosstalk from adjacent read channel | Ignore for faint discovery |
| **21** | `2097152` ($2^{21}$) | `SOURCE` | Cataloged astrophysical astronomical source | Preserve for forced photometry |
| **22** | `4194304` ($2^{22}$) | `GHOST` | Optical ghost reflection artifact | Reject candidate if coincident |
| **23** | `8388608` ($2^{23}$) | `GHOST_FPA` | Focal plane array ghost | Reject candidate if coincident |
| **24** | `16777216` ($2^{24}$) | `GHOST_EXT` | External optical baffle scatter | Reject candidate if coincident |
| **25** | `33554432` ($2^{25}$) | `STREAK` | Satellite streak or high-velocity trail | **Mask as NaN** |
| **26** | `67108864` ($2^{26}$) | `BLOOM` | Charge blooming from saturated star | **Mask as NaN** |
| **27** | `134217728` ($2^{27}$) | `SNOWBALL` | High-energy secondary cosmic ray particle shower | **Mask as NaN** |
| **28** | `268435456` ($2^{28}$) | `HALO` | Optical diffraction halo or transient halo | De-weight in detection |

### Severe Bad-Pixel Mask Definition
A pixel is rejected and converted to `np.nan` if:
```python
CRITICAL_BAD_MASK = (
    (1 << 0)   # TRANSIENT
    | (1 << 1) # OVERFLOW
    | (1 << 2) # SUR_ERROR
    | (1 << 6) # NONFUNC
    | (1 << 9) # MISSING_DATA
    | (1 << 10) # HOT
    | (1 << 11) # COLD
    | (1 << 12) # FULLSAMPLE
    | (1 << 19) # OUTLIER
    | (1 << 25) # STREAK
    | (1 << 26) # BLOOM
    | (1 << 27) # SNOWBALL
)
```

---

## 4. Empirical PSF Extension (`HDU 5: EPSF`)

`HDU 5 (EPSF)` is a binary table containing 441 spatial bins ($21 \times 21$ across the focal plane).
Columns:
- `BINX`, `BINY`: Spatial bin indices $(0\text{--}20)$
- `XCENTER`, `YCENTER`: Pixel coordinates of bin center
- `XWIDTH`, `YWIDTH`: Spatial coverage of bin in pixels
- `NSTAR`: Number of isolated field stars stacked to construct the empirical PSF
- `NEFF_MEAN`: Mean noise-equivalent pixels
- `CWAVE`: Central wavelength of the bin in microns ($\mu\text{m}$)
- `CBAND`: Band index
- `EPSF`: $33 \times 33$ 2D array of double-precision (`1089D`) values representing the normalized point spread function $P(u, v)$ with $\sum_{u, v} P(u, v) = 1.0$.

### Scientific Fallback Strategy
When querying non-SPHEREx legacy archives (e.g. DSS2, 2MASS, WISE) or when the SPHEREx `EPSF` table is absent in cutouts, the pipeline uses a 2D circularly symmetric Moffat or Gaussian kernel fallback:
$$\mathrm{PSF}(r) \propto \left(1 + \left(\frac{r}{\alpha}\right)^2\right)^{-\beta}$$
with $\mathrm{FWHM} = 6.2''$ for SPHEREx and $2.0''$ for 2MASS $K_s$.

---

## 5. Background & Zodiacal Light Subtraction (`HDU 4: ZODI`)

`HDU 4 (ZODI)` provides the pre-computed zodiacal light emission map modeled at the time of exposure.
- Background subtraction formula:
  $$I_{\text{sub}}(x, y) = I(x, y) - Z(x, y)$$
- Propagated variance:
  $$\sigma_{\text{sub}}^2(x, y) = \sigma^2_{\text{IMAGE}}(x, y) + \sigma^2_{\text{ZODI}}(x, y)$$
  When modeled without uncertainty, $\sigma^2_{\text{ZODI}}$ defaults to $0.05 \cdot Z(x, y)$ (5% systematic uncertainty).

