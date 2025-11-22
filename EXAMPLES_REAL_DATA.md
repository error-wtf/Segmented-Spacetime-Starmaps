# Real Data Examples - SSZ StarMaps

**Complete usage examples with GAIA DR3 and SIMBAD data**

---

## Example 1: Nearby Stars (Simple)

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog
from ssz_starmaps.viz import plot_sky_comparison

# Fetch 100 nearest stars
manager = CatalogManager()
stars = manager.fetch_nearby(distance_pc=50, max_stars=100)

# Transform with SSZ
stars_ssz = transform_catalog(stars)

# Visualize
plot_sky_comparison(stars_ssz, output='nearby_50pc.png')

print(f"Processed {len(stars_ssz)} stars")
print(f"Mean stretch: {stars_ssz['stretch_factor'].mean():.4f}")
```

**Output:** `nearby_50pc.png` (side-by-side comparison)

---

## Example 2: Orion Nebula Region

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog, print_statistics
from ssz_starmaps.viz import plot_sky_comparison, plot_distance_histogram

# Orion Nebula (pre-defined region)
manager = CatalogManager()
stars = manager.fetch_interesting('orion', max_stars=500)

print(f"Fetched {len(stars)} stars in Orion region")

# Transform
stars_ssz = transform_catalog(stars)

# Statistics
print_statistics(stars_ssz)

# Plots
plot_sky_comparison(stars_ssz, output='orion_sky.png')
plot_distance_histogram(stars_ssz, output='orion_histogram.png')

# Save
stars_ssz.to_csv('orion_ssz.csv', index=False)
```

---

## Example 3: Named Stars (Famous Stars)

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog

manager = CatalogManager()

# Fetch famous stars
stars = manager.fetch_famous_stars()

# Or specific stars
# stars = manager.fetch_named(['Sirius', 'Vega', 'Arcturus', 'Betelgeuse'])

print(f"Fetched {len(stars)} stars:")
for _, star in stars.iterrows():
    print(f"  - {star['name']}: {star['distance_pc']:.1f} pc")

# Transform
stars_ssz = transform_catalog(stars)

# Analyze stretch
for _, star in stars_ssz.iterrows():
    name = star['name']
    stretch = star['stretch_factor']
    print(f"{name:20s} stretch: {stretch:.6f}")
```

---

## Example 4: Custom Region (Cone Search)

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog
from ssz_starmaps.viz import plot_sky_comparison

# Custom region around Polaris
manager = CatalogManager()
stars = manager.fetch_region(
    ra=37.95,      # Polaris RA
    dec=89.26,     # Polaris Dec (near pole)
    radius=5.0,    # 5 degree radius
    max_stars=300
)

print(f"Found {len(stars)} stars near Polaris")

# Transform and plot
stars_ssz = transform_catalog(stars)
plot_sky_comparison(
    stars_ssz,
    output='polaris_region.png',
    fov_center=(37.95, 89.26),
    fov_deg=10
)
```

---

## Example 5: Bright Stars Comparison

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog
import matplotlib.pyplot as plt

manager = CatalogManager()

# Fetch bright stars (naked eye visible)
stars = manager.fetch_bright_stars(mag_limit=3.0, max_stars=100)

# Transform
stars_ssz = transform_catalog(stars)

# Plot stretch vs distance
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(
    stars_ssz['distance_pc'],
    stars_ssz['stretch_factor'],
    alpha=0.6,
    s=100
)
ax.set_xlabel('Distance [pc]')
ax.set_ylabel('SSZ Stretch Factor')
ax.set_title('Radial Stretch vs Distance (Bright Stars)')
ax.grid(True, alpha=0.3)
plt.savefig('stretch_vs_distance.png', dpi=300)
```

---

## Example 6: Multiple Regions Batch

```python
from ssz_starmaps.catalogs import CatalogManager, INTERESTING_REGIONS
from ssz_starmaps.transform import transform_catalog
from pathlib import Path

manager = CatalogManager()
output_dir = Path('multi_region_analysis')
output_dir.mkdir(exist_ok=True)

results = {}

for region_name in ['orion', 'pleiades', 'andromeda']:
    print(f"\nProcessing {region_name}...")
    
    # Fetch
    stars = manager.fetch_interesting(region_name, max_stars=300)
    
    # Transform
    stars_ssz = transform_catalog(stars, show_progress=False)
    
    # Save
    stars_ssz.to_csv(output_dir / f'{region_name}_ssz.csv', index=False)
    
    # Store stats
    results[region_name] = {
        'n_stars': len(stars_ssz),
        'mean_stretch': stars_ssz['stretch_factor'].mean(),
        'mean_distance': stars_ssz['distance_pc'].mean()
    }

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
for region, stats in results.items():
    print(f"{region:15s}: {stats['n_stars']:3d} stars, "
          f"<stretch>={stats['mean_stretch']:.4f}, "
          f"<d>={stats['mean_distance']:.1f} pc")
