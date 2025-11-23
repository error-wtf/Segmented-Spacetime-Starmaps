"""
Convert GAIA radial_velocity to v_los_mps (spectroscopy data)
"""
import pandas as pd
import numpy as np
from pathlib import Path


def convert_radial_velocity_to_spectroscopy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Copy GAIA radial_velocity to v_los_mps as spectroscopy data.
    
    GAIA radial_velocity is measured via Doppler shift - it's real spectroscopy!
    
    Parameters
    ----------
    df : pd.DataFrame
        Star database with 'radial_velocity' column (km/s)
        
    Returns
    -------
    pd.DataFrame
        Database with v_los_mps filled from GAIA data
    """
    print(f"[CONVERT] Converting GAIA radial_velocity to spectroscopy...")
    print(f"  - Total objects: {len(df):,}")
    
    # Ensure columns exist
    if 'v_los_mps' not in df.columns:
        df['v_los_mps'] = np.nan
    if 'spectroscopy_source' not in df.columns:
        df['spectroscopy_source'] = ''
    
    # Count existing
    has_spectroscopy = df['v_los_mps'].notna()
    existing_count = has_spectroscopy.sum()
    print(f"  - Existing spectroscopy: {existing_count:,}")
    
    # Find GAIA radial_velocity data
    has_gaia_rv = df['radial_velocity'].notna() & ~has_spectroscopy
    gaia_count = has_gaia_rv.sum()
    print(f"  - GAIA radial_velocity available: {gaia_count:,}")
    
    if gaia_count == 0:
        print(f"  - No new data to convert!")
        return df
    
    # Convert km/s to m/s
    print(f"  - Converting km/s to m/s...")
    df.loc[has_gaia_rv, 'v_los_mps'] = df.loc[has_gaia_rv, 'radial_velocity'] * 1000.0
    df.loc[has_gaia_rv, 'spectroscopy_source'] = 'GAIA_DR3'
    
    # Final stats
    total_with_spec = df['v_los_mps'].notna().sum()
    print(f"\n[CONVERT] Complete!")
    print(f"  - Existing (ESO/etc):  {existing_count:,}")
    print(f"  - Added (GAIA DR3):    {gaia_count:,}")
    print(f"  - Total spectroscopy:  {total_with_spec:,}")
    print(f"  - Coverage:            {total_with_spec/len(df)*100:.1f}%")
    
    return df


def update_enriched_database():
    """
    Load enriched database, convert GAIA RV to spectroscopy, and save.
    """
    data_path = Path(__file__).parent / "ssz_data"
    enriched_file = data_path / "star_database_enriched.csv"
    
    if not enriched_file.exists():
        print(f"❌ Enriched database not found: {enriched_file}")
        return False
    
    print(f"[LOAD] Loading: {enriched_file}")
    df = pd.read_csv(enriched_file)
    print(f"[LOAD] Loaded {len(df):,} objects")
    
    # Convert GAIA radial_velocity
    df = convert_radial_velocity_to_spectroscopy(df)
    
    # Save updated database
    print(f"\n[SAVE] Saving updated database...")
    df.to_csv(enriched_file, index=False)
    file_size = enriched_file.stat().st_size / 1024 / 1024
    print(f"[SAVE] SAVED: {enriched_file}")
    print(f"[SAVE] Size: {file_size:.2f} MB")
    
    return True


if __name__ == "__main__":
    update_enriched_database()
