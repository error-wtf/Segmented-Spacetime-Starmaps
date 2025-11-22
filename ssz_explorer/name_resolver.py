#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name Resolver - Resolve object names to coordinates

Supports aliases like:
- Sag A* / Sagittarius A* / Sgr A*
- Betelgeuse / α Ori / Alpha Orionis
- Proxima / Proxima Centauri

© 2025 Carmen Wrede, Lino Casu
"""

import os
import sys

# UTF-8 fix
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np

# Famous objects database
FAMOUS_OBJECTS = {
    # Galactic Center
    'sgr a*': {'name': 'Sgr A*', 'ra': 266.41683, 'dec': -29.00781, 'distance_ly': 26000, 'type': 'Black Hole'},
    'sag a*': {'name': 'Sgr A*', 'ra': 266.41683, 'dec': -29.00781, 'distance_ly': 26000, 'type': 'Black Hole'},
    'sagittarius a*': {'name': 'Sgr A*', 'ra': 266.41683, 'dec': -29.00781, 'distance_ly': 26000, 'type': 'Black Hole'},
    
    # Nearest Stars
    'proxima': {'name': 'Proxima Centauri', 'ra': 217.42894, 'dec': -62.67951, 'distance_ly': 4.24, 'type': 'Red Dwarf'},
    'proxima centauri': {'name': 'Proxima Centauri', 'ra': 217.42894, 'dec': -62.67951, 'distance_ly': 4.24, 'type': 'Red Dwarf'},
    'alpha centauri': {'name': 'α Centauri', 'ra': 219.90205, 'dec': -60.83399, 'distance_ly': 4.37, 'type': 'Binary'},
    
    # Bright Stars
    'betelgeuse': {'name': 'Betelgeuse', 'ra': 88.79293, 'dec': 7.40704, 'distance_ly': 642.5, 'type': 'Red Supergiant'},
    'α ori': {'name': 'Betelgeuse', 'ra': 88.79293, 'dec': 7.40704, 'distance_ly': 642.5, 'type': 'Red Supergiant'},
    'alpha orionis': {'name': 'Betelgeuse', 'ra': 88.79293, 'dec': 7.40704, 'distance_ly': 642.5, 'type': 'Red Supergiant'},
    
    'sirius': {'name': 'Sirius', 'ra': 101.28715, 'dec': -16.71314, 'distance_ly': 8.6, 'type': 'Binary'},
    'α cma': {'name': 'Sirius', 'ra': 101.28715, 'dec': -16.71314, 'distance_ly': 8.6, 'type': 'Binary'},
    
    'vega': {'name': 'Vega', 'ra': 279.23473, 'dec': 38.78369, 'distance_ly': 25.04, 'type': 'Main Sequence'},
    'α lyr': {'name': 'Vega', 'ra': 279.23473, 'dec': 38.78369, 'distance_ly': 25.04, 'type': 'Main Sequence'},
    
    'rigel': {'name': 'Rigel', 'ra': 78.63446, 'dec': -8.20164, 'distance_ly': 863, 'type': 'Blue Supergiant'},
    'β ori': {'name': 'Rigel', 'ra': 78.63446, 'dec': -8.20164, 'distance_ly': 863, 'type': 'Blue Supergiant'},
    
    # Galaxies
    'andromeda': {'name': 'M31 (Andromeda)', 'ra': 10.68471, 'dec': 41.26875, 'distance_ly': 2537000, 'type': 'Galaxy'},
    'm31': {'name': 'M31 (Andromeda)', 'ra': 10.68471, 'dec': 41.26875, 'distance_ly': 2537000, 'type': 'Galaxy'},
    
    'm33': {'name': 'M33 (Triangulum)', 'ra': 23.46204, 'dec': 30.66022, 'distance_ly': 2730000, 'type': 'Galaxy'},
    'triangulum': {'name': 'M33 (Triangulum)', 'ra': 23.46204, 'dec': 30.66022, 'distance_ly': 2730000, 'type': 'Galaxy'},
    
    'milky way': {'name': 'Milky Way Center', 'ra': 266.405, 'dec': -28.936, 'distance_ly': 26000, 'type': 'Galactic Center'},
    
    # Nebulae
    'orion nebula': {'name': 'M42 (Orion Nebula)', 'ra': 83.82208, 'dec': -5.39111, 'distance_ly': 1344, 'type': 'Nebula'},
    'm42': {'name': 'M42 (Orion Nebula)', 'ra': 83.82208, 'dec': -5.39111, 'distance_ly': 1344, 'type': 'Nebula'},
    
    'crab nebula': {'name': 'M1 (Crab Nebula)', 'ra': 83.63308, 'dec': 22.0145, 'distance_ly': 6500, 'type': 'Supernova Remnant'},
    'm1': {'name': 'M1 (Crab Nebula)', 'ra': 83.63308, 'dec': 22.0145, 'distance_ly': 6500, 'type': 'Supernova Remnant'},
    
    # Clusters
    'pleiades': {'name': 'M45 (Pleiades)', 'ra': 56.75, 'dec': 24.117, 'distance_ly': 444, 'type': 'Open Cluster'},
    'm45': {'name': 'M45 (Pleiades)', 'ra': 56.75, 'dec': 24.117, 'distance_ly': 444, 'type': 'Open Cluster'},
    
    # Additional famous objects
    'polaris': {'name': 'Polaris', 'ra': 37.95456, 'dec': 89.26411, 'distance_ly': 433, 'type': 'Supergiant'},
    'north star': {'name': 'Polaris', 'ra': 37.95456, 'dec': 89.26411, 'distance_ly': 433, 'type': 'Supergiant'},
    
    'canopus': {'name': 'Canopus', 'ra': 95.98795, 'dec': -52.69566, 'distance_ly': 310, 'type': 'Bright Giant'},
    'arcturus': {'name': 'Arcturus', 'ra': 213.91530, 'dec': 19.18241, 'distance_ly': 36.7, 'type': 'Red Giant'},
    'capella': {'name': 'Capella', 'ra': 79.17232, 'dec': 45.99799, 'distance_ly': 42.9, 'type': 'Binary'},
    
    # Exoplanet hosts
    '51 peg': {'name': '51 Pegasi', 'ra': 344.36658, 'dec': 20.76883, 'distance_ly': 50.9, 'type': 'Exoplanet Host'},
    'trappist-1': {'name': 'TRAPPIST-1', 'ra': 346.62200, 'dec': -5.04150, 'distance_ly': 39.6, 'type': 'Exoplanet Host'},
}


def resolve_name(name_query):
    """
    Resolve object name to coordinates.
    
    Args:
        name_query: String (e.g., "Sag A*", "Betelgeuse", "M31")
    
    Returns:
        dict or None: Object data with ra, dec, distance, etc.
    """
    if not name_query:
        return None
    
    # Normalize query
    query_lower = name_query.strip().lower()
    
    # Check famous objects first
    if query_lower in FAMOUS_OBJECTS:
        return FAMOUS_OBJECTS[query_lower]
    
    # Try SIMBAD if famous objects fail
    try:
        return query_simbad(name_query)
    except:
        return None


def query_simbad(name):
    """Query SIMBAD for object name."""
    try:
        from astroquery.simbad import Simbad
        
        # Query SIMBAD
        result_table = Simbad.query_object(name)
        
        if result_table is None:
            return None
        
        # Extract coordinates
        ra_str = result_table['RA'][0]
        dec_str = result_table['DEC'][0]
        
        # Convert to degrees
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        
        coord = SkyCoord(ra_str, dec_str, unit=(u.hourangle, u.deg))
        
        return {
            'name': name,
            'ra': coord.ra.deg,
            'dec': coord.dec.deg,
            'distance_ly': None,  # SIMBAD doesn't always have distance
            'type': 'SIMBAD Object'
        }
    except Exception as e:
        print(f"SIMBAD query failed: {e}")
        return None


def get_famous_objects_list():
    """Get list of all famous objects."""
    unique_objects = {}
    for alias, data in FAMOUS_OBJECTS.items():
        obj_name = data['name']
        if obj_name not in unique_objects:
            unique_objects[obj_name] = data
    
    return list(unique_objects.values())


def search_by_name_fuzzy(query):
    """Fuzzy search in famous objects."""
    query_lower = query.lower()
    matches = []
    
    for alias, data in FAMOUS_OBJECTS.items():
        if query_lower in alias or query_lower in data['name'].lower():
            if data['name'] not in [m['name'] for m in matches]:
                matches.append(data)
    
    return matches


if __name__ == "__main__":
    # Test
    print("Testing Name Resolver...")
    print()
    
    test_names = ["Sag A*", "Betelgeuse", "M31", "Proxima", "sgr a*", "andromeda"]
    
    for name in test_names:
        result = resolve_name(name)
        if result:
            print(f"✅ {name:20s} → {result['name']:20s} | RA: {result['ra']:.2f}° | Dec: {result['dec']:.2f}°")
        else:
            print(f"❌ {name:20s} → NOT FOUND")
    
    print()
    print(f"Total famous objects: {len(set(data['name'] for data in FAMOUS_OBJECTS.values()))}")
