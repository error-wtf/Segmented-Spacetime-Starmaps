# Data Hierarchy Guide - SSZ StarMaps

**Version:** 2.0  
**Date:** 2025-11-22  
**Critical:** This guide defines which data to use for which purpose

---

## 🎯 QUICK REFERENCE

```
For SSZ Validation:     fetch_primary()      → 97.9% success
For IR Mapping:         fetch_ir_map()       → Temperature/density
For Jacobian Tests:     fetch_multifreq()    → Multi-frequency
For Positions Only:     fetch_nearby()       → 51% for SSZ (use carefully!)
```

---

## 📊 DATA HIERARCHY (4 LEVELS)

### **Level 1: PRIMARY (97.9% validation)**

**Source:** ESO GRAVITY Spectroscopy  
**Method:** `fetch_primary()`  
**Observations:** 47  
**Use for:** SSZ physics validation

```python
from ssz_starmaps.catalogs import CatalogManager

manager = CatalogManager()
eso_data = manager.fetch_primary('sgr_a_stars')
# Returns: 47 ESO GRAVITY observations
# Success rate: 97.9% (46/47)
```

**Why PRIMARY?**
- Gold standard for SSZ validation
- High-quality spectroscopy
- Brγ emission lines
- 97.9% success rate
- Direct velocity measurements

**Targets:**
- `sgr_a_stars` - Sgr A* S-stars (default)
- `sgr_a_hotspot` - Sgr A* hotspot (future)
- `m87` - M87 observations (future)

---

### **Level 2: IR DATA**

**Source:** AKARI Infrared Satellite  
**Method:** `fetch_ir_map()`  
**Use for:** Nebula studies, temperature mapping

```python
manager = CatalogManager()
data, wcs = manager.fetch_ir_map('G79.29+0.46', 'N60')
# Returns: Diffuse emission map + WCS
```

**Use Cases:**
- Temperature mapping (dual-band photometry)
- Density structure analysis
- PDR (photodissociation region) studies
- Star formation regions
- Nebula morphology

**Regions:**
- `G79.29+0.46` - CygnusX Diamond Ring
- `CygnusX_DiamondRing` - Alternative name
- Others via AKARI archive

**Bands:**
- `N60` - 60 μm (good for temperature)
- `WIDE-S` - 9 μm
- `WIDE-L` - 18 μm  
- `N160` - 160 μm

---

### **Level 3: MULTI-FREQUENCY**

**Source:** NED (NASA/IPAC Extragalactic Database)  
**Method:** `fetch_multifreq()`  
**Use for:** Jacobian tests, SEDs, continuum

```python
manager = CatalogManager()
m87_spectrum = manager.fetch_multifreq('M87')
# Returns: ~139 frequency measurements
# Range: 9+ orders of magnitude
```

**Use Cases:**
- Jacobian tests (∂f/∂r relationships)
- Spectral energy distributions
- Multi-wavelength analysis
- Continuum spectrum
- Frequency scaling tests

**Best Targets:**
- `M87` - 139 frequencies (excellent!)
- `3C279` - Bright blazar
- Other NED objects

---

### **Level 4: AUXILIARY (51% for SSZ)**

**Source:** GAIA DR3 / SIMBAD  
**Method:** `fetch_nearby()`, `fetch_named()`  
**Use for:** Positions, astrometry, comparisons

```python
manager = CatalogManager()
stars = manager.fetch_nearby(distance_pc=100, max_stars=50)
# Returns: Nearby stars with positions
# [!] Only 51% success for SSZ validation!
```

**Use Cases (CORRECT):**
- Spatial positions
- Astrometry
- Parallax measurements
- Proper motions
- Star field context
- Visualization backgrounds

**NOT for:**
- ❌ SSZ physics validation (only 51%!)
- ❌ Velocity validation
- ❌ Primary science analysis

---

## ⚠️ CRITICAL DISTINCTIONS

### **PRIMARY vs AUXILIARY**

```
ESO (PRIMARY):
  ✅ Use for: SSZ validation
  ✅ Success: 97.9%
  ✅ Data: Spectroscopy (velocities)
  ✅ Quality: Gold standard

GAIA (AUXILIARY):
  ✅ Use for: Positions only
  ❌ Success: 51% (for SSZ)
  ⚠️ Data: Astrometry (no velocities)
  ⚠️ Quality: Fine for positions, poor for SSZ
```

### **Common Mistake:**

```python
# ❌ WRONG: Using GAIA for validation
stars = manager.fetch_nearby(100)
validate_ssz(stars)  # Only 51% success!

# ✅ CORRECT: Using ESO for validation
eso = manager.fetch_primary('sgr_a_stars')
validate_ssz(eso)  # 97.9% success!
```

---

## 🎯 USE CASE MATRIX

| Purpose | Method | Source | Success Rate |
|---------|--------|--------|--------------|
| SSZ Validation | `fetch_primary()` | ESO | 97.9% |
| Temperature Map | `fetch_ir_map()` | AKARI | N/A |
| Jacobian Tests | `fetch_multifreq()` | NED | N/A |
| Positions | `fetch_nearby()` | GAIA | N/A |
| Astrometry | `fetch_named()` | SIMBAD | N/A |

