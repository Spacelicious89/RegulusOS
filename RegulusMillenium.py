import datetime
import csv
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from zoneinfo import ZoneInfo
from skyfield.api import load, Star, wgs84
from skyfield import almanac

"""
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
"""

# =====================================================================
#                   GLOBAL USER INPUT ZONE & CONFIGURATION
# 👇 ================================================================ 👇

TARGET_YEARS = list(range(-2590, -2500)) #ephemeris setting below look for "👇"
# here you can specify the years you want to scan, de441 ephemeris supports years from -12352 to 12352, use de421 support for years from -4712 to 2119.
TIME_STEP_SECONDS = 300  
# we use 2 steps: 300 seconds (5 minutes) for the main scan, and 1 second for the mini-scan around the alignment window.

NELM_SUN_ALT = -2.72  # sun altitude for naked-eye limiting magnitude (NELM) threshold
MONUMENT_ALIGNMENT_AZ = 90.0  # target azimuth for the monument's alignment
IDEAL_SUN_ALT = -6.5 # target sun altitude for optimal pre-dawn visibility (distinct from civil twilight)

RED_STAR_MIN = 4.0 # limit for the red star window (minimum altitude for Regulus to appear red)
RED_STAR_MAX = 7.5  # limit for the red star window (maximum altitude for Regulus to appear red)

SITE_NAME = "Great Sphinx of Giza (Head)"  # here you can specify the name of your site, it will be printed in the log and in the CSV file.
SITE_LAT = 29.975234  # latitude of the site in decimal degrees
SITE_LON = 31.137772  # longitude of the site in decimal degrees
SITE_ELEVATION = 20.0  # elevation of the site in meters above sea level
SITE_TZ = "Africa/Cairo"  # timezone of the site, used for local time conversion in the log and CSV output.

ATM_TEMPERATURE = 18.0  # temperature in Celsius for atmospheric refraction calculations
ATM_PRESSURE = 1013.5  # pressure in hPa for atmospheric refraction calculations

TARGET_PLANETS = {  # here you can specify the target planets for the scan, using their Skyfield ephemeris names
    "mars": "mars barycenter",
    "venus": "venus",
    "moon": "moon",
    "jupiter": "jupiter barycenter",
    "saturn": "saturn barycenter",
    "mercury": "mercury",
    "uranus": "uranus barycenter",
    "neptune": "neptune barycenter",
    "pluto": "pluto barycenter",
}

TARGET_SCANS = {  # here you can specify the months and days to scan for each month, along with the start hour and scan duration in hours. This allows for precise control over the scanning windows.
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
    12: {"days": range(1, 32), "start_h": 0, "scan_h": 24},
}

# 👆 ================================================================ 👆

if isinstance(TARGET_YEARS, int):
    TARGET_YEARS = [TARGET_YEARS]


# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def jd_to_calendar(jd):
    jd += 0.5
    Z = int(jd)
    F = jd - Z
    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)

    day = B - D - int(30.6001 * E) + F
    month = E - 1 if E < 14 else E - 13
    year = C - 4716 if month > 2 else C - 4715

    frac = day - int(day)
    h = frac * 24
    m = (h - int(h)) * 60
    s = (m - int(m)) * 60

    return int(year), int(month), int(day), int(h), int(m), int(s)


def safe_date(jd_float):
    y, mo, d, h, m, s = jd_to_calendar(jd_float)
    return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"


def safe_time(jd_float):
    y, mo, d, h, m, s = jd_to_calendar(jd_float)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"


# =====================================================================
# EPHEMERIS & TARGET SETUP
# 👇 ================================================================ 👇
ts = load.timescale()
eph = load(
    "de441.bsp"
)  # 👆 here you may choose a different ephemeris file if you want to scan years outside the range of de441, e.g., de421 for years -4712 to 2119.
earth, sun = eph["earth"], eph["sun"]

planets = {name: eph[target] for name, target in TARGET_PLANETS.items()}

site = earth + wgs84.latlon(SITE_LAT, SITE_LON, elevation_m=SITE_ELEVATION)

regulus = Star(
    ra_hours=(10, 8, 22.311),
    dec_degrees=(11, 58, 1.95),
    ra_mas_per_year=-248.94,
    dec_mas_per_year=4.98,
)

