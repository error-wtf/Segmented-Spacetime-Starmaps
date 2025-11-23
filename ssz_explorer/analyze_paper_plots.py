#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze ALL 570 Plots from PAPER-RESTORED
==========================================

Creates automatic categorization for Gradio integration.
"""
import json
from pathlib import Path
from collections import defaultdict

PAPER_RESTORED_PATH = Path(r"E:\clone\PAPER-RESTORED")
plot_list_file = PAPER_RESTORED_PATH / "plot_list.json"

with open(plot_list_file, 'r') as f:
    ALL_PLOTS = json.load(f)

print(f"="*80)
print(f"ANALYZING {len(ALL_PLOTS)} PLOTS")
print(f"="*80)

# Categorize by directory structure
categories = defaultdict(list)

for plot_info in ALL_PLOTS:
    rel_path = plot_info['RelativePath']
    parts = Path(rel_path).parts
    
    if len(parts) == 2:
        # plots/filename.png
        category = "Root Plots"
    else:
        # plots/category/filename.png
        category = parts[1].replace('_', ' ').title()
    
    categories[category].append(rel_path)

# Print statistics
print(f"\n{'Category':<30s} {'Count':>6s}")
print(f"{'-'*40}")
for cat in sorted(categories.keys()):
    print(f"{cat:<30s} {len(categories[cat]):>6d}")

print(f"\n{'Total':<30s} {len(ALL_PLOTS):>6d}")

# Generate Python dict for Gradio
print(f"\n"+ "="*80)
print("PYTHON DICT FOR GRADIO:")
print("="*80)

print("PLOT_CATEGORIES = {")
for cat in sorted(categories.keys()):
    plots = categories[cat]
    print(f'    "{cat}": [')
    for plot in plots[:5]:  # Show first 5 as examples
        print(f'        "{plot}",')
    if len(plots) > 5:
        print(f'        # ... {len(plots)-5} more plots')
    print(f'    ],')
print("}")

# Save to JSON
output_file = Path("plot_categories.json")
with open(output_file, 'w') as f:
    json.dump(dict(categories), f, indent=2)

print(f"\n✓ Saved to: {output_file}")
