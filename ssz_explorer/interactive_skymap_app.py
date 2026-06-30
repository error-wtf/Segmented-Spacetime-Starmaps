#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERACTIVE 3D SKYMAP - Full Interactive3D-Style Application

Complete interactive application with:
- 3D Galaxy View
- System Detail View  
- Data Export Mode
- Settings Panel
- Menu Navigation
- Real-time SSZ calculations

© 2025 Carmen Wrede, Lino Casu
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json
from pathlib import Path

# Import our modules
import sys
sys.path.insert(0, str(Path(__file__).parent))
from phase1_galaxy_engine import GalaxyDataLoader, GalaxyRenderer
from phase2_system_details import PlanetGenerator, SystemRenderer
from ssz_data_exporter import SSZDataExporter

# Constants
PHI = (1 + np.sqrt(5)) / 2

# Initialize Dash app
app = dash.Dash(
    __name__,
    title='SSZ Galaxy Viewer',
    suppress_callback_exceptions=True
)

# Color scheme (Interactive3D-inspired)
COLORS = {
    'background': '#0a0e1a',
    'panel': '#1a2332',
    'primary': '#3498db',
    'secondary': '#2c3e50',
    'accent': '#e74c3c',
    'text': '#ecf0f1',
    'border': '#34495e'
}


def get_button_style(active=False):
    """Get button style based on active state."""
    return {
        'padding': '12px 24px',
        'fontSize': '14px',
        'fontWeight': 'bold',
        'border': f'2px solid {COLORS["primary"] if active else COLORS["border"]}',
        'borderRadius': '5px',
        'backgroundColor': COLORS['primary'] if active else COLORS['secondary'],
        'color': COLORS['text'],
        'cursor': 'pointer',
        'transition': 'all 0.3s',
        'boxShadow': f'0 0 10px {COLORS["primary"]}' if active else 'none'
    }


# App layout
app.layout = html.Div([
    # Hidden data stores
    dcc.Store(id='galaxy-data', data=None),
    dcc.Store(id='selected-star', data=None),
    dcc.Store(id='current-mode', data='galaxy'),
    dcc.Store(id='use-real-data', data=True),  # Default: use real GAIA data
    
    # Main container
    html.Div([
        # Header
        html.Div([
            html.H1('SSZ GALAXY VIEWER', style={
                'color': COLORS['primary'],
                'textAlign': 'center',
                'margin': '20px 0',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '36px',
                'textShadow': f'0 0 10px {COLORS["primary"]}'
            }),
            html.P('Segmented Spacetime Transformations - Interactive 3D Skymap', style={
                'color': COLORS['text'],
                'textAlign': 'center',
                'fontSize': '14px',
                'marginTop': '-10px'
            })
        ]),
        
        # Menu Bar
        html.Div([
            html.Button('🌌 GALAXY VIEW', id='btn-galaxy', n_clicks=0, style=get_button_style(True)),
            html.Button('🌟 SYSTEM VIEW', id='btn-system', n_clicks=0, style=get_button_style(False)),
            html.Button('📊 DATA EXPORT', id='btn-export', n_clicks=0, style=get_button_style(False)),
            html.Button('⚖️ COMPARISON', id='btn-comparison', n_clicks=0, style=get_button_style(False)),
            html.Button('🔬 SSZ ONLY', id='btn-ssz-only', n_clicks=0, style=get_button_style(False)),
            html.Button('⚙️ SETTINGS', id='btn-settings', n_clicks=0, style=get_button_style(False)),
            html.Button('❓ HELP', id='btn-help', n_clicks=0, style=get_button_style(False)),
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'gap': '10px',
            'margin': '20px 0',
            'padding': '10px',
            'backgroundColor': COLORS['panel'],
            'borderRadius': '5px'
        }),
        
        # Status bar
        html.Div([
            html.Div([
                html.Div(id='status-text', children='Ready', style={
                    'color': COLORS['text'],
                    'fontSize': '12px'
                }),
                html.Div(id='data-source-indicator', children='Data: Loading...', style={
                    'color': COLORS['primary'],
                    'fontSize': '11px',
                    'marginTop': '3px'
                })
            ]),
            html.Div([
                html.Div(id='star-count', children='Stars: 0', style={
                    'color': COLORS['text'],
                    'fontSize': '12px'
                }),
                html.Div([
                    html.Label('Real GAIA Data:', style={
                        'color': COLORS['text'],
                        'fontSize': '11px',
                        'marginRight': '5px'
                    }),
                    dcc.Checklist(
                        id='real-data-toggle',
                        options=[{'label': '', 'value': 'use_real'}],
                        value=['use_real'],
                        style={'display': 'inline-block'}
                    )
                ], style={'display': 'flex', 'alignItems': 'center', 'marginTop': '3px'})
            ])
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'padding': '10px',
            'backgroundColor': COLORS['panel'],
            'borderRadius': '5px',
            'margin': '10px 0'
        }),
        
        # Main content area
        html.Div(id='content-area', children=[], style={
            'minHeight': '600px',
            'backgroundColor': COLORS['background'],
            'borderRadius': '5px',
            'padding': '20px'
        })
        
    ], style={
        'maxWidth': '1400px',
        'margin': '0 auto',
        'padding': '20px',
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh',
        'fontFamily': 'Arial, sans-serif'
    })
], style={
    'backgroundColor': COLORS['background']
})


