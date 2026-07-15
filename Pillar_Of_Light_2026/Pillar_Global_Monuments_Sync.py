import datetime
import csv
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from zoneinfo import ZoneInfo
from skyfield.api import load, Star, wgs84
from skyfield import almanac
import numpy as np
from tqdm import tqdm

'''
=====================================================================
GLOSSARY, LEGEND & SCIENTIFIC DERIVATIONS
=====================================================================

1. OPTICAL & ATMOSPHERIC PARAMETERS:
   - NELM (Naked-Eye Limiting Magnitude): The brightness threshold where 
     sky background luminance washes out celestial objects (-2.72° Sun Alt).
   - RED_STAR_ALT: The altitude threshold (~7.5°) where atmospheric 
     extinction shifts stellar spectra to a reddish-orange tint.

2. ASTRONOMICAL ANCHORS:
   - Regulus (Alpha Leonis): Used as the primary target. 
   - Mars, Venus, Jupiter, Pluto, Moon: Used as secondary intersecting agents 
     to detect the "Pillar of Light" (Gravitational alignment).

3. SCORING MECHANISM (Gravitational Lock):
   - The engine looks for the tightest temporal clustering of planetary 
     azimuths crossing the geodetic anchor axis (e.g., 90° for Giza).
=====================================================================
'''

# -------------------------------------------------------------------
# GLOBAL USER INPUT ZONE
# -------------------------------------------------------------------
TARGET_YEARS = [2026] 

# RESOLUTION / PERFORMANCE
# 60s for rapid scanning, 10s for production runs, 1s for absolute precision
TIME_STEP_SECONDS = 10

# --- THE GEODETIC SITES MATRIX (Now with dynamic Time Zones) ---
TARGET_SITES = {
    "Great Sphinx of Giza": {"lat": 29.975234, "lon": 31.137772, "elev": 20.0, "azimuth": 90.0, "tz": "Africa/Cairo"},
    "Angkor Wat": {"lat": 13.412469, "lon": 103.866775, "elev": 60.0, "azimuth": 90.0, "tz": "Asia/Phnom_Penh"},
    "Stonehenge": {"lat": 51.178882, "lon": -1.826215, "elev": 100.0, "azimuth": 51.0, "tz": "Europe/London"},
    "Teotihuacan (Avenue of the Dead)": {"lat": 19.692592, "lon": -98.843795, "elev": 2280.0, "azimuth": 15.25, "tz": "America/Mexico_City"},
    "Chichen Itza (El Castillo)": {"lat": 20.683056, "lon": -88.568611, "elev": 30.0, "azimuth": 21.0, "tz": "America/Cancun"}
}

# --- THE TEMPORAL LOCKS ---
TARGET_SCANS = {
    9: {"days": [22, 23, 24, 25, 26], "start_h": 0, "scan_h": 24},
    11: {"days": [2, 3, 4, 5, 6], "start_h": 0, "scan_h": 24}
}

# -------------------------------------------------------------------
# ENGINE INITIALIZATION
# -------------------------------------------------------------------
ts = load.timescale()
eph = load('de421.bsp')
earth, sun, moon = eph['earth'], eph['sun'], eph['moon']

# Celestial Bodies Memory Bank for the Pillar of Light
TARGET_PLANETS = {
    'Venus': eph['venus barycenter'],
    'Mars': eph['mars barycenter'],
    'Jupiter': eph['jupiter barycenter'],
    'Saturn': eph['saturn barycenter'],
    'Mercury': eph['mercury barycenter'],
    'Uranus': eph['uranus barycenter'],
    'Neptune': eph['neptune barycenter'],
    'Pluto': eph['pluto barycenter'],
    'Moon': eph['moon']
}

regulus = Star(ra_hours=(10, 8, 22.311), dec_degrees=(11, 58, 1.95))
sirius = Star(ra_hours=(6, 45, 8.9), dec_degrees=(-16, 42, 58))
vega = Star(ra_hours=(18, 36, 56.3), dec_degrees=(38, 47, 1))
orion_belt_alnilam = Star(ra_hours=(5, 36, 12.8), dec_degrees=(-1, 12, 6.9))
galactic_center = Star(ra_hours=(17, 45, 40.0), dec_degrees=(-29, 0, 28.1))

ATM_TEMPERATURE = 15.0
ATM_PRESSURE = 1010.0