alnilam = Star(
    ra_hours=(5, 36, 12.81),
    dec_degrees=(-1, 12, 6.9),
    ra_mas_per_year=-1.02,
    dec_mas_per_year=-0.73,
)

sirius = Star(
    ra_hours=(6, 45, 8.917),
    dec_degrees=(-16, 42, 58.02),
    ra_mas_per_year=-546.01,
    dec_mas_per_year=-1223.07,
)

vega = Star(
    ra_hours=(18, 36, 56.336),
    dec_degrees=(38, 47, 11.28),
    ra_mas_per_year=200.94,
    dec_mas_per_year=286.23,
)

start_epoch_jd = ts.utc(2012, 12, 21).tt


# =====================================================================
# CORE ENGINE - MULTIPROCESSING WRAPPER
# =====================================================================
def scan_single_year(TARGET_YEAR):
    import numpy as np

    year_candidates = []
    output_buffer = []

    def log(msg):
        output_buffer.append(msg)

    for month, config in sorted(TARGET_SCANS.items()):
        log("=" * 75)
        log(f"                 SCAN MODULE - MONTH: {month:02d} / {TARGET_YEAR}")
        log("=" * 75)

        scan_seconds = config["scan_h"] * 3600
        step_days = TIME_STEP_SECONDS / 86400.0
        base_t = ts.tt(TARGET_YEAR, month, config["days"][0], config["start_h"], 0, 0)
        base_jd = base_t.tt
        num_steps = (scan_seconds // TIME_STEP_SECONDS) * len(config["days"])

        jd_matrix = base_jd + (np.arange(num_steps) * step_days)
        t_arr = ts.tt_jd(jd_matrix)

        reg_pos = (
            site.at(t_arr)
            .observe(regulus)
            .apparent()
            .altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
        )
        reg_azs = np.atleast_1d(reg_pos[1].degrees)
        reg_alts = np.atleast_1d(reg_pos[0].degrees)
        sun_alts = np.atleast_1d(
            site.at(t_arr)
            .observe(sun)
            .apparent()
            .altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[0]
            .degrees
        )

        crossings = np.where(np.diff(np.sign(reg_azs - MONUMENT_ALIGNMENT_AZ)) > 0)[0]

        for idx in crossings:
            jd_start = t_arr[idx].tt
            sec_steps = np.arange(0, 301) / 86400.0
            mini_jd = jd_start + sec_steps
            mini_t = ts.tt_jd(mini_jd)
            
            mini_reg = site.at(mini_t).observe(regulus).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
            mini_azs = mini_reg[1].degrees
            
            exact_sec_idx = np.argmin(np.abs(mini_azs - MONUMENT_ALIGNMENT_AZ))
            
            t_lock = mini_t[exact_sec_idx]
            sun_alt = site.at(t_lock).observe(sun).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[0].degrees
            reg_alt = mini_reg[0].degrees[exact_sec_idx]
           
            # ZABEZPIECZENIE: Tworzymy pusty słownik, żeby Python nie zwariował
            body_data_at_lock = {}
            
            if sun_alt < -2.72:
                for name, body in planets.items():
                    pos = site.at(t_lock).observe(body).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)
                    body_data_at_lock[name] = (np.atleast_1d(pos[0].degrees)[0], np.atleast_1d(pos[1].degrees)[0])

                moon_illum = 0.0
                try:
                    t_lock_arr = ts.tt(jd=[t_lock.tt, t_lock.tt + 0.00001])
                    moon_illum = float(almanac.fraction_illuminated(eph, 'moon', t_lock_arr)[0]) * 100.0
                except: pass

                candidate_data = {
                    "date": safe_date(t_lock.tt),
                    "sun_alt": sun_alt,
                    "reg_alt": reg_alt,
                    "is_visible": True,
                    "delta": 0,
                    "moon_alt": body_data_at_lock['moon'][0] if 'moon' in body_data_at_lock else 0,
                    "moon_illum": moon_illum,
                    "venus_az": body_data_at_lock['venus'][1] if 'venus' in body_data_at_lock else 0,
                    "venus_alt": body_data_at_lock['venus'][0] if 'venus' in body_data_at_lock else 0,
                    "mars_az": body_data_at_lock['mars'][1] if 'mars' in body_data_at_lock else 0,
                    "mars_alt": body_data_at_lock['mars'][0] if 'mars' in body_data_at_lock else 0,
                    "jupiter_az": body_data_at_lock['jupiter'][1] if 'jupiter' in body_data_at_lock else 0,
                    "jupiter_alt": body_data_at_lock['jupiter'][0] if 'jupiter' in body_data_at_lock else 0,
                    "neptune_az": body_data_at_lock['neptune'][1] if 'neptune' in body_data_at_lock else 0,
                    "neptune_alt": body_data_at_lock['neptune'][0] if 'neptune' in body_data_at_lock else 0,
                    "uranus_az": body_data_at_lock['uranus'][1] if 'uranus' in body_data_at_lock else 0,
                    "uranus_alt": body_data_at_lock['uranus'][0] if 'uranus' in body_data_at_lock else 0,
                    "pluto_az": body_data_at_lock['pluto'][1] if 'pluto' in body_data_at_lock else 0,
                    "pluto_alt": body_data_at_lock['pluto'][0] if 'pluto' in body_data_at_lock else 0,
                    "saturn_az": body_data_at_lock['saturn'][1] if 'saturn' in body_data_at_lock else 0,
                    "saturn_alt": body_data_at_lock['saturn'][0] if 'saturn' in body_data_at_lock else 0,
                    "mercury_az": body_data_at_lock['mercury'][1] if 'mercury' in body_data_at_lock else 0,
                    "mercury_alt": body_data_at_lock['mercury'][0] if 'mercury' in body_data_at_lock else 0,
                    # --- DODANE NOWE GWIAZDY ---
                    "sirius_az": float(np.atleast_1d(site.at(t_lock).observe(sirius).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[1].degrees)[0]),
                    "sirius_alt": float(np.atleast_1d(site.at(t_lock).observe(sirius).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[0].degrees)[0]),
                    "vega_az": float(np.atleast_1d(site.at(t_lock).observe(vega).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[1].degrees)[0]),
                    "vega_alt": float(np.atleast_1d(site.at(t_lock).observe(vega).apparent().altaz(temperature_C=ATM_TEMPERATURE, pressure_mbar=ATM_PRESSURE)[0].degrees)[0]),
                    "mars_delta_sec": 0
                }
                year_candidates.append(candidate_data)
                log(f"🏹 FOUND ALIGNMENT: {safe_time(t_lock.tt)} TT | Regulus Az: {reg_azs[idx]:.4f}°")

    return year_candidates, "\n".join(output_buffer)


