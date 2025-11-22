#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coordinate Converter - Multi-Format Support
===========================================
Kompatibel mit: Stellarium, Aladin, SIMBAD, VO-Tools, etc.

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import re
import numpy as np

# ============================================================================
# COORDINATE FORMAT PARSERS
# ============================================================================

def parse_sexagesimal_ra(ra_string):
    """
    Parse RA in sexagesimal format (HH:MM:SS or HH MM SS)
    
    Examples:
    - "12:30:45.5" → 187.689583°
    - "12h30m45.5s" → 187.689583°
    - "12 30 45.5" → 187.689583°
    """
    # Clean and normalize
    ra_str = str(ra_string).strip()
    
    # Remove h/m/s markers
    ra_str = ra_str.replace('h', ':').replace('m', ':').replace('s', '')
    
    # Split by : or space
    parts = re.split('[: ]', ra_str)
    parts = [p.strip() for p in parts if p.strip()]
    
    if len(parts) < 1:
        raise ValueError(f"Invalid RA format: {ra_string}")
    
    # Convert to decimal degrees
    hours = float(parts[0])
    minutes = float(parts[1]) if len(parts) > 1 else 0
    seconds = float(parts[2]) if len(parts) > 2 else 0
    
    # RA: 1 hour = 15 degrees
    ra_deg = (hours + minutes/60 + seconds/3600) * 15
    
    return ra_deg

def parse_sexagesimal_dec(dec_string):
    """
    Parse Dec in sexagesimal format (±DD:MM:SS or ±DD MM SS)
    
    Examples:
    - "+45:30:20" → +45.505556°
    - "-12:30:45.5" → -12.512639°
    - "-12d30m45.5s" → -12.512639°
    """
    # Clean and normalize
    dec_str = str(dec_string).strip()
    
    # Extract sign
    sign = -1 if dec_str.startswith('-') else 1
    dec_str = dec_str.lstrip('+-')
    
    # Remove d/m/s markers
    dec_str = dec_str.replace('d', ':').replace('m', ':').replace('s', '').replace('°', ':')
    
    # Split by : or space
    parts = re.split('[: ]', dec_str)
    parts = [p.strip() for p in parts if p.strip()]
    
    if len(parts) < 1:
        raise ValueError(f"Invalid Dec format: {dec_string}")
    
    # Convert to decimal degrees
    degrees = float(parts[0])
    arcmin = float(parts[1]) if len(parts) > 1 else 0
    arcsec = float(parts[2]) if len(parts) > 2 else 0
    
    dec_deg = sign * (degrees + arcmin/60 + arcsec/3600)
    
    return dec_deg

def parse_galactic_coords(l, b):
    """
    Convert Galactic coordinates (l, b) to Equatorial (RA, Dec)
    
    Uses simple spherical transformation.
    """
    # Galactic North Pole (J2000)
    ra_ngp = 192.85948  # deg
    dec_ngp = 27.12825  # deg
    l_ncp = 122.93192   # deg
    
    # Convert to radians
    l_rad = np.radians(float(l))
    b_rad = np.radians(float(b))
    ra_ngp_rad = np.radians(ra_ngp)
    dec_ngp_rad = np.radians(dec_ngp)
    l_ncp_rad = np.radians(l_ncp)
    
    # Transformation
    sin_dec = np.cos(b_rad) * np.cos(dec_ngp_rad) * np.sin(l_rad - l_ncp_rad) + np.sin(b_rad) * np.sin(dec_ngp_rad)
    dec = np.arcsin(sin_dec)
    
    cos_ra_diff = (np.cos(b_rad) * np.cos(l_rad - l_ncp_rad)) / np.cos(dec)
    sin_ra_diff = (np.cos(b_rad) * np.sin(dec_ngp_rad) * np.sin(l_rad - l_ncp_rad) - 
                   np.sin(b_rad) * np.cos(dec_ngp_rad)) / np.cos(dec)
    
    ra_diff = np.arctan2(sin_ra_diff, cos_ra_diff)
    ra = ra_ngp_rad + ra_diff
    
    # Convert to degrees
    ra_deg = np.degrees(ra) % 360
    dec_deg = np.degrees(dec)
    
    return ra_deg, dec_deg

