# Roadmap: Echte Sternkarten mit Astropy

**Datum:** 2025-11-22  
**Ziel:** Vollständige Integration echter astronomischer Daten  
**Status:** Production-Ready Roadmap

---

## ✅ Phase 0: SOFORT ERLEDIGEN (JETZT!)

### 0.1 README Update

**File:** `README.md` - Section "Validation Status" hinzufügen

```markdown
## ✅ Validation Status (NEW!)

**This implementation has been validated against 161 tests** from the Mass-Projection repository.

### Validated Results:
- ✅ r*/r_s = 1.386549 (expected: 1.386562, error: 0.001%)
- ✅ D_SSZ(r_s) = 0.555028 (finite! GR diverges)
- ✅ PPN β = γ = 1.0 (GR match)
- ✅ Dual velocity: v·v = c² (error < 10^-16)

See `MASS_PROJECTION_REPO_ANALYSIS.md` and `validate_against_mass_projection.py`.
```

### 0.2 Dependencies Update

**File:** `pyproject.toml`

```toml
dependencies = [
    "numpy>=1.24.0",
    "matplotlib>=3.7.0",
    "astropy>=5.3.0",
    "astroquery>=0.4.6",
    "scipy>=1.10.0",
    "pandas>=2.0.0",
    "tqdm>=4.65.0",
]

[project.optional-dependencies]
interactive = [
    "plotly>=5.17.0",
    "ipywidgets>=8.1.0",
]
```

### 0.3 Legacy Code Deprecation

**File:** `projection.py` - Bereits markiert ✓

---

## 📚 Phase 1: Catalog System (Week 1)

### Neue Files erstellen:

```
src/ssz_starmaps/catalogs/
├── __init__.py
├── manager.py          # Unified catalog manager
├── gaia_fetch.py       # GAIA DR3 queries
├── simbad_fetch.py     # SIMBAD queries
└── mock.py             # Offline mock catalogs
```

### Key Features:

**1. GAIA DR3 Integration**
```python
from astroquery.gaia import Gaia

# Cone search
def fetch_gaia_cone(ra, dec, radius_deg, max_stars=1000):
    query = f"""
    SELECT TOP {max_stars}
        source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag
    FROM gaiadr3.gaia_source
    WHERE 1=CONTAINS(POINT('ICRS', ra, dec), 
                     CIRCLE('ICRS', {ra}, {dec}, {radius_deg}))
    AND parallax > 0 AND parallax_over_error > 5
    ORDER BY phot_g_mean_mag ASC
    """
    job = Gaia.launch_job(query)
    return job.get_results().to_pandas()
```

**2. Named Stars**
```python
from astroquery.simbad import Simbad

def fetch_named_star(name):
    Simbad.add_votable_fields('sptype', 'distance', 'flux(V)')
    result = Simbad.query_object(name)
    return result.to_pandas()
```

---

## 🔄 Phase 2: Transform Pipeline (Week 1-2)

### Neue Files:

```
src/ssz_starmaps/transform/
├── __init__.py
├── batch.py           # Batch processing
└── coordinates.py     # Coordinate transformations
```

### Batch Transform:

```python
from joblib import Parallel, delayed
from tqdm import tqdm

def transform_catalog(stars_df, mass_kg=1.989e30):
    """Apply SSZ to entire catalog."""
    
    def transform_one(row):
        r_m = row['distance_pc'] * 3.086e16
        r_s = schwarzschild_radius(mass_kg)
        xi = Xi(r_m, r_s)
        stretch = radial_stretch(r_m, r_s)
        
        return {
            'name': row['name'],
            'ra': row['ra'],
            'dec': row['dec'],
            'distance_pc': row['distance_pc'],
            'distance_ssz_pc': row['distance_pc'] * stretch,
            'xi': xi,
            'stretch': stretch
        }
    
    results = Parallel(n_jobs=-1)(
        delayed(transform_one)(row) 
        for _, row in tqdm(stars_df.iterrows(), total=len(stars_df))
    )
    
    return pd.DataFrame(results)
```

---

## 📊 Phase 3: Visualization (Week 2)

### Neue Files:

