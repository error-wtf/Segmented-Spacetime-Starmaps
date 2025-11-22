"""
Batch SSZ transformation for large star catalogs.

Applies radial stretch based on Xi(r) to entire catalogs with parallel processing.

© 2025 Carmen Wrede, Lino Casu
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Union
from tqdm import tqdm

from ..ssz_metric import Xi, D_SSZ, schwarzschild_radius, radial_stretch


@dataclass
class TransformConfig:
    """
    Configuration for SSZ transformation.
    
    Attributes
    ----------
    mass_kg : float
        Central mass [kg] (default: solar mass = 1.989e30)
    apply_time_dilation : bool
        Compute time dilation factor (default: True)
    apply_radial_stretch : bool
        Apply radial deformation (default: True)
    parallel : bool
        Use parallel processing (default: False, needs joblib)
    n_jobs : int
        Number of parallel jobs (-1 = all CPUs)
    """
    mass_kg: float = 1.989e30  # Solar mass
    apply_time_dilation: bool = True
    apply_radial_stretch: bool = True
    parallel: bool = False
    n_jobs: int = -1


def transform_star(
    star_row: pd.Series,
    config: TransformConfig
) -> dict:
    """
    Apply SSZ transformation to a single star.
    
    Parameters
    ----------
    star_row : pd.Series
        Row from DataFrame with columns: ra, dec, distance_pc
    config : TransformConfig
        Transformation configuration
        
    Returns
    -------
    dict
        Transformed star data with keys:
        - Original: ra, dec, distance_pc
        - SSZ: ra_ssz, dec_ssz, distance_ssz_pc
        - Physics: xi, D_ssz, stretch_factor
    """
    # Convert to meters
    pc_to_m = 3.086e16
    r = star_row['distance_pc'] * pc_to_m
    r_s = schwarzschild_radius(config.mass_kg)
    
    # Calculate SSZ quantities
    xi = Xi(r, r_s)
    D = D_SSZ(r, r_s) if config.apply_time_dilation else 1.0
    stretch = radial_stretch(r, r_s) if config.apply_radial_stretch else 1.0
    
    # Apply transformations
    distance_ssz_pc = star_row['distance_pc'] * stretch
    
    # Angles unchanged in first approximation
    ra_ssz = star_row['ra']
    dec_ssz = star_row['dec']
    
    result = {
        # Original
        'name': star_row.get('name', f"Star-{star_row.name}"),
        'ra': star_row['ra'],
        'dec': star_row['dec'],
        'distance_pc': star_row['distance_pc'],
        
        # SSZ transformed
        'ra_ssz': ra_ssz,
        'dec_ssz': dec_ssz,
        'distance_ssz_pc': distance_ssz_pc,
        
        # Physics
        'xi': float(xi),
        'D_ssz': float(D),
        'stretch_factor': float(stretch),
    }
    
    # Preserve additional columns
    for col in ['vmag', 'phot_g_mean_mag', 'spectral_type', 'parallax']:
        if col in star_row.index and not pd.isna(star_row[col]):
            result[col] = star_row[col]
    
    return result


def transform_catalog(
    df: pd.DataFrame,
    config: Union[TransformConfig, None] = None,
    show_progress: bool = True
) -> pd.DataFrame:
    """
    Transform entire catalog with SSZ deformations.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input catalog with columns: ra, dec, distance_pc
    config : TransformConfig, optional
        Configuration (default: TransformConfig())
    show_progress : bool
        Show progress bar (default: True)
        
    Returns
    -------
    pd.DataFrame
        Transformed catalog with original + SSZ columns
        
    Examples
    --------
    >>> from ssz_starmaps.catalogs import fetch_gaia_nearby
    >>> from ssz_starmaps.transform import transform_catalog
    >>> 
    >>> stars = fetch_gaia_nearby(distance_pc=50, max_sources=100)
    >>> stars_ssz = transform_catalog(stars)
    >>> 
    >>> print(f"Mean stretch: {stars_ssz['stretch_factor'].mean():.4f}")
    """
    if config is None:
        config = TransformConfig()
    
    # Validate input
    required_cols = ['ra', 'dec', 'distance_pc']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Transform
    if config.parallel:
        try:
            from joblib import Parallel, delayed
            
            results = Parallel(n_jobs=config.n_jobs)(
                delayed(transform_star)(row, config)
                for _, row in tqdm(df.iterrows(), total=len(df),
                                  desc="SSZ Transform", disable=not show_progress)
            )
        except ImportError:
            print("joblib not available, falling back to serial processing")
            config.parallel = False
    
    if not config.parallel:
        results = [
            transform_star(row, config)
            for _, row in tqdm(df.iterrows(), total=len(df),
                             desc="SSZ Transform", disable=not show_progress)
        ]
    
    return pd.DataFrame(results)


def compute_statistics(df_ssz: pd.DataFrame) -> dict:
    """
    Compute statistics on transformed catalog.
    
    Parameters
    ----------
    df_ssz : pd.DataFrame
        Transformed catalog from transform_catalog()
        
    Returns
    -------
    dict
        Statistics including:
        - n_stars: Number of stars
        - mean_stretch: Average radial stretch
        - max_stretch: Maximum stretch
        - mean_xi: Average segment density
        - mean_D: Average time dilation
    """
    stats = {
        'n_stars': len(df_ssz),
        'mean_stretch': df_ssz['stretch_factor'].mean(),
        'std_stretch': df_ssz['stretch_factor'].std(),
        'max_stretch': df_ssz['stretch_factor'].max(),
        'min_stretch': df_ssz['stretch_factor'].min(),
        'mean_xi': df_ssz['xi'].mean(),
        'mean_D': df_ssz['D_ssz'].mean(),
        'mean_distance_pc': df_ssz['distance_pc'].mean(),
        'mean_distance_ssz_pc': df_ssz['distance_ssz_pc'].mean(),
    }
    
    return stats


def print_statistics(df_ssz: pd.DataFrame):
    """Print formatted statistics."""
    stats = compute_statistics(df_ssz)
    
    print("="*70)
    print("SSZ TRANSFORMATION STATISTICS")
    print("="*70)
    print(f"Number of stars:        {stats['n_stars']}")
    print(f"\nRadial Stretch:")
    print(f"  Mean:                 {stats['mean_stretch']:.6f}")
    print(f"  Std Dev:              {stats['std_stretch']:.6f}")
    print(f"  Range:                [{stats['min_stretch']:.6f}, {stats['max_stretch']:.6f}]")
    print(f"\nSegment Density:")
    print(f"  Mean Xi:              {stats['mean_xi']:.6f}")
    print(f"\nTime Dilation:")
    print(f"  Mean D_SSZ:           {stats['mean_D']:.6f}")
    print(f"\nDistances:")
    print(f"  Original (mean):      {stats['mean_distance_pc']:.2f} pc")
    print(f"  SSZ (mean):           {stats['mean_distance_ssz_pc']:.2f} pc")
    print(f"  Difference:           {stats['mean_distance_ssz_pc'] - stats['mean_distance_pc']:.2f} pc")
    print("="*70)
