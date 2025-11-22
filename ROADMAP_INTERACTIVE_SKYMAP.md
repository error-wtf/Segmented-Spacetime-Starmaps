# Roadmap: Interactive3D-Style 3D Interactive Skymap

**Vision:** Eine interaktive 3D-Sternenkarte mit SSZ-Physik wie in Interactive3D  
**Ziel:** Echtes, spielbares Programm zur Visualisierung von Segmented Spacetime  
**Technologie:** Python + moderne 3D-Grafik + Interaktivität

---

## 🎯 VISION: Was wir bauen wollen

### Interactive3D-Style Features:
1. **3D-Navigation**
   - Freie Kamerabewegung durch Raum
   - Zoom in/out (Parsec → Lichtjahr → AU scale)
   - Rotation, Pan, Fly-through

2. **Interaktive Sterne**
   - Click auf Stern → Info-Panel
   - SSZ-Effekte live visualisiert
   - Distanz-Messungen (Minkowski vs SSZ)
   - Gravitationsfelder sichtbar

3. **Visual Effects**
   - Sterne als leuchtende Punkte/Sphären
   - SSZ-Deformation als Glow/Halo
   - Gravitationslinsen-Effekte
   - Farbkodierung (Spektraltyp, SSZ-Stretch)

4. **UI/HUD**
   - Info-Panel (Stern-Properties)
   - SSZ-Parameter-Anzeige
   - Search & Filter
   - Mini-Map/Galactic Overview

5. **Physics-Accurate**
   - Echte GAIA-Positionen
   - SSZ-Transformationen live
   - Metriken-Visualisierung
   - Time-Dilation-Effekte

---

## 🏗️ TECHNOLOGIE-STACK

### Option A: **Plotly + Dash** (Web-basiert)
✅ **Vorteile:**
- Bereits teilweise vorhanden (viz/compare.py)
- Web-basiert (Browser, keine Installation)
- Interaktive 3D (plotly.graph_objects.Scatter3d)
- UI mit Dash Components
- Python-only (kein C++/OpenGL)

❌ **Nachteile:**
- Performance bei 10,000+ Sternen begrenzt
- Weniger "game-like" feel
- Limitierte Shader-Effekte

### Option B: **PyGame + OpenGL** (Desktop App)
✅ **Vorteile:**
- Echte Game-Engine feel
- Direkte GPU-Beschleunigung
- Custom Shader (GLSL)
- Volle Performance

❌ **Nachteile:**
- Mehr Code (Rendering-Pipeline)
- Installation nötig
- Komplexer Setup

### Option C: **Unity/Godot + Python** (Hybrid)
✅ **Vorteile:**
- Professionelle Game-Engine
- Beste Grafik
- Editor-Tools

❌ **Nachteile:**
- Nicht Pure Python
- Komplexe Integration
- Overkill für Wissenschafts-Tool?

### 🎯 **EMPFEHLUNG: Start mit Plotly+Dash, später PyGame**

Grund:
1. Plotly bereits vorhanden → schneller Start
2. Web = einfache Verteilung
3. Später: PyGame-Port für Performance

---

## 📋 IMPLEMENTIERUNGS-FAHRPLAN

### **Phase 1: 3D Foundation (4 Stunden)**

**Ziel:** Basis-3D-Viewer mit GAIA-Daten

**Tasks:**
1. ✅ 3D Scatter Plot (Plotly)
   - X, Y, Z aus GAIA (galaktische Koordinaten)
   - 1000 Sterne initial
   - Farbkodierung (Temperatur/Magnitude)

2. ✅ Interaktive Controls
   - Camera Rotation (Drag)
   - Zoom (Scroll)
   - Pan (Shift+Drag)

3. ✅ Hover Info
   - Stern-Name
   - RA/Dec, Distanz
   - Magnitude, Spektraltyp

**Code:**
```python
import plotly.graph_objects as go
from ssz_starmaps.catalogs import fetch_gaia_nearby

stars = fetch_gaia_nearby(distance_pc=100, max_stars=1000)

# 3D Scatter
fig = go.Figure(data=[go.Scatter3d(
    x=stars['x'],
    y=stars['y'],
    z=stars['z'],
    mode='markers',
    marker=dict(
        size=5,
        color=stars['temperature'],
        colorscale='Viridis',
        showscale=True
    ),
    text=stars['name'],
    hoverinfo='text'
)])

fig.show()
```

**Deliverables:**
- `skymap_3d_basic.py` - Basis-Viewer
- Funktioniert mit 1000+ Sternen

---

