# 📦 INSTALLATION GUIDE

**SSZ Interactive3D Viewer** - Setup Instructions  
**Date:** 2025-11-22

---

## 🚀 QUICK START

### **Option 1: Google Colab (Easiest - No Installation!)**
```
Click: "Open in Colab" badge in README
Everything installs automatically!
```

### **Option 2: Local Installation (Full Features)**

#### **Step 1: Clone Repository**
```bash
git clone https://github.com/error-wtf/Segmented-Spacetime-Starmaps.git
cd Segmented-Spacetime-Starmaps/Interactive3D_ssz_viewer
```

#### **Step 2: Install Dependencies**
```bash
# Install all dependencies (recommended)
pip install -r requirements.txt

# This installs:
# - dash, plotly, numpy, pandas (core)
# - astroquery, astropy (real GAIA data)
# - gradio (web UI)
# - psutil (performance monitoring)
```

#### **Step 3: Run Application**

**Option A: Dash App (7 Modes)**
```bash
python interactive_skymap_app.py
# Opens: http://127.0.0.1:8050
```

**Option B: Gradio App (Simple UI)**
```bash
python gradio_app.py
# Opens: http://127.0.0.1:7860
```

---

## 📦 DEPENDENCY BREAKDOWN

### **Required (Core Functionality):**
```bash
pip install dash>=2.14.0
pip install plotly>=5.17.0
pip install numpy>=1.24.0
pip install pandas>=2.0.0
```

**What you get:**
- ✅ Interactive 3D skymap
- ✅ 7 visualization modes
- ✅ SSZ vs GR comparison
- ✅ Synthetic data (1M stars)
- ✅ Data export

---

### **Recommended (Real Data):**
```bash
pip install astroquery>=0.4.6
pip install astropy>=6.0.0
```

**What you get:**
- ✅ Real GAIA DR3 data (1.8B stars!)
- ✅ Astronomical catalogs
- ✅ Proper coordinates
- ✅ Real masses & distances
- ✅ Validated results

**Without this:** App falls back to synthetic data automatically.

---

### **Optional (Enhanced UI):**
```bash
pip install gradio>=4.0.0
```

**What you get:**
- ✅ Gradio web interface
- ✅ Simpler UI
- ✅ Better for beginners
- ✅ Hugging Face compatible
- ✅ Colab optimized

**Without this:** Dash app still works perfectly!

---

### **Optional (Development):**
```bash
pip install pytest>=7.4.0
pip install black>=23.0.0
pip install flake8>=6.1.0
pip install psutil>=5.9.0
```

**What you get:**
- ✅ Run tests
- ✅ Code formatting
- ✅ Linting
- ✅ Performance monitoring

---

## 🐍 PYTHON VERSION

**Minimum:** Python 3.10  
**Recommended:** Python 3.11+

**Check your version:**
```bash
python --version
```

---

## 🖥️ SYSTEM REQUIREMENTS

### **Minimum:**
```
CPU: 2 cores
RAM: 4 GB
Storage: 1 GB
OS: Windows/Mac/Linux
```

### **Recommended:**
```
CPU: 4+ cores
RAM: 8+ GB
Storage: 10 GB (for large datasets)
GPU: Optional (faster rendering)
OS: Any modern OS
```

---

## 🔧 INSTALLATION METHODS

### **Method 1: All-in-One**
```bash
pip install -r requirements.txt
```
✅ Installs everything  
✅ Ready to go  
✅ Easiest

---

### **Method 2: Minimal Install**
```bash
pip install dash plotly numpy pandas
```
✅ Core only  
✅ Smaller footprint  
✅ Synthetic data works  
⚠️ No real GAIA data

---

### **Method 3: Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv ssz_env

# Activate (Windows)
ssz_env\Scripts\activate

