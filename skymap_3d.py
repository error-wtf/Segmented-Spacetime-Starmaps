#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Skymap 3D - Full Implementation (Phase 1)
Stellaris-style 3D interactive star map with SSZ physics

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import pandas as pd
import numpy as np

from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog
from skymap.core import (
    SkymapRenderer,
    prepare_star_coordinates,
    prepare_ssz_coordinates
)


def main():
    """Main application."""
    
    parser = argparse.ArgumentParser(
        description='SSZ Skymap 3D - Interactive Star Map'
    )
    parser.add_argument(
        '--distance', type=float, default=50,
        help='Maximum distance in parsecs (default: 50)'
    )
    parser.add_argument(
        '--max-stars', type=int, default=1000,
        help='Maximum number of stars (default: 1000)'
    )
    parser.add_argument(
        '--mode', choices=['dual', 'single'], default='dual',
        help='View mode: dual (Mink+SSZ) or single (default: dual)'
    )
    parser.add_argument(
        '--theme', choices=['dark', 'space', 'light'], default='dark',
        help='Color theme (default: dark)'
    )
    parser.add_argument(
        '--height', type=int, default=800,
        help='Plot height in pixels (default: 800)'
    )
    parser.add_argument(
        '--output', type=str, default=None,
        help='Save to HTML file (optional)'
    )
    parser.add_argument(
        '--offline', action='store_true',
        help='Use offline mode (mock data)'
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("SSZ SKYMAP 3D - PHASE 1 COMPLETE")
    print("="*70)
    print()
    print(f"Configuration:")
    print(f"  Distance: {args.distance} pc")
    print(f"  Max stars: {args.max_stars}")
    print(f"  Mode: {args.mode}")
    print(f"  Theme: {args.theme}")
    print(f"  Offline: {args.offline}")
    print()
    
    # Load data
    print("[1/5] Loading star catalog...")
    manager = CatalogManager(offline=args.offline)
    
    try:
        stars = manager.fetch_nearby(
            distance_pc=args.distance,
            max_stars=args.max_stars,
            source='gaia',
            use_cache=True
        )
        print(f"  Loaded {len(stars)} stars from GAIA")
    except Exception as e:
        print(f"  Warning: {e}")
        print(f"  Falling back to mock catalog...")
        stars = manager._get_mock_catalog(args.max_stars)
    
    print()
    
    # Prepare coordinates
    print("[2/5] Computing 3D coordinates...")
    stars = prepare_star_coordinates(stars)
    print(f"  X range: [{stars['x'].min():.1f}, {stars['x'].max():.1f}] pc")
    print(f"  Y range: [{stars['y'].min():.1f}, {stars['y'].max():.1f}] pc")
    print(f"  Z range: [{stars['z'].min():.1f}, {stars['z'].max():.1f}] pc")
    print()
    
    # SSZ Transform
    print("[3/5] Applying SSZ transformation...")
    stars_ssz = transform_catalog(stars, show_progress=True)
    stars_ssz = prepare_ssz_coordinates(stars_ssz)
    
    print(f"  Mean stretch factor: {stars_ssz['stretch_factor'].mean():.6f}")
    print(f"  Mean time dilation: {stars_ssz['D_ssz'].mean():.6f}")
    print(f"  SSZ distance shift: +{(stars_ssz['distance_ssz_pc'] - stars_ssz['distance_pc']).mean():.2f} pc")
    print()
    
    # Create renderer
    print("[4/5] Creating 3D visualization...")
    renderer = SkymapRenderer(theme=args.theme, height=args.height)
    
    if args.mode == 'dual':
        fig = renderer.create_dual_view(
            stars,
            stars_ssz,
            title="SSZ Skymap 3D"
        )
    else:
        fig = renderer.create_single_view(
            stars_ssz,
            mode='ssz',
            color_by='D_ssz',
            title="SSZ Skymap 3D (SSZ Mode)"
        )
    
    print(f"  [{args.mode} view created]")
    print()
    
    # Save/Show
    print("[5/5] Displaying...")
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        renderer.save_html(str(output_path))
        print(f"  Saved to: {output_path}")
    else:
        # Auto-save
        output_dir = Path(__file__).parent / 'outputs_quick_start'
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / 'skymap_3d.html'
        renderer.save_html(str(output_file))
        print(f"  Auto-saved to: {output_file}")
    
    print()
    print("="*70)
    print("Opening interactive 3D skymap in browser...")
    print("="*70)
    print()
    print("CONTROLS:")
    print("  Drag:        Rotate view")
    print("  Scroll:      Zoom in/out")
    print("  Shift+Drag:  Pan")
    print("  Hover:       Show star info")
    print("  Double-click: Reset camera")
    print()
    
    if args.mode == 'dual':
        print("DUAL VIEW:")
        print("  LEFT:  Minkowski space (standard)")
        print("  RIGHT: SSZ (color = time dilation)")
        print("  Notice: Stars are stretched in SSZ!")
    else:
        print("SINGLE VIEW (SSZ):")
        print("  Color: Time dilation (D_SSZ)")
        print("  Size: Slightly larger for SSZ effect")
    
    print()
    print(f"Rendering {len(stars)} stars...")
    
    renderer.show()
    
    print()
    print("="*70)
    print("[OK] PHASE 1 COMPLETE!")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
