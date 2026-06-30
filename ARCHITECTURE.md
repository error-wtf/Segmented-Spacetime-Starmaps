# SSZ StarMaps - Architecture Documentation

**Version:** 0.2.0  
**SSZ Approach:** Xi(r) - Segment Saturation (Golden Ratio)

© 2025 Carmen Wrede, Lino Casu

---

## Project Overview

SSZ StarMaps is a Python package for generating star maps with **Segmented Spacetime (SSZ)** metric deformations using real astronomical catalog data.

**Key Decision:** We use the **Xi(r)-based approach** from `ssz-metric-pure`, NOT the phi_G(r)-based approach.

---

## Directory Structure

```
Segmented-Spacetime-StarMaps/
│
├── src/ssz_starmaps/           # Main package
│   ├── __init__.py             # Public API exports
│   ├── ssz_metric.py           # ECHTE SSZ physics (Xi-based)
│   ├── projection.py           # Gnomonic + SSZ deformations
│   ├── catalog.py              # SIMBAD + GAIA DR3 integration
│   ├── geometry.py             # Ramanujan ellipse formulas
│   └── demo_starmap.py         # Main demo script
│
├── test_ssz_vs_minkowski.py   # Validation script
│
├── README.md                   # User documentation
├── EXAMPLES.md                 # Code examples
├── ARCHITECTURE.md             # This file
├── CHATGPT_CORRECTION.md       # Response to ChatGPT's phi_G suggestion
├── SSZ_APPROACHES_COMPARISON.md # Xi(r) vs phi_G(r) comparison
│
└── .venv/                      # Virtual environment
```

---

## Core Modules

### 1. `ssz_metric.py` - SSZ Physics Core

**Purpose:** Implements ECHTE SSZ formulas from `ssz-metric-pure`

**Approach:** Xi(r)-based Segment Saturation

**Key Functions:**
```python
PHI = (1 + sqrt(5)) / 2  # Golden Ratio = 1.618034

Xi(r, r_s) -> float:
    """Segment saturation: 1 - exp(-PHI * r_s / r)"""
    
D_SSZ(r, r_s) -> float:
    """Time dilation: 1 / (1 + Xi(r))"""
    
D_GR(r, r_s) -> float:
    """GR time dilation: sqrt(1 - r_s/r)"""
    
schwarzschild_radius(mass) -> float:
    """r_s = 2GM/c²"""
```

**Source:** Direct 1:1 implementation from `ssz-metric-pure/src/ssz_core/segment_density.py`

**NOT used:** phi_G(r), gamma(r), beta(r) - those are from the alternative Spiral approach!

---

### 2. `projection.py` - Coordinate Transformations

**Purpose:** Project celestial coordinates and apply SSZ deformations

**Key Functions:**

#### A) Gnomonic Projection
```python
gnomonic_projection(ra, dec, center_ra, center_dec) -> (x, y)
    """Standard tangent-plane projection"""
```

#### B) SSZ Deformation (ECHTE!)
```python
apply_ssz_metric_deformation(x, y, mass_kg, r_scale_deg) -> (x_ssz, y_ssz)
    """
    ECHTE SSZ deformation using Xi(r).
    
    Formula:
        r_coord = sqrt(x² + y²)
        r_physical = r_coord * r_scale_deg * r_s
        xi = Xi(r_physical, r_s)
        R_ssz = r_coord * (1 + xi)  # Direct formula!
        
    No integration needed!
    """
```

#### C) Legacy Deformation (DEPRECATED!)
```python
apply_ssz_deformation(x, y, eps, mode) -> (x_def, y_def)
    """
    LEGACY function with arbitrary eps-scaling.
    
    Deprecated since v0.2.0!
    Use apply_ssz_metric_deformation() instead.
    """
```

**Important:** No `DiagonalForm`, no `gamma` integration - pure Xi(r) approach!

---

### 3. `catalog.py` - Astronomical Data

**Purpose:** Fetch real star data from online databases

**Data Sources:**
- **SIMBAD:** General astronomical database
- **GAIA DR3:** High-precision astrometry

**Key Functions:**
```python
fetch_sample_catalog(center_ra, center_dec, radius, limit) -> dict
    """Query SIMBAD for stars"""
    
fetch_gaia_catalog(center_ra, center_dec, radius, limit, mag_limit) -> dict
    """Query GAIA DR3 for bright stars"""
    
create_mock_catalog(n_stars) -> dict
    """Offline testing with random stars"""
```

---

### 4. `geometry.py` - Ramanujan Formulas

**Purpose:** Accurate ellipse circumference calculations

**Key Function:**
```python
ramanujan_ellipse_circumference(a, b) -> float:
    """
    Ramanujan's first approximation:
    C ≈ π · [3(a+b) - sqrt((3a+b)(a+3b))]
    
    Accuracy: < 0.01% for all ellipses
    """
```

**Note:** This is for orbit/ellipse calculations, separate from SSZ deformation!

---

### 5. `demo_starmap.py` - Main Demo

**Purpose:** Complete demonstration pipeline

**Pipeline:**
1. Fetch star catalog (SIMBAD/GAIA or mock)
2. Gnomonic projection → (x, y)
3. Apply ECHTE SSZ deformation → (x_ssz, y_ssz)
4. Ramanujan ellipse analysis (separate!)
5. Plot Minkowski vs SSZ comparison

**Usage:**
```bash
python -m ssz_starmaps.demo_starmap
```

