#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Local Star Database - 50,000 stars from GAIA DR3

Generates a CSV file with real GAIA data for instant loading.

© 2025 Carmen Wrede, Lino Casu
"""

import os
import sys

# UTF-8 fix for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from pathlib import Path

print("Creating Star Database...")

# Try to fetch from GAIA
try:
    from astroquery.gaia import Gaia
    
    print("📡 Fetching 50,000 stars from GAIA DR3...")
    
    query = """
    SELECT TOP 50000
        source_id, ra, dec, parallax, 
        pmra, pmdec,
        phot_g_mean_mag, bp_rp,
        radial_velocity
    FROM gaiadr3.gaia_source
    WHERE parallax > 0.1
      AND phot_g_mean_mag < 15
      AND parallax_error/parallax < 0.1
    ORDER BY phot_g_mean_mag ASC
    """
    
    job = Gaia.launch_job_async(query)
    result = job.get_results()
    df = result.to_pandas()
    
    # Calculate distance
    df['distance_pc'] = 1000.0 / df['parallax']
    df['distance_ly'] = df['distance_pc'] * 3.26156
    
    # Add SSZ parameters
    PHI = (1 + np.sqrt(5)) / 2
    
    # Simple mass estimate from magnitude
    # M_V ~ G - 5*log10(dist/10)
    M_V = df['phot_g_mean_mag'] - 5*np.log10(df['distance_pc']/10)
    
    # Mass-Luminosity relation (rough)
    df['mass_msun'] = np.clip(10**((-M_V + 4.83) / 2.5 / 3.5), 0.08, 100)
    
    # Schwarzschild radius
    G = 6.67430e-11
    c = 2.99792458e8
    M_sun = 1.989e30
    
    M_kg = df['mass_msun'] * M_sun
    r_s = 2 * G * M_kg / (c**2)
    
    # Distance in meters
    PC_TO_M = 3.0857e16
    r_m = df['distance_pc'] * PC_TO_M
    
    # SSZ segment density
    df['xi'] = 1 - np.exp(-PHI * r_m / r_s)
    
    # SSZ time dilation
    df['D_ssz'] = 1 / (1 + df['xi'])
    
    print(f"✅ Fetched {len(df)} stars from GAIA!")
    
except Exception as e:
    print(f"⚠️ GAIA fetch failed: {e}")
    print("📊 Creating synthetic database...")
    
    # Fallback: Create synthetic data
    n = 50000
    
    # Galactic distribution
    data = []
    for i in range(n):
        # Disk + bulge
        if np.random.random() < 0.9:
            # Disk
            r = np.random.exponential(3000)
            z = np.random.normal(0, 300)
            theta = np.random.uniform(0, 2*np.pi)
            x = r * np.cos(theta)
            y = r * np.sin(theta)
        else:
            # Bulge
            r = np.random.exponential(1000)
            theta = np.random.uniform(0, 2*np.pi)
            phi = np.random.uniform(0, np.pi)
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)
        
        # Equatorial coords
        ra = np.arctan2(y, x) * 180/np.pi
        if ra < 0:
            ra += 360
        dec = np.arcsin(z / np.sqrt(x**2 + y**2 + z**2)) * 180/np.pi
        
        distance_pc = np.sqrt(x**2 + y**2 + z**2)
        parallax = 1000 / distance_pc if distance_pc > 0 else 0
        
        # Stellar mass (IMF)
        mass_msun = np.random.lognormal(-0.3, 0.6)
        mass_msun = np.clip(mass_msun, 0.08, 100)
        
        # Magnitude
        M_V = 4.83 - 2.5 * np.log10(mass_msun**3.5)
        mag_g = M_V + 5*np.log10(distance_pc/10)
        
        # SSZ physics
        G = 6.67430e-11
        c = 2.99792458e8
        M_sun = 1.989e30
        PHI = (1 + np.sqrt(5)) / 2
        PC_TO_M = 3.0857e16
        
        M_kg = mass_msun * M_sun
        r_s = 2 * G * M_kg / (c**2)
        r_m = distance_pc * PC_TO_M
        
        xi = 1 - np.exp(-PHI * r_m / r_s)
        D_ssz = 1 / (1 + xi)
        
        data.append({
            'source_id': i + 1000000000,
            'ra': ra,
            'dec': dec,
            'parallax': parallax,
            'pmra': np.random.normal(0, 5),
            'pmdec': np.random.normal(0, 5),
            'phot_g_mean_mag': mag_g,
            'bp_rp': np.random.uniform(-0.5, 2.0),
            'radial_velocity': np.random.normal(0, 30),
            'distance_pc': distance_pc,
            'distance_ly': distance_pc * 3.26156,
            'mass_msun': mass_msun,
            'xi': xi,
            'D_ssz': D_ssz
        })
    
    df = pd.DataFrame(data)
    print(f"✅ Generated {len(df)} synthetic stars!")

# Save to CSV
output_file = Path(__file__).parent / 'ssz_data' / 'star_database_50k.csv'
output_file.parent.mkdir(exist_ok=True, parents=True)

df.to_csv(output_file, index=False)

print(f"💾 Saved to: {output_file}")
print(f"📊 Database size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
print(f"⭐ Stars: {len(df):,}")
print(f"🎯 RA range: {df['ra'].min():.1f}° - {df['ra'].max():.1f}°")
print(f"🎯 Dec range: {df['dec'].min():.1f}° - {df['dec'].max():.1f}°")
print(f"📏 Distance range: {df['distance_ly'].min():.1f} - {df['distance_ly'].max():.1f} ly")
print()
print("✅ Database ready! App will load this automatically.")