def smart_coordinate_parser(coord_input):
    """
    Intelligenter Parser für verschiedene Koordinaten-Formate
    
    Unterstützt:
    - Decimal degrees: "266.4, -29.0"
    - Sexagesimal: "17:45:40.04, -29:00:28.1"
    - J2000: "J174540.04-290028.1"
    - Galactic: "l=359.94, b=-1.06" oder "G359.94-1.06"
    - Object names: "Sgr A*", "M31", etc. (via name_resolver)
    """
    coord_str = str(coord_input).strip()
    
    # Try decimal degrees first (simplest)
    if ',' in coord_str and not any(c in coord_str for c in [':', 'h', 'm', 's', 'd']):
        try:
            parts = coord_str.split(',')
            ra = float(parts[0].strip())
            dec = float(parts[1].strip())
            return ra, dec, "decimal"
        except:
            pass
    
    # Try sexagesimal format (HH:MM:SS, DD:MM:SS)
    if ':' in coord_str or any(c in coord_str for c in ['h', 'm', 's']):
        try:
            if ',' in coord_str:
                parts = coord_str.split(',')
                ra = parse_sexagesimal_ra(parts[0].strip())
                dec = parse_sexagesimal_dec(parts[1].strip())
                return ra, dec, "sexagesimal"
            else:
                # Single string: split by space
                parts = coord_str.split()
                if len(parts) >= 6:  # HH MM SS DD MM SS
                    ra_parts = ' '.join(parts[:3])
                    dec_parts = ' '.join(parts[3:6])
                    ra = parse_sexagesimal_ra(ra_parts)
                    dec = parse_sexagesimal_dec(dec_parts)
                    return ra, dec, "sexagesimal"
        except Exception as e:
            print(f"Sexagesimal parse failed: {e}")
    
    # Try J2000 format (JHHMMSS.ss±DDMMSS.s)
    j2000_match = re.match(r'J?(\d{2})(\d{2})(\d{2}\.?\d*)([+-])(\d{2})(\d{2})(\d{2}\.?\d*)', coord_str.replace(' ', ''))
    if j2000_match:
        try:
            hh, mm, ss, sign, dd, am, ase = j2000_match.groups()
            ra = parse_sexagesimal_ra(f"{hh}:{mm}:{ss}")
            dec = parse_sexagesimal_dec(f"{sign}{dd}:{am}:{ase}")
            return ra, dec, "j2000"
        except:
            pass
    
    # Try Galactic coordinates (l=..., b=... or G...±...)
    if 'l=' in coord_str.lower() and 'b=' in coord_str.lower():
        try:
            l_match = re.search(r'l\s*=\s*([+-]?\d+\.?\d*)', coord_str, re.IGNORECASE)
            b_match = re.search(r'b\s*=\s*([+-]?\d+\.?\d*)', coord_str, re.IGNORECASE)
            if l_match and b_match:
                l = float(l_match.group(1))
                b = float(b_match.group(1))
                ra, dec = parse_galactic_coords(l, b)
                return ra, dec, "galactic"
        except:
            pass
    
    # Try G-format (G359.94-1.06)
    g_match = re.match(r'G(\d+\.?\d*)([+-]\d+\.?\d*)', coord_str.replace(' ', ''))
    if g_match:
        try:
            l, b = g_match.groups()
            ra, dec = parse_galactic_coords(float(l), float(b))
            return ra, dec, "galactic"
        except:
            pass
    
    # If all else fails, try as object name
    try:
        from name_resolver import resolve_name
        result = resolve_name(coord_str)
        if result:
            return result['ra'], result['dec'], "object_name"
    except:
        pass
    
    raise ValueError(f"Could not parse coordinate format: {coord_input}")

# ============================================================================
# COORDINATE FORMAT CONVERTERS (OUTPUT)
# ============================================================================

def to_sexagesimal(ra_deg, dec_deg):
    """Convert decimal degrees to sexagesimal format"""
    # RA to HH:MM:SS
    ra_hours = ra_deg / 15.0
    ra_h = int(ra_hours)
    ra_m = int((ra_hours - ra_h) * 60)
    ra_s = ((ra_hours - ra_h) * 60 - ra_m) * 60
    
    # Dec to DD:MM:SS
    dec_sign = '-' if dec_deg < 0 else '+'
    dec_abs = abs(dec_deg)
    dec_d = int(dec_abs)
    dec_m = int((dec_abs - dec_d) * 60)
    dec_s = ((dec_abs - dec_d) * 60 - dec_m) * 60
    
    ra_str = f"{ra_h:02d}:{ra_m:02d}:{ra_s:06.3f}"
    dec_str = f"{dec_sign}{dec_d:02d}:{dec_m:02d}:{dec_s:06.3f}"
    
    return ra_str, dec_str

