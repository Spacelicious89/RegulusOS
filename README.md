# 🦁 Project Regulus
**Archaeoastronomical Alignment & Planetary Syzygy Script**

![Project Regulus - Sphinx 5-Body Alignment](images/sphinx_5body.png)

### 🔭 Physics & Prophecy Logic
The engine decodes the prophecy from Chris Bledsoe's *UFO of GOD*: 
> *"When the red star of Regulus aligns just before dawn in the gaze of the Sphinx, a new knowledge shall come into the world."*

**1. "The Red Star" (Atmospheric Extinction)**
Regulus at ~7.5° altitude triggers the "Red Star" phase. I implemented Rayleigh scattering math to calculate the spectral shift based on airmass. At this altitude, the light of the B-type star Regulus is filtered through dense layers of the atmosphere, resulting in a distinct reddish-orange spectral shift:

$$X = \frac{1}{\sin(\text{altitude})}$$

$$\Delta(B-V) \approx 0.15 \times X$$

**2. "Gaze of the Sphinx" (Geodetic Anchor)**
The script enforces a strict architectural constraint for the target monument:
**Azimuth = 90.0° (True East)**

**3. "Just Before Dawn" (Timing & Luminosity Windows)**
* **Dawn Start (Civil Twilight):** Officially begins when the Sun reaches exactly **-6.0°**.
* **The "Just Before Dawn" Target (-6.5°):** I calibrated the engine to **-6.5°** to capture the exact moment immediately preceding actual dawn. At Giza's latitude, the Sun takes approximately 2.5 to 3 minutes to travel this 0.5° difference. 
* **The Azimuth Lock Constraint:** This 2-3 minute window is critical. The Earth rotates at roughly 1° every 4 minutes. If you wait for the Sun to rise higher, Regulus will have already drifted ~0.5° to 0.7° away from the precise 90.0° Sphinx alignment. The "Just Before Dawn" condition is therefore a highly fleeting, precise temporal lock.
* **Washout Limit (-2.72°):** The empirical threshold where sky background luminance ($B_{sky}$) mathematically overrides stellar flux ($F_{star}$), making the star invisible to the naked eye.

---

### 🧠 Archaeological Context

![Giza Polar Alignment](images/giza_polar_alignment.png)

This tool provides a data-driven framework for archaeoastronomy. Building on the work of Dr. Filippo Biondi and Prof. Corrado Malanga regarding subterranean structures and Giza's physical resonance, this script lets researchers turn back the celestial clock. It allows users to verify what the sky looked like during antiquity, testing if specific planetary alignments—such as Venus (Hathor) in the Duat and Mars (Horus) at the zenith—dictated the original architectural design, orientation, and "pre-programmed" logic of these ancient monuments.

---

### ⚙️ Engine Capabilities
* **Visibility Logic:** Automated washout detection. The engine cross-references Sun altitude (NELM) and Lunar illumination (> 75%) to determine if a celestial object is truly "visible" or washed out at the moment of alignment.
* **Mars Conjunction Delta:** Calculates the exact time difference (seconds) between Mars crossing the target azimuth and Regulus hitting the "lock," identifying multi-planetary orbital resonances.
* **Resonance Metric (Prime Check):** Every scan checks if the delta in days from the 2012-12-21 epoch is a **Prime Number**, testing for mathematical harmonic resonance.
* **SkyMap Rendering:** Generates real-time data for:
    * **LST Clock:** Local Sidereal Time for precise coordinate alignment.
    * **Galactic Center & Orion's Belt:** Tracks coordinates to verify if the alignment correlates with known ancient stellar anchors.

---

### 🏆 Key Findings (The 2026 Trigger)

| Date | Phase | Astronomical Description |
| :--- | :--- | :--- |
| **Sept 21, 2026** | **Visual Window Opens** | The preliminary window begins. *(Mayan Tzolk'in: 8 Ik' - representing the Wind, breath of life, and a change of cosmic direction).* |
| **Sept 24, 2026** | **Mathematical Peak** | Validates the "Red Star just before dawn" condition at a perfect **-6.5°** sun altitude with an incredible **0.0100°** deviation. *(Mayan Tzolk'in: 11 Chikchan - the Serpent's awakening).* |
| **Nov 4, 2026** | **The Royal Syzygy** | The mechanical lock. A 5-body vertical pillar (Mars, Jupiter, Moon, Regulus) strikes exactly **90.0°** azimuth. Venus anchors the underworld at **-30.5°**. The Sun is completely off-axis, proving geometric purity. |

