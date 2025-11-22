#!/usr/bin/env python3
"""
Batch Process Multiple Interesting Sky Regions

Processes multiple pre-defined regions and generates comparison plots.

Usage:
    python scripts/batch_process_regions.py
    python scripts/batch_process_regions.py --region orion
    python scripts/batch_process_regions.py --all

© 2025 Carmen Wrede, Lino Casu
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ssz_starmaps.catalogs import CatalogManager, INTERESTING_REGIONS
from ssz_starmaps.transform import transform_catalog, print_statistics
from ssz_starmaps.viz import plot_sky_comparison, plot_distance_histogram


def process_region(region_name: str, output_dir: Path, max_stars: int = 500):
    """Process a single region."""
    print(f"\n{'='*80}")
    print(f"PROCESSING REGION: {region_name.upper()}")
    print(f"{'='*80}\n")
    
    # Fetch
    manager = CatalogManager()
    
    try:
        stars = manager.fetch_interesting(region_name, max_stars=max_stars)
        print(f"✓ Fetched {len(stars)} stars from {region_name}")
    except Exception as e:
        print(f"⚠ Error fetching {region_name}: {e}")
        print("Skipping region...")
        return
    
    # Transform
    print(f"\nTransforming {region_name}...")
    stars_ssz = transform_catalog(stars, show_progress=True)
    
    # Statistics
    print()
    print_statistics(stars_ssz)
    
    # Create region output directory
    region_dir = output_dir / region_name
    region_dir.mkdir(exist_ok=True)
    
    # Generate plots
    print(f"\nGenerating plots for {region_name}...")
    
    plot_sky_comparison(
        stars_ssz,
        output=region_dir / f'{region_name}_sky_comparison.png',
        dpi=300
    )
    
    plot_distance_histogram(
        stars_ssz,
        output=region_dir / f'{region_name}_distance_histogram.png',
        dpi=300
    )
    
    # Save data
    stars_ssz.to_csv(region_dir / f'{region_name}_ssz.csv', index=False)
    print(f"✓ Saved data to: {region_dir}")
    
    print(f"\n✅ {region_name.upper()} COMPLETE!")


def main():
    parser = argparse.ArgumentParser(
        description='Batch process astronomical regions with SSZ transformations'
    )
    parser.add_argument(
        '--region',
        choices=list(INTERESTING_REGIONS.keys()) + ['all'],
        default='all',
        help='Region to process (default: all)'
    )
    parser.add_argument(
        '--max-stars',
        type=int,
        default=500,
        help='Maximum stars per region (default: 500)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default='batch_outputs',
        help='Output directory (default: batch_outputs)'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    args.output_dir.mkdir(exist_ok=True)
    
    print("="*80)
    print("SSZ STARMAPS - BATCH REGION PROCESSING")
    print("="*80)
    print(f"Output directory: {args.output_dir}")
    print(f"Max stars per region: {args.max_stars}")
    print()
    
    # Select regions to process
    if args.region == 'all':
        regions_to_process = list(INTERESTING_REGIONS.keys())
        print(f"Processing ALL regions: {', '.join(regions_to_process)}")
    else:
        regions_to_process = [args.region]
        print(f"Processing region: {args.region}")
    
    # Process each region
    for i, region_name in enumerate(regions_to_process, 1):
        print(f"\n[{i}/{len(regions_to_process)}]", end=' ')
        
        try:
            process_region(region_name, args.output_dir, args.max_stars)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error processing {region_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Final summary
    print("\n" + "="*80)
    print("✅ BATCH PROCESSING COMPLETE!")
    print("="*80)
    print(f"\nProcessed {len(regions_to_process)} regions")
    print(f"Check outputs in: {args.output_dir}")
    print()
    
    # List outputs
    for region in regions_to_process:
        region_dir = args.output_dir / region
        if region_dir.exists():
            print(f"  {region}/")
            for file in sorted(region_dir.glob('*')):
                print(f"    - {file.name}")


if __name__ == '__main__':
    main()
