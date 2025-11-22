# 🚀 SSZ Explorer - Verbesserungs-Fahrplan

**Erstellt:** 2025-11-22  
**Status:** PRODUCTION (82% komplett)  
**Nächste Ziele:** Progressive Daten-Nachladen + Performance

---

## ⚠️ KRITISCHES PROBLEM (HÖCHSTE PRIORITÄT)

### **Problem: Daten werden nicht nachgeladen**

**Symptom:**
- ✅ Beim Start: Daten werden geladen (1k-10k Objekte)
- ❌ Beim Rauszoomen: Keine neuen Daten
- ❌ Beim Verlassen des Bereichs: Keine neuen Daten
- ❌ Map wird "leer" außerhalb des Start-Bereichs

**Ursache:**
```python
# data_manager.py - Zeile 48-72
# Lädt nur EINMAL beim Init, dann nie wieder!
def __init__(self, cache_dir='ssz_data/cache', default_level='standard'):
    self.current_data = None  # Wird nur einmal gesetzt
    # ❌ Kein dynamisches Nachladen implementiert!
```

**Impact:** 🔴 KRITISCH
- Nutzer sehen nur ~10% des Himmels
- Schlechte User Experience
- Katalog-Features werden nicht genutzt (2.2B Objekte verfügbar, aber nicht sichtbar)

---

## 🎯 FAHRPLAN - 3 PHASEN

### **PHASE 1: KRITISCHE FIXES (JETZT - 2-5 Stunden)**

#### 1.1 Dynamisches Daten-Nachladen ⭐⭐⭐⭐⭐

**Was:**
- Implementiere automatisches Nachladen wenn:
  - User raus-zoomt
  - User pan/scroll macht
  - Aktueller Viewport hat wenige Objekte (<100)

**Wo:**
- Neue Klasse: `ViewportManager` in `data_manager.py`
- Integration in: `interactive_skymap_app.py`

**Implementation:**
```python
class ViewportManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.current_viewport = None
        self.loaded_regions = []  # Track geladene Bereiche
        
    def update_viewport(self, ra_min, ra_max, dec_min, dec_max, zoom_level):
        """Prüfe ob neue Daten nötig sind."""
        if self._needs_reload(ra_min, ra_max, dec_min, dec_max):
            new_data = self._fetch_for_viewport(ra_min, ra_max, dec_min, dec_max)
            return new_data
        return None
    
    def _needs_reload(self, ra_min, ra_max, dec_min, dec_max):
        """Prüfe ob Viewport außerhalb geladener Bereiche."""
        for region in self.loaded_regions:
            if self._viewport_in_region(ra_min, ra_max, dec_min, dec_max, region):
                return False
        return True
    
    def _fetch_for_viewport(self, ra_min, ra_max, dec_min, dec_max):
        """Lade Daten für neuen Viewport."""
        # Nutze GAIA cone_search mit center + radius
        ra_center = (ra_min + ra_max) / 2
        dec_center = (dec_min + dec_max) / 2
        radius = max(abs(ra_max - ra_min), abs(dec_max - dec_min)) / 2
        
        return self.data_manager.fetch_cone(ra_center, dec_center, radius)
```

**Zeit:** 3-4 Stunden  
**Impact:** 🔴 KRITISCH - Löst Hauptproblem

---

#### 1.2 Cache-System Optimierung ⭐⭐⭐⭐

**Was:**
- Intelligentes Caching geladener Regionen
- LRU (Least Recently Used) Eviction
- Persistent Cache auf Disk

**Implementation:**
```python
class RegionCache:
    def __init__(self, max_regions=50, cache_dir='ssz_data/cache/regions'):
        self.cache = {}  # {region_id: DataFrame}
        self.access_times = {}
        self.max_regions = max_regions
        self.cache_dir = Path(cache_dir)
        
    def get(self, region_id):
        """Hole Region aus Cache (Memory oder Disk)."""
        if region_id in self.cache:
            self.access_times[region_id] = datetime.now()
            return self.cache[region_id]
        
        # Try disk cache
        cache_file = self.cache_dir / f"{region_id}.parquet"
        if cache_file.exists():
            df = pd.read_parquet(cache_file)
            self._add_to_memory(region_id, df)
            return df
        
        return None
    
    def set(self, region_id, data):
        """Speichere Region in Cache."""
        # Memory
        self._add_to_memory(region_id, data)
        
        # Disk (persistent)
        cache_file = self.cache_dir / f"{region_id}.parquet"
        data.to_parquet(cache_file)
    
    def _add_to_memory(self, region_id, data):
        """Füge zu Memory Cache hinzu, evict wenn nötig."""
        if len(self.cache) >= self.max_regions:
            # Remove least recently used
            lru_id = min(self.access_times, key=self.access_times.get)
            del self.cache[lru_id]
            del self.access_times[lru_id]
        
        self.cache[region_id] = data
        self.access_times[region_id] = datetime.now()
```

