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
# SYSTEM CONFIGURATION & EPHEMERIS SETUP
# =====================================================================
# Load JPL ephemeris data for highly accurate planetary positions
ts = load.timescale()
eph = load('de421.bsp')
earth = eph['earth']
sun = eph['sun']
mars = eph['mars']
venus = eph['venus']

# Dynamic Timezone Resolver - Automatically handles DST for any year/month in Egypt
EGYPT_TZ = ZoneInfo("Africa/Cairo")

# Set exact coordinates for the Great Sphinx of Giza
giza = earth + wgs84.latlon(29.97526, 31.13758, elevation_m=20.0)
lon_hours = 31.13758 / 15.0

# Define specific astronomical targets using J2000 epoch coordinates
regulus = Star(ra_hours=(10, 8, 22.311), dec_degrees=(11, 58, 1.95))
alnilam = Star(ra_hours=(5, 36, 12.81), dec_degrees=(-1, 12, 6.9))
sgra = Star(ra_hours=(17, 45, 40.04), dec_degrees=(-29, 0, 28.1))

# Baseline date for day-counting logic
start_date = datetime.date(2012, 12, 21)

# --- CRITICAL OPTICAL THRESHOLDS ---
# NELM (Naked-Eye Limiting Magnitude): Sun must be below this to see Regulus
NELM_SUN_ALT = -2.72 
# The exact azimuth the Sphinx faces (True East)
REGULUS_EAST_AZ = 90.0
# The perfect Sun altitude for maximum atmospheric Red-Shift (extinction effect)
IDEAL_SUN_ALT = -3.5  

# Memory array to hold all valid dates across all scanned months
global_candidates = []


# =====================================================================
# ENGINE STARTUP LOGS
# =====================================================================
print("=====================================================================")
print("         [PROJECT REGULUS] - MASTER COMPUTATION ENGINE v1.9")
print("=====================================================================")
print("Purpose: Calculate precise moments when Regulus aligns exactly with")
print("         the Great Sphinx of Giza facing True East (azimuth 90°)")
print("         in the pre-dawn sky, evaluating naked-eye visibility and")
print("         optimizing for maximum atmospheric red-shift.")
print("")
print("Key Parameters:")
print("• Location       : Great Sphinx of Giza (29.97526°N, 31.13758°E)")
print("• Target Star    : Regulus (α Leonis), visual magnitude +1.35~1.40")
print("• Visibility     : Sun altitude < -2.72° (empirical NELM threshold)")
print("• Alignment      : Regulus azimuth = exactly 90.0000° (True East)")
print("• Extinction     : Ideal Sun altitude ~ -3.5° (Red Dawn effect)")
print("• Timezone       : Africa/Cairo (Dynamic Auto-DST Resolution)")
print("=====================================================================")


# =====================================================================
# AUGUST MODULE (CONTROL GROUP)
# Checks summer conditions to verify the engine handles daylight washout
# =====================================================================
print("\n" + "="*70)
print("                 SCAN MODULE - AUGUST 2026")
print("="*70)

# 👇 ==================== USER INPUT ZONE ==================== 👇
# Add or remove days in August you want to scan. Format: [day1, day2]
aug_days = [20, 21]
# 👆 ========================================================= 👆

for day in aug_days:
    t_start = datetime.datetime(2026, 8, day, 1, 0, 0)
    found = False
    
    # Loop through 32,400 seconds (9 hours) to find the exact second of alignment
    for s in range(32400):
        dt = t_start + datetime.timedelta(seconds=s)
        t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        
        # Calculate apparent azimuth of Regulus including atmospheric refraction
        reg_az = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[1].degrees
        
        # Lock data exactly when Regulus crosses True East (90 degrees)
        if reg_az >= REGULUS_EAST_AZ:
            sun_alt = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
            
            is_vis = (-18.0 <= sun_alt < NELM_SUN_ALT)
            visibility = "❌ INVISIBLE (Washed out by daylight)" if sun_alt >= NELM_SUN_ALT else "✅ VISIBLE"
            
            # Dynamic Timezone resolution for print output
            local_time = t_sec.utc_datetime().astimezone(EGYPT_TZ).strftime('%H:%M:%S')
            print(f" 🎯 August {day}: Regulus 90° at {local_time} Local | Sun alt: {sun_alt:.4f}° -> {visibility}")
            
            global_candidates.append({
                "month": "August", "day": day, "sun_alt": sun_alt, "is_visible": is_vis, "delta": None
            })
            found = True
            break
            
    if not found:
        print(f" ❌ August {day}: No 90° alignment found in scanned window.")
