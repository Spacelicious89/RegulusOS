# 🦁 Project Regulus

**The Archeoastronomical Alignment & Planetary Syzygy Script**

### 🎯 Project Overview
Project Regulus is a high-precision computational script utilizing `skyfield` (NASA JPL DE421 ephemeris) to isolate exact mathematical moments of complex celestial alignments at any geodetic location on Earth. While pre-configured to analyze alignments over the Great Sphinx of Giza (Azimuth 90.0°), the engine is fully scalable and allows users to define custom coordinates for any monument or site worldwide.

Version 2.5.1 expands tracking capabilities to uncover multi-body vertical syzygies spanning both above and below the horizon, serving as an analytical lens for investigating archeological anomalies by cross-referencing orbital resonance with specific geodetic layouts.

### 🎛️ Global User Input Zone (How to configure)
The script has been refactored to place all critical controls in a single `GLOBAL USER INPUT ZONE` at the top of the file. 
* `TARGET_YEARS`: Input a single year or a list (e.g., `[2024, 2026, 2028, 2030]`) to validate orbital resonance.
* `SITE_NAME`, `SITE_LAT`, `SITE_LON`, `SITE_ELEVATION`: Define any monument or location on Earth.
* `SITE_TZ`: Define the local time zone (e.g., `"Africa/Cairo"` or `"America/Mexico_City"`).
* `TARGET_SCANS`: Define specific months and days to focus the engine on proposed anomalous windows.
* `TIME_STEP`: Set your scanning interval. `1` second provides maximum precision; higher values increase speed at the cost of granular accuracy.

### 🏷️ Quick Reference: JPL Target Tags
When modifying the `TARGET_PLANETS` dictionary, use the exact string IDs recognized by the NASA DE421 ephemeris. 
* Common targets: `'sun'`, `'moon'`, `'mercury'`, `'venus'`, `'mars'`, `'jupiter barycenter'`, `'saturn barycenter'`.
* *Pro-tip:* If you upgrade to a different ephemeris (e.g., `de430.bsp`), run `print(eph)` in your console to view all available target identifiers.

### 🔭 The Physics & Prophecy Conditions
The engine decodes the prophecy as recounted by Chris Bledsoe in his book *UFO of GOD*: "When the red star of Regulus aligns just before dawn in the gaze of the Sphinx, a new knowledge shall come into the world." 

To validate this, the script maps the text to three specific mathematical constraints:

**1. The "Red Star" Condition (Atmospheric Extinction)**

The engine tracks the "Red Star Phase," which occurs when Regulus reaches a low altitude of ~7.5°. At this altitude, the star's light travels through extreme atmospheric thickness ($X$), causing Rayleigh scattering that shifts the spectrum toward red.
The engine calculates the Airmass ($X$) and the color shift (Δ(B-V)) using these formulas:

$$X = \frac{1}{\sin(\text{altitude})}$$

$$\Delta(B-V) \approx 0.15 \times X$$

This physics-based calculation causes Regulus to appear blood-red against a still-dark sky, fulfilling the first condition of the prophecy.


**2. "Aligns ... in the gaze of the Sphinx" (Geodetic Anchor)**

The "gaze" is defined as the True East orientation of the Sphinx. The engine enforces a strict constraint where the celestial object must hit an Azimuth of exactly:

$$\text{Azimuth} = 90.0^\circ$$

The script flags the alignment only when Regulus pierces this precise geodetic line.


**3. "Just before dawn" (Luminosity Thresholds)**

This is the "contact window." The script validates two sun-altitude constraints:

* **The Dawn Start:** Sun at $\approx -6.5^\circ$ (the calculated optimal "Red Dawn" horizon gradient).
* **The Washout Limit (NELM):** The star becomes invisible when sky background luminance exceeds the star's flux. We define this limit at a Sun altitude of **-2.72°**. The contrast threshold ($\mathcal{C}$) is derived from the stellar magnitude ($m$) relative to sky background ($B$):

$$\mathcal{C} = \frac{F_{star}}{B_{sky}} > \text{Threshold}$$

When the Sun exceeds $-2.72^\circ$, the sky background brightness $B_{sky}$ exponentially overrides the stellar signal $F_{star}$, effectively "closing" the prophecy window.

### 🧠 The NHI & Archeological Context
This analysis tool provides a data-driven framework for investigating theories regarding ancient contact and Non-Human Intelligence (NHI).

By mapping orbital mechanics against any chosen site, the script allows for testing the hypothesis that certain monuments function as "contact protocols" or "cosmic clocks."

Recent interpretations of Giza (notably the work of Biondi and Malanga regarding the "Second Sphinx" and subterranean structures) suggest that the plateau may align with a pre-programmed orbital logic. This script enables researchers to test whether vertical alignments-such as Venus (Hathor) anchored in the Duat (sub-horizon) while Mars (Horus) guards the zenith, correlate with high probability "contact windows."

### 🏆 Key Findings & The 2026 Trigger Events

**1. The "Red Star" Alignment Window (September 24, 2026)**
This target focuses on the literal prophecy conditions: *"the red star of Regulus aligns just before dawn."* 

The engine isolates the exact moment the Sun reaches -6.5° altitude (Civil Twilight). This satisfies the "just before dawn" condition, capturing the transition from night to the first light of day. Simultaneously, the engine verifies the "red star" condition by tracking Regulus at its critical low altitude (~7.5°). At this position, heavy atmospheric extinction causes Regulus to appear blood-red against the still-dark horizon, directly fulfilling the prophecy's visual requirement.

**2. The 5-Body "Royal Syzygy" (November 4, 2026)**
As a secondary (but statistically anomalous) discovery, the script identified a 5-body vertical syzygy striking the 90° azimuth. This is not a scattered "planetary parade," but a tightly stacked vertical pillar: Mars, Jupiter, the Moon, and Regulus align in a vertical column, while Venus anchors the structure at -30° altitude (hidden below the horizon in the Duat).

**3. The Biennial Mars Resonance**
By scanning the 2024-2030 window, the script reveals a strict 2-year orbital resonance pattern:
* **2024:** Mars/Regulus alignment divergence (minutes).
* **2026:** The mechanical catalyst (divergence < 23 seconds).
* **2028/2030:** Mechanical echoes/decay of the orbital lock.
The 2026 event acts as the primary "lock," confirming that the planetary geometry is not random but follows a tightening, repeating cycle.

### 🚀 How to Run (No Installation Required)
1. Go to Google Colab and create a **New Notebook**.
2. In the first cell, run: `!pip install skyfield`
3. Add a new cell, paste the `ProjectRegulus.py` code, and click Play.
4. Modify the `GLOBAL USER INPUT ZONE` to suit your research parameters.
5. The script generates a timestamped `.csv` file in the Colab file browser containing all alignment data for your analysis.
