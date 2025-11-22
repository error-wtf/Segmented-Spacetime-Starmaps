"""
Integration tests for SSZ StarMaps real data pipeline.

Tests the complete workflow from catalog fetch to visualization.

© 2025 Carmen Wrede, Lino Casu
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ssz_starmaps.catalogs import CatalogManager, StarEntry
from ssz_starmaps.transform import transform_catalog, TransformConfig, compute_statistics
from ssz_starmaps.ssz_metric import Xi, D_SSZ, schwarzschild_radius


class TestCatalogManager:
    """Test catalog management."""
    
    def test_catalog_manager_init(self):
        """Test CatalogManager initialization."""
        manager = CatalogManager(offline=True)
        assert manager.offline == True
        assert manager.cache_dir.exists()
    
    def test_mock_catalog_generation(self):
        """Test mock catalog generation."""
        manager = CatalogManager(offline=True)
        stars = manager._get_mock_catalog(50)
        
        assert len(stars) == 50
        assert 'ra' in stars.columns
        assert 'dec' in stars.columns
        assert 'distance_pc' in stars.columns
        
        # Check ranges
        assert stars['ra'].min() >= 0
        assert stars['ra'].max() <= 360
        assert stars['dec'].min() >= -90
        assert stars['dec'].max() <= 90
        assert stars['distance_pc'].min() > 0
    
    def test_fetch_nearby_offline(self):
        """Test fetch_nearby in offline mode."""
        manager = CatalogManager(offline=True)
        stars = manager.fetch_nearby(distance_pc=100, max_stars=100)
        
        assert len(stars) == 100
        assert all(col in stars.columns for col in ['ra', 'dec', 'distance_pc'])
    
    def test_list_regions(self):
        """Test listing available regions."""
        manager = CatalogManager()
        regions = manager.list_regions()
        
        assert 'orion' in regions
        assert 'pleiades' in regions
        assert len(regions) >= 5


class TestTransformPipeline:
    """Test SSZ transformation pipeline."""
    
    @pytest.fixture
    def sample_stars(self):
        """Create sample star catalog."""
        return pd.DataFrame({
            'ra': np.linspace(0, 360, 20),
            'dec': np.linspace(-90, 90, 20),
            'distance_pc': np.logspace(0, 2, 20),  # 1-100 pc
            'name': [f'Star-{i}' for i in range(20)]
        })
    
    def test_transform_catalog(self, sample_stars):
        """Test catalog transformation."""
        stars_ssz = transform_catalog(sample_stars, show_progress=False)
        
        # Check output columns
        assert 'distance_ssz_pc' in stars_ssz.columns
        assert 'xi' in stars_ssz.columns
        assert 'stretch_factor' in stars_ssz.columns
        assert 'D_ssz' in stars_ssz.columns
        
        # Check lengths match
        assert len(stars_ssz) == len(sample_stars)
    
    def test_radial_stretch_physics(self, sample_stars):
        """Test that SSZ always stretches (never compresses)."""
        stars_ssz = transform_catalog(sample_stars, show_progress=False)
        
        # SSZ should always increase distance
        assert all(stars_ssz['distance_ssz_pc'] >= stars_ssz['distance_pc'])
        
        # Stretch factor should be >= 1
        assert all(stars_ssz['stretch_factor'] >= 1.0)
    
    def test_xi_bounds(self, sample_stars):
        """Test that Xi is bounded [0, 1)."""
        stars_ssz = transform_catalog(sample_stars, show_progress=False)
        
        assert all(stars_ssz['xi'] >= 0)
        assert all(stars_ssz['xi'] < 1)
    
    def test_transform_config(self, sample_stars):
        """Test custom transformation config."""
        config = TransformConfig(
            mass_kg=2.0 * 1.989e30,  # 2 solar masses
            apply_time_dilation=True,
            apply_radial_stretch=True
        )
        
        stars_ssz = transform_catalog(sample_stars, config=config, show_progress=False)
        
        assert len(stars_ssz) > 0
        assert 'D_ssz' in stars_ssz.columns
    
    def test_compute_statistics(self, sample_stars):
        """Test statistics computation."""
        stars_ssz = transform_catalog(sample_stars, show_progress=False)
        stats = compute_statistics(stars_ssz)
        
        # Check required keys
        assert 'n_stars' in stats
        assert 'mean_stretch' in stats
        assert 'mean_xi' in stats
        
        # Check values
        assert stats['n_stars'] == len(sample_stars)
        assert stats['mean_stretch'] >= 1.0
        assert 0 <= stats['mean_xi'] < 1


class TestStarEntry:
    """Test StarEntry dataclass."""
    
    def test_star_entry_creation(self):
        """Test creating StarEntry."""
        star = StarEntry(
            name='Test Star',
            ra=10.5,
            dec=-30.2,
            distance_pc=50.0,
            source='TEST'
        )
        
        assert star.name == 'Test Star'
        assert star.ra == 10.5
        assert star.distance_pc == 50.0
    
    def test_star_entry_to_dict(self):
        """Test conversion to dictionary."""
        star = StarEntry(
            name='Test',
            ra=0,
            dec=0,
            distance_pc=10,
            vmag=5.0,
            source='TEST'
        )
        
        d = star.to_dict()
        assert isinstance(d, dict)
        assert d['name'] == 'Test'
        assert d['vmag'] == 5.0


class TestPhysicsValidation:
    """Test physics against validated values."""
    
    def test_xi_at_known_points(self):
        """Test Xi at validated points."""
        r_s = schwarzschild_radius(1.989e30)  # Solar mass
        
        # At r = 2*r_s, Xi ≈ 0.960682 (from validation)
        r = 2.0 * r_s
        xi = Xi(r, r_s)
        
        assert abs(xi - 0.960682) < 1e-5
    
    def test_time_dilation_at_rs(self):
        """Test time dilation at Schwarzschild radius."""
        r_s = schwarzschild_radius(1.989e30)
        D = D_SSZ(r_s, r_s)
        
        # Should be finite (GR diverges here!)
        assert np.isfinite(D)
        assert D > 0
        assert D < 1
        
        # Expected value ~0.555
        assert abs(D - 0.555028) < 0.01
    
    def test_universal_crossover(self):
        """Test universal intersection point."""
        # This is tested in validate_against_mass_projection.py
        # but we include a simple check here
        r_s = schwarzschild_radius(1.989e30)
        
        # Around r*/r_s ≈ 1.387
        r_star = 1.387 * r_s
        D_ssz = D_SSZ(r_star, r_s)
        
        # D_SSZ should be close to ~0.528
        assert abs(D_ssz - 0.528) < 0.01


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_full_pipeline_offline(self, tmp_path):
        """Test complete pipeline in offline mode."""
        # Setup
        manager = CatalogManager(offline=True)
        
        # Fetch
        stars = manager.fetch_nearby(distance_pc=50, max_stars=20)
        assert len(stars) == 20
        
        # Transform
        stars_ssz = transform_catalog(stars, show_progress=False)
        assert len(stars_ssz) == 20
        
        # Save
        output_file = tmp_path / 'test_stars.csv'
        stars_ssz.to_csv(output_file, index=False)
        assert output_file.exists()
        
        # Reload
        stars_reloaded = pd.read_csv(output_file)
        assert len(stars_reloaded) == 20
        assert 'distance_ssz_pc' in stars_reloaded.columns
    
    def test_batch_transform_consistency(self):
        """Test that batch transform is consistent."""
        manager = CatalogManager(offline=True)
        stars = manager._get_mock_catalog(50)
        
        # Transform twice with same seed
        np.random.seed(42)
        stars1 = manager._get_mock_catalog(50)
        stars_ssz1 = transform_catalog(stars1, show_progress=False)
        
        np.random.seed(42)
        stars2 = manager._get_mock_catalog(50)
        stars_ssz2 = transform_catalog(stars2, show_progress=False)
        
        # Results should be identical
        pd.testing.assert_frame_equal(
            stars_ssz1[['distance_pc', 'distance_ssz_pc']],
            stars_ssz2[['distance_pc', 'distance_ssz_pc']]
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
