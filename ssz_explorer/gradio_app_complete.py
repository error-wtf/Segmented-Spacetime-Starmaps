#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Explorer - Complete & Stable Edition

100% funktionierende App mit ALLEN Features!

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

# ============================================================================
# UTF-8 SETUP (Windows-kompatibel)
# ============================================================================
import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ============================================================================
# IMPORTS - Nur funktionierende Module!
# ============================================================================
from pathlib import Path
import gradio as gr
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from astropy.coordinates import SkyCoord
from astropy import units as u

# Core modules (getestet & funktionierend!)
from star_map_generator import create_sky_map, create_3d_sky_map, create_default_universe
from ssz_physics_plots import (
    create_g1_g2_domain_plot,
    create_time_dilation_comparison,
    create_radial_stretch_plot,
    create_combined_ssz_analysis
)
from name_resolver import resolve_name, search_by_name_fuzzy, get_famous_objects_list

# ============================================================================
# GLOBALE VARIABLEN
# ============================================================================
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
star_database = None  # Wird beim Start geladen
last_query_data = None  # Für CSV Export
selected_object = None  # Aktuell selektiertes Objekt
selected_object_index = None  # Index des selektierten Objekts
selected_object_name = None  # Name des selektierten Objekts (für Physics Plots)

# ============================================================================
# DATENBANK-FUNKTIONEN
# ============================================================================

def load_star_database():
    """Lade 500k Sterne Datenbank."""
    global star_database
    
    if star_database is not None:
        return star_database
    
    # Try enhanced database first (with ALMA/AKARI/etc)
    enhanced_path = Path(__file__).parent / "ssz_data" / "star_database_enhanced.csv"
    if enhanced_path.exists():
        db_path = enhanced_path
        print(f"[INFO] Loading ENHANCED database with multi-catalog data: {db_path}")
    else:
        db_path = Path(__file__).parent / "ssz_data" / "star_database_50k.csv"
        print(f"[INFO] Loading standard GAIA database: {db_path}")
    
    # Try 500k first, fallback to 50k
    database_file_500k = Path(__file__).parent / 'ssz_data' / 'star_database_500k.csv'
    database_file_50k = Path(__file__).parent / 'ssz_data' / 'star_database_50k.csv'
    
    if database_file_500k.exists():
        print(f"[INFO] Loading 500k database: {database_file_500k}")
        star_database = pd.read_csv(database_file_500k)
        print(f"[INFO] Loaded {len(star_database):,} stars")
        return star_database
    elif database_file_50k.exists():
        print(f"[INFO] Loading 50k database: {database_file_50k}")
        star_database = pd.read_csv(database_file_50k)
        print(f"[INFO] Loaded {len(star_database):,} stars")
        return star_database
    else:
        print("[WARNING] Database not found, using default universe")
        star_database = create_default_universe()
        return star_database


# ============================================================================
# SKY MAP FUNKTIONEN
# ============================================================================

def generate_sky_map():
    """Generate 2D sky map with 500k database."""
    global last_query_data
    
    # Use query data if available, otherwise use database
    if last_query_data is not None and not last_query_data.empty:
        data = last_query_data
    else:
        data = load_star_database()
    
    # Sample for performance if too many
    if len(data) > 10000:
        import random
        indices = sorted(random.sample(range(len(data)), 10000))
        data_sample = data.iloc[indices].copy()
        # Store indices for click mapping
        data_sample['original_index'] = indices
    else:
        data_sample = data.copy()
        data_sample['original_index'] = data_sample.index
    
    fig = create_sky_map(
        data_sample,
        title=f"🌌 Sky Map - {len(data):,} Stars (showing {len(data_sample):,})<br><sub>GAIA DR3 - Click on star for details</sub>"
    )
    
    # Enable click mode
    fig.update_layout(clickmode='event+select')
    
    return fig


def generate_3d_sky_map():
    """Generate 3D sky map - OPTIMIZED for performance."""
    global last_query_data
    
    try:
        # Use query data if available, otherwise use database
        if last_query_data is not None and not last_query_data.empty:
            data = last_query_data
        else:
            data = load_star_database()
        
        # FAST MODE: Only 1000 stars for quick rendering
        if len(data) > 1000:
            import random
            indices = sorted(random.sample(range(len(data)), 1000))
            data_sample = data.iloc[indices].copy()
        else:
            data_sample = data.copy()
        
        return create_3d_sky_map(
            data_sample,
            title=f"🌌 3D Sky Map - {len(data):,} Total ({len(data_sample):,} shown)<br><sub>GAIA DR3 - Sampled for performance</sub>"
        )
    except Exception as e:
        # Return empty plot with error message
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error generating 3D map: {str(e)}<br>Try using fewer stars or check data format",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="red")
        )
        return fig


