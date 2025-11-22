#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Catalog Fetchers - Real API Implementations

Fetch data from real astronomical catalogs:
- GAIA DR3 (ESA)
- SIMBAD (CDS)
- NED (NASA/IPAC)
- NASA Exoplanet Archive
- ESO Archive

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import pandas as pd
from pathlib import Path
import warnings

# Try to import astroquery (optional dependency)
try:
    from astroquery.gaia import Gaia
    from astroquery.simbad import Simbad
    from astroquery.ipac.ned import Ned
    ASTROQUERY_AVAILABLE = True
except ImportError:
    ASTROQUERY_AVAILABLE = False
    warnings.warn("astroquery not available - using synthetic data")


class GAIAFetcher:
    """Fetch data from GAIA DR3."""
    
    def __init__(self):
        self.available = ASTROQUERY_AVAILABLE
        
    def cone_search(self, ra, dec, radius, max_sources=10000):
        """
        Cone search in GAIA DR3.
        
        Parameters
        ----------
        ra : float
            Right ascension (degrees)
        dec : float
            Declination (degrees)
        radius : float
            Search radius (degrees)
        max_sources : int
            Maximum number of sources to return
            
        Returns
        -------
        pd.DataFrame
            GAIA sources with columns:
            - source_id: Unique GAIA identifier
            - ra, dec: Equatorial coordinates (deg)
            - l, b: Galactic coordinates (deg)
            - parallax, parallax_error: Distance (mas)
            - pmra, pmdec: Proper motions (mas/yr)
            - phot_g_mean_mag: G-band magnitude
            - bp_rp: Color index
            - radial_velocity: Radial velocity (km/s)
        """
        
        if not self.available:
            warnings.warn("astroquery not available, returning empty DataFrame")
            return pd.DataFrame()
        
        print(f"Querying GAIA DR3: RA={ra:.4f}°, DEC={dec:.4f}°, radius={radius:.4f}°")
        
        try:
            from astropy import units as u
            from astropy.coordinates import SkyCoord
            
            # Create coordinate
            coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
            
            # Build column list (only columns that exist in GAIA DR3)
            columns = [
                'source_id',
                'ra', 'dec',
                'l', 'b',
                'parallax', 'parallax_error',
                'pmra', 'pmdec',
                'phot_g_mean_mag',
                'bp_rp',
                'radial_velocity'
            ]
            
            # Execute cone search
            print(f"  Submitting query to GAIA archive...")
            job = Gaia.cone_search_async(
                coord,
                radius=radius*u.deg
            )
            
            # Get results
            print(f"  Retrieving results...")
            result = job.get_results()
            
            # Convert to pandas DataFrame
            df = result.to_pandas()
            
            # Add distance in parsecs (from parallax)
            if 'parallax' in df.columns:
                # distance = 1000 / parallax (mas)
                # Only for positive parallax
                mask = df['parallax'] > 0
                df.loc[mask, 'distance_pc'] = 1000.0 / df.loc[mask, 'parallax']
                df.loc[~mask, 'distance_pc'] = np.nan
            
            # Limit to max sources
            if len(df) > max_sources:
                print(f"  Limiting to {max_sources} sources (from {len(df)})")
                df = df.iloc[:max_sources].copy()
            
            # Add metadata
            df.attrs['query_type'] = 'cone_search'
            df.attrs['query_params'] = {
                'ra': ra,
                'dec': dec,
                'radius': radius,
                'max_sources': max_sources
            }
            
            print(f"  [OK] Retrieved {len(df)} sources from GAIA DR3")
            
            return df
            
        except ConnectionError as e:
            error_msg = f"GAIA connection failed: No internet connection"
            warnings.warn(error_msg)
            print(f"  [ERROR] {error_msg}")
            return pd.DataFrame()
        except TimeoutError as e:
            error_msg = f"GAIA query timeout: Request took too long"
            warnings.warn(error_msg)
            print(f"  [ERROR] {error_msg}")
            return pd.DataFrame()
        except ValueError as e:
            error_msg = f"GAIA query invalid parameters: {e}"
            warnings.warn(error_msg)
            print(f"  [ERROR] {error_msg}")
            return pd.DataFrame()
        except Exception as e:
            error_msg = f"GAIA cone search failed: {type(e).__name__} - {str(e)[:100]}"
            warnings.warn(error_msg)
            print(f"  [ERROR] {error_msg}")
            print(f"  [INFO] Falling back to empty result - check network connection")
            return pd.DataFrame()
    
    def adql_query(self, query, max_sources=100000):
        """
        Custom ADQL query.
        
        Parameters
        ----------
        query : str
            ADQL query string
        max_sources : int
            Row limit
            
        Returns
        -------
        pd.DataFrame
            Query results
        """
        
        if not self.available:
            warnings.warn("astroquery not available")
            return pd.DataFrame()
        
        print(f"Executing ADQL query...")
        
        try:
            # Add row limit
            if 'TOP' not in query.upper():
                query = query.replace('SELECT', f'SELECT TOP {max_sources}')
            
            job = Gaia.launch_job_async(query)
            result = job.get_results()
            
            df = result.to_pandas()
            print(f"Retrieved {len(df)} rows")
            
            return df
            
        except Exception as e:
            warnings.warn(f"ADQL query failed: {e}")
            return pd.DataFrame()
    
    def box_search(self, ra_min, ra_max, dec_min, dec_max, max_sources=10000):
        """Box search in RA/Dec."""
        
        query = f"""
        SELECT TOP {max_sources}
            source_id, ra, dec, l, b,
            parallax, parallax_error,
            pmra, pmdec,
            phot_g_mean_mag, bp_rp
        FROM gaiadr3.gaia_source
        WHERE ra BETWEEN {ra_min} AND {ra_max}
          AND dec BETWEEN {dec_min} AND {dec_max}
          AND parallax > 0
        """
        
        return self.adql_query(query, max_sources)


