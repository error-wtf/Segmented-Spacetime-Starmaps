# Interactive 3D Skymap - User Guide

**Application:** Full Interactive3D-Style SSZ Galaxy Viewer  
**Version:** 1.0  
**Date:** 2025-11-22

---

## 🚀 QUICK START

### **Start the Application:**

```bash
cd Interactive3D_ssz_viewer
python interactive_skymap_app.py
```

### **Access:**

```
Open Browser: http://127.0.0.1:8050
```

### **Stop:**

```
Press Ctrl+C in terminal
```

---

## 🎮 MENU SYSTEM

### **5 Main Modes:**

```
🌌 GALAXY VIEW    - 3D visualization of 1000 stars
🌟 SYSTEM VIEW    - Detailed planetary systems
📊 DATA EXPORT    - Download SSZ calculations
⚙️ SETTINGS       - Adjust parameters
❓ HELP           - Documentation & controls
```

---

## 🌌 MODE 1: GALAXY VIEW

### **Features:**

- **3D Interactive Map:** 1000 stars in galactic distribution
- **Real SSZ Physics:** Segment density calculated for each star
- **Spectral Coloring:** O-type (blue) to M-type (red)
- **Size by Magnitude:** Brighter stars appear larger
- **Hover Info:** Complete star data on mouseover

### **Controls:**

```
Rotate:  Click and drag
Zoom:    Scroll wheel
Pan:     Right-click and drag
Reset:   Double-click
```

### **Star Information (Hover):**

```
- Name
- Spectral Type
- Mass (M_sun)
- Distance (pc)
- Xi(r) - Segment Density
- Click to view system
```

### **Color Coding:**

```
O-type: Blue      (#9bb0ff) - Massive hot stars
B-type: Blue-white (#aabfff)
A-type: White     (#cad7ff)
F-type: Yellow-white (#f8f7ff)
G-type: Yellow    (#fff4ea) - Sun-like
K-type: Orange    (#ffd2a1)
M-type: Red       (#ffcc6f) - Red dwarfs
```

---

## 🌟 MODE 2: SYSTEM VIEW

### **Features:**

- **Planet Generation:** Realistic based on star type
- **4-Panel Display:**
  1. System Overview (orbital ellipses)
  2. SSZ Field Visualization (contours)
  3. Planet Properties (bar chart)
  4. Orbital Comparison (Classical vs SSZ)

### **Star Selection:**

```
Method 1: Click star in Galaxy View
Method 2: Select from "Top 10" list
```

### **System Information:**

```
Star Properties:
  - Type, Mass, Distance
  
System Info:
  - Number of planets
  - Habitable zone boundaries
  - SSZ segment density
  
Planet Details:
  - Type (Rocky, Gas Giant, etc.)
  - Mass (Earth masses)
  - Orbital distance (AU)
  - Period (years)
  - SSZ corrections
```

### **Habitable Zone:**

- **Green zone** on orbital plot
- Calculated from stellar luminosity
- Planets marked if in HZ

---

## 📊 MODE 3: DATA EXPORT

### **3 Export Formats:**

#### **1. CSV (Excel-Compatible)**

```
File: skymap_export.csv
Columns: 44
Format: Scientific notation
Use: Excel, pandas, R
```

#### **2. JSON (Machine-Readable)**

```
File: skymap_export.json
Structure: Hierarchical with metadata
Use: APIs, web apps, programming
```

#### **3. Markdown Report**

```
File: skymap_export_report.md
Format: Human-readable
Use: Documentation, papers
```

### **Exported Parameters:**

```
Basic Properties (8):
  - Mass, Distance (m, km, AU, ly, pc)

Schwarzschild (8):
  - r_s, x, photon sphere, ISCO

SSZ Parameters (6):
  - Xi, D_SSZ, D_GR, stretch factor

Velocities (10):
  - Orbital, escape (classical & SSZ)

Time & Redshift (3):
  - tau/t, z_GR, z_SSZ

Orbital Periods (4):
  - T_orbital (classical & SSZ)

Gravity (3):
  - g, potential

Metadata (2):
  - Timestamp, phi
```

### **How to Export:**

1. Click "DATA EXPORT" in menu
2. Choose format (CSV, JSON, or Markdown)
3. Click download button
4. File saved to `ssz_exports/` folder

---

## ⚙️ MODE 4: SETTINGS

### **Adjustable Parameters:**

```
Number of Stars:
  Range: 100 - 5000
  Default: 1000
  Effect: More stars = slower rendering

Max Distance:
  Range: 1000 - 10000 pc
  Default: 5000 pc
  Effect: Larger view radius
```

### **Apply Changes:**

- Adjustments apply on next data reload
- Restart app to see changes

---

## ❓ MODE 5: HELP

### **Documentation Sections:**

- Navigation overview
- Control instructions
- SSZ physics formulas
- Technical specifications

### **Key Formulas:**

