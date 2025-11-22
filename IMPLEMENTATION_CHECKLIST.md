# Implementation Checklist - Echte Sternkarten

**Start:** 2025-11-22  
**Deadline:** 3 Wochen  
**Status:** Ready to begin!

---

## 🔧 PHASE 0: PRE-FLIGHT (JETZT SOFORT!)

### ✅ Task 0.1: README Update
**File:** `README.md`  
**Action:** Validation-Section hinzufügen nach Zeile 73

- [ ] Section "Validation Status" erstellen
- [ ] Link zu `MASS_PROJECTION_REPO_ANALYSIS.md`
- [ ] Link zu `validate_against_mass_projection.py`
- [ ] Testergebnisse einf ügen (r*, D, PPN, dual velocity)

**Estimated Time:** 15 min

---

### ✅ Task 0.2: Dependencies Update
**File:** `pyproject.toml`

- [ ] Update `scipy>=1.10.0` hinzufügen
- [ ] `pandas>=2.0.0` hinzufügen
- [ ] `tqdm>=4.65.0` hinzufügen
- [ ] Optional dependencies `[interactive]` section erstellen
- [ ] `plotly>=5.17.0` in optional
- [ ] Version bump auf 0.2.0

**Estimated Time:** 10 min

---

### ✅ Task 0.3: Test Existing Code
**Commands:**

```bash
cd E:\clone\Segmented-Spacetime-StarMaps

# Run validation
python validate_against_mass_projection.py

# Run unit tests
python test_xi_validated.py

# Check imports
python -c "from ssz_starmaps import *; print('OK')"
```

- [ ] All validations pass
- [ ] All unit tests pass
- [ ] No import errors

**Estimated Time:** 5 min

---

## 📚 PHASE 1: CATALOG SYSTEM

### Task 1.1: Create Directory Structure

```bash
mkdir -p src/ssz_starmaps/catalogs
mkdir -p src/ssz_starmaps/transform
mkdir -p src/ssz_starmaps/viz
mkdir -p scripts
mkdir -p tests/integration
```

- [ ] Directories created
- [ ] Add `__init__.py` to each module

**Estimated Time:** 5 min

---

### Task 1.2: GAIA Fetch Module
**File:** `src/ssz_starmaps/catalogs/gaia_fetch.py`

**Code to implement:**
```python
from astroquery.gaia import Gaia
import pandas as pd

def fetch_gaia_nearby(distance_pc=100, max_sources=1000):
    """Fetch nearby stars from GAIA DR3."""
    min_parallax = 1000 / distance_pc
    query = f"""
    SELECT TOP {max_sources}
        source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag
    FROM gaiadr3.gaia_source
    WHERE parallax > {min_parallax}
    AND parallax_over_error > 5
    ORDER BY parallax DESC
    """
    job = Gaia.launch_job(query)
    return job.get_results().to_pandas()

def fetch_gaia_cone(ra, dec, radius_deg, max_sources=1000):
    """Fetch stars in cone search."""
    # TODO: Implement
    pass
```

**Checklist:**
- [ ] Create file
- [ ] Implement `fetch_gaia_nearby()`
- [ ] Implement `fetch_gaia_cone()`
- [ ] Add docstrings
- [ ] Test with 10 stars
- [ ] Handle errors gracefully

**Estimated Time:** 45 min

---

### Task 1.3: SIMBAD Fetch Module
**File:** `src/ssz_starmaps/catalogs/simbad_fetch.py`

```python
from astroquery.simbad import Simbad

Simbad.add_votable_fields('sptype', 'distance', 'flux(V)')

def fetch_named_star(name):
    """Fetch single star by name."""
    result = Simbad.query_object(name)
    if result is None:
        return None
    return result.to_pandas()

def fetch_bright_stars(mag_limit=3.0):
    """Fetch bright stars."""
    # TODO: Implement
    pass
```

**Checklist:**
- [ ] Create file
- [ ] Implement `fetch_named_star()`
- [ ] Implement `fetch_bright_stars()`
- [ ] Test with "Sirius"
- [ ] Add error handling

**Estimated Time:** 30 min

---

### Task 1.4: Catalog Manager
**File:** `src/ssz_starmaps/catalogs/manager.py`

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class StarEntry:
    name: str
    ra: float
    dec: float
    distance_pc: float
    vmag: Optional[float] = None
    source: str = "unknown"

