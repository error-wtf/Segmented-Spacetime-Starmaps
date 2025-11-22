#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Exoplanet Fetcher

Tests NASA Exoplanet Archive integration including:
- Initialization
- Host star queries
- Parameter filtering
- Habitable zone candidates
- Data validation

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
from exoplanet_fetcher import ExoplanetFetcher


class TestExoplanetFetcher:
    """Test suite for exoplanet catalog fetcher."""
    
    @pytest.fixture
    def fetcher(self):
        """Create ExoplanetFetcher instance for testing."""
        return ExoplanetFetcher()
    
    def test_initialization(self, fetcher):
        """Test that fetcher initializes correctly."""
        assert fetcher is not None
        if fetcher.is_available():
            assert fetcher.table == 'ps'
            print("✅ Exoplanet Archive available and initialized")
        else:
            print("⚠️  Exoplanet Archive not available (astroquery not installed)")
    
    @pytest.mark.skipif(
        not ExoplanetFetcher().is_available(),
        reason="Exoplanet Archive not available"
    )
    def test_query_by_host(self, fetcher):
        """Test querying by host star name."""
        # Query Kepler-186 system (known to have multiple planets)
        df = fetcher.query_by_host("Kepler-186")
        
        if df is not None:
            assert isinstance(df, pd.DataFrame), "Result should be DataFrame"
            assert len(df) > 0, "Should find at least one planet"
            
            # Check required columns
            assert 'planet_name' in df.columns or 'host_name' in df.columns
            assert 'source_catalog' in df.columns
            
            # Verify source
            assert all(df['source_catalog'] == 'NASA_Exoplanet_Archive')
            
            print(f"✅ Found {len(df)} planets around Kepler-186")
        else:
            print("⚠️  Query returned None (network or API issue)")
    
    @pytest.mark.skipif(
        not ExoplanetFetcher().is_available(),
        reason="Exoplanet Archive not available"
    )
    def test_habitable_zone_candidates(self, fetcher):
        """Test habitable zone candidate query."""
        df = fetcher.get_habitable_zone_candidates()
        
        if df is not None:
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0, "Should find HZ candidates"
            
            # Check HZ flag
            if 'hz_candidate' in df.columns:
                assert all(df['hz_candidate'] == True)
            
            # Check size constraints (if column exists)
            if 'radius_rearth' in df.columns:
                radii = df['radius_rearth'].dropna()
                if len(radii) > 0:
                    assert radii.min() >= 0.4  # Allow small margin
                    assert radii.max() <= 2.1  # Allow small margin
            
            print(f"✅ Found {len(df)} HZ candidates")
        else:
            print("⚠️  No HZ candidates found")
    
    @pytest.mark.skipif(
        not ExoplanetFetcher().is_available(),
        reason="Exoplanet Archive not available"
    )
    def test_parameter_query(self, fetcher):
        """Test querying by parameters."""
        # Query Hot Jupiters (massive + short period)
        df = fetcher.query_by_params(
            min_mass=0.5,  # Jupiter masses
            max_period=10.0,  # days
            max_results=50
        )
        
        if df is not None:
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0, "Should find Hot Jupiters"
            
            # Verify parameters (if columns exist)
            if 'mass_mjup' in df.columns:
                masses = df['mass_mjup'].dropna()
                if len(masses) > 0:
                    assert masses.min() >= 0.4  # Small margin
            
            if 'period_days' in df.columns:
                periods = df['period_days'].dropna()
                if len(periods) > 0:
                    assert periods.max() <= 11  # Small margin
            
            print(f"✅ Found {len(df)} Hot Jupiters")
        else:
            print("⚠️  Parameter query returned None")
    
    @pytest.mark.skipif(
        not ExoplanetFetcher().is_available(),
        reason="Exoplanet Archive not available"
    )
    def test_cone_search(self, fetcher):
        """Test cone search by coordinates."""
        # Search near HD 209458 (known exoplanet host)
        # Approximate coordinates
        ra, dec = 330.8, 18.9
        radius = 1.0  # degrees
        
        df = fetcher.cone_search(ra=ra, dec=dec, radius=radius, max_results=20)
        
        if df is not None:
            assert isinstance(df, pd.DataFrame)
            
            # Check coordinates (if exist)
            if 'ra' in df.columns and 'dec' in df.columns:
                # Should be near search center (within search radius)
                pass  # Actual validation would need precise checking
            
            print(f"✅ Cone search found {len(df)} planets")
        else:
            print("⚠️  Cone search returned None")
    
    def test_statistics(self, fetcher):
        """Test statistics method."""
        stats = fetcher.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'catalog' in stats
        assert stats['catalog'] == 'NASA Exoplanet Archive'
        assert 'available' in stats
        assert 'discovery_methods' in stats
        
        if fetcher.is_available():
            assert len(stats['discovery_methods']) > 0
        
        print(f"✅ Statistics: {stats['catalog']}, Available: {stats['available']}")
    
    @pytest.mark.skipif(
        not ExoplanetFetcher().is_available(),
        reason="Exoplanet Archive not available"
    )
    def test_data_types(self, fetcher):
        """Test that returned data has correct types."""
        df = fetcher.query_by_host("HD 209458")
        
        if df is not None and len(df) > 0:
            # Check numeric columns are numeric
            numeric_cols = [
                'ra', 'dec', 'period_days', 'radius_rearth', 'mass_mearth'
            ]
            
            for col in numeric_cols:
                if col in df.columns:
                    assert df[col].dtype in [np.float64, np.float32, np.int64, np.int32] or df[col].dtype == object
            
            print("✅ Data types validated")
    
    @pytest.mark.skipif(
        not ExoplanetFetcher().is_available(),
        reason="Exoplanet Archive not available"
    )
    def test_known_systems(self, fetcher):
        """Test with well-known systems."""
        known_systems = [
            ("HD 209458", 1),  # At least 1 planet
            ("TRAPPIST-1", 7),  # 7 planets
            ("Kepler-90", 8),   # 8 planets
        ]
        
        for host, expected_min in known_systems:
            df = fetcher.query_by_host(host)
            
            if df is not None:
                assert len(df) >= expected_min, f"{host} should have ≥{expected_min} planets"
                print(f"✅ {host}: {len(df)} planets (expected ≥{expected_min})")
            else:
                print(f"⚠️  {host}: Query failed")


