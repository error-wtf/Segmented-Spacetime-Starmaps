#!/usr/bin/env python3
"""Test if Gradio can display the numpy array"""
import gradio as gr
from ssz_explorer.ssz_physics_plots_matplotlib import create_radial_stretch_png

def test_plot():
    try:
        img = create_radial_stretch_png()
        print(f"Type: {type(img)}")
        print(f"Shape: {img.shape}")
        print(f"Dtype: {img.dtype}")
        return img
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise

with gr.Blocks() as demo:
    gr.Markdown("# Test Radial Stretch")
    btn = gr.Button("Generate Plot")
    img_out = gr.Image(label="Result")
    
    btn.click(fn=test_plot, outputs=img_out)

demo.launch(server_port=9502)
