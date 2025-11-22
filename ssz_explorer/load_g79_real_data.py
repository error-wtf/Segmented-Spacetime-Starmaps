"""
Load REAL G79 Telescope Data for SSZ Physics
============================================

G79 data format (ECHTE Teleskop-Beobachtungen):
- AKARI FIS: Infrarot-Ringe (65-160 μm)
- Rizzo 2014: NH3 Geschwindigkeitskomponenten  
- Di Francesco 2010: Temperaturprofil
- Radial rings format: radius_pc, flux/temperature

NICHT wie GAIA! Stattdessen: Radiale Profile für SSZ γ_seg(r) fits!

© 2025 Carmen Wrede, Lino Casu, Bingsi
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import io

# UTF-8 für Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Path to g79-cygnus-test repository
G79_REPO = Path(r"E:\clone\g79-cygnus-test")

# ============================================================================
# LOAD REAL TELESCOPE DATA
# ============================================================================

def load_g79_temperature_profile():
    """
    Load G79 temperature profile (Di Francesco+ 2010)
    
    Returns:
        DataFrame with columns: radius_pc, temperature_K
        
    This is REAL telescope data - NOT synthetic!
    """
    csv_path = G79_REPO / "data" / "G79_temperatures.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Temperature data not found: {csv_path}\nEnsure g79-cygnus-test repo is cloned!")
    
    df = pd.read_csv(csv_path, names=['radius_pc', 'temperature_K'], skiprows=1)
    
    print(f"✓ Loaded REAL temperature profile: {len(df)} radial points")
    print(f"  Radial range: {df['radius_pc'].min():.2f} - {df['radius_pc'].max():.2f} pc")
    print(f"  Temperature:  {df['temperature_K'].min():.0f} - {df['temperature_K'].max():.0f} K")
    print(f"  Source: Di Francesco+ 2010 (Submm Array)")
    
    return df


def load_g79_nh3_velocities():
    """
    Load G79 NH3 velocity components (Rizzo+ 2014)
    
    Returns:
        DataFrame with velocity components
        
    This is PEER-REVIEWED spectroscopy from Effelsberg 100m!
    """
    csv_path = G79_REPO / "G79_Rizzo2014_NH3_Table1.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"NH3 data not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    print(f"\n✓ Loaded REAL NH3 velocity components: {len(df)} components")
    print(f"  Total Δv = {df['v_max_kms'].max() - df['v_min_kms'].min():.1f} km/s")
    print(f"  Source: Rizzo+ 2014 (A&A) - Effelsberg 100m")
    
    for _, row in df.iterrows():
        v_range = row['v_max_kms'] - row['v_min_kms']
        print(f"    {row['component']:8s}: Δv = {v_range:4.1f} km/s, T_rot = {row['Trot_K']:5.0f} K")
    
    return df


def load_g79_akari_rings():
    """
    Load G79 AKARI infrared rings
    
    Returns:
        DataFrame with AKARI FIS bands
        
    This is REAL infrared photometry from AKARI satellite!
    """
    csv_path = G79_REPO / "data" / "G79_AKARI_RINGS.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"AKARI rings not found: {csv_path}")
    
    # Skip header lines (start with #)
    df = pd.read_csv(csv_path, comment='#')
    
    print(f"\n✓ Loaded REAL AKARI infrared rings: {len(df)} rings")
    print(f"  Radial range: {df['radius_pc'].min():.2f} - {df['radius_pc'].max():.2f} pc")
    print(f"  Bands: 65, 90, 140, 160 μm")
    print(f"  Source: AKARI FIS All-Sky Survey")
    
    return df


def calculate_ssz_parameters_from_temperature(temp_df):
    """
    Calculate SSZ parameters from REAL temperature profile
    
    Args:
        temp_df: DataFrame with radius_pc, temperature_K
        
    Returns:
        DataFrame with SSZ physics parameters
    """
    # Physical constants
    G = 6.67430e-11
    C = 2.99792458e8
    M_SUN = 1.98847e30
    PC_TO_M = 3.0857e16
    
    # G79 parameters
    M_CORE = 8.7 * M_SUN  # Core mass from literature
    D_KPC = 1.7  # Distance
    
    # Calculate Schwarzschild radius
    r_s = 2 * G * M_CORE / (C**2)
    r_s_pc = r_s / PC_TO_M
    
    print(f"\n📊 SSZ Physics Calculation:")
    print(f"  Core mass: {M_CORE/M_SUN:.1f} M☉")
    print(f"  r_s = {r_s:.3e} m = {r_s_pc:.3e} pc")
    
    # Calculate gamma_seg from temperature
    # γ_seg(r) ≈ T₀ / T(r) (approximation)
    T_0 = temp_df['temperature_K'].max()
    
    ssz_df = temp_df.copy()
    ssz_df['gamma_seg'] = T_0 / ssz_df['temperature_K']
    ssz_df['xi_seg'] = 1 - ssz_df['gamma_seg']
    ssz_df['D_ssz'] = 1 / (1 + ssz_df['xi_seg'])
    ssz_df['r_over_rs'] = ssz_df['radius_pc'] / r_s_pc
    
    print(f"\n  γ_seg range: {ssz_df['gamma_seg'].min():.4f} - {ssz_df['gamma_seg'].max():.4f}")
    print(f"  Ξ range:     {ssz_df['xi_seg'].min():.6f} - {ssz_df['xi_seg'].max():.6f}")
    print(f"  D_ssz range: {ssz_df['D_ssz'].min():.6f} - {ssz_df['D_ssz'].max():.6f}")
    
    return ssz_df


# ============================================================================
# MAIN DATA LOADER
# ============================================================================

def load_all_g79_real_data():
    """
    Load ALL real G79 telescope data
    
    Returns:
        dict with all datasets
    """
    print("="*80)
    print("LOADING REAL G79.29+0.46 TELESCOPE DATA")
    print("="*80)
    print()
    
    data = {}
    
    try:
        # Temperature profile (REAL!)
        data['temperature'] = load_g79_temperature_profile()
        
        # NH3 velocities (REAL!)
        data['nh3_velocities'] = load_g79_nh3_velocities()
        
        # AKARI infrared (REAL!)
        data['akari_rings'] = load_g79_akari_rings()
        
        # Calculate SSZ parameters from REAL data
        data['ssz_parameters'] = calculate_ssz_parameters_from_temperature(data['temperature'])
        
        print("\n" + "="*80)
        print("✅ ALL REAL DATA LOADED SUCCESSFULLY!")
        print("="*80)
        print(f"\n📊 Data Summary:")
        print(f"  Temperature points: {len(data['temperature'])}")
        print(f"  NH3 components:     {len(data['nh3_velocities'])}")
        print(f"  AKARI rings:        {len(data['akari_rings'])}")
        print(f"  SSZ parameters:     {len(data['ssz_parameters'])}")
        
        print(f"\n🔬 Data Quality: PEER-REVIEWED")
        print(f"  ✓ Di Francesco+ 2010 (ApJ)")
        print(f"  ✓ Rizzo+ 2014 (A&A)")
        print(f"  ✓ AKARI FIS All-Sky Survey")
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\nMake sure g79-cygnus-test repo is cloned:")
        print(f"  git clone https://github.com/error-wtf/g79-cygnus-tests E:\\clone\\g79-cygnus-test")
        return None
    
    return data


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\nTesting REAL G79 data loader...")
    print()
    
    data = load_all_g79_real_data()
    
    if data:
        print("\n" + "="*80)
        print("SAMPLE DATA:")
        print("="*80)
        
        print("\n📍 Temperature Profile (first 5 points):")
        print(data['temperature'].head())
        
        print("\n🌊 NH3 Velocities:")
        print(data['nh3_velocities'])
        
        print("\n🔬 SSZ Parameters (first 5 points):")
        print(data['ssz_parameters'][['radius_pc', 'temperature_K', 'gamma_seg', 'xi_seg', 'D_ssz']].head())
        
        print("\n✅ READY TO USE FOR SSZ PHYSICS PLOTS!")
        print("\nNext steps:")
        print("  1. Use data['ssz_parameters'] for physics plots")
        print("  2. Plot gamma_seg vs radius_pc")
        print("  3. Compare with theoretical SSZ predictions")