class CatalogManager:
    def __init__(self, cache_dir="~/.ssz_catalogs", offline=False):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(exist_ok=True)
        self.offline = offline
    
    def fetch_nearby(self, distance_pc=100, max_stars=1000):
        """Fetch nearby stars (GAIA or cached)."""
        # TODO: Implement with caching
        pass
```

**Checklist:**
- [ ] Create `StarEntry` dataclass
- [ ] Implement `CatalogManager`
- [ ] Add caching support
- [ ] Offline mode with mock data
- [ ] Unit tests

**Estimated Time:** 60 min

---

## 🔄 PHASE 2: TRANSFORM PIPELINE

### Task 2.1: Batch Transform Module
**File:** `src/ssz_starmaps/transform/batch.py`

```python
from joblib import Parallel, delayed
from tqdm import tqdm
import pandas as pd
from ..ssz_metric import Xi, schwarzschild_radius, radial_stretch

def transform_star(star_row, mass_kg):
    """Transform single star."""
    r_m = star_row['distance_pc'] * 3.086e16
    r_s = schwarzschild_radius(mass_kg)
    
    xi = Xi(r_m, r_s)
    stretch = radial_stretch(r_m, r_s)
    
    return {
        'name': star_row.get('name', 'N/A'),
        'ra': star_row['ra'],
        'dec': star_row['dec'],
        'distance_pc': star_row['distance_pc'],
        'distance_ssz_pc': star_row['distance_pc'] * stretch,
        'xi': float(xi),
        'stretch_factor': float(stretch)
    }

def transform_catalog(df, mass_kg=1.989e30, parallel=True):
    """Transform entire catalog."""
    if parallel:
        results = Parallel(n_jobs=-1)(
            delayed(transform_star)(row, mass_kg)
            for _, row in tqdm(df.iterrows(), total=len(df))
        )
    else:
        results = [transform_star(row, mass_kg) 
                  for _, row in tqdm(df.iterrows(), total=len(df))]
    
    return pd.DataFrame(results)
```

**Checklist:**
- [ ] Create file
- [ ] Implement `transform_star()`
- [ ] Implement `transform_catalog()`
- [ ] Add progress bars
- [ ] Parallel processing option
- [ ] Test with 100 stars

**Estimated Time:** 45 min

---

### Task 2.2: Coordinate Helpers
**File:** Enhancement to `src/ssz_starmaps/geometry.py`

```python
def equatorial_to_cartesian_ssz(ra, dec, distance_pc, apply_ssz=True):
    """Convert to Cartesian with optional SSZ deformation."""
    # Standard conversion
    x, y, z = equatorial_to_cartesian(ra, dec, distance_pc)
    
    if apply_ssz:
        r_m = distance_pc * 3.086e16
        r_s = schwarzschild_radius(1.989e30)
        stretch = radial_stretch(r_m, r_s)
        x *= stretch
        y *= stretch
        z *= stretch
    
    return x, y, z
```

**Checklist:**
- [ ] Add function to `geometry.py`
- [ ] Test SSZ vs non-SSZ conversion
- [ ] Add docstring
- [ ] Update imports in `__init__.py`

**Estimated Time:** 20 min

---

## 📊 PHASE 3: VISUALIZATION

### Task 3.1: Comparison Plots
**File:** `src/ssz_starmaps/viz/compare.py`

```python
import matplotlib.pyplot as plt

def plot_sky_comparison(df, output='comparison.png', dpi=300):
    """Side-by-side: Minkowski vs SSZ."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left: Minkowski
    ax1.scatter(df['ra'], df['dec'], 
               s=100/df['distance_pc'], 
               alpha=0.6, c='blue', edgecolors='white', linewidths=0.5)
    ax1.set_xlabel('RA [deg]', fontsize=12)
    ax1.set_ylabel('Dec [deg]', fontsize=12)
    ax1.set_title('Minkowski (Standard Spacetime)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Right: SSZ
    ax2.scatter(df['ra'], df['dec'],
               s=100/df['distance_ssz_pc'],
               alpha=0.6, c='red', edgecolors='white', linewidths=0.5)
    ax2.set_xlabel('RA [deg]', fontsize=12)
    ax2.set_ylabel('Dec [deg]', fontsize=12)
    ax2.set_title('SSZ (φ-Deformed)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add SSZ parameters
    phi = 1.618034
    r_s = 2953
    text = f"SSZ Parameters:\nφ = {phi:.6f}\nr_s = {r_s:.0f} m"
    ax2.text(0.02, 0.98, text, transform=ax2.transAxes,
            va='top', fontsize=10, family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(output, dpi=dpi, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output}")

def plot_distance_histogram(df, output='histogram.png', bins=50):
    """Compare distance distributions."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Minkowski
    ax1.hist(df['distance_pc'], bins=bins, alpha=0.7, color='blue', edgecolor='black')
    ax1.set_xlabel('Distance [pc]')
    ax1.set_ylabel('Count')
    ax1.set_title('Minkowski Distance Distribution')
    ax1.grid(True, alpha=0.3)
    
    # SSZ
    ax2.hist(df['distance_ssz_pc'], bins=bins, alpha=0.7, color='red', edgecolor='black')
    ax2.set_xlabel('Distance [pc]')
    ax2.set_ylabel('Count')
    ax2.set_title('SSZ Distance Distribution (φ-Stretched)')
    ax2.grid(True, alpha=0.3)
    
    # Statistics
    mean_stretch = (df['distance_ssz_pc'] / df['distance_pc']).mean()
    stats = f"Average Stretch Factor: {mean_stretch:.4f}"
    ax2.text(0.98, 0.98, stats, transform=ax2.transAxes,
            ha='right', va='top', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output}")
