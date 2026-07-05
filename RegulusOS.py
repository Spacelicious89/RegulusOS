import datetime
import csv
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
TARGET_YEARS = [2026] # List of years to scan. Format : [2024, 2025, 2026] or [2024] for a single year.

# ENGINE OPTIMIZATION
TIME_STEP_SECONDS = 1  # Scanning time step in seconds (1 = MAXIMUM PRECISION) more than 1 second will speed up the scan but may skip critical events.

# OBSERVATION SITE CONFIGURATION
SITE_NAME = "Great Sphinx of Giza (Head)" # change this to your desired observation site name for logging purposes
SITE_LAT = 29.975234 # change this to your desired observation site latitude in decimal degrees
SITE_LON = 31.137772  # change this to your desired observation site longitude in decimal degrees
SITE_ELEVATION = 20.0  # change this to your desired observation site elevation in meters above sea level
SITE_TZ = "Africa/Cairo" # Change this for other monuments, e.g., "America/Mexico_City"

# ATMOSPHERIC CONDITIONS (Used for light refraction calculations)
ATM_TEMPERATURE = 21.0 # Degrees Celsius change this to your desired observation site temperature in Celsius
ATM_PRESSURE = 1011.0  # Hectopascals (mbar) change this to your desired observation site atmospheric pressure in hPa

# CELESTIAL BODIES TO TRACK - you can add more planets or celestial bodies here. The keys are the names used in the code, and the values are the corresponding ephemeris identifiers.
# Note: NASA DE421 ephemeris requires 'barycenter' tag for gas giants. In line 93, you can switch to 'de430.bsp' or 'de440s.bsp' for more recent ephemerides if needed.
# Type in console: print(eph) to see all available ephemeris identifiers.
TARGET_PLANETS = {
    'mars': 'mars',
    'venus': 'venus',
    'moon': 'moon',
    'jupiter': 'jupiter barycenter' 
}

# SCAN CONFIGURATION (SNIPER MODE) here you can change or add more months and days to scan. Format: {month_number: {"days": [list_of_days], "start_h": start_hour, "scan_h": scan_duration_hours}}
TARGET_SCANS = {
    9: {"days": [23, 24, 25], "start_h": 0, "scan_h": 24}, # The "Red Dawn" Window (Sept 24th, 2026)
   11: {"days": [3, 4, 5], "start_h": 0, "scan_h": 24} # The 5-Body Alignment Pillar (Nov 4th, 2026)
}

# CRITICAL OPTICAL THRESHOLDS - this is where you can adjust the visibility thresholds for Regulus and other celestial events
NELM_SUN_ALT = -2.72          # Threshold for Daylight Washout Regulus visibility (Naked-Eye Limiting Magnitude)
MONUMENT_ALIGNMENT_AZ = 90.0  # Geodetic anchor for monument orientation - where celestial alignment is evaluated (e.g., 90° for True East).
IDEAL_SUN_ALT = -6.5          # Red Dawn effect - change this to your desired sun altitude for optimal Regulus visibility (e.g., -6.5° for Civil Twilight)
RED_STAR_ALT = 7.5            # Color shift altitude threshold - where Regulus appears reddish-orange due to atmospheric extinction.
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

# =====================================================================
# EPHEMERIS & TARGET SETUP
# =====================================================================
ts = load.timescale()
eph = load('de421.bsp') # here you can switch to 'de430.bsp' or 'de440s.bsp' for more recent ephemerides if needed
earth, sun = eph['earth'], eph['sun']

planets = {name: eph[target] for name, target in TARGET_PLANETS.items()}

OBSERVATION_TZ = ZoneInfo(SITE_TZ)
site = earth + wgs84.latlon(SITE_LAT, SITE_LON, elevation_m=SITE_ELEVATION)
lon_hours = SITE_LON / 15.0

# Fixed stellar anchor points
regulus = Star(ra_hours=(10, 8, 22.311), dec_degrees=(11, 58, 1.95))
alnilam = Star(ra_hours=(5, 36, 12.81), dec_degrees=(-1, 12, 6.9))
sgra = Star(ra_hours=(17, 45, 40.04), dec_degrees=(-29, 0, 28.1))

start_date = datetime.date(2012, 12, 21)
global_candidates = []

