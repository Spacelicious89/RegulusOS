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
   - RED_STAR_WINDOW (4.0° - 8.0°): The specific altitude bounds where atmospheric 
     extinction shifts stellar spectra to a deep reddish-orange tint.
     Formula: Δ(B-V) ≈ 0.15 * X (where Airmass X = 1/sin(altitude)).
   - IDEAL_SUN_ALT: The precise pre-dawn target (-6.5°). Distinct from 
     standard Civil Twilight (-6.0°) to isolate the fleeting 2-3 minute 
     temporal window required for the geodetic lock.
   - ATM_REFRACTION (Temperature & Pressure): Used to calculate the 'apparent' 
     altitude of celestial bodies. Atmospheric density bends light, making 
     stars appear higher than their geometric position. Crucial for horizon accuracy.
     
2. GEODETIC PARAMETERS:
   - MONUMENT_ALIGNMENT_AZ: The target azimuth (e.g., 90.0° for True East). 
     Acts as the geodetic anchor for the monument's architectural 
     orientation, serving as the alignment target for celestial events.

3. ORBITAL & TEMPORAL MECHANICS:
   - MARS_DELTA_SEC: The temporal divergence (in seconds) between Mars 
     crossing the target azimuth and the primary Regulus alignment lock. 
     Used to measure the precision of multi-planetary orbital resonance.
   - PRIME METRIC: A harmonic resonance check evaluating if the elapsed 
     days from the global epoch (Dec 21, 2012) form a prime number.
