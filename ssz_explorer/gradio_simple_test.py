#!/usr/bin/env python3
"""Simple test to check if star map works"""

import gradio as gr
import pandas as pd
import numpy as np
from star_map_generator import create_sky_map, create_3d_sky_map

# Create test data
np.random.seed(42)
test_data = pd.DataFrame({
    'ra': np.random.uniform(260, 270, 100),
    'dec': np.random.uniform(-35, -25, 100),
    'magnitude': np.random.uniform(5, 15, 100)
})

def show_sky_map():
    return create_sky_map(test_data, "Test Sky Map")

def show_3d_map():
    return create_3d_sky_map(test_data, "Test 3D Map")

with gr.Blocks(title="Sky Map Test") as app:
    gr.Markdown("# Sky Map Test")
    
    with gr.Row():
        btn1 = gr.Button("Generate 2D Sky Map")
        btn2 = gr.Button("Generate 3D Sky Map")
    
    plot = gr.Plot()
    
    btn1.click(fn=show_sky_map, outputs=plot)
    btn2.click(fn=show_3d_map, outputs=plot)

print("="*80)
print("STARTING TEST APP ON PORT 7862")
print("="*80)

app.launch(server_port=7862, share=False)
