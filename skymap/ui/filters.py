#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data filtering functions for UI.

© 2025 Carmen Wrede, Lino Casu
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional


def filter_by_distance(
    stars: pd.DataFrame,
    min_distance: float,
    max_distance: float
) -> pd.DataFrame:
    """
    Filter stars by distance range.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog
    min_distance : float
        Minimum distance [pc]
    max_distance : float
        Maximum distance [pc]
        
    Returns
    -------
    pd.DataFrame
        Filtered stars
    """
    mask = (stars['distance_pc'] >= min_distance) & (stars['distance_pc'] <= max_distance)
    return stars[mask].copy()


def filter_by_magnitude(
    stars: pd.DataFrame,
    min_mag: float,
    max_mag: float
) -> pd.DataFrame:
    """
    Filter stars by magnitude range.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog
    min_mag : float
        Minimum magnitude (brighter)
    max_mag : float
        Maximum magnitude (fainter)
        
    Returns
    -------
    pd.DataFrame
        Filtered stars
    """
    if 'phot_g_mean_mag' not in stars.columns:
        return stars
    
    mask = (stars['phot_g_mean_mag'] >= min_mag) & (stars['phot_g_mean_mag'] <= max_mag)
    return stars[mask].copy()


def filter_by_spectral_type(
    stars: pd.DataFrame,
    spectral_types: List[str]
) -> pd.DataFrame:
    """
    Filter stars by spectral type.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog
    spectral_types : list
        List of spectral types (e.g., ['O', 'B', 'A'])
        
    Returns
    -------
    pd.DataFrame
        Filtered stars
    """
    if 'spectral_type' not in stars.columns or 'all' in spectral_types:
        return stars
    
    mask = stars['spectral_type'].str[0].isin(spectral_types)
    return stars[mask].copy()


def search_stars(
    stars: pd.DataFrame,
    search_term: str
) -> pd.DataFrame:
    """
    Search for stars by name.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog
    search_term : str
        Search query
        
    Returns
    -------
    pd.DataFrame
        Matching stars
    """
    if not search_term or len(search_term) < 2:
        return pd.DataFrame()
    
    search_term = search_term.lower()
    mask = stars['name'].str.lower().str.contains(search_term, na=False)
    
    return stars[mask].copy()


def get_nearest_stars(
    stars: pd.DataFrame,
    n: int = 10
) -> pd.DataFrame:
    """
    Get N nearest stars to Solar System.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog
    n : int
        Number of stars
        
    Returns
    -------
    pd.DataFrame
        Nearest stars
    """
    return stars.nsmallest(n, 'distance_pc')


def get_brightest_stars(
    stars: pd.DataFrame,
    n: int = 10
) -> pd.DataFrame:
    """
    Get N brightest stars.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog
    n : int
        Number of stars
        
    Returns
    -------
    pd.DataFrame
        Brightest stars
    """
    if 'phot_g_mean_mag' not in stars.columns:
        return stars.head(n)
    
    return stars.nsmallest(n, 'phot_g_mean_mag')


def apply_all_filters(
    stars: pd.DataFrame,
    distance_range: Tuple[float, float],
    magnitude_range: Optional[Tuple[float, float]] = None,
    spectral_types: Optional[List[str]] = None,
    search_term: Optional[str] = None
) -> pd.DataFrame:
    """
    Apply all filters in sequence.
    
    Parameters
    ----------
    stars : pd.DataFrame
        Star catalog
    distance_range : tuple
        (min, max) distance
    magnitude_range : tuple, optional
        (min, max) magnitude
    spectral_types : list, optional
        Spectral type list
    search_term : str, optional
        Search query
        
    Returns
    -------
    pd.DataFrame
        Filtered stars
    """
    result = stars.copy()
    
    # Distance filter
    result = filter_by_distance(result, distance_range[0], distance_range[1])
    
    # Magnitude filter
    if magnitude_range is not None:
        result = filter_by_magnitude(result, magnitude_range[0], magnitude_range[1])
    
    # Spectral type filter
    if spectral_types is not None and len(spectral_types) > 0:
        result = filter_by_spectral_type(result, spectral_types)
    
    # Search filter
    if search_term:
        result = search_stars(result, search_term)
    
    return result
