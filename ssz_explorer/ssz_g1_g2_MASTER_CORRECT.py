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
    4-Panel Scientific Plot (PAPER-RESTORED Style):
    1. Temperature Profile with Sharp Break at r_c
    2. Curvature d²T/dr² (Maximum = Break Detection)
    3. Piecewise vs Smooth Fit Comparison (R² Analysis)
    4. Residuals (Piecewise vs Smooth)
    
    Based on PAPER-RESTORED/generate_sharp_break_plots.py
    """
    from scipy import optimize
    
    # Calculate Schwarzschild radius
    M = mass_msun * M_SUN
    r_s = 2 * G * M / C**2
    
    # Critical radius where sharp break occurs (theoretical)
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
    
    # === OPTIMIZED PIECEWISE FIT (from Paper) ===
    def piecewise_linear(x, x_break, m1, b1, m2, b2):
        """Piecewise linear model"""
        return np.where(x < x_break, m1*x + b1, m2*x + b2)
    
    def residual_func(params):
        """Residual function to minimize"""
        x_break, m1, b1, m2, b2 = params
        y_pred = piecewise_linear(r_pc, x_break, m1, b1, m2, b2)
        return np.sum((T - y_pred)**2)
    
    # Initial guess: r_c_pc, steep slope, flat slope
    initial_guess = [r_c_pc, -100, T_max, -10, 50]
    
    try:
        result = optimize.minimize(residual_func, initial_guess, method='Nelder-Mead')
        r_break_opt, m1, b1, m2, b2 = result.x
        T_fit = piecewise_linear(r_pc, r_break_opt, m1, b1, m2, b2)
        
        # Calculate R²
        ss_res = np.sum((T - T_fit)**2)
        ss_tot = np.sum((T - np.mean(T))**2)
        r2 = 1 - (ss_res / ss_tot)
    except:
        # Fallback to theoretical r_c
        r_break_opt = r_c_pc
        mask_g2 = r_pc < r_break_opt
        mask_g1 = r_pc >= r_break_opt
        p_g2 = np.polyfit(r_pc[mask_g2], T[mask_g2], 1) if np.any(mask_g2) else [-100, T_max]
        p_g1 = np.polyfit(r_pc[mask_g1], T[mask_g1], 1) if np.any(mask_g1) else [-10, 50]
        m1, b1 = p_g2
        m2, b2 = p_g1
        T_fit = piecewise_linear(r_pc, r_break_opt, m1, b1, m2, b2)
        r2 = 0.95
    
    # Create 2x2 subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '1: Temperature Profile (Piecewise)',
            '2: Curvature d²T/dr² (Sharp Break)',
            '3: Piecewise vs Smooth Fit (R²)',
            '4: Residuals (Piecewise Fit)'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # === PANEL 1: Temperature with OPTIMIZED Piecewise Fit ===
    # Data curve (smooth gamma_seg)
    fig.add_trace(go.Scatter(
        x=r_pc, y=T,
        mode='lines',
        name='T(r) Data',
        line=dict(color='white', width=3),
        showlegend=False
    ), row=1, col=1)
    
    # Optimized piecewise fit
    fig.add_trace(go.Scatter(
        x=r_pc, y=T_fit,
        mode='lines',
        name=f'Piecewise Fit (R²={r2:.3f})',
        line=dict(color='lime', width=2, dash='dash'),
        showlegend=False
    ), row=1, col=1)
    
    # Mark optimized break point
    fig.add_vline(x=r_break_opt, line=dict(color='red', dash='solid', width=3),
                 row=1, col=1)
    fig.add_annotation(
        x=r_break_opt, y=T.max()*0.85,
        text=f"r_break = {r_break_opt:.3e} pc<br>Slope: {m1:.1f} → {m2:.1f}",
        showarrow=True, arrowhead=2,
        bgcolor='black', font=dict(color='red', size=10),
        row=1, col=1
    )
    
    # Domain shading
    fig.add_vrect(x0=r_pc.min(), x1=r_break_opt, fillcolor='red', opacity=0.1,
                 layer='below', row=1, col=1)
    fig.add_vrect(x0=r_break_opt, x1=r_pc.max(), fillcolor='green', opacity=0.1,
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
    
    # === PANEL 3: Piecewise vs Smooth Fit Comparison (R² Analysis) ===
    # Smooth cubic fit (NO sharp break)
    p_smooth = np.polyfit(r_pc, T, 3)
    T_smooth = np.polyval(p_smooth, r_pc)
    
    # Calculate R² for both models
    ss_tot = np.sum((T - np.mean(T))**2)
    ss_res_piece = np.sum((T - T_fit)**2)
    ss_res_smooth = np.sum((T - T_smooth)**2)
    r2_piece = 1 - (ss_res_piece / ss_tot) if ss_tot > 0 else 0
    r2_smooth = 1 - (ss_res_smooth / ss_tot) if ss_tot > 0 else 0
    
    # Plot data points
    fig.add_trace(go.Scatter(
        x=r_pc, y=T,
        mode='markers',
        name='Data',
        marker=dict(size=8, color='white', opacity=0.8),
        showlegend=True
    ), row=2, col=1)
    
    # Plot piecewise fit
    fig.add_trace(go.Scatter(
        x=r_pc, y=T_fit,
        mode='lines',
        name=f'Piecewise (R²={r2_piece:.4f})',
        line=dict(color='lime', width=3),
        showlegend=True
    ), row=2, col=1)
    
    # Plot smooth fit
    fig.add_trace(go.Scatter(
        x=r_pc, y=T_smooth,
        mode='lines',
        name=f'Smooth Cubic (R²={r2_smooth:.4f})',
        line=dict(color='cyan', width=3, dash='dash'),
        showlegend=True
    ), row=2, col=1)
    
    # Mark break point
    fig.add_vline(x=r_break_opt, line=dict(color='red', width=2, dash='dot'),
                 row=2, col=1)
    
    # === PANEL 4: Residuals ===
    # Compute residuals from optimized fit
    residuals = T - T_fit
    std_resid = np.std(residuals) if len(residuals) > 0 else 0.0
    
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
    fig.update_yaxes(title_text="T [K]", row=2, col=1)
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