```
src/ssz_starmaps/viz/
├── __init__.py
├── compare.py         # Side-by-side plots
├── interactive.py     # Plotly dashboards
└── export.py          # Export for papers
```

### Side-by-Side Plots:

```python
def plot_sky_comparison(df, output='comparison.png'):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left: Minkowski
    ax1.scatter(df['ra'], df['dec'], s=100/df['distance_pc'], c='blue')
    ax1.set_title('Minkowski (Standard)')
    
    # Right: SSZ
    ax2.scatter(df['ra'], df['dec'], s=100/df['distance_ssz_pc'], c='red')
    ax2.set_title('SSZ (φ-Deformed)')
    
    # Add parameters
    ax2.text(0.02, 0.98, f"φ = {PHI:.6f}\nr_s = 2953 m", 
             transform=ax2.transAxes, va='top')
    
    plt.savefig(output, dpi=300)
```

---

## 🚀 Phase 4: Production Scripts (Week 2-3)

### Main Demo Script:

**File:** `demo_starmap.py` (Update)

```python
#!/usr/bin/env python3
"""SSZ StarMaps - Real GAIA Data"""

import argparse
from ssz_starmaps.catalogs.gaia_fetch import fetch_gaia_nearby
from ssz_starmaps.transform.batch import transform_catalog
from ssz_starmaps.viz.compare import plot_sky_comparison

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--distance-pc', type=float, default=100)
    parser.add_argument('--max-stars', type=int, default=1000)
    parser.add_argument('--output', default='outputs')
    args = parser.parse_args()
    
    print("Fetching GAIA stars...")
    stars = fetch_gaia_nearby(args.distance_pc, args.max_stars)
    
    print("Applying SSZ transformation...")
    stars_ssz = transform_catalog(stars)
    
    print("Generating plots...")
    plot_sky_comparison(stars_ssz, f'{args.output}/comparison.png')
    stars_ssz.to_csv(f'{args.output}/stars_ssz.csv', index=False)
    
    print(f"Done! Check {args.output}/")

if __name__ == '__main__':
    main()
```

### Batch Processing:

**New File:** `scripts/batch_process.py`

```python
REGIONS = {
    'orion': (83.8, -5.4, 10),
    'pleiades': (56.75, 24.12, 5),
    'andromeda': (10.68, 41.27, 3),
}

for name, (ra, dec, radius) in REGIONS.items():
    print(f"Processing {name}...")
    stars = fetch_gaia_cone(ra, dec, radius)
    stars_ssz = transform_catalog(stars)
    stars_ssz.to_csv(f'{name}_ssz.csv', index=False)
```

---

## 📖 Phase 5: Documentation (Week 3)

### Neue Docs:

1. **EXAMPLES_REAL_DATA.md** - Code examples
2. **API_REFERENCE.md** - Full API docs
3. **PAPER_READY_PLOTS.md** - Publication-quality figures

---

## Timeline Summary

| Week | Phase | Deliverables |
|------|-------|--------------|
| **Week 1** | 0-2 | Catalog system + Transform pipeline |
| **Week 2** | 3-4 | Visualization + Production scripts |
| **Week 3** | 5 | Documentation + Testing |

---

## Success Criteria

### After Week 1:
- ✅ Fetch 1000 stars from GAIA DR3
- ✅ Transform with SSZ
- ✅ Save to CSV

### After Week 2:
- ✅ Side-by-side plots (Minkowski vs SSZ)
- ✅ Distance histogram comparisons
- ✅ Batch processing for multiple regions

### After Week 3:
- ✅ Complete documentation
- ✅ Paper-ready plots (300 DPI)
- ✅ Integration tests passing

---

## Quick Start Commands (AFTER IMPLEMENTATION)

```bash
# Install with real data support
pip install -e .[interactive]

# Fetch 100 nearby stars and transform
python -m ssz_starmaps.demo_starmap --distance-pc 50 --max-stars 100

# Process Orion region
python scripts/batch_process.py --region orion

# Generate comparison plots
python -m ssz_starmaps.viz.compare --input stars.csv --output comparison.png
```

---

**See IMPLEMENTATION_CHECKLIST.md for detailed step-by-step tasks.**

© 2025 Carmen Wrede, Lino Casu
