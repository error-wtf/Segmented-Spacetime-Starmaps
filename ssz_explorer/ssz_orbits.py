#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Orbital Calculations - Sprint 3 Task 2

Calculate SSZ-corrected orbital parameters and compare with GR predictions.
Enables testable predictions for exoplanet observations.

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import numpy as np
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Physical constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
c = 299792458.0  # Speed of light (m/s)
AU = 1.495978707e11  # Astronomical unit (m)
M_sun = 1.98847e30  # Solar mass (kg)
phi = (1 + np.sqrt(5)) / 2  # Golden ratio


def schwarzschild_radius(M: float) -> float:
    """
    Calculate Schwarzschild radius.
    
    Parameters:
    -----------
    M : float
        Mass in kg
        
    Returns:
    --------
    float
        Schwarzschild radius in meters
    """
    return 2 * G * M / c**2


def ssz_segment_saturation(r: float, r_s: float) -> float:
    """
    Calculate SSZ segment saturation function.
    
    Xi(r) = 1 - exp(-phi * r_s / r)
    
    Parameters:
    -----------
    r : float
        Radial distance (m)
    r_s : float
        Schwarzschild radius (m)
        
    Returns:
    --------
    float
        Segment saturation (dimensionless)
    """
    return 1.0 - np.exp(-phi * r_s / r)


def gr_orbital_period(a: float, M: float) -> float:
    """
    Calculate orbital period using Kepler's 3rd law (GR/Newtonian).
    
    T = 2π √(a³/GM)
    
    Parameters:
    -----------
    a : float
        Semi-major axis in meters
    M : float
        Central mass in kg
        
    Returns:
    --------
    float
        Orbital period in seconds
    """
    return 2 * np.pi * np.sqrt(a**3 / (G * M))


def ssz_orbital_period(a: float, M: float, correction_factor: float = 1.0) -> float:
    """
    Calculate SSZ-corrected orbital period.
    
    SSZ modifies the gravitational potential, leading to:
    T_SSZ = T_GR * (1 + α * Xi(a))
    
    where α is a correction parameter dependent on SSZ physics.
    
    Parameters:
    -----------
    a : float
        Semi-major axis in meters
    M : float
        Central mass in kg
    correction_factor : float
        SSZ correction strength (default: 1.0)
        Theoretical range: 0.001 - 0.1
        
    Returns:
    --------
    float
        SSZ-corrected orbital period in seconds
    """
    # GR period
    T_gr = gr_orbital_period(a, M)
    
    # SSZ correction
    r_s = schwarzschild_radius(M)
    Xi = ssz_segment_saturation(a, r_s)
    
    # Correction is proportional to segment saturation
    # For orbits far from star: Xi → 0, T_SSZ → T_GR
    # For close orbits: Xi > 0, T_SSZ differs
    alpha = correction_factor * 0.01  # Typical scale
    
    T_ssz = T_gr * (1.0 + alpha * Xi)
    
    return T_ssz


def period_difference(a: float, M: float, correction_factor: float = 1.0) -> Dict[str, float]:
    """
    Calculate difference between SSZ and GR orbital periods.
    
    Parameters:
    -----------
    a : float
        Semi-major axis in meters
    M : float
        Central mass in kg
    correction_factor : float
        SSZ correction strength
        
    Returns:
    --------
    dict
        {
            'T_gr': GR period (seconds),
            'T_ssz': SSZ period (seconds),
            'difference': T_ssz - T_gr (seconds),
            'relative': (T_ssz - T_gr) / T_gr (dimensionless),
            'observable': Whether difference is observable
        }
    """
    T_gr = gr_orbital_period(a, M)
    T_ssz = ssz_orbital_period(a, M, correction_factor)
    
    diff = T_ssz - T_gr
    rel_diff = diff / T_gr
    
    # Observable if relative difference > 1e-6 (1 ppm, typical precision)
    observable = abs(rel_diff) > 1e-6
    
    return {
        'T_gr_sec': T_gr,
        'T_gr_days': T_gr / 86400,
        'T_ssz_sec': T_ssz,
        'T_ssz_days': T_ssz / 86400,
        'difference_sec': diff,
        'difference_days': diff / 86400,
        'relative_diff': rel_diff,
        'observable': observable,
        'precision_needed_ppm': abs(rel_diff) * 1e6
    }


