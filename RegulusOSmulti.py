import datetime
import csv
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from zoneinfo import ZoneInfo
from skyfield.api import load, Star, wgs84
from skyfield import almanac

'''
=====================================================================
GLOSSARY, LEGEND & SCIENTIFIC DERIVATIONS
=====================================================================

1. OPTICAL & ATMOSPHERIC PARAMETERS:
   - NELM (Naked-Eye Limiting Magnitude): The brightness threshold where 
     sky background luminance washes out celestial objects (-2.72° Sun Alt).
   - RED_STAR_ALT: The altitude threshold (~7.5°) where atmospheric 
     extinction shifts stellar spectra to a reddish-orange tint.
     Formula: Δ(B-V) ≈ 0.15 * X (where Airmass X = 1/sin(altitude)).
   - IDEAL_SUN_ALT: The precise pre-dawn target (-6.5°). Distinct from 
     standard Civil Twilight (-6.0°) to isolate the fleeting 2-3 minute 
     temporal window required for the geodetic lock.
     
2. GEODETIC PARAMETERS:
   - MONUMENT_ALIGNMENT_AZ: The target azimuth (e.g., 90.0° for True East). 
     Acts as the geodetic anchor for the monument's architectural 
     orientation, serving as the alignment target for celestial events.

3. ORBITAL & TEMPORAL MECHANICS:
   - MARS_DELTA_SEC: The temporal divergence (in seconds) between Mars 
     crossing the target azimuth and the primary Regulus alignment lock. 
     Used to measure the strength of multi-planetary orbital resonance.
   - PRIME METRIC: A harmonic resonance check evaluating if the elapsed 
     days from the global epoch (Dec 21, 2012) form a prime number.
   - LST (Local Sidereal Time): Used during the SkyMap rendering to sync 
     the local meridian with deep-sky anchors (Orion, Galactic Center).
=====================================================================
'''

# =====================================================================
# GLOBAL USER INPUT ZONE & CONFIGURATION
# =====================================================================
# 👇 ================================================================ 👇
TARGET_YEARS = [2026] # List of years to scan. 
# Format : [2024, 2028, 2036] or [2024], or range(2024, 2030) for a range of years.

# ENGINE OPTIMIZATION
# Scanning time step in seconds (1 = MAXIMUM PRECISION) 
# you may use 1 second for high precision, or 5-10+ seconds for faster scans with less precision.
# WARNING: Values > 1s decrease temporal resolution, which may cause 'overshoot' of the precise alignment lock.
# test it with 5-10s for a quick scan, then refine with 1s for the final evaluation.
TIME_STEP_SECONDS = 10

# =====================================================================
# MULTI-SITE GEODETIC CONFIGURATION
# =====================================================================
# Engine will parallel-process all active sites listed below.
# You can add or remove sites here. Make sure to provide the specific azimuth target for each monument.
TARGET_SITES = {
    "Great Sphinx of Giza": {
        "lat": 29.975234, "lon": 31.137772, "elev": 20.0, "tz": "Africa/Cairo", "azimuth": 90.0
    },
    "Angkor Wat": {
        "lat": 13.412469, "lon": 103.866768, "elev": 60.0, "tz": "Asia/Phnom_Penh", "azimuth": 90.0 
    },
    "Stonehenge": {
        "lat": 51.178882, "lon": -1.826215, "elev": 100.0, "tz": "Europe/London", "azimuth": 51.0 # Summer Solstice Sunrise Axis
    },
    "Teotihuacan (Avenue of the Dead)": {
        "lat": 19.692500, "lon": -98.843800, "elev": 2280.0, "tz": "America/Mexico_City", "azimuth": 15.25 # Eastern deviation axis
    },
    "Chichen Itza (El Castillo)": {
        "lat": 20.683056, "lon": -88.568611, "elev": 30.0, "tz": "America/Cancun", "azimuth": 21.0
    }
}

# ATMOSPHERIC CONDITIONS (Used for light refraction calculations)
ATM_TEMPERATURE = 13.0 # Degrees Celsius adjust this to your site conditions.
ATM_PRESSURE = 1013.0  # Hectopascals (mbar) adjust this to your site conditions.

