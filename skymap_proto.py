#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Skymap - Quick Prototype
Interactive3D-style 3D interactive star map with SSZ physics

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    ASTROPY_AVAILABLE = True
except ImportError:
    ASTROPY_AVAILABLE = False
    print("⚠ astropy not available, using simplified coordinates")

from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog


def galactic_to_cartesian(ra, dec, distance_pc):
    """
    Convert RA/Dec/Distance to Galactic Cartesian coordinates.
    
    Parameters
    ----------
    ra : array
        Right ascension [degrees]
    dec : array
        Declination [degrees]
    distance_pc : array
        Distance [parsecs]
        
    Returns
    -------
    x, y, z : arrays
        Galactic Cartesian coordinates [parsecs]
    """
    if ASTROPY_AVAILABLE:
        coords = SkyCoord(
            ra=ra * u.deg,
            dec=dec * u.deg,
            distance=distance_pc * u.pc,
            frame='icrs'
        )
        gal = coords.galactic
        x, y, z = gal.cartesian.xyz.to(u.pc).value
    else:
        # Simplified conversion (not accurate, just for demo)
        ra_rad = np.radians(ra)
        dec_rad = np.radians(dec)
        x = distance_pc * np.cos(dec_rad) * np.cos(ra_rad)
        y = distance_pc * np.cos(dec_rad) * np.sin(ra_rad)
        z = distance_pc * np.sin(dec_rad)
    
    return x, y, z