# Callback: Mode switching
@app.callback(
    [Output('current-mode', 'data'),
     Output('btn-galaxy', 'style'),
     Output('btn-system', 'style'),
     Output('btn-export', 'style'),
     Output('btn-comparison', 'style'),
     Output('btn-ssz-only', 'style'),
     Output('btn-settings', 'style'),
     Output('btn-help', 'style')],
    [Input('btn-galaxy', 'n_clicks'),
     Input('btn-system', 'n_clicks'),
     Input('btn-export', 'n_clicks'),
     Input('btn-comparison', 'n_clicks'),
     Input('btn-ssz-only', 'n_clicks'),
     Input('btn-settings', 'n_clicks'),
     Input('btn-help', 'n_clicks')]
)
def switch_mode(n1, n2, n3, n4, n5, n6, n7):
    """Switch between different modes."""
    ctx = callback_context
    
    if not ctx.triggered:
        return 'galaxy', get_button_style(True), *[get_button_style(False)] * 6
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    modes = {
        'btn-galaxy': 'galaxy',
        'btn-system': 'system',
        'btn-export': 'export',
        'btn-comparison': 'comparison',
        'btn-ssz-only': 'ssz-only',
        'btn-settings': 'settings',
        'btn-help': 'help'
    }
    
    mode = modes.get(button_id, 'galaxy')
    
    # Update button styles
    styles = [
        get_button_style(button_id == 'btn-galaxy'),
        get_button_style(button_id == 'btn-system'),
        get_button_style(button_id == 'btn-export'),
        get_button_style(button_id == 'btn-comparison'),
        get_button_style(button_id == 'btn-ssz-only'),
        get_button_style(button_id == 'btn-settings'),
        get_button_style(button_id == 'btn-help')
    ]
    
    return mode, *styles


# Callback: Handle real data toggle
@app.callback(
    Output('use-real-data', 'data'),
    Input('real-data-toggle', 'value')
)
def update_real_data_setting(toggle_value):
    """Update real data usage setting."""
    return 'use_real' in (toggle_value or [])


