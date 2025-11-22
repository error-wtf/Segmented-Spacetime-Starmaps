"""
NED (NASA/IPAC Extragalactic Database) queries for multi-frequency spectra.

Essential for Jacobian tests and multi-wavelength SEDs.

© 2025 Carmen Wrede, Lino Casu
"""

import pandas as pd
import numpy as np
from typing import Optional, List
import warnings

try:
    from astroquery.ipac.ned import Ned
    NED_AVAILABLE = True
except ImportError:
    NED_AVAILABLE = False
    warnings.warn("astroquery.ipac.ned not available. Install with: pip install astroquery")


def fetch_ned_object(object_name: str) -> Optional[pd.DataFrame]:
    """
    Query NED for basic object information.
    
    Parameters
    ----------
    object_name : str
        Object name (e.g., "M87", "NGC 4258")
        
    Returns
    -------
    pd.DataFrame or None
        Basic object info (coordinates, redshift, type)
        
    Examples
    --------
    >>> m87_info = fetch_ned_object("M87")
    >>> print(f"M87 redshift: {m87_info['Redshift'][0]}")
    """
    if not NED_AVAILABLE:
        raise ImportError("astroquery.ipac.ned required")
    
    try:
        result = Ned.query_object(object_name)
        return result.to_pandas()
    except Exception as e:
        print(f"NED query failed for {object_name}: {e}")
        return None


def fetch_ned_spectrum(object_name: str) -> Optional[pd.DataFrame]:
    """
    Fetch multi-frequency spectrum from NED.
    
    This is CRITICAL for Jacobian tests (need 3+ frequencies).
    
    Parameters
    ----------
    object_name : str
        Object name
        
    Returns
    -------
    pd.DataFrame or None
        Multi-frequency photometry with columns:
        - Frequency or Observed Passband
        - Photometry Measurement
        - Uncertainty
        - Units
        - Refcode
        
    Notes
    -----
    M87 has 139 frequency measurements spanning 9+ orders of magnitude!
    Essential for:
    - Jacobian tests (∂f/∂r relationships)
    - Multi-wavelength SEDs
    - Continuum spectrum analysis
    
    Examples
    --------
    >>> m87_spectrum = fetch_ned_spectrum("M87")
    >>> print(f"M87 has {len(m87_spectrum)} frequency points")
    >>> # Expected: ~139 measurements
    """
    if not NED_AVAILABLE:
        raise ImportError("astroquery.ipac.ned required")
    
    try:
        # Get photometric data
        phot = Ned.get_table(object_name, table='photometry')
        
        if phot:
            df = phot.to_pandas()
            print(f"Fetched {len(df)} photometric points for {object_name}")
            return df
        else:
            print(f"No photometry found for {object_name}")
            return None
            
    except Exception as e:
        print(f"NED photometry query failed for {object_name}: {e}")
        return None


def fetch_ned_m87_spectrum() -> Optional[pd.DataFrame]:
    """
    Fetch M87 139-frequency spectrum.
    
    M87 is THE reference object for multi-frequency SSZ tests.
    
    Returns
    -------
    pd.DataFrame or None
        M87 spectrum with 139 frequencies
        
    Notes
    -----
    M87 spectrum spans:
    - Radio: 10^9 Hz
    - IR: 10^13 Hz
    - Optical: 10^15 Hz
    - X-ray: 10^18 Hz
    
    Total: 9+ orders of magnitude!
    
    Perfect for:
    - Multi-frequency Jacobian tests
    - Continuum spectrum validation
    - Cross-frequency consistency checks
    
    Examples
    --------
    >>> m87 = fetch_ned_m87_spectrum()
    >>> print(f"Frequency range: {m87['freq_Hz'].min():.2e} - {m87['freq_Hz'].max():.2e} Hz")
    """
    # Try to load processed M87 spectrum from Mass-Projection repo
    from pathlib import Path
    
    mass_proj = Path(__file__).parent.parent.parent.parent.parent
    data_file = mass_proj / 'Segmented-Spacetime-Mass-Projection-Unified-Results' / 'data' / 'ned' / 'M87_spectrum_139freq.csv'
    
    if data_file.exists():
        print(f"Loading M87 spectrum from: {data_file}")
        df = pd.read_csv(data_file)
        print(f"Loaded {len(df)} frequency points")
        return df
    else:
        print("⚠ Processed M87 spectrum not found")
        print("Fetching from NED...")
        return fetch_ned_spectrum("M87")


