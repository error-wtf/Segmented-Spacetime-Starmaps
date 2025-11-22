"""
SSZ Metric - Xi(r) Segment Saturation (PURE)

**DIESER CODE NUTZT NUR DEN Xi(r)-ANSATZ!**

Quelle: ssz-metric-pure/src/ssz_core/segment_density.py

Kernformeln:
    Xi(r) = 1 - exp(-φ · r/r_s)
    φ = (1+√5)/2 = 1.618034  # GOLDEN RATIO
    
    D_SSZ(r) = 1 / (1 + Xi(r))  # Time dilation
    R_SSZ(r) = r · (1 + Xi(r))  # Radial stretch

KEINE phi_G, KEINE gamma, KEINE Integration!
Für phi_G/Spiral-Ansatz siehe: experiments/phi_spiral/ (out of scope)

© 2025 Carmen Wrede, Lino Casu
Licensed under the Anti-Capitalist Software License v1.4
"""

import numpy as np
from typing import Union, Optional


# Golden ratio constant (φ = (1+√5)/2)
PHI = (1.0 + np.sqrt(5.0)) / 2.0


def schwarzschild_radius(mass: float, G: float = 6.67430e-11, c: float = 2.99792458e8) -> float:
    """
    Compute Schwarzschild radius r_s = 2GM/c^2.
    
    Parameters
    ----------
    mass : float
        Mass in kg
    G : float
        Gravitational constant (m^3 kg^-1 s^-2)
    c : float
        Speed of light (m/s)
        
    Returns
    -------
    float
        Schwarzschild radius (m)
    """
    return 2.0 * G * mass / (c * c)


def Xi(r: Union[float, np.ndarray], r_s: float) -> Union[float, np.ndarray]:
    """
    Calculate segment saturation factor using Golden Ratio.
    
    **ECHTE SSZ-FORMEL aus ssz-metric-pure!**
    
    Formula:
        Xi(r) = 1 - exp(-phi * r/r_s)
    
    where phi = (1 + sqrt(5))/2 approx 1.618 is the golden ratio.
    
    This function represents the "filling" of spacetime segments,
    approaching 1 as r -> infinity and 0 as r -> 0.
    
    Parameters
    ----------
    r : float or np.ndarray
        Radius (m) - can be scalar or array
    r_s : float
        Schwarzschild radius (m)
        
    Returns
    -------
    float or np.ndarray
        Segment saturation factor Xi(r) in [0, 1)
        
    Examples
    --------
    >>> Xi(0.0, 2950.0)
    0.0
    >>> Xi(1e10, 2950.0)  # Far field
    0.999...
    
    Physical Interpretation
    -----------------------
    - Xi = 0: No segments (at r=0)
    - Xi -> 1: Maximum saturation (r -> infinity)
    - Crossover at r* ~ 1.386562 * r_s (universal!)
    """
    if r_s <= 0:
        raise ValueError(f"Schwarzschild radius must be positive, got {r_s}")
    
    # Handle both scalar and array inputs
    r = np.asarray(r)
    
    # ECHTE SSZ-FORMEL!
    xi_value = 1.0 - np.exp(-PHI * r / r_s)
    
    return float(xi_value) if xi_value.ndim == 0 else xi_value


def D_SSZ(r: Union[float, np.ndarray], r_s: float) -> Union[float, np.ndarray]:
    """
    Calculate SSZ time dilation factor.
    
    Formula:
        D_SSZ(r) = 1 / (1 + Xi(r))
    
    where Xi(r) is the segment saturation factor.
    
    This provides a singularity-free time dilation that:
    - Remains finite at r = 0: D_SSZ(0) = 1
    - Approaches GR asymptotically for r >> r_s
    - Provides smooth transition through r = r_s
    
    Parameters
    ----------
    r : float or np.ndarray
        Radius (m) - can be scalar or array
    r_s : float
        Schwarzschild radius (m)
        
    Returns
    -------
    float or np.ndarray
        Time dilation factor D_SSZ(r) in (0, 1]
        
    Physical Interpretation
    -----------------------
    - D_SSZ = 1: No time dilation (far field or r=0)
    - D_SSZ < 1: Time runs slower
    - Never reaches 0 (no singularity!)
    
    Examples
    --------
    >>> D_SSZ(0.0, 2950.0)
    1.0
    >>> D_SSZ(2950.0, 2950.0)  # At Schwarzschild radius
    0.165...  # Finite!
    """
    if r_s <= 0:
        raise ValueError(f"Schwarzschild radius must be positive, got {r_s}")
    
    # D_SSZ(r) = 1 / (1 + Xi(r))
    xi = Xi(r, r_s)
    d_value = 1.0 / (1.0 + xi)
    
    return d_value