class SIMBADFetcher:
    """Fetch data from SIMBAD."""
    
    def __init__(self):
        self.available = ASTROQUERY_AVAILABLE
        
    def query_object(self, name):
        """Query single object by name."""
        
        if not self.available:
            return None
        
        try:
            result = Simbad.query_object(name)
            if result:
                return result.to_pandas()
            return None
        except Exception as e:
            warnings.warn(f"SIMBAD query failed: {e}")
            return None
    
    def query_region(self, ra, dec, radius):
        """Query region."""
        
        if not self.available:
            return pd.DataFrame()
        
        try:
            from astropy import units as u
            from astropy.coordinates import SkyCoord
            
            coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
            result = Simbad.query_region(coord, radius=radius*u.deg)
            
            if result:
                return result.to_pandas()
            return pd.DataFrame()
        except Exception as e:
            warnings.warn(f"SIMBAD query failed: {e}")
            return pd.DataFrame()


class NEDFetcher:
    """Fetch data from NED."""
    
    def __init__(self):
        self.available = ASTROQUERY_AVAILABLE
        
    def query_region(self, ra, dec, radius):
        """Query NED region."""
        
        if not self.available:
            return pd.DataFrame()
        
        try:
            from astropy import units as u
            from astropy.coordinates import SkyCoord
            
            coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
            result = Ned.query_region(coord, radius=radius*u.arcmin)
            
            if result:
                return result.to_pandas()
            return pd.DataFrame()
        except Exception as e:
            warnings.warn(f"NED query failed: {e}")
            return pd.DataFrame()
    
    def query_object(self, name):
        """Query single object."""
        
        if not self.available:
            return None
        
        try:
            result = Ned.query_object(name)
            if result:
                return result.to_pandas()
            return None
        except Exception as e:
            warnings.warn(f"NED query failed: {e}")
            return None


class ExoplanetFetcher:
    """Fetch data from NASA Exoplanet Archive."""
    
    def __init__(self):
        self.available = ASTROQUERY_AVAILABLE
        
    def get_confirmed_planets(self):
        """Get all confirmed exoplanets."""
        
        if not self.available:
            return pd.DataFrame()
        
        try:
            from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
            
            result = NasaExoplanetArchive.query_criteria(
                table="ps",  # Planetary Systems table
                select="*",
                where="default_flag=1"  # Confirmed planets only
            )
            
            return result.to_pandas()
        except Exception as e:
            warnings.warn(f"Exoplanet query failed: {e}")
            return pd.DataFrame()


class ESOFetcher:
    """Fetch data from ESO Archive."""
    
    def __init__(self):
        self.available = False  # ESO requires authentication
        
    def query_gravity_observations(self):
        """Query GRAVITY observations (Sgr A*, M87*)."""
        warnings.warn("ESO Archive requires authentication - not implemented")
        return pd.DataFrame()


def demo():
    """Demo: Catalog fetchers."""
    
    print("="*70)
    print("CATALOG FETCHERS - Demo")
    print("="*70)
    print()
    
    if not ASTROQUERY_AVAILABLE:
        print("⚠️  astroquery not installed")
        print("Install with: pip install astroquery")
        print()
        print("Demo will show API structure without actual queries")
        print("="*70)
        return
    
    # Test GAIA
    print("1. Testing GAIA fetcher...")
    gaia = GAIAFetcher()
    
    # Cone search around Galactic center
    data = gaia.cone_search(ra=266.4, dec=-29.0, radius=0.1, max_sources=100)
    if len(data) > 0:
        print(f"   Found {len(data)} sources")
        print(f"   Columns: {list(data.columns)[:5]}...")
    print()
    
    # Test SIMBAD
    print("2. Testing SIMBAD fetcher...")
    simbad = SIMBADFetcher()
    
    result = simbad.query_object("Sirius")
    if result is not None:
        print("   Sirius data retrieved")
    print()
    
    # Test NED
    print("3. Testing NED fetcher...")
    ned = NEDFetcher()
    
    result = ned.query_object("M87")
    if result is not None:
        print("   M87 data retrieved")
    print()
    
    # Test Exoplanets
    print("4. Testing Exoplanet fetcher...")
    exo = ExoplanetFetcher()
    
    planets = exo.get_confirmed_planets()
    if len(planets) > 0:
        print(f"   Found {len(planets)} confirmed exoplanets")
    print()
    
    print("="*70)
    print("DEMO COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    demo()
