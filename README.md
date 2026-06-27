# 🦁 Project Regulus - Master Computation Engine v1.9
**The Atmospheric Extinction ("Red Dawn") Update**

## 🎯 Project Overview
Project Regulus is a data-driven Python computation engine utilizing `skyfield` (JPL DE421 ephemeris) to isolate the precise mathematical moments when the star **Regulus (α Leonis)** aligns perfectly with the **Great Sphinx of Giza** (Azimuth 90.0000° - True East) in the pre-dawn sky. 

Version 1.9 represents a major paradigm shift. The engine no longer simply searches for the "longest visible window." Instead, it acts as a dynamic archeoastronomical tool, optimizing for **Maximum Atmospheric Extinction (The Red Shift Score)**.

## ⚙️ What's New in v1.9?
* **Red Shift Scoring System:** The algorithm evaluates every scanned date against an ideal Sun altitude target (`IDEAL_SUN_ALT = -3.5°`).
* **Nautical Dawn Sweet Spot:** It finds the exact compromise between optical visibility (Sun must be `< -2.72°` NELM) and maximum atmospheric density to filter the star's spectrum.
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
3. **The Mars Conjunction:** `November 25-27, 2026`. The engine successfully tracks Mars crossing the Sphinx's line of sight just 14.9 minutes after Regulus, resulting in a spectacular planetary conjunction on the eastern horizon.

## 🚀 How to Run Locally
1. Ensure you have Python installed.
2. Install dependencies: `pip install skyfield`
3. Run the script: `python regulus_engine.py`
4. *Optional:* Modify the arrays inside the `USER INPUT ZONE` blocks to test your own dates!
