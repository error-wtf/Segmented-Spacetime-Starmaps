# SSZ Skymap - Quick Reference Card

**Fast lookup for all commands and features**

---

## ⚡ Quick Commands

### **Fastest Start:**
```bash
python skymap_advanced.py
```

### **Production Quality:**
```bash
python skymap_3d.py --distance 50 --max-stars 800 --theme space
```

### **Interactive Dashboard:**
```bash
pip install dash dash-bootstrap-components
python skymap_dashboard.py
# → http://127.0.0.1:8050/
```

---

## 🎮 Mouse Controls

```
Drag               → Rotate 3D view
Scroll             → Zoom in/out
Shift + Drag       → Pan camera
Double-click       → Reset view
Click (Dashboard)  → Select star
```

---

## 📁 Output Files

```
outputs_quick_start/
├── skymap_proto.html         (Quick demo)
├── skymap_3d.html            (Production)
├── skymap_advanced.html      (With effects)
└── test_final.html           (Latest test)
```

---

## 🎨 Themes

```bash
--theme space    # Black background (presentations)
--theme dark     # Navy background (general use)
--theme light    # White background (printing)
```

---

## ✨ Effects

```bash
--effects glow             # Size ∝ SSZ stretch
--effects connections      # 867 connection lines
--effects glow connections # Both effects
```

---

## 🎭 Glow Modes

```bash
--glow-mode stretch     # Based on stretch factor
--glow-mode dilation    # Based on time dilation
--glow-mode combined    # Both (most dramatic!)
```

---

## 📊 Common Configurations

### **Quick Demo:**
```bash
python skymap_advanced.py
```

### **High Resolution:**
```bash
python skymap_3d.py --distance 100 --max-stars 1500
```

### **Presentation:**
```bash
python skymap_advanced.py \
    --effects glow connections \
    --glow-mode combined \
    --theme space
```

### **Research:**
```bash
python skymap_dashboard.py
```

### **Custom Save:**
```bash
python skymap_3d.py --output my_map.html --max-stars 1000
```

---

## 🔧 All Options

### **skymap_3d.py:**
```
--distance FLOAT       Max distance [pc] (default: 50)
--max-stars INT        Number of stars (default: 1000)
--mode [dual|single]   View mode (default: dual)
--theme THEME          Color theme (default: dark)
--height INT           Plot height [px] (default: 800)
--output FILE          Save to file (optional)
--offline              Use mock data
```

### **skymap_advanced.py:**
```
--distance FLOAT       Max distance [pc] (default: 50)
--max-stars INT        Number of stars (default: 500)
--effects LIST         glow, connections, ruler
--glow-mode MODE       stretch, dilation, combined
--connections          Enable connections
--theme THEME          space, dark, light
--height INT           Plot height [px] (default: 900)
--output FILE          Save to file (optional)
```

---

## 📊 Performance Guide

```
Fast (2s):       --max-stars 400
Balanced (4s):   --max-stars 800
Detailed (8s):   --max-stars 1500
```

---

## 🔍 Data Ranges

```
Distance:    0-100 pc
Stars:       100-2000
Magnitude:   -2 to 15
Spectral:    O, B, A, F, G, K, M
```

---

## 🎯 Use Cases

```
Quick demo:        python skymap_advanced.py
Production:        python skymap_3d.py --max-stars 800
Presentation:      python skymap_advanced.py --theme space
Research:          python skymap_dashboard.py
Custom analysis:   python skymap_3d.py --output results.html
```

---

## 🐛 Troubleshooting

```
Issue: Browser doesn't open
Fix:   Open outputs_quick_start/skymap_advanced.html

Issue: No module 'dash'
Fix:   pip install dash dash-bootstrap-components

Issue: Slow rendering
Fix:   python skymap_3d.py --max-stars 500

Issue: Want offline
Fix:   python skymap_3d.py --offline
```

---

## 📚 Documentation

```
README_SKYMAP.md               Main guide
USAGE_GUIDE.md                 Detailed usage
PROJECT_SUMMARY.md             Project summary
STELLARIS_SKYMAP_COMPLETE.md   Full report
INSTALL_DASHBOARD.md           Dashboard setup
```

---

## ⚡ One-Liners

```bash
# Instant demo
python skymap_advanced.py

# 800 stars
python skymap_3d.py --max-stars 800

# Space theme
python skymap_3d.py --theme space

# All effects
python skymap_advanced.py --effects glow connections --glow-mode combined

# Dashboard
pip install dash dash-bootstrap-components && python skymap_dashboard.py
```

---

## 🎨 Visual Encoding

```
Color:  Time dilation (D_SSZ)
        Red/Orange  → Slower time
        Blue/Purple → Faster time

Size:   SSZ stretch factor
        Large  → Strong effect
        Small  → Weak effect

Lines:  Spatial connections
        Links stars < 5 pc apart
```

---

## 📈 Typical Performance

```
Stars:       400-800
Load:        2-5 seconds
Render:      1-2 seconds
Memory:      200-300 MB
File size:   2-4 MB
```

---

## ✅ Quick Checklist

```
☐ Python 3.8+ installed
☐ Required packages installed
☐ Run one of the three apps
☐ Browser opens automatically
☐ Explore with mouse controls
☐ Check outputs_quick_start/ for HTML files
```

---

## 🚀 Quick Start Workflow

```
1. cd E:\clone\Segmented-Spacetime-StarMaps
2. python skymap_advanced.py
3. Wait 3 seconds
4. Explore in browser!
```

---

**Print this for quick reference!** 📄

© 2025 Carmen Wrede & Lino Casu
