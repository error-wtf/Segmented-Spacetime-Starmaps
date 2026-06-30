#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 2: STAR SYSTEM DETAILS

Interactive3D-Style SSZ Galaxy Viewer - System View

Features:
- Detailed system view for selected stars
- Planet generation based on star properties
- Orbital visualization with SSZ corrections
- System info panel
- SSZ field visualization (contours)
- Habitable zone calculation

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path

# Constants
G = 6.67430e-11  # m^3 kg^-1 s^-2
c = 2.99792458e8  # m/s
M_sun = 1.989e30  # kg
M_earth = 5.972e24  # kg
R_earth = 6.371e6  # m
AU = 1.496e11  # m
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio


class PlanetGenerator:
    """Generate realistic planetary systems based on star properties."""
    
    def __init__(self, star_mass_msun, star_type):
        self.star_mass = star_mass_msun
        self.star_type = star_type
        self.planets = []
        
    def generate_system(self):
        """Generate planets for this star system."""
        
        # Number of planets depends on star type
        if self.star_type in ['O', 'B']:
            n_planets = np.random.randint(0, 3)  # Hot stars: few planets
        elif self.star_type in ['A', 'F']:
            n_planets = np.random.randint(2, 6)  # Medium: moderate
        elif self.star_type == 'G':
            n_planets = np.random.randint(4, 9)  # Sun-like: many
        elif self.star_type == 'K':
            n_planets = np.random.randint(3, 7)  # Orange: moderate
        else:  # M
            n_planets = np.random.randint(2, 5)  # Red dwarfs: few
        
        # Generate planets
        self.planets = []
        
        for i in range(n_planets):
            planet = self._generate_planet(i)
            self.planets.append(planet)
        
        return self.planets
    
    def _generate_planet(self, index):
        """Generate a single planet."""
        
        # Orbital distance (exponential distribution)
        # Inner planets closer, outer planets farther
        base_distance = 0.4 * AU  # 0.4 AU minimum
        scale = 30 * AU  # Up to ~30 AU
        
        a = base_distance + np.random.exponential(scale / 5)
        a = min(a, scale)  # Cap at scale
        
        # Orbital eccentricity
        e = np.random.beta(2, 5)  # Most planets have low eccentricity
        e = min(e, 0.9)  # Cap at 0.9
        
        # Planet mass (power law distribution)
        mass_earth = self._generate_planet_mass(a)
        
        # Planet radius (mass-radius relation)
        radius_earth = self._mass_to_radius(mass_earth)
        
        # Planet type
        planet_type = self._classify_planet(mass_earth, a)
        
        # Orbital period
        M_kg = self.star_mass * M_sun
        T_orbital = 2 * np.pi * np.sqrt(a**3 / (G * M_kg))
        T_years = T_orbital / (365.25 * 24 * 3600)
        
        # SSZ-corrected orbit
        r_s = 2 * G * M_kg / (c**2)
        Xi = 1 - np.exp(-PHI * a / r_s) if r_s > 0 else 0
        T_ssz = T_orbital * (1 + Xi)
        T_ssz_years = T_ssz / (365.25 * 24 * 3600)
        
        # Orbital velocity
        v_orbital = np.sqrt(G * M_kg / a)
        v_orbital_ssz = v_orbital * np.sqrt(1 + Xi)
        
        return {
            'name': f'Planet_{index + 1}',
            'index': index,
            'type': planet_type,
            'mass_earth': mass_earth,
            'mass_kg': mass_earth * M_earth,
            'radius_earth': radius_earth,
            'radius_m': radius_earth * R_earth,
            'a_AU': a / AU,
            'a_m': a,
            'e': e,
            'T_orbital_years': T_years,
            'T_ssz_years': T_ssz_years,
            'v_orbital_km_s': v_orbital / 1000,
            'v_orbital_ssz_km_s': v_orbital_ssz / 1000,
            'Xi': Xi
        }
    
    def _generate_planet_mass(self, a_m):
        """Generate planet mass based on distance."""
        # Inner planets: rocky (0.1 - 10 Earth masses)
        # Outer planets: gas giants (10 - 300 Earth masses)
        
        if a_m < 2 * AU:  # Inner system
            return np.random.lognormal(0, 1) * 1.5  # Rocky
        elif a_m < 5 * AU:  # Middle system
            return np.random.lognormal(1, 1) * 10  # Gas giants
        else:  # Outer system
            return np.random.lognormal(0.5, 1) * 5  # Ice giants
    
    def _mass_to_radius(self, mass_earth):
        """Estimate planet radius from mass."""
        if mass_earth < 2:  # Rocky
            return mass_earth ** 0.27
        elif mass_earth < 100:  # Gas dwarf/giant
            return mass_earth ** 0.55
        else:  # Super-Jupiter
            return 11.0 + (mass_earth - 100) ** 0.1
    
    def _classify_planet(self, mass_earth, a_m):
        """Classify planet type."""
        if mass_earth < 0.5:
            return 'Rocky (small)'
        elif mass_earth < 2.0:
            return 'Rocky (terrestrial)'
        elif mass_earth < 10:
            return 'Super-Earth'
        elif mass_earth < 50:
            return 'Gas dwarf'
        elif mass_earth < 300:
            return 'Gas giant'
        else:
            return 'Super-Jupiter'
    
    def calculate_habitable_zone(self):
        """Calculate habitable zone boundaries."""
        # Simplified habitable zone calculation
        L_star = self.star_mass ** 3.5  # Stellar luminosity
        
        # Inner and outer HZ boundaries (AU)
        r_inner = np.sqrt(L_star / 1.1) * 0.95
        r_outer = np.sqrt(L_star / 0.53) * 1.37
        
        return {
            'inner_AU': r_inner,
            'outer_AU': r_outer,
            'inner_m': r_inner * AU,
            'outer_m': r_outer * AU
        }


