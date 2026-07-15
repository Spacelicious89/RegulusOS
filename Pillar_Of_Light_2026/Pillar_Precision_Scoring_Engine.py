import pandas as pd
import numpy as np
import datetime
from skyfield.api import load, Star, wgs84
from tqdm import tqdm
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

print("======================================================")
print("     ULTIMATE PILLAR OF LIGHT: DEEP PRECISION SCAN    ")
print("               (ACADEMIC MINUTE-RESOLUTION)           ")
print("======================================================")

ts = load.timescale()
eph = load('de441.bsp')
earth = eph['earth']
giza = earth + wgs84.latlon(29.975234, 31.137772, elevation_m=20.0)

targets = {
    'Mars': eph['mars barycenter'],
    'Venus': eph['venus barycenter'],
    'Jupiter': eph['jupiter barycenter'],
    'Moon': eph['moon'],
    'Pluto': eph['pluto barycenter']
}
regulus = Star(ra_hours=(10, 8, 22.311), dec_degrees=(11, 58, 1.95))

def deep_scan_year(year):
 
    best_score = 999999.0
    best_record = None
    
  
    t_hours = ts.utc(year, 1, 1, range(0, 366 * 24))
    
    _, reg_az, _ = giza.at(t_hours).observe(regulus).apparent().altaz()
    
    
    az_diff = np.abs(reg_az.degrees - 90.0)
    potential_hour_indices = np.where(az_diff < 2.0)[0]
    
    if len(potential_hour_indices) == 0:
        return None 
        
    for idx in potential_hour_indices:
     
        t_mins = ts.utc(year, 1, 1, int(idx), range(-60, 60))
        
        _, r_az_m, _ = giza.at(t_mins).observe(regulus).apparent().altaz()
        
        
        best_min_idx = np.argmin(np.abs(r_az_m.degrees - 90.0))
        t_moment = t_mins[best_min_idx]
        r_az_val = r_az_m.degrees[best_min_idx]
        
       
        m_az = giza.at(t_moment).observe(targets['Mars']).apparent().altaz()[1].degrees
        v_az = giza.at(t_moment).observe(targets['Venus']).apparent().altaz()[1].degrees
        j_az = giza.at(t_moment).observe(targets['Jupiter']).apparent().altaz()[1].degrees
        moon_az = giza.at(t_moment).observe(targets['Moon']).apparent().altaz()[1].degrees
        p_az = giza.at(t_moment).observe(targets['Pluto']).apparent().altaz()[1].degrees
        
        
        score = (
            abs(m_az - 90.0) +
            abs(v_az - 90.0) +
            abs(j_az - 90.0) +
            abs(moon_az - 90.0) +
            abs(p_az - 270.0)
        )
        
        if score < best_score:
            best_score = score
            y, mo, d, h, mn, s = t_moment.utc
            formatted_time = f"{int(y)}-{int(mo):02d}-{int(d):02d} {int(h):02d}:{int(mn):02d}:{int(s):02d}"
            
            best_record = {
                'Year': year,
                'UTC_Time': formatted_time,
                'Regulus_Az': round(r_az_val, 2),
                'Mars_Az': round(m_az, 2),
                'Venus_Az': round(v_az, 2),
                'Jupiter_Az': round(j_az, 2),
                'Moon_Az': round(moon_az, 2),
                'Pluto_Az': round(p_az, 2),
                'Total_Deviation_Score': round(score, 2)
            }
            
    return best_record

if __name__ == "__main__":
    try:
        df = pd.read_csv('Epoch_Pillar_Anomalies.csv')
        years_to_scan = df['Year'].unique().tolist()
        print(f"Loaded {len(years_to_scan)} anomaly years from Macro-Sieve.")
    except Exception as e:
        print("Brak pliku Epoch_Pillar_Anomalies.csv!")
        years_to_scan = []
        
   
    if 2026 not in years_to_scan:
        years_to_scan.append(2026)
        
    print(f"Total years targeted for Deep Sniper Scan: {len(years_to_scan)}")
    print("Initiating multi-core precision tracking (Minute Resolution)...\n")
    
    final_results = []
    
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(deep_scan_year, y): y for y in years_to_scan}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Sniper Scanning"):
            try:
                res = future.result()
                if res is not None:
                    final_results.append(res)
            except Exception as e:
                pass
                
    if final_results:
        results_df = pd.DataFrame(final_results)
        results_df = results_df.sort_values(by='Total_Deviation_Score', ascending=True)
        
        csv_out = 'Ultimate_Pillar_Ranking_Precision.csv'
        results_df.to_csv(csv_out, index=False)
        
        print("\n======================================================")
        print("                 DEEP SCAN COMPLETE")
        print("======================================================")
        print(f"Precision data saved to {csv_out}.")
        
        print("\n🏆 TOP 5 PILLARS OF LIGHT IN 16,000 YEARS 🏆")
        top_5 = results_df.head(5)
        for rank, (_, row) in enumerate(top_5.iterrows(), 1):
            print(f"#{rank} | Year {row['Year']} | Date: {row['UTC_Time']} | Total Dev: {row['Total_Deviation_Score']}°")
            
        rank_2026 = results_df[results_df['Year'] == 2026].index
        if not rank_2026.empty:
            actual_rank = results_df.index.get_loc(rank_2026[0]) + 1
            print(f"\n=> The 2026 Alignment ranked #{actual_rank} out of {len(results_df)} anomaly years!")
    else:
        print("Brak wyników. Skrypt nic nie znalazł.")