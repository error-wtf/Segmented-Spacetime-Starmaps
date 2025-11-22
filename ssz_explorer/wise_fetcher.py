#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WISE Catalog Fetcher - Sprint 2 Task 3

Queries WISE (Wide-field Infrared Survey Explorer) for mid-infrared photometry.
Provides W1, W2, W3, W4 band magnitudes for 747+ million sources.

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
    from astroquery.vizier import Vizier
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    VIZIER_AVAILABLE = True
    logger.info("Vizier module loaded successfully")
except ImportError:
    VIZIER_AVAILABLE = False
    logger.warning("astroquery.vizier not available - WISE queries will not work")


class WISEFetcher:
    """
    Fetches mid-infrared photometry from WISE (AllWISE) catalog.
    
    WISE (Wide-field Infrared Survey Explorer) contains mid-IR photometry
    for 747+ million sources across the entire sky.
    
    Bands:
    - W1: 3.4 μm
    - W2: 4.6 μm
    - W3: 12 μm
    - W4: 22 μm
    """
    
    def __init__(self):
        """Initialize WISE fetcher."""
        self.available = VIZIER_AVAILABLE
        
        if not self.available:
            logger.warning("WISE not available - install with: pip install astroquery")
            return
            
        # Configure Vizier
        self.vizier = Vizier(columns=['*'], row_limit=-1)
        self.catalog = 'II/328/allwise'  # AllWISE Source Catalog
        
        logger.info("WISEFetcher initialized")
    
    def is_available(self) -> bool:
        """Check if WISE is available."""
        return self.available
    
    def cone_search(
        self,
        ra: float,
        dec: float,
        radius: float = 1.0,
        max_results: int = 1000,
        bands: List[str] = ['W1', 'W2'],
        quality_filter: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Perform cone search in WISE catalog.
        
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
        bands : list
            Bands to include ['W1', 'W2', 'W3', 'W4'] (default: ['W1', 'W2'])
        quality_filter : bool
            Apply quality filters (default: True)
            
        Returns:
        --------
        pd.DataFrame or None
            DataFrame with WISE data, or None if error
        """
        if not self.available:
            logger.error("WISE not available")
            return None
            
        try:
            logger.info(f"Querying WISE: RA={ra:.4f}, Dec={dec:.4f}, radius={radius:.2f}'")
            
            # Set row limit
            self.vizier.ROW_LIMIT = max_results
            
            # Create coordinate
            coord = SkyCoord(ra=ra, dec=dec, unit=(u.degree, u.degree), frame='icrs')
            
            # Query Vizier
            result = self.vizier.query_region(
                coord,
                radius=radius * u.arcmin,
                catalog=self.catalog
            )
            
            if not result or len(result) == 0:
                logger.warning(f"No WISE sources found at RA={ra:.4f}, Dec={dec:.4f}")
                return None
            
            # Get first table (AllWISE)
            table = result[0]
            
            # Convert to pandas
            df = table.to_pandas()
            
            # Standardize columns
            df = self._standardize_columns(df)
            
            # Filter by requested bands
            df = self._filter_bands(df, bands)
            
            # Apply quality filter
            if quality_filter:
                df = self._apply_quality_filter(df)
            
            # Add source catalog
            df['source_catalog'] = 'WISE'
            
            logger.info(f"Found {len(df)} WISE sources")
            return df
            
        except Exception as e:
            logger.error(f"Error querying WISE: {e}")
            return None
    
    def get_sed(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build spectral energy distribution from WISE bands.
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with WISE photometry
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with added SED information
        """
        if df is None or len(df) == 0:
            return df
            
        try:
            # Calculate color temperatures (simplified)
            # W1-W2 correlates with stellar temperature
            if 'w1_mag' in df.columns and 'w2_mag' in df.columns:
                df['w1_w2'] = df['w1_mag'] - df['w2_mag']
            
            # W2-W3 sensitive to dust emission
            if 'w2_mag' in df.columns and 'w3_mag' in df.columns:
                df['w2_w3'] = df['w2_mag'] - df['w3_mag']
            
            # W3-W4 for very cool/dusty objects
            if 'w3_mag' in df.columns and 'w4_mag' in df.columns:
                df['w3_w4'] = df['w3_mag'] - df['w4_mag']
            
            logger.info("Built SED information")
            return df
            
        except Exception as e:
            logger.error(f"Error building SED: {e}")
            return df
    
    def classify_objects(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify objects based on WISE colors.
        
        Simple classification:
        - Stars: W1-W2 < 0.8
        - AGN candidates: W1-W2 > 0.8
        - YSOs: W1-W2 > 0.5, W3-W4 > 2
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with WISE colors
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with classification column
        """
        if df is None or len(df) == 0:
            return df
            
        try:
            # Ensure colors exist
            df = self.get_sed(df)
            
            # Initialize classification
            df['wise_class'] = 'Unknown'
            
            if 'w1_w2' in df.columns:
                # Stars
                mask_star = (df['w1_w2'] < 0.8)
                df.loc[mask_star, 'wise_class'] = 'Star'
                
                # AGN candidates
                mask_agn = (df['w1_w2'] > 0.8)
                df.loc[mask_agn, 'wise_class'] = 'AGN_candidate'
                
                # YSO candidates (if W3-W4 available)
                if 'w3_w4' in df.columns:
                    mask_yso = (df['w1_w2'] > 0.5) & (df['w3_w4'] > 2.0)
                    df.loc[mask_yso, 'wise_class'] = 'YSO_candidate'
            
            logger.info("Object classification complete")
            return df
            
        except Exception as e:
            logger.error(f"Error classifying objects: {e}")
            return df
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names."""
        column_map = {
            'RAJ2000': 'ra',
            'DEJ2000': 'dec',
            'W1mag': 'w1_mag',
            'W2mag': 'w2_mag',
            'W3mag': 'w3_mag',
            'W4mag': 'w4_mag',
            'e_W1mag': 'w1_mag_error',
            'e_W2mag': 'w2_mag_error',
            'e_W3mag': 'w3_mag_error',
            'e_W4mag': 'w4_mag_error',
            'qph': 'quality_ph',
            'ccf': 'contamination',
            'AllWISE': 'wise_id',
        }
        
        for old_name, new_name in column_map.items():
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)
        
        # Ensure numeric
        for col in ['ra', 'dec', 'w1_mag', 'w2_mag', 'w3_mag', 'w4_mag']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _filter_bands(self, df: pd.DataFrame, bands: List[str]) -> pd.DataFrame:
        """Keep only requested bands."""
        # Always keep coordinates and ID
        keep_cols = ['ra', 'dec', 'wise_id']
        
        # Add requested band columns
        for band in bands:
            band_lower = band.lower()
            keep_cols.extend([
                f'{band_lower}_mag',
                f'{band_lower}_mag_error'
            ])
        
        # Keep columns that exist
        keep_cols = [c for c in keep_cols if c in df.columns]
        
        # Keep quality flags if present
        for col in ['quality_ph', 'contamination']:
            if col in df.columns:
                keep_cols.append(col)
        
        return df[keep_cols].copy()
    
    def _apply_quality_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply quality filters to WISE data.
        
        Quality flag (qph): ABCD for W1/W2/W3/W4
        - A: S/N > 10
        - B: 3 < S/N ≤ 10
        - C: 2 < S/N ≤ 3
        - D: S/N ≤ 2 or upper limit
        - U: Upper limit
        """
        if 'quality_ph' not in df.columns:
            logger.warning("No quality_ph column - skipping quality filter")
            return df
        
        initial_count = len(df)
        
        try:
            # Keep sources with at least one A or B quality band
            mask = df['quality_ph'].str.contains('[AB]', na=False, regex=True)
            df = df[mask].copy()
            
            filtered_count = initial_count - len(df)
            if filtered_count > 0:
                logger.info(f"Quality filter removed {filtered_count} sources")
            
            return df
            
        except Exception as e:
            logger.error(f"Error applying quality filter: {e}")
            return df
    
    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about WISE catalog."""
        stats = {
            'catalog': 'WISE',
            'full_name': 'Wide-field Infrared Survey Explorer (AllWISE)',
            'available': self.available,
            'total_sources': '747+ million' if self.available else 'N/A',
            'description': 'Mid-infrared photometry of the entire sky',
            'coverage': 'All-sky',
            'bands': {
                'W1': '3.4 μm',
                'W2': '4.6 μm',
                'W3': '12 μm',
                'W4': '22 μm'
            },
            'typical_depth': {
                'W1': '16.6 mag (5σ)',
                'W2': '15.6 mag (5σ)',
                'W3': '11.3 mag (5σ)',
                'W4': '8.0 mag (5σ)'
            },
            'spatial_resolution': '6 arcsec (W1/W2), 12 arcsec (W3/W4)',
            'astrometric_accuracy': '≤ 0.15 arcsec',
            'survey_dates': '2010-2011 (primary), 2010-2014 (extended)',
            'data_release': 'AllWISE (2013)',
            'applications': [
                'AGN detection',
                'YSO identification',
                'Stellar classification',
                'Dust emission studies',
                'Brown dwarf searches'
            ]
        }
        return stats


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*80)
    print("WISE FETCHER TEST")
    print("="*80)
    
    fetcher = WISEFetcher()
    
    if not fetcher.is_available():
        print("\n❌ WISE not available!")
        print("Install with: pip install astroquery")
        exit(1)
    
    # Test 1: Cone search (W1/W2 only for speed)
    print("\n[Test 1] Cone search near Betelgeuse (W1/W2)")
    df = fetcher.cone_search(
        ra=88.793, dec=7.407, radius=5.0, 
        max_results=50, bands=['W1', 'W2']
    )
    
    if df is not None:
        print(f"✅ Found {len(df)} sources")
        print(f"\nColumns: {list(df.columns)}")
        
        cols = ['ra', 'dec', 'w1_mag', 'w2_mag']
        available_cols = [c for c in cols if c in df.columns]
        print(f"\nFirst 3 sources:")
        print(df[available_cols].head(3))
        
        # Test 2: SED
        print("\n[Test 2] Build SED")
        df = fetcher.get_sed(df)
        if 'w1_w2' in df.columns:
            print(f"✅ SED built")
            print(f"   Mean W1-W2: {df['w1_w2'].mean():.3f}")
        
        # Test 3: Classification
        print("\n[Test 3] Object Classification")
        df = fetcher.classify_objects(df)
        if 'wise_class' in df.columns:
            print(f"✅ Classification complete")
            print(f"\nClass distribution:")
            print(df['wise_class'].value_counts())
    else:
        print("❌ No sources found")
    
    # Test 4: Statistics
    print("\n[Test 4] Catalog Statistics")
    stats = fetcher.get_statistics()
    print(f"✅ Catalog: {stats['full_name']}")
    print(f"   Sources: {stats['total_sources']}")
    print(f"   Bands: {', '.join(stats['bands'].keys())}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETE")
    print("="*80)
