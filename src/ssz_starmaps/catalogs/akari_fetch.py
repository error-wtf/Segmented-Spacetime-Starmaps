"""
AKARI Infrared data queries.

AKARI provides diffuse IR emission maps (2-160 μm) essential for
nebula studies and temperature/density structure analysis.

© 2025 Carmen Wrede, Lino Casu
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Tuple
from pathlib import Path
import warnings

try:
    from astropy.io import fits
    from astropy.wcs import WCS
    ASTROPY_AVAILABLE = True
except ImportError:
    ASTROPY_AVAILABLE = False
    warnings.warn("astropy required for AKARI FITS files")


# AKARI band information
AKARI_BANDS = {
    'N60': {'wavelength_um': 65, 'fwhm_um': 21, 'description': 'Mid-IR'},
    'WIDE-S': {'wavelength_um': 90, 'fwhm_um': 37, 'description': 'Far-IR wide'},
    'WIDE-L': {'wavelength_um': 140, 'fwhm_um': 50, 'description': 'Far-IR long'},
    'N160': {'wavelength_um': 160, 'fwhm_um': 34, 'description': 'Far-IR'},
}


def fetch_akari_diffuse_map(
    region: str,
    band: str = 'N60',
    data_dir: Optional[Path] = None
) -> Optional[Tuple[np.ndarray, WCS]]:
    """
    Fetch AKARI diffuse emission map for a region.
    
    Parameters
    ----------
    region : str
        Region name (e.g., 'G79.29+0.46', 'CygnusX')
    band : str
        AKARI band (N60, WIDE-S, WIDE-L, N160)
    data_dir : Path, optional
        Directory containing AKARI FITS files
        
    Returns
    -------
    tuple or None
        (image_data, WCS) if found, else None
        
    Notes
    -----
    AKARI All-Sky Survey provides:
    - Diffuse Galactic emission
    - Temperature/density maps
    - PDR/molecular zone structure
    
    Critical for nebula studies like G79.29+0.46 (CygnusX).
    
    Examples
    --------
    >>> data, wcs = fetch_akari_diffuse_map('G79.29+0.46', 'N60')
    >>> if data is not None:
    ...     plot_temperature_map(data, wcs)
    """
    if not ASTROPY_AVAILABLE:
        raise ImportError("astropy required for AKARI FITS files")
    
    if band not in AKARI_BANDS:
        raise ValueError(f"Unknown band {band}. Use: {list(AKARI_BANDS.keys())}")
    
    # Try local AKARI data first
    if data_dir is None:
        # Check Mass-Projection repo
        mass_proj = Path(__file__).parent.parent.parent.parent.parent
        data_dir = mass_proj / 'Segmented-Spacetime-Mass-Projection-Unified-Results' / 'data' / 'akari'
    
    # AKARI file naming convention
    # Example: AKARI_G79_N60_diffuse.fits
    region_clean = region.replace('+', 'p').replace('-', 'm').replace('.', '')
    fits_file = data_dir / f'AKARI_{region_clean}_{band}_diffuse.fits'
    
    if fits_file.exists():
        print(f"Loading AKARI {band} map: {fits_file}")
        
        with fits.open(fits_file) as hdul:
            data = hdul[0].data
            header = hdul[0].header
            wcs = WCS(header)
            
            print(f"  Shape: {data.shape}")
            print(f"  Band: {band} ({AKARI_BANDS[band]['wavelength_um']} μm)")
            
            return data, wcs
    else:
        print(f"⚠ AKARI data not found: {fits_file}")
        print(f"Consider downloading from:")
        print(f"  - AKARI Archive: https://www.ir.isas.jaxa.jp/AKARI/Archive/")
        print(f"  - Or use included papers in Mass-Projection repo")
        return None


def extract_temperature_map(
    data_65um: np.ndarray,
    data_90um: np.ndarray,
    dust_emissivity: float = 2.0
) -> np.ndarray:
    """
    Derive dust temperature from AKARI dual-band photometry.
    
    Parameters
    ----------
    data_65um : ndarray
        65 μm intensity map
    data_90um : ndarray
        90 μm intensity map
    dust_emissivity : float
        Dust emissivity index β (default: 2.0)
        
    Returns
    -------
    ndarray
        Temperature map [K]
        
    Notes
    -----
    Uses modified blackbody fit:
    I_ν ∝ B_ν(T) × ν^β
    
    Temperature derived from intensity ratio:
    T ∝ (I_65/I_90)^(1/β) × constant
    
    Examples
    --------
    >>> data_65, _ = fetch_akari_diffuse_map('G79.29+0.46', 'N60')
    >>> data_90, _ = fetch_akari_diffuse_map('G79.29+0.46', 'WIDE-S')
    >>> temp_map = extract_temperature_map(data_65, data_90)
    >>> print(f"Temp range: {temp_map.min():.1f} - {temp_map.max():.1f} K")
    """
    # Wavelengths
    lambda_1 = 65e-6  # m
    lambda_2 = 90e-6  # m
    
    # Avoid division by zero
    ratio = np.divide(
        data_65,
        data_90,
        out=np.zeros_like(data_65),
        where=data_90 > 0
    )
    
    # Temperature from ratio (simplified)
    # Full derivation: see Etxaluze et al. 2009 (AKARI diffuse maps paper)
    c = 2.998e8  # m/s
    h = 6.626e-34  # J·s
    k_B = 1.381e-23  # J/K
    
    # Approximate temperature
    T = (h * c / k_B) * (1/lambda_1 - 1/lambda_2) / np.log(
        ratio * (lambda_2/lambda_1)**(3 + dust_emissivity)
    )
    
    # Filter unrealistic values
    T = np.clip(T, 10, 1000)  # Typical range: 10-1000 K
    
    return T


def fetch_akari_g79_data() -> Optional[pd.DataFrame]:
    """
    Fetch AKARI data for G79.29+0.46 (CygnusX region).
    
    This is a well-studied LBV nebula with AKARI diffuse maps.
    
    Returns
    -------
    pd.DataFrame or None
        Table with AKARI photometry if available
        
    Notes
    -----
    G79.29+0.46 observations:
    - AKARI N60, WIDE-S, WIDE-L, N160
    - Complemented by Spitzer and Herschel
    - Temperature: 20-40 K (cold dust shell)
    - Morphology: Circular shell ~4.5 pc diameter
    
    References:
    - Etxaluze et al. 2009 (AKARI diffuse maps)
    - Di Francesco et al. (Ammonia observations)
    
    Examples
    --------
    >>> g79_data = fetch_akari_g79_data()
    >>> if g79_data is not None:
    ...     print(g79_data[['band', 'flux_Jy', 'T_dust_K']])
    """
    # Check for processed AKARI photometry
    mass_proj = Path(__file__).parent.parent.parent.parent.parent
    data_file = mass_proj / 'Segmented-Spacetime-Mass-Projection-Unified-Results' / 'data' / 'akari' / 'G79_photometry.csv'
    
    if data_file.exists():
        print(f"Loading G79.29+0.46 AKARI data: {data_file}")
        return pd.read_csv(data_file)
    else:
        print("⚠ G79 AKARI data not found")
        print("Manual extraction from papers:")
        print("  - papers/The_AKARI_diffuse_maps.pdf")
        print("  - papers/Ammonia_observations_in_the_LBV_nebula_G7929046_Di.pdf")
        return None


def fetch_akari_cygnus_diamond_ring() -> Optional[pd.DataFrame]:
    """
    Fetch AKARI data for Diamond Ring in Cygnus X.
    
    Returns
    -------
    pd.DataFrame or None
        Diamond Ring photometry if available
        
    Notes
    -----
    The Diamond Ring is an advanced HII region in Cygnus X
    studied extensively with AKARI.
    
    References:
    - The_Diamond_Ring_in_Cygnus_X_Advanced_stage_of_an_.pdf
    - The_AKARI_diffuse_maps.pdf
    """
    mass_proj = Path(__file__).parent.parent.parent.parent.parent
    data_file = mass_proj / 'Segmented-Spacetime-Mass-Projection-Unified-Results' / 'data' / 'akari' / 'CygnusX_DiamondRing.csv'
    
    if data_file.exists():
        print(f"Loading Diamond Ring AKARI data: {data_file}")
        return pd.read_csv(data_file)
    else:
        print("⚠ Diamond Ring AKARI data not found")
        print("Extract from paper:")
        print("  - papers/The_Diamond_Ring_in_Cygnus_X_Advanced_stage_of_an_.pdf")
        return None


# Pre-defined AKARI regions
AKARI_REGIONS = {
    'G79.29+0.46': {
        'name': 'LBV nebula in CygnusX',
        'coordinates': (305.21, 0.46),  # Galactic l, b
        'distance_kpc': 1.7,
        'diameter_pc': 4.5,
        'bands': ['N60', 'WIDE-S', 'WIDE-L', 'N160'],
        'papers': [
            'The_AKARI_diffuse_maps.pdf',
            'Ammonia_observations_in_the_LBV_nebula_G7929046_Di.pdf'
        ]
    },
    'CygnusX_DiamondRing': {
        'name': 'Diamond Ring HII region',
        'coordinates': (310.0, 0.0),  # Approximate
        'distance_kpc': 1.4,
        'bands': ['N60', 'WIDE-S', 'N160'],
        'papers': [
            'The_Diamond_Ring_in_Cygnus_X_Advanced_stage_of_an_.pdf',
            'The_AKARI_diffuse_maps.pdf'
        ]
    },
}


def get_akari_region_list() -> List[str]:
    """Get list of available AKARI regions."""
    return list(AKARI_REGIONS.keys())


def get_akari_region_info(region: str) -> dict:
    """Get information about a specific AKARI region."""
    return AKARI_REGIONS.get(region, {})


def get_akari_band_info(band: str) -> dict:
    """Get information about a specific AKARI band."""
    return AKARI_BANDS.get(band, {})
