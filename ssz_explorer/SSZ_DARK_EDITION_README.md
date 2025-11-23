# 🌌 **SSZ EXPLORER - DARK EDITION**

**Fokussierte, kuratierte Physics Plots in PAPER-RESTORED Dark Theme**

© 2025 Carmen Wrede, Lino Casu, Bingsi

---

## ✅ **WAS IST DAS?**

**Die professionelle Version - keine 570 random plots!**

### **Selektive Filterung:**
- ✅ **NUR relevante Plots** (124 von 570)
- ✅ **6 Kategorien** statt 11
- ❌ **Keine "Additional" Spam-Plots** (478 entfernt!)
- ✅ **Dark Theme** wie PAPER-RESTORED

---

## 📊 **KURATIERTE KATEGORIEN**

| Kategorie | Count | Beschreibung |
|-----------|-------|--------------|
| **Paper Figures** | ~6 | Offizielle Paper-Plots |
| **Real Data** | ~9 | Echte Daten-Analysen |
| **Sharp Break** | ~6 | Temperature Break Analysen |
| **G79 Cygnus** | ~42 | G79.29+0.46 Plots |
| **Nested Metrics** | ~2 | Nested Submetric |
| **Comparison** | ~6 | Model Comparisons |

**Total:** 124 relevante Plots (statt 570!)

**Entfernt:**
- ❌ 478 "Additional" plots (generisch)
- ❌ 9 "Missing" plots (unvollständig)
- ❌ 4 "Generated" plots (Test)
- ❌ Vergleich-Zwischenschritt (redundant)

---

## 🎨 **DARK THEME COLORS**

**EXAKT wie PAPER-RESTORED:**

```python
DARK_BG = '#0a0a1f'        # Plot background (dunkelblau)
DARK_PAPER = '#000010'     # Paper background (fast schwarz)
DARK_GRID = 'rgba(100,100,150,0.3)'  # Grid lines
DARK_TEXT = 'white'        # Text

COLOR_GR = '#3498db'       # Blau für GR
COLOR_SSZ = '#e74c3c'      # Rot für SSZ
COLOR_ACCENT = '#2ecc71'   # Grün für Highlights
```

---

## 🔬 **LIVE PHYSICS PLOTS (7 Stück)**

Alle mit Dark Theme:

1. **Domain Structure** - Ξ(r) Segment Density
2. **Photon Sphere** - SSZ vs GR
3. **Shadow Radius** - EHT Observable (M87*)
4. **Time Dilation** - Universal Crossover
5. **Energy Conditions** - WEC/DEC/SEC (3-Panel)
6. **Kretschmann Scalar** - Curvature Invariant
7. **QNM Frequencies** - LIGO Band

**Alle Plots:**
- Dunkler Hintergrund (#0a0a1f)
- Weiße Schrift
- Professionelle Color-Scheme
- Interaktiv (Zoom, Pan)

---

## 🚀 **USAGE**

### **Start:**
```bash
cd E:\clone\Segmented-Spacetime-StarMaps\ssz_explorer
python ssz_explorer_dark.py
```

**Port:** http://localhost:7890

---

## 📂 **STRUKTUR**

```
ssz_explorer/
├── ssz_explorer_dark.py          # Dark Edition (124 Plots)
├── ssz_complete_570_plots.py     # Alle 570 Plots
├── gradio_app_complete.py        # Alte App (nur 4)
└── SSZ_DARK_EDITION_README.md    # Diese Datei
```

---

## 🎯 **UNTERSCHIEDE**

| Feature | Complete (570) | **Dark Edition** |
|---------|----------------|------------------|
| Plots | 570 | **124** (kuratiert!) |
| Kategorien | 11 | **6** (selektiert!) |
| Theme | Standard | **PAPER-RESTORED Dark** |
| "Additional" Spam | 478 | **0** (entfernt!) |
| Live Plots | 5 | **7** |
| Fokus | Alles | **Nur Wichtiges** |

---

## ✅ **VORTEILE**

**Warum Dark Edition?**

1. **Fokussiert** - Nur relevante Plots
2. **Professionell** - PAPER-RESTORED Style
3. **Performance** - Weniger Plots = schneller
4. **Übersichtlich** - Keine Spam-Plots
5. **Konsistent** - Dark Theme überall
6. **Wissenschaftlich** - Kuratierte Auswahl

---

## 📝 **FILTERUNG**

### **Ausgewählte Keywords:**
```python
if 'paper' in rel_path.lower():          # Paper Figures
elif 'real-data' in rel_path.lower():    # Real Data
elif 'sharp-break' in rel_path.lower():  # Sharp Break
elif 'g79' or 'cygnus':                  # G79 Cygnus
elif 'nested':                           # Nested Metrics
elif 'comparison':                       # Comparisons
```

### **Ignoriert:**
- ❌ `additional_*.png` (478 generic plots)
- ❌ `missing_*.png` (9 incomplete)
- ❌ `generated_*.png` (4 test plots)
- ❌ `vergleich-zwischenschritt` (redundant)

---

## 🔧 **TECHNISCHE DETAILS**

### **Plot Theme Function:**
```python
def apply_dark_theme(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color=DARK_TEXT)),
        plot_bgcolor=DARK_BG,
        paper_bgcolor=DARK_PAPER,
        font=dict(color=DARK_TEXT, size=12),
        xaxis=dict(gridcolor=DARK_GRID),
        yaxis=dict(gridcolor=DARK_GRID),
    )
    return fig
```

### **Automatische Filterung:**
- Lädt plot_list.json (570 plots)
- Filtert nach Kategorie-Keywords
- Reduziert auf 124 relevante
- Zeigt nur diese in Gallery

---

## 🎨 **VISUAL COMPARISON**

**Vorher (Standard Gradio):**
- ⚪ Weißer Hintergrund
- ⚫ Schwarzer Text
- 🎨 Default Colors

**Nachher (Dark Edition):**
- 🌌 Dunkelblauer Hintergrund (#0a0a1f)
- ⚪ Weißer Text
- 🎨 PAPER-RESTORED Colors (GR=Blue, SSZ=Red)

---

## 📊 **BEISPIEL: PHOTON SPHERE**

**Dark Edition:**
```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=masses, y=r_ph_gr, 
                        line=dict(color='#3498db', width=3)))
fig.add_trace(go.Scatter(x=masses, y=r_ph_ssz,
                        line=dict(color='#e74c3c', width=3)))

fig.update_layout(
    plot_bgcolor='#0a0a1f',     # Dark!
    paper_bgcolor='#000010',    # Darker!
    font=dict(color='white')    # White text!
)
```

**Resultat:** Professioneller Dark-Mode Plot! 🌌

---

## 🎯 **ZUSAMMENFASSUNG**

### **Was wurde gemacht:**
✅ 570 Plots analysiert  
✅ 124 relevante ausgewählt  
✅ 446 unwichtige entfernt  
✅ 6 Kategorien kuratiert  
✅ Dark Theme implementiert (PAPER-RESTORED Style)  
✅ 7 Live-Physics-Plots  
✅ Gallery mit Auto-Load  

### **Was ist besser:**
- 🎯 **Fokussiert** statt überladen
- 🌌 **Dark Theme** statt hell
- 📊 **124 Plots** statt 570 Spam
- ⚡ **Schneller** (weniger Daten)
- 🔬 **Professioneller** (kuratiert)

---

**KEINE SCHEISSE MEHR - NUR DAS WICHTIGSTE IN DARK!** 🚀

---

© 2025 Carmen Wrede, Lino Casu, Bingsi  
Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
