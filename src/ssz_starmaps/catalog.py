"""
Star catalog retrieval via Astropy/astroquery.

This module fetches real astronomical data from online catalogs
(SIMBAD, GAIA, etc.) for use in SSZ star maps.

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
from typing import Optional
import warnings

try:
    from astroquery.simbad import Simbad
    from astroquery.gaia import Gaia
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    ASTROQUERY_AVAILABLE = True
    GAIA_AVAILABLE = True
except ImportError:
    ASTROQUERY_AVAILABLE = False
    GAIA_AVAILABLE = False
    warnings.warn(
        "astroquery not available. Install with: pip install astroquery astropy"
    )


def fetch_sample_catalog(
    center_ra_deg: float,
    center_dec_deg: float,
    radius_deg: float,
    limit: int = 50
) -> Optional[dict]:
    """
    Fetch a sample of stars from SIMBAD around a given sky position.
    
    Parameters
    ----------
    center_ra_deg : float
        Right Ascension of search center (degrees, J2000)
    center_dec_deg : float
        Declination of search center (degrees, J2000)
    radius_deg : float
        Search radius (degrees)
    limit : int, optional
        Maximum number of objects to retrieve (default: 50)
        
    Returns
    -------
    dict or None
        Dictionary with keys:
        - 'ra': array of RA values (deg)
        - 'dec': array of Dec values (deg)
        - 'vmag': array of V magnitudes (when available, else NaN)
        - 'name': array of object identifiers
        
        Returns None if query fails or astroquery not available.
        
    Notes
    -----
    This function requires an active internet connection to access
    the SIMBAD database at CDS (Strasbourg).
    
    For offline testing, consider using cached data or local catalogs.
    """
    if not ASTROQUERY_AVAILABLE:
        print("ERROR: astroquery not installed!")
        print("Install with: pip install astroquery astropy")
        return None
    
    try:
        # Create sky coordinate for search center
        center = SkyCoord(
            ra=center_ra_deg * u.deg,
            dec=center_dec_deg * u.deg,
            frame='icrs'
        )
        
        # Configure SIMBAD query
        custom_simbad = Simbad()
        custom_simbad.add_votable_fields('flux(V)')  # Request V magnitude
        custom_simbad.ROW_LIMIT = limit
        
        print(f"\nQuerying SIMBAD...")
        print(f"  Center: RA={center_ra_deg:.3f}°, Dec={center_dec_deg:.3f}°")
        print(f"  Radius: {radius_deg:.3f}°")
        print(f"  Limit:  {limit} objects")
        
        # Execute query
        result_table = custom_simbad.query_region(
            center,
            radius=radius_deg * u.deg
        )
        
        if result_table is None or len(result_table) == 0:
            print("  No objects found in this region.")
            return None
        
        print(f"  Found: {len(result_table)} objects")
        
        # Extract data
        ra_values = []
        dec_values = []
        vmag_values = []
        names = []
        
        for row in result_table:
            # Parse coordinates
            coord = SkyCoord(
                row['RA'],
                row['DEC'],
                unit=(u.hourangle, u.deg),
                frame='icrs'
            )
            
            ra_values.append(coord.ra.deg)
            dec_values.append(coord.dec.deg)
            
            # Parse V magnitude (may be masked/missing)
            try:
                vmag = float(row['FLUX_V'])
            except (ValueError, TypeError, KeyError):
                vmag = np.nan
            vmag_values.append(vmag)
            
            # Object name
            names.append(str(row['MAIN_ID']))
        
        catalog = {
            'ra': np.array(ra_values),
            'dec': np.array(dec_values),
            'vmag': np.array(vmag_values),
            'name': np.array(names)
        }
        
        return catalog
        
    except Exception as e:
        print(f"\nERROR querying SIMBAD: {e}")
        print("Check your internet connection and try again.")
        return None


def get_sample_galactic_center(limit: int = 50) -> Optional[dict]:
    """
    Convenience function: fetch stars near Galactic Center.
    
    Parameters
    ----------
    limit : int
        Maximum number of objects
        
    Returns
    -------
    dict or None
        Star catalog, same format as fetch_sample_catalog()
    """
    # Galactic Center: RA ≈ 266.4°, Dec ≈ -29.0° (J2000)
    return fetch_sample_catalog(
        center_ra_deg=266.4,
        center_dec_deg=-29.0,
        radius_deg=2.0,
        limit=limit
    )


def get_sample_orion(limit: int = 50) -> Optional[dict]:
    """
    Convenience function: fetch stars in Orion region.
    
    Parameters
    ----------
    limit : int
        Maximum number of objects
        
    Returns
    -------
    dict or None
        Star catalog, same format as fetch_sample_catalog()
    """
    # Orion Nebula: RA ≈ 83.8°, Dec ≈ -5.4° (J2000)
    return fetch_sample_catalog(
        center_ra_deg=83.8,
        center_dec_deg=-5.4,
        radius_deg=5.0,
        limit=limit
    )


def fetch_gaia_catalog(
    center_ra_deg: float,
    center_dec_deg: float,
    radius_deg: float,
    limit: int = 1000,
    mag_limit: float = 15.0
) -> Optional[dict]:
    """
    Fetch real star catalog from GAIA DR3.
    
    GAIA Data Release 3 contains over 1.8 billion stars with
    precise positions, parallaxes, and magnitudes.
    
    Parameters
    ----------
    center_ra_deg : float
        Right Ascension of search center (degrees, J2000)
    center_dec_deg : float
        Declination of search center (degrees, J2000)
    radius_deg : float
        Search radius (degrees)
    limit : int, optional
        Maximum number of stars to retrieve (default: 1000)
    mag_limit : float, optional
        Magnitude limit (fainter stars excluded, default: 15.0)
        
    Returns
    -------
    dict or None
        Dictionary with keys:
        - 'ra': array of RA values (deg)
        - 'dec': array of Dec values (deg)
        - 'pmag': array of G magnitudes (GAIA phot_g_mean_mag)
        - 'parallax': array of parallax values (mas)
        - 'source_id': array of GAIA source IDs
        
        Returns None if query fails or GAIA not available.
        
    Notes
    -----
    This function requires an active internet connection to access
    the GAIA archive at ESA (European Space Agency).
    
    GAIA DR3: https://gea.esac.esa.int/archive/
    
    For large catalogs (>10,000 stars), consider using async queries
    or downloading data files directly.
    
    Examples
    --------
    >>> # Fetch 1000 bright stars near galactic center
    >>> catalog = fetch_gaia_catalog(266.4, -29.0, radius_deg=2.0, limit=1000)
    """
    if not GAIA_AVAILABLE:
        print("ERROR: GAIA module not available!")
        print("Install with: pip install astroquery astropy")
        return None
    
    try:
        # Build ADQL query (Astronomical Data Query Language)
        query = f"""
        SELECT TOP {limit}
            source_id,
            ra,
            dec,
            phot_g_mean_mag,
            parallax
        FROM gaiadr3.gaia_source
        WHERE CONTAINS(
            POINT('ICRS', ra, dec),
            CIRCLE('ICRS', {center_ra_deg}, {center_dec_deg}, {radius_deg})
        ) = 1
        AND phot_g_mean_mag < {mag_limit}
        ORDER BY phot_g_mean_mag ASC
        """
        
        print(f"\nQuerying GAIA DR3...")
        print(f"  Center: RA={center_ra_deg:.3f} deg, Dec={center_dec_deg:.3f} deg")
        print(f"  Radius: {radius_deg:.3f} deg")
        print(f"  Magnitude limit: {mag_limit:.1f}")
        print(f"  Max sources: {limit}")
        print(f"  (This may take 10-60 seconds...)")
        
        # Execute synchronous query
        job = Gaia.launch_job(query)
        result_table = job.get_results()
        
        if result_table is None or len(result_table) == 0:
            print("  No sources found in this region.")
            return None
        
        print(f"  Found: {len(result_table)} sources")
        
        # Extract data
        catalog = {
            'ra': np.array(result_table['ra']),
            'dec': np.array(result_table['dec']),
            'pmag': np.array(result_table['phot_g_mean_mag']),
            'parallax': np.array(result_table['parallax']),
            'source_id': np.array(result_table['source_id'], dtype=np.int64)
        }
        
        # Handle masked values (NaN parallaxes)
        if hasattr(catalog['parallax'], 'filled'):
            catalog['parallax'] = catalog['parallax'].filled(np.nan)
        
        return catalog
        
    except Exception as e:
        print(f"\nERROR querying GAIA: {e}")
        print("Check your internet connection and try again.")
        print("Note: GAIA queries can time out for very large areas or limits.")
        return None


def create_mock_catalog(n_stars: int = 50, seed: int = 42) -> dict:
    """
    Create a mock star catalog for offline testing.
    
    Parameters
    ----------
    n_stars : int
        Number of stars to generate
    seed : int
        Random seed for reproducibility
        
    Returns
    -------
    dict
        Mock catalog with same structure as fetch_sample_catalog()
    """
    rng = np.random.RandomState(seed)
    
    # Random positions in a small sky patch
    ra = rng.uniform(0, 10, n_stars)
    dec = rng.uniform(-5, 5, n_stars)
    
    # Random V magnitudes (typical range 5-15)
    vmag = rng.uniform(5, 15, n_stars)
    
    # Generic names
    names = np.array([f"MOCK_{i:03d}" for i in range(n_stars)])
    
    return {
        'ra': ra,
        'dec': dec,
        'vmag': vmag,
        'name': names
    }


if __name__ == "__main__":
    print("=" * 70)
    print("SSZ StarMaps - Catalog Module Test")
    print("=" * 70)
    
    if ASTROQUERY_AVAILABLE:
        print("\n[OK] astroquery is installed")
        print("\nAttempting to fetch sample catalog from SIMBAD...")
        print("(This requires internet connection)")
        
        # Try a small query around RA=0, Dec=0
        catalog = fetch_sample_catalog(
            center_ra_deg=0.0,
            center_dec_deg=0.0,
            radius_deg=5.0,
            limit=10
        )
        
        if catalog is not None:
            print("\n[OK] Query successful!")
            print(f"  Retrieved {len(catalog['ra'])} stars")
            print(f"\nFirst 3 objects:")
            for i in range(min(3, len(catalog['ra']))):
                print(f"  {catalog['name'][i]:20s}  "
                      f"RA={catalog['ra'][i]:8.3f}°  "
                      f"Dec={catalog['dec'][i]:+8.3f} deg  "
                      f"Vmag={catalog['vmag'][i]:5.2f}")
    else:
        print("\n[X] astroquery not available")
        print("  Install with: pip install astroquery astropy")
    
    print("\n" + "-" * 70)
    print("Creating mock catalog for offline testing...")
    mock = create_mock_catalog(n_stars=10)
    print(f"[OK] Generated {len(mock['ra'])} mock stars")
    print(f"\nFirst 3 mock objects:")
    for i in range(3):
        print(f"  {mock['name'][i]:20s}  "
              f"RA={mock['ra'][i]:8.3f}°  "
              f"Dec={mock['dec'][i]:+8.3f}°  "
              f"Vmag={mock['vmag'][i]:5.2f}")
    
    print("\n" + "=" * 70)
