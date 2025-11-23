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

def D_GR_func(r, r_s):
    """GR time dilation: D_GR(r) = √(1 - r_s/r)"""
    with np.errstate(invalid='ignore', divide='ignore'):
        result = np.sqrt(1.0 - r_s / r)
    return np.where(r > r_s, result, np.nan)

def create_time_dilation_comparison(mass_msun=4.3e6, object_name="Sgr A*"):
    """
    Plot SSZ vs GR TIME DILATION FACTOR D(r) with crossover point.
    
    CORRECT formulas from ssz-metric-pure:
    - D_SSZ(r) = 1 / (1 + Xi(r))  [Singularity-free]
    - D_GR(r) = √(1 - r_s/r)      [Singular at r_s]
    
    This shows:
    - GR: Diverges at r_s (D_GR → 0)
    - SSZ: Smooth through r_s (D_SSZ finite)
    - Intersection point where both agree
    """
    M = mass_msun * M_SUN
    r_s = 2 * G * M / C**2
    
    # Range: 0.1 to 10 r_s
    r_ratio = np.linspace(0.1, 10, 1000)
    r = r_ratio * r_s
    
    # Calculate TIME DILATION factors D(r), NOT metric A(r)!
    D_ssz = D_SSZ(r, r_s)
    D_gr = D_GR_func(r, r_s)
    
    # Find intersection (where both are valid and close)
    valid = ~np.isnan(D_gr) & (D_gr > 0) & (D_ssz > 0)
    if np.any(valid):
        diff = np.abs(D_ssz[valid] - D_gr[valid])
        idx_cross = np.argmin(diff)
        r_cross_ratio = r_ratio[valid][idx_cross]
        D_cross = D_ssz[valid][idx_cross]
    else:
        r_cross_ratio, D_cross = None, None
    
    fig = go.Figure()
    
    # SSZ curve (blue - singularity-free)
    fig.add_trace(go.Scatter(
        x=r_ratio, y=D_ssz,
        mode='lines',
        name='D_SSZ (Singularity-Free)',
        line=dict(color='dodgerblue', width=3),
        hovertemplate='r/r_s: %{x:.2f}<br>D_SSZ: %{y:.3f}<extra></extra>'
    ))
    
    # GR curve (red - singular)
    valid_gr = ~np.isnan(D_gr) & (D_gr > 0)
    fig.add_trace(go.Scatter(
        x=r_ratio[valid_gr], y=D_gr[valid_gr],
        mode='lines',
        name='D_GR (Schwarzschild)',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='r/r_s: %{x:.2f}<br>D_GR: %{y:.3f}<extra></extra>'
    ))
    
    # Schwarzschild radius
    fig.add_vline(x=1.0, line=dict(color='gray', dash='dot', width=2),
                 annotation=dict(text="r_s", yanchor='bottom', y=0.05))
    fig.add_vrect(x0=0, x1=1.0, fillcolor='red', opacity=0.05,
                 layer='below', annotation_text="GR Singular",
                 annotation_position='bottom left')
    
    # Intersection/Crossover
    if r_cross_ratio is not None:
        fig.add_trace(go.Scatter(
            x=[r_cross_ratio], y=[D_cross],
            mode='markers',
            name=f'Crossover r* = {r_cross_ratio:.3f} r_s',
            marker=dict(color='lime', size=18, symbol='star',
                       line=dict(color='darkgreen', width=2)),
            hovertemplate=f'Crossover<br>r*: {r_cross_ratio:.3f} r_s<br>D*: {D_cross:.3f}<extra></extra>'
        ))
        
        fig.add_annotation(
            x=r_cross_ratio, y=D_cross + 0.1,
            text=f"<b>CROSSOVER</b><br>r* = {r_cross_ratio:.3f} r_s<br>D* = {D_cross:.3f}",
            showarrow=True, arrowhead=2, arrowcolor='lime', arrowwidth=2,
            bgcolor='rgba(0,0,0,0.8)', font=dict(color='lime', size=12),
            bordercolor='lime', borderwidth=2
        )
    
    fig.update_layout(
        title=dict(
            text=f"<b>GR vs SSZ Time Dilation Factor D(r) - Universal Crossover</b><br>" +
                 f"<sub>{object_name} | M = {mass_msun:.2e} M☉ | r_c = {R_C} (dimensionless)</sub>",
            x=0.5, xanchor='center'
        ),
        xaxis=dict(
            title='<b>Radius (r / r_s)</b>',
            gridcolor='rgba(255,255,255,0.2)',
            zerolinecolor='rgba(255,255,255,0.3)',
            range=[0, 10]
        ),
        yaxis=dict(
            title='<b>Time Dilation Factor D(r)</b>',
            gridcolor='rgba(255,255,255,0.2)',
            zerolinecolor='rgba(255,255,255,0.3)',
            range=[0, 1.1]
        ),
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0.9)',
        paper_bgcolor='rgb(17,17,17)',
        font=dict(color='white', size=12),
        height=600,
        showlegend=True,
        legend=dict(
            x=0.02, y=0.98,
            bgcolor='rgba(0,0,0,0.8)',
            bordercolor='white', borderwidth=1
        )
    )
    
    return fig
