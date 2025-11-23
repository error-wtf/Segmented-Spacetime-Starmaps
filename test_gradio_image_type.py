#!/usr/bin/env python3
"""Test what gr.Image() accepts"""
import gradio as gr
import tempfile
import matplotlib.pyplot as plt
import numpy as np

def test_filepath():
    """Test if gr.Image accepts file path"""
    # Create a simple plot
    plt.figure(figsize=(8, 6))
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title("Test Plot")
    
    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(tmp.name)
    plt.close()
    tmp.close()
    
    print(f"Created file: {tmp.name}")
    return tmp.name

def test_pil():
    """Test if gr.Image accepts PIL Image"""
    from PIL import Image
    import io
    
    plt.figure(figsize=(8, 6))
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title("Test Plot PIL")
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    
    print(f"Created PIL Image: {type(img)}")
    return img

with gr.Blocks() as demo:
    gr.Markdown("# Test gr.Image() Input Types")
    
    with gr.Row():
        btn1 = gr.Button("Test File Path")
        btn2 = gr.Button("Test PIL Image")
    
    img1 = gr.Image(label="File Path Result")
    img2 = gr.Image(label="PIL Image Result")
    
    btn1.click(fn=test_filepath, outputs=img1)
    btn2.click(fn=test_pil, outputs=img2)

demo.launch(server_port=9503)
