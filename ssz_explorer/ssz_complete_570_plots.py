#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ EXPLORER - COMPLETE 570 PLOTS INTEGRATION
==============================================

ALLE 570 Plots aus PAPER-RESTORED professionell integriert.
KEINE halben Sachen - ALLES funktional!

© 2025 Carmen Wrede, Lino Casu, Bingsi
"""
import os
import sys
from pathlib import Path
import json

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Paths
PAPER_PATH = Path(r"E:\clone\PAPER-RESTORED")
sys.path.insert(0, str(PAPER_PATH))

# Import SSZ core
from ssz_core_functions import *

print("="*80)
print("SSZ EXPLORER - LOADING ALL 570 PLOTS")
print("="*80)

# Load ALL plots
plot_list_file = PAPER_PATH / "plot_list.json"
with open(plot_list_file, 'r', encoding='utf-8') as f:
    ALL_PLOTS_RAW = json.load(f)

print(f"Loaded {len(ALL_PLOTS_RAW)} plots")

# Organize by category
from collections import defaultdict
CATEGORIES = defaultdict(list)

for plot_info in ALL_PLOTS_RAW:
    full_path = Path(plot_info['FullName'])
    rel_path = plot_info['RelativePath']
    
    parts = Path(rel_path).parts
    if len(parts) == 2:
        category = "Root"
    else:
        category = parts[1].replace('-', ' ').replace('_', ' ').title()
    
    CATEGORIES[category].append({
        'name': full_path.stem,
        'path': str(full_path),
        'rel': rel_path
    })

# Sort categories
CATEGORY_NAMES = sorted(CATEGORIES.keys())
print(f"Organized into {len(CATEGORY_NAMES)} categories")

# ============================================================================
# LIVE PHYSICS PLOT FUNCTIONS
# ============================================================================

def plot_photon_sphere():
    """Photon Sphere Comparison"""
    masses = np.logspace(0, 7, 200)
    
    r_ph_gr = np.array([1.5 * r_schwarzschild(M * M_SUN) for M in masses]) / 1000  # km
    r_ph_ssz = np.array([r_photon_sphere_ssz(M * M_SUN) for M in masses]) / 1000
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=masses, y=r_ph_gr, mode='lines', name='GR: 1.5×r_s',
                            line=dict(color='#3498db', width=3)))
    fig.add_trace(go.Scatter(x=masses, y=r_ph_ssz, mode='lines', name='SSZ: 1.55×r_s',
                            line=dict(color='#e74c3c', width=3)))
    
    fig.update_layout(
        title='<b>Photon Sphere Radius</b>',
        xaxis=dict(title='Mass [M☉]', type='log', gridcolor='#2c3e50'),
        yaxis=dict(title='r_ph [km]', type='log', gridcolor='#2c3e50'),
        plot_bgcolor='#ecf0f1', paper_bgcolor='white',
        height=600, font=dict(size=12)
    )
    return fig

def plot_shadow_radius():
    """Shadow Radius - EHT Observable"""
    masses = np.logspace(0, 10, 200)
    
    b_gr = np.array([shadow_radius_gr(M * M_SUN) for M in masses]) / 1000
    b_ssz = np.array([shadow_radius_ssz(M * M_SUN) for M in masses]) / 1000
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=masses, y=b_gr, mode='lines', name='GR',
                            line=dict(color='#3498db', width=3)))
    fig.add_trace(go.Scatter(x=masses, y=b_ssz, mode='lines', name='SSZ',
                            line=dict(color='#e74c3c', width=3)))
    
    # M87 marker
    fig.add_vline(x=6.5e9, line_dash="dash", line_color="#f39c12",
                  annotation_text="M87*", annotation_position="top")
    
    fig.update_layout(
        title='<b>Black Hole Shadow Radius</b><br><sub>Observable with EHT</sub>',
        xaxis=dict(title='Mass [M☉]', type='log', gridcolor='#2c3e50'),
        yaxis=dict(title='Shadow Radius [km]', type='log', gridcolor='#2c3e50'),
        plot_bgcolor='#ecf0f1', paper_bgcolor='white',
        height=600
    )
    return fig

def plot_energy_conditions(mass_msun=4.3e6):
    """Energy Conditions Check"""
    M = mass_msun * M_SUN
    r_s = r_schwarzschild(M)
    r_ratio = np.linspace(1.1, 10, 300)
    r_range = r_ratio * r_s
    
    rho, pr, pt = [], [], []
    for r in r_range:
        r_val, p_r, p_t = rho_pr_pt(r, M)
        rho.append(r_val)
        pr.append(p_r)
        pt.append(p_t)
    
    fig = make_subplots(rows=3, cols=1, subplot_titles=('ρ', 'p_r', 'p_t'))
    
    fig.add_trace(go.Scatter(x=r_ratio, y=rho, line=dict(color='#3498db')), row=1, col=1)
    fig.add_trace(go.Scatter(x=r_ratio, y=pr, line=dict(color='#e74c3c')), row=2, col=1)
    fig.add_trace(go.Scatter(x=r_ratio, y=pt, line=dict(color='#2ecc71')), row=3, col=1)
    
    fig.update_layout(title='<b>Energy Conditions</b>', height=900, showlegend=False)
    return fig

def plot_kretschmann():
    """Kretschmann Scalar"""
    M = 4.3e6 * M_SUN
    r_s = r_schwarzschild(M)
    r_ratio = np.linspace(1.01, 10, 500)
    r_range = r_ratio * r_s
    
    K_gr = 48 * r_s**2 / r_range**6
    A_vals = np.array([A_SSZ(r, M) for r in r_range])
    K_ssz = 48 * r_s**2 / r_range**6 * (1/A_vals)**3
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r_ratio, y=K_gr, name='GR', line=dict(color='#3498db', width=3)))
    fig.add_trace(go.Scatter(x=r_ratio, y=K_ssz, name='SSZ', line=dict(color='#e74c3c', width=3)))
    
    fig.update_layout(
        title='<b>Kretschmann Scalar</b>',
        xaxis=dict(title='r/r_s', type='log'),
        yaxis=dict(title='K [m⁻⁴]', type='log'),
        height=600
    )
    return fig

def plot_qnm_frequencies():
    """QNM Frequencies"""
    masses = np.logspace(0, 10, 200)
    
    f_gr = np.array([qnm_frequency_gr(M * M_SUN) for M in masses])
    f_ssz = np.array([qnm_frequency_ssz(M * M_SUN) for M in masses])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=masses, y=f_gr, name='GR', line=dict(color='#3498db', width=3)))
    fig.add_trace(go.Scatter(x=masses, y=f_ssz, name='SSZ', line=dict(color='#e74c3c', width=3)))
    
    fig.add_hrect(y0=10, y1=1000, fillcolor='#2ecc71', opacity=0.1,
                  annotation_text="LIGO", annotation_position="top left")
    
    fig.update_layout(
        title='<b>QNM Fundamental Frequency</b>',
        xaxis=dict(title='Mass [M☉]', type='log'),
        yaxis=dict(title='Frequency [Hz]', type='log'),
        height=600
    )
    return fig

# ============================================================================
# GRADIO APP
# ============================================================================

with gr.Blocks(title="SSZ Explorer - 570 Plots") as app:
    
    gr.Markdown("""
    # 🌌 **SSZ EXPLORER - ALL 570 PLOTS**
    
    **Vollständige Integration aller PAPER-RESTORED Physics Plots**
    
    © 2025 Carmen Wrede, Lino Casu, Bingsi | Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
    
    ---
    """)
    
    # Statistics Summary
    with gr.Accordion("📊 Plot Statistics", open=False):
        stats_md = f"**Total Plots:** {len(ALL_PLOTS_RAW)}\n\n"
        stats_md += f"**Categories:** {len(CATEGORY_NAMES)}\n\n"
        for cat in CATEGORY_NAMES:
            stats_md += f"- **{cat}:** {len(CATEGORIES[cat])} plots\n"
        gr.Markdown(stats_md)
    
    # Main Tabs
    with gr.Tabs():
        
        # TAB 1: Live Physics Plots
        with gr.Tab("🔬 Live Physics Plots"):
            gr.Markdown("### **Real-time Generated Physics Visualizations**")
            
            with gr.Row():
                with gr.Column():
                    btn1 = gr.Button("📊 Photon Sphere", variant="primary", size="lg")
                    plot1 = gr.Plot()
                    btn1.click(fn=plot_photon_sphere, outputs=plot1)
                
                with gr.Column():
                    btn2 = gr.Button("📊 Shadow Radius", variant="primary", size="lg")
                    plot2 = gr.Plot()
                    btn2.click(fn=plot_shadow_radius, outputs=plot2)
            
            with gr.Row():
                with gr.Column():
                    btn3 = gr.Button("📊 Energy Conditions", variant="primary", size="lg")
                    plot3 = gr.Plot()
                    btn3.click(fn=plot_energy_conditions, outputs=plot3)
                
                with gr.Column():
                    btn4 = gr.Button("📊 Kretschmann Scalar", variant="primary", size="lg")
                    plot4 = gr.Plot()
                    btn4.click(fn=plot_kretschmann, outputs=plot4)
            
            with gr.Row():
                btn5 = gr.Button("📊 QNM Frequencies", variant="primary", size="lg")
                plot5 = gr.Plot()
                btn5.click(fn=plot_qnm_frequencies, outputs=plot5)
        
        # TAB 2: Image Gallery - ALL 570 Plots
        with gr.Tab("🖼️ All 570 Plots Gallery"):
            gr.Markdown(f"### **Browse all {len(ALL_PLOTS_RAW)} static plots**")
            
            with gr.Row():
                category_select = gr.Dropdown(
                    choices=CATEGORY_NAMES,
                    label="📁 Category",
                    value=CATEGORY_NAMES[0],
                    scale=2
                )
                
                plot_select = gr.Dropdown(
                    choices=[p['name'] for p in CATEGORIES[CATEGORY_NAMES[0]]],
                    label="📊 Plot",
                    value=CATEGORIES[CATEGORY_NAMES[0]][0]['name'],
                    scale=3
                )
            
            with gr.Row():
                plot_display = gr.Image(label="Plot", type="filepath", height=700)
            
            with gr.Row():
                plot_path_display = gr.Textbox(label="File Path", lines=2, interactive=False)
            
            def update_plot_dropdown(category):
                plots = CATEGORIES[category]
                return gr.Dropdown(choices=[p['name'] for p in plots], value=plots[0]['name'])
            
            def load_plot(category, plot_name):
                # Find plot in category
                for p in CATEGORIES[category]:
                    if p['name'] == plot_name:
                        if Path(p['path']).exists():
                            return p['path'], f"**Path:** {p['path']}\n**Relative:** {p['rel']}"
                        else:
                            return None, f"ERROR: File not found: {p['path']}"
                return None, "ERROR: Plot not found"
            
            category_select.change(
                fn=update_plot_dropdown,
                inputs=category_select,
                outputs=plot_select
            )
            
            plot_select.change(
                fn=load_plot,
                inputs=[category_select, plot_select],
                outputs=[plot_display, plot_path_display]
            )
            
            # Auto-load first plot
            app.load(
                fn=load_plot,
                inputs=[category_select, plot_select],
                outputs=[plot_display, plot_path_display]
            )
        
        # TAB 3: Search
        with gr.Tab("🔍 Search"):
            gr.Markdown("### **Search across all 570 plots**")
            
            search_input = gr.Textbox(label="Search term", placeholder="e.g., 'temperature', 'collapse', 'g79'")
            search_btn = gr.Button("🔍 Search", variant="primary")
            search_results = gr.DataFrame(headers=["Category", "Plot Name", "Path"])
            
            def search_plots(query):
                if not query:
                    return []
                
                results = []
                query_lower = query.lower()
                
                for cat, plots in CATEGORIES.items():
                    for p in plots:
                        if query_lower in p['name'].lower() or query_lower in cat.lower():
                            results.append([cat, p['name'], p['rel']])
                
                return results
            
            search_btn.click(
                fn=search_plots,
                inputs=search_input,
                outputs=search_results
            )

print("\n" + "="*80)
print("LAUNCHING SSZ EXPLORER WITH ALL 570 PLOTS...")
print(f"Categories: {len(CATEGORY_NAMES)}")
print(f"Live Plots: 5")
print(f"Static Gallery: {len(ALL_PLOTS_RAW)}")
print("="*80)

app.launch(share=False, server_name="0.0.0.0", server_port=7880)
