"""Test if plots work directly"""
import sys
import io

# UTF-8 output for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'ssz_explorer')

from ssz_physics_plots import create_g1_g2_domain_plot
import plotly.graph_objects as go

print("Testing physics plot generation...")

# Generate plot
fig = create_g1_g2_domain_plot()

print(f"✓ Figure created")
print(f"  Traces: {len(fig.data)}")
print(f"  Points: {len(fig.data[0].x)}")
print(f"  X range: {min(fig.data[0].x):.2e} to {max(fig.data[0].x):.2e} pc")
print(f"  Y range: {min(fig.data[0].y):.6f} to {max(fig.data[0].y):.6f}")
print(f"  Y has non-zero: {any(y > 0 for y in fig.data[0].y)}")

# Save to HTML
fig.write_html("test_physics_plot.html")
print("\n✓ Saved to test_physics_plot.html")
print("  Open this file in browser to see if plot renders!")
