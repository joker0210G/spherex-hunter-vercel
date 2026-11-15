import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots")
ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\dfa12069-392c-4ec0-9bbe-8778d9f4fe65"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def capture_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        
        # Suppress onboarding modal on first load
        context.add_init_script("""
            localStorage.setItem('spherex_hunter_onboarding_completed', 'true');
            localStorage.setItem('spherex_onboarding_completed', 'true');
        """)
        
        page = context.new_page()

        print("Navigating to SPHEREx Hunter...")
        page.goto("http://localhost:8000/app/index.html#target=wise0855&mode=blink&frame=1", wait_until="networkidle")
        time.sleep(3)

        # Ensure onboarding modal is closed
        page.evaluate("""() => {
            const m = document.getElementById('onboardingModal');
            if (m) m.classList.add('hidden');
        }""")
        time.sleep(1)

        # 1. Primary Observatory View (WISE 0855 Blink Mode with True Data)
        path_obs = os.path.join(OUTPUT_DIR, "01_wise0855_observatory_blink.png")
        page.screenshot(path=path_obs)
        print(f"Captured: {path_obs}")

        path_obs_art = os.path.join(ARTIFACT_DIR, "01_wise0855_observatory_blink.png")
        with open(path_obs, "rb") as f_in, open(path_obs_art, "wb") as f_out:
            f_out.write(f_in.read())

        # 2. Open Validation & Mission Codex Modal
        print("Opening Validation modal...")
        page.evaluate("""() => {
            const btnVal = document.getElementById('btnOpenValidation');
            if (btnVal) {
                btnVal.click();
            } else {
                const modal = document.getElementById('missionCodexModal');
                if (modal) modal.classList.remove('hidden');
                const tab = document.getElementById('codexTabValidation');
                const panel = document.getElementById('codexPanelValidation');
                if (tab && panel && typeof switchCodexTab === 'function') switchCodexTab(tab, panel);
            }
        }""")
        time.sleep(2)

        path_val = os.path.join(OUTPUT_DIR, "02_scientific_validation_modal.png")
        page.screenshot(path=path_val)
        print(f"Captured: {path_val}")

        path_val_art = os.path.join(ARTIFACT_DIR, "02_scientific_validation_modal.png")
        with open(path_val, "rb") as f_in, open(path_val_art, "wb") as f_out:
            f_out.write(f_in.read())

        # Close validation modal
        page.evaluate("""() => {
            const modal = document.getElementById('missionCodexModal');
            if (modal) modal.classList.add('hidden');
        }""")
        time.sleep(1)

        # 3. Switch to Aladin Sky Mode
        print("Switching to Aladin Sky mode...")
        page.evaluate("""() => {
            const wsAladin = document.getElementById('wsAladin');
            if (wsAladin) wsAladin.click();
        }""")
        time.sleep(5)  # Allow Aladin Lite & HiPS tiles to load

        path_aladin = os.path.join(OUTPUT_DIR, "03_aladin_sky_hips_view.png")
        page.screenshot(path=path_aladin)
        print(f"Captured: {path_aladin}")

        path_aladin_art = os.path.join(ARTIFACT_DIR, "03_aladin_sky_hips_view.png")
        with open(path_aladin, "rb") as f_in, open(path_aladin_art, "wb") as f_out:
            f_out.write(f_in.read())

        browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    capture_screenshots()
