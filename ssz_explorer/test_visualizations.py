"""
Test Visualizations - Quick diagnostic
"""
import os
import sys
from pathlib import Path

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("TESTING VISUALIZATIONS")
print("="*80)

# Test 1: Import star_map_generator
print("\n[TEST 1] Importing star_map_generator...")
try:
    from star_map_generator import create_3d_sky_map, create_sky_map
    print("  ✓ Import successful")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Load database
print("\n[TEST 2] Loading database...")
try:
    import pandas as pd
    enriched_file = Path(__file__).parent / "ssz_data" / "star_database_enriched.csv"
    df = pd.read_csv(enriched_file)
    print(f"  ✓ Loaded {len(df):,} objects")
    print(f"  Columns: {list(df.columns[:10])}")
except Exception as e:
    print(f"  ✗ Load failed: {e}")

# Test 3: Create 3D Sky Map
print("\n[TEST 3] Creating 3D Sky Map...")
try:
    # Use small sample
    sample = df.sample(100) if len(df) > 100 else df
    fig = create_3d_sky_map(sample, "Test 3D Map")
    print(f"  ✓ 3D Map created")
    print(f"  Figure type: {type(fig)}")
    print(f"  Has data: {len(fig.data) if hasattr(fig, 'data') else 'N/A'}")
except Exception as e:
    print(f"  ✗ 3D Map failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test generate_constellation_map
print("\n[TEST 4] Testing generate_constellation_map...")
try:
    from gradio_app_complete import generate_constellation_map
    fig = generate_constellation_map(266.4, -29.0, 30)
    print(f"  ✓ Constellation map created")
    print(f"  Figure type: {type(fig)}")
except Exception as e:
    print(f"  ✗ Constellation map failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test generate_3d_sky_map (from gradio_app)
print("\n[TEST 5] Testing generate_3d_sky_map (gradio)...")
try:
    from gradio_app_complete import generate_3d_sky_map as gen_3d
    fig = gen_3d()
    print(f"  ✓ 3D sky map created")
    print(f"  Figure type: {type(fig)}")
except Exception as e:
    print(f"  ✗ 3D sky map failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
