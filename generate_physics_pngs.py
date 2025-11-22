#!/usr/bin/env python3
"""
Generate Physics Plots as PNG Files
Keine Gradio-Probleme - einfach PNGs speichern!
"""
from ssz_explorer.ssz_physics_plots_matplotlib import (
    create_domains_plot_png,
    create_time_dilation_png,
    create_radial_stretch_png,
    create_combined_analysis_png
)
from pathlib import Path
import matplotlib.pyplot as plt

print("="*60)
print("GENERATE PHYSICS PLOTS AS PNG")
print("="*60)

# Output directory
output_dir = Path("ssz_explorer/static/physics_plots")
output_dir.mkdir(parents=True, exist_ok=True)

# Generate all 4 plots
print("\n1. Domains Plot...")
img = create_domains_plot_png()
plt.imsave(output_dir / "domains.png", img)
print(f"   OK Saved: {output_dir / 'domains.png'}")

print("\n2. Time Dilation...")
img = create_time_dilation_png()
plt.imsave(output_dir / "time_dilation.png", img)
print(f"   OK Saved: {output_dir / 'time_dilation.png'}")

print("\n3. Radial Stretch...")
img = create_radial_stretch_png()
plt.imsave(output_dir / "radial_stretch.png", img)
print(f"   OK Saved: {output_dir / 'radial_stretch.png'}")

print("\n4. Combined Analysis...")
img = create_combined_analysis_png()
plt.imsave(output_dir / "combined.png", img)
print(f"   OK Saved: {output_dir / 'combined.png'}")

print("\n" + "="*60)
print("OK ALLE 4 PLOTS ERSTELLT!")
print(f"Location: {output_dir.absolute()}")
print("="*60)
