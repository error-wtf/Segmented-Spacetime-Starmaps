"""
Debug selected_object - Check if it's set correctly
"""
import os
import sys
from pathlib import Path

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("DEBUG: SELECTED OBJECT CHECK")
print("="*80)

# Import gradio_app_complete to trigger initialization
print("\n[1] Importing gradio_app_complete...")
try:
    import gradio_app_complete as app
    print("  OK: Import successful")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check selected_object
print("\n[2] Checking selected_object...")
if hasattr(app, 'selected_object'):
    if app.selected_object is not None:
        print("  OK: selected_object is SET!")
        print(f"  Type: {type(app.selected_object)}")
        print(f"  Source ID: {app.selected_object.get('source_id', 'N/A')}")
        print(f"  Mass: {app.selected_object.get('mass_msun', 'N/A')} M_sun")
        print(f"  Distance: {app.selected_object.get('distance_ly', 'N/A')} ly")
        
        # Check SSZ parameters
        print("\n[3] Checking SSZ parameters...")
        if 'xi' in app.selected_object.index:
            print(f"  Xi: {app.selected_object['xi']}")
        else:
            print("  ERROR: xi NOT in object!")
            
        if 'D_ssz' in app.selected_object.index:
            print(f"  D_ssz: {app.selected_object['D_ssz']}")
        else:
            print("  ERROR: D_ssz NOT in object!")
    else:
        print("  ERROR: selected_object is NONE!")
else:
    print("  ERROR: selected_object does NOT exist!")

# Check if we can create a plot
print("\n[4] Testing plot creation...")
try:
    from ssz_physics_plots import create_g1_g2_domain_plot
    
    if app.selected_object is not None:
        mass = app.selected_object.get('mass_msun', 4.297e6)
        print(f"  Creating plot with mass={mass} M_sun...")
        fig = create_g1_g2_domain_plot(mass_msun=mass, object_name="Test")
        print(f"  OK: Plot created! Type: {type(fig)}")
        print(f"  Plot has {len(fig.data)} traces")
    else:
        print("  ERROR: Cannot create plot - no object!")
        
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("DEBUG COMPLETE")
print("="*80)
