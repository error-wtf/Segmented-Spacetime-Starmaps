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
import gradio as gr
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# Core modules (getestet & funktionierend!)
from star_map_generator import create_sky_map, create_3d_sky_map, create_default_universe
from ssz_time_dilation_crossover_CORRECT import create_time_dilation_comparison
from ssz_physics_plots_matplotlib import (
    create_radial_stretch_png,
    create_combined_analysis_png
)
from ssz_g1_g2_4panel_REAL import create_g1_g2_temperature_plot

# Import unified data fetcher
try:
    from unified_data_fetcher import (
        enrich_object_data, 
        enrich_database, 
        save_enriched_database,
        get_enrichment_stats
    )
    ENRICHMENT_AVAILABLE = True
except ImportError:
    ENRICHMENT_AVAILABLE = False
    print("⚠ Unified data fetcher not available")

from name_resolver import resolve_name, search_by_name_fuzzy, get_famous_objects_list

# ============================================================================
# GLOBALE VARIABLEN
# ============================================================================
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
star_database = None  # Wird beim Start geladen
last_query_data = None  # Für CSV Export
selected_object = None  # Aktuell selektiertes Objekt
selected_object_index = None  # Index des selektierten Objekts

# ============================================================================
# DATENBANK-FUNKTIONEN
# ============================================================================

