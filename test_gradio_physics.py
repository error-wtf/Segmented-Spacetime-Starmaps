#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Gradio Physics Tab mit neuem g1/g2 Plot
"""
import sys
import os
import io

# UTF-8 Setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, 'ssz_explorer')

import gradio as gr
from ssz_physics_plots import (
    create_g1_g2_domain_plot,
    create_time_dilation_comparison,
    create_radial_stretch_plot
)

print("Erstelle Gradio Interface...")

def get_physics_plot(plot_type):
    """Generate physics plot based on type"""
    if plot_type == "g1_g2_domains":
        return create_g1_g2_domain_plot()
    elif plot_type == "time_dilation":
        return create_time_dilation_comparison()
    elif plot_type == "radial_stretch":
        return create_radial_stretch_plot()
    else:
        return create_g1_g2_domain_plot()

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# SSZ Physics - NEW g1/g2 Plot Test")
    
    with gr.Row():
        plot_selector = gr.Radio(
            choices=["g1_g2_domains", "time_dilation", "radial_stretch"],
            value="g1_g2_domains",
            label="Select Physics Plot"
        )
    
    physics_plot = gr.Plot(label="Physics Visualization")
    
    # Update plot on selection
    plot_selector.change(
        fn=get_physics_plot,
        inputs=[plot_selector],
        outputs=[physics_plot]
    )
    
    # Initial load
    demo.load(
        fn=lambda: create_g1_g2_domain_plot(),
        outputs=[physics_plot]
    )

print("Starte Gradio App auf Port 7861...")
demo.launch(server_port=7861, share=False)
