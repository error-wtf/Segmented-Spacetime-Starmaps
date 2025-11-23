# 🌌 **SSZ EXPLORER - DARK EDITION (COMPLETE)**

**ALLE Features + PAPER-RESTORED Dark Theme!**

© 2025 Carmen Wrede, Lino Casu, Bingsi

---

## ✅ **VOLLSTÄNDIGE FEATURE-LISTE**

Die **gradio_app_complete.py** ist jetzt die **Dark Edition** mit ALLEN Funktionen:

---

### **🏠 TAB 1: Start & Data Fetch**

**Database Loading:**
- ✅ Automatisches Laden von 500k GAIA DR3 Sternen
- ✅ Unterstützung für enriched database
- ✅ Background-Enrichment während App läuft

**Data Fetch Suite:**
- ✅ **Fetch Mode Selection:**
  - All Objects (500k)
  - Specific Region
- ✅ **Region Presets:**
  - Galactic Center (Sgr A*)
  - Orion Nebula (M42)
  - Cygnus X
  - G79.29+0.46 (UCHII)
  - Carina Nebula
  - Custom Coordinates
- ✅ **External Data Sources:**
  - AKARI IRC (Infrared temperatures)
  - ESO GRAVITY (Spectroscopy)
  - 2MASS/WISE (Photometric data)
  - GAIA DR3 (Radial velocities)
- ✅ **Real-time Status Display**
- ✅ **Enrichment Statistics**
- ✅ **Save Enriched Database**

---

### **🗺️ TAB 2: 2D Sky Maps (DARK THEME!)**

