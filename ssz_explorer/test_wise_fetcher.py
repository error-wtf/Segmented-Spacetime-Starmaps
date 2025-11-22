#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for WISE Fetcher

Tests WISE integration including:
- Connection test
- Cone search
- Band filtering
- SED building
- Object classification
- Quality filtering

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
from wise_fetcher import WISEFetcher


class TestWISEFetcher:
    """Test suite for WISE catalog fetcher."""
    
    @pytest.fixture
    def fetcher(self):
        """Create WISEFetcher instance for testing."""
        return WISEFetcher()
    
    def test_initialization(self, fetcher):
        """Test that fetcher initializes correctly."""
        assert fetcher is not None
        if fetcher.is_available():
            assert fetcher.vizier is not None
            print("✅ WISE available and initialized")
        else:
            print("⚠️  WISE not available (astroquery not installed)")
    
    @pytest.mark.skipif(
        not WISEFetcher().is_available(),
        reason="WISE not available"
    )
    def test_cone_search_w1w2(self, fetcher):
        """Test cone search with W1/W2 bands."""
        ra, dec = 88.793, 7.407
        radius = 5.0
        
        df = fetcher.cone_search(
            ra=ra, dec=dec, radius=radius, 
            max_results=50, bands=['W1', 'W2']
        )
        
        assert df is not None, "Cone search returned None"
        assert isinstance(df, pd.DataFrame), "Result should be DataFrame"
        assert len(df) > 0, "Should find at least one source"
        
        # Check required columns
        assert 'ra' in df.columns, "Missing RA column"
        assert 'dec' in df.columns, "Missing Dec column"
        assert 'w1_mag' in df.columns, "Missing W1 magnitude"
        assert 'w2_mag' in df.columns, "Missing W2 magnitude"
        assert 'source_catalog' in df.columns, "Missing source_catalog"
        
        # Should NOT have W3/W4 (not requested)
        assert 'w3_mag' not in df.columns, "W3 should not be present"
        assert 'w4_mag' not in df.columns, "W4 should not be present"
        
        # Verify source catalog
        assert all(df['source_catalog'] == 'WISE'), "All sources should be WISE"
        
        print(f"✅ Cone search (W1/W2) found {len(df)} sources")
    
    @pytest.mark.skipif(
        not WISEFetcher().is_available(),
        reason="WISE not available"
    )
    def test_cone_search_all_bands(self, fetcher):
        """Test cone search with all bands."""
        df = fetcher.cone_search(
            ra=88.793, dec=7.407, radius=2.0,
            max_results=20, bands=['W1', 'W2', 'W3', 'W4']
        )
        
        if df is not None:
            # Should have all bands
            assert 'w1_mag' in df.columns, "Missing W1"
            assert 'w2_mag' in df.columns, "Missing W2"
            assert 'w3_mag' in df.columns, "Missing W3"
            assert 'w4_mag' in df.columns, "Missing W4"
            
            print(f"✅ All bands present: {len(df)} sources")
    
    @pytest.mark.skipif(
        not WISEFetcher().is_available(),
        reason="WISE not available"
    )
    def test_sed_building(self, fetcher):
        """Test SED construction."""
        df = fetcher.cone_search(
            ra=88.793, dec=7.407, radius=5.0,
            max_results=20, bands=['W1', 'W2', 'W3', 'W4']
        )
        
        if df is not None:
            df = fetcher.get_sed(df)
            
            # Check color columns exist
            assert 'w1_w2' in df.columns, "Missing W1-W2 color"
            
            if 'w2_mag' in df.columns and 'w3_mag' in df.columns:
                assert 'w2_w3' in df.columns, "Missing W2-W3 color"
            
            # Check colors are reasonable
            assert df['w1_w2'].between(-1, 3).all(), "W1-W2 colors out of range"
            
            print(f"✅ SED built: W1-W2 mean = {df['w1_w2'].mean():.3f}")
    
    @pytest.mark.skipif(
        not WISEFetcher().is_available(),
        reason="WISE not available"
    )
    def test_object_classification(self, fetcher):
        """Test object classification."""
        df = fetcher.cone_search(
            ra=88.793, dec=7.407, radius=5.0,
            max_results=30, bands=['W1', 'W2']
        )
        
        if df is not None:
            df = fetcher.classify_objects(df)
            
            assert 'wise_class' in df.columns, "Missing classification column"
            
            # Check valid classes
            valid_classes = ['Star', 'AGN_candidate', 'YSO_candidate', 'Unknown']
            assert df['wise_class'].isin(valid_classes).all(), "Invalid class"
            
            # Should have some stars
            star_count = (df['wise_class'] == 'Star').sum()
            
            print(f"✅ Classification: {star_count} stars out of {len(df)}")
    
    @pytest.mark.skipif(
        not WISEFetcher().is_available(),
        reason="WISE not available"
    )
    def test_quality_filter(self, fetcher):
        """Test quality filtering."""
        # Without filter
        df_all = fetcher.cone_search(
            ra=88.793, dec=7.407, radius=5.0,
            max_results=100, bands=['W1', 'W2'], quality_filter=False
        )
        
        # With filter
        df_filtered = fetcher.cone_search(
            ra=88.793, dec=7.407, radius=5.0,
            max_results=100, bands=['W1', 'W2'], quality_filter=True
        )
        
        if df_all is not None and df_filtered is not None:
            assert len(df_filtered) <= len(df_all), "Filter should not increase count"
            print(f"✅ Quality filter: {len(df_all)} → {len(df_filtered)} sources")
    
    def test_statistics(self, fetcher):
        """Test statistics method."""
        stats = fetcher.get_statistics()
        
        assert isinstance(stats, dict), "Statistics should be dict"
        assert 'catalog' in stats, "Should have catalog name"
        assert stats['catalog'] == 'WISE', "Catalog should be WISE"
        assert 'bands' in stats, "Should have band information"
        
        # Check all 4 bands
        assert 'W1' in stats['bands'], "Should have W1"
        assert 'W2' in stats['bands'], "Should have W2"
        assert 'W3' in stats['bands'], "Should have W3"
        assert 'W4' in stats['bands'], "Should have W4"
        
        print(f"✅ Statistics: {stats['full_name']}")
        print(f"   Sources: {stats['total_sources']}")
    
    @pytest.mark.skipif(
        not WISEFetcher().is_available(),
        reason="WISE not available"
    )
    def test_magnitude_ranges(self, fetcher):
        """Test that magnitudes are in reasonable ranges."""
        df = fetcher.cone_search(
            ra=88.793, dec=7.407, radius=5.0,
            max_results=30, bands=['W1', 'W2']
        )
        
        if df is not None:
            # WISE magnitudes typically 5-18
            assert df['w1_mag'].between(3, 20).all(), "W1 mags out of range"
            assert df['w2_mag'].between(3, 20).all(), "W2 mags out of range"
            
            print(f"✅ Magnitudes in valid range")


