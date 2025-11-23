# 🎯 **PRIORITY PLOTS - TODO LIST**

**Basis:** 570 Plots in PAPER-RESTORED analysiert  
**Ziel:** SSZ Explorer mit Key Physics Plots erweitern

---

## ✅ **AKTUELLER STATUS (4 Plots implementiert)**

| # | Plot | Status | Funktion |
|---|------|--------|----------|
| 1 | g₁/g₂ Domains | ✅ Fixed | `create_g1_g2_domain_plot()` |
| 2 | Time Dilation | ✅ Fixed | `create_time_dilation_comparison()` |
| 3 | Radial Stretch | ✅ Works | `create_radial_stretch_plot()` |
| 4 | Combined Analysis | ✅ Works | `create_combined_ssz_analysis()` |

**Fix Applied:**
- Alle Plots nutzen jetzt Sgr A* Masse (4.3×10⁶ M☉)
- Funktionieren korrekt für massive Objekte

---

## 🔴 **QUICK WINS - DIESE WOCHE (5 Plots, ~10-14h)**

### **1. Photon Sphere Comparison** ⏱️ 1-2h
**File:** `ssz_observables_plots.py`  
**Funktion:** `create_photon_sphere_plot()`

**Features:**
```python
- r_ph vs Mass (SSZ vs GR)
- 3% Shift Annotation
- r_ph = 1.5*r_s (GR) vs 1.55*r_s (SSZ)
- Multiple masses: 1M☉, 10M☉, 100M☉, Sgr A*
```

**Code Basis:**
```python
from ssz_core_functions import r_photon_sphere_gr, r_photon_sphere_ssz
# Already implemented!
```

---

### **2. Shadow Radius Plot** ⏱️ 1-2h
**File:** `ssz_observables_plots.py`  
**Funktion:** `create_shadow_radius_plot()`

**Features:**
```python
- Shadow Radius vs Mass
- b = 3√3*r_s/2 (GR)
- b = r_ph*√(1/A(r_ph)) (SSZ)
- 2-3% Difference
- EHT M87 comparison
```

**Code Basis:**
```python
from ssz_core_functions import shadow_radius_gr, shadow_radius_ssz
# Already implemented!
```

---

### **3. Energy Conditions Plot** ⏱️ 2-3h
**File:** `ssz_validation_plots.py`  
**Funktion:** `create_energy_conditions_plot()`

**Features:**
```python
- WEC: ρ ≥ 0, ρ + p_t ≥ 0
- DEC: ρ ≥ |p_r|, ρ ≥ |p_t|
- SEC: ρ + p_r + 2p_t ≥ 0
- 3-Panel Plot: ρ(r), p_r(r), p_t(r)
- Shaded regions: Satisfied vs Violated
```

**Code Basis:**
```python
from ssz_core_functions import check_energy_conditions, rho_pr_pt
# Already implemented!
```

---

### **4. G79 Enhanced Temperature Profile** ⏱️ 3-4h
**File:** `ssz_real_data_plots.py`  
**Funktion:** `create_g79_temperature_enhanced()`

**Features:**
```python
- Real G79.29+0.46 data points
- Piecewise SSZ fit (sharp break)
- Smooth GR fit (no break)
- Chi-squared comparison
- Annotations: break point, slopes
- Error bars
```

**Data:**
```python
# G79 Shell Data (from PAPER-RESTORED)
SHELL_R = [1.2, 2.3, 4.5]  # pc
SHELL_T = [500, 200, 60]   # K
```

---

### **5. Kretschmann Scalar Plot** ⏱️ 2-3h
**File:** `ssz_validation_plots.py`  
**Funktion:** `create_kretschmann_plot()`

**Features:**
```python
- K_GR = 48(GM)²/r⁶
- K_SSZ = D⁶ * K_GR
- Log-log plot
- Singularity comparison
- SSZ smoother near r_s
```

**Code Basis:**
```python
from ssz_core_functions import kretschmann_gr, kretschmann_ssz
# Already implemented!
```

---

## 🟡 **WEEK 2 - NESTED & REAL DATA (5 Plots, ~15-20h)**

### **6. Photon Redshift g²→g¹** ⏱️ 3-4h
**Beschreibung:** Radio precursor mechanism  
**Formel:** `z = 1/γ_seg - 1`

### **7. Cygnus X Velocity Plot** ⏱️ 3-4h
**Beschreibung:** Expansion velocity comparison  
**Data:** Cygnus X real measurements

### **8. Collapse Rate Real Data** ⏱️ 3-4h
**Beschreibung:** dΞ/dt from G79 data  
**Formel:** `C(Ξ) = Γ*[V']²`

### **9. QNM Frequency** ⏱️ 3-4h
**Beschreibung:** Quasi-normal modes SSZ vs GR  
**Formel:** `f = c/(1.55*r_s)`

### **10. Velocity Transform** ⏱️ 3-4h
**Beschreibung:** v_obs vs v_local in nested metric  
**Formel:** `v_obs = v_local / γ_seg`

