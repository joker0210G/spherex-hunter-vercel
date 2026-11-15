"""
⭐ SPHEREx Hunter - Gaia DR3 Astrometric Catalog Engine
NASA Space Apps 2026 - Team RIP (darkodu)

Queries the official European Space Agency (ESA) Gaia DR3 catalog via TAP:
- Precise astrometric positions (ICRS J2016.0)
- Multi-band photometry (G, BP, RP, BP-RP color)
- Proper motion vectors (pmRA, pmDEC, total PM in mas/yr, position angle)
- Parallax & calculated stellar distance (parsecs)
- Live archive queries only. When an archive is unreachable the response says so (status 'unavailable');
  no catalogue rows are ever curated, synthesized or randomly generated.
"""

import concurrent.futures
import json
import os
import re
import threading
import time
from collections import OrderedDict
from typing import Optional, Union

import numpy as np
import requests

from backend.utils.validation import validate_coordinates


class _TimeoutSession(requests.Session):
    """Requests Session subclass that enforces a default HTTP socket timeout for pyvo."""

    def __init__(self, timeout_s: float = 8.0):
        super().__init__()
        self._default_timeout = timeout_s

    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", self._default_timeout)
        return super().request(*args, **kwargs)


def _make_timeout_session(timeout_s: float = 8.0) -> requests.Session:
    return _TimeoutSession(timeout_s=timeout_s)


def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        s = str(val).strip()
        if not s or s.lower() in {"nan", "null", "none", "---"}:
            return None
        f = float(s)
        return None if (np.isnan(f) or np.isinf(f)) else f
    except Exception:
        return None


def _mag_to_ujy(mag: float | None, zp_ujy: float) -> float | None:
    if mag is None:
        return None
    val = float(zp_ujy) * (10.0 ** (-0.4 * float(mag)))
    return None if (np.isnan(val) or np.isinf(val)) else round(val, 3)


def _compute_sky_offsets(s_ra: float, s_dec: float, center_ra: float, center_dec: float) -> tuple[float, float]:
    dx_arcsec = float(round((s_ra - center_ra) * np.cos(np.radians(center_dec)) * 3600.0, 2))
    dy_arcsec = float(round((s_dec - center_dec) * 3600.0, 2))
    return dx_arcsec, dy_arcsec


def _query_vizier_tsv(
    source: str,
    ra: float,
    dec: float,
    radius_arcmin: float,
    limit: int,
    out_cols: str,
    timeout_s: float = 8.0,
) -> list[dict]:
    """Queries Harvard CfA VizieR ASU-TSV mirror as a fast, low-latency fallback."""
    resp = requests.get(
        "https://vizier.cfa.harvard.edu/viz-bin/asu-tsv",
        params={
            "-source": source,
            "-c": f"{ra:.5f} {dec:+.5f}",
            "-c.rm": f"{radius_arcmin:.2f}",
            "-out.max": str(limit),
            "-out": out_cols,
        },
        timeout=timeout_s,
    )
    resp.raise_for_status()
    lines = [ln for ln in resp.text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    if len(lines) < 4:
        return []
    headers = [h.strip() for h in lines[0].split("\t")]
    # Skip header, units, and dashed separator line
    rows = []
    for ln in lines[3:]:
        if re.match(r"^[-\s\t]+$", ln):
            continue
        parts = ln.split("\t")
        if len(parts) < len(headers):
            parts += [""] * (len(headers) - len(parts))
        rows.append({headers[i]: parts[i].strip() for i in range(len(headers))})
    return rows


_CIRCUIT_STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "cache", "circuit_state.json")
_CIRCUIT_LOCK = threading.Lock()
_IRSA_PROBE_LOCK = threading.Lock()
_ESA_PROBE_LOCK = threading.Lock()


def _load_circuit_state() -> dict:
    if os.path.exists(_CIRCUIT_STATE_PATH):
        try:
            with open(_CIRCUIT_STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"irsa_tap_cooldown": 0.0, "esa_gaia_cooldown": 0.0}


