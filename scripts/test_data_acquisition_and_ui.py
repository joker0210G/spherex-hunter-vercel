"""
Diagnostic script for SPHEREx Hunter Data Acquisition & UI Endpoints.
Probes boundaries, error handling, network timeouts, edge cases, and response schemas.
"""
import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def get(path):
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SPHEREx-Hunter-Audit"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()
            if "application/json" in content_type:
                return resp.status, json.loads(raw.decode("utf-8"))
            return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            body = raw.decode("utf-8", errors="ignore")
        return e.code, body
    except Exception as e:
        return 0, str(e)

def post(path, payload):
    url = f"{BASE_URL}{path}"
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "SPHEREx-Hunter-Audit"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            body = raw.decode("utf-8", errors="ignore")
        return e.code, body
    except Exception as e:
        return 0, str(e)

def main():
    results = []

    def check(name, status_code, body, expected_status=None, condition=None):
        ok = True
        notes = []
        if expected_status is not None and status_code != expected_status:
            ok = False
            notes.append(f"Expected status {expected_status}, got {status_code}")
        if condition is not None:
            cond_res = condition(status_code, body)
            if not cond_res:
                ok = False
                notes.append("Custom condition failed")
        results.append({
            "test": name,
            "status": status_code,
            "passed": ok,
            "notes": "; ".join(notes) if notes else "OK",
            "body_summary": str(body)[:200] if body else ""
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {name} -> HTTP {status_code} ({results[-1]['notes']})")

    print("--- 1. Testing Core Endpoints ---")
    status, body = get("/api/health")
    check("Health Check", status, body, 200, lambda s, b: b.get("status") in ["online", "healthy"])

    status, body = get("/api/bands")
    check("Bands API", status, body, 200, lambda s, b: b.get("status") == "success" and "arrays" in b and len(b["arrays"]) == 6)

    status, body = get("/api/resources_codex")
    check("Resources Codex", status, body, 200, lambda s, b: b.get("status") == "success" and "links" in b)

    print("\n--- 2. Testing Data Acquisition & Benchmarks ---")
    status, body = get("/api/cutout?ra=133.79513&dec=-7.24515&fov_arcmin=3.0&target=wise0855")
    check("Cutout WISE 0855 Benchmark", status, body, 200, lambda s, b: "epochs" in b and len(b["epochs"]) >= 2)

    status, body = get("/api/cutout?ra=269.4521&dec=4.6934&fov_arcmin=3.0&target=barnard")
    check("Cutout Barnard Benchmark", status, body, 200, lambda s, b: "epochs" in b)

    status, body = get("/api/spectrum?ra=133.79513&dec=-7.24515&target=wise0855")
    check("Spectrum WISE 0855", status, body, 200, lambda s, b: "bands" in b and len(b["bands"]) == 102)

    status, body = get("/api/gaia?ra=133.79513&dec=-7.24515&radius_arcsec=120")
    check("Gaia DR3 Cone Search", status, body, 200, lambda s, b: "sources" in b or "error" in b or "status" in b)

    status, body = get("/api/neossat?ra=133.79513&dec=-7.24515&radius_arcsec=180")
    check("NEOSSat / Asteroid Crossmatch", status, body, 200, lambda s, b: "tracked_asteroids" in b or "status" in b)

    status, body = get("/api/catalog/wise?ra=133.79513&dec=-7.24515&radius_arcsec=60")
    check("WISE Catalog Crossmatch", status, body, 200, lambda s, b: "sources" in b or "status" in b)

    status, body = get("/api/catalog/spherex?ra=133.79513&dec=-7.24515&radius_arcsec=60")
    check("SPHEREx Archive Catalog", status, body, 200, lambda s, b: "sources" in b or "status" in b)

    print("\n--- 3. Testing Coordinate Edge Cases & Validation ---")
    status, body = get("/api/cutout?ra=450.0&dec=0.0&fov_arcmin=3.0")
    check("Cutout RA > 360", status, body, 400)

    status, body = get("/api/cutout?ra=180.0&dec=95.0&fov_arcmin=3.0")
    check("Cutout Dec > 90", status, body, 400)

    status, body = get("/api/cutout?ra=180.0&dec=-95.0&fov_arcmin=3.0")
    check("Cutout Dec < -90", status, body, 400)

    status, body = get("/api/cutout?ra=-10.0&dec=0.0&fov_arcmin=3.0")
    check("Cutout RA < 0", status, body, 400)

    status, body = get("/api/cutout?ra=invalid&dec=0.0&fov_arcmin=3.0")
    check("Cutout Non-numeric RA", status, body, 400)

    print("\n--- 4. Testing Differencing & AI Co-Pilot ---")
    status, body = get("/api/source_discovery?ra=133.79513&dec=-7.24515&fov_arcmin=3.0&target=wise0855")
    check("Source Discovery", status, body, 200, lambda s, b: "candidates" in b)

    status, body = get("/api/ai/analyze?ra=133.79513&dec=-7.24515&target=wise0855")
    check("AI Analyze", status, body, 200, lambda s, b: b.get("status") == "success" and "plain_english_summary" in b)

    # Test POST with float coordinates (which previously failed with 422 before our fix)
    status, body = post("/api/ai/ask", {"question": "What is this target?", "ra": 133.79513, "dec": -7.24515, "target": "wise0855"})
    check("AI Ask (Float Coords)", status, body, 200, lambda s, b: "plain_english_answer" in b or "answer" in b)

    # Test POST with string sexagesimal coordinates
    status, body = post("/api/ai/ask", {"question": "Explain this object", "ra": "08h55m10.83s", "dec": "-07d14m42.5s", "target": "wise0855"})
    check("AI Ask (Sexagesimal String Coords)", status, body, 200, lambda s, b: "plain_english_answer" in b or "answer" in b)

    print("\n--- 5. Testing Static Files & UI Assets ---")
    status, body = get("/app/index.html")
    check("UI HTML Load", status, body, 200, lambda s, b: b"SPHEREx Hunter" in b or "SPHEREx Hunter" in str(b))

    status, body = get("/app/assets/logo.svg")
    check("UI Logo SVG", status, body, 200)

    with open("audit_results.json", "w") as f:
        json.dump(results, f, indent=2)

    failed = [r for r in results if not r["passed"]]
    print("\n==========================================")
    print(f"Total Tests: {len(results)}, Passed: {len(results)-len(failed)}, Failed: {len(failed)}")
    if failed:
        print("FAILURES:")
        for f in failed:
            print(f" - {f['test']}: {f['notes']} | status {f['status']}")
    print("==========================================")

if __name__ == "__main__":
    main()
