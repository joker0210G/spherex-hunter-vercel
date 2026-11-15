"""
Update demo_cache manifest and files with data_release and pipeline_version,
and refresh SHA-256 checksums.
"""

import hashlib
import json
import os

CACHE_DIR = "demo_cache"
DATA_RELEASE = "DR1"
PIPELINE_VERSION = "2.1.0"

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

manifest_path = os.path.join(CACHE_DIR, "manifest.json")
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

manifest["data_release"] = DATA_RELEASE
manifest["pipeline_version"] = PIPELINE_VERSION

# DR1 totals
dr1_counts = {
    "wise0855": 258,
    "barnard": 363,
    "epsindi": 459,
    "rwaur": 374,
    "rdraconis": 2542,
    "sample_leo": 262
}

for tid, tmeta in manifest["targets"].items():
    tmeta["data_release"] = DATA_RELEASE
    tmeta["pipeline_version"] = PIPELINE_VERSION
    if tid in dr1_counts:
        tmeta["public_exposures_total"] = dr1_counts[tid]

    tdir = os.path.join(CACHE_DIR, tid)
    if os.path.exists(tdir):
        for fname in os.listdir(tdir):
            fpath = os.path.join(tdir, fname)
            if fname.endswith(".json"):
                with open(fpath, "r", encoding="utf-8") as jf:
                    jdata = json.load(jf)

                # Update provenance if present or add
                if "provenance" not in jdata:
                    jdata["provenance"] = {}
                jdata["provenance"]["data_release"] = DATA_RELEASE
                jdata["provenance"]["pipeline_version"] = PIPELINE_VERSION

                if fname == "exposures.json" and tid in dr1_counts:
                    jdata["count_public_total"] = dr1_counts[tid]

                with open(fpath, "w", encoding="utf-8") as jf:
                    json.dump(jdata, jf, indent=2)

                # Update checksum
                if "checksums" in tmeta and fname in tmeta["checksums"]:
                    tmeta["checksums"][fname] = sha256_file(fpath)

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"Updated {manifest_path} and demo_cache files with data_release={DATA_RELEASE}, pipeline_version={PIPELINE_VERSION}")
