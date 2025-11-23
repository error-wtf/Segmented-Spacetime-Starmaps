#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Catalog Fetcher - ESO/ALMA, AKARI, NED, 2MASS, WISE, SIMBAD

Fills gaps in GAIA data with additional catalogs for:
- Star forming regions (ALMA)
- Infrared sources (AKARI, WISE)
- Galaxies/AGN (NED)
- General catalog cross-match (SIMBAD)

© 2025 Carmen Wrede, Lino Casu
"""
import os
import sys
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

import pandas as pd
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.alma import Alma
from astroquery.ipac.ned import Ned
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
import warnings
warnings.filterwarnings('ignore')

def fetch_alma_sources(ra, dec, radius_arcmin=30):
    """
    Fetch ALMA/ESO sources (star forming regions, molecular clouds).
    
    Args:
        ra, dec: Center coordinates (degrees)
        radius_arcmin: Search radius (arcminutes)
    """
    print(f"[ALMA] Querying ra={ra:.2f}, dec={dec:.2f}, radius={radius_arcmin}'...")
    
    try:
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # Query ALMA archive
        result = Alma.query_region(coord, radius=radius_arcmin*u.arcmin)
        
        if result is None or len(result) == 0:
            print(f"  [X] No ALMA sources found")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = result.to_pandas()
        df['catalog'] = 'ALMA'
        df['object_type'] = 'Radio Source'
        
        print(f"  [OK] Found {len(df)} ALMA sources")
        return df
        
    except Exception as e:
        print(f"  [X] ALMA query failed: {e}")
        return pd.DataFrame()


def fetch_akari_sources(ra, dec, radius_arcmin=30):
    """
    Fetch AKARI infrared sources.
    
    Args:
        ra, dec: Center coordinates (degrees)
        radius_arcmin: Search radius (arcminutes)
    """
    print(f"[AKARI] Querying ra={ra:.2f}, dec={dec:.2f}, radius={radius_arcmin}'...")
    
    try:
        # AKARI catalogs in VizieR
        catalogs = [
            'II/297',  # AKARI/IRC Point Source Catalogue
            'II/298',  # AKARI/FIS Bright Source Catalogue
        ]
        
        v = Vizier(columns=['*'], row_limit=1000)
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        all_sources = []
        for cat in catalogs:
            try:
                result = v.query_region(coord, radius=radius_arcmin*u.arcmin, catalog=cat)
                if result:
                    for table in result:
                        df = table.to_pandas()
                        df['catalog'] = f'AKARI_{cat.replace("/", "_")}'
                        df['object_type'] = 'Infrared Source'
                        all_sources.append(df)
            except:
                pass
        
        if all_sources:
            combined = pd.concat(all_sources, ignore_index=True)
            print(f"  [OK] Found {len(combined)} AKARI sources")
            return combined
        else:
            print(f"  [X] No AKARI sources found")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"  [X] AKARI query failed: {e}")
        return pd.DataFrame()


def fetch_ned_sources(ra, dec, radius_arcmin=30):
    """
    Fetch NED (NASA Extragalactic Database) sources.
    
    Args:
        ra, dec: Center coordinates (degrees)
        radius_arcmin: Search radius (arcminutes)
    """
    print(f"[NED] Querying ra={ra:.2f}, dec={dec:.2f}, radius={radius_arcmin}'...")
    
    try:
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # Query NED
        result = Ned.query_region(coord, radius=radius_arcmin*u.arcmin)
        
        if result is None or len(result) == 0:
            print(f"  [X] No NED sources found")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = result.to_pandas()
        df['catalog'] = 'NED'
        
        print(f"  [OK] Found {len(df)} NED sources")
        return df
        
    except Exception as e:
        print(f"  [X] NED query failed: {e}")
        return pd.DataFrame()


def fetch_2mass_sources(ra, dec, radius_arcmin=30):
    """
    Fetch 2MASS near-infrared sources.
    
    Args:
        ra, dec: Center coordinates (degrees)
        radius_arcmin: Search radius (arcminutes)
    """
    print(f"[2MASS] Querying ra={ra:.2f}, dec={dec:.2f}, radius={radius_arcmin}'...")
    
    try:
        v = Vizier(columns=['*'], row_limit=1000, catalog='II/246')  # 2MASS Point Source Catalog
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        result = v.query_region(coord, radius=radius_arcmin*u.arcmin)
        
        if not result:
            print(f"  [X] No 2MASS sources found")
            return pd.DataFrame()
        
        df = result[0].to_pandas()
        df['catalog'] = '2MASS'
        df['object_type'] = 'Near-IR Source'
        
        print(f"  [OK] Found {len(df)} 2MASS sources")
        return df
        
    except Exception as e:
        print(f"  [X] 2MASS query failed: {e}")
        return pd.DataFrame()


def fetch_wise_sources(ra, dec, radius_arcmin=30):
    """
    Fetch WISE mid-infrared sources.
    
    Args:
        ra, dec: Center coordinates (degrees)
        radius_arcmin: Search radius (arcminutes)
    """
    print(f"[WISE] Querying ra={ra:.2f}, dec={dec:.2f}, radius={radius_arcmin}'...")
    
    try:
        v = Vizier(columns=['*'], row_limit=1000, catalog='II/328')  # AllWISE Source Catalog
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        result = v.query_region(coord, radius=radius_arcmin*u.arcmin)
        
        if not result:
            print(f"  [X] No WISE sources found")
            return pd.DataFrame()
        
        df = result[0].to_pandas()
        df['catalog'] = 'WISE'
        df['object_type'] = 'Mid-IR Source'
        
        print(f"  [OK] Found {len(df)} WISE sources")
        return df
        
    except Exception as e:
        print(f"  [X] WISE query failed: {e}")
        return pd.DataFrame()


def fetch_simbad_region(ra, dec, radius_arcmin=30):
    """
    Fetch SIMBAD sources (comprehensive cross-match).
    
    Args:
        ra, dec: Center coordinates (degrees)
        radius_arcmin: Search radius (arcminutes)
    """
    print(f"[SIMBAD] Querying ra={ra:.2f}, dec={dec:.2f}, radius={radius_arcmin}'...")
    
    try:
        # Custom SIMBAD query with more fields
        custom_simbad = Simbad()
        custom_simbad.add_votable_fields('otype', 'ra', 'dec', 'pmra', 'pmdec', 'rv_value', 'plx', 'distance')
        
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        result = custom_simbad.query_region(coord, radius=radius_arcmin*u.arcmin)
        
        if result is None or len(result) == 0:
            print(f"  [X] No SIMBAD sources found")
            return pd.DataFrame()
        
        df = result.to_pandas()
        df['catalog'] = 'SIMBAD'
        
        print(f"  [OK] Found {len(df)} SIMBAD sources")
        return df
        
    except Exception as e:
        print(f"  [X] SIMBAD query failed: {e}")
        return pd.DataFrame()


def fetch_all_catalogs(ra, dec, radius_arcmin=30):
    """
    Fetch from ALL catalogs and merge.
    
    Args:
        ra, dec: Center coordinates (degrees)
        radius_arcmin: Search radius (arcminutes)
        
    Returns:
        Combined DataFrame with all sources
    """
    print("="*80)
    print(f"MULTI-CATALOG QUERY: RA={ra:.4f}°, Dec={dec:.4f}°, Radius={radius_arcmin}'")
    print("="*80)
    
    all_sources = []
    
    # Query each catalog
    for fetch_func in [
        fetch_alma_sources,
        fetch_akari_sources,
        fetch_ned_sources,
        fetch_2mass_sources,
        fetch_wise_sources,
        fetch_simbad_region
    ]:
        try:
            df = fetch_func(ra, dec, radius_arcmin)
            if not df.empty:
                all_sources.append(df)
        except Exception as e:
            print(f"  [X] {fetch_func.__name__} failed: {e}")
    
    if not all_sources:
        print("\n[X] No sources found in any catalog")
        return pd.DataFrame()
    
    # Combine all sources
    combined = pd.concat(all_sources, ignore_index=True, sort=False)
    
    print("\n" + "="*80)
    print(f"[OK] TOTAL: {len(combined)} sources from {len(all_sources)} catalogs")
    print("="*80)
    
    return combined


if __name__ == "__main__":
    # Test regions
    test_regions = [
        ("G79 Cygnus", 266.4, -29.0, 30),
        ("Cygnus X", 308.0, 41.0, 60),
        ("Sgr A*", 266.417, -29.008, 30),
    ]
    
    for name, ra, dec, radius in test_regions:
        print(f"\n{'='*80}")
        print(f"REGION: {name}")
        print(f"{'='*80}\n")
        
        result = fetch_all_catalogs(ra, dec, radius)
        
        if not result.empty:
            output_file = f"multi_catalog_{name.replace(' ', '_').lower()}.csv"
            result.to_csv(output_file, index=False)
            print(f"\n[OK] Saved to: {output_file}")
            print(f"  Columns: {list(result.columns[:10])}...")
        
        print("\n")