def generate_constellation_map(ra, dec, fov):
    """Generate constellation map for specific region."""
    try:
        db = load_star_database()
        
        # Validate inputs
        try:
            ra_val = float(ra) if ra else 266.4
            dec_val = float(dec) if dec else -29.0
            fov_val = float(fov) if fov else 30.0
        except (ValueError, TypeError):
            raise ValueError("Invalid coordinates - must be numbers")
        
        # Filter to region
        half_fov = fov_val / 2
        mask = (
            (db['ra'] >= ra_val - half_fov) &
            (db['ra'] <= ra_val + half_fov) &
            (db['dec'] >= dec_val - half_fov) &
            (db['dec'] <= dec_val + half_fov)
        )
        
        region_data = db[mask].copy()
        
        if len(region_data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text=f"❌ No stars found in region<br>RA={ra_val:.1f}°, Dec={dec_val:.1f}°, FOV={fov_val:.1f}°<br><br>Try different coordinates or larger FOV",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="orange")
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='#0a0a1f',
                plot_bgcolor='#000010'
            )
            return fig
        
        # Limit to 500 stars for performance
        if len(region_data) > 500:
            import random
            indices = sorted(random.sample(range(len(region_data)), 500))
            region_data = region_data.iloc[indices].copy()
        
        return create_3d_sky_map(
            region_data,
            title=f"📍 Region View: RA={ra_val:.1f}°, Dec={dec_val:.1f}° (FOV={fov_val:.1f}°)<br>"
                  f"<sub>{len(region_data)} stars shown (sampled for performance)</sub>"
        )
        
    except Exception as e:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_annotation(
            text=f"❌ Error: {str(e)}<br><br>Check coordinates and try again",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='#0a0a1f',
            plot_bgcolor='#000010'
        )
        return fig


def download_csv():
    """Download complete dataset as CSV."""
    global last_query_data
    
    if last_query_data is None or last_query_data.empty:
        # Use full database
        data = load_star_database()
    else:
        data = last_query_data
    
    # Save to temp file
    import tempfile
    fd, path = tempfile.mkstemp(suffix='.csv', prefix='ssz_export_')
    
    try:
        data.to_csv(path, index=False)
        return path
    except Exception as e:
        print(f"CSV export error: {e}")
        if os.path.exists(path):
            os.close(fd)
            os.unlink(path)
        return None


# ============================================================================
# OBJEKT-SELEKTION & SUCHE
# ============================================================================

