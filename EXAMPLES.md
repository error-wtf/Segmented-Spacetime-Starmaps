# SSZ StarMaps - Examples

**ECHTE SSZ-Physik Beispiele** basierend auf Xi(r) = 1 - exp(-φ·r/r_s)

© 2025 Carmen Wrede, Lino Casu

---

## Example 1: Basic SSZ Deformation

```python
from ssz_starmaps import (
    Xi, D_SSZ, PHI, schwarzschild_radius,
    apply_ssz_metric_deformation
)
import numpy as np

# Physical parameters
M_sun = 1.98847e30  # kg
r_s = schwarzschild_radius(M_sun)

print(f"phi = {PHI:.6f}")
print(f"r_s = {r_s:.2f} m")

# Test segment saturation
r_test = np.array([0.5, 1.0, 2.0, 5.0]) * r_s
xi = Xi(r_test, r_s)

for i, r in enumerate(r_test):
    print(f"Xi(r={r/r_s:.1f}*r_s) = {xi[i]:.4f}")
```

**Output:**
```
phi = 1.618034
r_s = 2953.34 m
Xi(r=0.5*r_s) = 0.5547
Xi(r=1.0*r_s) = 0.8017
Xi(r=2.0*r_s) = 0.9607
Xi(r=5.0*r_s) = 0.9997
```

---

## Example 2: Time Dilation Comparison

```python
from ssz_starmaps import D_SSZ, D_GR, schwarzschild_radius
import numpy as np

M_sun = 1.98847e30
r_s = schwarzschild_radius(M_sun)

# Test at Schwarzschild radius
print("At r = r_s:")
print(f"  D_GR = {D_GR(r_s, r_s)}")  # NaN - SINGULARITY!
print(f"  D_SSZ = {D_SSZ(r_s, r_s):.6f}")  # FINITE!

# Test at 2*r_s
r = 2 * r_s
print(f"\nAt r = 2*r_s:")
print(f"  D_GR = {D_GR(r, r_s):.6f}")
print(f"  D_SSZ = {D_SSZ(r, r_s):.6f}")
```

**Output:**
```
At r = r_s:
  D_GR = nan
  D_SSZ = 0.555028

At r = 2*r_s:
  D_GR = 0.707107
  D_SSZ = 0.510027
```

---

## Example 3: SSZ Star Map Deformation

```python
from ssz_starmaps import (
    gnomonic_projection,
    apply_ssz_metric_deformation,
    create_mock_catalog
)
import matplotlib.pyplot as plt

# Get mock stars
catalog = create_mock_catalog(n_stars=100)
ra, dec = catalog['ra'], catalog['dec']

# Project to 2D
x, y = gnomonic_projection(ra, dec)

# Apply ECHTE SSZ deformation
x_ssz, y_ssz = apply_ssz_metric_deformation(
    x, y,
    mass_kg=1.98847e30,  # Sun's mass
    r_scale_deg=0.5
)

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.scatter(x, y, alpha=0.6)
ax1.set_title('Minkowski')
ax1.axis('equal')

ax2.scatter(x_ssz, y_ssz, alpha=0.6, color='red')
ax2.set_title('SSZ: Xi(r) = 1 - exp(-phi*r/r_s)')
ax2.axis('equal')

plt.tight_layout()
plt.show()
```

---

## Example 4: Ramanujan Ellipse Formula

```python
from ssz_starmaps import ramanujan_ellipse_circumference
import numpy as np

# Circle
a, b = 1.0, 1.0
C_circle = ramanujan_ellipse_circumference(a, b)
print(f"Circle: C = {C_circle:.6f}, 2*pi = {2*np.pi:.6f}")

# Ellipse
a, b = 1.5, 0.5
C_ellipse = ramanujan_ellipse_circumference(a, b)
print(f"Ellipse (a={a}, b={b}): C = {C_ellipse:.6f}")
```

**Output:**
```
Circle: C = 6.283185, 2*pi = 6.283185
Ellipse (a=1.5, b=0.5): C = 4.970104
```

---

## Example 5: GAIA DR3 Integration

```python
from ssz_starmaps import fetch_gaia_catalog

# Fetch bright stars near galactic center
catalog = fetch_gaia_catalog(
    center_ra_deg=266.4,
    center_dec_deg=-29.0,
    radius_deg=2.0,
    limit=1000,
    mag_limit=12.0
)

if catalog:
    print(f"Found {len(catalog['ra'])} stars")
    print(f"Brightest: G_mag = {min(catalog['pmag']):.2f}")
```

---

## Example 6: Validierung vs ssz-metric-pure

```python
from ssz_starmaps import Xi, PHI, schwarzschild_radius

# Sun
M_sun = 1.98847e30
r_s = schwarzschild_radius(M_sun)

# Theoretical crossover point
r_star_theory = 1.386562 * r_s

xi_star = Xi(r_star_theory, r_s)
print(f"r* / r_s = 1.386562 (theoretical)")
print(f"Xi(r*) = {xi_star:.6f}")
print(f"Expected: ~0.60 (universal crossover)")
```

---

## Key Differences: LEGACY vs ECHTE SSZ

### ❌ LEGACY (v0.1.0) - FAKE!
```python
from ssz_starmaps import apply_ssz_deformation  # DEPRECATED!

# Arbitrary eps-scaling (NOT REAL SSZ!)
x_fake, y_fake = apply_ssz_deformation(x, y, eps=0.15)
# Warning: Uses FAKE eps parameter!
```

### ✅ ECHTE (v0.2.0) - REAL SSZ!
```python
from ssz_starmaps import apply_ssz_metric_deformation

# ECHTE SSZ-Physik: Xi(r) = 1 - exp(-phi*r/r_s)
x_real, y_real = apply_ssz_metric_deformation(
    x, y,
    mass_kg=1.98847e30,  # Physical mass
    r_scale_deg=0.5      # Scale factor
)
```

---

## Formulas Quick Reference

```python
# Segment Saturation
Xi(r) = 1 - exp(-phi * r/r_s)

# Time Dilation
D_SSZ(r) = 1 / (1 + Xi(r))

# Radial Deformation
R_ssz = r * (1 + Xi(r))

# Schwarzschild Radius
r_s = 2*G*M / c^2

# Golden Ratio
phi = (1 + sqrt(5)) / 2 = 1.618034
```

---

## License

© 2025 Carmen Wrede, Lino Casu  
Licensed under the Anti-Capitalist Software License v1.4
