"""
SSZ Physics Plots - Matplotlib Version (FUNKTIONIERT GARANTIERT!)
=================================================================

Nutzt Matplotlib wie PAPER-RESTORED - keine Gradio Plot Bugs!

© 2025 Carmen Wrede, Lino Casu, Bingsi
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
import io
from PIL import Image

# Constants
G = 6.67430e-11
C = 2.99792458e8
M_SUN = 1.98847e30
PC_TO_M = 3.0857e16

# SSZ Parameters (EXACT from PAPER-RESTORED)
ALPHA = 0.12
R_C = 1.9  # dimensionless scale factor (NOT parsecs!)

def r_schwarzschild(M):
    """Schwarzschild radius"""
    return 2 * G * M / (C**2)

def gamma_seg(r, r_s, alpha=ALPHA, r_c=R_C):
    """
    Segmentation field (EXACT from PAPER-RESTORED ssz_core_functions.py)
    γ(r) = 1 - α·exp[-(r/(r_c·r_s))²]
    
    Args:
        r: radius in meters
        r_s: Schwarzschild radius in meters
        alpha: segmentation parameter (default 0.12)
        r_c: dimensionless critical radius scale (default 1.9)
    """
    return 1.0 - alpha * np.exp(-(r / (r_c * r_s))**2)

def Xi(r, r_s, alpha=ALPHA, r_c=R_C):
    """
    Segmentation parameter Xi(r) = 1 - γ(r) = α·exp[-(r/(r_c·r_s))²]
    (from PAPER-RESTORED ssz_core_functions.py)
    """
    return 1.0 - gamma_seg(r, r_s, alpha, r_c)

def create_domains_plot_png(object_name="Sgr A*", mass_msun=1.0, distance_pc=1000.0):
    """
    g₁/g₂ Domains Plot - PAPER STYLE with sharp break, data points, domain splitting
    
    Args:
        object_name: Name of the object
        mass_msun: Mass in solar masses
        distance_pc: Distance in parsecs
    """
    print(f"\n{'='*80}")
    print(f"[PLOT] Paper-Style Domains Plot:")
    print(f"  Object: {object_name}")
    print(f"  Mass: {mass_msun:.3f} M☉, Distance: {distance_pc:.2f} pc")
    
    M = mass_msun * M_SUN
    r_s = r_schwarzschild(M)
    r_s_pc = r_s / PC_TO_M
    
    # PAPER MATH: r_c is CONSTANT 1.9 pc, but effective scale is r_c * r_s
    r_c_pc = R_C  # KONSTANT 1.9 pc
    r_c_eff_pc = r_c_pc * r_s_pc  # Effective scale (used in exponential)
    print(f"  r_c (constant): {r_c_pc:.2f} pc")
    print(f"  r_c * r_s (effective scale): {r_c_eff_pc:.2e} pc")
    print(f"  r_s: {r_s_pc:.2e} pc")
    print(f"{'='*80}\n")
    
    # Generate synthetic "measurement points" (10-15 points)
    r_min_pc = max(r_c_eff_pc * 0.1, 1e-6)
    r_max_pc = min(distance_pc * 10, 1e4)
    n_points = 12
    r_data_pc = np.logspace(np.log10(r_min_pc), np.log10(r_max_pc), n_points)
    r_data = r_data_pc * PC_TO_M
    
    # Calculate Xi at data points using PAPER FORMULA
    xi_data = np.array([Xi(r, r_s, ALPHA, R_C) for r in r_data])
    
    # Split into g₂ (r < r_c) and g₁ (r >= r_c) domains  
    # Use EFFECTIVE scale for domain split
    mask_g2 = r_data_pc < r_c_eff_pc
    mask_g1 = r_data_pc >= r_c_eff_pc
    
    r_g2 = r_data_pc[mask_g2]
    xi_g2 = xi_data[mask_g2]
    r_g1 = r_data_pc[mask_g1]
    xi_g1 = xi_data[mask_g1]
    
    # Create figure - DARK STYLE
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='#0a0a1f')
    ax.set_facecolor('#000010')
    
    # DOMAIN SHADING (like paper plots)
    ax.axvspan(r_min_pc, r_c_pc, alpha=0.15, color='red', label='g₂ domain (collapse)')
    ax.axvspan(r_c_pc, r_max_pc, alpha=0.15, color='green', label='g₁ domain (stable)')
    
    # SHARP BREAK LINE at r_c
    ax.axvline(r_c_pc, color='red', linestyle='--', linewidth=2.5, label=f'Sharp break: r_c = {r_c_pc:.2f} pc', zorder=5)
    
    # Plot DATA POINTS (white on dark background)
    ax.scatter(r_data_pc, xi_data, color='white', s=80, zorder=10, label='Data points', edgecolors='cyan', linewidths=1.5)
    
    # FIT g₂ domain (red line, STEEP)
    if len(r_g2) > 1:
        # Linear fit in log-space for g₂
        coeffs_g2 = np.polyfit(np.log10(r_g2), xi_g2, 1)
        r_g2_fine = np.logspace(np.log10(r_g2.min()), np.log10(r_c_pc), 100)
        xi_g2_fit = np.polyval(coeffs_g2, np.log10(r_g2_fine))
        ax.plot(r_g2_fine, xi_g2_fit, 'r-', linewidth=3, label=f'g₂ fit (steep, slope={coeffs_g2[0]:.3f})', zorder=8)
    
    # FIT g₁ domain (green line, FLAT)
    if len(r_g1) > 1:
        # Linear fit in log-space for g₁
        coeffs_g1 = np.polyfit(np.log10(r_g1), xi_g1, 1)
        r_g1_fine = np.logspace(np.log10(r_c_pc), np.log10(r_g1.max()), 100)
        xi_g1_fit = np.polyval(coeffs_g1, np.log10(r_g1_fine))
        ax.plot(r_g1_fine, xi_g1_fit, 'g-', linewidth=3, label=f'g₁ fit (flat, slope={coeffs_g1[0]:.3f})', zorder=8)
        
        # Calculate slope ratio
        if len(r_g2) > 1:
            slope_ratio = abs(coeffs_g2[0] / coeffs_g1[0]) if coeffs_g1[0] != 0 else np.inf
            print(f"  Slope ratio g₂/g₁: {slope_ratio:.2f}×")
    
    # Styling (dark style)
    ax.set_xscale('log')
    ax.set_xlabel('Radius [pc]', fontsize=14, color='white', fontweight='bold')
    ax.set_ylabel('Ξ(r) - Segment Density', fontsize=14, color='white', fontweight='bold')
    ax.set_title(f'Domain Structure (g₁/g₂) - {object_name}\nSharp Break at r_c = {r_c_pc:.2f} pc', 
                 fontsize=16, color='white', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, color='gray', linestyle=':', linewidth=0.5)
    ax.legend(fontsize=11, loc='upper right', framealpha=0.95, facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.tick_params(colors='white', labelsize=12)
    
    # Save
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        plt.savefig(tmp.name, format='png', dpi=150, bbox_inches='tight', facecolor='#0a0a1f')
        plt.close()
        return tmp.name


def create_time_dilation_png(object_name="Sgr A*", mass_msun=1.0, distance_pc=1000.0):
    """
    Time Dilation D(r) - SHARP BREAK at r_c with PIECEWISE FITS + GR Intersection
    Like PAPER-RESTORED temperature profiles!
    """
    M = mass_msun * M_SUN
    r_s = r_schwarzschild(M)
    r_s_pc = r_s / PC_TO_M
    r_c_eff_pc = R_C * r_s_pc
    
    # Generate data points with SHARP BREAK behavior
    r_min_pc = max(r_s_pc * 0.01, 1e-8)
    r_max_pc = min(distance_pc * 10, r_c_eff_pc * 50)
    n_points = 15
    r_data_pc = np.logspace(np.log10(r_min_pc), np.log10(r_max_pc), n_points)
    r_data = r_data_pc * PC_TO_M
    
    # Calculate A(r) = TIME DILATION COEFFICIENT (g_tt)
    # SSZ: A = D(r) * (1 - r_s/r) where D(r) = 1/(1+Xi)
    xi_data = np.array([Xi(r, r_s, ALPHA, R_C) for r in r_data])
    D_temp = 1 / (1 + xi_data)
    A_data = D_temp * (1 - r_s / r_data)  # CORRECT SSZ formula!
    
    # Fine grid for smooth curves
    r_smooth_pc = np.logspace(np.log10(r_min_pc), np.log10(r_max_pc), 500)
    r_smooth = r_smooth_pc * PC_TO_M
    xi_smooth = np.array([Xi(r, r_s, ALPHA, R_C) for r in r_smooth])
    D_smooth_temp = 1 / (1 + xi_smooth)
    A_ssz = D_smooth_temp * (1 - r_s / r_smooth)  # SSZ: A = D*(1-r_s/r)
    A_gr = 1 - r_s / r_smooth  # GR: A = 1 - r_s/r
    
    # Find INTERSECTION point (where A_SSZ = A_GR)
    diff = np.abs(A_ssz - A_gr)
    idx_intersect = np.argmin(diff)
    r_intersect_pc = r_smooth_pc[idx_intersect]
    A_intersect = A_ssz[idx_intersect]
    
    # PIECEWISE LINEAR FITS
    mask_g2 = r_data_pc < r_c_eff_pc
    mask_g1 = r_data_pc >= r_c_eff_pc
    
    # Fit g2 (collapse domain - STEEP)
    if np.sum(mask_g2) >= 2:
        p_g2 = np.polyfit(r_data_pc[mask_g2], A_data[mask_g2], 1)
        r_fit_g2 = np.linspace(r_data_pc[mask_g2].min(), r_c_eff_pc, 50)
        A_fit_g2 = np.polyval(p_g2, r_fit_g2)
        slope_g2 = p_g2[0]
    else:
        r_fit_g2 = None
        slope_g2 = 0
    
    # Fit g1 (stable domain - FLAT)
    if np.sum(mask_g1) >= 2:
        p_g1 = np.polyfit(r_data_pc[mask_g1], A_data[mask_g1], 1)
        r_fit_g1 = np.linspace(r_c_eff_pc, r_data_pc[mask_g1].max(), 50)
        A_fit_g1 = np.polyval(p_g1, r_fit_g1)
        slope_g1 = p_g1[0]
    else:
        r_fit_g1 = None
        slope_g1 = 0
    
    # Create figure - DARK STYLE
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#0a0a1f')
    ax.set_facecolor('#000010')
    
    # Domain shading
    ax.axvspan(r_min_pc, r_c_eff_pc, alpha=0.15, color='red', label='g₂ (collapse)', zorder=1)
    ax.axvspan(r_c_eff_pc, r_max_pc, alpha=0.15, color='green', label='g₁ (stable)', zorder=1)
    
    # Sharp break line
    ax.axvline(r_c_eff_pc, color='red', linestyle='--', linewidth=3, alpha=0.8, 
               label=f'r_c = {r_c_eff_pc:.3e} pc', zorder=4)
    
    # Plot SSZ smooth curve
    ax.plot(r_smooth_pc, A_ssz, color='#00ff00', linewidth=2.5, alpha=0.7, 
            label='SSZ: A(r)=D(r)*(1-r_s/r)', zorder=3)
    
    # Plot GR curve
    ax.plot(r_smooth_pc, A_gr, color='#ff6b6b', linewidth=2.5, linestyle='--', alpha=0.7,
            label='GR: A(r)=1-r_s/r [Singular]', zorder=3)
    
    # Plot DATA POINTS (colored by domain)
    ax.scatter(r_data_pc[mask_g2], A_data[mask_g2], color='red', s=100, 
               edgecolors='white', linewidths=2, zorder=10, label='g₂ data')
    ax.scatter(r_data_pc[mask_g1], A_data[mask_g1], color='lime', s=100, 
               edgecolors='white', linewidths=2, zorder=10, label='g₁ data')
    
    # Plot PIECEWISE FITS
    if r_fit_g2 is not None:
        ax.plot(r_fit_g2, A_fit_g2, 'r-', linewidth=3, alpha=0.9, 
                label=f'g₂ fit: slope={slope_g2:.2e}', zorder=5)
    if r_fit_g1 is not None:
        ax.plot(r_fit_g1, A_fit_g1, 'g-', linewidth=3, alpha=0.9, 
                label=f'g₁ fit: slope={slope_g1:.2e}', zorder=5)
    
    # Mark INTERSECTION POINT
    ax.plot(r_intersect_pc, A_intersect, 'yo', markersize=15, 
            markeredgewidth=3, markeredgecolor='white', zorder=20,
            label=f'Intersection: r*={r_intersect_pc:.3e} pc')
    ax.annotate(f'SSZ ∩ GR\nr={r_intersect_pc:.2e} pc\nA={A_intersect:.3f}',
                xy=(r_intersect_pc, A_intersect), xytext=(r_intersect_pc*3, A_intersect-0.15),
                fontsize=10, color='yellow', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.8, edgecolor='yellow'),
                arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
    
    # Styling
    ax.set_xscale('log')
    ax.set_xlabel('Radius [pc]', fontsize=14, color='white', fontweight='bold')
    ax.set_ylabel('A(r) = g_tt Metric Coefficient', fontsize=14, color='white', fontweight='bold')
    ax.set_title(f'Time Dilation A(r): Sharp Break at r_c - {object_name}\nSSZ: A=D(r)*(1-r_s/r) | GR: A=1-r_s/r',
                 fontsize=16, color='white', fontweight='bold', pad=20)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3, color='gray', linestyle=':', linewidth=0.5)
    ax.legend(fontsize=9, loc='lower right', framealpha=0.95, facecolor='#1a1a2e', 
              edgecolor='white', labelcolor='white', ncol=2)
    ax.tick_params(colors='white', labelsize=12)
    
    # Save
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        plt.savefig(tmp.name, format='png', dpi=150, bbox_inches='tight', facecolor='#0a0a1f')
        plt.close()
        return tmp.name


def create_radial_stretch_png(object_name="Sgr A*", mass_msun=1.0, distance_pc=1000.0):
    """
    Radial Metric γ(r) - SHARP BREAK at r_c with PIECEWISE FITS + Collapse Rate
    Like PAPER-RESTORED domain structure!
    """
    M = mass_msun * M_SUN
    r_s = r_schwarzschild(M)
    r_s_pc = r_s / PC_TO_M
    r_c_eff_pc = R_C * r_s_pc
    
    # Generate data points
    r_min_pc = max(r_s_pc * 0.01, 1e-8)
    r_max_pc = min(distance_pc * 10, r_c_eff_pc * 50)
    n_points = 15
    r_data_pc = np.logspace(np.log10(r_min_pc), np.log10(r_max_pc), n_points)
    r_data = r_data_pc * PC_TO_M
    
    # Calculate γ(r) = 1 - Xi for data points
    gamma_data = np.array([gamma_seg(r, r_s, ALPHA, R_C) for r in r_data])
    
    # Fine grid for smooth curves
    r_smooth_pc = np.logspace(np.log10(r_min_pc), np.log10(r_max_pc), 500)
    r_smooth = r_smooth_pc * PC_TO_M
    gamma_smooth = np.array([gamma_seg(r, r_s, ALPHA, R_C) for r in r_smooth])
    
    # Calculate COLLAPSE RATE (negative gradient) - SMOOTHED
    # Use central differences on linear (not log) spacing for smoother results
    r_linear = np.linspace(r_min_pc, r_max_pc, 500)
    gamma_linear = np.array([gamma_seg(r*PC_TO_M, r_s, ALPHA, R_C) for r in r_linear])
    dgamma_dr_linear = np.gradient(gamma_linear, r_linear)
    max_gradient = np.max(np.abs(dgamma_dr_linear))
    if max_gradient > 0:
        collapse_rate_linear = -dgamma_dr_linear / max_gradient
    else:
        collapse_rate_linear = np.zeros_like(dgamma_dr_linear)
    
    # PIECEWISE LINEAR FITS
    mask_g2 = r_data_pc < r_c_eff_pc
    mask_g1 = r_data_pc >= r_c_eff_pc
    
    # Fit g2 (collapse domain - NEGATIVE slope)
    if np.sum(mask_g2) >= 2:
        p_g2 = np.polyfit(r_data_pc[mask_g2], gamma_data[mask_g2], 1)
        r_fit_g2 = np.linspace(r_data_pc[mask_g2].min(), r_c_eff_pc, 50)
        gamma_fit_g2 = np.polyval(p_g2, r_fit_g2)
        slope_g2 = p_g2[0]
    else:
        r_fit_g2 = None
        slope_g2 = 0
    
    # Fit g1 (stable domain - FLAT)
    if np.sum(mask_g1) >= 2:
        p_g1 = np.polyfit(r_data_pc[mask_g1], gamma_data[mask_g1], 1)
        r_fit_g1 = np.linspace(r_c_eff_pc, r_data_pc[mask_g1].max(), 50)
        gamma_fit_g1 = np.polyval(p_g1, r_fit_g1)
        slope_g1 = p_g1[0]
    else:
        r_fit_g1 = None
        slope_g1 = 0
    
    # Create figure with 2 panels - DARK STYLE
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), facecolor='#0a0a1f')
    ax1.set_facecolor('#000010')
    ax2.set_facecolor('#000010')
    
    # === TOP PANEL: γ(r) with sharp break ===
    # Domain shading
    ax1.axvspan(r_min_pc, r_c_eff_pc, alpha=0.15, color='red', label='g₂ (collapse)', zorder=1)
    ax1.axvspan(r_c_eff_pc, r_max_pc, alpha=0.15, color='green', label='g₁ (stable)', zorder=1)
    
    # Sharp break line
    ax1.axvline(r_c_eff_pc, color='red', linestyle='--', linewidth=3, alpha=0.8,
                label=f'r_c = {r_c_eff_pc:.3e} pc', zorder=4)
    
    # Plot SSZ smooth curve
    ax1.plot(r_smooth_pc, gamma_smooth, color='cyan', linewidth=2.5, alpha=0.7,
             label='SSZ: γ(r)=1-Ξ', zorder=3)
    
    # Plot DATA POINTS
    ax1.scatter(r_data_pc[mask_g2], gamma_data[mask_g2], color='red', s=100,
                edgecolors='white', linewidths=2, zorder=10, label='g₂ data')
    ax1.scatter(r_data_pc[mask_g1], gamma_data[mask_g1], color='lime', s=100,
                edgecolors='white', linewidths=2, zorder=10, label='g₁ data')
    
    # Plot PIECEWISE FITS
    if r_fit_g2 is not None:
        ax1.plot(r_fit_g2, gamma_fit_g2, 'r-', linewidth=3, alpha=0.9,
                 label=f'g₂ fit: slope={slope_g2:.2e}', zorder=5)
    if r_fit_g1 is not None:
        ax1.plot(r_fit_g1, gamma_fit_g1, 'g-', linewidth=3, alpha=0.9,
                 label=f'g₁ fit: slope={slope_g1:.2e}', zorder=5)
    
    ax1.set_xscale('log')
    from matplotlib.ticker import ScalarFormatter
    ax1.xaxis.set_major_formatter(ScalarFormatter())
    ax1.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    ax1.set_xlabel('Radius [pc]', fontsize=13, color='white', fontweight='bold')
    ax1.set_ylabel('γ(r) = Segmentation Field', fontsize=13, color='white', fontweight='bold')
    ax1.set_title(f'Segmentation Field γ(r): Sharp Break at r_c - {object_name}',
                  fontsize=15, color='white', fontweight='bold', pad=15)
    ax1.set_ylim(0.85, 1.02)
    ax1.grid(True, alpha=0.3, color='gray', linestyle=':', linewidth=0.5)
    ax1.legend(fontsize=9, loc='lower right', framealpha=0.95, facecolor='#1a1a2e',
               edgecolor='white', labelcolor='white', ncol=2)
    ax1.tick_params(colors='white', labelsize=11)
    
    # === BOTTOM PANEL: Collapse Rate ===
    ax2.plot(r_linear, collapse_rate_linear, color='orange', linewidth=3, label='Collapse Rate C(r)', zorder=3)
    ax2.axvline(r_c_eff_pc, color='red', linestyle='--', linewidth=3, alpha=0.8, zorder=4)
    ax2.axvspan(r_min_pc, r_c_eff_pc, alpha=0.15, color='red', zorder=1)
    ax2.axvspan(r_c_eff_pc, r_max_pc, alpha=0.15, color='green', zorder=1)
    ax2.axhline(0, color='white', linestyle=':', linewidth=1, alpha=0.5)
    
    ax2.set_xscale('log')
    from matplotlib.ticker import ScalarFormatter
    ax2.xaxis.set_major_formatter(ScalarFormatter())
    ax2.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    ax2.set_xlabel('Radius [pc]', fontsize=13, color='white', fontweight='bold')
    ax2.set_ylabel('Collapse Rate C(r)', fontsize=13, color='white', fontweight='bold')
    ax2.set_title('Collapse Rate from -dγ/dr (high in g₂, low in g₁)',
                  fontsize=14, color='orange', fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, color='gray', linestyle=':', linewidth=0.5)
    ax2.legend(fontsize=10, loc='upper right', framealpha=0.95, facecolor='#1a1a2e',
               edgecolor='white', labelcolor='white')
    ax2.tick_params(colors='white', labelsize=11)
    
    plt.tight_layout()
    
    # Save
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        plt.savefig(tmp.name, format='png', dpi=150, bbox_inches='tight', facecolor='#0a0a1f')
        plt.close()
        return tmp.name


def create_combined_analysis_png(object_name="Sgr A*", mass_msun=1.0, distance_pc=1000.0):
    """
    Combined 4-Panel Analysis - PAPER STYLE with g1/g2 domains
    """
    M = mass_msun * M_SUN
    r_s = r_schwarzschild(M)
    r_s_pc = r_s / PC_TO_M
    
    # PAPER MATH
    r_c_pc = R_C
    r_c_eff_pc = r_c_pc * r_s_pc
    
    # Generate data points
    r_min_pc = max(r_c_eff_pc * 0.1, 1e-6)
    r_max_pc = min(distance_pc * 10, 1e4)
    n_points = 12
    r_data_pc = np.logspace(np.log10(r_min_pc), np.log10(r_max_pc), n_points)
    r_data = r_data_pc * PC_TO_M
    
    # Calculate all quantities
    xi_data = np.array([Xi(r, r_s, ALPHA, R_C) for r in r_data])
    gamma_data = np.array([gamma_seg(r, r_s, ALPHA, R_C) for r in r_data])
    D_data = 1 / (1 + xi_data)
    dtau_dr_data = gamma_data / D_data
    
    # Create 4-panel figure - DARK STYLE
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), facecolor='#0a0a1f')
    axes = axes.flatten()
    
    # Apply dark style to all panels
    from matplotlib.ticker import ScalarFormatter
    for i, ax in enumerate(axes):
        ax.set_facecolor('#000010')
        ax.axvspan(r_min_pc, r_c_pc, alpha=0.1, color='red')
        ax.axvspan(r_c_pc, r_max_pc, alpha=0.1, color='green')
        ax.axvline(r_c_pc, color='red', linestyle='--', linewidth=1.5, alpha=0.7, zorder=5)
        ax.set_xscale('log')
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
        ax.grid(True, alpha=0.3, color='gray', linestyle=':', linewidth=0.5)
        ax.tick_params(colors='white', labelsize=10)
    
    # Panel 1: Xi (Segment Density) - LINE + POINTS
    axes[0].plot(r_data_pc, xi_data, color='orange', linewidth=1.5, alpha=0.6, zorder=8)
    axes[0].scatter(r_data_pc, xi_data, color='orange', s=50, zorder=10, edgecolors='white', linewidths=1)
    axes[0].set_xlabel('Radius [pc]', color='white', fontweight='bold')
    axes[0].set_ylabel('Ξ(r)', color='white', fontweight='bold')
    axes[0].set_title('Segment Density Ξ(r)', color='white', fontweight='bold')
    
    # Panel 2: D(r) (Time Dilation) - LINE + POINTS
    axes[1].plot(r_data_pc, D_data, color='#00ff00', linewidth=1.5, alpha=0.6, zorder=8)
    axes[1].scatter(r_data_pc, D_data, color='#00ff00', s=50, zorder=10, edgecolors='white', linewidths=1)
    axes[1].set_xlabel('Radius [pc]', color='white', fontweight='bold')
    axes[1].set_ylabel('D(r)', color='white', fontweight='bold')
    axes[1].set_title('Time Dilation D(r) = 1/(1+Ξ)', color='white', fontweight='bold')
    
    # Panel 3: γ(r) (Radial Metric) - LINE + POINTS
    axes[2].plot(r_data_pc, gamma_data, color='cyan', linewidth=1.5, alpha=0.6, zorder=8)
    axes[2].scatter(r_data_pc, gamma_data, color='cyan', s=50, zorder=10, edgecolors='white', linewidths=1)
    axes[2].set_xlabel('Radius [pc]', color='white', fontweight='bold')
    axes[2].set_ylabel('γ(r)', color='white', fontweight='bold')
    axes[2].set_title('Radial Metric γ(r)', color='white', fontweight='bold')
    
    # Panel 4: dτ/dr (Proper Time) - LINE + POINTS
    axes[3].plot(r_data_pc, dtau_dr_data, color='magenta', linewidth=1.5, alpha=0.6, zorder=8)
    axes[3].scatter(r_data_pc, dtau_dr_data, color='magenta', s=50, zorder=10, edgecolors='white', linewidths=1)
    axes[3].set_xlabel('Radius [pc]', color='white', fontweight='bold')
    axes[3].set_ylabel('dτ/dr', color='white', fontweight='bold')
    axes[3].set_title('Proper Time dτ/dr = γ/D', color='white', fontweight='bold')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Add object info at top
    fig.text(0.5, 0.98, f'Combined SSZ Analysis: {object_name} | M={mass_msun:.2f} M☉ | d={distance_pc:.1f} pc | r_c={r_c_pc:.2f} pc', 
             fontsize=13, color='white', ha='center', va='top', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.7', facecolor='#1a1a2e', edgecolor='orange', alpha=0.9))
    
    # Save
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        plt.savefig(tmp.name, format='png', dpi=150, bbox_inches='tight', facecolor='#0a0a1f')
        plt.close()
        return tmp.name
