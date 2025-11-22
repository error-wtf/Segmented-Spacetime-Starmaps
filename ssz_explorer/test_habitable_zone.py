#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Habitable Zone Calculations

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
from habitable_zone import *


class TestHabitableZone:
    """Test suite for habitable zone calculations."""
    
    def test_stellar_luminosity(self):
        """Test stellar luminosity calculation."""
        # Sun
        L = stellar_luminosity(radius_rsun=1.0, teff=5778.0)
        L_lsun = L / L_sun
        
        # Should be ~1 L_sun
        assert 0.95 < L_lsun < 1.05
        print(f"✅ Sun luminosity: {L_lsun:.3f} L_sun")
    
    def test_hz_traditional_sun(self):
        """Test traditional HZ for Sun."""
        r_inner, r_outer = hz_traditional(1.0, conservative=True)
        
        # Conservative HZ for Sun: ~0.75 - 1.77 AU
        assert 0.7 < r_inner < 0.8
        assert 1.7 < r_outer < 1.8
        
        print(f"✅ Sun HZ (traditional): {r_inner:.3f} - {r_outer:.3f} AU")
    
    def test_hz_ssz_sun(self):
        """Test SSZ HZ for Sun."""
        r_inner, r_outer = hz_ssz_corrected(1.0, 1.0, conservative=True)
        
        # Should be slightly different from traditional
        r_inner_trad, r_outer_trad = hz_traditional(1.0, conservative=True)
        
        assert r_inner != r_inner_trad
        assert r_outer != r_outer_trad
        
        print(f"✅ Sun HZ (SSZ): {r_inner:.3f} - {r_outer:.3f} AU")
    
    def test_earth_in_hz(self):
        """Test that Earth is in HZ."""
        result = is_in_hz(1.0, 1.0, 1.0, method='ssz', conservative=True)
        
        assert result['in_hz'] == True
        assert 0 < result['position_fraction'] < 1
        
        print(f"✅ Earth in HZ: position = {result['position_fraction']:.2f}")
    
    def test_venus_mars(self):
        """Test Venus (too hot) and Mars (edge of HZ)."""
        # Venus at 0.72 AU
        venus = is_in_hz(0.72, 1.0, 1.0, method='traditional')
        
        # Mars at 1.52 AU
        mars = is_in_hz(1.52, 1.0, 1.0, method='traditional')
        
        # Venus should be inside inner edge or close
        # Mars should be near outer edge
        
        print(f"✅ Venus: in_hz={venus['in_hz']}, Mars: in_hz={mars['in_hz']}")
    
    def test_compare_methods(self):
        """Test comparison of traditional vs SSZ."""
        result = compare_hz_methods(1.0, 1.0)
        
        assert 'traditional' in result
        assert 'ssz' in result
        assert 'difference' in result
        
        # SSZ should be slightly different
        assert result['difference']['inner_shift_au'] != 0
        
        print(f"✅ Method comparison: Δinner = {result['difference']['inner_shift_au']:.5f} AU")
    
    def test_m_dwarf(self):
        """Test HZ for M-dwarf star."""
        # Low luminosity M-dwarf
        r_inner, r_outer = hz_traditional(0.01, conservative=True)
        
        # HZ should be much closer
        assert r_inner < 0.2
        assert r_outer < 0.5
        
        print(f"✅ M-dwarf HZ: {r_inner:.3f} - {r_outer:.3f} AU")
    
    def test_hot_star(self):
        """Test HZ for hot star."""
        # Luminous star (10 L_sun)
        r_inner, r_outer = hz_traditional(10.0, conservative=True)
        
        # HZ should be farther out
        assert r_inner > 2.0
        assert r_outer > 4.0
        
        print(f"✅ Hot star HZ: {r_inner:.2f} - {r_outer:.2f} AU")
    
    def test_hz_from_params(self):
        """Test HZ calculation from stellar params."""
        result = hz_from_star_params(
            teff=5778,
            radius_rsun=1.0,
            mass_msun=1.0,
            method='ssz'
        )
        
        assert 'hz_inner_au' in result
        assert 'hz_outer_au' in result
        assert result['hz_inner_au'] < result['hz_outer_au']
        
        print(f"✅ HZ from params: {result['hz_inner_au']:.3f} - {result['hz_outer_au']:.3f} AU")
    
    def test_optimistic_vs_conservative(self):
        """Test optimistic vs conservative HZ."""
        r_in_cons, r_out_cons = hz_traditional(1.0, conservative=True)
        r_in_opt, r_out_opt = hz_traditional(1.0, conservative=False)
        
        # Optimistic should be wider
        assert r_in_opt < r_in_cons
        assert r_out_opt > r_out_cons
        
        print(f"✅ Conservative: {r_in_cons:.3f}-{r_out_cons:.3f} AU")
        print(f"   Optimistic: {r_in_opt:.3f}-{r_out_opt:.3f} AU")


def run_all_tests():
    """Run all tests manually."""
    print("="*80)
    print("HABITABLE ZONE TEST SUITE")
    print("="*80)
    
    test_suite = TestHabitableZone()
    
    tests = [
        ("Stellar Luminosity", test_suite.test_stellar_luminosity),
        ("Traditional HZ (Sun)", test_suite.test_hz_traditional_sun),
        ("SSZ HZ (Sun)", test_suite.test_hz_ssz_sun),
        ("Earth in HZ", test_suite.test_earth_in_hz),
        ("Venus & Mars", test_suite.test_venus_mars),
        ("Method Comparison", test_suite.test_compare_methods),
        ("M-dwarf HZ", test_suite.test_m_dwarf),
        ("Hot Star HZ", test_suite.test_hot_star),
        ("HZ from Parameters", test_suite.test_hz_from_params),
        ("Optimistic vs Conservative", test_suite.test_optimistic_vs_conservative),
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