def to_j2000(ra_deg, dec_deg):
    """Convert to J2000 format (JHHMMSS.ss±DDMMSS.s)"""
    ra_str, dec_str = to_sexagesimal(ra_deg, dec_deg)
    
    # Remove colons and format
    ra_j = 'J' + ra_str.replace(':', '')
    dec_j = dec_str.replace(':', '')
    
    return ra_j + dec_j

def to_galactic(ra_deg, dec_deg):
    """Convert Equatorial to Galactic coordinates"""
    # Galactic North Pole (J2000)
    ra_ngp = 192.85948
    dec_ngp = 27.12825
    l_ncp = 122.93192
    
    # Convert to radians
    ra_rad = np.radians(ra_deg)
    dec_rad = np.radians(dec_deg)
    ra_ngp_rad = np.radians(ra_ngp)
    dec_ngp_rad = np.radians(dec_ngp)
    l_ncp_rad = np.radians(l_ncp)
    
    # Transformation
    sin_b = (np.sin(dec_rad) * np.sin(dec_ngp_rad) + 
             np.cos(dec_rad) * np.cos(dec_ngp_rad) * np.cos(ra_rad - ra_ngp_rad))
    b = np.arcsin(sin_b)
    
    cos_l_diff = (np.cos(dec_rad) * np.sin(ra_rad - ra_ngp_rad)) / np.cos(b)
    sin_l_diff = (np.sin(dec_rad) * np.cos(dec_ngp_rad) - 
                  np.cos(dec_rad) * np.sin(dec_ngp_rad) * np.cos(ra_rad - ra_ngp_rad)) / np.cos(b)
    
    l_diff = np.arctan2(cos_l_diff, sin_l_diff)
    l = (l_ncp_rad - l_diff) % (2 * np.pi)
    
    l_deg = np.degrees(l)
    b_deg = np.degrees(b)
    
    return l_deg, b_deg

# ============================================================================
# EXPORT FORMATS
# ============================================================================

def format_for_stellarium(ra_deg, dec_deg, name="Target"):
    """Format for Stellarium bookmarks"""
    ra_str, dec_str = to_sexagesimal(ra_deg, dec_deg)
    return f"{name}\t{ra_str}\t{dec_str}"

def format_for_aladin(ra_deg, dec_deg):
    """Format for Aladin/CDS"""
    return f"{ra_deg:.6f} {dec_deg:.6f}"

def format_for_simbad(ra_deg, dec_deg):
    """Format for SIMBAD query"""
    ra_str, dec_str = to_sexagesimal(ra_deg, dec_deg)
    return f"{ra_str} {dec_str}"

def format_for_vo_cone(ra_deg, dec_deg, radius_arcmin=10):
    """Format for VO Cone Search"""
    return f"RA={ra_deg:.6f}&DEC={dec_deg:.6f}&SR={radius_arcmin/60:.4f}"


if __name__ == "__main__":
    # UTF-8 for Windows
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    # Tests
    print("Testing Coordinate Converter...")
    
    # Test 1: Decimal
    ra, dec, fmt = smart_coordinate_parser("266.4, -29.0")
    print(f"[OK] Decimal: {ra:.2f}, {dec:.2f} ({fmt})")
    
    # Test 2: Sexagesimal
    ra, dec, fmt = smart_coordinate_parser("17:45:40, -29:00:28")
    print(f"[OK] Sexagesimal: {ra:.2f}, {dec:.2f} ({fmt})")
    
    # Test 3: J2000
    ra, dec, fmt = smart_coordinate_parser("J174540.04-290028.1")
    print(f"[OK] J2000: {ra:.2f}, {dec:.2f} ({fmt})")
    
    # Test 4: Galactic
    ra, dec, fmt = smart_coordinate_parser("l=359.94, b=-1.06")
    print(f"[OK] Galactic: {ra:.2f}, {dec:.2f} ({fmt})")
    
    # Test 5: Convert back
    ra_sex, dec_sex = to_sexagesimal(266.4, -29.0)
    print(f"[OK] To Sexagesimal: {ra_sex}, {dec_sex}")
    
    l, b = to_galactic(266.4, -29.0)
    print(f"[OK] To Galactic: l={l:.2f}, b={b:.2f}")
    
    print("\n[SUCCESS] All formats working!")