---

## 🟢 **WEEK 3 - SHARP BREAK & COLLAPSE (5 Plots, ~15-20h)**

### **11. Sharp Break Temperature** ⏱️ 3-4h
**Beschreibung:** Enhanced mit break detection

### **12. Gradient Curvature** ⏱️ 3-4h
**Beschreibung:** d²Ξ/dr² analysis

### **13. Coherence Decay** ⏱️ 3-4h
**Beschreibung:** Ξ(t) exponential decay

### **14. Coherence Scaling** ⏱️ 3-4h
**Beschreibung:** Multiple trajectories

### **15. Chi-Squared Split** ⏱️ 3-4h
**Beschreibung:** Statistical validation

---

## 📝 **IMPLEMENTIERUNGS-TEMPLATE**

**Für jeden neuen Plot:**

### **1. Create Function Skeleton:**
```python
def create_<plot_name>():
    """
    <Description>
    
    Shows: <What it shows>
    Formula: <Key formula>
    
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    # Constants
    M = 4.3e6 * M_SUN  # Sgr A*
    
    # Calculate data
    # ...
    
    # Create figure
    fig = go.Figure()
    
    # Add traces
    # ...
    
    # Update layout
    fig.update_layout(
        title="...",
        xaxis_title="...",
        yaxis_title="...",
        plot_bgcolor='#0a0a1f',
        paper_bgcolor='#000010',
        font=dict(color='white'),
        height=600
    )
    
    return fig
```

### **2. Add to Gradio UI:**
```python
with gr.Tab("<Tab Name>"):
    gr.Markdown("**Description**")
    btn = gr.Button("📊 Generate Plot")
    plot = gr.Plot()
    
    btn.click(fn=create_<plot_name>, outputs=plot)
```

### **3. Test:**
```python
# Test script
from ssz_<module> import create_<plot_name>
fig = create_<plot_name>()
print(f"Traces: {len(fig.data)}")
fig.show()  # or fig.write_html("test.html")
```

---

## 📊 **PROGRESS TRACKING**

### **Week 1:**
- [x] Fix existing 4 plots (Sgr A* mass)
- [ ] Photon Sphere (1-2h)
- [ ] Shadow Radius (1-2h)
- [ ] Energy Conditions (2-3h)
- [ ] G79 Enhanced (3-4h)
- [ ] Kretschmann (2-3h)

**Total Week 1:** 4 fixed + 5 new = **9 plots**

### **Week 2:**
- [ ] Photon Redshift (3-4h)
- [ ] Cygnus X Velocity (3-4h)
- [ ] Collapse Rate (3-4h)
- [ ] QNM Frequency (3-4h)
- [ ] Velocity Transform (3-4h)

**Total Week 2:** +5 = **14 plots**

### **Week 3:**
- [ ] Sharp Break Temp (3-4h)
- [ ] Gradient Curvature (3-4h)
- [ ] Coherence Decay (3-4h)
- [ ] Coherence Scaling (3-4h)
- [ ] Chi-Squared Split (3-4h)

**Total Week 3:** +5 = **19 plots**

---

## 🎯 **SUCCESS METRICS**

**1 Month Goal:**
- ✅ 20 Physics Plots implemented
- ✅ All with Plotly interactive
- ✅ Integrated in Gradio UI
- ✅ Tested with Sgr A* mass

**Quality Criteria:**
- ✅ Scientific accuracy (formulas from PAPER-RESTORED)
- ✅ Beautiful dark theme
- ✅ Interactive hover text
- ✅ Annotations & explanations
- ✅ Error handling

---

## 🔗 **RESOURCES**

**Code Sources:**
- `ssz_core_functions.py` - Core math
- PAPER-RESTORED plots_modules/ - Reference implementations
- `ssz_physics_plots.py` - Current 4 plots

**Documentation:**
- MATHEMATIK_ZUSAMMENFASSUNG.md
- PLOT_ANALYSIS_FOR_SSZ_EXPLORER.md
- PAPER-RESTORED/SHOW-ALL-PLOTS.md

**Data:**
- star_database_enriched.csv (500k objects)
- G79/Cygnus X shell data
- AKARI/ESO/NED enriched data

---

## ✅ **CHECKLIST PRO PLOT**

Für jeden neuen Plot:

- [ ] Mathematik aus PAPER-RESTORED übernommen
- [ ] Funktion implementiert
- [ ] Test-Script erstellt
- [ ] Gradio UI integriert
- [ ] Mit Sgr A* Masse getestet
- [ ] Dark theme styling
- [ ] Hover text informativ
- [ ] Annotationen hinzugefügt
- [ ] Error handling
- [ ] Dokumentation aktualisiert

---

**LOS GEHT'S MIT DEN QUICK WINS!** 🚀

---

© 2025 SSZ Explorer Team  
**Erstellt:** 2025-11-23  
**Nächstes Update:** Nach Week 1 (5 neue Plots)
