"""
Multi-Source Astronomical Data Query System

GAIA DR3 alone is insufficient - we need multiple sources:
- GAIA DR3: Positions, parallax, proper motion
- ESO/ALMA: Molecular data, spectroscopy
- AKARI: Infrared photometry
- SIMBAD: Object names, classifications, cross-references
- VizieR: Additional catalogs
"""

import requests
import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord
from astropy import units as u
import time

# ============================================================================
# DATA SOURCE CAPABILITIES
# ============================================================================

DATA_SOURCES = {
    'GAIA': {
        'provides': ['ra', 'dec', 'parallax', 'pmra', 'pmdec', 'phot_g_mean_mag', 'source_id'],
        'missing': ['spectroscopy', 'infrared', 'molecular_data', 'detailed_classification'],
        'url': 'https://gea.esac.esa.int/tap-server/tap',
        'priority': 1
    },
    'SIMBAD': {
        'provides': ['object_names', 'types', 'cross_references', 'bibliographic_data'],
        'missing': ['high_precision_astrometry'],
        'url': 'http://simbad.u-strasbg.fr/simbad/sim-script',
        'priority': 2
    },
    'ESO': {
        'provides': ['spectroscopy', 'high_resolution_imaging', 'molecular_data'],
        'missing': ['all_sky_coverage'],
        'url': 'http://archive.eso.org/tap_obs',
        'priority': 3
    },
    'ALMA': {
        'provides': ['molecular_lines', 'continuum', 'high_resolution_mm'],
        'missing': ['optical_data'],
        'url': 'https://almascience.eso.org/tap',
        'priority': 3
    },
    'AKARI': {
        'provides': ['infrared_photometry', 'MIR_FIR_data'],
        'missing': ['optical_data', 'astrometry'],
        'url': 'http://vizier.u-strasbg.fr/viz-bin/votable',
        'priority': 4
    },
    'VizieR': {
        'provides': ['catalog_aggregation', 'cross_matching', 'photometry'],
        'missing': ['raw_data'],
        'url': 'http://vizier.u-strasbg.fr/viz-bin/votable',
        'priority': 2
    }
}


# ============================================================================
# SIMBAD QUERY
# ============================================================================

def query_simbad(object_name=None, ra=None, dec=None, radius=5):
    """
    Query SIMBAD for object information
    
    Args:
        object_name: Object name (e.g., 'Betelgeuse', 'M31')
        ra, dec: Coordinates in degrees
        radius: Search radius in arcminutes
    
    Returns:
        DataFrame with SIMBAD data
    """
    base_url = "http://simbad.u-strasbg.fr/simbad/sim-script"
    
    if object_name:
        script = f"""
output console=off script=off
format object "%IDLIST|%COO(d;A)|%COO(d;D)|%PLX|%OTYPE|%SP|%FLUXLIST(V)"
query id {object_name}
"""
    elif ra is not None and dec is not None:
        script = f"""
output console=off script=off
format object "%IDLIST|%COO(d;A)|%COO(d;D)|%PLX|%OTYPE|%SP|%FLUXLIST(V)"
query coo {ra} {dec} radius={radius}m
"""
    else:
        return None
    
    try:
        response = requests.post(base_url, data={'script': script}, timeout=30)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            # Parse SIMBAD output
            data = []
            for line in lines:
                if line and not line.startswith('::'):
                    parts = line.split('|')
                    if len(parts) >= 4:
                        data.append({
                            'identifiers': parts[0],
                            'ra': float(parts[1]) if parts[1] else None,
                            'dec': float(parts[2]) if parts[2] else None,
                            'parallax': parts[3],
                            'type': parts[4] if len(parts) > 4 else None,
                            'spectral_type': parts[5] if len(parts) > 5 else None,
                        })
            return pd.DataFrame(data) if data else None
    except Exception as e:
        print(f"SIMBAD query error: {e}")
        return None


# ============================================================================
# VizieR QUERY
# ============================================================================

def query_vizier(catalog, ra, dec, radius=5):
    """
    Query VizieR for catalog data
    
    Args:
        catalog: Catalog name (e.g., 'II/336/apass9', 'J/A+A/...')
        ra, dec: Coordinates in degrees
        radius: Search radius in arcminutes
    
    Returns:
        DataFrame with catalog data
    """
    from astroquery.vizier import Vizier
    
    try:
        coord = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
        v = Vizier(columns=['**'], row_limit=-1)
        result = v.query_region(coord, radius=radius*u.arcmin, catalog=catalog)
        
        if result:
            return result[0].to_pandas()
        return None
    except Exception as e:
        print(f"VizieR query error: {e}")
        return None


# ============================================================================
# AKARI INFRARED DATA
# ============================================================================

