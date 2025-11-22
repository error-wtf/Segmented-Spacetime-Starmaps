#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2MASS Catalog Fetcher - Sprint 2 Task 2

Queries 2MASS (Two Micron All Sky Survey) for near-infrared photometry.
Provides J, H, K band magnitudes for 470+ million sources.

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
    logger.warning("astroquery.vizier not available - 2MASS queries will not work")


class TwoMASSFetcher:
    """
    Fetches near-infrared photometry from 2MASS catalog.
    
    2MASS (Two Micron All Sky Survey) contains J, H, K band photometry
    for 470+ million point sources across the entire sky.
    
    Bands:
    - J: 1.25 μm
    - H: 1.65 μm  
    - K: 2.17 μm (Ks band)
    """
    
    def __init__(self):
        """Initialize 2MASS fetcher."""
        self.available = VIZIER_AVAILABLE
        
        if not self.available:
            logger.warning("2MASS not available - install with: pip install astroquery")
            return
            
        # Configure Vizier
        self.vizier = Vizier(columns=['*'], row_limit=-1)  # All columns
        self.catalog = 'II/246/out'  # 2MASS Point Source Catalog
        
        logger.info("TwoMASSFetcher initialized")
    
    def is_available(self) -> bool:
        """Check if 2MASS is available."""
        return self.available
    
    def cone_search(
        self,
        ra: float,
        dec: float,
        radius: float = 1.0,
        max_results: int = 1000,
        quality_filter: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Perform cone search in 2MASS catalog.
        
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
        quality_filter : bool
            Apply quality filters (default: True)
            
        Returns:
        --------
        pd.DataFrame or None
            DataFrame with 2MASS data, or None if error
        """
        if not self.available:
            logger.error("2MASS not available")
            return None
            
        try:
            logger.info(f"Querying 2MASS: RA={ra:.4f}, Dec={dec:.4f}, radius={radius:.2f}'")
            
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
                logger.warning(f"No 2MASS sources found at RA={ra:.4f}, Dec={dec:.4f}")
                return None
            
            # Get first table (2MASS PSC)
            table = result[0]
            
            # Convert to pandas
            df = table.to_pandas()
            
            # Standardize columns
            df = self._standardize_columns(df)
            
            # Apply quality filter
            if quality_filter:
                df = self._apply_quality_filter(df)
            
            # Add source catalog
            df['source_catalog'] = '2MASS'
            
            logger.info(f"Found {len(df)} 2MASS sources")
            return df
            
        except Exception as e:
            logger.error(f"Error querying 2MASS: {e}")
            return None
    
    def get_colors(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate color indices from photometry.
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with J, H, K magnitudes
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with added color columns
        """
        if df is None or len(df) == 0:
            return df
            
        try:
            # Calculate colors
            if 'j_mag' in df.columns and 'h_mag' in df.columns:
                df['j_h'] = df['j_mag'] - df['h_mag']
            
            if 'h_mag' in df.columns and 'k_mag' in df.columns:
                df['h_k'] = df['h_mag'] - df['k_mag']
            
            if 'j_mag' in df.columns and 'k_mag' in df.columns:
                df['j_k'] = df['j_mag'] - df['k_mag']
            
            logger.info("Calculated color indices")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating colors: {e}")
            return df
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Raw 2MASS DataFrame
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with standardized columns
        """
        # Column mapping: 2MASS → Standard
        column_map = {
            'RAJ2000': 'ra',
            'DEJ2000': 'dec',
            'Jmag': 'j_mag',
            'Hmag': 'h_mag',
            'Kmag': 'k_mag',
            'e_Jmag': 'j_mag_error',
            'e_Hmag': 'h_mag_error',
            'e_Kmag': 'k_mag_error',
            'Qflg': 'quality_flag',
            'Rflg': 'read_flag',
            'Bflg': 'blend_flag',
            'Cflg': 'contamination_flag',
            '_2MASS': 'tmass_id',
        }
        
        # Rename columns that exist
        for old_name, new_name in column_map.items():
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)
        
        # Ensure numeric types
        for col in ['ra', 'dec', 'j_mag', 'h_mag', 'k_mag']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _apply_quality_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply quality filters to 2MASS data.
        
        Quality flag (Qflg): AAA is best, UUU is worst
        - A: S/N >= 10
        - B: 7 <= S/N < 10
        - C: 5 <= S/N < 7
        - D: 3 <= S/N < 5
        - E: 1 <= S/N < 3
        - F: S/N < 1
        - U: Upper limit
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with quality_flag column
            
        Returns:
        --------
        pd.DataFrame
            Filtered DataFrame
        """
        if 'quality_flag' not in df.columns:
            logger.warning("No quality_flag column - skipping quality filter")
            return df
        
        initial_count = len(df)
        
        try:
            # Keep only A, B, C quality (S/N >= 5 in at least one band)
            mask = df['quality_flag'].str.contains('[ABC]', na=False, regex=True)
            df = df[mask].copy()
            
            filtered_count = initial_count - len(df)
            if filtered_count > 0:
                logger.info(f"Quality filter removed {filtered_count} sources")
            
            return df
            
        except Exception as e:
            logger.error(f"Error applying quality filter: {e}")
            return df
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about 2MASS catalog.
        
        Returns:
        --------
        dict
            Statistics dictionary
        """
        stats = {
            'catalog': '2MASS',
            'full_name': 'Two Micron All Sky Survey',
            'available': self.available,
            'total_sources': '470+ million' if self.available else 'N/A',
            'description': 'Near-infrared photometry of the entire sky',
            'coverage': 'All-sky',
            'bands': {
                'J': '1.25 μm',
                'H': '1.65 μm',
                'K': '2.17 μm (Ks)'
            },
            'typical_depth': {
                'J': '15.8 mag (10σ)',
                'H': '15.1 mag (10σ)',
                'K': '14.3 mag (10σ)'
            },
            'spatial_resolution': '2.5 arcsec',
            'photometric_accuracy': '≤ 0.03 mag',
            'astrometric_accuracy': '≤ 0.1 arcsec',
            'survey_dates': '1997-2001',
            'data_release': 'Final (2003)'
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
    print("2MASS FETCHER TEST")
    print("="*80)
    
    fetcher = TwoMASSFetcher()
    
    if not fetcher.is_available():
        print("\n❌ 2MASS not available!")
        print("Install with: pip install astroquery")
        exit(1)
    
    # Test 1: Cone search near Betelgeuse
    print("\n[Test 1] Cone search near Betelgeuse")
    df = fetcher.cone_search(ra=88.793, dec=7.407, radius=5.0, max_results=50)
    
    if df is not None:
        print(f"✅ Found {len(df)} sources")
        print(f"\nColumns: {list(df.columns)}")
        
        # Show sample
        cols = ['ra', 'dec', 'j_mag', 'h_mag', 'k_mag', 'quality_flag']
        available_cols = [c for c in cols if c in df.columns]
        print(f"\nFirst 3 sources:")
        print(df[available_cols].head(3))
        
        # Test 2: Calculate colors
        print("\n[Test 2] Calculate color indices")
        df = fetcher.get_colors(df)
        
        if 'j_h' in df.columns:
            print(f"✅ Colors calculated")
            print(f"   Mean J-H: {df['j_h'].mean():.3f}")
            print(f"   Mean H-K: {df['h_k'].mean():.3f}")
            print(f"   Mean J-K: {df['j_k'].mean():.3f}")
        
    else:
        print("❌ No sources found")
    
    # Test 3: Statistics
    print("\n[Test 3] Catalog Statistics")
    stats = fetcher.get_statistics()
    print(f"✅ Catalog: {stats['full_name']}")
    print(f"   Sources: {stats['total_sources']}")
    print(f"   Bands: {', '.join(stats['bands'].keys())}")
    print(f"   Coverage: {stats['coverage']}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETE")
    print("="*80)