# Callback: Load galaxy data
@app.callback(
    [Output('galaxy-data', 'data'),
     Output('star-count', 'children'),
     Output('data-source-indicator', 'children'),
     Output('data-source-indicator', 'style')],
    [Input('current-mode', 'data'),
     Input('use-real-data', 'data')]
)
def load_galaxy_data(mode, use_real_data):
    """Load galaxy data when app starts or settings change."""
    if mode is None:
        return None, 'Stars: 0', 'Data: Not loaded', {'color': COLORS['text'], 'fontSize': '11px', 'marginTop': '3px'}
    
    try:
        from data_manager import DataManager
        
        # Initialize data manager
        dm = DataManager()
        
        # Load data with real/synthetic toggle
        print(f"Loading data (use_real_data={use_real_data})...")
        stars = dm.load_catalog(
            catalog='gaia',
            level='preview',
            limit=1000,
            use_real_data=use_real_data
        )
        
        # Check data source
        data_source = stars.attrs.get('data_source', 'unknown')
        is_real = stars.attrs.get('real_data', False)
        
        # Set indicator
        if is_real:
            indicator_text = f'Data: GAIA DR3 (Real)'
            indicator_style = {
                'color': '#2ecc71',  # Green for real
                'fontSize': '11px',
                'marginTop': '3px',
                'fontWeight': 'bold'
            }
        else:
            indicator_text = f'Data: Synthetic'
            indicator_style = {
                'color': '#f39c12',  # Orange for synthetic
                'fontSize': '11px',
                'marginTop': '3px'
            }
        
        # Convert to dict for JSON storage
        data = stars.to_dict('records')
        
        return data, f'Stars: {len(stars)}', indicator_text, indicator_style
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, 'Stars: 0', f'Error: {str(e)[:30]}', {'color': COLORS['accent'], 'fontSize': '11px', 'marginTop': '3px'}


# Callback: Render content based on mode
@app.callback(
    [Output('content-area', 'children'),
     Output('status-text', 'children')],
    [Input('current-mode', 'data'),
     Input('galaxy-data', 'data'),
     Input('selected-star', 'data')]
)
def render_content(mode, galaxy_data, selected_star):
    """Render content based on current mode."""
    
    if galaxy_data is None:
        return html.Div('Loading...', style={'color': COLORS['text']}), 'Loading data...'
    
    if mode == 'galaxy':
        return render_galaxy_view(galaxy_data), 'Galaxy View - Click a star to view system'
    
    elif mode == 'system':
        if selected_star is None:
            return render_system_selection(galaxy_data), 'System View - Select a star'
        else:
            return render_system_view(selected_star, galaxy_data), f'System View - {selected_star}'
    
    elif mode == 'export':
        return render_export_view(galaxy_data), 'Data Export - Download SSZ calculations'
    
    elif mode == 'comparison':
        return render_comparison_view(), 'Comparison Mode - SSZ vs GR'
    
    elif mode == 'ssz-only':
        return render_ssz_only_view(), 'SSZ-Only Mode - Pure SSZ Physics'
    
    elif mode == 'settings':
        return render_settings_view(), 'Settings'
    
    elif mode == 'help':
        return render_help_view(), 'Help & Documentation'
    
    return html.Div('Unknown mode', style={'color': COLORS['text']}), 'Error'


