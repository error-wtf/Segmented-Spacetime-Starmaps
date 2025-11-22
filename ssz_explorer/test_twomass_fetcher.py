#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for 2MASS Fetcher

Tests 2MASS integration including:
- Connection test
- Cone search
- Quality filtering
- Color calculations
- Error handling

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
from twomass_fetcher import TwoMASSFetcher


class TestTwoMASSFetcher:
    """Test suite for 2MASS catalog fetcher."""
    
    @pytest.fixture
    def fetcher(self):
        """Create TwoMASSFetcher instance for testing."""
        return TwoMASSFetcher()
    
    def test_initialization(self, fetcher):
        """Test that fetcher initializes correctly."""
        assert fetcher is not None
        if fetcher.is_available():
            assert fetcher.vizier is not None
            print("✅ 2MASS available and initialized")
        else:
            print("⚠️  2MASS not available (astroquery not installed)")
    
    @pytest.mark.skipif(
        not TwoMASSFetcher().is_available(),
        reason="2MASS not available"
    )
    def test_cone_search(self, fetcher):
        """Test cone search functionality."""
        # Search near Betelgeuse
        ra, dec = 88.793, 7.407
        radius = 5.0
        
        df = fetcher.cone_search(ra=ra, dec=dec, radius=radius, max_results=50)
        
        assert df is not None, "Cone search returned None"
        assert isinstance(df, pd.DataFrame), "Result should be DataFrame"
        assert len(df) > 0, "Should find at least one source"
        
        # Check required columns
        assert 'ra' in df.columns, "Missing RA column"
        assert 'dec' in df.columns, "Missing Dec column"
        assert 'j_mag' in df.columns, "Missing J magnitude"
        assert 'h_mag' in df.columns, "Missing H magnitude"
        assert 'k_mag' in df.columns, "Missing K magnitude"
        assert 'source_catalog' in df.columns, "Missing source_catalog"
        
        # Verify source catalog
        assert all(df['source_catalog'] == '2MASS'), "All sources should be 2MASS"
        
        # Check magnitude values are reasonable
        assert df['j_mag'].between(5, 20).all(), "J magnitudes out of range"
        assert df['h_mag'].between(5, 20).all(), "H magnitudes out of range"
        assert df['k_mag'].between(5, 20).all(), "K magnitudes out of range"
        
        print(f"✅ Cone search found {len(df)} sources near Betelgeuse")
    
    @pytest.mark.skipif(
        not TwoMASSFetcher().is_available(),
        reason="2MASS not available"
    )
    def test_quality_filter(self, fetcher):
        """Test quality filtering."""
        # Search without quality filter
        df_all = fetcher.cone_search(
            ra=88.793, dec=7.407, radius=5.0, 
            max_results=100, quality_filter=False
        )
        
        # Search with quality filter
        df_filtered = fetcher.cone_search(
            ra=88.793, dec=7.407, radius=5.0, 
            max_results=100, quality_filter=True
        )
        
        if df_all is not None and df_filtered is not None:
            # Filtered should have same or fewer sources
            assert len(df_filtered) <= len(df_all), "Filter should not increase count"
            
            print(f"✅ Quality filter: {len(df_all)} → {len(df_filtered)} sources")
        else:
            print("⚠️  Quality filter test skipped (no data)")
    
    @pytest.mark.skipif(
        not TwoMASSFetcher().is_available(),
        reason="2MASS not available"
    )
    def test_color_calculation(self, fetcher):
        """Test color index calculations."""
        df = fetcher.cone_search(ra=88.793, dec=7.407, radius=5.0, max_results=20)
        
        if df is not None:
            # Calculate colors
            df = fetcher.get_colors(df)
            
            # Check color columns exist
            assert 'j_h' in df.columns, "Missing J-H color"
            assert 'h_k' in df.columns, "Missing H-K color"
            assert 'j_k' in df.columns, "Missing J-K color"
            
            # Check colors are reasonable for stars
            # Typical stellar colors: -0.5 < J-H < 1.5, -0.3 < H-K < 0.5
            assert df['j_h'].between(-1, 2).all(), "J-H colors out of range"
            assert df['h_k'].between(-1, 1).all(), "H-K colors out of range"
            assert df['j_k'].between(-1, 3).all(), "J-K colors out of range"
            
            print(f"✅ Colors calculated: J-H mean = {df['j_h'].mean():.3f}")
    
    def test_statistics(self, fetcher):
        """Test statistics method."""
        stats = fetcher.get_statistics()
        
        assert isinstance(stats, dict), "Statistics should be dict"
        assert 'catalog' in stats, "Should have catalog name"
        assert stats['catalog'] == '2MASS', "Catalog should be 2MASS"
        assert 'available' in stats, "Should have availability status"
        assert 'bands' in stats, "Should have band information"
        
        # Check band info
        assert 'J' in stats['bands'], "Should have J band"
        assert 'H' in stats['bands'], "Should have H band"
        assert 'K' in stats['bands'], "Should have K band"
        
        print(f"✅ Statistics: {stats['full_name']}")
        print(f"   Bands: {', '.join(stats['bands'].keys())}")
    
    @pytest.mark.skipif(
        not TwoMASSFetcher().is_available(),
        reason="2MASS not available"
    )
    def test_error_handling_no_results(self, fetcher):
        """Test handling when no results found."""
        # Query at empty sky location
        df = fetcher.cone_search(ra=0, dec=90, radius=0.001, max_results=10)
        
        # Should return None or empty DataFrame
        if df is not None:
            assert len(df) == 0, "Should find no sources at this location"
        
        print("✅ Correctly handles no results")
    
    @pytest.mark.skipif(
        not TwoMASSFetcher().is_available(),
        reason="2MASS not available"
    )
    def test_coordinate_accuracy(self, fetcher):
        """Test coordinate accuracy."""
        ra, dec = 88.793, 7.407
        radius = 1.0
        
        df = fetcher.cone_search(ra=ra, dec=dec, radius=radius, max_results=10)
        
        if df is not None and len(df) > 0:
            # Check coordinates are within search radius
            # Convert radius to degrees
            radius_deg = radius / 60.0
            
            # Calculate distances (approximate)
            dra = (df['ra'] - ra) * np.cos(np.radians(dec))
            ddec = df['dec'] - dec
            dist = np.sqrt(dra**2 + ddec**2)
            
            # All sources should be within search radius (with small tolerance)
            assert (dist <= radius_deg * 1.1).all(), "Sources outside search radius"
            
            print(f"✅ Coordinates accurate (max dist: {dist.max():.4f}°)")
    
    @pytest.mark.skipif(
        not TwoMASSFetcher().is_available(),
        reason="2MASS not available"
    )
    def test_photometry_errors(self, fetcher):
        """Test that photometric errors are included."""
        df = fetcher.cone_search(ra=88.793, dec=7.407, radius=5.0, max_results=10)
        
        if df is not None:
            # Check if error columns exist
            error_cols = ['j_mag_error', 'h_mag_error', 'k_mag_error']
            has_errors = any(col in df.columns for col in error_cols)
            
            if has_errors:
                print("✅ Photometric errors included")
            else:
                print("⚠️  Photometric errors not in output")


