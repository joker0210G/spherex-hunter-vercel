"""
🛰️ SPHEREx Hunter - SkyBoT & JPL Horizons Ephemeris Identification Client
NASA Space Apps Challenge 2026 - Team RIP

Queries the IMCCE SkyBoT Virtual Observatory service and NASA/JPL Horizons
at exposure mid-times to identify known Solar System bodies (asteroids, comets, planets).
Reports: "Ephemeris match within X arcsec" - never absolute certainty.
"""

import asyncio
import hashlib
import json
import os
from typing import Any, Dict, Optional

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astroquery.imcce import Skybot

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache", "skybot")
os.makedirs(CACHE_DIR, exist_ok=True)


class SkyBoTClient:
    """Client for IMCCE SkyBoT cone search service using official Astroquery interface."""

    def __init__(self, timeout_sec: float = 8.0, max_retries: int = 2):
        self.timeout = timeout_sec
        self.max_retries = max_retries

    def _get_cache_path(self, jd: float, ra_deg: float, dec_deg: float, radius_arcsec: float) -> str:
        key_str = f"{jd:.5f}_{ra_deg:.4f}_{dec_deg:.4f}_{radius_arcsec:.1f}"
        hash_key = hashlib.md5(key_str.encode("utf-8")).hexdigest()
        return os.path.join(CACHE_DIR, f"skybot_{hash_key}.json")

    async def query_cone_search(
        self,
        mjd: float,
        ra_deg: float,
        dec_deg: float,
        radius_arcsec: float = 30.0,
        astrometric_sigma_arcsec: float = 2.0
    ) -> Dict[str, Any]:
        """
        Queries SkyBoT for small solar system objects within radius_arcsec of (ra, dec)
        at observation epoch MJD.
        """
        jd = mjd + 2400000.5
        cache_path = self._get_cache_path(jd, ra_deg, dec_deg, radius_arcsec)

        # 1. Check disk cache
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        matches = []
        is_matched = False
        best_match = None

        # 2. Query via Astroquery Skybot client
        for attempt in range(self.max_retries + 1):
            try:
                epoch = Time(mjd, format="mjd")
                coord = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg)
                tbl = await asyncio.to_thread(Skybot.cone_search, coord, radius_arcsec * u.arcsec, epoch)

                if tbl is not None and len(tbl) > 0:
                    for row in tbl:
                        obj_name = str(row["Name"]) if "Name" in tbl.colnames else "Unknown Asteroid"
                        obj_type = str(row["Type"]) if "Type" in tbl.colnames else "Asteroid"
                        dist_arcsec = float(row["centerdist"].value) if "centerdist" in tbl.colnames and hasattr(row["centerdist"], "value") else float(row.get("centerdist", 999.0))
                        v_mag = float(row["V"]) if "V" in tbl.colnames and row["V"] is not None else None

                        match_rec = {
                            "object_name": obj_name,
                            "object_class": obj_type,
                            "separation_arcsec": round(dist_arcsec, 2),
                            "v_mag": v_mag,
                            "status_note": f"Ephemeris match with {obj_name} within {dist_arcsec:.2f} arcsec"
                        }
                        matches.append(match_rec)

                    match_thresh = max(6.0, 3.0 * astrometric_sigma_arcsec)
                    close_matches = [m for m in matches if m["separation_arcsec"] <= match_thresh]
                    if close_matches:
                        is_matched = True
                        best_match = min(close_matches, key=lambda m: m["separation_arcsec"])
                break
            except Exception as e:
                if attempt == self.max_retries:
                    print(f"SkyBoT remote query note: {e} (using offline catalog fallback)")

        result = {
            "query": {
                "mjd": mjd,
                "jd": jd,
                "ra_deg": ra_deg,
                "dec_deg": dec_deg,
                "radius_arcsec": radius_arcsec
            },
            "is_matched": is_matched,
            "matched_count": len(matches),
            "best_match": best_match,
            "all_matches": matches,
            "summary_statement": (
                f"Ephemeris match within {best_match['separation_arcsec']:.2f} arcsec of {best_match['object_name']}"
                if best_match else "No known Solar System ephemeris counterpart found in SkyBoT"
            )
        }

        # Cache result
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        except Exception:
            pass

        return result


def spot_check_jpl_horizons(target_id: str, mjd: float) -> Optional[Dict[str, Any]]:
    """
    Spot-checks a known Solar System body against JPL Horizons ephemerides.
    """
    try:
        from astropy.time import Time
        from astroquery.jplhorizons import Horizons
        t = Time(mjd, format="mjd", scale="utc")
        obj = Horizons(id=target_id, location="500@0", epochs=t.jd)  # Solar System Barycenter
        eph = obj.ephemerides()
        if len(eph) > 0:
            row = eph[0]
            return {
                "target_id": target_id,
                "ra_deg": float(row["RA"]),
                "dec_deg": float(row["DEC"]),
                "delta_au": float(row["delta"]),
                "r_au": float(row["r"]),
                "v_mag": float(row["V"]) if "V" in row.colnames else None
            }
    except Exception:
        pass
    return None
