#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: G79 Region - Multi-Source Workflow

Demonstrates how to combine multiple data sources:
- AKARI infrared data for temperature mapping
- ESO spectroscopy for validation
- GAIA positions for context

Region: G79.29+0.46 (CygnusX Diamond Ring)

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ssz_starmaps.catalogs import CatalogManager
import numpy as np


def main():
    """G79 region multi-source analysis."""
    
    print("="*70)
    print("EXAMPLE: G79 REGION - MULTI-SOURCE WORKFLOW")
    print("="*70)
    print()
    
    # Initialize manager
    manager = CatalogManager()
    
    # Step 1: AKARI infrared data
    print("Step 1: AKARI Infrared Data (Temperature Mapping)")
    print("-"*70)
    print("Region: G79.29+0.46 (CygnusX Diamond Ring)")
    print("Purpose: Nebula temperature/density mapping")
    print()
    
    try:
        # Fetch AKARI diffuse emission map
        akari_data, wcs = manager.fetch_ir_map('G79.29+0.46', 'N60')
        
        if akari_data is not None:
            print(f"[OK] AKARI data loaded")
            print(f"  Shape: {akari_data.shape}")
            print(f"  WCS: {wcs is not None}")
            print()
            
            # Basic statistics
            print("Infrared intensity statistics:")
            print(f"  Min: {np.nanmin(akari_data):.2e}")
            print(f"  Max: {np.nanmax(akari_data):.2e}")
            print(f"  Mean: {np.nanmean(akari_data):.2e}")
            print()
        else:
            print("[INFO] AKARI data not available (requires local files)")
            print("See: akari_fetch.py for data acquisition")
            print()
    except Exception as e:
        print(f"[INFO] AKARI data: {e}")
        print()
    
    # Step 2: GAIA positions (for context)
    print("Step 2: GAIA Positions (Auxiliary Context)")
    print("-"*70)
    print("Purpose: Get nearby stars for spatial context")
    print()
    
    try:
        # Fetch nearby stars (for positions only!)
        gaia_stars = manager.fetch_nearby(distance_pc=500, max_stars=50, offline=True)
        
        if len(gaia_stars) > 0:
            print(f"[OK] Found {len(gaia_stars)} nearby stars")
            print(f"  Use: Spatial context, positions")
            print(f"  [!] NOT for SSZ validation (only 51% success)")
            print()
            
            # Show sample
            print("Sample (first 3):")
            cols = ['name', 'ra', 'dec', 'distance']
            if all(c in gaia_stars.columns for c in cols):
                print(gaia_stars[cols].head(3).to_string(index=False))
            print()
        else:
            print("[INFO] Using mock data (offline mode)")
            print()
    except Exception as e:
        print(f"[INFO] GAIA data: {e}")
        print()
    
    # Step 3: ESO data (if available)
    print("Step 3: ESO Spectroscopy (Gold Standard)")
    print("-"*70)
    print("Purpose: SSZ validation (97.9% success)")
    print()
    
    try:
        # Check if we have ESO observations for this region
        eso_data = manager.fetch_primary('sgr_a_stars', use_included=True)
        
        # Filter for relevant observations
        # (In real workflow, you'd filter by coordinates)
        print(f"[OK] ESO data available: {len(eso_data)} observations")
        print(f"  Use: SSZ physics validation")
        print(f"  Success rate: 97.9%")
        print()
        
    except Exception as e:
        print(f"[INFO] ESO data: {e}")
        print()
    
    # Step 4: Workflow summary
    print("Step 4: Analysis Workflow")
    print("-"*70)
    print()
    print("1. AKARI IR Data:")
    print("   - Temperature mapping")
    print("   - Density structure")
    print("   - Nebula morphology")
    print()
    print("2. GAIA Positions:")
    print("   - Spatial context")
    print("   - Star field background")
    print("   - [!] NOT for SSZ validation")
    print()
    print("3. ESO Spectroscopy:")
    print("   - SSZ validation (97.9%)")
    print("   - Gold standard measurements")
    print("   - Velocity/redshift analysis")
    print()
    
    # Step 5: Use cases
    print("Step 5: Scientific Use Cases")
    print("-"*70)
    print()
    print("Temperature Mapping:")
    print("  - Use AKARI N60 + N160 bands")
    print("  - Compute dust temperature")
    print("  - Map density distribution")
    print()
    print("SSZ Validation:")
    print("  - Use ESO spectroscopy")
    print("  - Apply SSZ transformation")
    print("  - Verify 97.9% success rate")
    print()
    print("Spatial Analysis:")
    print("  - Use GAIA for positions")
    print("  - Overlay on AKARI map")
    print("  - Visualize star-nebula relation")
    print()
    
    # Data hierarchy reminder
    print("="*70)
    print("[REMEMBER] DATA HIERARCHY:")
    print("="*70)
    print()
    print("PRIMARY (97.9%):  ESO spectroscopy")
    print("IR DATA:          AKARI diffuse maps")
    print("AUXILIARY (51%):  GAIA positions")
    print()
    print("Use the RIGHT data for the RIGHT purpose!")
    print()
    print("="*70)
    print("Example complete!")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
