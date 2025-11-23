"""
MINIMAL Gradio Test - Single Plot Only
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
from ssz_physics_plots import create_time_dilation_comparison

print("="*80)
print("MINIMAL GRADIO TEST - SINGLE PLOT")
print("="*80)
print(f"Gradio version: {gr.__version__}")
print()

# Create minimal app with ONLY time dilation plot
with gr.Blocks(title="Minimal Test") as app:
    gr.Markdown("# 🧪 Minimal Test: Time Dilation Plot")
    gr.Markdown("If this works, main app has integration problem. If not, Gradio problem.")
    
    with gr.Row():
        btn = gr.Button("⏱️ Generate Plot", variant="primary", size="lg")
    
    with gr.Row():
        plot_output = gr.Plot(label="Time Dilation")
    
    def create_plot():
        print("[MINIMAL TEST] Button clicked!")
        fig = create_time_dilation_comparison(mass_msun=4.3e6, object_name="Test")
        print(f"[MINIMAL TEST] Figure created with {len(fig.data)} traces")
        print(f"[MINIMAL TEST] Returning figure...")
        return fig
    
    btn.click(
        fn=create_plot,
        inputs=None,
        outputs=plot_output
    )

print("[INFO] Starting minimal test app on port 7862...")
print("[INFO] Open browser: http://localhost:7862")
print("[INFO] Click button - you should see 2 lines (GR=blue, SSZ=red) + green point!")
print("="*80)

try:
    app.launch(share=False, server_name="0.0.0.0", server_port=7862, debug=True)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