def search_object(search_term):
    """Suche nach Objekten in der Datenbank."""
    if not search_term or search_term.strip() == "":
        return [], "Enter search term (name, coordinates, or source_id)"
    
    # SPECIAL TEST OBJECTS for extreme comparisons
    if search_term.strip().lower().startswith('test:'):
        test_name = search_term.strip()[5:].strip().lower()
        test_objects = {
            'sun': {'name': 'Test: Sun', 'mass': 1.0, 'dist': 1.0},
            'neutron': {'name': 'Test: Neutron Star', 'mass': 2.0, 'dist': 100.0},
            'sgr a*': {'name': 'Test: Sgr A* (Real)', 'mass': 4.3e6, 'dist': 8000.0},
            'm87*': {'name': 'Test: M87* Black Hole', 'mass': 6.5e9, 'dist': 16.8e6},
            'small': {'name': 'Test: Small Star (0.5 M☉)', 'mass': 0.5, 'dist': 10.0},
            'giant': {'name': 'Test: Giant Star (20 M☉)', 'mass': 20.0, 'dist': 500.0}
        }
        if test_name in test_objects:
            obj = test_objects[test_name]
            # Return as special format: "NAME|test:TYPE"
            return [(f"{obj['name']} | M={obj['mass']:.1e} M☉ | d={obj['dist']:.1f} pc", f"test:{test_name}")], \
                   f"✅ Test object: {obj['name']}"
        else:
            available = ', '.join(test_objects.keys())
            return [], f"💡 Available test objects: test:{available}"
    
    db = load_star_database()
    search_term = search_term.strip().lower()
    
    # Smart preprocessing: "79" -> "G79", "87" -> "M87", etc.
    if search_term.isdigit():
        # Try common prefixes
        for prefix in ['G', 'M', 'NGC ']:
            name_result = resolve_name(prefix + search_term)
            if name_result:
                search_term = prefix + search_term
                break
    
    # Try name resolution first
    name_result = resolve_name(search_term)
    if name_result:
        # Found by name! Now find in database
        ra_search = name_result['ra']
        dec_search = name_result['dec']
        
        distances = np.sqrt((db['ra'] - ra_search)**2 + (db['dec'] - dec_search)**2)
        nearest_idx = np.argmin(distances)
        
        obj = db.iloc[nearest_idx]
        
        # WICHTIG: Speichere den GESUCHTEN Namen, nicht den GAIA Namen!
        # Format: "NAME|INDEX" so dass wir später wissen welcher Name gesucht wurde
        result = [(
            f"🌟 {name_result['name']} | RA:{obj['ra']:.2f}° Dec:{obj['dec']:.2f}° | {obj['distance_ly']:.1f}ly",
            f"{name_result['name']}|{int(nearest_idx)}"  # ← GEÄNDERT: Name + Index
        )]
        return result, f"✅ Found: {name_result['name']} ({name_result['type']}) - Distance to nearest star: {distances[nearest_idx]:.4f}°"
    
    # Try parsing as coordinates (RA, Dec)
    if ',' in search_term:
        try:
            parts = search_term.split(',')
            ra_search = float(parts[0].strip())
            dec_search = float(parts[1].strip())
            
            # Find nearby objects (within 1 degree)
            distances = np.sqrt((db['ra'] - ra_search)**2 + (db['dec'] - dec_search)**2)
            nearby_idx = np.argsort(distances)[:10]
            
            results = []
            for idx in nearby_idx:
                obj = db.iloc[idx]
                results.append((
                    f"ID:{obj['source_id']} | RA:{obj['ra']:.2f}° Dec:{obj['dec']:.2f}° | {obj['distance_ly']:.1f}ly",
                    int(idx)
                ))
            
            return results, f"Found {len(results)} objects near RA={ra_search}°, Dec={dec_search}°"
            
        except:
            pass
    
    # Try parsing as source_id
    try:
        source_id = int(search_term)
        mask = db['source_id'] == source_id
        if mask.any():
            idx = mask.idxmax()
            obj = db.iloc[idx]
            result = [(
                f"ID:{obj['source_id']} | RA:{obj['ra']:.2f}° Dec:{obj['dec']:.2f}° | {obj['distance_ly']:.1f}ly",
                int(idx)
            )]
            return result, f"Found object with ID {source_id}"
    except:
        pass
    
    # Try fuzzy name search
    fuzzy_results = search_by_name_fuzzy(search_term)
    if fuzzy_results:
        names = [f"{obj['name']} ({obj['type']})" for obj in fuzzy_results[:5]]
        return [], f"💡 Did you mean: {', '.join(names)}?"
    
    return [], f"❌ No objects found for: {search_term}\n💡 Try: 'Sag A*', 'Betelgeuse', 'M31', or coordinates"


