#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Physics Plots - WISSENSCHAFTLICH KORREKT
=============================================
Basierend auf korrekter SSZ Mathematik aus PAPER-RESTORED

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================
G = 6.67430e-11          # Gravitational constant [m³ kg⁻¹ s⁻²]
C = 2.99792458e8         # Speed of light [m/s]
M_SUN = 1.98847e30       # Solar mass [kg]
PHI = (1 + np.sqrt(5))/2 # Golden ratio

# SSZ Parameters (Standard)
ALPHA = 0.12
R_C = 1.9

# ============================================================================
# SSZ CORE FUNCTIONS (KORREKT!)
# ============================================================================

def r_schwarzschild(M):
    """Schwarzschild radius"""
    return 2*G*M/(C**2)

def gamma_seg(r, r_s, alpha=ALPHA, r_c=R_C):
    """Segmentation field: γ(r) = 1 - α*exp[-(r/r_c)²]"""
    return 1 - alpha * np.exp(-(r/(r_c*r_s))**2)

def Xi(r, r_s, alpha=ALPHA, r_c=R_C):
    """Segmentation Xi(r) = 1 - γ(r)"""
    return 1 - gamma_seg(r, r_s, alpha, r_c)

def D_SSZ(r, r_s, alpha=ALPHA, r_c=R_C):
    """D(r) = 1 / (1 + Xi(r)) - Time dilation factor"""
    return 1 / (1 + Xi(r, r_s, alpha, r_c))

def A_SSZ(r, M, alpha=ALPHA, r_c=R_C):
    """SSZ metric: A(r) = D(r) * (1 - r_s/r)"""
    r_s = r_schwarzschild(M)
    return D_SSZ(r, r_s, alpha, r_c) * (1 - r_s/r)

def A_GR(r, M):
    """GR Schwarzschild metric: A(r) = 1 - r_s/r"""
    r_s = r_schwarzschild(M)
    return 1 - r_s/r

def proper_time_factor(r, M, alpha=ALPHA, r_c=R_C):
    """dτ/dt = √|A(r)| - Proper time factor"""
    A = A_SSZ(r, M, alpha, r_c)
    return np.sqrt(np.abs(A))


