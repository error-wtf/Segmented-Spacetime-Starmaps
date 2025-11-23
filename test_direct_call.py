#!/usr/bin/env python3
"""Direct test of physics function"""
import sys
import traceback

try:
    from ssz_explorer.ssz_physics_plots_matplotlib import create_radial_stretch_png
    print("Import OK")
    
    result = create_radial_stretch_png()
    print(f"Result type: {type(result)}")
    print(f"Result shape: {result.shape if hasattr(result, 'shape') else 'NO SHAPE'}")
    print("SUCCESS!")
    
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
