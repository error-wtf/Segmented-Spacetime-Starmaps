# Migration Guide - Hierarchical Data Priority

**Date:** 2025-11-22  
**Version:** 2.0  
**Breaking Changes:** YES

---

## 🚨 IMPORTANT CHANGES

The StarMaps repository now uses a **hierarchical data priority system** with ESO spectroscopy as the PRIMARY data source for SSZ validation.

**Key Change:**
- OLD: GAIA-only (51% SSZ validation)
- NEW: ESO primary (97.9% SSZ validation)

---

## ⚠️ BREAKING API CHANGES

### **1. Data Source Hierarchy**

```python
# OLD WAY (51% validation - NOT RECOMMENDED):
manager = CatalogManager()
stars = manager.fetch_nearby(distance_pc=100)
# Uses GAIA - only 51% for SSZ validation!

# NEW WAY (97.9% validation - RECOMMENDED):
manager = CatalogManager()
eso_data = manager.fetch_primary('sgr_a_stars')
# Uses ESO - 97.9% validation!
```

### **2. Purpose-Specific Methods**

```python
# For SSZ validation (HIGH priority):
eso_data = manager.fetch_primary('sgr_a_stars')  # 97.9%

# For infrared studies:
akari_map, wcs = manager.fetch_ir_map('G79.29+0.46', 'N60')

# For multi-frequency analysis:
m87_spectrum = manager.fetch_multifreq('M87')

# For positions ONLY (LOW priority for SSZ):
gaia_stars = manager.fetch_nearby(distance_pc=100)  # 51% for SSZ
```

---

## 📊 DATA HIERARCHY

### **Priority Levels:**

```
1. PRIMARY (97.9%)     → ESO spectroscopy
   Use for: SSZ validation tests
   Method: fetch_primary()
   
2. IR DATA             → AKARI diffuse maps
   Use for: Nebula studies, temperature mapping
   Method: fetch_ir_map()
   
3. MULTI-FREQ          → NED continuum
   Use for: Jacobian tests, SEDs
   Method: fetch_multifreq()
   
4. AUXILIARY (51%)     → GAIA/SIMBAD
   Use for: Positions, astrometry ONLY
   Method: fetch_nearby(), fetch_named()
```

---

## 🔄 MIGRATION EXAMPLES

### **Example 1: SSZ Validation Script**

**BEFORE (❌ Wrong):**
```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog

# OLD: Using GAIA (only 51% validation)
manager = CatalogManager()
stars = manager.fetch_nearby(distance_pc=100, max_stars=50)

# Apply SSZ transformation
ssz_stars = transform_catalog(stars)

# Validate (will only get ~51% success)
# ❌ NOT RECOMMENDED for validation!
```

**AFTER (✅ Correct):**
```python
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog

# NEW: Using ESO (97.9% validation)
manager = CatalogManager()
eso_data = manager.fetch_primary('sgr_a_stars')

# Apply SSZ transformation
ssz_data = transform_catalog(eso_data)

# Validate (will get ~97.9% success)
# ✅ RECOMMENDED for validation!
```

### **Example 2: Position-Only Queries**

**BEFORE (✅ Still works):**
```python
# For positions/astrometry (no change needed)
manager = CatalogManager()
stars = manager.fetch_nearby(distance_pc=100)
# This is FINE if you only need positions!
```

**AFTER (✅ Same, but with clarity):**
```python
# For positions/astrometry (explicitly documented now)
manager = CatalogManager()
stars = manager.fetch_nearby(distance_pc=100)
# [!] Use for positions ONLY, NOT for SSZ validation!
```

### **Example 3: Multi-Source Workflow**

**NEW (✅ Recommended pattern):**
```python
manager = CatalogManager()

# Step 1: PRIMARY data for validation
eso_data = manager.fetch_primary('sgr_a_stars')  # 97.9%

# Step 2: IR data for temperature mapping
akari_map, wcs = manager.fetch_ir_map('G79.29+0.46', 'N60')

# Step 3: Multi-frequency for Jacobian tests
m87_spectrum = manager.fetch_multifreq('M87')

# Step 4: GAIA positions for spatial context
gaia_stars = manager.fetch_nearby(distance_pc=100)  # Positions only!

# Use the RIGHT data for the RIGHT purpose!
```

---

## 🎯 MIGRATION CHECKLIST

### **For Validation Scripts:**

- [ ] Replace `fetch_nearby()` with `fetch_primary()` for SSZ tests
- [ ] Update validation expectations (51% → 97.9%)
- [ ] Add comments explaining data source choice
- [ ] Test with new ESO data
- [ ] Update documentation

### **For Position Queries:**

- [ ] Keep using `fetch_nearby()` (no change)
- [ ] Add comment: "For positions only"
- [ ] Clarify in documentation
- [ ] No code changes needed

### **For Multi-Source Analysis:**

- [ ] Identify data purpose (validation vs. positions vs. IR)
- [ ] Use appropriate fetch method
- [ ] Document data source choices
- [ ] Test workflow

---

## 📝 CODE PATTERNS

### **Pattern 1: Check Data Availability**

```python
manager = CatalogManager()

# Check what's available
hierarchy = manager.get_data_hierarchy()

if hierarchy['primary']['available']:
    # Use ESO
    data = manager.fetch_primary('sgr_a_stars')
else:
    # Fallback to GAIA (positions only)
    data = manager.fetch_nearby(distance_pc=100)
```

### **Pattern 2: Print Usage Guide**

```python
manager = CatalogManager()

# Show user which data to use
manager.print_data_guide()

# Output:
# PRIMARY (97.9%): ESO spectroscopy
# Use fetch_primary() for SSZ validation
# ...
```

