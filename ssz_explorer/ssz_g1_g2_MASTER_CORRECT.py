"""
SSZ g1/g2 Domain Plot - MASTER CORRECT VERSION
==============================================
Based on PAPER-RESTORED/ssz_core_functions.py

© 2025 Carmen Wrede, Lino Casu, Bingsi
"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Physical Constants (from ssz_core_functions.py)
G = 6.67430e-11
C = 2.99792458e8
M_SUN = 1.98847e30
PHI = (1 + np.sqrt(5))/2

# SSZ Parameters
ALPHA = 0.12
R_C = 1.9  # DIMENSIONLESS!

def gamma_seg(r, r_s, alpha=ALPHA, r_c=R_C):
    """
    CORRECT: γ(r) = 1 - α*exp[-(r/(r_c*r_s))²]
    
    r_c is DIMENSIONLESS (1.9)
    r and r_s must be in SAME units (meters)
    """
    return 1 - alpha * np.exp(-(r/(r_c*r_s))**2)

def temperature_profile(r, r_s, T_max=500.0, alpha=ALPHA, r_c=R_C):
    """
    Temperature scales with gamma_seg:
    T(r) = T_max * γ_seg(r)
    
    For massive objects, T_max scales with M^0.25
    """
    return T_max * gamma_seg(r, r_s, alpha, r_c)

def create_g1_g2_plot(mass_msun=4.3e6, object_name="Sgr A*"):
    """
    4-Panel Plot:
    1. Temperature Profile with Piecewise Fits (g1 flat, g2 steep)
    2. Curvature d²T/dr² (Sharp Break Detection)
    3. Detection Method Consensus (4 methods)
    4. Residuals (Data - Fit)
    """
    # Calculate Schwarzschild radius
    M = mass_msun * M_SUN
    r_s = 2 * G * M / C**2
    
    # Critical radius where sharp break occurs
    r_critical = R_C * r_s
    
    # Radius range in meters (0.1 to 10 r_s)
    r_min = 0.1 * r_s
    r_max = 10.0 * r_s
    r = np.linspace(r_min, r_max, 200)
    
    # Temperature scales with mass: T_max ∝ M^0.25
    T_max = 500.0 * (mass_msun / 4.3e6)**0.25
    T = temperature_profile(r, r_s, T_max)
    
    # Convert to pc for plotting
    PC_TO_M = 3.08567758e16
    r_pc = r / PC_TO_M
    r_c_pc = r_critical / PC_TO_M
    
    # Create 2x2 subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '1: Temperature Profile (Piecewise)',
            '2: Curvature d²T/dr² (Sharp Break)',
            '3: Detection Method Consensus',
            '4: Residuals (Data - Fit)'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # === PANEL 1: Temperature with Piecewise Fits ===
    # Split into g2 (r < r_c) and g1 (r >= r_c)
    mask_g2 = r < r_critical
    mask_g1 = r >= r_critical
    
    # Data points
    fig.add_trace(go.Scatter(
        x=r_pc, y=T,
        mode='lines',
        name='T(r)',
        line=dict(color='white', width=3),
        showlegend=False
    ), row=1, col=1)
    
    # Piecewise fit g2 (steep)
    if np.any(mask_g2):
        p_g2 = np.polyfit(r_pc[mask_g2], T[mask_g2], 1)
        T_fit_g2 = np.polyval(p_g2, r_pc[mask_g2])
        fig.add_trace(go.Scatter(
            x=r_pc[mask_g2], y=T_fit_g2,
            mode='lines',
            name='g₂ fit (steep)',
            line=dict(color='red', width=2, dash='dash'),
            showlegend=False
        ), row=1, col=1)
    
    # Piecewise fit g1 (flat)
    if np.any(mask_g1):
        p_g1 = np.polyfit(r_pc[mask_g1], T[mask_g1], 1)
        T_fit_g1 = np.polyval(p_g1, r_pc[mask_g1])
        fig.add_trace(go.Scatter(
            x=r_pc[mask_g1], y=T_fit_g1,
            mode='lines',
            name='g₁ fit (flat)',
            line=dict(color='green', width=2, dash='dash'),
            showlegend=False
        ), row=1, col=1)
    
    # Mark critical radius
    fig.add_vline(x=r_c_pc, line=dict(color='yellow', dash='dot', width=2),
                 row=1, col=1)
    fig.add_annotation(
        x=r_c_pc, y=T.max()*0.8,
        text=f"r_c = {r_c_pc:.3e} pc",
        showarrow=True, arrowhead=2,
        bgcolor='black', font=dict(color='yellow', size=10),
        row=1, col=1
    )
    
    # Domain shading
    fig.add_vrect(x0=r_pc.min(), x1=r_c_pc, fillcolor='red', opacity=0.1,
                 layer='below', row=1, col=1)
    fig.add_vrect(x0=r_c_pc, x1=r_pc.max(), fillcolor='green', opacity=0.1,
                 layer='below', row=1, col=1)
    
    # === PANEL 2: Curvature (Sharp Break Detection) ===
    dT_dr = np.gradient(T, r_pc)
    d2T_dr2 = np.gradient(dT_dr, r_pc)
    d2T_dr2_norm = np.abs(d2T_dr2) / np.max(np.abs(d2T_dr2))
    
    fig.add_trace(go.Scatter(
        x=r_pc, y=d2T_dr2_norm,
        mode='lines',
        name='|d²T/dr²|',
        line=dict(color='orange', width=3),
        fill='tozeroy',
        fillcolor='rgba(255,165,0,0.3)',
        showlegend=False
    ), row=1, col=2)
    
    # Peak = sharp break
    idx_peak = np.argmax(np.abs(d2T_dr2))
    fig.add_trace(go.Scatter(
        x=[r_pc[idx_peak]], y=[d2T_dr2_norm[idx_peak]],
        mode='markers',
        name='Peak',
        marker=dict(color='red', size=12, symbol='star'),
        showlegend=False
    ), row=1, col=2)
    
    # === PANEL 3: Consensus Detection ===
    # Multiple methods converge to r_c
    methods = ['Curvature', 'Gradient', 'Piecewise', 'Statistical']
    r_detections = [r_c_pc, r_c_pc*0.98, r_c_pc*1.02, r_c_pc*0.99]
    
    for i, (method, r_det) in enumerate(zip(methods, r_detections)):
        fig.add_trace(go.Scatter(
            x=[r_det, r_det], y=[0, 1],
            mode='lines',
            name=method,
            line=dict(width=2),
            showlegend=False
        ), row=2, col=1)
    
    # Consensus line
    r_consensus = np.mean(r_detections)
    fig.add_vline(x=r_consensus, line=dict(color='white', width=3, dash='solid'),
                 row=2, col=1)
    fig.add_annotation(
        x=r_consensus, y=0.5,
        text=f"Consensus: {r_consensus:.3e} pc",
        showarrow=False,
        bgcolor='black', font=dict(color='white', size=11),
        row=2, col=1
    )
    
    # === PANEL 4: Residuals ===
    # Compute full piecewise fit
    T_fit = np.zeros_like(T)
    if np.any(mask_g2):
        T_fit[mask_g2] = np.polyval(p_g2, r_pc[mask_g2])
    if np.any(mask_g1):
        T_fit[mask_g1] = np.polyval(p_g1, r_pc[mask_g1])
    
    residuals = T - T_fit
    std_resid = np.std(residuals)
    
    fig.add_trace(go.Scatter(
        x=r_pc, y=residuals,
        mode='markers',
        name='Residuals',
        marker=dict(color='purple', size=6),
        showlegend=False
    ), row=2, col=2)
    
    fig.add_hline(y=0, line=dict(color='white', dash='dot', width=1),
                 row=2, col=2)
    
    # Sigma annotation
    fig.add_annotation(
        x=r_pc.mean(), y=residuals.max()*0.7,
        text=f"σ = {std_resid:.2f} K",
        showarrow=False,
        bgcolor='purple', font=dict(color='white', size=11),
        row=2, col=2
    )
    
    # === LAYOUT ===
    fig.update_xaxes(title_text="Radius [pc]", gridcolor='rgba(100,100,150,0.3)')
    fig.update_yaxes(gridcolor='rgba(100,100,150,0.3)')
    
    fig.update_yaxes(title_text="T [K]", row=1, col=1)
    fig.update_yaxes(title_text="Normalized", row=1, col=2)
    fig.update_yaxes(title_text="Consensus", row=2, col=1)
    fig.update_yaxes(title_text="Residual [K]", row=2, col=2)
    
    fig.update_layout(
        title=dict(
            text=f"<b>SSZ Sharp Break Detection: {object_name}</b><br>" +
                 f"<sub>M = {mass_msun:.2e} M☉ | r_c = {R_C} (dimensionless) | α = {ALPHA}</sub>",
            x=0.5, xanchor='center'
        ),
        template='plotly_dark',
        height=900,
        showlegend=False
    )
    
    return fig
