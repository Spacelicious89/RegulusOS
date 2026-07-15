import datetime
import csv
from zoneinfo import ZoneInfo
from skyfield.api import load, Star, wgs84
from tqdm import tqdm
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

print("======================================================")
print("      PILLAR OF LIGHT - 16,000 YEAR EPOCH SCANNER     ")
print("======================================================")
print("Loading DE441 Ephemeris (Epoch -13000 to +3000)...")

ts = load.timescale()
eph = load('de441.bsp')
earth = eph['earth']
giza = earth + wgs84.latlon(29.975234, 31.137772, elevation_m=20.0)


targets = {
    'Pluto': eph['pluto barycenter'],
    'Jupiter': eph['jupiter barycenter'],
    'Mars': eph['mars barycenter'],
    'Venus': eph['venus barycenter'],
    'Moon': eph['moon']
}
regulus = Star(ra_hours=(10, 8, 22.311), dec_degrees=(11, 58, 1.95))

def scan_decade(start_year):
    

    hits = []
    
    for year in range(start_year, start_year + 10):
        t_jan1 = ts.utc(year, 1, 1)
        pluto_astrometric = earth.at(t_jan1).observe(targets['Pluto'])
        ra_pluto, _, _ = pluto_astrometric.radec()
        
        
        is_pluto_aligned = (20.0 < ra_pluto.hours < 24.0) or (8.0 < ra_pluto.hours < 12.0)
        
        if not is_pluto_aligned:
            continue 

        
        t_mid = ts.utc(year, 6, 15)
        jup_astrometric = earth.at(t_mid).observe(targets['Jupiter'])
        ra_jup, _, _ = jup_astrometric.radec()
        
        if not (8.0 < ra_jup.hours < 12.0):
            continue 

        
        t_hours = ts.utc(year, 1, 1, range(0, 365 * 24, 6))
        
        for t in t_hours:
            mars_pos = giza.at(t).observe(targets['Mars']).apparent().altaz()
            reg_pos = giza.at(t).observe(regulus).apparent().altaz()
            
            
            if abs(mars_pos[1].degrees - 90.0) < 5.0 and abs(reg_pos[1].degrees - 90.0) < 5.0:
                
                
                y, m, d, _, _, _ = t.utc
                
                
                hits.append({
                    'Year': year,
                    'Date': f"{int(y)}-{int(m):02d}-{int(d):02d}",
                    'Potential': 'HIGH - Macro Conjunction Detected'
                })
                break 
                
    return hits

if __name__ == "__main__":
    print("Initiating Macro-Sieve from 13,000 BCE to 3000 CE...")
    start_epoch = -13000
    end_epoch = 3000
    decades = list(range(start_epoch, end_epoch, 10))
    
    global_hits = []
    
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(scan_decade, decade): decade for decade in decades}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Scanning Epoches (Decades)"):
            try:
                result = future.result()
                if result:
                    global_hits.extend(result)
            except Exception as e:
                pass
    
    print("======================================================")
    print("Loading DE441 Ephemeris (Epoch -13000 to +3000)...")            
    print("\n======================================================")
    print("                 SCAN COMPLETE")
    print("======================================================")
    print(f"Out of 16,000 years, the Macro-Sieve found {len(global_hits)} rough alignments.")
    
    csv_file = "Epoch_Pillar_Anomalies.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Year', 'Date', 'Potential'])
        writer.writeheader()
        writer.writerows(global_hits)
        
    print(f"Results saved to {csv_file}. These are your 'Golden Tickets' to investigate deeply.")
    
    if len(global_hits) > 0:
        print("Top dates to investigate:")
        for hit in global_hits[:10]:
            print(f" -> {hit['Date']}")