def create_g1_g2_domain_plot(objects_data=None):
    """
    Visualize g1 and g2 domains with REAL OBJECTS from maps!
    
    g2: Inner domain - strongly segmented
    g1: Outer domain - weakly segmented
    
    Args:
        objects_data: DataFrame with objects from maps (optional)
    """
    # Solar mass
    M_SUN = 1.98847e30  # kg
    r_s = schwarzschild_radius(M_SUN)
    
    # Radial range: 0.1 r_s to 20 r_s
    r_range = np.linspace(0.1 * r_s, 20 * r_s, 1000)
    r_ratio = r_range / r_s
    
    # Calculate Xi(r)
    xi_values = Xi(r_range, r_s)
    
    # Define domain boundaries
    # r* = universal transition radius
    r_star = 1.386562 * r_s  # Where D_SSZ = D_GR
    
    # g2 domain: r < r* (strong segmentation)
    # g1 domain: r > r* (weak segmentation)
    
    fig = go.Figure()
    
    # Plot Xi(r) with domain coloring
    g2_mask = r_ratio < 1.3866
    g1_mask = r_ratio >= 1.3866
    
    # g2 domain (red/orange)
    fig.add_trace(go.Scatter(
        x=r_ratio[g2_mask],
        y=xi_values[g2_mask],
        mode='lines',
        name='g₂ (Inner - Strong Segmentation)',
        line=dict(color='orange', width=3),
        fill='tozeroy',
        fillcolor='rgba(255,165,0,0.2)',
        hovertemplate='<b>g₂ Domain</b><br>' +
                      'r/r_s: %{x:.3f}<br>' +
                      'Ξ(r): %{y:.4f}<br>' +
                      '<extra></extra>'
    ))
    
    # g1 domain (blue/cyan)
    fig.add_trace(go.Scatter(
        x=r_ratio[g1_mask],
        y=xi_values[g1_mask],
        mode='lines',
        name='g₁ (Outer - Weak Segmentation)',
        line=dict(color='cyan', width=3),
        fill='tozeroy',
        fillcolor='rgba(0,255,255,0.1)',
        hovertemplate='<b>g₁ Domain</b><br>' +
                      'r/r_s: %{x:.3f}<br>' +
                      'Ξ(r): %{y:.4f}<br>' +
                      '<extra></extra>'
    ))
    
    # Mark transition point r*
    xi_star = Xi(r_star, r_s)
    fig.add_trace(go.Scatter(
        x=[r_star/r_s],
        y=[xi_star],
        mode='markers+text',
        name='r* (Transition)',
        marker=dict(size=15, color='red', symbol='star'),
        text=['r*'],
        textposition='top center',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>Transition Radius</b><br>' +
                      'r*/r_s: 1.3866<br>' +
                      'Ξ(r*): %{y:.4f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>🔬 SSZ Domains: g₂ vs g₁</b><br>' +
                 '<sub>Segmentation density Ξ(r) showing domain structure</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='white')
        ),
        xaxis=dict(
            title='<b>r / r_s</b>',
            type='log',
            gridcolor='rgba(100,100,150,0.3)',
            showgrid=True
        ),
        yaxis=dict(
            title='<b>Ξ(r) - Segment Density</b>',
            gridcolor='rgba(100,100,150,0.3)',
            showgrid=True,
            range=[0, 1.05]
        ),
        plot_bgcolor='#0a0a1f',
        paper_bgcolor='#000010',
        font=dict(color='white', size=12),
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='white',
            borderwidth=1
        )
    )
    
    # Add annotations
    fig.add_annotation(
        x=0.5, y=0.9,
        text='<b>g₂ Domain</b><br>Strong Segmentation<br>Tension Storage',
        showarrow=False,
        font=dict(size=12, color='orange'),
        bgcolor='rgba(255,165,0,0.2)',
        bordercolor='orange',
        borderwidth=2
    )
    
    fig.add_annotation(
        x=5, y=0.5,
        text='<b>g₁ Domain</b><br>Weak Segmentation<br>Tension Released',
        showarrow=False,
        font=dict(size=12, color='cyan'),
        bgcolor='rgba(0,255,255,0.1)',
        bordercolor='cyan',
        borderwidth=2
    )
    
    # Add REAL OBJECTS if data provided
    if objects_data is not None and len(objects_data) > 0:
        import pandas as pd
        
        # Get distances from parallax or distance column
        distances_pc = None
        if 'parallax' in objects_data.columns:
            # Convert parallax (mas) to distance (pc)
            parallax = objects_data['parallax'].copy()
            parallax = parallax[parallax > 0]  # Only positive
            if len(parallax) > 0:
                distances_pc = 1000.0 / parallax  # distance in pc
        elif 'distance' in objects_data.columns:
            distances_pc = objects_data['distance'].copy()
        elif 'dist' in objects_data.columns:
            distances_pc = objects_data['dist'].copy()
        
        if distances_pc is not None and len(distances_pc) > 0:
            # Convert to meters and calculate r/r_s
            distances_m = distances_pc * 3.0857e16  # pc to meters
            r_ratios_objects = distances_m / r_s
            
            # Calculate Xi for these objects
            xi_objects = Xi(distances_m.values, r_s)
            
            # Add as scatter points
            fig.add_trace(go.Scatter(
                x=r_ratios_objects.values,
                y=xi_objects,
                mode='markers',
                name='Real Objects',
                marker=dict(
                    size=8,
                    color='yellow',
                    symbol='star',
                    line=dict(width=1, color='white')
                ),
                hovertemplate='<b>Real Object</b><br>r/r_s: %{x:.3f}<br>Ξ(r): %{y:.4f}<extra></extra>'
            ))
    
    return fig


