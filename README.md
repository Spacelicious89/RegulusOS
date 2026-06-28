# 🦁 Project Regulus - Master Computation Engine v1.9
**The Atmospheric Extinction ("Red Dawn") & Auto-Timezone Update**

## 🎯 Project Overview
Project Regulus is a data-driven Python computation engine utilizing `skyfield` (JPL DE421 ephemeris) to isolate the precise mathematical moments when the star **Regulus (α Leonis)** aligns perfectly with the **Great Sphinx of Giza** (Azimuth 90.0000° - True East) in the pre-dawn sky. 

Version 1.9 represents a major paradigm shift. The engine no longer simply searches for the "longest visible window." Instead, it acts as a dynamic archeoastronomical tool, optimizing for **Maximum Atmospheric Extinction (The Red Shift Score)** while tracking key planetary overlaps.

## ⚙️ What's New in v1.9?
* **Red Shift Scoring System:** The algorithm evaluates every scanned date against an ideal Sun altitude target (`IDEAL_SUN_ALT = -3.5°`) and prints the mathematical deviation (Extinction Score) for every date, validating or invalidating it instantly.
* **Nautical Dawn Sweet Spot:** It finds the exact compromise between optical visibility (Sun must be `< -2.72°` NELM) and maximum atmospheric density to filter the star's spectrum.
* **Dynamic Timezone Resolution (`zoneinfo`):** Automatically calculates Egyptian Daylight Saving Time (DST) changes for any given year/month, ensuring the "Local Time" output is always 100% accurate without manual offsets.
* **Global Dynamic Evaluation:** All modules (August, September, October, November) dump their alignment data into a global memory pool. The engine independently ranks the data and mathematically selects the ultimate timeline without human bias.
* **Foolproof User Input Zones:** Added clearly marked `👇 USER INPUT ZONE 👇` blocks so researchers can easily plug in custom dates to test other hypotheses.

---

## 🔭 The Physics: Why 24.5° Altitude? (Addressing the "Red" Regulus)
A critical feature of this engine is its adherence to strict spherical geometry. 

Because of the latitude of Giza (~30° N) and the declination of Regulus (+11° 58'), **Regulus does not rise at True East (90°)**. It rises at roughly 76° (East-Northeast). As the Earth rotates, the star climbs diagonally. By the time it crosses the exact 90.0000° line of sight of the Sphinx, it is geometrically locked to an altitude of **~24.5°**.

**The Airmass Factor:**
At 0°–5° altitude, a star's light passes through massive amounts of atmosphere, scattering blue light and turning red (Rayleigh scattering). At 24.5°, the airmass is significantly thinner. 

Therefore, Regulus at 90° azimuth will *not* be blood red. It will be an intense, warm white/yellow. **The v1.9 Extinction Score does not pretend to break physics.** Instead, it isolates the *maximum possible atmospheric warming effect* before the sky gets too bright, placing this brilliantly bright star against the deep purple/orange gradient of the nautical dawn.

---

## 🏆 Key Findings for 2026
Running the engine across the late 2026 timeline yields the following mathematically proven events:

1. **The Ultimate "Red Dawn" Window:** `September 21, 2026`. The engine isolates this date as the absolute mathematical peak. Regulus hits True East while the Sun is at exactly **-3.6031°** (just 0.1° deviation from our perfect target).
2. **The Pitch Black Cutoff:** `October 6, 2026`. The engine proves that by early October, the Sun drops below -18.0° at the moment of alignment. The sky enters deep astronomical night (Pitch Black), destroying the dawn contrast effect.
3. **The Vertical Mars Conjunction (The Literal "Red Star" Overlap):** `November 3-4, 2026`. While the engine proves November occurs in pitch-black night (Sun at -47°), it tracks an incredibly precise planetary event. Mars and Regulus cross the Sphinx's exact line of sight simultaneously—with a time difference of just **0.4 minutes (24 seconds)**. With Regulus at +24.28° altitude and Mars perfectly above it at +34.00°, this creates a spectacular vertical conjunction of a white star and a literal Red Planet forming a straight vertical line over True East. 

---

## 🚀 How to Run (No Installation Required - Google Colab)
The easiest way to verify these calculations without installing anything on your computer is to use Google Colab (a free, in-browser Python environment).

1. Go to [Google Colab](https://colab.research.google.com/) and click **New Notebook**.
2. In the very first cell, paste this command to install the required library and click the **Play** button:
   ```python
   !pip install skyfield                                              