```

**Checklist:**
- [ ] Create `viz/` directory
- [ ] Implement `plot_sky_comparison()`
- [ ] Implement `plot_distance_histogram()`
- [ ] Test with sample data
- [ ] Add to `__init__.py`

**Estimated Time:** 60 min

---

## 🚀 PHASE 4: PRODUCTION SCRIPTS

### Task 4.1: Update Main Demo
**File:** `src/ssz_starmaps/demo_starmap.py`

```python
#!/usr/bin/env python3
"""SSZ StarMaps Demo - Real GAIA Data"""

import argparse
from pathlib import Path

from .catalogs.gaia_fetch import fetch_gaia_nearby
from .transform.batch import transform_catalog
from .viz.compare import plot_sky_comparison, plot_distance_histogram

def main():
    parser = argparse.ArgumentParser(description='Generate SSZ star maps')
    parser.add_argument('--distance-pc', type=float, default=100)
    parser.add_argument('--max-stars', type=int, default=1000)
    parser.add_argument('--output-dir', type=Path, default='outputs')
    args = parser.parse_args()
    
    args.output_dir.mkdir(exist_ok=True)
    
    print("="*80)
    print("SSZ STARMAPS - Real GAIA DR3 Data")
    print("="*80)
    print(f"Distance limit: {args.distance_pc} pc")
    print(f"Max stars: {args.max_stars}")
    print()
    
    # Step 1: Fetch
    print("[1/4] Fetching GAIA stars...")
    stars_df = fetch_gaia_nearby(args.distance_pc, args.max_stars)
    print(f"  Fetched: {len(stars_df)} stars")
    
    # Step 2: Transform
    print("[2/4] Applying SSZ transformation...")
    stars_ssz = transform_catalog(stars_df)
    print(f"  Transformed: {len(stars_ssz)} stars")
    
    # Step 3: Plot
    print("[3/4] Generating plots...")
    plot_sky_comparison(stars_ssz, args.output_dir / 'sky_comparison.png')
    plot_distance_histogram(stars_ssz, args.output_dir / 'distance_histogram.png')
    
    # Step 4: Save
    print("[4/4] Saving data...")
    stars_ssz.to_csv(args.output_dir / 'stars_ssz.csv', index=False)
    print(f"  Saved: stars_ssz.csv")
    
    print()
    print("="*80)
    print("COMPLETE! Check outputs/ directory")
    print("="*80)

if __name__ == '__main__':
    main()
