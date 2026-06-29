import datetime
from zoneinfo import ZoneInfo
from skyfield.api import load, Star, wgs84

# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================
def is_prime(n):
    """Checks if the number of days since the Mayan Calendar baseline is a prime number."""
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
# GLOBAL USER INPUT ZONE & CONFIGURATION
# =====================================================================
# 👇 ================================================================ 👇
# CHANGE THE TARGET YEAR HERE. The entire engine will adjust to this value.
TARGET_YEAR = 2026

# MASTER SCAN CONFIGURATION
# Format: Month: {"days": [list of days], "start_h": hour, "scan_h": duration_in_hours}
TARGET_SCANS = {
    8:  {"days": [10, 20],             "start_h": 1,  "scan_h": 9},  # Summer Washout Test
    9:  {"days": [20, 21, 22, 23, 24], "start_h": 3,  "scan_h": 4},  # Red Shift Target Window
    10: {"days": [4, 5, 6],            "start_h": 0,  "scan_h": 8},  # Pitch Black Test
    11: {"days": [2, 3, 4, 5, 6],      "start_h": 22, "scan_h": 5}   # Mars Conjunction Window
}

# CRITICAL OPTICAL THRESHOLDS
NELM_SUN_ALT = -2.72       # Sun altitude for Naked-Eye Limiting Magnitude (Sky too bright)
REGULUS_EAST_AZ = 90.0     # The exact azimuth the Sphinx faces (True East)
IDEAL_SUN_ALT = -3.5       # The perfect Sun altitude for maximum 'Red Dawn' extinction effect
# 👆 ================================================================ 👆

# =====================================================================
# EPHEMERIS & TARGET SETUP
# =====================================================================
ts = load.timescale()
eph = load('de421.bsp')
earth, sun, mars, venus = eph['earth'], eph['sun'], eph['mars'], eph['venus']

EGYPT_TZ = ZoneInfo("Africa/Cairo")
giza = earth + wgs84.latlon(29.97526, 31.13758, elevation_m=20.0)
lon_hours = 31.13758 / 15.0

regulus = Star(ra_hours=(10, 8, 22.311), dec_degrees=(11, 58, 1.95))
alnilam = Star(ra_hours=(5, 36, 12.81), dec_degrees=(-1, 12, 6.9))
sgra = Star(ra_hours=(17, 45, 40.04), dec_degrees=(-29, 0, 28.1))

start_date = datetime.date(2012, 12, 21)
global_candidates = []

# =====================================================================
# ENGINE STARTUP
# =====================================================================
print("=====================================================================")
print("         [PROJECT REGULUS] - MASTER COMPUTATION ENGINE v2.0")
print("=====================================================================")
print(f"TARGET YEAR SET TO: {TARGET_YEAR}")
print(f"SCANS ACTIVE      : Months {list(TARGET_SCANS.keys())}")
print("\nPurpose: Calculate precise moments when Regulus aligns exactly with")
print("         the Great Sphinx of Giza facing True East (azimuth 90°)")
print("         in the pre-dawn sky, evaluating naked-eye visibility and")
print("         optimizing for maximum atmospheric red-shift.")
print("\nKey Parameters:")
print("• Location       : Great Sphinx of Giza (29.97526°N, 31.13758°E)")
print("• Target Star    : Regulus (α Leonis), visual magnitude +1.35~1.40")
print(f"• Visibility     : Sun altitude < {NELM_SUN_ALT}° (empirical NELM threshold)")
print(f"• Alignment      : Regulus azimuth = exactly {REGULUS_EAST_AZ}° (True East)")
print(f"• Extinction     : Ideal Sun altitude ~ {IDEAL_SUN_ALT}° (Red Dawn effect)")
print("• Timezone       : Africa/Cairo (Dynamic Auto-DST Resolution)")
print("=====================================================================\n")

