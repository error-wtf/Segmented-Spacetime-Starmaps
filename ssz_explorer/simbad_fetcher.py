#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMBAD Catalog Fetcher - Sprint 2 Task 1

Queries SIMBAD database for astronomical object information.
Provides object identifiers, types, and properties.

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# Set up logging
logger = logging.getLogger(__name__)

# Import with error handling
try:
    from astroquery.simbad import Simbad
    SIMBAD_AVAILABLE = True
    logger.info("SIMBAD module loaded successfully")
except ImportError:
    SIMBAD_AVAILABLE = False
    logger.warning("astroquery.simbad not available - SIMBAD queries will not work")


class SIMBADFetcher:
    """
    Fetches astronomical object data from SIMBAD database.
    
    SIMBAD (Set of Identifications, Measurements, and Bibliography for Astronomical Data)
    contains information for ~11 million objects.
    """
    
    def __init__(self):
        """Initialize SIMBAD fetcher with custom field configuration."""
        self.available = SIMBAD_AVAILABLE
        
        if not self.available:
            logger.warning("SIMBAD not available - install with: pip install astroquery")
            return
            
        # Configure SIMBAD with fields we need
        self.simbad = Simbad()
        
        # Add custom fields
        self.simbad.add_votable_fields(
            'otype',        # Object type
            'otypes',       # All object types
            'ids',          # All identifiers
            'ra',           # Right ascension
            'dec',          # Declination
            'pmra',         # Proper motion RA
            'pmdec',        # Proper motion Dec
            'plx',          # Parallax
            'rv_value',     # Radial velocity
            'z_value',      # Redshift
            'sp',           # Spectral type
            'flux(V)',      # V magnitude
            'flux(B)',      # B magnitude
            'flux(K)',      # K magnitude
        )
        
        logger.info("SIMBADFetcher initialized with custom fields")
    
    def is_available(self) -> bool:
        """Check if SIMBAD is available."""
        return self.available
    
    def cone_search(
        self,
        ra: float,
        dec: float,
        radius: float = 1.0,
        max_results: int = 1000
    ) -> Optional[pd.DataFrame]:
        """
        Perform cone search around coordinates.
        
        Parameters:
        -----------
        ra : float
            Right ascension in degrees (J2000)
        dec : float
            Declination in degrees (J2000)
        radius : float
            Search radius in arcminutes (default: 1.0)
        max_results : int
            Maximum number of results (default: 1000)
            
        Returns:
        --------
        pd.DataFrame or None
            DataFrame with SIMBAD data, or None if error
        """
        if not self.available:
            logger.error("SIMBAD not available")
            return None
            
        try:
            logger.info(f"Querying SIMBAD: RA={ra:.4f}, Dec={dec:.4f}, radius={radius:.2f}'")
            
            # Set row limit
            self.simbad.ROW_LIMIT = max_results
            
            # Query SIMBAD
            from astropy import units as u
            from astropy.coordinates import SkyCoord
            
            coord = SkyCoord(ra=ra, dec=dec, unit=(u.degree, u.degree), frame='icrs')
            result_table = self.simbad.query_region(coord, radius=radius * u.arcmin)
            
            if result_table is None or len(result_table) == 0:
                logger.warning(f"No SIMBAD objects found at RA={ra:.4f}, Dec={dec:.4f}")
                return None
                
            # Convert to pandas DataFrame
            df = result_table.to_pandas()
            
            # Rename columns for consistency
            df = self._standardize_columns(df)
            
            # Add source catalog
            df['source_catalog'] = 'SIMBAD'
            
            logger.info(f"Found {len(df)} SIMBAD objects")
            return df
            
        except Exception as e:
            logger.error(f"Error querying SIMBAD: {e}")
            return None
    
    def query_object(self, identifier: str) -> Optional[pd.DataFrame]:
        """
        Query SIMBAD by object identifier.
        
        Parameters:
        -----------
        identifier : str
            Object name or identifier (e.g., "M31", "NGC 224", "* alf And")
            
        Returns:
        --------
        pd.DataFrame or None
            DataFrame with object data, or None if not found
        """
        if not self.available:
            logger.error("SIMBAD not available")
            return None
            
        try:
            logger.info(f"Querying SIMBAD for object: {identifier}")
            
            result_table = self.simbad.query_object(identifier)
            
            if result_table is None:
                logger.warning(f"Object not found in SIMBAD: {identifier}")
                return None
                
            df = result_table.to_pandas()
            df = self._standardize_columns(df)
            df['source_catalog'] = 'SIMBAD'
            
            logger.info(f"Found object {identifier} in SIMBAD")
            return df
            
        except Exception as e:
            logger.error(f"Error querying object {identifier}: {e}")
            return None
    
    def get_identifiers(self, ra: float, dec: float, radius: float = 0.1) -> List[str]:
        """
        Get all identifiers for objects near coordinates.
        
        Parameters:
        -----------
        ra : float
            Right ascension in degrees
        dec : float
            Declination in degrees
        radius : float
            Search radius in arcminutes (default: 0.1)
            
        Returns:
        --------
        list
            List of all identifiers found
        """
        if not self.available:
            return []
            
        try:
            df = self.cone_search(ra, dec, radius, max_results=10)
            if df is None or len(df) == 0:
                return []
                
            identifiers = []
            if 'ids' in df.columns:
                for ids_str in df['ids']:
                    if pd.notna(ids_str):
                        # Parse pipe-separated identifiers
                        ids = str(ids_str).split('|')
                        identifiers.extend(ids)
            
            return list(set(identifiers))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting identifiers: {e}")
            return []
    
    def get_object_type(self, identifier: str) -> Optional[str]:
        """
        Get object type for given identifier.
        
        Parameters:
        -----------
        identifier : str
            Object identifier
            
        Returns:
        --------
        str or None
            Object type (e.g., "Star", "Galaxy", "Nebula")
        """
        if not self.available:
            return None
            
        try:
            df = self.query_object(identifier)
            if df is None or len(df) == 0:
                return None
                
            if 'object_type' in df.columns:
                return str(df.iloc[0]['object_type'])
            return None
            
        except Exception as e:
            logger.error(f"Error getting object type: {e}")
            return None
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names for consistency with other catalogs.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Raw SIMBAD dataframe
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with standardized column names
        """
        # Column mapping: SIMBAD → Standard
        column_map = {
            'MAIN_ID': 'main_id',
            'RA': 'ra',
            'DEC': 'dec',
            'RA_PREC': 'ra_error',
            'DEC_PREC': 'dec_error',
            'PMRA': 'pmra',
            'PMDEC': 'pmdec',
            'PLX_VALUE': 'parallax',
            'RV_VALUE': 'radial_velocity',
            'Z_VALUE': 'redshift',
            'OTYPE': 'object_type',
            'OTYPES': 'object_types',
            'IDS': 'ids',
            'SP_TYPE': 'spectral_type',
            'FLUX_V': 'v_mag',
            'FLUX_B': 'b_mag',
            'FLUX_K': 'k_mag',
        }
        
        # Rename columns that exist
        for old_name, new_name in column_map.items():
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)
        
        # Ensure RA/Dec are in degrees
        if 'ra' in df.columns:
            df['ra'] = pd.to_numeric(df['ra'], errors='coerce')
        if 'dec' in df.columns:
            df['dec'] = pd.to_numeric(df['dec'], errors='coerce')
            
        return df
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about SIMBAD catalog.
        
        Returns:
        --------
        dict
            Statistics dictionary
        """
        stats = {
            'catalog': 'SIMBAD',
            'available': self.available,
            'total_objects': '~11 million' if self.available else 'N/A',
            'description': 'Set of Identifications, Measurements, and Bibliography for Astronomical Data',
            'coverage': 'All-sky',
            'object_types': [
                'Stars',
                'Galaxies',
                'Nebulae',
                'Star clusters',
                'Quasars',
                'And many more'
            ],
            'data_fields': [
                'Identifiers',
                'Coordinates',
                'Proper motions',
                'Parallax',
                'Radial velocity',
                'Spectral type',
                'Photometry',
                'Object classification'
            ]
        }
        return stats


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*80)
    print("SIMBAD FETCHER TEST")
    print("="*80)
    
    fetcher = SIMBADFetcher()
    
    if not fetcher.is_available():
        print("\n❌ SIMBAD not available!")
        print("Install with: pip install astroquery")
        exit(1)
    
    # Test 1: Cone search around Betelgeuse
    print("\n[Test 1] Cone search near Betelgeuse (α Ori)")
    df = fetcher.cone_search(ra=88.793, dec=7.407, radius=5.0, max_results=20)
    
    if df is not None:
        print(f"✅ Found {len(df)} objects")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nFirst 3 objects:")
        print(df[['main_id', 'ra', 'dec', 'object_type']].head(3))
    else:
        print("❌ No objects found")
    
    # Test 2: Query specific object
    print("\n[Test 2] Query Betelgeuse by name")
    df = fetcher.query_object("Betelgeuse")
    
    if df is not None:
        print(f"✅ Object found")
        print(f"\nMain ID: {df.iloc[0]['main_id']}")
        print(f"Type: {df.iloc[0].get('object_type', 'N/A')}")
        print(f"RA: {df.iloc[0]['ra']:.4f}°")
        print(f"Dec: {df.iloc[0]['dec']:.4f}°")
    else:
        print("❌ Object not found")
    
    # Test 3: Get identifiers
    print("\n[Test 3] Get identifiers near Betelgeuse")
    identifiers = fetcher.get_identifiers(ra=88.793, dec=7.407, radius=0.5)
    
    if identifiers:
        print(f"✅ Found {len(identifiers)} identifiers")
        print(f"Examples: {identifiers[:5]}")
    else:
        print("❌ No identifiers found")
    
    # Test 4: Statistics
    print("\n[Test 4] SIMBAD Statistics")
    stats = fetcher.get_statistics()
    print(f"✅ Catalog: {stats['catalog']}")
    print(f"   Objects: {stats['total_objects']}")
    print(f"   Coverage: {stats['coverage']}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETE")
    print("="*80)
