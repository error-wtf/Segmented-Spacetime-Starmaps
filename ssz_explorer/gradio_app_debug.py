#!/usr/bin/env python3
"""Debug version to find where it hangs"""

print("="*80)
print("STARTING DEBUG VERSION")
print("="*80)

print("\n[1/10] Importing gradio...")
import gradio as gr
print("✅ Gradio imported")

print("\n[2/10] Importing pandas/numpy...")
import pandas as pd
import numpy as np
print("✅ pandas/numpy imported")

print("\n[3/10] Importing plotly...")
import plotly.graph_objects as go
print("✅ Plotly imported")

print("\n[4/10] Importing star_map_generator...")
from star_map_generator import create_sky_map, create_3d_sky_map
print("✅ Star map generator imported")

print("\n[5/10] Importing data_manager...")
try:
    from data_manager import DataManager
    dm = DataManager()
    print("✅ DataManager imported")
except Exception as e:
    print(f"⚠️  DataManager: {e}")

print("\n[6/10] Importing exoplanet_fetcher...")
try:
    from exoplanet_fetcher import ExoplanetFetcher
    exo_fetch = ExoplanetFetcher()
    print("✅ Exoplanet fetcher imported")
except Exception as e:
    print(f"⚠️  Exoplanet: {e}")

print("\n[7/10] Importing SSZ modules...")
try:
    from habitable_zone import hz_from_star_params
    from ssz_orbits import calculate_for_planet
    print("✅ SSZ modules imported")
except Exception as e:
    print(f"⚠️  SSZ modules: {e}")

print("\n[8/10] Creating Gradio interface...")
with gr.Blocks(title="SSZ Explorer Debug") as app:
    gr.Markdown("# SSZ Explorer - Debug Version")
    gr.Markdown("If you see this, imports worked!")
    
    with gr.Row():
        btn = gr.Button("Generate Sky Map")
        
    plot = gr.Plot()
    
    def test_map():
        df = pd.DataFrame({
            'ra': [266.4, 267.0, 265.8],
            'dec': [-29.0, -28.5, -29.5],
            'magnitude': [10, 11, 9]
        })
        return create_sky_map(df, "Test")
    
    btn.click(fn=test_map, outputs=plot)

print("✅ Interface created")

print("\n[9/10] Launching app...")
print("Port: 7860")
print("This might take 10-20 seconds...")

try:
    app.launch(
        server_port=7860,
        server_name="127.0.0.1",
        share=False,
        quiet=False,
        show_error=True
    )
    print("✅ App launched!")
except Exception as e:
    print(f"❌ Launch failed: {e}")
    import traceback
    traceback.print_exc()
