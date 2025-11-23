#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name Database Builder - Build coordinate-to-name mapping from GAIA data

This script scans the star database and creates a reverse lookup
from coordinates to object names, using name_resolver.py

© 2025 Carmen Wrede, Lino Casu
"""
import pandas as pd
import numpy as np
from pathlib import Path
from name_resolver import FAMOUS_OBJECTS

def build_coordinate_name_map(tolerance_deg=0.1):
    """
    Build a dictionary mapping (RA, Dec) -> Name for quick lookup.
    
    Args:
        tolerance_deg: Coordinate matching tolerance in degrees
        
    Returns:
        dict: {(ra, dec): name} mapping
    """
    coord_map = {}
    
    # Add all famous objects to the map
    for alias, obj_data in FAMOUS_OBJECTS.items():
        ra = obj_data['ra']
        dec = obj_data['dec']
        name = obj_data['name']
        
        # Round coordinates for binning
        ra_bin = round(ra / tolerance_deg) * tolerance_deg
        dec_bin = round(dec / tolerance_deg) * tolerance_deg
        
        key = (ra_bin, dec_bin)
        
        # Store the most prominent name (avoid duplicates)
        if key not in coord_map or len(name) < len(coord_map[key]):
            coord_map[key] = name
    
    return coord_map


def find_name_for_coordinates(ra, dec, coord_map, tolerance_deg=0.1):
    """
    Find object name for given coordinates.
    
    Args:
        ra: Right Ascension in degrees
        dec: Declination in degrees
        coord_map: Prebuilt coordinate mapping
        tolerance_deg: Matching tolerance
        
    Returns:
        str or None: Object name if found
    """
    # Round to binning
    ra_bin = round(ra / tolerance_deg) * tolerance_deg
    dec_bin = round(dec / tolerance_deg) * tolerance_deg
    
    key = (ra_bin, dec_bin)
    
    return coord_map.get(key, None)


def add_names_to_database(df, coord_map=None, tolerance_deg=0.1):
    """
    Add 'common_name' column to star database DataFrame.
    
    Args:
        df: Star database DataFrame with 'ra' and 'dec' columns
        coord_map: Prebuilt coordinate map (or None to build new one)
        tolerance_deg: Matching tolerance
        
    Returns:
        DataFrame with added 'common_name' column
    """
    if coord_map is None:
        coord_map = build_coordinate_name_map(tolerance_deg)
    
    # Add names
    df['common_name'] = df.apply(
        lambda row: find_name_for_coordinates(row['ra'], row['dec'], coord_map, tolerance_deg),
        axis=1
    )
    
    return df


if __name__ == "__main__":
    print("="*80)
    print("NAME DATABASE BUILDER")
    print("="*80)
    
    # Build coordinate map
    print("\n[1/3] Building coordinate-to-name map...")
    coord_map = build_coordinate_name_map(tolerance_deg=0.1)
    print(f"✓ Created map with {len(coord_map)} coordinate bins")
    
    # Load star database
    print("\n[2/3] Loading star database...")
    db_path = Path(__file__).parent / 'ssz_data' / 'star_database_50k.csv'
    
    if db_path.exists():
        df = pd.read_csv(db_path)
        print(f"✓ Loaded {len(df):,} stars")
        
        # Add names
        print("\n[3/3] Adding common names...")
        df = add_names_to_database(df, coord_map)
        
        # Count named objects
        named_count = df['common_name'].notna().sum()
        print(f"✓ Found names for {named_count} objects ({named_count/len(df)*100:.2f}%)")
        
        # Show examples
        print("\n" + "="*80)
        print("EXAMPLES:")
        print("="*80)
        examples = df[df['common_name'].notna()].head(10)
        for idx, row in examples.iterrows():
            print(f"  • {row['common_name']:30s} | RA: {row['ra']:.2f}° | Dec: {row['dec']:.2f}°")
        
        # Save updated database
        output_path = db_path.parent / 'star_database_50k_with_names.csv'
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved to: {output_path}")
    else:
        print(f"✗ Database not found: {db_path}")
    
    print("\n" + "="*80)
    print("✓ DONE!")
    print("="*80)