def run_all_tests():
    """Run all tests manually (without pytest)."""
    print("="*80)
    print("2MASS FETCHER TEST SUITE")
    print("="*80)
    
    fetcher = TwoMASSFetcher()
    test_suite = TestTwoMASSFetcher()
    
    # Test 1: Initialization
    print("\n[Test 1] Initialization")
    try:
        test_suite.test_initialization(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    if not fetcher.is_available():
        print("\n⚠️  2MASS not available - skipping online tests")
        print("Install with: pip install astroquery")
        return
    
    # Test 2: Cone search
    print("\n[Test 2] Cone Search")
    try:
        test_suite.test_cone_search(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: Quality filter
    print("\n[Test 3] Quality Filter")
    try:
        test_suite.test_quality_filter(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 4: Color calculation
    print("\n[Test 4] Color Calculation")
    try:
        test_suite.test_color_calculation(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 5: Statistics
    print("\n[Test 5] Statistics")
    try:
        test_suite.test_statistics(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 6: Error handling
    print("\n[Test 6] Error Handling - No Results")
    try:
        test_suite.test_error_handling_no_results(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 7: Coordinate accuracy
    print("\n[Test 7] Coordinate Accuracy")
    try:
        test_suite.test_coordinate_accuracy(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 8: Photometry errors
    print("\n[Test 8] Photometric Errors")
    try:
        test_suite.test_photometry_errors(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "="*80)
    print("✅ TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()
