"""
Configurable Database System - Auswählbare Bereiche und Größen

Ermöglicht:
- Verschiedene Datenbankgrößen (500, 1k, 5k, 10k, 50k, 100k)
- RA/Dec Bereiche einschränken
- Magnitude Filter
- Distanz Filter
- Custom Queries
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================================
# DATABASE SIZE PRESETS
# ============================================================================

DATABASE_SIZES = {
    'XS': {
        'name': 'Extra Small',
        'size': 500,
        'description': 'Schnelle Tests, niedrige Auflösung',
        'query': "SELECT TOP 500 * FROM gaiadr3.gaia_source"
    },
    'S': {
        'name': 'Small',
        'size': 1000,
        'description': 'Schnelle Visualisierung',
        'query': "SELECT TOP 1000 * FROM gaiadr3.gaia_source"
    },
    'M': {
        'name': 'Medium',
        'size': 5000,
        'description': 'Gute Balance zwischen Speed/Detail',
        'query': "SELECT TOP 5000 * FROM gaiadr3.gaia_source"
    },
    'L': {
        'name': 'Large',
        'size': 10000,
        'description': 'Hohe Auflösung',
        'query': "SELECT TOP 10000 * FROM gaiadr3.gaia_source"
    },
    'XL': {
        'name': 'Extra Large',
        'size': 50000,
        'description': 'Sehr hohe Auflösung (langsamer)',
        'query': "SELECT TOP 50000 * FROM gaiadr3.gaia_source"
    },
    'XXL': {
        'name': 'Huge',
        'size': 100000,
        'description': 'Maximum Detail (sehr langsam)',
        'query': "SELECT TOP 100000 * FROM gaiadr3.gaia_source"
    }
}

# ============================================================================
# REGION PRESETS
# ============================================================================

REGION_PRESETS = {
    'full_sky': {
        'name': 'Full Sky',
        'ra_min': 0,
        'ra_max': 360,
        'dec_min': -90,
        'dec_max': 90,
        'description': 'Gesamter Himmel'
    },
    'galactic_center': {
        'name': 'Galactic Center',
        'ra_min': 265,
        'ra_max': 270,
        'dec_min': -30,
        'dec_max': -25,
        'description': 'Sgr A* Region'
    },
    'orion': {
        'name': 'Orion',
        'ra_min': 80,
        'ra_max': 90,
        'dec_min': -10,
        'dec_max': 10,
        'description': 'Orion Nebula Region'
    },
    'north_pole': {
        'name': 'North Celestial Pole',
        'ra_min': 0,
        'ra_max': 360,
        'dec_min': 60,
        'dec_max': 90,
        'description': 'Nördlicher Himmelspol'
    },
    'south_pole': {
        'name': 'South Celestial Pole',
        'ra_min': 0,
        'ra_max': 360,
        'dec_min': -90,
        'dec_max': -60,
        'description': 'Südlicher Himmelspol'
    },
    'ecliptic': {
        'name': 'Ecliptic Band',
        'ra_min': 0,
        'ra_max': 360,
        'dec_min': -30,
        'dec_max': 30,
        'description': 'Ekliptik-Band (Planeten-Region)'
    }
}

# ============================================================================
# FILTER CONFIGURATION
# ============================================================================

class DatabaseFilter:
    """Filter configuration for database queries"""
    
    def __init__(self):
        self.ra_min = 0
        self.ra_max = 360
        self.dec_min = -90
        self.dec_max = 90
        self.mag_min = None
        self.mag_max = None
        self.dist_min = None  # parsec
        self.dist_max = None  # parsec
        self.size = 'XL'
    
    def apply_region_preset(self, preset_name):
        """Apply region preset"""
        if preset_name in REGION_PRESETS:
            preset = REGION_PRESETS[preset_name]
            self.ra_min = preset['ra_min']
            self.ra_max = preset['ra_max']
            self.dec_min = preset['dec_min']
            self.dec_max = preset['dec_max']
    
    def to_dict(self):
        """Export as dictionary"""
        return {
            'ra_range': (self.ra_min, self.ra_max),
            'dec_range': (self.dec_min, self.dec_max),
            'mag_range': (self.mag_min, self.mag_max),
            'dist_range': (self.dist_min, self.dist_max),
            'size': self.size
        }


# ============================================================================
# DATABASE LOADER WITH FILTERS
# ============================================================================

def load_database_filtered(db_path='data/gaia_50k.csv', filter_config=None):
    """
    Load database with optional filters
    
    Args:
        db_path: Path to database file
        filter_config: DatabaseFilter instance
    
    Returns:
        Filtered DataFrame
    """
    # Load full database
    df = pd.read_csv(db_path)
    
    if filter_config is None:
        return df
    
    # Apply RA/Dec filter
    mask = (
        (df['ra'] >= filter_config.ra_min) &
        (df['ra'] <= filter_config.ra_max) &
        (df['dec'] >= filter_config.dec_min) &
        (df['dec'] <= filter_config.dec_max)
    )
    
    # Apply magnitude filter
    if filter_config.mag_min is not None:
        mask &= (df['phot_g_mean_mag'] >= filter_config.mag_min)
    if filter_config.mag_max is not None:
        mask &= (df['phot_g_mean_mag'] <= filter_config.mag_max)
    
    # Apply distance filter
    if filter_config.dist_min is not None:
        mask &= (df['distance_pc'] >= filter_config.dist_min)
    if filter_config.dist_max is not None:
        mask &= (df['distance_pc'] <= filter_config.dist_max)
    
    filtered = df[mask].copy()
    
    # Apply size limit
    if filter_config.size in DATABASE_SIZES:
        max_size = DATABASE_SIZES[filter_config.size]['size']
        if len(filtered) > max_size:
            # Sample randomly
            import random
            random.seed(42)
            indices = sorted(random.sample(range(len(filtered)), max_size))
            filtered = filtered.iloc[indices].copy()
    
    return filtered


# ============================================================================
# QUERY BUILDER
# ============================================================================

def build_gaia_query(filter_config):
    """
    Build GAIA TAP query from filter configuration
    
    Args:
        filter_config: DatabaseFilter instance
    
    Returns:
        SQL query string
    """
    size_limit = DATABASE_SIZES.get(filter_config.size, DATABASE_SIZES['M'])['size']
    
    query = f"""
    SELECT TOP {size_limit}
        source_id, ra, dec, parallax, 
        pmra, pmdec, phot_g_mean_mag,
        radial_velocity
    FROM gaiadr3.gaia_source
    WHERE 
        ra BETWEEN {filter_config.ra_min} AND {filter_config.ra_max}
        AND dec BETWEEN {filter_config.dec_min} AND {filter_config.dec_max}
    """
    
    if filter_config.mag_min is not None:
        query += f"\n    AND phot_g_mean_mag >= {filter_config.mag_min}"
    if filter_config.mag_max is not None:
        query += f"\n    AND phot_g_mean_mag <= {filter_config.mag_max}"
    
    # Distance filter (via parallax)
    if filter_config.dist_min is not None:
        plx_max = 1000.0 / filter_config.dist_min  # mas
        query += f"\n    AND parallax <= {plx_max}"
    if filter_config.dist_max is not None:
        plx_min = 1000.0 / filter_config.dist_max  # mas
        query += f"\n    AND parallax >= {plx_min}"
    
    query += "\n    ORDER BY phot_g_mean_mag ASC"
    
    return query


# ============================================================================
# DATABASE INFO
# ============================================================================

def get_database_info(df):
    """Get statistics about database"""
    info = {
        'total_stars': len(df),
        'ra_range': (df['ra'].min(), df['ra'].max()),
        'dec_range': (df['dec'].min(), df['dec'].max()),
        'mag_range': (df['phot_g_mean_mag'].min(), df['phot_g_mean_mag'].max()),
        'dist_range': (df['distance_pc'].min(), df['distance_pc'].max()) if 'distance_pc' in df else None,
        'coverage_deg2': None
    }
    
    # Calculate sky coverage
    ra_span = info['ra_range'][1] - info['ra_range'][0]
    dec_span = info['dec_range'][1] - info['dec_range'][0]
    # Rough approximation (doesn't account for spherical geometry)
    info['coverage_deg2'] = ra_span * dec_span
    info['coverage_percent'] = (info['coverage_deg2'] / 41253.0) * 100  # 41253 deg² = full sky
    
    return info


# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

def save_filter_config(filter_config, filename='filter_config.json'):
    """Save filter configuration to JSON"""
    import json
    with open(filename, 'w') as f:
        json.dump(filter_config.to_dict(), f, indent=2)


def load_filter_config(filename='filter_config.json'):
    """Load filter configuration from JSON"""
    import json
    with open(filename, 'r') as f:
        config_dict = json.load(f)
    
    config = DatabaseFilter()
    config.ra_min, config.ra_max = config_dict['ra_range']
    config.dec_min, config.dec_max = config_dict['dec_range']
    config.mag_min, config.mag_max = config_dict['mag_range']
    config.dist_min, config.dist_max = config_dict['dist_range']
    config.size = config_dict['size']
    
    return config


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    import io
    
    # UTF-8 for Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("="*80)
    print("CONFIGURABLE DATABASE SYSTEM")
    print("="*80)
    print()
    
    # Show available sizes
    print("📊 AVAILABLE DATABASE SIZES:")
    print("-" * 80)
    for key, info in DATABASE_SIZES.items():
        print(f"  {key:4s} - {info['name']:15s} ({info['size']:6,} stars) - {info['description']}")
    
    # Show region presets
    print("\n🗺️  REGION PRESETS:")
    print("-" * 80)
    for key, info in REGION_PRESETS.items():
        ra_range = f"RA: {info['ra_min']}-{info['ra_max']}°"
        dec_range = f"Dec: {info['dec_min']}-{info['dec_max']}°"
        print(f"  {key:20s} - {info['name']:25s} ({ra_range}, {dec_range})")
    
    # Example filter
    print("\n🔧 EXAMPLE: Galactic Center, Medium Size")
    print("-" * 80)
    
    filter_config = DatabaseFilter()
    filter_config.apply_region_preset('galactic_center')
    filter_config.size = 'M'
    filter_config.mag_max = 15.0  # Nur helle Sterne
    
    print(f"  Region: RA {filter_config.ra_min}-{filter_config.ra_max}°, Dec {filter_config.dec_min}-{filter_config.dec_max}°")
    print(f"  Size: {DATABASE_SIZES[filter_config.size]['name']} ({DATABASE_SIZES[filter_config.size]['size']:,} stars)")
    print(f"  Magnitude: < {filter_config.mag_max}")
    
    # Build query
    print("\n📝 GENERATED GAIA QUERY:")
    print("-" * 80)
    query = build_gaia_query(filter_config)
    print(query)
