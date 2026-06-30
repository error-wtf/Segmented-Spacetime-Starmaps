#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Comparison & Pure Visualizations

Two visualization modes:
1. COMPARISON MODE: SSZ vs GR side-by-side
2. SSZ-ONLY MODE: Pure SSZ physics without GR

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Constants
G = 6.67430e-11  # m^3 kg^-1 s^-2
c = 2.99792458e8  # m/s
M_sun = 1.989e30  # kg
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio


class ComparisonVisualizer:
    """Create SSZ vs GR comparison plots."""
    
    def __init__(self, colors=None):
        self.colors = colors or {
            'ssz': '#3498db',      # Blue
            'gr': '#e74c3c',       # Red
            'background': '#0a0e1a',
            'text': '#ecf0f1',
            'grid': '#1a2332'
        }
    
    def create_time_dilation_comparison(self, mass_msun, r_range_rs=(1.1, 10), n_points=100):
        """
        Compare SSZ vs GR time dilation.
        
        Parameters
        ----------
        mass_msun : float
            Mass in solar masses
        r_range_rs : tuple
            Range in units of r_s
        n_points : int
            Number of points
        """
        
        M_kg = mass_msun * M_sun
        r_s = 2 * G * M_kg / (c**2)
        
        # Create radial grid
        x_values = np.linspace(r_range_rs[0], r_range_rs[1], n_points)
        r_values = x_values * r_s
        
        # SSZ time dilation
        Xi = 1 - np.exp(-PHI * r_values / r_s)
        D_ssz = 1 / (1 + Xi)
        
        # GR time dilation
        D_gr = np.sqrt(1 - r_s / r_values)
        
        # Relative difference
        diff_percent = 100 * (D_ssz - D_gr) / D_gr
        
        # Create figure with subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Time Dilation: SSZ vs GR', 'Relative Difference (%)'),
            row_heights=[0.65, 0.35],
            vertical_spacing=0.12
        )
        
        # Plot 1: Direct comparison
        fig.add_trace(
            go.Scatter(
                x=x_values, y=D_ssz,
                mode='lines',
                name='SSZ (Segmented)',
                line=dict(color=self.colors['ssz'], width=3)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=x_values, y=D_gr,
                mode='lines',
                name='GR (Schwarzschild)',
                line=dict(color=self.colors['gr'], width=3, dash='dash')
            ),
            row=1, col=1
        )
        
        # Plot 2: Difference
        fig.add_trace(
            go.Scatter(
                x=x_values, y=diff_percent,
                mode='lines',
                name='Difference',
                line=dict(color='#f39c12', width=2),
                fill='tozeroy'
            ),
            row=2, col=1
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash='dot', line_color='white', opacity=0.5, row=2, col=1)
        
        # Update axes
        fig.update_xaxes(title_text="r / r_s", gridcolor=self.colors['grid'], row=1, col=1)
        fig.update_xaxes(title_text="r / r_s", gridcolor=self.colors['grid'], row=2, col=1)
        fig.update_yaxes(title_text="D(r)", gridcolor=self.colors['grid'], row=1, col=1)
        fig.update_yaxes(title_text="(D_SSZ - D_GR) / D_GR [%]", gridcolor=self.colors['grid'], row=2, col=1)
        
        # Update layout
        fig.update_layout(
            title=f'Time Dilation Comparison: M = {mass_msun:.2f} M_sun',
            paper_bgcolor=self.colors['background'],
            plot_bgcolor=self.colors['background'],
            font=dict(color=self.colors['text']),
            height=700,
            showlegend=True,
            legend=dict(x=0.7, y=0.95)
        )
        
        return fig
    
    def create_velocity_comparison(self, mass_msun, r_range_au=(0.1, 10), n_points=100):
        """Compare orbital velocities: SSZ vs GR."""
        
        M_kg = mass_msun * M_sun
        r_s = 2 * G * M_kg / (c**2)
        AU = 1.496e11
        
        # Radial grid
        r_values = np.linspace(r_range_au[0], r_range_au[1], n_points) * AU
        
        # Classical orbital velocity
        v_orb_classical = np.sqrt(G * M_kg / r_values)
        
        # SSZ correction
        Xi = 1 - np.exp(-PHI * r_values / r_s)
        v_orb_ssz = v_orb_classical * np.sqrt(1 + Xi)
        
        # GR (Schwarzschild) - approximate
        v_orb_gr = v_orb_classical * np.sqrt(1 - r_s / r_values)
        
        # Create figure
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Orbital Velocity Comparison', 'Velocity / c'),
            row_heights=[0.5, 0.5],
            vertical_spacing=0.12
        )
        
        # Plot 1: Absolute velocities
        fig.add_trace(
            go.Scatter(
                x=r_values/AU, y=v_orb_classical/1000,
                mode='lines',
                name='Classical',
                line=dict(color='gray', width=2, dash='dot')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=r_values/AU, y=v_orb_ssz/1000,
                mode='lines',
                name='SSZ',
                line=dict(color=self.colors['ssz'], width=3)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=r_values/AU, y=v_orb_gr/1000,
                mode='lines',
                name='GR',
                line=dict(color=self.colors['gr'], width=3, dash='dash')
            ),
            row=1, col=1
        )
        
        # Plot 2: Fraction of c
        fig.add_trace(
            go.Scatter(
                x=r_values/AU, y=v_orb_ssz/c,
                mode='lines',
                name='SSZ (v/c)',
                line=dict(color=self.colors['ssz'], width=3)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=r_values/AU, y=v_orb_gr/c,
                mode='lines',
                name='GR (v/c)',
                line=dict(color=self.colors['gr'], width=3, dash='dash')
            ),
            row=2, col=1
        )
        
        # Update axes
        fig.update_xaxes(title_text="Distance [AU]", gridcolor=self.colors['grid'], row=1, col=1)
        fig.update_xaxes(title_text="Distance [AU]", gridcolor=self.colors['grid'], row=2, col=1)
        fig.update_yaxes(title_text="v_orbital [km/s]", gridcolor=self.colors['grid'], row=1, col=1)
        fig.update_yaxes(title_text="v / c", gridcolor=self.colors['grid'], row=2, col=1)
        
        fig.update_layout(
            title=f'Orbital Velocity: M = {mass_msun:.2f} M_sun',
            paper_bgcolor=self.colors['background'],
            plot_bgcolor=self.colors['background'],
            font=dict(color=self.colors['text']),
            height=700
        )
        
        return fig
    
    def create_orbital_period_comparison(self, mass_msun, r_range_au=(0.5, 5), n_points=50):
        """Compare orbital periods: SSZ vs Classical."""
        
        M_kg = mass_msun * M_sun
        r_s = 2 * G * M_kg / (c**2)
        AU = 1.496e11
        
        r_values = np.linspace(r_range_au[0], r_range_au[1], n_points) * AU
        
        # Classical period
        T_classical = 2 * np.pi * np.sqrt(r_values**3 / (G * M_kg))
        T_classical_years = T_classical / (365.25 * 24 * 3600)
        
        # SSZ correction
        Xi = 1 - np.exp(-PHI * r_values / r_s)
        T_ssz = T_classical * (1 + Xi)
        T_ssz_years = T_ssz / (365.25 * 24 * 3600)
        
        # Difference
        delta_T_days = (T_ssz - T_classical) / (24 * 3600)
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Orbital Period Comparison', 'Period Difference (SSZ - Classical)'),
            row_heights=[0.6, 0.4],
            vertical_spacing=0.12
        )
        
        # Plot 1: Periods
        fig.add_trace(
            go.Scatter(
                x=r_values/AU, y=T_classical_years,
                mode='lines',
                name='Classical',
                line=dict(color='gray', width=2, dash='dot')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=r_values/AU, y=T_ssz_years,
                mode='lines',
                name='SSZ',
                line=dict(color=self.colors['ssz'], width=3)
            ),
            row=1, col=1
        )
        
        # Plot 2: Difference
        fig.add_trace(
            go.Scatter(
                x=r_values/AU, y=delta_T_days,
                mode='lines',
                name='Difference',
                line=dict(color='#f39c12', width=2),
                fill='tozeroy'
            ),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Distance [AU]", gridcolor=self.colors['grid'], row=1, col=1)
        fig.update_xaxes(title_text="Distance [AU]", gridcolor=self.colors['grid'], row=2, col=1)
        fig.update_yaxes(title_text="Orbital Period [years]", gridcolor=self.colors['grid'], row=1, col=1)
        fig.update_yaxes(title_text="ΔT [days]", gridcolor=self.colors['grid'], row=2, col=1)
        
        fig.update_layout(
            title=f'Orbital Period: M = {mass_msun:.2f} M_sun',
            paper_bgcolor=self.colors['background'],
            plot_bgcolor=self.colors['background'],
            font=dict(color=self.colors['text']),
            height=700
        )
        
        return fig


class SSZOnlyVisualizer:
    """Create pure SSZ visualizations without GR comparison."""
    
    def __init__(self, colors=None):
        self.colors = colors or {
            'primary': '#3498db',
            'secondary': '#2ecc71',
            'accent': '#9b59b6',
            'background': '#0a0e1a',
            'text': '#ecf0f1',
            'grid': '#1a2332'
        }
    
    def create_ssz_field_3d(self, mass_msun, grid_range_rs=(0.1, 5), n_points=50):
        """Create 3D SSZ segment density field."""
        
        M_kg = mass_msun * M_sun
        r_s = 2 * G * M_kg / (c**2)
        
        # Create 2D grid
        x = np.linspace(-grid_range_rs[1], grid_range_rs[1], n_points) * r_s
        y = np.linspace(-grid_range_rs[1], grid_range_rs[1], n_points) * r_s
        X, Y = np.meshgrid(x, y)
        
        # Calculate radius
        R = np.sqrt(X**2 + Y**2)
        
        # SSZ segment density
        Xi = np.where(R > 0, 1 - np.exp(-PHI * r_s / r), 0)
        
        # Create surface plot
        fig = go.Figure(data=[
            go.Surface(
                x=X/r_s, y=Y/r_s, z=Xi,
                colorscale='Viridis',
                name='Ξ(r)',
                colorbar=dict(title="Ξ(r)", x=1.1)
            )
        ])
        
        fig.update_layout(
            title=f'SSZ Segment Density Field: M = {mass_msun:.2f} M_sun',
            scene=dict(
                xaxis_title='x / r_s',
                yaxis_title='y / r_s',
                zaxis_title='Ξ(r)',
                bgcolor=self.colors['background'],
                xaxis=dict(gridcolor=self.colors['grid']),
                yaxis=dict(gridcolor=self.colors['grid']),
                zaxis=dict(gridcolor=self.colors['grid'])
            ),
            paper_bgcolor=self.colors['background'],
            font=dict(color=self.colors['text']),
            height=700
        )
        
        return fig
    
    def create_ssz_radial_profiles(self, mass_msun, r_range_rs=(1.1, 10), n_points=100):
        """Create multiple SSZ parameter profiles."""
        
        M_kg = mass_msun * M_sun
        r_s = 2 * G * M_kg / (c**2)
        
        x_values = np.linspace(r_range_rs[0], r_range_rs[1], n_points)
        r_values = x_values * r_s
        
        # Calculate SSZ parameters
        Xi = 1 - np.exp(-PHI * r_values / r_s)
        D_ssz = 1 / (1 + Xi)
        stretch = 1 + Xi
        R_ssz = r_values * stretch
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Segment Density Ξ(r)',
                'Time Dilation D_SSZ(r)',
                'Radial Stretch Factor',
                'SSZ Radius R_SSZ'
            )
        )
        
        # Plot 1: Segment density
        fig.add_trace(
            go.Scatter(
                x=x_values, y=Xi,
                mode='lines',
                name='Ξ(r)',
                line=dict(color=self.colors['primary'], width=3),
                fill='tozeroy'
            ),
            row=1, col=1
        )
        
        # Plot 2: Time dilation
        fig.add_trace(
            go.Scatter(
                x=x_values, y=D_ssz,
                mode='lines',
                name='D_SSZ(r)',
                line=dict(color=self.colors['secondary'], width=3)
            ),
            row=1, col=2
        )
        
        # Plot 3: Stretch factor
        fig.add_trace(
            go.Scatter(
                x=x_values, y=stretch,
                mode='lines',
                name='1 + Ξ',
                line=dict(color=self.colors['accent'], width=3)
            ),
            row=2, col=1
        )
        
        # Plot 4: SSZ radius
        fig.add_trace(
            go.Scatter(
                x=x_values, y=R_ssz/r_s,
                mode='lines',
                name='R_SSZ / r_s',
                line=dict(color='#e74c3c', width=3)
            ),
            row=2, col=2
        )
        
        # Add identity line to R_SSZ plot
        fig.add_trace(
            go.Scatter(
                x=x_values, y=x_values,
                mode='lines',
                name='r / r_s',
                line=dict(color='gray', width=1, dash='dash'),
                showlegend=False
            ),
            row=2, col=2
        )
        
        # Update all x-axes
        for row in [1, 2]:
            for col in [1, 2]:
                fig.update_xaxes(title_text="r / r_s", gridcolor=self.colors['grid'], row=row, col=col)
        
        # Update y-axes
        fig.update_yaxes(title_text="Ξ(r)", gridcolor=self.colors['grid'], row=1, col=1)
        fig.update_yaxes(title_text="D_SSZ(r)", gridcolor=self.colors['grid'], row=1, col=2)
        fig.update_yaxes(title_text="1 + Ξ", gridcolor=self.colors['grid'], row=2, col=1)
        fig.update_yaxes(title_text="R_SSZ / r_s", gridcolor=self.colors['grid'], row=2, col=2)
        
        fig.update_layout(
            title=f'SSZ Radial Profiles: M = {mass_msun:.2f} M_sun',
            paper_bgcolor=self.colors['background'],
            plot_bgcolor=self.colors['background'],
            font=dict(color=self.colors['text']),
            height=800,
            showlegend=False
        )
        
        return fig
    
    def create_ssz_parameter_space(self, mass_range_msun=(0.1, 100), r_fixed_au=1.0, n_points=100):
        """Show how SSZ parameters vary with mass."""
        
        AU = 1.496e11
        r_fixed = r_fixed_au * AU
        masses = np.logspace(np.log10(mass_range_msun[0]), np.log10(mass_range_msun[1]), n_points)
        
        # Calculate for each mass
        Xi_values = []
        D_ssz_values = []
        
        for M_msun in masses:
            M_kg = M_msun * M_sun
            r_s = 2 * G * M_kg / (c**2)
            Xi = 1 - np.exp(-PHI * r_fixed / r_s)
            D_ssz = 1 / (1 + Xi)
            Xi_values.append(Xi)
            D_ssz_values.append(D_ssz)
        
        # Create figure
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                f'Segment Density at r = {r_fixed_au} AU',
                f'Time Dilation at r = {r_fixed_au} AU'
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=masses, y=Xi_values,
                mode='lines',
                name='Ξ(r)',
                line=dict(color=self.colors['primary'], width=3)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=masses, y=D_ssz_values,
                mode='lines',
                name='D_SSZ(r)',
                line=dict(color=self.colors['secondary'], width=3)
            ),
            row=1, col=2
        )
        
        fig.update_xaxes(title_text="Mass [M_sun]", type="log", gridcolor=self.colors['grid'], row=1, col=1)
        fig.update_xaxes(title_text="Mass [M_sun]", type="log", gridcolor=self.colors['grid'], row=1, col=2)
        fig.update_yaxes(title_text="Ξ(r)", gridcolor=self.colors['grid'], row=1, col=1)
        fig.update_yaxes(title_text="D_SSZ(r)", gridcolor=self.colors['grid'], row=1, col=2)
        
        fig.update_layout(
            title='SSZ Parameters vs Mass',
            paper_bgcolor=self.colors['background'],
            plot_bgcolor=self.colors['background'],
            font=dict(color=self.colors['text']),
            height=500,
            showlegend=False
        )
        
        return fig


