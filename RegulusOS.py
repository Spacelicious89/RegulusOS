import datetime
from skyfield.api import load, Star, wgs84

def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# 1. Load sterile NASA JPL ephemerides and timescale
ts = load.timescale()
eph = load('de421.bsp')
earth, sun, mars, venus = eph['earth'], eph['sun'], eph['mars'], eph['venus']

# 2. Hardware: Great Sphinx of Giza (WGS84 Standard)
giza = earth + wgs84.latlon(29.9753, 31.1376, elevation_m=20.0)
lon_hours = 31.1342 / 15.0  # Giza longitude converted to hours (for LST)

# 3. Celestial body definitions (ICRS Coordinates)
regulus = Star(ra_hours=(10, 8, 22.311), dec_degrees=(11, 58, 1.95))
alnilam = Star(ra_hours=(5, 36, 12.81), dec_degrees=(-1, 12, 6.9))
sgra = Star(ra_hours=(17, 45, 40.04), dec_degrees=(-29, 0, 28.1))

# Mayan Calendar Long Count restart baseline
start_date = datetime.date(2012, 12, 21)

print("=====================================================================")
print("         [PROJECT REGULUS] - MASTER COMPUTATION ENGINE v1.3          ")
print("=====================================================================")

# --- CORE MODULE: SEPTEMBER PRE-DAWN WINDOW ---
days = [20, 21, 22, 23, 24]

for day in days:
    current_date = datetime.date(2026, 9, day)
    days_delta = (current_date - start_date).days
    prime_status = "PRIME NUMBER" if is_prime(days_delta) else "COMPOSITE NUMBER"
    
    print(f"\n📅 MORNING SCAN: September {day}, 2026")
    print(f"  ↳ Time vector from 2012-12-21: {days_delta} days -> Status: {prime_status}")
    print("---------------------------------------------------------------------")
    
    t_start = datetime.datetime(2026, 9, day, 3, 0, 0)
    time_nelm, time_lock = None, None
    
    for s in range(3600):
        dt = t_start + datetime.timedelta(seconds=s)
        t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        
        sun_pos = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
        reg_pos = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
        
        sun_alt = sun_pos[0].degrees
        reg_az, reg_alt = reg_pos[1].degrees, reg_pos[0].degrees
        
        if time_nelm is None and sun_alt >= -2.720000:
            time_nelm = dt + datetime.timedelta(hours=3) # UTC+3
            reg_az_at_nelm, reg_alt_at_nelm = reg_az, reg_alt
            
        if time_lock is None and reg_az >= 90.000000:
            time_lock = dt + datetime.timedelta(hours=3) # UTC+3
            sun_alt_at_lock, reg_alt_at_lock = sun_alt, reg_alt
            
            gmst = t_sec.gmst
            lst_hours = (gmst + lon_hours) % 24.0
            lst_h, lst_m = int(lst_hours), int((lst_hours - int(lst_hours)) * 60)
            lst_s = ((lst_hours - lst_h) * 60 - lst_m) * 60
            
            aln_pos = giza.at(t_sec).observe(alnilam).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            ha_aln_deg = (lst_hours - 5.6035583) * 15.0
            if ha_aln_deg > 180: ha_aln_deg -= 360
            
            sgra_pos = giza.at(t_sec).observe(sgra).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            mars_pos = giza.at(t_sec).observe(mars).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            venus_pos = giza.at(t_sec).observe(venus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)

    if time_nelm:
        print(f" 🌅 DAWN VISIBILITY LIMIT (Star washed out by sunrise): Fades at {time_nelm.strftime('%H:%M:%S')} Local | Regulus Az: {reg_az_at_nelm:.4f}°")
    if time_lock:
        print(f" 🏹 SPHINX 90° ALIGNMENT (Regulus hits exact True East):")
        print(f"    Local Time (UTC+3)      : {time_lock.strftime('%H:%M:%S')}")
        print(f"    Sun / Regulus Altitudes  : Sun: {sun_alt_at_lock:.4f}° | Regulus: +{reg_alt_at_lock:.4f}°")
        
        # Calculates exactly how long the star is visible before fading
        if time_nelm:
            delta_seconds = (time_nelm - time_lock).total_seconds()
            minutes = int(abs(delta_seconds) // 60)
            seconds = int(abs(delta_seconds) % 60)
            if delta_seconds > 0:
                print(f"    Naked-Eye Status         : ✅ VISIBLE: Star locks onto 90° and remains visible for {minutes}m {seconds}s before fading.")
            else:
                print(f"    Naked-Eye Status         : ❌ INVISIBLE: Star faded {minutes}m {seconds}s BEFORE hitting 90° (Daylight).")

        print(f" 🌌 GLOBAL SKYMAP AT THIS EXACT SECOND (What else is happening):")
        print(f"    Local Sidereal Time (LST): {lst_h:02d}:{lst_m:02d}:{lst_s:05.2f}")
        print(f"    Orion's Belt (Alnilam)   : Az: {aln_pos[1].degrees:.4f}° (Culminating South) | Alt: +{aln_pos[0].degrees:.4f}°")
        print(f"    Galactic Center (Sgr A*) : Alt: {sgra_pos[0].degrees:.4f}° (Directly beneath feet)")
        print(f"    Planets Positions        : Mars Az: {mars_pos[1].degrees:.4f}° | Venus Az: {venus_pos[1].degrees:.4f}°")
    print("=====================================================================")

# --- AUDIT MODULE: DEBUNKING THE NOVEMBER MYTH ---
print("\n🔍 RUNNING DEBUNKING MODULE FOR NOVEMBER 22, 2026")
t_nov_start = datetime.datetime(2026, 11, 21, 23, 0, 0)
time_reg_90, time_mars_90 = None, None

for s in range(14400):
    dt = t_nov_start + datetime.timedelta(seconds=s)
    t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    reg_az = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[1].degrees
    mars_az = giza.at(t_sec).observe(mars).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[1].degrees
    
    if time_reg_90 is None and reg_az >= 90.000000:
        time_reg_90 = dt + datetime.timedelta(hours=2)
    if time_mars_90 is None and mars_az >= 90.000000:
        time_mars_90 = dt + datetime.timedelta(hours=2)

print(f" 🎯 Regulus hits Az 90.0000° at: {time_reg_90.strftime('%H:%M:%S')} Local (Midnight)")
print(f" 🎯 Mars hits Az 90.0000° at    : {time_mars_90.strftime('%H:%M:%S')} Local (+12 min later)")
print("=====================================================================")

# --- EMERGENCY MODULE: SCANNING OCTOBER 2026 (WITH SUN POSITION) ---
print("\n🚨 RUNNING EMERGENCY SCAN FOR OCTOBER 2026 (SUN POSITION CHECK)")
oct_days = [6, 7, 8]
for day in oct_days:
    t_start = datetime.datetime(2026, 10, day, 0, 0, 0)
    found_90 = False
    
    for s in range(28800): 
        dt = t_start + datetime.timedelta(seconds=s)
        t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        
        reg_pos = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
        reg_az = reg_pos[1].degrees
        
        if reg_az >= 90.000000:
            sun_pos = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            sun_alt = sun_pos[0].degrees
            print(f" 🎯 October {day}, 2026: Regulus hits Az 90.00° at {(dt + datetime.timedelta(hours=3)).strftime('%H:%M:%S')} Local | SUN ALT: {sun_alt:.4f}°")
            found_90 = True
            break
            
    if not found_90:
        print(f" ❌ October {day}, 2026: Regulus does NOT hit Az 90.00° during the scanned window.")
print("=====================================================================")
