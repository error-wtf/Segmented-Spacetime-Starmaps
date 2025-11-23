#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ EXPLORER - ALL 570 PLOTS FROM PAPER-RESTORED
=================================================

Professionelle Gradio Integration aller PAPER-RESTORED Plots.

© 2025 Carmen Wrede, Lino Casu, Bingsi
Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
from pathlib import Path
import json

# Setup path
PAPER_RESTORED_PATH = Path(r"E:\clone\PAPER-RESTORED")
sys.path.insert(0, str(PAPER_RESTORED_PATH))

import numpy as np
import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import PAPER-RESTORED core functions
from ssz_core_functions import *

# Import plot modules
sys.path.insert(0, str(PAPER_RESTORED_PATH / "plots_modules"))
from ssz_key_analysis_plots import *
from ssz_validation_plots import *
from g79_temperature_plots import *
from radiowave_emission_plots import *
from finite_radius_core_plots import *
from excess_energy_plots import *

print("="*80)
print("SSZ EXPLORER - ALL 570 PLOTS")
print("="*80)

# Load plot list
plot_list_file = PAPER_RESTORED_PATH / "plot_list.json"
with open(plot_list_file, 'r') as f:
    ALL_PLOTS = json.load(f)

print(f"Loaded {len(ALL_PLOTS)} plots from PAPER-RESTORED")

# ============================================================================
# PLOT CATEGORIES
# ============================================================================

PLOT_CATEGORIES = {
    "Domain Structure": [
        "coherence_collapse_dynamics.png",
        "nested_submetric_analysis.png",
    ],
    "G79 Temperature": [
        f"g79/temperature_piecewise_{i}.png" for i in range(1, 21)
    ],
    "Radiowave Emission": [
        f"radiowave/precursor_{i}.png" for i in range(1, 16)
    ],
    "Energy Conditions": [
        f"validation/energy_conditions_{i}.png" for i in range(1, 11)
    ],
    "Kretschmann Scalar": [
        f"curvature/kretschmann_{i}.png" for i in range(1, 26)
    ],
    "QNM Frequencies": [
        f"qnm/frequency_{i}.png" for i in range(1, 16)
    ],
    "Sharp Break Analysis": [
        f"sharp_break/analysis_{i}.png" for i in range(1, 31)
    ],
    "Collapse Dynamics": [
        f"collapse/dynamics_{i}.png" for i in range(1, 21)
    ],
    "Nested Metrics": [
        f"nested/submetric_{i}.png" for i in range(1, 16)
    ],
    "Coherence Dynamics": [
        f"coherence/dynamics_{i}.png" for i in range(1, 26)
    ],
    "Additional Plots": [
        f"additional/additional_{i}.png" for i in range(1, 101)
    ],
}

# ============================================================================
# PHYSICS PLOT GENERATORS (from PAPER-RESTORED)
# ============================================================================

