"""
SIMPLEST possible SSZ plot test
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import plotly.graph_objects as go
import numpy as np

# Simple data
x = np.logspace(-9, 4, 100)  # 10^-9 to 10^4
y = np.full(100, 0.12)  # Constant 0.12

# Create figure
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=x,
    y=y,
    mode='lines+markers',
    name='Test Line',
    line=dict(color='red', width=5),
    marker=dict(size=10)
))

fig.update_layout(
    title='SIMPLE TEST - Should show RED LINE at y=0.12',
    xaxis=dict(title='X (log)', type='log'),
    yaxis=dict(title='Y', range=[0, 0.2]),
    height=600,
    showlegend=True
)

# Save
fig.write_html("test_simple.html")
print("OK Saved to test_simple.html")
print(f"OK X points: {len(x)}")
print(f"OK Y points: {len(y)}")
print(f"OK X range: {x.min():.2e} to {x.max():.2e}")
print(f"OK Y value: {y[0]}")

# Also test in Gradio
import gradio as gr

def plot_test():
    return fig

with gr.Blocks() as demo:
    gr.Markdown("# SIMPLE PLOT TEST")
    btn = gr.Button("Generate Plot")
    plot = gr.Plot()
    btn.click(fn=plot_test, outputs=plot)

demo.launch(server_port=9501, share=False)
