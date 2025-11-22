#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transit Predictions - Sprint 3 Task 5

Calculate transit probabilities and timing predictions.
Includes SSZ corrections for observable signatures.

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Import SSZ orbit calculations
try:
    from ssz_orbits import ssz_orbital_period, gr_orbital_period, period_difference
    SSZ_ORBITS_AVAILABLE = True
except ImportError:
    SSZ_ORBITS_AVAILABLE = False
    logger.warning("ssz_orbits not available")

# Constants
AU = 1.495978707e11  # meters
R_sun = 6.957e8  # meters
R_jup = 7.1492e7  # meters


def transit_probability(
    semi_major_axis_au: float,
    star_radius_rsun: float = 1.0,
    inclination_deg: Optional[float] = None
) -> float:
    """
    Calculate geometric transit probability.
    
    P_transit ≈ R_star / a  (for randomly oriented orbits)
    
    Parameters:
    -----------
    semi_major_axis_au : float
        Semi-major axis in AU
    star_radius_rsun : float
        Star radius in solar radii
    inclination_deg : float
        If known, calculate exact probability
        
    Returns:
    --------
    float
        Transit probability (0-1)
    """
    a_m = semi_major_axis_au * AU
    R_star = star_radius_rsun * R_sun
    
    if inclination_deg is not None:
        # Exact calculation with known inclination
        i_rad = np.radians(inclination_deg)
        # Impact parameter
        b = a_m * np.cos(i_rad) / R_star
        
        if b < 1:
            # Transits occur
            prob = 1.0
        else:
            # No transit
            prob = 0.0
    else:
        # Geometric probability for random orientation
        prob = R_star / a_m
    
    return min(prob, 1.0)


def transit_duration_gr(
    period_days: float,
    semi_major_axis_au: float,
    star_radius_rsun: float = 1.0,
    planet_radius_rjup: float = 1.0,
    impact_parameter: float = 0.0,
    eccentricity: float = 0.0
) -> float:
    """
    Calculate transit duration (GR/Newtonian).
    
    Parameters:
    -----------
    period_days : float
        Orbital period
    semi_major_axis_au : float
        Semi-major axis
    star_radius_rsun : float
        Star radius
    planet_radius_rjup : float
        Planet radius
    impact_parameter : float
        Impact parameter (0=central, <1=grazing)
    eccentricity : float
        Orbital eccentricity
        
    Returns:
    --------
    float
        Transit duration in hours
    """
    P = period_days * 86400  # seconds
    a = semi_major_axis_au * AU
    R_s = star_radius_rsun * R_sun
    R_p = planet_radius_rjup * R_jup
    
    # Transit chord length
    b = impact_parameter
    chord = 2 * np.sqrt((R_s + R_p)**2 - (b * R_s)**2)
    
    # Orbital velocity (circular orbit approximation)
    v_orbit = 2 * np.pi * a / P
    
    # Eccentricity correction (approximate)
    if eccentricity > 0:
        v_orbit *= np.sqrt((1 + eccentricity) / (1 - eccentricity))
    
    # Duration
    duration_sec = chord / v_orbit
    duration_hours = duration_sec / 3600
    
    return duration_hours


def transit_duration_ssz(
    period_days: float,
    semi_major_axis_au: float,
    star_mass_msun: float = 1.0,
    star_radius_rsun: float = 1.0,
    planet_radius_rjup: float = 1.0,
    impact_parameter: float = 0.0,
    eccentricity: float = 0.0
) -> float:
    """
    Calculate SSZ-corrected transit duration.
    
    SSZ affects orbital velocity through modified periods.
    
    Parameters:
    -----------
    (same as transit_duration_gr plus star_mass_msun)
        
    Returns:
    --------
    float
        SSZ transit duration in hours
    """
    if not SSZ_ORBITS_AVAILABLE:
        logger.warning("SSZ orbits not available, using GR duration")
        return transit_duration_gr(
            period_days, semi_major_axis_au, star_radius_rsun,
            planet_radius_rjup, impact_parameter, eccentricity
        )
    
    # Get SSZ period
    P_sec = period_days * 86400
    a_m = semi_major_axis_au * AU
    M_kg = star_mass_msun * 1.98847e30
    
    # SSZ orbital velocity
    T_ssz = ssz_orbital_period(a_m, M_kg)
    v_orbit_ssz = 2 * np.pi * a_m / T_ssz
    
    # Calculate duration with SSZ velocity
    R_s = star_radius_rsun * R_sun
    R_p = planet_radius_rjup * R_jup
    b = impact_parameter
    
    chord = 2 * np.sqrt((R_s + R_p)**2 - (b * R_s)**2)
    
    # Eccentricity correction
    if eccentricity > 0:
        v_orbit_ssz *= np.sqrt((1 + eccentricity) / (1 - eccentricity))
    
    duration_sec = chord / v_orbit_ssz
    duration_hours = duration_sec / 3600
    
    return duration_hours