# CELESTIAL BODIES TO TRACK - you can add more planets or celestial bodies here. The keys are the names used in the code.
# Note: NASA DE421 ephemeris requires 'barycenter' tag for gas giants. In line 112, you can switch to 'de430.bsp' or 'de440s.bsp' for more recent ephemerides if needed.
# Type in console: print(eph) to see all available ephemeris identifiers.
TARGET_PLANETS = {
    'mars': 'mars',
    'venus': 'venus',
    'moon': 'moon',
    'jupiter': 'jupiter barycenter',
    'saturn': 'saturn barycenter',
    'mercury': 'mercury',
    'neptune': 'neptune barycenter',
    'uranus': 'uranus barycenter',
    'pluto': 'pluto barycenter'
}

# SCAN CONFIGURATION (SNIPER MODE)
# here you can change or add more months and days to scan.
# Format: TARGET_SCANS = {month_number: {"days": [day1, day2, ...], "start_h": start_hour, "scan_h": scan_duration_hours}, ...}
TARGET_SCANS = {
    9: {"days": [22, 23, 24, 25, 26], "start_h": 0, "scan_h": 24},
    11: {"days": [2, 3, 4, 5, 6], "start_h": 0, "scan_h": 24}
}

# CRITICAL OPTICAL THRESHOLDS
NELM_SUN_ALT = -2.72          # Threshold for Daylight Washout for Regulus - if different planets/celestial bodies are used, this may need adjustment
IDEAL_SUN_ALT = -6.5          # Pre-dawn target - adjust where you want the sun to be for optimal extinction (e.g., -6.0° for Civil Twilight, -6.5° for "just" before the dawn red phase)

# Color shift altitude threshold (ATMOSPHERIC GRADIENT WINDOW)
RED_STAR_MIN = 4.0            # Lower boundary for Red Star phase (deep red, highly extinguished)
RED_STAR_MAX = 8.0            # Upper boundary for Red Star phase (transitioning to orange)
# 👆 ================================================================ 👆

# =====================================================================
# TYPE COERCION FOR TARGET YEARS
# =====================================================================
if isinstance(TARGET_YEARS, int):
    TARGET_YEARS = [TARGET_YEARS]

# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================
def is_prime(n):
    """Evaluates whether the given number of days is a prime number."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def calculate_intercept_time(t_current, az_current, target_az, site=None):
    """Predicts exact time of intercept based on Earth's rotation (15 deg/hr -> 240s/deg)."""
    diff_az = az_current - target_az
    seconds_to_intercept = diff_az * 240.0
    intercept_time = t_current - datetime.timedelta(seconds=seconds_to_intercept)
    return intercept_time

# =====================================================================
# EPHEMERIS & TARGET SETUP
# =====================================================================
ts = load.timescale()
eph = load('de421.bsp') # 👈 here you can switch to 'de430.bsp' or 'de440s.bsp' for more recent ephemerides if needed.
earth, sun = eph['earth'], eph['sun']

planets = {name: eph[target] for name, target in TARGET_PLANETS.items()}

# Fixed stellar anchor points
regulus = Star(ra_hours=(10, 8, 22.311), dec_degrees=(11, 58, 1.95))
alnilam = Star(ra_hours=(5, 36, 12.81), dec_degrees=(-1, 12, 6.9))
sgra = Star(ra_hours=(17, 45, 40.04), dec_degrees=(-29, 0, 28.1))
sirius = Star(ra_hours=(6, 45, 8.9), dec_degrees=(-16, 42, 58))
vega = Star(ra_hours=(18, 36, 56.3), dec_degrees=(38, 47, 1))

start_date = datetime.date(2012, 12, 21)