def run_all_tests():
    """Run all tests manually (without pytest)."""
    print("="*80)
    print("WISE FETCHER TEST SUITE")
    print("="*80)
    
    fetcher = WISEFetcher()
    test_suite = TestWISEFetcher()
    
    # Test 1: Initialization
    print("\n[Test 1] Initialization")
    try:
        test_suite.test_initialization(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    if not fetcher.is_available():
        print("\n⚠️  WISE not available - skipping online tests")
        print("Install with: pip install astroquery")
        return
    
    # Test 2: Cone search W1/W2
    print("\n[Test 2] Cone Search (W1/W2)")
    try:
        test_suite.test_cone_search_w1w2(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: All bands
    print("\n[Test 3] Cone Search (All Bands)")
    try:
        test_suite.test_cone_search_all_bands(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 4: SED
    print("\n[Test 4] SED Building")
    try:
        test_suite.test_sed_building(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 5: Classification
    print("\n[Test 5] Object Classification")
    try:
        test_suite.test_object_classification(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 6: Quality filter
    print("\n[Test 6] Quality Filter")
    try:
        test_suite.test_quality_filter(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 7: Statistics
    print("\n[Test 7] Statistics")
    try:
        test_suite.test_statistics(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 8: Magnitude ranges
    print("\n[Test 8] Magnitude Ranges")
    try:
        test_suite.test_magnitude_ranges(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "="*80)
    print("✅ TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()
