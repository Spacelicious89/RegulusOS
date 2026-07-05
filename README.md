# 🦁 Project Regulus

**The Archeoastronomical Alignment & Planetary Syzygy Script**

### 🎯 Overview: A Global Analytical Tool
Project Regulus is a high-precision computational script utilizing `skyfield` (NASA JPL DE421 ephemeris) to isolate exact mathematical moments of complex celestial alignments at **any geodetic location on Earth**. 

While pre-configured to analyze alignments over the Great Sphinx of Giza (Azimuth 90.0°), the engine is fully scalable. It serves as an analytical lens for investigating archeological anomalies by cross-referencing orbital resonance with specific geodetic layouts, allowing researchers to test the hypothesis that ancient monuments function as "cosmic clocks" or "contact protocols."

### 🚀 Quick Start (No Installation Required)
1. Go to Google Colab and create a **New Notebook**.
2. In the first cell, run: `!pip install skyfield`
3. Add a new cell, paste the `ProjectRegulus.py` code, and click Play.
4. Modify the `GLOBAL USER INPUT ZONE` (see below) to suit your research parameters.
5. The script generates a timestamped `.csv` file in the Colab file browser containing all alignment data for your analysis.

### 🎛️ Configuration & Input Zone
The script is designed for rapid iteration. All critical controls are located in the `GLOBAL USER INPUT ZONE` at the top of the file:
* `TARGET_YEARS`: Input a single year or a list (e.g., `[2024, 2026, 2028, 2030]`) to validate orbital resonance.
* `SITE_NAME`, `SITE_LAT`, `SITE_LON`, `SITE_ELEVATION`: Define any monument or location on Earth.
* `SITE_TZ`: Define the local time zone (e.g., `"Africa/Cairo"` or `"America/Mexico_City"`).
* `TARGET_SCANS`: Define specific months and days to focus the engine on proposed anomalous windows.
* `TIME_STEP`: Set your scanning interval. `1` second provides maximum precision.

**🏷️ JPL Target Tags:** When modifying the `TARGET_PLANETS` dictionary, use the exact string IDs (e.g., `'mars'`, `'jupiter barycenter'`). If you upgrade to a different ephemeris (e.g., `de430.bsp`), run `print(eph)` in your console to view all available target identifiers.

---

### 🔭 Physics & Prophecy Conditions
The engine decodes the prophecy as recounted by Chris Bledsoe in his book *UFO of GOD*: "When the red star of Regulus aligns just before dawn in the gaze of the Sphinx, a new knowledge shall come into the world." 

**1. The "Red Star" Condition (Atmospheric Extinction)**
The engine tracks the "Red Star Phase" at an altitude of ~7.5°. Atmospheric thickness ($X$) shifts the spectrum toward red:
$$X = \frac{1}{\sin(\text{altitude})}$$
$$\Delta(B-V) \approx 0.15 \times X$$

**2. "Aligns in the gaze of the Sphinx" (Geodetic Anchor)**
The engine enforces a strict constraint: $$\text{Azimuth} = 90.0^\circ$$.

**3. "Just before dawn" (Luminosity Thresholds)**
We validate the timing with two constraints:
* **The Dawn Start:** Sun at $\approx -6.5^\circ$ (Civil Twilight).
* **The Washout Limit (NELM):** Regulus is invisible when background luminance exceeds stellar flux at Sun altitude **-2.72°**.

### 🧠 The NHI & Archeological Context
Building upon the hypothesis that Giza acts as a resonant system (notably the work of Dr. Filippo Biondi and Prof. Corrado Malanga regarding subterranean structures), this script allows researchers to test whether vertical alignments—such as Venus (Hathor) anchored in the Duat while Mars (Horus) guards the zenith—correlate with high-probability "contact windows."

### 🏆 Key Findings (The 2026 Trigger)
**1. The "Red Star" Alignment (Sept 24, 2026):** Validates the "Red Star just before dawn" prophecy condition at -6.5° sun altitude.
**2. The 5-Body "Royal Syzygy" (Nov 4, 2026):** A tightly stacked vertical pillar (Mars, Jupiter, Moon, Regulus) with Venus anchoring the underworld at -30°.
**3. The Biennial Mars Resonance**
By scanning the 2024–2030 window, the script reveals a strict 2-year orbital resonance pattern. While Mars and Regulus reach conjunction biennially regardless of the observer's location, the 2026 event is unique. It serves as the primary "lock" where the orbital conjunction perfectly intersects the 90° azimuth (the Sphinx's gaze) with a divergence of < 23 seconds, creating a rare geodetic-celestial trigger that does not occur during the biennial echoes in 2028 or 2030.

