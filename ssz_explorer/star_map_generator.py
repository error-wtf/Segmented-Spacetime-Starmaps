#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Star Map Generator - Real astronomical visualizations

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Optional
from progressive_loader import ProgressiveDataLoader, ViewportBounds, get_loader
from plotly.subplots import make_subplots


def _add_ssz_parameters(row, columns):
    """Add all SSZ (Segmented Spacetime) parameters to hover text"""
    text = ""
    
    # SSZ-specific columns
    ssz_cols = {
        # Core SSZ parameters
        'ssz_correction': '🔬 SSZ Correction',
        'ssz_metric': '📐 SSZ Metric',
        'ssz_segment': '📊 SSZ Segment',
        'ssz_gamma': 'γ (SSZ)',
        'ssz_beta': 'β (SSZ)',
        'ssz_alpha': 'α (SSZ)',
        
        # Velocity and motion
        'v_escape': 'v_escape',
        'v_fall': 'v_fall', 
        'proper_motion': 'Proper Motion',
        'pmra': 'PM RA',
        'pmdec': 'PM Dec',
        'radial_velocity': 'Radial Velocity',
        
        # Gravitational parameters
        'gravitational_redshift': 'Grav. Redshift',
        'redshift': 'Redshift (z)',
        'mass': 'Mass',
        'mass_solar': 'Mass (M☉)',
        
        # Distance measures
        'parallax': 'Parallax',
        'distance_pc': 'Distance (pc)',
        'distance_ly': 'Distance (ly)',
        'distance_modulus': 'Distance Modulus',
        
        # SSZ-specific physics
        'ssz_potential': 'φ (SSZ Potential)',
        'ssz_curvature': 'R (SSZ Curvature)',
        'ssz_energy': 'E (SSZ Energy)',
        'ssz_momentum': 'p (SSZ Momentum)',
        
        # Deviation from GR
        'gr_deviation': 'Δ(GR)',
        'ssz_vs_gr': 'SSZ vs GR',
        'correction_factor': 'Correction Factor'
    }
    
    # Check which SSZ parameters are available
    ssz_found = False
    for col, label in ssz_cols.items():
        if col in columns and pd.notna(row[col]):
            if not ssz_found:
                text += "<br><b>🔬 SSZ Parameters:</b><br>"
                ssz_found = True
            
            value = row[col]
            if isinstance(value, (int, float)):
                # Format based on magnitude
                if abs(value) < 0.001:
                    text += f"<b>{label}:</b> {value:.6e}<br>"
                elif abs(value) < 1:
                    text += f"<b>{label}:</b> {value:.6f}<br>"
                elif abs(value) < 1000:
                    text += f"<b>{label}:</b> {value:.4f}<br>"
                else:
                    text += f"<b>{label}:</b> {value:.2f}<br>"
            else:
                text += f"<b>{label}:</b> {value}<br>"
    
    return text


