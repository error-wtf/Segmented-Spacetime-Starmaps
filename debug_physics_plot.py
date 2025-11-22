"""
DEBUG SSZ Physics Plot - Show EXACT values
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'ssz_explorer')
from ssz_physics_plots import create_g1_g2_domain_plot
import numpy as np

print("="*80)
print("DEBUGGING SSZ PHYSICS PLOT")
print("="*80)

# Generate the plot
fig = create_g1_g2_domain_plot()

print(f"\n1. Figure has {len(fig.data)} traces")

for i, trace in enumerate(fig.data):
    print(f"\n2. Trace {i}: {trace.name}")
    print(f"   Type: {trace.type}")
    print(f"   Mode: {trace.mode}")
    
    if hasattr(trace, 'x') and trace.x is not None:
        x_arr = np.array(trace.x)
        print(f"   X: {len(x_arr)} points")
        print(f"   X min: {x_arr.min():.6e}")
        print(f"   X max: {x_arr.max():.6e}")
        print(f"   X[0:5]: {x_arr[:5]}")
    
    if hasattr(trace, 'y') and trace.y is not None:
        y_arr = np.array(trace.y)
        print(f"   Y: {len(y_arr)} points")
        print(f"   Y min: {y_arr.min():.6f}")
        print(f"   Y max: {y_arr.max():.6f}")
        print(f"   Y mean: {y_arr.mean():.6f}")
        print(f"   Y[0:5]: {y_arr[:5]}")
        print(f"   Y has non-zero: {np.any(y_arr > 0)}")
        print(f"   Y unique values: {len(np.unique(y_arr))}")

print(f"\n3. Layout:")
print(f"   Title: {fig.layout.title.text if fig.layout.title else 'None'}")
print(f"   X-axis type: {fig.layout.xaxis.type}")
print(f"   X-axis range: {fig.layout.xaxis.range}")
print(f"   Y-axis range: {fig.layout.yaxis.range}")

print(f"\n4. Saving to debug_plot.html...")
fig.write_html("debug_plot.html")
print(f"   DONE! Open debug_plot.html in browser!")

print("\n" + "="*80)
print("DIAGNOSIS:")
print("="*80)

if len(fig.data) == 0:
    print("ERROR: NO TRACES! Plot will be empty!")
elif len(fig.data[0].x) == 0:
    print("ERROR: NO X DATA! Plot will be empty!")
elif len(fig.data[0].y) == 0:
    print("ERROR: NO Y DATA! Plot will be empty!")
elif np.all(np.array(fig.data[0].y) == 0):
    print("ERROR: ALL Y VALUES ARE ZERO! Plot will appear empty!")
elif np.allclose(np.array(fig.data[0].y), np.array(fig.data[0].y)[0]):
    print("WARNING: All Y values nearly identical - might look like flat line")
    print(f"  Y value: {np.array(fig.data[0].y)[0]:.6f}")
else:
    print("OK: Plot should display correctly!")
    print(f"  X: {len(fig.data[0].x)} points from {np.array(fig.data[0].x).min():.2e} to {np.array(fig.data[0].x).max():.2e}")
    print(f"  Y: varies from {np.array(fig.data[0].y).min():.6f} to {np.array(fig.data[0].y).max():.6f}")
