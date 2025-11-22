#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glow effects for SSZ visualization.

Glow intensity proportional to SSZ effects (stretch factor, time dilation).

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import pandas as pd
from typing import Tuple


def calculate_glow_intensity(
    stretch_factor: np.ndarray,
    D_ssz: np.ndarray,
    mode: str = 'stretch'
) -> np.ndarray:
    """
    Calculate glow intensity based on SSZ parameters.
    
    Parameters
    ----------
    stretch_factor : array
        SSZ radial stretch factor (1 + Xi)
    D_ssz : array
        SSZ time dilation factor
    mode : str
        'stretch', 'dilation', or 'combined'
        
    Returns
    -------
    array
        Glow intensity (normalized 0-1)
        
    Notes
    -----
    Glow intensity visualizes SSZ effects:
    - Higher stretch → Brighter glow
    - Lower D_ssz (more dilation) → Brighter glow
    """
    if mode == 'stretch':
        # Intensity ∝ (stretch - 1)
        # Range: [1, 2] → [0, 1]
        intensity = (stretch_factor - 1.0)
        intensity = np.clip(intensity, 0, 1)
        
    elif mode == 'dilation':
        # Intensity ∝ (1 - D_ssz)
        # D_ssz = 0.5 → intensity = 0.5
        intensity = 1.0 - D_ssz
        intensity = np.clip(intensity, 0, 1)
        
    elif mode == 'combined':
        # Combined effect
        stretch_contrib = (stretch_factor - 1.0) * 0.5
        dilation_contrib = (1.0 - D_ssz) * 0.5
        intensity = stretch_contrib + dilation_contrib
        intensity = np.clip(intensity, 0, 1)
        
    else:
        raise ValueError(f"Unknown mode: {mode}")
    
    return intensity


def apply_glow_effect(
    stars: pd.DataFrame,
    base_size: float = 5.0,
    glow_factor: float = 2.0,
    mode: str = 'stretch'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply glow effect to star markers.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog with stretch_factor and D_ssz
    base_size : float
        Base marker size
    glow_factor : float
        Maximum size multiplier for glow
    mode : str
        Glow mode
        
    Returns
    -------
    sizes : array
        Marker sizes with glow
    opacities : array
        Marker opacities with glow
        
    Examples
    --------
    >>> sizes, opacities = apply_glow_effect(stars_ssz)
    >>> # Use in Plotly:
    >>> fig.add_trace(go.Scatter3d(
    ...     marker=dict(size=sizes, opacity=opacities)
    ... ))
    """
    # Calculate glow intensity
    intensity = calculate_glow_intensity(
        stars['stretch_factor'].values,
        stars['D_ssz'].values,
        mode=mode
    )
    
    # Sizes: base + glow
    sizes = base_size * (1.0 + intensity * (glow_factor - 1.0))
    
    # Opacities: slightly higher for bright glows
    opacities = 0.7 + 0.3 * intensity
    opacities = np.clip(opacities, 0.5, 1.0)
    
    return sizes, opacities


def create_glow_gradient(
    n_levels: int = 5,
    max_radius: float = 2.0
) -> list:
    """
    Create concentric circles for glow effect.
    
    Parameters
    ----------
    n_levels : int
        Number of glow layers
    max_radius : float
        Maximum glow radius (relative to base size)
        
    Returns
    -------
    list
        List of (radius, opacity) tuples for each layer
        
    Notes
    -----
    Creates multiple transparent layers for smooth glow.
    Use with Plotly's marker.line settings.
    """
    layers = []
    
    for i in range(n_levels):
        # Radius increases linearly
        radius = 1.0 + (max_radius - 1.0) * (i + 1) / n_levels
        
        # Opacity decreases exponentially
        opacity = np.exp(-2.0 * i / n_levels)
        
        layers.append((radius, opacity))
    
    return layers


def get_color_temperature_glow(
    stretch_factor: np.ndarray
) -> np.ndarray:
    """
    Get color temperature shift due to SSZ.
    
    Parameters
    ----------
    stretch_factor : array
        SSZ stretch factor
        
    Returns
    -------
    array
        Temperature shift [K]
        
    Notes
    -----
    Higher stretch → Cooler appearance (redshift analog)
    Lower stretch → Hotter appearance (blueshift analog)
    
    This is a visual effect, not physical temperature!
    """
    # Baseline: neutral (0 K shift)
    # Stretch > 1: Redshift → Cooler (-500 K per unit)
    # Stretch < 1: Blueshift → Hotter (+500 K per unit)
    
    temp_shift = -500.0 * (stretch_factor - 1.0)
    
    return temp_shift
