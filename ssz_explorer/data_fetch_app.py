#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Data Fetch Suite - Standalone App
======================================
Enrich GAIA database with AKARI/ESO/ALMA data

© 2025 Carmen Wrede, Lino Casu
"""

import gradio as gr
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Import fetcher
try:
    from unified_data_fetcher import (
        enrich_database,
        save_enriched_database,
        get_enrichment_stats
    )
    FETCH_AVAILABLE = True
except:
    FETCH_AVAILABLE = False

# Check if in Colab
IN_COLAB = 'google.colab' in sys.modules

# Load database
DB_PATH = Path(__file__).parent / "ssz_data" / "star_database_500k.csv"
if not DB_PATH.exists():
    DB_PATH = Path(__file__).parent / "ssz_data" / "star_database_50k.csv"

db = pd.read_csv(DB_PATH) if DB_PATH.exists() else pd.DataFrame()

# Region definitions
REGIONS = {
    "galactic_center": {"ra": 266.4, "dec": -29.0, "radius": 5.0, "name": "Galactic Center"},
    "cygnus_x": {"ra": 305.2, "dec": 0.5, "radius": 3.0, "name": "Cygnus X"},
    "orion": {"ra": 83.8, "dec": -5.4, "radius": 2.0, "name": "Orion Nebula"},
    "pleiades": {"ra": 56.75, "dec": 24.12, "radius": 2.0, "name": "Pleiades"},
    "andromeda": {"ra": 10.68, "dec": 41.27, "radius": 1.0, "name": "Andromeda"}
}

# Create app
with gr.Blocks(title="SSZ Data Fetch Suite", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🔄 SSZ Data Fetch Suite")
    gr.Markdown(f"**Database:** {len(db):,} objects | **Fetch from:** AKARI, ESO, ALMA, NED")
    
    with gr.Row():
        with gr.Column():
            fetch_mode = gr.Radio(
                choices=[("All Objects", "all"), ("Specific Region", "region")],
                value="all",
                label="Fetch Mode"
            )
            
            region_selector = gr.Dropdown(
                choices=list(REGIONS.keys()) + ["custom"],
                label="Region",
                visible=False
            )
            
            with gr.Row():
                custom_ra = gr.Number(label="RA", visible=False)
                custom_dec = gr.Number(label="Dec", visible=False)
                custom_radius = gr.Number(label="Radius", visible=False)
            
            fetch_btn = gr.Button("🚀 Start Fetch", variant="primary", size="lg")
            save_btn = gr.Button("💾 Save Database", variant="secondary")
        
        with gr.Column():
            fetch_status = gr.Textbox(label="Status", lines=15, interactive=False)
    
    stats_display = gr.Markdown("**No data fetched yet**")
    
    def toggle_region(mode):
        return gr.update(visible=(mode == "region"))
    
    def toggle_custom(region):
        visible = (region == "custom")
        return gr.update(visible=visible), gr.update(visible=visible), gr.update(visible=visible)
    
    def run_fetch(mode, region, ra, dec, radius):
        global db
        
        if not FETCH_AVAILABLE:
            return "❌ Fetch system not available!"
        
        status = ""
        if mode == "all":
            status += f"Fetching ALL {len(db):,} objects...\n"
            max_objects = len(db)
        else:
            if region == "custom":
                region_name = f"Custom ({ra},{dec})"
            else:
                r_data = REGIONS[region]
                ra, dec, radius = r_data["ra"], r_data["dec"], r_data["radius"]
                region_name = r_data["name"]
            
            dist = np.sqrt((db['ra'] - ra)**2 + (db['dec'] - dec)**2)
            mask = dist <= radius
            max_objects = mask.sum()
            status += f"Fetching region: {region_name}\n"
            status += f"Objects in region: {max_objects}\n"
        
        status += "\n✓ Starting enrichment...\n"
        
        try:
            db = enrich_database(db, max_objects=max_objects)
            stats = get_enrichment_stats(db)
            
            status += f"\n✅ Complete!\n"
            status += f"  Enriched: {stats['enriched_objects']}\n"
            status += f"  Temperature: {stats['with_temperature']}\n"
            status += f"  Spectroscopy: {stats['with_spectroscopy']}\n"
            
            return status
        except Exception as e:
            return status + f"\n❌ Error: {e}"
    
    def save_db():
        output = Path(__file__).parent / "ssz_data" / "star_database_enriched.csv"
        output.parent.mkdir(exist_ok=True)
        
        if save_enriched_database(db, output):
            stats = get_enrichment_stats(db)
            return f"✅ Saved: {output}\nSize: {output.stat().st_size/1024/1024:.1f} MB\nEnriched: {stats['enriched_objects']}"
        return "❌ Save failed!"
    
    def update_stats():
        stats = get_enrichment_stats(db)
        return f"""**Statistics:**
- Total: {stats['total_objects']:,}
- Enriched: {stats['enriched_objects']}
- Temperature: {stats['with_temperature']}
- Spectroscopy: {stats['with_spectroscopy']}
"""
    
    fetch_mode.change(toggle_region, fetch_mode, region_selector)
    region_selector.change(toggle_custom, region_selector, [custom_ra, custom_dec, custom_radius])
    
    fetch_btn.click(
        run_fetch,
        [fetch_mode, region_selector, custom_ra, custom_dec, custom_radius],
        fetch_status
    ).then(update_stats, None, stats_display)
    
    save_btn.click(save_db, None, fetch_status)

if __name__ == "__main__":
    # Auto-enable share for Colab
    share = IN_COLAB or "--share" in sys.argv
    port = 7861  # Different port from main app
    
    print("="*80)
    print("SSZ DATA FETCH SUITE")
    print("="*80)
    print(f"Port: {port}")
    if share:
        print("Share: Generating public link...")
    print("="*80)
    
    app.launch(share=share, server_port=port, server_name="0.0.0.0")