=====================================================================
'''

# =====================================================================
# GLOBAL USER INPUT ZONE & CONFIGURATION
# =====================================================================
# 👇 ================================================================ 👇
TARGET_YEARS = range(2026, 2027)
# ENGINE OPTIMIZATION
# Scanning time step in seconds (1 = MAXIMUM PRECISION) 
# you may use 1 second for high precision, or 5-10+ seconds for faster scans with less precision.
# WARNING: Values > 1s decrease temporal resolution, which may cause 'overshoot' of the precise alignment lock.
# test it with 5-10s for a quick scan, then refine with 1s for the final evaluation.
TIME_STEP_SECONDS = 300

#OPTICAL THRESHOLDS
NELM_SUN_ALT = -2.72          # Threshold for Daylight Washout for Regulus - if different planets/celestial bodies are used, this may need adjustment
MONUMENT_ALIGNMENT_AZ = 90.0  # Geodetic anchor for monument orientation - this is gaze of the sphinx head, adjust if using other monuments
IDEAL_SUN_ALT = -6.5          # Pre-dawn target - adjust where you want the sun to be for optimal extinction (e.g., -6.0° for Civil Twilight, -6.5° )

# Color shift altitude threshold (ATMOSPHERIC GRADIENT WINDOW)
RED_STAR_MIN = 4.0            # Lower boundary for Red Star phase (deep red, highly extinguished)
RED_STAR_MAX = 7.5            # Upper boundary for Red Star phase (transitioning to orange)

# OBSERVATION SITE CONFIGURATION
SITE_NAME = "Great Sphinx of Giza (Head)" # change this to your desired observation site name
SITE_LAT = 29.975234 # change this to your desired observation site latitude
SITE_LON = 31.137772  # change this to your desired observation site longitude
SITE_ELEVATION = 20.0  # change this to your desired observation site elevation
SITE_TZ = "Africa/Cairo" # Change this for other monuments, e.g., "America/Mexico_City"

# ATMOSPHERIC CONDITIONS (Used for light refraction calculations)
ATM_TEMPERATURE = 18.0 # Degrees Celsius adjust this to your local conditions for more accurate refraction calculations
ATM_PRESSURE = 1013.5  # Hectopascals (mbar) adjust this to your "local conditions" for more accurate refraction calculations

# CELESTIAL BODIES TO TRACK - you can add more planets or celestial bodies here.
TARGET_PLANETS = {
    'mars': 'mars barycenter',
    'venus': 'venus',
    'moon': 'moon',
    'jupiter': 'jupiter barycenter',
    'saturn': 'saturn barycenter',
    'mercury': 'mercury',
    'uranus': 'uranus barycenter',
    'neptune': 'neptune barycenter',
    'pluto': 'pluto barycenter'
}

# FULL YEAR SCAN (Juggernaut Mode: 365 days / 24h)
# Scans all 12 months, day by day. 
# I used range(1, 32) which covers days 1 through 31.
# NOTE: February is set to range(1, 29) meaning 28 days. I did this intentionally 
# so the engine doesn't crash on "February 29th" during non-leap years across a 1000-year scan!
TARGET_SCANS = {
    1: {"days": range(1, 32), "start_h": 0, "scan_h": 24},
    2: {"days": range(1, 29), "start_h": 0, "scan_h": 24},
    3: {"days": range(1, 32), "start_h": 0, "scan_h": 24},
    4: {"days": range(1, 31), "start_h": 0, "scan_h": 24},
    5: {"days": range(1, 32), "start_h": 0, "scan_h": 24},
    6: {"days": range(1, 31), "start_h": 0, "scan_h": 24},
    7: {"days": range(1, 32), "start_h": 0, "scan_h": 24},
    8: {"days": range(1, 32), "start_h": 0, "scan_h": 24},
    9: {"days": range(1, 31), "start_h": 0, "scan_h": 24},
    10: {"days": range(1, 32), "start_h": 0, "scan_h": 24},
    11: {"days": range(1, 31), "start_h": 0, "scan_h": 24},
    12: {"days": range(1, 32), "start_h": 0, "scan_h": 24}
}

# 👆 ================================================================ 👆

# =====================================================================
# COERCION FOR TARGET YEARS
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
eph = load('de422.bsp') # 👈 here you can switch to 'de430.bsp' or 'de440s.bsp' for more recent ephemerides if needed.
earth, sun = eph['earth'], eph['sun']

planets = {name: eph[target] for name, target in TARGET_PLANETS.items()}

OBSERVATION_TZ = ZoneInfo(SITE_TZ)
site = earth + wgs84.latlon(SITE_LAT, SITE_LON, elevation_m=SITE_ELEVATION)
lon_hours = SITE_LON / 15.0 # here we convert longitude to hours for sidereal calculations

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
def scan_single_year(TARGET_YEAR):
    year_candidates = []
    output_buffer = []
    mars_azs = []
    mars_alts = []
    
    def log(msg):
        output_buffer.append(msg)

    for month, config in sorted(TARGET_SCANS.items()):
        log("="*75)
        log(f"                 SCAN MODULE - MONTH: {month:02d} / {TARGET_YEAR}")
        log("="*75)
        
        for day in config["days"]:
            current_date = datetime.date(TARGET_YEAR, month, day)
            days_delta = (current_date - start_date).days
            prime_status = "PRIME NUMBER" if is_prime(days_delta) else "COMPOSITE NUMBER"
            
            log(f"\n📅 SCANNING: {current_date.strftime('%B %d, %Y')}")
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

            # --- [VECTORIZATION START] ---
            scan_seconds = config["scan_h"] * 3600
            t_list = [t_start + datetime.timedelta(seconds=s) for s in range(0, scan_seconds, TIME_STEP_SECONDS)]
            t_arr = ts.utc([t.year for t in t_list], [t.month for t in t_list], [t.day for t in t_list], 
                           [t.hour for t in t_list], [t.minute for t in t_list], [t.second for t in t_list])
            
            sun_alts = site.at(t_arr).observe(sun).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[0].degrees
            reg_pos = site.at(t_arr).observe(regulus).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
            reg_alts, reg_azs = reg_pos[0].degrees, reg_pos[1].degrees
            
            planet_data = {}
            for name, body in planets.items():
                pos = site.at(t_arr).observe(body).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                planet_data[name] = {"alt": pos[0].degrees, "az": pos[1].degrees}
            # --- [VECTORIZATION END] ---


            for i in range(len(t_list)):
                t_sec = t_arr[i]
                sun_alt = sun_alts[i]
                curr_reg_az, curr_reg_alt = reg_azs[i], reg_alts[i]
                curr_mars_az, curr_mars_alt = planet_data['mars']["az"][i], planet_data['mars']["alt"][i]
                
                # --- SUN TRACKING ---
                if time_nelm is None and sun_alt >= NELM_SUN_ALT:
                    time_nelm = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)

                # --- REGULUS TRACKING ---
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
                        for name in TARGET_PLANETS:
                            body_data_at_red[name] = site.at(t_sec).observe(planets[name]).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)

                if time_red_star_end is None and prev_reg_alt is not None:
                    if prev_reg_alt < RED_STAR_MAX <= curr_reg_alt:
                        time_red_star_end = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)

                # --- MARS TRACKING ---
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
                        for name in TARGET_PLANETS:
                            body_data_at_lock[name] = (planet_data[name]["alt"][i], planet_data[name]["az"][i])

                
                prev_reg_az, prev_reg_alt = curr_reg_az, curr_reg_alt
                prev_mars_az = curr_mars_az
                
                if time_lock and time_nelm and time_red_star and time_mars_cross: 
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
                moon_alt = moon_data[0] if moon_data else -90.0

                if sun_alt_at_lock >= NELM_SUN_ALT:
                    status = "❌ INVISIBLE (Washed out by daylight)"
                elif moon_alt > 0.0 and moon_illum > 75.0:
                    status = f"❌ INVISIBLE (Lunar Washout: Moon at {moon_alt:+.1f}°, {moon_illum:.1f}%)"
                elif sun_alt_at_lock < -18.0:
                    status = "🌙 NIGHTTIME (Pitch black)"
                else:
                    is_visible = True
                    if time_nelm:
                        delta = (time_nelm - time_lock).total_seconds()
                        minutes, seconds = int(abs(delta) // 60), int(abs(delta) % 60)
                        status = f"✅ VISIBLE for {minutes}m {seconds}s after alignment" if delta > 0 else f"❌ INVISIBLE (Faded {minutes}m {seconds}s BEFORE alignment)"
                        if delta <= 0: is_visible = False
                
                mars_delta_csv = "N/A"
                if time_mars_cross and time_lock:
                    t1 = time_lock.replace(year=2000, month=1, day=1)
                    t2 = time_mars_cross.replace(year=2000, month=1, day=1)
                    mars_delta_csv = (t1 - t2).total_seconds()

                candidate_data = {
                    "date": current_date,
                    "sun_alt": sun_alt_at_lock,
                    "reg_alt": reg_alt_at_lock,
                    "is_visible": is_visible,
                    "delta": delta,
                    "moon_alt": moon_alt,
                    "moon_illum": moon_illum,
                    "venus_az": body_data_at_lock['venus'][1] if body_data_at_lock.get('venus') else None,
                    "venus_alt": body_data_at_lock['venus'][0] if body_data_at_lock.get('venus') else None,
                    "mars_az": body_data_at_lock['mars'][1] if body_data_at_lock.get('mars') else None,
                    "mars_alt": body_data_at_lock['mars'][0] if body_data_at_lock.get('mars') else None,
                    "jupiter_az": body_data_at_lock['jupiter'][1] if body_data_at_lock.get('jupiter') else None,
                    "jupiter_alt": body_data_at_lock['jupiter'][0] if body_data_at_lock.get('jupiter') else None,
                    "neptune_az": body_data_at_lock['neptune'][1] if body_data_at_lock.get('neptune') else None,
                    "neptune_alt": body_data_at_lock['neptune'][0] if body_data_at_lock.get('neptune') else None,
                    "uranus_az": body_data_at_lock['uranus'][1] if body_data_at_lock.get('uranus') else None,
                    "uranus_alt": body_data_at_lock['uranus'][0] if body_data_at_lock.get('uranus') else None,
                    "pluto_az": body_data_at_lock['pluto'][1] if body_data_at_lock.get('pluto') else None,
                    "pluto_alt": body_data_at_lock['pluto'][0] if body_data_at_lock.get('pluto') else None,
                    "saturn_az": body_data_at_lock['saturn'][1] if body_data_at_lock.get('saturn') else None,
                    "saturn_alt": body_data_at_lock['saturn'][0] if body_data_at_lock.get('saturn') else None,
                    "mercury_az": body_data_at_lock['mercury'][1] if body_data_at_lock.get('mercury') else None,
                    "mercury_alt": body_data_at_lock['mercury'][0] if body_data_at_lock.get('mercury') else None,
                    "sirius_az": site.at(time_lock_tsec).observe(sirius).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[1].degrees,
                    "sirius_alt": site.at(time_lock_tsec).observe(sirius).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[0].degrees,
                    "vega_az": site.at(time_lock_tsec).observe(vega).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[1].degrees,
                    "vega_alt": site.at(time_lock_tsec).observe(vega).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[0].degrees,
                    "mars_delta_sec": mars_delta_csv
                }
                year_candidates.append(candidate_data)
                
                log(f" 🏹 ALIGNMENT POINT: {time_lock.strftime('%H:%M:%S')} Local (Regulus hits {MONUMENT_ALIGNMENT_AZ}°)")
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
                    log(f"    Venus        : Az: {body_data_at_lock['venus'][1]:.4f}° | Alt: {body_data_at_lock['venus'][0]:+.4f}°")
                if body_data_at_lock.get('mars'):
                    log(f"    Mars         : Az: {body_data_at_lock['mars'][1]:.4f}° | Alt: {body_data_at_lock['mars'][0]:+.4f}°")
                if body_data_at_lock.get('jupiter'):
                    log(f"    Jupiter      : Az: {body_data_at_lock['jupiter'][1]:.4f}° | Alt: {body_data_at_lock['jupiter'][0]:+.4f}°")
                if body_data_at_lock.get('neptune'):
                    log(f"    Neptune      : Az: {body_data_at_lock['neptune'][1]:.4f}° | Alt: {body_data_at_lock['neptune'][0]:+.4f}°")
                if body_data_at_lock.get('uranus'):
                    log(f"    Uranus       : Az: {body_data_at_lock['uranus'][1]:.4f}° | Alt: {body_data_at_lock['uranus'][0]:+.4f}°")
                if body_data_at_lock.get('pluto'):
                    log(f"    Pluto        : Az: {body_data_at_lock['pluto'][1]:.4f}° | Alt: {body_data_at_lock['pluto'][0]:+.4f}°")
                if body_data_at_lock.get('saturn'):
                    log(f"    Saturn       : Az: {body_data_at_lock['saturn'][1]:.4f}° | Alt: {body_data_at_lock['saturn'][0]:+.4f}°")
                if body_data_at_lock.get('mercury'):
                    log(f"    Mercury      : Az: {body_data_at_lock['mercury'][1]:.4f}° | Alt: {body_data_at_lock['mercury'][0]:+.4f}°")    

                if body_data_at_lock.get('moon'):
                    moon_illum = almanac.fraction_illuminated(eph, 'moon', time_lock_tsec) * 100.0
                    log(f" 🌕 LUNAR STATUS : Az: {body_data_at_lock['moon'][1]:.4f}° | Alt: {body_data_at_lock['moon'][0]:+.4f}° | Illum: {moon_illum:.1f}%")
            else:
                log(f"    ⚠️ Regulus did not reach {MONUMENT_ALIGNMENT_AZ}° in scan window.")

            if time_mars_cross:
                log(f" 🔴 MARS CROSSING: Hits {MONUMENT_ALIGNMENT_AZ}° azimuth at {time_mars_cross.strftime('%H:%M:%S')} (Alt: {mars_alt_at_cross:+.2f}°)")
                
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
                    log("    ℹ️ Mars crossed 90°, but Regulus did not align in this scan window.")

    return year_candidates, "\n".join(output_buffer)

# =====================================================================
# SYSTEM MAIN BLOCK & ENGINE STARTUP
# =====================================================================
if __name__ == '__main__':
    print("=====================================================================")
    print("         [PROJECT REGULUS] - Celestial Alignment Scan Engine")
    print("=====================================================================")
    print(f"TARGET YEARS SET TO: {TARGET_YEARS}")
    print(f"CORES ENGAGED      : {min(6, multiprocessing.cpu_count())} (Limited to preserve system responsiveness)")
    print(f"SITE LOCATION      : {SITE_NAME}")
    print(f"SCANS ACTIVE       : Months {sorted(list(TARGET_SCANS.keys()))}")
    print(f"TIME STEP          : {TIME_STEP_SECONDS} seconds")
    print(f"ATMOSPHERE SET TO  : {ATM_TEMPERATURE}°C, {ATM_PRESSURE} hPa")
    print("\nKey Parameters:")
    print(f"• Alignment      : Azimuth = {MONUMENT_ALIGNMENT_AZ}°")
    print(f"• Dawn Limit : Sun ~ {IDEAL_SUN_ALT}°")
    print(f"• Red Star Phase : Regulus Alt ~ {RED_STAR_MIN}° - {RED_STAR_MAX}°")
    print("\nWARNING: Multiprocessing initialized. Please wait for the final compiled log...")
    print("=====================================================================\n")
    
    # Setup CSV filename and header
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"regulus_scan_results_{timestamp}.csv"
    headers = [
        'Date', 'Sun_Alt', 'Deviation_From_Ideal', 'Regulus_Alt', 
        'Is_Visible', 'Visibility_Delta_Sec', 'Moon_Alt', 'Moon_Illum_%', 
        'Venus_Az', 'Venus_Alt', 'Mars_Az', 'Mars_Alt', 'Jupiter_Az', 
        'Jupiter_Alt', 'Neptune_Az', 'Neptune_Alt', 'Saturn_Az', 
        'Saturn_Alt', 'Mercury_Az', 'Mercury_Alt', 'Uranus_Az', 
        'Uranus_Alt', 'Pluto_Az', 'Pluto_Alt', 'Sirius_Az', 
        'Sirius_Alt', 'Vega_Az', 'Vega_Alt', 'Mars_Delta_Sec'
    ]

    # Initialize CSV file with headers
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

    print(f"🚀 Scan started. Results will be appended to: {csv_filename}")
    
    global_candidates = []
    fmt = lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else x

    # ==========================================
    # PROGRESS BAR INITIALIZATION
    # ==========================================
    total_years = len(TARGET_YEARS)
    completed_years = 0

    # Execute scans with max_workers to prevent OS freeze
    with ProcessPoolExecutor(max_workers=6) as executor:
        # Submit tasks and map the future object to the target year
        futures = {executor.submit(scan_single_year, y): y for y in TARGET_YEARS}
        
        for future in as_completed(futures):
            current_scanned_year = futures[future]
            
            try:
                candidates, log_output = future.result()
                print(log_output)
                
                # Append year results to CSV immediately to save RAM
                with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    for c in candidates:
                        row = [
                            c['date'].strftime('%Y-%m-%d'), fmt(c['sun_alt']), fmt(abs(c['sun_alt'] - IDEAL_SUN_ALT)), 
                            fmt(c['reg_alt']), c['is_visible'], fmt(c['delta']) if c['delta'] is not None else "N/A",
                            fmt(c['moon_alt']), fmt(c['moon_illum']), fmt(c.get('venus_az')), fmt(c.get('venus_alt')),
                            fmt(c.get('mars_az')), fmt(c.get('mars_alt')), fmt(c.get('jupiter_az')), fmt(c.get('jupiter_alt')),
                            fmt(c.get('neptune_az')), fmt(c.get('neptune_alt')), fmt(c.get('saturn_az')) or "N/A", 
                            fmt(c.get('saturn_alt')) or "N/A", fmt(c.get('mercury_az')) or "N/A", 
                            fmt(c.get('mercury_alt')) or "N/A", fmt(c.get('uranus_az')) or "N/A", 
                            fmt(c.get('uranus_alt')) or "N/A", fmt(c.get('pluto_az')) or "N/A", 
                            fmt(c.get('pluto_alt')) or "N/A", fmt(c.get('sirius_az')) or "N/A", 
                            fmt(c.get('sirius_alt')) or "N/A", fmt(c.get('vega_az')) or "N/A", 
                            fmt(c.get('vega_alt')) or "N/A", fmt(c['mars_delta_sec'])
                        ]
                        writer.writerow(row)
                
                # Keep candidates in memory only for final evaluation
                global_candidates.extend(candidates)
                
                # ==========================================
                # PROGRESS BAR UPDATE & DISPLAY
                # ==========================================
                completed_years += 1
                percent_done = (completed_years / total_years) * 100
                
                bar_length = 30
                filled_length = int(bar_length * completed_years // total_years)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                print(f"[{bar}] {percent_done:5.1f}% | ✅ Year {current_scanned_year} appended to CSV! ({completed_years}/{total_years})")
                
            except Exception as e:
                # Increment counter even if it fails to prevent progress bar getting stuck
                completed_years += 1
                percent_done = (completed_years / total_years) * 100
                bar_length = 30
                filled_length = int(bar_length * completed_years // total_years)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                print(f"[{bar}] {percent_done:5.1f}% | ❌ Error processing year {current_scanned_year}: {e} ({completed_years}/{total_years})")

    # =====================================================================
    # FINAL EVALUATION (Runs only after all years are scanned)
    # =====================================================================
    print("\n" + "="*85)
    print("         PROJECT REGULUS - GLOBAL EVALUATION")
    print("="*85)
    
    # Sort and evaluate
    global_candidates.sort(key=lambda x: x['date'])
    best_match = None
    best_score = -9999

    for c in global_candidates:
        if c['is_visible']:
            score = -abs(c['sun_alt'] - IDEAL_SUN_ALT) 
            date_str = c['date'].strftime('%B %d, %Y')
            print(f"• {date_str:<20} : ✅ Valid Window | Sun alt: {c['sun_alt']:+.4f}° | Score: {score:+.4f}")
            if score > best_score:
                best_score = score
                best_match = c

    print("\n[ ENGINE CONCLUSION : OPTIMAL before the dawn SELECTION ]")
    if best_match:
        print(f"🏆 SYSTEM SELECTION: {best_match['date'].strftime('%B %d, %Y')}")
        print(f"   Sun Altitude    : {best_match['sun_alt']:+.4f}°")
        print(f"   Target Zone     : {IDEAL_SUN_ALT}° (Max Extinction)")
        print(f"   Deviation       : {abs(best_score):.4f}° from ideal")
    else:
        print("System found NO viable timeline in this scan segment.")
    print("="*85)