**Features:**
- ✅ **Interactive 2D Sky Map**
  - 500k stars (sampled to 10k for performance)
  - Click on stars for details
  - DARK BACKGROUND (#0a0a1f)
  
- ✅ **Object Selection:**
  - Click on star → auto-select
  - Selected star details displayed
  
- ✅ **Query System:**
  - Search by Name (Fuzzy matching!)
  - Search by RA/Dec coordinates
  - Radius search
  
- ✅ **Famous Objects Dropdown:**
  - Betelgeuse, Rigel, Sirius, Aldebaran
  - Deneb, Vega, Altair, Antares
  - Polaris, Proxima Centauri, Alpha Centauri
  - Barnard's Star
  
- ✅ **CSV Export:**
  - Export query results
  - Download as CSV file

---

### **🌐 TAB 3: 3D Sky Maps (DARK THEME!)**

**Features:**
- ✅ **Full 3D Visualization**
  - WebGL rendering
  - Rotate, zoom, pan
  - DARK BACKGROUND
  
- ✅ **Centered on Selected Object:**
  - 3D view centered on chosen star
  - Distance/angle controls
  - Highlight selected object
  
- ✅ **Performance Optimized:**
  - 5k stars for full map
  - 1k stars for centered view

---

### **🎭 TAB 4: Constellation Maps (DARK THEME!)**

**Features:**
- ✅ **Region-specific 3D Maps**
  - Custom RA/Dec coordinates
  - Field of View control
  - Up to 2000 stars per region
  
- ✅ **Galactic Center Preset**
- ✅ **Orion Preset**
- ✅ **Pleiades Preset**
- ✅ **Custom Coordinates**

---

### **🔬 TAB 5: SSZ Physics (DARK THEME!)**

**All plots with PAPER-RESTORED Dark Theme:**

**4 Main Physics Plots:**

1. **g₁/g₂ Domain Structure**
   - 4-panel subplot
   - Domain transition
   - Piecewise fit
   - Temperature gradient
   - **Dark Theme:** #0a0a1f background, white text

2. **Time Dilation Comparison**
   - SSZ vs GR
   - Universal crossover point
   - Log scale
   - **Dark Theme:** Applied

3. **Radial Stretch**
   - Metric components
   - SSZ effects
   - **Dark Theme:** Applied

4. **Combined Analysis**
   - 2x2 subplot
   - All metrics together
   - **Dark Theme:** Applied

**Object Selection for Physics:**
- ✅ Use selected object from Sky Maps
- ✅ Default: Sgr A* (4.3×10⁶ M☉)
- ✅ Shows object mass in plots

---

### **🖼️ TAB 6: PAPER-RESTORED Gallery**

**Features:**
- ✅ **124 Curated Plots** (from 570 total)
- ✅ **6 Categories:**
  - Paper Figures
  - Real Data
  - Sharp Break Analysis
  - G79 Cygnus
  - Nested Metrics
  - Model Comparisons
  
- ✅ **Category Dropdown**
- ✅ **Plot Dropdown**
- ✅ **Auto-load on selection**
- ✅ **Full file path display**

---

## 🎨 **DARK THEME IMPLEMENTATION**

### **Colors (PAPER-RESTORED Style):**

```python
DARK_BG = '#0a0a1f'        # Plot background (dunkelblau)
DARK_PAPER = '#000010'     # Paper background (fast schwarz)
DARK_GRID = 'rgba(100,100,150,0.3)'  # Grid lines
DARK_TEXT = 'white'        # Text color

COLOR_GR = '#3498db'       # Blue for GR
COLOR_SSZ = '#e74c3c'      # Red for SSZ
COLOR_ACCENT = '#2ecc71'   # Green for highlights
```

### **Applied to:**
- ✅ All 2D Sky Maps
- ✅ All 3D Sky Maps
- ✅ All Constellation Maps
- ✅ All Physics Plots (g₁/g₂, Time Dilation, Radial Stretch, Combined)
- ✅ Error messages
- ✅ Empty state displays

### **Helper Function:**
```python
def apply_dark_theme(fig, title=""):
    """Apply PAPER-RESTORED Dark Theme to any Plotly figure"""
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=DARK_TEXT)),
        plot_bgcolor=DARK_BG,
        paper_bgcolor=DARK_PAPER,
        font=dict(color=DARK_TEXT, size=11),
    )
    # Update all axes
    for i in range(1, 10):
        for axis_type in ['xaxis', 'yaxis']:
            axis_name = f'{axis_type}{i if i > 1 else ""}'
            if hasattr(fig.layout, axis_name):
                getattr(fig.layout, axis_name).update(
                    gridcolor=DARK_GRID, 
                    zerolinecolor=DARK_GRID
                )
    return fig
```

### **Wrappers:**
```python
create_sky_map_dark()      # 2D with dark theme
create_3d_sky_map_dark()   # 3D with dark theme
```

---

## 🚀 **USAGE**

### **Start the App:**
```bash
cd E:\clone\Segmented-Spacetime-StarMaps\ssz_explorer
python gradio_app_complete.py
```

**Port:** http://localhost:7860

---

## 📊 **WORKFLOW EXAMPLE**

### **1. Search for Object:**
```
Tab: 2D Sky Maps
→ Famous Objects: "Betelgeuse"
→ Click "Search"
→ Object auto-selected
```

### **2. View in 3D:**
```
Tab: 3D Sky Maps
→ Map shows Betelgeuse highlighted
→ Rotate/Zoom in 3D
```

### **3. Physics Analysis:**
```
Tab: SSZ Physics
→ Auto-uses Betelgeuse mass
→ Generate physics plots
→ All in Dark Theme!
```

### **4. Region Analysis:**
```
Tab: Constellation Maps
→ Galactic Center preset
→ Generate region map
→ Dark Theme applied
```

### **5. Compare with Papers:**
```
Tab: PAPER-RESTORED Gallery
→ Category: G79 Cygnus
→ View original plots
→ Compare with live data
```

---

## 🔧 **TECHNICAL DETAILS**

### **Database:**
- **Format:** CSV (GAIA DR3)
- **Size:** 500k stars (base), up to 50k enriched
- **Columns:** ra, dec, parallax, distance_ly, mag, temperature, etc.

### **Performance:**
- **2D Maps:** 10k stars sampled from 500k
- **3D Maps:** 5k stars for full view, 1k for centered
- **Constellation:** Up to 2k stars per region
- **Physics Plots:** Real-time calculation

### **External APIs:**
- ✅ AKARI IRC (VizieR)
- ✅ ESO Archive
- ✅ 2MASS (VizieR)
- ✅ NED (NASA/IPAC)

---

## 📝 **ALLE TABS IM DETAIL**

| Tab | Features | Dark Theme | Status |
|-----|----------|------------|--------|
| **Start & Fetch** | Data enrichment, stats, save | N/A | ✅ |
| **2D Sky Maps** | 500k stars, click select, search | ✅ YES | ✅ |
| **3D Sky Maps** | Full 3D, centered view | ✅ YES | ✅ |
| **Constellation** | Region maps, presets | ✅ YES | ✅ |
| **SSZ Physics** | 4 physics plots | ✅ YES | ✅ |
| **Gallery** | 124 curated PAPER plots | N/A (images) | ✅ |

---

## ✅ **UNTERSCHIED ZU VORHER**

### **Vorher (ssz_explorer_dark.py):**
- ❌ Nur 7 Live Physics Plots
- ❌ Nur 124 statische Plots
- ❌ KEINE Sky Maps
- ❌ KEINE Object Selection
- ❌ KEINE Constellation Maps
- ❌ KEINE Data Fetching

### **Jetzt (gradio_app_complete.py - DARK EDITION):**
- ✅ **ALLE** Original Features
- ✅ **+ Dark Theme** überall
- ✅ 2D/3D Sky Maps (Dark!)
- ✅ Object Selection & Search
- ✅ Constellation Maps (Dark!)
- ✅ Data Fetching Suite
- ✅ 4 Physics Plots (Dark!)
- ✅ 124 Gallery Plots
- ✅ CSV Export
- ✅ Famous Objects Dropdown

---

## 🎯 **ZUSAMMENFASSUNG**

### **Was ist drin:**
✅ **500k GAIA DR3 Stars** geladen  
✅ **2D Sky Maps** mit Dark Theme  
✅ **3D Sky Maps** mit Dark Theme  
✅ **Constellation Maps** mit Dark Theme  
✅ **Object Search** (Name, Coords, Radius)  
✅ **Object Selection** (Click oder Famous Objects)  
✅ **4 Physics Plots** (g₁/g₂, Time Dilation, Radial Stretch, Combined)  
✅ **124 PAPER-RESTORED Plots** (Gallery)  
✅ **Data Fetching** (AKARI, ESO, 2MASS, NED)  
✅ **CSV Export**  
✅ **Dark Theme** ÜBERALL (PAPER-RESTORED Style)  

### **Was ist NICHT drin:**
❌ Nichts! ALLES ist integriert!

---

**KEINE HALBEN SACHEN - ALLES MIT DARK THEME!** 🌌🚀

---

© 2025 Carmen Wrede, Lino Casu, Bingsi  
Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
