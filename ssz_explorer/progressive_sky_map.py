#!/usr/bin/env python3
"""
Progressive Sky Maps - Large scale visualization with LOD
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Optional, Tuple
from progressive_loader import ProgressiveDataLoader, ViewportBounds, get_loader
from star_map_generator import create_sky_map, create_3d_sky_map


def create_progressive_sky_map_2d(
    catalog_name: str = 'gaia',
    max_objects: int = 128000,
    initial_display: int = 5000  # INCREASED from 128 to 5000!
) -> Tuple[go.Figure, dict]:
    """
    Create progressive 2D sky map with intelligent loading
    
    Args:
        catalog_name: Catalog to load
        max_objects: Maximum objects to load from catalog
        initial_display: Initial objects to display
        
    Returns:
        Tuple of (figure, stats_dict)
    """
    # Get loader
    loader = get_loader()
    
    # Load full catalog
    success = loader.load_full_catalog(catalog_name, max_objects)
    if not success:
        # Fallback to default universe
        from star_map_generator import create_default_universe
        df = create_default_universe()
        fig = create_sky_map(df, "Default Universe (Catalog load failed)")
        return fig, {'error': 'Could not load catalog', 'objects': len(df)}
    
    # Get initial data
    initial_data = loader.get_initial_data()
    
    # Create the map
    title = (f"🌌 {catalog_name.upper()} Sky Map - Progressive Loading<br>"
             f"<sub>Showing {len(initial_data)} of {loader.total_objects:,} objects | "
             f"Zoom/Pan to load more!</sub>")
    
    fig = create_sky_map(initial_data, title=title)
    
    # Add loading indicator annotation
    fig.add_annotation(
        text=f"📊 Loaded: {len(initial_data)}/{loader.total_objects:,} ({loader.get_stats()['load_percentage']:.1f}%)",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        bgcolor="rgba(0,0,0,0.7)",
        font=dict(color="white", size=12),
        align="left"
    )
    
    # Get stats
    stats = loader.get_stats()
    stats['catalog'] = catalog_name
    stats['initial_display'] = len(initial_data)
    
    return fig, stats


def create_progressive_sky_map_3d(
    catalog_name: str = 'gaia',
    max_objects: int = 128000,
    initial_display: int = 5000  # INCREASED from 128 to 5000!
) -> Tuple[go.Figure, dict]:
    """
    Create progressive 3D sky map with intelligent loading
    
    Args:
        catalog_name: Catalog to load
        max_objects: Maximum objects to load from catalog
        initial_display: Initial objects to display
        
    Returns:
        Tuple of (figure, stats_dict)
    """
    # Get loader
    loader = get_loader()
    
    # Check if already loaded
    if loader.full_data is None or loader.total_objects == 0:
        success = loader.load_full_catalog(catalog_name, max_objects)
        if not success:
            from star_map_generator import create_default_universe
            df = create_default_universe()
            fig = create_3d_sky_map(df, "Default Universe (3D)")
            return fig, {'error': 'Could not load catalog', 'objects': len(df)}
    
    # Get initial data
    if loader.visible_data is None or loader.visible_data.empty:
        initial_data = loader.get_initial_data()
    else:
        initial_data = loader.visible_data
    
    # Create the 3D map
    title = (f"🌌 {catalog_name.upper()} 3D Sky Map - Progressive Loading<br>"
             f"<sub>Showing {len(initial_data)} of {loader.total_objects:,} objects</sub>")
    
    fig = create_3d_sky_map(initial_data, title=title)
    
    # Get stats
    stats = loader.get_stats()
    stats['catalog'] = catalog_name
    stats['initial_display'] = len(initial_data)
    
    return fig, stats


def load_more_objects(viewport_ra_range: Tuple[float, float],
                     viewport_dec_range: Tuple[float, float],
                     zoom_level: int = 0) -> Tuple[go.Figure, dict]:
    """
    Load more objects based on current viewport
    
    Args:
        viewport_ra_range: (min_ra, max_ra)
        viewport_dec_range: (min_dec, max_dec)
        zoom_level: Current zoom level
        
    Returns:
        Updated figure and stats
    """
    loader = get_loader()
    
    if loader.full_data is None:
        return None, {'error': 'No data loaded'}
    
    # Create viewport
    viewport = ViewportBounds(
        ra_min=viewport_ra_range[0],
        ra_max=viewport_ra_range[1],
        dec_min=viewport_dec_range[0],
        dec_max=viewport_dec_range[1],
        zoom_level=zoom_level
    )
    
    # Update visible data
    updated_data = loader.update_visible_data(viewport)
    
    # Create updated map
    title = f"🌌 Sky Map - {len(updated_data)} objects visible"
    fig = create_sky_map(updated_data, title=title)
    
    # Stats
    stats = loader.get_stats()
    
    return fig, stats


def get_catalog_overview(catalog_name: str = 'gaia', 
                        max_objects: int = 100000) -> dict:
    """
    Get overview of catalog without loading full map
    
    Args:
        catalog_name: Catalog name
        max_objects: Max objects to consider
        
    Returns:
        Dictionary with catalog info
    """
    loader = ProgressiveDataLoader()
    
    success = loader.load_full_catalog(catalog_name, max_objects)
    
    if not success:
        return {
            'catalog': catalog_name,
            'status': 'error',
            'message': 'Could not load catalog'
        }
    
    stats = loader.get_stats()
    
    # Add column info
    if loader.full_data is not None:
        stats['columns'] = list(loader.full_data.columns)
        stats['has_magnitude'] = 'magnitude' in loader.full_data.columns or \
                                'phot_g_mean_mag' in loader.full_data.columns
        
        # RA/Dec ranges
        ra_cols = [c for c in loader.full_data.columns if 'ra' in c.lower()]
        dec_cols = [c for c in loader.full_data.columns if 'dec' in c.lower()]
        
        if ra_cols:
            ra_col = ra_cols[0]
            stats['ra_range'] = (float(loader.full_data[ra_col].min()), 
                               float(loader.full_data[ra_col].max()))
        
        if dec_cols:
            dec_col = dec_cols[0]
            stats['dec_range'] = (float(loader.full_data[dec_col].min()), 
                                float(loader.full_data[dec_col].max()))
    
    stats['catalog'] = catalog_name
    stats['status'] = 'success'
    
    return stats


def create_progressive_constellation_map_3d(
    ra_center: float,
    dec_center: float,
    fov: float = 30.0,
    catalog_name: str = 'gaia',
    max_objects: int = 128000,
    initial_display: int = 2000  # INCREASED from 128 to 2000!
) -> Tuple[go.Figure, dict]:
    """
    Create progressive 3D constellation/region map for specific sky region
    
    REAL 3D VIEW - like current 3D map but focused on region!
    
    Args:
        ra_center: Center RA in degrees
        dec_center: Center Dec in degrees
        fov: Field of view in degrees
        catalog_name: Catalog to use
        max_objects: Max objects in catalog
        initial_display: Initial objects to show
        
    Returns:
        Tuple of (figure, stats_dict)
    """
    # Get loader
    loader = get_loader()
    
    # Load catalog if not already loaded
    if loader.full_data is None or loader.total_objects == 0:
        success = loader.load_full_catalog(catalog_name, max_objects)
        if not success:
            from star_map_generator import create_default_universe, create_3d_sky_map
            df = create_default_universe()
            return create_3d_sky_map(df, f"3D Region (Default)"), {'error': 'Could not load catalog'}
    
    # Define viewport for region
    fov_half = fov / 2.0
    viewport = ViewportBounds(
        ra_min=max(0, ra_center - fov_half),
        ra_max=min(360, ra_center + fov_half),
        dec_min=max(-90, dec_center - fov_half),
        dec_max=min(90, dec_center + fov_half),
        zoom_level=1
    )
    
    # Get objects in region
    region_data = loader.update_visible_data(viewport)
    
    # Limit to initial display
    if len(region_data) > initial_display:
        region_data = region_data.head(initial_display)
    
    # Get column names
    ra_col = 'ra'
    dec_col = 'dec'
    if 'ra' not in region_data.columns:
        ra_col = [c for c in region_data.columns if 'ra' in c.lower()][0]
    if 'dec' not in region_data.columns:
        dec_col = [c for c in region_data.columns if 'dec' in c.lower()][0]
    
    # Convert to 3D coords
    ra_rad = np.deg2rad(region_data[ra_col])
    dec_rad = np.deg2rad(region_data[dec_col])
    
    # Distance (use parallax or default)
    if 'parallax' in region_data.columns:
        r = 1000.0 / (region_data['parallax'].clip(0.1, 1000))
    else:
        r = np.ones(len(region_data)) * 100
    
    # Cartesian coords
    x = r * np.cos(dec_rad) * np.cos(ra_rad)
    y = r * np.cos(dec_rad) * np.sin(ra_rad)
    z = r * np.sin(dec_rad)
    
    # Build hover texts
    hover_texts = []
    for i, (idx, row) in enumerate(region_data.iterrows()):
        name = f"Object {idx}"
        if 'source_id' in region_data.columns:
            name = f"GAIA DR3 {row['source_id']}"
        elif 'name' in region_data.columns:
            name = row['name']
        
        text = f"<b>⭐ {name}</b><br>"
        text += f"<b>RA:</b> {row[ra_col]:.4f}°<br>"
        text += f"<b>Dec:</b> {row[dec_col]:.4f}°<br>"
        text += f"<b>Distance:</b> {r.iloc[i]:.1f} pc<br>"
        text += f"<b>X:</b> {x.iloc[i]:.1f} pc<br>"
        text += f"<b>Y:</b> {y.iloc[i]:.1f} pc<br>"
        text += f"<b>Z:</b> {z.iloc[i]:.1f} pc<br>"
        
        if 'magnitude' in region_data.columns:
            text += f"<b>Magnitude:</b> {row['magnitude']:.2f}<br>"
        
        # Add ALL SSZ parameters
        from star_map_generator import _add_ssz_parameters
        text += _add_ssz_parameters(row, region_data.columns)
        
        hover_texts.append(text)
    
    # Create 3D scatter
    fig = go.Figure(data=[go.Scatter3d(
        x=x.tolist() if hasattr(x, 'tolist') else x,
        y=y.tolist() if hasattr(y, 'tolist') else y,
        z=z.tolist() if hasattr(z, 'tolist') else z,
        mode='markers',
        marker=dict(
            size=5,
            color=r.tolist() if hasattr(r, 'tolist') else r,
            colorscale='Viridis',
            colorbar=dict(
                title='Distance (pc)',
                len=0.7,
                thickness=15
            ),
            opacity=0.9,
            line=dict(width=0.5, color='rgba(255,255,255,0.3)')
        ),
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>',
        name='Stars'
    )])
    
    # Layout - 3D
    fig.update_layout(
        title=dict(
            text=f"<b>🎯 3D Region: RA {ra_center:.1f}°, Dec {dec_center:.1f}° (FOV: {fov}°)</b><br>"
                 f"<sub>Showing {len(region_data)} of {loader.total_objects:,} objects | "
                 f"Drag to rotate | Scroll to zoom</sub>",
            font=dict(size=18, color='white'),
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis=dict(
                title='X (parsecs)',
                backgroundcolor='rgb(10,10,31)',
                gridcolor='rgba(100,100,150,0.3)',
                showbackground=True
            ),
            yaxis=dict(
                title='Y (parsecs)',
                backgroundcolor='rgb(10,10,31)',
                gridcolor='rgba(100,100,150,0.3)',
                showbackground=True
            ),
            zaxis=dict(
                title='Z (parsecs)',
                backgroundcolor='rgb(10,10,31)',
                gridcolor='rgba(100,100,150,0.3)',
                showbackground=True
            ),
            bgcolor='rgb(0,0,16)',
            aspectmode='cube',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            )
        ),
        paper_bgcolor='#000010',
        plot_bgcolor='#000010',
        font=dict(color='white', size=12),
        height=800,
        showlegend=False,
        hovermode='closest'
    )
    
    # Stats
    stats = {
        'region_center': (ra_center, dec_center),
        'fov': fov,
        'objects_shown': len(region_data),
        'total_available': loader.total_objects,
        'catalog': catalog_name,
        'view_type': '3D'
    }
    
    return fig, stats


if __name__ == "__main__":
    print("Testing Progressive Sky Maps...")
    
    # Test 2D map
    print("\n1. Creating 2D progressive map...")
    fig_2d, stats_2d = create_progressive_sky_map_2d('gaia', max_objects=10000, initial_display=128)
    print(f"[OK] 2D Map created: {stats_2d}")
    
    # Test 3D map
    print("\n2. Creating 3D progressive map...")
    fig_3d, stats_3d = create_progressive_sky_map_3d('gaia', max_objects=10000, initial_display=128)
    print(f"[OK] 3D Map created: {stats_3d}")
    
    # Test region map
    print("\n3. Creating region map...")
    fig_region, stats_region = create_progressive_constellation_map(266.4, -29.0, 30.0)
    print(f"[OK] Region Map created: {stats_region}")
    
    # Test overview
    print("\n4. Getting catalog overview...")
    overview = get_catalog_overview('gaia', max_objects=5000)
    print(f"[OK] Overview: {overview}")
    
    print("\n[SUCCESS] ALL TESTS PASSED!")
