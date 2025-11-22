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

# SSZ Parameters
ALPHA = 0.12
R_C = 1.9  # pc

def r_schwarzschild(M):
    """Schwarzschild radius"""
    return 2 * G * M / (C**2)

def Xi(r, r_s):
    """Segment density"""
    r_c = R_C * r_s
    return ALPHA * np.exp(-(r / r_c)**2)

def create_domains_plot_png():
    """
    g₁/g₂ Domains Plot - Returns PIL Image
    """
    M = 4.3e6 * M_SUN  # Sgr A*
    r_s = r_schwarzschild(M)
    r_s_pc = r_s / PC_TO_M
    
    # Radius range
    r_min_pc = 1e-9
    r_max_pc = 1e4
    r_range_pc = np.logspace(np.log10(r_min_pc), np.log10(r_max_pc), 500)
    r_range = r_range_pc * PC_TO_M
    
    # Calculate Xi
    xi_values = np.array([Xi(r, r_s) for r in r_range])
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='#0a0a1f')
    ax.set_facecolor('#000010')
    
    # Plot Xi(r)
    ax.plot(r_range_pc, xi_values, color='orange', linewidth=3, label='Ξ(r) = Segment Density')
    ax.fill_between(r_range_pc, 0, xi_values, color='orange', alpha=0.2)
    
    # Mark r_c
    r_c_pc = R_C * r_s_pc
    ax.axvline(r_c_pc, color='red', linestyle='--', linewidth=2, label=f'r_c = {r_c_pc:.2e} pc')
    
    # Styling
    ax.set_xscale('log')
    ax.set_xlabel('Radius [parsec]', fontsize=14, color='white', fontweight='bold')
    ax.set_ylabel('Ξ(r) = 1 - γ(r)', fontsize=14, color='white', fontweight='bold')
    ax.set_title('Segment Density Ξ(r)\nγ(r) = 1 - α·exp[-(r/r_c)²], α=0.12, r_c=1.9 pc', 
                 fontsize=16, color='white', fontweight='bold', pad=20)
    ax.set_ylim(0, 0.15)
    ax.grid(True, alpha=0.3, color='gray')
    ax.legend(fontsize=12, facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.tick_params(colors='white')
    
    # Convert to PIL Image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#0a0a1f')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    
    return img


def create_time_dilation_png():
    """
    Time Dilation Plot - Returns PIL Image
    """
    M = 4.3e6 * M_SUN
    r_s = r_schwarzschild(M)
    
    # r/r_s range
    r_ratio = np.linspace(1.1, 100, 500)
    
    # SSZ: A_ssz = D(r) = 1/(1 + Xi)
    xi_vals = np.array([Xi(r * r_s, r_s) for r in r_ratio])
    A_ssz = 1 / (1 + xi_vals)
    
    # GR: A_gr = 1 - 1/r
    A_gr = 1 - 1/r_ratio
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='#0a0a1f')
    ax.set_facecolor('#000010')
    
    # Plot both
    ax.plot(r_ratio, A_ssz, color='#00ff00', linewidth=3, label='A_SSZ (Finite at r=0)')
    ax.plot(r_ratio, A_gr, color='#ff6b6b', linewidth=3, linestyle='--', label='A_GR (Singular!)')
    
    # Mark event horizon
    ax.axvline(1, color='yellow', linestyle=':', linewidth=2, alpha=0.7, label='r_s (Event Horizon)')
    
    # Styling
    ax.set_xscale('log')
    ax.set_xlabel('r / r_s', fontsize=14, color='white', fontweight='bold')
    ax.set_ylabel('A(r)', fontsize=14, color='white', fontweight='bold')
    ax.set_title('Metric Function A(r) - SSZ vs GR\nΑ_SSZ = D(r) = 1/(1 + Xi), Mobil finite!',
                 fontsize=16, color='white', fontweight='bold', pad=20)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3, color='gray')
    ax.legend(fontsize=12, facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.tick_params(colors='white')
    
    # Convert to PIL Image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#0a0a1f')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    
    return img


def create_radial_stretch_png():
    """
    Radial Stretch Plot - Returns PIL Image
    """
    M = 4.3e6 * M_SUN
    r_s = r_schwarzschild(M)
    
    r_ratio = np.linspace(1.01, 1000, 500)
    
    # SSZ: B_ssz = gamma(r)
    xi_vals = np.array([Xi(r * r_s, r_s) for r in r_ratio])
    B_ssz = 1 - xi_vals
    
    # GR: B_gr = 1/(1-1/r)
    B_gr = 1 / (1 - 1/r_ratio)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='#0a0a1f')
    ax.set_facecolor('#000010')
    
    ax.plot(r_ratio, B_ssz, color='#00ff00', linewidth=3, label='γ_SSZ (Finite)')
    ax.plot(r_ratio, B_gr, color='#ff6b6b', linewidth=3, linestyle='--', label='B_GR (Singular)')
    
    ax.axvline(1, color='yellow', linestyle=':', linewidth=2, alpha=0.7)
    ax.axhline(1, color='white', linestyle=':', linewidth=1, alpha=0.5)
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('r / r_s', fontsize=14, color='white', fontweight='bold')
    ax.set_ylabel('dr/dt = γ(r)', fontsize=14, color='white', fontweight='bold')
    ax.set_title('Proper Time dr/dt - SSZ vs GR\nSSZ hat finite proper time at singularity',
                 fontsize=16, color='white', fontweight='bold', pad=20)
    ax.set_ylim(0.1, 10)
    ax.grid(True, alpha=0.3, color='gray')
    ax.legend(fontsize=12, facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.tick_params(colors='white')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#0a0a1f')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    
    return img


def create_combined_analysis_png():
    """
    Combined 4-Panel Analysis - Returns PIL Image
    """
    M = 4.3e6 * M_SUN
    r_s = r_schwarzschild(M)
    r_ratio = np.linspace(1.1, 100, 200)
    
    xi_vals = np.array([Xi(r * r_s, r_s) for r in r_ratio])
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor='#0a0a1f')
    fig.suptitle('Complete SSZ Physics Analysis', fontsize=18, color='white', fontweight='bold')
    
    for ax in axes.flat:
        ax.set_facecolor('#000010')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3, color='gray')
    
    # Panel 1: Segment Density
    axes[0, 0].plot(r_ratio, xi_vals, color='orange', linewidth=2)
    axes[0, 0].set_xlabel('r/r_s', color='white')
    axes[0, 0].set_ylabel('Ξ(r)', color='white')
    axes[0, 0].set_title('Segment Density', color='white', fontweight='bold')
    axes[0, 0].set_xscale('log')
    
    # Panel 2: Time Dilation
    A_ssz = 1 / (1 + xi_vals)
    axes[0, 1].plot(r_ratio, A_ssz, color='#00ff00', linewidth=2)
    axes[0, 1].set_xlabel('r/r_s', color='white')
    axes[0, 1].set_ylabel('D(r)', color='white')
    axes[0, 1].set_title('Time Dilation', color='white', fontweight='bold')
    axes[0, 1].set_xscale('log')
    
    # Panel 3: Gamma
    gamma = 1 - xi_vals
    axes[1, 0].plot(r_ratio, gamma, color='cyan', linewidth=2)
    axes[1, 0].set_xlabel('r/r_s', color='white')
    axes[1, 0].set_ylabel('γ(r)', color='white')
    axes[1, 0].set_title('Radial Metric', color='white', fontweight='bold')
    axes[1, 0].set_xscale('log')
    
    # Panel 4: Proper Time
    dtau_dr = gamma / A_ssz
    axes[1, 1].plot(r_ratio, dtau_dr, color='magenta', linewidth=2)
    axes[1, 1].set_xlabel('r/r_s', color='white')
    axes[1, 1].set_ylabel('dτ/dr', color='white')
    axes[1, 1].set_title('Proper Time', color='white', fontweight='bold')
    axes[1, 1].set_xscale('log')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#0a0a1f')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    
    return img
