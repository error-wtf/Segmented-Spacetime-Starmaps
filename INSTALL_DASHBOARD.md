# Install SSZ Skymap Dashboard

**Quick install for Phase 3 Dashboard**

---

## Option 1: Install Dependencies

```bash
pip install dash dash-bootstrap-components
```

Or full requirements:
```bash
pip install -r requirements-dashboard.txt
```

---

## Option 2: Use Static Versions (No Dash needed)

**If you don't want to install Dash**, you can use:

```bash
# Phase 1: Basic 3D (works now!)
python skymap_3d.py

# Phase 2: Advanced with effects (works now!)
python skymap_advanced.py
```

These create **standalone HTML files** that work in any browser!

---

## Installation Steps

### Windows:
```powershell
# Install Dash
pip install dash dash-bootstrap-components

# Run dashboard
python skymap_dashboard.py

# Open browser to: http://127.0.0.1:8050/
```

### Linux/Mac:
```bash
# Install Dash
pip3 install dash dash-bootstrap-components

# Run dashboard
python3 skymap_dashboard.py

# Open browser to: http://127.0.0.1:8050/
```

---

## What You Have WITHOUT Dash

**Already working (no extra install):**
- ✅ `skymap_proto.py` - Quick prototype
- ✅ `skymap_3d.py` - Full 3D view
- ✅ `skymap_advanced.py` - With effects

**These create HTML files in `outputs_quick_start/`**

---

## What Dash Adds

**With Dash installed:**
- ✅ Interactive controls (sliders, buttons)
- ✅ Real-time updates (no page reload)
- ✅ Click on stars → see info
- ✅ Search functionality
- ✅ Live statistics
- ✅ Filter system

**Trade-off:**
- Without Dash: Static HTML (works everywhere, no install)
- With Dash: Interactive webapp (needs pip install)

---

## Recommended Approach

### For quick demo:
```bash
python skymap_advanced.py
# Opens in browser, no install needed!
```

### For full experience:
```bash
pip install dash dash-bootstrap-components
python skymap_dashboard.py
# Full Interactive3D-style dashboard!
```

---

## Troubleshooting

### ModuleNotFoundError: dash
```bash
pip install dash
```

### ModuleNotFoundError: dash_bootstrap_components
```bash
pip install dash-bootstrap-components
```

### Port 8050 already in use
```bash
# Kill existing process or use different port
# Edit skymap_dashboard.py line: app.run_server(debug=True, port=8051)
```

---

© 2025 Carmen Wrede, Lino Casu
