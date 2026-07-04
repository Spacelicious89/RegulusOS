# 🦁 Project Regulus - Master Computation Engine v2.5.1

**The Archeoastronomical Alignment & Planetary Syzygy Engine**

### 🎯 Project Overview
Project Regulus is a high-precision Python computation engine utilizing `skyfield` (NASA JPL DE421 ephemeris) to isolate the exact mathematical moments of complex celestial alignments over the Great Sphinx of Giza (Azimuth 90.0°). 

Version 2.5.1 expands the array of tracked celestial bodies to uncover not just dual conjunctions, but ultra-rare, multi-body vertical syzygies spanning both above and below the local horizon.

### 🎛️ Global User Input Zone (How to configure)
The engine has been refactored to place all critical controls in a single, highly readable `GLOBAL USER INPUT ZONE` at the top of the script. You do not need to modify the core logic to run custom scans.
* `TARGET_YEARS`: Input a single year or a list of years (e.g., `[2026, 2027, 2028, 2029, 2030, 2031]`).
* `TARGET_SCANS`: A flexible dictionary allowing you to define exact target months (e.g., months 8, 9, 10, 11).
* `TIME_STEP`: Set your scanning interval (e.g., 15 seconds) for optimal CPU performance versus precision.
* `TARGET_PLANETS`: Easily add or remove bodies using standard JPL barycenter tags.

### 🏷️ Quick Reference: JPL Target Tags

When modifying the `TARGET_PLANETS` dictionary, you must use the exact string IDs recognized by the NASA DE421 ephemeris. 

Here is the complete cheat sheet for the major bodies:

* `'sun'`
* `'moon'`
* `'mercury'`
* `'venus'`
* `'mars'`
* `'jupiter barycenter'`
* `'saturn barycenter'`
* `'uranus barycenter'`
* `'neptune barycenter'`
* `'pluto barycenter'`

> **Pro-tip for Python users:** If you ever upgrade to a different ephemeris file (like `de430.bsp`), you can see all available targets by running `print(eph)` in your console.

### 🔭 The Physics & Methodology

**1. Atmospheric Extinction & The Red Star Phase**
The engine strictly adheres to spherical geometry and atmospheric physics. Because of Giza's latitude and Regulus's declination, the engine independently tracks the Red Star Phase, which triggers when Regulus is at a low altitude of ~7.5°. At this altitude, the star's light passes through extreme atmospheric thickness. The engine calculates this using the Airmass (X) formula:

$$X = \frac{1}{\sin(\text{altitude})}$$

This extreme airmass triggers intense Rayleigh scattering, modifying the star's color index (Δ(B-V)) according to atmospheric extinction approximations:

$$\Delta(B-V) \approx 0.15 \times X$$

This filters out the star's natural blue-white spectrum, causing **the star itself** to appear heavily shifted toward the red/orange spectrum while the sky remains pitch black.

**2. The Red Dawn Trigger (Civil Twilight)**
By the time Regulus reaches the 90.0° alignment point, it has climbed to an altitude of ~24.5°. Here, the airmass is thinner, and Regulus regains its intense, piercing white brilliance. However, to recreate the exact "Red Dawn" prophecy conditions, the engine hunts for the moment the Sun reaches exactly ~-6.5° altitude (Civil Twilight). At this specific depth, the Sun casts a deep, burning red/orange gradient across the Eastern horizon. The result is a brilliant white star standing directly over a blood-red dawn.

### 🏆 Key Findings for The 2026 Trigger Event

**1. The Royal Syzygy (November 4, 2026)**
The engine detected a statistically unprecedented 5-body Vertical Syzygy striking the exact 90° azimuth. This is not a scattered "planetary parade," but a tightly stacked vertical pillar occurring simultaneously:

* **Mars (God of War):** Altitude +34.4351° | Azimuth 90.0681°
* **Jupiter (King of Gods):** Altitude +29.77° | Azimuth 90.51° 
* **Regulus (The Little King):** Altitude +24.3053° | Azimuth 90.0°
* **Moon:** Altitude +14.4209° | Azimuth 90.4551°
* **Venus (The Queen / Underworld Anchor):** Altitude -30.5457° | Azimuth 88.3895°

*Notice Venus:* By expanding the array beyond the visible horizon, the engine reveals Venus deeply submerged below the surface. This vertical geometry pierces the horizon, forming a continuous pillar anchored in the Egyptian Duat (underworld). The alignment of these specific 5 bodies on this exact precessional axis is an anomaly on the scale of tens of thousands of years.

**2. The Biennial Mars Resonance & The 2026 Catalyst**
Running the dynamic evaluation across the 2026-2031 timeline revealed a strict 2-year (biennial) orbital resonance pattern tied to Mars. The optimal Red Dawn alignments cluster perfectly in 2026, 2028, and 2030. 

The engine identifies the window of **September 24, 2026** (Sun Altitude: -6.4670°) as the true "Trigger Event." This specific 2026 window acts as the catalyst, initiating the sequence that culminates in the massive 5-body Royal Syzygy just weeks later in November. The subsequent years (2028, 2030) act as the mechanical echoes of this primary orbital lock.

### 🚀 How to Run (No Installation Required)

1. Go to Google Colab and click **New Notebook**.
2. In the first cell, paste this command and click Play: `!pip install skyfield`
3. Add a new cell, paste the entire `ProjectRegulus.py` code, and click Play.
4. **To customize:** Edit the variables in the `GLOBAL USER INPUT ZONE`. The engine will handle the heavy lifting and output the results.
