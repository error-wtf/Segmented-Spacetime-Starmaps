"""
GAIA DR3 catalog queries with error handling.

Functions for fetching stellar data from the GAIA archive:
- Nearby stars by distance
- Cone searches by sky coordinates
- Region queries

© 2025 Carmen Wrede, Lino Casu
"""

import pandas as pd
import numpy as np
from typing import Optional
import warnings

try:
    from astroquery.gaia import Gaia
    GAIA_AVAILABLE = True
except ImportError:
    GAIA_AVAILABLE = False
    warnings.warn("astroquery not available. Install with: pip install astroquery")


def fetch_gaia_nearby(
    distance_pc: float = 100,
    max_sources: int = 1000,
    min_parallax_snr: float = 5.0
) -> pd.DataFrame:
    """
    Fetch nearby stars from GAIA DR3 by distance.
    
    Parameters
    ----------
    distance_pc : float, optional
        Maximum distance in parsecs (default: 100)
    max_sources : int, optional
        Maximum number of sources to retrieve (default: 1000)
    min_parallax_snr : float, optional
        Minimum parallax signal-to-noise ratio (default: 5.0)
        
    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - source_id: GAIA source identifier
        - ra, dec: Position [degrees, ICRS]
        - parallax: Parallax [mas]
        - parallax_error: Parallax uncertainty [mas]
        - pmra, pmdec: Proper motion [mas/yr]
        - phot_g_mean_mag: G-band magnitude
        - distance_pc: Computed distance [parsec]
        
    Raises
    ------
    ImportError
        If astroquery is not installed
    RuntimeError
        If GAIA query fails
        
    Notes
    -----
    Requires active internet connection to GAIA archive.
    Query uses parallax_over_error > min_parallax_snr to ensure quality.
    
    Examples
    --------
    >>> stars = fetch_gaia_nearby(distance_pc=50, max_sources=100)
    >>> print(f"Found {len(stars)} stars within 50 pc")
    """
    if not GAIA_AVAILABLE:
        raise ImportError(
            "astroquery is required for GAIA queries. "
            "Install with: pip install astroquery astropy"
        )
    
    # Convert distance to minimum parallax (mas)
    min_parallax = 1000.0 / distance_pc
    
    query = f"""
    SELECT TOP {max_sources}
        source_id, 
        ra, dec, 
        parallax, parallax_error,
        pmra, pmdec,
        phot_g_mean_mag
    FROM gaiadr3.gaia_source
    WHERE parallax > {min_parallax}
    AND parallax_over_error > {min_parallax_snr}
    ORDER BY parallax DESC
    """
    
    try:
        print(f"Querying GAIA DR3 for stars within {distance_pc} pc...")
        job = Gaia.launch_job(query)
        table = job.get_results()
        
        # Convert to pandas
        df = table.to_pandas()
        
        # Add computed distance
        df['distance_pc'] = 1000.0 / df['parallax']
        
        print(f"  Retrieved {len(df)} stars")
        
        return df
        
    except Exception as e:
        raise RuntimeError(f"GAIA query failed: {e}")


def fetch_gaia_cone(
    ra_deg: float,
    dec_deg: float,
    radius_deg: float,
    max_sources: int = 1000,
    min_parallax_snr: float = 5.0,
    mag_limit: Optional[float] = None
) -> pd.DataFrame:
    """
    Fetch stars in a cone search from GAIA DR3.
    
    Parameters
    ----------
    ra_deg : float
        Right ascension of cone center [degrees, ICRS]
    dec_deg : float
        Declination of cone center [degrees, ICRS]
    radius_deg : float
        Search radius [degrees]
    max_sources : int, optional
        Maximum number of sources (default: 1000)
    min_parallax_snr : float, optional
        Minimum parallax SNR (default: 5.0)
    mag_limit : float, optional
        Maximum G magnitude (fainter excluded)
        
    Returns
    -------
    pd.DataFrame
        DataFrame with GAIA sources in the cone
        
    Examples
    --------
    >>> # Orion Nebula region
    >>> stars = fetch_gaia_cone(ra_deg=83.8, dec_deg=-5.4, radius_deg=1.0)
    """
    if not GAIA_AVAILABLE:
        raise ImportError(
            "astroquery is required. Install with: pip install astroquery"
        )
    
    # Build query
    mag_constraint = ""
    if mag_limit is not None:
        mag_constraint = f"AND phot_g_mean_mag < {mag_limit}"
    
    query = f"""
    SELECT TOP {max_sources}
        source_id,
        ra, dec,
        parallax, parallax_error,
        pmra, pmdec,
        phot_g_mean_mag
    FROM gaiadr3.gaia_source
    WHERE 1=CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', {ra_deg}, {dec_deg}, {radius_deg})
    )
    AND parallax IS NOT NULL
    AND parallax_over_error > {min_parallax_snr}
    {mag_constraint}
    ORDER BY phot_g_mean_mag ASC
    """
    
    try:
        print(f"Querying GAIA cone: RA={ra_deg:.2f}, Dec={dec_deg:.2f}, "
              f"radius={radius_deg:.2f} deg")
        
        job = Gaia.launch_job(query)
        table = job.get_results()
        df = table.to_pandas()
        
        # Add distance where parallax is positive
        mask = df['parallax'] > 0
        df.loc[mask, 'distance_pc'] = 1000.0 / df.loc[mask, 'parallax']
        
        print(f"  Retrieved {len(df)} sources")
        
        return df
        
    except Exception as e:
        raise RuntimeError(f"GAIA cone search failed: {e}")


