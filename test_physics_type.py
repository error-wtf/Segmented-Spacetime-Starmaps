#!/usr/bin/env python3
# Test: Was geben die Funktionen zurück?

from ssz_explorer.ssz_physics_plots_matplotlib import create_domains_plot_png
import numpy as np

result = create_domains_plot_png()

print(f"Type: {type(result)}")
print(f"Type name: {type(result).__name__}")

if hasattr(result, 'shape'):
    print(f"✓ Hat .shape: {result.shape}")
elif hasattr(result, 'size'):
    print(f"✓ Hat .size (PIL): {result.size}")
    # Convert to numpy
    arr = np.array(result)
    print(f"✓ Als Numpy: {arr.shape}, dtype={arr.dtype}")
    
    # Save test
    import matplotlib.pyplot as plt
    plt.imsave('test_from_pil.png', arr)
    print("✓ Gespeichert als test_from_pil.png")
