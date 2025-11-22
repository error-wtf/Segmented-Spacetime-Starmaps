# SSZ StarMaps - Setup Instructions

Quick reference for setting up and running the project.

## Windows PowerShell

### 1. Navigate to project folder
```powershell
cd E:\clone\Segmented-Spacetime-StarMaps
```

### 2. Create virtual environment
```powershell
python -m venv .venv
```

### 3. Activate virtual environment
```powershell
.\.venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Upgrade pip
```powershell
python -m pip install --upgrade pip
```

### 5. Install dependencies
```powershell
pip install -r requirements.txt
```

### 6. Run the demo
```powershell
python -m ssz_starmaps.demo_starmap
```

### 7. Run tests
```powershell
python tests/test_geometry.py
```

### 8. Test individual modules
```powershell
python -m ssz_starmaps.geometry
python -m ssz_starmaps.catalog
python -m ssz_starmaps.projection
```

---

## Linux / macOS

### 1-2. Navigate and create venv
```bash
cd /path/to/Segmented-Spacetime-StarMaps
python3 -m venv .venv
```

### 3. Activate venv
```bash
source .venv/bin/activate
```

### 4-8. Same as Windows
```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m ssz_starmaps.demo_starmap
python tests/test_geometry.py
```

---

## Expected Output

```
================================================================================
SSZ STARMAPS - Segmented Spacetime Star Map Demo
================================================================================

[1/5] Fetching star catalog...
  ✓ Loaded 42 stars

[2/5] Projecting to 2D plane (gnomonic)...
  ✓ Projected 42 positions

[3/5] Applying SSZ deformation (eps=0.15)...
  ✓ Deformed coordinates computed

[4/5] Computing orbit circumferences...
  Orbit Analysis (r = 1.0):
    Minkowski (circle):  C = 6.283185
    SSZ (ellipse):       C = 6.264822
    Deviation:           -0.292%

[5/5] Generating plot...
  ✓ Plot saved: ssz_starmap_demo.png

✓ Demo complete!
```

---

## Troubleshooting

**Q: "astroquery not found"**  
A: Make sure virtual environment is activated, then: `pip install astroquery`

**Q: "SIMBAD query failed"**  
A: Check internet connection. The demo will automatically fall back to mock data.

**Q: "ModuleNotFoundError: No module named 'ssz_starmaps'"**  
A: Make sure you're running from the project root and venv is activated.

**Q: matplotlib window doesn't show**  
A: The plot is saved as `ssz_starmap_demo.png` even if the window fails to open.

---

© 2025 Carmen Wrede, Lino Casu
