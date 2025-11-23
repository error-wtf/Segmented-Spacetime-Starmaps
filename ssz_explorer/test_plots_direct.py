"""
Direct test of ALL plot functions
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
print("DIRECT TEST - ALL PHYSICS PLOTS")
print("="*80)

# Import functions
print("\n[1] Importing plot functions...")
try:
    from ssz_physics_plots import (
        create_g1_g2_domain_plot,
        create_time_dilation_comparison,
        create_radial_stretch_plot,
        create_combined_ssz_analysis
    )
    print("  ✓ All imports successful")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test each function
tests = [
    ("g1/g2 Domains", create_g1_g2_domain_plot, {}),
    ("Time Dilation", create_time_dilation_comparison, {}),
    ("Radial Stretch", create_radial_stretch_plot, {}),
    ("Combined Analysis", create_combined_ssz_analysis, {})
]

results = []

for name, func, kwargs in tests:
    print(f"\n[TEST] {name}...")
    try:
        fig = func(**kwargs)
        
        # Check figure
        if fig is None:
            print(f"  ✗ Returns None!")
            results.append((name, False, "Returns None"))
            continue
        
        if not hasattr(fig, 'data'):
            print(f"  ✗ No data attribute!")
            results.append((name, False, "No data attribute"))
            continue
        
        num_traces = len(fig.data)
        if num_traces == 0:
            print(f"  ✗ No traces in figure!")
            results.append((name, False, "No traces"))
            continue
        
        # Check if traces have data
        empty_traces = 0
        for i, trace in enumerate(fig.data):
            if hasattr(trace, 'x') and hasattr(trace, 'y'):
                x_len = len(trace.x) if hasattr(trace.x, '__len__') else 1
                y_len = len(trace.y) if hasattr(trace.y, '__len__') else 1
                if x_len == 0 or y_len == 0:
                    empty_traces += 1
        
        if empty_traces > 0:
            print(f"  ⚠ {empty_traces}/{num_traces} traces are empty")
            results.append((name, True, f"{num_traces} traces ({empty_traces} empty)"))
        else:
            print(f"  ✓ {num_traces} traces with data")
            results.append((name, True, f"{num_traces} traces"))
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        results.append((name, False, str(e)))

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

success = sum(1 for _, status, _ in results if status)
failed = len(results) - success

for name, status, info in results:
    symbol = "✓" if status else "✗"
    print(f"{symbol} {name}: {info}")

print(f"\nSuccess: {success}/{len(results)}")
print(f"Failed: {failed}/{len(results)}")

print("\n" + "="*80)
