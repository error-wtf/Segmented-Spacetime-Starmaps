#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gravitational halo visualization for SSZ.

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import List, Tuple


def create_gravitational_halo(
    star_pos: Tuple[float, float, float],
    mass_msun: float,
    halo_radius: float = 10.0,
    n_points: int = 20,
    opacity: float = 0.3
) -> go.Surface:
    """
    Create a spherical halo around a massive star.
    
    Parameters
    ----------
    star_pos : tuple
        (x, y, z) position of star
    mass_msun : float
        Star mass in solar masses
    halo_radius : float
        Halo radius in parsecs
    n_points : int
        Resolution (points per dimension)
    opacity : float
        Halo transparency
        
    Returns
    -------
    go.Surface
        Plotly surface object for halo
        
    Notes
    -----
    Halo intensity ∝ 1/r² (gravitational field strength)
    Used to visualize gravitational influence zone.
    """
    # Create spherical mesh
    theta = np.linspace(0, np.pi, n_points)
    phi = np.linspace(0, 2*np.pi, n_points)
    theta_grid, phi_grid = np.meshgrid(theta, phi)
    
    # Spherical coordinates
    x = star_pos[0] + halo_radius * np.sin(theta_grid) * np.cos(phi_grid)
    y = star_pos[1] + halo_radius * np.sin(theta_grid) * np.sin(phi_grid)
    z = star_pos[2] + halo_radius * np.cos(theta_grid)
    
    # Color intensity ∝ mass (visual only)
    intensity = np.log10(mass_msun + 1) / 10.0
    intensity = np.clip(intensity, 0, 1)
    
    # Create surface
    surface = go.Surface(
        x=x, y=y, z=z,
        surfacecolor=np.ones_like(x) * intensity,
        colorscale='Blues',
        showscale=False,
        opacity=opacity,
        name='Gravitational Halo',
        hoverinfo='skip'
    )
    
    return surface


def create_ssz_field_iso_surface(
    star_pos: Tuple[float, float, float],
    stretch_threshold: float = 1.5,
    grid_size: int = 20,
    extent: float = 20.0
) -> go.Isosurface:
    """
    Create isosurface of SSZ stretch factor.
    
    Parameters
    ----------
    star_pos : tuple
        Center position
    stretch_threshold : float
        Stretch factor threshold for isosurface
    grid_size : int
        Grid resolution
    extent : float
        Grid extent in parsecs
        
    Returns
    -------
    go.Isosurface
        Plotly isosurface
        
    Notes
    -----
    Visualizes regions where stretch > threshold.
    Shows SSZ "influence bubble".
    """
    # Create 3D grid
    x = np.linspace(-extent, extent, grid_size) + star_pos[0]
    y = np.linspace(-extent, extent, grid_size) + star_pos[1]
    z = np.linspace(-extent, extent, grid_size) + star_pos[2]
    X, Y, Z = np.meshgrid(x, y, z)
    
    # Distance from star
    r = np.sqrt((X - star_pos[0])**2 + 
                (Y - star_pos[1])**2 + 
                (Z - star_pos[2])**2)
    
    # Simplified SSZ stretch (decreases with distance)
    # Real SSZ: stretch = 1 + Xi(r)
    # Here: simple 1/r falloff for visualization
    stretch = 1.0 + 5.0 / (r + 1.0)
    
    # Create isosurface
    isosurface = go.Isosurface(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=stretch.flatten(),
        isomin=stretch_threshold,
        isomax=stretch_threshold + 0.1,
        opacity=0.2,
        surface_count=1,
        colorscale='Reds',
        showscale=False,
        name=f'SSZ Field (stretch>{stretch_threshold})',
        hoverinfo='skip'
    )
    
    return isosurface


def create_connection_halo(
    pos1: Tuple[float, float, float],
    pos2: Tuple[float, float, float],
    n_points: int = 50,
    tube_radius: float = 0.5
) -> go.Scatter3d:
    """
    Create tube connection between two stars.
    
    Parameters
    ----------
    pos1, pos2 : tuples
        Star positions
    n_points : int
        Points along tube
    tube_radius : float
        Tube radius
        
    Returns
    -------
    go.Scatter3d
        Tube trace
        
    Notes
    -----
    Used to show gravitational connections or
    paths through SSZ spacetime.
    """
    # Parametric line
    t = np.linspace(0, 1, n_points)
    x = pos1[0] + t * (pos2[0] - pos1[0])
    y = pos1[1] + t * (pos2[1] - pos1[1])
    z = pos1[2] + t * (pos2[2] - pos1[2])
    
    # Tube effect via marker size variation
    # Size decreases toward middle (visual depth)
    sizes = tube_radius * (1.0 + 0.5 * np.sin(np.pi * t))
    
    trace = go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers+lines',
        marker=dict(
            size=sizes,
            color=t,
            colorscale='Viridis',
            showscale=False,
            opacity=0.6
        ),
        line=dict(
            color='rgba(100,100,255,0.3)',
            width=2
        ),
        name='Connection',
        hoverinfo='skip'
    )
    
    return trace


def create_grid_overlay(
    extent: float = 50.0,
    spacing: float = 10.0,
    opacity: float = 0.1
) -> List[go.Scatter3d]:
    """
    Create 3D grid overlay for spatial reference.
    
    Parameters
    ----------
    extent : float
        Grid extent in parsecs
    spacing : float
        Grid line spacing
    opacity : float
        Grid transparency
        
    Returns
    -------
    list
        List of grid line traces
        
    Notes
    -----
    Helps visualize spatial scale and deformation.
    """
    traces = []
    
    # Create grid lines
    coords = np.arange(-extent, extent + spacing, spacing)
    
    # XY plane lines (parallel to X)
    for y in coords:
        for z in [-extent, extent]:
            traces.append(go.Scatter3d(
                x=[-extent, extent],
                y=[y, y],
                z=[z, z],
                mode='lines',
                line=dict(color='rgba(255,255,255,0.1)', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # XY plane lines (parallel to Y)
    for x in coords:
        for z in [-extent, extent]:
            traces.append(go.Scatter3d(
                x=[x, x],
                y=[-extent, extent],
                z=[z, z],
                mode='lines',
                line=dict(color='rgba(255,255,255,0.1)', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    return traces
