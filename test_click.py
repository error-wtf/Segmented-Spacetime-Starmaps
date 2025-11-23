#!/usr/bin/env python3
import sys
import traceback

print("="*60)
print("DIREKTER TEST - RADIAL STRETCH BUTTON CLICK")
print("="*60)

try:
    # Simuliere Button Click
    from ssz_explorer.ssz_physics_plots_matplotlib import create_radial_stretch_png
    
    print("\n1. Calling function...")
    result = create_radial_stretch_png()
    
    print(f"\n2. Result type: {type(result)}")
    print(f"3. Result value: {result}")
    
    # Check if file exists
    import os
    if isinstance(result, str) and os.path.exists(result):
        size = os.path.getsize(result)
        print(f"4. File exists: YES")
        print(f"5. File size: {size} bytes")
        print(f"6. File path: {result}")
        print("\n✓ SUCCESS - Function returns valid file path!")
    else:
        print(f"4. File exists: NO")
        print("\n✗ ERROR - File not found or wrong return type!")
        
except Exception as e:
    print(f"\n✗ EXCEPTION: {e}")
    traceback.print_exc()
    sys.exit(1)
