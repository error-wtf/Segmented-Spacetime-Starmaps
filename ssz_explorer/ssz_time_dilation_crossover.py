"""GR vs SSZ Time Dilation - Universal Crossover"""
import numpy as np
import plotly.graph_objects as go

G,C,M_SUN,ALPHA,R_C = 6.67430e-11,2.99792458e8,1.98847e30,0.12,1.9

def create_time_dilation_comparison(mass_msun=4.3e6, object_name="Sgr A*"):
    r_s = 2*G*mass_msun*M_SUN/C**2
    
    # Range: 1 to 6 r_s
    r_ratio = np.linspace(1.01, 6, 500)
    r = r_ratio * r_s
    
    # SSZ: D(r) = 1/(1+Xi) where Xi = 1 - gamma = alpha*exp(-(r/(r_c*r_s))^2)
    Xi = ALPHA * np.exp(-(r/(R_C*r_s))**2)
    D_ssz = 1 / (1 + Xi)
    
    # GR: D(r) = 1 - r_s/r (but this is A(r), not D!)
    # For comparison: GR metric coefficient
    D_gr = 1 - r_s/r
    
    # Find CROSSOVER (intersection)
    diff = np.abs(D_ssz - D_gr)
    idx_cross = np.argmin(diff)
    r_cross_ratio = r_ratio[idx_cross]
    D_cross = D_ssz[idx_cross]
    
    fig = go.Figure()
    
    # GR curve (blue, rising)
    fig.add_trace(go.Scatter(
        x=r_ratio, y=D_gr,
        mode='lines',
        name='General Relativity',
        line=dict(color='blue', width=3)
    ))
    
    # SSZ curve (red, flat)
    fig.add_trace(go.Scatter(
        x=r_ratio, y=D_ssz,
        mode='lines',
        name='Segmented Spacetime (SSZ)',
        line=dict(color='red', width=3)
    ))
    
    # Crossover point (green)
    fig.add_trace(go.Scatter(
        x=[r_cross_ratio], y=[D_cross],
        mode='markers',
        name=f'Intersection r*/r_s = {r_cross_ratio:.3f}',
        marker=dict(color='lime', size=15, symbol='circle',
                   line=dict(color='darkgreen', width=3))
    ))
    
    # Vertical line at crossover
    fig.add_vline(x=r_cross_ratio, line=dict(color='gray', dash='dash', width=1))
    
    # Annotation
    fig.add_annotation(
        x=r_cross_ratio, y=D_cross,
        text=f"D* = {D_cross:.3f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor='lime',
        bgcolor='black',
        font=dict(color='lime', size=12)
    )
    
    fig.update_layout(
        title=dict(
            text=f"<b>GR vs SSZ Time Dilation - Universal Crossover</b><br>" +
                 f"<sub>Object: {object_name} (M = {mass_msun:.2e} M☉)</sub>",
            x=0.5, xanchor='center'
        ),
        xaxis=dict(
            title='<b>r / r_s</b>',
            gridcolor='rgba(200,200,200,0.3)'
        ),
        yaxis=dict(
            title='<b>Time Dilation D(r)</b>',
            gridcolor='rgba(200,200,200,0.3)',
            range=[0.2, 1.0]
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        height=600,
        showlegend=True,
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)')
    )
    
    return fig
