#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ EXPLORER - DARK EDITION
============================

Fokussierte Auswahl der wichtigsten Physics Plots.
Dark Theme wie PAPER-RESTORED.

© 2025 Carmen Wrede, Lino Casu, Bingsi
"""
import os
import sys
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json

# Paths
PAPER_PATH = Path(r"E:\clone\PAPER-RESTORED")
sys.path.insert(0, str(PAPER_PATH))

from ssz_core_functions import *

# DARK THEME COLORS (wie PAPER-RESTORED)
DARK_BG = '#0a0a1f'        # Plot background (dunkelblau)
DARK_PAPER = '#000010'     # Paper background (fast schwarz)
DARK_GRID = 'rgba(100,100,150,0.3)'
DARK_TEXT = 'white'
COLOR_GR = '#3498db'       # Blau für GR
COLOR_SSZ = '#e74c3c'      # Rot für SSZ
COLOR_ACCENT = '#2ecc71'   # Grün für Highlights

print("="*80)
print("SSZ EXPLORER - DARK EDITION")
print("="*80)

# ============================================================================
# SELEKTIVE PLOT KATEGORIEN (NUR WICHTIGE!)
# ============================================================================

plot_list_file = PAPER_PATH / "plot_list.json"
with open(plot_list_file, 'r', encoding='utf-8') as f:
    ALL_PLOTS = json.load(f)

# Filtern: NUR diese Kategorien
SELECTED_CATEGORIES = {
    'Paper Figures': [],
    'Real Data': [],
    'Sharp Break': [],
    'G79 Cygnus': [],
    'Nested Metrics': [],
    'Comparison': []
}

for plot in ALL_PLOTS:
    rel_path = plot['RelativePath']
    parts = Path(rel_path).parts
    
    if 'paper' in rel_path.lower():
        SELECTED_CATEGORIES['Paper Figures'].append(plot)
    elif 'real-data' in rel_path.lower():
        SELECTED_CATEGORIES['Real Data'].append(plot)
    elif 'sharp-break' in rel_path.lower():
        SELECTED_CATEGORIES['Sharp Break'].append(plot)
    elif 'g79' in rel_path.lower() or 'cygnus' in rel_path.lower():
        SELECTED_CATEGORIES['G79 Cygnus'].append(plot)
    elif 'nested' in rel_path.lower():
        SELECTED_CATEGORIES['Nested Metrics'].append(plot)
    elif 'comparison' in rel_path.lower():
        SELECTED_CATEGORIES['Comparison'].append(plot)

# Remove empty categories
SELECTED_CATEGORIES = {k: v for k, v in SELECTED_CATEGORIES.items() if v}

total_selected = sum(len(v) for v in SELECTED_CATEGORIES.values())
print(f"Selected {total_selected} plots from {len(SELECTED_CATEGORIES)} categories")
print(f"Filtered out {len(ALL_PLOTS) - total_selected} irrelevant plots")

# ============================================================================
# DARK THEME PHYSICS PLOTS
# ============================================================================

def apply_dark_theme(fig, title=""):
    """Apply PAPER-RESTORED dark theme to figure"""
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color=DARK_TEXT)),
        plot_bgcolor=DARK_BG,
        paper_bgcolor=DARK_PAPER,
        font=dict(color=DARK_TEXT, size=12),
        xaxis=dict(gridcolor=DARK_GRID),
        yaxis=dict(gridcolor=DARK_GRID),
    )
    return fig

def plot_domain_structure(mass_msun=4.3e6):
    """g₁/g₂ Domain Structure - Dark Theme"""
    M = mass_msun * M_SUN
    r_s = r_schwarzschild(M)
    
    r_ratio = np.linspace(1.1, 10.0, 200)
    r_m = r_ratio * r_s
    Xi_values = np.array([Xi(r_val, r_s, ALPHA, R_C) for r_val in r_m])
    
    fig = go.Figure()
    
    # Domain plot
    fig.add_trace(go.Scatter(
        x=r_ratio, y=Xi_values * 100,
        mode='lines+markers',
        name='Ξ(r) - Segment Density',
        line=dict(color=COLOR_SSZ, width=3),
        marker=dict(size=6)
    ))
    
    fig = apply_dark_theme(fig, f'<b>SSZ Domain Structure</b><br><sub>M = {mass_msun:.2e} M☉</sub>')
    fig.update_xaxes(title='r / r_s', type='log')
    fig.update_yaxes(title='Ξ(r) × 100')
    fig.update_layout(height=600)
    
    return fig

def plot_photon_sphere():
    """Photon Sphere - Dark Theme"""
    masses = np.logspace(0, 7, 200)
    
    r_ph_gr = np.array([1.5 * r_schwarzschild(M * M_SUN) for M in masses]) / 1000
    r_ph_ssz = np.array([r_photon_sphere_ssz(M * M_SUN) for M in masses]) / 1000
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=masses, y=r_ph_gr, name='GR: 1.5×r_s',
                            line=dict(color=COLOR_GR, width=3)))
    fig.add_trace(go.Scatter(x=masses, y=r_ph_ssz, name='SSZ: 1.55×r_s',
                            line=dict(color=COLOR_SSZ, width=3)))
    
    fig = apply_dark_theme(fig, '<b>Photon Sphere Radius</b>')
    fig.update_xaxes(title='Mass [M☉]', type='log')
    fig.update_yaxes(title='r_ph [km]', type='log')
    fig.update_layout(height=600)
    
    return fig

def plot_shadow_radius():
    """Shadow Radius - Dark Theme"""
    masses = np.logspace(0, 10, 200)
    
    b_gr = np.array([shadow_radius_gr(M * M_SUN) for M in masses]) / 1000
    b_ssz = np.array([shadow_radius_ssz(M * M_SUN) for M in masses]) / 1000
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=masses, y=b_gr, name='GR',
                            line=dict(color=COLOR_GR, width=3)))
    fig.add_trace(go.Scatter(x=masses, y=b_ssz, name='SSZ',
                            line=dict(color=COLOR_SSZ, width=3)))
    
    # M87 marker
    fig.add_vline(x=6.5e9, line_dash="dash", line_color=COLOR_ACCENT,
                  annotation_text="M87*", annotation_position="top",
                  annotation_font_color=DARK_TEXT)
    
    fig = apply_dark_theme(fig, '<b>Black Hole Shadow</b><br><sub>EHT Observable</sub>')
    fig.update_xaxes(title='Mass [M☉]', type='log')
    fig.update_yaxes(title='Shadow Radius [km]', type='log')
    fig.update_layout(height=600)
    
    return fig

def plot_time_dilation():
    """Time Dilation - Dark Theme"""
    mass_msun = 4.3e6
    M = mass_msun * M_SUN
    r_s = r_schwarzschild(M)
    
    r_ratio = np.linspace(1.01, 6.0, 500)
    r_range = r_ratio * r_s
    
    D_gr = np.sqrt(1 - 1.0/r_ratio)
    A_ssz = np.array([A_SSZ(r, M) for r in r_range])
    D_ssz = np.sqrt(np.abs(A_ssz))
    
    # Crossover
    diff = np.abs(D_gr - D_ssz)
    idx = np.argmin(diff)
    r_cross = r_ratio[idx]
    D_cross = D_gr[idx]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r_ratio, y=D_gr, name='GR',
                            line=dict(color=COLOR_GR, width=3)))
    fig.add_trace(go.Scatter(x=r_ratio, y=D_ssz, name='SSZ',
                            line=dict(color=COLOR_SSZ, width=3)))
    fig.add_trace(go.Scatter(x=[r_cross], y=[D_cross], name='Crossover',
                            mode='markers', marker=dict(size=15, color=COLOR_ACCENT)))
    
    fig = apply_dark_theme(fig, '<b>Time Dilation D(r)</b><br><sub>Universal Crossover</sub>')
    fig.update_xaxes(title='r / r_s', range=[np.log10(1.0), np.log10(6.0)], type='log')
    fig.update_yaxes(title='D(r)', range=[0.2, 1.0])
    fig.update_layout(height=600)
    
    return fig

def plot_energy_conditions():
    """Energy Conditions - Dark Theme"""
    M = 4.3e6 * M_SUN
    r_s = r_schwarzschild(M)
    r_ratio = np.linspace(1.1, 10, 300)
    r_range = r_ratio * r_s
    
    rho, pr, pt = [], [], []
    for r in r_range:
        r_val, p_r, p_t = rho_pr_pt(r, M)
        rho.append(r_val)
        pr.append(p_r)
        pt.append(p_t)
    
    fig = make_subplots(rows=3, cols=1, 
                       subplot_titles=('Energy Density ρ', 'Radial Pressure p_r', 'Tangential Pressure p_t'),
                       vertical_spacing=0.12)
    
    fig.add_trace(go.Scatter(x=r_ratio, y=rho, line=dict(color=COLOR_GR, width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=r_ratio, y=pr, line=dict(color=COLOR_SSZ, width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=r_ratio, y=pt, line=dict(color=COLOR_ACCENT, width=2)), row=3, col=1)
    
    fig.update_layout(
        title='<b>Energy Conditions</b><br><sub>WEC, DEC, SEC</sub>',
        plot_bgcolor=DARK_BG,
        paper_bgcolor=DARK_PAPER,
        font=dict(color=DARK_TEXT),
        height=900,
        showlegend=False
    )
    
    for i in range(1, 4):
        fig.update_xaxes(gridcolor=DARK_GRID, row=i, col=1)
        fig.update_yaxes(gridcolor=DARK_GRID, row=i, col=1)
    
    return fig

def plot_kretschmann():
    """Kretschmann Scalar - Dark Theme"""
    M = 4.3e6 * M_SUN
    r_s = r_schwarzschild(M)
    r_ratio = np.linspace(1.01, 10, 500)
    r_range = r_ratio * r_s
    
    K_gr = np.array([kretschmann_gr(r, M) for r in r_range])
    K_ssz = np.array([kretschmann_ssz(r, M) for r in r_range])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r_ratio, y=K_gr, name='GR', line=dict(color=COLOR_GR, width=3)))
    fig.add_trace(go.Scatter(x=r_ratio, y=K_ssz, name='SSZ', line=dict(color=COLOR_SSZ, width=3)))
    
    fig = apply_dark_theme(fig, '<b>Kretschmann Scalar</b><br><sub>Curvature Invariant</sub>')
    fig.update_xaxes(title='r / r_s', type='log')
    fig.update_yaxes(title='K [m⁻⁴]', type='log')
    fig.update_layout(height=600)
    
    return fig

def plot_qnm():
    """QNM Frequencies - Dark Theme"""
    masses = np.logspace(0, 10, 200)
    
    f_gr = np.array([qnm_frequency_gr(M * M_SUN) for M in masses])
    f_ssz = np.array([qnm_frequency_ssz(M * M_SUN) for M in masses])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=masses, y=f_gr, name='GR', line=dict(color=COLOR_GR, width=3)))
    fig.add_trace(go.Scatter(x=masses, y=f_ssz, name='SSZ', line=dict(color=COLOR_SSZ, width=3)))
    
    # LIGO band
    fig.add_hrect(y0=10, y1=1000, fillcolor=COLOR_ACCENT, opacity=0.15,
                  annotation_text="LIGO", annotation_position="top left",
                  annotation_font_color=DARK_TEXT)
    
    fig = apply_dark_theme(fig, '<b>QNM Frequencies</b><br><sub>Quasi-Normal Modes</sub>')
    fig.update_xaxes(title='Mass [M☉]', type='log')
    fig.update_yaxes(title='Frequency [Hz]', type='log')
    fig.update_layout(height=600)
    
    return fig

# ============================================================================
# GRADIO APP - DARK THEME
# ============================================================================

with gr.Blocks(title="SSZ Explorer - Dark") as app:
    
    gr.Markdown("""
    # 🌌 **SSZ EXPLORER - DARK EDITION**
    
    **Selektive Physics Plots | PAPER-RESTORED Dark Theme**
    
    © 2025 Carmen Wrede, Lino Casu, Bingsi
    
    ---
    """)
    
    with gr.Tabs():
        
        # TAB 1: Live Physics
        with gr.Tab("🔬 Physics Plots"):
            
            with gr.Row():
                gr.Markdown(f"""
                ### **{total_selected} Curated Plots**
                **Categories:** {', '.join(SELECTED_CATEGORIES.keys())}
                """)
            
            gr.Markdown("### **Real-Time Generated Plots**")
            
            with gr.Row():
                with gr.Column():
                    btn1 = gr.Button("📊 Domain Structure", variant="primary")
                    plot1 = gr.Plot()
                    btn1.click(fn=plot_domain_structure, outputs=plot1)
                
                with gr.Column():
                    btn2 = gr.Button("📊 Photon Sphere", variant="primary")
                    plot2 = gr.Plot()
                    btn2.click(fn=plot_photon_sphere, outputs=plot2)
            
            with gr.Row():
                with gr.Column():
                    btn3 = gr.Button("📊 Shadow Radius", variant="primary")
                    plot3 = gr.Plot()
                    btn3.click(fn=plot_shadow_radius, outputs=plot3)
                
                with gr.Column():
                    btn4 = gr.Button("📊 Time Dilation", variant="primary")
                    plot4 = gr.Plot()
                    btn4.click(fn=plot_time_dilation, outputs=plot4)
            
            with gr.Row():
                with gr.Column():
                    btn5 = gr.Button("📊 Energy Conditions", variant="primary")
                    plot5 = gr.Plot()
                    btn5.click(fn=plot_energy_conditions, outputs=plot5)
                
                with gr.Column():
                    btn6 = gr.Button("📊 Kretschmann", variant="primary")
                    plot6 = gr.Plot()
                    btn6.click(fn=plot_kretschmann, outputs=plot6)
            
            with gr.Row():
                btn7 = gr.Button("📊 QNM Frequencies", variant="primary")
                plot7 = gr.Plot()
                btn7.click(fn=plot_qnm, outputs=plot7)
        
        # TAB 2: Selected Gallery
        with gr.Tab("🖼️ Selected Gallery"):
            
            gr.Markdown(f"### **{total_selected} Curated Plots from PAPER-RESTORED**")
            
            category_select = gr.Dropdown(
                choices=list(SELECTED_CATEGORIES.keys()),
                label="Category",
                value=list(SELECTED_CATEGORIES.keys())[0]
            )
            
            plot_select = gr.Dropdown(
                choices=[Path(p['FullName']).stem for p in SELECTED_CATEGORIES[list(SELECTED_CATEGORIES.keys())[0]]],
                label="Plot"
            )
            
            plot_img = gr.Image(label="Plot", type="filepath", height=700)
            plot_info = gr.Textbox(label="Info", lines=2)
            
            def update_plots(cat):
                plots = [Path(p['FullName']).stem for p in SELECTED_CATEGORIES[cat]]
                return gr.Dropdown(choices=plots, value=plots[0] if plots else None)
            
            def load_plot(cat, name):
                for p in SELECTED_CATEGORIES[cat]:
                    if Path(p['FullName']).stem == name:
                        path = p['FullName']
                        if Path(path).exists():
                            return path, f"**Category:** {cat}\n**File:** {Path(path).name}"
                        return None, "File not found"
                return None, "Plot not found"
            
            category_select.change(fn=update_plots, inputs=category_select, outputs=plot_select)
            plot_select.change(fn=load_plot, inputs=[category_select, plot_select], outputs=[plot_img, plot_info])
            
            # Auto-load first
            app.load(fn=load_plot, 
                    inputs=[category_select, plot_select],
                    outputs=[plot_img, plot_info])

print("\n" + "="*80)
print("LAUNCHING DARK EDITION...")
print(f"Curated Plots: {total_selected}")
print(f"Categories: {len(SELECTED_CATEGORIES)}")
print("Dark Theme: PAPER-RESTORED Style")
print("="*80)

app.launch(share=False, server_name="0.0.0.0", server_port=7890)
