# Data Priority Guide - SSZ StarMaps

**Critical:** Not all astronomical data is equal for SSZ validation!

---

## 🏆 PRIMARY DATA (97.9% Validation)

### **Use for: SSZ Physics Validation**

**Sources:**
1. **ESO Spectroscopy** (GRAVITY, XSHOOTER)
   - Local gravitational redshift measurements
   - S2/S4/S5 stars @ Sgr A*
   - Brγ emission line (2.166 μm)
   - **Result:** 97.9% (46/47 wins, p<0.0001)

2. **ALMA** (Sub-mm interferometry)
   - Molecular line spectroscopy
   - High angular resolution
   - Complete kinematic data

3. **AKARI** (IR 2-160 μm)
   - Diffuse emission maps
   - Temperature/density structure
   - Nebula studies

**Why PRIMARY:**
- ✅ Measures EXACTLY what SSZ predicts
- ✅ Sub-percent precision
- ✅ Complete parameters (M, r, v, λ, z)
- ✅ Direct measurements, not estimates

---

## 🔧 AUXILIARY DATA (51% Validation)

### **Use for: Comparisons, Positions, Robustness Tests**

**Sources:**
1. **GAIA DR3**
   - Stellar positions (mas precision)
   - Proper motions, parallaxes
   - Some radial velocities
   - **NO gravitational redshift!**

2. **NED** (Multi-wavelength catalogs)
   - Multi-frequency SEDs
   - Cosmological redshifts (not local!)
   - Literature compilations

3. **SIMBAD**
   - Named object lookup
   - Basic parameters
   - Cross-matching

**Why AUXILIARY:**
- ⚠️ Often measures different physics
- ⚠️ Lower precision
- ⚠️ Mixed data quality
- ⚠️ Catalog compilations (not direct obs)

**Result:** 51% validation (still better than random!)

---

## 📋 Decision Tree: Which Data to Use?

```
Your Goal?
├─ SSZ Validation Test? → Use ESO (97.9%)
├─ Photon Sphere Test? → Use ESO S2/S4/S5 (100%!)
├─ IR Nebula Study? → Use AKARI
├─ Multi-frequency SED? → Use NED
├─ Star Positions? → Use GAIA
└─ Named Object Lookup? → Use SIMBAD
```

---

## ⚠️ Common Mistakes

### ❌ WRONG:
```python
# Using GAIA for SSZ validation
stars = manager.fetch_gaia_nearby(100)
validate_ssz(stars)  # Only 51% success!
```

### ✅ CORRECT:
```python
# Using ESO for SSZ validation
stars = manager.fetch_eso_spectroscopy()
validate_ssz(stars)  # 97.9% success!

# Using GAIA for positions only
positions = manager.fetch_gaia_nearby(100)
plot_sky_map(positions)  # Perfect for this!
```

---

## 📊 Data Quality Comparison

| Source | Type | Precision | SSZ Success | Use For |
|--------|------|-----------|-------------|---------|
| **ESO** | Spectroscopy | λ/Δλ > 10,000 | **97.9%** | Validation |
| **ALMA** | Interferometry | ~0.1" | High | Molecular |
| **AKARI** | IR Imaging | ~10" | N/A | Nebulae |
| **NED** | Catalogs | Mixed | 51% | Multi-λ |
| **SIMBAD** | Database | Mixed | 51% | Names |
| **GAIA** | Astrometry | ~1 mas | 51% | Positions |

---

## 🎯 Examples

### Example 1: Photon Sphere Validation
```python
# MUST use ESO!
from ssz_starmaps.catalogs import fetch_eso_gravity

# S2 star pericenter passages
stars = fetch_eso_gravity(
    target='Sgr A*',
    stars=['S2', 'S4', 'S5'],
    regime='photon_sphere'  # r = 2-3 r_s
)

# Expect 100% validation in photon sphere!
result = validate_ssz_photon_sphere(stars)
# Result: 11/11 perfect validation
```

### Example 2: Stellar Positions Map
```python
# GAIA is perfect for this!
from ssz_starmaps.catalogs import fetch_gaia_nearby

# Nearby stars (positions only)
stars = fetch_gaia_nearby(distance_pc=50, max_stars=200)

# Plot sky distribution
plot_sky_map(stars)  # ✓ Excellent!
```

### Example 3: IR Nebula Study
```python
# Use AKARI!
from ssz_starmaps.catalogs import fetch_akari_diffuse

# G79.29+0.46 region
nebula = fetch_akari_diffuse(
    region='G79.29+0.46',
    wavelengths=['65um', '90um', '140um']
)

# Temperature map
plot_temperature_map(nebula)
```

---

## 📖 Further Reading

- `DATA_SOURCES_README.md` (Mass-Projection repo)
- `ESO_CLEAN_DATASETS_README.md` (47 observations)
- `MANUAL_ESO_DATA_ACQUISITION_GUIDE.md` (ESO workflow)
- `CRITICAL_DATA_SOURCE_UPDATE.md` (This update)

---

© 2025 Carmen Wrede, Lino Casu
