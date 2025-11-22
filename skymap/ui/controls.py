#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Control panel components for Dash dashboard.

© 2025 Carmen Wrede, Lino Casu
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_control_panel(max_distance=100, max_stars=2000):
    """
    Create control panel with sliders and toggles.
    
    Parameters
    ----------
    max_distance : float
        Maximum distance slider value
    max_stars : int
        Maximum stars slider value
        
    Returns
    -------
    dbc.Card
        Control panel component
    """
    controls = dbc.Card([
        dbc.CardHeader(html.H4("Controls", className="text-center")),
        dbc.CardBody([
            # Distance slider
            html.Label("Distance Range [pc]", className="fw-bold"),
            dcc.RangeSlider(
                id='distance-slider',
                min=0,
                max=max_distance,
                step=5,
                value=[0, 50],
                marks={i: f'{i}' for i in range(0, max_distance+1, 20)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            html.Br(),
            
            # Number of stars
            html.Label("Number of Stars", className="fw-bold"),
            dcc.Slider(
                id='stars-slider',
                min=100,
                max=max_stars,
                step=100,
                value=500,
                marks={i: f'{i}' for i in range(0, max_stars+1, 500)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            html.Br(),
            
            # Glow mode
            html.Label("Glow Effect Mode", className="fw-bold"),
            dcc.Dropdown(
                id='glow-mode-dropdown',
                options=[
                    {'label': 'Stretch Factor', 'value': 'stretch'},
                    {'label': 'Time Dilation', 'value': 'dilation'},
                    {'label': 'Combined', 'value': 'combined'}
                ],
                value='stretch',
                clearable=False
            ),
            html.Br(),
            
            # Color scale
            html.Label("Color Scale", className="fw-bold"),
            dcc.Dropdown(
                id='colorscale-dropdown',
                options=[
                    {'label': 'Plasma', 'value': 'Plasma'},
                    {'label': 'Viridis', 'value': 'Viridis'},
                    {'label': 'Inferno', 'value': 'Inferno'},
                    {'label': 'Magma', 'value': 'Magma'},
                    {'label': 'Hot', 'value': 'Hot'},
                    {'label': 'Cool', 'value': 'Cool'}
                ],
                value='Plasma',
                clearable=False
            ),
            html.Br(),
            
            # Toggle switches
            html.Label("Visual Effects", className="fw-bold"),
            dbc.Checklist(
                id='effects-checklist',
                options=[
                    {'label': ' Show Connections', 'value': 'connections'},
                    {'label': ' Show Glow', 'value': 'glow'},
                    {'label': ' Show Grid', 'value': 'grid'},
                    {'label': ' Show SSZ', 'value': 'ssz'}
                ],
                value=['glow', 'ssz'],
                switch=True
            ),
            html.Br(),
            
            # Theme selector
            html.Label("Theme", className="fw-bold"),
            dbc.RadioItems(
                id='theme-radio',
                options=[
                    {'label': ' Space (Black)', 'value': 'space'},
                    {'label': ' Dark (Navy)', 'value': 'dark'},
                    {'label': ' Light', 'value': 'light'}
                ],
                value='space',
                inline=False
            ),
            html.Br(),
            
            # Update button
            dbc.Button(
                "Update View",
                id='update-button',
                color="primary",
                className="w-100",
                size="lg"
            )
        ])
    ], color="dark", outline=True)
    
    return controls


def create_search_panel():
    """
    Create search panel for finding stars.
    
    Returns
    -------
    dbc.Card
        Search panel component
    """
    search = dbc.Card([
        dbc.CardHeader(html.H4("Search", className="text-center")),
        dbc.CardBody([
            dbc.Input(
                id='star-search-input',
                type='text',
                placeholder='Enter star name...',
                debounce=True
            ),
            html.Br(),
            dbc.Button(
                "Search",
                id='search-button',
                color="success",
                className="w-100"
            ),
            html.Br(),
            html.Div(id='search-results', className="mt-3")
        ])
    ], color="dark", outline=True)
    
    return search


def create_filter_panel():
    """
    Create filter panel for magnitude/type filtering.
    
    Returns
    -------
    dbc.Card
        Filter panel component
    """
    filters = dbc.Card([
        dbc.CardHeader(html.H4("Filters", className="text-center")),
        dbc.CardBody([
            html.Label("Magnitude Range", className="fw-bold"),
            dcc.RangeSlider(
                id='magnitude-slider',
                min=-2,
                max=15,
                step=0.5,
                value=[-2, 10],
                marks={i: f'{i}' for i in range(-2, 16, 2)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            html.Br(),
            
            html.Label("Spectral Type", className="fw-bold"),
            dcc.Dropdown(
                id='spectral-type-dropdown',
                options=[
                    {'label': 'All', 'value': 'all'},
                    {'label': 'O (Blue)', 'value': 'O'},
                    {'label': 'B (Blue-White)', 'value': 'B'},
                    {'label': 'A (White)', 'value': 'A'},
                    {'label': 'F (Yellow-White)', 'value': 'F'},
                    {'label': 'G (Yellow)', 'value': 'G'},
                    {'label': 'K (Orange)', 'value': 'K'},
                    {'label': 'M (Red)', 'value': 'M'}
                ],
                value='all',
                multi=True
            ),
            html.Br(),
            
            dbc.Button(
                "Apply Filters",
                id='filter-button',
                color="info",
                className="w-100"
            )
        ])
    ], color="dark", outline=True)
    
    return filters
