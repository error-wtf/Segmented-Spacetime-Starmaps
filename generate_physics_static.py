#!/usr/bin/env python3
"""Generate static physics plots that can be loaded in Gradio"""
import sys
sys.path.insert(0, 'ssz_explorer')

from ssz_physics_plots_matplotlib import (
    create_domains_plot_png,
    create_time_dilation_png,
    create_radial_stretch_png,
    create_combined_analysis_png
)
from pathlib import Path

output_dir = Path("ssz_explorer/static/physics_plots")
output_dir.mkdir(parents=True, exist_ok=True)

print("Generating static PNG files...")

# Generate all 4 plots
imgs = {
    'domains': create_domains_plot_png(),
    'time_dilation': create_time_dilation_png(),
    'radial_stretch': create_radial_stretch_png(),
    'combined': create_combined_analysis_png()
}

# Save to static files
for name, filepath in imgs.items():
    # Functions return temp file paths, copy to static
    import shutil
    dest = output_dir / f"{name}.png"
    shutil.copy(filepath, dest)
    print(f"OK {dest}")

print(f"\nALL 4 PLOTS READY in {output_dir}/")