**Zeit:** 2 Stunden  
**Impact:** 🟡 HOCH - Massive Performance-Verbesserung

---

#### 1.3 Progress Indicators ⭐⭐⭐

**Was:**
- Loading Spinner beim Nachladen
- Progress Bar für große Queries
- "Loading region..." Message

**Wo:**
- Gradio UI: `gradio_app_extended.py`
- HTML Output: Custom CSS/JS

**Zeit:** 1 Stunde  
**Impact:** 🟢 MITTEL - Bessere UX

---

### **PHASE 2: PERFORMANCE & FEATURES (NÄCHSTE WOCHE - 10-15 Stunden)**

#### 2.1 Adaptive Level-of-Detail (LOD) ⭐⭐⭐⭐⭐

**Was:**
- Zoom Level 1 (weit raus): 1k Objekte, nur helle Sterne
- Zoom Level 2 (mittel): 10k Objekte
- Zoom Level 3 (nah): 100k Objekte, alle Details
- Zoom Level 4 (sehr nah): 1M Objekte, Exoplaneten sichtbar

**Implementation:**
```python
class LODManager:
    def __init__(self):
        self.zoom_levels = {
            1: {'max_objects': 1000, 'mag_limit': 6.0, 'catalogs': ['gaia']},
            2: {'max_objects': 10000, 'mag_limit': 10.0, 'catalogs': ['gaia', 'simbad']},
            3: {'max_objects': 100000, 'mag_limit': 15.0, 'catalogs': ['gaia', 'simbad', '2mass']},
            4: {'max_objects': 1000000, 'mag_limit': 20.0, 'catalogs': ['gaia', 'simbad', '2mass', 'wise', 'exoplanets']}
        }
    
    def get_query_params(self, zoom_level):
        """Hole optimale Query-Parameter für Zoom Level."""
        return self.zoom_levels.get(zoom_level, self.zoom_levels[2])
```

**Zeit:** 4-5 Stunden  
**Impact:** 🔴 KRITISCH - Skalierbarkeit!

---

#### 2.2 Multi-Catalog Streaming ⭐⭐⭐⭐

**Was:**
- Paralleles Laden aus mehreren Katalogen
- Async/Threading für schnellere Queries
- Priority Queue (GAIA zuerst, dann Rest)

**Implementation:**
```python
import asyncio
import concurrent.futures

class StreamingFetcher:
    def __init__(self):
        self.fetchers = {
            'gaia': GAIAFetcher(),
            'simbad': SIMBADFetcher(),
            '2mass': TwoMASSFetcher(),
            'wise': WISEFetcher()
        }
    
    async def fetch_parallel(self, ra, dec, radius, catalogs=['gaia', 'simbad']):
        """Lade aus mehreren Katalogen parallel."""
        tasks = []
        for cat in catalogs:
            if cat in self.fetchers:
                task = asyncio.create_task(
                    self._fetch_async(cat, ra, dec, radius)
                )
                tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return self._merge_results(results)
    
    async def _fetch_async(self, catalog, ra, dec, radius):
        """Async fetch wrapper."""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool, 
                self.fetchers[catalog].cone_search,
                ra, dec, radius
            )
        return result
```

**Zeit:** 3-4 Stunden  
**Impact:** 🟡 HOCH - 3-5x schneller

---

#### 2.3 Smart Sampling ⭐⭐⭐

**Was:**
- Bei zu vielen Objekten: Intelligentes Sampling
- Behalte: Helle Sterne, Spezielle Objekte, Exoplaneten
- Verwerfe: Schwache Sterne zufällig

**Zeit:** 2 Stunden  
**Impact:** 🟢 MITTEL - Memory-Einsparung

---

#### 2.4 Heatmap Mode ⭐⭐⭐

**Was:**
- Wenn >100k Objekte: Zeige Heatmap statt Punkte
- Aggregiere Dichte in Grid
- Schneller Überblick über Verteilung

**Zeit:** 3 Stunden  
**Impact:** 🟢 MITTEL - Alternative Visualisierung

---

### **PHASE 3: ADVANCED FEATURES (NÄCHSTER MONAT - 20-30 Stunden)**

#### 3.1 Query Builder UI ⭐⭐⭐⭐

**Was:**
- Interaktive Query-Erstellung
- Filter: Magnitude, Farbe, Typ, etc.
- Saved Queries
- History

