"""
Unit tests for geometry module.

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ssz_starmaps.geometry import (
    ramanujan_ellipse_circumference,
    deform_circle_to_ellipse,
    compute_circumference_ratio
)


def test_circle():
    """Test that a circle (a=b) gives 2πr."""
    r = 1.0
    C = ramanujan_ellipse_circumference(r, r)
    expected = 2 * np.pi * r
    
    assert np.abs(C - expected) < 1e-6, f"Circle test failed: {C} != {expected}"
    print("✓ Circle test passed")


def test_deformation_symmetry():
    """Test that deformation preserves approximate area."""
    r = 1.0
    eps = 0.1
    
    a, b = deform_circle_to_ellipse(r, eps)
    
    area_circle = np.pi * r**2
    area_ellipse = np.pi * a * b
    
    # Should be close for small eps
    rel_error = abs(area_ellipse - area_circle) / area_circle
    
    assert rel_error < 0.01, f"Area not preserved: {rel_error} > 1%"
    print(f"✓ Area preservation test passed (error: {rel_error:.4%})")


def test_positive_circumference():
    """Test that all circumferences are positive."""
    test_cases = [
        (1.0, 1.0),   # circle
        (2.0, 1.0),   # ellipse
        (1.0, 0.5),   # thin ellipse
        (10.0, 0.1),  # very thin ellipse
    ]
    
    for a, b in test_cases:
        C = ramanujan_ellipse_circumference(a, b)
        assert C > 0, f"Negative circumference for a={a}, b={b}"
    
    print("✓ Positive circumference test passed")


def test_ratio_computation():
    """Test the ratio computation function."""
    r = 1.0
    eps = 0.0
    
    result = compute_circumference_ratio(r, eps)
    
    assert 'C_minkowski' in result
    assert 'C_ssz' in result
    assert 'ratio' in result
    
    # For eps=0, ratio should be ~1.0
    assert abs(result['ratio'] - 1.0) < 1e-6
    
    print("✓ Ratio computation test passed")


if __name__ == "__main__":
    print("=" * 60)
    print("Running SSZ Geometry Tests")
    print("=" * 60)
    
    test_circle()
    test_deformation_symmetry()
    test_positive_circumference()
    test_ratio_computation()
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
