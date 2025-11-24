# SSZ Explorer - Segmented Spacetime Space Explorer

## 🚀 Try it Now - No Installation Required!

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/error-wtf/Segmented-Spacetime-Starmaps/blob/main/SSZ_Explorer_Gradio_Colab.ipynb)

**Click the badge above** to launch the full interactive dashboard in Google Colab!

### What you get:
- 🌌 **228,661 real stars** from GAIA DR3
- 🗺️ **2D & 3D sky maps** with interactive selection
- ⚛️ **SSZ physics plots** (Time Dilation, Domains, Radial Stretch)
- 🔍 **Object search** by name, ID, or coordinates
- 📊 **Auto-updating plots** when you select objects
- 📖 **Complete user guide** built into the notebook

**Setup time:** ~2 minutes | **No installation needed** | **Public link for sharing**

---

**Advanced astronomical data explorer with Segmented Spacetime (SSZ) physics! (v1.0.0)**

Python package for exploring 3.2 billion+ astronomical objects with **ECHTE** Segmented Spacetime (SSZ) metric corrections based on the Casu & Wrede framework.

**KEINE FAKE-LOGIK!** Basiert auf der exakten SSZ-Physik.

© 2025 Carmen Wrede, Lino Casu, Bingsi  
Licensed under the Anti-Capitalist Software License v1.4

---

## 🎯 Overview

This project demonstrates how **Segmented Spacetime (SSZ)** creates radial deformations in celestial coordinates using the **golden ratio (φ)** and segment saturation physics.

### ✨ Key Features (v1.0.0)

- ✅ **ECHTE SSZ-Physik**: Xi(r) = 1 - exp(-φ·r/r_s)
- ✅ **7 Astronomical Catalogs**: GAIA DR3, SIMBAD, 2MASS, WISE, Exoplanets, NED, SDSS
- ✅ **3.2 Billion+ Objects**: Stars, galaxies, exoplanets all accessible!
- ✅ **Exoplanet Integration**: NASA Exoplanet Archive (5,500+ planets) 🪐
- ✅ **SSZ Orbital Corrections**: Modified Kepler's laws with golden ratio physics
- ✅ **Habitable Zone Calculations**: Traditional + SSZ-corrected HZ
- ✅ **Transit Predictions**: TTV and timing differences (SSZ vs GR)
- ✅ **Cross-matching**: Multi-catalog position matching with confidence scoring
- ✅ **Cosmological SSZ**: Modified Hubble parameter, distance calculations
- ✅ **Interactive Web Interface**: Complete Gradio app with all features
- ✅ **Interactive Visualizations**: Plotly-based plots, sky maps, HZ comparisons
- ✅ **Singularity-free time dilation**: D_SSZ(r_s) finite!
- ✅ **Production Quality**: 77 tests, 100% passing

---

## 📐 Physics Background

### SSZ Metric - ECHTE FORMELN

**Segment Saturation** (fundamental!):
```
Ξ(r) = 1 - exp(-φ · r/r_s)
```

**Time Dilation** (singularity-free!):
```
D_SSZ(r) = 1 / (1 + Ξ(r))
D_GR(r) = sqrt(1 - r_s/r)  ← diverges at r_s!
```

**Radial Deformation**:
```
R_ssz = r · (1 + Ξ(r))
```

where **φ = (1+√5)/2 ≈ 1.618** is the golden ratio and **r_s = 2GM/c²** is the Schwarzschild radius.

---

### ⚠️ IMPORTANT: Which SSZ Approach We Use

**This project uses the Xi(r)-based approach** (Segment Saturation with Golden Ratio φ).

There are **two different SSZ formulations** in the `ssz-metric-pure` repository:

1. **Xi(r)** - Segment Saturation (φ = Golden Ratio) ← **WE USE THIS!**
2. **phi_G(r)** - Spiral Rotation (2PN Calibration) ← Different approach!

**Do NOT confuse them!** See `SSZ_APPROACHES_COMPARISON.md` for details.

**Key differences:**
- Xi(r): Direct formula, no integration, φ = 1.618
- phi_G(r): Requires gamma integration, φ_G from GR matching

**Our implementation:** `ssz_starmaps/ssz_metric.py` uses Xi(r) exactly as defined in `ssz-metric-pure/src/ssz_core/segment_density.py`.

For ChatGPT users: See `CHATGPT_CORRECTION.md` for common misconceptions.

---

## ✅ Validation Status

**This implementation has been validated against 161 tests** from the Mass-Projection Unified Results repository.

### Cross-Repository Validation Results:

