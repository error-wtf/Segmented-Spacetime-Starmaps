"""
Sky projection and SSZ metric deformations.

**Xi(r)-ANSATZ ONLY!**

This module handles:
- Gnomonic projection (RA/Dec → x,y)
- SSZ deformation using Xi(r) = 1 - exp(-φ·r_s / r)

KEINE phi_G, KEINE gamma, KEINE Integration!

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import warnings
from typing import Tuple, Optional
try:
    from .ssz_metric import Xi, radial_stretch, PHI, schwarzschild_radius
    SSZ_METRIC_AVAILABLE = True
except ImportError:
    SSZ_METRIC_AVAILABLE = False
    PHI = (1.0 + np.sqrt(5.0)) / 2.0  # fallback


def gnomonic_projection(
    ra: np.ndarray,
    dec: np.ndarray,
    center_ra: float = 0.0,
    center_dec: float = 0.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Project celestial coordinates onto a tangent plane (gnomonic projection).
    
    This is a simple tangent-plane projection commonly used for small
    fields of view. For large sky areas, consider other projections.
    
    Parameters
    ----------
    ra : np.ndarray
        Right Ascension values (degrees)
    dec : np.ndarray
        Declination values (degrees)
    center_ra : float, optional
        RA of projection center (degrees)
    center_dec : float, optional
        Dec of projection center (degrees)
        
    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        (x, y) coordinates in projection plane (degrees)
        
    Notes
    -----
    Simplified gnomonic projection:
        x = (RA - RA_center) * cos(Dec_center)
        y = Dec - Dec_center
    
    This is valid for small angular separations from the center.
    For full spherical geometry, use astropy.wcs or similar.
    """
    ra = np.asarray(ra)
    dec = np.asarray(dec)
    
    # Convert to radians for trig
    dec_rad = np.deg2rad(dec)
    center_dec_rad = np.deg2rad(center_dec)
    
    # Simple tangent plane
    x = (ra - center_ra) * np.cos(center_dec_rad)
    y = dec - center_dec
    
    return x, y