### **Phase 2: SSZ Integration (6 Stunden)**

**Ziel:** SSZ-Physik live visualisieren

**Tasks:**
1. ✅ SSZ-Transform on-the-fly
   - Berechne SSZ-Positionen
   - Vergleich Minkowski vs SSZ
   - Toggle zwischen beiden

2. ✅ Visual SSZ-Effekte
   - Glow-Intensity ∝ Stretch-Factor
   - Farbshift für Time-Dilation
   - Gravitationsfeld als Halo

3. ✅ Dual-View Mode
   - Split-Screen: Links Minkowski, Rechts SSZ
   - Sync Camera
   - Highlight Unterschiede

**Code:**
```python
from ssz_starmaps.transform import transform_catalog

# Transform
stars_ssz = transform_catalog(stars)

# Dual plot
fig = make_subplots(
    rows=1, cols=2,
    specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}]],
    subplot_titles=('Minkowski', 'SSZ')
)

# Left: Original
fig.add_trace(go.Scatter3d(...), row=1, col=1)

# Right: SSZ
fig.add_trace(go.Scatter3d(
    x=stars_ssz['x_ssz'],
    y=stars_ssz['y_ssz'],
    z=stars_ssz['z_ssz'],
    marker=dict(
        size=5 * stars_ssz['stretch_factor'],  # Size ∝ stretch
        color=stars_ssz['D_ssz']  # Color = time dilation
    )
), row=1, col=2)
```

**Deliverables:**
- `skymap_ssz_interactive.py` - SSZ-Viewer
- Dual-View funktionsfähig

---

### **Phase 3: UI/HUD System (6 Stunden)**

**Ziel:** Interactive3D-style Interface

**Tasks:**
1. ✅ Info-Panel (Dash)
   - Selected Star Info
   - SSZ Parameters
   - Distance Measurements

2. ✅ Control Panel
   - Slider: Distance Filter
   - Toggle: Show SSZ Effects
   - Dropdown: Color by (Temp/Magnitude/SSZ)

3. ✅ Search & Select
   - Star Name Search
   - Jump to Star
   - Bookmark Favorites

**Layout:**
```
┌─────────────────────────────────────┐
│  SSZ SKYMAP                    [X]  │
├─────────────────────────────────────┤
│ [Search: ____] [Filter] [Settings] │
├─────────────┬───────────────────────┤
│             │                       │
│  Controls   │    3D View (Main)     │
│             │                       │
│  - Distance │                       │
│  - SSZ ON/  │                       │
│  - Colors   │                       │
│             │                       │
├─────────────┼───────────────────────┤
│ Selected:   │  SSZ Parameters       │
│ Sirius      │  r*: 1.387 r_s       │
│ Dist: 8.6pc │  Stretch: 2.15x      │
└─────────────┴───────────────────────┘
```

**Deliverables:**
- `skymap_dashboard.py` - Full App
- Dash-basiert, Web-Interface

---

### **Phase 4: Advanced Graphics (8 Stunden)**

**Ziel:** Interactive3D-level Grafik

**Tasks:**
1. ✅ Gravitationslinsen
   - Raytracing für Lichtablenkung
   - Multiple Images (Einstein Ring)
   - Magnification

2. ✅ Particle Effects
   - Star Glow (Post-Processing)
   - Nebulae (Volume Rendering)
   - Gravitationswellen (Animation)

3. ✅ Background
   - Milchstraße Panorama
   - Distant Galaxies
   - Realistic Sky

4. ✅ Performance
   - LOD (Level of Detail)
   - Octree Culling
   - GPU Acceleration

**Deliverables:**
- `skymap_advanced.py` - High-Quality Renderer
- 10,000+ Sterne smooth

---

### **Phase 5: Interactive Features (6 Stunden)**

**Ziel:** Game-like Interaktivität

**Tasks:**
1. ✅ Path Planning
   - Click 2 stars → Show path
   - Distance (Minkowski vs SSZ)
   - Travel time (subluminal)

2. ✅ Region Highlighting
   - Select region (box/sphere)
   - Statistics für Region
   - Export selected stars

3. ✅ Annotations
   - Labels für wichtige Sterne
   - Linien (Konstellationen)
   - Custom Markers

4. ✅ Animation
   - Time Evolution (proper motion)
   - Orbit-Visualisierung
   - SSZ-Effekt over time

**Deliverables:**
- `skymap_interactive.py` - Full Features
- Game-like Experience

---

### **Phase 6: Data Integration (4 Stunden)**

**Ziel:** Alle Datenquellen verfügbar