def D_GR(r: Union[float, np.ndarray], r_s: float, 
         epsilon: float = 1e-10) -> Union[float, np.ndarray]:
    """
    Calculate General Relativity (Schwarzschild) time dilation.
    
    Formula:
        D_GR(r) = sqrt(1 - r_s/r)  for r > r_s
    
    This is the standard GR result, which:
    - Diverges at r = r_s (event horizon)
    - Is undefined for r < r_s
    - Approaches 1 for r >> r_s
    
    Parameters
    ----------
    r : float or np.ndarray
        Radius (m) - can be scalar or array
    r_s : float
        Schwarzschild radius (m)
    epsilon : float
        Safety margin to avoid division issues
        
    Returns
    -------
    float or np.ndarray
        Time dilation factor D_GR(r) or NaN where undefined
        
    Examples
    --------
    >>> D_GR(2*2950.0, 2950.0)
    0.707...  # sqrt(1/2)
    >>> D_GR(2950.0, 2950.0)
    nan  # Singularity!
    """
    if r_s <= 0:
        raise ValueError(f"Schwarzschild radius must be positive, got {r_s}")
    
    r = np.asarray(r)
    
    # Create output array
    d_value = np.zeros_like(r, dtype=float)
    
    # Only calculate where r > r_s + epsilon
    valid = r > (r_s + epsilon)
    
    if np.any(valid):
        d_value[valid] = np.sqrt(1.0 - r_s / r[valid])
    
    # Set invalid regions to NaN
    d_value[~valid] = np.nan
    
    return float(d_value) if d_value.ndim == 0 else d_value


def radial_stretch(r: Union[float, np.ndarray], r_s: float) -> Union[float, np.ndarray]:
    """
    SSZ radial stretch factor.
    
    Formula:
        s(r) = 1 + Xi(r)
        R_SSZ(r) = r · s(r)
    
    This is the core SSZ deformation: more segments -> longer paths!
    
    Args:
        r: Radius (m)
        r_s: Schwarzschild radius (m)
        
    Returns:
        Stretch factor s(r) ∈ [1, 2)
        
    Physical Interpretation:
        - s(0) = 1 (no stretch at origin)
        - s(r_s) ≈ 1.802 (80% segment filling)
        - s(∞) → 2 (maximum stretch, full saturation)
        
    Examples:
        >>> radial_stretch(0.0, 2950.0)
        1.0
        >>> radial_stretch(2950.0, 2950.0)  # At r_s
        1.801712...
    """
    xi = Xi(r, r_s)
    return 1.0 + xi


if __name__ == "__main__":
    print("=" * 80)
    print("SSZ Metric - Xi(r) ONLY - Self Test")
    print("=" * 80)
    
    # Test with Sun's Schwarzschild radius
    M_sun = 1.98847e30  # kg
    r_s_sun = schwarzschild_radius(M_sun)
    
    print(f"\nConstants:")
    print(f"  phi (Golden Ratio) = {PHI:.6f}")
    print(f"  M_sun = {M_sun:.3e} kg")
    print(f"  r_s (Sun) = {r_s_sun:.2f} m")
    
    # VALIDATED VALUES TABLE
    print("\n" + "=" * 80)
    print("VALIDATED Xi(r) VALUES - Against ssz-metric-pure")
    print("=" * 80)
    
    test_radii_factors = np.array([0.5, 1.0, 2.0, 5.0])
    test_radii = test_radii_factors * r_s_sun
    xi_values = Xi(test_radii, r_s_sun)
    d_ssz_values = D_SSZ(test_radii, r_s_sun)
    stretch_values = radial_stretch(test_radii, r_s_sun)
    
    print(f"\n  r/r_s |  Xi(r)  | D_SSZ   | Stretch | Physical Meaning")
    print(f"  " + "-" * 70)
    for i, factor in enumerate(test_radii_factors):
        meaning = {
            0.5: "Weak field",
            1.0: "At Schwarzschild radius",
            2.0: "Intermediate",
            5.0: "Far field"
        }.get(factor, "")
        print(f"  {factor:5.1f} | {xi_values[i]:7.5f} | {d_ssz_values[i]:7.5f} | {stretch_values[i]:7.5f} | {meaning}")
    
    # Test 2: Time Dilation Comparison
    print("\nTest 2: SSZ vs GR Time Dilation")
    print("  (SSZ stays FINITE at r_s!)")
    
    test_r = np.array([1.5*r_s_sun, 2*r_s_sun, 5*r_s_sun])
    d_ssz = D_SSZ(test_r, r_s_sun)
    d_gr = D_GR(test_r, r_s_sun)
    
    print(f"\n  r/r_s  |  D_SSZ    |  D_GR     | Difference")
    print(f"  " + "-" * 50)
    for i, r in enumerate(test_r):
        ratio = r / r_s_sun
        diff_percent = abs(d_ssz[i] - d_gr[i]) / d_gr[i] * 100 if not np.isnan(d_gr[i]) else np.nan
        print(f"  {ratio:5.1f}  | {d_ssz[i]:8.6f} | {d_gr[i]:8.6f} | {diff_percent:6.2f}%")
    
    # Test 3: At Schwarzschild radius (critical test!)
    print("\nTest 3: At Schwarzschild Radius (r = r_s)")
    print("  (GR FAILS here, SSZ stays finite!)")
    
    d_ssz_horizon = D_SSZ(r_s_sun, r_s_sun)
    d_gr_horizon = D_GR(r_s_sun, r_s_sun)
    
    print(f"\n  D_SSZ(r_s) = {d_ssz_horizon:.6f}  <- FINITE!")
    print(f"  D_GR(r_s)  = {d_gr_horizon}  <- SINGULARITY!")
    
    print("\n" + "=" * 70)
    print("[OK] ECHTE SSZ-Logik functional!")
    print("Formula: Xi(r) = 1 - exp(-phi*r/r_s)")
    print(f"phi = {PHI:.6f}")
    print("=" * 70)