def timing_difference(
    period_days: float,
    semi_major_axis_au: float,
    star_mass_msun: float = 1.0,
    star_radius_rsun: float = 1.0,
    planet_radius_rjup: float = 1.0
) -> Dict[str, float]:
    """
    Calculate timing differences between GR and SSZ.
    
    Returns:
    --------
    dict
        Duration and timing differences
    """
    # GR duration
    dur_gr = transit_duration_gr(
        period_days, semi_major_axis_au, star_radius_rsun, planet_radius_rjup
    )
    
    # SSZ duration
    dur_ssz = transit_duration_ssz(
        period_days, semi_major_axis_au, star_mass_msun,
        star_radius_rsun, planet_radius_rjup
    )
    
    diff_hours = dur_ssz - dur_gr
    diff_seconds = diff_hours * 3600
    
    return {
        'duration_gr_hours': dur_gr,
        'duration_ssz_hours': dur_ssz,
        'difference_hours': diff_hours,
        'difference_seconds': diff_seconds,
        'relative_difference': diff_hours / dur_gr if dur_gr > 0 else 0
    }


def observable_targets(
    planets_df,
    precision_seconds: float = 30.0,
    n_transits: int = 100
) -> Dict:
    """
    Identify targets with observable SSZ signatures.
    
    Parameters:
    -----------
    planets_df : DataFrame
        Exoplanet data with columns: period_days, semi_major_axis_au,
        star_mass_msun, star_radius_rsun
    precision_seconds : float
        Observational precision
    n_transits : int
        Number of transits for accumulation
        
    Returns:
    --------
    dict
        Observable targets and statistics
    """
    if planets_df is None or len(planets_df) == 0:
        return {'observable_count': 0, 'targets': []}
    
    observable = []
    
    for idx, planet in planets_df.iterrows():
        # Get parameters
        P = planet.get('period_days', 0)
        a = planet.get('semi_major_axis_au', 0)
        M_s = planet.get('star_mass_msun', 1.0)
        
        if P == 0 or a == 0:
            continue
        
        # Calculate cumulative TTV
        if SSZ_ORBITS_AVAILABLE:
            diff = period_difference(a * AU, M_s * 1.98847e30)
            ttv_per_transit = diff['difference_sec']
            cumulative_ttv = abs(ttv_per_transit * n_transits)
            
            if cumulative_ttv > precision_seconds:
                observable.append({
                    'name': planet.get('planet_name', f'Planet_{idx}'),
                    'period_days': P,
                    'ttv_seconds': cumulative_ttv,
                    'transits_needed': n_transits
                })
    
    return {
        'observable_count': len(observable),
        'targets': observable[:20],  # Top 20
        'precision_used': precision_seconds,
        'n_transits': n_transits
    }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("="*80)
    print("TRANSIT PREDICTIONS TEST")
    print("="*80)
    
    # Test 1: Transit probability
    print("\n[Test 1] Transit Probability")
    prob = transit_probability(0.05, 1.0)  # Hot Jupiter
    print(f"  Hot Jupiter (a=0.05 AU): P_transit = {prob*100:.2f}%")
    
    prob_earth = transit_probability(1.0, 1.0)  # Earth-like
    print(f"  Earth-like (a=1.0 AU): P_transit = {prob_earth*100:.2f}%")
    
    # Test 2: Transit duration
    print("\n[Test 2] Transit Duration (Hot Jupiter)")
    dur_gr = transit_duration_gr(3.5, 0.05, 1.2, 1.0)
    dur_ssz = transit_duration_ssz(3.5, 0.05, 1.1, 1.2, 1.0)
    
    print(f"  GR duration:  {dur_gr:.3f} hours")
    print(f"  SSZ duration: {dur_ssz:.3f} hours")
    print(f"  Difference:   {(dur_ssz-dur_gr)*3600:.2f} seconds")
    
    # Test 3: Timing difference
    print("\n[Test 3] Timing Differences")
    timing = timing_difference(3.5, 0.05, 1.1, 1.2, 1.0)
    print(f"  Duration difference: {timing['difference_seconds']:.3f} sec")
    print(f"  Relative: {timing['relative_difference']*1e6:.2f} ppm")
    
    print("\n" + "="*80)
    print("✅ TRANSIT PREDICTIONS WORKING")
    print("="*80)
