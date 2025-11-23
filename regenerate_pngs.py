#!/usr/bin/env python3
"""Regenerate ALL physics PNG files - CORRECT way"""
import sys
sys.path.insert(0, 'ssz_explorer')

from pathlib import Path
from ssz_physics_plots_matplotlib import (
    create_domains_plot_png,
    create_time_dilation_png,
    create_radial_stretch_png,
    create_combined_analysis_png
)
import shutil

output_dir = Path("ssz_explorer/static/physics_plots")
output_dir.mkdir(parents=True, exist_ok=True)

print("Regenerating PNG files...")

# Generate all 4 plots (returns temp file paths)
try:
    print("1. Domains...")
    domains_path = create_domains_plot_png()
    shutil.copy(domains_path, output_dir / "domains.png")
    print(f"   OK: {output_dir / 'domains.png'}")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    print("2. Time Dilation...")
    time_path = create_time_dilation_png()
    shutil.copy(time_path, output_dir / "time_dilation.png")
    print(f"   OK: {output_dir / 'time_dilation.png'}")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    print("3. Radial Stretch...")
    radial_path = create_radial_stretch_png()
    shutil.copy(radial_path, output_dir / "radial_stretch.png")
    print(f"   OK: {output_dir / 'radial_stretch.png'}")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    print("4. Combined Analysis...")
    combined_path = create_combined_analysis_png()
    shutil.copy(combined_path, output_dir / "combined.png")
    print(f"   OK: {output_dir / 'combined.png'}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\nDONE!")