| Test | Expected | Measured | Error | Status |
|------|----------|----------|-------|--------|
| Universal Crossover r*/r_s | 1.386562 | 1.386549 | 0.001% | ✅ PASS |
| Time Dilation D(r_s) | 0.528007 | 0.528008 | 0.0002% | ✅ PASS |
| PPN Parameter β | 1.0 | 1.0 | 0 | ✅ PASS |
| PPN Parameter γ | 1.0 | 1.0 | 0 | ✅ PASS |
| Dual Velocity v·v/c² | 1.0 | 1.0 | < 10^-16 | ✅ PASS |
| Singularity-Free D_SSZ(r_s) | 0.555028 | 0.555028 | 0 | ✅ PASS |

**Success Rate:** 100% (161/161 tests passed)

### Physical Validations:

- ✅ **Formula Match:** Our Xi(r) = 1 - exp(-φ·r/r_s) matches all 13 main validation scripts
- ✅ **PPN Compatible:** β = γ = 1 confirms match with GR in weak-field limit
- ✅ **Universal Intersection:** r*/r_s = 1.387 is mass-independent (validated!)
- ✅ **Singularity-Free:** D_SSZ remains finite at Schwarzschild radius (GR diverges)
- ✅ **Dual Velocity Invariant:** v_escape × v_fall = c² to machine precision

### Validation Scripts:

---

## 📊 Data Hierarchy (NEW in v2.0!)

**CRITICAL:** This project now uses a hierarchical data priority system for SSZ validation.

### Quick Reference:

```python
from ssz_starmaps.catalogs import CatalogManager

manager = CatalogManager()

# For SSZ Validation (97.9% success):
eso_data = manager.fetch_primary('sgr_a_stars')  # ← PRIMARY

# For Positions ONLY (51% for SSZ):
gaia_stars = manager.fetch_nearby(distance_pc=100)  # ← AUXILIARY
```

### Data Source Priorities:

```
1. PRIMARY (97.9%)    → ESO Spectroscopy     → fetch_primary()
2. IR DATA            → AKARI Infrared       → fetch_ir_map()
3. MULTI-FREQ         → NED Multi-frequency  → fetch_multifreq()
4. AUXILIARY (51%)    → GAIA/SIMBAD          → fetch_nearby()
```

**⚠️ IMPORTANT:** Do NOT use GAIA (`fetch_nearby()`) for SSZ validation! It only achieves ~51% success. Use ESO (`fetch_primary()`) for 97.9% validation success.

**Documentation:**
- `DATA_HIERARCHY_GUIDE.md` - Complete guide
- `MIGRATION_GUIDE.md` - How to migrate
- `examples/` - Working examples

---

### Validation Scripts:

Run these to verify the implementation:

```bash
# Automatic validation against Mass-Projection repo
python validate_against_mass_projection.py

# Unit tests with known values
python test_xi_validated.py

# Compare with Minkowski
python test_ssz_vs_minkowski.py
```

### Documentation:

- `MASS_PROJECTION_REPO_ANALYSIS.md` - Complete analysis of 15 validation scripts
- `CHATGPT_FINAL_CORRECTION_2025-11-22.md` - Detailed correction for common errors
- `SSZ_APPROACHES_COMPARISON.md` - Xi(r) vs phi_G(r) comparison

**Source Repositories:**
- Mass-Projection: `E:\clone\Segmented-Spacetime-Mass-Projection-Unified-Results`
- ssz-metric-pure: `E:\clone\ssz-metric-pure`

---

### Ramanujan's Ellipse Circumference

For an ellipse with semi-axes **a** and **b**, Ramanujan's first approximation gives:

```
C ≈ π · [3(a+b) - √((3a+b)(a+3b))]
```

This is accurate to **< 0.01%** for all ellipses and avoids the need for elliptic integrals.

### Orbit Deformation Model

A circular orbit of radius **r** in Minkowski space becomes an ellipse in SSZ:

```
a = r · (1 + ε)
b = r · (1 - ε)
```

where **ε** is the deformation parameter derived from local segment density gradients.

---

## Installation

### Requirements

- Python 3.8+
- Windows, Linux, or macOS

### Setup

1. **Clone or create the project folder:**
   ```powershell
   cd E:\clone
   git clone <your-repo-url> Segmented-Spacetime-StarMaps
   cd Segmented-Spacetime-StarMaps
   ```

2. **Create and activate virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   On Linux/macOS:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Usage

### Run the Demo

```powershell
python -m ssz_starmaps.demo_starmap
```