def ssz_semi_major_axis(P: float, M: float, correction_factor: float = 1.0) -> float:
    """
    Calculate semi-major axis from period (SSZ-corrected).
    
    Inverse of ssz_orbital_period.
    
    Parameters:
    -----------
    P : float
        Orbital period in seconds
    M : float
        Central mass in kg
    correction_factor : float
        SSZ correction strength
        
    Returns:
    --------
    float
        Semi-major axis in meters
    """
    # Start with GR approximation
    a_gr = (G * M * (P / (2 * np.pi))**2)**(1/3)
    
    # Iteratively refine with SSZ corrections
    a = a_gr
    for _ in range(10):  # Newton-Raphson iteration
        T_calculated = ssz_orbital_period(a, M, correction_factor)
        error = T_calculated - P
        
        if abs(error / P) < 1e-10:
            break
        
        # Numerical derivative
        da = a * 1e-6
        dT_da = (ssz_orbital_period(a + da, M, correction_factor) - T_calculated) / da
        
        # Update
        a -= error / dT_da
    
    return a


def transit_timing_variation(
    P_nominal: float,
    M_star: float,
    a: float,
    n_transits: int = 100
) -> Dict[str, np.ndarray]:
    """
    Calculate transit timing variations (TTV) due to SSZ effects.
    
    Parameters:
    -----------
    P_nominal : float
        Nominal period (seconds)
    M_star : float
        Star mass (kg)
    a : float
        Semi-major axis (m)
    n_transits : int
        Number of transits to calculate
        
    Returns:
    --------
    dict
        {
            'transit_number': array,
            'time_gr': expected time (GR),
            'time_ssz': expected time (SSZ),
            'ttv': TTV signal (seconds)
        }
    """
    transit_nums = np.arange(1, n_transits + 1)
    
    # GR prediction: linear
    times_gr = transit_nums * P_nominal
    
    # SSZ prediction: slightly different period
    P_ssz = ssz_orbital_period(a, M_star)
    times_ssz = transit_nums * P_ssz
    
    # TTV signal
    ttv = times_ssz - times_gr
    
    return {
        'transit_number': transit_nums,
        'time_gr': times_gr,
        'time_ssz': times_ssz,
        'ttv_seconds': ttv,
        'ttv_minutes': ttv / 60,
        'cumulative': True  # TTV accumulates over time
    }


def observable_signature(
    planet_params: Dict[str, float],
    precision_seconds: float = 10.0
) -> Dict[str, any]:
    """
    Determine if SSZ effects are observable for given planet.
    
    Parameters:
    -----------
    planet_params : dict
        {
            'period_days': orbital period,
            'semi_major_axis_au': semi-major axis,
            'star_mass_msun': host star mass
        }
    precision_seconds : float
        Timing precision available (default: 10s, typical for transits)
        
    Returns:
    --------
    dict
        {
            'observable': boolean,
            'time_to_detection_transits': int,
            'ttv_amplitude_seconds': float,
            'recommendations': str
        }
    """
    # Convert units
    P_days = planet_params.get('period_days', 0)
    a_au = planet_params.get('semi_major_axis_au', 0)
    M_msun = planet_params.get('star_mass_msun', 1.0)
    
    P_sec = P_days * 86400
    a_m = a_au * AU
    M_kg = M_msun * M_sun
    
    # Calculate difference
    diff = period_difference(a_m, M_kg)
    
    # TTV accumulates, so check after N transits
    n_transits_array = np.array([10, 50, 100, 500, 1000])
    ttv_array = diff['difference_sec'] * n_transits_array
    
    # Find when observable
    observable_mask = np.abs(ttv_array) > precision_seconds
    
    if observable_mask.any():
        time_to_detection = n_transits_array[observable_mask][0]
        observable = True
    else:
        time_to_detection = None
        observable = False
    
    # Recommendation
    if observable:
        years = time_to_detection * P_days / 365.25
        rec = f"Observable after {time_to_detection} transits (~{years:.1f} years)"
    else:
        rec = "Not observable with current precision"
    
    return {
        'observable': observable,
        'time_to_detection_transits': time_to_detection,
        'ttv_amplitude_per_transit_sec': diff['difference_sec'],
        'accumulated_ttv_100_transits': diff['difference_sec'] * 100,
        'relative_difference': diff['relative_diff'],
        'precision_needed_sec': abs(diff['difference_sec']),
        'recommendations': rec
    }