# =====================================================================
# CORE ENGINE - MULTIPROCESSING WRAPPER
# =====================================================================
def scan_single_location_year(TARGET_YEAR, SITE_NAME, SITE_CONFIG):
    """Processes a single year for a specific geographical site configuration."""
    year_candidates = []
    output_buffer = []
    
    
    def log(msg):
        output_buffer.append(msg)

    # Initialize site-specific variables
    SITE_LAT = SITE_CONFIG["lat"]
    SITE_LON = SITE_CONFIG["lon"]
    SITE_ELEVATION = SITE_CONFIG["elev"]
    MONUMENT_ALIGNMENT_AZ = SITE_CONFIG["azimuth"]
    OBSERVATION_TZ = ZoneInfo(SITE_CONFIG["tz"])
    
    site = earth + wgs84.latlon(SITE_LAT, SITE_LON, elevation_m=SITE_ELEVATION)
    lon_hours = SITE_LON / 15.0

    log("="*75)
    log(f"                 SCAN MODULE - YEAR: {TARGET_YEAR} | SITE: {SITE_NAME}")
    log(f"                 GEODETIC ANCHOR AZIMUTH: {MONUMENT_ALIGNMENT_AZ}°")
    log("="*75)

    for month, config in sorted(TARGET_SCANS.items()):
        
        for day in config["days"]:
            try:
                current_date = datetime.date(TARGET_YEAR, month, day)
            except ValueError:
                continue
            
            days_delta = (current_date - start_date).days
            prime_status = "PRIME NUMBER" if is_prime(days_delta) else "COMPOSITE NUMBER"
            
            log(f"\n📅 SCANNING: {current_date.strftime('%B %d, %Y')} [{SITE_NAME}]")
            log(f"  ↳ Days from 2012-12-21: {days_delta} → {prime_status}")
            log("-" * 75)
            
            t_start = datetime.datetime(TARGET_YEAR, month, day, config["start_h"], 0, 0)
            
            # State Trackers
            time_nelm = time_lock = time_reg_rise = time_red_star = time_red_star_end = None
            time_lock_tsec = None
            sun_alt_at_lock = reg_alt_at_lock = reg_az_at_rise = 0.0
            sun_alt_at_red = reg_az_at_red = reg_alt_at_red = 0.0
            
            time_mars_cross = None
            mars_alt_at_cross = 0.0
            mars_az_at_cross = 0.0
            
            body_data_at_lock = {name: None for name in TARGET_PLANETS}
            body_data_at_red = {name: None for name in TARGET_PLANETS}
            prev_reg_az = prev_reg_alt = prev_mars_az = None

            for s in range(0, config["scan_h"] * 3600, TIME_STEP_SECONDS): 
                dt = t_start + datetime.timedelta(seconds=s)
                t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                
                # --- SUN TRACKING ---
                sun_alt = site.at(t_sec).observe(sun).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[0].degrees
                
                if time_nelm is None and sun_alt >= NELM_SUN_ALT:
                    time_nelm = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)

                # --- REGULUS TRACKING ---
                reg_pos = site.at(t_sec).observe(regulus).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                curr_reg_az, curr_reg_alt = reg_pos[1].degrees, reg_pos[0].degrees
                
                if time_reg_rise is None and prev_reg_alt is not None:
                    if prev_reg_alt < 0.0 <= curr_reg_alt:
                        time_reg_rise = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)
                        reg_az_at_rise = curr_reg_az

                if time_red_star is None and prev_reg_alt is not None:
                    if prev_reg_alt < RED_STAR_MIN <= curr_reg_alt:
                        time_red_star = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)
                        sun_alt_at_red = sun_alt
                        reg_az_at_red = curr_reg_az
                        reg_alt_at_red = curr_reg_alt
                        
                        for name, body in planets.items():
                            body_data_at_red[name] = site.at(t_sec).observe(body).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)

                # --- RED STAR EXIT TRACKING (8.0 MAX) ---
                if time_red_star_end is None and prev_reg_alt is not None:
                    if prev_reg_alt < RED_STAR_MAX <= curr_reg_alt:
                        time_red_star_end = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)

                # --- MARS TRACKING ---
                mars_pos = site.at(t_sec).observe(planets['mars']).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                curr_mars_az, curr_mars_alt = mars_pos[1].degrees, mars_pos[0].degrees
                
                if time_mars_cross is None and prev_mars_az is not None:
                    if (MONUMENT_ALIGNMENT_AZ - prev_mars_az) % 360 < (curr_mars_az - prev_mars_az) % 360:
                        time_mars_cross = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)
                        mars_alt_at_cross = curr_mars_alt
                        mars_az_at_cross = curr_mars_az

                # --- MAIN ALIGNMENT LOCK ---
                if time_lock is None and prev_reg_az is not None:
                    if (MONUMENT_ALIGNMENT_AZ - prev_reg_az) % 360 < (curr_reg_az - prev_reg_az) % 360:
                        time_lock = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)
                        time_lock_tsec = t_sec
                        reg_alt_at_lock = curr_reg_alt
                        sun_alt_at_lock = sun_alt
                        
                        for name, body in planets.items():
                            body_data_at_lock[name] = site.at(t_sec).observe(body).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)

                prev_reg_az, prev_reg_alt = curr_reg_az, curr_reg_alt
                prev_mars_az = curr_mars_az
                
                if time_lock and time_nelm and time_red_star:
                    if month == 9:
                        break
                    elif month == 11 and time_mars_cross:
                        break 
                
            # ==================== DAILY REPORT ====================
            if time_reg_rise:
                log(f" 🌅 REGULUS RISING : {time_reg_rise.strftime('%H:%M:%S')} Local (Azimuth: {reg_az_at_rise:.4f}°)")

            if time_red_star:
                night_status = "🌙 Pitch Black" if sun_alt_at_red < -18.0 else "Twilight"
                log(f" [TRIGGER]🔴 RED STAR LIMIT : {time_red_star.strftime('%H:%M:%S')} Local | Regulus Az: {reg_az_at_red:.4f}° | Regulus Alt: {reg_alt_at_red:+.4f}° | Sun Alt: {sun_alt_at_red:+.4f}° ({night_status})")
                
                if time_red_star_end:
                    red_duration = (time_red_star_end - time_red_star).total_seconds()
                    m, s = divmod(int(red_duration), 60)
                    log(f" ⏱️ RED PHASE DURATION: {m}m {s}s (from {RED_STAR_MIN}° to {RED_STAR_MAX}°)")
                for body_name in body_data_at_red:
                    if body_data_at_red[body_name]:
                        log(f"    ↳ {body_name.upper()} at Trigger: Azimuth {body_data_at_red[body_name][1].degrees:.4f}° | Alt {body_data_at_red[body_name][0].degrees:+.4f}°")
                        

            if time_lock:
                is_visible = False
                delta = None
                
                moon_data = body_data_at_lock.get('moon')
                moon_illum = almanac.fraction_illuminated(eph, 'moon', time_lock_tsec) * 100.0 if moon_data else 0.0
                moon_alt = moon_data[0].degrees if moon_data else -90.0

                if sun_alt_at_lock >= NELM_SUN_ALT:
                    status = "❌ INVISIBLE (Washed out by daylight)"
                elif moon_alt > 0.0 and moon_illum > 75.0:
                    status = f"❌ INVISIBLE (Lunar Washout: Moon at {moon_alt:+.1f}°, {moon_illum:.1f}%)"
                elif sun_alt_at_lock < -18.0:
                    status = "🌙 NIGHTTIME (Pitch black, no \"just\" before dawn)"
                else:
                    is_visible = True
                    if time_nelm:
                        delta = (time_nelm - time_lock).total_seconds()
                        minutes, seconds = int(abs(delta) // 60), int(abs(delta) % 60)
                        status = f"✅ VISIBLE up to {minutes}m {seconds}s after alignment" if delta > 0 else f"❌ INVISIBLE (Faded {minutes}m {seconds}s BEFORE alignment)"
                        if delta <= 0: is_visible = False
                
                mars_delta_csv = "N/A"
                if time_mars_cross and time_lock:
                    t1 = time_lock.replace(year=2000, month=1, day=1)
                    t2 = time_mars_cross.replace(year=2000, month=1, day=1)
                    mars_delta_csv = (t1 - t2).total_seconds()

                candidate_data = {
                    "site_name": SITE_NAME,
                    "date": current_date,
                    "sun_alt": sun_alt_at_lock,
                    "reg_alt": reg_alt_at_lock,
                    "is_visible": is_visible,
                    "delta": delta,
                    "moon_alt": moon_alt,
                    "moon_illum": moon_illum,
                    "saturn_az": body_data_at_lock['saturn'][1].degrees if body_data_at_lock.get('saturn') else None,
                    "saturn_alt": body_data_at_lock['saturn'][0].degrees if body_data_at_lock.get('saturn') else None,
                    "mercury_az": body_data_at_lock['mercury'][1].degrees if body_data_at_lock.get('mercury') else None,
                    "mercury_alt": body_data_at_lock['mercury'][0].degrees if body_data_at_lock.get('mercury') else None,
                    "venus_az": body_data_at_lock['venus'][1].degrees if body_data_at_lock.get('venus') else None,
                    "venus_alt": body_data_at_lock['venus'][0].degrees if body_data_at_lock.get('venus') else None,
                    "mars_az": body_data_at_lock['mars'][1].degrees if body_data_at_lock.get('mars') else None,
                    "mars_alt": body_data_at_lock['mars'][0].degrees if body_data_at_lock.get('mars') else None,
                    "jupiter_az": body_data_at_lock['jupiter'][1].degrees if body_data_at_lock.get('jupiter') else None,
                    "jupiter_alt": body_data_at_lock['jupiter'][0].degrees if body_data_at_lock.get('jupiter') else None,
                    "neptune_az": body_data_at_lock['neptune'][1].degrees if body_data_at_lock.get('neptune') else None,
                    "neptune_alt": body_data_at_lock['neptune'][0].degrees if body_data_at_lock.get('neptune') else None,
                    "uranus_az": body_data_at_lock['uranus'][1].degrees if body_data_at_lock.get('uranus') else None,
                    "uranus_alt": body_data_at_lock['uranus'][0].degrees if body_data_at_lock.get('uranus') else None,
                    "pluto_az": body_data_at_lock['pluto'][1].degrees if body_data_at_lock.get('pluto') else None,
                    "pluto_alt": body_data_at_lock['pluto'][0].degrees if body_data_at_lock.get('pluto') else None,
                    "mars_delta_sec": mars_delta_csv
                }
                year_candidates.append(candidate_data)
                
                log(f" 🏹 ALIGNMENT POINT: {time_lock.strftime('%H:%M:%S')} Local (Regulus hits {MONUMENT_ALIGNMENT_AZ}° target axis)")
                log(f"    Altitudes    : Sun: {sun_alt_at_lock:+.4f}° | Regulus: {reg_alt_at_lock:+.4f}°")
                log(f"    Eye Status   : {status}")
                
                log(f" 🌌 GLOBAL SKYMAP (At moment of {MONUMENT_ALIGNMENT_AZ}° Alignment):")
                
                orion_pos = site.at(time_lock_tsec).observe(alnilam).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                log(f"    Orion's Belt : Az: {orion_pos[1].degrees:.4f}° | Alt: {orion_pos[0].degrees:+.4f}°")
                
                gc_pos = site.at(time_lock_tsec).observe(sgra).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                log(f"    Galactic Ctr : Alt: {gc_pos[0].degrees:+.4f}°")
                
                sirius_pos = site.at(time_lock_tsec).observe(sirius).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                log(f"    Sirius       : Az: {sirius_pos[1].degrees:.4f}° | Alt: {sirius_pos[0].degrees:+.4f}°")
    
                vega_pos = site.at(time_lock_tsec).observe(vega).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                log(f"    Vega         : Az: {vega_pos[1].degrees:.4f}° | Alt: {vega_pos[0].degrees:+.4f}°")
                
                if body_data_at_lock.get('venus'):
                    log(f"    Venus        : Az: {body_data_at_lock['venus'][1].degrees:.4f}° | Alt: {body_data_at_lock['venus'][0].degrees:+.4f}°")
                if body_data_at_lock.get('mars'):
                    log(f"    Mars         : Az: {body_data_at_lock['mars'][1].degrees:.4f}° | Alt: {body_data_at_lock['mars'][0].degrees:+.4f}°")
                if body_data_at_lock.get('jupiter'):
                    log(f"    Jupiter      : Az: {body_data_at_lock['jupiter'][1].degrees:.4f}° | Alt: {body_data_at_lock['jupiter'][0].degrees:+.4f}°")
                if body_data_at_lock.get('neptune'):
                    log(f"    Neptune      : Az: {body_data_at_lock['neptune'][1].degrees:.4f}° | Alt: {body_data_at_lock['neptune'][0].degrees:+.4f}°")
                if body_data_at_lock.get('uranus'):
                    log(f"    Uranus       : Az: {body_data_at_lock['uranus'][1].degrees:.4f}° | Alt: {body_data_at_lock['uranus'][0].degrees:+.4f}°")
                if body_data_at_lock.get('pluto'):
                    log(f"    Pluto        : Az: {body_data_at_lock['pluto'][1].degrees:.4f}° | Alt: {body_data_at_lock['pluto'][0].degrees:+.4f}°")
                if body_data_at_lock.get('saturn'):
                    log(f"    Saturn       : Az: {body_data_at_lock['saturn'][1].degrees:.4f}° | Alt: {body_data_at_lock['saturn'][0].degrees:+.4f}°")
                if body_data_at_lock.get('mercury'):
                    log(f"    Mercury      : Az: {body_data_at_lock['mercury'][1].degrees:.4f}° | Alt: {body_data_at_lock['mercury'][0].degrees:+.4f}°")
                    
                sun_pos_at_lock = site.at(time_lock_tsec).observe(sun).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                log(f" ☀️ SUN STATUS     : Az: {sun_pos_at_lock[1].degrees:.4f}° | Alt: {sun_pos_at_lock[0].degrees:+.4f}°")
                
                if body_data_at_lock.get('moon'):
                    moon_illum = almanac.fraction_illuminated(eph, 'moon', time_lock_tsec) * 100.0
                    log(f" 🌕 LUNAR STATUS : Az: {body_data_at_lock['moon'][1].degrees:.4f}° | Alt: {body_data_at_lock['moon'][0].degrees:+.4f}° | Illum: {moon_illum:.1f}%")
            else:
                log(f"    ⚠️ Regulus did not reach {MONUMENT_ALIGNMENT_AZ}° target axis in scan window.")

            if time_mars_cross:
                log(f" 🔴 MARS CROSSING: Hits {MONUMENT_ALIGNMENT_AZ}° target azimuth at {time_mars_cross.strftime('%H:%M:%S')} (Alt: {mars_alt_at_cross:+.2f}°)")
                
                if time_lock:
                    t1 = time_lock.replace(year=2000, month=1, day=1)
                    t2 = time_mars_cross.replace(year=2000, month=1, day=1)
                    
                    diff_seconds = (t1 - t2).total_seconds()
                    abs_diff_sec = int(abs(diff_seconds))
                    h, remainder = divmod(abs_diff_sec, 3600)
                    m, s = divmod(remainder, 60)
                    
                    before_after = "BEFORE" if diff_seconds > 0 else "AFTER"
                    
                    if h > 0: time_str = f"{h}h {m}m {s}s"
                    elif m > 0: time_str = f"{m}m {s}s"
                    else: time_str = f"{s} seconds"
                    
                    log(f"    ⚠️ CONJUNCTION ALERT: Mars crosses exact azimuth {time_str} {before_after} Regulus!")
                else:
                    log(f"    ℹ️ Mars crossed target axis, but Regulus did not align in this scan window.")

    return year_candidates, "\n".join(output_buffer)

# =====================================================================
# SYSTEM MAIN BLOCK & ENGINE STARTUP
# =====================================================================
if __name__ == '__main__':
    print("=====================================================================")
    print("         [PROJECT REGULUS] - GLOBAL MULTI-SITE SCANNER v3.1")
    print("=====================================================================")
    print(f"TARGET YEARS SET TO: {TARGET_YEARS}")
    print(f"CORES ENGAGED      : {multiprocessing.cpu_count()}")
    print(f"SITES LOADED       : {len(TARGET_SITES)} monument(s)")
    for site_name, config in TARGET_SITES.items():
        print(f"  ↳ {site_name} (Target Axis: {config['azimuth']}°)")
    print(f"SCANS ACTIVE       : Months {sorted(list(TARGET_SCANS.keys()))}")
    print(f"TIME STEP          : {TIME_STEP_SECONDS} seconds")
    print("\nWARNING: Multiprocessing initialized across multiple sites. Please wait for the final compiled log...")
    print("=====================================================================\n")

    global_candidates = []
    
    # Generate tasks for every combination of Year + Site
    tasks = []
    for y in TARGET_YEARS:
        for site_name, site_config in TARGET_SITES.items():
            tasks.append((y, site_name, site_config))
            
    with ProcessPoolExecutor() as executor:
        # Submit all tasks to the parallel processor
        futures = {executor.submit(scan_single_location_year, task[0], task[1], task[2]): task for task in tasks}
        
        for future in as_completed(futures):
            try:
                candidates, log_output = future.result()
                global_candidates.extend(candidates)
                print(log_output)
            except Exception as e:
                task_info = futures[future]
                print(f"❌ Error processing Year {task_info[0]} for Site {task_info[1]}: {e}")

    # =====================================================================
    # CSV INITIALIZATION & SAVING
    # =====================================================================
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"regulus_global_scan_{timestamp}.csv"

    # Sort by Date then by Site Name
    global_candidates.sort(key=lambda x: (x['date'], x['site_name']))

    fmt = lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else x
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Site_Name', 'Date', 'Sun_Alt', 'Deviation_From_Ideal', 'Regulus_Alt', 
            'Is_Visible', 'Visibility_Delta_Sec',
            'Moon_Alt', 'Moon_Illum_%', 
            'Venus_Az', 'Venus_Alt', 
            'Mars_Az', 'Mars_Alt', 
            'Jupiter_Az', 'Jupiter_Alt',
            'Neptune_Az', 'Neptune_Alt',
            'Saturn_Az', 'Saturn_Alt',
            'Mercury_Az', 'Mercury_Alt',
            'Uranus_Az', 'Uranus_Alt',
            'Pluto_Az', 'Pluto_Alt',
            'Mars_Delta_Sec'
        ])
        
        for c in global_candidates:
            dev = abs(c['sun_alt'] - IDEAL_SUN_ALT)
            saturn_az = c.get('saturn_az')
            saturn_alt = c.get('saturn_alt')
            mercury_az = c.get('mercury_az')
            mercury_alt = c.get('mercury_alt')
            uranus_az = c.get('uranus_az')
            uranus_alt = c.get('uranus_alt')
            pluto_az = c.get('pluto_az')
            pluto_alt = c.get('pluto_alt')
            writer.writerow([
                c['site_name'], c['date'].strftime('%Y-%m-%d'), fmt(c['sun_alt']), fmt(dev), fmt(c['reg_alt']),
                c['is_visible'], fmt(c['delta']) if c['delta'] is not None else "N/A",
                fmt(c['moon_alt']), fmt(c['moon_illum']), fmt(c['venus_az']), fmt(c['venus_alt']),
                fmt(c['mars_az']), fmt(c['mars_alt']), fmt(c['jupiter_az']), fmt(c['jupiter_alt']),
                fmt(c['neptune_az']), fmt(c['neptune_alt']), 
                fmt(saturn_az) if saturn_az is not None else "N/A", fmt(saturn_alt) if saturn_alt is not None else "N/A",
                fmt(mercury_az) if mercury_az is not None else "N/A", fmt(mercury_alt) if mercury_alt is not None else "N/A",
                fmt(uranus_az) if uranus_az is not None else "N/A", fmt(uranus_alt) if uranus_alt is not None else "N/A",
                fmt(pluto_az) if pluto_az is not None else "N/A", fmt(pluto_alt) if pluto_alt is not None else "N/A", fmt(c['mars_delta_sec'])
            ])
            
    # =====================================================================
    # FINAL EVALUATION
    # =====================================================================
    print("\n" + "="*85)
    print("         PROJECT REGULUS - GLOBAL DYNAMIC EVALUATION v3.1 ULTIMATE")
    print("="*85)
    best_match = None
    best_score = -9999

    for c in global_candidates:
        if c['is_visible']:
            score = -abs(c['sun_alt'] - IDEAL_SUN_ALT) 
            date_str = c['date'].strftime('%B %d, %Y')
            site_display = c['site_name'][:20]
            print(f"• [{site_display:<20}] {date_str:<18} : ✅ Valid Window | Sun alt: {c['sun_alt']:+.4f}° | Score: {score:+.4f}")
            if score > best_score:
                best_score = score
                best_match = c

    print("\n[ ENGINE CONCLUSION : OPTIMAL RED-SHIFT SELECTION ACROSS ALL SITES ]")
    if best_match:
        print(f"🏆 OVERALL WINNER: {best_match['site_name']}")
        print(f"   Date            : {best_match['date'].strftime('%B %d, %Y')}")
        print(f"   Sun Altitude    : {best_match['sun_alt']:+.4f}°")
        print(f"   Target Zone     : {IDEAL_SUN_ALT}° (Max Extinction)")
        print(f"   Deviation       : {abs(best_score):.4f}° from ideal")
    else:
        print("System found NO viable timeline for any site in this scan segment.")
    print("="*85)
    print(f"\n📊 [DATA EXPORT COMPLETED] Global scan results were successfully saved to: {csv_filename}")