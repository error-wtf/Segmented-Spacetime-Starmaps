#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D Renderer for SSZ Skymap.

Handles all 3D visualization with Plotly.

© 2025 Carmen Wrede, Lino Casu
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, Dict, List, Tuple


class SkymapRenderer:
    """
    3D renderer for star maps.
    
    Parameters
    ----------
    theme : str
        Color theme ('dark', 'light', 'space')
    height : int
        Plot height in pixels
    """
    
    def __init__(
        self,
        theme: str = 'dark',
        height: int = 800
    ):
        self.theme = theme
        self.height = height
        self.fig = None
        
        # Theme colors
        self.themes = {
            'dark': {
                'paper_bg': '#0a0a1e',
                'plot_bg': '#0a0a1e',
                'grid_color': '#333366',
                'text_color': 'white',
                'accent': 'cyan'
            },
            'space': {
                'paper_bg': '#000000',
                'plot_bg': '#000000',
                'grid_color': '#1a1a2e',
                'text_color': '#00ffff',
                'accent': '#ff00ff'
            },
            'light': {
                'paper_bg': '#ffffff',
                'plot_bg': '#f8f8f8',
                'grid_color': '#cccccc',
                'text_color': 'black',
                'accent': 'blue'
            }
        }
        
        self.colors = self.themes.get(theme, self.themes['dark'])
    
    def create_dual_view(
        self,
        stars: pd.DataFrame,
        stars_ssz: pd.DataFrame,
        title: str = "SSZ Skymap"
    ) -> go.Figure:
        """
        Create dual-view plot (Minkowski vs SSZ).
        
        Parameters
        ----------
        stars : pd.DataFrame
            Original stars with x, y, z columns
        stars_ssz : pd.DataFrame
            SSZ-transformed stars with x_ssz, y_ssz, z_ssz
        title : str
            Plot title
            
        Returns
        -------
        go.Figure
            Plotly figure
        """
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}]],
            subplot_titles=(
                'Minkowski Space',
                'SSZ (Segmented Spacetime)'
            ),
            horizontal_spacing=0.05
        )
        
        # Hover text
        hover_mink = self._create_hover_text(stars, mode='minkowski')
        hover_ssz = self._create_hover_text(stars_ssz, mode='ssz')
        
        # LEFT: Minkowski
        fig.add_trace(
            go.Scatter3d(
                x=stars['x'],
                y=stars['y'],
                z=stars['z'],
                mode='markers',
                marker=dict(
                    size=4,
                    color=self.colors['accent'],
                    opacity=0.8,
                    line=dict(width=0)
                ),
                name='Minkowski',
                text=hover_mink,
                hovertemplate='%{text}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # RIGHT: SSZ
        fig.add_trace(
            go.Scatter3d(
                x=stars_ssz['x_ssz'],
                y=stars_ssz['y_ssz'],
                z=stars_ssz['z_ssz'],
                mode='markers',
                marker=dict(
                    size=6,
                    color=stars_ssz['D_ssz'],
                    colorscale='Plasma',
                    showscale=True,
                    opacity=0.9,
                    line=dict(width=0.5, color='white'),
                    colorbar=dict(
                        title="Time<br>Dilation<br>D_SSZ",
                        x=1.05,
                        len=0.5,
                        thickness=15
                    )
                ),
                name='SSZ',
                text=hover_ssz,
                hovertemplate='%{text}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f'<b>{title}</b><br>' +
                     '<sub>Interactive 3D Star Map with SSZ Physics</sub>',
                x=0.5,
                xanchor='center',
                font=dict(size=20, color=self.colors['text_color'])
            ),
            paper_bgcolor=self.colors['paper_bg'],
            plot_bgcolor=self.colors['plot_bg'],
            font=dict(color=self.colors['text_color'], size=12),
            showlegend=True,
            legend=dict(
                x=0.5,
                y=-0.1,
                xanchor='center',
                orientation='h',
                bgcolor=f"rgba(10,10,30,0.8)",
                bordercolor=self.colors['accent'],
                borderwidth=1
            ),
            height=self.height,
            margin=dict(l=0, r=0, t=100, b=80)
        )
        
        # Update scenes
        scene_layout = self._get_scene_layout()
        fig.update_scenes(scene_layout, row=1, col=1)
        fig.update_scenes(scene_layout, row=1, col=2)
        
        self.fig = fig
        return fig
    
    def create_single_view(
        self,
        stars: pd.DataFrame,
        mode: str = 'ssz',
        color_by: str = 'D_ssz',
        title: str = "SSZ Skymap"
    ) -> go.Figure:
        """
        Create single-view 3D plot.
        
        Parameters
        ----------
        stars : pd.DataFrame
            Star catalog
        mode : str
            'minkowski' or 'ssz'
        color_by : str
            Column to use for coloring
        title : str
            Plot title
            
        Returns
        -------
        go.Figure
            Plotly figure
        """
        fig = go.Figure()
        
        # Select coordinates
        if mode == 'ssz' and 'x_ssz' in stars.columns:
            x, y, z = stars['x_ssz'], stars['y_ssz'], stars['z_ssz']
        else:
            x, y, z = stars['x'], stars['y'], stars['z']
        
        # Color
        if color_by in stars.columns:
            colors = stars[color_by]
            colorscale = 'Plasma'
            showscale = True
        else:
            colors = self.colors['accent']
            colorscale = None
            showscale = False
        
        # Hover
        hover = self._create_hover_text(stars, mode=mode)
        
        # Add trace
        fig.add_trace(
            go.Scatter3d(
                x=x, y=y, z=z,
                mode='markers',
                marker=dict(
                    size=6,
                    color=colors,
                    colorscale=colorscale,
                    showscale=showscale,
                    opacity=0.9,
                    line=dict(width=0.5, color='white')
                ),
                text=hover,
                hovertemplate='%{text}<extra></extra>'
            )
        )
        
        # Layout
        fig.update_layout(
            title=dict(
                text=f'<b>{title}</b>',
                x=0.5,
                xanchor='center',
                font=dict(size=20, color=self.colors['text_color'])
            ),
            paper_bgcolor=self.colors['paper_bg'],
            plot_bgcolor=self.colors['plot_bg'],
            font=dict(color=self.colors['text_color'], size=12),
            height=self.height,
            scene=self._get_scene_layout()
        )
        
        self.fig = fig
        return fig
    
    def _create_hover_text(
        self,
        stars: pd.DataFrame,
        mode: str = 'minkowski'
    ) -> List[str]:
        """Create hover text for stars."""
        hover_text = []
        
        for idx, row in stars.iterrows():
            text = f"<b>{row.get('name', 'Unknown')}</b><br>"
            
            if mode == 'minkowski':
                text += f"Distance: {row.get('distance_pc', 0):.2f} pc<br>"
                if 'phot_g_mean_mag' in row and not pd.isna(row['phot_g_mean_mag']):
                    text += f"Magnitude: {row['phot_g_mean_mag']:.2f}<br>"
                text += f"Position: ({row.get('x', 0):.1f}, {row.get('y', 0):.1f}, {row.get('z', 0):.1f}) pc"
            else:  # SSZ
                text += f"Distance (Mink): {row.get('distance_pc', 0):.2f} pc<br>"
                text += f"Distance (SSZ): {row.get('distance_ssz_pc', 0):.2f} pc<br>"
                text += f"Stretch: {row.get('stretch_factor', 1):.4f}x<br>"
                text += f"Time Dilation: {row.get('D_ssz', 0.5):.4f}<br>"
                text += f"Position: ({row.get('x_ssz', 0):.1f}, {row.get('y_ssz', 0):.1f}, {row.get('z_ssz', 0):.1f}) pc"
            
            hover_text.append(text)
        
        return hover_text
    
    def _get_scene_layout(self) -> Dict:
        """Get 3D scene layout."""
        return dict(
            xaxis=dict(
                title='X [pc]',
                backgroundcolor=self.colors['plot_bg'],
                gridcolor=self.colors['grid_color'],
                showbackground=True,
                zerolinecolor=self.colors['grid_color']
            ),
            yaxis=dict(
                title='Y [pc]',
                backgroundcolor=self.colors['plot_bg'],
                gridcolor=self.colors['grid_color'],
                showbackground=True,
                zerolinecolor=self.colors['grid_color']
            ),
            zaxis=dict(
                title='Z [pc]',
                backgroundcolor=self.colors['plot_bg'],
                gridcolor=self.colors['grid_color'],
                showbackground=True,
                zerolinecolor=self.colors['grid_color']
            ),
            bgcolor=self.colors['plot_bg'],
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        )
    
    def show(self):
        """Show the plot."""
        if self.fig:
            self.fig.show()
    
    def save_html(self, filename: str):
        """Save plot as HTML."""
        if self.fig:
            self.fig.write_html(filename)
    
    def save_image(self, filename: str):
        """Save plot as static image (requires kaleido)."""
        if self.fig:
            try:
                self.fig.write_image(filename)
            except Exception as e:
                print(f"Could not save image: {e}")
                print("Install kaleido: pip install kaleido")