# =====================================================================
# ENGINE STARTUP
# =====================================================================
print("=====================================================================")
print("         [PROJECT REGULUS] - MASTER COMPUTATION ENGINE v2.5.1")
print("=====================================================================")
print(f"TARGET YEARS SET TO: {TARGET_YEARS}")
print(f"SITE LOCATION     : {SITE_NAME}")
print(f"SCANS ACTIVE      : Months {sorted(list(TARGET_SCANS.keys()))}")
print(f"TIME STEP         : {TIME_STEP_SECONDS} seconds")
print(f"ATMOSPHERE SET TO : {ATM_TEMPERATURE}°C, {ATM_PRESSURE} hPa")
print("\nKey Parameters:")
print(f"• Alignment      : Azimuth = {MONUMENT_ALIGNMENT_AZ}°")
print(f"• Red Dawn Limit : Sun ~ {IDEAL_SUN_ALT}°")
print(f"• Red Star Phase : Regulus Alt ~ {RED_STAR_ALT}°")
print("=====================================================================\n")

# =====================================================================
# CSV INITIALIZATION (ON-THE-FLY SAVING)
# =====================================================================
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"regulus_scan_results_{timestamp}.csv"

with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([
        'Date', 'Sun_Alt', 'Deviation_From_Ideal', 'Regulus_Alt', 
        'Is_Visible', 'Visibility_Delta_Sec',
        'Moon_Alt', 'Moon_Illum_%', 
        'Venus_Az', 'Venus_Alt', 
        'Mars_Az', 'Mars_Alt', 
        'Jupiter_Az', 'Jupiter_Alt',
        'Mars_Delta_Sec'
    ])
print(f"📁 CSV file saved on the fly: {csv_filename}\n")

