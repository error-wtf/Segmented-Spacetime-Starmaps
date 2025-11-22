#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for SSZ Orbital Calculations

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import os
import sys

# UTF-8 für Windows-Konsole
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

import pytest
import numpy as np
from ssz_orbits import *


class TestSSZOrbits:
    """Test suite for SSZ orbital calculations."""
    
    def test_schwarzschild_radius(self):
        """Test Schwarzschild radius calculation."""
        # Sun
        M_sun_kg = 1.98847e30
        r_s = schwarzschild_radius(M_sun_kg)
        
        # Should be ~2953 meters
        assert 2900 < r_s < 3000
        print(f"✅ Sun r_s = {r_s:.1f} m")
    
    def test_segment_saturation(self):
        """Test SSZ segment saturation."""
        r_s = 3000.0  # meters
        
        # At r = 0: Xi → 0 (actually approaches but never 0)
        Xi_0 = ssz_segment_saturation(1.0, r_s)
        assert 0 <= Xi_0 < 0.01
        
        # At r >> r_s: Xi → 1
        Xi_inf = ssz_segment_saturation(1e10, r_s)
        assert 0.99 < Xi_inf <= 1.0
        
        print(f"✅ Xi(r→0) = {Xi_0:.6f}, Xi(r→∞) = {Xi_inf:.6f}")
    
    def test_gr_orbital_period(self):
        """Test GR/Newtonian period calculation."""
        # Earth around Sun
        a = 1.496e11  # 1 AU in meters
        M = 1.98847e30  # Solar mass
        
        T = gr_orbital_period(a, M)
        T_days = T / 86400
        
        # Should be ~365 days
        assert 364 < T_days < 366
        print(f"✅ Earth period (GR) = {T_days:.2f} days")
    
    def test_ssz_orbital_period(self):
        """Test SSZ-corrected period."""
        a = 1.496e11  # 1 AU
        M = 1.98847e30  # Solar mass
        
        T_gr = gr_orbital_period(a, M)
        T_ssz = ssz_orbital_period(a, M)
        
        # SSZ should differ slightly from GR
        assert T_ssz != T_gr
        
        # Difference should be small for Earth
        rel_diff = abs(T_ssz - T_gr) / T_gr
        assert rel_diff < 1e-3  # Less than 0.1%
        
        print(f"✅ Earth: T_GR = {T_gr/86400:.6f} days, T_SSZ = {T_ssz/86400:.6f} days")
        print(f"   Relative difference: {rel_diff*1e6:.2f} ppm")
    
    def test_period_difference(self):
        """Test period difference calculation."""
        # Hot Jupiter
        a = 0.05 * 1.496e11  # 0.05 AU
        M = 1.98847e30
        
        diff = period_difference(a, M)
        
        assert 'T_gr_days' in diff
        assert 'T_ssz_days' in diff
        assert 'difference_sec' in diff
        assert 'relative_diff' in diff
        assert 'observable' in diff
        
        print(f"✅ Hot Jupiter: ΔT = {diff['difference_sec']:.3f} sec")
        print(f"   Observable: {diff['observable']}")
    
    def test_semi_major_axis(self):
        """Test semi-major axis calculation from period."""
        # Known: Earth, P = 365.25 days
        P = 365.25 * 86400  # seconds
        M = 1.98847e30
        
        a = ssz_semi_major_axis(P, M)
        a_au = a / 1.496e11
        
        # Should be ~1 AU
        assert 0.99 < a_au < 1.01
        print(f"✅ For P=365.25 days: a = {a_au:.4f} AU")
    
    def test_transit_timing_variation(self):
        """Test TTV calculation."""
        P = 3.5 * 86400  # Hot Jupiter
        M = 1.1 * 1.98847e30
        a = 0.05 * 1.496e11
        
        ttv = transit_timing_variation(P, M, a, n_transits=100)
        
        assert 'transit_number' in ttv
        assert 'ttv_seconds' in ttv
        assert len(ttv['transit_number']) == 100
        
        # TTV should accumulate
        assert abs(ttv['ttv_seconds'][-1]) > abs(ttv['ttv_seconds'][0])
        
        print(f"✅ TTV after 100 transits: {ttv['ttv_seconds'][-1]:.2f} sec")
    
    def test_observable_signature(self):
        """Test observability determination."""
        params = {
            'period_days': 3.5,
            'semi_major_axis_au': 0.05,
            'star_mass_msun': 1.1
        }
        
        obs = observable_signature(params, precision_seconds=10.0)
        
        assert 'observable' in obs
        assert 'recommendations' in obs
        
        print(f"✅ Observable: {obs['observable']}")
        print(f"   {obs['recommendations']}")
    
    def test_calculate_for_planet(self):
        """Test convenience function."""
        result = calculate_for_planet(
            period_days=365.0,
            star_mass_msun=1.0
        )
        
        # Should have all keys
        assert 'T_gr_days' in result
        assert 'T_ssz_days' in result
        assert 'observable' in result
        assert 'recommendations' in result
        
        print(f"✅ Complete calculation for Earth-like planet")
        print(f"   Period difference: {result['difference_sec']:.3f} sec")
    
    def test_extreme_cases(self):
        """Test extreme orbital cases."""
        # Very close orbit
        result_close = calculate_for_planet(
            period_days=0.5,
            star_mass_msun=1.0
        )
        
        # Very distant orbit
        result_far = calculate_for_planet(
            period_days=10000.0,
            star_mass_msun=1.0
        )
        
        # Close orbits should have larger relative SSZ effects
        assert abs(result_close['relative_diff']) > abs(result_far['relative_diff'])
        
        print("✅ Extreme cases handled correctly")


def run_all_tests():
    """Run all tests manually."""
    print("="*80)
    print("SSZ ORBITS TEST SUITE")
    print("="*80)
    
    test_suite = TestSSZOrbits()
    
    tests = [
        ("Schwarzschild Radius", test_suite.test_schwarzschild_radius),
        ("Segment Saturation", test_suite.test_segment_saturation),
        ("GR Orbital Period", test_suite.test_gr_orbital_period),
        ("SSZ Orbital Period", test_suite.test_ssz_orbital_period),
        ("Period Difference", test_suite.test_period_difference),
        ("Semi-Major Axis", test_suite.test_semi_major_axis),
        ("Transit Timing Variation", test_suite.test_transit_timing_variation),
        ("Observable Signature", test_suite.test_observable_signature),
        ("Calculate for Planet", test_suite.test_calculate_for_planet),
        ("Extreme Cases", test_suite.test_extreme_cases),
    ]
    
    for i, (name, test_func) in enumerate(tests, 1):
        print(f"\n[Test {i}] {name}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print("\n" + "="*80)
    print("✅ TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()
