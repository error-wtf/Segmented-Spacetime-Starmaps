# Quick Start: SSZ StarMaps mit echten GAIA-Daten

**Ready in 3 Minuten!** 🚀

---

## Installation

```bash
cd E:\clone\Segmented-Spacetime-StarMaps

# Install dependencies
pip install -e .

# Or with interactive tools
pip install -e .[interactive]
```

---

## Quick Demo (100 Stars)

```bash
python demo_quick_start.py
```

**Output:**
```
outputs_quick_start/
├── sky_comparison.png        # Minkowski vs SSZ side-by-side
├── distance_histogram.png    # Distance distributions
└── stars_ssz.csv             # Transformed catalog
```

**Runtime:** ~30 seconds (with GAIA fetch)

---

## Usage Examples

### 1. Fetch Nearby Stars

```python
from ssz_starmaps.catalogs import CatalogManager

manager = CatalogManager()

# 100 nearest stars within 100 parsecs
stars = manager.fetch_nearby(distance_pc=100, max_stars=100)

print(f"Found {len(stars)} stars")
```

### 2. Apply SSZ Transformation

```python
from ssz_starmaps.transform import transform_catalog

stars_ssz = transform_catalog(stars)

# Check results
mean_stretch = stars_ssz['stretch_factor'].mean()
print(f"Average radial stretch: {mean_stretch:.4f}")
```

### 3. Visualize

```python
from ssz_starmaps.viz import plot_sky_comparison

plot_sky_comparison(stars_ssz, output='comparison.png')
```

---

## Pre-Defined Regions

```python
# Orion Nebula
stars = manager.fetch_interesting('orion', max_stars=500)

# Pleiades
stars = manager.fetch_interesting('pleiades', max_stars=300)

# Available regions:
regions = manager.list_regions()
# ['orion', 'pleiades', 'andromeda', 'cygnus', 'galactic_center']
```

---

## Offline Mode (No Internet)

```python
manager = CatalogManager(offline=True)

# Uses mock catalog
stars = manager.fetch_nearby(distance_pc=50, max_stars=100)
```

---

## Full Pipeline Example

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog, print_statistics
from ssz_starmaps.viz import plot_sky_comparison, plot_distance_histogram

# Fetch
manager = CatalogManager()
stars = manager.fetch_nearby(distance_pc=50, max_stars=200)

# Transform
stars_ssz = transform_catalog(stars)

# Statistics
print_statistics(stars_ssz)

# Plots
plot_sky_comparison(stars_ssz, output='sky.png')
plot_distance_histogram(stars_ssz, output='histogram.png')

# Save
stars_ssz.to_csv('stars_ssz.csv', index=False)
```

---

## Validated Physics

This implementation is **validated against 161 tests** from the Mass-Projection repository:

| Test | Status |
|------|--------|
| r*/r_s = 1.387 | ✅ 0.001% error |
| PPN β = γ = 1 | ✅ Perfect match |
| Singularity-free | ✅ D(r_s) finite |
| Dual velocity | ✅ < 10^-16 error |

See `MASS_PROJECTION_REPO_ANALYSIS.md` for details.

---

## Troubleshooting

### GAIA Query Fails

```python
# Use cached data
stars = manager.fetch_nearby(distance_pc=100, use_cache=True)

# Or offline mode
manager = CatalogManager(offline=True)
stars = manager.fetch_nearby(distance_pc=100)
```

### Import Errors

```bash
# Install missing dependencies
pip install astropy astroquery pandas matplotlib scipy tqdm
```

---

## Next Steps

- See `EXAMPLES_REAL_DATA.md` for advanced examples
- See `API_REFERENCE.md` for full API documentation
- See `ROADMAP_REAL_STARMAPS.md` for development roadmap

---

© 2025 Carmen Wrede, Lino Casu  
Licensed under the Anti-Capitalist Software License v1.4
