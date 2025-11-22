#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Using PRIMARY Data (ESO) for SSZ Validation

This example demonstrates how to use fetch_primary() to access
the GOLD STANDARD ESO spectroscopy data (97.9% validation rate).

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog
import pandas as pd


def main():
    """Demonstrate PRIMARY data usage."""
    
    print("="*70)
    print("EXAMPLE: PRIMARY DATA (ESO) FOR SSZ VALIDATION")
    print("="*70)
    print()
    
    # Initialize manager
    manager = CatalogManager()
    
    # Show data hierarchy
    print("Step 1: Understanding the Data Hierarchy")
    print("-"*70)
    manager.print_data_guide()
    
    # Fetch PRIMARY data
    print("\nStep 2: Fetching PRIMARY Data (ESO)")
    print("-"*70)
    eso_data = manager.fetch_primary('sgr_a_stars', use_included=True)
    print(f"Loaded {len(eso_data)} ESO observations")
    print()
    
    # Show data structure
    print("Step 3: Data Structure")
    print("-"*70)
    print("Columns available:")
    for i, col in enumerate(eso_data.columns, 1):
        print(f"  {i:2d}. {col}")
    print()
    
    # Show first few observations
    print("Step 4: Sample Observations")
    print("-"*70)
    sample_cols = ['case', 'category', 'M_solar', 'r_emit_m', 'v_tot_mps']
    print(eso_data[sample_cols].head(5).to_string(index=False))
    print()
    
    # Category breakdown
    print("Step 5: Category Breakdown")
    print("-"*70)
    print(eso_data['category'].value_counts())
    print()
    
    # Statistics
    print("Step 6: Data Statistics")
    print("-"*70)
    print(f"Mass range:     {eso_data['M_solar'].min():.2e} - {eso_data['M_solar'].max():.2e} M_sun")
    print(f"Velocity range: {eso_data['v_tot_mps'].min():.2e} - {eso_data['v_tot_mps'].max():.2e} m/s")
    print(f"Eccentricity:   {eso_data['e'].min():.3f} - {eso_data['e'].max():.3f}")
    print()
    
    # Filter specific categories
    print("Step 7: Filtering by Category")
    print("-"*70)
    s_stars = eso_data[eso_data['category'] == 'S-stars']
    print(f"S-stars only: {len(s_stars)} observations")
    print(s_stars[['case', 'M_solar', 'v_tot_mps']].to_string(index=False))
    print()
    
    # Usage for SSZ validation
    print("Step 8: Usage for SSZ Validation")
    print("-"*70)
    print("This data is GOLD STANDARD for SSZ validation!")
    print(f"  - Observations: {len(eso_data)}")
    print(f"  - Success rate: 97.9% (46/47)")
    print(f"  - Data source: ESO GRAVITY spectroscopy")
    print()
    print("For full SSZ validation, see:")
    print("  Mass-Projection/perfect_paired_test.py")
    print()
    
    # Comparison with GAIA
    print("Step 9: Why Not GAIA?")
    print("-"*70)
    print("[!] IMPORTANT: Do NOT use GAIA for SSZ validation!")
    print()
    print("PRIMARY (ESO):")
    print("  Success rate: 97.9%")
    print("  Use for: SSZ physics validation")
    print()
    print("AUXILIARY (GAIA):")
    print("  Success rate: ~51% (for SSZ)")
    print("  Use for: Positions, astrometry only")
    print()
    
    print("="*70)
    print("Example complete!")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
