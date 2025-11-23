#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Time Dilation Plot mit Universal Crossover
"""
import sys
import os
import io

# UTF-8 Setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, 'ssz_explorer')

from ssz_physics_plots import create_time_dilation_comparison

print("Teste Time Dilation Plot mit Universal Crossover...\n")

# Test 1: Default (Sgr A*)
print("1. Default (Sgr A*)...")
fig1 = create_time_dilation_comparison()
fig1.write_html("test_timedilation_sgrA.html")
print("   Gespeichert: test_timedilation_sgrA.html")

# Test 2: Sun
print("2. Sun (M = 1.0 Msun)...")
fig2 = create_time_dilation_comparison(mass_msun=1.0, object_name="Sun")
fig2.write_html("test_timedilation_sun.html")
print("   Gespeichert: test_timedilation_sun.html")

# Test 3: M87*
print("3. M87* (M = 6.5e9 Msun)...")
fig3 = create_time_dilation_comparison(mass_msun=6.5e9, object_name="M87*")
fig3.write_html("test_timedilation_m87.html")
print("   Gespeichert: test_timedilation_m87.html")

print("\nAlle Tests erfolgreich!")
print("Der Universal Crossover sollte bei r*/r_s ca. 1.387 mit D* ca. 0.528 sein!")
