#!/usr/bin/env python3
"""
Object Selector for 3D View
Allows selecting objects and rotating camera around them
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Tuple, Dict, Optional


def create_object_centered_view(
    data: pd.DataFrame,
    selected_object_index: Optional[int] = None,
    camera_distance: float = 500.0,
    camera_angle_h: float = 0.0,
    camera_angle_v: float = 45.0
) -> Tuple[go.Figure, Dict]:
    """
    Create 3D view centered on selected object
    
    Args:
        data: DataFrame with objects
        selected_object_index: Index of selected object (None = center at origin)
        camera_distance: Distance from selected object (pc)
        camera_angle_h: Horizontal camera angle (degrees)
        camera_angle_v: Vertical camera angle (degrees)
        
    Returns:
        Figure and info dict
    """
    
    # Get coordinates
    ra_col = 'ra' if 'ra' in data.columns else [c for c in data.columns if 'ra' in c.lower()][0]
    dec_col = 'dec' if 'dec' in data.columns else [c for c in data.columns if 'dec' in c.lower()][0]
    
    # Convert to 3D
    ra_rad = np.deg2rad(data[ra_col])
    dec_rad = np.deg2rad(data[dec_col])
    
    # Distance
    if 'parallax' in data.columns:
        r = 1000.0 / data['parallax'].clip(0.1, 1000)
    else:
        r = np.ones(len(data)) * 1000
    
    x = r * np.cos(dec_rad) * np.cos(ra_rad)
    y = r * np.cos(dec_rad) * np.sin(ra_rad)
    z = r * np.sin(dec_rad)
    
    # Determine center
    if selected_object_index is not None and selected_object_index < len(data):
        center_x = x.iloc[selected_object_index]
        center_y = y.iloc[selected_object_index]
        center_z = z.iloc[selected_object_index]
        selected_name = data.iloc[selected_object_index].get('name', f'Object {selected_object_index}')
    else:
        center_x = 0
        center_y = 0
        center_z = 0
        selected_name = "Origin"
    
    # Sizes by magnitude
    if 'magnitude' in data.columns:
        mag = data['magnitude'].clip(-2, 15)
        sizes = 20 - mag * 1.5
        sizes = sizes.clip(3, 25)
    else:
        sizes = np.ones(len(data)) * 5
    
    # Colors by OBJECT TYPE
    colors = []
    for idx, row in data.iterrows():
        if 'type' in data.columns:
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
    
    # Hover texts
    hover_texts = []
    for idx, row in data.iterrows():
        name = row.get('name', f'Object {idx}')
        if 'source_id' in data.columns:
            name = f"GAIA {row['source_id']}"
        
        text = f"<b>⭐ {name}</b><br>"
        text += f"<b>Index:</b> {idx}<br>"
        text += f"<b>RA:</b> {row[ra_col]:.2f}°<br>"
        text += f"<b>Dec:</b> {row[dec_col]:.2f}°<br>"
        
        if 'magnitude' in data.columns:
            text += f"<b>Mag:</b> {row['magnitude']:.2f}<br>"
        
        hover_texts.append(text)
    
    # Create figure
    fig = go.Figure()
    
    # Add all objects
    fig.add_trace(go.Scatter3d(
        x=x.tolist(),
        y=y.tolist(),
        z=z.tolist(),
        mode='markers',
        marker=dict(
            size=sizes.tolist(),
            color=colors,  # Direct colors by type
            showscale=False,
            opacity=0.8,
            line=dict(width=1, color='rgba(255,255,255,0.2)')
        ),
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>',
        name='Objects'
    ))
    
    # Add CENTER marker (selected object or origin)
    fig.add_trace(go.Scatter3d(
        x=[center_x],
        y=[center_y],
        z=[center_z],
        mode='markers+text',
        marker=dict(
            size=25,
            color='red',
            symbol='diamond',
            line=dict(width=3, color='yellow')
        ),
        text=[f'🎯 {selected_name}'],
        textposition='top center',
        textfont=dict(size=16, color='yellow'),
        name='Selected',
        hovertemplate=f'<b>ROTATION CENTER</b><br>{selected_name}<extra></extra>'
    ))
    
    # Camera position relative to center
    cam_h_rad = np.deg2rad(camera_angle_h)
    cam_v_rad = np.deg2rad(camera_angle_v)
    
    # Camera eye position
    eye_x = center_x + camera_distance * np.cos(cam_v_rad) * np.cos(cam_h_rad)
    eye_y = center_y + camera_distance * np.cos(cam_v_rad) * np.sin(cam_h_rad)
    eye_z = center_z + camera_distance * np.sin(cam_v_rad)
    
    # Normalize for Plotly (relative positions)
    scene_range = max(2000, camera_distance * 3)
    
    fig.update_layout(
        title=dict(
            text=f'<b>🎯 Object-Centered View</b><br>'
                 f'<sub>Center: {selected_name} | '
                 f'Camera: {camera_distance:.0f} pc away | '
                 f'Angles: H={camera_angle_h:.0f}° V={camera_angle_v:.0f}°</sub>',
            font=dict(size=20, color='white'),
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis=dict(
                visible=False,
                showbackground=False,
                range=[center_x - scene_range, center_x + scene_range]
            ),
            yaxis=dict(
                visible=False,
                showbackground=False,
                range=[center_y - scene_range, center_y + scene_range]
            ),
            zaxis=dict(
                visible=False,
                showbackground=False,
                range=[center_z - scene_range, center_z + scene_range]
            ),
            bgcolor='rgb(0,0,10)',
            camera=dict(
                eye=dict(
                    x=(eye_x - center_x) / scene_range * 2,
                    y=(eye_y - center_y) / scene_range * 2,
                    z=(eye_z - center_z) / scene_range * 2
                ),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode='cube'
        ),
        paper_bgcolor='#000010',
        plot_bgcolor='#000010',
        font=dict(color='white', size=12),
        height=900,
        showlegend=True,
        hovermode='closest',
        margin=dict(l=0, r=0, t=60, b=0)
    )
    
    info = {
        'center_object': selected_name,
        'center_position': (center_x, center_y, center_z),
        'camera_distance': camera_distance,
        'camera_angles': (camera_angle_h, camera_angle_v),
        'total_objects': len(data)
    }
    
    return fig, info


def get_object_list(data: pd.DataFrame, max_items: int = 100) -> list:
    """
    Get list of objects for selection dropdown
    
    Args:
        data: DataFrame with objects
        max_items: Maximum items in list
        
    Returns:
        List of (index, name) tuples
    """
    objects = []
    
    # Limit to max_items brightest
    if len(data) > max_items and 'magnitude' in data.columns:
        data_subset = data.nsmallest(max_items, 'magnitude')
    else:
        data_subset = data.head(max_items)
    
    for idx, row in data_subset.iterrows():
        # Try to get name
        name = None
        for col in ['name', 'MAIN_ID', 'designation']:
            if col in data.columns:
                name = row[col]
                break
        
        if name is None:
            if 'source_id' in data.columns:
                name = f"GAIA {row['source_id']}"
            else:
                name = f"Object {idx}"
        
        # Add magnitude if available
        if 'magnitude' in data.columns:
            name = f"{name} (mag {row['magnitude']:.1f})"
        
        objects.append((int(idx), str(name)))
    
    return objects


if __name__ == "__main__":
    print("Testing Object Selector...")
    
    # Create test data
    test_data = pd.DataFrame({
        'ra': np.random.uniform(0, 360, 50),
        'dec': np.random.uniform(-90, 90, 50),
        'magnitude': np.random.uniform(5, 15, 50),
        'parallax': np.random.uniform(1, 10, 50),
        'name': [f'Star {i}' for i in range(50)]
    })
    
    # Test view
    fig, info = create_object_centered_view(test_data, selected_object_index=5)
    print(f"[OK] Created view centered on: {info['center_object']}")
    
    # Test object list
    obj_list = get_object_list(test_data, max_items=20)
    print(f"[OK] Object list: {len(obj_list)} items")
    print(f"[OK] First 3: {obj_list[:3]}")
    
    print("\n[SUCCESS] Object selector ready!")