def create_default_universe():
    """
    Create a DEFAULT UNIVERSE with famous astronomical objects!
    
    Returns a DataFrame with interesting objects from our universe.
    Perfect as a fallback when no data is queried.
    """
    # Famous objects in our universe
    objects = [
        # Bright Stars
        {"name": "Sirius", "ra": 101.29, "dec": -16.72, "magnitude": -1.46, "type": "Star", "distance_ly": 8.6, "constellation": "Canis Major"},
        {"name": "Canopus", "ra": 95.99, "dec": -52.70, "magnitude": -0.72, "type": "Star", "distance_ly": 310, "constellation": "Carina"},
        {"name": "Arcturus", "ra": 213.92, "dec": 19.18, "magnitude": -0.05, "type": "Star", "distance_ly": 37, "constellation": "Boötes"},
        {"name": "Vega", "ra": 279.23, "dec": 38.78, "magnitude": 0.03, "type": "Star", "distance_ly": 25, "constellation": "Lyra"},
        {"name": "Rigel", "ra": 78.63, "dec": -8.20, "magnitude": 0.12, "type": "Star", "distance_ly": 860, "constellation": "Orion"},
        {"name": "Betelgeuse", "ra": 88.79, "dec": 7.41, "magnitude": 0.50, "type": "Star", "distance_ly": 640, "constellation": "Orion"},
        {"name": "Altair", "ra": 297.70, "dec": 8.87, "magnitude": 0.77, "type": "Star", "distance_ly": 17, "constellation": "Aquila"},
        {"name": "Aldebaran", "ra": 68.98, "dec": 16.51, "magnitude": 0.85, "type": "Star", "distance_ly": 65, "constellation": "Taurus"},
        {"name": "Antares", "ra": 247.35, "dec": -26.43, "magnitude": 1.09, "type": "Star", "distance_ly": 550, "constellation": "Scorpius"},
        {"name": "Spica", "ra": 201.30, "dec": -11.16, "magnitude": 0.98, "type": "Star", "distance_ly": 250, "constellation": "Virgo"},
        
        # Galactic Center Region
        {"name": "Sgr A*", "ra": 266.42, "dec": -29.01, "magnitude": 20.0, "type": "Black Hole", "distance_ly": 26000, "constellation": "Sagittarius"},
        
        # Star Clusters
        {"name": "Pleiades (M45)", "ra": 56.75, "dec": 24.12, "magnitude": 1.6, "type": "Open Cluster", "distance_ly": 440, "constellation": "Taurus"},
        {"name": "Hyades", "ra": 67.50, "dec": 15.87, "magnitude": 0.5, "type": "Open Cluster", "distance_ly": 153, "constellation": "Taurus"},
        
        # Nebulae
        {"name": "Orion Nebula (M42)", "ra": 83.82, "dec": -5.39, "magnitude": 4.0, "type": "Nebula", "distance_ly": 1344, "constellation": "Orion"},
        {"name": "Carina Nebula", "ra": 161.25, "dec": -59.87, "magnitude": 3.0, "type": "Nebula", "distance_ly": 8500, "constellation": "Carina"},
        
        # Galaxies
        {"name": "Andromeda (M31)", "ra": 10.68, "dec": 41.27, "magnitude": 3.44, "type": "Galaxy", "distance_ly": 2537000, "constellation": "Andromeda"},
        {"name": "Triangulum (M33)", "ra": 23.46, "dec": 30.66, "magnitude": 5.72, "type": "Galaxy", "distance_ly": 2730000, "constellation": "Triangulum"},
        {"name": "Large Magellanic Cloud", "ra": 80.89, "dec": -69.76, "magnitude": 0.9, "type": "Galaxy", "distance_ly": 163000, "constellation": "Dorado"},
        {"name": "Small Magellanic Cloud", "ra": 13.16, "dec": -72.80, "magnitude": 2.7, "type": "Galaxy", "distance_ly": 200000, "constellation": "Tucana"},
        
        # Pulsars & Special
        {"name": "Crab Pulsar (M1)", "ra": 83.63, "dec": 22.01, "magnitude": 8.4, "type": "Pulsar", "distance_ly": 6500, "constellation": "Taurus"},
        {"name": "Vela Pulsar", "ra": 128.75, "dec": -45.18, "magnitude": 23.6, "type": "Pulsar", "distance_ly": 1000, "constellation": "Vela"},
        
        # Binary Systems
        {"name": "Algol", "ra": 47.04, "dec": 40.96, "magnitude": 2.12, "type": "Binary Star", "distance_ly": 93, "constellation": "Perseus"},
        {"name": "Mizar", "ra": 200.98, "dec": 54.92, "magnitude": 2.04, "type": "Binary Star", "distance_ly": 78, "constellation": "Ursa Major"},
        
        # Globular Clusters
        {"name": "Omega Centauri", "ra": 201.70, "dec": -47.48, "magnitude": 3.9, "type": "Globular Cluster", "distance_ly": 15800, "constellation": "Centaurus"},
        {"name": "47 Tucanae", "ra": 6.02, "dec": -72.08, "magnitude": 4.0, "type": "Globular Cluster", "distance_ly": 13000, "constellation": "Tucana"},
        
        # Solar System (for reference)
        {"name": "Sun", "ra": 0.0, "dec": 0.0, "magnitude": -26.74, "type": "Star", "distance_ly": 0.0000158, "constellation": "Solar System"},
    ]
    
    df = pd.DataFrame(objects)
    
    # Add some visual info
    df['info'] = df.apply(lambda x: 
        f"{x['name']}<br>"
        f"Type: {x['type']}<br>"
        f"Constellation: {x['constellation']}<br>"
        f"Distance: {x['distance_ly']:.1f} ly<br>"
        f"Magnitude: {x['magnitude']:.2f}", 
        axis=1
    )
    
    return df


