#!/usr/bin/env python3
"""
MINIMAL GRADIO TEST - Physics Plots
Testet ob Matplotlib PNG -> Numpy -> Gradio funktioniert
"""
import gradio as gr
from ssz_explorer.ssz_physics_plots_matplotlib import (
    create_domains_plot_png,
    create_time_dilation_png,
    create_radial_stretch_png,
    create_combined_analysis_png
)

print("="*60)
print("MINIMAL GRADIO TEST - Physics Plots")
print("="*60)

with gr.Blocks(title="Physics Test") as demo:
    gr.Markdown("# 🔬 SSZ Physics - Minimal Test")
    
    with gr.Tabs():
        with gr.Tab("Domains"):
            btn1 = gr.Button("Plot Domains", variant="primary")
            out1 = gr.Image(label="Segment Density")  # KEIN type Parameter!
            btn1.click(fn=create_domains_plot_png, outputs=out1)
        
        with gr.Tab("Time Dilation"):
            btn2 = gr.Button("Plot Time Dilation", variant="primary")
            out2 = gr.Image(label="A(r)")  # KEIN type Parameter!
            btn2.click(fn=create_time_dilation_png, outputs=out2)
        
        with gr.Tab("Radial Stretch"):
            btn3 = gr.Button("Plot Radial Stretch", variant="primary")
            out3 = gr.Image(label="B(r)")  # KEIN type Parameter!
            btn3.click(fn=create_radial_stretch_png, outputs=out3)
        
        with gr.Tab("Combined"):
            btn4 = gr.Button("Plot Combined", variant="primary")
            out4 = gr.Image(label="4-Panel")  # KEIN type Parameter!
            btn4.click(fn=create_combined_analysis_png, outputs=out4)

print("\nStarte Gradio auf Port 9501...")
demo.launch(server_port=9501, share=False)
