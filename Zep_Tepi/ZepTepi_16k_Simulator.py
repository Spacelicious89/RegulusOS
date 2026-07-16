from skyfield.api import load, Star, wgs84
import numpy as np
import csv
# ==========================================
# 1. STAR CONFIGURATION (Proper motion incl.)
# ==========================================
STARS = {
    "Alnitak": Star(
        ra_hours=(5, 40, 45.5),
        dec_degrees=(-1, 56, 34),
        ra_mas_per_year=2.18,
        dec_mas_per_year=-1.25,
        parallax_mas=2.16,
    ),
    "Alnilam": Star(
        ra_hours=(5, 36, 12.81),
        dec_degrees=(-1, 12, 6.9),
        ra_mas_per_year=2.19,
        dec_mas_per_year=-1.12,
        parallax_mas=1.73,
    ),
    "Mintaka": Star(
        ra_hours=(5, 32, 0.4),
        dec_degrees=(0, 17, 57),
        ra_mas_per_year=2.55,
        dec_mas_per_year=-1.22,
        parallax_mas=2.26,
    ),
    "Regulus": Star(
        ra_hours=(10, 8, 22.311),
        dec_degrees=(11, 58, 1.95),
        ra_mas_per_year=-247.96,
        dec_mas_per_year=3.87,
        parallax_mas=42.11,
    ),
    "Sirius": Star(
        ra_hours=(6, 45, 8.9),
        dec_degrees=(-16, 42, 58),
        ra_mas_per_year=-546.01,
        dec_mas_per_year=-1223.08,
        parallax_mas=379.21,
    ),
    "Thuban": Star(
        ra_hours=(14, 4, 23.3),
        dec_degrees=(64, 22, 33),
        ra_mas_per_year=-14.0,
        dec_mas_per_year=-24.0,
        parallax_mas=14.0,
    ),
    "Kochab": Star(
        ra_hours=(14, 50, 42.3),
        dec_degrees=(74, 9, 20),
        ra_mas_per_year=-140.0,
        dec_mas_per_year=-60.0,
        parallax_mas=25.0,
    ),
}

# ==========================================
# 2. THEORY DEFINITIONS
# ==========================================
# Added 'target' for all shafts to verify the specific altitude required by Bauval.
THEORIES = {
    "Orion": {
        "stars": ["Alnilam"],
        "criteria": {"type": "nadir_altitude", "target": 9.33, "tolerance": 0.5},
    },
    "Leo": {
        "stars": ["Regulus"],
        "criteria": {"type": "azimuth_match", "target": 90.0, "tolerance": 0.5},
    },
    "King_Shaft": {
        "stars": ["Alnitak"],
        "criteria": {
            "type": "meridian_transit",
            "direction": 180.0,
            "target": 45.0,
            "tolerance": 0.2,
        },
    },
    "Queen_Shaft": {
        "stars": ["Sirius"],
        "criteria": {
            "type": "meridian_transit",
            "direction": 180.0,
            "target": 35.0,
            "tolerance": 0.2,
        },
    },
    "North_Shaft": {
        "stars": ["Thuban"],
        "criteria": {
            "type": "meridian_transit",
            "direction": 0.0,
            "target": 32.5,
            "tolerance": 0.2,
        },
    },
}

# ==========================================
# 3. ASTRONOMICAL ENGINE
# ==========================================
ts = load.timescale()
eph = load("de441.bsp")
earth = eph["earth"]

OBSERVER_SPHINX = earth + wgs84.latlon(29.975278, 31.137500, elevation_m=20.0)

OBSERVER_KHUFU = earth + wgs84.latlon(29.979167, 31.134167, elevation_m=70.0)


def scan_star(star_name, time, observer):
    alt, az, _ = observer.at(time).observe(STARS[star_name]).apparent().altaz()
    return {"alt": alt.degrees, "az": az.degrees}


def evaluate_theory(theory_name, year):
    theory = THEORIES[theory_name]
    criteria = theory["criteria"]

    current_observer = OBSERVER_SPHINX if theory_name == "Leo" else OBSERVER_KHUFU

    # Precession cycle shifts over millennia. Testing one full September day per year is sufficient.
    # Vernal Equinox (March 21) - The Holy Grail of Hancock's Sphinx Theory
    t_start = ts.utc(year, 3, 21)
    t_end = ts.utc(year, 3, 22)
    # Scanning every 10 minutes for extreme precision during the 24h window
    times = ts.linspace(t_start, t_end, 144)

    positions = [scan_star(theory["stars"][0], t, current_observer) for t in times]

    if criteria["type"] == "nadir_altitude":
        # Culmination at the South meridian (maximum altitude reached)
        metric = max(p["alt"] for p in positions)
        dev = abs(metric - criteria["target"])
        return {
            "pass": dev <= criteria["tolerance"],
            "deviation": dev,
            "metric": metric,
        }

    elif criteria["type"] == "meridian_transit":
        # Shafts check: Altitude exactly at meridian crossing
        if criteria["direction"] == 180.0:
            metric = max(p["alt"] for p in positions)  # Upper culmination (South)
        else:
            metric = min(
                p["alt"] for p in positions
            )  # Lower culmination (North, circumpolar)

        dev = abs(metric - criteria["target"])
        return {
            "pass": dev <= criteria["tolerance"],
            "deviation": dev,
            "metric": metric,
        }

    elif criteria["type"] == "azimuth_match":
        # Leo theory check: Azimuth at the exact moment of rising (East hemisphere)
        east_positions = [p for p in positions if p["az"] < 180]
        if east_positions:
            closest_to_horizon = min(east_positions, key=lambda p: abs(p["alt"]))
            metric = closest_to_horizon["az"]
        else:
            metric = 999.9  # Star did not rise or set (circumpolar scenario)

        dev = abs(metric - criteria["target"])
        return {
            "pass": dev <= criteria["tolerance"],
            "deviation": dev,
            "metric": metric,
        }

    return {"pass": False, "deviation": 999.9, "metric": 0.0}


# ==========================================
# 4. REPORTING AND EXPORT
# ==========================================
def run_full_simulation(start_year, end_year, output_filename):
    print(f"--- Starting simulation: {start_year} to {end_year} ---")

    with open(output_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "Theory", "Status", "Deviation", "Metric_Value"])

        for year in range(start_year, end_year + 1):
            for name in THEORIES:
                res = evaluate_theory(name, year)
                status = "PASS" if res.get("pass") else "FAIL"
                deviation = res.get("deviation", 0.0)
                metric = res.get("metric", 0.0)

                writer.writerow(
                    [year, name, status, f"{deviation:.4f}", f"{metric:.4f}"]
                )

                # Console output for active monitoring
                if year % 100 == 0 or status == "PASS":
                    print(
                        f"[{year}] {name:<12} | {status} | Metric: {metric:.4f}° | Dev: {deviation:.4f}°"
                    )

    print("=================================================")
    print(f"Simulation finished. Full data saved to: {output_filename}")


# --- EXECUTION ---
if __name__ == "__main__":
    run_full_simulation(-13000, 3000, "ZepTepi_-13.000_3000.csv")
