# 🦁 Project Regulus (v2.5.1)
**Archeoastronomical Alignment & Planetary Syzygy Script**

### 🔭 Physics & Prophecy Logic
The engine decodes the prophecy from Chris Bledsoe's *UFO of GOD*: *"When the red star of Regulus aligns just before dawn in the gaze of the Sphinx, a new knowledge shall come into the world."*

**1. "The Red Star" (Atmospheric Extinction)**
Regulus at ~7.5° altitude triggers the "Red Star" phase. I implemented Rayleigh scattering math to calculate the spectral shift Δ(B-V) based on airmass (X). At this altitude, the light of the B-type star Regulus is filtered through dense atmosphere, resulting in a distinct reddish-orange spectral shift:

$$X = \frac{1}{\sin(\text{altitude})}$$

$$\Delta(B-V) \approx 0.15 \times X$$

**2. "Gaze of the Sphinx" (Geodetic Anchor)**
The script enforces a strict Azimuth constraint for the target:

$$\text{Azimuth} = 90.0^\circ$$

**3. "Just Before Dawn" (Timing & Luminosity Windows)**
* **Dawn Start (Civil Twilight):** Officially begins when the Sun reaches exactly **-6.0°**.
* **The "Just Before Dawn" Target (-6.5°):** We calibrate the engine to **-6.5°** to capture the exact moment immediately preceding actual dawn. At Giza's latitude, the Sun takes approximately **2.5 to 3 minutes** to travel this 0.5° difference. 
* **The Azimuth Lock Constraint:** This 2-3 minute window is critical. The Earth rotates at roughly 1° every 4 minutes. If you wait for the Sun to rise higher, Regulus will have already drifted ~0.5° to 0.7° away from the precise 90.0° Sphinx alignment. The "Just Before Dawn" condition is therefore a highly fleeting, precise temporal lock.
* **Washout Limit (-2.72°):** The empirical threshold where sky background luminance ($B_{sky}$) mathematically overrides stellar flux ($F_{star}$), making the star invisible to the naked eye.

### 🧠 Archaeological Context
This tool provides a data-driven framework for archaeoastronomy. Building on the work of Dr. Filippo Biondi and Prof. Corrado Malanga regarding subterranean structures and Giza's physical resonance, this script lets researchers turn back the celestial clock. It allows users to verify what the sky looked like during antiquity, testing if specific planetary alignments-such as Venus (Hathor) in the Duat and Mars (Horus) at the zenith-dictated the original architectural design, orientation, and "pre-programmed" logic of these ancient monuments.

### ⚙️ Engine Capabilities
* **Visibility Logic:** Automated washout detection. The engine cross-references Sun altitude (NELM) and Lunar illumination (> 75%) to determine if a celestial object is truly "visible" or washed out at the moment of alignment.
* **Mars Conjunction Delta:** Calculates the exact time difference (seconds) between Mars crossing the target azimuth and Regulus hitting the "lock," identifying potential orbital resonances.
* **Resonance Metric (Prime Check):** Every scan checks if the delta in days from the 2012-12-21 epoch is a **Prime Number**, testing for mathematical harmonic resonance.
* **SkyMap Rendering:** Generates real-time data for:
    * **LST Clock:** Local Sidereal Time for precise coordinate alignment.
    * **Galactic Center & Orion's Belt:** Tracks coordinates to verify if the alignment correlates with known ancient stellar anchors.

### 🏆 Key Findings (The 2026 Trigger)
1. **Sept 24, 2026:** Validates the "Red Star just before dawn" condition at -6.5° sun altitude.
2. **Nov 4, 2026 (Royal Syzygy):** A 5-body vertical pillar (Mars, Jupiter, Moon, Regulus) striking 90° azimuth, with Venus anchoring the underworld at -30°.
3. **Biennial Mars Resonance:** Scanning the 2024-2030 window reveals a strict 2-year cycle. The 2026 event acts as the "primary lock" (< 23s divergence), while 2028 and 2030 represent mechanical echoes/decay.

### 📊 Empirical Proof: The 2026 Mars Resonance (Data Logs)
To prove this isn't a common occurrence, I ran the `ProjectRegulus.py` engine across a multi year baseline (2024-2030) to test the exact synchronization of Mars and Regulus striking the 90.0° Sphinx azimuth. 

The engine tracks `Mars_Delta_Sec` (the exact time divergence between Mars crossing the target azimuth and the Regulus alignment lock). The results show a strict orbital decay pattern centering on 2026:

* **Oct 2024 (Echo):** Divergence is ~4,723 seconds (over **1 hour and 18 minutes**). Complete mechanical failure of the alignment.
* **Nov 4, 2026 (The Lock):** Divergence is **< 23 seconds**. A near-perfect simultaneous geometrical lock on the geodetic target.
* **Oct 2030 (Echo):** Divergence is ~ -769 seconds (almost **13 minutes**). The orbital machinery is shifting out of resonance.

This isn't astrology; it's hard celestial mechanics. The exact parameters described in Bledsoe's "prophecy" (Regulus at 90° before dawn) happen annually-they act purely as a celestial timing key. However, the script mathematically proves that in late 2026, this annual key perfectly synchronizes with a hidden, multi-planetary orbital resonance (the < 23s Mars lock). This creates an isolated, highly specific geometric window that simply does not exist in the surrounding years. The prophecy itself isn't the anomaly; it's the precise coordinate required to witness the anomaly.

### 🚀 Quick Start
1. **Google Colab:** Create a New Notebook.
2. **Install:** `!pip install skyfield`
3. **Run:** Copy `ProjectRegulus.py` into a cell and press Play.
4. **Output:** The script generates a timestamped `.csv` file in your browser, mapping all alignment windows for your analysis.

### 🎛️ Configuration & Ephemeris
All critical controls are at the top of the file in the `GLOBAL USER INPUT ZONE`:
* `TARGET_YEARS`: List of years (e.g., `[2026]`).
* `SITE_DATA`: Define `NAME`, `LAT`, `LON`, `ELEVATION`.
* `SITE_TZ`: Time zone (e.g., `"Africa/Cairo"`).
* `TIME_STEP`: 1s is recommended for max precision.

**Ephemeris Selection:**
* `de421.bsp` (Default): 1900 – 2053.
* `de422.bsp`: -3000 – 3000 (Antiquity research).
* `de431.bsp`: -13200 – 17000 (Deep history/Paleolithic).

### 🛠️ Default Settings Rationale
* **Azimuth 90.0°:** The geodetic anchor for the Sphinx's True East orientation.
* **RED_STAR_ALT (7.5°):** The critical altitude where Rayleigh scattering increases significantly. While Regulus is naturally blue-white, observation at this low angle - especially in the presence of aerosols, desert dust, or high humidity—intensifies light scattering, shifting the hue to a deep reddish-orange or "blood-red," fulfilling the prophecy under specific atmospheric conditions.
* **Sun Altitude -6.5°:** Custom threshold for the pre-dawn window; ensures we are in the deeper pre-dawn phase before civil twilight.
* **Sun Altitude -2.72° (Washout Limit):** Empirical threshold where sky background luminance ($B_{sky}$) overrides stellar flux ($F_{star}$).


