#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test g1/g2 Plot fuer verschiedene Objekte
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

from ssz_physics_plots import create_g1_g2_domain_plot

print("Teste g1/g2 Plot fuer verschiedene Objekte...\n")

# Test 1: Default (Sgr A*)
print("1. Default (Sgr A*)...")
fig1 = create_g1_g2_domain_plot()
fig1.write_html("test_g1g2_sgrA.html")
print("   Gespeichert: test_g1g2_sgrA.html")

# Test 2: Sun
print("2. Sun (M = 1.0 Msun)...")
fig2 = create_g1_g2_domain_plot(mass_msun=1.0, object_name="Sun")
fig2.write_html("test_g1g2_sun.html")
print("   Gespeichert: test_g1g2_sun.html")

# Test 3: Betelgeuse (massive star)
print("3. Betelgeuse (M = 20 Msun)...")
fig3 = create_g1_g2_domain_plot(mass_msun=20.0, object_name="Betelgeuse")
fig3.write_html("test_g1g2_betelgeuse.html")
print("   Gespeichert: test_g1g2_betelgeuse.html")

# Test 4: Stellar mass black hole
print("4. Stellar BH (M = 10 Msun)...")
fig4 = create_g1_g2_domain_plot(mass_msun=10.0, object_name="Stellar BH")
fig4.write_html("test_g1g2_stellarBH.html")
print("   Gespeichert: test_g1g2_stellarBH.html")

# Test 5: Supermassive black hole M87
print("5. M87* (M = 6.5e9 Msun)...")
fig5 = create_g1_g2_domain_plot(mass_msun=6.5e9, object_name="M87*")
fig5.write_html("test_g1g2_m87.html")
print("   Gespeichert: test_g1g2_m87.html")

print("\nAlle Tests erfolgreich!")
print("Oeffne die HTML-Dateien im Browser um die Plots zu sehen.")
