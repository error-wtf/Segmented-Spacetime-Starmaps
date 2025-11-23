"""
Calculate theoretical temperatures from GAIA photometry
"""
import pandas as pd
import numpy as np
from pathlib import Path


def calculate_temperature_from_color(bp_rp):
    """
    Calculate effective temperature from GAIA BP-RP color.
    Based on Casagrande et al. 2021 calibration.
    
    Parameters
    ----------
    bp_rp : float
        BP-RP color index from GAIA
        
    Returns
    -------
    float
        Effective temperature in Kelvin
    """
    if pd.isna(bp_rp):
        return np.nan
    
    # Clamp to valid range
    bp_rp = np.clip(bp_rp, -0.5, 4.0)
    
    # Polynomial fit (Casagrande et al. 2021)
    # T_eff = a + b*x + c*x^2 + d*x^3
    # where x = BP-RP
    a = 8540.0
    b = -3150.0
    c = 520.0
    d = -35.0
    
    T_eff = a + b*bp_rp + c*bp_rp**2 + d*bp_rp**3
    
    # Reasonable limits for main sequence stars
    T_eff = np.clip(T_eff, 2500, 50000)
    
    return T_eff


def add_calculated_temperatures(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add calculated temperatures to database where real data is missing.
    
    Parameters
    ----------
    df : pd.DataFrame
        Star database with 'bp_rp' column
        
    Returns
    -------
    pd.DataFrame
        Database with calculated temperatures added
    """
    print(f"[CALCULATE] Starting temperature calculation...")
    print(f"  - Total objects: {len(df):,}")
    
    # Ensure columns exist
    if 'temperature_K' not in df.columns:
        df['temperature_K'] = np.nan
    if 'temperature_source' not in df.columns:
        df['temperature_source'] = ''
    
    # Count existing real data
    has_real_temp = df['temperature_K'].notna()
    real_count = has_real_temp.sum()
    print(f"  - Objects with REAL temperature: {real_count:,}")
    
    # Find objects that need calculation
    needs_calc = ~has_real_temp & df['bp_rp'].notna()
    calc_count = needs_calc.sum()
    print(f"  - Objects that CAN be calculated: {calc_count:,}")
    
    if calc_count == 0:
        print(f"  - No objects to calculate!")
        return df
    
    # Calculate temperatures
    print(f"  - Calculating temperatures from BP-RP color...")
    calculated_temps = df.loc[needs_calc, 'bp_rp'].apply(calculate_temperature_from_color)
    
    # Add to dataframe
    df.loc[needs_calc, 'temperature_K'] = calculated_temps
    df.loc[needs_calc, 'temperature_source'] = 'Calculated_BP_RP'
    
    # Final stats
    total_with_temp = df['temperature_K'].notna().sum()
    print(f"\n[CALCULATE] Complete!")
    print(f"  - Real (fetched):      {real_count:,}")
    print(f"  - Calculated (BP-RP):  {calc_count:,}")
    print(f"  - Total with temp:     {total_with_temp:,}")
    print(f"  - Missing:             {len(df) - total_with_temp:,}")
    
    return df


def update_enriched_database():
    """
    Load enriched database, add calculated temperatures, and save.
    """
    data_path = Path(__file__).parent / "ssz_data"
    enriched_file = data_path / "star_database_enriched.csv"
    
    if not enriched_file.exists():
        print(f"❌ Enriched database not found: {enriched_file}")
        return False
    
    print(f"[LOAD] Loading: {enriched_file}")
    df = pd.read_csv(enriched_file)
    print(f"[LOAD] Loaded {len(df):,} objects")
    
    # Add calculated temperatures
    df = add_calculated_temperatures(df)
    
    # Save updated database
    print(f"\n[SAVE] Saving updated database...")
    df.to_csv(enriched_file, index=False)
    file_size = enriched_file.stat().st_size / 1024 / 1024
    print(f"[SAVE] SAVED: {enriched_file}")
    print(f"[SAVE] Size: {file_size:.2f} MB")
    
    return True


if __name__ == "__main__":
    update_enriched_database()