def create_time_dilation_comparison():
    """WISSENSCHAFTLICH KORREKT: Metric Function A(r) - SSZ vs GR
    
    Zeigt die Metrik-Funktion die NICHT singulär ist bei r=0!
    """
    M = 4.3e6 * M_SUN  # Sgr A* Mass
    r_s = r_schwarzschild(M)
    
    r_range = np.linspace(0.1 * r_s, 20 * r_s, 1000)
    r_ratio = r_range / r_s
    
    # Calculate time dilations
    d_ssz = D_SSZ(r_range, r_s)
    d_gr = D_GR(r_range, r_s)
    
    # Transition point
    r_star_ratio = 1.386562
    
    fig = go.Figure()
    
    # SSZ with domain coloring
    g2_mask = r_ratio < r_star_ratio
    g1_mask = r_ratio >= r_star_ratio
    
    # SSZ g2
    fig.add_trace(go.Scatter(
        x=r_ratio[g2_mask],
        y=d_ssz[g2_mask],
        mode='lines',
        name='D_SSZ (g₂)',
        line=dict(color='orange', width=3),
        hovertemplate='<b>SSZ (g₂)</b><br>r/r_s: %{x:.3f}<br>D: %{y:.4f}<extra></extra>'
    ))
    
    # SSZ g1
    fig.add_trace(go.Scatter(
        x=r_ratio[g1_mask],
        y=d_ssz[g1_mask],
        mode='lines',
        name='D_SSZ (g₁)',
        line=dict(color='cyan', width=3),
        hovertemplate='<b>SSZ (g₁)</b><br>r/r_s: %{x:.3f}<br>D: %{y:.4f}<extra></extra>'
    ))
    
    # GR for comparison
    fig.add_trace(go.Scatter(
        x=r_ratio,
        y=d_gr,
        mode='lines',
        name='D_GR (Singularity!)',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='<b>GR</b><br>r/r_s: %{x:.3f}<br>D: %{y:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>⏱️ Time Dilation: SSZ vs GR</b><br>' +
                 '<sub>g₂ domain (strong) vs g₁ domain (weak)</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='white')
        ),
        xaxis=dict(
            title='<b>r / r_s</b>',
            type='log',
            gridcolor='rgba(100,100,150,0.3)'
        ),
        yaxis=dict(
            title='<b>D(r) - Time Dilation Factor</b>',
            gridcolor='rgba(100,100,150,0.3)',
            range=[0, 1.05]
        ),
        plot_bgcolor='#0a0a1f',
        paper_bgcolor='#000010',
        font=dict(color='white', size=12),
        height=600,
        hovermode='closest',
        showlegend=True
    )
    
    # Add REAL OBJECTS
    if objects_data is not None and len(objects_data) > 0:
        import pandas as pd
        distances_pc = None
        if 'parallax' in objects_data.columns:
            parallax = objects_data['parallax'].copy()
            parallax = parallax[parallax > 0]
            if len(parallax) > 0:
                distances_pc = 1000.0 / parallax
        elif 'distance' in objects_data.columns:
            distances_pc = objects_data['distance'].copy()
        elif 'dist' in objects_data.columns:
            distances_pc = objects_data['dist'].copy()
        
        if distances_pc is not None and len(distances_pc) > 0:
            distances_m = distances_pc * 3.0857e16
            r_ratios = distances_m / r_s
            d_ssz_objects = D_SSZ(distances_m.values, r_s)
            
            fig.add_trace(go.Scatter(
                x=r_ratios.values,
                y=d_ssz_objects,
                mode='markers',
                name='Real Objects (SSZ)',
                marker=dict(size=8, color='yellow', symbol='star')
            ))
    
    return fig


def create_radial_stretch_plot():
    """WISSENSCHAFTLICH KORREKT: Proper Time dτ/dt - SSZ vs GR
    
    Zeigt dass SSZ finite bleibt at singularity!
    """
    M = 4.3e6 * M_SUN  # Sgr A* Mass
    r_s = r_schwarzschild(M)
    
    r_range = np.linspace(0.1 * r_s, 20 * r_s, 1000)
    r_ratio = r_range / r_s
    
    # Calculate stretch
    stretch = radial_stretch(r_range, r_s)
    
    r_star_ratio = 1.386562
    g2_mask = r_ratio < r_star_ratio
    g1_mask = r_ratio >= r_star_ratio
    
    fig = go.Figure()
    
    # g2 domain
    fig.add_trace(go.Scatter(
        x=r_ratio[g2_mask],
        y=stretch[g2_mask],
        mode='lines',
        name='Stretch (g₂)',
        line=dict(color='orange', width=3),
        fill='tozeroy',
        fillcolor='rgba(255,165,0,0.2)'
    ))
    
    # g1 domain
    fig.add_trace(go.Scatter(
        x=r_ratio[g1_mask],
        y=stretch[g1_mask],
        mode='lines',
        name='Stretch (g₁)',
        line=dict(color='cyan', width=3),
        fill='tozeroy',
        fillcolor='rgba(0,255,255,0.1)'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>📏 Radial Stretch Factor</b><br>' +
                 '<sub>R_SSZ(r) = r · (1 + Ξ(r))</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='white')
        ),
        xaxis=dict(
            title='<b>r / r_s</b>',
            type='log',
            gridcolor='rgba(100,100,150,0.3)'
        ),
        yaxis=dict(
            title='<b>1 + Ξ(r) - Stretch Factor</b>',
            gridcolor='rgba(100,100,150,0.3)'
        ),
        plot_bgcolor='#0a0a1f',
        paper_bgcolor='#000010',
        font=dict(color='white', size=12),
        height=600,
        hovermode='closest'
    )
    
    # Add REAL OBJECTS
    if objects_data is not None and len(objects_data) > 0:
        import pandas as pd
        distances_pc = None
        if 'parallax' in objects_data.columns:
            parallax = objects_data['parallax'].copy()
            parallax = parallax[parallax > 0]
            if len(parallax) > 0:
                distances_pc = 1000.0 / parallax
        elif 'distance' in objects_data.columns:
            distances_pc = objects_data['distance'].copy()
        elif 'dist' in objects_data.columns:
            distances_pc = objects_data['dist'].copy()
        
        if distances_pc is not None and len(distances_pc) > 0:
            distances_m = distances_pc * 3.0857e16
            r_ratios = distances_m / r_s
            stretch_objects = radial_stretch(distances_m.values, r_s)
            
            fig.add_trace(go.Scatter(
                x=r_ratios.values,
                y=stretch_objects,
                mode='markers',
                name='Real Objects',
                marker=dict(size=8, color='yellow', symbol='star')
            ))
    
    return fig


