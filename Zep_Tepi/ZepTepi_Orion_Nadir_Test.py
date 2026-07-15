import csv
from skyfield.api import load, Star, wgs84
from skyfield import almanac
import numpy as np

print("======================================================")
print("      ZEP TEPI (Hancock & Bauval Test)     ")
print("======================================================")
print("Initializing astronomical models (de441.bsp)...")

ts = load.timescale()
eph = load('de441.bsp')
earth, sun = eph['earth'], eph['sun']
giza = earth + wgs84.latlon(29.975234, 31.137772, elevation_m=20.0)

# Anchor Stars for Hancock/Bauval Theory
# Testing the entire Orion's Belt, starting with the central star
alnilam = Star(ra_hours=(5, 36, 12.81), dec_degrees=(-1, 12, 6.9))
regulus = Star(ra_hours=(10, 8, 22.311), dec_degrees=(11, 58, 1.95))

results = []

print("\nScanning Epoch: 13000 BCE to 10000 BCE (Step: 10 years)")
print("Methodology: Finding the absolute minimum altitude of Orion")
print("-" * 54)

for year in range(-13000, -6999, 10): # changed for 10-year increments for performance, adjust as needed
    t0 = ts.utc(year, 1, 1)
    t1 = ts.utc(year, 12, 31)
    
    # 1. FIND EXACT VERNAL EQUINOX FOR THIS YEAR
    t_seasons, seasons = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    ve_time = None
    for t, s in zip(t_seasons, seasons):
        if s == 0:  # 0 represents Vernal Equinox 
            ve_time = t
            break
            
    if ve_time is None: continue

    # 2. ORION TEST (Lowest Transit Point) - 1-minute resolution
    # Generate 1440 minutes of data to find the EXACT peak altitude of Orion
    t_minutes_orion = ts.utc(ve_time.utc.year, ve_time.utc.month, ve_time.utc.day, 0, range(24 * 60))
    alnilam_alt, _, _ = giza.at(t_minutes_orion).observe(alnilam).apparent().altaz()
    alnilam_max_alt = float(np.max(alnilam_alt.degrees))

    # 3. LEO/SPHINX TEST (Vernal Equinox Dawn)
    # Generate minute-by-minute data to find exactly when Sun Alt hits -6.0°
    t_minutes = ts.utc(ve_time.utc.year, ve_time.utc.month, ve_time.utc.day, 0, range(24 * 60))
    sun_alt, _, _ = giza.at(t_minutes).observe(sun).apparent().altaz()
    
    dawn_time = None
    for i in range(1, len(sun_alt.degrees)):
        if sun_alt.degrees[i-1] < -6.0 and sun_alt.degrees[i] >= -6.0:
            dawn_time = t_minutes[i]
            break
            
    if dawn_time is not None:
        reg_alt, reg_az, _ = giza.at(dawn_time).observe(regulus).apparent().altaz()
        
        reg_az_val = float(np.atleast_1d(reg_az.degrees)[0])
        dev_east = abs(reg_az_val - 90.0)
        
        y, mo, d, h, mn, s = dawn_time.utc
        formatted_time = f"{int(y)}-{int(mo):02d}-{int(d):02d} {int(h):02d}:{int(mn):02d}:{int(s):02d}"
        
        results.append({
            'Year': year,
            'Equinox_Dawn_UTC': formatted_time,
            'Orion_Max_Alt': round(alnilam_max_alt, 2),
            'Regulus_Az_at_Dawn': round(reg_az_val, 2),
            'Regulus_Deviation_from_East': round(dev_east, 2)
        })
        
        # Live console tracking
        print(f"Year {year} | Orion Peak Alt: {alnilam_max_alt:.2f}° | Regulus Azimuth: {reg_az_val:.2f}°")

csv_file = "Zep_Tepi_Orion_Nadir_Results.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Year', 'Equinox_Dawn_UTC', 'Orion_Max_Alt', 'Regulus_Az_at_Dawn', 'Regulus_Deviation_from_East'])
    writer.writeheader()
    writer.writerows(results)

print("-" * 54)
print(f"\n[SCAN COMPLETE] Mythbuster results saved to: {csv_file}")

# --- DATA-DRIVEN ANALYSIS ---
# Finding the absolute minimum altitude of Orion's Belt across all scanned years
min_orion_entry = min(results, key=lambda x: x['Orion_Max_Alt'])
absolute_nadir = min_orion_entry['Orion_Max_Alt']
nadir_year = min_orion_entry['Year']

print("\n--- METHDOLOGICAL CONCLUSION ---")
print(f"1. ASTRONOMICAL NADIR: The absolute lowest point of Orion's Belt occurred in year {nadir_year}.")
print(f"2. MEASUREMENT: At this Nadir, Orion's Belt peaked at an altitude of {absolute_nadir}°.")
print(f"3. BAUVAL'S THEORY: Theory demands 9.33°. The mathematical reality misses this by {abs(absolute_nadir - 9.33):.2f}°.")

if abs(absolute_nadir - 9.33) > 0.5:
    print("VERDICT: The 10,500 BCE 'perfect alignment' is mathematically impossible. The sky never reached 9.33°.")
