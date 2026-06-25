# 🔭 Project Regulus: Master Computation Engine

Project Regulus is a Python-based, high-precision astronomical computation engine built to verify geometric and optical alignment hypotheses regarding the Great Sphinx of Giza. 

Instead of relying on approximations or static star charts, this engine performs a brute-force, second-by-second scan of orbital mechanics. It utilizes the `Skyfield` library, the WGS84 topocentric model, and official NASA JPL `de421.bsp` planetary ephemerides to calculate extreme-precision celestial events.

---

## 📜 The Context: Testing the Prophecy
This engine was specifically built to mathematically test the "Chris Bledsoe Prophecy" regarding the star Regulus. The claim suggests a specific global shift will occur when Regulus perfectly aligns with the exact gaze of the Sphinx (Azimuth 90° / True East) *just before dawn*. 

Due to the spread of misinformation and the use of basic phone apps that ignore atmospheric physics, many impossible dates (August, October, November) have been circulated. This script acts as a mathematical auditor to separate physics from fiction.

---

## 🎯 Key Findings (The TL;DR)
Running the engine reveals hard astronomical truths about the 2026 timeline:
* ❌ **November/October are Busted:** Alignments during these months occur in the dead of night (e.g., Sun is 64° below the horizon in November). They do not fit the "just before dawn" parameter.
* ❌ **August is Busted:** In early August, Regulus rises completely washed out by the Sun's daylight glare. It is invisible to the naked eye.
* ✅ **The True Window (Late September):** The actual mathematical window where Regulus hits exactly 90° and remains visible right before dawn occurs around **September 21-24**. 
* ⏳ **The Precession Clock:** Due to the slow axial wobble of the Earth, Regulus is drifting south. In roughly 2,500 years, it will completely fall out of the Sphinx's 90° window and won't return for 13,000 years, acting as a massive countdown clock.

---

## ⚙️ Core Mechanics & Features
* **Stationary Reference Point:** Defines the Great Sphinx as an optical instrument located at precise coordinates (29.97526° N, 31.13758° E) with a 20m elevation, targeting exactly Azimuth 90.0000°.
* **Photometric Extinction Model (NELM):** Calculates the exact second of visual extinction (contrast threshold) for a +1.4 mag star. It computes when the Sun reaches approx `-2.72°` altitude during civil dawn, incorporating desert atmospheric refraction (21°C, 1011 hPa).
* **Deep Time Verification:** Maps time vectors from the Mayan Long Count reset (Dec 21, 2012) to identify prime-number day intervals intersecting with alignment dates.
* **Background Celestial Architecture:** Simultaneously calculates the transit of Orion's Belt, Venus, Mars, and the Galactic Center (Sgr A*) to map the complete astronomical background during the primary alignment.

**Data-Driven. Zero Approximations. Pure Physics.**

---

## 🚀 How to Run the Engine

**1. Install Dependencies:**
You will need Python 3 installed. Install the required `skyfield` library:
```bash
pip install skyfield
