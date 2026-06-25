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


# ====================== CONFIGURATION ======================
ts = load.timescale()
eph = load('de421.bsp')
earth = eph['earth']
sun = eph['sun']
mars = eph['mars']
venus = eph['venus']

# Great Sphinx of Giza
giza = earth + wgs84.latlon(29.97526, 31.13758, elevation_m=20.0)
lon_hours = 31.13758 / 15.0

# Celestial objects
regulus = Star(ra_hours=(10, 8, 22.311), dec_degrees=(11, 58, 1.95))
alnilam = Star(ra_hours=(5, 36, 12.81), dec_degrees=(-1, 12, 6.9))
sgra = Star(ra_hours=(17, 45, 40.04), dec_degrees=(-29, 0, 28.1))

# Mayan Calendar baseline
start_date = datetime.date(2012, 12, 21)

# Constants
# --- NAKED EYE LIMITING MAGNITUDE (NELM) CALCULUS ---
# Regulus has a visual magnitude of +1.35 to +1.40.
# Empirical astronomical models for atmospheric extinction and dawn glare
# indicate that a +1.4 mag star becomes washed out to the naked eye 
# when the Sun reaches approx -2.72° altitude.
NELM_SUN_ALT = -2.72
REGULUS_EAST_AZ = 90.0

print("=====================================================================")
print("         [PROJECT REGULUS] - MASTER COMPUTATION ENGINE v1.4          ")
print("=====================================================================")


# ====================== CORE MODULE: SEPTEMBER 2026 ======================
days = [20, 21, 22, 23, 24]

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
    lst_data = None
    aln_pos = sgra_pos = mars_pos = venus_pos = None

    for s in range(3600):
        dt = t_start + datetime.timedelta(seconds=s)
        t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        
        # Positions
        sun_alt = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
        reg_pos = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
        reg_az = reg_pos[1].degrees
        reg_alt = reg_pos[0].degrees

        # NELM - Regulus becomes invisible
        if time_nelm is None and sun_alt >= NELM_SUN_ALT:
            time_nelm = dt + datetime.timedelta(hours=3)
            reg_az_at_nelm = reg_az
            reg_alt_at_nelm = reg_alt

        # Regulus reaches exact East (90°)
        if time_lock is None and reg_az >= REGULUS_EAST_AZ:
            time_lock = dt + datetime.timedelta(hours=3)
            sun_alt_at_lock = sun_alt
            reg_alt_at_lock = reg_alt

            # Capture skymap data at lock moment
            gmst = t_sec.gmst
            lst_hours = (gmst + lon_hours) % 24.0
            lst_h = int(lst_hours)
            lst_m = int((lst_hours - lst_h) * 60)
            lst_s = (lst_hours - lst_h) * 3600 - lst_m * 60

            aln_pos = giza.at(t_sec).observe(alnilam).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            sgra_pos = giza.at(t_sec).observe(sgra).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            mars_pos = giza.at(t_sec).observe(mars).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            venus_pos = giza.at(t_sec).observe(venus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)
            
            lst_data = (lst_h, lst_m, lst_s)

    # ====================== RESULTS ======================
    if time_nelm:
        print(f" 🌅 DAWN VISIBILITY LIMIT: Regulus fades at {time_nelm.strftime('%H:%M:%S')} Local | Az: {reg_az_at_nelm:.4f}°")

    if time_lock:
        print(f" 🏹 SPHINX 90° ALIGNMENT (Regulus hits True East):")
        print(f"    Local Time (UTC+3)     : {time_lock.strftime('%H:%M:%S')}")
        print(f"    Sun / Regulus Altitude : Sun: {sun_alt_at_lock:.4f}° | Regulus: +{reg_alt_at_lock:.4f}°")
        
        if time_nelm:
            delta = (time_nelm - time_lock).total_seconds()
            minutes = int(abs(delta) // 60)
            seconds = int(abs(delta) % 60)
            if delta > 0:
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


# ====================== NOVEMBER DEBUNK MODULE ======================
print("\n🔍 RUNNING DEBUNKING MODULE FOR NOVEMBER 22, 2026")
t_nov_start = datetime.datetime(2026, 11, 21, 23, 0, 0)

time_reg_90 = None
time_mars_90 = None
sun_alt_at_reg = None
sun_alt_at_mars = None

for s in range(14400):  # 4 godziny
    dt = t_nov_start + datetime.timedelta(seconds=s)
    t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    
    # Obliczamy azymuty
    reg_az = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[1].degrees
    mars_az = giza.at(t_sec).observe(mars).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[1].degrees
    
    # Regulus 90°
    if time_reg_90 is None and reg_az >= REGULUS_EAST_AZ:
        time_reg_90 = dt + datetime.timedelta(hours=2)
        sun_alt_at_reg = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
    
    # Mars 90°
    if time_mars_90 is None and mars_az >= REGULUS_EAST_AZ:
        time_mars_90 = dt + datetime.timedelta(hours=2)
        sun_alt_at_mars = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees

print(f" 🎯 Regulus reaches 90° at: {time_reg_90.strftime('%H:%M:%S')} Local  |  Sun altitude: {sun_alt_at_reg:.4f}°")
print(f" 🎯 Mars reaches 90° at    : {time_mars_90.strftime('%H:%M:%S')} Local  |  Sun altitude: {sun_alt_at_mars:.4f}°")
print("=====================================================================")


# ====================== OCTOBER EMERGENCY SCAN ======================
print("\n🚨 RUNNING EMERGENCY SCAN FOR OCTOBER 2026")
oct_days = [6, 7, 8]
for day in oct_days:
    t_start = datetime.datetime(2026, 10, day, 0, 0, 0)
    found = False
    for s in range(28800):
        dt = t_start + datetime.timedelta(seconds=s)
        t_sec = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        reg_az = giza.at(t_sec).observe(regulus).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[1].degrees
        
        if reg_az >= REGULUS_EAST_AZ:
            sun_alt = giza.at(t_sec).observe(sun).apparent().altaz(temperature_C=21.0, pressure_mbar=1011.0)[0].degrees
            print(f" 🎯 October {day}: Regulus 90° at {(dt + datetime.timedelta(hours=3)).strftime('%H:%M:%S')} | Sun alt: {sun_alt:.4f}°")
            found = True
            break
    if not found:
        print(f" ❌ October {day}: No 90° alignment found in scanned window.")
print("=====================================================================")
