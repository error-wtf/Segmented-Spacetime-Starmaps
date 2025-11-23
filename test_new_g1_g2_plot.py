#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test fuer neuen g1/g2 Plot
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

print("Erstelle g1/g2 Plot...")
fig = create_g1_g2_domain_plot()
print("Plot erfolgreich erstellt!")

# Speichere als HTML
output_file = "test_g1_g2_plot.html"
fig.write_html(output_file)
print(f"Gespeichert: {output_file}")