# =====================================================================
# UNIFIED SCAN LOOP
# =====================================================================
for TARGET_YEAR in TARGET_YEARS:
    for month, config in sorted(TARGET_SCANS.items()):
        print("="*75)
        print(f"                 SCAN MODULE - MONTH: {month:02d} / {TARGET_YEAR}")
        print("="*75)
        
        for day in config["days"]:
            current_date = datetime.date(TARGET_YEAR, month, day)
            days_delta = (current_date - start_date).days
            prime_status = "PRIME NUMBER" if is_prime(days_delta) else "COMPOSITE NUMBER"
            
            print(f"\n📅 SCANNING: {current_date.strftime('%B %d, %Y')}")
            print(f"  ↳ Days from 2012-12-21: {days_delta} → {prime_status}")
            print("-" * 75)
            
            t_start = datetime.datetime(TARGET_YEAR, month, day, config["start_h"], 0, 0)
            
            # State Trackers
            time_nelm = time_lock = time_reg_rise = time_red_star = None
            time_lock_tsec = None
            sun_alt_at_lock = reg_alt_at_lock = reg_az_at_rise = 0.0
            sun_alt_at_red = reg_az_at_red = 0.0
            
            time_mars_cross = None
            mars_alt_at_cross = 0.0
            
            body_data_at_lock = {name: None for name in TARGET_PLANETS}
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
                    if prev_reg_alt < RED_STAR_ALT <= curr_reg_alt:
                        time_red_star = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)
                        sun_alt_at_red = sun_alt
                        reg_az_at_red = curr_reg_az

                # --- MARS TRACKING ---
                mars_pos = site.at(t_sec).observe(planets['mars']).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                curr_mars_az, curr_mars_alt = mars_pos[1].degrees, mars_pos[0].degrees
                
                if time_mars_cross is None and prev_mars_az is not None:
                    if prev_mars_az < MONUMENT_ALIGNMENT_AZ <= curr_mars_az:
                        time_mars_cross = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)
                        mars_alt_at_cross = curr_mars_alt

                # --- MAIN ALIGNMENT LOCK ---
                if time_lock is None and prev_reg_az is not None:
                    if prev_reg_az < MONUMENT_ALIGNMENT_AZ <= curr_reg_az:
                        time_lock = t_sec.utc_datetime().astimezone(OBSERVATION_TZ)
                        time_lock_tsec = t_sec
                        reg_alt_at_lock = curr_reg_alt
                        sun_alt_at_lock = sun_alt
                        
                        for name, body in planets.items():
                            body_data_at_lock[name] = site.at(t_sec).observe(body).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)

                prev_reg_az, prev_reg_alt = curr_reg_az, curr_reg_alt
                prev_mars_az = curr_mars_az
                
                if time_lock and time_nelm and time_red_star and time_mars_cross: break

            # ==================== DAILY REPORT ====================
            if time_reg_rise:
                print(f" 🌅 REGULUS RISING : {time_reg_rise.strftime('%H:%M:%S')} Local (Azimuth: {reg_az_at_rise:.4f}°)")

            if time_red_star:
                night_status = "🌙 (Pitch Black)" if sun_alt_at_red < -18.0 else "🌆 (Twilight)"
                print(f" 🔴 RED STAR LIMIT : {time_red_star.strftime('%H:%M:%S')} Local | Regulus Az: {reg_az_at_red:.4f}° | Sun Alt: {sun_alt_at_red:+.4f}° {night_status}")

            if time_lock:
                is_visible = False
                delta = None
                
                # Extract lunar data at the moment of alignment lock
                moon_data = body_data_at_lock.get('moon')
                moon_illum = almanac.fraction_illuminated(eph, 'moon', time_lock_tsec) * 100.0 if moon_data else 0.0
                moon_alt = moon_data[0].degrees if moon_data else -90.0

                # VISIBILITY LOGIC 
                if sun_alt_at_lock >= NELM_SUN_ALT:
                    status = "❌ INVISIBLE (Washed out by daylight)"
                elif moon_alt > 0.0 and moon_illum > 75.0:
                    status = f"❌ INVISIBLE (Lunar Washout: Moon at {moon_alt:+.1f}°, {moon_illum:.1f}%)"
                elif sun_alt_at_lock < -18.0:
                    status = "🌙 NIGHTTIME (Pitch black, no red dawn)"
                else:
                    is_visible = True
                    if time_nelm:
                        delta = (time_nelm - time_lock).total_seconds()
                        minutes, seconds = int(abs(delta) // 60), int(abs(delta) % 60)
                        status = f"✅ VISIBLE for {minutes}m {seconds}s after alignment" if delta > 0 else f"❌ INVISIBLE (Faded {minutes}m {seconds}s BEFORE alignment)"
                        if delta <= 0: is_visible = False
                
                # --- Calculate Mars Delta for CSV ---
                mars_delta_csv = "N/A"
                if time_mars_cross and time_lock:
                    t1 = time_lock.replace(year=2000, month=1, day=1)
                    t2 = time_mars_cross.replace(year=2000, month=1, day=1)
                    mars_delta_csv = (t1 - t2).total_seconds()
                # -------------------------------------

                candidate_data = {
                    "date": current_date,
                    "sun_alt": sun_alt_at_lock,
                    "reg_alt": reg_alt_at_lock,
                    "is_visible": is_visible,
                    "delta": delta,
                    "moon_alt": moon_alt,
                    "moon_illum": moon_illum,
                    "venus_az": body_data_at_lock['venus'][1].degrees if body_data_at_lock.get('venus') else None,
                    "venus_alt": body_data_at_lock['venus'][0].degrees if body_data_at_lock.get('venus') else None,
                    "mars_az": body_data_at_lock['mars'][1].degrees if body_data_at_lock.get('mars') else None,
                    "mars_alt": body_data_at_lock['mars'][0].degrees if body_data_at_lock.get('mars') else None,
                    "jupiter_az": body_data_at_lock['jupiter'][1].degrees if body_data_at_lock.get('jupiter') else None,
                    "jupiter_alt": body_data_at_lock['jupiter'][0].degrees if body_data_at_lock.get('jupiter') else None,
                    "mars_delta_sec": mars_delta_csv
                }
                global_candidates.append(candidate_data)
                
                # --- Save to CSV ---
                dev = abs(candidate_data['sun_alt'] - IDEAL_SUN_ALT)
                fmt = lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else x
                
                with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        candidate_data['date'].strftime('%Y-%m-%d'),
                        fmt(candidate_data['sun_alt']),
                        fmt(dev),
                        fmt(candidate_data['reg_alt']),
                        candidate_data['is_visible'],
                        fmt(candidate_data['delta']) if candidate_data['delta'] is not None else "N/A",
                        fmt(candidate_data['moon_alt']),
                        fmt(candidate_data['moon_illum']),
                        fmt(candidate_data['venus_az']),
                        fmt(candidate_data['venus_alt']),
                        fmt(candidate_data['mars_az']),
                        fmt(candidate_data['mars_alt']),
                        fmt(candidate_data['jupiter_az']),
                        fmt(candidate_data['jupiter_alt']),
                        fmt(candidate_data['mars_delta_sec'])
                    ])
                # ----------------------------
                
                print(f" 🏹 ALIGNMENT POINT: {time_lock.strftime('%H:%M:%S')} Local (Regulus hits {MONUMENT_ALIGNMENT_AZ}°)")
                print(f"    Altitudes    : Sun: {sun_alt_at_lock:+.4f}° | Regulus: {reg_alt_at_lock:+.4f}°")
                print(f"    Eye Status   : {status}")
                # ----------------------------------------
                
                # --- CUSTOM SKYMAP RENDERING ---
                print(f" 🌌 GLOBAL SKYMAP (At moment of {MONUMENT_ALIGNMENT_AZ}° Alignment):")
                
                # LST Clock Calculation
                lst = time_lock_tsec.gast + lon_hours
                lst = lst % 24.0
                h = int(lst)
                m = int((lst - h) * 60)
                s_lst = (lst - h - m/60.0) * 3600
                print(f"    LST Clock    : {h:02d}:{m:02d}:{s_lst:05.2f}")
                
                # Orion & Galactic Center Coordinates
                orion_pos = site.at(time_lock_tsec).observe(alnilam).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                print(f"    Orion's Belt : Az: {orion_pos[1].degrees:.4f}° | Alt: {orion_pos[0].degrees:+.4f}°")
                
                gc_pos = site.at(time_lock_tsec).observe(sgra).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                print(f"    Galactic Ctr : Alt: {gc_pos[0].degrees:+.4f}°")
                
                # Dynamic Planets Log
                if body_data_at_lock.get('venus'):
                    print(f"    Venus        : Az: {body_data_at_lock['venus'][1].degrees:.4f}° | Alt: {body_data_at_lock['venus'][0].degrees:+.4f}°")
                if body_data_at_lock.get('mars'):
                    print(f"    Mars         : Az: {body_data_at_lock['mars'][1].degrees:.4f}° | Alt: {body_data_at_lock['mars'][0].degrees:+.4f}°")
                if body_data_at_lock.get('jupiter'):
                    print(f"    Jupiter      : Az: {body_data_at_lock['jupiter'][1].degrees:.4f}° | Alt: {body_data_at_lock['jupiter'][0].degrees:+.4f}°")
                
                # Lunar Status
                if body_data_at_lock.get('moon'):
                    moon_illum = almanac.fraction_illuminated(eph, 'moon', time_lock_tsec) * 100.0
                    print(f" 🌕 LUNAR STATUS : Az: {body_data_at_lock['moon'][1].degrees:.4f}° | Alt: {body_data_at_lock['moon'][0].degrees:+.4f}° | Illum: {moon_illum:.1f}%")
                
                # Mars Conjunction Tracker
                if time_mars_cross:
                    # Normalize dates to avoid 24h rollover bugs
                    t1 = time_lock.replace(year=2000, month=1, day=1)
                    t2 = time_mars_cross.replace(year=2000, month=1, day=1)
                    
                    diff_seconds = (t1 - t2).total_seconds()
                    diff_min = abs(diff_seconds) / 60.0
                    
                    # Logic: If diff is positive, Lock happened AFTER Mars cross
                    before_after = "BEFORE" if diff_seconds > 0 else "AFTER"
        
                    # Convert absolute difference to hours, minutes, seconds
                    abs_diff_sec = int(abs(diff_seconds))
                    h, remainder = divmod(abs_diff_sec, 3600)
                    m, s = divmod(remainder, 60)
                    
                    # Formating the time string
                    if h > 0:
                        time_str = f"{h}h {m}m {s}s"
                    elif m > 0:
                        time_str = f"{m}m {s}s"
                    else:
                        time_str = f"{s} seconds"
        
                    print(f" 🔴 MARS CROSSING: Hits {MONUMENT_ALIGNMENT_AZ}° azimuth at {time_mars_cross.strftime('%H:%M:%S')} (Alt: {mars_alt_at_cross:+.2f}°)")
                    print(f"    ⚠️ CONJUNCTION ALERT: Mars crosses exact azimuth {time_str} {before_after} Regulus!")

            else:
                print(f"    ⚠️ Regulus did not reach {MONUMENT_ALIGNMENT_AZ}° in scan window.")


# =====================================================================
# FINAL EVALUATION
# =====================================================================
print("\n" + "="*85)
print("         PROJECT REGULUS - GLOBAL DYNAMIC EVALUATION v2.5.1")
print("="*85)
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

print("\n[ ENGINE CONCLUSION : OPTIMAL RED-SHIFT SELECTION ]")
if best_match:
    print(f"🏆 SYSTEM SELECTION: {best_match['date'].strftime('%B %d, %Y')}")
    print(f"   Sun Altitude    : {best_match['sun_alt']:+.4f}°")
    print(f"   Target Zone     : {IDEAL_SUN_ALT}° (Max Extinction)")
    print(f"   Deviation       : {abs(best_score):.4f}° from ideal")
else:
    print("System found NO viable timeline in this scan segment.")
print("="*85)
print(f"\n📊 [DATA EXPORT COMPLETED] Scan results were successfully saved on the fly to: {csv_filename}")
