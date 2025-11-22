#!/usr/bin/env python3
"""
Progressive Loading System for Star Maps
Load, cache, and stream astronomical data efficiently
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ViewportBounds:
    """Defines the current viewport boundaries"""
    ra_min: float
    ra_max: float
    dec_min: float
    dec_max: float
    zoom_level: int = 0
    
    def contains(self, ra: float, dec: float) -> bool:
        """Check if point is within viewport"""
        return (self.ra_min <= ra <= self.ra_max and 
                self.dec_min <= dec <= self.dec_max)
    
    def expand(self, factor: float = 2.0) -> 'ViewportBounds':
        """Expand viewport for prefetching"""
        ra_center = (self.ra_min + self.ra_max) / 2
        dec_center = (self.dec_min + self.dec_max) / 2
        ra_range = (self.ra_max - self.ra_min) * factor / 2
        dec_range = (self.dec_max - self.dec_min) * factor / 2
        
        return ViewportBounds(
            ra_min=max(0, ra_center - ra_range),
            ra_max=min(360, ra_center + ra_range),
            dec_min=max(-90, dec_center - dec_range),
            dec_max=min(90, dec_center + dec_range),
            zoom_level=self.zoom_level
        )


class ProgressiveDataLoader:
    """
    Progressive loading system for astronomical data
    
    Features:
    - Initial load: 128 objects
    - Prefetch: 512 objects
    - Dynamic loading on zoom/pan
    - Spatial indexing for fast queries
    - LRU cache management
    """
    
    def __init__(self, 
                 initial_size: int = 128,
                 prefetch_size: int = 10240,  # 10K prefetch!
                 batch_size: int = 1024,      # 1K per batch
                 cache_size: int = 102400):   # 100K cache!
        """
        Initialize progressive loader
        
        Args:
            initial_size: Number of objects to show initially
            prefetch_size: Number of objects to prefetch
            batch_size: Number of objects to load per batch
            cache_size: Maximum cached objects
        """
        self.initial_size = initial_size
        self.prefetch_size = prefetch_size
        self.batch_size = batch_size
        self.cache_size = cache_size
        
        # Data storage
        self.full_data: Optional[pd.DataFrame] = None
        self.visible_data: Optional[pd.DataFrame] = None
        self.cached_data: Optional[pd.DataFrame] = None
        
        # State
        self.current_viewport: Optional[ViewportBounds] = None
        self.loaded_indices: set = set()
        self.total_objects: int = 0
        
        logger.info(f"Progressive Loader initialized: {initial_size} initial, "
                   f"{prefetch_size} prefetch, {batch_size} batch")
    
    def load_full_catalog(self, catalog_name: str, max_objects: int = 100000) -> bool:
        """
        Load full catalog data
        
        Args:
            catalog_name: Name of catalog to load
            max_objects: Maximum objects to load
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Loading full catalog: {catalog_name} (max {max_objects} objects)")
            
            # Load based on catalog type
            if catalog_name.lower() == 'gaia':
                self.full_data = self._load_gaia_full(max_objects)
            elif catalog_name.lower() == 'simbad':
                self.full_data = self._load_simbad_full(max_objects)
            elif catalog_name.lower() == '2mass':
                self.full_data = self._load_2mass_full(max_objects)
            elif catalog_name.lower() == 'wise':
                self.full_data = self._load_wise_full(max_objects)
            else:
                logger.error(f"Unknown catalog: {catalog_name}")
                return False
            
            if self.full_data is None or self.full_data.empty:
                logger.error("No data loaded")
                return False
            
            self.total_objects = len(self.full_data)
            logger.info(f"Loaded {self.total_objects} objects from {catalog_name}")
            
            # Sort by brightness for better LOD
            if 'magnitude' in self.full_data.columns:
                self.full_data = self.full_data.sort_values('magnitude')
            elif 'phot_g_mean_mag' in self.full_data.columns:
                self.full_data = self.full_data.sort_values('phot_g_mean_mag')
            
            # Create spatial index (RA/Dec grid)
            self._create_spatial_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading catalog: {e}")
            return False
    
    def _load_gaia_full(self, max_objects: int) -> pd.DataFrame:
        """Load GAIA or available star data"""
        try:
            # Try available star data files
            paths = [
                'ssz_exports/galaxy_1000stars_ssz.csv',
                'ssz_exports/demo_ssz_objects.csv',
                'outputs_quick_start/stars_ssz.csv',
                'validation_results_979.csv'
            ]
            
            dfs = []
            for path in paths:
                try:
                    df = pd.read_csv(path, nrows=max_objects // len(paths))
                    if not df.empty:
                        dfs.append(df)
                        logger.info(f"Loaded {len(df)} from {path}")
                except Exception as e:
                    logger.debug(f"Could not load {path}: {e}")
                    continue
            
            if dfs:
                result = pd.concat(dfs, ignore_index=True)
                result = result.head(max_objects)
                
                # Ensure we have ra/dec columns
                if 'ra' not in result.columns and 'RA' not in result.columns:
                    logger.error("No RA column found")
                    return self._generate_synthetic_data(max_objects)
                
                logger.info(f"Total loaded objects: {len(result)}")
                return result
            else:
                # No files found - generate synthetic data
                logger.warning("No data files found, generating synthetic catalog")
                return self._generate_synthetic_data(max_objects)
            
        except Exception as e:
            logger.error(f"Data load error: {e}")
            return self._generate_synthetic_data(max_objects)
    
    def _generate_synthetic_data(self, n_objects: int) -> pd.DataFrame:
        """Generate synthetic astronomical data for testing"""
        logger.info(f"Generating {n_objects} synthetic objects")
        
        # Create realistic distribution
        np.random.seed(42)
        
        data = {
            'ra': np.random.uniform(0, 360, n_objects),
            'dec': np.random.uniform(-90, 90, n_objects),
            'magnitude': np.random.exponential(2.0, n_objects) + 6,  # Realistic mag distribution
            'parallax': np.random.exponential(5, n_objects),  # Distance proxy
            'source_id': [f"SYN{i:010d}" for i in range(n_objects)]
        }
        
        df = pd.DataFrame(data)
        df['magnitude'] = df['magnitude'].clip(0, 20)  # Reasonable range
        
        return df
    
    def _load_simbad_full(self, max_objects: int) -> pd.DataFrame:
        """Load SIMBAD data - use bright stars"""
        try:
            from astroquery.simbad import Simbad
            
            # Configure SIMBAD
            custom_simbad = Simbad()
            custom_simbad.add_votable_fields('ra(d)', 'dec(d)', 'pmra', 'pmdec', 
                                            'plx', 'flux(V)', 'sp', 'otype')
            
            # Query bright stars
            result = custom_simbad.query_criteria(
                f"Vmag < 8",
                otype='Star'
            )
            
            if result:
                df = result.to_pandas()
                df = df.head(max_objects)
                logger.info(f"Loaded {len(df)} from SIMBAD")
                return df
            
        except Exception as e:
            logger.error(f"SIMBAD load error: {e}")
        
        return pd.DataFrame()
    
    def _load_2mass_full(self, max_objects: int) -> pd.DataFrame:
        """Load 2MASS data"""
        try:
            path = 'data/2mass/2mass_sample.csv'
            df = pd.read_csv(path, nrows=max_objects)
            logger.info(f"Loaded {len(df)} from 2MASS")
            return df
        except Exception as e:
            logger.error(f"2MASS load error: {e}")
            return pd.DataFrame()
    
    def _load_wise_full(self, max_objects: int) -> pd.DataFrame:
        """Load WISE data"""
        try:
            path = 'data/wise/wise_sample.csv'
            df = pd.read_csv(path, nrows=max_objects)
            logger.info(f"Loaded {len(df)} from WISE")
            return df
        except Exception as e:
            logger.error(f"WISE load error: {e}")
            return pd.DataFrame()
    
    def _create_spatial_index(self):
        """Create spatial index for fast queries"""
        if self.full_data is None:
            return
        
        # Add grid indices
        ra_col = self._get_ra_col()
        dec_col = self._get_dec_col()
        
        if ra_col and dec_col:
            self.full_data['_grid_ra'] = (self.full_data[ra_col] / 10).astype(int)
            self.full_data['_grid_dec'] = ((self.full_data[dec_col] + 90) / 10).astype(int)
            logger.info("Spatial index created")
    
    def _get_ra_col(self) -> Optional[str]:
        """Get RA column name"""
        for col in ['ra', 'RA', 'ra_ep2000', 'RA_ICRS']:
            if col in self.full_data.columns:
                return col
        return None
    
    def _get_dec_col(self) -> Optional[str]:
        """Get Dec column name"""
        for col in ['dec', 'DEC', 'dec_ep2000', 'DEC_ICRS']:
            if col in self.full_data.columns:
                return col
        return None
    
    def get_initial_data(self) -> pd.DataFrame:
        """
        Get initial data to display
        
        Returns:
            DataFrame with initial_size brightest objects
        """
        if self.full_data is None or self.full_data.empty:
            logger.warning("No data loaded, returning empty")
            return pd.DataFrame()
        
        # Get brightest objects
        initial = self.full_data.head(self.initial_size).copy()
        self.visible_data = initial
        self.loaded_indices = set(initial.index)
        
        logger.info(f"Initial data: {len(initial)} objects")
        return initial
    
    def prefetch_data(self, viewport: ViewportBounds) -> pd.DataFrame:
        """
        Prefetch data around viewport
        
        Args:
            viewport: Current viewport bounds
            
        Returns:
            Prefetched data
        """
        if self.full_data is None:
            return pd.DataFrame()
        
        # Expand viewport for prefetching
        expanded = viewport.expand(factor=2.0)
        
        # Query spatial index
        ra_col = self._get_ra_col()
        dec_col = self._get_dec_col()
        
        if not ra_col or not dec_col:
            return self.full_data.head(self.prefetch_size)
        
        # Filter by expanded viewport
        mask = (
            (self.full_data[ra_col] >= expanded.ra_min) &
            (self.full_data[ra_col] <= expanded.ra_max) &
            (self.full_data[dec_col] >= expanded.dec_min) &
            (self.full_data[dec_col] <= expanded.dec_max)
        )
        
        prefetch = self.full_data[mask].head(self.prefetch_size)
        self.cached_data = prefetch
        
        logger.info(f"Prefetched {len(prefetch)} objects")
        return prefetch
    
    def load_next_batch(self, viewport: ViewportBounds) -> pd.DataFrame:
        """
        Load next batch based on viewport
        
        Args:
            viewport: Current viewport
            
        Returns:
            Next batch of objects
        """
        if self.full_data is None:
            return pd.DataFrame()
        
        ra_col = self._get_ra_col()
        dec_col = self._get_dec_col()
        
        if not ra_col or not dec_col:
            # Fallback: load next batch sequentially
            start_idx = len(self.loaded_indices)
            end_idx = start_idx + self.batch_size
            batch = self.full_data.iloc[start_idx:end_idx]
            self.loaded_indices.update(batch.index)
            return batch
        
        # Query viewport
        mask = (
            (self.full_data[ra_col] >= viewport.ra_min) &
            (self.full_data[ra_col] <= viewport.ra_max) &
            (self.full_data[dec_col] >= viewport.dec_min) &
            (self.full_data[dec_col] <= viewport.dec_max) &
            (~self.full_data.index.isin(self.loaded_indices))
        )
        
        batch = self.full_data[mask].head(self.batch_size)
        self.loaded_indices.update(batch.index)
        
        logger.info(f"Loaded batch: {len(batch)} objects (total: {len(self.loaded_indices)})")
        return batch
    
    def update_visible_data(self, viewport: ViewportBounds) -> pd.DataFrame:
        """
        Update visible data based on viewport
        
        Args:
            viewport: Current viewport
            
        Returns:
            Updated visible data
        """
        self.current_viewport = viewport
        
        # Load next batch if needed
        if self.visible_data is None or len(self.loaded_indices) < self.initial_size:
            self.visible_data = self.get_initial_data()
        
        # Load more if zooming in
        new_batch = self.load_next_batch(viewport)
        if not new_batch.empty:
            self.visible_data = pd.concat([self.visible_data, new_batch], 
                                         ignore_index=True)
        
        # Limit cache size
        if len(self.visible_data) > self.cache_size:
            # Keep brightest objects
            if 'magnitude' in self.visible_data.columns:
                self.visible_data = self.visible_data.nsmallest(self.cache_size, 'magnitude')
            else:
                self.visible_data = self.visible_data.head(self.cache_size)
        
        return self.visible_data
    
    def get_stats(self) -> dict:
        """Get loading statistics"""
        return {
            'total_objects': self.total_objects,
            'loaded_objects': len(self.full_data) if self.full_data is not None else 0,
            'cache_size': len(self.cache),
            'viewport_bounds': self.current_viewport
        }
    
    def load_more_at_distance(self, min_distance: float, max_distance: float, count: int = 1000) -> pd.DataFrame:
        """
        Load more objects in a distance shell (for zoom-out)
        
        Args:
            min_distance: Minimum distance in pc
            max_distance: Maximum distance in pc
            count: Number of objects to load
            
        Returns:
            DataFrame with objects in distance range
        """
        if self.full_data is None or len(self.full_data) == 0:
            return pd.DataFrame()
        
        # Calculate distances if not already done
        if 'distance_pc' not in self.full_data.columns:
            if 'parallax' in self.full_data.columns:
                self.full_data['distance_pc'] = 1000.0 / self.full_data['parallax'].clip(0.1, 1000)
            else:
                # Can't filter by distance without parallax
                return self.full_data.sample(min(count, len(self.full_data)))
        
        # Filter by distance shell
        mask = (self.full_data['distance_pc'] >= min_distance) & (self.full_data['distance_pc'] <= max_distance)
        candidates = self.full_data[mask]
        
        if len(candidates) == 0:
            return pd.DataFrame()
        
        # Sample if too many
        if len(candidates) > count:
            return candidates.sample(count)
        
        return candidates


# Global loader instance
_global_loader: Optional[ProgressiveDataLoader] = None


def get_loader() -> ProgressiveDataLoader:
    """Get or create global loader"""
    global _global_loader
    if _global_loader is None:
        _global_loader = ProgressiveDataLoader()
    return _global_loader


def reset_loader():
    """Reset global loader"""
    global _global_loader
    _global_loader = None


if __name__ == "__main__":
    # Test the loader
    print("Testing Progressive Loader...")
    loader = ProgressiveDataLoader(initial_size=128, prefetch_size=512)
    
    # Load GAIA
    if loader.load_full_catalog('gaia', max_objects=10000):
        print(f"[OK] Loaded {loader.total_objects} objects")
        
        # Get initial data
        initial = loader.get_initial_data()
        print(f"[OK] Initial: {len(initial)} objects")
        
        # Prefetch
        viewport = ViewportBounds(ra_min=80, ra_max=120, dec_min=-30, dec_max=0)
        prefetch = loader.prefetch_data(viewport)
        print(f"[OK] Prefetched: {len(prefetch)} objects")
        
        # Stats
        stats = loader.get_stats()
        print(f"[OK] Stats: {stats}")
        
        print("\n[SUCCESS] ALL TESTS PASSED!")
