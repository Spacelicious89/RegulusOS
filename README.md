# 🦁 Project Regulus (v2.5.1)
**Archeoastronomical Alignment & Planetary Syzygy Script**

### Overview: What is this?
I built Project Regulus to bridge the gap between ancient prophecies and orbital mechanics. Using `skyfield` (NASA JPL ephemeris), this script isolates exact moments of celestial alignment for any location on Earth. 

While it defaults to the Great Sphinx of Giza (Azimuth 90.0°), the code is fully scalable. It acts as an analytical lens, letting you test the theory that ancient monuments function as "cosmic clocks" or "contact protocols" by mapping precise orbital data against geodetic layouts.

### 🚀 Quick Start
1. **Google Colab:** Create a New Notebook.
2. **Install:** `!pip install skyfield`
3. **Run:** Copy `ProjectRegulus.py` into a cell and press Play.
4. **Output:** The script generates a timestamped `.csv` file in your browser, mapping all alignment windows for your analysis.

### 🎛️ Configuration & Ephemeris
All critical controls are at the top of the file in the `GLOBAL USER INPUT ZONE`:
* `TARGET_YEARS`: List of years (e.g., `[2024, 2026, 2028, 2030]`) to validate resonance.
* `SITE_DATA`: Set `NAME`, `LAT`, `LON`, `ELEVATION` for your site.
* `SITE_TZ`: Define time zone (e.g., `"Africa/Cairo"`).
* `TARGET_SCANS`: Specific months/days for focus.
* `TIME_STEP`: 1s is recommended for max precision.

**Ephemeris Selection (Time Range)**
The script uses NASA JPL ephemeris files. You can swap these based on the era you are researching:
* `de421.bsp` (Default): 1900 – 2053.
* `de422.bsp`: -3000 – 3000. Use this for standard antiquity research.
* `de431.bsp`: -13200 – 17000. Use this for deep history, ice age archaeology, and paleolithic studies.

*Note: Ensure the corresponding `.bsp` file is loaded in your environment if you switch away from the default.*

### 🔭 Physics & Prophecy Logic
The script decodes the prophecy from Chris Bledsoe's *UFO of GOD*: *"When the red star of Regulus aligns just before dawn in the gaze of the Sphinx, a new knowledge shall come into the world."*

**1. "The Red Star" (Atmospheric Extinction)**
Regulus at ~7.5° altitude creates the "Red Star" phase. I implemented Rayleigh scattering math to calculate the color shift ($\Delta(B-V)$) based on airmass ($X$):

$$X = \frac{1}{\sin(\text{altitude})}$$

$$\Delta(B-V) \approx 0.15 \times X$$

**2. "Gaze of the Sphinx" (Geodetic Anchor)**
The script enforces a strict Azimuth constraint for the target:

$$\text{Azimuth} = 90.0^\circ$$

**3. "Just Before Dawn" (Luminosity Windows)**
* **Dawn Start:** Sun at $\approx -6.5^\circ$ (Civil Twilight).
* **Washout Limit:** Stars vanish when background luminance overrides stellar flux at Sun altitude **-2.72°**.

### 🧠 Archaeological Context
This tool provides a data-driven framework for archaeoastronomy. Building on the work of Dr. Filippo Biondi and Prof. Corrado Malanga regarding subterranean structures and Giza's physical resonance, this script lets researchers turn back the celestial clock. It allows users to verify exactly what the sky looked like during antiquity, testing if specific planetary alignments—such as Venus (Hathor) anchored in the Duat and Mars (Horus) at the zenith—dictated the original architectural design, orientation, and "pre-programmed" logic of these ancient monuments.

### 🏆 Key Findings (The 2026 Trigger)
1. **Sept 24, 2026:** Validates the "Red Star just before dawn" condition at -6.5° sun altitude.
2. **Nov 4, 2026 (Royal Syzygy):** A massive 5-body vertical pillar (Mars, Jupiter, Moon, Regulus) striking the 90° azimuth, with Venus anchoring the underworld at -30°.
3. **Biennial Mars Resonance:** Scanning the 2024–2030 window reveals a strict 2-year cycle. The 2026 event is the "lock" (< 23s divergence), while 2028 and 2030 are essentially mechanical echoes/decay of the orbital pattern.
