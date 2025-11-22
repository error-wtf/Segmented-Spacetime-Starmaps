#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Cross-Matcher

Tests cross-matching functionality including:
- Basic two-catalog matching
- Multi-catalog matching
- Confidence scoring
- Statistics calculation

 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import os
import sys

# UTF-8 für Windows-Konsole
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

import pytest
import pandas as pd
import numpy as np
from cross_matcher import CrossMatcher


class TestCrossMatcher:
    """Test suite for catalog cross-matching."""
    
    @pytest.fixture
    def matcher(self):
        """Create CrossMatcher instance."""
        return CrossMatcher(match_radius=1.0, confidence_threshold=0.8)
    
    @pytest.fixture
    def test_catalogs(self):
        """Create test catalogs with known matches."""
        np.random.seed(42)
        
        # Catalog 1: Reference catalog
        n = 50
        cat1 = pd.DataFrame({
            'ra': 100.0 + np.random.randn(n) * 0.05,
            'dec': 40.0 + np.random.randn(n) * 0.05,
            'mag_g': 16.0 + np.random.randn(n),
            'id_opt': [f'OPT_{i:03d}' for i in range(n)]
        })
        
        # Catalog 2: Offset slightly + some missing objects
        n2 = 40
        cat2 = pd.DataFrame({
            'ra': 100.0 + np.random.randn(n2) * 0.05 + 0.0001,  # ~0.36″ offset
            'dec': 40.0 + np.random.randn(n2) * 0.05 + 0.0001,
            'mag_j': 15.0 + np.random.randn(n2),
            'id_ir': [f'IR_{i:03d}' for i in range(n2)]
        })
        
        return cat1, cat2
    
    def test_initialization(self, matcher):
        """Test matcher initialization."""
        assert matcher is not None
        assert matcher.match_radius == 1.0
        assert matcher.confidence_threshold == 0.8
        print("✅ Matcher initialized correctly")
    
    def test_basic_matching(self, matcher, test_catalogs):
        """Test basic two-catalog matching."""
        cat1, cat2 = test_catalogs
        
        matches, stats = matcher.match_catalogs(cat1, cat2, 'optical', 'infrared')
        
        assert matches is not None, "Matching returned None"
        assert isinstance(matches, pd.DataFrame), "Should return DataFrame"
        assert len(matches) > 0, "Should find some matches"
        
        # Check required columns
        assert 'ra' in matches.columns, "Missing RA"
        assert 'dec' in matches.columns, "Missing Dec"
        assert 'match_separation_arcsec' in matches.columns, "Missing separation"
        assert 'match_confidence' in matches.columns, "Missing confidence"
        
        # Check statistics
        assert 'matched' in stats, "Missing matched count"
        assert 'match_rate' in stats, "Missing match rate"
        assert stats['matched'] == len(matches), "Inconsistent counts"
        
        print(f"✅ Matched {len(matches)}/{len(cat1)} objects ({stats['match_rate']:.1f}%)")
    
    def test_confidence_scores(self, matcher, test_catalogs):
        """Test that confidence scores are reasonable."""
        cat1, cat2 = test_catalogs
        
        matches, stats = matcher.match_catalogs(cat1, cat2)
        
        if matches is not None and len(matches) > 0:
            # All matches should meet confidence threshold
            assert (matches['match_confidence'] >= matcher.confidence_threshold).all()
            
            # Confidence should be between 0 and 1
            assert (matches['match_confidence'] >= 0).all()
            assert (matches['match_confidence'] <= 1).all()
            
            print(f"✅ Confidence scores valid (mean: {stats['mean_confidence']:.3f})")
    
    def test_separation_values(self, matcher, test_catalogs):
        """Test that separations are within match radius."""
        cat1, cat2 = test_catalogs
        
        matches, stats = matcher.match_catalogs(cat1, cat2)
        
        if matches is not None and len(matches) > 0:
            # All separations should be <= match radius
            assert (matches['match_separation_arcsec'] <= matcher.match_radius).all()
            
            # Separations should be positive
            assert (matches['match_separation_arcsec'] >= 0).all()
            
            print(f"✅ Separations valid (median: {stats['median_separation']:.3f}″)")
    
    def test_coordinate_averaging(self, matcher):
        """Test that matched coordinates are averaged."""
        # Create perfect match with known offset
        cat1 = pd.DataFrame({
            'ra': [100.0],
            'dec': [40.0],
            'mag': [15.0]
        })
        
        cat2 = pd.DataFrame({
            'ra': [100.0002],  # 0.72″ offset
            'dec': [40.0002],
            'flux': [1000.0]
        })
        
        matches, stats = matcher.match_catalogs(cat1, cat2)
        
        if matches is not None and len(matches) > 0:
            # Matched RA should be average
            expected_ra = (100.0 + 100.0002) / 2.0
            assert abs(matches.iloc[0]['ra'] - expected_ra) < 1e-6
            
            print("✅ Coordinates averaged correctly")
    
    def test_empty_catalogs(self, matcher):
        """Test handling of empty catalogs."""
        empty = pd.DataFrame(columns=['ra', 'dec'])
        cat = pd.DataFrame({'ra': [100.0], 'dec': [40.0]})
        
        # Empty cat1
        matches1, stats1 = matcher.match_catalogs(empty, cat)
        assert matches1 is not None
        assert len(matches1) == 0
        assert stats1['matched'] == 0
        
        # Empty cat2
        matches2, stats2 = matcher.match_catalogs(cat, empty)
        assert matches2 is not None
        assert len(matches2) == 0
        
        print("✅ Empty catalogs handled correctly")
    
    def test_no_matches(self, matcher):
        """Test when catalogs don't overlap."""
        cat1 = pd.DataFrame({
            'ra': [0.0],
            'dec': [0.0]
        })
        
        cat2 = pd.DataFrame({
            'ra': [180.0],  # Opposite side of sky
            'dec': [0.0]
        })
        
        matches, stats = matcher.match_catalogs(cat1, cat2)
        
        assert matches is not None
        assert len(matches) == 0
        assert stats['matched'] == 0
        assert stats['match_rate'] == 0.0
        
        print("✅ No matches handled correctly")
    
    def test_multi_catalog_matching(self, matcher):
        """Test matching multiple catalogs."""
        np.random.seed(42)
        
        # Three catalogs with overlapping objects
        cat1 = pd.DataFrame({
            'ra': 50.0 + np.random.randn(30) * 0.01,
            'dec': 20.0 + np.random.randn(30) * 0.01,
            'mag_opt': 15.0 + np.random.randn(30)
        })
        
        cat2 = pd.DataFrame({
            'ra': 50.0 + np.random.randn(25) * 0.01 + 0.0001,
            'dec': 20.0 + np.random.randn(25) * 0.01 + 0.0001,
            'mag_ir': 14.0 + np.random.randn(25)
        })
        
        cat3 = pd.DataFrame({
            'ra': 50.0 + np.random.randn(20) * 0.01 + 0.00005,
            'dec': 20.0 + np.random.randn(20) * 0.01 + 0.00005,
            'mag_radio': 12.0 + np.random.randn(20)
        })
        
        catalogs = {
            'optical': cat1,
            'infrared': cat2,
            'radio': cat3
        }
        
        matches, stats = matcher.match_multiple(catalogs, primary_catalog='optical')
        
        assert matches is not None
        assert isinstance(matches, pd.DataFrame)
        
        if len(matches) > 0:
            # Should have data from multiple catalogs
            assert 'mag_opt' in matches.columns or 'mag_opt' in str(matches.columns)
            
            print(f"✅ Multi-catalog: {len(matches)} final matches")
            for cat_name, cat_stats in stats.items():
                print(f"   {cat_name}: {cat_stats['matched']} matched")
    
    def test_statistics_calculation(self, matcher, test_catalogs):
        """Test that statistics are calculated correctly."""
        cat1, cat2 = test_catalogs
        
        matches, stats = matcher.match_catalogs(cat1, cat2)
        
        # Check all expected stats exist
        required_stats = [
            'matched', 'unmatched_cat1', 'unmatched_cat2',
            'match_rate', 'median_separation', 'mean_separation',
            'median_confidence', 'mean_confidence'
        ]
        
        for stat in required_stats:
            assert stat in stats, f"Missing stat: {stat}"
        
        # Check consistency
        total = stats['matched'] + stats['unmatched_cat1']
        assert total == len(cat1), "Inconsistent totals"
        
        # Match rate should be percentage
        assert 0 <= stats['match_rate'] <= 100
        
        print("✅ Statistics calculated correctly")


