#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Skymap Dashboard - Full Interactive Web Application
Phase 3: UI/HUD System with Dash

Interactive3D-style dashboard with interactive controls!

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

from dash import Dash, html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog
from skymap.core import prepare_star_coordinates, prepare_ssz_coordinates
from skymap.effects import apply_glow_effect, create_connection_lines
from skymap.ui import (
    create_control_panel,
    create_info_panel,
    create_stats_panel,
    create_filter_panel,
    create_search_panel,
    format_star_info,
    format_stats
)

# Initialize app
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "SSZ Skymap Dashboard"

# Global data store (will be loaded on startup)
global_stars = None
global_stars_ssz = None

def load_initial_data():
    """Load initial star data."""
    global global_stars, global_stars_ssz
    
    print("Loading initial data...")
    manager = CatalogManager(offline=True)
    
    try:
        stars = manager.fetch_nearby(distance_pc=50, max_stars=500, use_cache=True)
    except:
        stars = manager._get_mock_catalog(500)
    
    stars = prepare_star_coordinates(stars)
    stars_ssz = transform_catalog(stars, show_progress=False)
    stars_ssz = prepare_ssz_coordinates(stars_ssz)
    
    global_stars = stars
    global_stars_ssz = stars_ssz
    
    print(f"Loaded {len(stars)} stars")
    return stars, stars_ssz

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("SSZ Skymap Dashboard", className="text-center text-primary"),
            html.H5("Interactive 3D Star Map with Segmented Spacetime Physics",
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    dbc.Row([
        # Left sidebar - Controls
        dbc.Col([
            create_control_panel(),
            html.Br(),
            create_search_panel(),
            html.Br(),
            create_filter_panel()
        ], width=3),
        
        # Main area - 3D plot
        dbc.Col([
            dcc.Graph(
                id='main-plot',
                style={'height': '70vh'},
                config={'displayModeBar': True}
            ),
            html.Br(),
            dbc.Alert(
                id='status-message',
                children="Ready. Click 'Update View' to refresh.",
                color="info",
                dismissable=True
            )
        ], width=6),
        
        # Right sidebar - Info
        dbc.Col([
            create_info_panel(),
            html.Br(),
            create_stats_panel()
        ], width=3)
    ]),
    
    # Store components (hidden data)
    dcc.Store(id='current-stars-store'),
    dcc.Store(id='filtered-stars-store'),
    
], fluid=True, className="p-4")


