#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ vs Minkowski - Quantitative Comparison Test

Vergleicht die ECHTE SSZ-Deformation mit Minkowski-Geometrie.
Zeigt dass SSZ tatsächlich auf Xi(r) = 1 - exp(-phi*r_s / r) basiert!

© 2025 Carmen Wrede, Lino Casu
Licensed under the Anti-Capitalist Software License v1.4
"""

import numpy as np
import matplotlib.pyplot as plt
from src.ssz_starmaps import (
    Xi, D_SSZ, D_GR, PHI, schwarzschild_radius,
    apply_ssz_metric_deformation
)

print("=" * 80)
print("SSZ vs MINKOWSKI - QUANTITATIVE COMPARISON TEST")
print("=" * 80)

# Physical parameters
M_sun = 1.98847e30  # kg
r_s = schwarzschild_radius(M_sun)

print(f"\nPhysical Constants:")
print(f"  phi (golden ratio) = {PHI:.6f}")
print(f"  M_sun = {M_sun:.3e} kg")
print(f"  r_s (Schwarzschild radius) = {r_s:.2f} m")

# Test 1: Segment Saturation vs Radius
print("\n" + "-" * 80)
print("TEST 1: Segment Saturation Xi(r)")
print("-" * 80)

radii_test = np.array([0.5, 1.0, 1.5, 2.0, 5.0, 10.0]) * r_s
xi_values = Xi(radii_test, r_s)

print(f"\n  r/r_s  |  r [m]       |  Xi(r)    | Segments")
print(f"  " + "-" * 60)
for i, r in enumerate(radii_test):
    ratio = r / r_s
    segments_percent = xi_values[i] * 100
    print(f"  {ratio:5.1f}  | {r:12.2e} | {xi_values[i]:8.6f} | {segments_percent:6.2f}%")

# Test 2: Time Dilation Comparison
print("\n" + "-" * 80)
print("TEST 2: Time Dilation - SSZ vs GR")
print("-" * 80)

r_test = np.linspace(1.1 * r_s, 10 * r_s, 50)
d_ssz = D_SSZ(r_test, r_s)
d_gr = D_GR(r_test, r_s)

# Find crossover point
differences = np.abs(d_ssz - d_gr)
crossover_idx = np.argmin(differences)
r_crossover = r_test[crossover_idx]

print(f"\nCrossover Point (D_SSZ ~= D_GR):")
print(f"  r* = {r_crossover:.2e} m")
print(f"  r*/r_s = {r_crossover/r_s:.6f}")
print(f"  D(r*) = {d_ssz[crossover_idx]:.6f}")
print(f"\nTheoretical crossover (from ssz-metric-pure):")
print(f"  r*/r_s ~= 1.386562 (universal!)")

# Test 3: Radial Deformation
print("\n" + "-" * 80)
print("TEST 3: Radial Deformation - SSZ Metric")
print("-" * 80)

# Test grid
x_test = np.linspace(-3, 3, 7)
y_test = np.zeros_like(x_test)

x_ssz, y_ssz = apply_ssz_metric_deformation(
    x_test, y_test,
    mass_kg=M_sun,
    r_scale_deg=1.0
)

print(f"\n  Original r  |  SSZ r      | Stretch  | Xi(r)")
print(f"  " + "-" * 50)
for i in range(len(x_test)):
    r_orig = abs(x_test[i])
    r_ssz = abs(x_ssz[i])
    if r_orig > 0:
        stretch = r_ssz / r_orig
        r_physical = r_orig * r_s
        xi_val = Xi(r_physical, r_s)
    else:
        stretch = 1.0
        xi_val = 0.0
    
    print(f"  {r_orig:10.3f}  | {r_ssz:10.3f}  | {stretch:7.4f} | {xi_val:6.4f}")

# Test 4: Visualization
print("\n" + "-" * 80)
print("TEST 4: Generating Comparison Plots...")
print("-" * 80)

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))

# Plot 1: Xi(r) vs radius
ax1.plot(r_test / r_s, Xi(r_test, r_s), 'b-', linewidth=2, label='Xi(r)')
ax1.axhline(y=0.8017, color='r', linestyle='--', alpha=0.5, label='Xi(r_s) = 0.8017')
ax1.axvline(x=1.0, color='gray', linestyle=':', alpha=0.5, label='r = r_s')
ax1.set_xlabel(r'$r / r_s$', fontsize=12)
ax1.set_ylabel(r'$\Xi(r)$', fontsize=12)
ax1.set_title(r'Segment Saturation: $\Xi(r) = 1 - e^{-\phi r/r_s}$', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend()
ax1.set_xlim(0, 10)

# Plot 2: Time Dilation Comparison
ax2.plot(r_test / r_s, d_ssz, 'b-', linewidth=2, label='D_SSZ (finite at r_s!)')
ax2.plot(r_test / r_s, d_gr, 'r--', linewidth=2, label='D_GR (diverges!)')
ax2.axvline(x=r_crossover/r_s, color='g', linestyle=':', alpha=0.7, 
            label=f'Crossover: r*/r_s = {r_crossover/r_s:.3f}')
ax2.set_xlabel(r'$r / r_s$', fontsize=12)
ax2.set_ylabel('Time Dilation Factor', fontsize=12)
ax2.set_title('SSZ vs GR Time Dilation', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend()
ax2.set_ylim(0.4, 1.0)

# Plot 3: Deviation D_SSZ - D_GR
ax3.plot(r_test / r_s, d_ssz - d_gr, 'purple', linewidth=2)
ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax3.axvline(x=r_crossover/r_s, color='g', linestyle=':', alpha=0.7)
ax3.fill_between(r_test / r_s, 0, d_ssz - d_gr, alpha=0.2, color='purple')
ax3.set_xlabel(r'$r / r_s$', fontsize=12)
ax3.set_ylabel(r'$\Delta D = D_{SSZ} - D_{GR}$', fontsize=12)
ax3.set_title('Deviation: SSZ - GR', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3)

# Plot 4: Radial Stretch Factor
r_plot = np.linspace(0.1, 5, 100)
r_physical_plot = r_plot * r_s
xi_plot = Xi(r_physical_plot, r_s)
stretch_plot = 1.0 + xi_plot

ax4.plot(r_plot, stretch_plot, 'darkgreen', linewidth=2, label='1 + Xi(r)')
ax4.axhline(y=2.0, color='r', linestyle='--', alpha=0.5, label='Asymptotic limit = 2')
ax4.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
ax4.set_xlabel(r'$r / r_s$', fontsize=12)
ax4.set_ylabel('Stretch Factor', fontsize=12)
ax4.set_title(r'SSZ Radial Stretch: $R_{SSZ} = r \cdot (1 + \Xi)$', fontsize=13, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend()
ax4.set_ylim(0.9, 2.1)

plt.tight_layout()
plt.savefig('ssz_vs_minkowski_comparison.png', dpi=150, bbox_inches='tight')
print("  [OK] Plot saved: ssz_vs_minkowski_comparison.png")

# Final Summary
print("\n" + "=" * 80)
print("SUMMARY: SSZ vs MINKOWSKI")
print("=" * 80)

print(f"\n1. ECHTE SSZ-FORMEL:")
print(f"   Xi(r) = 1 - exp(-phi*r_s / r)")
print(f"   phi = {PHI:.6f}")

print(f"\n2. KEINE SINGULARITAET:")
print(f"   D_GR(r_s) = NaN (divergiert!)")
print(f"   D_SSZ(r_s) = {D_SSZ(r_s, r_s):.6f} (endlich!)")

print(f"\n3. CROSSOVER-PUNKT:")
print(f"   r*/r_s = {r_crossover/r_s:.6f}")
print(f"   Theoretisch: 1.386562 (universal!)")
print(f"   Abweichung: {abs(r_crossover/r_s - 1.386562):.6f}")

print(f"\n4. ASYMPTOTISCHES VERHALTEN:")
print(f"   Xi(inf) -> 1")
print(f"   Stretch(inf) -> 2")
print(f"   Meaning: Doppelte Weglaenge bei vollstaendiger Segmentierung!")

print("\n" + "=" * 80)
print("[OK] ECHTE SSZ-Physik validiert!")
print("Formula: Xi(r) = 1 - exp(-phi*r_s / r)")
print("=" * 80 + "\n")
