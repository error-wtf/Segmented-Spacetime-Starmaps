#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connection lines and path visualization.

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import List, Tuple, Optional


def create_connection_lines(
    stars: pd.DataFrame,
    max_distance: float = 5.0,
    min_connections: int = 2,
    max_connections: int = 5
) -> List[go.Scatter3d]:
    """
    Create connection lines between nearby stars.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog with x, y, z
    max_distance : float
        Maximum connection distance in parsecs
    min_connections : int
        Minimum connections per star
    max_connections : int
        Maximum connections per star
        
    Returns
    -------
    list
        List of line traces
        
    Notes
    -----
    Creates web of connections showing spatial relationships.
    Useful for constellation-like patterns.
    """
    traces = []
    
    positions = stars[['x', 'y', 'z']].values
    n_stars = len(stars)
    
    # Calculate all pairwise distances
    from scipy.spatial.distance import cdist
    distances = cdist(positions, positions)
    
    # For each star, find nearest neighbors
    connected = set()
    
    for i in range(n_stars):
        # Get indices sorted by distance
        neighbors = np.argsort(distances[i])
        
        # Skip self (distance=0)
        neighbors = neighbors[1:]
        
        # Connect to nearest neighbors within max_distance
        n_connected = 0
        for j in neighbors:
            if n_connected >= max_connections:
                break
            
            dist = distances[i, j]
            if dist > max_distance:
                break
            
            # Avoid duplicate connections
            pair = tuple(sorted([i, j]))
            if pair in connected:
                continue
            
            connected.add(pair)
            n_connected += 1
            
            # Create line trace
            trace = go.Scatter3d(
                x=[positions[i, 0], positions[j, 0]],
                y=[positions[i, 1], positions[j, 1]],
                z=[positions[i, 2], positions[j, 2]],
                mode='lines',
                line=dict(
                    color='rgba(100,150,255,0.3)',
                    width=1
                ),
                showlegend=False,
                hoverinfo='skip'
            )
            traces.append(trace)
    
    return traces


def create_path_trace(
    waypoints: List[Tuple[float, float, float]],
    mode: str = 'geodesic',
    n_samples: int = 100,
    color: str = 'yellow'
) -> go.Scatter3d:
    """
    Create path between waypoints.
    
    Parameters
    ----------
    waypoints : list
        List of (x, y, z) positions
    mode : str
        'geodesic' or 'straight'
    n_samples : int
        Points along path
    color : str
        Path color
        
    Returns
    -------
    go.Scatter3d
        Path trace
        
    Notes
    -----
    'geodesic': Curved path (simulates SSZ effects)
    'straight': Direct line (Minkowski)
    """
    if len(waypoints) < 2:
        return None
    
    # Parametric path through all waypoints
    segments = len(waypoints) - 1
    t_total = np.linspace(0, segments, n_samples)
    
    x_path = np.interp(t_total, np.arange(len(waypoints)), 
                       [w[0] for w in waypoints])
    y_path = np.interp(t_total, np.arange(len(waypoints)), 
                       [w[1] for w in waypoints])
    z_path = np.interp(t_total, np.arange(len(waypoints)), 
                       [w[2] for w in waypoints])
    
    if mode == 'geodesic':
        # Add curvature (simplified)
        # Real geodesic needs full metric calculation
        curvature = 0.1 * np.sin(np.pi * t_total / segments)
        z_path += curvature
    
    trace = go.Scatter3d(
        x=x_path,
        y=y_path,
        z=z_path,
        mode='lines',
        line=dict(color=color, width=4),
        name=f'Path ({mode})',
        hoverinfo='text',
        text=[f'Path point {i}' for i in range(len(x_path))]
    )
    
    return trace