def scan_single_location_year(year, SITE_NAME, SITE_CONFIG):
    """
    Worker function executed independently for each location.
    Returns (candidate_list, formatted_log_string)
    """
    output_buffer = []
    def log(msg):
        output_buffer.append(msg)

    site = earth + wgs84.latlon(SITE_CONFIG["lat"], SITE_CONFIG["lon"], elevation_m=SITE_CONFIG["elev"])
    site_target_azimuth = SITE_CONFIG["azimuth"]
    local_tz = ZoneInfo(SITE_CONFIG["tz"])
    
    candidates = []

    log("===========================================================================")
    log(f"                 SCAN MODULE - YEAR: {year} | SITE: {SITE_NAME}")
    log(f"                 GEODETIC ANCHOR AZIMUTH: {site_target_azimuth}°")
    log(f"                 LOCAL TIME ZONE: {SITE_CONFIG['tz']}")
    log("===========================================================================\n")

    for month, config in sorted(TARGET_SCANS.items()):
        for day in config["days"]:
            dt_base = datetime.date(year, month, day)
            
            log(f"📅 SCANNING: {dt_base.strftime('%B %d, %Y')} [{SITE_NAME}]")
            log("-" * 75)

            t_start = datetime.datetime(year, month, day, config["start_h"], 0, 0, tzinfo=ZoneInfo("UTC"))
            
            alignment_trigger_time = None
            alignment_sun_alt = None
            alignment_regulus_alt = None
            
            body_data_at_lock = {name: {"az": None, "alt": None} for name in TARGET_PLANETS}
            prev_reg_az = None

            # 1. Primary Scan: Find Regulus intersection with target azimuth
            for s in range(0, config["scan_h"] * 3600, TIME_STEP_SECONDS): 
                dt = t_start + datetime.timedelta(seconds=s)
                t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                
                # Regulus Tracking
                reg_pos = site.at(t_sec).observe(regulus).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                curr_reg_az, curr_reg_alt = reg_pos[1].degrees, reg_pos[0].degrees
                
                if prev_reg_az is not None:
                    # Target Azimuth Intersection Logic
                    if (prev_reg_az <= site_target_azimuth < curr_reg_az) or (prev_reg_az >= site_target_azimuth > curr_reg_az):
                        alignment_trigger_time = t_sec.utc_datetime().astimezone(local_tz)
                        alignment_regulus_alt = curr_reg_alt
                        
                        sun_alt = site.at(t_sec).observe(sun).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[0].degrees
                        alignment_sun_alt = sun_alt

                        # Record positions of all planets exactly at the moment Regulus locks
                        for b_name, b_obj in TARGET_PLANETS.items():
                            b_pos = site.at(t_sec).observe(b_obj).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                            body_data_at_lock[b_name]["az"] = b_pos[1].degrees
                            body_data_at_lock[b_name]["alt"] = b_pos[0].degrees
                        break # Intersection found, stop primary scan for this day

                prev_reg_az = curr_reg_az

            # 2. Secondary Scan: Mars Temporal Conjunction
            mars_cross_time = None
            mars_cross_alt = None
            prev_mars_az = None
            
            for s in range(0, config["scan_h"] * 3600, TIME_STEP_SECONDS):
                dt = t_start + datetime.timedelta(seconds=s)
                t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                m_pos = site.at(t_sec).observe(TARGET_PLANETS['Mars']).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                curr_mars_az = m_pos[1].degrees
                
                if prev_mars_az is not None:
                     if (prev_mars_az <= site_target_azimuth < curr_mars_az) or (prev_mars_az >= site_target_azimuth > curr_mars_az):
                        mars_cross_time = t_sec.utc_datetime().astimezone(local_tz)
                        mars_cross_alt = m_pos[0].degrees
                        break
                prev_mars_az = curr_mars_az

            # --- OUTPUT COMPILATION FOR THIS DAY ---
            if alignment_trigger_time:
                log(f" 🏹 REGULUS ANCHOR LOCK: {alignment_trigger_time.strftime('%H:%M:%S')} Local (Hits {site_target_azimuth}° target axis)")
                log(f"    Sun Altitude     : {alignment_sun_alt:+.4f}°")
                
                delta_mars = 999999
                if mars_cross_time:
                    delta_mars = (mars_cross_time - alignment_trigger_time).total_seconds()
                    direction = "AFTER" if delta_mars > 0 else "BEFORE"
                    d_m, d_s = divmod(abs(delta_mars), 60)
                    d_h, d_m = divmod(d_m, 60)
                    log(f" 🔴 MARS CONJUNCTION : Mars hits axis {int(d_h)}h {int(d_m)}m {int(d_s)}s {direction} Regulus (Alt: {mars_cross_alt:+.2f}°)")

                candidates.append({
                    "site_name": SITE_NAME,
                    "date": dt_base,
                    "trigger_utc": alignment_trigger_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "sun_alt": alignment_sun_alt,
                    "reg_alt": alignment_regulus_alt,
                    "mars_alt": mars_cross_alt if mars_cross_time else 0.0,
                    "mars_delta_sec": delta_mars,
                    
                    # Store Pillar of Light planetary positions at exact lock
                    "venus_az": body_data_at_lock['Venus']['az'],
                    "venus_alt": body_data_at_lock['Venus']['alt'],
                    "jupiter_az": body_data_at_lock['Jupiter']['az'],
                    "jupiter_alt": body_data_at_lock['Jupiter']['alt'],
                    "moon_az": body_data_at_lock['Moon']['az'],
                    "moon_alt": body_data_at_lock['Moon']['alt'],
                    "pluto_az": body_data_at_lock['Pluto']['az'],
                    "pluto_alt": body_data_at_lock['Pluto']['alt']
                })
            else:
                log(f" 🏹 REGULUS ANCHOR LOCK: Regulus never crossed target axis {site_target_azimuth}°.")
            log("") 

    return candidates, "\n".join(output_buffer)

