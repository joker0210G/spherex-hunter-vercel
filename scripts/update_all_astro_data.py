"""
SPHEREx Hunter - Multi-Survey Catalog & Cutout Pre-Fetch Pipeline
NASA Space Apps Challenge 2026 - Team RIP

Pre-fetches and caches authentic multi-survey astronomical data across all
benchmark targets and showcase deep-sky regions:
- ESA Gaia DR3 (+ IRSA gaia_dr3_source fallback)
- NASA 2MASS PSC (+ Harvard CfA VizieR II/246/out fallback)
- NASA AllWISE + NEOWISE-R (+ Harvard CfA VizieR II/328/allwise fallback)
- NASA SPHEREx DR1 (spherex.obscore coverage + DR1 reference planes)
- CDS SIMBAD classifications
- Multi-survey cross-match & anchored 102-band SED spectra
- FITS optical/IR cutout difference images (preserving existing FITS cache: force_refresh=False)
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pyvo

from backend.services.catalog_engine import (
    CACHE_DIR_SPHEREX,
    _make_timeout_session,
    _safe_float,
    crossmatch_photometry,
    query_2mass_psc,
    query_gaia_dr3,
    query_simbad_metadata,
    query_spherex_archive,
    query_wise_catalog,
)
from backend.services.cutout_engine import BENCHMARKS, fetch_real_cutout, get_102_band_spectrum


def populate_spherex_reference_planes(timeout_s: float = 180.0) -> list[dict]:
    ref_path = os.path.join(CACHE_DIR_SPHEREX, "spherex_dr1_reference_planes.json")
    if os.path.exists(ref_path):
        try:
            with open(ref_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, list) and len(existing) > 0:
                print(f"[SPHEREx DR1] Loaded {len(existing)} cached DR1 reference planes from {ref_path}")
                return existing
        except Exception:
            pass

    print(f"[SPHEREx DR1] Querying IRSA spherex.obscore TOP 15 reference planes (timeout={timeout_s:.0f}s)...")
    t0 = time.time()
    try:
        tap = pyvo.dal.TAPService(
            "https://irsa.ipac.caltech.edu/TAP",
            session=_make_timeout_session(timeout_s),
        )
        res = tap.search(
            """
            SELECT TOP 15
                obs_id, s_ra, s_dec, t_min, t_max,
                energy_bandpassname, em_min, em_max, access_url
            FROM spherex.obscore
            """
        )
        planes = []
        for row in res:
            em_min_m = _safe_float(row["em_min"])
            em_max_m = _safe_float(row["em_max"])
            planes.append({
                "obs_id": str(row["obs_id"]),
                "s_ra": _safe_float(row["s_ra"]),
                "s_dec": _safe_float(row["s_dec"]),
                "t_min": _safe_float(row["t_min"]),
                "t_max": _safe_float(row["t_max"]),
                "energy_bandpassname": str(row["energy_bandpassname"] or ""),
                "em_min_um": round(em_min_m * 1e6, 4) if em_min_m is not None else None,
                "em_max_um": round(em_max_m * 1e6, 4) if em_max_m is not None else None,
                "access_url": str(row["access_url"] or ""),
            })
        planes.sort(key=lambda p: p["t_min"] if p["t_min"] is not None else -1.0, reverse=True)
        planes = planes[:12]
        if planes:
            with open(ref_path, "w", encoding="utf-8") as f:
                json.dump(planes, f, indent=2)
            print(f"[SPHEREx DR1] Cached {len(planes)} live DR1 reference planes in {time.time() - t0:.2f}s")
            return planes
    except Exception as e:
        print(f"[SPHEREx DR1] Reference query fallback unavailable ({time.time() - t0:.2f}s): {e}")
    return []


def build_target_list() -> dict[str, dict]:
    targets = {
        k: {"name": v["name"], "ra": v["ra"], "dec": v["dec"], "benchmark": True}
        for k, v in BENCHMARKS.items()
    }
    targets["orion"] = {"name": "Orion Nebula (M42)", "ra": 83.82208, "dec": -5.39111, "benchmark": False}
    targets["sgra"] = {"name": "Galactic Center (Sgr A*)", "ra": 266.41683, "dec": -29.00781, "benchmark": False}
    return targets


def main():
    os.makedirs(os.path.join("backend", "cache"), exist_ok=True)
    ref_planes = populate_spherex_reference_planes(timeout_s=180.0)
    targets = build_target_list()

    summary = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "spherex_dr1_reference_planes_count": len(ref_planes),
        "targets": {},
    }

    for key, info in targets.items():
        ra, dec = info["ra"], info["dec"]
        tkey = key if info["benchmark"] else None
        print(f"\n=== Updating {key} ({info['name']} @ RA={ra:.5f}, Dec={dec:.5f}) ===")

        # Cache both 3.0' (crossmatch/UI default) and 1.5' (get_102_band_spectrum default)
        for rad in (3.0, 1.5):
            gaia_res = query_gaia_dr3(ra=ra, dec=dec, radius_arcmin=rad, limit=20)
            twomass_res = query_2mass_psc(ra=ra, dec=dec, radius_arcmin=rad, limit=20)
            wise_res = query_wise_catalog(
                ra=ra, dec=dec, radius_arcmin=rad, limit=20,
                timeout_s=8.0, neowise_timeout_s=5.0,
            )
            print(
                f"  r={rad}': Gaia={gaia_res.get('total_sources', 0)} ({gaia_res.get('status')}), "
                f"2MASS={twomass_res.get('total_sources', 0)} ({twomass_res.get('status')}), "
                f"WISE={wise_res.get('count', 0)} ({wise_res.get('source_archive', wise_res.get('status'))})"
            )

        spherex_res = query_spherex_archive(ra=ra, dec=dec, radius_arcmin=15.0, limit=12, timeout_s=12.0)
        simbad_res = query_simbad_metadata(ra=ra, dec=dec, radius_arcmin=3.0)
        xmatch_3 = crossmatch_photometry(ra=ra, dec=dec, radius_arcmin=3.0)
        spec_res = get_102_band_spectrum(ra=ra, dec=dec, target_key=tkey)
        try:
            cutout_res = fetch_real_cutout(
                ra=ra, dec=dec, fov_arcmin=3.0, target_key=tkey, lod=1, force_refresh=False
            )
            cutout_status = cutout_res.get("status", "unknown")
        except Exception as ce:
            cutout_status = f"error: {ce}"

        wise_cp = xmatch_3.get("wise_counterpart") or {}
        summary["targets"][key] = {
            "name": info["name"],
            "ra": ra,
            "dec": dec,
            "gaia_count": xmatch_3.get("all_gaia_sources_count", 0),
            "twomass_count": xmatch_3.get("all_2mass_sources_count", 0),
            "wise_count": xmatch_3.get("all_wise_sources_count", 0),
            "wise_designation": wise_cp.get("designation"),
            "wise_w1_mag": wise_cp.get("w1_mag"),
            "wise_w2_mag": wise_cp.get("w2_mag"),
            "wise_w1_w2": wise_cp.get("w1_w2_color"),
            "spherex_coverage_type": spherex_res.get("coverage_type"),
            "spherex_planes_count": spherex_res.get("count", 0),
            "simbad_id": simbad_res.get("simbad_id"),
            "spectrum_data_type": spec_res.get("data_type"),
            "spectrum_measured_points": len(spec_res.get("measured_photometry_points", [])),
            "cutout_status": cutout_status,
        }
        print(
            f"  SPHEREx={spherex_res.get('coverage_type')} ({spherex_res.get('count', 0)}), "
            f"Spectrum={spec_res.get('data_type')} ({len(spec_res.get('measured_photometry_points', []))} pts), "
            f"Cutout={cutout_status}"
        )

    out_path = os.path.join("backend", "cache", "MULTI_SURVEY_SUMMARY.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved multi-survey cache summary to {out_path}")


if __name__ == "__main__":
    main()
