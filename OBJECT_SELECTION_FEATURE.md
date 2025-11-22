# 🎯 Object Selection Feature - Klickbare Objekte in Physics Plots

**Erstellt:** 2025-11-22  
**Priorität:** ⭐⭐⭐⭐⭐ HOCH  
**Zeit:** 4-6 Stunden  
**User Request:** "Objekte in den Physik-Bereichen müssen überall auswählbar sein"

---

## ❌ AKTUELLES PROBLEM

**Die Physics-Plots zeigen nur abstrakte Kurven, KEINE auswählbaren Objekte!**

```python
# comparison_visualizations.py - Zeile 78
fig.add_trace(go.Scatter(
    x=x_values, y=D_ssz,
    mode='lines',  # ❌ Nur Linie, keine Punkte!
    # ❌ KEINE echten Objekte
    # ❌ KEIN customdata
    # ❌ NICHT klickbar
))
```

**User sieht:**
- Mathematische Funktionen ✅
- ABER: Welcher Stern hat welchen Wert? ❌
- Click auf Plot → Nichts passiert ❌

---

## ✅ LÖSUNG - 3 STUFEN

### STUFE 1: Hover Info (1-2h) ⭐⭐⭐⭐⭐

Zeige Objekt-Details beim Mouse-Over

```python
def create_physics_plot_with_objects(objects_df):
    # Jedes Objekt als Punkt
    fig.add_trace(go.Scatter(
        x=objects_df['r_over_rs'],
        y=objects_df['D_ssz'],
        mode='markers',  # ✅ Punkte!
        customdata=objects_df[['source_id', 'ra', 'dec']],
        hovertemplate='<b>Star:</b> %{customdata[0]}<br>...'
    ))
```

### STUFE 2: Click Selection (2-3h) ⭐⭐⭐⭐

Click → Highlight in ALLEN Plots + Details zeigen

### STUFE 3: Multi-Select (1-2h) ⭐⭐⭐

Mehrere Objekte auswählen, vergleichen, exportieren

---

## 🎯 BETROFFENE PLOTS

❌ **Time Dilation** - Nur Kurven  
❌ **Velocity** - Nur Kurven  
❌ **Parameter Space** - Nicht klickbar  
❌ **Segment Density** - Keine Objekte  
⚠️  **Sky Map** - Teilweise OK (braucht Click)

---

## 📋 IMPLEMENTATION PLAN

**Phase 1 (2h):**
1. Update comparison_visualizations.py
2. Add hover info mit echten Objekten
3. Test

**Phase 2 (3h):**  
4. Erweitere object_selector.py
5. Integration in Gradio
6. Cross-plot highlight

**Phase 3 (1h):**
7. Multi-select
8. Export selection

---

## 🚀 QUICK START?

**Soll ich starten mit Phase 1 (Hover)?**

Das würde sofort zeigen:
- Welcher Stern wo ist
- Alle Object-Details
- Bessere wissenschaftliche Nutzbarkeit

**Zeit: 2 Stunden**

---

© 2025 Carmen Wrede, Lino Casu