def create_distance_ruler(
    pos1: Tuple[float, float, float],
    pos2: Tuple[float, float, float],
    distance_mink: float,
    distance_ssz: float
) -> List[go.Scatter3d]:
    """
    Create distance ruler showing Mink vs SSZ distances.
    
    Parameters
    ----------
    pos1, pos2 : tuples
        Star positions
    distance_mink : float
        Minkowski distance
    distance_ssz : float
        SSZ distance
        
    Returns
    -------
    list
        Ruler traces (Mink line + SSZ line + labels)
    """
    traces = []
    
    # Minkowski line (straight, cyan)
    traces.append(go.Scatter3d(
        x=[pos1[0], pos2[0]],
        y=[pos1[1], pos2[1]],
        z=[pos1[2], pos2[2]],
        mode='lines+text',
        line=dict(color='cyan', width=3),
        text=['', f'{distance_mink:.2f} pc (Mink)'],
        textposition='middle center',
        textfont=dict(color='cyan', size=10),
        name='Minkowski Distance',
        hoverinfo='text',
        hovertext=f'Minkowski: {distance_mink:.2f} pc'
    ))
    
    # SSZ line (slightly offset, magenta)
    offset = 0.5
    traces.append(go.Scatter3d(
        x=[pos1[0] + offset, pos2[0] + offset],
        y=[pos1[1], pos2[1]],
        z=[pos1[2], pos2[2]],
        mode='lines+text',
        line=dict(color='magenta', width=3, dash='dash'),
        text=['', f'{distance_ssz:.2f} pc (SSZ)'],
        textposition='top center',
        textfont=dict(color='magenta', size=10),
        name='SSZ Distance',
        hoverinfo='text',
        hovertext=f'SSZ: {distance_ssz:.2f} pc (Δ={distance_ssz-distance_mink:.2f} pc)'
    ))
    
    return traces


def create_constellation_pattern(
    star_positions: np.ndarray,
    pattern_indices: List[List[int]],
    name: str = 'Constellation'
) -> List[go.Scatter3d]:
    """
    Create constellation pattern from star indices.
    
    Parameters
    ----------
    star_positions : ndarray
        Array of (x, y, z) positions
    pattern_indices : list of lists
        Each sublist is a connected line segment
        e.g., [[0,1,2], [1,3], [2,4]]
    name : str
        Constellation name
        
    Returns
    -------
    list
        Pattern traces
        
    Examples
    --------
    >>> # Create simple triangle
    >>> positions = np.array([[0,0,0], [1,0,0], [0.5,1,0]])
    >>> pattern = [[0,1,2,0]]  # Close the triangle
    >>> traces = create_constellation_pattern(positions, pattern, 'Triangle')
    """
    traces = []
    
    for segment in pattern_indices:
        if len(segment) < 2:
            continue
        
        x = [star_positions[i][0] for i in segment]
        y = [star_positions[i][1] for i in segment]
        z = [star_positions[i][2] for i in segment]
        
        trace = go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(color='rgba(255,255,100,0.6)', width=2),
            name=name,
            showlegend=True,
            hoverinfo='text',
            text=f'{name} pattern'
        )
        traces.append(trace)
    
    return traces


def highlight_star_neighborhood(
    star_pos: Tuple[float, float, float],
    radius: float = 10.0,
    n_points: int = 50,
    color: str = 'rgba(255,255,0,0.2)'
) -> go.Scatter3d:
    """
    Highlight spherical neighborhood around a star.
    
    Parameters
    ----------
    star_pos : tuple
        Center position
    radius : float
        Neighborhood radius
    n_points : int
        Sphere resolution
    color : str
        Highlight color
        
    Returns
    -------
    go.Scatter3d
        Sphere trace
    """
    # Create sphere surface points
    phi = np.linspace(0, 2*np.pi, n_points)
    theta = np.linspace(0, np.pi, n_points//2)
    phi_grid, theta_grid = np.meshgrid(phi, theta)
    
    x = star_pos[0] + radius * np.sin(theta_grid) * np.cos(phi_grid)
    y = star_pos[1] + radius * np.sin(theta_grid) * np.sin(phi_grid)
    z = star_pos[2] + radius * np.cos(theta_grid)
    
    # Flatten for Scatter3d
    trace = go.Scatter3d(
        x=x.flatten(),
        y=y.flatten(),
        z=z.flatten(),
        mode='markers',
        marker=dict(
            size=2,
            color=color,
            opacity=0.3
        ),
        name='Neighborhood',
        showlegend=False,
        hoverinfo='skip'
    )
    
    return trace
