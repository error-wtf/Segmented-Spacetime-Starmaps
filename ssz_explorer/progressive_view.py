#!/usr/bin/env python3
"""
Progressive View with Manual Load More
Since Plotly in Gradio can't detect zoom, use manual loading
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Tuple, Dict


class ProgressiveViewState:
    """Track state of progressive loading"""
    
    def __init__(self):
        self.loaded_distances = []  # List of (min, max) ranges loaded
        self.current_max_distance = 1000.0  # pc
        self.all_data = None
        self.loaded_objects = pd.DataFrame()
        
    def get_next_shell(self, shell_size: float = 2000.0) -> Tuple[float, float]:
        """Get next distance shell to load"""
        min_dist = self.current_max_distance
        max_dist = min_dist + shell_size
        self.current_max_distance = max_dist
        return min_dist, max_dist
    
    def add_loaded_shell(self, min_dist: float, max_dist: float):
        """Record loaded shell"""
        self.loaded_distances.append((min_dist, max_dist))


# Global state
_view_state = ProgressiveViewState()


def reset_progressive_view():
    """Reset to initial state"""
    global _view_state
    _view_state = ProgressiveViewState()


def create_progressive_3d_view(
    all_data: pd.DataFrame,
    load_more: bool = False,
    shell_size: float = 2000.0
) -> Tuple[go.Figure, Dict]:
    """
    Create 3D view with progressive loading
    
    Args:
        all_data: All available data
        load_more: If True, load next shell
        shell_size: Size of each shell in parsecs
        
    Returns:
        Figure and info dict
    """
    global _view_state
    
    # Store all data
    if _view_state.all_data is None:
        _view_state.all_data = all_data
    
    # Initial load or load more
    if len(_view_state.loaded_objects) == 0:
        # Initial: Load first 1000 pc
        min_dist = 0
        max_dist = 1000.0
        _view_state.current_max_distance = max_dist
    elif load_more:
        # Load next shell
        min_dist, max_dist = _view_state.get_next_shell(shell_size)
    else:
        # Just redraw current
        return _create_figure_from_loaded(_view_state.loaded_objects)
    
    # Get objects in distance range
    new_objects = _get_objects_in_shell(all_data, min_dist, max_dist)
    
    if len(new_objects) > 0:
        # Add to loaded objects
        _view_state.loaded_objects = pd.concat([_view_state.loaded_objects, new_objects], ignore_index=True)
        _view_state.add_loaded_shell(min_dist, max_dist)
    
    # Create figure
    return _create_figure_from_loaded(_view_state.loaded_objects)


def _get_objects_in_shell(data: pd.DataFrame, min_dist: float, max_dist: float) -> pd.DataFrame:
    """Get objects in distance shell"""
    if 'parallax' not in data.columns:
        # No distance info, return sample
        return data.sample(min(1000, len(data)))
    
    # Calculate distances
    parallax = data['parallax'].copy()
    parallax = parallax[parallax > 0]
    
    if len(parallax) == 0:
        return pd.DataFrame()
    
    distances_pc = 1000.0 / parallax
    
    # Filter by shell
    mask = (distances_pc >= min_dist) & (distances_pc <= max_dist)
    candidates = data[mask]
    
    # Sample if too many
    if len(candidates) > 2000:
        return candidates.sample(2000)
    
    return candidates


def _create_figure_from_loaded(data: pd.DataFrame) -> Tuple[go.Figure, Dict]:
    """Create 3D figure from loaded objects"""
    
    if len(data) == 0:
        # Empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No objects loaded yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color='white')
        )
        fig.update_layout(
            paper_bgcolor='#000010',
            height=800
        )
        info = {'total_loaded': 0, 'max_distance': 0}
        return fig, info
    
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
    
    # Sizes by magnitude
    if 'magnitude' in data.columns:
        mag = data['magnitude'].clip(-2, 15)
        sizes = 20 - mag * 1.5
        sizes = sizes.clip(2, 20)
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
        text += f"<b>RA:</b> {row[ra_col]:.2f}°<br>"
        text += f"<b>Dec:</b> {row[dec_col]:.2f}°<br>"
        
        if 'magnitude' in data.columns:
            text += f"<b>Mag:</b> {row['magnitude']:.2f}<br>"
        
        if 'parallax' in data.columns and row['parallax'] > 0:
            dist = 1000.0 / row['parallax']
            text += f"<b>Distance:</b> {dist:.1f} pc<br>"
        
        hover_texts.append(text)
    
    # Create figure
    fig = go.Figure(data=[go.Scatter3d(
        x=x.tolist(),
        y=y.tolist(),
        z=z.tolist(),
        mode='markers',
        marker=dict(
            size=sizes.tolist(),
            color=colors,
            showscale=False,
            opacity=0.8,
            line=dict(width=1, color='rgba(255,255,255,0.2)')
        ),
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>',
        name='Objects'
    )])
    
    # Calculate max distance
    max_dist = r.max() if hasattr(r, 'max') else max(r)
    
    # Layout
    scene_range = max(2000, max_dist * 1.2)
    
    fig.update_layout(
        title=dict(
            text=f'<b>🌌 Progressive View</b><br>'
                 f'<sub>{len(data):,} objects loaded | Max distance: {max_dist:.0f} pc | '
                 f'Click "Load More" to expand!</sub>',
            font=dict(size=20, color='white'),
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis=dict(
                visible=False,
                showbackground=False,
                range=[-scene_range, scene_range]
            ),
            yaxis=dict(
                visible=False,
                showbackground=False,
                range=[-scene_range, scene_range]
            ),
            zaxis=dict(
                visible=False,
                showbackground=False,
                range=[-scene_range, scene_range]
            ),
            bgcolor='rgb(0,0,10)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode='cube'
        ),
        paper_bgcolor='#000010',
        plot_bgcolor='#000010',
        font=dict(color='white', size=12),
        height=900,
        showlegend=False,
        hovermode='closest',
        margin=dict(l=0, r=0, t=60, b=0)
    )
    
    info = {
        'total_loaded': len(data),
        'max_distance': max_dist,
        'shells_loaded': len(_view_state.loaded_distances),
        'current_range': f"0 - {_view_state.current_max_distance:.0f} pc"
    }
    
    return fig, info


if __name__ == "__main__":
    print("Testing Progressive View...")
    
    # Test data
    test_data = pd.DataFrame({
        'ra': np.random.uniform(0, 360, 5000),
        'dec': np.random.uniform(-90, 90, 5000),
        'parallax': np.random.uniform(0.1, 10, 5000),
        'magnitude': np.random.uniform(5, 15, 5000)
    })
    
    # Initial load
    reset_progressive_view()
    fig, info = create_progressive_3d_view(test_data, load_more=False)
    print(f"[OK] Initial load: {info['total_loaded']} objects")
    
    # Load more
    fig, info = create_progressive_3d_view(test_data, load_more=True)
    print(f"[OK] After load more: {info['total_loaded']} objects")
    print(f"[OK] Range: {info['current_range']}")
    
    print("\n[SUCCESS] Progressive view ready!")