def demo():
    """Demo: Create all comparison and SSZ-only visualizations."""
    
    print("="*70)
    print("SSZ COMPARISON & PURE VISUALIZATIONS - Demo")
    print("="*70)
    print()
    
    # Test masses
    test_cases = [
        ('Sun', 1.0),
        ('Massive Star', 20.0),
        ('Black Hole', 4.3e6)
    ]
    
    comp_viz = ComparisonVisualizer()
    ssz_viz = SSZOnlyVisualizer()
    
    for name, mass in test_cases:
        print(f"Generating visualizations for {name} (M = {mass:.2e} M_sun)...")
        
        # Comparison plots
        fig1 = comp_viz.create_time_dilation_comparison(mass)
        fig1.write_html(f'comparison_time_dilation_{name.lower().replace(" ", "_")}.html')
        
        fig2 = comp_viz.create_velocity_comparison(mass)
        fig2.write_html(f'comparison_velocity_{name.lower().replace(" ", "_")}.html')
        
        # SSZ-only plots
        fig3 = ssz_viz.create_ssz_radial_profiles(mass)
        fig3.write_html(f'ssz_only_profiles_{name.lower().replace(" ", "_")}.html')
        
        print(f"  [OK] Created 3 visualizations for {name}")
    
    # Additional SSZ-only visualizations
    print("\nCreating parameter space visualization...")
    fig4 = ssz_viz.create_ssz_parameter_space()
    fig4.write_html('ssz_only_parameter_space.html')
    
    print()
    print("="*70)
    print("DEMO COMPLETE!")
    print("="*70)
    print()
    print("Files created:")
    print("  COMPARISON MODE:")
    print("    - comparison_time_dilation_*.html")
    print("    - comparison_velocity_*.html")
    print()
    print("  SSZ-ONLY MODE:")
    print("    - ssz_only_profiles_*.html")
    print("    - ssz_only_parameter_space.html")
    print()
    print("="*70)


if __name__ == "__main__":
    demo()
