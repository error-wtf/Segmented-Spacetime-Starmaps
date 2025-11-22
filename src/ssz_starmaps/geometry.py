"""
Ellipse geometry and Ramanujan approximations for SSZ StarMaps.

This module provides utilities for computing ellipse circumferences
using Ramanujan's approximation, which is essential for modeling
deformed circular orbits in Segmented Spacetime.

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np


def ramanujan_ellipse_circumference(a: float, b: float) -> float:
    """
    Compute ellipse circumference using Ramanujan's approximation.
    
    Ramanujan's formula (first approximation):
    C ≈ π * [3(a+b) - √((3a+b)(a+3b))]
    
    This is accurate to within 0.01% for all ellipses.
    
    Parameters
    ----------
    a : float
        Semi-major axis length
    b : float
        Semi-minor axis length
        
    Returns
    -------
    float
        Approximate circumference of the ellipse
        
    Notes
    -----
    In SSZ theory, circular orbits in Minkowski space become ellipses
    due to anisotropic segment density fields. The proper circumference
    is computed using this formula.
    
    References
    ----------
    Ramanujan, S. (1914). "Modular Equations and Approximations to π"
    """
    a = float(a)
    b = float(b)
    
    # Ensure a >= b (swap if necessary)
    if b > a:
        a, b = b, a
    
    # Ramanujan's first approximation
    term1 = 3 * (a + b)
    term2 = np.sqrt((3*a + b) * (a + 3*b))
    
    circumference = np.pi * (term1 - term2)
    
    return circumference


def deform_circle_to_ellipse(r: float, eps: float) -> tuple[float, float]:
    """
    Deform a circle of radius r into an ellipse via anisotropic scaling.
    
    In SSZ theory, the segment density field N(x) creates anisotropic
    metric components, effectively stretching circles into ellipses.
    
    Parameters
    ----------
    r : float
        Original circle radius (Minkowski)
    eps : float
        Deformation parameter (typically |eps| << 1)
        Positive eps stretches along major axis
        
    Returns
    -------
    tuple[float, float]
        (a, b) - semi-major and semi-minor axes
        
    Notes
    -----
    Simple linear model:
        a = r * (1 + eps)
        b = r * (1 - eps)
    
    For small eps, this preserves area approximately (πab ≈ πr²).
    In full SSZ theory, eps would be determined by the local
    segment density gradient and φ-scaling.
    """
    a = r * (1.0 + eps)
    b = r * (1.0 - eps)
    
    return (a, b)


def compute_circumference_ratio(r: float, eps: float) -> dict:
    """
    Compute the ratio of SSZ ellipse circumference to Minkowski circle.
    
    Parameters
    ----------
    r : float
        Circle radius
    eps : float
        Deformation parameter
        
    Returns
    -------
    dict
        Dictionary with keys:
        - 'C_minkowski': Circle circumference (2πr)
        - 'C_ssz': Ellipse circumference (Ramanujan)
        - 'a': Semi-major axis
        - 'b': Semi-minor axis
        - 'ratio': C_ssz / C_minkowski
        - 'deviation_percent': (ratio - 1) * 100
    """
    # Minkowski circle
    C_minkowski = 2 * np.pi * r
    
    # SSZ ellipse
    a, b = deform_circle_to_ellipse(r, eps)
    C_ssz = ramanujan_ellipse_circumference(a, b)
    
    ratio = C_ssz / C_minkowski
    deviation_percent = (ratio - 1.0) * 100.0
    
    return {
        'C_minkowski': C_minkowski,
        'C_ssz': C_ssz,
        'a': a,
        'b': b,
        'ratio': ratio,
        'deviation_percent': deviation_percent
    }


if __name__ == "__main__":
    # Quick self-test
    print("=" * 70)
    print("SSZ Ellipse Geometry - Self Test")
    print("=" * 70)
    
    # Test 1: Circle (eps=0) should give exact 2πr
    r = 1.0
    eps = 0.0
    a, b = deform_circle_to_ellipse(r, eps)
    C = ramanujan_ellipse_circumference(a, b)
    C_exact = 2 * np.pi * r
    
    print(f"\nTest 1: Circle (eps=0)")
    print(f"  r = {r}, eps = {eps}")
    print(f"  a = {a:.6f}, b = {b:.6f}")
    print(f"  Ramanujan C = {C:.10f}")
    print(f"  Exact 2*pi*r = {C_exact:.10f}")
    print(f"  Error       = {abs(C - C_exact):.2e}")
    
    # Test 2: Moderate deformation
    eps = 0.1
    result = compute_circumference_ratio(r, eps)
    
    print(f"\nTest 2: Deformed orbit (eps={eps})")
    print(f"  a = {result['a']:.6f}, b = {result['b']:.6f}")
    print(f"  C_Minkowski = {result['C_minkowski']:.6f}")
    print(f"  C_SSZ       = {result['C_ssz']:.6f}")
    print(f"  Ratio       = {result['ratio']:.6f}")
    print(f"  Deviation   = {result['deviation_percent']:+.3f}%")
    
    print("\n" + "=" * 70)