---

## 📚 EXAMPLES

### **Example 1: SSZ Validation (CORRECT)**

```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog

# Step 1: Get PRIMARY data
manager = CatalogManager()
eso_data = manager.fetch_primary('sgr_a_stars')

# Step 2: Apply SSZ transformation
ssz_data = transform_catalog(eso_data)

# Step 3: Validate
# Expected: 97.9% success rate
```

### **Example 2: Multi-Source Workflow**

```python
manager = CatalogManager()

# PRIMARY: Validation
eso = manager.fetch_primary('sgr_a_stars')  # 97.9%

# IR: Temperature mapping
akari, wcs = manager.fetch_ir_map('G79.29+0.46', 'N60')

# MULTI-FREQ: Jacobian tests
m87 = manager.fetch_multifreq('M87')  # 139 frequencies

# AUXILIARY: Positions only
gaia = manager.fetch_nearby(distance_pc=100)

# Use each for its PURPOSE!
```

### **Example 3: Checking Availability**

```python
manager = CatalogManager()

# Check what's available
hierarchy = manager.get_data_hierarchy()

print("Available data sources:")
for level, info in hierarchy.items():
    print(f"{level}: {info['available']}")

# Print usage guide
manager.print_data_guide()
```

---

## 🔍 DATA QUALITY

### **PRIMARY (ESO):**

```
Observations: 47
Success rate: 97.9% (46/47)
Data type: Spectroscopy
Measurements: Velocities, redshifts
Targets: Sgr A* S-stars, jets, binaries
Quality: Gold standard
```

### **IR DATA (AKARI):**

```
Type: Diffuse emission maps
Resolution: ~10 arcsec
Bands: 4 (N60, WIDE-S, WIDE-L, N160)
Coverage: Galactic plane
Quality: Excellent for nebulae
```

### **MULTI-FREQ (NED):**

```
M87 example: 139 measurements
Frequency range: 9+ orders of magnitude
Coverage: Radio to gamma-ray
Quality: Varies by source
```

### **AUXILIARY (GAIA):**

```
Stars: Millions
Precision: μas (positions), ~km/s (velocities)
Success for SSZ: 51% (NOT recommended)
Quality: Excellent for astrometry
```

---

## 💡 BEST PRACTICES

### **1. Always Check Availability**

```python
hierarchy = manager.get_data_hierarchy()
if hierarchy['primary']['available']:
    data = manager.fetch_primary('sgr_a_stars')
else:
    print("ESO data not available")
```

### **2. Document Your Choice**

```python
# For SSZ validation - use PRIMARY (97.9%)
eso_data = manager.fetch_primary('sgr_a_stars')

# For positions only - use AUXILIARY
gaia_data = manager.fetch_nearby(100)  # [!] NOT for validation
```

### **3. Use Print Guide**

```python
manager = CatalogManager()
manager.print_data_guide()
# Shows complete hierarchy with availability
```

---

## 🐛 TROUBLESHOOTING

### **Problem: "ESO module not available"**

**Solution:**
```bash
pip install astroquery
```

Or use included data:
```python
eso_data = manager.fetch_primary('sgr_a_stars', use_included=True)
```

### **Problem: "Low validation success rate"**

**Check:** Are you using the right data?
```python
# ❌ This will give ~51%:
data = manager.fetch_nearby(100)

# ✅ This will give ~97.9%:
data = manager.fetch_primary('sgr_a_stars')
```

### **Problem: "Missing columns"**

**Check:** Data source schema
```python
print(data.columns)
# ESO has: case, M_solar, v_tot_mps, etc.
# GAIA has: ra, dec, parallax, etc.
```

---

## 📖 FURTHER READING

**Documentation:**
- `MIGRATION_GUIDE.md` - How to migrate from old system
- `examples/example_eso_primary.py` - PRIMARY data usage
- `examples/example_g79_workflow.py` - Multi-source workflow
- `examples/example_m87_multifreq.py` - Multi-frequency analysis

**Source Files:**
- `src/ssz_starmaps/catalogs/eso_fetch.py` - ESO implementation
- `src/ssz_starmaps/catalogs/akari_fetch.py` - AKARI implementation
- `src/ssz_starmaps/catalogs/ned_fetch.py` - NED implementation
- `src/ssz_starmaps/catalogs/manager.py` - Unified interface

---

## 🎓 SUMMARY

### **The Golden Rule:**

```
Use the RIGHT data for the RIGHT purpose!

SSZ Validation → PRIMARY (ESO) → 97.9%
Temperature Map → IR (AKARI)
Jacobian Tests → MULTI-FREQ (NED)
Positions → AUXILIARY (GAIA)
```

### **Remember:**

- ✅ PRIMARY for physics validation (97.9%)
- ✅ AUXILIARY for positions only (51% for SSZ)
- ❌ Never use GAIA for SSZ validation
- ✅ Always check availability
- ✅ Document your data choices

---

**Data Hierarchy Guide Version:** 2.0  
**Last Updated:** 2025-11-22

© 2025 Carmen Wrede, Lino Casu  
Licensed under ACSL v1.4