if __name__ == "__main__":
    print("=====================================================================")
    print("         [PROJECT REGULUS] - GLOBAL PILLAR SCANNER v4.1")
    print("=====================================================================")
    print(f"TARGET YEARS SET TO: {TARGET_YEARS}")
    print(f"CORES ENGAGED      : {multiprocessing.cpu_count()}")
    print(f"SITES LOADED       : {len(TARGET_SITES)} monument(s)")
    for site_name, config in TARGET_SITES.items():
        print(f"  ↳ {site_name} (Target Axis: {config['azimuth']}° | TZ: {config['tz']})")
    print(f"TIME STEP          : {TIME_STEP_SECONDS} seconds")
    print("\nWARNING: Multiprocessing initialized across multiple sites...")
    print("=====================================================================\n")

    global_candidates = []
    tasks = []
    for y in TARGET_YEARS:
        for site_name, site_config in TARGET_SITES.items():
            tasks.append((y, site_name, site_config))
            
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(scan_single_location_year, task[0], task[1], task[2]): task for task in tasks}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Global Sites"):
            try:
                candidates, log_output = future.result()
                global_candidates.extend(candidates)
                # print(log_output) # Uncomment if you want raw logs in console
            except Exception as exc:
                print(f"!!! FATAL ERROR in worker task: {exc}")

    # -----------------------------------------------------------------------
    # EXPORTING PILLAR OF LIGHT DATA (ALL PLANETS)
    # -----------------------------------------------------------------------
    csv_filename = "Regulus_Global_MultiSite_Pillar_Scan_2026.csv"
    
    fieldnames = [
        "site_name", "date", "trigger_utc", "sun_alt", "reg_alt", 
        "mars_alt", "mars_delta_sec",
        "venus_az", "venus_alt",
        "jupiter_az", "jupiter_alt",
        "moon_az", "moon_alt",
        "pluto_az", "pluto_alt"
    ]
    
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(global_candidates)

    # -----------------------------------------------------------------------
    # ANALYSIS ENGINE: HUNTING THE GRAVITATIONAL LOCK
    # -----------------------------------------------------------------------
    print("="*85)
    print("\n[ ENGINE CONCLUSION: THE GIZA 'PILLAR OF LIGHT' ]")
    
    best_giza_match = None
    min_mars_delta_giza = 999999
    
    for c in global_candidates:
        if "Giza" in c['site_name']:
            if abs(c['mars_delta_sec']) < abs(min_mars_delta_giza):
                min_mars_delta_giza = c['mars_delta_sec']
                best_giza_match = c

    if best_giza_match:
        print(f"🏆 GIZA'S BEST GRAVITATIONAL ALIGNMENT:")
        print(f"   Date            : {best_giza_match['date'].strftime('%B %d, %Y')}")
        print(f"   Lock Time       : {best_giza_match['trigger_utc']} (Local Cairo Time)")
        print(f"   Sun Status      : {best_giza_match['sun_alt']:+.2f}° (Visibility condition)")
        print(f"   Mars Offset     : {abs(best_giza_match['mars_delta_sec'])/3600:.2f} hours from Regulus")
        print("\n   [PILLAR PLANETARY AZIMUTHS AT EXACT LOCK (Target: 90°)]")
        print(f"   Regulus : 90.00° (Anchor)")
        print(f"   Venus   : {best_giza_match['venus_az']:.2f}°")
        print(f"   Jupiter : {best_giza_match['jupiter_az']:.2f}°")
        print(f"   Moon    : {best_giza_match['moon_az']:.2f}°")
        print(f"   Pluto   : {best_giza_match['pluto_az']:.2f}°")
    else:
        print("System didn't find Giza in this batch.")
        
    print("="*85)
    print(f"\n📊 [DATA EXPORT COMPLETED] Global pillar data saved to: {csv_filename}")