**Tasks:**
1. ✅ Multi-Source Loader
   - GAIA (positions)
   - ESO (spectroscopy)
   - AKARI (IR overlay)
   - NED (multi-freq)

2. ✅ Data Layers
   - Toggle: GAIA stars
   - Toggle: ESO observations
   - Toggle: AKARI maps
   - Toggle: NED objects

3. ✅ Smart Loading
   - Stream data (nicht alles auf einmal)
   - Cache Management
   - Progressive Detail

**Deliverables:**
- Full data integration
- Alle Quellen nutzbar

---

### **Phase 7: Polish & Distribution (4 Stunden)**

**Ziel:** Production-Ready

**Tasks:**
1. ✅ UI Polish
   - Dark Theme (Space-like)
   - Icons & Graphics
   - Smooth Animations

2. ✅ Documentation
   - User Manual
   - Keyboard Shortcuts
   - Tutorial Mode

3. ✅ Packaging
   - Standalone Executable (PyInstaller)
   - Web-Version (deploy)
   - GitHub Release

**Deliverables:**
- `ssz-skymap.exe` (Windows)
- Web-Version hosted
- Full documentation

---

## 🎨 DESIGN MOCKUP

### Main View (3D):
```
        ╔════════════════════════════════════════╗
        ║  ░░ Stars as points/spheres         ║
        ║     • Size ∝ Magnitude              ║
        ║     • Color ∝ Temperature           ║
        ║     • Glow ∝ SSZ-Stretch            ║
        ║                                      ║
        ║           ⭐ Sirius                  ║
        ║        ⭐                            ║
        ║  ⭐                 ⭐               ║
        ║       ⭐  Proxima    ⭐              ║
        ║            Centauri                 ║
        ║  ⭐        ⭐           ⭐            ║
        ║                                      ║
        ╚════════════════════════════════════════╝
```

### Info Panel:
```
┌─────────────────────────────────────┐
│ SELECTED: Sirius (α CMa)           │
├─────────────────────────────────────┤
│ Type: A1V (Main Sequence)          │
│ Distance: 8.6 pc (Minkowski)        │
│           9.5 pc (SSZ)              │
│ Magnitude: -1.46 (brightest)        │
│                                     │
│ SSZ PARAMETERS:                     │
│ ├─ r_s: 5.9 km                     │
│ ├─ Xi(r): 0.98                     │
│ ├─ D_SSZ: 0.505                    │
│ ├─ Stretch: 1.98x                  │
│ └─ Time Dilation: 50.5%            │
│                                     │
│ [Jump to] [Bookmark] [Details]     │
└─────────────────────────────────────┘
```

---

## 📊 IMPLEMENTIERUNGS-ZEITPLAN

| Phase | Beschreibung | Zeit | Priorität |
|-------|--------------|------|-----------|
| **Phase 1** | 3D Foundation | 4h | 🔴 CRITICAL |
| **Phase 2** | SSZ Integration | 6h | 🔴 CRITICAL |
| **Phase 3** | UI/HUD | 6h | 🟡 HIGH |
| **Phase 4** | Advanced Graphics | 8h | 🟢 MEDIUM |
| **Phase 5** | Interactivity | 6h | 🟡 HIGH |
| **Phase 6** | Data Integration | 4h | 🟡 HIGH |
| **Phase 7** | Polish | 4h | 🟢 MEDIUM |
| **TOTAL** | | **38h** | |

**MVP (Minimum Viable Product):** Phase 1-3 = 16 Stunden  
**Full Release:** Alle Phasen = 38 Stunden

---

## 🎯 MILESTONE TARGETS

### MVP (16h):
- ✅ 3D-Viewer funktioniert
- ✅ GAIA-Daten geladen
- ✅ SSZ-Transform visualisiert
- ✅ Basic UI (Dash)
- ✅ Click auf Stern → Info

### Beta (28h):
- ✅ Advanced Graphics
- ✅ Alle Interaktivität
- ✅ Multi-Source Daten
- ✅ Performance optimiert

### Release (38h):
- ✅ Production-Ready
- ✅ Dokumentiert
- ✅ Packaging
- ✅ Tutorial

---

## 💻 EXAMPLE CODE STRUCTURE