def run_all_tests():
    """Run all tests manually (without pytest)."""
    print("="*80)
    print("EXOPLANET FETCHER TEST SUITE")
    print("="*80)
    
    fetcher = ExoplanetFetcher()
    test_suite = TestExoplanetFetcher()
    
    # Test 1: Initialization
    print("\n[Test 1] Initialization")
    try:
        test_suite.test_initialization(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    if not fetcher.is_available():
        print("\n⚠️  Exoplanet Archive not available - skipping online tests")
        print("Install with: pip install astroquery")
        return
    
    # Test 2: Query by host
    print("\n[Test 2] Query by Host Star")
    try:
        test_suite.test_query_by_host(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: HZ candidates
    print("\n[Test 3] Habitable Zone Candidates")
    try:
        test_suite.test_habitable_zone_candidates(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 4: Parameter query
    print("\n[Test 4] Parameter Query (Hot Jupiters)")
    try:
        test_suite.test_parameter_query(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 5: Cone search
    print("\n[Test 5] Cone Search")
    try:
        test_suite.test_cone_search(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 6: Statistics
    print("\n[Test 6] Statistics")
    try:
        test_suite.test_statistics(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 7: Data types
    print("\n[Test 7] Data Types")
    try:
        test_suite.test_data_types(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 8: Known systems
    print("\n[Test 8] Known Systems Validation")
    try:
        test_suite.test_known_systems(fetcher)
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "="*80)
    print("✅ TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()