print("=====================================================================")


# =====================================================================
# SEPTEMBER MODULE (RED SHIFT TARGET WINDOW)
# Tracks the exact days where Regulus perfectly balances visibility & color
# =====================================================================
print("\n" + "="*70)
print("                 SCAN MODULE - SEPTEMBER 2026")
print("="*70)

# 👇 ==================== USER INPUT ZONE ==================== 👇
# Edit dates below to expand the September scan. 
# These dates are closest to the -3.5° Red Shift atmospheric target.
days = [20, 21, 22]
# 👆 ========================================================= 👆

for day in days:
    current_date = datetime.date(2026, 9, day)
    days_delta = (current_date - start_date).days
    prime_status = "PRIME NUMBER" if is_prime(days_delta) else "COMPOSITE NUMBER"
    
    print(f"\n📅 MORNING SCAN: September {day}, 2026")
    print(f"  ↳ Days from 2012-12-21: {days_delta} → {prime_status}")
    print("---------------------------------------------------------------------")
    
    t_start = datetime.datetime(2026, 9, day, 3, 0, 0)
    
    time_nelm = None
    time_lock = None
    reg_az_at_nelm = reg_alt_at_nelm = 0.0
    sun_alt_at_lock = reg_alt_at_lock = 0.0
    lst_data = aln_pos = sgra_pos = mars_pos = venus_pos = None

    # Scan 14,400 seconds (4 hours) starting from 03:00 AM
    for s in range(14400): 
        dt = t_start + datetime.timedelta(seconds=s)
        t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        
        sun_alt = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
        reg_pos = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
        reg_az = reg_pos[1].degrees
        reg_alt = reg_pos[0].degrees

        # Marker 1: When does the sky get too bright? (Sun hits -2.72)
        if time_nelm is None and sun_alt >= NELM_SUN_ALT:
            time_nelm = t_sec.utc_datetime().astimezone(EGYPT_TZ)
            reg_az_at_nelm = reg_az
            reg_alt_at_nelm = reg_alt

        # Marker 2: When does Regulus hit exactly 90.000° azimuth?
        if time_lock is None and reg_az >= REGULUS_EAST_AZ:
            time_lock = t_sec.utc_datetime().astimezone(EGYPT_TZ)
            sun_alt_at_lock = sun_alt
            reg_alt_at_lock = reg_alt

            # Calculate Local Sidereal Time for the global skymap
            gmst = t_sec.gmst
            lst_hours = (gmst + lon_hours) % 24.0
            lst_h = int(lst_hours)
            lst_m = int((lst_hours - lst_h) * 60)
            lst_s = (lst_hours - lst_h) * 3600 - lst_m * 60

            # Lock coordinates of other key celestial objects for context
            aln_pos = giza.at(t_sec).observe(alnilam).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            sgra_pos = giza.at(t_sec).observe(sgra).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            mars_pos = giza.at(t_sec).observe(mars).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            venus_pos = giza.at(t_sec).observe(venus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            
            lst_data = (lst_h, lst_m, lst_s)

    # Output detailed results for the daily scan
    if time_nelm and time_lock:
        print(f" 🌅 DAWN VISIBILITY LIMIT: Regulus fades at {time_nelm.strftime('%H:%M:%S')} Local | Az: {reg_az_at_nelm:.4f}°")
        print(f" 🏹 SPHINX 90° ALIGNMENT (Regulus hits True East):")
        print(f"    Local Time (Egypt)     : {time_lock.strftime('%H:%M:%S')}")
        print(f"    Sun / Regulus Altitude : Sun: {sun_alt_at_lock:.4f}° | Regulus: +{reg_alt_at_lock:.4f}°")
        
        # Calculate how long the star remains visible after aligning
        delta = (time_nelm - time_lock).total_seconds()
        is_visible = delta > 0
        
        global_candidates.append({
            "month": "September", "day": day, "sun_alt": sun_alt_at_lock, "is_visible": is_visible, "delta": delta
        })

        minutes = int(abs(delta) // 60)
        seconds = int(abs(delta) % 60)
        
        if is_visible:
            print(f"    Naked-Eye Status       : ✅ VISIBLE for {minutes}m {seconds}s after alignment")
        else:
            print(f"    Naked-Eye Status       : ❌ INVISIBLE - faded {minutes}m {seconds}s BEFORE 90°")

        if lst_data:
            lst_h, lst_m, lst_s = lst_data
            print(f" 🌌 GLOBAL SKYMAP AT ALIGNMENT:")
            print(f"    Local Sidereal Time    : {lst_h:02d}:{lst_m:02d}:{lst_s:05.2f}")
            print(f"    Orion's Belt (Alnilam) : Az: {aln_pos[1].degrees:.4f}° | Alt: +{aln_pos[0].degrees:.4f}°")
            print(f"    Galactic Center (Sgr A*): Alt: {sgra_pos[0].degrees:.4f}°")
            print(f"    Planets                : Mars Az: {mars_pos[1].degrees:.4f}° | Venus Az: {venus_pos[1].degrees:.4f}°")
    else:
        print("    ⚠️  Regulus did not reach 90° in the scanned window.")
    print("=====================================================================")


# =====================================================================
# OCTOBER MODULE (PITCH BLACK / WINDOW CLOSURE)
# Tracks when the Sun drops below -18°, entering deep astronomical night
# =====================================================================
print("\n" + "="*70)
print("                 SCAN MODULE - OCTOBER 2026")
print("="*70)
print("Tracking the closure of the dawn window (transition to Pitch Black)")

# 👇 ==================== USER INPUT ZONE ==================== 👇
# These dates identify the exact day the sky transitions into deep night
oct_days = [4, 5, 6, 7]
# 👆 ========================================================= 👆

for day in oct_days:
    t_start = datetime.datetime(2026, 10, day, 0, 0, 0)
    found = False
    for s in range(28800):
        dt = t_start + datetime.timedelta(seconds=s)
        t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        reg_az = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[1].degrees
        
        if reg_az >= REGULUS_EAST_AZ:
            sun_alt = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
            
            is_vis = (-18.0 <= sun_alt < NELM_SUN_ALT)
            # Flag as Pitch Black if sun is lower than -18.0
            status = "🌙 NIGHTTIME (Pitch black, no red shift)" if sun_alt < -18.0 else "✅ VISIBLE"
            
            local_time = t_sec.utc_datetime().astimezone(EGYPT_TZ).strftime('%H:%M:%S')
            print(f" 🎯 October {day}: Regulus 90° at {local_time} Local | Sun alt: {sun_alt:.4f}° -> {status}")
            
            global_candidates.append({
                "month": "October", "day": day, "sun_alt": sun_alt, "is_visible": is_vis, "delta": None
            })
            found = True
            break
            
    if not found:
        print(f" ❌ October {day}: No 90° alignment found in scanned window.")
print("=====================================================================")


# =====================================================================
# NOVEMBER MODULE (MARS CONJUNCTION)
# Tracks the planetary approach of Mars and its conjunction with Regulus
# =====================================================================
print("\n" + "="*70)
print("                 SCAN MODULE - NOVEMBER 2026")
print("="*70)
print("Checking Regulus-Mars proximity and exact conjunction on eastern horizon")

# 👇 ==================== USER INPUT ZONE ==================== 👇
# Track the Mars flyby. Nov 26 is the closest point of approach.
nov_days = [25, 26, 27]
# 👆 ========================================================= 👆

for day in nov_days:
    t_start = datetime.datetime(2026, 11, day, 22, 0, 0)   
    time_reg_90 = time_mars_90 = None
    sun_alt_reg = sun_alt_mars = reg_alt = mars_alt = None

    for s in range(18000):   
        dt = t_start + datetime.timedelta(seconds=s)
        t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        
        reg_az = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[1].degrees
        mars_az = giza.at(t_sec).observe(mars).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[1].degrees
        
        # Track when Regulus hits True East
        if time_reg_90 is None and reg_az >= REGULUS_EAST_AZ:
            time_reg_90 = t_sec.utc_datetime().astimezone(EGYPT_TZ)
            sun_alt_reg = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
            reg_alt = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
            
            is_vis = (-18.0 <= sun_alt_reg < NELM_SUN_ALT)
            global_candidates.append({
                "month": "November", "day": day, "sun_alt": sun_alt_reg, "is_visible": is_vis, "delta": None
            })
        
        # Track when Mars hits True East
        if time_mars_90 is None and mars_az >= REGULUS_EAST_AZ:
            time_mars_90 = t_sec.utc_datetime().astimezone(EGYPT_TZ)
            sun_alt_mars = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
            mars_alt = giza.at(t_sec).observe(mars).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees

    print(f"\n📅 November {day}, 2026")
    if time_reg_90:
        print(f"   Regulus → 90° at: {time_reg_90.strftime('%H:%M:%S')} Local | Alt: {reg_alt:+.2f}° | Sun: {sun_alt_reg:+.2f}°")
    if time_mars_90:
        print(f"   Mars    → 90° at: {time_mars_90.strftime('%H:%M:%S')} Local | Alt: {mars_alt:+.2f}° | Sun: {sun_alt_mars:+.2f}°")
    
    # Calculate time difference between Regulus and Mars hitting the azimuth mark
    if time_reg_90 and time_mars_90:
        delta_min = (time_mars_90 - time_reg_90).total_seconds() / 60
        note = ""
        if delta_min < 15:
            note = "   ← CLOSE OVERLAP / CONJUNCTION"
        elif delta_min < 30:
            note = "   ← Moderate separation"
        print(f"   Difference: {delta_min:.1f} minutes apart{note}")
print("\n" + "="*70)


# =====================================================================
# SYSTEM CORE: FINAL DATA EVALUATION & SELECTION
# Iterates through all tracked dates and scores them against the Red Shift target
# =====================================================================
print("\n" + "="*85)
print("         PROJECT REGULUS - 100% DATA-DRIVEN SCAN COMPLETE v2.0")
print("="*85)
print("\n[ GLOBAL DYNAMIC EVALUATION ]")
print(f"Evaluating all scanned dates against ideal Red Shift atmospheric target: {IDEAL_SUN_ALT}°")
print("-" * 85)

best_match = None
best_score = -9999

for c in global_candidates:
    date_str = f"{c['month']} {c['day']}, 2026"
    alt = c['sun_alt']
    vis = c['is_visible']
    
    # Mathematical Scoring: Distance from the IDEAL_SUN_ALT. 
    # Closer to 0 is better. Perfect score = 0.
    score = -abs(alt - IDEAL_SUN_ALT)
    
    if vis:
        if c['delta'] is not None:
            m = int(abs(c['delta']) // 60)
            s = int(abs(c['delta']) % 60)
            print(f"• {date_str:<20} : ✅ Valid window ({m}m {s}s) | Sun alt: {alt:+.4f}° | Extinction Score: {score:+.4f}")
        else:
            print(f"• {date_str:<20} : ✅ Valid (Visible)        | Sun alt: {alt:+.4f}° | Extinction Score: {score:+.4f}")
            
        # Update the best match if this date scores higher
        if score > best_score:
            best_score = score
            best_match = c
    else:
        if alt >= NELM_SUN_ALT:
            reason = "Washed out by daylight"
        else:
            reason = "Pitch black / No red shift"
        print(f"• {date_str:<20} : ❌ Invalid ({reason}) | Sun alt: {alt:+.4f}° | Extinction Score: {score:+.4f}")


# --- Output the ultimate mathematical conclusion ---
print("\n[ ENGINE CONCLUSION : OPTIMAL RED-SHIFT SELECTION ]")
if best_match:
    print(f"🏆 SYSTEM SELECTION: {best_match['month']} {best_match['day']}, 2026")
    print(f"   Sun Altitude    : {best_match['sun_alt']:+.4f}°")
    print(f"   Target Zone     : {IDEAL_SUN_ALT}° (Maximum Atmospheric Extinction)")
    print(f"   Score Distance  : {abs(best_score):.4f}° deviation from perfect ideal")
    print("\nConclusion: The engine mathematically isolated this specific date as the absolute best")
    print("timeline fulfilling both pre-dawn True East alignment AND maximum 'Red Dawn' effect.")
else:
    print("System found NO mathematically viable timeline fulfilling the constraints across all scanned months.")
print("="*85)