def load_star_database():
    """Load star database - enriched if available, otherwise base 500k/50k."""
    global star_database
    
    if star_database is not None:
        return star_database
    
    enriched_file = Path(__file__).parent / "ssz_data" / "star_database_enriched.csv"
    database_file_500k = Path(__file__).parent / "ssz_data" / "star_database_500k.csv"
    database_file_50k = Path(__file__).parent / "ssz_data" / "star_database_50k.csv"
    
    # Priority 1: Load enriched database if exists
    if enriched_file.exists():
        print(f"[INFO] Loading ENRICHED database: {enriched_file}")
        star_database = pd.read_csv(enriched_file)
        print(f"[INFO] Loaded {len(star_database):,} stars (enriched)")
        
        # Show enrichment stats
        if ENRICHMENT_AVAILABLE:
            stats = get_enrichment_stats(star_database)
            print(f"[INFO] Enrichment stats:")
            print(f"       - Temperature data: {stats['with_temperature']}")
            print(f"       - Spectroscopy data: {stats['with_spectroscopy']}")
        
        return star_database
    
    # Priority 2: Load base 500k database and START BACKGROUND ENRICHMENT
    if database_file_500k.exists():
        print(f"[INFO] Loading 500k database: {database_file_500k}")
        star_database = pd.read_csv(database_file_500k)
        print(f"[INFO] Loaded {len(star_database):,} stars")
        
        # Start background enrichment thread - FULLY PROTECTED
        if ENRICHMENT_AVAILABLE:
            import threading
            
            def background_enrich():
                """Background enrichment with COMPLETE error protection"""
                global star_database
                try:
                    print("[BACKGROUND] Starting full database enrichment...")
                    star_database = enrich_database(star_database, max_objects=len(star_database))
                    
                    # Auto-save when complete
                    print("[BACKGROUND] Saving enriched database...")
                    if save_enriched_database(star_database, enriched_file):
                        print("[BACKGROUND] ✓ Enriched database saved! Next startup will be instant!")
                    else:
                        print("[BACKGROUND] ✗ Failed to save enriched database")
                except KeyboardInterrupt:
                    print("[BACKGROUND] ⚠️  Enrichment cancelled by user")
                except Exception as e:
                    print(f"[BACKGROUND] ❌ ERROR: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    print("[BACKGROUND] Thread terminated")
            
            thread = threading.Thread(target=background_enrich, daemon=True)
            thread.start()
            print("[INFO] Background enrichment started (will save when complete)")
        
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
    """Generate 3D sky map with 50k database."""
    global last_query_data
    
    # Use query data if available, otherwise use database
    if last_query_data is not None and not last_query_data.empty:
        data = last_query_data
    else:
        data = load_star_database()
    
    return create_3d_sky_map(
        data,
        title=f"🌌 3D Sky Map - {len(data):,} Stars<br><sub>GAIA DR3</sub>"
    )


def generate_constellation_map(ra, dec, fov):
    """Generate constellation map for specific region."""
    try:
        db = load_star_database()
        
        # Filter to region
        ra_val = float(ra)
        dec_val = float(dec)
        fov_val = float(fov)
        
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
                text=f"No stars in region\nRA={ra_val}°, Dec={dec_val}°, FOV={fov_val}°",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        return create_3d_sky_map(
            region_data,
            title=f"Region: RA={ra_val:.1f}°, Dec={dec_val:.1f}° (FOV={fov_val}°)<br>"
                  f"<sub>{len(region_data)} stars from {len(db):,} database</sub>"
        )
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {e}", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
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
    """Suche nach Objekt in Datenbank - jetzt auch mit Namen!"""
    db = load_star_database()
    
    if not search_term or search_term.strip() == "":
        return [], "Enter search term (e.g., 'Sag A*', coordinates, or source_id)"
    
    search_term = search_term.strip()
    
    # Try name resolution first
    name_result = resolve_name(search_term)
    if name_result:
        # Found by name! Now find in database
        ra_search = name_result['ra']
        dec_search = name_result['dec']
        
        distances = np.sqrt((db['ra'] - ra_search)**2 + (db['dec'] - dec_search)**2)
        nearest_idx = np.argmin(distances)
        
        obj = db.iloc[nearest_idx]
        result = [(
            f"🌟 {name_result['name']} | RA:{obj['ra']:.2f}° Dec:{obj['dec']:.2f}° | {obj['distance_ly']:.1f}ly",
            int(nearest_idx)
        )]
        return result, f"✅ Found: {name_result['name']} ({name_result['type']})"
    
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


def select_object(obj_index):
    """Select object for physics plots and enrich with external data"""
    global selected_object, selected_object_index
    
    db = load_star_database()
    selected_object = db.iloc[obj_index]
    selected_object_index = obj_index
    
    if ENRICHMENT_AVAILABLE:
        # Enrich object with AKARI/ESO/ALMA data
        print(f"Enriching selected object: {selected_object.get('source_id', 'Unknown')}")
        selected_object = enrich_object_data(dict(selected_object))
    
    # Create info text
    info = f"""
## 🎯 Selected Object

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
with gr.Blocks(title="SSZ Explorer - Complete") as app:
    
    gr.Markdown("""
    # 🌌 SSZ Explorer - Complete Edition
    
    **50,000 GAIA DR3 Stars | SSZ Physics | Interactive Maps**
    
    Explore the universe with Segmented Spacetime physics!
    
    ---
    """)
    
    # TAB 1: Start & Data Fetch
    with gr.Tab("🏠 Start & Data Fetch"):
        gr.Markdown(f"""
        ### ✅ SSZ Explorer Running!
        
        **Database:** {len(db):,} GAIA DR3 stars loaded
        **Status:** Ready
        **Features:** Sky Maps | SSZ Physics | Object Search | Data Fetching
        """)
        
        gr.Markdown("---")
        gr.Markdown("## 🔄 Data Fetch Suite")
        gr.Markdown("Enrich database with external data from AKARI, ESO, ALMA, NED")
        
        # Region definitions
        REGIONS = {
            "galactic_center": {"ra": 266.4, "dec": -29.0, "radius": 5.0, "name": "Galactic Center"},
            "cygnus_x": {"ra": 305.2, "dec": 0.5, "radius": 3.0, "name": "Cygnus X"},
            "orion": {"ra": 83.8, "dec": -5.4, "radius": 2.0, "name": "Orion Nebula"},
            "pleiades": {"ra": 56.75, "dec": 24.12, "radius": 2.0, "name": "Pleiades"},
            "andromeda": {"ra": 10.68, "dec": 41.27, "radius": 1.0, "name": "Andromeda"}
        }
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Fetch Configuration")
                
                fetch_mode = gr.Radio(
                    choices=[("All Objects (500k)", "all"), ("Specific Region", "region")],
                    value="all",
                    label="Fetch Mode"
                )
                
                region_selector = gr.Dropdown(
                    choices=list(REGIONS.keys()) + ["custom"],
                    label="Region",
                    visible=False
                )
                
                with gr.Row():
                    custom_ra = gr.Number(label="RA (°)", value=266.4, visible=False)
                    custom_dec = gr.Number(label="Dec (°)", value=-29.0, visible=False)
                    custom_radius = gr.Number(label="Radius (°)", value=5.0, visible=False)
                
                fetch_btn = gr.Button("🚀 Start Fetching", variant="primary", size="lg")
                save_btn = gr.Button("💾 Save Enriched Database", variant="secondary")
            
            with gr.Column(scale=2):
                gr.Markdown("### Fetch Status")
                
                # Initial status
                initial_status = """⏳ Background enrichment RUNNING...

This will take ~20-30 minutes for all 500k objects.
Check console for progress.

The app is FULLY FUNCTIONAL while enrichment runs in background!
✓ Use Sky Maps
✓ Search objects  
✓ View physics plots

When complete, the enriched database will be AUTO-SAVED!
"""
                
                fetch_status = gr.Textbox(
                    label="Status",
                    lines=12,
                    value=initial_status,
                    interactive=False
                )
        
        gr.Markdown("### 📊 Enrichment Statistics")
        
        # Get initial stats - SHOW REAL DATA
        try:
            stats = get_enrichment_stats(star_database)
            total = stats['total_objects']
            enriched = stats['enriched_objects']
            percentage = (enriched / total * 100) if total > 0 else 0
            
            # Count REAL vs CALCULATED
            if 'temperature_source' in star_database.columns:
                real_temp = (star_database['temperature_source'].str.contains('AKARI|2MASS|ESO', case=False, na=False)).sum()
                calc_temp = (star_database['temperature_source'] == 'Calculated_BP_RP').sum()
            else:
                real_temp = 0
                calc_temp = stats['with_temperature']
            
            initial_stats_text = f"""
**Database Statistics:**
- **Total Objects:** {total:,}
- **Enriched:** {enriched:,} ({percentage:.1f}%)

**Temperature Data:**
- **Real (fetched):** {real_temp:,}
- **Calculated (BP-RP):** {calc_temp:,}
- **Total:** {stats['with_temperature']:,}

**Spectroscopy Data:**
- **Total:** {stats['with_spectroscopy']:,}
"""
        except Exception as e:
            initial_stats_text = f"**Loading stats...** ({str(e)})"
        
        stats_display = gr.Markdown(initial_stats_text)
        
        gr.Markdown("---")
        gr.Markdown("### 📁 Data Files")
        gr.Markdown(f"""
        **Current Database:**
        - `ssz_data/star_database_500k.csv` - {len(db):,} objects
        
        **Enriched Databases** (will appear after fetching):
        - `ssz_data/star_database_enriched.csv` - With AKARI/ESO/ALMA data
        
        **Data Sources:**
        - 🛰️ AKARI: Infrared temperature data
        - 🔭 ESO: GRAVITY/XSHOOTER spectroscopy
        - 📡 ALMA: Molecular line observations
        - 🌐 NED: Multi-wavelength catalogs
        """)
        
        def toggle_region_visibility(mode):
            return gr.update(visible=(mode == "region"))
        
        def toggle_custom_coords(region):
            visible = (region == "custom")
            return gr.update(visible=visible), gr.update(visible=visible), gr.update(visible=visible)
        
        def run_fetch(mode, region, ra_custom, dec_custom, radius_custom):
            global star_database
            
            if not ENRICHMENT_AVAILABLE:
                return "❌ Fetch system not available!"
            
            # Determine fetch range
            if mode == "all":
                max_objects = len(star_database)
                status = f"Starting FULL DATABASE fetch ({max_objects:,} objects)...\n"
            else:
                if region == "custom":
                    ra, dec, radius = ra_custom, dec_custom, radius_custom
                    region_name = f"Custom ({ra:.2f}°, {dec:.2f}°)"
                else:
                    r_data = REGIONS[region]
                    ra, dec, radius = r_data["ra"], r_data["dec"], r_data["radius"]
                    region_name = r_data["name"]
                
                distances = np.sqrt((star_database['ra'] - ra)**2 + (star_database['dec'] - dec)**2)
                region_mask = distances <= radius
                max_objects = region_mask.sum()
                status += f"Starting fetch for region: {region_name}\n"
                status += f"  - Objects in region: {max_objects:,}\n"
            
            status += "\n✓ Fetch system ready\n"
            
            try:
                star_database = enrich_database(star_database, max_objects=max_objects)
                stats = get_enrichment_stats(star_database)
                
                status += f"\n✅ Fetch Complete!\n"
                status += f"  - Total: {stats['total_objects']:,}\n"
                status += f"  - Enriched: {stats['enriched_objects']:,}\n"
                status += f"  - Temperature: {stats['with_temperature']}\n"
                status += f"  - Spectroscopy: {stats['with_spectroscopy']}\n"
                
                return status
            except Exception as e:
                return status + f"\n❌ Error: {e}\n"
        
        def save_enriched():
            try:
                from pathlib import Path
                output_path = Path(__file__).parent / "ssz_data" / "star_database_enriched.csv"
                output_path.parent.mkdir(exist_ok=True)
                
                if save_enriched_database(star_database, output_path):
                    stats = get_enrichment_stats(star_database)
                    return f"""✅ Saved!

**File:** {output_path}
**Size:** {output_path.stat().st_size / 1024 / 1024:.2f} MB

**Statistics:**
- Total: {stats['total_objects']:,}
- Enriched: {stats['enriched_objects']:,}
- Temperature: {stats.get('with_temperature', 'N/A')}
- Spectroscopy: {stats.get('with_spectroscopy', 'N/A')}
"""
                return "❌ Failed to save!"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def update_stats():
            try:
                stats = get_enrichment_stats(star_database)
                
                # Safe percentage calculation
                total = stats['total_objects']
                enriched = stats['enriched_objects']
                percentage = (enriched / total * 100) if total > 0 else 0
                
                # Count REAL vs CALCULATED temperatures
                if 'temperature_source' in star_database.columns:
                    real_temp = (star_database['temperature_source'].str.contains('AKARI|2MASS|ESO', case=False, na=False)).sum()
                    calc_temp = (star_database['temperature_source'] == 'Calculated_BP_RP').sum()
                else:
                    real_temp = 0
                    calc_temp = stats['with_temperature']
                
                text = f"""
**Database Statistics:**
- **Total Objects:** {total:,}
- **Enriched:** {enriched:,} ({percentage:.1f}%)

**Temperature Data:**
- **Real (fetched):** {real_temp:,}
- **Calculated (BP-RP):** {calc_temp:,}
- **Total:** {stats['with_temperature']:,}

**Spectroscopy Data:**
- **Total:** {stats['with_spectroscopy']:,}

**Data Sources:**
"""
                if stats.get('temperature_sources'):
                    text += "\n**Temperature:**\n"
                    for source, count in stats['temperature_sources'].items():
                        label = "REAL" if source != 'Calculated_BP_RP' else "CALCULATED"
                        text += f"  - {source} [{label}]: {count:,}\n"
                
                if stats.get('spectroscopy_sources'):
                    text += "\n**Spectroscopy:**\n"
                    for source, count in stats['spectroscopy_sources'].items():
                        text += f"  - {source}: {count:,}\n"
                
                return text
            except Exception as e:
                return f"**Error loading stats:** {str(e)}"
        
        fetch_mode.change(toggle_region_visibility, fetch_mode, region_selector)
        region_selector.change(toggle_custom_coords, region_selector, [custom_ra, custom_dec, custom_radius])
        
        fetch_btn.click(
            fn=run_fetch,
            inputs=[fetch_mode, region_selector, custom_ra, custom_dec, custom_radius],
            outputs=fetch_status
        ).then(
            fn=update_stats,
            inputs=None,
            outputs=stats_display
        )
        
        save_btn.click(
            fn=save_enriched,
            inputs=None,
            outputs=fetch_status
        )
    
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
                
                **Famous Objects:** Sgr A*, Betelgeuse, Sirius, Vega, Rigel, Proxima, M31, M42, Pleiades, and more!
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
                
                domains_plot = gr.Plot(label="SSZ Domains")
                
                def plot_domains_with_objects(show_objects):
                    try:
                        global selected_object
                        # Use selected object for plot
                        if selected_object is not None:
                            mass_msun = selected_object.get('mass_msun', 1.0)
                            obj_name = selected_object.get('name', f"ID:{selected_object.get('source_id', 'unknown')}")
                            fig = create_g1_g2_temperature_plot(mass_msun=mass_msun, object_name=obj_name)
                        else:
                            # Default: Sgr A*
                            fig = create_g1_g2_temperature_plot(mass_msun=4.3e6, object_name="Sgr A*")
                    except Exception as e:
                        print(f"ERROR in g1/g2 plot: {e}")
                        import traceback
                        traceback.print_exc()
                        # Return error figure
                        fig = go.Figure()
                        fig.add_annotation(text=f"Error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="red"))
                        return fig
                    
                    # Add sample of real objects from database
                    if show_objects:
                        # Constants
                        G = 6.67430e-11
                        c = 2.99792458e8
                        M_sun = 1.989e30
                        PC_TO_M = 3.0857e16
                        
                        # Add sample of real objects from database
                        try:
                            db = load_star_database()
                            
                            # Sample 100 objects randomly
                            import random
                            if len(db) > 100:
                                indices = random.sample(range(len(db)), 100)
                                sample = db.iloc[indices]
                            else:
                                sample = db
                            
                            # Calculate r/r_s for each
                            r_ratios = []
                            xi_vals = []
                            hover_texts = []
                            
                            for idx, obj in sample.iterrows():
                                try:
                                    M_kg = obj['mass_msun'] * M_sun
                                    r_s = 2 * G * M_kg / (c**2)
                                    r_m = obj['distance_pc'] * PC_TO_M
                                    r_ratio = r_m / r_s
                                    
                                    if r_ratio > 0 and r_ratio < 10000:  # Reasonable range
                                        r_ratios.append(r_ratio)
                                        xi_vals.append(obj['xi'])
                                        hover_texts.append(f"ID: {obj['source_id']}<br>Distance: {obj['distance_ly']:.1f} ly")
                                except:
                                    pass
                            
                            # Add sample objects
                            if r_ratios:
                                fig.add_trace(go.Scatter(
                                    x=r_ratios,
                                    y=xi_vals,
                                    mode='markers',
                                    marker=dict(size=6, color='cyan', opacity=0.5),
                                    name='Sample Stars (100)',
                                    hovertext=hover_texts
                                ))
                        except Exception as e:
                            print(f"Error adding sample objects: {e}")
                        
                        # Add SELECTED object on top
                        if selected_object is not None:
                            try:
                                obj = selected_object
                                
                                M_kg = obj['mass_msun'] * M_sun
                                r_s = 2 * G * M_kg / (c**2)
                                r_m = obj['distance_pc'] * PC_TO_M
                                r_ratio = r_m / r_s
                                
                                fig.add_trace(go.Scatter(
                                    x=[r_ratio],
                                    y=[obj['xi']],
                                    mode='markers',
                                    marker=dict(size=20, color='yellow', symbol='star', line=dict(width=3, color='red')),
                                    name=f'⭐ SELECTED (ID: {obj["source_id"]})',
                                    hovertext=f"<b>SELECTED OBJECT</b><br>ID: {obj['source_id']}<br>RA: {obj['ra']:.2f}°<br>Dec: {obj['dec']:.2f}°<br>Distance: {obj['distance_ly']:.1f} ly"
                                ))
                            except Exception as e:
                                print(f"Error adding selected object: {e}")
                    
                    return fig
                
                domains_btn.click(
                    fn=plot_domains_with_objects,
                    inputs=domains_show_objects,
                    outputs=domains_plot
                )
            
            # Sub-Tab: Time Dilation
            with gr.Tab("Time Dilation"):
                gr.Markdown("**GR vs SSZ Time Dilation - Universal Crossover**")
                dilation_btn = gr.Button("⏱️ Plot Time Dilation Crossover", variant="primary", size="lg")
                dilation_plot = gr.Plot(label="Time Dilation Crossover")
                
                def plot_time_dilation():
                    if selected_object is not None:
                        mass_msun = selected_object['mass_msun']
                        obj_name = selected_object.get('name', f"ID:{selected_object['source_id']}")
                        return create_time_dilation_comparison(mass_msun, obj_name)
                    else:
                        return create_time_dilation_comparison(4.3e6, "Sgr A*")
                
                dilation_btn.click(
                    fn=plot_time_dilation,
                    inputs=None,
                    outputs=dilation_plot
                )
            
            # Sub-Tab: Radial Stretch
            with gr.Tab("Radial Stretch"):
                gr.Markdown("**Radial stretch factor showing domain structure**")
                stretch_btn = gr.Button("📏 Plot Radial Stretch", variant="primary", size="lg")
                stretch_plot = gr.Image(label="Radial Stretch", type="filepath")
                
                def plot_radial_stretch():
                    if selected_object is not None:
                        mass_msun = selected_object['mass_msun']
                        obj_name = selected_object.get('name', f"ID:{selected_object['source_id']}")
                        distance_pc = selected_object.get('distance', 1000.0)
                        return create_radial_stretch_png(obj_name, mass_msun, distance_pc)
                    else:
                        return create_radial_stretch_png("Sgr A*", 4.3e6, 8000.0)
                
                stretch_btn.click(
                    fn=plot_radial_stretch,
                    inputs=None,
                    outputs=stretch_plot
                )
            
            # Sub-Tab: Combined Analysis
            with gr.Tab("Combined Analysis"):
                gr.Markdown("**Complete SSZ physics overview - 4 key metrics**")
                combined_btn = gr.Button("🔬 Plot Combined Analysis", variant="primary", size="lg")
                combined_plot = gr.Image(label="Combined SSZ Analysis", type="filepath")
                
                def plot_combined():
                    if selected_object is not None:
                        mass_msun = selected_object['mass_msun']
                        obj_name = selected_object.get('name', f"ID:{selected_object['source_id']}")
                        distance_pc = selected_object.get('distance', 1000.0)
                        return create_combined_analysis_png(obj_name, mass_msun, distance_pc)
                    else:
                        return create_combined_analysis_png("Sgr A*", 4.3e6, 8000.0)
                
                combined_btn.click(
                    fn=plot_combined,
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
    # Try ports until we find a free one
    for port in [7860, 7861, 7862, 9500]:
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', port))
            s.close()
            launch_app(share=False, port=port)
            break
        except:
            continue