# =====================================================================
# UNIFIED SCAN LOOP
# =====================================================================
for month, config in TARGET_SCANS.items():
    print("="*75)
    print(f"                 SCAN MODULE - MONTH: {month:02d} / {TARGET_YEAR}")
    print("="*75)
    
    for day in config["days"]:
        # Calculate Mayan Baseline
        current_date = datetime.date(TARGET_YEAR, month, day)
        days_delta = (current_date - start_date).days
        prime_status = "PRIME NUMBER" if is_prime(days_delta) else "COMPOSITE NUMBER"
        
        print(f"\n📅 SCANNING: {current_date.strftime('%B %d, %Y')}")
        print(f"  ↳ Days from 2012-12-21: {days_delta} → {prime_status}")
        print("-" * 75)
        
        t_start = datetime.datetime(TARGET_YEAR, month, day, config["start_h"], 0, 0)
        
        # State Trackers
        time_nelm = None
        time_lock = None
        time_mars = None
        
        sun_alt_at_lock = reg_alt_at_lock = 0.0
        mars_alt_at_cross = 0.0
        lst_data = aln_pos = sgra_pos = venus_pos = None

        # AZIMUTH MEMORY (To detect exact physical crossing, preventing instant-triggers)
        prev_reg_az = None
        prev_mars_az = None

        # Main Time Loop (Iterating strictly per second within the defined scan window)
        for s in range(config["scan_h"] * 3600): 
            dt = t_start + datetime.timedelta(seconds=s)
            t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            
            # 1. Track Sun for NELM Limit (Washout marker)
            if time_nelm is None:
                sun_alt = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
                if sun_alt >= NELM_SUN_ALT:
                    time_nelm = t_sec.utc_datetime().astimezone(EGYPT_TZ)
                    reg_az_at_nelm = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[1].degrees

            # Get exact current coordinates for Regulus ONLY (saves CPU time)
            reg_pos = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            curr_reg_az = reg_pos[1].degrees
            
            # 2. Track Regulus for EXACT 90.0° Physical Crossing
            if time_lock is None and prev_reg_az is not None:
                if prev_reg_az < REGULUS_EAST_AZ <= curr_reg_az:
                    time_lock = t_sec.utc_datetime().astimezone(EGYPT_TZ)
                    reg_alt_at_lock = reg_pos[0].degrees
                    sun_alt_at_lock = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
                    
                    # Fetch expensive Skymap data ONLY ONCE when alignment is hit
                    gmst = t_sec.gmst
                    lst_hours = (gmst + lon_hours) % 24.0
                    lst_h, lst_m = int(lst_hours), int((lst_hours % 1) * 60)
                    lst_s = ((lst_hours * 60) % 1) * 60
                    lst_data = (lst_h, lst_m, lst_s)
                    
                    aln_pos = giza.at(t_sec).observe(alnilam).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
                    sgra_pos = giza.at(t_sec).observe(sgra).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
                    venus_pos = giza.at(t_sec).observe(venus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)

            # 3. Track Mars (OPTIMIZED: Scans Mars ONLY in November to save CPU load)
            if month == 11:
                mars_pos = giza.at(t_sec).observe(mars).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
                curr_mars_az = mars_pos[1].degrees
                
                if time_mars is None and prev_mars_az is not None:
                    if prev_mars_az < REGULUS_EAST_AZ <= curr_mars_az:
                        time_mars = t_sec.utc_datetime().astimezone(EGYPT_TZ)
                        mars_alt_at_cross = mars_pos[0].degrees
                
                prev_mars_az = curr_mars_az

            # Save Regulus azimuth for the next second's calculation
            prev_reg_az = curr_reg_az

            # Break early if all parameters are found to save CPU time
            if time_lock and time_nelm and (time_mars or month != 11):
                break

        # ==================== DAILY REPORT GENERATION ====================
        if time_lock:
            # Determine Naked-Eye Status
            is_visible = False
            delta = None
            if sun_alt_at_lock >= NELM_SUN_ALT:
                status = "❌ INVISIBLE (Washed out by daylight)"
                is_visible = False
            elif sun_alt_at_lock < -18.0:
                status = "🌙 NIGHTTIME (Pitch black, no red shift)"
                is_visible = False # Poprawiony bug!
            else:
                is_visible = True
                if time_nelm:
                    delta = (time_nelm - time_lock).total_seconds()
                    minutes, seconds = int(abs(delta) // 60), int(abs(delta) % 60)
                    if delta > 0:
                        status = f"✅ VISIBLE for {minutes}m {seconds}s after alignment"
                    else:
                        status = f"❌ INVISIBLE (Faded {minutes}m {seconds}s BEFORE alignment)"
                        is_visible = False
                else:
                    status = "✅ VISIBLE (Dawn limit not reached in scan window)"
            
            global_candidates.append({
                "date": current_date, "sun_alt": sun_alt_at_lock, "is_visible": is_visible, "delta": delta
            })

            # Print Data
            print(f" 🏹 SPHINX 90° ALIGNMENT (Regulus hits True East):")
            print(f"    Time (Egypt) : {time_lock.strftime('%H:%M:%S')} Local")
            print(f"    Altitudes    : Sun: {sun_alt_at_lock:+.4f}° | Regulus: {reg_alt_at_lock:+.4f}°")
            print(f"    Eye Status   : {status}")
            
            if time_nelm and sun_alt_at_lock < NELM_SUN_ALT:
                print(f" 🌅 DAWN LIMIT   : Regulus fades at {time_nelm.strftime('%H:%M:%S')} (Az: {reg_az_at_nelm:.4f}°)")

            # Global Skymap
            lst_h, lst_m, lst_s = lst_data
            print(f" 🌌 GLOBAL SKYMAP:")
            print(f"    LST Clock    : {lst_h:02d}:{lst_m:02d}:{lst_s:05.2f}")
            print(f"    Orion's Belt : Az: {aln_pos[1].degrees:.4f}° | Alt: {aln_pos[0].degrees:+.4f}°")
            print(f"    Galactic Ctr : Alt: {sgra_pos[0].degrees:+.4f}°")
            print(f"    Venus        : Az: {venus_pos[1].degrees:.4f}°")

            # Mars Radar Alert System
            if time_mars:
                delta_mars_sec = (time_mars - time_lock).total_seconds()
                delta_mars_min = abs(delta_mars_sec) / 60
                
                print(f" 🔴 MARS RADAR  : Mars hits 90° at {time_mars.strftime('%H:%M:%S')} (Alt: {mars_alt_at_cross:+.2f}°)")
                if delta_mars_min <= 60.0:
                    timing_word = "AFTER" if delta_mars_sec > 0 else "BEFORE"
                    print(f"    ⚠️ CONJUNCTION ALERT: Mars crosses exact azimuth {delta_mars_min:.1f} min {timing_word} Regulus!")
        else:
            print("    ⚠️ Regulus did not reach 90° in the scanned window. Adjust scan_h or start_h.")


# =====================================================================
# FINAL SYSTEM EVALUATION & SCORING
# =====================================================================
print("\n" + "="*85)
print("         PROJECT REGULUS - GLOBAL DYNAMIC EVALUATION v2.0")
print("="*85)
print(f"Evaluating valid dates against ideal Red Shift target: {IDEAL_SUN_ALT}°")
print("-" * 85)

best_match = None
best_score = -9999

for c in global_candidates:
    date_str = c['date'].strftime('%B %d, %Y')
    alt = c['sun_alt']
    vis = c['is_visible']
    score = -abs(alt - IDEAL_SUN_ALT) # Closer to 0 is better
    
    if vis:
        time_note = ""
        if c['delta'] is not None and c['delta'] > 0:
            m, s = int(c['delta'] // 60), int(c['delta'] % 60)
            time_note = f"({m}m {s}s)"
        print(f"• {date_str:<20} : ✅ Valid Window {time_note:<10} | Sun alt: {alt:+.4f}° | Score: {score:+.4f}")
        
        if score > best_score:
            best_score = score
            best_match = c
    else:
        reason = "Daylight Washout" if alt >= NELM_SUN_ALT else "Pitch Black"
        print(f"• {date_str:<20} : ❌ Invalid ({reason:<16}) | Sun alt: {alt:+.4f}° | Score: {score:+.4f}")

print("\n[ ENGINE CONCLUSION : OPTIMAL RED-SHIFT SELECTION ]")
if best_match:
    print(f"🏆 SYSTEM SELECTION: {best_match['date'].strftime('%B %d, %Y')}")
    print(f"   Sun Altitude    : {best_match['sun_alt']:+.4f}°")
    print(f"   Target Zone     : {IDEAL_SUN_ALT}° (Max Extinction)")
    print(f"   Deviation       : {abs(best_score):.4f}° from ideal")
else:
    print("System found NO mathematically viable timeline fulfilling all constraints.")
print("="*85)