```

**Checklist:**
- [ ] Update file with new structure
- [ ] Add argparse
- [ ] Test with --distance-pc 50 --max-stars 100
- [ ] Verify outputs generated
- [ ] Add to README usage section

**Estimated Time:** 30 min

---

### Task 4.2: Batch Processing Script
**File:** `scripts/batch_process_regions.py`

```python
#!/usr/bin/env python3
"""Batch process multiple interesting sky regions."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ssz_starmaps.catalogs.gaia_fetch import fetch_gaia_cone
from ssz_starmaps.transform.batch import transform_catalog
from ssz_starmaps.viz.compare import plot_sky_comparison

REGIONS = {
    'orion': (83.8, -5.4, 10),       # Orion Nebula
    'pleiades': (56.75, 24.12, 5),   # Pleiades
    'andromeda': (10.68, 41.27, 3),  # Andromeda
}

def main():
    output_dir = Path('batch_outputs')
    output_dir.mkdir(exist_ok=True)
    
    for name, (ra, dec, radius) in REGIONS.items():
        print(f"\nProcessing {name}...")
        print(f"  RA={ra}, Dec={dec}, Radius={radius} deg")
        
        # Fetch
        stars = fetch_gaia_cone(ra, dec, radius)
        print(f"  Fetched: {len(stars)} stars")
        
        # Transform
        stars_ssz = transform_catalog(stars)
        
        # Plot
        plot_sky_comparison(stars_ssz, output_dir / f'{name}_comparison.png')
        
        # Save
        stars_ssz.to_csv(output_dir / f'{name}_ssz.csv', index=False)
        print(f"  Saved: {name}_ssz.csv")

if __name__ == '__main__':
    main()
```

**Checklist:**
- [ ] Create `scripts/` directory
- [ ] Implement batch script
- [ ] Test with one region
- [ ] Verify all regions process
- [ ] Add usage to README

**Estimated Time:** 30 min

---

## 📖 PHASE 5: DOCUMENTATION

### Task 5.1: Examples Document
**File:** `EXAMPLES_REAL_DATA.md`

**Content:**
- Quick start example
- Named stars example
- Region processing example
- Custom catalog example
- Export for papers

**Checklist:**
- [ ] Create file
- [ ] Add 5 code examples
- [ ] Test all examples work
- [ ] Screenshots
- [ ] Link from README

**Estimated Time:** 45 min

---

### Task 5.2: API Reference
**File:** `API_REFERENCE.md`

**Content:**
- All modules documented
- Function signatures
- Parameter descriptions
- Return types
- Examples for each

**Checklist:**
- [ ] Document `catalogs` module
- [ ] Document `transform` module
- [ ] Document `viz` module
- [ ] Add cross-references
- [ ] Link from README

**Estimated Time:** 60 min

---

## ✅ TESTING & VALIDATION

### Task 6.1: Integration Tests
**File:** `tests/integration/test_real_data_pipeline.py`

```python
import pytest
from ssz_starmaps.catalogs.gaia_fetch import fetch_gaia_nearby
from ssz_starmaps.transform.batch import transform_catalog

def test_gaia_fetch():
    """Test GAIA fetch with small sample."""
    stars = fetch_gaia_nearby(distance_pc=50, max_sources=10)
    assert len(stars) > 0
    assert 'ra' in stars.columns
    assert 'dec' in stars.columns

def test_transform_pipeline():
    """Test complete pipeline."""
    stars = fetch_gaia_nearby(distance_pc=50, max_sources=10)
    stars_ssz = transform_catalog(stars)
    
    # Verify columns
    assert 'distance_ssz_pc' in stars_ssz.columns
    assert 'xi' in stars_ssz.columns
    assert 'stretch_factor' in stars_ssz.columns
    
    # Physics checks
    assert all(stars_ssz['distance_ssz_pc'] >= stars_ssz['distance_pc'])
    assert all((stars_ssz['xi'] >= 0) & (stars_ssz['xi'] < 1))
```

**Checklist:**
- [ ] Create test file
- [ ] Test GAIA fetch
- [ ] Test transform
- [ ] Test plots
- [ ] Run with pytest

**Estimated Time:** 30 min

---

## 📦 FINAL CHECKLIST

### Before Release:

- [ ] All Phase 0 tasks complete
- [ ] All Phase 1 tasks complete
- [ ] All Phase 2 tasks complete
- [ ] All Phase 3 tasks complete
- [ ] All Phase 4 tasks complete
- [ ] All Phase 5 tasks complete
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Examples tested
- [ ] README updated
- [ ] Version bumped to 0.2.0

### Ready to announce!

---

## Time Estimate Summary

| Phase | Tasks | Time |
|-------|-------|------|
| Phase 0 | 3 | 30 min |
| Phase 1 | 4 | 2.5 hrs |
| Phase 2 | 2 | 1 hr |
| Phase 3 | 1 | 1 hr |
| Phase 4 | 2 | 1 hr |
| Phase 5 | 2 | 1.5 hrs |
| Testing | 1 | 30 min |
| **TOTAL** | **15** | **~8 hours** |

**Realistic timeline:** 2-3 days (with testing & debugging)

---

## Next Action: START Phase 0!

```bash
cd E:\clone\Segmented-Spacetime-StarMaps
# Begin with Task 0.1: README update
```

© 2025 Carmen Wrede, Lino Casu
