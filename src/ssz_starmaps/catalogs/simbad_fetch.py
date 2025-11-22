"""
SIMBAD catalog queries for named objects.

Functions for fetching stellar parameters from SIMBAD:
- Named stars (e.g., "Sirius", "Alpha Centauri")
- Bright stars by magnitude
- Messier objects

© 2025 Carmen Wrede, Lino Casu
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict
import warnings

try:
    from astroquery.simbad import Simbad
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    SIMBAD_AVAILABLE = True
except ImportError:
    SIMBAD_AVAILABLE = False
    warnings.warn("astroquery not available for SIMBAD queries")


# Configure SIMBAD to return additional fields
if SIMBAD_AVAILABLE:
    Simbad.add_votable_fields('sptype', 'distance', 'flux(V)', 'pmra', 'pmdec')


def fetch_named_star(name: str) -> Optional[Dict]:
    """
    Fetch a single star by name from SIMBAD.
    
    Parameters
    ----------
    name : str
        Star name (e.g., "Sirius", "Alpha Centauri", "M31")
        
    Returns
    -------
    dict or None
        Dictionary with keys:
        - name: Object name
        - ra, dec: Position [degrees]
        - distance_pc: Distance [parsecs] (if available)
        - spectral_type: Spectral classification
        - vmag: V magnitude
        - pmra, pmdec: Proper motion [mas/yr]
        - source: 'SIMBAD'
        
        Returns None if object not found.
        
    Examples
    --------
    >>> sirius = fetch_named_star("Sirius")
    >>> print(f"Sirius distance: {sirius['distance_pc']:.1f} pc")
    """
    if not SIMBAD_AVAILABLE:
        raise ImportError("astroquery required for SIMBAD")
    
    try:
        result = Simbad.query_object(name)
        
        if result is None:
            print(f"Object '{name}' not found in SIMBAD")
            return None
        
        row = result[0]
        
        # Extract coordinates
        coord = SkyCoord(row['RA'], row['DEC'], unit=(u.hourangle, u.deg))
        
        # Build result dictionary
        data = {
            'name': name,
            'ra': coord.ra.degree,
            'dec': coord.dec.degree,
            'source': 'SIMBAD'
        }
        
        # Add optional fields if available
        if 'Distance_distance' in row.colnames and row['Distance_distance']:
            data['distance_pc'] = float(row['Distance_distance'])
        
        if 'SP_TYPE' in row.colnames and row['SP_TYPE']:
            data['spectral_type'] = str(row['SP_TYPE'])
        
        if 'FLUX_V' in row.colnames and row['FLUX_V']:
            data['vmag'] = float(row['FLUX_V'])
        
        if 'PMRA' in row.colnames and row['PMRA']:
            data['pmra'] = float(row['PMRA'])
        
        if 'PMDEC' in row.colnames and row['PMDEC']:
            data['pmdec'] = float(row['PMDEC'])
        
        return data
        
    except Exception as e:
        print(f"Error fetching '{name}': {e}")
        return None


def fetch_bright_stars(mag_limit: float = 3.0, max_stars: int = 100) -> pd.DataFrame:
    """
    Fetch bright stars from SIMBAD.
    
    Parameters
    ----------
    mag_limit : float, optional
        Maximum V magnitude (default: 3.0 - naked eye limit)
    max_stars : int, optional
        Maximum number of stars to retrieve
        
    Returns
    -------
    pd.DataFrame
        Bright stars with their parameters
        
    Examples
    --------
    >>> bright = fetch_bright_stars(mag_limit=2.0, max_stars=50)
    >>> print(f"Brightest: {bright.iloc[0]['name']}")
    """
    if not SIMBAD_AVAILABLE:
        raise ImportError("astroquery required")
    
    # Query for bright stars
    query = f"""
    SELECT TOP {max_stars} 
        main_id, ra, dec, pmra, pmdec, 
        sp_type, flux_V, distance_result
    FROM basic
    WHERE flux_V < {mag_limit}
    AND otype = 'Star'
    ORDER BY flux_V ASC
    """
    
    try:
        # Use TAP query for more control
        from astroquery.simbad import Simbad
        
        # Alternative: query by magnitude constraint
        Simbad.ROW_LIMIT = max_stars
        result = Simbad.query_criteria(
            f"Vmag < {mag_limit}",
            otype='Star'
        )
        
        if result is None:
            print("No bright stars found")
            return pd.DataFrame()
        
        # Convert to DataFrame
        stars = []
        for row in result:
            coord = SkyCoord(row['RA'], row['DEC'], unit=(u.hourangle, u.deg))
            
            star = {
                'name': str(row['MAIN_ID']),
                'ra': coord.ra.degree,
                'dec': coord.dec.degree,
            }
            
            if 'FLUX_V' in row.colnames and row['FLUX_V']:
                star['vmag'] = float(row['FLUX_V'])
            
            if 'Distance_distance' in row.colnames and row['Distance_distance']:
                star['distance_pc'] = float(row['Distance_distance'])
            
            stars.append(star)
        
        return pd.DataFrame(stars)
        
    except Exception as e:
        print(f"Error fetching bright stars: {e}")
        return pd.DataFrame()


def fetch_multiple_stars(names: List[str]) -> pd.DataFrame:
    """
    Fetch multiple named stars in batch.
    
    Parameters
    ----------
    names : list of str
        List of star names
        
    Returns
    -------
    pd.DataFrame
        All successfully fetched stars
        
    Examples
    --------
    >>> stars = fetch_multiple_stars(['Sirius', 'Vega', 'Arcturus'])
    """
    results = []
    
    for name in names:
        print(f"Fetching {name}...", end=' ')
        star = fetch_named_star(name)
        if star:
            results.append(star)
            print("OK")
        else:
            print("Not found")
    
    return pd.DataFrame(results)


# Pre-defined star lists
FAMOUS_STARS = [
    'Sirius', 'Canopus', 'Arcturus', 'Vega', 'Capella',
    'Rigel', 'Procyon', 'Betelgeuse', 'Altair', 'Aldebaran',
    'Antares', 'Spica', 'Pollux', 'Fomalhaut', 'Deneb',
    'Regulus', 'Adhara', 'Castor', 'Bellatrix', 'Alnilam'
]

MESSIER_STARS = [
    'M1', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M11',
    'M13', 'M15', 'M22', 'M31', 'M42', 'M45', 'M51',
]


def fetch_famous_stars() -> pd.DataFrame:
    """
    Fetch a curated list of famous bright stars.
    
    Returns
    -------
    pd.DataFrame
        Famous stars with parameters
    """
    print("Fetching famous stars...")
    return fetch_multiple_stars(FAMOUS_STARS)


def fetch_messier_objects() -> pd.DataFrame:
    """
    Fetch Messier catalog objects.
    
    Returns
    -------
    pd.DataFrame
        Messier objects
    """
    print("Fetching Messier objects...")
    return fetch_multiple_stars(MESSIER_STARS)