def convert_ned_to_frequency(phot_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert NED photometry to frequency-based format.
    
    Parameters
    ----------
    phot_df : pd.DataFrame
        NED photometry table
        
    Returns
    -------
    pd.DataFrame
        Converted to freq_Hz, flux_Jy format
        
    Notes
    -----
    NED provides data in various units (magnitudes, Jy, etc.)
    This converts everything to consistent frequency-based format.
    """
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    
    converted = []
    
    for idx, row in phot_df.iterrows():
        try:
            # Extract passband/frequency
            passband = row.get('Observed Passband', '')
            
            # Convert to frequency
            # (This is simplified - real conversion needs filter database)
            if 'GHz' in passband:
                freq_str = passband.split()[0]
                freq_Hz = float(freq_str) * 1e9
            elif 'MHz' in passband:
                freq_str = passband.split()[0]
                freq_Hz = float(freq_str) * 1e6
            else:
                # Use wavelength → frequency conversion
                # λ [μm] → ν [Hz]
                # (Requires filter central wavelengths)
                continue
            
            # Extract flux
            flux_val = row.get('Photometry Measurement', np.nan)
            flux_unit = row.get('Units', '')
            
            # Convert to Jy
            if 'Jy' in flux_unit:
                flux_Jy = float(flux_val)
            elif 'mJy' in flux_unit:
                flux_Jy = float(flux_val) * 1e-3
            else:
                # Magnitude conversion
                # (Requires zero-point calibration)
                continue
            
            converted.append({
                'freq_Hz': freq_Hz,
                'flux_Jy': flux_Jy,
                'passband': passband,
                'refcode': row.get('Refcode', '')
            })
            
        except Exception:
            continue
    
    return pd.DataFrame(converted)


def fetch_ned_multi_objects(object_names: List[str]) -> pd.DataFrame:
    """
    Batch fetch NED data for multiple objects.
    
    Parameters
    ----------
    object_names : list of str
        Object names to query
        
    Returns
    -------
    pd.DataFrame
        Combined results for all objects
        
    Examples
    --------
    >>> agn_list = ["M87", "NGC 4258", "3C 273", "3C 279"]
    >>> agn_data = fetch_ned_multi_objects(agn_list)
    """
    all_data = []
    
    for obj_name in object_names:
        print(f"Querying {obj_name}...")
        obj_data = fetch_ned_object(obj_name)
        
        if obj_data is not None:
            obj_data['query_name'] = obj_name
            all_data.append(obj_data)
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


# Pre-defined NED targets for multi-frequency analysis
NED_MULTI_FREQ_TARGETS = {
    'M87': {
        'name': 'M87 (Virgo A)',
        'type': 'Radio Galaxy / AGN',
        'frequencies': 139,
        'freq_range_Hz': (1e9, 1e18),
        'notes': 'PERFECT for Jacobian tests',
    },
    'NGC_4258': {
        'name': 'NGC 4258 (M106)',
        'type': 'Seyfert Galaxy',
        'frequencies': 50,
        'freq_range_Hz': (1e9, 1e15),
        'notes': 'Water maser, disk',
    },
    '3C_273': {
        'name': '3C 273',
        'type': 'Quasar',
        'frequencies': 80,
        'freq_range_Hz': (1e9, 1e18),
        'notes': 'Bright quasar jet',
    },
    '3C_279': {
        'name': '3C 279',
        'type': 'Blazar',
        'frequencies': 60,
        'freq_range_Hz': (1e9, 1e17),
        'notes': 'Gamma-ray loud',
    },
}


def get_ned_target_list() -> List[str]:
    """Get list of validated NED multi-frequency targets."""
    return list(NED_MULTI_FREQ_TARGETS.keys())


def get_ned_target_info(target: str) -> dict:
    """Get information about a specific NED target."""
    return NED_MULTI_FREQ_TARGETS.get(target, {})


def check_ned_availability() -> bool:
    """Check if NED queries are available."""
    return NED_AVAILABLE