def run_all_tests():
    """Run all tests manually."""
    print("="*80)
    print("CROSS-MATCHER TEST SUITE")
    print("="*80)
    
    matcher = CrossMatcher(match_radius=1.0, confidence_threshold=0.8)
    test_suite = TestCrossMatcher()
    
    # Create test catalogs
    np.random.seed(42)
    n = 50
    cat1 = pd.DataFrame({
        'ra': 100.0 + np.random.randn(n) * 0.05,
        'dec': 40.0 + np.random.randn(n) * 0.05,
        'mag_g': 16.0 + np.random.randn(n)
    })
    
    n2 = 40
    cat2 = pd.DataFrame({
        'ra': 100.0 + np.random.randn(n2) * 0.05 + 0.0001,
        'dec': 40.0 + np.random.randn(n2) * 0.05 + 0.0001,
        'mag_j': 15.0 + np.random.randn(n2)
    })
    
    test_catalogs = (cat1, cat2)
    
    # Test 1
    print("\n[Test 1] Initialization")
    try:
        test_suite.test_initialization(matcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 2
    print("\n[Test 2] Basic Matching")
    try:
        test_suite.test_basic_matching(matcher, test_catalogs)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3
    print("\n[Test 3] Confidence Scores")
    try:
        test_suite.test_confidence_scores(matcher, test_catalogs)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 4
    print("\n[Test 4] Separation Values")
    try:
        test_suite.test_separation_values(matcher, test_catalogs)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 5
    print("\n[Test 5] Coordinate Averaging")
    try:
        test_suite.test_coordinate_averaging(matcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 6
    print("\n[Test 6] Empty Catalogs")
    try:
        test_suite.test_empty_catalogs(matcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 7
    print("\n[Test 7] No Matches")
    try:
        test_suite.test_no_matches(matcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 8
    print("\n[Test 8] Multi-Catalog")
    try:
        test_suite.test_multi_catalog_matching(matcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 9
    print("\n[Test 9] Statistics")
    try:
        test_suite.test_statistics_calculation(matcher, test_catalogs)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "="*80)
    print("✅ TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()
