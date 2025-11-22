#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive SSZ Viewer - Object Selection with Full Parameter Display

Click on any object to see all SSZ-computed values:
- Schwarzschild radius
- Segment density Xi(r)
- Time dilation D_SSZ(r)
- Radial stretch
- Escape velocity
- Orbital velocity
- And more!

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Constants
G = 6.67430e-11  # m^3 kg^-1 s^-2
c = 2.99792458e8  # m/s
M_sun = 1.989e30  # kg
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio


def compute_all_ssz_values(M_solar, r_m):
    """
    Compute ALL SSZ values for an object.
    
    Parameters
    ----------
    M_solar : float
        Mass in solar masses
    r_m : float
        Distance in meters
        
    Returns
    -------
    dict
        All computed SSZ parameters
    """
    M_kg = M_solar * M_sun
    
    # Schwarzschild radius
    r_s = 2 * G * M_kg / (c**2)
    
    # Dimensionless radius
    x = r_m / r_s if r_s > 0 else np.inf
    
    # SSZ segment density
    Xi = 1 - np.exp(-PHI * r_m / r_s) if r_s > 0 else 0
    
    # Time dilation (SSZ)
    D_ssz = 1 / (1 + Xi) if Xi < 1 else 0
    
    # Time dilation (GR)
    D_gr = np.sqrt(1 - r_s / r_m) if r_m > r_s else 0
    
    # Radial stretch
    R_ssz = r_m * (1 + Xi)
    
    # Velocities
    v_orbital = np.sqrt(G * M_kg / r_m) if r_m > 0 else 0
    v_escape = np.sqrt(2 * G * M_kg / r_m) if r_m > 0 else 0
    
    # SSZ-corrected velocities
    v_orbital_ssz = v_orbital * np.sqrt(1 + Xi)
    v_escape_ssz = v_escape * np.sqrt(1 + Xi)
    
    # Photon sphere
    r_ph = 1.5 * r_s
    
    # ISCO (Innermost Stable Circular Orbit)
    r_isco = 3 * r_s
    
    # Proper time ratio
    tau_ratio = D_ssz
    
    # Gravitational redshift
    z_gr = (1 / D_gr - 1) if D_gr > 0 else np.inf
    z_ssz = (1 / D_ssz - 1) if D_ssz > 0 else np.inf
    
    return {
        # Basic parameters
        'M_solar': M_solar,
        'M_kg': M_kg,
        'r_m': r_m,
        'r_au': r_m / 1.496e11,  # AU
        'r_ly': r_m / 9.461e15,  # light-years
        
        # Schwarzschild parameters
        'r_s': r_s,
        'x': x,
        'r_ph': r_ph,
        'r_isco': r_isco,
        
        # SSZ parameters
        'Xi': Xi,
        'D_ssz': D_ssz,
        'D_gr': D_gr,
        'R_ssz': R_ssz,
        'stretch_factor': (1 + Xi),
        
        # Velocities
        'v_orbital': v_orbital,
        'v_escape': v_escape,
        'v_orbital_ssz': v_orbital_ssz,
        'v_escape_ssz': v_escape_ssz,
        'v_orbital_c': v_orbital / c,
        'v_escape_c': v_escape / c,
        
        # Time and redshift
        'tau_ratio': tau_ratio,
        'z_gr': z_gr,
        'z_ssz': z_ssz,
        
        # Derived
        'gravity_m_s2': G * M_kg / (r_m**2),
        'potential': -G * M_kg / r_m,
    }


def format_value(value, unit='', decimals=3):
    """Format a value with scientific notation if needed."""
    if abs(value) < 0.001 or abs(value) > 1000:
        return f"{value:.{decimals}e} {unit}"
    else:
        return f"{value:.{decimals}f} {unit}"


