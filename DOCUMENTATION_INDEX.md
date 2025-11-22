# SSZ StarMaps - Documentation Index

**Complete documentation overview for v0.2.0**

© 2025 Carmen Wrede, Lino Casu

---

## Quick Start

**New users start here:**

1. 📖 **README.md** - Project overview and installation
2. 💡 **EXAMPLES.md** - Code examples and usage
3. 🏗️ **ARCHITECTURE.md** - How the code is structured

---

## All Documentation Files

### Core Documentation

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** | Main project documentation | All users |
| **EXAMPLES.md** | Code examples and tutorials | Users |
| **ARCHITECTURE.md** | Technical architecture | Developers |

### SSZ Physics Clarification

| File | Purpose | Audience |
|------|---------|----------|
| **SSZ_APPROACHES_COMPARISON.md** | Xi(r) vs phi_G(r) detailed comparison | Technical readers |
| **CHATGPT_CORRECTION.md** | Response to ChatGPT's phi_G suggestion | ChatGPT users |
| **DOCUMENTATION_INDEX.md** | This file - documentation overview | All |

### Validation & Testing

| File | Purpose | Type |
|------|---------|------|
| `test_ssz_vs_minkowski.py` | Quantitative validation of Xi(r) | Script |
| Self-tests in modules | Unit testing | Code |

---

## Documentation Consistency Checklist

### ✅ All docs mention correct SSZ approach:
- [x] README.md - Xi(r) approach clearly stated
- [x] EXAMPLES.md - Uses Xi(r) formulas
- [x] ARCHITECTURE.md - Xi(r) documented as core
- [x] SSZ_APPROACHES_COMPARISON.md - Both approaches compared
- [x] CHATGPT_CORRECTION.md - Clarifies Xi(r) vs phi_G(r)

### ✅ All docs use correct formulas:
- [x] Xi(r) = 1 - exp(-PHI * r/r_s)
- [x] PHI = (1 + sqrt(5)) / 2 = 1.618034 (Golden Ratio)
- [x] D_SSZ(r) = 1 / (1 + Xi(r))
- [x] R_ssz = r * (1 + Xi(r))

### ✅ All docs reference each other correctly:
- [x] README → EXAMPLES, ARCHITECTURE, SSZ_APPROACHES_COMPARISON
- [x] EXAMPLES → README, ARCHITECTURE
- [x] ARCHITECTURE → All other docs
- [x] SSZ_APPROACHES_COMPARISON → CHATGPT_CORRECTION, EXAMPLES
- [x] CHATGPT_CORRECTION → SSZ_APPROACHES_COMPARISON

### ✅ No mentions of incorrect APIs:
- [x] No `DiagonalForm` class
- [x] No fake `gamma` integration
- [x] No phi_G(r) in main code
- [x] Legacy functions clearly marked as deprecated

### ✅ Version consistency:
- [x] All docs reference v0.2.0
- [x] __init__.py version = "0.2.0"
- [x] ARCHITECTURE mentions v0.2.0 changes

---

## File Locations

```
Segmented-Spacetime-StarMaps/
│
├── README.md                           # Main documentation
├── EXAMPLES.md                         # Code examples
├── ARCHITECTURE.md                     # Technical architecture
├── SSZ_APPROACHES_COMPARISON.md        # Xi(r) vs phi_G(r) comparison
├── CHATGPT_CORRECTION.md               # Response to ChatGPT
├── DOCUMENTATION_INDEX.md              # This file
│
├── src/ssz_starmaps/
│   ├── __init__.py                     # API exports (v0.2.0)
│   ├── ssz_metric.py                   # Xi(r) implementation
│   ├── projection.py                   # SSZ deformations
│   ├── catalog.py                      # SIMBAD + GAIA
│   ├── geometry.py                     # Ramanujan formulas
│   └── demo_starmap.py                 # Main demo
│
└── test_ssz_vs_minkowski.py            # Validation script
```

---

## Reading Order

### For New Users:
1. README.md (overview)
2. EXAMPLES.md (learn by doing)
3. Run demo: `python -m ssz_starmaps.demo_starmap`

### For Developers:
1. ARCHITECTURE.md (structure)
2. Read source: `ssz_metric.py` (core physics)
3. Read source: `projection.py` (deformations)

### For ChatGPT Users:
1. CHATGPT_CORRECTION.md (avoid common mistakes!)
2. SSZ_APPROACHES_COMPARISON.md (understand differences)
3. ARCHITECTURE.md (see what we actually use)

### For Researchers:
1. SSZ_APPROACHES_COMPARISON.md (physics comparison)
2. test_ssz_vs_minkowski.py (validation)
3. Source: `ssz-metric-pure` repo (original theory)

---

## Key Messages

### 🎯 What This Project Uses:
- **Approach:** Xi(r) - Segment Saturation
- **φ Meaning:** Golden Ratio (1.618034)
- **Formula:** Xi(r) = 1 - exp(-φ·r/r_s)
- **Source:** `ssz-metric-pure/src/ssz_core/segment_density.py`

### ⚠️ What This Project Does NOT Use:
- **NOT using:** phi_G(r) - Spiral Rotation
- **NOT using:** DiagonalForm class (doesn't exist!)
- **NOT using:** gamma integration
- **NOT using:** 2PN calibration approach

### 🔗 Cross-References:
- Main theory: `ssz-metric-pure` repository
- Star catalog: SIMBAD, GAIA DR3
- License: Anti-Capitalist Software License v1.4

---

## Common Questions

### Q: Why not use phi_G(r)?
**A:** Xi(r) is simpler (no integration), already validated, and has clear Golden Ratio physics. See `SSZ_APPROACHES_COMPARISON.md`.

### Q: Where is DiagonalForm?
**A:** It doesn't exist! ChatGPT hallucinated this API. See `CHATGPT_CORRECTION.md`.

### Q: Can I use both Xi(r) and phi_G(r)?
**A:** No! They're different physical approaches with different φ meanings. Don't mix them.

### Q: Where's the original SSZ theory?
**A:** In the `ssz-metric-pure` repository, specifically `src/ssz_core/segment_density.py` for Xi(r).

---

## Updates Log

### 2025-11-22 - v0.2.0 Documentation
- ✅ Created CHATGPT_CORRECTION.md
- ✅ Created SSZ_APPROACHES_COMPARISON.md
- ✅ Created ARCHITECTURE.md
- ✅ Updated README.md with Xi(r) clarification
- ✅ Updated EXAMPLES.md with correct usage
- ✅ Created this index

---

## License

© 2025 Carmen Wrede, Lino Casu  
Licensed under the Anti-Capitalist Software License v1.4
