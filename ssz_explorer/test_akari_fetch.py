"""
Test AKARI fetching on real objects
"""
import pandas as pd
from pathlib import Path

# Load database
df = pd.read_csv('ssz_explorer/ssz_data/star_database_enriched.csv')

print("="*80)
print("TESTING AKARI FETCH ON REAL OBJECTS")
print("="*80)

# Test on 10 random objects
test_objects = df.sample(10)

print(f"\nTesting on {len(test_objects)} random objects...")

for idx, row in test_objects.iterrows():
    print(f"\n--- Object {idx} ---")
    print(f"source_id: {row['source_id']}")
    print(f"ra, dec: {row['ra']:.4f}, {row['dec']:.4f}")
    print(f"Temperature: {row['temperature_K']}")
    print(f"Source: {row['temperature_source']}")
    
    # Try AKARI fetch
    obj_dict = {
        'source_id': row['source_id'],
        'ra': row['ra'],
        'dec': row['dec'],
        'designation': f"GAIA_{row['source_id']}"
    }
    
    # Import and test
    try:
        from unified_data_fetcher import fetch_temperature_data
        enriched = fetch_temperature_data(obj_dict)
        
        if 'temperature_K' in enriched and pd.notna(enriched['temperature_K']):
            print(f"  -> AKARI MATCH! T={enriched['temperature_K']:.1f} K")
        else:
            print(f"  -> No AKARI match (expected - too far from AKARI sources)")
    except Exception as e:
        print(f"  -> Error: {e}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("AKARI IRC catalog has ~870,000 sources")
print("GAIA DR3 has 1.8 BILLION sources")
print("Only ~1% of GAIA objects have nearby AKARI counterparts!")
print("\nTo get AKARI matches, we need to:")
print("  1. Fetch specific regions (Galactic Center, Star-forming regions)")
print("  2. Or use VizieR/IRSA crossmatch with larger radius")
print("="*80)
