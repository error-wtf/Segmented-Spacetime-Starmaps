"""
Plotly to HTML Converter for Gradio
===================================

Workaround for Gradio 4.44.0 Plot rendering issues
"""

def fig_to_html(fig):
    """
    Convert Plotly figure to HTML string for gr.HTML()
    
    Args:
        fig: Plotly figure object
    
    Returns:
        HTML string
    """
    return fig.to_html(
        include_plotlyjs='cdn',
        config={'responsive': True, 'displayModeBar': True}
    )
