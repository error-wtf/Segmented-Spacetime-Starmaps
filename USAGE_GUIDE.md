# SSZ Skymap - Usage Guide

**Complete guide for using all three applications**

---

## 🎯 Choose Your Application

### **Need:** Quick Demo
**Use:** `skymap_advanced.py`
```bash
python skymap_advanced.py
```
**→ Opens in 3 seconds!** ✨

---

### **Need:** Production Quality
**Use:** `skymap_3d.py`
```bash
python skymap_3d.py --distance 50 --max-stars 800 --theme space
```
**→ 800 real GAIA stars!** 🌌

---

### **Need:** Full Control
**Use:** `skymap_dashboard.py`
```bash
pip install dash dash-bootstrap-components
python skymap_dashboard.py
# → http://127.0.0.1:8050/
```
**→ Interactive dashboard!** 🎛️

---

## 📖 Complete Command Reference

### **skymap_3d.py**

```bash
python skymap_3d.py [OPTIONS]
```

**All Options:**
```
--distance FLOAT       Maximum distance [pc] (default: 50)
--max-stars INT        Number of stars (default: 1000)
--mode [dual|single]   View mode (default: dual)
--theme [dark|space|light]  Color theme (default: dark)
--height INT           Plot height [px] (default: 800)
--output FILE          Save HTML file (optional)
--offline              Use mock data (no GAIA fetch)
```

**Examples:**
```bash
# Basic
python skymap_3d.py

# High resolution
python skymap_3d.py --distance 100 --max-stars 1500

# Space theme
python skymap_3d.py --theme space --height 1000

# Save to file
python skymap_3d.py --output results/my_skymap.html

# Offline (mock data)
python skymap_3d.py --offline --max-stars 500
```

---

### **skymap_advanced.py**

```bash
python skymap_advanced.py [OPTIONS]
```

**All Options:**
```
--distance FLOAT       Maximum distance [pc] (default: 50)
--max-stars INT        Number of stars (default: 500)
--effects LIST         Visual effects (default: glow)
                      Options: glow, connections, ruler
--glow-mode MODE       Glow calculation mode
                      Options: stretch, dilation, combined
--connections          Enable connection lines
--theme THEME          Color theme
                      Options: space, dark, light
--height INT           Plot height [px] (default: 900)
--output FILE          Save HTML file (optional)
```

**Examples:**
```bash
# Quick demo
python skymap_advanced.py

# All effects
python skymap_advanced.py --effects glow connections

# Combined glow mode
python skymap_advanced.py --glow-mode combined

# Space theme + connections
python skymap_advanced.py \
    --theme space \
    --effects glow connections \
    --max-stars 600

# High resolution
python skymap_advanced.py \
    --distance 80 \
    --max-stars 1000 \
    --height 1200
```

---

### **skymap_dashboard.py**

```bash
python skymap_dashboard.py
```

**No command-line options - all control via web interface!**

**Access:** http://127.0.0.1:8050/

**Dashboard Controls:**
- **Distance Slider:** 0-100 pc
- **Stars Slider:** 100-2000
- **Magnitude Slider:** -2 to 15
- **Glow Mode:** stretch / dilation / combined
- **Color Scale:** Plasma / Viridis / Inferno / Magma / Hot / Cool
- **Effects:** [✓] Connections, [✓] Glow, [✓] Grid, [✓] SSZ
- **Theme:** Space / Dark / Light
- **Search:** Type star name
- **Filters:** Spectral type (O/B/A/F/G/K/M)

---

## 🎨 Visual Effect Modes

### **Glow Modes:**

**1. Stretch Mode**
```bash
--glow-mode stretch
```
- Size ∝ (stretch_factor - 1)
- Shows radial expansion
- Good for seeing SSZ extent

**2. Dilation Mode**
```bash
--glow-mode dilation
```
- Size ∝ (1 - D_SSZ)
- Shows time slowdown
- Good for temporal effects

**3. Combined Mode**
```bash
--glow-mode combined
```
- Both effects together
- Most dramatic visual
- Best for presentations

---

## 🎭 Theme Comparison

### **Space Theme:**
```
Background: Pure black (#000000)
Stars: Bright colors
Grid: Dark grey
Best for: Presentations, screenshots
```

### **Dark Theme:**
```
Background: Navy (#0a0a1e)
Stars: Normal brightness
Grid: Blue-grey
Best for: General use, comfortable viewing
```

### **Light Theme:**
```
Background: White (#ffffff)
Stars: Dark colors
Grid: Light grey
Best for: Printing, daytime, papers
```

---

## 📊 Output Files

### **Automatic Saving:**
All apps save to: `outputs_quick_start/`

```
outputs_quick_start/
├── skymap_proto.html
├── skymap_3d.html
└── skymap_advanced.html
```

### **Custom Saving:**
```bash
python skymap_3d.py --output my_results/stars_2025.html
```

### **Opening Files:**
```bash
# Windows
start outputs_quick_start\skymap_3d.html

# Linux/Mac
open outputs_quick_start/skymap_3d.html
```

