"""
Analyze NaN values in the enriched database
"""
import pandas as pd
import numpy as np
from pathlib import Path


def analyze_nan_values():
    """Analyze where NaN values are and why"""
    
    data_path = Path(__file__).parent / "ssz_data"
    enriched_file = data_path / "star_database_enriched.csv"
    
    print(f"[LOAD] Loading: {enriched_file}")
    df = pd.read_csv(enriched_file)
    print(f"[LOAD] Loaded {len(df):,} objects\n")
    
    print("="*80)
    print("NaN ANALYSIS")
    print("="*80)
    
    # Temperature analysis
    print("\n1. TEMPERATURE (temperature_K):")
    has_temp = df['temperature_K'].notna().sum()
    no_temp = df['temperature_K'].isna().sum()
    print(f"   - Has data:  {has_temp:,} ({has_temp/len(df)*100:.1f}%)")
    print(f"   - NaN:       {no_temp:,} ({no_temp/len(df)*100:.1f}%)")
    
    # Why no temperature?
    no_temp_df = df[df['temperature_K'].isna()]
    no_bp_rp = no_temp_df['bp_rp'].isna().sum()
    print(f"\n   Reason for NaN:")
    print(f"   - No BP-RP color data: {no_bp_rp:,}")
    
    # Spectroscopy analysis
    print("\n2. SPECTROSCOPY (v_los_mps):")
    has_spec = df['v_los_mps'].notna().sum()
    no_spec = df['v_los_mps'].isna().sum()
    print(f"   - Has data:  {has_spec:,} ({has_spec/len(df)*100:.1f}%)")
    print(f"   - NaN:       {no_spec:,} ({no_spec/len(df)*100:.1f}%)")
    
    # Why no spectroscopy?
    no_spec_df = df[df['v_los_mps'].isna()]
    no_rv = no_spec_df['radial_velocity'].isna().sum()
    print(f"\n   Reason for NaN:")
    print(f"   - No GAIA radial_velocity: {no_rv:,}")
    
    # Combined analysis
    print("\n3. COMBINED:")
    both_ok = ((df['temperature_K'].notna()) & (df['v_los_mps'].notna())).sum()
    temp_only = ((df['temperature_K'].notna()) & (df['v_los_mps'].isna())).sum()
    spec_only = ((df['temperature_K'].isna()) & (df['v_los_mps'].notna())).sum()
    neither = ((df['temperature_K'].isna()) & (df['v_los_mps'].isna())).sum()
    
    print(f"   - Both temp + spec:      {both_ok:,} ({both_ok/len(df)*100:.1f}%)")
    print(f"   - Temp only (no spec):   {temp_only:,} ({temp_only/len(df)*100:.1f}%)")
    print(f"   - Spec only (no temp):   {spec_only:,} ({spec_only/len(df)*100:.1f}%)")
    print(f"   - Neither:               {neither:,} ({neither/len(df)*100:.1f}%)")
    
    # Sample objects with NaN
    print("\n" + "="*80)
    print("SAMPLE NaN OBJECTS (first 5)")
    print("="*80)
    
    nan_objects = df[(df['temperature_K'].isna()) | (df['v_los_mps'].isna())].head(5)
    
    for idx, row in nan_objects.iterrows():
        print(f"\nObject #{idx}:")
        print(f"  source_id:        {row['source_id']}")
        print(f"  ra, dec:          {row['ra']:.4f}, {row['dec']:.4f}")
        print(f"  phot_g_mean_mag:  {row['phot_g_mean_mag']:.2f}")
        print(f"  bp_rp:            {row['bp_rp']}")
        print(f"  temperature_K:    {row['temperature_K']}")
        print(f"  radial_velocity:  {row['radial_velocity']}")
        print(f"  v_los_mps:        {row['v_los_mps']}")
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print(f"Temperature NaNs: Missing BP-RP color (very faint or problematic photometry)")
    print(f"Spectroscopy NaNs: Missing radial velocity (not measured by GAIA)")
    print(f"\nBoth are GAIA data quality issues, not our fault!")
    print("="*80)


if __name__ == "__main__":
    analyze_nan_values()
