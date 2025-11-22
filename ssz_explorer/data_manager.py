#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Manager - Progressive Loading System

Complete data management for SSZ Interactive3D Viewer.
Supports 5 levels of data density from preview to complete.

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import warnings

# Constants
G = 6.67430e-11  # m^3 kg^-1 s^-2
c = 2.99792458e8  # m/s
M_sun = 1.989e30  # kg
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
PC_TO_M = 3.0857e16


class DataLevel:
    """Data density levels."""
    PREVIEW = 1    # 1k-10k objects, instant
    STANDARD = 2   # 100k-1M objects, fast
    DETAILED = 3   # 10M-100M objects, minutes
    COMPLETE = 4   # 1B+ objects, hours
    CUSTOM = 5     # User data, unlimited


class DataManager:
    """
    Progressive data loading and management.
    
    Features:
    - 5 data density levels
    - Multiple catalog sources
    - Automatic caching
    - Query optimization
    - SSZ parameter computation
    """
    
    def __init__(self, cache_dir='ssz_data/cache', default_level='standard'):
        """
        Initialize data manager.
        
        Parameters
        ----------
        cache_dir : str
            Cache directory path
        default_level : str
            Default data level ('preview', 'standard', 'detailed', 'complete', 'custom')
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.levels = {
            'preview': DataLevel.PREVIEW,
            'standard': DataLevel.STANDARD,
            'detailed': DataLevel.DETAILED,
            'complete': DataLevel.COMPLETE,
            'custom': DataLevel.CUSTOM
        }
        
        self.default_level = default_level
        self.current_data = None
        self.metadata = self._load_metadata()
        
    def _load_metadata(self):
        """Load metadata about available catalogs."""
        metadata_file = self.cache_dir.parent / 'metadata' / 'catalog_info.json'
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
        
        # Default metadata
        return {
            'catalogs': {
                'gaia': {
                    'name': 'GAIA DR3',
                    'objects': 1800000000,
                    'type': 'stars',
                    'status': 'available',
                    'api': 'astroquery.gaia',
                    'columns': ['source_id', 'ra', 'dec', 'parallax', 'pmra', 'pmdec', 
                               'phot_g_mean_mag', 'bp_rp']
                },
                'simbad': {
                    'name': 'SIMBAD',
                    'objects': 11000000,
                    'type': 'stars',
                    'status': 'available',
                    'api': 'astroquery.simbad'
                },
                'ned': {
                    'name': 'NED',
                    'objects': 200000000,
                    'type': 'galaxies',
                    'status': 'available',
                    'api': 'astroquery.ned'
                },
                'exoplanets': {
                    'name': 'NASA Exoplanet Archive',
                    'objects': 5000,
                    'type': 'exoplanets',
                    'status': 'available',
                    'api': 'astroquery.ipac.nexsci'
                }
            },
            'last_update': datetime.now().isoformat()
        }
    
    def load_catalog(self, catalog='gaia', level='standard', region=None, filters=None, **kwargs):
        """
        Load catalog data with specified level.
        
        Parameters
        ----------
        catalog : str
            Catalog name ('gaia', 'simbad', 'ned', 'exoplanets', 'custom')
        level : str
            Data level ('preview', 'standard', 'detailed', 'complete')
        region : dict, optional
            Region specification {'ra_min', 'ra_max', 'dec_min', 'dec_max'}
            or {'ra', 'dec', 'radius'}
        filters : dict, optional
            Data filters (magnitude, parallax, etc.)
        
        Returns
        -------
        pd.DataFrame
            Loaded data with SSZ parameters
        """
        
        # Validate inputs
        valid_catalogs = ['gaia', 'simbad', 'ned', 'exoplanets', 'custom']
        valid_levels = ['preview', 'standard', 'detailed', 'complete']
        
        if catalog not in valid_catalogs:
            raise ValueError(f"Invalid catalog '{catalog}'. Must be one of: {valid_catalogs}")
        
        if level not in valid_levels:
            raise ValueError(f"Invalid level '{level}'. Must be one of: {valid_levels}")
        
        print(f"Loading {catalog} catalog at {level} level...")
        
        # Check cache first
        cache_file = self._get_cache_file(catalog, level, region)
        
        if cache_file.exists():
            print(f"Loading from cache: {cache_file}")
            data = pd.read_parquet(cache_file)
        else:
            # Generate or query data
            if catalog == 'gaia':
                data = self._load_gaia(level, region, filters, **kwargs)
            elif catalog == 'simbad':
                data = self._load_simbad(level, region, filters, **kwargs)
            elif catalog == 'ned':
                data = self._load_ned(level, region, filters, **kwargs)
            elif catalog == 'exoplanets':
                data = self._load_exoplanets(level, filters, **kwargs)
            elif catalog == 'custom':
                data = self._load_custom(**kwargs)
            else:
                raise ValueError(f"Unknown catalog: {catalog}")
            
            # Save to cache
            self._save_to_cache(data, cache_file)
        
        # Compute SSZ parameters
        data = self._compute_ssz_parameters(data)
        
        # Apply filters
        if filters:
            data = self._apply_filters(data, filters)
        
        self.current_data = data
        print(f"Loaded {len(data)} objects")
        
        return data
    
    def _load_gaia(self, level, region, filters, **kwargs):
        """Load GAIA data - real or synthetic."""
        
        use_real_data = kwargs.get('use_real_data', True)
        
        if use_real_data:
            return self._load_gaia_real(level, region, filters, **kwargs)
        else:
            return self._load_gaia_synthetic(level, region, filters, **kwargs)
    
    def _load_gaia_real(self, level, region, filters, **kwargs):
        """Load real GAIA DR3 data via API."""
        
        try:
            from catalog_fetchers import GAIAFetcher
            
            # Determine number of objects for level
            n_objects = {
                'preview': 1000,
                'standard': 10000,
                'detailed': 100000,
                'complete': 1000000
            }[level]
            
            n = min(n_objects, kwargs.get('limit', n_objects))
            
            print(f"Loading {n} real GAIA DR3 objects...")
            
            fetcher = GAIAFetcher()
            
            if not fetcher.available:
                print("  [WARN] astroquery not available, falling back to synthetic data")
                return self._load_gaia_synthetic(level, region, filters, **kwargs)
            
            # Use region if provided, otherwise query around galactic center
            if region:
                ra = region.get('ra', 266.4)
                dec = region.get('dec', -29.0)
                radius = region.get('radius')
            else:
                # Default: Galactic center region
                ra = 266.4
                dec = -29.0
                radius = None
            
            if radius is None:
                radius = 10.0  # degrees
            
            # Query GAIA
            data = fetcher.cone_search(
                ra=ra,
                dec=dec,
                radius=radius,
                max_sources=n
            )
            
            if len(data) == 0:
                print("  [WARN] No data returned from GAIA, falling back to synthetic")
                return self._load_gaia_synthetic(level, region, filters, **kwargs)
            
            # Add stellar mass estimate (from color-magnitude relation)
            if 'phot_g_mean_mag' in data.columns and 'bp_rp' in data.columns:
                # Simple mass estimate from G magnitude and color
                # M_V ~ G - 5*log10(distance/10)
                # Then mass from M_V
                data['mass_msun'] = self._estimate_mass_from_gaia(data)
            else:
                # Default mass if photometry missing
                data['mass_msun'] = 1.0
            
            # Add spectral type estimate
            if 'bp_rp' in data.columns:
                data['spectral_type'] = data['bp_rp'].apply(self._color_to_spectral_type)
            else:
                data['spectral_type'] = 'G'
            
            # Mark as real data
            data.attrs['data_source'] = 'GAIA_DR3'
            data.attrs['real_data'] = True
            
            print(f"  [OK] Loaded {len(data)} real GAIA stars")
            
            return data
            
        except ImportError as e:
            print(f"  [ERROR] catalog_fetchers not available: {e}")
            print("  [INFO] Falling back to synthetic data")
            return self._load_gaia_synthetic(level, region, filters, **kwargs)
        except ConnectionError as e:
            print(f"  [ERROR] No internet connection")
            print("  [INFO] Falling back to synthetic data")
            return self._load_gaia_synthetic(level, region, filters, **kwargs)
        except TimeoutError as e:
            print(f"  [ERROR] GAIA query timeout (slow connection)")
            print("  [INFO] Falling back to synthetic data")
            return self._load_gaia_synthetic(level, region, filters, **kwargs)
        except ValueError as e:
            print(f"  [ERROR] Invalid query parameters: {e}")
            print("  [INFO] Falling back to synthetic data")
            return self._load_gaia_synthetic(level, region, filters, **kwargs)
        except Exception as e:
            print(f"  [ERROR] Unexpected error loading GAIA data: {type(e).__name__}")
            print(f"  [DETAIL] {str(e)[:200]}")
            print("  [INFO] Falling back to synthetic data")
            return self._load_gaia_synthetic(level, region, filters, **kwargs)
    
    def _load_gaia_synthetic(self, level, region, filters, **kwargs):
        """Generate synthetic GAIA-like data (fallback)."""
        
        n_objects = {
            'preview': 1000,
            'standard': 100000,
            'detailed': 1000000,
            'complete': 10000000
        }[level]
        
        n = min(n_objects, kwargs.get('limit', n_objects))
        
        print(f"Generating {n} synthetic GAIA objects...")
        
        # Generate realistic galactic distribution
        # Exponential disk + spherical bulge
        data = []
        
        for i in range(n):
            # 90% disk, 10% bulge
            if np.random.random() < 0.9:
                # Disk
                r = np.random.exponential(3000)  # pc
                z = np.random.normal(0, 300)
                theta = np.random.uniform(0, 2*np.pi)
                x = r * np.cos(theta)
                y = r * np.sin(theta)
            else:
                # Bulge
                r = np.random.exponential(1000)
                theta = np.random.uniform(0, 2*np.pi)
                phi = np.random.uniform(0, np.pi)
                x = r * np.sin(phi) * np.cos(theta)
                y = r * np.sin(phi) * np.sin(theta)
                z = r * np.cos(phi)
            
            # Convert to equatorial
            ra = np.arctan2(y, x) * 180/np.pi
            if ra < 0:
                ra += 360
            dec = np.arcsin(z / np.sqrt(x**2 + y**2 + z**2)) * 180/np.pi
            
            distance_pc = np.sqrt(x**2 + y**2 + z**2)
            parallax = 1000 / distance_pc if distance_pc > 0 else 0  # mas
            
            # Stellar properties
            mass_msun = self._generate_stellar_mass()
            mag_g = self._mass_to_magnitude(mass_msun) + 5*np.log10(distance_pc/10)
            bp_rp = self._mass_to_color(mass_msun)
            spectral_type = self._mass_to_spectral_type(mass_msun)
            
            data.append({
                'source_id': i + 1000000000,
                'ra': ra,
                'dec': dec,
                'l': 0,  # TODO: convert to galactic
                'b': 0,
                'parallax': parallax,
                'pmra': np.random.normal(0, 5),  # mas/yr
                'pmdec': np.random.normal(0, 5),
                'phot_g_mean_mag': mag_g,
                'bp_rp': bp_rp,
                'distance_pc': distance_pc,
                'mass_msun': mass_msun,
                'spectral_type': spectral_type
            })
        
        df = pd.DataFrame(data)
        df.attrs['data_source'] = 'synthetic'
        df.attrs['real_data'] = False
        
        return df
    
    def _load_simbad(self, level, region, filters, **kwargs):
        """Load SIMBAD data."""
        # Placeholder - use GAIA for now
        return self._load_gaia(level, region, filters, **kwargs)
    
    def _load_ned(self, level, region, filters, **kwargs):
        """Load NED galaxy data."""
        
        n_objects = {
            'preview': 100,
            'standard': 10000,
            'detailed': 100000,
            'complete': 1000000
        }[level]
        
        n = min(n_objects, kwargs.get('limit', n_objects))
        
        print(f"Generating {n} NED galaxies...")
        
        data = []
        for i in range(n):
            ra = np.random.uniform(0, 360)
            dec = np.random.uniform(-90, 90)
            
            # Redshift distribution
            z = np.random.lognormal(-1, 1)
            z = min(z, 10)
            
            # Luminosity distance (simplified)
            H0 = 70  # km/s/Mpc
            distance_mpc = (c * z) / (H0 * 1000)  # Mpc
            
            # Galaxy mass (Tully-Fisher relation)
            log_mass = np.random.uniform(9, 12)  # log10(M_sun)
            mass_msun = 10**log_mass
            
            data.append({
                'ned_id': i + 1000000,
                'ra': ra,
                'dec': dec,
                'redshift': z,
                'distance_mpc': distance_mpc,
                'mass_msun': mass_msun,
                'morphology': np.random.choice(['E', 'S0', 'Sa', 'Sb', 'Sc', 'Irr']),
                'magnitude': np.random.uniform(12, 22)
            })
        
        return pd.DataFrame(data)
    
    def _load_exoplanets(self, level, filters, **kwargs):
        """Load exoplanet data."""
        # Placeholder
        print("Exoplanet loading not yet implemented")
        return pd.DataFrame()
    
    def _load_custom(self, **kwargs):
        """Load user-provided custom data."""
        file_path = kwargs.get('file_path')
        if not file_path:
            raise ValueError("Custom data requires 'file_path' parameter")
        
        file_path = Path(file_path)
        
        if file_path.suffix == '.csv':
            data = pd.read_csv(file_path)
        elif file_path.suffix == '.parquet':
            data = pd.read_parquet(file_path)
        elif file_path.suffix in ['.fits', '.fit']:
            from astropy.io import fits
            with fits.open(file_path) as hdul:
                data = pd.DataFrame(hdul[1].data)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        return data
    
    def _compute_ssz_parameters(self, data):
        """Compute SSZ parameters for all objects."""
        
        print("Computing SSZ parameters...")
        
        if 'mass_msun' not in data.columns:
            warnings.warn("No mass column found, skipping SSZ calculations")
            return data
        
        # Compute for each object
        M_kg = data['mass_msun'].values * M_sun
        
        # Distance in meters
        if 'distance_pc' in data.columns:
            r_m = data['distance_pc'].values * PC_TO_M
        elif 'distance_mpc' in data.columns:
            r_m = data['distance_mpc'].values * 1e6 * PC_TO_M
        else:
            # Use parallax
            if 'parallax' in data.columns:
                r_m = (1000 / data['parallax'].values) * PC_TO_M
            else:
                warnings.warn("No distance information, using 1 kpc default")
                r_m = np.ones(len(data)) * 1000 * PC_TO_M
        
        # Schwarzschild radius
        r_s = 2 * G * M_kg / (c**2)
        
        # SSZ segment density
        Xi = np.where(r_s > 0, 1 - np.exp(-PHI * r_m / r_s), 0)
        
        # Time dilation
        D_ssz = 1 / (1 + Xi)
        D_gr = np.sqrt(np.maximum(1 - r_s / r_m, 0))
        
        # Add to dataframe
        data['r_s'] = r_s
        data['Xi'] = Xi
        data['D_ssz'] = D_ssz
        data['D_gr'] = D_gr
        data['stretch_factor'] = 1 + Xi
        
        return data
    
    def _apply_filters(self, data, filters):
        """Apply data filters."""
        
        filtered = data.copy()
        
        for key, value in filters.items():
            if isinstance(value, tuple) and len(value) == 2:
                # Range filter
                filtered = filtered[
                    (filtered[key] >= value[0]) & 
                    (filtered[key] <= value[1])
                ]
            elif isinstance(value, list):
                # List filter
                filtered = filtered[filtered[key].isin(value)]
            else:
                # Exact match
                filtered = filtered[filtered[key] == value]
        
        return filtered
    
    def _get_cache_file(self, catalog, level, region):
        """Get cache file path."""
        
        level_dir = self.cache_dir / level
        level_dir.mkdir(exist_ok=True)
        
        # Create filename
        if region:
            region_str = '_'.join([f"{k}{v}" for k, v in region.items()])
            filename = f"{catalog}_{level}_{region_str}.parquet"
        else:
            filename = f"{catalog}_{level}.parquet"
        
        return level_dir / filename
    
    def _save_to_cache(self, data, cache_file):
        """Save data to cache."""
        print(f"Saving to cache: {cache_file}")
        data.to_parquet(cache_file, index=False)
    
    def _generate_stellar_mass(self):
        """Generate stellar mass following IMF."""
        rand = np.random.random()
        if rand < 0.7:
            return np.random.uniform(0.1, 0.5)
        elif rand < 0.95:
            return np.random.uniform(0.5, 2.0)
        else:
            return np.random.uniform(2.0, 50.0)
    
    def _mass_to_magnitude(self, mass):
        """Estimate absolute magnitude from mass."""
        if mass < 0.43:
            L = 0.23 * (mass ** 2.3)
        else:
            L = mass ** 4
        return 4.83 - 2.5 * np.log10(L)
    
    def _mass_to_color(self, mass):
        """Estimate color from mass."""
        if mass < 0.5:
            return 1.5
        elif mass < 1.0:
            return 1.0
        elif mass < 2.0:
            return 0.5
        else:
            return 0.0
    
    def _mass_to_spectral_type(self, mass):
        """Convert mass to spectral type."""
        if mass < 0.45:
            return 'M'
        elif mass < 0.8:
            return 'K'
        elif mass < 1.04:
            return 'G'
        elif mass < 1.4:
            return 'F'
        elif mass < 2.1:
            return 'A'
        elif mass < 16:
            return 'B'
        else:
            return 'O'
    
    def _estimate_mass_from_gaia(self, data):
        """Estimate stellar mass from GAIA photometry."""
        
        # Use color-magnitude relation
        # This is a simple approximation
        mass_list = []
        
        for _, row in data.iterrows():
            g_mag = row.get('phot_g_mean_mag', 15)
            bp_rp = row.get('bp_rp', 1.0)
            distance_pc = row.get('distance_pc', 1000)
            
            if pd.isna(distance_pc) or distance_pc <= 0:
                mass_list.append(1.0)
                continue
            
            # Absolute magnitude
            M_G = g_mag - 5 * np.log10(distance_pc / 10)
            
            # Mass-luminosity relation (very approximate)
            # M ~ L^0.25 for main sequence
            # M_G ~ -2.5 * log10(L)
            # Rough conversion
            if M_G < 2:  # Bright/massive
                mass = 2.0 ** ((5 - M_G) / 3)
            elif M_G < 6:  # Sun-like
                mass = 1.5 ** ((5 - M_G) / 2.5)
            else:  # Faint/low mass
                mass = 0.5 ** ((M_G - 5) / 3)
            
            # Clamp to reasonable range
            mass = np.clip(mass, 0.08, 50.0)
            mass_list.append(mass)
        
        return mass_list
    
    def _color_to_spectral_type(self, bp_rp):
        """Convert BP-RP color to spectral type."""
        if pd.isna(bp_rp):
            return 'G'
        
        if bp_rp < 0.5:
            return 'A'
        elif bp_rp < 0.8:
            return 'F'
        elif bp_rp < 1.2:
            return 'G'
        elif bp_rp < 1.8:
            return 'K'
        else:
            return 'M'
    
    def cone_search(self, ra, dec, radius, catalog='gaia', level='standard'):
        """
        Cone search around coordinates.
        
        Parameters
        ----------
        ra : float
            Right ascension (degrees)
        dec : float
            Declination (degrees)
        radius : float
            Search radius (degrees)
        catalog : str
            Catalog to search
        level : str
            Data level
        
        Returns
        -------
        pd.DataFrame
            Objects within cone
        """
        
        # Load full catalog
        data = self.load_catalog(catalog, level)
        
        # Angular separation
        ra_rad = np.radians(data['ra'].values)
        dec_rad = np.radians(data['dec'].values)
        ra0_rad = np.radians(ra)
        dec0_rad = np.radians(dec)
        
        # Haversine formula
        dra = ra_rad - ra0_rad
        ddec = dec_rad - dec0_rad
        
        a = np.sin(ddec/2)**2 + np.cos(dec0_rad) * np.cos(dec_rad) * np.sin(dra/2)**2
        ang_sep = 2 * np.arcsin(np.sqrt(a))
        ang_sep_deg = np.degrees(ang_sep)
        
        # Filter
        mask = ang_sep_deg <= radius
        return data[mask].copy()
    
    def box_search(self, ra_min, ra_max, dec_min, dec_max, catalog='gaia', level='standard'):
        """Box search in RA/Dec."""
        
        data = self.load_catalog(catalog, level)
        
        mask = (
            (data['ra'] >= ra_min) & 
            (data['ra'] <= ra_max) &
            (data['dec'] >= dec_min) & 
            (data['dec'] <= dec_max)
        )
        
        return data[mask].copy()
    
    def get_statistics(self):
        """Get statistics about current data."""
        
        if self.current_data is None:
            return "No data loaded"
        
        stats = {
            'n_objects': len(self.current_data),
            'catalogs': self.current_data.get('catalog', 'unknown').unique().tolist() if 'catalog' in self.current_data.columns else ['unknown'],
            'ra_range': (self.current_data['ra'].min(), self.current_data['ra'].max()),
            'dec_range': (self.current_data['dec'].min(), self.current_data['dec'].max()),
        }
        
        if 'Xi' in self.current_data.columns:
            stats['xi_range'] = (self.current_data['Xi'].min(), self.current_data['Xi'].max())
            stats['xi_mean'] = self.current_data['Xi'].mean()
        
        return stats


def demo():
    """Demo: Data manager usage."""
    
    print("="*70)
    print("DATA MANAGER - Demo")
    print("="*70)
    print()
    
    # Initialize
    dm = DataManager()
    
    # Load preview data
    print("1. Loading PREVIEW level (1k stars)...")
    preview = dm.load_catalog('gaia', level='preview', limit=1000)
    print(f"   Loaded: {len(preview)} stars")
    print(f"   Columns: {list(preview.columns)}")
    print()
    
    # Load standard data
    print("2. Loading STANDARD level (100k stars)...")
    standard = dm.load_catalog('gaia', level='standard', limit=100000)
    print(f"   Loaded: {len(standard)} stars")
    print()
    
    # Cone search
    print("3. Cone search (Galactic center)...")
    cone_data = dm.cone_search(ra=266.4, dec=-29.0, radius=10.0, level='preview')  # INCREASED to 10°
    print(f"   Found: {len(cone_data)} objects within 10 degrees")
    print()
    
    # Statistics
    print("4. Data statistics:")
    stats = dm.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # Load galaxies
    print("5. Loading NED galaxies (preview)...")
    galaxies = dm.load_catalog('ned', level='preview', limit=100)
    print(f"   Loaded: {len(galaxies)} galaxies")
    print()
    
    print("="*70)
    print("DEMO COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    demo()
