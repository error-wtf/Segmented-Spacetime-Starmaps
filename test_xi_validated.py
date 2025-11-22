#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Test for Xi(r) - Against Validated Values

Checks that our Xi(r) implementation matches the validated values
from ssz-metric-pure/src/ssz_core/segment_density.py

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
from src.ssz_starmaps import Xi, D_SSZ, radial_stretch, PHI, schwarzschild_radius

# Test configuration
M_SUN = 1.98847e30  # kg
r_s = schwarzschild_radius(M_SUN)

# Validated values from ssz-metric-pure
VALIDATED_TABLE = {
    # r/r_s : (Xi, D_SSZ, Stretch)
    0.5: (0.55470, 0.64321, 1.55470),
    1.0: (0.80171, 0.55503, 1.80171),
    2.0: (0.96068, 0.51003, 1.96068),
    5.0: (0.99969, 0.50008, 1.99969),
}

TOLERANCE = 1e-4  # 0.01% tolerance


def test_xi_values():
    """Test Xi(r) against validated values."""
    print("\n" + "=" * 80)
    print("TEST: Xi(r) Values")
    print("=" * 80)
    
    all_passed = True
    
    for r_factor, (xi_expected, d_ssz_expected, stretch_expected) in VALIDATED_TABLE.items():
        r = r_factor * r_s
        
        # Compute
        xi_computed = Xi(r, r_s)
        d_ssz_computed = D_SSZ(r, r_s)
        stretch_computed = radial_stretch(r, r_s)
        
        # Check
        xi_ok = abs(xi_computed - xi_expected) < TOLERANCE
        d_ssz_ok = abs(d_ssz_computed - d_ssz_expected) < TOLERANCE
        stretch_ok = abs(stretch_computed - stretch_expected) < TOLERANCE
        
        status = "PASS" if (xi_ok and d_ssz_ok and stretch_ok) else "FAIL"
        
        if status == "FAIL":
            all_passed = False
        
        print(f"\nr/r_s = {r_factor:.1f}:")
        print(f"  Xi(r):      {xi_computed:.5f}  (expected: {xi_expected:.5f})  [{xi_ok}]")
        print(f"  D_SSZ(r):   {d_ssz_computed:.5f}  (expected: {d_ssz_expected:.5f})  [{d_ssz_ok}]")
        print(f"  Stretch(r): {stretch_computed:.5f}  (expected: {stretch_expected:.5f})  [{stretch_ok}]")
        print(f"  Status: {status}")
    
    return all_passed


def test_phi_value():
    """Test that PHI is golden ratio."""
    print("\n" + "=" * 80)
    print("TEST: Golden Ratio Value")
    print("=" * 80)
    
    phi_expected = (1.0 + np.sqrt(5.0)) / 2.0
    phi_ok = abs(PHI - phi_expected) < 1e-10
    
    print(f"  PHI = {PHI:.10f}")
    print(f"  Expected: {phi_expected:.10f}")
    print(f"  Match: {phi_ok}")
    print(f"  Status: {'PASS' if phi_ok else 'FAIL'}")
    
    return phi_ok


def test_asymptotic_behavior():
    """Test that Xi(inf) -> 1 and Stretch(inf) -> 2."""
    print("\n" + "=" * 80)
    print("TEST: Asymptotic Behavior")
    print("=" * 80)
    
    r_large = 1000 * r_s  # Very large r
    
    xi_large = Xi(r_large, r_s)
    stretch_large = radial_stretch(r_large, r_s)
    
    xi_near_1 = abs(xi_large - 1.0) < 0.01  # Should be within 1% of 1
    stretch_near_2 = abs(stretch_large - 2.0) < 0.01  # Should be within 1% of 2
    
    print(f"  r = 1000*r_s")
    print(f"  Xi(r) = {xi_large:.6f}  (should be ~1.0)")
    print(f"  Stretch(r) = {stretch_large:.6f}  (should be ~2.0)")
    print(f"  Xi near 1: {xi_near_1}")
    print(f"  Stretch near 2: {stretch_near_2}")
    print(f"  Status: {'PASS' if (xi_near_1 and stretch_near_2) else 'FAIL'}")
    
    return xi_near_1 and stretch_near_2


def test_origin_behavior():
    """Test that Xi(0) = 0 and Stretch(0) = 1."""
    print("\n" + "=" * 80)
    print("TEST: Origin Behavior")
    print("=" * 80)
    
    xi_zero = Xi(0.0, r_s)
    stretch_zero = radial_stretch(0.0, r_s)
    
    xi_ok = abs(xi_zero) < 1e-10
    stretch_ok = abs(stretch_zero - 1.0) < 1e-10
    
    print(f"  Xi(0) = {xi_zero:.10f}  (should be 0)")
    print(f"  Stretch(0) = {stretch_zero:.10f}  (should be 1)")
    print(f"  Xi is zero: {xi_ok}")
    print(f"  Stretch is one: {stretch_ok}")
    print(f"  Status: {'PASS' if (xi_ok and stretch_ok) else 'FAIL'}")
    
    return xi_ok and stretch_ok


if __name__ == "__main__":
    print("=" * 80)
    print("Xi(r) VALIDATION TEST SUITE")
    print("Against ssz-metric-pure validated values")
    print("=" * 80)
    
    print(f"\nConstants:")
    print(f"  PHI = {PHI:.6f}")
    print(f"  M_sun = {M_SUN:.3e} kg")
    print(f"  r_s = {r_s:.2f} m")
    print(f"  Tolerance = {TOLERANCE}")
    
    # Run tests
    results = {
        "Xi Values": test_xi_values(),
        "Golden Ratio": test_phi_value(),
        "Asymptotic": test_asymptotic_behavior(),
        "Origin": test_origin_behavior(),
    }
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "PASS [OK]" if passed else "FAIL [X]"
        print(f"  {test_name:20s}: {status}")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("ALL TESTS PASSED!")
        print("Xi(r) implementation matches ssz-metric-pure exactly!")
    else:
        print("SOME TESTS FAILED!")
        print("Check implementation against ssz-metric-pure!")
    print("=" * 80 + "\n")
    
    # Exit code
    exit(0 if all_passed else 1)
