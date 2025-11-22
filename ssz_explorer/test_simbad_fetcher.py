#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for SIMBAD Fetcher

Tests SIMBAD integration including:
- Connection test
- Cone search
- Object queries
- Identifier retrieval
- Error handling

© 2025 Carmen Wrede, Lino Casu
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
from simbad_fetcher import SIMBADFetcher


class TestSIMBADFetcher:
    """Test suite for SIMBAD catalog fetcher."""
    
    @pytest.fixture
    def fetcher(self):
        """Create SIMBADFetcher instance for testing."""
        return SIMBADFetcher()
    
    def test_initialization(self, fetcher):
        """Test that fetcher initializes correctly."""
        assert fetcher is not None
        # Check if SIMBAD is available
        if fetcher.is_available():
            assert fetcher.simbad is not None
            print("✅ SIMBAD available and initialized")
        else:
            print("⚠️  SIMBAD not available (astroquery not installed)")
    
    @pytest.mark.skipif(
        not SIMBADFetcher().is_available(),
        reason="SIMBAD not available"
    )
    def test_cone_search(self, fetcher):
        """Test cone search functionality."""
        # Search near Betelgeuse (α Ori)
        ra, dec = 88.793, 7.407
        radius = 5.0  # arcminutes
        
        df = fetcher.cone_search(ra=ra, dec=dec, radius=radius, max_results=20)
        
        assert df is not None, "Cone search returned None"
        assert isinstance(df, pd.DataFrame), "Result should be DataFrame"
        assert len(df) > 0, "Should find at least one object"
        
        # Check required columns
        assert 'ra' in df.columns, "Missing RA column"
        assert 'dec' in df.columns, "Missing Dec column"
        assert 'main_id' in df.columns, "Missing main_id column"
        assert 'source_catalog' in df.columns, "Missing source_catalog"
        
        # Verify source catalog
        assert all(df['source_catalog'] == 'SIMBAD'), "All sources should be SIMBAD"
        
        print(f"✅ Cone search found {len(df)} objects near Betelgeuse")
    
    @pytest.mark.skipif(
        not SIMBADFetcher().is_available(),
        reason="SIMBAD not available"
    )
    def test_query_object(self, fetcher):
        """Test querying by object name."""
        # Query Betelgeuse
        df = fetcher.query_object("Betelgeuse")
        
        assert df is not None, "Object query returned None"
        assert isinstance(df, pd.DataFrame), "Result should be DataFrame"
        assert len(df) > 0, "Should find the object"
        
        # Check coordinates are reasonable for Betelgeuse
        ra = df.iloc[0]['ra']
        dec = df.iloc[0]['dec']
        
        assert 85 < ra < 92, f"RA {ra} out of range for Betelgeuse"
        assert 5 < dec < 10, f"Dec {dec} out of range for Betelgeuse"
        
        print(f"✅ Found Betelgeuse at RA={ra:.4f}, Dec={dec:.4f}")
    
    @pytest.mark.skipif(
        not SIMBADFetcher().is_available(),
        reason="SIMBAD not available"
    )
    def test_get_identifiers(self, fetcher):
        """Test identifier retrieval."""
        # Get identifiers near Betelgeuse
        ra, dec = 88.793, 7.407
        
        identifiers = fetcher.get_identifiers(ra=ra, dec=dec, radius=0.5)
        
        assert isinstance(identifiers, list), "Should return list"
        if len(identifiers) > 0:
            assert all(isinstance(id, str) for id in identifiers), "All IDs should be strings"
            print(f"✅ Found {len(identifiers)} identifiers")
        else:
            print("⚠️  No identifiers found (query may have failed)")
    
    @pytest.mark.skipif(
        not SIMBADFetcher().is_available(),
        reason="SIMBAD not available"
    )
    def test_get_object_type(self, fetcher):
        """Test object type retrieval."""
        obj_type = fetcher.get_object_type("Betelgeuse")
        
        if obj_type:
            assert isinstance(obj_type, str), "Object type should be string"
            print(f"✅ Betelgeuse type: {obj_type}")
        else:
            print("⚠️  Object type not available")
    
    def test_statistics(self, fetcher):
        """Test statistics method."""
        stats = fetcher.get_statistics()
        
        assert isinstance(stats, dict), "Statistics should be dict"
        assert 'catalog' in stats, "Should have catalog name"
        assert stats['catalog'] == 'SIMBAD', "Catalog should be SIMBAD"
        assert 'available' in stats, "Should have availability status"
        
        print(f"✅ Statistics: {stats['catalog']}, Available: {stats['available']}")
    
    def test_error_handling_no_results(self, fetcher):
        """Test handling when no results found."""
        if not fetcher.is_available():
            pytest.skip("SIMBAD not available")
        
        # Query at empty sky location
        df = fetcher.cone_search(ra=0, dec=90, radius=0.001, max_results=10)
        
        # Should return None or empty DataFrame
        if df is not None:
            assert len(df) == 0, "Should find no objects at this location"
        
        print("✅ Correctly handles no results")
    
    def test_invalid_object_name(self, fetcher):
        """Test handling of invalid object names."""
        if not fetcher.is_available():
            pytest.skip("SIMBAD not available")
        
        df = fetcher.query_object("ThisObjectDoesNotExist12345")
        
        # Should return None for invalid object
        assert df is None, "Should return None for invalid object"
        
        print("✅ Correctly handles invalid object names")


def run_all_tests():
    """Run all tests manually (without pytest)."""
    print("="*80)
    print("SIMBAD FETCHER TEST SUITE")
    print("="*80)
    
    fetcher = SIMBADFetcher()
    test_suite = TestSIMBADFetcher()
    
    # Test 1: Initialization
    print("\n[Test 1] Initialization")
    try:
        test_suite.test_initialization(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    if not fetcher.is_available():
        print("\n⚠️  SIMBAD not available - skipping online tests")
        print("Install with: pip install astroquery")
        return
    
    # Test 2: Cone search
    print("\n[Test 2] Cone Search")
    try:
        test_suite.test_cone_search(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: Object query
    print("\n[Test 3] Object Query")
    try:
        test_suite.test_query_object(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 4: Get identifiers
    print("\n[Test 4] Get Identifiers")
    try:
        test_suite.test_get_identifiers(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 5: Get object type
    print("\n[Test 5] Get Object Type")
    try:
        test_suite.test_get_object_type(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 6: Statistics
    print("\n[Test 6] Statistics")
    try:
        test_suite.test_statistics(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 7: Error handling
    print("\n[Test 7] Error Handling - No Results")
    try:
        test_suite.test_error_handling_no_results(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 8: Invalid object
    print("\n[Test 8] Error Handling - Invalid Object")
    try:
        test_suite.test_invalid_object_name(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "="*80)
    print("✅ TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()
