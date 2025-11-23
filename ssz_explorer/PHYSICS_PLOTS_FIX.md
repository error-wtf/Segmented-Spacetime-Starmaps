# 🔬 Physics Plots Fix - Status & Lösung

## ❌ **PROBLEM:**

Physics Plots sind **LEER** weil:
1. ✗ Kein Objekt ist beim Start selektiert (`selected_object = None`)
2. ✗ User muss MANUELL in "Object Search" gehen und Objekt wählen
3. ✗ Erst DANN funktionieren die Physics Plots
4. ✗ Keine klare Anleitung für User

## ✅ **LÖSUNG:**

### **Option 1: Auto-Select Default Object (EMPFOHLEN)**

Beim App-Start automatisch ein interessantes Objekt selektieren:
- Sgr A* (wenn in DB)
- Oder erstes Objekt mit guten SSZ-Parametern
- Physics Plots funktionieren SOFORT

### **Option 2: Clear Instructions**

Große Warnung im Physics Tab:
```
⚠️ NO OBJECT SELECTED!

Please go to "Object Search" tab first:
1. Search for: "Sag A*" or any object
2. Click "Select Object"
3. Return here to see physics plots
```

### **Option 3: Integrated Object Selector**

Object-Selector DIREKT im Physics Tab einbauen
- User kann dort sofort Objekt wählen
- Keine Navigation zwischen Tabs nötig

## 🎯 **EMPFOHLENE IMPLEMENTIERUNG:**

**Kombination aus Option 1 + 3:**
1. ✅ Default-Objekt beim Start
2. ✅ Quick-Selector im Physics Tab
3. ✅ Plots funktionieren SOFORT
4. ✅ User kann einfach wechseln

---

## 📊 **Aktuelle Code-Analyse:**

**select_object() Funktion (Line 398):**
```python
def select_object(obj_index):
    global selected_object, selected_object_index
    
    db = load_star_database()
    selected_object = db.iloc[obj_index]  # ← Wird nur bei User-Auswahl gesetzt!
    selected_object_index = obj_index
```

**Physics Plot Button (Line 1038):**
```python
def plot_domains_with_objects(show_objects):
    if selected_object is not None:  # ← Wenn None, dann default Sgr A*
        mass_msun = selected_object['mass_msun']
        fig = create_g1_g2_domain_plot(mass_msun=mass_msun)
    else:
        fig = create_g1_g2_domain_plot()  # Default Sgr A*
```

**Problem:** Default Sgr A* funktioniert theoretisch, ABER Plots zeigen keine echten Daten weil `selected_object = None`!

---

## 🔧 **QUICK FIX:**

**Initialisiere selected_object beim App-Start:**

```python
# Am Ende von load_star_database(), nach [2/3] Database ready:
print("[3/3] Auto-selecting default object (Galactic Center)...")

# Find object near Galactic Center
db = load_star_database()
gc_ra, gc_dec = 266.42, -29.01
distances = np.sqrt((db['ra'] - gc_ra)**2 + (db['dec'] - gc_dec)**2)
nearest_idx = np.argmin(distances)

selected_object = db.iloc[nearest_idx]
selected_object_index = nearest_idx

print(f"[3/3] Default object: ID {selected_object['source_id']} ({selected_object['distance_ly']:.1f} ly)")
```

**Result:**
- ✅ Physics Plots funktionieren SOFORT
- ✅ User sieht interessantes Objekt (nahe Galactic Center)
- ✅ User kann immer noch anderes Objekt wählen

---

© 2025 SSZ Explorer
Erstellt: 2025-11-23
