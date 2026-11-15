# 💻 Role: Full-Stack Web Lead
> **Mission:** Build a responsive, lightning-fast web tool that lets anyone input coordinates and blink multi-epoch images smoothly.

---

## 🎯 Key Deliverables
1. **Interactive Blink Viewer:**
   - HTML5 Canvas or WebGL player displaying Epoch 1 and Epoch 2 (and subsequent epochs).
   - Play/Pause toggle, loop speed slider (0.5 FPS to 10 FPS), Step Forward/Back buttons.
   - Contrast/Brightness adjustment sliders (asinh, square root, linear stretch).
2. **Coordinate & Preset Navigator:**
   - Quick search input supporting RA/Dec sexagesimal (`08h55m10.8s, -07d14m42.5s`) and decimal degrees (`133.795, -7.245`).
   - One-click buttons for the **5 NASA Benchmark Targets** (Barnard's Star, WISE 0855, etc.).
3. **URL Query Parameter Deep-Linking:**
   - Read & update URL query parameters on the fly:
     `?ra=133.7951&dec=-7.2451&fov=300&speed=3&diff=true`
   - Enables users to share a direct link to any candidate with friends or researchers.
4. **Interactive 102-Band Spectra Modal:**
   - Click anywhere on the image to open a popup chart (using Recharts or Chart.js) showing the 102-band infrared spectrum.

---

## 🛠️ Recommended Tech Stack
- **Framework:** React 18 / Next.js or Vite (lightweight and rapid for hackathons).
- **Styling:** Tailwind CSS + Lucide Icons + Shadcn/ui (dark mode astronomical theme).
- **Canvas / Mapping:** HTML5 2D Canvas or **Aladin Lite v3** (developed by CDS Strasbourg for astronomical FITS/HiPS display).
- **Charts:** Recharts (for the 102-band spectral plot).

---

## 🚀 Step-by-Step Setup Guide
```bash
# 1. Initialize Vite React project
npm create vite@latest spherex-hunter-ui -- --template react-ts
cd spherex-hunter-ui

# 2. Install dependencies
npm install lucide-react recharts clsx tailwindcss @radix-ui/react-slider

# 3. Setup Tailwind
npx tailwindcss init -p
```

---

## 🔗 Cross-Links
- System Architecture: [[01 - Architecture Overview]]
- Image Math Spec: [[03 - Image Processing & Blink Comparator Spec]]
- URL Spec: [[04 - API & URL Deep-Linking Specification]]
