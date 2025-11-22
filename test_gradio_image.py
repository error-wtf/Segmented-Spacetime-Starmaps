#!/usr/bin/env python3
# Quick test: Matplotlib → Gradio gr.Image()

import gradio as gr
from ssz_explorer.ssz_physics_plots_matplotlib import create_radial_stretch_png

def test_callback():
    """Test if matplotlib PNG works in Gradio"""
    try:
        img = create_radial_stretch_png()
        print(f"✓ Created image: {img.size}, mode: {img.mode}")
        return img
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

with gr.Blocks() as demo:
    gr.Markdown("# Test: Matplotlib → Gradio")
    
    btn = gr.Button("Generate Plot")
    output = gr.Image(label="Test Plot", type="pil")
    
    btn.click(fn=test_callback, inputs=None, outputs=output)

if __name__ == "__main__":
    demo.launch(server_port=9501, share=False)
