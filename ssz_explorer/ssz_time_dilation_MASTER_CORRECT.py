"""
SSZ Time Dilation - MASTER CORRECT VERSION
==========================================
Based on PAPER-RESTORED/ssz_core_functions.py

A_SSZ(r) = D(r) * (1 - r_s/r)
D(r) = 1 / (1 + Xi(r))
Xi(r) = 1 - gamma_seg(r)
gamma_seg(r) = 1 - α*exp[-(r/(r_c*r_s))²]

© 2025 Carmen Wrede, Lino Casu, Bingsi
"""
import numpy as np
import plotly.graph_objects as go

# Physical Constants
G = 6.67430e-11
C = 2.99792458e8
M_SUN = 1.98847e30

# SSZ Parameters
ALPHA = 0.12
R_C = 1.9  # DIMENSIONLESS

def gamma_seg(r, r_s, alpha=ALPHA, r_c=R_C):
    """γ(r) = 1 - α*exp[-(r/(r_c*r_s))²]"""
    return 1 - alpha * np.exp(-(r/(r_c*r_s))**2)

def Xi(r, r_s, alpha=ALPHA, r_c=R_C):
    """Xi(r) = 1 - γ(r)"""
    return 1 - gamma_seg(r, r_s, alpha, r_c)

def D_SSZ(r, r_s, alpha=ALPHA, r_c=R_C):
    """D(r) = 1 / (1 + Xi(r))"""
    return 1.0 / (1.0 + Xi(r, r_s, alpha, r_c))

def A_SSZ(r, r_s, alpha=ALPHA, r_c=R_C):
    """SSZ metric: A(r) = D(r) * (1 - r_s/r)"""
    return D_SSZ(r, r_s, alpha, r_c) * (1 - r_s/r)

def A_GR(r, r_s):
    """GR Schwarzschild metric: A(r) = 1 - r_s/r"""
    with np.errstate(invalid='ignore', divide='ignore'):
        result = 1 - r_s/r
    return np.where(r > r_s, result, np.nan)

def create_time_dilation_comparison(mass_msun=4.3e6, object_name="Sgr A*"):
    """
    Plot SSZ vs GR time dilation A(r) with crossover point.
    
    This shows:
    - GR: Singular at r_s (A_GR → 0)
    - SSZ: Smooth through r_s (A_SSZ finite)
    - Intersection point where both agree
    """
    M = mass_msun * M_SUN
    r_s = 2 * G * M / C**2
    
    # Range: 0.1 to 10 r_s
    r_ratio = np.linspace(0.1, 10, 1000)
    r = r_ratio * r_s
    
    # Calculate metrics
    A_ssz = A_SSZ(r, r_s)
    A_gr = A_GR(r, r_s)
    
    # Find intersection (where both are valid and close)
    valid = ~np.isnan(A_gr) & (A_gr > 0) & (A_ssz > 0)
    if np.any(valid):
        diff = np.abs(A_ssz[valid] - A_gr[valid])
        idx_cross = np.argmin(diff)
        r_cross_ratio = r_ratio[valid][idx_cross]
        A_cross = A_ssz[valid][idx_cross]
    else:
        r_cross_ratio, A_cross = None, None
    
    fig = go.Figure()
    
    # SSZ curve (blue - singularity-free)
    fig.add_trace(go.Scatter(
        x=r_ratio, y=A_ssz,
        mode='lines',
        name='SSZ (Singularity-Free)',
        line=dict(color='dodgerblue', width=3),
        hovertemplate='r/r_s: %{x:.2f}<br>A_SSZ: %{y:.3f}<extra></extra>'
    ))
    
    # GR curve (red - singular)
    valid_gr = ~np.isnan(A_gr) & (A_gr > 0)
    fig.add_trace(go.Scatter(
        x=r_ratio[valid_gr], y=A_gr[valid_gr],
        mode='lines',
        name='GR (Schwarzschild)',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='r/r_s: %{x:.2f}<br>A_GR: %{y:.3f}<extra></extra>'
    ))
    
    # Schwarzschild radius
    fig.add_vline(x=1.0, line=dict(color='gray', dash='dot', width=2),
                 annotation=dict(text="r_s", yanchor='top', y=0.95))
    fig.add_vrect(x0=0, x1=1.0, fillcolor='red', opacity=0.05,
                 layer='below', annotation_text="Singular in GR",
                 annotation_position='top left')
    
    # Intersection/Crossover
    if r_cross_ratio is not None:
        fig.add_trace(go.Scatter(
            x=[r_cross_ratio], y=[A_cross],
            mode='markers',
            name=f'Crossover r* = {r_cross_ratio:.3f} r_s',
            marker=dict(color='lime', size=18, symbol='star',
                       line=dict(color='darkgreen', width=2)),
            hovertemplate=f'Crossover<br>r*: {r_cross_ratio:.3f} r_s<br>A*: {A_cross:.3f}<extra></extra>'
        ))
        
        fig.add_annotation(
            x=r_cross_ratio, y=A_cross + 0.15,
            text=f"<b>CROSSOVER</b><br>r* = {r_cross_ratio:.3f} r_s<br>A* = {A_cross:.3f}",
            showarrow=True, arrowhead=2, arrowcolor='lime', arrowwidth=2,
            bgcolor='rgba(0,0,0,0.8)', font=dict(color='lime', size=12),
            bordercolor='lime', borderwidth=2
        )
    
    fig.update_layout(
        title=dict(
            text=f"<b>GR vs SSZ Metric Component A(r) - Universal Crossover</b><br>" +
                 f"<sub>{object_name} | M = {mass_msun:.2e} M☉ | r_c = {R_C} (dimensionless)</sub>",
            x=0.5, xanchor='center'
        ),
        xaxis=dict(
            title='<b>Radius (r / r_s)</b>',
            gridcolor='rgba(200,200,200,0.3)',
            range=[0, 10]
        ),
        yaxis=dict(
            title='<b>Metric Component A(r)</b>',
            gridcolor='rgba(200,200,200,0.3)',
            range=[-0.1, 1.1]
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black', size=12),
        height=600,
        showlegend=True,
        legend=dict(
            x=0.02, y=0.98,
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='black', borderwidth=1
        )
    )
    
    return fig