def render_galaxy_view(galaxy_data):
    """Render 3D galaxy view."""
    
    # Convert to DataFrame
    df = pd.DataFrame(galaxy_data)
    
    # Create 3D scatter plot
    fig = go.Figure()
    
    # Spectral type colors
    color_map = {
        'O': '#9bb0ff', 'B': '#aabfff', 'A': '#cad7ff',
        'F': '#f8f7ff', 'G': '#fff4ea', 'K': '#ffd2a1', 'M': '#ffcc6f'
    }
    colors = df['spectral_type'].map(color_map)
    
    # Size based on magnitude
    sizes = 10 - df['magnitude'] / 2
    sizes = sizes.clip(2, 20)
    
    # Create hover text
    hover_texts = []
    for _, row in df.iterrows():
        text = (
            f"<b>{row['name']}</b><br>"
            f"Type: {row['spectral_type']}<br>"
            f"Mass: {row['mass_msun']:.2f} M_sun<br>"
            f"Distance: {row['distance_pc']:.1f} pc<br>"
            f"Xi(r): {row['Xi']:.6f}<br>"
            f"<i>Click to view system</i>"
        )
        hover_texts.append(text)
    
    fig.add_trace(go.Scatter3d(
        x=df['x_pc'],
        y=df['y_pc'],
        z=df['z_pc'],
        mode='markers',
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.8,
            line=dict(width=0)
        ),
        text=df['name'],
        hovertext=hover_texts,
        hoverinfo='text',
        name='Stars'
    ))
    
    # Update layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X (pc)', backgroundcolor=COLORS['background'], gridcolor=COLORS['border']),
            yaxis=dict(title='Y (pc)', backgroundcolor=COLORS['background'], gridcolor=COLORS['border']),
            zaxis=dict(title='Z (pc)', backgroundcolor=COLORS['background'], gridcolor=COLORS['border']),
            bgcolor=COLORS['background'],
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        paper_bgcolor=COLORS['background'],
        plot_bgcolor=COLORS['background'],
        font=dict(color=COLORS['text']),
        height=700,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        hovermode='closest'
    )
    
    return html.Div([
        html.H3('3D Galaxy Map', style={'color': COLORS['primary']}),
        dcc.Graph(figure=fig, id='galaxy-graph', style={'height': '700px'}),
        html.Div([
            html.P('Controls:', style={'color': COLORS['text'], 'fontWeight': 'bold'}),
            html.Ul([
                html.Li('Rotate: Click and drag', style={'color': COLORS['text']}),
                html.Li('Zoom: Scroll wheel', style={'color': COLORS['text']}),
                html.Li('Pan: Right-click and drag', style={'color': COLORS['text']}),
                html.Li('Select: Click on a star (System View)', style={'color': COLORS['text']})
            ])
        ], style={'marginTop': '20px'})
    ])


def render_system_selection(galaxy_data):
    """Render system selection interface."""
    df = pd.DataFrame(galaxy_data)
    
    # Top 10 interesting systems
    interesting = df.nlargest(10, 'mass_msun')
    
    return html.Div([
        html.H3('Select a Star System', style={'color': COLORS['primary']}),
        html.P('Choose a star to view detailed system information:', style={'color': COLORS['text']}),
        html.Div([
            html.Div([
                html.Button(
                    f"{row['name']} ({row['spectral_type']}-type, {row['mass_msun']:.2f} M_sun)",
                    id={'type': 'star-select', 'index': i},
                    n_clicks=0,
                    style={
                        'padding': '15px',
                        'margin': '10px',
                        'backgroundColor': COLORS['secondary'],
                        'color': COLORS['text'],
                        'border': f'2px solid {COLORS["primary"]}',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'width': '100%',
                        'textAlign': 'left'
                    }
                )
                for i, (_, row) in enumerate(interesting.iterrows())
            ])
        ])
    ])