def create_skymap_proto():
    """Create prototype 3D skymap."""
    
    print("="*70)
    print("SSZ SKYMAP - PROTOTYPE")
    print("="*70)
    print()
    
    # Load stars
    print("[1/4] Loading GAIA stars...")
    manager = CatalogManager(offline=True)
    stars = manager.fetch_nearby(distance_pc=50, max_stars=500, source='gaia')
    print(f"  Loaded {len(stars)} stars")
    print()
    
    # Convert to 3D coordinates
    print("[2/4] Converting to 3D coordinates...")
    x, y, z = galactic_to_cartesian(
        stars['ra'].values,
        stars['dec'].values,
        stars['distance_pc'].values
    )
    stars['x'] = x
    stars['y'] = y
    stars['z'] = z
    print(f"  Range: X=[{x.min():.1f}, {x.max():.1f}] pc")
    print(f"         Y=[{y.min():.1f}, {y.max():.1f}] pc")
    print(f"         Z=[{z.min():.1f}, {z.max():.1f}] pc")
    print()
    
    # SSZ Transform
    print("[3/4] Applying SSZ transformation...")
    stars_ssz = transform_catalog(stars, show_progress=False)
    print(f"  Mean stretch factor: {stars_ssz['stretch_factor'].mean():.4f}")
    print(f"  Mean time dilation: {stars_ssz['D_ssz'].mean():.4f}")
    print()
    
    # SSZ coordinates
    stars_ssz['x_ssz'] = stars['x'] * stars_ssz['stretch_factor']
    stars_ssz['y_ssz'] = stars['y'] * stars_ssz['stretch_factor']
    stars_ssz['z_ssz'] = stars['z'] * stars_ssz['stretch_factor']
    
    # Create hover text
    hover_text_mink = [
        f"<b>{name}</b><br>" +
        f"Distance: {dist:.2f} pc<br>" +
        f"Magnitude: {mag:.2f}<br>" +
        f"Position: ({x:.1f}, {y:.1f}, {z:.1f}) pc"
        for name, dist, mag, x, y, z in zip(
            stars['name'],
            stars['distance_pc'],
            stars.get('phot_g_mean_mag', [np.nan]*len(stars)),
            stars['x'], stars['y'], stars['z']
        )
    ]
    
    hover_text_ssz = [
        f"<b>{name}</b><br>" +
        f"Distance (Mink): {dist_m:.2f} pc<br>" +
        f"Distance (SSZ): {dist_s:.2f} pc<br>" +
        f"Stretch: {stretch:.4f}x<br>" +
        f"Time Dilation: {D:.4f}<br>" +
        f"Position: ({x:.1f}, {y:.1f}, {z:.1f}) pc"
        for name, dist_m, dist_s, stretch, D, x, y, z in zip(
            stars['name'],
            stars['distance_pc'],
            stars_ssz['distance_ssz_pc'],
            stars_ssz['stretch_factor'],
            stars_ssz['D_ssz'],
            stars_ssz['x_ssz'], stars_ssz['y_ssz'], stars_ssz['z_ssz']
        )
    ]
    
    # Create dual-view plot
    print("[4/4] Creating interactive 3D plot...")
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}]],
        subplot_titles=('Minkowski Space', 'SSZ (Segmented Spacetime)'),
        horizontal_spacing=0.05
    )
    
    # LEFT: Minkowski
    fig.add_trace(
        go.Scatter3d(
            x=stars['x'],
            y=stars['y'],
            z=stars['z'],
            mode='markers',
            marker=dict(
                size=4,
                color='cyan',
                opacity=0.8,
                line=dict(width=0)
            ),
            name='Minkowski',
            text=hover_text_mink,
            hoverinfo='text',
            hovertemplate='%{text}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # RIGHT: SSZ
    fig.add_trace(
        go.Scatter3d(
            x=stars_ssz['x_ssz'],
            y=stars_ssz['y_ssz'],
            z=stars_ssz['z_ssz'],
            mode='markers',
            marker=dict(
                size=6,
                color=stars_ssz['D_ssz'],
                colorscale='Plasma',
                showscale=True,
                opacity=0.9,
                line=dict(width=0.5, color='white'),
                colorbar=dict(
                    title="Time<br>Dilation<br>D_SSZ",
                    x=1.05,
                    len=0.5,
                    thickness=15
                )
            ),
            name='SSZ',
            text=hover_text_ssz,
            hoverinfo='text',
            hovertemplate='%{text}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='<b>SSZ Skymap - Prototype</b><br>' +
                 '<sub>Interactive 3D Star Map with Segmented Spacetime Physics</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='white')
        ),
        paper_bgcolor='#0a0a1e',
        plot_bgcolor='#0a0a1e',
        font=dict(color='white', size=12),
        showlegend=True,
        legend=dict(
            x=0.5,
            y=-0.1,
            xanchor='center',
            orientation='h',
            bgcolor='rgba(10,10,30,0.8)',
            bordercolor='cyan',
            borderwidth=1
        ),
        height=800,
        margin=dict(l=0, r=0, t=100, b=80)
    )
    
    # Update 3D scenes
    scene_layout = dict(
        xaxis=dict(
            title='X [pc]',
            backgroundcolor='#0a0a1e',
            gridcolor='#333366',
            showbackground=True,
            zerolinecolor='#666699'
        ),
        yaxis=dict(
            title='Y [pc]',
            backgroundcolor='#0a0a1e',
            gridcolor='#333366',
            showbackground=True,
            zerolinecolor='#666699'
        ),
        zaxis=dict(
            title='Z [pc]',
            backgroundcolor='#0a0a1e',
            gridcolor='#333366',
            showbackground=True,
            zerolinecolor='#666699'
        ),
        bgcolor='#0a0a1e',
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.2)
        )
    )
    
    fig.update_scenes(scene_layout, row=1, col=1)
    fig.update_scenes(scene_layout, row=1, col=2)
    
    print("  [OK] Plot created")
    print()
    print("="*70)
    print("Opening interactive 3D skymap in browser...")
    print("="*70)
    print()
    print("CONTROLS:")
    print("  - Drag: Rotate view")
    print("  - Scroll: Zoom in/out")
    print("  - Shift+Drag: Pan")
    print("  - Hover: Show star info")
    print()
    print("Compare LEFT (Minkowski) vs RIGHT (SSZ)!")
    print("Notice: SSZ stars are stretched and color-coded by time dilation")
    print()
    
    # Show
    fig.show()
    
    # Save HTML
    output_file = Path(__file__).parent / 'outputs_quick_start' / 'skymap_proto.html'
    output_file.parent.mkdir(exist_ok=True)
    fig.write_html(output_file)
    print(f"Saved to: {output_file}")
    print()


if __name__ == "__main__":
    create_skymap_proto()