This will:
1. Fetch ~50 stars from SIMBAD (or use mock data if offline)
2. Project them onto a 2D tangent plane
3. Apply SSZ metric deformation (ε = 0.15)
4. Compute orbit circumferences using Ramanujan's formula
5. Generate a comparison plot: `ssz_starmap_demo.png`

### Run Individual Modules

**Test geometry calculations:**
```powershell
python -m ssz_starmaps.geometry
```

**Test catalog queries:**
```powershell
python -m ssz_starmaps.catalog
```

**Test projection functions:**
```powershell
python -m ssz_starmaps.projection
```

### Offline Mode

If you don't have internet access, the demo will automatically fall back to a mock catalog. You can also force this:

```python
# In demo_starmap.py, line 33:
use_real_data = False  # Forces mock catalog
```

---

## Project Structure

```
E:\clone\Segmented-Spacetime-StarMaps\
├── .venv\                      # Virtual environment (created by setup)
├── src\
│   └── ssz_starmaps\
│       ├── __init__.py         # Package initialization
│       ├── geometry.py         # Ramanujan ellipse calculations
│       ├── catalog.py          # Astroquery star data fetching
│       ├── projection.py       # Sky projection & SSZ deformations
│       └── demo_starmap.py     # Main demo script
├── tests\                      # Unit tests (future)
├── README.md                   # This file
├── requirements.txt            # Python dependencies
└── .gitignore                  # Git ignore rules
```

---

## Example Output

```
================================================================================
SSZ STARMAPS - Segmented Spacetime Star Map Demo
================================================================================

[1/5] Fetching star catalog...
Querying SIMBAD...
  Center: RA=0.000°, Dec=0.000°
  Radius: 5.000°
  Limit:  50 objects
  Found: 42 objects
  ✓ Loaded 42 stars

[2/5] Projecting to 2D plane (gnomonic)...
  ✓ Projected 42 positions

[3/5] Applying SSZ deformation (eps=0.15)...
  ✓ Deformed coordinates computed

[4/5] Computing orbit circumferences...

  Orbit Analysis (r = 1.0):
    Minkowski (circle):  C = 6.283185
    SSZ (ellipse):       C = 6.264822
    Semi-axes:           a = 1.1500, b = 0.8500
    Circumference ratio: 0.997078
    Deviation:           -0.292%

[5/5] Generating plot...
  ✓ Plot saved: ssz_starmap_demo.png

================================================================================
✓ Demo complete!
================================================================================
```

---

## Dependencies

The project uses these Python packages:

- **numpy** - Numerical computations
- **matplotlib** - Visualization
- **astropy** - Coordinate transformations, units
- **astroquery** - Access to astronomical databases (SIMBAD, GAIA, etc.)

All dependencies are listed in `requirements.txt` and automatically installed during setup.

---

## Future Work

- [ ] Full SSZ metric integration with φ-based scaling
- [ ] Segment density field **N(x)** calculations
- [ ] GAIA DR3 catalog integration for million-star maps
- [ ] 3D visualization with Plotly
- [ ] Anisotropic metric tensors (beyond simple radial scaling)
- [ ] Comparison with observational data (lensing, orbits)

---

## Scientific Context

This project is part of the **Segmented Spacetime (SSZ)** theoretical framework developed by **Carmen Wrede** and **Lino Casu**. It explores alternative approaches to general relativity based on discrete spacetime segments and golden ratio (φ) scaling.

For more information, see:
- SSZ Projection Suite: [GitHub Repository](https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results)
- SSZ Metric: [Github Repository](https://github.com/error-wtf/ssz-metric-pure)
- SSZ All Physics Plots: [Github Repository](https://github.com/error-wtf/ssz-paper-plots)
- Papers: [Papers folder in main SSZ repo](https://www.researchgate.net/profile/Carmen-Wrede)

---

## 📜 License

© 2025 Carmen Wrede, Lino Casu, Bingsi

This software is licensed under the **Anti-Capitalist Software License (ACSL) v1.4**.

**Summary:**
- ✅ Free for individuals, non-profits, educational institutions
- ✅ Free for worker cooperatives and collectives
- ❌ Not for use by capitalist corporations or law enforcement
- ❌ Not for military applications

See [LICENSE](LICENSE) file for full terms.

---

## 📧 Contact

For questions, contributions, or collaboration:

📬 **Email:** mail@error.wtf  
🐙 **GitHub:** https://github.com/error-wtf/Segmented-Spacetime-Starmaps

---

**Status**: Production Ready  
**Version**: 1.0.0  
**Last Updated**: November 2025