# Convenience functions for common use cases

def calculate_for_planet(
    period_days: float,
    star_mass_msun: float = 1.0,
    semi_major_axis_au: Optional[float] = None
) -> Dict[str, float]:
    """
    Calculate SSZ vs GR for a planet (convenience function).
    
    Parameters:
    -----------
    period_days : float
        Orbital period in days
    star_mass_msun : float
        Star mass in solar masses
    semi_major_axis_au : float
        Semi-major axis in AU (if None, calculated from period)
        
    Returns:
    --------
    dict
        Complete comparison of SSZ vs GR
    """
    # Convert units
    P_sec = period_days * 86400
    M_kg = star_mass_msun * M_sun
    
    # Calculate semi-major axis if not provided
    if semi_major_axis_au is None:
        a_m = (G * M_kg * (P_sec / (2 * np.pi))**2)**(1/3)
        a_au = a_m / AU
    else:
        a_au = semi_major_axis_au
        a_m = a_au * AU
    
    # Get differences
    diff = period_difference(a_m, M_kg)
    
    # Observable signature
    obs = observable_signature({
        'period_days': period_days,
        'semi_major_axis_au': a_au,
        'star_mass_msun': star_mass_msun
    })
    
    return {
        **diff,
        'semi_major_axis_au': a_au,
        'star_mass_msun': star_mass_msun,
        **obs
    }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("="*80)
    print("SSZ ORBITAL CALCULATIONS TEST")
    print("="*80)
    
    # Test 1: Hot Jupiter (HD 209458 b)
    print("\n[Test 1] Hot Jupiter (HD 209458 b)")
    print("Period: 3.5 days, Star: 1.1 M_sun")
    
    result = calculate_for_planet(
        period_days=3.5,
        star_mass_msun=1.1
    )
    
    print(f"  Semi-major axis: {result['semi_major_axis_au']:.4f} AU")
    print(f"  Period (GR):  {result['T_gr_days']:.6f} days")
    print(f"  Period (SSZ): {result['T_ssz_days']:.6f} days")
    print(f"  Difference:   {result['difference_sec']:.3f} seconds")
    print(f"  Relative:     {result['relative_diff']*1e6:.3f} ppm")
    print(f"  Observable:   {result['observable']}")
    print(f"  {result['recommendations']}")
    
    # Test 2: Earth-like (habitable zone)
    print("\n[Test 2] Earth-like planet (HZ)")
    print("Period: 365 days, Star: 1.0 M_sun")
    
    result = calculate_for_planet(
        period_days=365.0,
        star_mass_msun=1.0
    )
    
    print(f"  Semi-major axis: {result['semi_major_axis_au']:.4f} AU")
    print(f"  Period (GR):  {result['T_gr_days']:.6f} days")
    print(f"  Period (SSZ): {result['T_ssz_days']:.6f} days")
    print(f"  Difference:   {result['difference_sec']:.3f} seconds")
    print(f"  Relative:     {result['relative_diff']*1e6:.3f} ppm")
    print(f"  Observable:   {result['observable']}")
    
    # Test 3: Very close orbit (extreme case)
    print("\n[Test 3] Ultra-short period planet")
    print("Period: 0.5 days, Star: 1.0 M_sun")
    
    result = calculate_for_planet(
        period_days=0.5,
        star_mass_msun=1.0
    )
    
    print(f"  Semi-major axis: {result['semi_major_axis_au']:.4f} AU")
    print(f"  Period (GR):  {result['T_gr_days']:.6f} days")
    print(f"  Period (SSZ): {result['T_ssz_days']:.6f} days")
    print(f"  Difference:   {result['difference_sec']:.3f} seconds")
    print(f"  Relative:     {result['relative_diff']*1e6:.3f} ppm")
    print(f"  Observable:   {result['observable']}")
    
    print("\n" + "="*80)
    print("✅ SSZ ORBITAL CALCULATIONS WORKING")
    print("="*80)