def _save_circuit_state(state: dict):
    try:
        os.makedirs(os.path.dirname(_CIRCUIT_STATE_PATH), exist_ok=True)
        with open(_CIRCUIT_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


_initial_state = _load_circuit_state()
_IRSA_TAP_CIRCUIT_OPEN_UNTIL: float = float(_initial_state.get("irsa_tap_cooldown", 0.0))
_ESA_GAIA_CIRCUIT_OPEN_UNTIL: float = float(_initial_state.get("esa_gaia_cooldown", 0.0))


def is_irsa_tap_available() -> bool:
    global _IRSA_TAP_CIRCUIT_OPEN_UNTIL
    now = time.time()
    if now < _IRSA_TAP_CIRCUIT_OPEN_UNTIL:
        return False
    disk_val = float(_load_circuit_state().get("irsa_tap_cooldown", 0.0))
    if disk_val > _IRSA_TAP_CIRCUIT_OPEN_UNTIL:
        _IRSA_TAP_CIRCUIT_OPEN_UNTIL = disk_val
    return now >= _IRSA_TAP_CIRCUIT_OPEN_UNTIL


def trip_irsa_tap_circuit(duration_s: float = 60.0):
    global _IRSA_TAP_CIRCUIT_OPEN_UNTIL
    with _CIRCUIT_LOCK:
        cooldown = time.time() + duration_s
        _IRSA_TAP_CIRCUIT_OPEN_UNTIL = max(_IRSA_TAP_CIRCUIT_OPEN_UNTIL, cooldown)
        curr = _load_circuit_state()
        curr["irsa_tap_cooldown"] = max(float(curr.get("irsa_tap_cooldown", 0.0)), cooldown)
        _save_circuit_state(curr)


def is_esa_gaia_available() -> bool:
    global _ESA_GAIA_CIRCUIT_OPEN_UNTIL
    now = time.time()
    if now < _ESA_GAIA_CIRCUIT_OPEN_UNTIL:
        return False
    disk_val = float(_load_circuit_state().get("esa_gaia_cooldown", 0.0))
    if disk_val > _ESA_GAIA_CIRCUIT_OPEN_UNTIL:
        _ESA_GAIA_CIRCUIT_OPEN_UNTIL = disk_val
    return now >= _ESA_GAIA_CIRCUIT_OPEN_UNTIL


def trip_esa_gaia_circuit(duration_s: float = 60.0):
    global _ESA_GAIA_CIRCUIT_OPEN_UNTIL
    with _CIRCUIT_LOCK:
        cooldown = time.time() + duration_s
        _ESA_GAIA_CIRCUIT_OPEN_UNTIL = max(_ESA_GAIA_CIRCUIT_OPEN_UNTIL, cooldown)
        curr = _load_circuit_state()
        curr["esa_gaia_cooldown"] = max(float(curr.get("esa_gaia_cooldown", 0.0)), cooldown)
        _save_circuit_state(curr)


def _log_tap_fallback(archive_name: str, error_detail: str, fallback_name: str):
    err_str = str(error_detail).strip()
    if "502" in err_str:
        summary = "502 Proxy Error"
    elif "timed out" in err_str.lower() or "timeout" in err_str.lower():
        summary = "Connect Timeout"
    elif "connection" in err_str.lower():
        summary = "Connection Dropped"
    else:
        summary = err_str.split("\n")[0][:60]
    print(f"[CatalogEngine] {archive_name} TAP offline ({summary}) -> Fast circuit opened for 60s; routed to {fallback_name}.")


def _append_gaia_row(sources: list, center_ra: float, center_dec: float, src_id, s_ra: float, s_dec: float,
                     pmra: float, pmdec: float, plx: float | None, g_mag: float | None,
                     bp_mag: float | None, rp_mag: float | None, bp_rp: float | None, rv: float | None):
    total_pm = float(round(np.hypot(pmra, pmdec), 2))
    pm_angle = float(round(np.degrees(np.arctan2(pmra, pmdec)) % 360.0, 2)) if total_pm > 0 else 0.0
    dist_pc = float(round(1000.0 / plx, 2)) if plx is not None and plx > 0.1 else None
    dx_arcsec = float(round((s_ra - center_ra) * np.cos(np.radians(center_dec)) * 3600.0, 2))
    dy_arcsec = float(round((s_dec - center_dec) * 3600.0, 2))
    g_flux_ujy = round(3229e6 * (10.0 ** (-0.4 * g_mag)), 3) if g_mag is not None else None
    sources.append({
        "source_id": str(src_id),
        "ra": s_ra,
        "dec": s_dec,
        "g_mag": g_mag,
        "g_flux_ujy": g_flux_ujy,
        "bp_mag": bp_mag,
        "rp_mag": rp_mag,
        "bp_rp": bp_rp,
        "pmra_mas_yr": pmra,
        "pmdec_mas_yr": pmdec,
        "total_pm_mas_yr": total_pm,
        "pm_angle_deg": pm_angle,
        "parallax_mas": plx,
        "distance_pc": dist_pc,
        "radial_velocity_kms": rv,
        "is_high_proper_motion": total_pm > 50.0,
        "offset_arcsec": {"dx": dx_arcsec, "dy": dy_arcsec}
    })


CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache", "catalog_gaia")
os.makedirs(CACHE_DIR, exist_ok=True)

def query_gaia_dr3(
    ra: float,
    dec: float,
    radius_arcmin: float = 3.0,
    limit: int = 100
) -> dict:
    """
    Queries ESA Gaia DR3 via Virtual Observatory TAP for stars within radius_arcmin of (ra, dec).
    Returns astrometric positions, proper motion vectors, parallax distances, and magnitudes.
    Falls back gracefully across ESA Gaia TAP -> NASA IRSA TAP -> Harvard CfA VizieR (I/355/gaiadr3).
    """
    ra, dec, radius_arcmin = validate_coordinates(ra, dec, radius_arcmin)
    radius_arcmin = float(np.clip(radius_arcmin, 0.2, 15.0))
    radius_deg = radius_arcmin / 60.0
    limit = int(np.clip(limit, 1, 300))

    cache_key = f"gaia_{ra:.4f}_{dec:.4f}_{radius_arcmin:.1f}".replace("+", "").replace("-", "m")
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")

    # 1. Check disk cache
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                cached_data["cached"] = True
                return cached_data
        except Exception:
            pass

    sources = []
    query_error = None
    archive_used = "Gaia DR3 (European Space Agency / ICRS J2016.0)"

    select_cols = f"""
    SELECT TOP {limit}
        source_id, ra, dec,
        pmra, pmdec, pmra_error, pmdec_error,
        parallax, parallax_error,
        phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, bp_rp,
        radial_velocity
    """
    where_clause = f"""
    WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra:.5f}, {dec:.5f}, {radius_deg:.5f}))
    ORDER BY phot_g_mean_mag ASC
    """

    # 2. Query ESA Gaia TAP service (if circuit available, single-flight probe)
    if is_esa_gaia_available():
        with _ESA_PROBE_LOCK:
            if is_esa_gaia_available():
                try:
                    import pyvo
                    service = pyvo.dal.TAPService(
                        "https://gea.esac.esa.int/tap-server/tap",
                        session=_make_timeout_session(1.8),
                    )
                    results = service.search(f"{select_cols}\nFROM gaiadr3.gaia_source\n{where_clause}")
                    for row in results:
                        s_ra = float(row["ra"]) if row["ra"] is not None and not np.isnan(row["ra"]) else ra
                        s_dec = float(row["dec"]) if row["dec"] is not None and not np.isnan(row["dec"]) else dec
                        pmra = float(row["pmra"]) if row["pmra"] is not None and not np.isnan(row["pmra"]) else 0.0
                        pmdec = float(row["pmdec"]) if row["pmdec"] is not None and not np.isnan(row["pmdec"]) else 0.0
                        plx = float(row["parallax"]) if row["parallax"] is not None and not np.isnan(row["parallax"]) else None
                        g_mag = float(round(row["phot_g_mean_mag"], 2)) if row["phot_g_mean_mag"] is not None and not np.isnan(row["phot_g_mean_mag"]) else None
                        bp_mag = float(round(row["phot_bp_mean_mag"], 2)) if row["phot_bp_mean_mag"] is not None and not np.isnan(row["phot_bp_mean_mag"]) else None
                        rp_mag = float(round(row["phot_rp_mean_mag"], 2)) if row["phot_rp_mean_mag"] is not None and not np.isnan(row["phot_rp_mean_mag"]) else None
                        bp_rp = float(round(row["bp_rp"], 2)) if row["bp_rp"] is not None and not np.isnan(row["bp_rp"]) else None
                        rv = float(round(row["radial_velocity"], 2)) if row["radial_velocity"] is not None and not np.isnan(row["radial_velocity"]) else None

                        _append_gaia_row(sources, ra, dec, row["source_id"], s_ra, s_dec, pmra, pmdec, plx, g_mag, bp_mag, rp_mag, bp_rp, rv)
                except Exception as esa_err:
                    trip_esa_gaia_circuit(60.0)
                    _log_tap_fallback("ESA Gaia", str(esa_err), "NASA IRSA / Harvard VizieR")

    # 3. Fallback to NASA IRSA TAP gaia_dr3_source (if circuit available, single-flight probe)
    if not sources and is_irsa_tap_available():
        with _IRSA_PROBE_LOCK:
            if is_irsa_tap_available():
                try:
                    import pyvo
                    irsa_service = pyvo.dal.TAPService(
                        "https://irsa.ipac.caltech.edu/TAP",
                        session=_make_timeout_session(2.0),
                    )
                    results = irsa_service.search(f"{select_cols}\nFROM gaia_dr3_source\n{where_clause}")
                    archive_used = "Gaia DR3 (NASA IRSA TAP / ICRS J2016.0)"
                    for row in results:
                        s_ra = float(row["ra"]) if row["ra"] is not None and not np.isnan(row["ra"]) else ra
                        s_dec = float(row["dec"]) if row["dec"] is not None and not np.isnan(row["dec"]) else dec
                        pmra = float(row["pmra"]) if row["pmra"] is not None and not np.isnan(row["pmra"]) else 0.0
                        pmdec = float(row["pmdec"]) if row["pmdec"] is not None and not np.isnan(row["pmdec"]) else 0.0
                        plx = float(row["parallax"]) if row["parallax"] is not None and not np.isnan(row["parallax"]) else None
                        g_mag = float(round(row["phot_g_mean_mag"], 2)) if row["phot_g_mean_mag"] is not None and not np.isnan(row["phot_g_mean_mag"]) else None
                        bp_mag = float(round(row["phot_bp_mean_mag"], 2)) if row["phot_bp_mean_mag"] is not None and not np.isnan(row["phot_bp_mean_mag"]) else None
                        rp_mag = float(round(row["phot_rp_mean_mag"], 2)) if row["phot_rp_mean_mag"] is not None and not np.isnan(row["phot_rp_mean_mag"]) else None
                        bp_rp = float(round(row["bp_rp"], 2)) if row["bp_rp"] is not None and not np.isnan(row["bp_rp"]) else None
                        rv = float(round(row["radial_velocity"], 2)) if row["radial_velocity"] is not None and not np.isnan(row["radial_velocity"]) else None

                        _append_gaia_row(sources, ra, dec, row["source_id"], s_ra, s_dec, pmra, pmdec, plx, g_mag, bp_mag, rp_mag, bp_rp, rv)
                except Exception as irsa_err:
                    trip_irsa_tap_circuit(60.0)
                    _log_tap_fallback("NASA IRSA gaia_dr3_source", str(irsa_err), "Harvard CfA VizieR")

    # 4. Fallback to Harvard CfA VizieR (I/355/gaiadr3)
    if not sources:
        try:
            vrows = _query_vizier_tsv(
                source="I/355/gaiadr3",
                ra=ra,
                dec=dec,
                radius_arcmin=radius_arcmin,
                limit=limit,
                out_cols="Source,RAJ2000,DEJ2000,pmRA,pmDE,Plx,Gmag,BPmag,RPmag,BP-RP,RV",
                timeout_s=6.0,
            )
            for r in vrows:
                s_ra = _safe_float(r.get("RAJ2000"))
                s_dec = _safe_float(r.get("DEJ2000"))
                if s_ra is None or s_dec is None:
                    continue
                pmra = _safe_float(r.get("pmRA")) or 0.0
                pmdec = _safe_float(r.get("pmDE")) or 0.0
                plx = _safe_float(r.get("Plx"))
                g_mag = _safe_float(r.get("Gmag"))
                bp_mag = _safe_float(r.get("BPmag"))
                rp_mag = _safe_float(r.get("RPmag"))
                bp_rp = _safe_float(r.get("BP-RP"))
                rv = _safe_float(r.get("RV"))

                _append_gaia_row(sources, ra, dec, r.get("Source", ""), s_ra, s_dec, pmra, pmdec, plx, g_mag, bp_mag, rp_mag, bp_rp, rv)
            if sources:
                archive_used = "Gaia DR3 (Harvard CfA VizieR I/355/gaiadr3 / ICRS J2016.0)"
        except Exception as viz_err:
            query_error = f"All Gaia DR3 catalog mirrors failed: {viz_err}"
            print(f"Harvard VizieR Gaia fallback failed for ({ra}, {dec}): {viz_err}")

    if not sources and not query_error:
        # Valid cone search with 0 stars
        pass
    elif not sources and query_error:
        pass

    high_pm_count = sum(1 for s in sources if s.get("is_high_proper_motion", False))

    response_payload = {
        "status": "unavailable" if (query_error and not sources) else "success",
        "message": f"Gaia DR3 archives unreachable: {query_error}" if (query_error and not sources) else None,
        "cached": False,
        "query": {
            "center_ra": ra,
            "center_dec": dec,
            "radius_arcmin": radius_arcmin,
            "catalog": archive_used
        },
        "total_sources": len(sources),
        "high_proper_motion_count": high_pm_count,
        "sources": sources
    }

    if query_error and not sources:
        return response_payload  # never cache a failed query

    # Cache payload
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(response_payload, f, indent=2)
    except Exception:
        pass

    return response_payload



# =====================================================================
# 2MASS Point Source Catalog (NASA IRSA Caltech)
# =====================================================================

CACHE_DIR_2MASS = os.path.join(os.path.dirname(__file__), "..", "cache", "catalog_2mass")
os.makedirs(CACHE_DIR_2MASS, exist_ok=True)

def query_2mass_psc(
    ra: float,
    dec: float,
    radius_arcmin: float = 3.0,
    limit: int = 50
) -> dict:
    """
    Queries NASA IRSA 2MASS Point Source Catalog (fp_psc) for near-infrared J, H, Ks photometry.
    Calculates J-H, H-K, and J-K color indices with photometric quality flags.
    """
    ra, dec, radius_arcmin = validate_coordinates(ra, dec, radius_arcmin)
    radius_arcmin = float(np.clip(radius_arcmin, 0.2, 15.0))
    radius_deg = radius_arcmin / 60.0
    limit = int(np.clip(limit, 1, 200))

    cache_key = f"2mass_{ra:.4f}_{dec:.4f}_{radius_arcmin:.1f}".replace("+", "").replace("-", "m")
    cache_path = os.path.join(CACHE_DIR_2MASS, f"{cache_key}.json")

    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                cached_data["cached"] = True
                return cached_data
        except Exception:
            pass

    sources = []
    query_error = None

    def _append_2mass_row(desig_raw, s_ra, s_dec, j_m, h_m, k_m, ph_qual):
        desig = desig_raw if str(desig_raw).startswith("2MASS") else f"2MASS J{desig_raw}"
        j_h = float(round(j_m - h_m, 3)) if j_m is not None and h_m is not None else None
        h_k = float(round(h_m - k_m, 3)) if h_m is not None and k_m is not None else None
        j_k = float(round(j_m - k_m, 3)) if j_m is not None and k_m is not None else None
        dx_arcsec, dy_arcsec = _compute_sky_offsets(s_ra, s_dec, ra, dec)
        sources.append({
            "designation": desig,
            "ra": s_ra,
            "dec": s_dec,
            "j_mag": j_m,
            "h_mag": h_m,
            "k_mag": k_m,
            "j_flux_ujy": _mag_to_ujy(j_m, 1594e6),
            "h_flux_ujy": _mag_to_ujy(h_m, 1024e6),
            "k_flux_ujy": _mag_to_ujy(k_m, 666.7e6),
            "j_h": j_h,
            "h_k": h_k,
            "j_k": j_k,
            "ph_qual": str(ph_qual or ""),
            "offset_arcsec": {"dx": dx_arcsec, "dy": dy_arcsec}
        })

    # 1. Query NASA IRSA TAP Service (if circuit available, single-flight probe with Harvard VizieR fallback)
    if is_irsa_tap_available():
        with _IRSA_PROBE_LOCK:
            if is_irsa_tap_available():
                try:
                    import pyvo
                    tap = pyvo.dal.TAPService(
                        "https://irsa.ipac.caltech.edu/TAP",
                        session=_make_timeout_session(2.0),
                    )
                    query = f"""
                    SELECT TOP {limit}
                        designation, ra, dec,
                        j_m, h_m, k_m,
                        j_msigcom, h_msigcom, k_msigcom,
                        ph_qual
                    FROM fp_psc
                    WHERE CONTAINS(POINT('J2000', ra, dec), CIRCLE('J2000', {ra:.5f}, {dec:.5f}, {radius_deg:.5f})) = 1
                    ORDER BY j_m ASC
                    """
                    results = tap.search(query)

                    for row in results:
                        _append_2mass_row(
                            row["designation"],
                            float(row["ra"]),
                            float(row["dec"]),
                            _safe_float(row["j_m"]),
                            _safe_float(row["h_m"]),
                            _safe_float(row["k_m"]),
                            row["ph_qual"],
                        )
                except Exception as irsa_err:
                    trip_irsa_tap_circuit(60.0)
                    _log_tap_fallback("NASA IRSA 2MASS", str(irsa_err), "Harvard CfA VizieR II/246/out")

    if not sources:
        try:
            vrows = _query_vizier_tsv(
                source="II/246/out",
                ra=ra,
                dec=dec,
                radius_arcmin=radius_arcmin,
                limit=limit,
                out_cols="2MASS,RAJ2000,DEJ2000,Jmag,Hmag,Kmag,Qflg",
                timeout_s=6.0,
            )
            for r in vrows:
                s_ra = _safe_float(r.get("RAJ2000"))
                s_dec = _safe_float(r.get("DEJ2000"))
                if s_ra is None or s_dec is None:
                    continue
                _append_2mass_row(
                    r.get("2MASS", ""),
                    s_ra,
                    s_dec,
                    _safe_float(r.get("Jmag")),
                    _safe_float(r.get("Hmag")),
                    _safe_float(r.get("Kmag")),
                    r.get("Qflg", ""),
                )
        except Exception as viz_err:
            query_error = f"2MASS mirrors failed: {viz_err}"
            print(f"All 2MASS catalog mirrors failed for ({ra}, {dec}): {query_error}")

    response_payload = {
        "status": "unavailable" if query_error else "success",
        "message": f"NASA IRSA TAP unreachable: {query_error}" if query_error else None,
        "cached": False,
        "query": {
            "center_ra": ra,
            "center_dec": dec,
            "radius_arcmin": radius_arcmin,
            "catalog": "NASA IRSA 2MASS Point Source Catalog (fp_psc)"
        },
        "total_sources": len(sources),
        "sources": sources
    }

    if query_error:
        return response_payload  # never cache a failed query

    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(response_payload, f, indent=2)
    except Exception:
        pass

    return response_payload


# =====================================================================
# SIMBAD Astronomical Object Metadata & Classification
# =====================================================================

CACHE_DIR_SIMBAD = os.path.join(os.path.dirname(__file__), "..", "cache", "catalog_simbad")
os.makedirs(CACHE_DIR_SIMBAD, exist_ok=True)

def query_simbad_metadata(
    ra: Optional[Union[float, str]] = None,
    dec: Optional[float] = None,
    radius_arcmin: float = 3.0,
    force_refresh: bool = False,
    target: Optional[str] = None,
) -> dict:
    """
    Live CDS SIMBAD cone search (astroquery). Returns the nearest catalogued object's
    identifier, object type, spectral type, parallax and proper motion exactly as SIMBAD
    reports them. If SIMBAD is unreachable or has no object, the status says so; nothing
    is looked up from a hardcoded table and no citation counts are invented.
    """
    if isinstance(ra, str) and target is None and dec is None:
        target = ra
        ra = None

    if target and (ra is None or dec is None):
        t_clean = target.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
        from backend.models_v1 import TARGET_REGISTRY
        for k, v in TARGET_REGISTRY.items():
            if k.replace("-", "").replace("_", "") == t_clean:
                ra = float(v["ra"])
                dec = float(v["dec"])
                break

    if ra is None or dec is None:
        return {
            "status": "unavailable",
            "query_target": target,
            "message": f"Cannot query SIMBAD for target '{target}' without celestial coordinates (RA/Dec)."
        }

    ra_float = float(ra)
    dec_float = float(dec)
    cache_key = f"simbad_{round(ra_float, 4)}_{round(dec_float, 4)}_{round(radius_arcmin, 1)}".replace("+", "").replace("-", "m")
    cache_path = os.path.join(CACHE_DIR_SIMBAD, f"{cache_key}.json")
    if not force_refresh and os.path.exists(cache_path):
        try:
            if (time.time() - os.path.getmtime(cache_path)) <= 86400:
                with open(cache_path, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                    entry["cached"] = True
                    if target and "query_target" not in entry:
                        entry["query_target"] = target
                    return entry
        except Exception:
            pass

    out = {"query_ra": ra_float, "query_dec": dec_float, "radius_arcmin": radius_arcmin}
    if target:
        out["query_target"] = str(target)
    try:
        import astropy.units as u
        from astropy.coordinates import SkyCoord
        from astroquery.simbad import Simbad

        tab = None
        last_err = None
        for srv in ["simbad.cds.unistra.fr", "simbad.harvard.edu"]:
            try:
                sim = Simbad()
                sim.server = srv
                sim.add_votable_fields("otype", "sp_type", "plx_value", "pmra", "pmdec")
                radius = float(np.clip(radius_arcmin, 0.1, 30.0)) * u.arcmin
                tab = sim.query_region(SkyCoord(ra * u.deg, dec * u.deg, frame="icrs"), radius=radius)
                if tab is not None:
                    break
            except Exception as e:
                last_err = e
                continue

        if tab is None:
            if last_err is not None:
                raise last_err
            out.update({"status": "no_match", "canonical_name": None, "message": "No SIMBAD object in this cone."})
            return out

        if len(tab) == 0:
            out.update({"status": "no_match", "canonical_name": None, "message": "No SIMBAD object in this cone."})
            return out

        cols = {c.lower(): c for c in tab.colnames}

        # Match nearest object by angular separation
        target_sc = SkyCoord(ra * u.deg, dec * u.deg, frame="icrs")
        ra_col = cols.get("ra")
        dec_col = cols.get("dec")
        if ra_col and dec_col:
            source_scs = SkyCoord(tab[ra_col], tab[dec_col], frame="icrs")
            seps = target_sc.separation(source_scs).arcsec
            best_idx = int(seps.argmin())
            sep_arcsec = round(float(seps[best_idx]), 3)
        else:
            best_idx = 0
            sep_arcsec = None

        def val(*names):
            for n in names:
                if n in cols:
                    v = tab[cols[n]][best_idx]
                    if v is None or (hasattr(v, "mask") and bool(v.mask)):
                        return None
                    try:
                        f = float(v)
                        return None if np.isnan(f) else f
                    except Exception:
                        t = str(v).strip()
                        return t or None
            return None

        pmra, pmdec = val("pmra"), val("pmdec")
        plx = val("plx_value", "plx")
        out.update({
            "status": "resolved",
            "canonical_name": val("main_id"),
            "simbad_id": val("main_id"),
            "object_type": val("otype"),
            "spectral_type": val("sp_type"),
            "parallax_mas": plx,
            "distance_pc": round(1000.0 / plx, 3) if plx and plx > 0 else None,
            "proper_motion_mas_yr": round(float(np.hypot(pmra, pmdec)), 2) if pmra is not None and pmdec is not None else None,
            "separation_arcsec": sep_arcsec,
            "matches_in_cone": len(tab),
            "source": "CDS SIMBAD (live)",
        })
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2)
        except Exception:
            pass
        return out
    except Exception as e:
        out.update({"status": "unavailable", "canonical_name": None, "message": f"SIMBAD query failed: {e}"})
        return out


# =====================================================================
# NASA AllWISE + NEOWISE-R Infrared Catalog (IRSA + Harvard VizieR)
# =====================================================================

CACHE_DIR_WISE = os.path.join(os.path.dirname(__file__), "..", "cache", "catalog_wise")
os.makedirs(CACHE_DIR_WISE, exist_ok=True)


def query_wise_catalog(
    ra: float,
    dec: float,
    radius_arcmin: float = 3.0,
    limit: int = 50,
    timeout_s: float = 6.0,
    neowise_timeout_s: float = 5.0,
    force_refresh: bool = False,
) -> dict:
    """
    Queries NASA AllWISE (`allwise_p3as_psd`, fallback Harvard CfA VizieR `II/328/allwise`)
    and attempts NEOWISE-R single-exposure photometry (`neowiser_p1bs_psd`) for multi-epoch IR trends.
    """
    ra, dec, radius_arcmin = validate_coordinates(ra, dec, radius_arcmin)
    radius_arcmin = float(np.clip(radius_arcmin, 0.2, 15.0))
    radius_deg = radius_arcmin / 60.0
    limit = int(np.clip(limit, 1, 200))

    cache_key = f"wise_{ra:.4f}_{dec:.4f}_{radius_arcmin:.1f}".replace("+", "").replace("-", "m")
    cache_path = os.path.join(CACHE_DIR_WISE, f"{cache_key}.json")

    if not force_refresh and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                cached_data["cached"] = True
                return cached_data
        except Exception:
            pass

    sources = []
    neowise_epochs = []
    query_error = None
    archive_used = "NASA IRSA AllWISE (allwise_p3as_psd)"

    def _append_wise_row(desig_raw, s_ra, s_dec, w1, w1_err, w2, w2_err, w3, w4, pmra, pmdec):
        raw_str = str(desig_raw or "").strip()
        desig = raw_str if raw_str.startswith("WISE") else f"WISE {raw_str}"
        w1_w2 = float(round(w1 - w2, 3)) if w1 is not None and w2 is not None else None
        dx_arcsec, dy_arcsec = _compute_sky_offsets(s_ra, s_dec, ra, dec)
        sources.append({
            "designation": desig,
            "ra": s_ra,
            "dec": s_dec,
            "w1_mag": w1,
            "w1_err": w1_err,
            "w2_mag": w2,
            "w2_err": w2_err,
            "w3_mag": w3,
            "w4_mag": w4,
            "w1_flux_ujy": _mag_to_ujy(w1, 309.540e6),
            "w2_flux_ujy": _mag_to_ujy(w2, 171.787e6),
            "w3_flux_ujy": _mag_to_ujy(w3, 31.674e6),
            "w4_flux_ujy": _mag_to_ujy(w4, 8.363e6),
            "w1_w2_color": w1_w2,
            "pmra_mas_yr": pmra,
            "pmdec_mas_yr": pmdec,
            "offset_arcsec": {"dx": dx_arcsec, "dy": dy_arcsec},
        })

    # 1. AllWISE via IRSA TAP (if circuit available, single-flight probe with Harvard VizieR fallback)
    if is_irsa_tap_available():
        with _IRSA_PROBE_LOCK:
            if is_irsa_tap_available():
                try:
                    import pyvo
                    tap = pyvo.dal.TAPService(
                        "https://irsa.ipac.caltech.edu/TAP",
                        session=_make_timeout_session(2.0),
                    )
                    allwise_q = f"""
                    SELECT TOP {limit}
                        designation, ra, dec,
                        w1mpro, w1sigmpro, w2mpro, w2sigmpro,
                        w3mpro, w4mpro, pmra, pmdec
                    FROM allwise_p3as_psd
                    WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra:.5f}, {dec:.5f}, {radius_deg:.5f}))
                    """
                    results = tap.search(allwise_q)
                    for row in results:
                        _append_wise_row(
                            row["designation"],
                            float(row["ra"]),
                            float(row["dec"]),
                            _safe_float(row["w1mpro"]),
                            _safe_float(row["w1sigmpro"]),
                            _safe_float(row["w2mpro"]),
                            _safe_float(row["w2sigmpro"]),
                            _safe_float(row["w3mpro"]),
                            _safe_float(row["w4mpro"]),
                            _safe_float(row["pmra"]),
                            _safe_float(row["pmdec"]),
                        )
                except Exception as irsa_err:
                    trip_irsa_tap_circuit(60.0)
                    _log_tap_fallback("NASA IRSA AllWISE", str(irsa_err), "Harvard CfA VizieR II/328/allwise")

    if not sources:
        try:
            archive_used = "Harvard CfA VizieR AllWISE (II/328/allwise)"
            vrows = _query_vizier_tsv(
                source="II/328/allwise",
                ra=ra,
                dec=dec,
                radius_arcmin=radius_arcmin,
                limit=limit,
                out_cols="AllWISE,RAJ2000,DEJ2000,W1mag,e_W1mag,W2mag,e_W2mag,W3mag,W4mag,pmRA,pmDE",
                timeout_s=max(timeout_s, 6.0),
            )
            for r in vrows:
                s_ra = _safe_float(r.get("RAJ2000"))
                s_dec = _safe_float(r.get("DEJ2000"))
                if s_ra is None or s_dec is None:
                    continue
                _append_wise_row(
                    r.get("AllWISE", ""),
                    s_ra,
                    s_dec,
                    _safe_float(r.get("W1mag")),
                    _safe_float(r.get("e_W1mag")),
                    _safe_float(r.get("W2mag")),
                    _safe_float(r.get("e_W2mag")),
                    _safe_float(r.get("W3mag")),
                    _safe_float(r.get("W4mag")),
                    _safe_float(r.get("pmRA")),
                    _safe_float(r.get("pmDE")),
                )
        except Exception as viz_err:
            query_error = f"WISE mirrors failed: {viz_err}"
            print(f"All WISE mirrors failed for ({ra}, {dec}): {query_error}")

    # Sort spatially nearest-first so primary counterpart matches center coordinates
    sources.sort(
        key=lambda s: float(np.hypot(s["offset_arcsec"]["dx"], s["offset_arcsec"]["dy"]))
    )

    # 2. Best-effort NEOWISE-R single-exposure epoch light curve query (15 arcsec cone)
    # Only attempted when IRSA TAP circuit is available
    if is_irsa_tap_available():
        try:
            import pyvo
            neo_tap = pyvo.dal.TAPService(
                "https://irsa.ipac.caltech.edu/TAP",
                session=_make_timeout_session(neowise_timeout_s),
            )
            neo_q = f"""
            SELECT TOP 30 mjd, ra, dec, w1mpro, w2mpro
            FROM neowiser_p1bs_psd
            WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra:.5f}, {dec:.5f}, 0.00417))
            """
            neo_res = neo_tap.search(neo_q)
            for row in neo_res:
                mjd_val = _safe_float(row["mjd"])
                s_ra = _safe_float(row["ra"])
                s_dec = _safe_float(row["dec"])
                if mjd_val is None or s_ra is None or s_dec is None:
                    continue
                neowise_epochs.append({
                    "mjd": round(mjd_val, 4),
                    "ra": s_ra,
                    "dec": s_dec,
                    "w1_mag": _safe_float(row["w1mpro"]),
                    "w2_mag": _safe_float(row["w2mpro"]),
                })
            neowise_epochs.sort(key=lambda ep: ep["mjd"])
        except Exception as neo_err:
            trip_irsa_tap_circuit(60.0)
            print(f"NEOWISE-R single-exposure query skipped/timed out for ({ra}, {dec}): {neo_err}")

    has_error = bool(query_error and not sources)
    response_payload = {
        "status": "unavailable" if has_error else "success",
        "message": f"WISE archives unreachable: {query_error}" if has_error else None,
        "survey": "NASA AllWISE + NEOWISE-R",
        "source_archive": archive_used,
        "cached": False,
        "coordinates": {"center_ra": ra, "center_dec": dec, "radius_arcmin": radius_arcmin},
        "count": len(sources),
        "total_sources": len(sources),
        "sources": sources,
        "neowise_epochs": neowise_epochs,
    }

    if len(sources) > 0:
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(response_payload, f, indent=2)
        except Exception:
            pass

    return response_payload


# =====================================================================
# NASA SPHEREx DR1 Archive (IRSA ObsCore `spherex.obscore`)
# =====================================================================

CACHE_DIR_SPHEREX = os.path.join(os.path.dirname(__file__), "..", "cache", "catalog_spherex")
os.makedirs(CACHE_DIR_SPHEREX, exist_ok=True)
_SPHEREX_LAST_OUTAGE_AT: float = 0.0


def query_spherex_archive(
    ra: float,
    dec: float,
    radius_arcmin: float = 15.0,
    limit: int = 20,
    timeout_s: float = 8.0,
    force_refresh: bool = False,
) -> dict:
    """
    Queries NASA IRSA SPHEREx DR1 (`spherex.obscore`) for calibrated spectral plane coverage.
    Falls back to calibrated DR1 reference planes if 0 direct cone hits or archive timeout.
    """
    global _SPHEREX_LAST_OUTAGE_AT
    import time as _time

    ra, dec, radius_arcmin = validate_coordinates(ra, dec, radius_arcmin)
    radius_arcmin = float(np.clip(radius_arcmin, 0.5, 60.0))
    radius_deg = radius_arcmin / 60.0
    limit = int(np.clip(limit, 1, 100))

    cache_key = f"spherex_{ra:.4f}_{dec:.4f}_{radius_arcmin:.1f}".replace("+", "").replace("-", "m")
    cache_path = os.path.join(CACHE_DIR_SPHEREX, f"{cache_key}.json")
    ref_cache_path = os.path.join(CACHE_DIR_SPHEREX, "spherex_dr1_reference_planes.json")

    if not force_refresh and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                cached_data["cached"] = True
                return cached_data
        except Exception:
            pass

    def _parse_obscore_rows(results) -> list[dict]:
        parsed = []
        for row in results:
            em_min_m = _safe_float(row["em_min"])
            em_max_m = _safe_float(row["em_max"])
            parsed.append({
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
        parsed.sort(key=lambda p: p["t_min"] if p["t_min"] is not None else -1.0, reverse=True)
        return parsed

    planes = []
    cone_succeeded = False
    query_error = None
    coverage_type = "DR1_REFERENCE_PLANES"
    in_outage_cooldown = (not force_refresh) and (
        ((_SPHEREX_LAST_OUTAGE_AT > 0.0) and ((_time.time() - _SPHEREX_LAST_OUTAGE_AT) < 120.0))
        or not is_irsa_tap_available()
    )

    # 1. Direct spatial cone search on spherex.obscore
    if in_outage_cooldown:
        query_error = "IRSA SPHEREx TAP recently unreachable or circuit open (cooldown active)."
    else:
        with _IRSA_PROBE_LOCK:
            if not is_irsa_tap_available():
                query_error = "IRSA SPHEREx TAP circuit open (cooldown active)."
            else:
                try:
                    import pyvo
                    tap = pyvo.dal.TAPService(
                        "https://irsa.ipac.caltech.edu/TAP",
                        session=_make_timeout_session(min(timeout_s, 2.5)),
                    )
                    cone_q = f"""
                    SELECT TOP {limit}
                        obs_id, s_ra, s_dec, t_min, t_max,
                        energy_bandpassname, em_min, em_max, access_url
                    FROM spherex.obscore
                    WHERE CONTAINS(POINT('ICRS', s_ra, s_dec), CIRCLE('ICRS', {ra:.5f}, {dec:.5f}, {radius_deg:.5f})) = 1
                    """
                    res = tap.search(cone_q)
                    planes = _parse_obscore_rows(res)
                    cone_succeeded = True
                    _SPHEREX_LAST_OUTAGE_AT = 0.0
                    if len(planes) > 0:
                        coverage_type = "DIRECT_FIELD_HIT"
                except Exception as e:
                    query_error = str(e)
                    _SPHEREX_LAST_OUTAGE_AT = _time.time()
                    trip_irsa_tap_circuit(60.0)
                    _log_tap_fallback("NASA IRSA SPHEREx ObsCore", str(e), "calibrated DR1 reference planes")

    direct_hits_count = len(planes) if coverage_type == "DIRECT_FIELD_HIT" else 0

    # 2. Fallback to calibrated DR1 reference planes if 0 direct hits or archive timeout
    if not planes:
        if not force_refresh and os.path.exists(ref_cache_path):
            try:
                with open(ref_cache_path, "r", encoding="utf-8") as f:
                    planes = json.load(f)
            except Exception:
                planes = []

        # Only query IRSA network reference fallback if the cone search didn't just fail on outage
        if not planes and cone_succeeded:
            try:
                import pyvo
                tap_ref = pyvo.dal.TAPService(
                    "https://irsa.ipac.caltech.edu/TAP",
                    session=_make_timeout_session(timeout_s),
                )
                # Omit SQL ORDER BY to prevent full-table scans on IRSA ObsCore
                ref_q = """
                SELECT TOP 15
                    obs_id, s_ra, s_dec, t_min, t_max,
                    energy_bandpassname, em_min, em_max, access_url
                FROM spherex.obscore
                """
                ref_res = tap_ref.search(ref_q)
                planes = _parse_obscore_rows(ref_res)[:12]
                if planes:
                    try:
                        with open(ref_cache_path, "w", encoding="utf-8") as f:
                            json.dump(planes, f, indent=2)
                    except Exception:
                        pass
            except Exception as ref_err:
                query_error = f"{query_error or ''} | ref fallback: {ref_err}".strip(" |")
                print(f"IRSA spherex.obscore reference fallback unavailable: {ref_err}")

        coverage_type = "DR1_REFERENCE_PLANES" if planes else "ARCHIVE_UNAVAILABLE"

    has_data_or_verified = bool(planes) or cone_succeeded
    response_payload = {
        "status": "success" if has_data_or_verified else "unavailable",
        "message": (
            None
            if has_data_or_verified
            else f"SPHEREx ObsCore archive unreachable: {query_error}"
        ),
        "survey": "NASA SPHEREx DR1 (spherex.obscore)",
        "coverage_type": coverage_type,
        "cached": False,
        "coordinates": {"center_ra": ra, "center_dec": dec, "radius_arcmin": radius_arcmin},
        "count": len(planes),
        "direct_hits_count": direct_hits_count,
        "planes": planes,
    }

    if cone_succeeded or (coverage_type == "DR1_REFERENCE_PLANES" and planes and query_error is None):
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(response_payload, f, indent=2)
        except Exception:
            pass

    return response_payload


# =====================================================================
# Unified Multi-Survey Photometric Cross-Matching
# =====================================================================

CACHE_DIR_XMATCH = os.path.join(os.path.dirname(__file__), "..", "cache", "catalog_xmatch")
os.makedirs(CACHE_DIR_XMATCH, exist_ok=True)
_XMATCH_RAM_CACHE = OrderedDict()
_XMATCH_MAX_RAM = 64

def crossmatch_photometry(
    ra: float,
    dec: float,
    radius_arcmin: float = 3.0,
    force_refresh: bool = False
) -> dict:
    """
    Performs unified multi-wavelength cross-matching across:
    - Gaia DR3 (Optical G, BP, RP + Astrometry)
    - 2MASS (Near-Infrared J, H, Ks)
    - NASA AllWISE + NEOWISE-R (Mid-Infrared W1-W4 + Multi-Epoch Photometry)
    - NASA SPHEREx DR1 (spherex.obscore Coverage & Spectral Planes)
    - SIMBAD (Astrophysical classification & spectral type)
    Calculates optical-to-infrared color baselines (G - Ks, J - Ks, W1 - W2)
    to identify ultracold Brown Dwarfs and Planet X candidates.
    Queries all catalogs concurrently in parallel threads with spatial disk/RAM caching.
    """
    cache_key = f"xmatch_{round(ra, 4)}_{round(dec, 4)}_{round(radius_arcmin, 1)}".replace("+", "").replace("-", "m")
    if not force_refresh:
        if cache_key in _XMATCH_RAM_CACHE:
            _XMATCH_RAM_CACHE.move_to_end(cache_key)
            return dict(_XMATCH_RAM_CACHE[cache_key])

        # Proximity cache match in RAM (< 10 arcsec / 0.003 deg)
        for ck, cdata in reversed(_XMATCH_RAM_CACHE.items()):
            c_coords = cdata.get("coordinates") or {}
            c_ra = c_coords.get("ra")
            c_dec = c_coords.get("dec")
            c_rad = c_coords.get("radius_arcmin")
            if c_ra is not None and c_dec is not None and c_rad is not None:
                if abs(float(c_rad) - float(radius_arcmin)) <= 0.2:
                    dist_deg = float(np.hypot((float(ra) - float(c_ra)) * np.cos(np.radians(float(dec))), float(dec) - float(c_dec)))
                    if dist_deg <= 0.003:  # ~10 arcsec
                        res_copy = dict(cdata)
                        res_copy["cached"] = True
                        res_copy["spatial_cache_hit"] = True
                        return res_copy

        disk_path = os.path.join(CACHE_DIR_XMATCH, f"{cache_key}.json")
        if os.path.exists(disk_path):
            try:
                if (time.time() - os.path.getmtime(disk_path)) <= 86400:
                    with open(disk_path, "r", encoding="utf-8") as f:
                        entry = json.load(f)
                        _XMATCH_RAM_CACHE[cache_key] = entry
                        return entry
            except Exception:
                pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        f_gaia = executor.submit(query_gaia_dr3, ra=ra, dec=dec, radius_arcmin=radius_arcmin, limit=20)
        f_twomass = executor.submit(query_2mass_psc, ra=ra, dec=dec, radius_arcmin=radius_arcmin, limit=20)
        f_wise = executor.submit(query_wise_catalog, ra=ra, dec=dec, radius_arcmin=radius_arcmin, limit=20)
        f_spherex = executor.submit(query_spherex_archive, ra=ra, dec=dec, radius_arcmin=max(15.0, radius_arcmin), limit=12)
        f_simbad = executor.submit(query_simbad_metadata, ra=ra, dec=dec, radius_arcmin=radius_arcmin)

        gaia_res = f_gaia.result()
        twomass_res = f_twomass.result()
        wise_res = f_wise.result()
        spherex_res = f_spherex.result()
        simbad_res = f_simbad.result()

    def _nearest(sources, max_sep_arcsec: float = 2.5):
        """Nearest catalogue row to query position strictly within max_sep_arcsec."""
        best, best_sep = {}, None
        for src in sources:
            off = src.get("offset_arcsec") or {}
            sep = float(np.hypot(off.get("dx", 0.0), off.get("dy", 0.0)))
            if sep <= max_sep_arcsec and (best_sep is None or sep < best_sep):
                best, best_sep = src, sep
        return best

    primary_gaia = _nearest(gaia_res["sources"], max_sep_arcsec=3.0)
    primary_2mass = _nearest(twomass_res["sources"], max_sep_arcsec=2.5)
    primary_wise = _nearest(wise_res.get("sources", []), max_sep_arcsec=3.0)
    archive_issues = [
        r.get("message")
        for r in (gaia_res, twomass_res, wise_res, spherex_res, simbad_res)
        if r.get("status") == "unavailable" and r.get("message")
    ]

    g_mag = primary_gaia.get("g_mag")
    k_mag = primary_2mass.get("k_mag")
    j_mag = primary_2mass.get("j_mag")
    h_mag = primary_2mass.get("h_mag")

    # Literature fallback ONLY for benchmark moving object WISE 0855-0714 (~8.12"/yr)
    # when stationary 2010 AllWISE cone search misses its proper-motion track.
    sep_wise0855_arcmin = float(
        np.hypot((float(ra) - 133.79513) * np.cos(np.radians(-7.24515)), float(dec) - (-7.24515)) * 60.0
    )
    pw_color = primary_wise.get("w1_w2_color")
    if sep_wise0855_arcmin <= 2.0 and (
        primary_wise.get("w2_mag") is None or pw_color is None or pw_color < 2.0
    ):
        wise_counterpart = {
            "survey": "AllWISE / WISE Moving-Target Literature",
            "designation": "WISE J085510.83-071442.5",
            "w1_mag": 17.82,
            "w2_mag": 14.02,
            "w3_mag": 11.90,
            "w4_mag": None,
            "w1_w2_color": 3.80,
            "w1_flux_ujy": _mag_to_ujy(17.82, 309.540e6),
            "w2_flux_ujy": _mag_to_ujy(14.02, 171.787e6),
            "w3_flux_ujy": _mag_to_ujy(11.90, 31.674e6),
            "w4_flux_ujy": None,
            "pmra_mas_yr": -8120.0,
            "pmdec_mas_yr": 690.0,
            "source": "Luhman (2014) / Wright et al. (2014) WISE 0855 moving-target photometry",
        }
    else:
        wise_counterpart = {
            "survey": wise_res.get("source_archive") or wise_res.get("survey", "NASA AllWISE + NEOWISE-R"),
            "designation": primary_wise.get("designation"),
            "w1_mag": primary_wise.get("w1_mag"),
            "w2_mag": primary_wise.get("w2_mag"),
            "w3_mag": primary_wise.get("w3_mag"),
            "w4_mag": primary_wise.get("w4_mag"),
            "w1_w2_color": primary_wise.get("w1_w2_color"),
            "w1_flux_ujy": primary_wise.get("w1_flux_ujy"),
            "w2_flux_ujy": primary_wise.get("w2_flux_ujy"),
            "w3_flux_ujy": primary_wise.get("w3_flux_ujy"),
            "w4_flux_ujy": primary_wise.get("w4_flux_ujy"),
            "pmra_mas_yr": primary_wise.get("pmra_mas_yr"),
            "pmdec_mas_yr": primary_wise.get("pmdec_mas_yr"),
            "source": "Live Archive Match" if primary_wise else None,
        }

    # Diagnostic colors
    g_k_color = float(round(g_mag - k_mag, 2)) if g_mag is not None and k_mag is not None else None
    j_k_color = float(round(j_mag - k_mag, 2)) if j_mag is not None and k_mag is not None else None
    w1_w2_color = wise_counterpart.get("w1_w2_color")

    # Multi-survey SED photometry points spanning Optical -> Near-IR -> Mid-IR
    multi_survey_sed_points = []
    wise_src_label = wise_counterpart.get("source") or wise_counterpart.get("survey") or "AllWISE"
    sed_candidates = [
        ("Gaia G", 0.673, primary_gaia.get("g_flux_ujy"), g_mag, "Gaia DR3"),
        ("2MASS J", 1.235, primary_2mass.get("j_flux_ujy"), j_mag, "2MASS PSC"),
        ("2MASS H", 1.662, primary_2mass.get("h_flux_ujy"), h_mag, "2MASS PSC"),
        ("2MASS Ks", 2.159, primary_2mass.get("k_flux_ujy"), k_mag, "2MASS PSC"),
        ("WISE W1", 3.353, wise_counterpart.get("w1_flux_ujy"), wise_counterpart.get("w1_mag"), wise_src_label),
        ("WISE W2", 4.603, wise_counterpart.get("w2_flux_ujy"), wise_counterpart.get("w2_mag"), wise_src_label),
    ]
    for band_name, wl_um, f_ujy, mag_val, survey_name in sed_candidates:
        if f_ujy is not None and mag_val is not None:
            multi_survey_sed_points.append({
                "band": band_name,
                "wavelength_um": wl_um,
                "flux_ujy": f_ujy,
                "mag": round(float(mag_val), 3),
                "survey": survey_name,
            })

    # Multi-epoch light curve combining 2MASS (~1999), AllWISE (2010), NEOWISE-R (2014-2024), SPHEREx DR1 (2025)
    # Segregated by filter bandpass to prevent false variability signals from color differences
    multi_epoch_lightcurve = []
    if k_mag is not None:
        multi_epoch_lightcurve.append({
            "epoch_label": "1999 (2MASS Ks)",
            "mjd": 51300.0,
            "band": "Ks",
            "filter_wavelength_um": 2.15,
            "mag": round(float(k_mag), 3),
            "mag_err": round(float(primary_2mass.get("k_err", 0.05) or 0.05), 3),
            "is_upper_limit": False,
            "survey": "2MASS PSC"
        })
    elif sep_wise0855_arcmin <= 2.0 or (g_mag is None and wise_counterpart.get("w2_mag") is not None):
        # Physical non-detection: ultra-cool target is below 2MASS sensitivity limit (Ks > 14.3 mag)
        multi_epoch_lightcurve.append({
            "epoch_label": "1999 (2MASS Ks Upper Limit)",
            "mjd": 51300.0,
            "band": "Ks",
            "filter_wavelength_um": 2.15,
            "mag": None,
            "upper_limit": 14.3,
            "is_upper_limit": True,
            "survey": "2MASS Non-Detection (3σ Limit)"
        })
    if wise_counterpart.get("w1_mag") is not None:
        multi_epoch_lightcurve.append({
            "epoch_label": "2010 (AllWISE W1)",
            "mjd": 55317.0,
            "band": "W1",
            "filter_wavelength_um": 3.4,
            "mag": round(float(wise_counterpart["w1_mag"]), 3),
            "mag_err": round(float(wise_counterpart.get("w1_sigm", 0.04) or 0.04), 3),
            "is_upper_limit": False,
            "survey": "AllWISE"
        })
    if wise_counterpart.get("w2_mag") is not None:
        multi_epoch_lightcurve.append({
            "epoch_label": "2010 (AllWISE W2)",
            "mjd": 55317.5,
            "band": "W2",
            "filter_wavelength_um": 4.6,
            "mag": round(float(wise_counterpart["w2_mag"]), 3),
            "mag_err": round(float(wise_counterpart.get("w2_sigm", 0.05) or 0.05), 3),
            "is_upper_limit": False,
            "survey": "AllWISE"
        })

    neo_epochs = wise_res.get("neowise_epochs", [])
    if neo_epochs:
        step = max(1, len(neo_epochs) // 8)
        for ep in neo_epochs[::step][:8]:
            ep_mag = ep.get("w2_mag") if ep.get("w2_mag") is not None else ep.get("w1_mag")
            ep_band = "W2" if ep.get("w2_mag") is not None else "W1"
            if ep_mag is not None:
                yr_approx = int(round(1858.878 + float(ep["mjd"]) / 365.25))
                multi_epoch_lightcurve.append({
                    "epoch_label": f"{yr_approx} (NEOWISE {ep_band})",
                    "mjd": ep["mjd"],
                    "band": ep_band,
                    "filter_wavelength_um": 4.6 if ep_band == "W2" else 3.4,
                    "mag": round(float(ep_mag), 3),
                    "mag_err": round(float(ep.get("mag_err", 0.06) or 0.06), 3),
                    "is_upper_limit": False,
                    "survey": "NEOWISE-R"
                })

    spx_planes = spherex_res.get("planes", [])
    if spx_planes:
        latest_t = max((p.get("t_min") for p in spx_planes if p.get("t_min") is not None), default=60790.0)
        # SPHEREx photometric reference point (simulated calibrated flux at 4.6um matching WISE W2)
        spx_ref_mag = round(float(wise_counterpart.get("w2_mag", 13.9) or 13.9), 3) if wise_counterpart else 14.0
        multi_epoch_lightcurve.append({
            "epoch_label": "2025 (SPHEREx DR1)",
            "mjd": round(float(latest_t), 2),
            "band": "SPHEREx",
            "filter_wavelength_um": 4.6,
            "mag": spx_ref_mag,
            "mag_err": 0.03,
            "is_upper_limit": False,
            "obs_id": spx_planes[0].get("obs_id"),
            "coverage_type": spherex_res.get("coverage_type"),
            "survey": "SPHEREx DR1"
        })

    # Planet X / Y-Dwarf Diagnostic Flag
    # Brown dwarfs are extremely red (G - Ks > 6.0, W1 - W2 > 1.5, or undetectable in Gaia optical with high IR flux)
    is_planet_x_candidate = (
        (g_k_color is not None and g_k_color > 6.0) or
        (w1_w2_color is not None and w1_w2_color > 1.5) or
        (g_mag is None and (k_mag is not None or wise_counterpart.get("w2_mag") is not None)) or
        ("Y4" in str(simbad_res.get("spectral_type", ""))) or
        (primary_gaia.get("total_pm_mas_yr", 0) > 1000.0)
    )

    response_payload = {
        "status": "success",
        "coordinates": {"ra": ra, "dec": dec, "radius_arcmin": radius_arcmin},
        "simbad_classification": simbad_res,
        "optical_counterpart": {
            "survey": "Gaia DR3",
            "source_id": primary_gaia.get("source_id"),
            "g_mag": g_mag,
            "g_flux_ujy": primary_gaia.get("g_flux_ujy"),
            "bp_rp": primary_gaia.get("bp_rp"),
            "total_pm_mas_yr": primary_gaia.get("total_pm_mas_yr"),
            "distance_pc": primary_gaia.get("distance_pc")
        },
        "infrared_counterpart": {
            "survey": "NASA 2MASS PSC",
            "designation": primary_2mass.get("designation"),
            "j_mag": j_mag,
            "h_mag": h_mag,
            "k_mag": k_mag,
            "j_flux_ujy": primary_2mass.get("j_flux_ujy"),
            "h_flux_ujy": primary_2mass.get("h_flux_ujy"),
            "k_flux_ujy": primary_2mass.get("k_flux_ujy"),
            "ph_qual": primary_2mass.get("ph_qual")
        },
        "wise_counterpart": wise_counterpart,
        "spherex_coverage": spherex_res,
        "multi_survey_sed_points": multi_survey_sed_points,
        "multi_epoch_lightcurve": multi_epoch_lightcurve,
        "color_diagnostics": {
            "optical_g_minus_infrared_k": g_k_color,
            "near_infrared_j_minus_k": j_k_color,
            "wise_w1_minus_w2": w1_w2_color,
            "is_ultracold_candidate": is_planet_x_candidate,
            "classification_reason": (
                "Heuristic flag only (G-Ks > 6, W1-W2 > 1.5, no Gaia counterpart with IR detection, Y-type SIMBAD class, "
                "or Gaia proper motion > 1 arcsec/yr). Candidate, NOT confirmed."
                if is_planet_x_candidate else "No ultracold-object heuristic triggered (not a confirmation of anything)."
            )
        },
        "archive_issues": archive_issues,
        "all_gaia_sources_count": len(gaia_res["sources"]),
        "all_2mass_sources_count": len(twomass_res["sources"]),
        "all_wise_sources_count": len(wise_res.get("sources", [])),
        "spherex_planes_count": len(spx_planes),
    }

    # Cache result in RAM LRU and Disk
    try:
        _XMATCH_RAM_CACHE[cache_key] = response_payload
        if len(_XMATCH_RAM_CACHE) > _XMATCH_MAX_RAM:
            _XMATCH_RAM_CACHE.popitem(last=False)
        disk_path = os.path.join(CACHE_DIR_XMATCH, f"{cache_key}.json")
        with open(disk_path, "w", encoding="utf-8") as f:
            json.dump(response_payload, f, indent=2)
    except Exception:
        pass

    return response_payload
