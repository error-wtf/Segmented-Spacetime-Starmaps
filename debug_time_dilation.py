"""
DEBUG Time Dilation Plot
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'ssz_explorer')
from ssz_physics_plots import create_time_dilation_comparison
import numpy as np

print("="*80)
print("DEBUGGING TIME DILATION PLOT")
print("="*80)

fig = create_time_dilation_comparison()

print(f"\n1. Figure has {len(fig.data)} traces")

for i, trace in enumerate(fig.data):
    print(f"\n2. Trace {i}: {trace.name}")
    print(f"   Type: {trace.type}")
    
    if hasattr(trace, 'x') and trace.x is not None:
        x_arr = np.array(trace.x)
        print(f"   X: {len(x_arr)} points")
        if len(x_arr) > 0:
            print(f"   X min: {x_arr.min():.6e}")
            print(f"   X max: {x_arr.max():.6e}")
            print(f"   X[0:5]: {x_arr[:5]}")
    
    if hasattr(trace, 'y') and trace.y is not None:
        y_arr = np.array(trace.y)
        print(f"   Y: {len(y_arr)} points")
        if len(y_arr) > 0:
            print(f"   Y min: {y_arr.min():.6f}")
            print(f"   Y max: {y_arr.max():.6f}")
            print(f"   Y[0:5]: {y_arr[:5]}")
            print(f"   Y has non-zero: {np.any(y_arr != 0)}")

print(f"\n3. Saving to debug_time_dilation.html...")
fig.write_html("debug_time_dilation.html")
print(f"   DONE!")

print("\n" + "="*80)
if len(fig.data) == 0:
    print("ERROR: NO TRACES!")
elif len(fig.data[0].x) == 0:
    print("ERROR: NO X DATA!")
else:
    print("OK: Data exists - if still empty in Gradio → Gradio bug!")
