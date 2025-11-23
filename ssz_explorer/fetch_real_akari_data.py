"""
Fetch REAL AKARI data for all objects and update database
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Import fetcher
sys.path.insert(0, str(Path(__file__).parent))
from unified_data_fetcher import fetch_temperature_data, FETCHERS_AVAILABLE

def update_with_real_akari_data():
    """Replace calculated temperatures with real AKARI data where available"""
    
    if not FETCHERS_AVAILABLE:
        print("ERROR: AKARI fetchers not available!")
        return False
    
    data_path = Path(__file__).parent / "ssz_data"
    enriched_file = data_path / "star_database_enriched.csv"
    
    print("="*80)
    print("FETCHING REAL AKARI DATA")
    print("="*80)
    
    print(f"\n[LOAD] Loading: {enriched_file}")
    df = pd.read_csv(enriched_file)
    print(f"[LOAD] Loaded {len(df):,} objects")
    
    # Statistics BEFORE
    calculated_before = (df['temperature_source'] == 'Calculated_BP_RP').sum()
    real_before = (~df['temperature_source'].str.contains('Calculated', na=False)).sum()
    
    print(f"\n[BEFORE]")
    print(f"  - Calculated (BP-RP): {calculated_before:,}")
    print(f"  - Real (fetched):     {real_before:,}")
    
    # Process in batches
    print(f"\n[FETCH] Fetching AKARI data for {len(df):,} objects...")
    print(f"  - This will take ~30-60 minutes")
    print(f"  - Progress updates every 1000 objects")
    
    akari_matches = 0
    errors = 0
    
    for idx in range(len(df)):
        if idx % 1000 == 0:
            print(f"  Progress: {idx:,}/{len(df):,} ({idx/len(df)*100:.1f}%) - AKARI matches: {akari_matches:,}")
        
        try:
            # Create object dict
            obj_dict = {
                'source_id': df.at[idx, 'source_id'],
                'ra': df.at[idx, 'ra'],
                'dec': df.at[idx, 'dec'],
                'designation': f"GAIA_{df.at[idx, 'source_id']}"
            }
            
            # Fetch AKARI data
            enriched = fetch_temperature_data(obj_dict)
            
            # Check if we got REAL data (not calculated)
            if 'temperature_K' in enriched and pd.notna(enriched['temperature_K']):
                if 'temperature_source' in enriched and enriched['temperature_source']:
                    # Check if it's REAL data (AKARI/2MASS)
                    if enriched['temperature_source'] != 'Calculated_BP_RP':
                        # Update database
                        df.at[idx, 'temperature_K'] = enriched['temperature_K']
                        df.at[idx, 'temperature_source'] = enriched['temperature_source']
                        akari_matches += 1
        
        except Exception as e:
            errors += 1
            if errors < 10:  # Show first 10 errors
                print(f"  ! Error at {idx}: {str(e)[:100]}")
    
    # Statistics AFTER
    calculated_after = (df['temperature_source'] == 'Calculated_BP_RP').sum()
    real_after = (~df['temperature_source'].str.contains('Calculated', na=False)).sum()
    
    print(f"\n[AFTER]")
    print(f"  - Calculated (BP-RP): {calculated_after:,}")
    print(f"  - Real (fetched):     {real_after:,}")
    print(f"  - New AKARI matches:  {akari_matches:,}")
    print(f"  - Errors:             {errors:,}")
    
    # Save
    print(f"\n[SAVE] Saving updated database...")
    df.to_csv(enriched_file, index=False)
    file_size = enriched_file.stat().st_size / 1024 / 1024
    print(f"[SAVE] SAVED: {enriched_file}")
    print(f"[SAVE] Size: {file_size:.2f} MB")
    
    print("\n" + "="*80)
    print("COMPLETE!")
    print("="*80)
    
    return True


if __name__ == "__main__":
    update_with_real_akari_data()