def select_object(obj_index_or_combo):
    """Selektiere ein Objekt."""
    global selected_object, selected_object_index, selected_object_name
    
    if obj_index_or_combo is None:
        selected_object = None
        selected_object_index = None
        selected_object_name = None
        return "No object selected"
    
    # Handle TEST objects
    if isinstance(obj_index_or_combo, str) and obj_index_or_combo.startswith('test:'):
        test_name = obj_index_or_combo[5:]
        test_objects = {
            'sun': {'name': 'Test: Sun', 'mass': 1.0, 'dist': 1.0, 'source_id': 'TEST_SUN'},
            'neutron': {'name': 'Test: Neutron Star', 'mass': 2.0, 'dist': 100.0, 'source_id': 'TEST_NEUTRON'},
            'sgr a*': {'name': 'Test: Sgr A* (Real)', 'mass': 4.3e6, 'dist': 8000.0, 'source_id': 'TEST_SGRA'},
            'm87*': {'name': 'Test: M87* Black Hole', 'mass': 6.5e9, 'dist': 16.8e6, 'source_id': 'TEST_M87'},
            'small': {'name': 'Test: Small Star (0.5 M☉)', 'mass': 0.5, 'dist': 10.0, 'source_id': 'TEST_SMALL'},
            'giant': {'name': 'Test: Giant Star (20 M☉)', 'mass': 20.0, 'dist': 500.0, 'source_id': 'TEST_GIANT'}
        }
        obj = test_objects[test_name]
        selected_object_name = obj['name']
        selected_object_index = -1
        # Create fake pandas Series
        selected_object = pd.Series({
            'source_id': obj['source_id'],
            'ra': 0.0, 'dec': 0.0,
            'distance_pc': obj['dist'],
            'distance_ly': obj['dist'] * 3.26,
            'mass_msun': obj['mass'],
            'phot_g_mean_mag': 10.0,
            'xi': 0.1,
            'D_ssz': 0.9,
            'pmra': 0.0, 'pmdec': 0.0,
            'radial_velocity': 0.0
        })
        info = f"""
## 🎯 Selected Object

**Name:** {selected_object_name}  
**Source ID:** {obj['source_id']} (TEST OBJECT)  
**Position:** Test Object (no real coordinates)  
**Distance:** {selected_object['distance_ly']:.2f} ly ({selected_object['distance_pc']:.2f} pc)  
**Mass:** {selected_object['mass_msun']:.2e} M☉

### ⚠️ TEST OBJECT for extreme comparison
This is a synthetic object for testing physics plot differences.
"""
        print(f"[INFO] Selected TEST object: {selected_object_name}")
        return info
    
    db = load_star_database()
    
    # Check if we got "NAME|INDEX" format (from search) or just INDEX
    if isinstance(obj_index_or_combo, str) and '|' in obj_index_or_combo:
        # Format: "Sgr A*|12345"
        parts = obj_index_or_combo.split('|')
        searched_name = parts[0]
        obj_index = int(parts[1])
        
        # Use the SEARCHED name directly!
        selected_object_name = searched_name
        print(f"[INFO] Using searched name: {searched_name}")
    else:
        # Regular index, try to resolve name
        obj_index = int(obj_index_or_combo)
        selected_object_name = None  # Will be set below
    
    if obj_index >= len(db):
        return f"Invalid index: {obj_index}"
    
    selected_object = db.iloc[obj_index]
    selected_object_index = obj_index
    
    # Try to get name (only if not already set from search)
    if not selected_object_name:
        obj_result = resolve_name(f"{selected_object['ra']},{selected_object['dec']}")
        if obj_result:
            selected_object_name = obj_result['name']
        else:
            # Check if object has a name column
            if 'name' in selected_object.index and pd.notna(selected_object['name']):
                selected_object_name = str(selected_object['name'])
            elif 'target_name' in selected_object.index and pd.notna(selected_object['target_name']):
                selected_object_name = str(selected_object['target_name'])
            else:
                # Use shortened GAIA ID
                source_id = str(selected_object['source_id'])
                if len(source_id) > 15:
                    selected_object_name = f"GAIA ...{source_id[-8:]}"
                else:
                    selected_object_name = f"GAIA {source_id}"
    
    # Create info text
    info = f"""
## 🎯 Selected Object

**Name:** {selected_object_name}  
**Source ID:** {selected_object['source_id']}  
**Position:** RA = {selected_object['ra']:.4f}°, Dec = {selected_object['dec']:.4f}°  
**Distance:** {selected_object['distance_ly']:.2f} ly ({selected_object['distance_pc']:.2f} pc)  
**Magnitude:** {selected_object['phot_g_mean_mag']:.2f}  
**Mass:** {selected_object['mass_msun']:.3f} M☉

### SSZ Parameters:
- **Ξ(r):** {selected_object['xi']:.6f}  
- **D_SSZ:** {selected_object['D_ssz']:.6f}  

**Proper Motion:** RA: {selected_object['pmra']:.2f} mas/yr, Dec: {selected_object['pmdec']:.2f} mas/yr
"""
    
    if not pd.isna(selected_object.get('radial_velocity')):
        info += f"**Radial Velocity:** {selected_object['radial_velocity']:.2f} km/s\n"
    
    print(f"[INFO] Selected object: {selected_object_name}")  # Debug
    
    return info


# ============================================================================
# GRADIO APP
# ============================================================================

print("="*80)
print("SSZ EXPLORER - COMPLETE EDITION")
print("="*80)
print()
print("[1/3] Loading 50,000 star database...")
db = load_star_database()
print(f"[2/3] Database ready: {len(db):,} stars")
print()

