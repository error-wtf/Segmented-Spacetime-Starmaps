#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coordinate transformations for SSZ Skymap.

Handles conversions between:
- RA/Dec → Galactic
- Spherical → Cartesian
- Minkowski → SSZ

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional

try:
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    ASTROPY_AVAILABLE = True
except ImportError:
    ASTROPY_AVAILABLE = False


def galactic_to_cartesian(
    ra: np.ndarray,
    dec: np.ndarray,
    distance_pc: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert RA/Dec/Distance to Galactic Cartesian coordinates.
    
    Parameters
    ----------
    ra : array
        Right ascension [degrees]
    dec : array
        Declination [degrees]
    distance_pc : array
        Distance [parsecs]
        
    Returns
    -------
    x, y, z : arrays
        Galactic Cartesian coordinates [parsecs]
        
    Notes
    -----
    Uses Astropy if available, otherwise simplified conversion.
    Galactic center at (0,0,0), Sun at (~8000, 0, ~20) pc.
    """
    if ASTROPY_AVAILABLE:
        coords = SkyCoord(
            ra=ra * u.deg,
            dec=dec * u.deg,
            distance=distance_pc * u.pc,
            frame='icrs'
        )
        gal = coords.galactic
        x, y, z = gal.cartesian.xyz.to(u.pc).value
    else:
        # Simplified conversion (less accurate)
        ra_rad = np.radians(ra)
        dec_rad = np.radians(dec)
        x = distance_pc * np.cos(dec_rad) * np.cos(ra_rad)
        y = distance_pc * np.cos(dec_rad) * np.sin(ra_rad)
        z = distance_pc * np.sin(dec_rad)
    
    return x, y, z


def cartesian_to_spherical(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert Cartesian to Spherical coordinates.
    
    Parameters
    ----------
    x, y, z : arrays
        Cartesian coordinates
        
    Returns
    -------
    r, theta, phi : arrays
        Spherical coordinates (radius, polar angle, azimuthal angle)
        theta in [0, π], phi in [0, 2π]
    """
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(np.clip(z / r, -1, 1))  # polar angle
    phi = np.arctan2(y, x)  # azimuthal angle
    
    return r, theta, phi


def spherical_to_cartesian(
    r: np.ndarray,
    theta: np.ndarray,
    phi: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert Spherical to Cartesian coordinates.
    
    Parameters
    ----------
    r, theta, phi : arrays
        Spherical coordinates
        
    Returns
    -------
    x, y, z : arrays
        Cartesian coordinates
    """
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    
    return x, y, z


def apply_ssz_stretch(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    stretch_factor: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Apply SSZ radial stretch to coordinates.
    
    Parameters
    ----------
    x, y, z : arrays
        Original Cartesian coordinates
    stretch_factor : array
        SSZ stretch factor (1 + Xi)
        
    Returns
    -------
    x_ssz, y_ssz, z_ssz : arrays
        SSZ-stretched coordinates
        
    Notes
    -----
    SSZ stretches space radially from the observer.
    r_ssz = r * (1 + Xi(r))
    """
    x_ssz = x * stretch_factor
    y_ssz = y * stretch_factor
    z_ssz = z * stretch_factor
    
    return x_ssz, y_ssz, z_ssz


def prepare_star_coordinates(
    stars: pd.DataFrame,
    observer_pos: Optional[Tuple[float, float, float]] = None
) -> pd.DataFrame:
    """
    Prepare star coordinates for visualization.
    
    Adds x, y, z columns in Galactic Cartesian frame.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog with ra, dec, distance_pc
    observer_pos : tuple, optional
        Observer position (x, y, z) in pc
        Default: (0, 0, 0) = Solar System
        
    Returns
    -------
    pd.DataFrame
        Stars with added x, y, z columns
    """
    # Convert to Cartesian
    x, y, z = galactic_to_cartesian(
        stars['ra'].values,
        stars['dec'].values,
        stars['distance_pc'].values
    )
    
    # Apply observer offset
    if observer_pos is not None:
        x -= observer_pos[0]
        y -= observer_pos[1]
        z -= observer_pos[2]
    
    stars['x'] = x
    stars['y'] = y
    stars['z'] = z
    
    return stars


def prepare_ssz_coordinates(
    stars_ssz: pd.DataFrame,
    observer_pos: Optional[Tuple[float, float, float]] = None
) -> pd.DataFrame:
    """
    Prepare SSZ coordinates for visualization.
    
    Adds x_ssz, y_ssz, z_ssz columns.
    
    Parameters
    ----------
    stars_ssz : pd.DataFrame
        SSZ-transformed catalog with stretch_factor
    observer_pos : tuple, optional
        Observer position
        
    Returns
    -------
    pd.DataFrame
        Stars with added SSZ coordinates
    """
    # First get Minkowski coordinates
    if 'x' not in stars_ssz.columns:
        stars_ssz = prepare_star_coordinates(stars_ssz, observer_pos)
    
    # Apply SSZ stretch
    x_ssz, y_ssz, z_ssz = apply_ssz_stretch(
        stars_ssz['x'].values,
        stars_ssz['y'].values,
        stars_ssz['z'].values,
        stars_ssz['stretch_factor'].values
    )
    
    stars_ssz['x_ssz'] = x_ssz
    stars_ssz['y_ssz'] = y_ssz
    stars_ssz['z_ssz'] = z_ssz
    
    return stars_ssz


def calculate_distance_3d(
    x1: float, y1: float, z1: float,
    x2: float, y2: float, z2: float
) -> float:
    """
    Calculate 3D Euclidean distance.
    
    Parameters
    ----------
    x1, y1, z1 : float
        First point
    x2, y2, z2 : float
        Second point
        
    Returns
    -------
    float
        Distance
    """
    return np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)


def get_region_stars(
    stars: pd.DataFrame,
    center: Tuple[float, float, float],
    radius: float
) -> pd.DataFrame:
    """
    Get stars within a spherical region.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog with x, y, z
    center : tuple
        Region center (x, y, z)
    radius : float
        Region radius
        
    Returns
    -------
    pd.DataFrame
        Stars within region
    """
    dx = stars['x'] - center[0]
    dy = stars['y'] - center[1]
    dz = stars['z'] - center[2]
    dist = np.sqrt(dx**2 + dy**2 + dz**2)
    
    return stars[dist <= radius]


def get_box_stars(
    stars: pd.DataFrame,
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    z_range: Tuple[float, float]
) -> pd.DataFrame:
    """
    Get stars within a box region.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog with x, y, z
    x_range, y_range, z_range : tuples
        (min, max) for each axis
        
    Returns
    -------
    pd.DataFrame
        Stars within box
    """
    mask = (
        (stars['x'] >= x_range[0]) & (stars['x'] <= x_range[1]) &
        (stars['y'] >= y_range[0]) & (stars['y'] <= y_range[1]) &
        (stars['z'] >= z_range[0]) & (stars['z'] <= z_range[1])
    )
    
    return stars[mask]
