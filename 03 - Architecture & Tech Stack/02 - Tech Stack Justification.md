# 🛠️ Tech Stack & Architectural Decisions

| Layer | Selected Technology | Why Selected | Alternatives Considered |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | **React + Vite + TypeScript** | Instant HMR, zero-config build, ultra-fast for 48-hr hackathon, massive component ecosystem. | Next.js (slower build cycles), Plain HTML/JS (lacks state management). |
| **Styling & Icons** | **Tailwind CSS + Lucide Icons** | Rapid styling, dark mode presets, clean NASA dashboard aesthetic in minutes. | Bootstrap (dated look), Vanilla CSS (too slow). |
| **Astronomical Rendering** | **HTML5 2D Canvas + Aladin Lite v3** | Aladin Lite is the official CDS Strasbourg tool designed specifically for FITS/HiPS astronomical sky display. | Leaflet (general maps, lacks FITS WCS), Three.js (overkill for 2D cutouts). |
| **Backend API** | **Python FastAPI + Uvicorn** | Native async, automatic OpenAPI docs, seamless integration with Astropy scientific libraries. | Flask (synchronous, slower), Node.js (poor astronomical library support). |
| **Astronomy Core** | **Astropy + Astroquery + Reproject** | The gold standard NASA-backed library for coordinate transforms, WCS projections, and FITS math. | Custom math (error prone, unvalidated). |
| **Data Viz** | **Recharts** | Declarative, responsive React charting library for plotting the 102-band infrared spectrum. | Chart.js, D3 (steeper learning curve). |
| **Hosting & Deployment** | **Vercel (Frontend) + Render / Railway (Backend)** | Free tier, 1-click Git deployments, immediate public URL for NASA judges. | AWS / GCP (complex IAM setup). |
