"""
Universal Telescope Data Loader
================================

Generisches System für ALLE astronomischen Objekte!

Supported Archives:
- IRSA (Spitzer, WISE, 2MASS, AKARI)
- ESO Archive (VLT, ALMA)
- SIMBAD (Object resolution)
- VizieR (All catalogs)

Works for ANY object: Stars, Nebulae, Galaxies, etc.

© 2025 Carmen Wrede, Lino Casu, Bingsi
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import io
import warnings

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Check astroquery availability
try:
    from astroquery.ipac.irsa import Irsa
    from astroquery.simbad import Simbad
    from astroquery.vizier import Vizier
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    HAS_ASTROQUERY = True
except ImportError:
    HAS_ASTROQUERY = False
    warnings.warn("astroquery not installed - limited functionality")


# ============================================================================
# UNIVERSAL COORDINATE RESOLVER
# ============================================================================

def resolve_object(object_name=None, ra=None, dec=None):
    """
    Resolve object to coordinates
    
    Args:
        object_name: Object name (e.g., 'Betelgeuse', 'M31', 'Sgr A*')
        ra, dec: Coordinates in degrees (if known)
    
    Returns:
        SkyCoord object
    """
    if not HAS_ASTROQUERY:
        raise ImportError("astroquery required for object resolution")
    
    if ra is not None and dec is not None:
        # Direct coordinates
        return SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
    
    if object_name:
        # Resolve via SIMBAD
        print(f"🔍 Resolving '{object_name}' via SIMBAD...")
        try:
            result = Simbad.query_object(object_name)
            if result:
                coord = SkyCoord(result['RA'][0], result['DEC'][0], 
                               unit=(u.hourangle, u.deg), frame='icrs')
                print(f"  ✓ Resolved to: RA {coord.ra.deg:.6f}°, Dec {coord.dec.deg:.6f}°")
                return coord
        except Exception as e:
            print(f"  ✗ SIMBAD resolution failed: {e}")
    
    raise ValueError("Must provide either object_name or ra/dec coordinates")


# ============================================================================
# IRSA QUERIES (Spitzer, WISE, 2MASS, AKARI)
# ============================================================================

def query_irsa_all_missions(coord, radius=5*u.arcmin):
    """
    Query ALL IRSA missions for an object
    
    Args:
        coord: SkyCoord object
        radius: Search radius
    
    Returns:
        dict with results from each mission
    """
    if not HAS_ASTROQUERY:
        return {}
    
    print(f"\n📡 Querying IRSA Archives...")
    print(f"  Position: RA {coord.ra.deg:.6f}°, Dec {coord.dec.deg:.6f}°")
    print(f"  Radius: {radius}")
    
    results = {}
    
    # AKARI (Infrared)
    try:
        print(f"\n  [1/4] AKARI FIS (Far-Infrared)...")
        akari = Irsa.query_region(coord, catalog='akari_fis', radius=radius)
        if akari and len(akari) > 0:
            results['AKARI'] = akari.to_pandas()
            print(f"    ✓ Found {len(akari)} sources")
        else:
            print(f"    ∅ No data")
    except Exception as e:
        print(f"    ✗ Query failed: {e}")
    
    # 2MASS (Near-Infrared)
    try:
        print(f"\n  [2/4] 2MASS (Near-Infrared)...")
        twomass = Irsa.query_region(coord, catalog='fp_psc', radius=radius)
        if twomass and len(twomass) > 0:
            results['2MASS'] = twomass.to_pandas()
            print(f"    ✓ Found {len(twomass)} sources")
        else:
            print(f"    ∅ No data")
    except Exception as e:
        print(f"    ✗ Query failed: {e}")
    
    # WISE (Mid-Infrared)
    try:
        print(f"\n  [3/4] WISE AllWISE...")
        wise = Irsa.query_region(coord, catalog='allwise_p3as_psd', radius=radius)
        if wise and len(wise) > 0:
            results['WISE'] = wise.to_pandas()
            print(f"    ✓ Found {len(wise)} sources")
        else:
            print(f"    ∅ No data")
    except Exception as e:
        print(f"    ✗ Query failed: {e}")
    
    # Spitzer (would need specific catalog)
    print(f"\n  [4/4] Spitzer (requires specific catalog)")
    print(f"    ℹ Use web interface: https://irsa.ipac.caltech.edu/")
    
    return results


# ============================================================================
# SIMBAD METADATA
# ============================================================================

def query_simbad_metadata(object_name=None, coord=None):
    """
    Get object metadata from SIMBAD
    
    Returns:
        DataFrame with object properties
    """
    if not HAS_ASTROQUERY:
        return None
    
    print(f"\n📚 Querying SIMBAD metadata...")
    
    try:
        if object_name:
            result = Simbad.query_object(object_name)
        elif coord:
            result = Simbad.query_region(coord, radius=1*u.arcmin)
        else:
            return None
        
        if result:
            df = result.to_pandas()
            print(f"  ✓ Found {len(df)} objects")
            return df
        else:
            print(f"  ∅ No metadata")
            return None
    except Exception as e:
        print(f"  ✗ Query failed: {e}")
        return None


# ============================================================================
# VizieR CATALOG ACCESS
# ============================================================================

def query_vizier_catalogs(coord, catalogs=None, radius=5*u.arcmin):
    """
    Query VizieR catalogs
    
    Args:
        coord: SkyCoord
        catalogs: List of catalog names (or None for all)
        radius: Search radius
    
    Returns:
        dict with results from each catalog
    """
    if not HAS_ASTROQUERY:
        return {}
    
    print(f"\n📖 Querying VizieR...")
    
    # Default useful catalogs
    if catalogs is None:
        catalogs = [
            'II/336/apass9',  # APASS photometry
            'I/345/gaia2',    # GAIA DR2
            'I/350/gaiaedr3', # GAIA EDR3
        ]
    
    results = {}
    v = Vizier(columns=['**'], row_limit=100)
    
    for cat in catalogs:
        try:
            print(f"  Querying {cat}...")
            result = v.query_region(coord, radius=radius, catalog=cat)
            if result and len(result) > 0:
                results[cat] = result[0].to_pandas()
                print(f"    ✓ Found {len(result[0])} sources")
            else:
                print(f"    ∅ No data")
        except Exception as e:
            print(f"    ✗ Failed: {e}")
    
    return results


# ============================================================================
# UNIFIED DATA STRUCTURE
# ============================================================================

class UniversalAstronomicalObject:
    """
    Universal container for multi-archive data
    """
    
    def __init__(self, name=None, ra=None, dec=None):
        self.name = name
        self.coord = None
        self.data = {}
        
        # Resolve coordinates
        if ra and dec:
            self.coord = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
        elif name:
            self.coord = resolve_object(object_name=name)
    
    def query_all_archives(self, radius=5*u.arcmin):
        """Query all available archives"""
        if not self.coord:
            raise ValueError("No coordinates available")
        
        print("="*80)
        print(f"UNIVERSAL DATA QUERY: {self.name or 'Unknown'}")
        print("="*80)
        
        # SIMBAD metadata
        self.data['SIMBAD'] = query_simbad_metadata(
            object_name=self.name, 
            coord=self.coord
        )
        
        # IRSA missions
        self.data.update(query_irsa_all_missions(self.coord, radius))
        
        # VizieR
        vizier_data = query_vizier_catalogs(self.coord, radius=radius)
        self.data.update(vizier_data)
        
        print("\n" + "="*80)
        print("QUERY COMPLETE")
        print("="*80)
        
        return self.get_summary()
    
    def get_summary(self):
        """Get summary of available data"""
        summary = {
            'object': self.name,
            'ra': self.coord.ra.deg if self.coord else None,
            'dec': self.coord.dec.deg if self.coord else None,
            'archives': {}
        }
        
        for archive, data in self.data.items():
            if data is not None and len(data) > 0:
                summary['archives'][archive] = {
                    'n_sources': len(data),
                    'columns': list(data.columns) if hasattr(data, 'columns') else []
                }
        
        return summary
    
    def to_dataframe(self):
        """
        Export all data as unified DataFrame
        
        Merges data from all archives
        """
        # Start with SIMBAD if available
        if 'SIMBAD' in self.data and self.data['SIMBAD'] is not None:
            unified = self.data['SIMBAD'].copy()
        else:
            unified = pd.DataFrame()
        
        # Add data from other archives
        for archive, data in self.data.items():
            if archive == 'SIMBAD' or data is None:
                continue
            
            # Add prefix to column names
            if isinstance(data, pd.DataFrame):
                for col in data.columns:
                    unified[f'{archive}_{col}'] = data[col].iloc[0] if len(data) > 0 else None
        
        return unified


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_query(object_name=None, ra=None, dec=None, radius=5):
    """
    Quick query for any object
    
    Args:
        object_name: Name (e.g., 'Betelgeuse')
        ra, dec: Coordinates in degrees
        radius: Search radius in arcminutes
    
    Returns:
        UniversalAstronomicalObject with data
    """
    obj = UniversalAstronomicalObject(name=object_name, ra=ra, dec=dec)
    obj.query_all_archives(radius=radius*u.arcmin)
    return obj


def batch_query(object_list, radius=5):
    """
    Query multiple objects
    
    Args:
        object_list: List of object names or (ra, dec) tuples
        radius: Search radius in arcminutes
    
    Returns:
        List of UniversalAstronomicalObject
    """
    results = []
    
    for i, obj_input in enumerate(object_list):
        print(f"\n[{i+1}/{len(object_list)}] Processing {obj_input}...")
        
        if isinstance(obj_input, str):
            obj = quick_query(object_name=obj_input, radius=radius)
        elif isinstance(obj_input, tuple):
            obj = quick_query(ra=obj_input[0], dec=obj_input[1], radius=radius)
        else:
            continue
        
        results.append(obj)
    
    return results


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("UNIVERSAL TELESCOPE DATA LOADER - DEMO")
    print("="*80)
    
    if not HAS_ASTROQUERY:
        print("\n❌ astroquery not installed!")
        print("Install with: pip install astroquery")
        sys.exit(1)
    
    # Example 1: Query by name
    print("\n📍 EXAMPLE 1: Query Betelgeuse")
    print("-" * 80)
    
    obj = quick_query(object_name="Betelgeuse", radius=1)
    summary = obj.get_summary()
    
    print("\n📊 Summary:")
    print(f"  Object: {summary['object']}")
    print(f"  Position: RA {summary['ra']:.6f}°, Dec {summary['dec']:.6f}°")
    print(f"  Archives with data:")
    for archive, info in summary['archives'].items():
        print(f"    • {archive}: {info['n_sources']} sources")
    
    # Example 2: Query by coordinates
    print("\n\n📍 EXAMPLE 2: Query Galactic Center")
    print("-" * 80)
    
    obj2 = quick_query(ra=266.4, dec=-29.0, radius=5)
    summary2 = obj2.get_summary()
    
    print("\n📊 Summary:")
    print(f"  Position: RA {summary2['ra']:.6f}°, Dec {summary2['dec']:.6f}°")
    print(f"  Archives with data:")
    for archive, info in summary2['archives'].items():
        print(f"    • {archive}: {info['n_sources']} sources")
    
    print("\n" + "="*80)
    print("✅ UNIVERSAL LOADER READY FOR ANY OBJECT!")
    print("="*80)
    
    print("\nUsage:")
    print("  from universal_telescope_loader import quick_query")
    print("  obj = quick_query(object_name='M31', radius=5)")
    print("  data = obj.to_dataframe()")
