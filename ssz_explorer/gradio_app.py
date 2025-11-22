#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Explorer - Gradio Edition

Interactive web interface using Gradio for easy Colab deployment.

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import gradio as gr
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_manager import DataManager
from comparison_visualizations import ComparisonVisualizer, SSZOnlyVisualizer
from ssz_data_exporter import SSZDataExporter

# Initialize
dm = DataManager()
comp_viz = ComparisonVisualizer()
ssz_viz = SSZOnlyVisualizer()
exporter = SSZDataExporter()

# Golden ratio
PHI = (1 + np.sqrt(5)) / 2


def load_gaia_data(num_stars, use_real_data):
    """Load GAIA data (real or synthetic)."""
    try:
        stars = dm.load_catalog(
            catalog='gaia',
            level='preview',
            limit=int(num_stars),
            use_real_data=use_real_data
        )
        
        data_source = stars.attrs.get('data_source', 'unknown')
        is_real = stars.attrs.get('real_data', False)
        
        status = f"✅ Loaded {len(stars)} stars\n"
        status += f"Data source: {data_source}\n"
        status += f"Real data: {is_real}"
        
        # Create summary DataFrame
        summary = stars[['source_id', 'ra', 'dec', 'distance_pc', 'mass_msun', 
                        'spectral_type', 'Xi', 'D_ssz']].head(10)
        
        return status, summary
        
    except Exception as e:
        return f"❌ Error: {e}", pd.DataFrame()


def create_comparison_plot(mass, plot_type):
    """Create SSZ vs GR comparison plots."""
    try:
        mass_val = float(mass)
        
        if plot_type == "Time Dilation":
            fig = comp_viz.create_time_dilation_comparison(mass=mass_val)
        elif plot_type == "Velocity Comparison":
            fig = comp_viz.create_velocity_comparison(mass=mass_val)
        elif plot_type == "Orbital Period":
            fig = comp_viz.create_orbital_period_comparison(mass=mass_val)
        else:
            fig = comp_viz.create_time_dilation_comparison(mass=mass_val)
        
        return fig
        
    except Exception as e:
        # Return empty figure with error message
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {e}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="red")
        )
        return fig


def create_ssz_plot(mass, plot_type):
    """Create pure SSZ plots."""
    try:
        mass_val = float(mass)
        
        if plot_type == "Radial Profiles":
            fig = ssz_viz.create_ssz_radial_profiles(mass=mass_val)
        elif plot_type == "3D Segment Field":
            fig = ssz_viz.create_ssz_3d_field(mass=mass_val)
        elif plot_type == "Time Dilation Map":
            fig = ssz_viz.create_ssz_time_dilation_map(mass=mass_val)
        else:
            fig = ssz_viz.create_ssz_radial_profiles(mass=mass_val)
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {e}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="red")
        )
        return fig


def query_galactic_center(radius):
    """Query stars near Sgr A*."""
    try:
        stars = dm.cone_search(
            ra=266.4,
            dec=-29.0,
            radius=float(radius) if radius else 10.0,  # INCREASED: Default 10° instead of 5°
            level='preview'
        )
        
        if len(stars) == 0:
            return "No stars found in region (synthetic data may not include this area)", pd.DataFrame()
        
        status = f"✅ Found {len(stars)} stars near Sgr A*\n"
        status += f"RA range: {stars['ra'].min():.2f} - {stars['ra'].max():.2f}\n"
        status += f"DEC range: {stars['dec'].min():.2f} - {stars['dec'].max():.2f}"
        
        # Show brightest stars
        result = stars.nsmallest(10, 'phot_g_mean_mag')[
            ['source_id', 'ra', 'dec', 'phot_g_mean_mag', 'distance_pc', 'Xi']
        ]
        
        return status, result
        
    except Exception as e:
        return f"❌ Error: {e}", pd.DataFrame()


def export_data(stars_df, format_type):
    """Export data to file."""
    try:
        if format_type == "CSV":
            filename = "ssz_export.csv"
            exporter.export_objects_csv(stars_df, filename)
        elif format_type == "JSON":
            filename = "ssz_export.json"
            exporter.export_objects_json(stars_df, filename)
        else:
            filename = "ssz_export.md"
            exporter.export_objects_markdown(stars_df, filename)
        
        return f"✅ Data exported to {filename}"
        
    except Exception as e:
        return f"❌ Export failed: {e}"


def get_statistics():
    """Get current dataset statistics."""
    try:
        stats = dm.get_statistics()
        
        result = "📊 Dataset Statistics\n"
        result += "=" * 50 + "\n"
        for key, value in stats.items():
            result += f"{key}: {value}\n"
        result += "=" * 50
        
        return result
        
    except Exception as e:
        return f"❌ Error: {e}"