# =====================================================================
# SYSTEM MAIN BLOCK & ENGINE STARTUP
# =====================================================================
if __name__ == "__main__":
    print("=====================================================================")
    print("         [PROJECT REGULUS] - Celestial Alignment Scan Engine")
    print("=====================================================================")
    print(f"TARGET YEARS SET TO: {TARGET_YEARS}")
    print(
        f"CORES ENGAGED      : {min(6, multiprocessing.cpu_count())} (Limited to preserve system responsiveness)"
    )
    print(f"SITE LOCATION      : {SITE_NAME}")
    print(f"SCANS ACTIVE       : Months {sorted(list(TARGET_SCANS.keys()))}")
    print(f"TIME STEP          : {TIME_STEP_SECONDS} seconds")
    print(f"ATMOSPHERE SET TO  : {ATM_TEMPERATURE}°C, {ATM_PRESSURE} hPa")
    print("\nKey Parameters:")
    print(f"• Alignment      : Azimuth = {MONUMENT_ALIGNMENT_AZ}°")
    print(f"• Dawn Limit : Sun ~ {IDEAL_SUN_ALT}°")
    print(f"• Red Star Phase : Regulus Alt ~ {RED_STAR_MIN}° - {RED_STAR_MAX}°")
    print(
        "\nWARNING: Multiprocessing initialized. Please wait for the final compiled log..."
    )
    print("=====================================================================\n")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"regulus_scan_results_{timestamp}.csv"
    headers = [
        "Date",
        "Sun_Alt",
        "Deviation_From_Ideal",
        "Regulus_Alt",
        "Is_Visible",
        "Visibility_Delta_Sec",
        "Moon_Alt",
        "Moon_Illum_%",
        "Venus_Az",
        "Venus_Alt",
        "Mars_Az",
        "Mars_Alt",
        "Jupiter_Az",
        "Jupiter_Alt",
        "Neptune_Az",
        "Neptune_Alt",
        "Saturn_Az",
        "Saturn_Alt",
        "Mercury_Az",
        "Mercury_Alt",
        "Uranus_Az",
        "Uranus_Alt",
        "Pluto_Az",
        "Pluto_Alt",
        "Sirius_Az",
        "Sirius_Alt",
        "Vega_Az",
        "Vega_Alt",
        "Mars_Delta_Sec",
    ]

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

    print(f"🚀 Scan started. Results will be appended to: {csv_filename}")

    global_candidates = []
    fmt = lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else x

    total_years = len(TARGET_YEARS)
    completed_years = 0

    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(scan_single_year, y): y for y in TARGET_YEARS}

        for future in as_completed(futures):
            current_scanned_year = futures[future]

            try:
                candidates, log_output = future.result()
                print(log_output)

                with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    for c in candidates:
                        row = [
                            c["date"],
                            fmt(c["sun_alt"]),
                            fmt(abs(c["sun_alt"] - IDEAL_SUN_ALT)),
                            fmt(c["reg_alt"]),
                            c["is_visible"],
                            fmt(c["delta"]) if c["delta"] is not None else "N/A",
                            fmt(c["moon_alt"]),
                            fmt(c["moon_illum"]),
                            fmt(c.get("venus_az")),
                            fmt(c.get("venus_alt")),
                            fmt(c.get("mars_az")),
                            fmt(c.get("mars_alt")),
                            fmt(c.get("jupiter_az")),
                            fmt(c.get("jupiter_alt")),
                            fmt(c.get("neptune_az")),
                            fmt(c.get("neptune_alt")),
                            fmt(c.get("saturn_az")) or "N/A",
                            fmt(c.get("saturn_alt")) or "N/A",
                            fmt(c.get("mercury_az")) or "N/A",
                            fmt(c.get("mercury_alt")) or "N/A",
                            fmt(c.get("uranus_az")) or "N/A",
                            fmt(c.get("uranus_alt")) or "N/A",
                            fmt(c.get("pluto_az")) or "N/A",
                            fmt(c.get("pluto_alt")) or "N/A",
                            fmt(c.get("sirius_az")) or "N/A",
                            fmt(c.get("sirius_alt")) or "N/A",
                            fmt(c.get("vega_az")) or "N/A",
                            fmt(c.get("vega_alt")) or "N/A",
                            fmt(c["mars_delta_sec"]),
                        ]
                        writer.writerow(row)

                global_candidates.extend(candidates)

                completed_years += 1
                percent_done = (completed_years / total_years) * 100

                bar_length = 30
                filled_length = int(bar_length * completed_years // total_years)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                print(
                    f"[{bar}] {percent_done:5.1f}% | ✅ Year {current_scanned_year} appended to CSV! ({completed_years}/{total_years})"
                )

            except Exception as e:
                completed_years += 1
                percent_done = (completed_years / total_years) * 100
                bar_length = 30
                filled_length = int(bar_length * completed_years // total_years)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                print(
                    f"[{bar}] {percent_done:5.1f}% | ❌ Error processing year {current_scanned_year}: {e} ({completed_years}/{total_years})"
                )

    # =====================================================================
    # FINAL EVALUATION
    # =====================================================================
    print("\n" + "=" * 85)
    print("         PROJECT REGULUS - GLOBAL EVALUATION")
    print("=" * 85)

    global_candidates.sort(key=lambda x: x["date"])
    best_match = None
    best_score = -9999

    for c in global_candidates:
        if c["is_visible"]:
            score = -abs(c["sun_alt"] - IDEAL_SUN_ALT)
            date_str = c["date"]
            print(
                f"• {date_str:<20} : ✅ Valid Window | Sun alt: {c['sun_alt']:+.4f}° | Score: {score:+.4f}"
            )
            if score > best_score:
                best_score = score
                best_match = c

    print("\n[ ENGINE CONCLUSION : OPTIMAL before the dawn SELECTION ]")
    if best_match:
        print(f"🏆 SYSTEM SELECTION: {best_match['date']}")
        print(f"   Sun Altitude    : {best_match['sun_alt']:+.4f}°")
        print(f"   Target Zone     : {IDEAL_SUN_ALT}° (Max Extinction)")
        print(f"   Deviation       : {abs(best_score):.4f}° from ideal")
    else:
        print("System found NO viable timeline in this scan segment.")
    print("=" * 85)
