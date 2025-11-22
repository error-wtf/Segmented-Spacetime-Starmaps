"""
Plot Wrapper for Gradio - Convert Plotly to working format
===========================================================

Fixes Gradio gr.Plot() rendering issues by converting to JSON or HTML
"""

import plotly.graph_objects as go
import json

def wrap_for_gradio(fig):
    """
    Wrap Plotly figure for Gradio display - CONVERT TO HTML!
    
    Args:
        fig: Plotly figure object
    
    Returns:
        HTML string that Gradio CAN render
    """
    # SOLUTION: Convert to HTML because gr.Plot() has bugs!
    return fig.to_html(
        include_plotlyjs='cdn',
        config={
            'responsive': True,
            'displayModeBar': True,
            'displaylogo': False
        },
        div_id='plot-container'
    )


def fig_to_html_string(fig):
    """
    Convert figure to HTML string for gr.HTML()
    
    Args:
        fig: Plotly figure
        
    Returns:
        HTML string
    """
    return fig.to_html(
        include_plotlyjs='cdn',
        config={
            'responsive': True,
            'displayModeBar': True,
            'displaylogo': False
        }
    )