def apply_ssz_deformation(
    x: np.ndarray,
    y: np.ndarray,
    eps: float = 0.1,
    mode: str = 'radial'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply SSZ-like anisotropic deformation to projected coordinates.
    
    .. deprecated:: 0.2.0
        **LEGACY FUNCTION! KEINE ECHTE SSZ-PHYSIK!**
        Use :func:`apply_ssz_metric_deformation` instead for ECHTE SSZ-Logik
        basierend auf Xi(r) = 1 - exp(-phi*r_s / r).
        
        This function uses ARBITRARY eps-scaling, NOT the real SSZ metric!
    
    **WARNUNG**: Dies ist ein vereinfachter Stub nur für Demos!
    NICHT für wissenschaftliche Arbeit verwenden!
    
    Für ECHTE SSZ-Physik nutze:
        >>> from ssz_starmaps import apply_ssz_metric_deformation
        >>> x_ssz, y_ssz = apply_ssz_metric_deformation(x, y, mass_kg=1.98847e30)
    
    Parameters
    ----------
    x, y : np.ndarray
        Projected sky coordinates
    eps : float
        Deformation strength parameter
    mode : str, optional
        Deformation mode:
        - 'radial': anisotropic radial scaling
        - 'shear': simple xy shear
        
    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        (x', y') deformed coordinates
        
    Notes
    -----
    Current implementation:
    - mode='radial': 
        x' = x * (1 + eps * r/r_max)
        y' = y * (1 - eps * r/r_max)
      where r = sqrt(x² + y²)
      
    - mode='shear':
        x' = x + eps * y
        y' = y
    
    In full SSZ theory, this would involve:
        g_ij = φ^(α·N) * δ_ij  (isotropic)
    or anisotropic variants with directional scaling.
    """
    # Issue deprecation warning
    warnings.warn(
        "apply_ssz_deformation() is LEGACY and uses FAKE eps-scaling! "
        "Use apply_ssz_metric_deformation() for ECHTE SSZ-Physik "
        "based on Xi(r) = 1 - exp(-phi*r_s / r).",
        DeprecationWarning,
        stacklevel=2
    )
    
    x = np.asarray(x)
    y = np.asarray(y)
    
    if mode == 'radial':
        # Radial distance
        r = np.sqrt(x**2 + y**2)
        r_max = np.max(r) if np.max(r) > 0 else 1.0
        
        # Radial deformation factor
        f = eps * r / r_max
        
        # Anisotropic scaling
        x_deformed = x * (1.0 + f)
        y_deformed = y * (1.0 - f)
        
    elif mode == 'shear':
        # Simple shear deformation
        x_deformed = x + eps * y
        y_deformed = y.copy()
        
    else:
        raise ValueError(f"Unknown mode: {mode}")
    
    return x_deformed, y_deformed


def compute_deformation_field(
    x: np.ndarray,
    y: np.ndarray,
    eps: float = 0.1
) -> dict:
    """
    Compute deformation field statistics for visualization.
    
    Parameters
    ----------
    x, y : np.ndarray
        Original coordinates
    eps : float
        Deformation parameter
        
    Returns
    -------
    dict
        Statistics about the deformation:
        - 'displacement': array of displacement magnitudes
        - 'mean_displacement': average displacement
        - 'max_displacement': maximum displacement
        - 'rms_displacement': RMS displacement
    """
    x_def, y_def = apply_ssz_deformation(x, y, eps=eps)
    
    dx = x_def - x
    dy = y_def - y
    
    displacement = np.sqrt(dx**2 + dy**2)
    
    return {
        'displacement': displacement,
        'mean_displacement': np.mean(displacement),
        'max_displacement': np.max(displacement),
        'rms_displacement': np.sqrt(np.mean(displacement**2))
    }


def apply_ssz_metric_deformation(
    x: np.ndarray,
    y: np.ndarray,
    mass_kg: float = 1.98847e30,  # Sun's mass
    r_scale_deg: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply SSZ deformation using Xi(r)-approach.
    
    Formula:
        Xi(r) = 1 - exp(-φ · r_s / r), φ = Golden Ratio
        R_SSZ(r) = r · (1 + Xi(r))
    
    NO integration, NO gamma, NO phi_G - Pure Xi(r) stretch!
    
    Parameters
    ----------
    x, y : np.ndarray
        Projected coordinates (degrees)
    mass_kg : float
        Central mass (kg), default: Sun
    r_scale_deg : float
        Scale factor (coordinate units → r_s)
        
    Returns
    -------
    (x_ssz, y_ssz) : tuple[np.ndarray, np.ndarray]
        SSZ-deformed coordinates
        
    Examples
    --------
    >>> x_ssz, y_ssz = apply_ssz_metric_deformation(x, y)
    """
    if not SSZ_METRIC_AVAILABLE:
        print("WARNING: SSZ metric not available!")
        return x, y  # Return unmodified
    
    x = np.asarray(x)
    y = np.asarray(y)
    
    # Polar coordinates
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    
    # Schwarzschild radius
    r_s = schwarzschild_radius(mass_kg)
    
    # Physical radius
    r_physical = r * r_scale_deg * r_s
    
    # SSZ stretch factor: s(r) = 1 + Xi(r)
    stretch = radial_stretch(r_physical, r_s)
    R_ssz = r * stretch
    
    # Back to Cartesian
    x_deformed = R_ssz * np.cos(theta)
    y_deformed = R_ssz * np.sin(theta)
    
    return x_deformed, y_deformed


if __name__ == "__main__":
    print("=" * 70)
    print("SSZ Projection Module - Self Test")
    print("=" * 70)
    
    # Test 1: Gnomonic projection
    print("\nTest 1: Gnomonic Projection")
    ra_test = np.array([0, 1, 2, 3])
    dec_test = np.array([0, 0.5, -0.5, 1])
    
    x, y = gnomonic_projection(ra_test, dec_test, center_ra=0, center_dec=0)
    
    print(f"  Input RA:  {ra_test}")
    print(f"  Input Dec: {dec_test}")
    print(f"  Output x:  {x}")
    print(f"  Output y:  {y}")
    
    # Test 2: SSZ deformation
    print("\nTest 2: SSZ Radial Deformation (eps=0.1)")
    x_grid = np.linspace(-5, 5, 5)
    y_grid = np.linspace(-5, 5, 5)
    
    x_def, y_def = apply_ssz_deformation(x_grid, y_grid, eps=0.1, mode='radial')
    
    print(f"  Original x: {x_grid}")
    print(f"  Deformed x: {x_def}")
    print(f"  Original y: {y_grid}")
    print(f"  Deformed y: {y_def}")
    
    # Test 3: Deformation statistics
    print("\nTest 3: Deformation Field Statistics")
    stats = compute_deformation_field(x_grid, y_grid, eps=0.2)
    
    print(f"  Mean displacement: {stats['mean_displacement']:.4f}°")
    print(f"  Max displacement:  {stats['max_displacement']:.4f}°")
    print(f"  RMS displacement:  {stats['rms_displacement']:.4f}°")
    
    # Test 4: ECHTE SSZ Metric Deformation
    if SSZ_METRIC_AVAILABLE:
        print("\nTest 4: ECHTE SSZ Metric Deformation")
        print("  (Xi(r) = 1 - exp(-phi*r_s / r), R_ssz = r*(1+Xi))")
        
        # Test grid around Sun
        x_test = np.array([0.0, 1.0, 2.0, 3.0])
        y_test = np.array([0.0, 0.0, 0.0, 0.0])
        
        x_ssz, y_ssz = apply_ssz_metric_deformation(
            x_test, y_test,
            mass_kg=1.98847e30,  # Sun's mass
            r_scale_deg=1.0  # Assume x,y in units of r_s
        )
        
        print(f"  Original x: {x_test}")
        print(f"  SSZ x:      {x_ssz}")
        
        # Compute stretch factors
        stretch = np.zeros_like(x_test)
        for i in range(len(x_test)):
            if x_test[i] > 0:
                stretch[i] = x_ssz[i] / x_test[i]
        print(f"  Stretch:    {stretch}")
        print(f"  phi = {PHI:.6f}")
    else:
        print("\nTest 4: SSZ Metric module not available")
    
    print("\n" + "=" * 70)
    if SSZ_METRIC_AVAILABLE:
        print("[OK] ECHTE SSZ metric integration functional!")
        print("Formula: Xi(r) = 1 - exp(-phi*r_s / r)")
    else:
        print("NOTE: Using placeholder implementation.")
        print("Install ssz_metric.py for ECHTE SSZ-Logik.")
    print("=" * 70)
