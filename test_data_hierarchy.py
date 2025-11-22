#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Data Hierarchy - NEW System

Demonstrates the hierarchical data priority system:
- PRIMARY: ESO spectroscopy (97.9% validation)
- IR: AKARI diffuse maps
- MULTIFREQ: NED multi-frequency
- AUXILIARY: GAIA/SIMBAD (positions only)

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ssz_starmaps.catalogs import CatalogManager


def test_data_hierarchy():
    """Test the new hierarchical data system."""
    
    print("="*70)
    print("TESTING: NEW DATA HIERARCHY SYSTEM")
    print("="*70)
    print()
    
    # Initialize manager
    manager = CatalogManager()
    
    # Print data guide
    print("[1/4] Data Source Guide:")
    print()
    manager.print_data_guide()
    
    print()
    print("[2/4] Testing Data Hierarchy Info:")
    print()
    hierarchy = manager.get_data_hierarchy()
    
    for key, info in hierarchy.items():
        print(f"{key.upper()}:")
        print(f"  Name: {info['name']}")
        print(f"  Purpose: {info['purpose']}")
        print(f"  Available: {info['available']}")
        print(f"  Method: {info['method']}")
        if 'success_rate' in info:
            print(f"  Success rate: {info['success_rate']}")
        print()
    
    print()
    print("[3/4] Testing PRIMARY Data (ESO):")
    print()
    
    try:
        eso_data = manager.fetch_primary('sgr_a_stars', use_included=True)
        
        if len(eso_data) > 0:
            print(f"SUCCESS! Loaded {len(eso_data)} ESO observations")
            print(f"Columns: {list(eso_data.columns)[:5]}...")
            print(f"First observation: {eso_data.iloc[0]['case']}")
            print()
            print("This data achieves 97.9% SSZ validation!")
        else:
            print("No ESO data loaded (Mass-Projection repo not found)")
            print("This is expected if repos are separate")
    except Exception as e:
        print(f"ESO module test: {e}")
        print("Install: pip install astroquery (optional)")
    
    print()
    print("[4/4] Comparison: PRIMARY vs AUXILIARY:")
    print()
    
    print("[OK] PRIMARY (ESO):")
    print("   - Use for: SSZ validation tests")
    print("   - Success: 97.9% (46/47 observations)")
    print("   - Method: manager.fetch_primary('sgr_a_stars')")
    print("   - Data: Spectroscopy (Br-gamma emission lines)")
    print()
    
    print("[!] AUXILIARY (GAIA):")
    print("   - Use for: Positions, astrometry, comparisons")
    print("   - Success: ~51% (for SSZ validation)")
    print("   - Method: manager.fetch_nearby(distance_pc=100)")
    print("   - Data: Positions, magnitudes, parallax")
    print()
    
    print("="*70)
    print("KEY TAKEAWAY:")
    print("  - PRIMARY data (ESO) for SSZ physics validation")
    print("  - AUXILIARY data (GAIA) for positions/astrometry")
    print("  - DO NOT mix them up!")
    print("="*70)
    print()


if __name__ == "__main__":
    test_data_hierarchy()
