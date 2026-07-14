import datetime
import csv
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from zoneinfo import ZoneInfo
from skyfield.api import load, Star, wgs84
from skyfield import almanac
import numpy as np
import calendar
import time
import os

"""
=====================================================================
GLOSSARY
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
=====================================================================
"""

# =====================================================================
#                   GLOBAL USER INPUT ZONE & CONFIGURATION
# 👇 ================================================================ 👇
TARGET_YEARS = list(range(-10000, -7500))

# 300s jest O WIELE szybsze niż 1800s, ponieważ redukuje 6-krotnie 
# rozmiar najbardziej obciążającego skanowania "sekunda-po-sekundzie".
TIME_STEP_SECONDS = 300 

# 🔴 GŁÓWNY PRZEŁĄCZNIK ATMOSFERY 🔴
# Ustaw na False dla BŁYSKAWICZNEGO skanowania (czysta geometria orbit).
# Ustaw na True dla ultra-realistycznego wizualnego wschodu z Gizy (Mocno obciąża procesor).
USE_REFRACTION = False

NELM_SUN_ALT = -2.72  # sun altitude for naked-eye limiting magnitude (NELM) threshold
MONUMENT_ALIGNMENT_AZ = 90.0  # target azimuth for the monument's alignment
IDEAL_SUN_ALT = -6.5 # target sun altitude for optimal pre-dawn visibility (distinct from civil twilight)

RED_STAR_MIN = 4.0 # limit for the red star window (minimum altitude for Regulus to appear red)
RED_STAR_MAX = 7.5  # limit for the red star window (maximum altitude for Regulus to appear red)

SITE_NAME = "Great Sphinx of Giza (Head)"  # here you can specify the name of your site
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

# 👆 ================================================================ 👆

if isinstance(TARGET_YEARS, int):
    TARGET_YEARS = [TARGET_YEARS]

# =====================================================================
# EPHEMERIS & TARGET SETUP
# 👇 ================================================================ 👇
ts = load.timescale()
eph = load("de441.bsp")  # 👆 here you may choose a different ephemeris file 
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

    year_candidates = []
    output_buffer = []

    # Dynamiczny pakiet refrakcji – wstrzykuje parametry tylko, gdy włączone
    ref_kwargs = {"temperature_C": ATM_TEMPERATURE, "pressure_mbar": ATM_PRESSURE} if USE_REFRACTION else {}

    for month in range(1, 13):
        
        _, last_day = calendar.monthrange(TARGET_YEAR, month)
        
        start_t = ts.tt(TARGET_YEAR, month, 1, 0, 0, 0)
        end_t = ts.tt(TARGET_YEAR, month, last_day, 23, 59, 59)
        
        num_steps = int((end_t.tt - start_t.tt) * 86400 / TIME_STEP_SECONDS)
        jd_matrix = start_t.tt + (np.arange(num_steps) * (TIME_STEP_SECONDS / 86400.0))
        t_arr = ts.tt_jd(jd_matrix)

        reg_pos = (
            site.at(t_arr)
            .observe(regulus)
            .apparent()
            .altaz(**ref_kwargs)
        )
        reg_azs = np.atleast_1d(reg_pos[1].degrees)
        
        crossings = np.where(np.diff(np.sign(reg_azs - MONUMENT_ALIGNMENT_AZ)) > 0)[0]

        for idx in crossings:
            rough_t = t_arr[idx]
            rough_sun_alt = site.at(rough_t).observe(sun).apparent().altaz(**ref_kwargs)[0].degrees
            if rough_sun_alt > 0.0:
                continue

            jd_start = t_arr[idx].tt
            sec_steps = np.arange(0, int(TIME_STEP_SECONDS) + 2) / 86400.0
            mini_jd = jd_start + sec_steps
            mini_t = ts.tt_jd(mini_jd)
            
            mini_reg = site.at(mini_t).observe(regulus).apparent().altaz(**ref_kwargs)
            mini_azs = mini_reg[1].degrees
            
            exact_sec_idx = np.argmin(np.abs(mini_azs - MONUMENT_ALIGNMENT_AZ))
            
            t_lock = mini_t[exact_sec_idx]
            sun_alt = site.at(t_lock).observe(sun).apparent().altaz(**ref_kwargs)[0].degrees
            reg_alt = mini_reg[0].degrees[exact_sec_idx]
           
            body_data_at_lock = {}
            
            if sun_alt < -2.72:
                for name, body in planets.items():
                    pos = site.at(t_lock).observe(body).apparent().altaz(**ref_kwargs)
                    body_data_at_lock[name] = (np.atleast_1d(pos[0].degrees)[0], np.atleast_1d(pos[1].degrees)[0])

                moon_illum = 0.0
                try:
                    t_lock_arr = ts.tt(jd=[t_lock.tt, t_lock.tt + 0.00001])
                    moon_illum = float(almanac.fraction_illuminated(eph, 'moon', t_lock_arr)[0]) * 100.0
                except: pass

                y, mo, d, h, m, s = t_lock.utc
                date_str = f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
                time_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

                mars_az_val = body_data_at_lock['mars'][1] if 'mars' in body_data_at_lock else 0

                candidate_data = {
                    "date": date_str,   
                    "time": time_str,
                    "sun_alt": sun_alt,
                    "reg_alt": reg_alt,
                    "is_visible": True,
                    "delta": 0.0,
                    "moon_alt": body_data_at_lock['moon'][0] if 'moon' in body_data_at_lock else 0,
                    "moon_illum": moon_illum,
                    "venus_az": body_data_at_lock['venus'][1] if 'venus' in body_data_at_lock else 0,
                    "venus_alt": body_data_at_lock['venus'][0] if 'venus' in body_data_at_lock else 0,
                    "mars_az": mars_az_val,
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
                    "sirius_az": float(np.atleast_1d(site.at(t_lock).observe(sirius).apparent().altaz(**ref_kwargs)[1].degrees)[0]),
                    "sirius_alt": float(np.atleast_1d(site.at(t_lock).observe(sirius).apparent().altaz(**ref_kwargs)[0].degrees)[0]),
                    "vega_az": float(np.atleast_1d(site.at(t_lock).observe(vega).apparent().altaz(**ref_kwargs)[1].degrees)[0]),
                    "vega_alt": float(np.atleast_1d(site.at(t_lock).observe(vega).apparent().altaz(**ref_kwargs)[0].degrees)[0]),
                    "mars_delta_sec": float((mars_az_val - MONUMENT_ALIGNMENT_AZ) * 240) if mars_az_val != 0 else 0.0
                }
                year_candidates.append(candidate_data)
        
                log_msg = f"🏹 FOUND ALIGNMENT: {date_str} {time_str} UTC | Regulus Az: {reg_azs[idx]:.4f}°"
                output_buffer.append(log_msg)

    return year_candidates, "\n".join(output_buffer)


