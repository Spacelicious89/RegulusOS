Project Regulus: Master Computation Engine 🔭
Project Regulus is a Python-based, high-precision astronomical computation engine built to verify geometric and optical alignment hypotheses regarding the Great Sphinx of Giza.

Instead of relying on approximations or static star charts, this engine performs a brute-force, second-by-second scan of orbital mechanics. It utilizes the Skyfield library, the modern wgs84 topocentric model, and NASA JPL's de421.bsp ephemerides to calculate extreme-precision celestial events.

⚙️ Core Mechanics & Features:
True Topocentric Hardware: Treats the Great Sphinx as an optical instrument (Azimuth 90.000000°) located at precise coordinates with a 20m elevation.

Photometric Extinction Model: Calculates the exact second of visual extinction (contrast threshold) when the Sun reaches -2.72° altitude during civil dawn, incorporating desert atmospheric refraction (21°C, 1011 hPa).

Deep Time Verification: Maps time vectors from the Mayan Long Count reset (Dec 21, 2012) to identify prime-number day intervals.

Background Celestial Architecture: Simultaneously calculates the transit of Orion's Belt and the Galactic Center (Sgr A*) to map the complete astronomical background during the primary alignment.

Data-Driven. Zero Approximations. Pure Physics.
