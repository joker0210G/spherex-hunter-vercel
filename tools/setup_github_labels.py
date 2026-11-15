#!/usr/bin/env python3
"""
🏷️ Team RIP: GitHub Labels Provisioner
NASA Space Apps Challenge 2026 - Planet X & SPHEREx
Repository: joker0210G/spherex-hunter

Sets up the multi-track label taxonomy for Team RIP across:
- Tracks: Feature/Backend, Web/Frontend, UI/UX/Pitch, Image Math, System Lead
- Teammate Roles: jokerodu, darkodu, coolodu, iceodu, astrodu
- Asymmetric Resource Profiles: token-heavy, compute-heavy, standard
- Status & Verification: needs-refinement, ready-for-dev, in-review, nasa-verified
"""

import json
import os
import urllib.error
import urllib.request

REPO = "joker0210G/spherex-hunter"
API_BASE = f"https://api.github.com/repos/{REPO}/labels"

LABELS = [
    # 🎯 Tracks
    {"name": "track:feature-backend", "color": "0052CC", "description": "Backend API, NASA IRSA queries, TAP astrometry, FITS cutouts"},
    {"name": "track:web-frontend",    "color": "1D76DB", "description": "60 FPS Canvas viewport, WebGL, Aladin Lite, WiseView, UI controls"},
    {"name": "track:uiux-pitch",       "color": "D93F0B", "description": "Citizen Science UX, tutorial, slide deck, video pitch script"},
    {"name": "track:image-math",      "color": "5319E7", "description": "Alard-Lupton difference imaging, PSF convolution, 102-band SED"},
    {"name": "track:system-lead",     "color": "0E8A16", "description": "Architecture, Golden Verification Suite, PR merge reviews"},

    # 👥 Teammate Roles
    {"name": "role:jokerodu", "color": "006B75", "description": "Owned by jokerodu (main branch - System Lead)"},
    {"name": "role:darkodu",  "color": "5319E7", "description": "Owned by darkodu (darkodu/astro-backend)"},
    {"name": "role:coolodu",  "color": "1D76DB", "description": "Owned by coolodu (coolodu/web-frontend - Paid Pro Powerhouse)"},
    {"name": "role:iceodu",   "color": "0052CC", "description": "Owned by iceodu (iceodu/image-math-ai - Compute Engine)"},
    {"name": "role:astrodu",  "color": "D93F0B", "description": "Owned by astrodu (astrodu/ui-story-pitch - Story Lead)"},

    # ⚡ Asymmetrical Resource Matrix
    {"name": "resource:token-heavy",   "color": "FBCA04", "description": "Requires Paid Pro / Pro Gemini token quota for large reasoning"},
    {"name": "resource:compute-heavy", "color": "E99695", "description": "Requires high-spec local hardware (CPU/GPU/RAM) for matrix math"},
    {"name": "resource:hybrid",        "color": "D4C5F9", "description": "Both token-heavy and compute-heavy task"},
    {"name": "resource:standard",      "color": "C2E0C6", "description": "Standard task executable on standard laptop & model"},

    # 🚦 Lifecycle & NASA Verification
    {"name": "status:needs-refinement", "color": "BFDADC", "description": "Draft task requiring spec or acceptance criteria refinement"},
    {"name": "status:ready-for-dev",    "color": "0E8A16", "description": "Refined and ready for teammate to claim on their branch"},
    {"name": "status:in-review",        "color": "FBCA04", "description": "PR submitted; awaiting Golden Test Suite / Lead verification"},
    {"name": "status:nasa-verified",    "color": "238636", "description": "100% verified against NASA Benchmarks and merged to main"},
]

def get_github_token():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        import subprocess
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n",
            capture_output=True,
            text=True,
            check=True
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def main():
    token = get_github_token()
    print(f"🛰️ Team RIP: Configuring Labels for {REPO}...")

    if not token:
        print("\n⚠️ Note: GITHUB_TOKEN environment variable is not set.")
        print("To push these labels directly to GitHub, run:")
        print("  $env:GITHUB_TOKEN = '<your_github_token>'")
        print("  python tools/setup_github_labels.py")
        print("\nListing label definitions that will be applied:")
        for l in LABELS:
            print(f"  - [{l['name']}] (#{l['color']}): {l['description']}")
        return

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "TeamRIP-Label-Sync"
    }

    success_count = 0
    for label in LABELS:
        payload = json.dumps(label).encode("utf-8")
        req = urllib.request.Request(API_BASE, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req):
                print(f"  ✅ Created label: {label['name']}")
                success_count += 1
        except urllib.error.HTTPError as e:
            if e.code == 422: # Already exists, update it via PATCH
                update_url = f"{API_BASE}/{urllib.parse.quote(label['name'])}"
                req_patch = urllib.request.Request(update_url, data=payload, headers=headers, method="PATCH")
                try:
                    with urllib.request.urlopen(req_patch):
                        print(f"  🔄 Updated existing label: {label['name']}")
                        success_count += 1
                except Exception as ex:
                    print(f"  ❌ Error updating {label['name']}: {ex}")
            else:
                print(f"  ❌ Failed creating {label['name']}: HTTP {e.code}")
        except Exception as e:
            print(f"  ❌ Network error for {label['name']}: {e}")

    print(f"\n🎉 Finished! Successfully synchronized {success_count}/{len(LABELS)} labels on {REPO}.")

if __name__ == "__main__":
    main()