def create_combined_ssz_analysis():
    """Combined view of all SSZ physics"""
    M_SUN = 1.98847e30
    r_s = schwarzschild_radius(M_SUN)
    
    r_range = np.linspace(0.1 * r_s, 20 * r_s, 500)
    r_ratio = r_range / r_s
    
    # Calculate all quantities
    xi_vals = Xi(r_range, r_s)
    d_ssz_vals = D_SSZ(r_range, r_s)
    d_gr_vals = D_GR(r_range, r_s)
    stretch_vals = radial_stretch(r_range, r_s)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Ξ(r) - Segment Density',
            'D(r) - Time Dilation',
            '1+Ξ(r) - Radial Stretch',
            'SSZ vs GR Comparison'
        ),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "scatter"}]]
    )
    
    # Plot 1: Xi(r)
    fig.add_trace(
        go.Scatter(x=r_ratio, y=xi_vals, name='Ξ(r)', 
                   line=dict(color='orange', width=2)),
        row=1, col=1
    )
    
    # Plot 2: Time dilation
    fig.add_trace(
        go.Scatter(x=r_ratio, y=d_ssz_vals, name='D_SSZ',
                   line=dict(color='cyan', width=2)),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=r_ratio, y=d_gr_vals, name='D_GR',
                   line=dict(color='red', width=2, dash='dash')),
        row=1, col=2
    )
    
    # Plot 3: Stretch
    fig.add_trace(
        go.Scatter(x=r_ratio, y=stretch_vals, name='1+Ξ(r)',
                   line=dict(color='green', width=2)),
        row=2, col=1
    )
    
    # Plot 4: Deviation
    deviation = np.abs(d_ssz_vals - d_gr_vals) / d_gr_vals * 100
    fig.add_trace(
        go.Scatter(x=r_ratio, y=deviation, name='Deviation %',
                   line=dict(color='purple', width=2)),
        row=2, col=2
    )
    
    fig.update_xaxes(title_text="r / r_s", type="log")
    fig.update_yaxes(title_text="Value")
    
    fig.update_layout(
        title_text='<b>🔬 Complete SSZ Physics Analysis</b>',
        height=800,
        showlegend=True,
        plot_bgcolor='#0a0a1f',
        paper_bgcolor='#000010',
        font=dict(color='white', size=10)
    )
    
    return fig


if __name__ == "__main__":
    print("Testing SSZ Physics Plots...")
    fig1 = create_g1_g2_domain_plot()
    print("[OK] g1/g2 domain plot created")
    
    fig2 = create_time_dilation_comparison()
    print("[OK] Time dilation plot created")
    
    fig3 = create_radial_stretch_plot()
    print("[OK] Radial stretch plot created")
    
    fig4 = create_combined_ssz_analysis()
    print("[OK] Combined analysis plot created")
    
    print("\n[SUCCESS] All SSZ physics plots working!")