![Vertical Planetary Lock - November 2026](images/Syzygy_4_11_2026.png)

---

### 📊 Empirical Proof: The 2026 Mars Resonance

![Mars-Regulus Orbital Synchronization (2014-2035)](images/Mars_Regulus_sync_2014-2035.png)

To prove this isn't a common occurrence, the `RegulusOS.py` engine was run across a multi-year baseline (2024-2030) to test the exact synchronization of Mars and Regulus striking the 90.0° Sphinx azimuth. 

The engine tracks `Mars_Delta_Sec` (the exact time divergence between Mars crossing the target azimuth and the Regulus alignment lock). The data shows a strict orbital decay pattern centering entirely on 2026:

| Epoch | Resonance Phase | Divergence Error | System Status |
| :--- | :--- | :--- | :--- |
| **Oct 2024** | Mechanical Echo | ~ 4,723s *(> 1h 18m)* | ❌ Complete failure of alignment |
| **Nov 2026** | **Primary Lock** | **< 23 seconds** | ✅ **Near-perfect geodetic lock** |
| **Oct 2030** | Orbital Decay | ~ -769s *(~ 13m)* | ❌ Machinery shifting out of tune |

This isn't astrology; it's hard celestial mechanics. The exact parameters described in Bledsoe's prophecy happen annually—acting purely as a celestial timing key. However, the script mathematically proves that in late 2026, this annual key perfectly synchronizes with a hidden, multi-planetary orbital resonance. The prophecy itself isn't the anomaly; it is the precise coordinate required to witness the anomaly.

---

### 🌍 Global Control Scans (Raw Data)
To verify the geographic uniqueness of the November 2026 alignment, a multi-site control scan was executed against other megalithic structures (Angkor Wat, Stonehenge, Chichén Itzá, Teotihuacan). 

The raw CSV export is available in the `logs/` directory. The data conclusively demonstrates that the precise 23-second multi-planetary vertical lock is mathematically exclusive to the specific coordinates and the 90.0° orientation of the Giza Plateau.

---

### 🚀 Quick Start
1. **Google Colab:** Create a New Notebook.
2. **Install:** Run `!pip install skyfield` in the first cell.
3. **Execute:** Copy `ProjectRegulusGlobal.py` into a cell and press Play.
4. **Analyze Output:** The script generates timestamped `.csv` files in your environment, mapping all alignment windows for your analysis.

---

### 🎛️ Configuration & Ephemeris
All critical controls are located at the top of the file in the `GLOBAL USER INPUT ZONE`:
* `TARGET_YEARS`: List of years to scan (e.g., `[2026]`).
* `TARGET_SITES`: Define `NAME`, `LAT`, `LON`, `ELEVATION`, `AZIMUTH`, and `TZ`.
* `TIME_STEP_SECONDS`: `1` is highly recommended for maximum precision.

**Ephemeris Selection (NASA JPL):**
* `de421.bsp` *(Default)*: 1900 – 2053.
* `de422.bsp`: -3000 – 3000 (Ideal for antiquity research).
* `de431.bsp`: -13200 – 17000 (Deep history/Paleolithic alignments).

### 🛠️ Default Settings Rationale
* **Azimuth 90.0°:** The geodetic anchor for the Sphinx's True East orientation.
* **RED_STAR_ALT (7.5°):** The critical altitude where Rayleigh scattering increases significantly. While Regulus is naturally blue-white, observation at this low angle—especially in the presence of aerosols, desert dust, or high humidity—intensifies light scattering, shifting the hue to a deep reddish-orange or "blood-red."
* **Sun Altitude -6.5°:** Custom threshold for the pre-dawn window; ensures the alignment occurs in the deeper pre-dawn phase before civil twilight.
* **Sun Altitude -2.72° (Washout Limit):** Empirical threshold where sky background luminance ($B_{sky}$) overrides stellar flux ($F_{star}$).