```

---

## Example 7: Offline Mode (No Internet)

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog
from ssz_starmaps.viz import plot_sky_comparison

# Offline mode with mock catalog
manager = CatalogManager(offline=True)

# Generate mock stars
stars = manager.fetch_nearby(distance_pc=100, max_stars=200)

print("Using mock catalog (offline mode)")

# Transform and visualize (same as online)
stars_ssz = transform_catalog(stars)
plot_sky_comparison(stars_ssz, output='mock_comparison.png')
```

---

## Example 8: With Caching

```python
from ssz_starmaps.catalogs import CatalogManager
from pathlib import Path

manager = CatalogManager(cache_dir='my_cache')

# First run: fetches from GAIA
print("First run (fetching)...")
stars1 = manager.fetch_nearby(distance_pc=100, max_stars=500, use_cache=True)

# Second run: loads from cache (instant!)
print("Second run (cached)...")
stars2 = manager.fetch_nearby(distance_pc=100, max_stars=500, use_cache=True)

assert len(stars1) == len(stars2), "Cache works!"

# Clear cache if needed
# manager.clear_cache()
```

---

## Example 9: Advanced Statistics

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog, compute_statistics
import json

manager = CatalogManager()
stars = manager.fetch_nearby(distance_pc=100, max_stars=500)
stars_ssz = transform_catalog(stars)

# Compute statistics
stats = compute_statistics(stars_ssz)

# Save statistics
with open('ssz_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print("Statistics saved to ssz_stats.json")
print(f"Mean stretch: {stats['mean_stretch']:.6f}")
print(f"Std dev: {stats['std_stretch']:.6f}")
```

---

## Example 10: 3D Visualization

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog
from ssz_starmaps.viz import plot_3d_comparison

manager = CatalogManager()
stars = manager.fetch_nearby(distance_pc=50, max_stars=200)
stars_ssz = transform_catalog(stars)

# 3D scatter plot
plot_3d_comparison(
    stars_ssz,
    output='stars_3d.png',
    elev=30,
    azim=45
)
```

---

## Example 11: Paper-Quality Plots

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog
from ssz_starmaps.viz import plot_sky_comparison, plot_distance_histogram

manager = CatalogManager()
stars = manager.fetch_interesting('orion', max_stars=1000)
stars_ssz = transform_catalog(stars)

# High-resolution for papers
plot_sky_comparison(
    stars_ssz,
    output='paper_fig1_orion_comparison.png',
    dpi=600,  # High DPI
    figsize=(20, 10)  # Large figure
)

plot_distance_histogram(
    stars_ssz,
    output='paper_fig2_orion_histogram.png',
    dpi=600,
    bins=100
)
```

---

## Example 12: All Regions at Once

**See:** `scripts/batch_process_regions.py`

```bash
# Process all pre-defined regions
python scripts/batch_process_regions.py --all

# Process specific region
python scripts/batch_process_regions.py --region orion --max-stars 1000

# Output structure:
# batch_outputs/
# ├── orion/
# │   ├── orion_sky_comparison.png
# │   ├── orion_distance_histogram.png
# │   └── orion_ssz.csv
# ├── pleiades/
# │   └── ...
# └── andromeda/
#     └── ...
```

---

## Available Pre-Defined Regions

```python
from ssz_starmaps.catalogs import INTERESTING_REGIONS

for name, info in INTERESTING_REGIONS.items():
    print(f"{name:20s}: {info['name']}")

# Output:
# orion               : Orion Nebula
# pleiades            : Pleiades (M45)
# andromeda           : Andromeda Galaxy
# cygnus              : Cygnus Region
# galactic_center     : Galactic Center
```

---

## Troubleshooting

### GAIA Query Timeout

```python
# Use smaller max_sources
stars = manager.fetch_nearby(distance_pc=50, max_stars=100)

# Or use cache
stars = manager.fetch_nearby(distance_pc=100, use_cache=True)
```

### Memory Issues with Large Catalogs

```python
# Process in chunks
from ssz_starmaps.transform import TransformConfig

config = TransformConfig(parallel=False)  # Disable parallel
stars_ssz = transform_catalog(large_catalog, config=config)
```

### Offline Usage

```python
manager = CatalogManager(offline=True)
stars = manager.fetch_nearby(distance_pc=100, max_stars=500)
# Uses mock catalog automatically
```

---

## Next Steps

- See `QUICK_START.md` for installation
- See `API_REFERENCE.md` for full function documentation
- See `ROADMAP_REAL_STARMAPS.md` for future features

---

© 2025 Carmen Wrede, Lino Casu  
Licensed under the Anti-Capitalist Software License v1.4