### **Pattern 3: Purpose-Specific Fetching**

```python
def get_validation_data():
    """For SSZ validation - use PRIMARY."""
    manager = CatalogManager()
    return manager.fetch_primary('sgr_a_stars')

def get_position_data():
    """For positions - use AUXILIARY."""
    manager = CatalogManager()
    return manager.fetch_nearby(distance_pc=100)

def get_ir_data():
    """For temperature mapping - use IR."""
    manager = CatalogManager()
    return manager.fetch_ir_map('G79.29+0.46', 'N60')
```

---

## ⚠️ COMMON PITFALLS

### **Pitfall 1: Using GAIA for SSZ Validation**

```python
# ❌ WRONG:
stars = manager.fetch_nearby(distance_pc=100)
validate_ssz(stars)  # Only 51% success!

# ✅ CORRECT:
eso_data = manager.fetch_primary('sgr_a_stars')
validate_ssz(eso_data)  # 97.9% success!
```

### **Pitfall 2: Not Checking Availability**

```python
# ❌ WRONG:
eso_data = manager.fetch_primary('sgr_a_stars')
# Might fail if Mass-Projection repo not accessible

# ✅ CORRECT:
hierarchy = manager.get_data_hierarchy()
if hierarchy['primary']['available']:
    eso_data = manager.fetch_primary('sgr_a_stars')
else:
    print("ESO data not available")
    print("Check Mass-Projection repo connection")
```

### **Pitfall 3: Mixing Data Sources**

```python
# ❌ WRONG:
eso_data = manager.fetch_primary('sgr_a_stars')
gaia_data = manager.fetch_nearby(distance_pc=100)
combined = pd.concat([eso_data, gaia_data])  # Different schemas!

# ✅ CORRECT:
# Use ESO for validation
eso_data = manager.fetch_primary('sgr_a_stars')
validate_ssz(eso_data)

# Use GAIA for positions separately
gaia_data = manager.fetch_nearby(distance_pc=100)
plot_positions(gaia_data)
```

---

## 🔍 BACKWARD COMPATIBILITY

### **What Still Works:**

✅ `fetch_nearby()` - Works, but document purpose  
✅ `fetch_named_star()` - No changes  
✅ `fetch_famous_stars()` - No changes  
✅ `fetch_interesting_region()` - No changes  
✅ `transform_catalog()` - Works with all data

### **What's New:**

🆕 `fetch_primary()` - ESO spectroscopy  
🆕 `fetch_ir_map()` - AKARI infrared  
🆕 `fetch_multifreq()` - NED multi-frequency  
🆕 `get_data_hierarchy()` - Info method  
🆕 `print_data_guide()` - Usage guide

---

## 📚 EXAMPLES

See the `examples/` directory for complete examples:

```
examples/
├── example_eso_primary.py      - PRIMARY data usage
├── example_g79_workflow.py     - Multi-source workflow
└── example_m87_multifreq.py    - Multi-frequency analysis
```

**Run examples:**
```bash
python examples/example_eso_primary.py
python examples/example_g79_workflow.py
python examples/example_m87_multifreq.py
```

---

## 🐛 TROUBLESHOOTING

### **Problem 1: "ESO module not available"**

**Cause:** `astroquery` not installed or Mass-Projection repo not accessible

**Solution:**
```bash
pip install astroquery
```

Or use included data:
```python
eso_data = manager.fetch_primary('sgr_a_stars', use_included=True)
```

### **Problem 2: "AKARI module not available"**

**Cause:** AKARI data files not downloaded

**Solution:** See `akari_fetch.py` for data acquisition instructions

### **Problem 3: "NED module not available"**

**Cause:** `astroquery` not installed or no internet connection

**Solution:**
```bash
pip install astroquery
```

---

## 📊 VALIDATION COMPARISON

### **Before Migration:**
```
Data source: GAIA DR3
Success rate: ~51%
Use case: Positions (correct), SSZ validation (incorrect)
```

### **After Migration:**
```
Data source: ESO GRAVITY
Success rate: 97.9%
Use case: SSZ validation (correct)

Data source: GAIA DR3
Success rate: N/A (positions only)
Use case: Positions (correct)
```

---

## 🚀 QUICK START

### **1. Check Data Availability:**
```python
from ssz_starmaps.catalogs import CatalogManager

manager = CatalogManager()
manager.print_data_guide()
```

### **2. Fetch PRIMARY Data:**
```python
eso_data = manager.fetch_primary('sgr_a_stars')
print(f"Loaded {len(eso_data)} observations")
```

### **3. Run Your Analysis:**
```python
from ssz_starmaps.transform import transform_catalog

ssz_data = transform_catalog(eso_data)
# Continue with your SSZ validation...
```

---

## 📞 SUPPORT

**Questions?** Check:
- `PHASE4_COMPLETE.md` - Data validation details
- `MANAGER_UPDATE_COMPLETE.md` - Implementation details
- `examples/` - Working code examples

**Issues?** Verify:
1. Data source availability (`get_data_hierarchy()`)
2. Correct method for purpose (validation vs. positions)
3. Dependencies installed (`astroquery`)

---

## ✅ MIGRATION STATUS

After completing migration:

- [ ] All validation scripts use `fetch_primary()`
- [ ] Position queries documented as "auxiliary"
- [ ] Data source choices explained in comments
- [ ] Tests updated for 97.9% success rate
- [ ] Documentation updated

---

**Migration Guide Version:** 2.0  
**Date:** 2025-11-22  
**Status:** Complete

© 2025 Carmen Wrede, Lino Casu  
Licensed under ACSL v1.4
