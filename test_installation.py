#!/usr/bin/env python3
"""
Quick installation test for SSZ StarMaps.

Tests all major imports and functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("="*70)
print("SSZ STARMAPS - INSTALLATION TEST")
print("="*70)
print()

# Test 1: Basic imports
print("[1/5] Testing basic imports...")
try:
    from ssz_starmaps.catalogs import CatalogManager, INTERESTING_REGIONS
    from ssz_starmaps.transform import transform_catalog, TransformConfig
    from ssz_starmaps.viz import plot_sky_comparison
    from ssz_starmaps.ssz_metric import Xi, D_SSZ, schwarzschild_radius
    print("  [OK] All imports successful")
except ImportError as e:
    print(f"  [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: Catalog manager
print("\n[2/5] Testing catalog manager...")
try:
    manager = CatalogManager(offline=True)
    stars = manager._get_mock_catalog(10)
    print(f"  [OK] Generated {len(stars)} mock stars")
except Exception as e:
    print(f"  [FAIL] Catalog test failed: {e}")
    sys.exit(1)

# Test 3: Transform
print("\n[3/5] Testing SSZ transformation...")
try:
    stars_ssz = transform_catalog(stars, show_progress=False)
    assert 'distance_ssz_pc' in stars_ssz.columns
    assert 'stretch_factor' in stars_ssz.columns
    mean_stretch = stars_ssz['stretch_factor'].mean()
    print(f"  [OK] Transformed {len(stars_ssz)} stars")
    print(f"    Mean stretch: {mean_stretch:.6f}")
except Exception as e:
    print(f"  [FAIL] Transform failed: {e}")
    sys.exit(1)

# Test 4: Physics validation
print("\n[4/5] Testing SSZ physics...")
try:
    r_s = schwarzschild_radius(1.989e30)
    r = 2.0 * r_s
    xi = Xi(r, r_s)
    D = D_SSZ(r, r_s)
    
    # Validated value from Mass-Projection repo
    assert abs(xi - 0.960682) < 1e-4, f"Xi mismatch: {xi}"
    assert abs(D - 0.510027) < 1e-4, f"D mismatch: {D}"
    
    print(f"  [OK] Xi(2r_s) = {xi:.6f} (expected: 0.960682)")
    print(f"  [OK] D(2r_s) = {D:.6f} (expected: 0.510027)")
except AssertionError as e:
    print(f"  [FAIL] Physics validation failed: {e}")
    sys.exit(1)

# Test 5: Available regions
print("\n[5/5] Testing pre-defined regions...")
try:
    regions = list(INTERESTING_REGIONS.keys())
    print(f"  [OK] {len(regions)} regions available:")
    for region in regions:
        print(f"    - {region}")
except Exception as e:
    print(f"  [FAIL] Regions test failed: {e}")

# Success!
print()
print("="*70)
print("[OK] ALL TESTS PASSED!")
print("="*70)
print()
print("Installation is working correctly!")
print()
print("Next steps:")
print("  1. Run: python demo_quick_start.py")
print("  2. Or: python scripts/batch_process_regions.py")
print("  3. See: QUICK_START.md for more examples")
print()