---

## 🔍 Understanding the Visualization

### **Color Scale (Plasma):**
```
Purple/Blue:  D_SSZ = 1.0   (no time dilation)
Green:        D_SSZ = 0.75  (mild dilation)
Yellow:       D_SSZ = 0.5   (moderate)
Orange/Red:   D_SSZ = 0.25  (strong dilation)
```

### **Star Size:**
```
Small (4px):   stretch = 1.0x  (minimal SSZ)
Medium (6px):  stretch = 1.5x  (moderate SSZ)
Large (10px):  stretch = 2.0x  (strong SSZ)
Huge (15px):   stretch = 3.0x  (extreme SSZ)
```

### **Connection Lines:**
```
Thin grey lines connect stars within 5 pc
Show spatial relationships
Form natural web structure
867 connections for 400 stars (typical)
```

---

## 🎯 Use Case Workflows

### **Quick Presentation:**
```bash
1. python skymap_advanced.py --theme space
2. Wait 3 seconds
3. Present! (already in browser)
```

### **Research Exploration:**
```bash
1. pip install dash dash-bootstrap-components
2. python skymap_dashboard.py
3. Open http://127.0.0.1:8050/
4. Adjust sliders, click stars, search
```

### **High-Quality Export:**
```bash
1. python skymap_3d.py \
     --distance 100 \
     --max-stars 1500 \
     --theme space \
     --height 1200 \
     --output paper_figure.html
     
2. Open in browser
3. Screenshot (Ctrl+Shift+S)
4. Use in paper/presentation
```

### **Batch Analysis:**
```python
# Custom script
for distance in [25, 50, 75, 100]:
    os.system(f"python skymap_3d.py \
                --distance {distance} \
                --output results/skymap_{distance}pc.html")
```

---

## 💡 Pro Tips

### **Performance:**
```bash
# Fast rendering (< 2 seconds)
python skymap_3d.py --max-stars 400

# Balanced (3-5 seconds)
python skymap_3d.py --max-stars 800

# High detail (5-8 seconds)
python skymap_3d.py --max-stars 1500
```

### **Visual Quality:**
```bash
# Maximum visual impact
python skymap_advanced.py \
    --effects glow connections \
    --glow-mode combined \
    --theme space \
    --height 1200
```

### **Scientific Accuracy:**
```bash
# No visual effects, pure data
python skymap_3d.py \
    --mode single \
    --theme light \
    --offline
```

---

## 🐛 Common Issues

### **Issue:** Browser doesn't open
**Solution:** Manually open `outputs_quick_start/skymap_advanced.html`

### **Issue:** "No module named 'dash'"
**Solution:** 
```bash
pip install dash dash-bootstrap-components
```

### **Issue:** Slow rendering
**Solution:** Reduce stars:
```bash
python skymap_3d.py --max-stars 500
```

### **Issue:** Want offline mode
**Solution:**
```bash
python skymap_3d.py --offline
```

### **Issue:** Port 8050 in use (Dashboard)
**Solution:** Edit `skymap_dashboard.py` line 436:
```python
app.run_server(debug=True, port=8051)  # Use different port
```

---

## 📈 Typical Performance

```
Configuration: 800 stars, dual-view, space theme

Load Time:     2.5 seconds
Transform:     0.8 seconds
Render:        1.2 seconds
Total:         4.5 seconds

File Size:     3.2 MB
Memory:        250 MB
Browser:       Chrome/Firefox/Edge (all work)
```

---

## 🎓 Learning Path

### **Beginner:**
1. Start with: `python skymap_advanced.py`
2. Explore in browser (rotate, zoom)
3. Try different themes

### **Intermediate:**
2. Use: `python skymap_3d.py` with options
3. Experiment with `--distance` and `--max-stars`
4. Compare dual-view (Minkowski vs SSZ)

### **Advanced:**
3. Install dashboard: `pip install dash dash-bootstrap-components`
4. Run: `python skymap_dashboard.py`
5. Use all controls, search, filters

### **Expert:**
4. Write custom Python scripts using modules
5. Integrate with own data sources
6. Extend with new features

---

## 📚 Next Steps

**After Quick Start:**
1. ✅ Read `README_SKYMAP.md` (detailed features)
2. ✅ Check `Interactive3D_SKYMAP_COMPLETE.md` (full project)
3. ✅ Explore code in `skymap/` directory
4. ✅ Try dashboard if interested

**For Development:**
1. ✅ Study `skymap/core/renderer.py`
2. ✅ Check `skymap/effects/` modules
3. ✅ Extend with custom features

---

## ✨ Summary

**Three Apps, Three Use Cases:**

```
skymap_advanced.py   → Quick demos (3 sec)
skymap_3d.py         → Production (5 sec, 800 stars)
skymap_dashboard.py  → Research (interactive, real-time)
```

**Choose based on your needs!** 🚀

---

© 2025 Carmen Wrede & Lino Casu
