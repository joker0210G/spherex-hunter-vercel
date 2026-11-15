# 👥 Citizen Science Best Practices (Backyard Worlds)

---

## 💡 Lessons from Backyard Worlds: Planet 9
The Zooniverse project **Backyard Worlds: Planet 9** launched in 2017 using infrared data from NASA's WISE mission. To date, citizen scientists have discovered:
- Over **3,000 brown dwarfs** (including some of the coldest known objects in the solar neighborhood).
- Thousands of moving asteroids and white dwarfs.

### Why was it so successful?
1. **Low Barrier to Entry:** No astronomy knowledge needed—volunteers simply watch a 4-frame animated gif (blink) and look for objects that move relative to static background stars.
2. **Immediate Satisfaction:** Volunteers feel direct ownership: when an object moves, they know they may be the first human to ever see it.
3. **Artifact Guidance:** Providing an "Is it real or an artifact?" visual guide directly inside the app prevents frustration (e.g. teaching volunteers what a cosmic ray strike or diffraction spike looks like).

---

## 🎨 Applying this to SPHEREx Hunter
- Include an **"Artifact Gallery"** tooltip in the UI:
  - **Real Object:** Moves consistently between epochs, appears in multiple infrared bands.
  - **Cosmic Ray:** Appears in only 1 epoch and exactly 1 pixel channel; sharp, unblurred edges.
  - **Optical Ghost / Reflection:** Large diffuse circular haze caused by bright off-axis stars.

---

## 🔗 Technical Tools & Deep-Linking Architecture
- **[[WISEVIEW_BYW_TOOLS_SITEMAP]]** — Complete architectural site map and 30+ parameter URL hash specification for Dan Caselden's WiseView (`byw.tools/wiseview`), including difference imaging, Asinh stretch parameters, and synthetic source injection.
- **[[NASA_AND_PARTNER_DATA_PORTALS]]** — Cross-survey integration protocols with NASA IRSA, MAST, and CADC.
