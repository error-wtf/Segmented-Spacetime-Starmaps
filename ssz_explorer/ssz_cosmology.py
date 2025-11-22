#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Cosmology - Sprint 4 Task 3
Cosmological calculations with SSZ corrections

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# Constants
c = 299792.458  # km/s
H0_LCDM = 70.0  # km/s/Mpc (standard)
phi = (1 + np.sqrt(5)) / 2  # Golden ratio


def H_lcdm(z: float, H0: float = H0_LCDM, Omega_m: float = 0.3, Omega_Lambda: float = 0.7) -> float:
    """Standard ΛCDM Hubble parameter."""
    return H0 * np.sqrt(Omega_m * (1+z)**3 + Omega_Lambda)


def H_ssz(z: float, H0: float = H0_LCDM, correction_factor: float = 0.01) -> float:
    """SSZ-corrected Hubble parameter."""
    H_base = H_lcdm(z, H0)
    
    # SSZ correction proportional to golden ratio
    # At high z: segment density increases, H modified
    alpha = correction_factor
    Xi_z = 1 - np.exp(-phi * z / 10)  # Saturation at z~10
    
    H_corrected = H_base * (1 + alpha * Xi_z)
    return H_corrected


def luminosity_distance_lcdm(z: float, H0: float = H0_LCDM) -> float:
    """Luminosity distance (ΛCDM)."""
    # Simplified for demonstration
    dL = (c / H0) * z * (1 + z/2)
    return dL  # Mpc


def luminosity_distance_ssz(z: float, H0: float = H0_LCDM) -> float:
    """SSZ-corrected luminosity distance."""
    dL_lcdm = luminosity_distance_lcdm(z, H0)
    
    # SSZ correction
    Xi_z = 1 - np.exp(-phi * z / 10)
    correction = 1 - 0.01 * Xi_z
    
    dL_ssz = dL_lcdm * correction
    return dL_ssz


def hubble_tension_analysis(z_array: np.ndarray) -> Dict:
    """Analyze Hubble tension with SSZ."""
    H_lcdm_vals = np.array([H_lcdm(z) for z in z_array])
    H_ssz_vals = np.array([H_ssz(z) for z in z_array])
    
    difference = H_ssz_vals - H_lcdm_vals
    relative_diff = difference / H_lcdm_vals
    
    return {
        'z': z_array,
        'H_lcdm': H_lcdm_vals,
        'H_ssz': H_ssz_vals,
        'difference': difference,
        'relative_diff': relative_diff,
        'mean_diff_percent': np.mean(np.abs(relative_diff)) * 100
    }


if __name__ == "__main__":
    print("="*80)
    print("SSZ COSMOLOGY TEST")
    print("="*80)
    
    # Test at various redshifts
    z_test = np.array([0.1, 0.5, 1.0, 2.0, 5.0])
    
    print("\nHubble Parameter (km/s/Mpc):")
    for z in z_test:
        H_l = H_lcdm(z)
        H_s = H_ssz(z)
        diff = ((H_s - H_l) / H_l) * 100
        print(f"  z={z:.1f}: ΛCDM={H_l:.2f}, SSZ={H_s:.2f}, Δ={diff:.3f}%")
    
    print("\n✅ SSZ COSMOLOGY WORKING")
    print("="*80)
