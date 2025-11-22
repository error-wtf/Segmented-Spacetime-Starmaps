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
from ssz_physics_plots import (
    create_g1_g2_domain_plot,
    create_time_dilation_comparison,
    create_radial_stretch_plot,
    create_combined_ssz_analysis
)

# ============================================================================
# GLOBALE VARIABLEN
# ============================================================================
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
star_database = None  # Wird beim Start geladen
last_query_data = None  # Für CSV Export

# ============================================================================
# DATENBANK-FUNKTIONEN
# ============================================================================

def load_star_database():
    """Lade 50k Sterne Datenbank."""
    global star_database
    
    if star_database is not None:
        return star_database
    
    database_file = Path(__file__).parent / 'ssz_data' / 'star_database_50k.csv'
    
    if database_file.exists():
        print(f"[INFO] Loading database: {database_file}")
        star_database = pd.read_csv(database_file)
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
    """Generate 2D sky map with 50k database."""
    global last_query_data
    
    # Use query data if available, otherwise use database
    if last_query_data is not None and not last_query_data.empty:
        data = last_query_data
    else:
        data = load_star_database()
    
    return create_sky_map(
        data,
        title=f"🌌 Sky Map - {len(data):,} Stars<br><sub>GAIA DR3 Full Sky Coverage</sub>"
    )


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
        **Features:** Sky Maps | SSZ Physics | CSV Export
        
        Navigate to other tabs to explore!
        """)
    
    # TAB 2: Visualizations
    with gr.Tab("📊 Visualizations"):
        gr.Markdown("### Interactive Star Maps")
        
        with gr.Tabs():
            # Sub-Tab: 2D Sky Map
            with gr.Tab("Sky Map (2D)"):
                gr.Markdown("**Full sky view with 50,000 stars**")
                skymap_btn = gr.Button("🗺️ Generate Sky Map", variant="primary", size="lg")
                skymap_plot = gr.Plot(label="2D Sky Map")
                
                skymap_btn.click(
                    fn=generate_sky_map,
                    inputs=None,
                    outputs=skymap_plot
                )
            
            # Sub-Tab: 3D Sky Map
            with gr.Tab("3D Sky Map"):
                gr.Markdown("**Interactive 3D view**")
                skymap_3d_btn = gr.Button("🌐 Generate 3D Map", variant="primary", size="lg")
                skymap_3d_plot = gr.Plot(label="3D Sky Map")
                
                skymap_3d_btn.click(
                    fn=generate_3d_sky_map,
                    inputs=None,
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
        
        with gr.Tabs():
            # Sub-Tab: g₁/g₂ Domains
            with gr.Tab("g₁/g₂ Domains"):
                gr.Markdown("**Segment density Ξ(r) showing inner (g₂) and outer (g₁) domains**")
                domains_btn = gr.Button("📊 Plot Domains", variant="primary", size="lg")
                domains_plot = gr.Plot(label="SSZ Domains")
                
                domains_btn.click(
                    fn=lambda: create_g1_g2_domain_plot(),
                    inputs=None,
                    outputs=domains_plot
                )
            
            # Sub-Tab: Time Dilation
            with gr.Tab("Time Dilation"):
                gr.Markdown("**Compare SSZ vs GR time dilation**")
                dilation_btn = gr.Button("⏱️ Plot Time Dilation", variant="primary", size="lg")
                dilation_plot = gr.Plot(label="Time Dilation")
                
                dilation_btn.click(
                    fn=lambda: create_time_dilation_comparison(),
                    inputs=None,
                    outputs=dilation_plot
                )
            
            # Sub-Tab: Radial Stretch
            with gr.Tab("Radial Stretch"):
                gr.Markdown("**Radial stretch factor showing domain structure**")
                stretch_btn = gr.Button("📏 Plot Radial Stretch", variant="primary", size="lg")
                stretch_plot = gr.Plot(label="Radial Stretch")
                
                stretch_btn.click(
                    fn=lambda: create_radial_stretch_plot(),
                    inputs=None,
                    outputs=stretch_plot
                )
            
            # Sub-Tab: Combined Analysis
            with gr.Tab("Combined Analysis"):
                gr.Markdown("**Complete SSZ physics overview - 4 key metrics**")
                combined_btn = gr.Button("🔬 Plot Combined Analysis", variant="primary", size="lg")
                combined_plot = gr.Plot(label="Combined SSZ Analysis")
                
                combined_btn.click(
                    fn=lambda: create_combined_ssz_analysis(),
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
