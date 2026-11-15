#!/usr/bin/env python3
"""
🛰️ SPHEREx Hunter - Sample Data Retrieval Utility
Downloads authentic SPHEREx Level-2 spectral-image FITS products from NASA IRSA
or local mirrors into data_samples/ for full-scale offline development and validation.
"""

import os
import sys
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data_samples")
os.makedirs(DATA_DIR, exist_ok=True)

# NASA IRSA sample product endpoint or official IPAC mirror
SAMPLE_FITS_URL = "https://irsa.ipac.caltech.edu/data/SPHEREx/level2_sample.fits"
LOCAL_FITS_PATH = os.path.join(DATA_DIR, "spherex_level2_sample.fits")


def fetch_spherex_sample(force: bool = False):
    if os.path.exists(LOCAL_FITS_PATH) and not force:
        size_mb = os.path.getsize(LOCAL_FITS_PATH) / (1024 * 1024)
        print(f"✅ SPHEREx Level-2 sample already exists: {LOCAL_FITS_PATH} ({size_mb:.1f} MB)")
        return LOCAL_FITS_PATH

    print(f"📥 Downloading authentic SPHEREx sample FITS from {SAMPLE_FITS_URL}...")
    try:
        urllib.request.urlretrieve(SAMPLE_FITS_URL, LOCAL_FITS_PATH)
        print(f"✅ Download complete: {LOCAL_FITS_PATH}")
        return LOCAL_FITS_PATH
    except Exception as e:
        print(f"⚠️ Could not download from remote URL ({e}).")
        print("Note: In testing environments, use tests/fixtures/synthetic_spherex.py for full-fidelity tests without downloads.")
        return None


if __name__ == "__main__":
    force_download = "--force" in sys.argv
    fetch_spherex_sample(force=force_download)

