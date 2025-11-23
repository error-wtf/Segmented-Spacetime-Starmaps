"""GR vs SSZ Time Dilation - KORREKT aus ssz-metric-pure"""
import numpy as np
import plotly.graph_objects as go

G,C,M_SUN = 6.67430e-11,2.99792458e8,1.98847e30
PHI = (1 + np.sqrt(5)) / 2  # Golden Ratio ≈ 1.618

def Xi_SSZ(r, r_s):
    """Segment saturation: Ξ(r) = 1 - exp(-φ · r/r_s)"""
    return 1.0 - np.exp(-PHI * r / r_s)

def D_SSZ(r, r_s):
    """SSZ time dilation: D_SSZ(r) = 1 / (1 + Ξ(r))"""
    return 1.0 / (1.0 + Xi_SSZ(r, r_s))

def D_GR(r, r_s):
    """GR time dilation: D_GR(r) = √(1 - r_s/r)"""
    # Only valid for r > r_s
    with np.errstate(invalid='ignore'):
        result = np.sqrt(1.0 - r_s / r)
    return np.where(r > r_s, result, np.nan)

def create_time_dilation_comparison(mass_msun=4.3e6, object_name="Sgr A*"):
    """
    Plot SSZ vs GR time dilation with intersection point.
    
    CORRECT implementation from ssz-metric-pure repo.
    """
    r_s = 2 * G * mass_msun * M_SUN / C**2
    
    # Range: 0.01 to 10 r_s
    r_ratio = np.linspace(0.01, 10, 1000)
    r = r_ratio * r_s
    
    # Calculate time dilations
    d_ssz = D_SSZ(r, r_s)
    d_gr = D_GR(r, r_s)
    
    # Find intersection (where both are defined and equal)
    valid = ~np.isnan(d_gr)
    if np.any(valid):
        diff = np.abs(d_ssz[valid] - d_gr[valid])
        idx_min = np.argmin(diff)
        r_cross_ratio = r_ratio[valid][idx_min]
        d_cross = d_ssz[valid][idx_min]
    else:
        r_cross_ratio, d_cross = None, None
    
    fig = go.Figure()
    
    # SSZ curve (blue - singularity-free)
    fig.add_trace(go.Scatter(
        x=r_ratio, y=d_ssz,
        mode='lines',
        name='SSZ (Singularity-Free)',
        line=dict(color='blue', width=3),
        hovertemplate='r/r_s: %{x:.2f}<br>D_SSZ: %{y:.3f}<extra></extra>'
    ))
    
    # GR curve (red - singular at r_s)
    valid_gr = ~np.isnan(d_gr)
    fig.add_trace(go.Scatter(
        x=r_ratio[valid_gr], y=d_gr[valid_gr],
        mode='lines',
        name='GR (Schwarzschild)',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='r/r_s: %{x:.2f}<br>D_GR: %{y:.3f}<extra></extra>'
    ))
    
    # Schwarzschild radius marker
    fig.add_vline(x=1.0, line=dict(color='gray', dash='dot', width=1),
                 annotation=dict(text="r_s", y=0.9))
    
    # Intersection point
    if r_cross_ratio is not None:
        fig.add_trace(go.Scatter(
            x=[r_cross_ratio], y=[d_cross],
            mode='markers',
            name=f'r* = {r_cross_ratio:.3f} r_s',
            marker=dict(color='lime', size=15, symbol='circle',
                       line=dict(color='darkgreen', width=3)),
            hovertemplate=f'Intersection<br>r*: {r_cross_ratio:.3f} r_s<br>D*: {d_cross:.3f}<extra></extra>'
        ))
        fig.add_vline(x=r_cross_ratio, line=dict(color='green', dash='dot', width=1, opacity=0.5))
        fig.add_annotation(
            x=r_cross_ratio, y=d_cross + 0.1,
            text=f"D* = {d_cross:.3f}",
            showarrow=True, arrowhead=2, arrowcolor='lime',
            bgcolor='black', font=dict(color='lime', size=12)
        )
    
    fig.update_layout(
        title=dict(
            text=f"<b>GR vs SSZ Time Dilation - Universal Crossover</b><br>" +
                 f"<sub>{object_name} | M = {mass_msun:.2e} M☉ | φ-based Segment Saturation</sub>",
            x=0.5, xanchor='center'
        ),
        xaxis=dict(
            title='<b>Radius (r / r_s)</b>',
            gridcolor='rgba(200,200,200,0.3)',
            range=[0, 10]
        ),
        yaxis=dict(
            title='<b>Time Dilation Factor D(r)</b>',
            gridcolor='rgba(200,200,200,0.3)',
            range=[0, 1.1]
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        height=600,
        showlegend=True,
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.9)',
                   bordercolor='black', borderwidth=1)
    )
    
    return fig
