# 🗺️ ROADMAP: ADVANCED FEATURES

**Status:** IN ENTWICKLUNG
**Datum:** 2025-11-22, 20:45 UTC+1

---

## ✅ PHASE 8.1: GRÖSSERE DATENBANK (LÄUFT)

**Status:** In Arbeit...
- [x] create_star_database.py → 500k Sterne
- [ ] GAIA Query läuft (~5-10 Min)
- [ ] CSV wird gespeichert
- [ ] App updaten auf neue DB

---

## 📋 PHASE 8.2: OBJEKT-SELEKTION

**Was gebraucht wird:**
1. Click-Handler in Plotly Maps
2. Selected Object State
3. Info-Panel bei Click
4. Highlight in Plot

**Implementierung:**
```python
# In create_sky_map()
fig.update_layout(
    clickmode='event+select',
    hovermode='closest'
)

# Add custom data for selection
fig.data[0].customdata = df[['source_id', 'name', 'distance_ly']]

# Gradio callback
@gr.on(plot.select)
def on_select(evt):
    # evt.index = selected point
    obj_data = df.iloc[evt.index]
    return create_object_info(obj_data)
```

---

## 📋 PHASE 8.3: SUCHMASKE

**Features:**
- Textbox für Name/Koordinaten
- Autocomplete Dropdown
- "Find" Button
- Zoom to object

**UI Layout:**
```python
with gr.Row():
    search_box = gr.Textbox(label="Search (Name or RA,Dec)")
    search_btn = gr.Button("Find")

suggestions = gr.Dropdown(label="Suggestions", choices=[])
```

---

## 📋 PHASE 8.4: 3D NAVIGATION

**Rotation um Objekt:**
```python
def create_3d_centered_view(df, center_idx, distance, h_angle, v_angle):
    center_obj = df.iloc[center_idx]
    
    # Set camera
    camera = dict(
        center=dict(x=center_obj['x'], y=center_obj['y'], z=center_obj['z']),
        eye=dict(
            x=distance * np.cos(h_angle) * np.cos(v_angle),
            y=distance * np.sin(h_angle) * np.cos(v_angle),
            z=distance * np.sin(v_angle)
        )
    )
    
    fig.update_layout(scene_camera=camera)
```

**UI:**
- Object Dropdown
- Distance Slider
- H-Angle Slider
- V-Angle Slider
- Rotation Buttons

---

## 📋 PHASE 8.5: PROGRESSIVE LOADING

**Konzept:**
1. Initial: Load nearby objects (distance < threshold)
2. On zoom: Load more in view
3. On pan: Load new region

**Implementierung:**
```python
class ProgressiveLoader:
    def __init__(self, full_db):
        self.full_db = full_db
        self.loaded_shells = []
    
    def load_shell(self, distance_min, distance_max):
        mask = (
            (self.full_db['distance_ly'] >= distance_min) &
            (self.full_db['distance_ly'] < distance_max)
        )
        return self.full_db[mask]
    
    def load_region(self, ra_min, ra_max, dec_min, dec_max):
        mask = (
            (self.full_db['ra'] >= ra_min) &
            (self.full_db['ra'] <= ra_max) &
            (self.full_db['dec'] >= dec_min) &
            (self.full_db['dec'] <= dec_max)
        )
        return self.full_db[mask]
```

---

## 📋 PHASE 8.6: PHYSICS MIT OBJEKTEN

**Real Data in Physics Plots:**

```python
def create_g1_g2_with_objects(objects_df):
    # Theorie-Kurven
    fig = create_g1_g2_domain_plot()
    
    # Real objects overlaid
    if objects_df is not None:
        # Calculate r/r_s for each object
        for idx, obj in objects_df.iterrows():
            r_ratio = obj['distance_pc'] * PC_TO_M / obj['r_s']
            xi_val = obj['xi']
            
            fig.add_trace(go.Scatter(
                x=[r_ratio],
                y=[xi_val],
                mode='markers',
                marker=dict(size=8, color='yellow'),
                name=obj['name']
            ))
    
    return fig
```

**Selektion:**
- Click auf Punkt
- Zeige Details
- Highlight in anderen Plots

---

## ⏱️ ZEITPLAN:

| Phase | Feature | Zeit | Status |
|-------|---------|------|--------|
| 8.1 | Größere DB | 15 min | 🔄 Läuft |
| 8.2 | Objekt-Selektion | 20 min | ⏳ Wartet |
| 8.3 | Suchmaske | 15 min | ⏳ Wartet |
| 8.4 | 3D Navigation | 25 min | ⏳ Wartet |
| 8.5 | Progressive Load | 30 min | ⏳ Wartet |
| 8.6 | Physics Integration | 20 min | ⏳ Wartet |

**TOTAL:** ~125 Minuten

---

## 🎯 PRIORITÄT:

**MUSS HEUTE:**
1. ✅ Größere Datenbank (500k)
2. Objekt-Selektion
3. Suchmaske

**KANN SPÄTER:**
4. 3D Navigation (komplex)
5. Progressive Loading (komplex)
6. Physics Integration

---

**Fortsetzung wenn 500k DB fertig ist!** ⏳