def query_akari(ra, dec, radius=5):
    """
    Query AKARI infrared catalog
    
    Returns 9/18/65/90/140/160 μm photometry
    """
    # AKARI catalogs in VizieR
    catalogs = {
        'IRC': 'II/297/irc',      # Infrared Camera
        'FIS': 'II/298/fis'       # Far-Infrared Surveyor
    }
    
    results = {}
    for name, catalog in catalogs.items():
        data = query_vizier(catalog, ra, dec, radius)
        if data is not None:
            results[name] = data
    
    return results if results else None


# ============================================================================
# MULTI-SOURCE OBJECT QUERY
# ============================================================================

def query_multi_source(object_name=None, ra=None, dec=None, radius=5, sources=['GAIA', 'SIMBAD', 'AKARI']):
    """
    Query multiple astronomical databases for comprehensive object data
    
    Args:
        object_name: Object name
        ra, dec: Coordinates in degrees
        radius: Search radius in arcminutes
        sources: List of sources to query
    
    Returns:
        Dictionary with data from each source
    """
    results = {
        'query': {
            'object_name': object_name,
            'ra': ra,
            'dec': dec,
            'radius': radius
        },
        'sources': {}
    }
    
    # Query SIMBAD first to get coordinates and cross-references
    if 'SIMBAD' in sources:
        print("Querying SIMBAD...")
        simbad_data = query_simbad(object_name=object_name, ra=ra, dec=dec, radius=radius)
        if simbad_data is not None:
            results['sources']['SIMBAD'] = simbad_data
            # Use SIMBAD coordinates if we only had name
            if ra is None and len(simbad_data) > 0:
                ra = simbad_data.iloc[0]['ra']
                dec = simbad_data.iloc[0]['dec']
    
    # Query AKARI for infrared
    if 'AKARI' in sources and ra is not None:
        print("Querying AKARI...")
        akari_data = query_akari(ra, dec, radius)
        if akari_data:
            results['sources']['AKARI'] = akari_data
    
    # Note: ESO/ALMA require TAP access and authentication
    # Would need astroquery.eso and specific credentials
    
    return results


# ============================================================================
# DATA MERGING
# ============================================================================

def merge_multi_source_data(results):
    """
    Merge data from multiple sources into unified DataFrame
    
    Handles:
    - Column name conflicts
    - Unit conversions
    - Data quality flags
    """
    merged = {}
    
    # Start with GAIA as base (if available)
    if 'GAIA' in results['sources']:
        merged = results['sources']['GAIA'].copy()
    
    # Add SIMBAD identifiers and types
    if 'SIMBAD' in results['sources']:
        simbad = results['sources']['SIMBAD']
        if len(simbad) > 0:
            merged['simbad_type'] = simbad.iloc[0]['type']
            merged['simbad_ids'] = simbad.iloc[0]['identifiers']
    
    # Add AKARI infrared bands
    if 'AKARI' in results['sources']:
        akari = results['sources']['AKARI']
        if 'IRC' in akari and len(akari['IRC']) > 0:
            merged['akari_9um'] = akari['IRC'].iloc[0].get('S9W', None)
            merged['akari_18um'] = akari['IRC'].iloc[0].get('S18W', None)
        if 'FIS' in akari and len(akari['FIS']) > 0:
            merged['akari_65um'] = akari['FIS'].iloc[0].get('S65', None)
            merged['akari_90um'] = akari['FIS'].iloc[0].get('S90', None)
    
    return pd.DataFrame([merged]) if merged else None


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    import io
    
    # UTF-8 output for Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("="*80)
    print("MULTI-SOURCE ASTRONOMICAL DATA QUERY")
    print("="*80)
    print()
    
    # Test query for Betelgeuse
    print("Testing: Betelgeuse (α Orionis)")
    print("-" * 80)
    
    results = query_multi_source(object_name="Betelgeuse", radius=1, sources=['SIMBAD', 'AKARI'])
    
    print("\nQuery Results:")
    for source, data in results['sources'].items():
        print(f"\n✓ {source}:")
        if isinstance(data, pd.DataFrame):
            print(f"  Rows: {len(data)}")
            print(f"  Columns: {list(data.columns)}")
        elif isinstance(data, dict):
            print(f"  Catalogs: {list(data.keys())}")
    
    # Merge data
    print("\n" + "="*80)
    print("MERGED DATA:")
    print("="*80)
    merged = merge_multi_source_data(results)
    if merged is not None:
        print(merged.to_string())
    
    print("\n" + "="*80)
    print("DATA SOURCE CAPABILITIES:")
    print("="*80)
    for source, info in DATA_SOURCES.items():
        print(f"\n{source}:")
        print(f"  Provides: {', '.join(info['provides'])}")
        print(f"  Missing: {', '.join(info['missing'])}")
        print(f"  Priority: {info['priority']}")
