# 🎞️ Image Processing & Blink Comparator Specification

---

## 1. Why the Blink Comparator Works
In 1930, Clyde Tombaugh discovered Pluto using a mechanical blink comparator that flipped rapidly between two photographic glass plates. The human brain contains specialized **motion-sensitive neurons (Area MT/V5)** that detect localized spatial shifts between alternating frames even when an object is faint.

Our digital web comparator replicates this digitally:
- Displays **Epoch 1** (e.g. SPHEREx Pass 1 / May 2025) for $t$ milliseconds.
- Displays **Epoch 2** (e.g. SPHEREx Pass 2 / Nov 2025) for $t$ milliseconds.
- Repeats cyclically. Stationary stars remain rock solid; moving bodies (Barnard's Star, WISE 0855) flicker back and forth!

---

## 2. Mathematical Alignment & Image Subtraction

### Sub-Pixel Registration
Before blinking or subtracting, images must share the identical **World Coordinate System (WCS)** projection matrix:
$$egin{pmatrix} x \ y \end{pmatrix} = \mathbf{WCS}_{	ext{epoch}} egin{pmatrix} lpha \ \delta \end{pmatrix}$$

We use `reproject.reproject_interp` to resample Epoch 2 onto the pixel grid of Epoch 1.

### Difference Imaging ($I_{	ext{diff}}$)
$$I_{	ext{diff}}(x, y) = I_{	ext{epoch } 2}(x, y) - lpha \cdot I_{	ext{epoch } 1}(x, y)$$
where $lpha$ is a scaling factor matching the median sky background:
$$lpha = rac{	ext{median}(I_{	ext{epoch } 2})}{	ext{median}(I_{	ext{epoch } 1})}$$

- **Result:**
  - Stationary stars $ightarrow 0$ (neutral gray).
  - Variable stars (flaring) $ightarrow$ Bright white spot.
  - Variable stars (fading) $ightarrow$ Dark black hole.
  - Moving objects $ightarrow$ **Dipole** (adjacent dark and light spots representing position in Epoch 1 vs Epoch 2).

---

## 3. Co-adding the 6 Detector Arrays for High SNR
SPHEREx's 102 bands span 6 detector arrays:
- **Array 1:** Channels 1–17 ($0.75 - 1.11\ \mu	ext{m}$)
- **Array 2:** Channels 18–34 ($1.11 - 1.64\ \mu	ext{m}$)
- **Array 3:** Channels 35–51 ($1.64 - 2.42\ \mu	ext{m}$)
- **Array 4:** Channels 52–68 ($2.42 - 3.82\ \mu	ext{m}$)
- **Array 5:** Channels 69–85 ($3.82 - 4.42\ \mu	ext{m}$)
- **Array 6:** Channels 86–102 ($4.42 - 5.00\ \mu	ext{m}$)

To maximize signal-to-noise for faint candidates, our tool allows users to toggle **"Co-add Arrays"**:
$$I_{	ext{coadd}} = rac{1}{N} \sum_{k \in 	ext{Array}} I_k$$
This increases SNR by up to $\sqrt{17} pprox 4.12	imes$, revealing faint brown dwarfs that are invisible in single narrow bands!
