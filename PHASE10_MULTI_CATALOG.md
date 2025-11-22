# 🚀 PHASE 10: MULTI-CATALOG & NAME SEARCH

**Start:** 2025-11-22, 20:45 UTC+1
**Ziel:** Namen-Suche + Alle Datenbanken integrieren

---

## 📋 REQUIREMENTS:

### 1. Namen-Suche mit Aliases
**Beispiele:**
- "Sag A*" → Sgr A*
- "Sagittarius A*" → Sgr A*
- "Betelgeuse" → α Ori
- "Proxima" → Proxima Centauri
- "Andromeda" → M31

**Implementation:**
- SIMBAD Name Resolver
- Alias Mapping
- Fuzzy Matching

### 2. Multi-Catalog Integration
**Catalogs:**
- ✅ GAIA DR3 (500k already)
- ⭕ ESO
- ⭕ ALMA
- ⭕ Akari
- ⭕ 2MASS
- ⭕ WISE
- ⭕ Hipparcos
- ⭕ SIMBAD

**Strategy:**
- Query multiple catalogs
- Merge results
- Remove duplicates
- Combine data columns

### 3. Combined Database
**Structure:**
```
combined_database/
├── gaia_500k.csv (base)
├── simbad_names.csv (aliases)
├── multi_catalog_cache.csv (merged queries)
└── famous_objects.csv (curated list)
```

---

## 🎯 IMPLEMENTATION PLAN:

### Phase 10.1: Name Resolver (30 min)
- [ ] SIMBAD integration
- [ ] Alias mapping
- [ ] Cache results

### Phase 10.2: Multi-Catalog Query (40 min)
- [ ] Query builder
- [ ] Parallel fetching
- [ ] Result merging

### Phase 10.3: Famous Objects DB (20 min)
- [ ] Curated list (Sag A*, M31, etc.)
- [ ] Instant lookup
- [ ] Coordinates + Info

### Phase 10.4: UI Integration (20 min)
- [ ] Name search field
- [ ] Catalog selector
- [ ] Combined results view

---

## ⏱️ TOTAL: ~110 Minuten (1.8 Std)

**STARTE JETZT!** 🚀