def fetch_gaia_region(
    ra_min: float,
    ra_max: float,
    dec_min: float,
    dec_max: float,
    max_sources: int = 1000
) -> pd.DataFrame:
    """
    Fetch stars in a rectangular region.
    
    Parameters
    ----------
    ra_min, ra_max : float
        RA boundaries [degrees]
    dec_min, dec_max : float
        Dec boundaries [degrees]
    max_sources : int, optional
        Maximum sources to retrieve
        
    Returns
    -------
    pd.DataFrame
        Stars in the specified region
    """
    if not GAIA_AVAILABLE:
        raise ImportError("astroquery required")
    
    query = f"""
    SELECT TOP {max_sources}
        source_id, ra, dec, parallax, parallax_error,
        pmra, pmdec, phot_g_mean_mag
    FROM gaiadr3.gaia_source
    WHERE ra BETWEEN {ra_min} AND {ra_max}
    AND dec BETWEEN {dec_min} AND {dec_max}
    AND parallax IS NOT NULL
    ORDER BY phot_g_mean_mag ASC
    """
    
    try:
        job = Gaia.launch_job(query)
        df = job.get_results().to_pandas()
        
        mask = df['parallax'] > 0
        df.loc[mask, 'distance_pc'] = 1000.0 / df.loc[mask, 'parallax']
        
        return df
    except Exception as e:
        raise RuntimeError(f"GAIA region query failed: {e}")


# Pre-defined interesting regions
INTERESTING_REGIONS = {
    'orion': {
        'name': 'Orion Nebula',
        'ra': 83.8,
        'dec': -5.4,
        'radius': 10.0,
    },
    'pleiades': {
        'name': 'Pleiades (M45)',
        'ra': 56.75,
        'dec': 24.12,
        'radius': 5.0,
    },
    'andromeda': {
        'name': 'Andromeda Galaxy',
        'ra': 10.68,
        'dec': 41.27,
        'radius': 3.0,
    },
    'cygnus': {
        'name': 'Cygnus Region',
        'ra': 312.5,
        'dec': 40.2,
        'radius': 10.0,
    },
    'galactic_center': {
        'name': 'Galactic Center',
        'ra': 266.4,
        'dec': -29.0,
        'radius': 5.0,
    }
}


def fetch_interesting_region(region_name: str, **kwargs) -> pd.DataFrame:
    """
    Fetch stars from a pre-defined interesting region.
    
    Parameters
    ----------
    region_name : str
        One of: 'orion', 'pleiades', 'andromeda', 'cygnus', 'galactic_center'
    **kwargs
        Additional arguments passed to fetch_gaia_cone()
        
    Returns
    -------
    pd.DataFrame
        Stars in the region
        
    Examples
    --------
    >>> stars = fetch_interesting_region('orion', max_sources=500)
    """
    if region_name not in INTERESTING_REGIONS:
        valid = ', '.join(INTERESTING_REGIONS.keys())
        raise ValueError(f"Unknown region '{region_name}'. Valid: {valid}")
    
    region = INTERESTING_REGIONS[region_name]
    print(f"Fetching region: {region['name']}")
    
    return fetch_gaia_cone(
        ra_deg=region['ra'],
        dec_deg=region['dec'],
        radius_deg=region['radius'],
        **kwargs
    )