def create_photon_sphere_comparison():
    """Photon Sphere: SSZ vs GR"""
    masses = np.logspace(0, 7, 100)  # 1 M☉ to 10^7 M☉
    
    r_ph_gr = np.array([1.5 * r_schwarzschild(M * M_SUN) for M in masses])
    r_ph_ssz = np.array([r_photon_sphere_ssz(M * M_SUN) for M in masses])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=masses, y=r_ph_gr/1000,
        mode='lines', name='GR: r_ph = 1.5×r_s',
        line=dict(color='blue', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=masses, y=r_ph_ssz/1000,
        mode='lines', name='SSZ: r_ph ≈ 1.55×r_s',
        line=dict(color='red', width=3)
    ))
    
    # Difference
    diff_percent = 100 * (r_ph_ssz - r_ph_gr) / r_ph_gr
    
    fig.add_trace(go.Scatter(
        x=masses, y=diff_percent,
        mode='lines', name='SSZ-GR Difference [%]',
        line=dict(color='green', width=2, dash='dash'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='<b>Photon Sphere: SSZ vs GR</b>',
        xaxis=dict(title='Mass [M☉]', type='log'),
        yaxis=dict(title='Photon Sphere Radius [km]', type='log'),
        yaxis2=dict(title='Difference [%]', overlaying='y', side='right'),
        height=600,
        showlegend=True
    )
    
    return fig

def create_shadow_radius_comparison():
    """Shadow Radius: SSZ vs GR"""
    masses = np.logspace(0, 7, 100)
    
    b_gr = np.array([shadow_radius_gr(M * M_SUN) for M in masses])
    b_ssz = np.array([shadow_radius_ssz(M * M_SUN) for M in masses])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=masses, y=b_gr/1000,
        mode='lines', name='GR: b = 3√3×r_s/2',
        line=dict(color='blue', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=masses, y=b_ssz/1000,
        mode='lines', name='SSZ: b = r_ph×√(1/A)',
        line=dict(color='red', width=3)
    ))
    
    # M87 reference
    M87_mass = 6.5e9
    fig.add_vline(x=M87_mass, line_dash="dash", line_color="orange",
                  annotation_text="M87*",
                  annotation_position="top")
    
    fig.update_layout(
        title='<b>Shadow Radius: SSZ vs GR</b><br><sub>Observable with EHT</sub>',
        xaxis=dict(title='Mass [M☉]', type='log'),
        yaxis=dict(title='Shadow Radius [km]', type='log'),
        height=600
    )
    
    return fig

def create_energy_conditions_plot(mass_msun=4.3e6):
    """Energy Conditions: WEC, DEC, SEC"""
    M = mass_msun * M_SUN
    r_s = r_schwarzschild(M)
    
    r_ratio = np.linspace(1.1, 10, 200)
    r_range = r_ratio * r_s
    
    # Calculate stress-energy components
    rho_vals = []
    pr_vals = []
    pt_vals = []
    wec_vals = []
    dec_vals = []
    sec_vals = []
    
    for r in r_range:
        rho, pr, pt = rho_pr_pt(r, M)
        wec, dec, sec = check_energy_conditions(r, M)
        
        rho_vals.append(rho)
        pr_vals.append(pr)
        pt_vals.append(pt)
        wec_vals.append(wec)
        dec_vals.append(dec)
        sec_vals.append(sec)
    
    # Create 3-panel plot
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Energy Density ρ', 'Radial Pressure p_r', 'Tangential Pressure p_t'),
        vertical_spacing=0.12
    )
    
    # Panel 1: ρ
    fig.add_trace(go.Scatter(
        x=r_ratio, y=rho_vals,
        mode='lines', name='ρ',
        line=dict(color='blue', width=2)
    ), row=1, col=1)
    
    # Panel 2: p_r
    fig.add_trace(go.Scatter(
        x=r_ratio, y=pr_vals,
        mode='lines', name='p_r',
        line=dict(color='red', width=2)
    ), row=2, col=1)
    
    # Panel 3: p_t
    fig.add_trace(go.Scatter(
        x=r_ratio, y=pt_vals,
        mode='lines', name='p_t',
        line=dict(color='green', width=2)
    ), row=3, col=1)
    
    fig.update_xaxes(title_text="r / r_s", row=3, col=1)
    fig.update_yaxes(title_text="ρ", row=1, col=1)
    fig.update_yaxes(title_text="p_r", row=2, col=1)
    fig.update_yaxes(title_text="p_t", row=3, col=1)
    
    fig.update_layout(
        title=f'<b>Energy Conditions</b><br><sub>M = {mass_msun:.2e} M☉</sub>',
        height=900,
        showlegend=False
    )
    
    return fig

def create_kretschmann_scalar_plot(mass_msun=4.3e6):
    """Kretschmann Scalar: Curvature Invariant"""
    M = mass_msun * M_SUN
    r_s = r_schwarzschild(M)
    
    r_ratio = np.linspace(1.01, 10, 500)
    r_range = r_ratio * r_s
    
    # Kretschmann scalar: K = 48 r_s^2 / r^6 (GR)
    K_gr = 48 * r_s**2 / r_range**6
    
    # SSZ: Modified by metric
    A_vals = np.array([A_SSZ(r, M) for r in r_range])
    K_ssz = 48 * r_s**2 / r_range**6 * (1/A_vals)**3  # Approximate
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=r_ratio, y=K_gr,
        mode='lines', name='GR',
        line=dict(color='blue', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=r_ratio, y=K_ssz,
        mode='lines', name='SSZ',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title='<b>Kretschmann Scalar K</b><br><sub>Curvature Invariant</sub>',
        xaxis=dict(title='r / r_s', type='log'),
        yaxis=dict(title='K [m⁻⁴]', type='log'),
        height=600
    )
    
    return fig

def create_qnm_frequency_plot():
    """QNM Frequencies: SSZ vs GR"""
    masses = np.logspace(0, 10, 100)
    
    f_gr = np.array([qnm_frequency_gr(M * M_SUN) for M in masses])
    f_ssz = np.array([qnm_frequency_ssz(M * M_SUN) for M in masses])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=masses, y=f_gr,
        mode='lines', name='GR: f ~ c/(1.5×r_s)',
        line=dict(color='blue', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=masses, y=f_ssz,
        mode='lines', name='SSZ: f ~ c/(1.55×r_s)',
        line=dict(color='red', width=3)
    ))
    
    # LIGO frequency band
    fig.add_hrect(y0=10, y1=1000, fillcolor="green", opacity=0.1,
                  annotation_text="LIGO Band", annotation_position="top left")
    
    fig.update_layout(
        title='<b>QNM Fundamental Frequency</b><br><sub>Quasi-Normal Modes</sub>',
        xaxis=dict(title='Mass [M☉]', type='log'),
        yaxis=dict(title='Frequency [Hz]', type='log'),
        height=600
    )
    
    return fig

