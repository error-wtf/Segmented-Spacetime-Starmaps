import pandas as pd
import numpy as np

df = pd.read_csv('ssz_explorer/ssz_data/star_database_enriched.csv', nrows=1000)

G = 6.67430e-11
C = 2.99792458e8
M_SUN = 1.98847e30
PC_TO_M = 3.0857e16

valid = 0
total = 0
r_ratios = []

for idx, obj in df.iterrows():
    total += 1
    m = obj.get('mass_msun', 1.0)
    d_pc = obj.get('distance_pc', None)
    
    if m > 0 and not np.isnan(m) and d_pc and not np.isnan(d_pc):
        r_s = 2 * G * (m * M_SUN) / C**2
        r = d_pc * PC_TO_M
        r_ratio = r / r_s
        r_ratios.append(r_ratio)
        
        if r_ratio >= 0.5 and r_ratio <= 20:
            valid += 1

print(f'Valid objects: {valid} / {total}')
if r_ratios:
    print(f'r_ratio range: {min(r_ratios):.2e} - {max(r_ratios):.2e}')
    print(f'r_ratio median: {np.median(r_ratios):.2e}')
