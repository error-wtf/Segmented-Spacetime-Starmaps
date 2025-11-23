"""
Test ACTUAL DATA VALUES in plots
"""
import os
import sys
from pathlib import Path
import numpy as np

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("TEST: ACTUAL PLOT DATA VALUES")
print("="*80)

from ssz_physics_plots import create_time_dilation_comparison

print("\n[1] Creating Time Dilation plot...")
fig = create_time_dilation_comparison()

print(f"\n[2] Figure has {len(fig.data)} traces")

for i, trace in enumerate(fig.data):
    print(f"\n--- Trace {i}: {trace.name} ---")
    
    if hasattr(trace, 'x') and hasattr(trace, 'y'):
        x_data = np.array(trace.x)
        y_data = np.array(trace.y)
        
        print(f"  Type: {type(trace).__name__}")
        print(f"  X points: {len(x_data)}")
        print(f"  Y points: {len(y_data)}")
        
        if len(x_data) > 0:
            print(f"  X range: [{x_data.min():.6f}, {x_data.max():.6f}]")
            print(f"  X first 5: {x_data[:5]}")
            
            # Check for NaN/Inf
            nan_count_x = np.sum(np.isnan(x_data))
            inf_count_x = np.sum(np.isinf(x_data))
            print(f"  X NaN: {nan_count_x}, Inf: {inf_count_x}")
        
        if len(y_data) > 0:
            print(f"  Y range: [{y_data.min():.6f}, {y_data.max():.6f}]")
            print(f"  Y first 5: {y_data[:5]}")
            
            # Check for NaN/Inf
            nan_count_y = np.sum(np.isnan(y_data))
            inf_count_y = np.sum(np.isinf(y_data))
            print(f"  Y NaN: {nan_count_y}, Inf: {inf_count_y}")
    else:
        print(f"  No x/y data!")

# Check layout
print(f"\n[3] Layout check:")
if hasattr(fig.layout, 'xaxis'):
    print(f"  X-axis:")
    print(f"    title: {fig.layout.xaxis.title.text if fig.layout.xaxis.title else 'None'}")
    print(f"    type: {fig.layout.xaxis.type}")
    print(f"    range: {fig.layout.xaxis.range}")
    
if hasattr(fig.layout, 'yaxis'):
    print(f"  Y-axis:")
    print(f"    title: {fig.layout.yaxis.title.text if fig.layout.yaxis.title else 'None'}")
    print(f"    range: {fig.layout.yaxis.range}")

# Save to HTML to verify
print(f"\n[4] Saving to HTML...")
output_file = Path(__file__).parent / "test_time_dilation.html"
fig.write_html(str(output_file))
print(f"  Saved to: {output_file}")
print(f"  Open this file in browser to see if plot works!")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print("""
If HTML file shows the plot correctly:
  → Problem is in Gradio integration
  
If HTML file is also empty:
  → Problem is in plot generation
  
If data has NaN/Inf:
  → Problem is in calculations
""")
