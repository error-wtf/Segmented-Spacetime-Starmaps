#!/usr/bin/env python3
"""
Combined Physics View - Object Selection + SSZ Physics
Show SSZ parameters for SELECTED objects
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Tuple, Dict, Optional

# Import SSZ functions
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ssz_starmaps import Xi, D_SSZ, D_GR, PHI, schwarzschild_radius, radial_stretch
except ImportError:
    PHI = (1.0 + np.sqrt(5.0)) / 2.0
    
    def schwarzschild_radius(mass, G=6.67430e-11, c=2.99792458e8):
        return 2.0 * G * mass / (c * c)
    
    def Xi(r, r_s):
        return 1.0 - np.exp(-PHI * r_s / r)
    
    def D_SSZ(r, r_s):
        xi = Xi(r, r_s)
        return 1.0 / (1.0 + xi)
    
    def D_GR(r, r_s):
        return np.sqrt(np.clip(1.0 - r_s / r, 0, None))
    
    def radial_stretch(r, r_s):
        return 1.0 + Xi(r, r_s)


def create_combined_physics_view(
    all_objects: pd.DataFrame,
    selected_object_index: Optional[int] = None
) -> Tuple[go.Figure, Dict]:
    """
    Create combined view showing SSZ physics with selected object highlighted
    
    Args:
        all_objects: DataFrame with all objects
        selected_object_index: Index of selected object (or None)
        
    Returns:
        Figure and info dict
    """
    
    # Solar mass for reference
    M_SUN = 1.98847e30  # kg
    r_s = schwarzschild_radius(M_SUN)
    
    # Theoretical curve
    r_range = np.linspace(0.1 * r_s, 20 * r_s, 1000)
    r_ratio = r_range / r_s
    
    xi_curve = Xi(r_range, r_s)
    d_ssz_curve = D_SSZ(r_range, r_s)
    d_gr_curve = D_GR(r_range, r_s)
    stretch_curve = radial_stretch(r_range, r_s)
    
    # Get selected object data
    selected_name = "None"
    selected_xi = None
    selected_d_ssz = None
    selected_stretch = None
    selected_r_ratio = None
    
    if selected_object_index is not None and selected_object_index < len(all_objects):
        obj = all_objects.iloc[selected_object_index]
        
        # Get name
        selected_name = obj.get('name', f'Object {selected_object_index}')
        if 'source_id' in all_objects.columns:
            selected_name = f"GAIA {obj['source_id']}"
        
        # Get distance
        if 'parallax' in all_objects.columns and obj['parallax'] > 0:
            dist_pc = 1000.0 / obj['parallax']
            dist_m = dist_pc * 3.0857e16
            
            # Calculate SSZ parameters
            selected_r_ratio = dist_m / r_s
            selected_xi = Xi(dist_m, r_s)
            selected_d_ssz = D_SSZ(dist_m, r_s)
            selected_stretch = radial_stretch(dist_m, r_s)
    
    # Create 2x2 subplot
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Ξ(r) - Segment Density',
            'D(r) - Time Dilation',
            '1+Ξ(r) - Radial Stretch',
            'Object SSZ Parameters'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "table"}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    # Plot 1: Xi(r) - Segment Density
    # Theoretical curve
    fig.add_trace(
        go.Scatter(
            x=r_ratio, y=xi_curve,
            mode='lines',
            name='Theory',
            line=dict(color='orange', width=2),
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Selected object
    if selected_xi is not None:
        fig.add_trace(
            go.Scatter(
                x=[selected_r_ratio], y=[selected_xi],
                mode='markers+text',
                name='Selected',
                marker=dict(size=20, color='red', symbol='star',
                           line=dict(width=3, color='yellow')),
                text=[selected_name],
                textposition='top center',
                textfont=dict(size=12, color='white'),
                showlegend=False,
                hovertemplate=f'<b>{selected_name}</b><br>' +
                             f'r/r_s: {selected_r_ratio:.2f}<br>' +
                             f'Ξ(r): {selected_xi:.4f}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Plot 2: Time Dilation
    # SSZ
    fig.add_trace(
        go.Scatter(
            x=r_ratio, y=d_ssz_curve,
            mode='lines',
            name='SSZ',
            line=dict(color='cyan', width=2),
            showlegend=True
        ),
        row=1, col=2
    )
    
    # GR
    fig.add_trace(
        go.Scatter(
            x=r_ratio, y=d_gr_curve,
            mode='lines',
            name='GR',
            line=dict(color='red', width=2, dash='dash'),
            showlegend=True
        ),
        row=1, col=2
    )
    
    # Selected object
    if selected_d_ssz is not None:
        fig.add_trace(
            go.Scatter(
                x=[selected_r_ratio], y=[selected_d_ssz],
                mode='markers+text',
                name='Selected',
                marker=dict(size=20, color='red', symbol='star',
                           line=dict(width=3, color='yellow')),
                text=[selected_name],
                textposition='top right',
                textfont=dict(size=12, color='white'),
                showlegend=False,
                hovertemplate=f'<b>{selected_name}</b><br>' +
                             f'r/r_s: {selected_r_ratio:.2f}<br>' +
                             f'D_SSZ: {selected_d_ssz:.4f}<extra></extra>'
            ),
            row=1, col=2
        )
    
    # Plot 3: Radial Stretch
    fig.add_trace(
        go.Scatter(
            x=r_ratio, y=stretch_curve,
            mode='lines',
            name='Theory',
            line=dict(color='green', width=2),
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Selected object
    if selected_stretch is not None:
        fig.add_trace(
            go.Scatter(
                x=[selected_r_ratio], y=[selected_stretch],
                mode='markers+text',
                name='Selected',
                marker=dict(size=20, color='red', symbol='star',
                           line=dict(width=3, color='yellow')),
                text=[selected_name],
                textposition='top center',
                textfont=dict(size=12, color='white'),
                showlegend=False,
                hovertemplate=f'<b>{selected_name}</b><br>' +
                             f'r/r_s: {selected_r_ratio:.2f}<br>' +
                             f'Stretch: {selected_stretch:.4f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    # Plot 4: Table with SSZ parameters
    if selected_xi is not None:
        # Calculate additional parameters
        d_gr_obj = D_GR(selected_r_ratio * r_s, r_s)
        deviation = abs(selected_d_ssz - d_gr_obj) / d_gr_obj * 100 if d_gr_obj > 0 else 0
        
        # Determine domain
        r_star = 1.386562
        domain = "g₂ (Strong)" if selected_r_ratio < r_star else "g₁ (Weak)"
        
        table_data = [
            ['Parameter', 'Value'],
            ['Object', selected_name],
            ['r/r_s', f'{selected_r_ratio:.2f}'],
            ['Domain', domain],
            ['Ξ(r)', f'{selected_xi:.6f}'],
            ['D_SSZ(r)', f'{selected_d_ssz:.6f}'],
            ['D_GR(r)', f'{d_gr_obj:.6f}'],
            ['Deviation', f'{deviation:.2f}%'],
            ['Stretch', f'{selected_stretch:.6f}'],
            ['Distance', f'{selected_r_ratio * r_s / 3.0857e16:.1f} pc']
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['<b>Parameter</b>', '<b>Value</b>'],
                    fill_color='darkblue',
                    font=dict(color='white', size=14),
                    align='left'
                ),
                cells=dict(
                    values=list(zip(*table_data[1:])),
                    fill_color=['lightblue', 'white'],
                    font=dict(color='black', size=12),
                    align='left',
                    height=30
                )
            ),
            row=2, col=2
        )
    else:
        # Empty state
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['<b>Info</b>'],
                    fill_color='darkgray',
                    font=dict(color='white', size=14)
                ),
                cells=dict(
                    values=[['Select an object to see SSZ parameters']],
                    fill_color='lightgray',
                    font=dict(color='black', size=12),
                    height=30
                )
            ),
            row=2, col=2
        )
    
    # Update axes
    fig.update_xaxes(title_text="r / r_s", type="log", row=1, col=1)
    fig.update_xaxes(title_text="r / r_s", type="log", row=1, col=2)
    fig.update_xaxes(title_text="r / r_s", type="log", row=2, col=1)
    
    fig.update_yaxes(title_text="Ξ(r)", row=1, col=1)
    fig.update_yaxes(title_text="D(r)", row=1, col=2)
    fig.update_yaxes(title_text="1 + Ξ(r)", row=2, col=1)
    
    # Layout
    title_text = '<b>🔬 SSZ Physics Analysis</b><br>'
    if selected_name != "None":
        title_text += f'<sub>Selected: {selected_name}</sub>'
    else:
        title_text += '<sub>Select an object to see its SSZ parameters</sub>'
    
    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='white')
        ),
        plot_bgcolor='#0a0a1f',
        paper_bgcolor='#000010',
        font=dict(color='white', size=10),
        height=900,
        showlegend=True,
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='white',
            borderwidth=1
        )
    )
    
    info = {
        'selected_object': selected_name,
        'has_data': selected_xi is not None,
        'r_ratio': selected_r_ratio,
        'xi': selected_xi,
        'd_ssz': selected_d_ssz,
        'stretch': selected_stretch
    }
    
    return fig, info


if __name__ == "__main__":
    print("Testing Combined Physics View...")
    
    # Test data
    test_data = pd.DataFrame({
        'ra': np.random.uniform(0, 360, 50),
        'dec': np.random.uniform(-90, 90, 50),
        'parallax': np.random.uniform(1, 10, 50),
        'name': [f'Star {i}' for i in range(50)]
    })
    
    fig, info = create_combined_physics_view(test_data, selected_object_index=5)
    print(f"[OK] Created view for: {info['selected_object']}")
    print(f"[OK] Has data: {info['has_data']}")
    if info['has_data']:
        print(f"[OK] Xi(r) = {info['xi']:.4f}")
        print(f"[OK] D_SSZ(r) = {info['d_ssz']:.4f}")
    
    print("\n[SUCCESS] Combined physics view ready!")
