"""
Direct test - Create physics plot without Gradio
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("DIRECT PHYSICS PLOT TEST")
print("="*80)

# Load database
print("\n[1] Loading database...")
enriched_file = Path(__file__).parent / "ssz_data" / "star_database_enriched.csv"
df = pd.read_csv(enriched_file)
print(f"  Loaded {len(df):,} objects")

# Select object near Galactic Center
print("\n[2] Selecting object near Galactic Center...")
gc_ra, gc_dec = 266.42, -29.01
distances = np.sqrt((df['ra'] - gc_ra)**2 + (df['dec'] - gc_dec)**2)
nearest_idx = np.argmin(distances)
selected_obj = df.iloc[nearest_idx]

print(f"  ID: {selected_obj['source_id']}")
print(f"  Position: RA={selected_obj['ra']:.2f}°, Dec={selected_obj['dec']:.2f}°")
print(f"  Distance: {selected_obj['distance_ly']:.1f} ly")
print(f"  Mass: {selected_obj['mass_msun']:.3f} M_sun")

# Check SSZ parameters
print("\n[3] Checking SSZ parameters...")
print(f"  xi: {selected_obj['xi']}")
print(f"  D_ssz: {selected_obj['D_ssz']}")

# Try to create plot
print("\n[4] Creating plot...")
try:
    from ssz_physics_plots import create_g1_g2_domain_plot
    
    mass = selected_obj['mass_msun']
    obj_name = f"ID:{selected_obj['source_id']}"
    
    print(f"  Calling create_g1_g2_domain_plot(mass_msun={mass}, object_name='{obj_name}')")
    fig = create_g1_g2_domain_plot(mass_msun=mass, object_name=obj_name)
    
    print(f"  SUCCESS: Plot created!")
    print(f"  Type: {type(fig)}")
    print(f"  Traces: {len(fig.data)}")
    
    # Check if plot has data
    if len(fig.data) > 0:
        print(f"\n[5] Plot data check:")
        for i, trace in enumerate(fig.data):
            if hasattr(trace, 'x') and hasattr(trace, 'y'):
                x_len = len(trace.x) if hasattr(trace.x, '__len__') else 1
                y_len = len(trace.y) if hasattr(trace.y, '__len__') else 1
                print(f"  Trace {i}: {trace.name} - {x_len} x-points, {y_len} y-points")
        
        print(f"\n✅ PLOT IS NOT EMPTY!")
    else:
        print(f"\n❌ PLOT HAS NO TRACES!")
        
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
