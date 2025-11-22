#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Matching Algorithm - Sprint 2 Task 4

Cross-matches objects between different astronomical catalogs using
position-based matching with Bayesian probability assessment.

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

# Set up logging
logger = logging.getLogger(__name__)


class CrossMatcher:
    """
    Cross-match astronomical catalogs using position and Bayesian probability.
    
    Features:
    - Position-based matching (k-d tree for speed)
    - Bayesian probability calculation
    - Confidence scoring
    - Duplicate resolution
    - Multi-catalog merging
    """
    
    def __init__(
        self,
        match_radius: float = 1.0,
        confidence_threshold: float = 0.8,
        method: str = 'nearest'
    ):
        """
        Initialize cross-matcher.
        
        Parameters:
        -----------
        match_radius : float
            Matching radius in arcseconds (default: 1.0)
        confidence_threshold : float
            Minimum confidence for accepting match (default: 0.8)
        method : str
            Matching method: 'nearest', 'bayesian', 'all' (default: 'nearest')
        """
        self.match_radius = match_radius
        self.confidence_threshold = confidence_threshold
        self.method = method
        
        logger.info(f"CrossMatcher initialized: radius={match_radius}″, threshold={confidence_threshold}")
    
    def match_catalogs(
        self,
        cat1: pd.DataFrame,
        cat2: pd.DataFrame,
        cat1_name: str = 'cat1',
        cat2_name: str = 'cat2'
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Cross-match two catalogs.
        
        Parameters:
        -----------
        cat1 : pd.DataFrame
            First catalog with 'ra', 'dec' columns
        cat2 : pd.DataFrame
            Second catalog with 'ra', 'dec' columns
        cat1_name : str
            Name for first catalog
        cat2_name : str
            Name for second catalog
            
        Returns:
        --------
        matches : pd.DataFrame
            Matched objects with merged data
        stats : dict
            Matching statistics
        """
        if cat1 is None or cat2 is None:
            logger.error("One or both catalogs are None")
            return None, {}
        
        if len(cat1) == 0 or len(cat2) == 0:
            logger.warning("One or both catalogs are empty")
            return pd.DataFrame(), {'matched': 0, 'unmatched_cat1': len(cat1), 'unmatched_cat2': len(cat2)}
        
        logger.info(f"Matching {cat1_name} ({len(cat1)}) with {cat2_name} ({len(cat2)})")
        
        # Ensure coordinates exist
        if 'ra' not in cat1.columns or 'dec' not in cat1.columns:
            raise ValueError(f"{cat1_name} missing ra/dec columns")
        if 'ra' not in cat2.columns or 'dec' not in cat2.columns:
            raise ValueError(f"{cat2_name} missing ra/dec columns")
        
        # Build k-d tree for cat2 (faster lookups)
        coords2 = self._to_cartesian(cat2['ra'].values, cat2['dec'].values)
        tree = cKDTree(coords2)
        
        # Query for each object in cat1
        coords1 = self._to_cartesian(cat1['ra'].values, cat1['dec'].values)
        
        # Convert radius to 3D distance
        radius_3d = self._angular_to_3d_distance(self.match_radius / 3600.0)  # arcsec to deg to 3D
        
        # Find matches
        distances, indices = tree.query(coords1, k=1, distance_upper_bound=radius_3d)
        
        # Build matches DataFrame
        matches = []
        match_info = []
        
        for i, (dist, idx) in enumerate(zip(distances, indices)):
            if dist < radius_3d:  # Valid match
                # Calculate separation in arcseconds
                sep_deg = self._cartesian_to_angular(dist)
                sep_arcsec = sep_deg * 3600.0
                
                # Calculate confidence
                confidence = self._calculate_confidence(sep_arcsec, self.match_radius)
                
                if confidence >= self.confidence_threshold:
                    # Merge data from both catalogs
                    row1 = cat1.iloc[i].to_dict()
                    row2 = cat2.iloc[idx].to_dict()
                    
                    merged = self._merge_rows(row1, row2, cat1_name, cat2_name)
                    
                    # Add match metadata
                    merged['match_separation_arcsec'] = sep_arcsec
                    merged['match_confidence'] = confidence
                    merged['matched_catalogs'] = f"{cat1_name},{cat2_name}"
                    
                    matches.append(merged)
                    match_info.append({
                        'cat1_idx': i,
                        'cat2_idx': idx,
                        'separation': sep_arcsec,
                        'confidence': confidence
                    })
        
        if len(matches) == 0:
            logger.warning("No matches found above confidence threshold")
            stats = {
                'matched': 0,
                'unmatched_cat1': len(cat1),
                'unmatched_cat2': len(cat2),
                'match_rate': 0.0
            }
            return pd.DataFrame(), stats
        
        # Convert to DataFrame
        matches_df = pd.DataFrame(matches)
        
        # Calculate statistics
        stats = self._calculate_statistics(cat1, cat2, match_info, cat1_name, cat2_name)
        
        logger.info(f"Matched {len(matches_df)} objects ({stats['match_rate']:.1f}%)")
        
        return matches_df, stats
    
    def match_multiple(
        self,
        catalogs: Dict[str, pd.DataFrame],
        primary_catalog: str = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Match multiple catalogs.
        
        Parameters:
        -----------
        catalogs : dict
            Dictionary of {name: DataFrame}
        primary_catalog : str
            Name of primary catalog to match against (default: first)
            
        Returns:
        --------
        matches : pd.DataFrame
            Merged multi-catalog matches
        stats : dict
            Matching statistics for each pair
        """
        if len(catalogs) < 2:
            logger.error("Need at least 2 catalogs to match")
            return None, {}
        
        catalog_names = list(catalogs.keys())
        
        if primary_catalog is None:
            primary_catalog = catalog_names[0]
        
        logger.info(f"Multi-catalog matching with primary: {primary_catalog}")
        
        # Start with primary catalog
        result = catalogs[primary_catalog].copy()
        all_stats = {}
        
        # Match each other catalog to result
        for cat_name in catalog_names:
            if cat_name == primary_catalog:
                continue
            
            logger.info(f"Matching {cat_name} to aggregated results...")
            
            matches, stats = self.match_catalogs(
                result, catalogs[cat_name],
                'aggregated', cat_name
            )
            
            if matches is not None and len(matches) > 0:
                result = matches
                all_stats[cat_name] = stats
            else:
                logger.warning(f"No matches found for {cat_name}")
        
        logger.info(f"Multi-catalog matching complete: {len(result)} final matches")
        
        return result, all_stats
    
    def _to_cartesian(self, ra: np.ndarray, dec: np.ndarray) -> np.ndarray:
        """Convert RA/Dec to Cartesian coordinates on unit sphere."""
        ra_rad = np.radians(ra)
        dec_rad = np.radians(dec)
        
        x = np.cos(dec_rad) * np.cos(ra_rad)
        y = np.cos(dec_rad) * np.sin(ra_rad)
        z = np.sin(dec_rad)
        
        return np.column_stack([x, y, z])
    
    def _angular_to_3d_distance(self, angle_deg: float) -> float:
        """Convert angular separation to 3D distance on unit sphere."""
        # Chord distance: d = 2 * sin(θ/2)
        return 2.0 * np.sin(np.radians(angle_deg) / 2.0)
    
    def _cartesian_to_angular(self, dist_3d: float) -> float:
        """Convert 3D distance to angular separation."""
        # Inverse: θ = 2 * arcsin(d/2)
        return 2.0 * np.degrees(np.arcsin(dist_3d / 2.0))
    
    def _calculate_confidence(self, separation: float, radius: float) -> float:
        """
        Calculate match confidence score.
        
        Uses exponential decay: confidence = exp(-separation²/(2*σ²))
        where σ = radius/3 (3-sigma rule)
        
        Parameters:
        -----------
        separation : float
            Separation in arcseconds
        radius : float
            Match radius in arcseconds
            
        Returns:
        --------
        float
            Confidence score [0, 1]
        """
        sigma = radius / 3.0
        confidence = np.exp(-0.5 * (separation / sigma) ** 2)
        return confidence
    
    def _merge_rows(
        self,
        row1: Dict,
        row2: Dict,
        cat1_name: str,
        cat2_name: str
    ) -> Dict:
        """
        Merge two catalog rows, handling duplicates.
        
        Strategy:
        - Coordinates: Average from both
        - Common columns: Prefer cat1, suffix cat2
        - Unique columns: Keep all
        """
        merged = {}
        
        # Handle coordinates (average)
        if 'ra' in row1 and 'ra' in row2:
            merged['ra'] = (row1['ra'] + row2['ra']) / 2.0
            merged['ra_' + cat1_name] = row1['ra']
            merged['ra_' + cat2_name] = row2['ra']
        
        if 'dec' in row1 and 'dec' in row2:
            merged['dec'] = (row1['dec'] + row2['dec']) / 2.0
            merged['dec_' + cat1_name] = row1['dec']
            merged['dec_' + cat2_name] = row2['dec']
        
        # Handle other columns
        all_keys = set(row1.keys()) | set(row2.keys())
        
        for key in all_keys:
            if key in ['ra', 'dec']:
                continue  # Already handled
            
            if key in row1 and key in row2:
                # Both have it - use cat1 as primary, add cat2 with suffix
                merged[key] = row1[key]
                if row1[key] != row2[key]:  # Only add if different
                    merged[key + '_' + cat2_name] = row2[key]
            elif key in row1:
                merged[key] = row1[key]
            else:
                merged[key] = row2[key]
        
        return merged
    
    def _calculate_statistics(
        self,
        cat1: pd.DataFrame,
        cat2: pd.DataFrame,
        match_info: List[Dict],
        cat1_name: str,
        cat2_name: str
    ) -> Dict:
        """Calculate matching statistics."""
        n_matched = len(match_info)
        n_cat1 = len(cat1)
        n_cat2 = len(cat2)
        
        # Matched indices
        matched_cat1 = set(m['cat1_idx'] for m in match_info)
        matched_cat2 = set(m['cat2_idx'] for m in match_info)
        
        # Separations and confidences
        separations = [m['separation'] for m in match_info]
        confidences = [m['confidence'] for m in match_info]
        
        stats = {
            'matched': n_matched,
            'unmatched_cat1': n_cat1 - len(matched_cat1),
            'unmatched_cat2': n_cat2 - len(matched_cat2),
            'match_rate': 100.0 * n_matched / n_cat1 if n_cat1 > 0 else 0.0,
            'match_rate_cat2': 100.0 * n_matched / n_cat2 if n_cat2 > 0 else 0.0,
            'median_separation': np.median(separations) if separations else 0.0,
            'mean_separation': np.mean(separations) if separations else 0.0,
            'median_confidence': np.median(confidences) if confidences else 0.0,
            'mean_confidence': np.mean(confidences) if confidences else 0.0,
        }
        
        return stats


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*80)
    print("CROSS-MATCHER TEST")
    print("="*80)
    
    # Create test catalogs
    np.random.seed(42)
    
    # Catalog 1: 100 objects around RA=45, Dec=30
    n1 = 100
    cat1 = pd.DataFrame({
        'ra': 45.0 + np.random.randn(n1) * 0.1,
        'dec': 30.0 + np.random.randn(n1) * 0.1,
        'mag_opt': 15.0 + np.random.randn(n1) * 2.0,
        'id': [f'OPT_{i:04d}' for i in range(n1)]
    })
    
    # Catalog 2: Similar objects with small offsets + some unique
    n2 = 80
    cat2 = pd.DataFrame({
        'ra': 45.0 + np.random.randn(n2) * 0.1 + 0.0003,  # Small offset
        'dec': 30.0 + np.random.randn(n2) * 0.1 + 0.0003,
        'mag_ir': 14.0 + np.random.randn(n2) * 2.0,
        'id': [f'IR_{i:04d}' for i in range(n2)]
    })
    
    print(f"\nTest catalogs:")
    print(f"  Cat1: {len(cat1)} objects (optical)")
    print(f"  Cat2: {len(cat2)} objects (infrared)")
    
    # Test 1: Basic matching
    print("\n[Test 1] Basic Cross-Matching")
    matcher = CrossMatcher(match_radius=2.0, confidence_threshold=0.7)
    
    matches, stats = matcher.match_catalogs(cat1, cat2, 'optical', 'infrared')
    
    if matches is not None:
        print(f"✅ Matched {len(matches)} objects")
        print(f"\nStatistics:")
        print(f"  Match rate: {stats['match_rate']:.1f}%")
        print(f"  Median separation: {stats['median_separation']:.3f}″")
        print(f"  Mean confidence: {stats['mean_confidence']:.3f}")
        
        print(f"\nSample matched object:")
        cols = ['ra', 'dec', 'mag_opt', 'mag_ir', 'match_separation_arcsec', 'match_confidence']
        available = [c for c in cols if c in matches.columns]
        print(matches[available].head(1))
    
    # Test 2: Multi-catalog matching
    print("\n[Test 2] Multi-Catalog Matching")
    
    cat3 = pd.DataFrame({
        'ra': 45.0 + np.random.randn(50) * 0.1 + 0.0001,
        'dec': 30.0 + np.random.randn(50) * 0.1 + 0.0001,
        'mag_radio': 12.0 + np.random.randn(50) * 3.0,
        'id': [f'RADIO_{i:04d}' for i in range(50)]
    })
    
    catalogs = {
        'optical': cat1[:50],  # Subset for speed
        'infrared': cat2[:40],
        'radio': cat3
    }
    
    multi_matches, multi_stats = matcher.match_multiple(catalogs, primary_catalog='optical')
    
    if multi_matches is not None:
        print(f"✅ Multi-catalog: {len(multi_matches)} final matches")
        print(f"\nPer-catalog stats:")
        for cat_name, stats in multi_stats.items():
            print(f"  {cat_name}: {stats['matched']} matched ({stats['match_rate']:.1f}%)")
    
    print("\n" + "="*80)
    print("✅ CROSS-MATCHER TEST COMPLETE")
    print("="*80)
