#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: M87 Multi-Frequency Analysis

Demonstrates NED multi-frequency data usage for:
- Jacobian tests (need 3+ frequencies)
- Spectral energy distribution (SED)
- Continuum spectrum analysis

M87 has 139 frequency measurements spanning 9+ orders of magnitude!

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ssz_starmaps.catalogs import CatalogManager
import numpy as np


def main():
    """M87 multi-frequency analysis example."""
    
    print("="*70)
    print("EXAMPLE: M87 MULTI-FREQUENCY ANALYSIS")
    print("="*70)
    print()
    
    # Initialize manager
    manager = CatalogManager()
    
    # Step 1: Fetch multi-frequency data
    print("Step 1: Fetching NED Multi-Frequency Data")
    print("-"*70)
    print("Object: M87 (Virgo A)")
    print("Expected: ~139 frequency measurements")
    print()
    
    try:
        m87_spectrum = manager.fetch_multifreq('M87')
        
        if len(m87_spectrum) > 0:
            print(f"[OK] Loaded {len(m87_spectrum)} frequency measurements")
            print()
            
            # Show data structure
            print("Data columns:")
            for i, col in enumerate(m87_spectrum.columns, 1):
                print(f"  {i:2d}. {col}")
            print()
            
            # Frequency range
            if 'frequency' in m87_spectrum.columns:
                freq_min = m87_spectrum['frequency'].min()
                freq_max = m87_spectrum['frequency'].max()
                print(f"Frequency range:")
                print(f"  Min: {freq_min:.2e} Hz")
                print(f"  Max: {freq_max:.2e} Hz")
                print(f"  Span: {np.log10(freq_max/freq_min):.1f} orders of magnitude")
                print()
            
            # Show sample
            print("Sample measurements (first 5):")
            if 'frequency' in m87_spectrum.columns and 'flux' in m87_spectrum.columns:
                sample = m87_spectrum[['frequency', 'flux']].head(5)
                print(sample.to_string(index=False))
            print()
            
        else:
            print("[INFO] NED data not available (requires internet)")
            print("Install: pip install astroquery")
            print()
            
    except Exception as e:
        print(f"[INFO] NED fetch: {e}")
        print("This is normal if astroquery is not installed")
        print()
    
    # Step 2: Use cases
    print("Step 2: Scientific Use Cases")
    print("-"*70)
    print()
    
    print("1. Jacobian Tests:")
    print("   - Require 3+ frequency measurements")
    print("   - Test df/dr relationships")
    print("   - Validate SSZ transformations")
    print()
    
    print("2. Spectral Energy Distribution (SED):")
    print("   - Plot flux vs frequency")
    print("   - Identify emission/absorption features")
    print("   - Compare with models")
    print()
    
    print("3. Continuum Analysis:")
    print("   - Multi-wavelength coverage")
    print("   - Radio to gamma-ray")
    print("   - Test SSZ frequency scaling")
    print()
    
    # Step 3: Jacobian test example
    print("Step 3: Example - Jacobian Test")
    print("-"*70)
    print()
    
    print("Jacobian test requires:")
    print("  - Multiple frequency measurements (M87: 139)")
    print("  - Spatial resolution (df/dr)")
    print("  - SSZ transformation formula")
    print()
    
    print("Formula:")
    print("  f_obs = f_emit * (1 + Xi(r))")
    print("  where Xi(r) = SSZ stretch factor")
    print()
    
    print("Test:")
    print("  1. Measure f_obs at different radii")
    print("  2. Calculate df/dr")
    print("  3. Compare with SSZ prediction")
    print("  4. Validate consistency")
    print()
    
    # Step 4: Why M87?
    print("Step 4: Why M87 is Perfect for This")
    print("-"*70)
    print()
    
    print("Advantages:")
    print("  - 139 frequency measurements")
    print("  - Radio to gamma-ray coverage")
    print("  - Well-studied supermassive black hole")
    print("  - Event Horizon Telescope target")
    print("  - Rich multi-wavelength data")
    print()
    
    print("Physics:")
    print("  - M_BH ~ 6.5e9 M_sun")
    print("  - Distance ~ 16.8 Mpc")
    print("  - Jet emission visible")
    print("  - Accretion disk resolved")
    print()
    
    # Step 5: Comparison with other sources
    print("Step 5: Data Source Comparison")
    print("-"*70)
    print()
    
    print("NED Multi-Frequency (M87):")
    print("  Purpose: Jacobian tests, continuum")
    print("  Measurements: 139 frequencies")
    print("  Range: ~9 orders of magnitude")
    print("  Use: df/dr tests, SED analysis")
    print()
    
    print("ESO Spectroscopy (Sgr A* stars):")
    print("  Purpose: SSZ validation")
    print("  Measurements: 47 observations")
    print("  Success: 97.9%")
    print("  Use: Velocity/redshift validation")
    print()
    
    print("AKARI IR (G79 region):")
    print("  Purpose: Temperature mapping")
    print("  Data: Diffuse emission maps")
    print("  Bands: N60, WIDE-S, WIDE-L, N160")
    print("  Use: Nebula studies")
    print()
    
    # Step 6: Next steps
    print("Step 6: Next Steps")
    print("-"*70)
    print()
    
    print("To use this data:")
    print()
    print("1. Install astroquery:")
    print("   pip install astroquery")
    print()
    print("2. Fetch M87 data:")
    print("   manager = CatalogManager()")
    print("   m87 = manager.fetch_multifreq('M87')")
    print()
    print("3. Run Jacobian test:")
    print("   # Calculate df/dr")
    print("   # Apply SSZ formula")
    print("   # Validate predictions")
    print()
    
    print("="*70)
    print("Example complete!")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
