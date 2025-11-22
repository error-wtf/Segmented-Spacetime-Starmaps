#!/usr/bin/env python3
"""Direct test of sky map generation"""

import sys
sys.path.insert(0, '.')

from star_map_generator import create_default_universe, create_sky_map

print("Testing default universe...")
universe = create_default_universe()
print(f"[OK] Created universe with {len(universe)} objects")
print(f"Columns: {list(universe.columns)}")
print(f"\nFirst object:")
print(universe.iloc[0])

print("\n" + "="*80)
print("Creating sky map...")
try:
    fig = create_sky_map(universe, "Test Sky Map")
    print("[OK] Sky map created successfully!")
    print(f"Figure type: {type(fig)}")
    print(f"Has data: {len(fig.data) > 0}")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