def create_sky_map(df, title="Sky Map", color_by='magnitude', size_by='magnitude', interactive=True):
    """
    Create FULLY INTERACTIVE sky map from catalog data.
    
    Features:
    - Click on objects for details
    - Zoom/Pan navigation
    - Object selection
    - Hover for quick info
    - Beautiful dark theme
    
    Parameters:
    -----------
    df : DataFrame
        Catalog data with ra, dec columns
    title : str
        Plot title
    color_by : str
        Column to color points by
    size_by : str
        Column to size points by
    interactive : bool
        Enable full interactivity
        
    Returns:
    --------
    plotly Figure with full interactivity
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available. Query a catalog first!",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(height=600)
        return fig
    
    # Find RA/Dec columns (flexible naming)
    ra_col = None
    dec_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'ra' in col_lower and ra_col is None:
            ra_col = col
        if 'dec' in col_lower and dec_col is None:
            dec_col = col
    
    if ra_col is None or dec_col is None:
        fig = go.Figure()
        fig.add_annotation(
            text="No RA/Dec coordinates found in data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Get magnitude column for sizing
    mag_col = None
    for col in df.columns:
        if 'mag' in col.lower():
            mag_col = col
            break
    
    # Get color/size data - CONVERT TO LISTS for Plotly compatibility
    color_data = None
    size_data = None
    
    if color_by in df.columns:
        color_data = df[color_by].tolist()
    elif mag_col:
        color_data = df[mag_col].tolist()
        
    if size_by in df.columns:
        size_data = df[size_by]
        # Invert magnitude (brighter = larger)
        if 'mag' in size_by.lower():
            size_data = 20 - size_data.clip(-5, 20)
            size_data = size_data.clip(3, 15)
        size_data = size_data.tolist()
    elif mag_col:
        size_data = 20 - df[mag_col].clip(-5, 20)
        size_data = size_data.clip(3, 15)
        size_data = size_data.tolist()
    else:
        size_data = [6] * len(df)
    
    # Build DETAILED hover text with SMART OBJECT NAMES
    hover_texts = []
    for idx, row in df.iterrows():
        # SMART NAME DETECTION - try multiple name columns
        object_name = None
        name_candidates = [
            'name', 'Name', 'NAME',                    # Generic
            'MAIN_ID', 'main_id',                      # SIMBAD
            'designation', 'DESIGNATION',              # 2MASS, WISE
            'source_id', 'SOURCE_ID',                  # GAIA
            'pl_name', 'hostname',                     # Exoplanets
            'objname', 'OBJNAME',                      # NED
            'specobjid', 'SPECOBJID'                   # SDSS
        ]
        
        for name_col in name_candidates:
            if name_col in df.columns and pd.notna(row[name_col]):
                object_name = str(row[name_col])
                break
        
        # Fallback: create intelligent name from data
        if not object_name:
            if 'source_id' in df.columns:
                object_name = f"GAIA DR3 {row['source_id']}"
            elif 'designation' in df.columns:
                object_name = str(row['designation'])
            else:
                object_name = f"Object {idx}"
        
        # Check if this is from our default universe (has 'type' column)
        if 'type' in df.columns:
            # BEAUTIFUL hover for universe objects
            text = f"<b>✨ {object_name}</b><br>"
            text += f"<b>Type:</b> {row['type']}<br>"
            if 'constellation' in df.columns:
                text += f"<b>Constellation:</b> {row['constellation']}<br>"
            text += f"<b>RA:</b> {row[ra_col]:.4f}°<br>"
            text += f"<b>Dec:</b> {row[dec_col]:.4f}°<br>"
            if 'distance_ly' in df.columns:
                dist = row['distance_ly']
                if dist < 100:
                    text += f"<b>Distance:</b> {dist:.2f} light-years<br>"
                elif dist < 100000:
                    text += f"<b>Distance:</b> {dist:.0f} light-years<br>"
                else:
                    text += f"<b>Distance:</b> {dist/1000000:.2f} million ly<br>"
            if 'magnitude' in df.columns:
                text += f"<b>Magnitude:</b> {row['magnitude']:.2f}<br>"
            
            # Add SSZ parameters if available
            text += _add_ssz_parameters(row, df.columns)
        else:
            # Standard hover for catalog data - WITH SMART NAMES!
            text = f"<b>⭐ {object_name}</b><br>"
            text += f"<b>RA:</b> {row[ra_col]:.6f}°<br>"
            text += f"<b>Dec:</b> {row[dec_col]:.6f}°<br>"
            
            # Add important columns first
            priority_cols = ['magnitude', 'parallax', 'pmra', 'pmdec', 'phot_g_mean_mag', 
                           'radial_velocity', 'dist', 'distance', 'j_m', 'h_m', 'k_m']
            
            # Show priority columns
            for col in priority_cols:
                if col in df.columns and pd.notna(row[col]):
                    value = row[col]
                    if isinstance(value, (int, float)):
                        text += f"<b>{col}:</b> {value:.4f}<br>"
            
            # Add remaining columns (max 5 more)
            shown = 0
            for col in df.columns:
                if col not in [ra_col, dec_col, 'info'] + name_candidates + priority_cols:
                    if shown >= 5:
                        break
                    value = row[col]
                    if pd.notna(value):
                        if isinstance(value, (int, float)):
                            text += f"<b>{col}:</b> {value:.4f}<br>"
                        else:
                            text += f"<b>{col}:</b> {value}<br>"
                        shown += 1
            
            # Add ALL SSZ parameters (not limited!)
            text += _add_ssz_parameters(row, df.columns)
        
        hover_texts.append(text)
    
    # Create plot with FULL interactivity
    fig = go.Figure()
    
    # COLOR CODING by object type
    is_black_hole = np.zeros(len(df), dtype=bool)
    is_planet = np.zeros(len(df), dtype=bool)
    is_star = np.zeros(len(df), dtype=bool)
    
    if 'type' in df.columns:
        # Black holes: BLAU!
        bh_types = ['Black Hole', 'black hole', 'BH', 'SMBH', 'Supermassive Black Hole']
        for bh_type in bh_types:
            is_black_hole |= df['type'].str.contains(bh_type, case=False, na=False)
        
        # Planets: GRÜN!
        planet_types = ['Planet', 'planet', 'Exoplanet', 'exoplanet']
        for p_type in planet_types:
            is_planet |= df['type'].str.contains(p_type, case=False, na=False)
        
        # Stars: GELB! (everything not BH or planet)
        is_star = ~(is_black_hole | is_planet)
    else:
        # Default: all are stars
        is_star = np.ones(len(df), dtype=bool)
    
    # Add STARS (yellow)
    if is_star.any():
        fig.add_trace(go.Scattergl(
            x=df[ra_col][is_star].tolist(),
            y=df[dec_col][is_star].tolist(),
            mode='markers',
            marker=dict(
                size=5,
                color='yellow',  # GELB für Sterne!
                opacity=0.8,
                line=dict(width=1, color='rgba(255,200,0,0.4)')
            ),
            text=[hover_texts[i] for i, mask in enumerate(is_star) if mask],
            hovertemplate='%{text}<extra></extra>',
            name='⭐ Stars'
        ))
    
    # Add PLANETS (green)
    if is_planet.any():
        fig.add_trace(go.Scattergl(
            x=df[ra_col][is_planet].tolist(),
            y=df[dec_col][is_planet].tolist(),
            mode='markers',
            marker=dict(
                size=8,
                color='lime',  # GRÜN für Planeten!
                symbol='circle',
                line=dict(width=2, color='darkgreen'),
                opacity=0.9
            ),
            text=[hover_texts[i] for i, mask in enumerate(is_planet) if mask],
            hovertemplate='%{text}<extra></extra>',
            name='🌍 Planets'
        ))
    
    # Add BLACK HOLES (blue)
    if is_black_hole.any():
        fig.add_trace(go.Scattergl(
            x=df[ra_col][is_black_hole].tolist(),
            y=df[dec_col][is_black_hole].tolist(),
            mode='markers',
            marker=dict(
                size=15,  # Larger!
                color='blue',  # BLAU für Black Holes!
                symbol='circle',
                line=dict(width=3, color='darkblue'),
                opacity=0.9
            ),
            text=[hover_texts[i] for i, mask in enumerate(is_black_hole) if mask],
            hovertemplate='%{text}<extra></extra>',
            name='⚫ Black Holes'
        ))
    
    # Fallback: if no types detected at all, add all as yellow stars
    if not is_star.any() and not is_planet.any() and not is_black_hole.any():
        fig.add_trace(go.Scattergl(
            x=df[ra_col].tolist(),
            y=df[dec_col].tolist(),
            mode='markers',
            marker=dict(
                size=5,
                color='yellow',  # GELB default
                opacity=0.8,
                line=dict(width=1, color='rgba(255,200,0,0.4)')
            ),
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            name='⭐ Stars',
            customdata=df.index.tolist()
        ))
    
    # Enhanced Layout with FULL CONTROLS
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br><sub>{len(df)} objects | Click to select | Drag to pan | Scroll to zoom</sub>",
            font=dict(size=20),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="<b>Right Ascension (degrees)</b>",
            gridcolor='rgba(100,100,150,0.2)',
            showgrid=True,
            zeroline=False,
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikecolor='rgba(255,255,0,0.5)',
            spikethickness=1
        ),
        yaxis=dict(
            title="<b>Declination (degrees)</b>",
            gridcolor='rgba(100,100,150,0.2)',
            showgrid=True,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikecolor='rgba(255,255,0,0.5)',
            spikethickness=1
        ),
        plot_bgcolor='#0a0a1f',
        paper_bgcolor='#000010',
        font=dict(color='white', size=12),
        height=750,
        hovermode='closest',
        showlegend=False,
        # DRAG MODE for navigation
        dragmode='pan'
    )
    
    # Configure ZOOM/PAN/SELECT tools
    fig.update_xaxes(
        fixedrange=False,  # Allow zoom
        rangeslider_visible=False
    )
    fig.update_yaxes(
        fixedrange=False  # Allow zoom
    )
    
    # Add navigation instructions
    fig.add_annotation(
        text="<b>Controls:</b> Scroll=Zoom | Drag=Pan | Click=Select | Double-click=Reset",
        xref="paper", yref="paper",
        x=0.5, y=-0.08,
        showarrow=False,
        font=dict(size=10, color='rgba(255,255,255,0.6)'),
        xanchor='center'
    )
    
    return fig


def create_3d_sky_map(df, title="3D Sky Map"):
    """
    Create INTERACTIVE 3D celestial sphere visualization.
    
    Features:
    - Rotate with mouse
    - Click objects for details
    - Zoom in/out
    - Full 3D navigation
    
    Parameters:
    -----------
    df : DataFrame
        Data with ra, dec, distance columns
        
    Returns:
    --------
    Interactive 3D plotly Figure
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Find columns
    ra_col = next((col for col in df.columns if 'ra' in col.lower()), None)
    dec_col = next((col for col in df.columns if 'dec' in col.lower()), None)
    dist_col = next((col for col in df.columns if 'dist' in col.lower()), None)
    
    if ra_col is None or dec_col is None:
        fig = go.Figure()
        fig.add_annotation(text="Missing coordinates", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    # Convert to Cartesian (celestial sphere)
    ra_rad = np.radians(df[ra_col])
    dec_rad = np.radians(df[dec_col])
    
    # Use distance if available, otherwise unit sphere
    if dist_col and dist_col in df.columns:
        r = df[dist_col].clip(1, 1000)  # Clip extreme values
    else:
        r = np.ones(len(df)) * 100  # Unit sphere at radius 100
    
    # Cartesian coordinates
    x = r * np.cos(dec_rad) * np.cos(ra_rad)
    y = r * np.cos(dec_rad) * np.sin(ra_rad)
    z = r * np.sin(dec_rad)
    
    # Build detailed hover text with SMART NAMES
    hover_texts = []
    for i, (idx, row) in enumerate(df.iterrows()):
        # SMART NAME DETECTION
        object_name = None
        name_candidates = [
            'name', 'Name', 'NAME',
            'MAIN_ID', 'main_id',
            'designation', 'DESIGNATION',
            'source_id', 'SOURCE_ID',
            'pl_name', 'hostname',
            'objname', 'OBJNAME',
            'specobjid', 'SPECOBJID'
        ]
        
        for name_col in name_candidates:
            if name_col in df.columns and pd.notna(row[name_col]):
                object_name = str(row[name_col])
                break
        
        if not object_name:
            if 'source_id' in df.columns:
                object_name = f"GAIA DR3 {row['source_id']}"
            elif 'designation' in df.columns:
                object_name = str(row['designation'])
            else:
                object_name = f"Object {idx}"
        
        # Build hover text
        text = f"<b>⭐ {object_name}</b><br>"
        text += f"<b>RA:</b> {row[ra_col]:.4f}°<br>"
        text += f"<b>Dec:</b> {row[dec_col]:.4f}°<br>"
        if dist_col and dist_col in df.columns:
            text += f"<b>Distance:</b> {row[dist_col]:.2f} pc<br>"
        
        # Get current position using enumerate index i
        current_x = x.iloc[i] if hasattr(x, 'iloc') else x[i]
        current_y = y.iloc[i] if hasattr(y, 'iloc') else y[i]
        current_z = z.iloc[i] if hasattr(z, 'iloc') else z[i]
        
        text += f"<b>X:</b> {current_x:.2f} pc<br>"
        text += f"<b>Y:</b> {current_y:.2f} pc<br>"
        text += f"<b>Z:</b> {current_z:.2f} pc<br>"
        
        # Add type if available
        if 'type' in df.columns:
            text += f"<b>Type:</b> {row['type']}<br>"
        
        # Add ALL SSZ parameters
        text += _add_ssz_parameters(row, df.columns)
        
        hover_texts.append(text)
    
    # Create 3D scatter with FULL interactivity
    fig = go.Figure(data=[go.Scatter3d(
        x=x.tolist() if hasattr(x, 'tolist') else x,
        y=y.tolist() if hasattr(y, 'tolist') else y,
        z=z.tolist() if hasattr(z, 'tolist') else z,
        mode='markers',
        marker=dict(
            size=4,
            color=r.tolist() if dist_col else list(np.random.rand(len(df))),
            colorscale='Turbo' if dist_col else 'Viridis',
            colorbar=dict(
                title='Distance (pc)' if dist_col else 'Index',
                len=0.7,
                thickness=20
            ),
            opacity=0.9,
            line=dict(width=0.5, color='rgba(255,255,255,0.3)'),
            # Selection styling for 3D
            showscale=True
        ),
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>',
        name='Objects',
        customdata=df.index
    )])
    
    # Enhanced 3D Layout
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br><sub>{len(df)} objects | Drag to rotate | Scroll to zoom</sub>",
            font=dict(size=18),
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis=dict(
                title='<b>X (pc)</b>',
                backgroundcolor='#000000',
                gridcolor='rgba(100,150,200,0.3)',
                showbackground=True,
                zerolinecolor='rgba(255,255,0,0.3)'
            ),
            yaxis=dict(
                title='<b>Y (pc)</b>',
                backgroundcolor='#000000',
                gridcolor='rgba(100,150,200,0.3)',
                showbackground=True,
                zerolinecolor='rgba(255,255,0,0.3)'
            ),
            zaxis=dict(
                title='<b>Z (pc)</b>',
                backgroundcolor='#000000',
                gridcolor='rgba(100,150,200,0.3)',
                showbackground=True,
                zerolinecolor='rgba(255,255,0,0.3)'
            ),
            bgcolor='#0a0a1f',
            # Camera settings for better view
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode='cube'
        ),
        paper_bgcolor='#000010',
        font=dict(color='white', size=12),
        height=750,
        hovermode='closest',
        showlegend=False
    )
    
    # Add navigation instructions
    fig.add_annotation(
        text="<b>Controls:</b> Drag=Rotate | Scroll=Zoom | Right-drag=Pan | Double-click=Reset",
        xref="paper", yref="paper",
        x=0.5, y=0.02,
        showarrow=False,
        font=dict(size=10, color='rgba(255,255,255,0.7)'),
        xanchor='center'
    )
    
    return fig


