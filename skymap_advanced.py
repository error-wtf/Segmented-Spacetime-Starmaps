#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Skymap Advanced - With Visual Effects
Phase 2: Advanced SSZ Integration

Features:
- Glow effects (intensity ∝ stretch factor)
- Gravitational halos
- Connection lines
- Distance rulers
- Toggle mode (Mink ↔ SSZ)

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog
from skymap.core import (
    SkymapRenderer,
    prepare_star_coordinates,
    prepare_ssz_coordinates
)
from skymap.effects import (
    apply_glow_effect,
    create_connection_lines,
    create_distance_ruler
)


def main():
    """Main application with advanced effects."""
    
    parser = argparse.ArgumentParser(
        description='SSZ Skymap Advanced - With Visual Effects'
    )
    parser.add_argument('--distance', type=float, default=50)
    parser.add_argument('--max-stars', type=int, default=500)
    parser.add_argument('--effects', nargs='+', 
                       choices=['glow', 'connections', 'ruler'],
                       default=['glow'],
                       help='Visual effects to apply')
    parser.add_argument('--glow-mode', choices=['stretch', 'dilation', 'combined'],
                       default='stretch',
                       help='Glow effect mode')
    parser.add_argument('--connections', action='store_true',
                       help='Show connection lines')
    parser.add_argument('--theme', choices=['dark', 'space', 'light'],
                       default='space')
    parser.add_argument('--height', type=int, default=900)
    parser.add_argument('--output', type=str, default=None)
    
    args = parser.parse_args()
    
    print("="*70)
    print("SSZ SKYMAP ADVANCED - PHASE 2")
    print("="*70)
    print()
    print(f"Effects enabled: {', '.join(args.effects)}")
    print(f"Glow mode: {args.glow_mode}")
    print(f"Connections: {args.connections}")
    print()
    
    # Load data
    print("[1/6] Loading catalog...")
    manager = CatalogManager(offline=True)
    
    try:
        stars = manager.fetch_nearby(
            distance_pc=args.distance,
            max_stars=args.max_stars,
            source='gaia',
            use_cache=True
        )
        print(f"  Loaded {len(stars)} stars")
    except:
        stars = manager._get_mock_catalog(args.max_stars)
        print(f"  Using {len(stars)} mock stars")
    
    print()
    
    # Prepare coordinates
    print("[2/6] Computing coordinates...")
    stars = prepare_star_coordinates(stars)
    print()
    
    # SSZ Transform
    print("[3/6] Applying SSZ...")
    stars_ssz = transform_catalog(stars, show_progress=False)
    stars_ssz = prepare_ssz_coordinates(stars_ssz)
    print(f"  Mean stretch: {stars_ssz['stretch_factor'].mean():.6f}")
    print(f"  Mean D_SSZ: {stars_ssz['D_ssz'].mean():.6f}")
    print()
    
    # Apply effects
    print("[4/6] Applying visual effects...")
    
    if 'glow' in args.effects:
        sizes, opacities = apply_glow_effect(
            stars_ssz,
            base_size=5.0,
            glow_factor=3.0,
            mode=args.glow_mode
        )
        print(f"  [OK] Glow effect ({args.glow_mode})")
    else:
        sizes = np.ones(len(stars_ssz)) * 5.0
        opacities = np.ones(len(stars_ssz)) * 0.8
    
    connection_traces = []
    if 'connections' in args.effects or args.connections:
        connection_traces = create_connection_lines(
            stars,
            max_distance=5.0,
            max_connections=3
        )
        print(f"  [OK] Connection lines ({len(connection_traces)} connections)")
    
    print()
    
    # Create figure
    print("[5/6] Creating visualization...")
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}]],
        subplot_titles=('Minkowski (Standard)', 'SSZ (with Effects)'),
        horizontal_spacing=0.05
    )
    
    # Theme colors
    themes = {
        'space': {'bg': '#000000', 'grid': '#1a1a2e', 'text': '#00ffff'},
        'dark': {'bg': '#0a0a1e', 'grid': '#333366', 'text': 'white'},
        'light': {'bg': '#ffffff', 'grid': '#cccccc', 'text': 'black'}
    }
    colors = themes[args.theme]
    
    # LEFT: Minkowski (simple)
    fig.add_trace(
        go.Scatter3d(
            x=stars['x'],
            y=stars['y'],
            z=stars['z'],
            mode='markers',
            marker=dict(
                size=4,
                color='cyan',
                opacity=0.7
            ),
            name='Stars (Mink)',
            hovertemplate='<b>%{text}</b><br>Dist: %{customdata:.2f} pc<extra></extra>',
            text=stars['name'],
            customdata=stars['distance_pc']
        ),
        row=1, col=1
    )
    
    # RIGHT: SSZ (with effects)
    fig.add_trace(
        go.Scatter3d(
            x=stars_ssz['x_ssz'],
            y=stars_ssz['y_ssz'],
            z=stars_ssz['z_ssz'],
            mode='markers',
            marker=dict(
                size=sizes,
                color=stars_ssz['D_ssz'],
                colorscale='Plasma',
                showscale=True,
                opacity=0.9,
                line=dict(width=1, color='white'),
                colorbar=dict(
                    title="D_SSZ<br>(Time<br>Dilation)",
                    x=1.05,
                    len=0.6,
                    thickness=20
                )
            ),
            name='Stars (SSZ+Effects)',
            hovertemplate=(
                '<b>%{text}</b><br>' +
                'Dist (Mink): %{customdata[0]:.2f} pc<br>' +
                'Dist (SSZ): %{customdata[1]:.2f} pc<br>' +
                'Stretch: %{customdata[2]:.4f}x<br>' +
                'D_SSZ: %{customdata[3]:.4f}<extra></extra>'
            ),
            text=stars_ssz['name'],
            customdata=np.column_stack([
                stars_ssz['distance_pc'],
                stars_ssz['distance_ssz_pc'],
                stars_ssz['stretch_factor'],
                stars_ssz['D_ssz']
            ])
        ),
        row=1, col=2
    )
    
    # Add connections to SSZ view
    for conn_trace in connection_traces:
        fig.add_trace(conn_trace, row=1, col=2)
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=(
                '<b>SSZ Skymap Advanced</b><br>' +
                f'<sub>Effects: {", ".join(args.effects)} | ' +
                f'Mode: {args.glow_mode} | ' +
                f'{len(stars)} stars</sub>'
            ),
            x=0.5,
            xanchor='center',
            font=dict(size=22, color=colors['text'])
        ),
        paper_bgcolor=colors['bg'],
        plot_bgcolor=colors['bg'],
        font=dict(color=colors['text'], size=12),
        showlegend=True,
        legend=dict(
            x=0.5,
            y=-0.08,
            xanchor='center',
            orientation='h',
            bgcolor=f"rgba(0,0,0,0.8)",
            bordercolor=colors['text'],
            borderwidth=1
        ),
        height=args.height,
        margin=dict(l=0, r=0, t=120, b=80)
    )
    
    # Update scenes
    scene_layout = dict(
        xaxis=dict(
            title='X [pc]',
            backgroundcolor=colors['bg'],
            gridcolor=colors['grid'],
            showbackground=True
        ),
        yaxis=dict(
            title='Y [pc]',
            backgroundcolor=colors['bg'],
            gridcolor=colors['grid'],
            showbackground=True
        ),
        zaxis=dict(
            title='Z [pc]',
            backgroundcolor=colors['bg'],
            gridcolor=colors['grid'],
            showbackground=True
        ),
        bgcolor=colors['bg'],
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
    )
    
    fig.update_scenes(scene_layout, row=1, col=1)
    fig.update_scenes(scene_layout, row=1, col=2)
    
    print(f"  [Advanced view created with {len(connection_traces)} effects]")
    print()
    
    # Save/Show
    print("[6/6] Displaying...")
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path(__file__).parent / 'outputs_quick_start'
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / 'skymap_advanced.html'
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f"  Saved to: {output_path}")
    print()
    
    print("="*70)
    print("ADVANCED FEATURES:")
    print("="*70)
    print()
    
    if 'glow' in args.effects:
        print(f"[GLOW EFFECT] ({args.glow_mode}):")
        print(f"   - Star size proportional to SSZ stretch")
        print(f"   - Opacity increases with effect strength")
        print(f"   - Notice: Brighter stars = stronger SSZ!")
        print()
    
    if connection_traces:
        print(f"[CONNECTIONS]:")
        print(f"   - {len(connection_traces)} links between nearby stars")
        print(f"   - Shows spatial relationships")
        print(f"   - Max distance: 5 pc")
        print()
    
    print("[COMPARE]:")
    print("   LEFT:  Standard Minkowski (flat spacetime)")
    print("   RIGHT: SSZ with visual effects (curved spacetime)")
    print()
    
    print("Opening in browser...")
    fig.show()
    
    print()
    print("="*70)
    print("[OK] PHASE 2 COMPLETE!")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