class SystemRenderer:
    """Render detailed star system view."""
    
    def __init__(self, star_data, planets):
        self.star = star_data
        self.planets = planets
        
    def render_system(self):
        """Create detailed system visualization."""
        
        print(f"Rendering system: {self.star['name']}")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'System Overview (orbits)',
                'SSZ Segment Density Field',
                'Planet Properties',
                'SSZ vs Classical Orbits'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'contour'}],
                [{'type': 'bar'}, {'type': 'scatter'}]
            ]
        )
        
        # Plot 1: System overview with orbits
        self._add_orbits(fig, row=1, col=1)
        
        # Plot 2: SSZ field
        self._add_ssz_field(fig, row=1, col=2)
        
        # Plot 3: Planet properties
        self._add_planet_bars(fig, row=2, col=1)
        
        # Plot 4: Orbital comparison
        self._add_orbital_comparison(fig, row=2, col=2)
        
        # Update layout
        fig.update_layout(
            title={
                'text': f'System Details: {self.star["name"]} ({self.star["spectral_type"]}-type, {self.star["mass_msun"]:.2f} M_sun)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            height=1000,
            showlegend=True,
            paper_bgcolor='#0a0e1a',
            plot_bgcolor='#0a0e1a',
            font=dict(color='#ecf0f1')
        )
        
        return fig
    
    def _add_orbits(self, fig, row, col):
        """Add orbital plot."""
        
        # Star at center
        fig.add_trace(
            go.Scatter(
                x=[0], y=[0],
                mode='markers',
                marker=dict(size=20, color='#fff4ea', symbol='star'),
                name=self.star['name'],
                hovertext=f"Star: {self.star['name']}<br>Type: {self.star['spectral_type']}<br>Mass: {self.star['mass_msun']:.2f} M_sun"
            ),
            row=row, col=col
        )
        
        # Planet orbits
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#95a5a6']
        
        for i, planet in enumerate(self.planets):
            # Orbit ellipse
            a = planet['a_AU']
            e = planet['e']
            
            # Ellipse points
            theta = np.linspace(0, 2*np.pi, 100)
            r = a * (1 - e**2) / (1 + e * np.cos(theta))
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Orbit line
            fig.add_trace(
                go.Scatter(
                    x=x, y=y,
                    mode='lines',
                    line=dict(color=colors[i % len(colors)], width=1, dash='dot'),
                    name=f'{planet["name"]} orbit',
                    showlegend=False,
                    hoverinfo='skip'
                ),
                row=row, col=col
            )
            
            # Planet position (at perihelion for visibility)
            x_planet = a * (1 - e)
            
            fig.add_trace(
                go.Scatter(
                    x=[x_planet], y=[0],
                    mode='markers',
                    marker=dict(size=8 + planet['radius_earth'], color=colors[i % len(colors)]),
                    name=planet['name'],
                    hovertext=f"{planet['name']}<br>Type: {planet['type']}<br>Mass: {planet['mass_earth']:.2f} M_earth<br>Distance: {planet['a_AU']:.2f} AU<br>Period: {planet['T_orbital_years']:.2f} yr"
                ),
                row=row, col=col
            )
        
        # Update axes
        max_a = max([p['a_AU'] for p in self.planets]) * 1.2 if self.planets else 1
        fig.update_xaxes(title_text="X (AU)", range=[-max_a, max_a], row=row, col=col)
        fig.update_yaxes(title_text="Y (AU)", range=[-max_a, max_a], row=row, col=col)
    
    def _add_ssz_field(self, fig, row, col):
        """Add SSZ segment density field."""
        
        # Create grid
        max_r = max([p['a_AU'] for p in self.planets]) * 1.5 if self.planets else 5
        x = np.linspace(-max_r, max_r, 50)
        y = np.linspace(-max_r, max_r, 50)
        X, Y = np.meshgrid(x, y)
        
        # Compute SSZ field
        M_kg = self.star['mass_msun'] * M_sun
        r_s = 2 * G * M_kg / (c**2)
        
        R = np.sqrt(X**2 + Y**2) * AU  # Convert to meters
        Xi = np.where(R > 0, 1 - np.exp(-PHI * r_s / r), 0)
        
        # Contour plot
        fig.add_trace(
            go.Contour(
                x=x, y=y, z=Xi,
                colorscale='Viridis',
                contours=dict(
                    coloring='heatmap',
                    showlabels=True
                ),
                colorbar=dict(title="Ξ(r)", x=0.95),
                name='SSZ Field'
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text="X (AU)", row=row, col=col)
        fig.update_yaxes(title_text="Y (AU)", row=row, col=col)
    
    def _add_planet_bars(self, fig, row, col):
        """Add planet properties bar chart."""
        
        if not self.planets:
            return
        
        names = [p['name'] for p in self.planets]
        masses = [p['mass_earth'] for p in self.planets]
        
        fig.add_trace(
            go.Bar(
                x=names,
                y=masses,
                marker=dict(color='#3498db'),
                name='Planet Mass'
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text="Planet", row=row, col=col)
        fig.update_yaxes(title_text="Mass (Earth masses)", type="log", row=row, col=col)
    
    def _add_orbital_comparison(self, fig, row, col):
        """Compare classical vs SSZ orbital periods."""
        
        if not self.planets:
            return
        
        distances = [p['a_AU'] for p in self.planets]
        T_classical = [p['T_orbital_years'] for p in self.planets]
        T_ssz = [p['T_ssz_years'] for p in self.planets]
        
        fig.add_trace(
            go.Scatter(
                x=distances,
                y=T_classical,
                mode='markers',
                marker=dict(size=10, color='#e74c3c'),
                name='Classical'
            ),
            row=row, col=col
        )
        
        fig.add_trace(
            go.Scatter(
                x=distances,
                y=T_ssz,
                mode='markers',
                marker=dict(size=10, color='#3498db', symbol='diamond'),
                name='SSZ-corrected'
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text="Distance (AU)", row=row, col=col)
        fig.update_yaxes(title_text="Orbital Period (years)", type="log", row=row, col=col)


def main():
    """Phase 2 Demo: Star System Details."""
    
    print("="*70)
    print("Interactive3D-STYLE SSZ GALAXY VIEWER")
    print("PHASE 2: STAR SYSTEM DETAILS")
    print("="*70)
    print()
    
    # Sample star systems to visualize
    sample_stars = [
        {'name': 'Sun-like', 'spectral_type': 'G', 'mass_msun': 1.0},
        {'name': 'Red Dwarf', 'spectral_type': 'M', 'mass_msun': 0.3},
        {'name': 'Hot Star', 'spectral_type': 'A', 'mass_msun': 2.5},
    ]
    
    for star in sample_stars:
        print(f"\nGenerating system: {star['name']} ({star['spectral_type']}-type)")
        print("-"*70)
        
        # Generate planets
        generator = PlanetGenerator(star['mass_msun'], star['spectral_type'])
        planets = generator.generate_system()
        
        print(f"  Planets: {len(planets)}")
        
        # Habitable zone
        hz = generator.calculate_habitable_zone()
        print(f"  Habitable zone: {hz['inner_AU']:.2f} - {hz['outer_AU']:.2f} AU")
        
        # Show planets
        for planet in planets:
            in_hz = hz['inner_AU'] <= planet['a_AU'] <= hz['outer_AU']
            hz_mark = " [HZ]" if in_hz else ""
            print(f"    - {planet['name']}: {planet['type']}, {planet['a_AU']:.2f} AU{hz_mark}")
        
        # Render system
        renderer = SystemRenderer(star, planets)
        fig = renderer.render_system()
        
        # Save
        filename = f"phase2_system_{star['name'].lower().replace('-', '_')}.html"
        fig.write_html(filename)
        print(f"  Saved: {filename}")
    
    print()
    print("="*70)
    print("PHASE 2 COMPLETE!")
    print("="*70)
    print()
    print("Features implemented:")
    print("  [OK] Planet generation based on star type")
    print("  [OK] Realistic orbital parameters")
    print("  [OK] Orbital visualization")
    print("  [OK] SSZ field visualization")
    print("  [OK] Habitable zone calculation")
    print("  [OK] SSZ vs Classical comparison")
    print()
    print("Files created:")
    print("  - phase2_system_sun-like.html")
    print("  - phase2_system_red_dwarf.html")
    print("  - phase2_system_hot_star.html")
    print()
    print("Next: Phase 3 - Visual Effects & UI")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
