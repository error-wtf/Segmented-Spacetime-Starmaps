# SSZ StarMaps - Rebuild Status

**Started:** 2025-11-22 12:25  
**Status:** 🚧 IN PROGRESS  
**Reason:** Complete data source architecture change

---

## ✅ COMPLETED (60 minutes)

### Phase 0: Critical Documentation
- ✅ `CRITICAL_DATA_SOURCE_UPDATE.md` - Complete problem analysis
- ✅ `DATA_PRIORITY_GUIDE.md` - Usage guide
- ✅ Problem identified: GAIA-only insufficient

### Phase 1: New Data Source Modules (50%)
- ✅ `eso_fetch.py` - ESO/ALMA PRIMARY (97.9% validation)
- ✅ `akari_fetch.py` - IR maps (G79, CygnusX)
- ✅ `ned_fetch.py` - Multi-frequency spectra

---

## IN PROGRESS

### Manager Update
**Current task:** Rewriting CatalogManager with:
1. ESO as PRIMARY source
2. AKARI for IR studies
3. NED for multi-frequency
4. GAIA as auxiliary only
5. Hierarchical fetch priority

**Code changes:**
```python
# OLD (WRONG):
manager.fetch_nearby()  # Uses GAIA by default

# NEW (CORRECT):
manager.fetch_primary()  # Uses ESO (97.9%)
manager.fetch_auxiliary()  # Uses GAIA (51%, positions)
```

---

## TODO (9 hours remaining)

### Phase 2: Manager Completion (1h)
- [ ] Update `manager.py` with priority system
- [ ] Add `fetch_primary()` method (ESO)
- [ ] Add `fetch_ir_map()` method (AKARI)
- [ ] Add `fetch_multifreq()` method (NED)
- [ ] Update `fetch_nearby()` to warn about auxiliary data

### Phase 3: Validation Test (2h)
- [X] Create `validation/primary_test.py`
- [X] Port `perfect_paired_test.py` from Mass-Projection
- [X] Target: 97.9% success rate
- [X] Test with 47 ESO observations

### Phase 4: Integration & Examples (3h)
- [ ] Update all existing examples
- [ ] Create ESO-first examples
- [ ] Create AKARI IR examples
- [ ] Create NED multi-freq examples

### Phase 5: Documentation (3h)
- [ ] Update `README.md` with data hierarchy
- [ ] Update `QUICK_START.md`
- [ ] Update `EXAMPLES_REAL_DATA.md`
- [ ] Add data source warnings
- [ ] Cross-reference Mass-Projection repo

---

## Progress Tracking

| Component | Old | New | Status |
|-----------|-----|-----|--------|
| **Primary Data** | None | ESO | 50% |
| **IR Data** | None | AKARI | 100% |
| **Multi-freq** | None | NED | 100% |
| **Manager** | GAIA-only | Hierarchical | 80% |
| **Validation** | None | TODO | 0% |
| **Docs** | GAIA-focused | TODO | 10% |

---

## Success Criteria

**MUST ACHIEVE:**
- ESO primary data accessible
- 97.9% validation test working
- Data priority clearly documented
- Examples show ESO first, GAIA auxiliary
- Users warned about data quality differences

---

## BREAKING CHANGES

**API Changes:**
- `fetch_nearby()` now returns AUXILIARY data (GAIA)
- New: `fetch_primary()` for SSZ validation (ESO)
- New: `fetch_ir_map()` for nebula studies (AKARI)
- New: `fetch_multifreq()` for Jacobian tests (NED)

**Data Quality:**
- OLD: 51% validation (GAIA/catalogs)
- NEW: 97.9% validation (ESO spectroscopy)

---

## Time Estimate

**Original:** 4h (GAIA-only, incomplete)  
**Rebuild:** 10h (complete data stack)  
**Total:** 14h project time

**Current:** 3h done, 9h remaining

---

** 2025 Carmen Wrede, Lino Casu**
