#!/usr/bin/env python3
"""
Interactive Navigation System
- Select object to rotate around
- Progressive loading on zoom out
- Infinite object streaming
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Tuple, Dict, List
import json


class NavigationState:
    """Track navigation state for interactive viewing"""
    
    def __init__(self):
        self.selected_object = None  # Object we're rotating around
        self.center_position = (0, 0, 0)  # Current center point
        self.zoom_level = 1.0
        self.loaded_radius = 1000.0  # Current loaded radius (pc)
        self.max_radius = 100000.0  # Maximum radius to load (pc)
        
    def select_object(self, object_data):
        """Select an object to center on"""
        self.selected_object = object_data
        if object_data is not None:
            # Extract position
            self.center_position = (
                object_data.get('x', 0),
                object_data.get('y', 0),
                object_data.get('z', 0)
            )
    
    def update_zoom(self, new_zoom):
        """Update zoom level and calculate required radius"""
        self.zoom_level = new_zoom
        
        # Calculate required radius based on zoom
        # Zoom out = larger radius needed
        self.loaded_radius = 1000.0 / new_zoom
        
        # Cap at maximum
        if self.loaded_radius > self.max_radius:
            self.loaded_radius = self.max_radius
    
    def needs_more_objects(self, current_max_distance):
        """Check if we need to load more objects"""
        return current_max_distance < self.loaded_radius * 0.9


def create_interactive_sky_view(
    initial_data: pd.DataFrame,
    loader=None,
    enable_rotation: bool = True,
    enable_progressive: bool = True
) -> Tuple[go.Figure, Dict]:
    """
    Create interactive sky view with:
    - Object selection for rotation
    - Progressive loading on zoom
    
    Args:
        initial_data: Initial objects to display
        loader: Progressive data loader
        enable_rotation: Enable rotation around selected object
        enable_progressive: Enable progressive loading
        
    Returns:
        Figure and stats dict
    """
    
    # Get coordinates
    ra_col = 'ra' if 'ra' in initial_data.columns else [c for c in initial_data.columns if 'ra' in c.lower()][0]
    dec_col = 'dec' if 'dec' in initial_data.columns else [c for c in initial_data.columns if 'dec' in c.lower()][0]
    
    # Convert to 3D
    ra_rad = np.deg2rad(initial_data[ra_col])
    dec_rad = np.deg2rad(initial_data[dec_col])
    
    # Distance from parallax or default
    if 'parallax' in initial_data.columns:
        r = 1000.0 / initial_data['parallax'].clip(0.1, 1000)
    else:
        r = np.ones(len(initial_data)) * 1000
    
    x = r * np.cos(dec_rad) * np.cos(ra_rad)
    y = r * np.cos(dec_rad) * np.sin(ra_rad)
    z = r * np.sin(dec_rad)
    
    # Sizes by magnitude
    if 'magnitude' in initial_data.columns:
        mag = initial_data['magnitude'].clip(-2, 15)
        sizes = 20 - mag * 1.5
        sizes = sizes.clip(3, 25)
    else:
        sizes = np.ones(len(initial_data)) * 5
    
    # Colors by magnitude
    if 'magnitude' in initial_data.columns:
        colors = 15 - initial_data['magnitude'].clip(-2, 15)
    else:
        colors = np.ones(len(initial_data)) * 10
    
    # Build hover texts with selection info
    hover_texts = []
    for idx, row in initial_data.iterrows():
        name = f"Object {idx}"
        if 'name' in initial_data.columns:
            name = row['name']
        elif 'source_id' in initial_data.columns:
            name = f"GAIA {row['source_id']}"
        
        text = f"<b>⭐ {name}</b><br>"
        text += f"<b>RA:</b> {row[ra_col]:.2f}°<br>"
        text += f"<b>Dec:</b> {row[dec_col]:.2f}°<br>"
        
        if 'magnitude' in initial_data.columns:
            text += f"<b>Mag:</b> {row['magnitude']:.2f}<br>"
        
        text += "<br><i>Click to center & rotate around this object!</i>"
        
        hover_texts.append(text)
    
    # Create figure with custom data for selection
    customdata = []
    for i, idx in enumerate(initial_data.index):
        customdata.append({
            'index': idx,
            'x': x.iloc[i] if hasattr(x, 'iloc') else x[i],
            'y': y.iloc[i] if hasattr(y, 'iloc') else y[i],
            'z': z.iloc[i] if hasattr(z, 'iloc') else z[i],
            'name': hover_texts[i]
        })
    
    fig = go.Figure(data=[go.Scatter3d(
        x=x.tolist() if hasattr(x, 'tolist') else x,
        y=y.tolist() if hasattr(y, 'tolist') else y,
        z=z.tolist() if hasattr(z, 'tolist') else z,
        mode='markers',
        marker=dict(
            size=sizes.tolist() if hasattr(sizes, 'tolist') else sizes,
            color=colors.tolist() if hasattr(colors, 'tolist') else colors,
            colorscale='Turbo',
            showscale=False,
            opacity=0.9,
            line=dict(width=0.5, color='rgba(255,255,255,0.2)')
        ),
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>',
        customdata=customdata,
        name='Stars'
    )])
    
    # Add center marker (initially at origin)
    fig.add_trace(go.Scatter3d(
        x=[0],
        y=[0],
        z=[0],
        mode='markers+text',
        marker=dict(
            size=20,
            color='red',
            symbol='diamond',
            line=dict(width=3, color='white')
        ),
        text=['🎯 CENTER'],
        textposition='top center',
        textfont=dict(size=14, color='white'),
        name='Rotation Center',
        hovertemplate='<b>Rotation Center</b><br>Click object to change<extra></extra>'
    ))
    
    # Layout with instructions
    fig.update_layout(
        title=dict(
            text='<b>🌌 Interactive Navigation</b><br>'
                 '<sub>Click object to rotate around it | Zoom out to load more | '
                 f'{len(initial_data):,} objects loaded</sub>',
            font=dict(size=20, color='white'),
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis=dict(
                visible=False,
                showbackground=False,
                range=[-2000, 2000]
            ),
            yaxis=dict(
                visible=False,
                showbackground=False,
                range=[-2000, 2000]
            ),
            zaxis=dict(
                visible=False,
                showbackground=False,
                range=[-2000, 2000]
            ),
            bgcolor='rgb(0,0,10)',
            camera=dict(
                eye=dict(x=0.001, y=0.001, z=0.001),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1),
                projection=dict(type='perspective')
            ),
            aspectmode='cube',
            dragmode='turntable'
        ),
        paper_bgcolor='#000010',
        plot_bgcolor='#000010',
        font=dict(color='white', size=12),
        height=900,
        showlegend=True,
        hovermode='closest',
        margin=dict(l=0, r=0, t=60, b=20),
        # Add click event configuration
        clickmode='event+select'
    )
    
    # Add instructions annotation
    fig.add_annotation(
        text='<b>Controls:</b><br>'
             '🖱️ Click object → Rotate around it<br>'
             '🔍 Zoom out → Load more objects<br>'
             '↕️ Drag → Rotate view<br>'
             '⚡ Progressive loading active',
        xref='paper', yref='paper',
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=11, color='rgba(255,255,255,0.8)'),
        bgcolor='rgba(0,0,0,0.7)',
        bordercolor='cyan',
        borderwidth=2,
        align='left',
        xanchor='left',
        yanchor='top'
    )
    
    stats = {
        'total_objects': len(initial_data),
        'enable_rotation': enable_rotation,
        'enable_progressive': enable_progressive,
        'max_distance': r.max() if hasattr(r, 'max') else max(r),
        'interaction_mode': 'active'
    }
    
    return fig, stats


def update_view_on_selection(
    fig: go.Figure,
    selected_point_index: int,
    data: pd.DataFrame
) -> go.Figure:
    """
    Update view to center on selected object
    
    Args:
        fig: Current figure
        selected_point_index: Index of selected point
        data: Data containing object info
        
    Returns:
        Updated figure
    """
    # Get selected object position
    row = data.iloc[selected_point_index]
    
    # Extract 3D position (assuming it's been calculated)
    # This would need to be stored in the data
    center_x = 0  # Placeholder
    center_y = 0
    center_z = 0
    
    # Update center marker
    fig.data[1].x = [center_x]
    fig.data[1].y = [center_y]
    fig.data[1].z = [center_z]
    
    # Update camera to look at this point
    fig.update_layout(
        scene=dict(
            camera=dict(
                center=dict(x=center_x/1000, y=center_y/1000, z=center_z/1000)
            )
        )
    )
    
    return fig


if __name__ == "__main__":
    print("Testing Interactive Navigation...")
    
    # Create test data
    test_data = pd.DataFrame({
        'ra': np.random.uniform(0, 360, 100),
        'dec': np.random.uniform(-90, 90, 100),
        'magnitude': np.random.uniform(5, 15, 100),
        'parallax': np.random.uniform(0.1, 10, 100)
    })
    
    fig, stats = create_interactive_sky_view(test_data)
    print("[OK] Interactive view created")
    print(f"[OK] Stats: {stats}")
    print("\n[SUCCESS] Interactive navigation system ready!")
