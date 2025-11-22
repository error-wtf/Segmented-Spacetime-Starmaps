#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exoplanet Fetcher - Sprint 3 Task 1

Queries NASA Exoplanet Archive for confirmed exoplanets.
Provides planetary and host star parameters for SSZ analysis.

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
    from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
    EXOPLANET_AVAILABLE = True
    logger.info("NASA Exoplanet Archive module loaded successfully")
except ImportError:
    EXOPLANET_AVAILABLE = False
    logger.warning("astroquery.ipac.nexsci not available - exoplanet queries will not work")


class ExoplanetFetcher:
    """
    Fetches exoplanet data from NASA Exoplanet Archive.
    
    NASA Exoplanet Archive contains 5,500+ confirmed exoplanets
    with orbital parameters, masses, radii, and host star properties.
    """
    
    def __init__(self):
        """Initialize Exoplanet fetcher."""
        self.available = EXOPLANET_AVAILABLE
        
        if not self.available:
            logger.warning("Exoplanet Archive not available - install with: pip install astroquery")
            return
        
        # Use PS (Planetary Systems) table - most complete
        self.table = 'ps'
        
        logger.info("ExoplanetFetcher initialized")
    
    def is_available(self) -> bool:
        """Check if Exoplanet Archive is available."""
        return self.available
    
    def query_all(self, max_results: int = 10000) -> Optional[pd.DataFrame]:
        """
        Query all confirmed exoplanets.
        
        Parameters:
        -----------
        max_results : int
            Maximum number of results (default: 10000, covers all ~5,500)
            
        Returns:
        --------
        pd.DataFrame or None
            DataFrame with exoplanet data, or None if error
        """
        if not self.available:
            logger.error("Exoplanet Archive not available")
            return None
        
        try:
            logger.info("Querying all confirmed exoplanets...")
            
            # Query confirmed planets
            result = NasaExoplanetArchive.query_criteria(
                table=self.table,
                select='*',
                cache=True
            )
            
            if result is None or len(result) == 0:
                logger.warning("No exoplanets found")
                return None
            
            # Convert to pandas
            df = result.to_pandas()
            
            # Standardize columns
            df = self._standardize_columns(df)
            
            # Add source catalog
            df['source_catalog'] = 'NASA_Exoplanet_Archive'
            
            logger.info(f"Found {len(df)} confirmed exoplanets")
            return df
            
        except Exception as e:
            logger.error(f"Error querying exoplanets: {e}")
            return None
    
    def cone_search(
        self,
        ra: float,
        dec: float,
        radius: float = 5.0,
        max_results: int = 1000
    ) -> Optional[pd.DataFrame]:
        """
        Cone search for exoplanets by host star coordinates.
        
        Parameters:
        -----------
        ra : float
            Right ascension in degrees (J2000)
        dec : float
            Declination in degrees (J2000)
        radius : float
            Search radius in degrees (default: 5.0)
        max_results : int
            Maximum number of results (default: 1000)
            
        Returns:
        --------
        pd.DataFrame or None
            DataFrame with exoplanet data, or None if error
        """
        if not self.available:
            logger.error("Exoplanet Archive not available")
            return None
        
        try:
            logger.info(f"Cone search: RA={ra:.4f}, Dec={dec:.4f}, radius={radius:.2f}°")
            
            # Query with coordinate constraint
            # Note: NASA Exoplanet Archive uses ra/dec for host stars
            result = NasaExoplanetArchive.query_region(
                table=self.table,
                coordinates=f"{ra} {dec}",
                radius=f"{radius} deg",
                cache=True
            )
            
            if result is None or len(result) == 0:
                logger.warning(f"No exoplanets found at RA={ra:.4f}, Dec={dec:.4f}")
                return None
            
            df = result.to_pandas()
            df = self._standardize_columns(df)
            df['source_catalog'] = 'NASA_Exoplanet_Archive'
            
            logger.info(f"Found {len(df)} exoplanets in cone")
            return df
            
        except Exception as e:
            logger.error(f"Error in cone search: {e}")
            return None
    
    def query_by_host(self, host_name: str) -> Optional[pd.DataFrame]:
        """
        Query exoplanets by host star name.
        
        Parameters:
        -----------
        host_name : str
            Host star name (e.g., "Kepler-186", "HD 209458")
            
        Returns:
        --------
        pd.DataFrame or None
            DataFrame with planets around this host, or None if not found
        """
        if not self.available:
            logger.error("Exoplanet Archive not available")
            return None
        
        try:
            logger.info(f"Querying planets around host: {host_name}")
            
            # Query by hostname
            result = NasaExoplanetArchive.query_criteria(
                table=self.table,
                select='*',
                where=f"hostname like '%{host_name}%'",
                cache=True
            )
            
            if result is None or len(result) == 0:
                logger.warning(f"No planets found for host: {host_name}")
                return None
            
            df = result.to_pandas()
            df = self._standardize_columns(df)
            df['source_catalog'] = 'NASA_Exoplanet_Archive'
            
            logger.info(f"Found {len(df)} planets around {host_name}")
            return df
            
        except Exception as e:
            logger.error(f"Error querying host {host_name}: {e}")
            return None
    
    def query_by_params(
        self,
        min_mass: Optional[float] = None,
        max_mass: Optional[float] = None,
        min_radius: Optional[float] = None,
        max_radius: Optional[float] = None,
        min_period: Optional[float] = None,
        max_period: Optional[float] = None,
        discovery_method: Optional[str] = None,
        max_results: int = 1000
    ) -> Optional[pd.DataFrame]:
        """
        Query exoplanets by parameters.
        
        Parameters:
        -----------
        min_mass : float
            Minimum planet mass in Jupiter masses
        max_mass : float
            Maximum planet mass in Jupiter masses
        min_radius : float
            Minimum planet radius in Jupiter radii
        max_radius : float
            Maximum planet radius in Jupiter radii
        min_period : float
            Minimum orbital period in days
        max_period : float
            Maximum orbital period in days
        discovery_method : str
            Discovery method (e.g., "Transit", "Radial Velocity")
        max_results : int
            Maximum number of results
            
        Returns:
        --------
        pd.DataFrame or None
            DataFrame with filtered exoplanets
        """
        if not self.available:
            logger.error("Exoplanet Archive not available")
            return None
        
        try:
            # Build WHERE clause
            conditions = []
            
            if min_mass is not None:
                conditions.append(f"pl_bmassj >= {min_mass}")
            if max_mass is not None:
                conditions.append(f"pl_bmassj <= {max_mass}")
            if min_radius is not None:
                conditions.append(f"pl_radj >= {min_radius}")
            if max_radius is not None:
                conditions.append(f"pl_radj <= {max_radius}")
            if min_period is not None:
                conditions.append(f"pl_orbper >= {min_period}")
            if max_period is not None:
                conditions.append(f"pl_orbper <= {max_period}")
            if discovery_method is not None:
                conditions.append(f"discoverymethod = '{discovery_method}'")
            
            where_clause = " and ".join(conditions) if conditions else None
            
            logger.info(f"Querying with filters: {where_clause}")
            
            # Query
            result = NasaExoplanetArchive.query_criteria(
                table=self.table,
                select='*',
                where=where_clause,
                cache=True
            )
            
            if result is None or len(result) == 0:
                logger.warning("No planets match filters")
                return None
            
            df = result.to_pandas()
            df = self._standardize_columns(df)
            df['source_catalog'] = 'NASA_Exoplanet_Archive'
            
            logger.info(f"Found {len(df)} planets matching filters")
            return df
            
        except Exception as e:
            logger.error(f"Error in parameter query: {e}")
            return None
    
    def get_habitable_zone_candidates(self) -> Optional[pd.DataFrame]:
        """
        Get potentially habitable exoplanets.
        
        Criteria:
        - Earth-like size (0.5 - 2.0 Earth radii)
        - Temperate (equilibrium temp 200-350 K)
        - Known host star luminosity
        
        Returns:
        --------
        pd.DataFrame or None
            Habitable zone candidate planets
        """
        if not self.available:
            return None
        
        try:
            logger.info("Querying habitable zone candidates...")
            
            # Query with HZ criteria
            # pl_rade: planet radius in Earth radii
            # pl_eqt: equilibrium temperature
            result = NasaExoplanetArchive.query_criteria(
                table=self.table,
                select='*',
                where="pl_rade >= 0.5 and pl_rade <= 2.0 and pl_eqt >= 200 and pl_eqt <= 350",
                cache=True
            )
            
            if result is None or len(result) == 0:
                logger.warning("No HZ candidates found")
                return None
            
            df = result.to_pandas()
            df = self._standardize_columns(df)
            df['source_catalog'] = 'NASA_Exoplanet_Archive'
            df['hz_candidate'] = True
            
            logger.info(f"Found {len(df)} HZ candidates")
            return df
            
        except Exception as e:
            logger.error(f"Error querying HZ candidates: {e}")
            return None
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names for consistency.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Raw NASA Exoplanet Archive DataFrame
            
        Returns:
        --------
        pd.DataFrame
            Standardized DataFrame
        """
        # Key column mappings
        column_map = {
            # Host star
            'hostname': 'host_name',
            'ra': 'ra',
            'dec': 'dec',
            'sy_dist': 'distance_pc',
            'st_teff': 'host_teff',
            'st_rad': 'host_radius_rsun',
            'st_mass': 'host_mass_msun',
            'st_lum': 'host_luminosity',
            
            # Planet
            'pl_name': 'planet_name',
            'pl_orbper': 'period_days',
            'pl_orbsmax': 'semi_major_axis_au',
            'pl_rade': 'radius_rearth',
            'pl_radj': 'radius_rjup',
            'pl_bmasse': 'mass_mearth',
            'pl_bmassj': 'mass_mjup',
            'pl_orbeccen': 'eccentricity',
            'pl_eqt': 'equilibrium_temp_k',
            'pl_orbincl': 'inclination_deg',
            'discoverymethod': 'discovery_method',
            'disc_year': 'discovery_year',
        }
        
        # Rename columns that exist
        for old_name, new_name in column_map.items():
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)
        
        # Ensure numeric types
        numeric_cols = [
            'ra', 'dec', 'distance_pc', 'host_teff', 'host_radius_rsun', 'host_mass_msun',
            'period_days', 'semi_major_axis_au', 'radius_rearth', 'mass_mearth',
            'eccentricity', 'equilibrium_temp_k', 'inclination_deg'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about exoplanet catalog.
        
        Returns:
        --------
        dict
            Statistics dictionary
        """
        stats = {
            'catalog': 'NASA Exoplanet Archive',
            'available': self.available,
            'total_planets': '5,500+' if self.available else 'N/A',
            'description': 'Confirmed exoplanets from all discovery methods',
            'coverage': 'All-sky',
            'discovery_methods': [
                'Transit',
                'Radial Velocity',
                'Imaging',
                'Microlensing',
                'Transit Timing Variations',
                'Astrometry',
                'Orbital Brightness Modulation',
                'Pulsar Timing'
            ],
            'parameters': [
                'Orbital period',
                'Semi-major axis',
                'Planet mass & radius',
                'Eccentricity',
                'Inclination',
                'Equilibrium temperature',
                'Host star properties',
                'Discovery information'
            ],
            'applications': [
                'SSZ orbital corrections',
                'Habitable zone studies',
                'Transit predictions',
                'Host star characterization',
                'Population statistics'
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
    print("EXOPLANET FETCHER TEST")
    print("="*80)
    
    fetcher = ExoplanetFetcher()
    
    if not fetcher.is_available():
        print("\n❌ Exoplanet Archive not available!")
        print("Install with: pip install astroquery")
        exit(1)
    
    # Test 1: Query by host star
    print("\n[Test 1] Query planets around Kepler-186")
    df = fetcher.query_by_host("Kepler-186")
    
    if df is not None:
        print(f"✅ Found {len(df)} planets")
        cols = ['planet_name', 'period_days', 'radius_rearth', 'equilibrium_temp_k']
        available = [c for c in cols if c in df.columns]
        print(f"\nPlanets:")
        print(df[available])
    
    # Test 2: Habitable zone candidates
    print("\n[Test 2] Habitable Zone Candidates")
    df_hz = fetcher.get_habitable_zone_candidates()
    
    if df_hz is not None:
        print(f"✅ Found {len(df_hz)} HZ candidates")
        print(f"\nSample candidates:")
        cols = ['planet_name', 'radius_rearth', 'equilibrium_temp_k', 'period_days']
        available = [c for c in cols if c in df_hz.columns]
        print(df_hz[available].head(5))
    
    # Test 3: Parameter query (Hot Jupiters)
    print("\n[Test 3] Hot Jupiters (M>0.5 Mjup, P<10 days)")
    df_hj = fetcher.query_by_params(
        min_mass=0.5,
        max_period=10.0,
        max_results=20
    )
    
    if df_hj is not None:
        print(f"✅ Found {len(df_hj)} Hot Jupiters")
        cols = ['planet_name', 'mass_mjup', 'period_days', 'host_name']
        available = [c for c in cols if c in df_hj.columns]
        print(f"\nSample Hot Jupiters:")
        print(df_hj[available].head(5))
    
    # Test 4: Statistics
    print("\n[Test 4] Catalog Statistics")
    stats = fetcher.get_statistics()
    print(f"✅ Catalog: {stats['catalog']}")
    print(f"   Planets: {stats['total_planets']}")
    print(f"   Methods: {len(stats['discovery_methods'])}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETE")
    print("="*80)
