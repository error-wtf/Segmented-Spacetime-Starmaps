"""
Test if Gradio button callbacks work
"""
import os
import sys
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("TEST: GRADIO BUTTON CALLBACKS")
print("="*80)

# Import everything from gradio_app
print("\n[1] Importing gradio_app_complete...")
try:
    import gradio_app_complete as app
    print("  ✓ Import successful")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check selected_object
print("\n[2] Checking selected_object...")
if hasattr(app, 'selected_object'):
    if app.selected_object is not None:
        print(f"  ✓ selected_object is set")
        print(f"    ID: {app.selected_object.get('source_id', 'N/A')}")
        print(f"    Mass: {app.selected_object.get('mass_msun', 'N/A')} M_sun")
    else:
        print(f"  ⚠ selected_object is None")
else:
    print(f"  ✗ selected_object does not exist!")

# Simulate button click
print("\n[3] Simulating 'Plot Domains' button click...")
try:
    from ssz_physics_plots import create_g1_g2_domain_plot
    import plotly.graph_objects as go
    
    # This is what the button does
    mass_msun = 4.3e6  # Sgr A*
    obj_name = f"Sgr A* (M = {mass_msun:.2e} M☉)"
    
    print(f"  Calling create_g1_g2_domain_plot(mass_msun={mass_msun}, object_name='{obj_name}')")
    fig = create_g1_g2_domain_plot(mass_msun=mass_msun, object_name=obj_name)
    
    if fig is None:
        print(f"  ✗ Function returned None!")
    elif not hasattr(fig, 'data'):
        print(f"  ✗ Figure has no data attribute!")
    elif len(fig.data) == 0:
        print(f"  ✗ Figure has no traces!")
    else:
        print(f"  ✓ Figure created with {len(fig.data)} traces")
        
        # Check trace data
        for i, trace in enumerate(fig.data):
            if hasattr(trace, 'x') and hasattr(trace, 'y'):
                x_len = len(trace.x) if hasattr(trace.x, '__len__') else 1
                y_len = len(trace.y) if hasattr(trace.y, '__len__') else 1
                print(f"    Trace {i} ({trace.name}): {x_len} x-points, {y_len} y-points")
        
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("DIAGNOSIS:")
print("="*80)
print("""
If plots don't show in Gradio UI, possible causes:

1. ✗ Gradio version incompatibility
   → Check: import gradio; print(gradio.__version__)
   
2. ✗ Browser caching issue  
   → Solution: Hard refresh (Ctrl+Shift+R)
   
3. ✗ Plot object not returned properly
   → Check: Function must 'return fig'
   
4. ✗ Button callback not bound
   → Check: domains_btn.click(fn=..., outputs=...)
   
5. ✗ JavaScript console errors
   → Check: Open browser DevTools (F12)
""")

print("="*80)
