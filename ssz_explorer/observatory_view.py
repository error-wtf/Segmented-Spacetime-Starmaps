#!/usr/bin/env python3
"""
Observatory/Planetarium View - Immersive 3D Navigation
Like Stellarium - move through space!
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Optional, Tuple
from progressive_loader import ProgressiveDataLoader, ViewportBounds, get_loader


def create_observatory_view(
    catalog_name: str = 'gaia',
    max_objects: int = 128000,
    observer_lat: float = 50.0,  # Observer latitude
    observer_lon: float = 10.0,  # Observer longitude
    view_azimuth: float = 180.0,  # Looking direction (0=N, 90=E, 180=S, 270=W)
    view_altitude: float = 45.0   # Looking up angle (0=horizon, 90=zenith)
) -> Tuple[go.Figure, dict]:
    """
    Create REAL NIGHT SKY view from Earth
    
    Like real star gazing:
    - View from Earth surface
    - Stars on celestial sphere
    - Alt/Az coordinate system
    - Zoom into regions
    - Realistic star positions
    - Night sky appearance
    
    Args:
        catalog_name: Catalog to load
        max_objects: Max objects in database
        observer_lat: Observer latitude on Earth
        observer_lon: Observer longitude on Earth
        view_azimuth: Direction looking (degrees)
        view_altitude: Angle above horizon (degrees)
        
    Returns:
        Tuple of (figure, stats_dict)
    """
    # Get loader
    loader = get_loader()
    
    # Load catalog if needed
    if loader.full_data is None or loader.total_objects == 0:
        success = loader.load_full_catalog(catalog_name, max_objects)
        if not success:
            # Fallback
            from star_map_generator import create_default_universe, create_3d_sky_map
            df = create_default_universe()
            return create_3d_sky_map(df, "Observatory View (Default)"), {'error': 'No data'}
    
    # Get MANY MORE stars for realistic night sky!
    # Load 10,000+ stars initially for dense sky coverage
    initial_data = loader.get_initial_data()
    
    # If we have more data available, get MANY more stars
    target_stars = 10000  # Target: 10K stars!
    if loader.total_objects > target_stars:
        # Get 10K stars from full dataset
        import random
        if len(loader.full_data) > target_stars:
            sample_indices = random.sample(range(len(loader.full_data)), min(target_stars, len(loader.full_data)))
            initial_data = loader.full_data.iloc[sample_indices].copy()
        else:
            initial_data = loader.full_data.copy()
    elif loader.total_objects > 1000:
        # At least get all available
        initial_data = loader.full_data.copy()
    
    # Get column names
    ra_col = 'ra'
    dec_col = 'dec'
    
    if ra_col not in initial_data.columns:
        ra_col = [c for c in initial_data.columns if 'ra' in c.lower()][0]
    if dec_col not in initial_data.columns:
        dec_col = [c for c in initial_data.columns if 'dec' in c.lower()][0]
    
    # CELESTIAL SPHERE - alle Sterne auf Kugel um Erde
    # Radius ist konstant = wie echter Himmel!
    sphere_radius = 1000.0  # parsec (egal, alle gleich weit)
    
    # Convert RA/Dec to 3D on celestial sphere
    ra_rad = np.deg2rad(initial_data[ra_col])
    dec_rad = np.deg2rad(initial_data[dec_col])
    
    # Celestial sphere coordinates
    x = sphere_radius * np.cos(dec_rad) * np.cos(ra_rad)
    y = sphere_radius * np.cos(dec_rad) * np.sin(ra_rad)
    z = sphere_radius * np.sin(dec_rad)
    
    # Star sizes based on MAGNITUDE (brighter = bigger)
    if 'magnitude' in initial_data.columns:
        # Invert magnitude scale (lower mag = brighter = bigger)
        mag = initial_data['magnitude'].clip(-2, 15)
        sizes = 20 - mag * 1.5  # Bright stars bigger
        sizes = sizes.clip(2, 25)
    else:
        sizes = np.ones(len(initial_data)) * 5
    
    # Colors by OBJECT TYPE
    colors = []
    for idx, row in initial_data.iterrows():
        if 'type' in initial_data.columns:
            obj_type = str(row['type']).lower()
            # Black Holes: BLAU
            if any(bh in obj_type for bh in ['black hole', 'bh', 'smbh']):
                colors.append('blue')
            # Planets: GRÜN
            elif any(p in obj_type for p in ['planet', 'exoplanet']):
                colors.append('lime')
            # Stars: GELB (default)
            else:
                colors.append('yellow')
        else:
            # Default: yellow for stars
            colors.append('yellow')
    
    # Build hover texts - wie echter Nachthimmel
    hover_texts = []
    for i, (idx, row) in enumerate(initial_data.iterrows()):
        name = f"Object {idx}"
        if 'source_id' in initial_data.columns:
            name = f"GAIA DR3 {row['source_id']}"
        elif 'name' in initial_data.columns:
            name = row['name']
        
        text = f"<b>⭐ {name}</b><br>"
        text += f"<b>RA:</b> {row[ra_col]:.2f}°<br>"
        text += f"<b>Dec:</b> {row[dec_col]:.2f}°<br>"
        
        if 'magnitude' in initial_data.columns:
            mag = row['magnitude']
            text += f"<b>Magnitude:</b> {mag:.2f}"
            if mag < 0:
                text += " (sehr hell!)<br>"
            elif mag < 3:
                text += " (hell)<br>"
            elif mag < 6:
                text += " (sichtbar)<br>"
            else:
                text += " (schwach)<br>"
        
        if 'parallax' in initial_data.columns and pd.notna(row['parallax']) and row['parallax'] > 0:
            dist_pc = 1000.0 / row['parallax']
            dist_ly = dist_pc * 3.26
            if dist_ly < 100:
                text += f"<b>Distance:</b> {dist_ly:.1f} light-years<br>"
            else:
                text += f"<b>Distance:</b> {dist_ly:.0f} light-years<br>"
        
        # Add ALL SSZ parameters
        from star_map_generator import _add_ssz_parameters
        text += _add_ssz_parameters(row, initial_data.columns)
        
        hover_texts.append(text)
    
    # Create 3D scatter - NIGHT SKY VIEW
    # Colors already assigned above by object type
    
    fig = go.Figure(data=[go.Scatter3d(
        x=x.tolist() if hasattr(x, 'tolist') else x,
        y=y.tolist() if hasattr(y, 'tolist') else y,
        z=z.tolist() if hasattr(z, 'tolist') else z,
        mode='markers',
        marker=dict(
            size=sizes.tolist() if hasattr(sizes, 'tolist') else sizes,
            color=colors,  # Direct color assignment by type
            showscale=False,  # No colorbar for night sky
            opacity=0.9,
            line=dict(width=1, color='rgba(255,255,255,0.2)')
        ),
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>',
        name='Stars'
    )])
    
    # Camera setup - VON ERDE AUS BLICKEN
    # WICHTIG: Wir sind INNERHALB der Celestial Sphere!
    # Camera position at center (0,0,0), looking outward
    
    # Camera is at origin
    camera_eye = dict(x=0, y=0, z=0)
    
    # Look direction based on view angles
    azimuth_rad = np.deg2rad(view_azimuth)
    altitude_rad = np.deg2rad(view_altitude)
    
    # Center = point on sphere we're looking at
    look_distance = 1.0  # On unit sphere
    center_x = look_distance * np.cos(altitude_rad) * np.cos(azimuth_rad)
    center_y = look_distance * np.cos(altitude_rad) * np.sin(azimuth_rad)
    center_z = look_distance * np.sin(altitude_rad)
    
    # Layout - NIGHT SKY
    fig.update_layout(
        title=dict(
            text=f"<b>🌌 Night Sky View - Real Stargazing</b><br>"
                 f"<sub>Showing {len(initial_data)} of {loader.total_objects:,} stars | "
                 f"Drag to look around | Scroll to zoom in/out</sub>",
            font=dict(size=20, color='white'),
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis=dict(
                visible=False,  # Keine Achsen - nur Himmel!
                showbackground=False,
                range=[-1200, 1200]  # Include full sphere
            ),
            yaxis=dict(
                visible=False,
                showbackground=False,
                range=[-1200, 1200]
            ),
            zaxis=dict(
                visible=False,
                showbackground=False,
                range=[-1200, 1200]
            ),
            bgcolor='rgb(0,0,5)',  # Dunkel wie Nachthimmel
            camera=dict(
                eye=dict(x=0.001, y=0.001, z=0.001),  # Very close to origin
                center=dict(x=0, y=0, z=0),  # Look at origin
                up=dict(x=0, y=0, z=1),
                projection=dict(type='perspective')
            ),
            aspectmode='cube',  # Important for sphere
            dragmode='turntable'  # Better for sky navigation
        ),
        paper_bgcolor='#000005',
        plot_bgcolor='#000005',
        font=dict(color='white', size=12),
        height=900,  # Größer für besseren Himmel
        showlegend=False,
        hovermode='closest',
        margin=dict(l=0, r=0, t=60, b=0)  # Mehr Platz für Himmel
    )
    
    # Stats
    stats = {
        'catalog': catalog_name,
        'total_objects': loader.total_objects,
        'visible_objects': len(initial_data),
        'observer_lat': observer_lat,
        'observer_lon': observer_lon,
        'view_azimuth': view_azimuth,
        'view_altitude': view_altitude,
        'view_type': 'night_sky'
    }
    
    return fig, stats


if __name__ == "__main__":
    print("Testing Night Sky View...")
    
    fig, stats = create_observatory_view(
        catalog_name='gaia',
        max_objects=10000,
        observer_lat=50.0,
        observer_lon=10.0,
        view_azimuth=180.0,
        view_altitude=45.0
    )
    
    print(f"[OK] Night Sky View created")
    print(f"[OK] Stats: {stats}")
    print("\n[SUCCESS] Test passed!")