def create_info_text(params):
    """Create formatted info text for an object."""
    
    text = "<b>OBJECT PARAMETERS</b><br><br>"
    
    # Basic info
    text += "<b>Basic Properties:</b><br>"
    text += f"Mass: {format_value(params['M_solar'], 'M☉')}<br>"
    text += f"Distance: {format_value(params['r_m'], 'm')}<br>"
    text += f"Distance: {format_value(params['r_au'], 'AU')}<br>"
    text += "<br>"
    
    # Schwarzschild
    text += "<b>Schwarzschild Radius:</b><br>"
    text += f"r_s: {format_value(params['r_s'], 'm')}<br>"
    text += f"x = r/r_s: {format_value(params['x'], '', 2)}<br>"
    text += f"Photon sphere: {format_value(params['r_ph'], 'm')}<br>"
    text += f"ISCO: {format_value(params['r_isco'], 'm')}<br>"
    text += "<br>"
    
    # SSZ parameters
    text += "<b>SSZ Parameters:</b><br>"
    text += f"Ξ(r): {format_value(params['Xi'], '', 6)}<br>"
    text += f"D_SSZ(r): {format_value(params['D_ssz'], '', 6)}<br>"
    text += f"D_GR(r): {format_value(params['D_gr'], '', 6)}<br>"
    text += f"Stretch: {format_value(params['stretch_factor'], 'x', 6)}<br>"
    text += f"R_SSZ: {format_value(params['R_ssz'], 'm')}<br>"
    text += "<br>"
    
    # Velocities
    text += "<b>Velocities:</b><br>"
    text += f"v_orb: {format_value(params['v_orbital'], 'm/s')}<br>"
    text += f"v_orb (SSZ): {format_value(params['v_orbital_ssz'], 'm/s')}<br>"
    text += f"v_orb/c: {format_value(params['v_orbital_c'], '', 4)}<br>"
    text += f"v_esc: {format_value(params['v_escape'], 'm/s')}<br>"
    text += f"v_esc (SSZ): {format_value(params['v_escape_ssz'], 'm/s')}<br>"
    text += f"v_esc/c: {format_value(params['v_escape_c'], '', 4)}<br>"
    text += "<br>"
    
    # Time & Redshift
    text += "<b>Time Dilation & Redshift:</b><br>"
    text += f"τ/t: {format_value(params['tau_ratio'], '', 6)}<br>"
    text += f"z_GR: {format_value(params['z_gr'], '', 6)}<br>"
    text += f"z_SSZ: {format_value(params['z_ssz'], '', 6)}<br>"
    text += "<br>"
    
    # Gravity
    text += "<b>Gravitational Field:</b><br>"
    text += f"g: {format_value(params['gravity_m_s2'], 'm/s²')}<br>"
    text += f"Φ: {format_value(params['potential'], 'J/kg')}<br>"
    
    return text


