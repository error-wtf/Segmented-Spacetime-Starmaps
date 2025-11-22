#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Info panels for displaying star data and statistics.

© 2025 Carmen Wrede, Lino Casu
"""

from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np


def create_info_panel():
    """
    Create info panel for selected star details.
    
    Returns
    -------
    dbc.Card
        Info panel component
    """
    info = dbc.Card([
        dbc.CardHeader(html.H4("Selected Star", className="text-center")),
        dbc.CardBody([
            html.Div(id='star-info-content', children=[
                html.P("Click on a star to see details", className="text-muted text-center")
            ])
        ])
    ], color="dark", outline=True)
    
    return info


def create_stats_panel():
    """
    Create statistics panel for current view.
    
    Returns
    -------
    dbc.Card
        Stats panel component
    """
    stats = dbc.Card([
        dbc.CardHeader(html.H4("Statistics", className="text-center")),
        dbc.CardBody([
            html.Div(id='stats-content', children=[
                dbc.Row([
                    dbc.Col([
                        html.P("Total Stars:", className="fw-bold mb-1"),
                        html.H5("0", id='stats-total', className="text-primary")
                    ], width=6),
                    dbc.Col([
                        html.P("Visible:", className="fw-bold mb-1"),
                        html.H5("0", id='stats-visible', className="text-success")
                    ], width=6)
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.P("Mean Distance:", className="fw-bold mb-1"),
                        html.H6("0.0 pc", id='stats-distance')
                    ], width=6),
                    dbc.Col([
                        html.P("SSZ Stretch:", className="fw-bold mb-1"),
                        html.H6("1.000x", id='stats-stretch')
                    ], width=6)
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.P("Time Dilation:", className="fw-bold mb-1"),
                        html.H6("0.500", id='stats-dilation')
                    ], width=12)
                ])
            ])
        ])
    ], color="dark", outline=True)
    
    return stats


def format_star_info(star_data):
    """
    Format star data for display in info panel.
    
    Parameters
    ----------
    star_data : dict
        Star properties
        
    Returns
    -------
    list
        Dash HTML components
    """
    if star_data is None:
        return [html.P("No star selected", className="text-muted")]
    
    components = [
        html.H5(star_data.get('name', 'Unknown'), className="text-primary"),
        html.Hr(),
        
        dbc.Row([
            dbc.Col([
                html.P("RA:", className="fw-bold mb-1"),
                html.P(f"{star_data.get('ra', 0):.4f}°")
            ], width=6),
            dbc.Col([
                html.P("Dec:", className="fw-bold mb-1"),
                html.P(f"{star_data.get('dec', 0):.4f}°")
            ], width=6)
        ]),
        
        html.Hr(),
        
        html.P("Distance (Minkowski):", className="fw-bold mb-1"),
        html.H6(f"{star_data.get('distance_pc', 0):.2f} pc", className="text-info"),
        
        html.P("Distance (SSZ):", className="fw-bold mb-1"),
        html.H6(f"{star_data.get('distance_ssz_pc', 0):.2f} pc", className="text-warning"),
        
        html.Hr(),
        
        dbc.Row([
            dbc.Col([
                html.P("Stretch Factor:", className="fw-bold mb-1"),
                html.H6(f"{star_data.get('stretch_factor', 1):.6f}x")
            ], width=6),
            dbc.Col([
                html.P("Time Dilation:", className="fw-bold mb-1"),
                html.H6(f"{star_data.get('D_ssz', 0.5):.6f}")
            ], width=6)
        ]),
        
        html.Hr(),
        
        html.P("Xi(r):", className="fw-bold mb-1"),
        html.P(f"{star_data.get('Xi', 0):.6f}"),
        
        html.P("Position:", className="fw-bold mb-1"),
        html.P(f"({star_data.get('x', 0):.1f}, {star_data.get('y', 0):.1f}, {star_data.get('z', 0):.1f}) pc")
    ]
    
    # Add magnitude if available
    if 'phot_g_mean_mag' in star_data and not pd.isna(star_data['phot_g_mean_mag']):
        components.extend([
            html.Hr(),
            html.P("Magnitude:", className="fw-bold mb-1"),
            html.P(f"G = {star_data['phot_g_mean_mag']:.2f}")
        ])
    
    return components


def format_stats(stars_df):
    """
    Format statistics for display.
    
    Parameters
    ----------
    stars_df : pd.DataFrame
        Star catalog
        
    Returns
    -------
    dict
        Statistics values
    """
    if stars_df is None or len(stars_df) == 0:
        return {
            'total': 0,
            'visible': 0,
            'mean_distance': 0.0,
            'mean_stretch': 1.0,
            'mean_dilation': 0.5
        }
    
    stats = {
        'total': len(stars_df),
        'visible': len(stars_df),  # Can be filtered
        'mean_distance': stars_df['distance_pc'].mean(),
        'mean_stretch': stars_df.get('stretch_factor', pd.Series([1.0])).mean(),
        'mean_dilation': stars_df.get('D_ssz', pd.Series([0.5])).mean()
    }
    
    return stats


def create_legend_panel():
    """
    Create legend panel explaining colors and symbols.
    
    Returns
    -------
    dbc.Card
        Legend panel
    """
    legend = dbc.Card([
        dbc.CardHeader(html.H4("Legend", className="text-center")),
        dbc.CardBody([
            html.P("Color Scale:", className="fw-bold"),
            html.Ul([
                html.Li("Red/Orange: Low time dilation (slower time)"),
                html.Li("Yellow/Green: Medium time dilation"),
                html.Li("Blue/Purple: High time dilation (faster time)")
            ]),
            html.Hr(),
            html.P("Marker Size:", className="fw-bold"),
            html.Ul([
                html.Li("Larger markers: Higher SSZ stretch factor"),
                html.Li("Smaller markers: Lower SSZ effects")
            ]),
            html.Hr(),
            html.P("Connection Lines:", className="fw-bold"),
            html.Ul([
                html.Li("Link nearby stars (< 5 pc)"),
                html.Li("Show spatial relationships")
            ])
        ])
    ], color="dark", outline=True)
    
    return legend