# Create Gradio Interface
with gr.Blocks(title="SSZ Explorer", theme=gr.themes.Soft()) as app:
    
    gr.Markdown("""
    # 🌌 SSZ Explorer
    
    **Interactive 3D Visualization of Segmented Spacetime Physics with Real GAIA DR3 Data**
    
    Explore the universe with SSZ (Segmented Spacetime) physics! 
    Query real stars from GAIA DR3, visualize SSZ vs GR predictions, and export data.
    
    ---
    """)
    
    # Tab 1: Load Data
    with gr.Tab("📊 Load GAIA Data"):
        gr.Markdown("### Query Real Stars from GAIA DR3")
        
        with gr.Row():
            with gr.Column():
                num_stars = gr.Slider(
                    minimum=10,
                    maximum=1000,
                    value=100,
                    step=10,
                    label="Number of Stars"
                )
                use_real = gr.Checkbox(
                    label="Use Real GAIA Data (may be slower)",
                    value=True
                )
                load_btn = gr.Button("🚀 Load Data", variant="primary")
            
            with gr.Column():
                load_status = gr.Textbox(
                    label="Status",
                    lines=3,
                    interactive=False
                )
        
        data_table = gr.Dataframe(
            label="Loaded Stars (first 10)",
            interactive=False
        )
        
        load_btn.click(
            fn=load_gaia_data,
            inputs=[num_stars, use_real],
            outputs=[load_status, data_table]
        )
    
    # Tab 2: SSZ vs GR Comparison
    with gr.Tab("⚖️ SSZ vs GR Comparison"):
        gr.Markdown("### Compare Segmented Spacetime with General Relativity")
        
        with gr.Row():
            with gr.Column():
                comp_mass = gr.Slider(
                    minimum=0.1,
                    maximum=100,
                    value=1.0,
                    step=0.1,
                    label="Stellar Mass (M☉)"
                )
                comp_plot_type = gr.Radio(
                    choices=["Time Dilation", "Velocity Comparison", "Orbital Period"],
                    value="Time Dilation",
                    label="Plot Type"
                )
                comp_btn = gr.Button("📊 Generate Plot", variant="primary")
        
        comp_plot = gr.Plot(label="Comparison Plot")
        
        comp_btn.click(
            fn=create_comparison_plot,
            inputs=[comp_mass, comp_plot_type],
            outputs=comp_plot
        )
        
        gr.Markdown("""
        **Physics Notes:**
        - **SSZ**: Uses golden ratio (φ) in spacetime geometry
        - **GR**: Standard General Relativity predictions
        - Differences most visible near Schwarzschild radius
        """)
    
    # Tab 3: Pure SSZ Visualization
    with gr.Tab("🔬 SSZ Physics"):
        gr.Markdown("### Pure SSZ Physics Visualization")
        
        with gr.Row():
            with gr.Column():
                ssz_mass = gr.Slider(
                    minimum=0.1,
                    maximum=100,
                    value=1.0,
                    step=0.1,
                    label="Stellar Mass (M☉)"
                )
                ssz_plot_type = gr.Radio(
                    choices=["Radial Profiles", "3D Segment Field", "Time Dilation Map"],
                    value="Radial Profiles",
                    label="Visualization Type"
                )
                ssz_btn = gr.Button("🔬 Generate Plot", variant="primary")
        
        ssz_plot = gr.Plot(label="SSZ Plot")
        
        ssz_btn.click(
            fn=create_ssz_plot,
            inputs=[ssz_mass, ssz_plot_type],
            outputs=ssz_plot
        )
        
        gr.Markdown("""
        **SSZ Formulas:**
        - Segment Density: Ξ(r) = 1 - exp(-φ·r/r_s)
        - Time Dilation: D_SSZ = 1/(1 + Ξ)
        - Golden Ratio: φ = 1.618...
        """)
    
    # Tab 4: Galactic Center Query
    with gr.Tab("🌟 Galactic Center"):
        gr.Markdown("### Query Stars Near Sgr A*")
        
        with gr.Row():
            with gr.Column():
                gc_radius = gr.Slider(
                    minimum=0.1,
                    maximum=5.0,
                    value=1.0,
                    step=0.1,
                    label="Search Radius (degrees)"
                )
                gc_btn = gr.Button("🔍 Search", variant="primary")
            
            with gr.Column():
                gc_status = gr.Textbox(
                    label="Query Status",
                    lines=3,
                    interactive=False
                )
        
        gc_table = gr.Dataframe(
            label="Brightest Stars Near Sgr A*",
            interactive=False
        )
        
        gc_btn.click(
            fn=query_galactic_center,
            inputs=gc_radius,
            outputs=[gc_status, gc_table]
        )
    
    # Tab 5: Statistics & Info
    with gr.Tab("📈 Statistics"):
        gr.Markdown("### Dataset Statistics")
        
        stats_btn = gr.Button("📊 Get Statistics", variant="primary")
        stats_output = gr.Textbox(
            label="Statistics",
            lines=15,
            interactive=False
        )
        
        stats_btn.click(
            fn=get_statistics,
            inputs=None,
            outputs=stats_output
        )
        
        gr.Markdown("""
        ### 🔬 SSZ Physics Background
        
        **Segmented Spacetime (SSZ)** is an alternative theory of gravity that:
        - Uses the golden ratio (φ) as a fundamental constant
        - Eliminates singularities at event horizons
        - Makes testable predictions different from GR
        - Maintains agreement with GR in weak field limit
        
        **Key Features:**
        - Segment density field Ξ(r) based on φ
        - Modified time dilation near massive objects
        - Finite properties at Schwarzschild radius
        - Observable differences in strong gravitational fields
        """)
    
    gr.Markdown("""
    ---
    
    ### 📚 Documentation
    
    - [GAIA Integration Guide](https://github.com/error-wtf/Segmented-Spacetime-Starmaps/blob/main/Interactive3D_ssz_viewer/GAIA_INTEGRATION.md)
    - [Quick Reference](https://github.com/error-wtf/Segmented-Spacetime-Starmaps/blob/main/Interactive3D_ssz_viewer/QUICK_REFERENCE.md)
    - [GitHub Repository](https://github.com/error-wtf/Segmented-Spacetime-Starmaps)
    
    **© 2025 Carmen Wrede, Lino Casu** | Licensed under ACSL v1.4
    """)


# Launch function
def launch_app(share=False):
    """Launch the Gradio app."""
    app.launch(share=share, server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    # For local use
    launch_app(share=False)
    
    # For Colab, use: launch_app(share=True)
