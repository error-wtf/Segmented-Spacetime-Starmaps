"""
Minimal Gradio Test - Does Plotly work in Gradio?
"""
import os
import sys
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from ssz_physics_plots import create_g1_g2_domain_plot

print("="*80)
print("MINIMAL GRADIO TEST")
print("="*80)
print(f"Gradio version: {gr.__version__}")

# Create minimal app
with gr.Blocks(title="Minimal Test") as app:
    gr.Markdown("# Minimal Gradio + Plotly Test")
    
    with gr.Row():
        btn = gr.Button("🔬 Generate Plot", variant="primary", size="lg")
    
    with gr.Row():
        plot_output = gr.Plot(label="Test Plot")
    
    # Direct function call (no wrapper)
    btn.click(
        fn=create_g1_g2_domain_plot,
        inputs=None,
        outputs=plot_output
    )

print("\n[INFO] Starting minimal test app on port 7861...")
print("[INFO] Open browser: http://localhost:7861")
print("[INFO] Click the button and see if plot appears!")
print("="*80)

app.launch(share=False, server_name="0.0.0.0", server_port=7861)