def render_system_view(star_name, galaxy_data):
    """Render detailed system view."""
    df = pd.DataFrame(galaxy_data)
    star = df[df['name'] == star_name].iloc[0] if len(df[df['name'] == star_name]) > 0 else df.iloc[0]
    
    # Generate planets
    generator = PlanetGenerator(star['mass_msun'], star['spectral_type'])
    planets = generator.generate_system()
    hz = generator.calculate_habitable_zone()
    
    # Create visualization
    renderer = SystemRenderer(star, planets)
    fig = renderer.render_system()
    
    fig.update_layout(
        paper_bgcolor=COLORS['background'],
        plot_bgcolor=COLORS['background'],
        font=dict(color=COLORS['text'])
    )
    
    return html.Div([
        html.H3(f'System: {star["name"]}', style={'color': COLORS['primary']}),
        html.Div([
            html.Div([
                html.H4('Star Properties', style={'color': COLORS['primary']}),
                html.P(f"Type: {star['spectral_type']}", style={'color': COLORS['text']}),
                html.P(f"Mass: {star['mass_msun']:.2f} M_sun", style={'color': COLORS['text']}),
                html.P(f"Distance: {star['distance_pc']:.1f} pc", style={'color': COLORS['text']})
            ], style={'flex': '1', 'padding': '15px', 'backgroundColor': COLORS['panel'], 'borderRadius': '5px'}),
            html.Div([
                html.H4('System Info', style={'color': COLORS['primary']}),
                html.P(f"Planets: {len(planets)}", style={'color': COLORS['text']}),
                html.P(f"Habitable Zone: {hz['inner_AU']:.2f} - {hz['outer_AU']:.2f} AU", style={'color': COLORS['text']}),
                html.P(f"SSZ Segment Density: {star['Xi']:.6f}", style={'color': COLORS['text']})
            ], style={'flex': '1', 'padding': '15px', 'backgroundColor': COLORS['panel'], 'borderRadius': '5px'})
        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),
        dcc.Graph(figure=fig)
    ])


def render_export_view(galaxy_data):
    """Render data export interface."""
    df = pd.DataFrame(galaxy_data)
    
    return html.Div([
        html.H3('Data Export', style={'color': COLORS['primary']}),
        html.P('Download complete SSZ calculations for all objects:', style={'color': COLORS['text']}),
        html.Div([
            html.Div([
                html.H4('CSV Format', style={'color': COLORS['primary']}),
                html.P('Excel-compatible spreadsheet', style={'color': COLORS['text']}),
                html.P(f'44 columns × {len(df)} rows', style={'color': COLORS['text'], 'fontSize': '12px'}),
                html.Button('Download CSV', id='btn-download-csv', style={
                    'padding': '10px 20px',
                    'backgroundColor': COLORS['primary'],
                    'color': COLORS['text'],
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'marginTop': '10px'
                })
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': COLORS['panel'], 'borderRadius': '5px'}),
            html.Div([
                html.H4('JSON Format', style={'color': COLORS['primary']}),
                html.P('Machine-readable data', style={'color': COLORS['text']}),
                html.P(f'{len(df)} objects with metadata', style={'color': COLORS['text'], 'fontSize': '12px'}),
                html.Button('Download JSON', id='btn-download-json', style={
                    'padding': '10px 20px',
                    'backgroundColor': COLORS['primary'],
                    'color': COLORS['text'],
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'marginTop': '10px'
                })
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': COLORS['panel'], 'borderRadius': '5px'}),
            html.Div([
                html.H4('Markdown Report', style={'color': COLORS['primary']}),
                html.P('Human-readable documentation', style={'color': COLORS['text']}),
                html.P(f'{len(df)} detailed object reports', style={'color': COLORS['text'], 'fontSize': '12px'}),
                html.Button('Download Report', id='btn-download-md', style={
                    'padding': '10px 20px',
                    'backgroundColor': COLORS['primary'],
                    'color': COLORS['text'],
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'marginTop': '10px'
                })
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': COLORS['panel'], 'borderRadius': '5px'})
        ], style={'display': 'flex', 'gap': '20px', 'marginTop': '20px'}),
        html.Div(id='export-status', style={'color': COLORS['text'], 'marginTop': '20px'})
    ])


def render_settings_view():
    """Render settings interface."""
    return html.Div([
        html.H3('Settings', style={'color': COLORS['primary']}),
        html.Div([
            html.H4('Display Options', style={'color': COLORS['primary']}),
            html.Label('Number of stars:', style={'color': COLORS['text']}),
            dcc.Slider(min=100, max=5000, step=100, value=1000, id='slider-stars'),
            html.Label('Max distance (pc):', style={'color': COLORS['text'], 'marginTop': '20px'}),
            dcc.Slider(min=1000, max=10000, step=1000, value=5000, id='slider-distance')
        ], style={'padding': '20px', 'backgroundColor': COLORS['panel'], 'borderRadius': '5px'})
    ])


def render_comparison_view():
    """Render SSZ vs GR comparison interface."""
    from comparison_visualizations import ComparisonVisualizer
    
    viz = ComparisonVisualizer(colors=COLORS)
    
    return html.Div([
        html.H3('SSZ vs GR Comparison', style={'color': COLORS['primary']}),
        html.P('Compare Segmented Spacetime (SSZ) with General Relativity (GR)', 
               style={'color': COLORS['text']}),
        
        # Mass selector
        html.Div([
            html.Label('Select Mass:', style={'color': COLORS['text']}),
            dcc.Dropdown(
                id='comparison-mass',
                options=[
                    {'label': 'Sun (1 M☉)', 'value': 1.0},
                    {'label': 'Massive Star (20 M☉)', 'value': 20.0},
                    {'label': 'Stellar Black Hole (50 M☉)', 'value': 50.0},
                    {'label': 'Intermediate BH (10³ M☉)', 'value': 1000.0},
                    {'label': 'Supermassive BH (10⁶ M☉)', 'value': 1e6},
                ],
                value=1.0,
                style={'width': '300px', 'color': '#000'}
            )
        ], style={'marginBottom': '20px'}),
        
        # Comparison plots
        html.Div([
            dcc.Graph(id='comparison-time-dilation'),
            dcc.Graph(id='comparison-velocity'),
            dcc.Graph(id='comparison-period')
        ])
    ])


def render_ssz_only_view():
    """Render pure SSZ physics interface."""
    from comparison_visualizations import SSZOnlyVisualizer
    
    viz = SSZOnlyVisualizer(colors=COLORS)
    
    return html.Div([
        html.H3('SSZ-Only Visualization', style={'color': COLORS['primary']}),
        html.P('Pure Segmented Spacetime physics without GR comparison', 
               style={'color': COLORS['text']}),
        
        # Mass selector
        html.Div([
            html.Label('Select Mass:', style={'color': COLORS['text']}),
            dcc.Dropdown(
                id='ssz-only-mass',
                options=[
                    {'label': 'Sun (1 M☉)', 'value': 1.0},
                    {'label': 'Massive Star (20 M☉)', 'value': 20.0},
                    {'label': 'Stellar Black Hole (50 M☉)', 'value': 50.0},
                    {'label': 'Intermediate BH (10³ M☉)', 'value': 1000.0},
                    {'label': 'Supermassive BH (10⁶ M☉)', 'value': 1e6},
                ],
                value=1.0,
                style={'width': '300px', 'color': '#000'}
            )
        ], style={'marginBottom': '20px'}),
        
        # SSZ plots
        html.Div([
            dcc.Graph(id='ssz-radial-profiles'),
            dcc.Graph(id='ssz-parameter-space')
        ])
    ])


def render_help_view():
    """Render help interface."""
    return html.Div([
        html.H3('Help & Documentation', style={'color': COLORS['primary']}),
        html.Div([
            html.H4('Navigation', style={'color': COLORS['primary']}),
            html.Ul([
                html.Li('Galaxy View: 3D visualization of all stars', style={'color': COLORS['text']}),
                html.Li('System View: Detailed planetary system information', style={'color': COLORS['text']}),
                html.Li('Data Export: Download SSZ calculations', style={'color': COLORS['text']}),
                html.Li('Settings: Adjust display parameters', style={'color': COLORS['text']})
            ]),
            html.H4('Controls', style={'color': COLORS['primary'], 'marginTop': '20px'}),
            html.Ul([
                html.Li('3D View: Click and drag to rotate', style={'color': COLORS['text']}),
                html.Li('Zoom: Use scroll wheel', style={'color': COLORS['text']}),
                html.Li('Pan: Right-click and drag', style={'color': COLORS['text']}),
                html.Li('Select: Click on objects for details', style={'color': COLORS['text']})
            ]),
            html.H4('SSZ Physics', style={'color': COLORS['primary'], 'marginTop': '20px'}),
            html.P('Segment Density: Xi(r) = 1 - exp(-phi * r_s / r)', style={'color': COLORS['text'], 'fontFamily': 'monospace'}),
            html.P('Time Dilation: D_SSZ(r) = 1/(1 + Xi)', style={'color': COLORS['text'], 'fontFamily': 'monospace'}),
            html.P(f'Golden Ratio: phi = {PHI:.10f}', style={'color': COLORS['text'], 'fontFamily': 'monospace'})
        ], style={'padding': '20px', 'backgroundColor': COLORS['panel'], 'borderRadius': '5px'})
    ])


# Callback: Export data
@app.callback(
    Output('export-status', 'children'),
    [Input('btn-download-csv', 'n_clicks'),
     Input('btn-download-json', 'n_clicks'),
     Input('btn-download-md', 'n_clicks')],
    State('galaxy-data', 'data')
)
def handle_export(n_csv, n_json, n_md, galaxy_data):
    """Handle data export."""
    ctx = callback_context
    
    if not ctx.triggered or galaxy_data is None:
        return ''
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    df = pd.DataFrame(galaxy_data)
    exporter = SSZDataExporter()
    
    if button_id == 'btn-download-csv':
        path = exporter.export_objects_csv(df, 'skymap_export.csv')
        return html.Div(f'✓ CSV exported to: {path}', style={'color': '#2ecc71'})
    
    elif button_id == 'btn-download-json':
        path = exporter.export_objects_json(df, 'skymap_export.json')
        return html.Div(f'✓ JSON exported to: {path}', style={'color': '#2ecc71'})
    
    elif button_id == 'btn-download-md':
        path = exporter.export_objects_markdown(df, 'skymap_export_report.md')
        return html.Div(f'✓ Report exported to: {path}', style={'color': '#2ecc71'})
    
    return ''


# Callback: Update comparison plots
@app.callback(
    [Output('comparison-time-dilation', 'figure'),
     Output('comparison-velocity', 'figure'),
     Output('comparison-period', 'figure')],
    Input('comparison-mass', 'value')
)
def update_comparison_plots(mass):
    """Update comparison plots based on selected mass."""
    from comparison_visualizations import ComparisonVisualizer
    
    if mass is None:
        mass = 1.0
    
    viz = ComparisonVisualizer(colors=COLORS)
    
    fig1 = viz.create_time_dilation_comparison(mass)
    fig2 = viz.create_velocity_comparison(mass)
    fig3 = viz.create_orbital_period_comparison(mass)
    
    return fig1, fig2, fig3


# Callback: Update SSZ-only plots
@app.callback(
    [Output('ssz-radial-profiles', 'figure'),
     Output('ssz-parameter-space', 'figure')],
    Input('ssz-only-mass', 'value')
)
def update_ssz_only_plots(mass):
    """Update SSZ-only plots based on selected mass."""
    from comparison_visualizations import SSZOnlyVisualizer
    
    if mass is None:
        mass = 1.0
    
    viz = SSZOnlyVisualizer(colors=COLORS)
    
    fig1 = viz.create_ssz_radial_profiles(mass)
    fig2 = viz.create_ssz_parameter_space()
    
    return fig1, fig2


if __name__ == '__main__':
    print("="*70)
    print("INTERACTIVE 3D SKYMAP - Starting...")
    print("="*70)
    print()
    print("Opening browser at: http://127.0.0.1:8050")
    print()
    print("Features:")
    print("  - 3D Galaxy View (1000 stars)")
    print("  - System Detail View")
    print("  - Data Export (CSV/JSON/MD)")
    print("  - Interactive Menu Navigation")
    print("  - Real-time SSZ calculations")
    print()
    print("Press Ctrl+C to stop")
    print("="*70)
    print()
    
    app.run(debug=True, port=8050)
