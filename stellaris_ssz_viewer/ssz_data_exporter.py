#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Data Exporter - Download Object Data with SSZ Physics

Export star/planet data with complete SSZ calculations:
- CSV format (Excel-compatible)
- JSON format (machine-readable)
- Markdown format (human-readable reports)
- Full SSZ parameter calculations

© 2025 Carmen Wrede, Lino Casu
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Constants
G = 6.67430e-11  # m^3 kg^-1 s^-2
c = 2.99792458e8  # m/s
M_sun = 1.989e30  # kg
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
PC_TO_M = 3.0857e16  # parsec to meters


class SSZDataExporter:
    """Export astronomical objects with complete SSZ calculations."""
    
    def __init__(self):
        self.export_dir = Path('ssz_exports')
        self.export_dir.mkdir(exist_ok=True)
        
    def compute_full_ssz_parameters(self, M_solar, r_m, name='Object'):
        """
        Compute ALL SSZ parameters for an object.
        
        Parameters
        ----------
        M_solar : float
            Mass in solar masses
        r_m : float
            Distance in meters
        name : str
            Object name
            
        Returns
        -------
        dict
            Complete SSZ parameter set
        """
        M_kg = M_solar * M_sun
        
        # Schwarzschild radius
        r_s = 2 * G * M_kg / (c**2) if M_kg > 0 else 0
        
        # Dimensionless radius
        x = r_m / r_s if r_s > 0 else np.inf
        
        # SSZ segment density
        Xi = 1 - np.exp(-PHI * r_m / r_s) if r_s > 0 else 0
        
        # Time dilation (SSZ)
        D_ssz = 1 / (1 + Xi) if Xi < 1 else 0
        
        # Time dilation (GR)
        D_gr = np.sqrt(1 - r_s / r_m) if r_m > r_s else 0
        
        # Radial stretch
        R_ssz = r_m * (1 + Xi)
        stretch_factor = 1 + Xi
        
        # Velocities
        v_orbital = np.sqrt(G * M_kg / r_m) if r_m > 0 else 0
        v_escape = np.sqrt(2 * G * M_kg / r_m) if r_m > 0 else 0
        
        # SSZ-corrected velocities
        v_orbital_ssz = v_orbital * np.sqrt(1 + Xi)
        v_escape_ssz = v_escape * np.sqrt(1 + Xi)
        
        # Velocity fractions
        v_orbital_c = v_orbital / c
        v_escape_c = v_escape / c
        
        # Photon sphere and ISCO
        r_ph = 1.5 * r_s
        r_isco = 3 * r_s
        
        # Gravitational redshift
        z_gr = (1 / D_gr - 1) if D_gr > 0 and D_gr < 1 else (np.inf if D_gr == 0 else 0)
        z_ssz = (1 / D_ssz - 1) if D_ssz > 0 and D_ssz < 1 else (np.inf if D_ssz == 0 else 0)
        
        # Gravitational field
        g_m_s2 = G * M_kg / (r_m**2) if r_m > 0 else 0
        g_earth_g = g_m_s2 / 9.81  # In Earth g's
        
        # Gravitational potential
        phi_potential = -G * M_kg / r_m if r_m > 0 else 0
        
        # Proper time ratio
        tau_ratio = D_ssz
        
        # Orbital period (classical)
        T_orbital = 2 * np.pi * np.sqrt(r_m**3 / (G * M_kg)) if M_kg > 0 and r_m > 0 else 0
        T_orbital_years = T_orbital / (365.25 * 24 * 3600)
        
        # Orbital period (SSZ-corrected)
        T_orbital_ssz = T_orbital * (1 + Xi)
        T_orbital_ssz_years = T_orbital_ssz / (365.25 * 24 * 3600)
        
        # Event horizon comparison
        horizon_ratio = r_m / r_s if r_s > 0 else np.inf
        inside_photon_sphere = r_m < r_ph
        inside_isco = r_m < r_isco
        
        return {
            # Basic properties
            'name': name,
            'M_solar': M_solar,
            'M_kg': M_kg,
            'r_m': r_m,
            'r_km': r_m / 1000,
            'r_AU': r_m / 1.496e11,
            'r_ly': r_m / 9.461e15,
            'r_pc': r_m / PC_TO_M,
            
            # Schwarzschild parameters
            'r_s_m': r_s,
            'r_s_km': r_s / 1000,
            'x_dimensionless': x,
            'horizon_ratio': horizon_ratio,
            'r_ph_m': r_ph,
            'r_isco_m': r_isco,
            'inside_photon_sphere': inside_photon_sphere,
            'inside_isco': inside_isco,
            
            # SSZ parameters
            'Xi_segment_density': Xi,
            'D_ssz_time_dilation': D_ssz,
            'D_gr_time_dilation': D_gr,
            'stretch_factor': stretch_factor,
            'R_ssz_m': R_ssz,
            'R_ssz_km': R_ssz / 1000,
            
            # Velocities (m/s)
            'v_orbital_m_s': v_orbital,
            'v_escape_m_s': v_escape,
            'v_orbital_ssz_m_s': v_orbital_ssz,
            'v_escape_ssz_m_s': v_escape_ssz,
            
            # Velocities (km/s)
            'v_orbital_km_s': v_orbital / 1000,
            'v_escape_km_s': v_escape / 1000,
            'v_orbital_ssz_km_s': v_orbital_ssz / 1000,
            'v_escape_ssz_km_s': v_escape_ssz / 1000,
            
            # Velocities (fraction of c)
            'v_orbital_over_c': v_orbital_c,
            'v_escape_over_c': v_escape_c,
            
            # Time and redshift
            'tau_over_t': tau_ratio,
            'z_gr_redshift': z_gr,
            'z_ssz_redshift': z_ssz,
            
            # Orbital periods
            'T_orbital_seconds': T_orbital,
            'T_orbital_years': T_orbital_years,
            'T_orbital_ssz_seconds': T_orbital_ssz,
            'T_orbital_ssz_years': T_orbital_ssz_years,
            
            # Gravitational field
            'g_m_s2': g_m_s2,
            'g_earth_g': g_earth_g,
            'phi_potential_J_kg': phi_potential,
            
            # Metadata
            'export_timestamp': datetime.now().isoformat(),
            'phi_golden_ratio': PHI
        }
    
    def export_objects_csv(self, objects_data, filename='ssz_objects.csv'):
        """
        Export objects to CSV format.
        
        Parameters
        ----------
        objects_data : list of dict or DataFrame
            Object data with mass and distance
        filename : str
            Output filename
        """
        print(f"Exporting to CSV: {filename}")
        
        # Convert to DataFrame if needed
        if isinstance(objects_data, list):
            df_input = pd.DataFrame(objects_data)
        else:
            df_input = objects_data.copy()
        
        # Compute SSZ parameters for all objects
        ssz_params_list = []
        
        for idx, row in df_input.iterrows():
            name = row.get('name', row.get('case', f'Object_{idx}'))
            M_solar = row.get('M_solar', row.get('mass_msun', 1.0))
            r_m = row.get('r_m', row.get('r_emit_m', row.get('distance_pc', 1) * PC_TO_M))
            
            params = self.compute_full_ssz_parameters(M_solar, r_m, name)
            ssz_params_list.append(params)
        
        # Create DataFrame
        df_export = pd.DataFrame(ssz_params_list)
        
        # Save to CSV
        output_path = self.export_dir / filename
        df_export.to_csv(output_path, index=False, float_format='%.10e')
        
        print(f"[OK] Saved {len(df_export)} objects to: {output_path}")
        print(f"     Columns: {len(df_export.columns)}")
        print(f"     Size: {output_path.stat().st_size / 1024:.1f} KB")
        
        return output_path
    
    def export_objects_json(self, objects_data, filename='ssz_objects.json'):
        """
        Export objects to JSON format.
        
        Parameters
        ----------
        objects_data : list of dict or DataFrame
            Object data
        filename : str
            Output filename
        """
        print(f"Exporting to JSON: {filename}")
        
        # Convert to DataFrame if needed
        if isinstance(objects_data, list):
            df_input = pd.DataFrame(objects_data)
        else:
            df_input = objects_data.copy()
        
        # Compute SSZ parameters
        ssz_objects = []
        
        for idx, row in df_input.iterrows():
            name = row.get('name', row.get('case', f'Object_{idx}'))
            M_solar = row.get('M_solar', row.get('mass_msun', 1.0))
            r_m = row.get('r_m', row.get('r_emit_m', row.get('distance_pc', 1) * PC_TO_M))
            
            params = self.compute_full_ssz_parameters(M_solar, r_m, name)
            ssz_objects.append(params)
        
        # Create export structure
        export_data = {
            'metadata': {
                'title': 'SSZ Object Data Export',
                'description': 'Complete SSZ physics calculations for astronomical objects',
                'export_date': datetime.now().isoformat(),
                'n_objects': len(ssz_objects),
                'constants': {
                    'G': G,
                    'c': c,
                    'M_sun': M_sun,
                    'phi': PHI
                },
                'units': {
                    'mass': 'solar masses / kg',
                    'distance': 'meters / km / AU / ly / pc',
                    'velocity': 'm/s / km/s / fraction of c',
                    'time': 'seconds / years',
                    'gravity': 'm/s^2 / Earth g',
                    'potential': 'J/kg'
                }
            },
            'objects': ssz_objects
        }
        
        # Save to JSON
        output_path = self.export_dir / filename
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"[OK] Saved {len(ssz_objects)} objects to: {output_path}")
        print(f"     Size: {output_path.stat().st_size / 1024:.1f} KB")
        
        return output_path
    
    def export_objects_markdown(self, objects_data, filename='ssz_objects_report.md'):
        """
        Export objects to Markdown report format.
        
        Parameters
        ----------
        objects_data : list of dict or DataFrame
            Object data
        filename : str
            Output filename
        """
        print(f"Exporting to Markdown: {filename}")
        
        # Convert to DataFrame if needed
        if isinstance(objects_data, list):
            df_input = pd.DataFrame(objects_data)
        else:
            df_input = objects_data.copy()
        
        # Start report
        lines = [
            "# SSZ Object Data Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Objects:** {len(df_input)}",
            "",
            "---",
            "",
            "## Constants Used",
            "",
            f"- **G (Gravitational constant):** {G:.6e} m³/(kg·s²)",
            f"- **c (Speed of light):** {c:.6e} m/s",
            f"- **M☉ (Solar mass):** {M_sun:.6e} kg",
            f"- **φ (Golden ratio):** {PHI:.10f}",
            "",
            "---",
            "",
            "## Objects",
            ""
        ]
        
        # Add each object
        for idx, row in df_input.iterrows():
            name = row.get('name', row.get('case', f'Object_{idx}'))
            M_solar = row.get('M_solar', row.get('mass_msun', 1.0))
            r_m = row.get('r_m', row.get('r_emit_m', row.get('distance_pc', 1) * PC_TO_M))
            
            params = self.compute_full_ssz_parameters(M_solar, r_m, name)
            
            lines.extend([
                f"### {params['name']}",
                "",
                "#### Basic Properties",
                "",
                f"- **Mass:** {params['M_solar']:.4f} M☉ ({params['M_kg']:.4e} kg)",
                f"- **Distance:** {params['r_m']:.4e} m ({params['r_km']:.2f} km, {params['r_AU']:.4f} AU)",
                "",
                "#### Schwarzschild Parameters",
                "",
                f"- **r_s:** {params['r_s_m']:.4e} m ({params['r_s_km']:.2f} km)",
                f"- **x (r/r_s):** {params['x_dimensionless']:.4e}",
                f"- **Photon sphere:** {params['r_ph_m']:.4e} m",
                f"- **ISCO:** {params['r_isco_m']:.4e} m",
                "",
                "#### SSZ Parameters",
                "",
                f"- **Ξ(r):** {params['Xi_segment_density']:.10f}",
                f"- **D_SSZ(r):** {params['D_ssz_time_dilation']:.10f}",
                f"- **D_GR(r):** {params['D_gr_time_dilation']:.10f}",
                f"- **Stretch factor:** {params['stretch_factor']:.10f}",
                f"- **R_SSZ:** {params['R_ssz_m']:.4e} m",
                "",
                "#### Velocities",
                "",
                f"- **v_orbital:** {params['v_orbital_km_s']:.2f} km/s ({params['v_orbital_over_c']:.6f} c)",
                f"- **v_orbital (SSZ):** {params['v_orbital_ssz_km_s']:.2f} km/s",
                f"- **v_escape:** {params['v_escape_km_s']:.2f} km/s ({params['v_escape_over_c']:.6f} c)",
                f"- **v_escape (SSZ):** {params['v_escape_ssz_km_s']:.2f} km/s",
                "",
                "#### Time & Redshift",
                "",
                f"- **τ/t:** {params['tau_over_t']:.10f}",
                f"- **z_GR:** {params['z_gr_redshift']:.6e}",
                f"- **z_SSZ:** {params['z_ssz_redshift']:.6e}",
                "",
                "#### Orbital Period",
                "",
                f"- **T (classical):** {params['T_orbital_years']:.6f} years",
                f"- **T (SSZ):** {params['T_orbital_ssz_years']:.6f} years",
                "",
                "#### Gravitational Field",
                "",
                f"- **g:** {params['g_m_s2']:.4e} m/s² ({params['g_earth_g']:.2f} Earth g)",
                f"- **Φ:** {params['phi_potential_J_kg']:.4e} J/kg",
                "",
                "---",
                ""
            ])
        
        # Save to file
        output_path = self.export_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[OK] Saved report to: {output_path}")
        print(f"     Size: {output_path.stat().st_size / 1024:.1f} KB")
        
        return output_path
    
    def export_all_formats(self, objects_data, base_name='ssz_objects'):
        """
        Export to all formats.
        
        Parameters
        ----------
        objects_data : list of dict or DataFrame
            Object data
        base_name : str
            Base filename (without extension)
        """
        print("="*70)
        print("EXPORTING SSZ OBJECT DATA - ALL FORMATS")
        print("="*70)
        print()
        
        paths = {}
        
        # CSV
        paths['csv'] = self.export_objects_csv(objects_data, f'{base_name}.csv')
        print()
        
        # JSON
        paths['json'] = self.export_objects_json(objects_data, f'{base_name}.json')
        print()
        
        # Markdown
        paths['markdown'] = self.export_objects_markdown(objects_data, f'{base_name}_report.md')
        print()
        
        print("="*70)
        print("EXPORT COMPLETE!")
        print("="*70)
        print()
        print("Files created:")
        for format_name, path in paths.items():
            print(f"  [{format_name.upper():8s}] {path}")
        print()
        print(f"Export directory: {self.export_dir.absolute()}")
        print("="*70)
        
        return paths


