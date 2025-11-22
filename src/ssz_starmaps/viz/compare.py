"""
Side-by-side comparison plots: Minkowski vs SSZ.

© 2025 Carmen Wrede, Lino Casu
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional


PHI = 1.618034  # Golden ratio


def plot_sky_comparison(
    df: pd.DataFrame,
    output: Union[str, Path, None] = None,
    dpi: int = 300,
    fov_center: Optional[tuple] = None,
    fov_deg: Optional[float] = None,
    figsize: tuple = (16, 8)
) -> plt.Figure:
    """
    Create side-by-side sky map: Minkowski vs SSZ.
    
    Parameters
    ----------
    df : pd.DataFrame
        Transformed catalog with columns: ra, dec, distance_pc,
        ra_ssz, dec_ssz, distance_ssz_pc
    output : str or Path, optional
        Output filename (if None, displays interactively)
    dpi : int
        Resolution (default: 300)
    fov_center : tuple of float, optional
        (ra, dec) center for field of view
    fov_deg : float, optional
        Field of view size [degrees]
    figsize : tuple
        Figure size in inches
        
    Returns
    -------
    matplotlib.Figure
        The created figure
        
    Examples
    --------
    >>> plot_sky_comparison(stars_ssz, output='comparison.png')
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    fig.patch.set_facecolor('#0a0a1e')  # Dark background
    
    # Configure axes
    for ax in (ax1, ax2):
        ax.set_facecolor('#0a0a1e')
        ax.tick_params(colors='white', labelsize=10)
        for spine in ax.spines.values():
            spine.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
    
    # Marker size scaling by distance
    size_minkowski = 100 / df['distance_pc']
    size_ssz = 100 / df['distance_ssz_pc']
    
    # Left: Minkowski
    ax1.scatter(
        df['ra'], df['dec'],
        s=size_minkowski,
        alpha=0.6,
        c='#00BFFF',  # Deep sky blue
        edgecolors='white',
        linewidths=0.3,
        label='Stars'
    )
    ax1.set_xlabel('Right Ascension [deg]', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Declination [deg]', fontsize=12, fontweight='bold')
    ax1.set_title('Minkowski (Standard Spacetime)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.2, color='white', linestyle=':')
    
    # Right: SSZ
    ax2.scatter(
        df['ra_ssz'], df['dec_ssz'],
        s=size_ssz,
        alpha=0.6,
        c='#FF1493',  # Deep pink
        edgecolors='white',
        linewidths=0.3,
        label='Stars'
    )
    ax2.set_xlabel('Right Ascension [deg]', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Declination [deg]', fontsize=12, fontweight='bold')
    ax2.set_title('SSZ (φ-Deformed Spacetime)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.2, color='white', linestyle=':')
    
    # Set same limits if fov specified
    if fov_center and fov_deg:
        ra_c, dec_c = fov_center
        half = fov_deg / 2
        for ax in (ax1, ax2):
            ax.set_xlim(ra_c - half, ra_c + half)
            ax.set_ylim(dec_c - half, dec_c + half)
    
    # Add SSZ parameters text box
    r_s = 2953  # meters (Sun)
    n_stars = len(df)
    mean_stretch = df['stretch_factor'].mean()
    
    params_text = (
        f"SSZ Parameters:\n"
        f"φ = {PHI:.6f}\n"
        f"r_s = {r_s:.0f} m\n"
        f"\n"
        f"N_stars = {n_stars}\n"
        f"<stretch> = {mean_stretch:.4f}"
    )
    
    ax2.text(
        0.02, 0.98, params_text,
        transform=ax2.transAxes,
        va='top', ha='left',
        fontsize=10,
        family='monospace',
        color='white',
        bbox=dict(
            boxstyle='round,pad=0.5',
            facecolor='#1a1a2e',
            edgecolor='#FFD700',
            linewidth=2,
            alpha=0.9
        )
    )
    
    plt.tight_layout()
    
    if output:
        plt.savefig(output, dpi=dpi, facecolor='#0a0a1e', bbox_inches='tight')
        print(f"Saved: {output}")
        plt.close()
    else:
        plt.show()
    
    return fig


def plot_distance_histogram(
    df: pd.DataFrame,
    output: Union[str, Path, None] = None,
    bins: int = 50,
    dpi: int = 300,
    figsize: tuple = (12, 10)
) -> plt.Figure:
    """
    Compare distance distributions: Minkowski vs SSZ.
    
    Parameters
    ----------
    df : pd.DataFrame
        Transformed catalog
    output : str or Path, optional
        Output filename
    bins : int
        Number of histogram bins
    dpi : int
        Resolution
    figsize : tuple
        Figure size
        
    Returns
    -------
    matplotlib.Figure
        The created figure
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize)
    fig.patch.set_facecolor('#0a0a1e')
    
    for ax in (ax1, ax2, ax3):
        ax.set_facecolor('#0a0a1e')
        ax.tick_params(colors='white', labelsize=10)
        for spine in ax.spines.values():
            spine.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
    
    # Panel 1: Minkowski distances
    ax1.hist(
        df['distance_pc'],
        bins=bins,
        alpha=0.7,
        color='#00BFFF',
        edgecolor='white',
        linewidth=1.5
    )
    ax1.set_xlabel('Distance [pc]', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax1.set_title('Minkowski Distance Distribution', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.2, color='white', linestyle=':')
    
    mean_m = df['distance_pc'].mean()
    ax1.axvline(mean_m, color='#FFD700', linestyle='--', linewidth=2,
                label=f'Mean = {mean_m:.1f} pc')
    ax1.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    
    # Panel 2: SSZ distances
    ax2.hist(
        df['distance_ssz_pc'],
        bins=bins,
        alpha=0.7,
        color='#FF1493',
        edgecolor='white',
        linewidth=1.5
    )
    ax2.set_xlabel('Distance [pc]', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax2.set_title('SSZ Distance Distribution (φ-Stretched)', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.2, color='white', linestyle=':')
    
    mean_ssz = df['distance_ssz_pc'].mean()
    ax2.axvline(mean_ssz, color='#FFD700', linestyle='--', linewidth=2,
                label=f'Mean = {mean_ssz:.1f} pc')
    ax2.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    
    # Panel 3: Stretch factor distribution
    ax3.hist(
        df['stretch_factor'],
        bins=bins,
        alpha=0.7,
        color='#00FF00',
        edgecolor='white',
        linewidth=1.5
    )
    ax3.set_xlabel('Stretch Factor', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax3.set_title('Radial Stretch Distribution', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.2, color='white', linestyle=':')
    
    mean_stretch = df['stretch_factor'].mean()
    ax3.axvline(mean_stretch, color='#FFD700', linestyle='--', linewidth=2,
                label=f'Mean = {mean_stretch:.4f}')
    ax3.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    
    # Statistics text box
    stats_text = (
        f"Statistics:\n"
        f"N = {len(df)}\n"
        f"\n"
        f"Distance Shift:\n"
        f"  Δ<d> = {mean_ssz - mean_m:.2f} pc\n"
        f"  Rel = {(mean_ssz/mean_m - 1)*100:.2f}%\n"
        f"\n"
        f"Stretch:\n"
        f"  <stretch> = {mean_stretch:.4f}\n"
        f"  σ = {df['stretch_factor'].std():.4f}"
    )
    
    ax3.text(
        0.98, 0.98, stats_text,
        transform=ax3.transAxes,
        va='top', ha='right',
        fontsize=10,
        family='monospace',
        color='white',
        bbox=dict(
            boxstyle='round,pad=0.5',
            facecolor='#1a1a2e',
            edgecolor='#00FF00',
            linewidth=2,
            alpha=0.9
        )
    )
    
    plt.tight_layout()
    
    if output:
        plt.savefig(output, dpi=dpi, facecolor='#0a0a1e', bbox_inches='tight')
        print(f"Saved: {output}")
        plt.close()
    else:
        plt.show()
    
    return fig


def plot_3d_comparison(
    df: pd.DataFrame,
    output: Union[str, Path, None] = None,
    elev: float = 20,
    azim: float = 45
) -> plt.Figure:
    """
    3D scatter plot comparison (requires mpl_toolkits.mplot3d).
    
    Parameters
    ----------
    df : pd.DataFrame
        Transformed catalog
    output : str or Path, optional
        Output filename
    elev : float
        Elevation angle for 3D view
    azim : float
        Azimuth angle for 3D view
        
    Returns
    -------
    matplotlib.Figure
    """
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure(figsize=(16, 8))
    fig.patch.set_facecolor('#0a0a1e')
    
    # Convert to Cartesian
    ra_rad = np.deg2rad(df['ra'])
    dec_rad = np.deg2rad(df['dec'])
    
    # Minkowski
    x_m = df['distance_pc'] * np.cos(dec_rad) * np.cos(ra_rad)
    y_m = df['distance_pc'] * np.cos(dec_rad) * np.sin(ra_rad)
    z_m = df['distance_pc'] * np.sin(dec_rad)
    
    # SSZ
    x_ssz = df['distance_ssz_pc'] * np.cos(dec_rad) * np.cos(ra_rad)
    y_ssz = df['distance_ssz_pc'] * np.cos(dec_rad) * np.sin(ra_rad)
    z_ssz = df['distance_ssz_pc'] * np.sin(dec_rad)
    
    # Left: Minkowski
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.scatter(x_m, y_m, z_m, c='#00BFFF', alpha=0.6, s=20)
    ax1.set_xlabel('X [pc]', color='white')
    ax1.set_ylabel('Y [pc]', color='white')
    ax1.set_zlabel('Z [pc]', color='white')
    ax1.set_title('Minkowski', color='white', fontweight='bold')
    ax1.view_init(elev=elev, azim=azim)
    ax1.set_facecolor('#0a0a1e')
    
    # Right: SSZ
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.scatter(x_ssz, y_ssz, z_ssz, c='#FF1493', alpha=0.6, s=20)
    ax2.set_xlabel('X [pc]', color='white')
    ax2.set_ylabel('Y [pc]', color='white')
    ax2.set_zlabel('Z [pc]', color='white')
    ax2.set_title('SSZ (φ-Deformed)', color='white', fontweight='bold')
    ax2.view_init(elev=elev, azim=azim)
    ax2.set_facecolor('#0a0a1e')
    
    plt.tight_layout()
    
    if output:
        plt.savefig(output, dpi=300, facecolor='#0a0a1e', bbox_inches='tight')
        print(f"Saved: {output}")
        plt.close()
    else:
        plt.show()
    
    return fig
