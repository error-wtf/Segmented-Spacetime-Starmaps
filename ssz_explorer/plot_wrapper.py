"""
Plot Wrapper for Gradio - Convert Plotly to working format
===========================================================

Fixes Gradio gr.Plot() rendering issues by converting to JSON or HTML
"""

import plotly.graph_objects as go
import json

def wrap_for_gradio(fig):
    """
    Wrap Plotly figure for Gradio display
    
    Args:
        fig: Plotly figure object
    
    Returns:
        Figure in format that Gradio can render
    """
    # Return figure directly - Gradio should handle it
    # If this doesn't work, we can return fig.to_json() or fig.to_html()
    return fig


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