**Zeit:** 5-6 Stunden  
**Impact:** 🟡 HOCH - Power User Feature

---

#### 3.2 Object Clustering ⭐⭐⭐

**Was:**
- Bei weit raus-zoomen: Cluster Objekte
- Zeige "500 objects in this region" statt 500 Punkte
- Click to expand Cluster

**Zeit:** 4-5 Stunden  
**Impact:** 🟡 HOCH - Übersichtlichkeit

---

#### 3.3 Data Export & Bookmarks ⭐⭐⭐

**Was:**
- Speichere aktuelle Ansicht
- Export sichtbare Objekte als CSV/FITS
- Bookmark interessante Regionen
- Share Link (URL mit Viewport)

**Zeit:** 3-4 Stunden  
**Impact:** 🟢 MITTEL - Wissenschaftliche Nutzung

---

#### 3.4 Background Prefetching ⭐⭐⭐⭐

**Was:**
- Lade angrenzende Regionen im Hintergrund
- Predict User Movement
- Smooth Experience

**Zeit:** 4-5 Stunden  
**Impact:** 🟡 HOCH - Proaktiv

---

#### 3.5 Offline Mode ⭐⭐

**Was:**
- Vollständige Region Download
- Arbeite ohne Internet
- Sync später

**Zeit:** 6-8 Stunden  
**Impact:** 🟢 NIEDRIG - Nische

---

## 📊 TECHNISCHE VERBESSERUNGEN

### Performance Optimizations

**1. Database Backend ⭐⭐⭐⭐**
```python
# Statt Parquet: Nutze DuckDB für schnelle Queries
import duckdb

class DuckDBCache:
    def __init__(self, db_file='ssz_data/cache.duckdb'):
        self.conn = duckdb.connect(db_file)
        self._init_tables()
    
    def query_viewport(self, ra_min, ra_max, dec_min, dec_max):
        """Sehr schnelle Spatial Query."""
        return self.conn.execute(f"""
            SELECT * FROM stars 
            WHERE ra BETWEEN {ra_min} AND {ra_max}
              AND dec BETWEEN {dec_min} AND {dec_max}
        """).df()
```

**Zeit:** 3-4 Stunden  
**Impact:** 🔴 KRITISCH - 10-100x schneller

---

**2. Spatial Indexing ⭐⭐⭐⭐**
```python
# R-Tree Index für schnelle Spatial Queries
from rtree import index

class SpatialIndex:
    def __init__(self):
        self.idx = index.Index()
        self.objects = {}
    
    def insert(self, obj_id, ra, dec):
        """Füge Objekt zu Spatial Index."""
        self.idx.insert(obj_id, (ra, dec, ra, dec))
        self.objects[obj_id] = {'ra': ra, 'dec': dec}
    
    def query_region(self, ra_min, ra_max, dec_min, dec_max):
        """Finde alle Objekte in Region (sehr schnell!)."""
        hits = list(self.idx.intersection((ra_min, dec_min, ra_max, dec_max)))
        return [self.objects[h] for h in hits]
```

**Zeit:** 2-3 Stunden  
**Impact:** 🟡 HOCH - Schnelle Lookups

---

**3. Data Compression ⭐⭐⭐**
```python
# Komprimiere Cache-Dateien
import blosc2

def compress_dataframe(df):
    """Komprimiere DataFrame ~5-10x."""
    buffer = df.to_parquet()
    compressed = blosc2.compress(buffer, codec='zstd', clevel=9)
    return compressed

def decompress_dataframe(compressed):
    """Dekomprimiere zurück zu DataFrame."""
    buffer = blosc2.decompress(compressed)
    return pd.read_parquet(io.BytesIO(buffer))
```

**Zeit:** 1-2 Stunden  
**Impact:** 🟢 MITTEL - Weniger Disk Space

---

## 🎨 UI/UX VERBESSERUNGEN

### 1. Mini-Map ⭐⭐⭐⭐
**Was:** Kleine Übersichtskarte zeigt wo User ist  
**Zeit:** 2-3 Stunden

### 2. Object Info Panel ⭐⭐⭐⭐
**Was:** Click auf Stern → Zeige Details (Mag, Type, Distance, etc.)  
**Zeit:** 2-3 Stunden

### 3. Search Function ⭐⭐⭐⭐⭐
**Was:** "Go to M31", "Find Betelgeuse", etc.  
**Zeit:** 2 Stunden

### 4. Layer Toggle ⭐⭐⭐
**Was:** Toggle Catalogs on/off (GAIA, SIMBAD, Exoplanets separat)  
**Zeit:** 1-2 Stunden

