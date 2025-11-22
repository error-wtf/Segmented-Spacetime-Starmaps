#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Explorer - Extended Gradio App
WITH ALL 7 CATALOGS + EXOPLANETS + CROSS-MATCHING!

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

# Fix Windows UTF-8 encoding
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import gradio as gr
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Import modules (but don't initialize yet - lazy loading!)
from star_map_generator import create_sky_map, create_3d_sky_map, create_constellation_map
from ssz_physics_plots import (
    create_g1_g2_domain_plot,
    create_time_dilation_comparison,
    create_radial_stretch_plot,
    create_combined_ssz_analysis
)
from interactive_navigation import create_interactive_sky_view, NavigationState
from object_selector import create_object_centered_view, get_object_list
from combined_physics_view import create_combined_physics_view
from progressive_view import create_progressive_3d_view, reset_progressive_view

# Global variables for lazy-loaded modules
_dm = None
_exo_fetch = None
_matcher = None
_ned_fetch = None
_sdss_fetch = None

# Global variable to store last query results for sky map
last_query_data = None

# Lazy loading functions
def get_data_manager():
    global _dm
    if _dm is None:
        from data_manager import DataManager
        _dm = DataManager()
    return _dm

def get_exoplanet_fetcher():
    global _exo_fetch
    if _exo_fetch is None:
        from exoplanet_fetcher import ExoplanetFetcher
        _exo_fetch = ExoplanetFetcher()
    return _exo_fetch

def get_cross_matcher():
    global _matcher
    if _matcher is None:
        from cross_matcher import CrossMatcher
        _matcher = CrossMatcher()
    return _matcher

def get_ned_fetcher():
    global _ned_fetch
    if _ned_fetch is None:
        from ned_fetcher import NEDFetcher
        _ned_fetch = NEDFetcher()
    return _ned_fetch

def get_sdss_fetcher():
    global _sdss_fetch
    if _sdss_fetch is None:
        from sdss_fetcher import SDSSFetcher
        _sdss_fetch = SDSSFetcher()
    return _sdss_fetch


def download_csv():
    """Download complete query results as CSV."""
    global last_query_data
    
    if last_query_data is None or last_query_data.empty:
        return None
    
    # Save to temporary CSV file
    import tempfile
    import os
    
    # Create temp file
    fd, path = tempfile.mkstemp(suffix='.csv', prefix='ssz_export_')
    
    try:
        # Write CSV
        last_query_data.to_csv(path, index=False)
        return path
    except Exception as e:
        print(f"CSV export error: {e}")
        if os.path.exists(path):
            os.close(fd)
            os.unlink(path)
        return None


def query_multi_catalog(catalog, ra, dec, radius):
    """Query any catalog by coordinates."""
    global last_query_data
    
    try:
        ra_val, dec_val, rad_val = float(ra), float(dec), float(radius)
        
        if catalog == "GAIA DR3":
            dm = get_data_manager()
            stars = dm.load_catalog('gaia', level='preview', limit=100)
            last_query_data = stars  # Store for sky map
            return f"✅ Found {len(stars)} stars", stars.head(20)
            
        elif catalog == "SIMBAD":
            from simbad_fetcher import SIMBADFetcher
            fetcher = SIMBADFetcher()
            result = fetcher.cone_search(ra_val, dec_val, rad_val)
            if result is not None:
                last_query_data = result
                return f"✅ Found {len(result)} objects", result.head(20)
            return "❌ No results", pd.DataFrame()
            
        elif catalog == "2MASS":
            from twomass_fetcher import TwoMASSFetcher
            fetcher = TwoMASSFetcher()
            result = fetcher.cone_search(ra_val, dec_val, rad_val)
            if result is not None:
                last_query_data = result
                return f"✅ Found {len(result)} sources", result.head(20)
            return "❌ No results", pd.DataFrame()
            
        elif catalog == "WISE":
            from wise_fetcher import WISEFetcher
            fetcher = WISEFetcher()
            result = fetcher.cone_search(ra_val, dec_val, rad_val)
            if result is not None:
                last_query_data = result
                return f"✅ Found {len(result)} sources", result.head(20)
            return "❌ No results", pd.DataFrame()
            
        elif catalog == "NED":
            ned_fetch = get_ned_fetcher()
            result = ned_fetch.cone_search(ra_val, dec_val, rad_val)
            if result is not None:
                last_query_data = result
                return f"✅ Found {len(result)} galaxies", result.head(20)
            return "❌ No results", pd.DataFrame()
            
        elif catalog == "SDSS":
            sdss_fetch = get_sdss_fetcher()
            result = sdss_fetch.cone_search(ra_val, dec_val, rad_val)
            if result is not None:
                last_query_data = result
                return f"✅ Found {len(result)} objects", result.head(20)
            return "❌ No results", pd.DataFrame()
        
    except Exception as e:
        return f"❌ Error: {e}", pd.DataFrame()


def search_exoplanets(host_name, min_mass, max_mass):
    """Search for exoplanets."""
    try:
        exo_fetch = get_exoplanet_fetcher()
        if not exo_fetch.is_available():
            return "❌ Exoplanet Archive not available", pd.DataFrame()
        
        if host_name:
            result = exo_fetch.query_by_host(host_name)
        else:
            result = exo_fetch.query_by_params(
                min_mass=float(min_mass) if min_mass else None,
                max_mass=float(max_mass) if max_mass else None,
                max_results=50
            )
        
        if result is not None and len(result) > 0:
            return f"✅ Found {len(result)} planets", result.head(20)
        
    except Exception as e:
        return f" Error: {e}", pd.DataFrame()


def calculate_habitable_zone(teff, star_mass, planet_dist):
    """Calculate habitable zone."""
    try:
        from habitable_zone import is_in_hz, hz_from_star_params
        teff_val = float(teff)
        mass_val = float(star_mass)
        dist = float(planet_dist) if planet_dist else 1.0
        
        # Calculate HZ
        result = hz_from_star_params(teff_val, mass_msun=mass_val, method='ssz')
        
        # Check if planet is in HZ
        in_hz_result = is_in_hz(dist, result['star_luminosity_lsun'], mass_val, method='ssz')
        
        output = f"""### Habitable Zone Results

**Star Parameters:**
- T_eff: {teff_val} K
- Mass: {mass_val} M_sun
- Luminosity: {result['star_luminosity_lsun']:.3f} L_sun

**Habitable Zone (SSZ-corrected):**
- Inner boundary: {result['hz_inner_au']:.3f} AU
- Outer boundary: {result['hz_outer_au']:.3f} AU
- Center: {result['hz_center_au']:.3f} AU
- Width: {result['hz_width_au']:.3f} AU

**Planet at {dist:.2f} AU:**
- In HZ: {'✅ YES' if in_hz_result['in_hz'] else '❌ NO'}
- Position: {in_hz_result['position_fraction']:.2f} (0=inner, 1=outer)
"""
        
        return output
        
    except Exception as e:
        return f"❌ Error: {e}"


def calculate_ssz_orbit(period_days, star_mass):
    """Calculate SSZ vs GR orbital parameters."""
    try:
        from ssz_orbits import calculate_for_planet
        P = float(period_days)
        M = float(star_mass)
        
        result = calculate_for_planet(P, M)
        
        output = f"""### Orbital Calculation Results

**Input:**
- Period: {P:.2f} days
- Star mass: {M:.2f} M_sun

**Semi-major axis:**
- {result['semi_major_axis_au']:.4f} AU

**Orbital Period:**
- GR:  {result['T_gr_days']:.6f} days
- SSZ: {result['T_ssz_days']:.6f} days
- Difference: {result['difference_sec']:.3f} seconds
- Relative: {result['relative_diff']*1e6:.2f} ppm

**Observability:**
- Observable: {result['observable']}
- {result['recommendations']}
"""
        
        return output
        
    except Exception as e:
        return f"❌ Error: {e}"


def cross_match_catalogs(catalog1, catalog2, ra, dec, radius, match_radius):
    """Cross-match two catalogs."""
    try:
        # Query both catalogs
        status1, df1 = query_multi_catalog(catalog1, ra, dec, radius)
        status2, df2 = query_multi_catalog(catalog2, ra, dec, radius)
        
        if df1.empty or df2.empty:
            return "❌ One or both catalogs returned no results", pd.DataFrame(), ""
        
        # Perform cross-matching
        matcher = get_cross_matcher()
        matched = matcher.match_catalogs(
            df1, df2,
            radius_arcsec=float(match_radius),
            min_confidence=0.5
        )
        
        if matched is None or len(matched) == 0:
            return "❌ No matches found", pd.DataFrame(), ""
        
        # Get statistics
        stats = matcher.get_match_statistics()
        
        status = f"""### Cross-Match Results
        
**Catalogs:** {catalog1} × {catalog2}
**Found:** {stats['matched_count']} matches
**Match rate:** {stats['match_rate']*100:.1f}%
**Mean confidence:** {stats['mean_confidence']:.3f}
**Mean separation:** {stats['mean_separation_arcsec']:.2f} arcsec
"""
        
        return status, matched.head(50), f"Total matches: {len(matched)}"
        
    except Exception as e:
        return f"❌ Error: {e}", pd.DataFrame(), ""


def plot_hz_comparison(teff, mass):
    """Plot habitable zone comparison."""
    try:
        from habitable_zone import hz_from_star_params, hz_traditional, stellar_luminosity, L_sun
        teff_val = float(teff)
        mass_val = float(mass)
        
        # Calculate HZ
        result = hz_from_star_params(teff_val, mass_msun=mass_val, method='ssz')
        
        # Traditional HZ
        L = stellar_luminosity(result['star_radius_rsun'], teff_val)
        L_lsun = L / L_sun
        inner_trad, outer_trad = hz_traditional(L_lsun, conservative=True)
        
        # Create plot
        fig = go.Figure()
        
        # Traditional HZ
        fig.add_trace(go.Scatter(
            x=[inner_trad, outer_trad],
            y=[1, 1],
            mode='markers+lines',
            name='Traditional HZ',
            marker=dict(size=12, color='blue'),
            line=dict(width=4, color='lightblue')
        ))
        
        # SSZ HZ
        fig.add_trace(go.Scatter(
            x=[result['hz_inner_au'], result['hz_outer_au']],
            y=[0.5, 0.5],
            mode='markers+lines',
            name='SSZ HZ',
            marker=dict(size=12, color='red'),
            line=dict(width=4, color='lightcoral')
        ))
        
        # Reference planets
        fig.add_trace(go.Scatter(
            x=[1.0],
            y=[0.75],
            mode='markers',
            name='Earth (1 AU)',
            marker=dict(size=15, color='green', symbol='star')
        ))
        
        fig.update_layout(
            title=f"Habitable Zone: T_eff={teff_val}K, M={mass_val}M_sun",
            xaxis_title="Distance (AU)",
            yaxis_title="",
            yaxis=dict(showticklabels=False, range=[0, 1.5]),
            height=400,
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Error: {e}", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig


def plot_sky_positions(df, title="Sky Positions"):
    """Plot object positions on sky (replaced by create_sky_map)."""
    return create_sky_map(df, title)


def generate_sky_map():
    """Generate sky map with GUARANTEED data!"""
    global last_query_data
    
    # ALWAYS load default universe as fallback
    from star_map_generator import create_default_universe
    
    # If we have query data, use it, otherwise use default universe
    if last_query_data is not None and not last_query_data.empty:
        try:
            return create_sky_map(last_query_data, f"Sky Map ({len(last_query_data)} objects)")
        except Exception as e:
            print(f"Error creating sky map from query data: {e}")
            # Fall through to default
    
    # Default: Famous objects from our universe
    universe = create_default_universe()
    return create_sky_map(
        universe, 
        title="🌌 Our Universe - Famous Objects (Default View)<br>"
              "<sub>Query catalogs in 'Multi-Catalog Search' tab for real data!</sub>"
    )


def generate_3d_sky_map():
    """Generate 3D sky map with GUARANTEED data!"""
    global last_query_data
    
    # ALWAYS have fallback ready
    from star_map_generator import create_default_universe, create_3d_sky_map
    
    # If we have query data, use it
    if last_query_data is not None and not last_query_data.empty:
        try:
            return create_3d_sky_map(last_query_data, f"3D Sky Map ({len(last_query_data)} objects)")
        except Exception as e:
            print(f"Error creating 3D map from query data: {e}")
            # Fall through to default
    
    # Default: Famous objects from our universe
    universe = create_default_universe()
    return create_3d_sky_map(universe, "🌌 Our Universe - 3D View (Default)<br><sub>Query catalogs for real data!</sub>")


def generate_constellation_map(ra, dec, fov):
    """Generate 3D REGION MAP - Like 3D Sky Map but focused on region!"""
    try:
        # Use NEW 3D region map
        use_3d_region = True
        
        if use_3d_region:
            try:
                from progressive_sky_map import create_progressive_constellation_map_3d
                
                fig, stats = create_progressive_constellation_map_3d(
                    ra_center=float(ra),
                    dec_center=float(dec),
                    fov=float(fov),
                    catalog_name='gaia',
                    max_objects=128000,  # MASSIVE DATABASE!
                    initial_display=2000  # 2K objects for region!
                )
                
                return fig
                
            except Exception as e:
                print(f"3D region map failed: {e}")
                import traceback
                traceback.print_exc()
                # Fallback below
        
        # Fallback: old 2D method
        return create_constellation_map(float(ra), float(dec), float(fov))
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Error: {e}", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig


# Build Gradio Interface
with gr.Blocks(title="SSZ Explorer - Complete Edition", theme=gr.themes.Soft()) as app:
    
    gr.Markdown("""
    # 🌌 SSZ Explorer - Complete Edition
    
    **All 7 Catalogs | Exoplanets | Cross-Matching | SSZ Physics**
    
    Explore 3.2 billion+ astronomical objects with Segmented Spacetime corrections!
    """)
    
    with gr.Tabs():
        
        # Tab 1: Multi-Catalog Query
        with gr.Tab("🔍 Multi-Catalog Search"):
            gr.Markdown("### Query Any Catalog")
            
            with gr.Row():
                catalog_select = gr.Dropdown(
                    choices=["GAIA DR3", "SIMBAD", "2MASS", "WISE", "NED", "SDSS"],
                    value="GAIA DR3",
                    label="Select Catalog"
                )
            
            with gr.Row():
                with gr.Column():
                    ra_input = gr.Number(value=266.4, label="RA (degrees)")
                    dec_input = gr.Number(value=-29.0, label="Dec (degrees)")
                    radius_input = gr.Number(value=5.0, label="Radius (arcmin)")
                    search_btn = gr.Button("🔍 Search", variant="primary")
                
                with gr.Column():
                    status_out = gr.Textbox(label="Status", lines=2)
            
            results_table = gr.Dataframe(label="Results (Preview - First 20 rows)", interactive=False)
            
            with gr.Row():
                download_btn = gr.DownloadButton("📥 Download Complete CSV", variant="secondary")
                gr.Markdown("**Download includes ALL results, not just preview!**")
            
            search_btn.click(
                fn=query_multi_catalog,
                inputs=[catalog_select, ra_input, dec_input, radius_input],
                outputs=[status_out, results_table]
            )
            
            download_btn.click(
                fn=download_csv,
                inputs=[],
                outputs=download_btn
            )
        
        # Tab 2: Exoplanets
        with gr.Tab("🪐 Exoplanets"):
            gr.Markdown("### Search Exoplanets (5,500+ planets!)")
            
            with gr.Row():
                with gr.Column():
                    host_input = gr.Textbox(label="Host Star Name (e.g., Kepler-186)", value="")
                    min_mass = gr.Number(label="Min Mass (M_jupiter)", value="")
                    max_mass = gr.Number(label="Max Mass (M_jupiter)", value="")
                    exo_search_btn = gr.Button("🔍 Search Planets", variant="primary")
                
                with gr.Column():
                    exo_status = gr.Textbox(label="Status", lines=2)
            
            exo_table = gr.Dataframe(label="Found Exoplanets", interactive=False)
            
            exo_search_btn.click(
                fn=search_exoplanets,
                inputs=[host_input, min_mass, max_mass],
                outputs=[exo_status, exo_table]
            )
        
        # Tab 3: Habitable Zone Calculator
        with gr.Tab("🌍 Habitable Zone"):
            gr.Markdown("### Calculate Habitable Zone (Traditional + SSZ)")
            
            with gr.Row():
                with gr.Column():
                    hz_teff = gr.Number(value=5778, label="Star T_eff (K)")
                    hz_mass = gr.Number(value=1.0, label="Star Mass (M_sun)")
                    hz_planet_dist = gr.Number(value=1.0, label="Planet Distance (AU)")
                    hz_calc_btn = gr.Button("Calculate HZ", variant="primary")
                
                with gr.Column():
                    hz_output = gr.Markdown("Results will appear here...")
            
            hz_calc_btn.click(
                fn=calculate_habitable_zone,
                inputs=[hz_teff, hz_mass, hz_planet_dist],
                outputs=hz_output
            )
        
        # Tab 4: Cross-Matching
        with gr.Tab("🔗 Cross-Matching"):
            gr.Markdown("### Match Objects Across Catalogs")
            
            with gr.Row():
                with gr.Column():
                    cm_cat1 = gr.Dropdown(
                        choices=["GAIA DR3", "SIMBAD", "2MASS", "WISE"],
                        value="GAIA DR3",
                        label="Catalog 1"
                    )
                    cm_cat2 = gr.Dropdown(
                        choices=["GAIA DR3", "SIMBAD", "2MASS", "WISE"],
                        value="SIMBAD",
                        label="Catalog 2"
                    )
                
                with gr.Column():
                    cm_ra = gr.Number(value=266.4, label="RA (degrees)")
                    cm_dec = gr.Number(value=-29.0, label="Dec (degrees)")
            
            with gr.Row():
                with gr.Column():
                    cm_radius = gr.Number(value=5.0, label="Search Radius (arcmin)")
                    cm_match_radius = gr.Number(value=2.0, label="Match Radius (arcsec)")
                    cm_match_btn = gr.Button("🔗 Match Catalogs", variant="primary")
                
                with gr.Column():
                    cm_status = gr.Markdown("Status will appear here...")
            
            cm_results = gr.Dataframe(label="Matched Objects", interactive=False)
            cm_summary = gr.Textbox(label="Summary", lines=1)
            
            cm_match_btn.click(
                fn=cross_match_catalogs,
                inputs=[cm_cat1, cm_cat2, cm_ra, cm_dec, cm_radius, cm_match_radius],
                outputs=[cm_status, cm_results, cm_summary]
            )
        
        # Tab 5: SSZ Orbital Calculator
        with gr.Tab("⚛️ SSZ Orbits"):
            gr.Markdown("### Calculate Orbital Parameters (SSZ vs GR)")
            
            with gr.Row():
                with gr.Column():
                    orbit_period = gr.Number(value=365.0, label="Orbital Period (days)")
                    orbit_star_mass = gr.Number(value=1.0, label="Star Mass (M_sun)")
                    orbit_calc_btn = gr.Button("Calculate", variant="primary")
                
                with gr.Column():
                    orbit_output = gr.Markdown("Results will appear here...")
            
            orbit_calc_btn.click(
                fn=calculate_ssz_orbit,
                inputs=[orbit_period, orbit_star_mass],
                outputs=orbit_output
            )
        
        # Tab 6: Visualizations
        with gr.Tab("📊 Visualizations"):
            gr.Markdown("### Interactive Plots")
            
            with gr.Tabs():
                with gr.Tab("HZ Comparison"):
                    with gr.Row():
                        with gr.Column():
                            viz_hz_teff = gr.Number(value=5778, label="Star T_eff (K)")
                            viz_hz_mass = gr.Number(value=1.0, label="Star Mass (M_sun)")
                            viz_hz_btn = gr.Button("Plot HZ", variant="primary")
                        
                        with gr.Column():
                            hz_plot = gr.Plot(label="Habitable Zone Comparison")
                    
                    viz_hz_btn.click(
                        fn=plot_hz_comparison,
                        inputs=[viz_hz_teff, viz_hz_mass],
                        outputs=hz_plot
                    )
                
                with gr.Tab("Sky Map"):
                    gr.Markdown("### Interactive Star Map")
                    gr.Markdown("*Query objects in 'Multi-Catalog Search' tab first, then click 'Generate Sky Map'*")
                    
                    with gr.Row():
                        with gr.Column():
                            skymap_btn = gr.Button("Generate Sky Map", variant="primary")
                            skymap_3d_btn = gr.Button("Generate 3D Map")
                        
                        with gr.Column():
                            gr.Markdown("**Sky Map shows:**\n- Object positions (RA/Dec)\n- Interactive zoom/pan\n- Hover for details")
                    
                    sky_plot = gr.Plot(label="Sky Map")
                    
                    skymap_btn.click(
                        fn=generate_sky_map,
                        inputs=None,
                        outputs=sky_plot
                    )
                    
                    skymap_3d_btn.click(
                        fn=generate_3d_sky_map,
                        inputs=None,
                        outputs=sky_plot
                    )
                
                with gr.Tab("Constellation View"):
                    gr.Markdown("### Custom Region")
                    
                    with gr.Row():
                        with gr.Column():
                            const_ra = gr.Number(value=266.4, label="Center RA (deg)")
                            const_dec = gr.Number(value=-29.0, label="Center Dec (deg)")
                            const_fov = gr.Number(value=30, label="Field of View (deg)")
                            const_btn = gr.Button("Generate Region Map", variant="primary")
                        
                        with gr.Column():
                            const_plot = gr.Plot(label="Constellation Region")
                    
                    const_btn.click(
                        fn=generate_constellation_map,
                        inputs=[const_ra, const_dec, const_fov],
                        outputs=const_plot
                    )
                
                with gr.Tab("Progressive Loading"):
                    gr.Markdown("### 🔄 Progressive Object Loading")
                    gr.Markdown("**Load objects in distance shells - Click 'Load More' to expand!**")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("### 🎮 Controls")
                            
                            progressive_reset_btn = gr.Button("🔄 Reset View", variant="secondary")
                            
                            progressive_initial_btn = gr.Button("🚀 Initial Load (0-1000 pc)", variant="primary", size="lg")
                            
                            progressive_more_btn = gr.Button("➕ Load More Objects!", variant="primary", size="lg")
                            
                            shell_size = gr.Slider(
                                minimum=500,
                                maximum=5000,
                                value=2000,
                                step=500,
                                label="Shell Size (pc)",
                                info="Distance range per load"
                            )
                            
                            gr.Markdown("""
                            **How it works:**
                            1. Click "Initial Load" → 0-1000 pc
                            2. Click "Load More" → Next 2000 pc
                            3. Keep clicking → Infinite expansion!
                            
                            **Shell System:**
                            - Shell 1: 0-1000 pc
                            - Shell 2: 1000-3000 pc (if size=2000)
                            - Shell 3: 3000-5000 pc
                            - Shell N: ... → ∞
                            
                            **Color Coding:**
                            - ⭐ Yellow = Stars
                            - 🌍 Green = Planets
                            - ⚫ Blue = Black Holes
                            """)
                        
                        with gr.Column(scale=2):
                            progressive_plot = gr.Plot(label="Progressive 3D View")
                            progressive_info = gr.Markdown("**Click 'Initial Load' to start**")
                    
                    def progressive_reset():
                        reset_progressive_view()
                        return go.Figure(), "**View reset! Click 'Initial Load' to start**"
                    
                    def progressive_initial(shell_sz):
                        from progressive_loader import get_loader
                        loader = get_loader()
                        
                        if loader.full_data is None or len(loader.full_data) == 0:
                            from star_map_generator import create_default_universe
                            data = create_default_universe()
                        else:
                            data = loader.full_data
                        
                        reset_progressive_view()
                        fig, info = create_progressive_3d_view(data, load_more=False, shell_size=shell_sz)
                        
                        info_text = f"""
**📊 Loaded:** {info['total_loaded']:,} objects  
**📏 Range:** {info['current_range']}  
**🔢 Shells:** {info['shells_loaded']}  
**📍 Max Distance:** {info['max_distance']:.0f} pc  

*Click "Load More" to expand!*
                        """
                        
                        return fig, info_text
                    
                    def progressive_more(shell_sz):
                        from progressive_loader import get_loader
                        loader = get_loader()
                        
                        if loader.full_data is None or len(loader.full_data) == 0:
                            from star_map_generator import create_default_universe
                            data = create_default_universe()
                        else:
                            data = loader.full_data
                        
                        fig, info = create_progressive_3d_view(data, load_more=True, shell_size=shell_sz)
                        
                        info_text = f"""
**📊 Loaded:** {info['total_loaded']:,} objects  
**📏 Range:** {info['current_range']}  
**🔢 Shells:** {info['shells_loaded']}  
**📍 Max Distance:** {info['max_distance']:.0f} pc  

*Keep clicking to load more!*
                        """
                        
                        return fig, info_text
                    
                    progressive_reset_btn.click(
                        fn=progressive_reset,
                        inputs=None,
                        outputs=[progressive_plot, progressive_info]
                    )
                    
                    progressive_initial_btn.click(
                        fn=progressive_initial,
                        inputs=[shell_size],
                        outputs=[progressive_plot, progressive_info]
                    )
                    
                    progressive_more_btn.click(
                        fn=progressive_more,
                        inputs=[shell_size],
                        outputs=[progressive_plot, progressive_info]
                    )
                
                with gr.Tab("Interactive Navigation"):
                    gr.Markdown("### 🎮 Object-Centered Rotation")
                    gr.Markdown("**Select an object and rotate camera around it with full control!**")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("### 🎯 Object Selection")
                            
                            # Object dropdown
                            object_dropdown = gr.Dropdown(
                                label="Select Object to Center On",
                                choices=[("None - Origin", -1)],
                                value=-1,
                                interactive=True
                            )
                            
                            load_objects_btn = gr.Button("🔄 Load Object List", variant="secondary")
                            
                            gr.Markdown("### 📷 Camera Controls")
                            
                            # Camera distance
                            camera_distance = gr.Slider(
                                minimum=10,
                                maximum=5000,
                                value=500,
                                step=10,
                                label="Camera Distance (pc)",
                                interactive=True
                            )
                            
                            # Horizontal angle
                            camera_h_angle = gr.Slider(
                                minimum=0,
                                maximum=360,
                                value=0,
                                step=5,
                                label="Horizontal Angle (°)",
                                interactive=True
                            )
                            
                            # Vertical angle
                            camera_v_angle = gr.Slider(
                                minimum=-90,
                                maximum=90,
                                value=45,
                                step=5,
                                label="Vertical Angle (°)",
                                interactive=True
                            )
                            
                            gr.Markdown("### 🎬 Quick Actions")
                            
                            with gr.Row():
                                rotate_left_btn = gr.Button("⬅️ Left")
                                rotate_right_btn = gr.Button("➡️ Right")
                            
                            with gr.Row():
                                rotate_up_btn = gr.Button("⬆️ Up")
                                rotate_down_btn = gr.Button("⬇️ Down")
                            
                            update_view_btn = gr.Button("🔄 Update View", variant="primary", size="lg")
                        
                        with gr.Column(scale=2):
                            interactive_plot = gr.Plot(label="Object-Centered 3D View")
                            
                            view_info = gr.Markdown("**Select an object and adjust camera to start**")
                    
                    # Load object list function
                    def load_object_list():
                        from progressive_loader import get_loader
                        loader = get_loader()
                        
                        if loader.full_data is not None and len(loader.full_data) > 0:
                            obj_list = get_object_list(loader.full_data, max_items=100)
                            choices = [("None - Origin", -1)] + [(name, idx) for idx, name in obj_list]
                            return gr.Dropdown(choices=choices, value=-1)
                        else:
                            return gr.Dropdown(choices=[("None - Origin", -1)], value=-1)
                    
                    # Update view function
                    def update_view(obj_idx, cam_dist, cam_h, cam_v):
                        from progressive_loader import get_loader
                        loader = get_loader()
                        
                        if loader.full_data is None or len(loader.full_data) == 0:
                            from star_map_generator import create_default_universe
                            data = create_default_universe()
                        else:
                            # Sample for performance
                            import random
                            if len(loader.full_data) > 5000:
                                indices = random.sample(range(len(loader.full_data)), 5000)
                                data = loader.full_data.iloc[indices].copy()
                            else:
                                data = loader.full_data.copy()
                        
                        # Create view
                        selected_idx = None if obj_idx == -1 else obj_idx
                        fig, info = create_object_centered_view(
                            data,
                            selected_object_index=selected_idx,
                            camera_distance=cam_dist,
                            camera_angle_h=cam_h,
                            camera_angle_v=cam_v
                        )
                        
                        info_text = f"""
**🎯 Center:** {info['center_object']}  
**📍 Position:** ({info['center_position'][0]:.1f}, {info['center_position'][1]:.1f}, {info['center_position'][2]:.1f}) pc  
**📷 Distance:** {info['camera_distance']:.1f} pc  
**🔄 Angles:** H={info['camera_angles'][0]:.0f}° V={info['camera_angles'][1]:.0f}°  
**⭐ Objects:** {info['total_objects']:,}
                        """
                        
                        return fig, info_text
                    
                    # Rotation helper functions
                    def rotate_left(cam_h):
                        return cam_h - 15
                    
                    def rotate_right(cam_h):
                        return cam_h + 15
                    
                    def rotate_up(cam_v):
                        return min(cam_v + 15, 90)
                    
                    def rotate_down(cam_v):
                        return max(cam_v - 15, -90)
                    
                    # Wire up controls
                    load_objects_btn.click(
                        fn=load_object_list,
                        inputs=None,
                        outputs=object_dropdown
                    )
                    
                    update_view_btn.click(
                        fn=update_view,
                        inputs=[object_dropdown, camera_distance, camera_h_angle, camera_v_angle],
                        outputs=[interactive_plot, view_info]
                    )
                    
                    rotate_left_btn.click(
                        fn=rotate_left,
                        inputs=[camera_h_angle],
                        outputs=camera_h_angle
                    )
                    
                    rotate_right_btn.click(
                        fn=rotate_right,
                        inputs=[camera_h_angle],
                        outputs=camera_h_angle
                    )
                    
                    rotate_up_btn.click(
                        fn=rotate_up,
                        inputs=[camera_v_angle],
                        outputs=camera_v_angle
                    )
                    
                    rotate_down_btn.click(
                        fn=rotate_down,
                        inputs=[camera_v_angle],
                        outputs=camera_v_angle
                    )
        
        # Tab 7: SSZ Physics
        with gr.Tab("🔬 SSZ Physics"):
            gr.Markdown("### Segmented Spacetime Physics - g₁ and g₂ Domains")
            gr.Markdown("*Visualize the fundamental physics of SSZ metric*")
            
            with gr.Tabs():
                with gr.Tab("🎯 Object Physics"):
                    gr.Markdown("**Select an object to see its SSZ parameters on the curves!**")
                    gr.Markdown("*Red star shows selected object position on all curves*")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("### Select Object")
                            
                            physics_object_dropdown = gr.Dropdown(
                                label="Choose Object",
                                choices=[("None", -1)],
                                value=-1,
                                interactive=True
                            )
                            
                            physics_load_btn = gr.Button("🔄 Load Objects", variant="secondary")
                            
                            physics_update_btn = gr.Button("🔬 Show Physics", variant="primary", size="lg")
                            
                            gr.Markdown("""
                            **What you'll see:**
                            - 🟠 Orange/Cyan curves = Theory
                            - ⭐ Red star = Selected object
                            - 📊 Table = All SSZ parameters
                            - Domain indicator (g₁ or g₂)
                            """)
                        
                        with gr.Column(scale=2):
                            physics_plot = gr.Plot(label="SSZ Physics Analysis")
                            physics_info = gr.Markdown("**Select an object to see SSZ physics**")
                    
                    def load_physics_objects():
                        from progressive_loader import get_loader
                        loader = get_loader()
                        
                        if loader.full_data is not None and len(loader.full_data) > 0:
                            obj_list = get_object_list(loader.full_data, max_items=100)
                            choices = [("None", -1)] + [(name, idx) for idx, name in obj_list]
                            return gr.Dropdown(choices=choices, value=-1)
                        else:
                            return gr.Dropdown(choices=[("None", -1)], value=-1)
                    
                    def show_physics(obj_idx):
                        from progressive_loader import get_loader
                        loader = get_loader()
                        
                        if loader.full_data is None or len(loader.full_data) == 0:
                            from star_map_generator import create_default_universe
                            data = create_default_universe()
                        else:
                            data = loader.full_data
                        
                        selected_idx = None if obj_idx == -1 else obj_idx
                        fig, info = create_combined_physics_view(data, selected_idx)
                        
                        if info['has_data']:
                            info_text = f"""
**🎯 Selected:** {info['selected_object']}  
**📊 SSZ Parameters:**  
- **r/r_s:** {info['r_ratio']:.2f}  
- **Ξ(r):** {info['xi']:.6f}  
- **D_SSZ(r):** {info['d_ssz']:.6f}  
- **Stretch:** {info['stretch']:.6f}  

*Red star marks object position on all curves!*
                            """
                        else:
                            info_text = "**Select an object to see its SSZ parameters**"
                        
                        return fig, info_text
                    
                    physics_load_btn.click(
                        fn=load_physics_objects,
                        inputs=None,
                        outputs=physics_object_dropdown
                    )
                    
                    physics_update_btn.click(
                        fn=show_physics,
                        inputs=[physics_object_dropdown],
                        outputs=[physics_plot, physics_info]
                    )
                
                with gr.Tab("g₁/g₂ Domains"):
                    gr.Markdown("**Segment density Ξ(r) showing inner (g₂) and outer (g₁) domains**")
                    gr.Markdown("*Yellow stars = Real objects from current maps!*")
                    domains_btn = gr.Button("Plot g₁/g₂ Domains with Real Objects", variant="primary")
                    domains_plot = gr.Plot(label="SSZ Domains")
                    
                    def plot_domains_with_objects():
                        # Get current objects from loader
                        from progressive_loader import get_loader
                        loader = get_loader()
                        objects_df = None
                        if loader.full_data is not None:
                            objects_df = loader.full_data
                        return create_g1_g2_domain_plot(objects_df)
                    
                    domains_btn.click(
                        fn=plot_domains_with_objects,
                        inputs=None,
                        outputs=domains_plot
                    )
                
                with gr.Tab("Time Dilation"):
                    gr.Markdown("**Compare SSZ vs GR time dilation across domains**")
                    gr.Markdown("*Yellow stars = Real objects from current maps!*")
                    dilation_btn = gr.Button("Plot Time Dilation with Real Objects", variant="primary")
                    dilation_plot = gr.Plot(label="Time Dilation Comparison")
                    
                    def plot_dilation_with_objects():
                        from progressive_loader import get_loader
                        loader = get_loader()
                        objects_df = None
                        if loader.full_data is not None:
                            objects_df = loader.full_data
                        return create_time_dilation_comparison(objects_df)
                    
                    dilation_btn.click(
                        fn=plot_dilation_with_objects,
                        inputs=None,
                        outputs=dilation_plot
                    )
                
                with gr.Tab("Radial Stretch"):
                    gr.Markdown("**Radial stretch factor showing domain structure**")
                    gr.Markdown("*Yellow stars = Real objects from current maps!*")
                    stretch_btn = gr.Button("Plot Radial Stretch with Real Objects", variant="primary")
                    stretch_plot = gr.Plot(label="Radial Stretch")
                    
                    def plot_stretch_with_objects():
                        from progressive_loader import get_loader
                        loader = get_loader()
                        objects_df = None
                        if loader.full_data is not None:
                            objects_df = loader.full_data
                        return create_radial_stretch_plot(objects_df)
                    
                    stretch_btn.click(
                        fn=plot_stretch_with_objects,
                        inputs=None,
                        outputs=stretch_plot
                    )
                
                with gr.Tab("Combined Analysis"):
                    gr.Markdown("**Complete SSZ physics overview - Theoretical curves**")
                    gr.Markdown("*Shows 4 key SSZ metrics in one view*")
                    combined_btn = gr.Button("Plot Combined Analysis", variant="primary")
                    combined_plot = gr.Plot(label="Combined SSZ Analysis")
                    
                    combined_btn.click(
                        fn=lambda: create_combined_ssz_analysis(),
                        inputs=None,
                        outputs=combined_plot
                    )
        
        # Tab 8: Info
        with gr.Tab("ℹ️ Info"):
            gr.Markdown("""
            ## 🌌 SSZ Explorer - Complete Edition
            
            ### Available Catalogs (7):
            1. **GAIA DR3** - 1.8 billion stars
            2. **SIMBAD** - 11 million objects
            3. **2MASS** - 470 million infrared sources
            4. **WISE** - 747 million mid-IR sources
            5. **Exoplanets** - 5,500+ confirmed planets
            6. **NED** - 200 million+ galaxies
            7. **SDSS** - 1 million+ galaxies with spectra
            
            ### Total: 3.2 BILLION+ Objects! 🌟
            
            ### SSZ Features:
            - Golden ratio (φ) based physics
            - Orbital corrections
            - Habitable zone calculations
            - Transit predictions
            - Cosmological corrections
            
            ### Documentation:
            - [GitHub Repository](https://github.com/error-wtf/Segmented-Spacetime-Starmaps)
            - [Quick Reference](QUICK_REFERENCE.md)
            - [Complete Roadmap](COMPLETE_ROADMAP.md)
            
            **© 2025 Carmen Wrede, Lino Casu** | ACSL v1.4
            """)


def launch_app(share=False, port=7860):
    """Launch the extended Gradio app."""
    app.launch(share=share, server_name="0.0.0.0", server_port=port, inbrowser=True)


if __name__ == "__main__":
    print("="*80)
    print("SSZ EXPLORER - COLOR CODED!")
    print("="*80)
    print("⭐ GELB = Stars | 🌍 GRÜN = Planets | ⚫ BLAU = Black Holes!")
    print("🎯 Object Selector + 🔬 Physics!")
    print("📊 Full SSZ Analysis + Color Coding!")
    print("Launching on PORT 9400...")
    print("="*80)
    
    launch_app(share=False, port=9400)