---

## Design Decisions

### Why Xi(r) and NOT phi_G(r)?

| Aspect | Xi(r) ✅ | phi_G(r) ❌ |
|--------|---------|-------------|
| **Simplicity** | Direct formula | Requires integration |
| **φ Meaning** | Golden Ratio (1.618) | GR calibration parameter |
| **Deformation** | `R = r*(1+Xi)` | `ℓ = ∫gamma dr` |
| **Implementation** | 1:1 from segment_density.py | Would need new module |
| **Testing** | Already validated | Would need new tests |

**Decision:** Xi(r) is simpler, more elegant, and already working perfectly!

---

## Public API

### Exported from `__init__.py`:

```python
from ssz_starmaps import (
    # SSZ Metric (ECHTE formulas)
    Xi, D_SSZ, D_GR, PHI, schwarzschild_radius,
    
    # Projections
    gnomonic_projection,
    apply_ssz_metric_deformation,  # ECHTE SSZ!
    apply_ssz_deformation,         # LEGACY (deprecated)
    
    # Catalog
    fetch_sample_catalog,
    fetch_gaia_catalog,
    create_mock_catalog,
    
    # Geometry
    ramanujan_ellipse_circumference,
    deform_circle_to_ellipse,
)
```

---

## Data Flow

```
SIMBAD/GAIA
    ↓
[catalog.py] fetch_sample_catalog()
    ↓
RA/Dec coordinates
    ↓
[projection.py] gnomonic_projection()
    ↓
(x, y) Minkowski coordinates
    ↓
[projection.py] apply_ssz_metric_deformation()
    ↓
[ssz_metric.py] Xi(r, r_s)  ← ECHTE SSZ!
    ↓
(x_ssz, y_ssz) SSZ coordinates
    ↓
[matplotlib] Visualization
```

**Note:** No phi_G, no gamma, no integration in this flow!

---

## Testing Strategy

### 1. Unit Tests (Module Level)
- `ssz_metric.py`: Xi(r), D_SSZ(r), D_GR(r)
- `projection.py`: Deformation correctness
- `geometry.py`: Ramanujan accuracy

### 2. Integration Tests
- `test_ssz_vs_minkowski.py`: Compare SSZ vs GR
- Self-tests in each module (`if __name__ == "__main__"`)

### 3. Validation
```bash
# Run SSZ vs Minkowski comparison
python test_ssz_vs_minkowski.py

# Expected results:
# - Xi(r_s) ≈ 0.802
# - D_SSZ(r_s) ≈ 0.555 (finite!)
# - Crossover: r*/r_s ≈ 1.46
```

---

## Dependencies

### Core
- `numpy` - Numerical computations
- `matplotlib` - Plotting
- `astropy` - Astronomical utilities
- `astroquery` - SIMBAD/GAIA queries

### Optional
- `scipy` - Advanced integrations (not used in Xi approach!)

---

## Version History

### v0.2.0 (2025-11-22) - ECHTE SSZ Implementation
- ✅ Replaced fake eps-scaling with ECHTE Xi(r) formulas
- ✅ Imported Xi(r) directly from ssz-metric-pure
- ✅ Added D_SSZ, D_GR time dilation functions
- ✅ Deprecated old `apply_ssz_deformation`
- ✅ Added comprehensive documentation
- ✅ Clarified: NOT using phi_G approach!

### v0.1.0 (2025-11) - Initial Prototype
- ❌ Used fake eps-scaling (arbitrary deformation)
- ✅ Basic gnomonic projection
- ✅ SIMBAD integration
- ✅ Ramanujan ellipse formulas

---

## Common Misconceptions (for ChatGPT users)

### ❌ WRONG: "Use DiagonalForm class"
```python
from ssz_metric import DiagonalForm  # Does NOT exist!
```

### ✅ CORRECT: Use Xi(r) functions
```python
from ssz_starmaps import Xi, D_SSZ, apply_ssz_metric_deformation
```

### ❌ WRONG: "Integrate gamma(r) for proper distance"
That's the phi_G approach, we don't use it!

### ✅ CORRECT: Direct Xi(r) deformation
```python
R_ssz = r * (1 + Xi(r, r_s))  # No integration!
```

**See:** `CHATGPT_CORRECTION.md` for detailed response

---

## Future Extensions (Optional)

If we ever want to add the phi_G approach:

1. Create new module: `ssz_starmaps_spiral.py`
2. Import from: `ssz_metric_pure.calibration_2pn.SSZCalibration`
3. Implement gamma integration: `ℓ(r) = ∫gamma dr`
4. Document as **alternative approach**, not replacement
5. Keep Xi(r) as default!

**Principle:** Don't mix Xi(r) and phi_G(r) - they're different physics!

---

## References

### Internal Documentation
- `README.md` - User guide
- `EXAMPLES.md` - Code examples
- `SSZ_APPROACHES_COMPARISON.md` - Xi(r) vs phi_G(r)
- `CHATGPT_CORRECTION.md` - Response to ChatGPT

### Source Repository
- `ssz-metric-pure` - Our SSZ physics source
- File: `src/ssz_core/segment_density.py` (Xi approach)
- File: `src/ssz_metric_pure/calibration_2pn.py` (phi_G approach - NOT used here!)

---

## License

© 2025 Carmen Wrede, Lino Casu  
Licensed under the Anti-Capitalist Software License v1.4