# Activate (Mac/Linux)
source ssz_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run app
python interactive_skymap_app.py
```

✅ Isolated environment  
✅ No conflicts  
✅ Clean  
✅ Professional

---

## 🧪 VERIFY INSTALLATION

### **Test 1: Import Check**
```bash
python -c "import dash, plotly, numpy, pandas; print('Core OK!')"
```

### **Test 2: GAIA Connection**
```bash
python test_gaia_connection.py
```

Expected output:
```
[OK] GAIA CONNECTION TEST COMPLETE
```

### **Test 3: Run App**
```bash
python interactive_skymap_app.py
```

Expected: Browser opens with app.

---

## ❌ TROUBLESHOOTING

### **Problem: "No module named 'dash'"**
```bash
Solution:
pip install dash
```

### **Problem: "No module named 'gradio'"**
```bash
Solution (if you want Gradio):
pip install gradio

Or: Skip Gradio and use Dash app
```

### **Problem: "GAIA query failed"**
```bash
Possible causes:
1. No internet connection
2. astroquery not installed
3. GAIA servers down

Solution:
- Check internet
- pip install astroquery astropy
- App will fallback to synthetic data
```

### **Problem: Port already in use**
```bash
Error: "Address already in use: 8050"

Solution 1: Close other instances
Solution 2: Change port in code:
  app.run_server(port=8051)
```

### **Problem: Slow performance**
```bash
Solution:
1. Use smaller data level ('preview' not 'complete')
2. Enable cache (automatic)
3. Close other applications
4. Use GPU if available
```

---

## 🌐 CLOUD PLATFORMS

### **Google Colab:**
```python
# No installation needed!
# Click "Open in Colab" badge
# Run cells
```

### **Hugging Face Spaces:**
```bash
# Automatic installation
# Just upload code + requirements.txt
# Space handles rest
```

### **Local Server:**
```bash
# Run on network
python interactive_skymap_app.py --host 0.0.0.0
# Access from any device: http://your-ip:8050
```

---

## 📱 MOBILE ACCESS

### **From Phone/Tablet:**
```
1. Run app on computer
2. Note IP address (ipconfig/ifconfig)
3. Open browser on phone
4. Go to: http://computer-ip:8050
```

### **Future: Native Mobile Apps**
```
Coming in Phase 12:
- iOS app
- Android app
- React Native version
```

---

## 🎓 FIRST TIME SETUP CHECKLIST

```
□ Python 3.10+ installed
□ Git installed (optional)
□ Repository cloned
□ Virtual environment created
□ Requirements installed
□ GAIA test passed
□ App runs successfully
□ Browser opens
□ Data loads
□ Visualizations work
□ Can export data
```

---

## 🆘 GETTING HELP

### **If stuck:**

1. **Check documentation:**
   - README.md
   - QUICK_REFERENCE.md
   - This guide

2. **Run tests:**
   ```bash
   python test_gaia_connection.py
   python error_handling_test.py
   ```

3. **Check GitHub Issues:**
   - Search existing issues
   - Create new if needed

4. **Minimal example:**
   ```python
   from data_manager import DataManager
   dm = DataManager()
   data = dm.load_catalog('gaia', level='preview')
   print(len(data))
   ```

---

## ✅ SUCCESS CRITERIA

**Installation successful if:**
```
✅ Python imports work
✅ Tests pass
✅ App starts
✅ Browser opens
✅ Data loads (real or synthetic)
✅ Plots display
✅ Export works
```

---

## 🚀 NEXT STEPS

**After successful installation:**

1. **Explore:** Try all 7 modes
2. **Query:** Load real GAIA data
3. **Analyze:** Compare SSZ vs GR
4. **Export:** Download results
5. **Learn:** Read documentation
6. **Contribute:** Join development
7. **Share:** Tell colleagues

---

## 📊 ESTIMATED TIMES

```
Method              Time    
----------------------------
Colab (no install)  0 min   ✅
Minimal install     5 min
Full install        10 min
Virtual env setup   15 min
Full verification   20 min
```

---

**INSTALLATION GUIDE Version:** 1.0  
**Last Updated:** 2025-11-22  
**Status:** Complete

**Ready to explore the universe with SSZ! 🌌**

---

© 2025 Carmen Wrede, Lino Casu  
Licensed under ACSL v1.4