### 5. Night Mode ⭐⭐
**Was:** Dunkles Theme für Astronomen  
**Zeit:** 1 Stunde

---

## 📅 ZEITPLAN & PRIORITÄTEN

### **WOCHE 1 (JETZT): Kritische Fixes**
```
Tag 1-2: Dynamisches Nachladen (Phase 1.1) ⭐⭐⭐⭐⭐
Tag 3: Cache-Optimierung (Phase 1.2) ⭐⭐⭐⭐
Tag 4: Progress Indicators (Phase 1.3) ⭐⭐⭐
Tag 5: Testing & Bug Fixes

Ergebnis: Basisfunktionalität komplett ✅
```

### **WOCHE 2-3: Performance & Features**
```
Woche 2:
  - LOD System (Phase 2.1) ⭐⭐⭐⭐⭐
  - Multi-Catalog Streaming (Phase 2.2) ⭐⭐⭐⭐
  - DuckDB Backend (Tech.1) ⭐⭐⭐⭐

Woche 3:
  - Smart Sampling (Phase 2.3) ⭐⭐⭐
  - Spatial Index (Tech.2) ⭐⭐⭐⭐
  - Query Builder UI (Phase 3.1) ⭐⭐⭐⭐

Ergebnis: Professionelles Tool ✅
```

### **MONAT 2: Advanced Features**
```
  - Object Clustering (Phase 3.2)
  - Background Prefetching (Phase 3.4)
  - Alle UI Improvements
  - Heatmap Mode (Phase 2.4)

Ergebnis: Production-Grade Platform ✅
```

---

## 🎯 QUICK WINS (Heute noch!)

**Diese können SOFORT gemacht werden:**

### 1. Größere Initial Region (30 min)
```python
# In catalog_fetchers.py
# Ändere default radius von 1° auf 10°
def fetch_initial_data(ra=0, dec=0, radius=10.0):  # War: 1.0
    return cone_search(ra, dec, radius, max_results=50000)  # War: 10000
```

### 2. Magnitude Limit erhöhen (15 min)
```python
# Zeige schwächere Sterne
# phot_g_mean_mag < 15.0 statt 10.0
```

### 3. Warn User bei Viewport Change (15 min)
```python
def on_viewport_change(ra, dec):
    if not has_data_for_region(ra, dec):
        gr.Warning("⚠️ No data for this region yet. Loading...")
```

**Total: 1 Stunde → Sofortige Verbesserung!**

---

## 🔧 IMPLEMENTATION STARTER

**Ich kann JETZT implementieren:**

**Option A:** Nur Quick Wins (1 Stunde)  
**Option B:** Phase 1 komplett (2-5 Stunden)  
**Option C:** Phase 1 + Phase 2.1 (LOD) (6-10 Stunden)

**Was möchtest du?**

---

## 📈 IMPACT MATRIX

```
Feature                     Impact    Effort    Priority
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dynamisches Nachladen      🔴 HOCH   3h        ⭐⭐⭐⭐⭐
LOD System                  🔴 HOCH   4h        ⭐⭐⭐⭐⭐
DuckDB Backend              🔴 HOCH   3h        ⭐⭐⭐⭐
Cache Optimierung           🟡 MITTEL 2h        ⭐⭐⭐⭐
Spatial Index               🟡 MITTEL 2h        ⭐⭐⭐⭐
Multi-Catalog Streaming     🟡 MITTEL 3h        ⭐⭐⭐⭐
Search Function             🟡 MITTEL 2h        ⭐⭐⭐⭐
Query Builder               🟡 MITTEL 5h        ⭐⭐⭐
Object Info Panel           🟢 NIEDRIG 2h       ⭐⭐⭐
Progress Indicators         🟢 NIEDRIG 1h       ⭐⭐⭐
Mini-Map                    🟢 NIEDRIG 2h       ⭐⭐⭐
Background Prefetch         🟡 MITTEL 4h        ⭐⭐
Heatmap Mode                🟢 NIEDRIG 3h       ⭐⭐
Object Clustering           🟢 NIEDRIG 4h       ⭐⭐
```

---

## 💡 EMPFEHLUNG

**JETZT SOFORT (heute Abend):**
1. Quick Wins umsetzen (1h) → Sofortige Verbesserung
2. Dynamisches Nachladen starten (3-4h) → Hauptproblem lösen

**NÄCHSTE WOCHE:**
3. LOD System (4h) → Skalierbarkeit
4. DuckDB Backend (3h) → Performance

**DANN:**
- Alles andere nach Bedarf

**Soll ich mit den Quick Wins anfangen?** 🚀

---

© 2025 Carmen Wrede, Lino Casu  
Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