def create_constellation_map(ra_center=0, dec_center=0, fov=30):
    """
    Create constellation map for a region of sky.
    
    Parameters:
    -----------
    ra_center : float
        Center RA in degrees
    dec_center : float
        Center Dec in degrees
    fov : float
        Field of view in degrees
        
    Returns:
    --------
    plotly Figure
    """
    # Create empty star field
    fig = go.Figure()
    
    # Galactic plane (approximate)
    if abs(dec_center) < 60:
        galactic_lon = np.linspace(ra_center - fov, ra_center + fov, 100)
        galactic_lat = np.zeros_like(galactic_lon)
        
        fig.add_trace(go.Scatter(
            x=galactic_lon,
            y=galactic_lat,
            mode='lines',
            line=dict(color='rgba(255,200,100,0.3)', width=2, dash='dash'),
            name='Galactic Plane',
            hoverinfo='skip'
        ))
    
    # Ecliptic (approximate)
    ecliptic_lon = np.linspace(ra_center - fov, ra_center + fov, 100)
    ecliptic_lat = 23.5 * np.sin(np.radians(ecliptic_lon))
    
    fig.add_trace(go.Scatter(
        x=ecliptic_lon,
        y=ecliptic_lat,
        mode='lines',
        line=dict(color='rgba(200,200,255,0.3)', width=2, dash='dot'),
        name='Ecliptic',
        hoverinfo='skip'
    ))
    
    # Layout
    fig.update_layout(
        title=f"Sky Region: RA={ra_center:.1f}°, Dec={dec_center:.1f}° (FOV={fov}°)",
        xaxis=dict(
            title="RA (degrees)",
            range=[ra_center - fov/2, ra_center + fov/2],
            gridcolor='rgba(100,100,100,0.2)'
        ),
        yaxis=dict(
            title="Dec (degrees)",
            range=[dec_center - fov/2, dec_center + fov/2],
            scaleanchor="x",
            scaleratio=1,
            gridcolor='rgba(100,100,100,0.2)'
        ),
        plot_bgcolor='#0a0a1f',
        paper_bgcolor='#000010',
        font=dict(color='white'),
        height=600,
        showlegend=True
    )
    
    return fig


# Example usage
if __name__ == "__main__":
    print("="*80)
    print("STAR MAP GENERATOR TEST")
    print("="*80)
    
    # Create test data
    np.random.seed(42)
    n_stars = 1000
    
    test_data = pd.DataFrame({
        'ra': np.random.uniform(0, 360, n_stars),
        'dec': np.random.uniform(-90, 90, n_stars),
        'magnitude': np.random.uniform(0, 15, n_stars),
        'distance_pc': np.random.uniform(10, 1000, n_stars)
    })
    
    print(f"\n✅ Created test data with {len(test_data)} stars")
    
    # Test 2D map
    fig_2d = create_sky_map(test_data, "Test Sky Map")
    print("✅ 2D Sky map created")
    
    # Test 3D map
    fig_3d = create_3d_sky_map(test_data, "Test 3D Map")
    print("✅ 3D Sky map created")
    
    # Test constellation map
    fig_const = create_constellation_map(266.4, -29.0, 30)
    print("✅ Constellation map created")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED")
    print("="*80)
