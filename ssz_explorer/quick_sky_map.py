#!/usr/bin/env python3
"""Quick Sky Map Demo - Guaranteed to work!"""

import gradio as gr
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def create_test_sky_map():
    """Create a test sky map with fake stars"""
    # Generate test stars around Galactic Center
    np.random.seed(42)
    n_stars = 200
    
    ra = np.random.uniform(260, 273, n_stars)
    dec = np.random.uniform(-35, -23, n_stars)
    magnitude = np.random.uniform(5, 15, n_stars)
    
    # Create plot
    fig = go.Figure()
    
    # Add stars
    fig.add_trace(go.Scattergl(
        x=ra,
        y=dec,
        mode='markers',
        marker=dict(
            size=20 - magnitude,  # Brighter = larger
            color=magnitude,
            colorscale='Viridis',
            colorbar=dict(title='Magnitude'),
            opacity=0.8,
            line=dict(width=0.5, color='white')
        ),
        text=[f"RA: {r:.2f}°<br>Dec: {d:.2f}°<br>Mag: {m:.1f}" 
              for r, d, m in zip(ra, dec, magnitude)],
        hovertemplate='%{text}<extra></extra>',
        name='Stars'
    ))
    
    # Layout
    fig.update_layout(
        title="Sky Map - Galactic Center Region (Test Data)",
        xaxis=dict(
            title="Right Ascension (degrees)",
            gridcolor='rgba(100,100,100,0.3)',
            showgrid=True
        ),
        yaxis=dict(
            title="Declination (degrees)",
            gridcolor='rgba(100,100,100,0.3)',
            showgrid=True,
            scaleanchor="x",
            scaleratio=1
        ),
        plot_bgcolor='#0a0a1f',
        paper_bgcolor='#000000',
        font=dict(color='white'),
        height=700,
        hovermode='closest'
    )
    
    return fig


def create_3d_test_map():
    """Create 3D celestial sphere"""
    np.random.seed(42)
    n_stars = 200
    
    # Spherical coordinates
    ra_rad = np.random.uniform(np.radians(260), np.radians(273), n_stars)
    dec_rad = np.random.uniform(np.radians(-35), np.radians(-23), n_stars)
    r = np.random.uniform(50, 500, n_stars)
    
    # Convert to Cartesian
    x = r * np.cos(dec_rad) * np.cos(ra_rad)
    y = r * np.cos(dec_rad) * np.sin(ra_rad)
    z = r * np.sin(dec_rad)
    
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            size=3,
            color=r,
            colorscale='Plasma',
            colorbar=dict(title='Distance (pc)'),
            opacity=0.8
        ),
        hovertemplate='Distance: %{marker.color:.0f} pc<extra></extra>'
    )])
    
    fig.update_layout(
        title="3D Celestial Sphere (Test Data)",
        scene=dict(
            xaxis=dict(title='X (pc)', backgroundcolor='black', gridcolor='gray'),
            yaxis=dict(title='Y (pc)', backgroundcolor='black', gridcolor='gray'),
            zaxis=dict(title='Z (pc)', backgroundcolor='black', gridcolor='gray'),
            bgcolor='black'
        ),
        paper_bgcolor='black',
        font=dict(color='white'),
        height=700
    )
    
    return fig


# Create Gradio interface
with gr.Blocks(title="Sky Map Demo", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🌟 Sky Map Demo
    
    **Test der interaktiven Sternenkarte!**
    
    - 200 Test-Sterne um Galactic Center
    - Interaktiv (zoom/pan/hover)
    - 2D und 3D Ansichten
    """)
    
    with gr.Row():
        btn_2d = gr.Button("Generate 2D Sky Map", variant="primary", size="lg")
        btn_3d = gr.Button("Generate 3D Map", variant="secondary", size="lg")
    
    sky_plot = gr.Plot(label="Sky Map")
    
    btn_2d.click(fn=create_test_sky_map, outputs=sky_plot)
    btn_3d.click(fn=create_3d_test_map, outputs=sky_plot)
    
    gr.Markdown("""
    ### Features:
    - **Zoom:** Mausrad oder Box-Zoom
    - **Pan:** Klicken & Ziehen
    - **Hover:** Maus über Stern für Details
    - **Reset:** Doppelklick
    """)

if __name__ == "__main__":
    print("="*80)
    print("SKY MAP DEMO - PORT 7863")
    print("="*80)
    print("Starting...")
    app.launch(server_port=7863, server_name="127.0.0.1", share=False)