# Erstelle Gradio Interface
with gr.Blocks(title="SSZ Explorer - Complete", theme=gr.themes.Soft()) as app:
    
    gr.Markdown("""
    # 🌌 SSZ Explorer - Complete Edition
    
    **50,000 GAIA DR3 Stars | SSZ Physics | Interactive Maps**
    
    Explore the universe with Segmented Spacetime physics!
    
    ---
    """)
    
    # TAB 1: Start
    with gr.Tab("🏠 Start"):
        gr.Markdown(f"""
        ### ✅ SSZ Explorer Running!
        
        **Database:** {len(db):,} GAIA DR3 stars loaded
        **Status:** Ready
        **Features:** Sky Maps | SSZ Physics | Object Search | CSV Export
        
        Navigate to other tabs to explore!
        """)
    
    # TAB 1.5: Object Search & Selection
    with gr.Tab("🔍 Object Search"):
        gr.Markdown("### Search & Select Objects")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("""
                **Search by:**
                - **Name:** `Sag A*`, `Betelgeuse`, `M31`, `Proxima`
                - **Aliases:** `Sagittarius A*`, `α Ori`, `Andromeda`
                - **Coordinates:** `RA, Dec` (e.g., `266.4, -29.0`)
                - **Source ID:** Integer (e.g., `1234567890`)
                - **Test Objects:** `test:sun`, `test:sgr a*`, `test:m87*` (for extreme comparisons)
                
                **Famous Objects:** Sgr A*, Betelgeuse, Sirius, Vega, Rigel, Proxima, M31, M42, Pleiades, and more!
                
                **🧪 Test Objects (extreme masses for plot comparison):**
                - `test:sun` - 1 M☉, 1 pc
                - `test:neutron` - 2 M☉, 100 pc
                - `test:sgr a*` - 4.3×10⁶ M☉, 8000 pc
                - `test:m87*` - 6.5×10⁹ M☉, 16.8 Mpc
                - `test:small` - 0.5 M☉, 10 pc
                - `test:giant` - 20 M☉, 500 pc
                """)
                
                search_input = gr.Textbox(
                    label="Search Term",
                    placeholder="Enter coordinates (RA,Dec) or source ID",
                    lines=1
                )
                search_btn = gr.Button("🔍 Search", variant="primary", size="lg")
                
                search_results = gr.Dropdown(
                    label="Search Results",
                    choices=[],
                    interactive=True
                )
                
                select_btn = gr.Button("✅ Select Object", variant="secondary")
                
            with gr.Column(scale=2):
                object_info = gr.Markdown("**No object selected**")
        
        search_status = gr.Textbox(label="Status", lines=2, interactive=False)
        
        def on_search(search_term):
            results, status = search_object(search_term)
            if results:
                return gr.Dropdown(choices=results, value=results[0][1]), status
            else:
                return gr.Dropdown(choices=[]), status
        
        def on_select(obj_idx):
            if obj_idx is None:
                return "No object selected"
            info = select_object(obj_idx)
            return info
        
        search_btn.click(
            fn=on_search,
            inputs=search_input,
            outputs=[search_results, search_status]
        )
        
        select_btn.click(
            fn=on_select,
            inputs=search_results,
            outputs=object_info
        )
    
    # TAB 2: Visualizations
    with gr.Tab("📊 Visualizations"):
        gr.Markdown("### Interactive Star Maps")
        
        with gr.Tabs():
            # Sub-Tab: 2D Sky Map
            with gr.Tab("Sky Map (2D)"):
                gr.Markdown("**Full sky view - Click on star for details**")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        skymap_btn = gr.Button("🗺️ Generate Sky Map", variant="primary", size="lg")
                        skymap_plot = gr.Plot(label="2D Sky Map")
                    
                    with gr.Column(scale=1):
                        clicked_object_info = gr.Markdown("**Click on a star to see details**")
                
                skymap_btn.click(
                    fn=generate_sky_map,
                    inputs=None,
                    outputs=skymap_plot
                )
                
                # Note: Plotly click events in Gradio need special handling
                # For now, users can use Object Search tab to find objects
                gr.Markdown("*Tip: Use 'Object Search' tab to find specific objects by coordinates*")
            
            # Sub-Tab: 3D Sky Map
            with gr.Tab("3D Sky Map"):
                gr.Markdown("**Interactive 3D view with Object-Centered Navigation**")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        skymap_3d_btn = gr.Button("🌐 Generate 3D Map", variant="primary", size="lg")
                        skymap_3d_plot = gr.Plot(label="3D Sky Map")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎯 Object-Centered View")
                        gr.Markdown("*Select an object in 'Object Search' tab first*")
                        
                        center_on_obj_btn = gr.Button("📍 Center on Selected Object", variant="secondary")
                        
                        nav_distance = gr.Slider(
                            minimum=10,
                            maximum=1000,
                            value=100,
                            step=10,
                            label="Camera Distance (ly)"
                        )
                        
                        nav_h_angle = gr.Slider(
                            minimum=0,
                            maximum=360,
                            value=45,
                            step=5,
                            label="Horizontal Angle (°)"
                        )
                        
                        nav_v_angle = gr.Slider(
                            minimum=-90,
                            maximum=90,
                            value=30,
                            step=5,
                            label="Vertical Angle (°)"
                        )
                        
                        update_view_btn = gr.Button("🔄 Update View", variant="primary")
                
                def generate_3d_centered(distance, h_angle, v_angle):
                    """Generate 3D map centered on selected object - OPTIMIZED."""
                    data = load_star_database()
                    
                    # FAST MODE: Only 1000 stars for quick rendering
                    if len(data) > 1000:
                        import random
                        indices = sorted(random.sample(range(len(data)), 1000))
                        data_sample = data.iloc[indices].copy()
                    else:
                        data_sample = data.copy()
                    
                    fig = create_3d_sky_map(data_sample, f"🌌 3D Sky Map - {len(data):,} Total ({len(data_sample):,} shown)")
                    
                    if selected_object is not None:
                        try:
                            obj = selected_object
                            
                            # Highlight selected object
                            fig.add_trace(go.Scatter3d(
                                x=[obj['ra']],
                                y=[obj['dec']],
                                z=[obj['distance_ly']],
                                mode='markers',
                                marker=dict(size=10, color='yellow', symbol='diamond', line=dict(width=2, color='red')),
                                name=f'Selected: {obj["source_id"]}',
                                hovertext=f"ID: {obj['source_id']}<br>RA: {obj['ra']:.2f}°<br>Dec: {obj['dec']:.2f}°<br>Distance: {obj['distance_ly']:.1f} ly"
                            ))
                            
                            # Set camera to look at object
                            import numpy as np
                            h_rad = np.radians(h_angle)
                            v_rad = np.radians(v_angle)
                            
                            eye_x = obj['ra'] + distance * np.cos(h_rad) * np.cos(v_rad)
                            eye_y = obj['dec'] + distance * np.sin(h_rad) * np.cos(v_rad)
                            eye_z = obj['distance_ly'] + distance * np.sin(v_rad)
                            
                            fig.update_layout(
                                scene=dict(
                                    camera=dict(
                                        eye=dict(x=eye_x, y=eye_y, z=eye_z),
                                        center=dict(x=obj['ra'], y=obj['dec'], z=obj['distance_ly'])
                                    )
                                )
                            )
                        except Exception as e:
                            print(f"Error centering on object: {e}")
                    
                    return fig
                
                skymap_3d_btn.click(
                    fn=generate_3d_sky_map,
                    inputs=None,
                    outputs=skymap_3d_plot
                )
                
                center_on_obj_btn.click(
                    fn=lambda: generate_3d_centered(100, 45, 30),
                    inputs=None,
                    outputs=skymap_3d_plot
                )
                
                update_view_btn.click(
                    fn=generate_3d_centered,
                    inputs=[nav_distance, nav_h_angle, nav_v_angle],
                    outputs=skymap_3d_plot
                )
            
            # Sub-Tab: Constellation View
            with gr.Tab("Constellation View"):
                gr.Markdown("**Focus on specific region**")
                
                with gr.Row():
                    with gr.Column():
                        const_ra = gr.Number(value=266.4, label="Center RA (deg)")
                        const_dec = gr.Number(value=-29.0, label="Center Dec (deg)")
                        const_fov = gr.Number(value=30, label="Field of View (deg)")
                        const_btn = gr.Button("🔍 Generate Region", variant="primary")
                    
                    with gr.Column():
                        const_plot = gr.Plot(label="Region View")
                
                const_btn.click(
                    fn=generate_constellation_map,
                    inputs=[const_ra, const_dec, const_fov],
                    outputs=const_plot
                )
    
    # TAB 3: SSZ Physics
    with gr.Tab("🔬 SSZ Physics"):
        gr.Markdown("### Segmented Spacetime Physics Visualizations")
        
        # Object selector for physics
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("**Select an object to visualize in physics plots:**")
                
                physics_search = gr.Textbox(
                    label="Quick Search",
                    placeholder="Sag A*, Betelgeuse, M31, or coordinates",
                    scale=2
                )
                physics_search_btn = gr.Button("🔍 Find", size="sm")
                
            with gr.Column(scale=3):
                physics_object_dropdown = gr.Dropdown(
                    label="Select Object",
                    choices=[],
                    interactive=True
                )
                physics_select_btn = gr.Button("✅ Select for Physics Plots", variant="primary")
                
            with gr.Column(scale=2):
                physics_object_status = gr.Markdown("**No object selected**")
        
        def physics_quick_search(term):
            results, status = search_object(term)
            if results:
                return gr.Dropdown(choices=results, value=results[0][1]), status
            return gr.Dropdown(choices=[]), status
        
        def physics_select_object(idx):
            if idx is None:
                return "❌ No object selected"
            info = select_object(idx)
            return info
        
        physics_search_btn.click(
            fn=physics_quick_search,
            inputs=physics_search,
            outputs=[physics_object_dropdown, physics_object_status]
        )
        
        physics_select_btn.click(
            fn=physics_select_object,
            inputs=physics_object_dropdown,
            outputs=physics_object_status
        )
        
        gr.Markdown("---")
        
        with gr.Tabs():
            # Sub-Tab: g₁/g₂ Domains
            with gr.Tab("g₁/g₂ Domains"):
                gr.Markdown("**Segment density Ξ(r) - Theory + Real Objects**")
                
                with gr.Row():
                    domains_show_objects = gr.Checkbox(label="Show real objects", value=True)
                    domains_btn = gr.Button("📊 Plot Domains", variant="primary", size="lg")
                
                domains_plot = gr.Image(label="SSZ Domains", type="filepath")
                
                def plot_domains_with_objects(show_objects):
                    """Generate domains plot with current selected object - OBJECT SPECIFIC."""
                    global selected_object_name, selected_object
                    
                    # Use stored object name or default
                    object_name = selected_object_name if selected_object_name else "Sgr A*"
                    
                    # Get object parameters
                    if selected_object is not None:
                        mass_msun = float(selected_object.get('mass_msun', 1.0))
                        distance_pc = float(selected_object.get('distance_pc', 1000.0))
                    else:
                        mass_msun = 1.0
                        distance_pc = 1000.0
                    
                    # Generate OBJECT-SPECIFIC plot
                    from ssz_physics_plots_matplotlib import create_domains_plot_png
                    print(f"[DEBUG] Generating Domains plot for: {object_name} (M={mass_msun:.2f} M☉, d={distance_pc:.1f} pc)")
                    
                    return create_domains_plot_png(object_name=object_name, mass_msun=mass_msun, distance_pc=distance_pc)
                
                domains_btn.click(
                    fn=plot_domains_with_objects,
                    inputs=domains_show_objects,
                    outputs=domains_plot
                )
            
            # Sub-Tab: Time Dilation
            with gr.Tab("Time Dilation"):
                gr.Markdown("**Compare SSZ vs GR time dilation**")
                dilation_btn = gr.Button("⏱️ Plot Time Dilation", variant="primary", size="lg")
                dilation_plot = gr.Image(label="Time Dilation", type="filepath")
                
                def plot_dilation_dynamic():
                    """Generate time dilation plot - OBJECT SPECIFIC."""
                    global selected_object_name, selected_object
                    
                    object_name = selected_object_name if selected_object_name else "Sgr A*"
                    
                    # Get object parameters
                    if selected_object is not None:
                        mass_msun = float(selected_object.get('mass_msun', 1.0))
                        distance_pc = float(selected_object.get('distance_pc', 1000.0))
                    else:
                        mass_msun = 1.0
                        distance_pc = 1000.0
                    
                    from ssz_physics_plots_matplotlib import create_time_dilation_png
                    print(f"[DEBUG] Generating Time Dilation plot for: {object_name} (M={mass_msun:.2f} M☉)")
                    
                    return create_time_dilation_png(object_name=object_name, mass_msun=mass_msun, distance_pc=distance_pc)
                
                dilation_btn.click(
                    fn=plot_dilation_dynamic,
                    inputs=None,
                    outputs=dilation_plot
                )
            
            # Sub-Tab: Radial Stretch
            with gr.Tab("Radial Stretch"):
                gr.Markdown("**Radial stretch factor showing domain structure**")
                stretch_btn = gr.Button("📏 Plot Radial Stretch", variant="primary", size="lg")
                stretch_plot = gr.Image(label="Radial Stretch", type="filepath")
                
                def plot_stretch_dynamic():
                    """Generate radial stretch plot - OBJECT SPECIFIC."""
                    global selected_object_name, selected_object
                    
                    object_name = selected_object_name if selected_object_name else "Sgr A*"
                    
                    # Get object parameters
                    if selected_object is not None:
                        mass_msun = float(selected_object.get('mass_msun', 1.0))
                        distance_pc = float(selected_object.get('distance_pc', 1000.0))
                    else:
                        mass_msun = 1.0
                        distance_pc = 1000.0
                    
                    from ssz_physics_plots_matplotlib import create_radial_stretch_png
                    print(f"[DEBUG] Generating Radial Stretch plot for: {object_name} (M={mass_msun:.2f} M☉)")
                    
                    return create_radial_stretch_png(object_name=object_name, mass_msun=mass_msun, distance_pc=distance_pc)
                
                stretch_btn.click(
                    fn=plot_stretch_dynamic,
                    inputs=None,
                    outputs=stretch_plot
                )
            
            # Sub-Tab: Combined Analysis
            with gr.Tab("Combined Analysis"):
                gr.Markdown("**Complete SSZ physics overview - 4 key metrics**")
                combined_btn = gr.Button("🔬 Plot Combined Analysis", variant="primary", size="lg")
                combined_plot = gr.Image(label="Combined SSZ Analysis", type="filepath")
                
                def plot_combined_dynamic():
                    """Generate combined analysis plot - OBJECT SPECIFIC."""
                    global selected_object_name, selected_object
                    
                    object_name = selected_object_name if selected_object_name else "Sgr A*"
                    
                    # Get object parameters
                    if selected_object is not None:
                        mass_msun = float(selected_object.get('mass_msun', 1.0))
                        distance_pc = float(selected_object.get('distance_pc', 1000.0))
                    else:
                        mass_msun = 1.0
                        distance_pc = 1000.0
                    
                    from ssz_physics_plots_matplotlib import create_combined_analysis_png
                    print(f"[DEBUG] Generating Combined Analysis for: {object_name} (M={mass_msun:.2f} M☉)")
                    
                    return create_combined_analysis_png(object_name=object_name, mass_msun=mass_msun, distance_pc=distance_pc)
                
                combined_btn.click(
                    fn=plot_combined_dynamic,
                    inputs=None,
                    outputs=combined_plot
                )
    
    # TAB 4: Info
    with gr.Tab("ℹ️ Info"):
        gr.Markdown(f"""
        ### SSZ Explorer - Complete Edition
        
        **Database:** {len(db):,} GAIA DR3 stars loaded
        
        **Features:**
        - 📊 **Visualizations:** 2D/3D Sky Maps, Constellation View
        - 🔬 **SSZ Physics:** g₁/g₂ Domains, Time Dilation, Radial Stretch, Combined Analysis
        - 📥 **Export:** Data available in database file
        
        **SSZ Physics:**
        - Golden ratio (φ) = 1.618...
        - Segment Density: Ξ(r) = 1 - exp(-φ·r/r_s)
        - Time Dilation: D_SSZ = 1/(1 + Ξ)
        
        **Database Location:**
        ```
        ssz_explorer/ssz_data/star_database_50k.csv
        ```
        
        ---
        
        ### 📚 Documentation
        
        - [GitHub Repository](https://github.com/error-wtf/Segmented-Spacetime-Starmaps)
        - [Quick Reference](QUICK_REFERENCE.md)
        - [Complete Roadmap](COMPLETE_ROADMAP.md)
        """)

    
    gr.Markdown("""
    ---
    **© 2025 Carmen Wrede, Lino Casu** | ACSL v1.4
    """)


# ============================================================================
# LAUNCH
# ============================================================================

def launch_app(share=False, port=9500):
    """Launch the complete SSZ Explorer."""
    print(f"[3/3] Launching on Port {port}...")
    print(f"      Open browser: http://localhost:{port}")
    print("="*80)
    app.launch(share=share, server_name="0.0.0.0", server_port=port)


if __name__ == "__main__":
    launch_app(share=False, port=9500)
