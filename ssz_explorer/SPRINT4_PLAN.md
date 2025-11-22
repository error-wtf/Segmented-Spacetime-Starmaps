# 🌌 SPRINT 4 PLAN - Galaxy Integration

**Goal:** Integrate NED & SDSS for cosmological SSZ testing  
**Duration:** 3-4 hours planned (~1 hour actual based on velocity)  
**Status:** Starting NOW!  
**Date:** 2025-11-22

---

## 🎯 SPRINT GOALS

**Primary:**
- ✅ Integrate NED (NASA/IPAC Extragalactic Database)
- ✅ Integrate SDSS (Sloan Digital Sky Survey)
- ✅ Cosmological SSZ calculations
- ✅ Distance ladder corrections
- ✅ Hubble tension analysis

**Success Criteria:**
- Query galaxies by various parameters
- Calculate SSZ cosmological corrections
- Compare with standard ΛCDM
- Hubble parameter differences
- Export results

---

## 📋 TASKS BREAKDOWN

### **Task 1: NED Fetcher (1 hour)**

**1.1: Create NEDFetcher class (40 min)**
```python
File: ned_fetcher.py

Features:
  □ NED queries via astroquery
  □ Cone search
  □ Query by name
  □ Redshift filtering
  □ Galaxy type filtering
  □ Column standardization
  
Methods:
  - __init__()
  - is_available()
  - cone_search(ra, dec, radius)
  - query_by_name(name)
  - query_by_redshift(z_min, z_max)
  - get_statistics()
```

**1.2: Test Suite (20 min)**
```python
File: test_ned_fetcher.py

Tests:
  □ Initialization
  □ Cone search
  □ Name query
  □ Redshift filtering
  □ Data validation
```

---

### **Task 2: SDSS Fetcher (1 hour)**

**2.1: SDSS Module (40 min)**
```python
File: sdss_fetcher.py

Features:
  □ SDSS queries via astroquery
  □ Spectroscopic data
  □ Photometric data
  □ SQL queries
  □ Galaxy properties
  
Methods:
  - cone_search()
  - spectroscopic_search()
  - get_galaxy_properties()
```

**2.2: Test Suite (20 min)**
```python
File: test_sdss_fetcher.py

Tests:
  □ Cone search
  □ Spectroscopic queries
  □ Photometry
  □ SQL queries
```

---

### **Task 3: Cosmological SSZ (45 min)**

**3.1: SSZ Cosmology Module (30 min)**
```python
File: ssz_cosmology.py

Features:
  □ Modified Hubble parameter (SSZ)
  □ Distance calculations (SSZ vs ΛCDM)
  □ Redshift corrections
  □ Hubble tension analysis
  
Functions:
  - H_ssz(z)
  - distance_modulus_ssz(z)
  - luminosity_distance_ssz(z)
  - hubble_tension_analysis()
```

**3.2: Testing (15 min)**
```python
File: test_ssz_cosmology.py
```

---

### **Task 4: Integration (30 min)**

**4.1: Catalog Integration (15 min)**
```python
Update: catalog_fetchers.py
  □ Import NED & SDSS fetchers
```

**4.2: Documentation (15 min)**
```markdown
Updates: README.md, docs
```

---

## ⏱️ TIME ESTIMATE

```
Task 1: NED Fetcher              1.0 hours
Task 2: SDSS Fetcher             1.0 hours
Task 3: SSZ Cosmology            0.75 hours
Task 4: Integration              0.5 hours

TOTAL: 3.25 hours planned
With velocity: ~45-60 minutes actual! 🚀
```

---

## 🚀 EXECUTION

**WICHTIG: Nach diesem Sprint → PAUSE!** ⚠️

Let's do this quickly and efficiently! 🌌

© 2025 Carmen Wrede, Lino Casu