```
Segment Density:
  Xi(r) = 1 - exp(-phi * r/r_s)

Time Dilation:
  D_SSZ(r) = 1/(1 + Xi)

Golden Ratio:
  phi = 1.6180339887...
```

---

## 🎨 USER INTERFACE

### **Color Scheme (Interactive3D-Inspired):**

```
Background:  #0a0e1a (deep space blue)
Panels:      #1a2332 (dark blue-gray)
Primary:     #3498db (bright blue)
Secondary:   #2c3e50 (dark gray)
Accent:      #e74c3c (red)
Text:        #ecf0f1 (light gray)
Borders:     #34495e (medium gray)
```

### **Layout:**

```
+------------------------------------------+
|           SSZ GALAXY VIEWER              |
+------------------------------------------+
| 🌌 | 🌟 | 📊 | ⚙️ | ❓  | (Menu Buttons)
+------------------------------------------+
| Status: Ready      |  Stars: 1000       |
+------------------------------------------+
|                                          |
|         MAIN CONTENT AREA                |
|                                          |
|   (Changes based on selected mode)       |
|                                          |
+------------------------------------------+
```

---

## 🔧 TECHNICAL DETAILS

### **Requirements:**

```
Python 3.10+
dash
plotly
numpy
pandas
```

### **Install:**

```bash
pip install dash plotly numpy pandas
```

### **Data Flow:**

```
1. Load galaxy data (1000 stars)
2. Compute SSZ parameters
3. Cache to JSON
4. Render based on mode
5. Update on user interaction
```

### **Performance:**

```
Initial Load:  2-3 seconds
Mode Switch:   <1 second
3D Rendering:  Smooth (60 FPS)
Data Export:   <1 second
```

---

## 🎯 USE CASES

### **1. Scientific Exploration:**

- Study galactic structure
- Compare SSZ vs GR predictions
- Analyze stellar distributions
- Export data for research

### **2. Education:**

- Interactive astronomy teaching
- Visualize SSZ physics
- Explore planetary systems
- Understand spacetime geometry

### **3. Data Analysis:**

- Download complete datasets
- Run statistical analyses
- Generate reports
- Create visualizations

### **4. Presentations:**

- Live demonstrations
- Interactive talks
- Conference displays
- Educational materials

---

## 🐛 TROUBLESHOOTING

### **App won't start:**

```
Check: Port 8050 available?
Solution: Close other apps using port
Or: Change port in code (app.run_server(port=8051))
```

### **Slow performance:**

```
Problem: Too many stars
Solution: Reduce in Settings (e.g., 500 stars)
```

### **Data not loading:**

```
Check: galaxy_cache.json exists?
Solution: Delete cache, restart app
```

### **Export fails:**

```
Check: ssz_exports/ folder exists?
Solution: Create manually or restart app
```

---

## 📚 KEYBOARD SHORTCUTS

### **Navigation:**

```
1 - Galaxy View
2 - System View
3 - Data Export
4 - Settings
5 - Help
```

### **3D Controls:**

```
R - Reset view
F - Fit to screen
H - Toggle help
```

*(Note: Keyboard shortcuts to be implemented in future version)*

---

## 🚀 ADVANCED FEATURES

### **Coming in Future Versions:**

- [ ] Multi-star selection
- [ ] Route planning between stars
- [ ] Time evolution (animation)
- [ ] Custom filters
- [ ] Save/load sessions
- [ ] Screenshot export
- [ ] VR support
- [ ] Real GAIA data integration

---

## 📖 EXAMPLE WORKFLOWS

### **Workflow 1: Explore & Export**

1. Start app
2. Browse Galaxy View
3. Click interesting star
4. View system details
5. Export all data
6. Analyze in Excel

### **Workflow 2: Teaching Session**

1. Start app
2. Show Galaxy View (3D structure)
3. Explain spectral types (colors)
4. Select Sun-like star
5. Show habitable zone
6. Discuss SSZ effects

### **Workflow 3: Research**

1. Export all data (JSON)
2. Load in Python
3. Filter by criteria
4. Statistical analysis
5. Generate plots
6. Write paper

---

## 🎓 LEARNING RESOURCES

### **SSZ Physics:**

- Segment Density: How spacetime "segments"
- Time Dilation: How time flows differently
- Golden Ratio: Why φ appears in nature

### **Astronomical Concepts:**

- Spectral Classification: O-B-A-F-G-K-M
- Habitable Zones: Where life could exist
- Orbital Mechanics: How planets move

### **Data Science:**

- 3D Visualization: plotly techniques
- Interactive Dashboards: Dash framework
- Data Export: Multiple formats

---

## 📞 SUPPORT

### **Questions?**

- Check Help mode in app
- Read Interactive3D_ROADMAP.md
- View example code

### **Bug Reports:**

- Note the mode you were in
- Describe what happened
- Check terminal output

---

## 📄 LICENSE

```
© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
```

---

**Interactive Skymap Version:** 1.0  
**Last Updated:** 2025-11-22  
**Status:** Production-Ready

**🌟 Enjoy exploring the SSZ Galaxy! 🌟**