# =====================================================================
# SYSTEM MAIN BLOCK & ENGINE STARTUP
# =====================================================================
if __name__ == "__main__":
    AVAILABLE_CORES = 6  # 🔴 TWÓJ LIMIT RDZENI (Możesz pracować na kompie w tle)
    
    print("=====================================================================")
    print("         [PROJECT REGULUS] - Celestial Alignment Scan Engine")
    print("=====================================================================")
    print(f"TARGET YEARS SET TO: {TARGET_YEARS[0]} to {TARGET_YEARS[-1]}")
    print(f"CORES ENGAGED      : {AVAILABLE_CORES}")
    print(f"SITE LOCATION      : {SITE_NAME}")
    print(f"TIME STEP          : {TIME_STEP_SECONDS} seconds")
    print(f"REFRACTION         : {'ENABLED (High Precision, Slow)' if USE_REFRACTION else 'DISABLED (Geometric, Ultra-Fast)'}")
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
        "Date", "Sun_Alt", "Deviation_From_Ideal", "Regulus_Alt", "Is_Visible",
        "Visibility_Delta_Sec", "Moon_Alt", "Moon_Illum_%", "Venus_Az", "Venus_Alt",
        "Mars_Az", "Mars_Alt", "Jupiter_Az", "Jupiter_Alt", "Neptune_Az",
        "Neptune_Alt", "Saturn_Az", "Saturn_Alt", "Mercury_Az", "Mercury_Alt",
        "Uranus_Az", "Uranus_Alt", "Pluto_Az", "Pluto_Alt", "Sirius_Az",
        "Sirius_Alt", "Vega_Az", "Vega_Alt", "Mars_Delta_Sec"
    ]

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

    print(f"🚀 Scan started. Results will be appended to: {csv_filename}")

    global_candidates = []
    fmt = lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else x

    total_years = len(TARGET_YEARS)
    completed_years = 0
    start_time = time.time()

    with ProcessPoolExecutor(max_workers=AVAILABLE_CORES) as executor:
        futures = {executor.submit(scan_single_year, y): y for y in TARGET_YEARS}

        for future in as_completed(futures):
            current_scanned_year = futures[future]

            try:
                candidates, log_output = future.result()
                if log_output.strip():
                    print(log_output)

                with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    for c in candidates:
                        row = [
                            c["date"], fmt(c["sun_alt"]), fmt(abs(c["sun_alt"] - IDEAL_SUN_ALT)),
                            fmt(c["reg_alt"]), c["is_visible"], fmt(c["delta"]) if c["delta"] is not None else "N/A",
                            fmt(c["moon_alt"]), fmt(c["moon_illum"]), fmt(c.get("venus_az")),
                            fmt(c.get("venus_alt")), fmt(c.get("mars_az")), fmt(c.get("mars_alt")),
                            fmt(c.get("jupiter_az")), fmt(c.get("jupiter_alt")), fmt(c.get("neptune_az")),
                            fmt(c.get("neptune_alt")), fmt(c.get("saturn_az")) or "N/A",
                            fmt(c.get("saturn_alt")) or "N/A", fmt(c.get("mercury_az")) or "N/A",
                            fmt(c.get("mercury_alt")) or "N/A", fmt(c.get("uranus_az")) or "N/A",
                            fmt(c.get("uranus_alt")) or "N/A", fmt(c.get("pluto_az")) or "N/A",
                            fmt(c.get("pluto_alt")) or "N/A", fmt(c.get("sirius_az")) or "N/A",
                            fmt(c.get("sirius_alt")) or "N/A", fmt(c.get("vega_az")) or "N/A",
                            fmt(c.get("vega_alt")) or "N/A", fmt(c["mars_delta_sec"]),
                        ]
                        writer.writerow(row)

                global_candidates.extend(candidates)

                completed_years += 1
                percent_done = (completed_years / total_years) * 100

                elapsed_time = time.time() - start_time
                avg_time_per_year = elapsed_time / completed_years
                years_left = total_years - completed_years
                eta_seconds = int(avg_time_per_year * years_left)
                eta_str = str(datetime.timedelta(seconds=eta_seconds))

                bar_length = 30
                filled_length = int(bar_length * completed_years // total_years)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                print(
                    f"[{bar}] {percent_done:5.1f}% | ⏳ ETA: {eta_str} | ✅ Year {current_scanned_year} appended to CSV! ({completed_years}/{total_years})"
                )

            except Exception as e:
                completed_years += 1
                percent_done = (completed_years / total_years) * 100
                
                elapsed_time = time.time() - start_time
                avg_time_per_year = elapsed_time / completed_years
                years_left = total_years - completed_years
                eta_seconds = int(avg_time_per_year * years_left)
                eta_str = str(datetime.timedelta(seconds=eta_seconds))

                bar_length = 30
                filled_length = int(bar_length * completed_years // total_years)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                print(
                    f"[{bar}] {percent_done:5.1f}% | ⏳ ETA: {eta_str} | ❌ Error processing year {current_scanned_year}: {e} ({completed_years}/{total_years})"
                )

    # =====================================================================
    # FINAL EVALUATION: ZEP TEPI HORIZON LOCK
    # =====================================================================
    print("\n" + "=" * 85)
    print("         PROJECT REGULUS - ZEP TEPI (TRUE EAST) EVALUATION")
    print("=" * 85)

    global_candidates.sort(key=lambda x: x["date"])
    best_match = None
    best_score = -9999

    for c in global_candidates:
        if c["is_visible"]:

            score = -abs(c["reg_alt"])
            
            if score > best_score:
                best_score = score
                best_match = c

    print("\n[ ENGINE CONCLUSION : TRUE EAST HORIZON LOCK (HANCOCK TEST) ]")
    if best_match:
        print(f"🏆 SYSTEM SELECTION (Closest to Horizon): {best_match['date']}")
        print(f"   Regulus Altitude: {best_match['reg_alt']:+.4f}° (Ideal is 0.0°)")
        print(f"   Sun Altitude    : {best_match['sun_alt']:+.4f}°")
        print(f"   Deviation       : {abs(best_score):.4f}° from true horizon")
    else:
        print("System found NO viable timeline in this scan segment.")
    print("=" * 85)