def demo_export():
    """Demo: Export sample objects with SSZ calculations."""
    
    print("="*70)
    print("SSZ DATA EXPORTER - DEMO")
    print("="*70)
    print()
    
    # Sample objects
    sample_objects = [
        {'name': 'Sun', 'M_solar': 1.0, 'distance_pc': 0.000004848},  # ~1 AU
        {'name': 'Earth-Sun Distance', 'M_solar': 1.0, 'r_m': 1.496e11},
        {'name': 'Jupiter-Sun Distance', 'M_solar': 1.0, 'r_m': 7.78e11},
        {'name': 'Proxima Centauri', 'M_solar': 0.122, 'distance_pc': 1.301},
        {'name': 'Sirius A', 'M_solar': 2.063, 'distance_pc': 2.64},
        {'name': 'Betelgeuse', 'M_solar': 16.5, 'distance_pc': 168},
        {'name': 'Sgr A* (at 1 pc)', 'M_solar': 4.3e6, 'distance_pc': 1},
        {'name': 'M87* (at 10 pc)', 'M_solar': 6.5e9, 'distance_pc': 10},
    ]
    
    # Convert distance_pc to r_m where needed
    for obj in sample_objects:
        if 'distance_pc' in obj and 'r_m' not in obj:
            obj['r_m'] = obj['distance_pc'] * PC_TO_M
    
    print(f"Sample objects: {len(sample_objects)}")
    print()
    
    # Export
    exporter = SSZDataExporter()
    exporter.export_all_formats(sample_objects, base_name='demo_ssz_objects')
    
    print()
    print("You can now:")
    print("  1. Open the CSV in Excel/LibreOffice")
    print("  2. Read the JSON with any programming language")
    print("  3. View the Markdown report in any text editor")
    print()


if __name__ == "__main__":
    demo_export()