def main():
    """Create interactive SSZ viewer with object selection."""
    
    print("="*70)
    print("INTERACTIVE SSZ VIEWER - Object Selection")
    print("="*70)
    print()
    print("Loading data...")
    
    # Get PRIMARY data
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        from ssz_starmaps.catalogs import CatalogManager
        manager = CatalogManager()
        eso_data = manager.fetch_primary('sgr_a_stars', use_included=True)
        print(f"Loaded {len(eso_data)} ESO observations")
    except Exception as e:
        print(f"Using sample data (ESO not available: {e})")
        # Sample data if ESO not available
        eso_data = {
            'case': ['Sun', 'Earth', 'Jupiter', 'Black Hole'],
            'M_solar': [1.0, 3e-6, 9.5e-4, 4e6],
            'r_emit_m': [1.496e11, 1.496e11, 7.78e11, 2e16],
            'category': ['Star', 'Planet', 'Planet', 'SMBH']
        }
        import pandas as pd
        eso_data = pd.DataFrame(eso_data)
    
    # Compute all SSZ values
    print("Computing SSZ parameters...")
    objects = []
    
    for idx, row in eso_data.iterrows():
        case = row.get('case', f'Object_{idx}')
        M_solar = row.get('M_solar', 1.0)
        r_m = row.get('r_emit_m', 1.496e11)
        
        params = compute_all_ssz_values(M_solar, r_m)
        params['name'] = case
        params['category'] = row.get('category', 'Unknown')
        
        objects.append(params)
    
    print(f"Computed parameters for {len(objects)} objects")
    print()
    
    # Create interactive plot
    print("Creating interactive visualization...")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Mass vs Distance',
            'SSZ Segment Density Ξ(r)',
            'Time Dilation D(r)',
            'Velocity Ratios'
        ),
        specs=[
            [{'type': 'scatter'}, {'type': 'scatter'}],
            [{'type': 'scatter'}, {'type': 'scatter'}]
        ]
    )
    
    # Extract data
    names = [obj['name'] for obj in objects]
    masses = [obj['M_solar'] for obj in objects]
    distances = [obj['r_m'] for obj in objects]
    xi_values = [obj['Xi'] for obj in objects]
    d_ssz_values = [obj['D_ssz'] for obj in objects]
    d_gr_values = [obj['D_gr'] for obj in objects]
    v_orb_c = [obj['v_orbital_c'] for obj in objects]
    v_esc_c = [obj['v_escape_c'] for obj in objects]
    
    # Create hover texts with ALL parameters
    hover_texts = [create_info_text(obj) for obj in objects]
    
    # Plot 1: Mass vs Distance
    fig.add_trace(
        go.Scatter(
            x=distances,
            y=masses,
            mode='markers',
            marker=dict(
                size=10,
                color=xi_values,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Ξ(r)", x=0.46)
            ),
            text=names,
            hovertext=hover_texts,
            hoverinfo='text',
            name='Objects'
        ),
        row=1, col=1
    )
    
    # Plot 2: Segment Density
    fig.add_trace(
        go.Scatter(
            x=distances,
            y=xi_values,
            mode='markers',
            marker=dict(size=10, color='blue'),
            text=names,
            hovertext=hover_texts,
            hoverinfo='text',
            name='Ξ(r)'
        ),
        row=1, col=2
    )
    
    # Plot 3: Time Dilation
    fig.add_trace(
        go.Scatter(
            x=distances,
            y=d_ssz_values,
            mode='markers',
            marker=dict(size=10, color='red'),
            text=names,
            hovertext=hover_texts,
            hoverinfo='text',
            name='D_SSZ'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=distances,
            y=d_gr_values,
            mode='markers',
            marker=dict(size=10, color='orange', symbol='diamond'),
            text=names,
            hovertext=hover_texts,
            hoverinfo='text',
            name='D_GR'
        ),
        row=2, col=1
    )
    
    # Plot 4: Velocities
    fig.add_trace(
        go.Scatter(
            x=v_orb_c,
            y=v_esc_c,
            mode='markers',
            marker=dict(size=10, color='green'),
            text=names,
            hovertext=hover_texts,
            hoverinfo='text',
            name='Velocities'
        ),
        row=2, col=2
    )
    
    # Update axes
    fig.update_xaxes(title_text="Distance [m]", type="log", row=1, col=1)
    fig.update_yaxes(title_text="Mass [M☉]", type="log", row=1, col=1)
    
    fig.update_xaxes(title_text="Distance [m]", type="log", row=1, col=2)
    fig.update_yaxes(title_text="Ξ(r)", row=1, col=2)
    
    fig.update_xaxes(title_text="Distance [m]", type="log", row=2, col=1)
    fig.update_yaxes(title_text="D(r)", row=2, col=1)
    
    fig.update_xaxes(title_text="v_orb / c", row=2, col=2)
    fig.update_yaxes(title_text="v_esc / c", row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Interactive SSZ Viewer - Click on any point to see all parameters',
            'x': 0.5,
            'xanchor': 'center'
        },
        height=900,
        showlegend=True,
        hovermode='closest'
    )
    
    # Save and show
    output_file = 'interactive_ssz_viewer.html'
    fig.write_html(output_file)
    
    print(f"[OK] Interactive viewer saved to: {output_file}")
    print()
    print("="*70)
    print("USAGE:")
    print("="*70)
    print("1. Open the HTML file in your browser")
    print("2. Hover over any point to see ALL SSZ parameters")
    print("3. Click and drag to pan")
    print("4. Scroll to zoom")
    print("5. Double-click to reset view")
    print()
    print("The info box shows:")
    print("  - Basic properties (mass, distance)")
    print("  - Schwarzschild radius & critical radii")
    print("  - SSZ parameters (Xi, D_SSZ, stretch)")
    print("  - Velocities (orbital, escape, SSZ-corrected)")
    print("  - Time dilation & redshift")
    print("  - Gravitational field strength")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