@app.callback(
    [Output('main-plot', 'figure'),
     Output('status-message', 'children'),
     Output('stats-total', 'children'),
     Output('stats-visible', 'children'),
     Output('stats-distance', 'children'),
     Output('stats-stretch', 'children'),
     Output('stats-dilation', 'children')],
    [Input('update-button', 'click'),
     Input('filter-button', 'click')],
    [State('distance-slider', 'value'),
     State('stars-slider', 'value'),
     State('glow-mode-dropdown', 'value'),
     State('colorscale-dropdown', 'value'),
     State('effects-checklist', 'value'),
     State('theme-radio', 'value'),
     State('magnitude-slider', 'value')],
    prevent_initial_call=False
)
def update_plot(update_click, filter_click, distance_range, max_stars, 
                glow_mode, colorscale, effects, theme, mag_range):
    """Update main plot based on controls."""
    
    # Load data if not loaded
    if global_stars is None:
        load_initial_data()
    
    stars = global_stars.copy()
    stars_ssz = global_stars_ssz.copy()
    
    # Apply filters
    mask = (stars['distance_pc'] >= distance_range[0]) & (stars['distance_pc'] <= distance_range[1])
    stars = stars[mask].head(max_stars)
    stars_ssz = stars_ssz[mask].head(max_stars)
    
    # Calculate effects
    show_glow = 'glow' in effects
    show_connections = 'connections' in effects
    show_ssz = 'ssz' in effects
    
    if show_glow:
        sizes, opacities = apply_glow_effect(stars_ssz, base_size=5.0, glow_factor=3.0, mode=glow_mode)
    else:
        sizes = np.ones(len(stars_ssz)) * 5.0
    
    connection_traces = []
    if show_connections:
        connection_traces = create_connection_lines(stars, max_distance=5.0, max_connections=3)
    
    # Theme colors
    themes = {
        'space': {'bg': '#000000', 'grid': '#1a1a2e', 'text': '#00ffff'},
        'dark': {'bg': '#0a0a1e', 'grid': '#333366', 'text': 'white'},
        'light': {'bg': '#ffffff', 'grid': '#cccccc', 'text': 'black'}
    }
    colors = themes[theme]
    
    # Create figure
    if show_ssz:
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}]],
            subplot_titles=('Minkowski', 'SSZ'),
            horizontal_spacing=0.05
        )
        
        # Left: Minkowski
        fig.add_trace(go.Scatter3d(
            x=stars['x'], y=stars['y'], z=stars['z'],
            mode='markers',
            marker=dict(size=4, color='cyan', opacity=0.7),
            name='Minkowski',
            hovertemplate='<b>%{text}</b><br>Distance: %{customdata:.2f} pc<extra></extra>',
            text=stars['name'],
            customdata=stars['distance_pc']
        ), row=1, col=1)
        
        # Right: SSZ
        fig.add_trace(go.Scatter3d(
            x=stars_ssz['x_ssz'], y=stars_ssz['y_ssz'], z=stars_ssz['z_ssz'],
            mode='markers',
            marker=dict(
                size=sizes,
                color=stars_ssz['D_ssz'],
                colorscale=colorscale,
                showscale=True,
                opacity=0.9,
                colorbar=dict(title="D_SSZ", x=1.05)
            ),
            name='SSZ',
            hovertemplate='<b>%{text}</b><br>Stretch: %{customdata:.4f}x<extra></extra>',
            text=stars_ssz['name'],
            customdata=stars_ssz['stretch_factor']
        ), row=1, col=2)
        
        # Add connections to SSZ
        for conn in connection_traces[:100]:  # Limit for performance
            fig.add_trace(conn, row=1, col=2)
    else:
        # Single view (Minkowski only)
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(
            x=stars['x'], y=stars['y'], z=stars['z'],
            mode='markers',
            marker=dict(size=5, color='cyan', opacity=0.8),
            name='Stars',
            hovertemplate='<b>%{text}</b><br>Distance: %{customdata:.2f} pc<extra></extra>',
            text=stars['name'],
            customdata=stars['distance_pc']
        ))
    
    # Update layout
    fig.update_layout(
        title=f"SSZ Skymap - {len(stars)} Stars",
        paper_bgcolor=colors['bg'],
        plot_bgcolor=colors['bg'],
        font=dict(color=colors['text']),
        showlegend=False,
        height=700
    )
    
    scene_layout = dict(
        xaxis=dict(title='X [pc]', backgroundcolor=colors['bg'], gridcolor=colors['grid']),
        yaxis=dict(title='Y [pc]', backgroundcolor=colors['bg'], gridcolor=colors['grid']),
        zaxis=dict(title='Z [pc]', backgroundcolor=colors['bg'], gridcolor=colors['grid']),
        bgcolor=colors['bg']
    )
    
    if show_ssz:
        fig.update_scenes(scene_layout, row=1, col=1)
        fig.update_scenes(scene_layout, row=1, col=2)
    else:
        fig.update_scenes(scene_layout)
    
    # Update stats
    stats = format_stats(stars_ssz)
    
    status = f"Updated! Showing {len(stars)} stars in range {distance_range[0]}-{distance_range[1]} pc"
    
    return (
        fig,
        status,
        str(stats['total']),
        str(stats['visible']),
        f"{stats['mean_distance']:.2f} pc",
        f"{stats['mean_stretch']:.6f}x",
        f"{stats['mean_dilation']:.6f}"
    )


@app.callback(
    Output('star-info-content', 'children'),
    Input('main-plot', 'clickData')
)
def display_star_info(click_data):
    """Display info for clicked star."""
    if click_data is None or global_stars_ssz is None:
        return [html.P("Click on a star to see details", className="text-muted text-center")]
    
    try:
        point_index = click_data['points'][0]['pointIndex']
        star_data = global_stars_ssz.iloc[point_index].to_dict()
        return format_star_info(star_data)
    except:
        return [html.P("Error loading star data", className="text-danger")]


@app.callback(
    Output('search-results', 'children'),
    Input('search-button', 'n_clicks'),
    State('star-search-input', 'value')
)
def search_stars(n_clicks, search_term):
    """Search for stars by name."""
    if not n_clicks or not search_term or global_stars is None:
        return []
    
    from skymap.ui import search_stars as search_func
    results = search_func(global_stars, search_term)
    
    if len(results) == 0:
        return [html.P("No results found", className="text-muted")]
    
    items = []
    for idx, row in results.head(10).iterrows():
        items.append(
            dbc.ListGroupItem([
                html.Strong(row['name']),
                html.Br(),
                html.Small(f"Distance: {row['distance_pc']:.2f} pc")
            ])
        )
    
    return [dbc.ListGroup(items)]


if __name__ == '__main__':
    print("="*70)
    print("SSZ SKYMAP DASHBOARD - PHASE 3")
    print("="*70)
    print()
    print("Starting Dash server...")
    print("Open browser to: http://127.0.0.1:8050/")
    print()
    print("Features:")
    print("  - Interactive controls (sliders, dropdowns)")
    print("  - Real-time updates")
    print("  - Star info on click")
    print("  - Search functionality")
    print("  - Statistics panel")
    print()
    print("Press Ctrl+C to stop server")
    print("="*70)
    print()
    
    # Load data before starting
    load_initial_data()
    
    # Run app
    app.run_server(debug=True, port=8050)