```
ssz-skymap/
├── skymap/
│   ├── __init__.py
│   ├── core/
│   │   ├── renderer.py       # 3D rendering engine
│   │   ├── camera.py         # Camera controls
│   │   └── scene.py          # Scene management
│   ├── physics/
│   │   ├── ssz_transform.py  # SSZ calculations
│   │   ├── coordinates.py    # Coord transforms
│   │   └── metrics.py        # Distance, time dilation
│   ├── data/
│   │   ├── loader.py         # Data loading
│   │   ├── cache.py          # Caching system
│   │   └── filters.py        # Data filtering
│   ├── ui/
│   │   ├── dashboard.py      # Dash app
│   │   ├── panels.py         # UI panels
│   │   └── controls.py       # Interactive controls
│   └── graphics/
│       ├── effects.py        # Visual effects
│       ├── shaders/          # GLSL shaders (optional)
│       └── materials.py      # Star materials
├── app.py                    # Main application
├── config.yaml               # Configuration
└── README.md
```

---

## 🚀 QUICK START PROTOTYPE

**Erstelle jetzt in 30 Minuten:**

```python
# skymap_proto.py - Quick Prototype
import plotly.graph_objects as go
from ssz_starmaps.catalogs import fetch_gaia_nearby
from ssz_starmaps.transform import transform_catalog

# Load stars
stars = fetch_gaia_nearby(distance_pc=50, max_stars=500)

# Convert to 3D (galactic coords)
from astropy.coordinates import SkyCoord
coords = SkyCoord(
    ra=stars['ra'].values,
    dec=stars['dec'].values,
    distance=stars['distance_pc'].values,
    unit=('deg', 'deg', 'pc'),
    frame='icrs'
)
gal = coords.galactic
x, y, z = gal.cartesian.xyz.value

# SSZ Transform
stars_ssz = transform_catalog(stars)

# 3D Plot
fig = go.Figure()

# Original
fig.add_trace(go.Scatter3d(
    x=x, y=y, z=z,
    mode='markers',
    marker=dict(size=3, color='cyan'),
    name='Minkowski',
    text=stars['name']
))

# SSZ
fig.add_trace(go.Scatter3d(
    x=x * stars_ssz['stretch_factor'],
    y=y * stars_ssz['stretch_factor'],
    z=z * stars_ssz['stretch_factor'],
    mode='markers',
    marker=dict(
        size=5,
        color=stars_ssz['D_ssz'],
        colorscale='Plasma',
        showscale=True
    ),
    name='SSZ',
    text=stars['name']
))

fig.update_layout(
    title='SSZ Skymap Prototype',
    scene=dict(
        xaxis_title='X [pc]',
        yaxis_title='Y [pc]',
        zaxis_title='Z [pc]',
        bgcolor='black'
    ),
    paper_bgcolor='black',
    font=dict(color='white')
)

fig.show()
```

**Jetzt laufen lassen:**
```bash
python skymap_proto.py
# → Öffnet interaktive 3D-Karte im Browser!
```

---

## 🎮 Interactive3D-VERGLEICH

| Feature | Interactive3D | SSZ Skymap | Status |
|---------|-----------|------------|--------|
| **3D Navigation** | ✅ | 🎯 Target | Phase 1 |
| **Star Info** | ✅ | 🎯 Target | Phase 3 |
| **Zoom Levels** | ✅ | 🎯 Target | Phase 1 |
| **Search** | ✅ | 🎯 Target | Phase 3 |
| **Path Finding** | ✅ | 🎯 Target | Phase 5 |
| **Physics-Accurate** | ❌ | ✅ | Built-in! |
| **SSZ Effects** | ❌ | ✅ | Phase 2 |
| **Real Data** | ❌ | ✅ | GAIA/ESO |

**Unser Vorteil:** Real physics, real data, wissenschaftlich korrekt!

---

## 📖 REFERENZEN

### Inspiration:
- **Interactive3D** - UI/UX Design
- **Space Engine** - Realistic sky
- **Universe Sandbox** - Physics simulation
- **Celestia** - Scientific accuracy

### Tech Docs:
- Plotly 3D: https://plotly.com/python/3d-charts/
- Dash: https://dash.plotly.com/
- GAIA Coords: https://docs.astropy.org/

---

## ✅ NEXT STEPS

**Sofort (30 min):**
1. Prototype erstellen (`skymap_proto.py`)
2. Testen mit 500 Sternen
3. Interaktivität prüfen

**Heute (4h):**
- Phase 1 komplett implementieren
- 3D-Viewer fertig

**Diese Woche (16h):**
- MVP (Phase 1-3)
- Basic Interactive3D-Style App

---

**Bereit für den Prototype? Soll ich `skymap_proto.py` jetzt erstellen?** 🚀

---

© 2025 Carmen Wrede, Lino Casu  
**"From validated physics to interactive exploration"** ✨
