"""
Quick AKARI test - Fetch 5000 objects with logging
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Import fetcher
sys.path.insert(0, str(Path(__file__).parent))
from unified_data_fetcher import fetch_temperature_data, FETCHERS_AVAILABLE

def quick_akari_test():
    """Test AKARI fetch on 5000 objects with full logging"""
    
    if not FETCHERS_AVAILABLE:
        print("ERROR: AKARI fetchers not available!")
        return False
    
    data_path = Path(__file__).parent / "ssz_data"
    enriched_file = data_path / "star_database_enriched.csv"
    
    print("="*80)
    print("QUICK AKARI TEST - 5000 OBJECTS")
    print("="*80)
    
    print(f"\n[LOAD] Loading: {enriched_file}")
    df = pd.read_csv(enriched_file)
    print(f"[LOAD] Loaded {len(df):,} objects")
    
    # Test on first 5000 objects
    test_count = 5000
    print(f"\n[TEST] Testing AKARI fetch on first {test_count:,} objects...")
    
    akari_matches = 0
    errors_logged = []
    
    for idx in range(test_count):
        if idx % 500 == 0:
            print(f"  Progress: {idx:,}/{test_count:,} ({idx/test_count*100:.1f}%) - AKARI: {akari_matches:,}")
        
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
            
            # Check if we got REAL data
            if 'temperature_K' in enriched and pd.notna(enriched['temperature_K']):
                if 'temperature_source' in enriched and enriched['temperature_source']:
                    # Check if it's REAL data (AKARI/2MASS)
                    source = enriched['temperature_source']
                    if source and source != 'Calculated_BP_RP':
                        # Update database
                        old_temp = df.at[idx, 'temperature_K']
                        df.at[idx, 'temperature_K'] = enriched['temperature_K']
                        df.at[idx, 'temperature_source'] = source
                        akari_matches += 1
                        
                        print(f"    ✓ Match #{akari_matches}: idx={idx}, T={enriched['temperature_K']:.1f}K ({source})")
        
        except Exception as e:
            if len(errors_logged) < 5:
                error_msg = str(e)[:100]
                errors_logged.append(f"idx={idx}: {error_msg}")
                print(f"    ! Error at {idx}: {error_msg}")
    
    print(f"\n[RESULTS]")
    print(f"  - Objects tested:     {test_count:,}")
    print(f"  - AKARI matches:      {akari_matches:,} ({akari_matches/test_count*100:.2f}%)")
    print(f"  - Errors encountered: {len(errors_logged)}")
    
    if akari_matches > 0:
        print(f"\n[SUCCESS] AKARI fetch is WORKING!")
        print(f"  Found {akari_matches:,} real temperature measurements!")
        
        # Save updated database
        print(f"\n[SAVE] Saving updated database...")
        df.to_csv(enriched_file, index=False)
        file_size = enriched_file.stat().st_size / 1024 / 1024
        print(f"[SAVE] SAVED: {enriched_file}")
        print(f"[SAVE] Size: {file_size:.2f} MB")
        
        # Show sample
        real_data = df[~df['temperature_source'].str.contains('Calculated', na=False)].head(5)
        print(f"\n[SAMPLE] First 5 REAL measurements:")
        for idx, row in real_data.iterrows():
            print(f"  - idx={idx}: T={row['temperature_K']:.1f}K ({row['temperature_source']})")
    else:
        print(f"\n[NOTICE] No AKARI matches in first {test_count:,} objects")
        print(f"  This is normal - AKARI coverage is ~1% for random objects")
        print(f"  Try specific regions (Galactic Center, Cygnus X) for better matches!")
    
    print("\n" + "="*80)
    
    return akari_matches > 0


if __name__ == "__main__":
    quick_akari_test()