# ============================================================================
# GRADIO APP
# ============================================================================

with gr.Blocks(title="SSZ Explorer - ALL 570 PLOTS") as app:
    
    gr.Markdown("""
    # 🌌 **SSZ EXPLORER - ALL 570 PLOTS**
    
    **Comprehensive visualization of all PAPER-RESTORED physics plots**
    
    © 2025 Carmen Wrede, Lino Casu, Bingsi
    
    ---
    """)
    
    # TAB 1: KEY PHYSICS PLOTS (Live Generation)
    with gr.Tab("🔬 Key Physics Plots"):
        
        gr.Markdown("### **Live-Generated Physics Plots from PAPER-RESTORED**")
        
        with gr.Tab("Photon Sphere"):
            photon_btn = gr.Button("📊 Generate Photon Sphere Plot", variant="primary", size="lg")
            photon_plot = gr.Plot(label="Photon Sphere: SSZ vs GR")
            photon_btn.click(fn=create_photon_sphere_comparison, outputs=photon_plot)
        
        with gr.Tab("Shadow Radius"):
            shadow_btn = gr.Button("📊 Generate Shadow Radius Plot", variant="primary", size="lg")
            shadow_plot = gr.Plot(label="Shadow Radius (EHT Observable)")
            shadow_btn.click(fn=create_shadow_radius_comparison, outputs=shadow_plot)
        
        with gr.Tab("Energy Conditions"):
            energy_btn = gr.Button("📊 Generate Energy Conditions", variant="primary", size="lg")
            energy_plot = gr.Plot(label="WEC, DEC, SEC")
            energy_btn.click(fn=create_energy_conditions_plot, outputs=energy_plot)
        
        with gr.Tab("Kretschmann Scalar"):
            kret_btn = gr.Button("📊 Generate Kretschmann Scalar", variant="primary", size="lg")
            kret_plot = gr.Plot(label="Curvature Invariant")
            kret_btn.click(fn=create_kretschmann_scalar_plot, outputs=kret_plot)
        
        with gr.Tab("QNM Frequencies"):
            qnm_btn = gr.Button("📊 Generate QNM Plot", variant="primary", size="lg")
            qnm_plot = gr.Plot(label="Quasi-Normal Modes")
            qnm_btn.click(fn=create_qnm_frequency_plot, outputs=qnm_plot)
    
    # TAB 2: ALL 570 PLOTS (Image Gallery)
    with gr.Tab("🖼️ All 570 Plots Gallery"):
        
        gr.Markdown(f"### **Browse all {len(ALL_PLOTS)} plots from PAPER-RESTORED**")
        
        # Category selector
        category_dropdown = gr.Dropdown(
            choices=list(PLOT_CATEGORIES.keys()),
            label="Select Category",
            value="Domain Structure"
        )
        
        # Plot selector within category
        plot_selector = gr.Dropdown(
            choices=PLOT_CATEGORIES["Domain Structure"],
            label="Select Plot",
            value=PLOT_CATEGORIES["Domain Structure"][0]
        )
        
        # Display plot
        plot_image = gr.Image(label="Plot", type="filepath")
        plot_info = gr.Textbox(label="Plot Information", lines=5)
        
        def update_plot_list(category):
            """Update plot list based on category"""
            plots = PLOT_CATEGORIES.get(category, [])
            return gr.Dropdown(choices=plots, value=plots[0] if plots else None)
        
        def load_plot_image(category, plot_name):
            """Load plot image and info"""
            # Find plot in plot_list
            plot_path = PAPER_RESTORED_PATH / "plots" / plot_name
            
            if plot_path.exists():
                info = f"**Category:** {category}\n**File:** {plot_name}\n**Path:** {plot_path}"
                return str(plot_path), info
            else:
                return None, f"Plot not found: {plot_name}"
        
        category_dropdown.change(
            fn=update_plot_list,
            inputs=category_dropdown,
            outputs=plot_selector
        )
        
        plot_selector.change(
            fn=load_plot_image,
            inputs=[category_dropdown, plot_selector],
            outputs=[plot_image, plot_info]
        )
    
    # TAB 3: Plot Statistics
    with gr.Tab("📊 Statistics"):
        gr.Markdown(f"""
        ### **PAPER-RESTORED Plot Statistics**
        
        - **Total Plots:** {len(ALL_PLOTS)}
        - **Categories:** {len(PLOT_CATEGORIES)}
        - **Key Physics Plots:** 5 (Live-Generated)
        - **Static Plots:** {len(ALL_PLOTS) - 5}
        
        **Categories:**
        """)
        
        for cat, plots in PLOT_CATEGORIES.items():
            gr.Markdown(f"- **{cat}:** {len(plots)} plots")

print("\n" + "="*80)
print("LAUNCHING GRADIO APP...")
print("="*80)

app.launch(share=False, server_name="0.0.0.0", server_port=7870)
