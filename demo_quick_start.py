#!/usr/bin/env python3
"""
Quick Start Demo for SSZ StarMaps

Fetches 100 nearby stars from GAIA and applies SSZ transformations.

Usage:
    python demo_quick_start.py

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog, print_statistics
from ssz_starmaps.viz import plot_sky_comparison, plot_distance_histogram


def main():
    print("="*80)
    print("SSZ STARMAPS - QUICK START DEMO")
    print("="*80)
    print()
    
    # Create output directory
    output_dir = Path('outputs_quick_start')
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}")
    print()
    
    # Step 1: Fetch catalog
    print("[1/4] Fetching nearby stars from GAIA DR3...")
    print("-"*80)
    
    manager = CatalogManager(offline=False)  # Set to True for offline mode
    
    try:
        # Fetch 100 nearby stars within 100 parsecs
        stars = manager.fetch_nearby(
            distance_pc=100,
            max_stars=100,
            source='gaia',
            use_cache=True
        )
        
        print(f"[OK] Fetched {len(stars)} stars")
        print(f"  Distance range: {stars['distance_pc'].min():.1f} - {stars['distance_pc'].max():.1f} pc")
        print()
        
    except Exception as e:
        print(f"[WARN] GAIA fetch failed: {e}")
        print("Falling back to mock catalog...")
        stars = manager._get_mock_catalog(100)
        print()
    
    # Step 2: Apply SSZ transformation
    print("[2/4] Applying SSZ transformation...")
    print("-"*80)
    
    stars_ssz = transform_catalog(stars, show_progress=True)
    
    print(f"[OK] Transformed {len(stars_ssz)} stars")
    print()
    
    # Print statistics
    print_statistics(stars_ssz)
    print()
    
    # Step 3: Generate plots
    print("[3/4] Generating plots...")
    print("-"*80)
    
    # Sky comparison
    plot_sky_comparison(
        stars_ssz,
        output=output_dir / 'sky_comparison.png',
        dpi=300
    )
    
    # Distance histogram
    plot_distance_histogram(
        stars_ssz,
        output=output_dir / 'distance_histogram.png',
        dpi=300
    )
    
    print()
    
    # Step 4: Save data
    print("[4/4] Saving data...")
    print("-"*80)
    
    csv_file = output_dir / 'stars_ssz.csv'
    stars_ssz.to_csv(csv_file, index=False)
    print(f"[OK] Saved: {csv_file}")
    print()
    
    # Summary
    print("="*80)
    print("[OK] DEMO COMPLETE!")
    print("="*80)
    print()
    print("Generated files:")
    print(f"  - {output_dir / 'sky_comparison.png'}")
    print(f"  - {output_dir / 'distance_histogram.png'}")
    print(f"  - {output_dir / 'stars_ssz.csv'}")
    print()
    print("Check the outputs_quick_start/ directory!")
    print("="*80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
