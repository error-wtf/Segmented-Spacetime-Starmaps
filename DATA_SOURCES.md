# Multi-Source Astronomical Data Requirements

## Problem: GAIA DR3 Limitations

**GAIA DR3 provides:**
- ✅ Astrometry (RA, Dec, parallax, proper motion)
- ✅ Photometry (G, BP, RP bands)
- ✅ Radial velocity (for subset of stars)
- ✅ 50M+ sources

**GAIA DR3 MISSING:**
- ❌ Spectroscopy (detailed spectral lines)
- ❌ Infrared photometry (thermal emission)
- ❌ Molecular data (gas, dust)
- ❌ Object classification (beyond basic)
- ❌ Extended sources (galaxies, nebulae)
- ❌ Complete all-sky coverage

---

## Required Data Sources

### 1. **SIMBAD** (CDS Strasbourg)
**Purpose:** Object identification & cross-references

**Provides:**
- Object names and aliases
- Object types (star, galaxy, nebula, etc.)
- Cross-references to other catalogs
- Bibliographic data
- Basic measurements

**Use cases:**
- Name resolution ("Betelgeuse" → coordinates)
- Object classification
- Finding related observations

**API:** http://simbad.u-strasbg.fr/simbad/sim-script

---

### 2. **ESO Archive** (European Southern Observatory)
**Purpose:** High-resolution spectroscopy & imaging

**Provides:**
- VLT spectroscopy (UVES, FLAMES, X-SHOOTER)
- High-resolution imaging (SPHERE, MUSE)
- Molecular line data
- Detailed chemical composition

**Use cases:**
- Stellar atmosphere analysis
- Velocity structure
- Chemical abundances

**API:** http://archive.eso.org/tap_obs

---

### 3. **ALMA Archive** (Atacama Large Millimeter Array)
**Purpose:** Molecular & dust emission

**Provides:**
- Molecular line observations (CO, H2O, etc.)
- Continuum emission (dust)
- High angular resolution (milliarcsec)
- Circumstellar disks, outflows

**Use cases:**
- Molecular cloud physics
- Dust properties
- Mass-loss rates

**API:** https://almascience.eso.org/tap

---

### 4. **AKARI** (Japanese IR satellite)
**Purpose:** Infrared photometry

**Provides:**
- 9, 18, 65, 90, 140, 160 μm bands
- All-sky infrared survey
- Thermal emission
- Dust temperatures

**Use cases:**
- Stellar temperatures
- Dust content
- Circumstellar material

**Catalogs:**
- IRC: Infrared Camera (9/18 μm)
- FIS: Far-Infrared Surveyor (65-160 μm)

**Access:** VizieR catalogs II/297 (IRC), II/298 (FIS)

---

### 5. **VizieR** (CDS catalog service)
**Purpose:** Catalog aggregation & cross-matching

**Provides:**
- 20,000+ astronomical catalogs
- Cross-matching between catalogs
- Unified query interface
- Historical data

**Use cases:**
- Finding complementary data
- Literature values
- Multi-wavelength photometry

**API:** http://vizier.u-strasbg.fr/viz-bin/votable

---

### 6. **2MASS** (Two Micron All-Sky Survey)
**Purpose:** Near-infrared photometry

**Provides:**
- J, H, K bands (1.25, 1.65, 2.17 μm)
- All-sky coverage
- Point sources & extended

**Use cases:**
- Extinction measurements
- Stellar populations
- Cool stars

**Access:** VizieR catalog II/246

---

## Data Integration Strategy

### Priority Levels:

1. **GAIA** (base astrometry) → Always query first
2. **SIMBAD** (identification) → Get object type & names
3. **AKARI/2MASS** (IR) → Thermal properties
4. **ESO/ALMA** (spectroscopy) → Detailed physics
5. **VizieR** (supplementary) → Fill gaps

### Workflow:

```
1. Query GAIA for astrometry
   ↓
2. Query SIMBAD for identification & cross-refs
   ↓
3. Query AKARI/2MASS for IR photometry
   ↓
4. Query ESO/ALMA for spectroscopy (if available)
   ↓
5. Cross-match with VizieR for additional data
   ↓
6. Merge into unified database
```

---

## Implementation Status

✅ **Implemented:**
- SIMBAD query function
- VizieR query function
- AKARI catalog access
- Multi-source query wrapper
- Data merging function

⏳ **TODO:**
- ESO TAP authentication
- ALMA query integration
- Automated cross-matching
- Database caching
- Quality flag handling

---

## Column Mapping

| Property | GAIA | SIMBAD | AKARI | ESO | ALMA |
|----------|------|---------|-------|-----|------|
| RA/Dec | ✅ | ✅ | ❌ | ✅ | ✅ |
| Parallax | ✅ | ✅ | ❌ | ❌ | ❌ |
| PM | ✅ | ❌ | ❌ | ❌ | ❌ |
| G-band | ✅ | ❌ | ❌ | ❌ | ❌ |
| IR bands | ❌ | ❌ | ✅ | ❌ | ❌ |
| Spectroscopy | ❌ | ❌ | ❌ | ✅ | ❌ |
| Molecular | ❌ | ❌ | ❌ | ✅ | ✅ |
| Type | ❌ | ✅ | ❌ | ❌ | ❌ |

---

## Usage Example

```python
from multi_source_data import query_multi_source, merge_multi_source_data

# Query Betelgeuse from multiple sources
results = query_multi_source(
    object_name="Betelgeuse",
    radius=1,
    sources=['SIMBAD', 'AKARI', 'VizieR']
)

# Merge into unified DataFrame
data = merge_multi_source_data(results)

print(data[['ra', 'dec', 'simbad_type', 'akari_9um', 'akari_18um']])
```

---

## References

- GAIA DR3: https://www.cosmos.esa.int/web/gaia/dr3
- SIMBAD: http://simbad.u-strasbg.fr/
- ESO Archive: http://archive.eso.org/
- ALMA Science Archive: https://almascience.eso.org/
- AKARI: https://www.ir.isas.jaxa.jp/AKARI/
- VizieR: https://vizier.u-strasbg.fr/
