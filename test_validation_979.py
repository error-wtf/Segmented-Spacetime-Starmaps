#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Validation Test - 97.9% Target

Tests the PRIMARY data source (ESO) for SSZ validation.
Target: 46/47 observations should pass (97.9%)

This validates that fetch_primary() returns the correct
high-quality data for SSZ physics tests.

© 2025 Carmen Wrede, Lino Casu
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import numpy as np
import pandas as pd
from ssz_starmaps.catalogs import CatalogManager
from ssz_starmaps.transform import transform_catalog


def validate_ssz_observation(row: pd.Series, tolerance: float = 0.1) -> dict:
    """
    Validate a single SSZ observation.
    
    Parameters
    ----------
    row : pd.Series
        Observation with M_solar, a_m, e, r_m, v_m
    tolerance : float
        Tolerance for validation (default: 10%)
        
    Returns
    -------
    dict
        Validation result with 'passed', 'error', 'ratio'
    """
    try:
        # Extract parameters
        M = row['M_solar']  # Solar masses
        a = row['a_m']      # Semi-major axis [m]
        e = row['e']        # Eccentricity
        r = row['r_m']      # Distance [m]
        v_obs = row['v_m']  # Observed velocity [m/s]
        
        # Constants
        G = 6.67430e-11  # m^3 kg^-1 s^-2
        M_sun = 1.989e30  # kg
        c = 2.99792458e8  # m/s
        
        # SSZ parameter
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        
        # Calculate SSZ predictions
        M_kg = M * M_sun
        r_s = 2 * G * M_kg / (c**2)  # Schwarzschild radius
        
        # SSZ stretch factor Xi
        Xi = 1 - np.exp(-phi * r_s / r)
        
        # SSZ velocity prediction
        # v_SSZ = sqrt(GM/r) * sqrt(1 + Xi)
        v_kepler = np.sqrt(G * M_kg / r)
        v_ssz = v_kepler * np.sqrt(1 + Xi)
        
        # Compare with observation
        error = abs(v_ssz - v_obs) / v_obs
        ratio = v_ssz / v_obs
        passed = error < tolerance
        
        return {
            'passed': passed,
            'error': error,
            'ratio': ratio,
            'v_obs': v_obs,
            'v_ssz': v_ssz,
            'Xi': Xi
        }
        
    except Exception as e:
        return {
            'passed': False,
            'error': np.nan,
            'ratio': np.nan,
            'exception': str(e)
        }


def run_validation_test():
    """Run complete validation test on ESO data."""
    
    print("="*70)
    print("SSZ VALIDATION TEST - PRIMARY DATA (ESO)")
    print("="*70)
    print()
    print("Target: 97.9% success rate (46/47 observations)")
    print("Tolerance: 10% error")
    print()
    
    # Load PRIMARY data
    print("[1/4] Loading PRIMARY data (ESO)...")
    manager = CatalogManager()
    
    try:
        eso_data = manager.fetch_primary('sgr_a_stars', use_included=True)
        print(f"  Loaded {len(eso_data)} ESO observations")
        print()
    except Exception as e:
        print(f"ERROR: Cannot load ESO data: {e}")
        print("This test requires access to Mass-Projection repo data")
        return
    
    # Check required columns (adapted to actual ESO data structure)
    required = ['M_solar', 'a_m', 'e', 'r_emit_m', 'v_tot_mps']
    if not all(col in eso_data.columns for col in required):
        print("ERROR: Missing required columns")
        print(f"Required: {required}")
        print(f"Available: {list(eso_data.columns)}")
        return
    
    # Rename columns for validation function
    eso_data = eso_data.copy()
    eso_data['r_m'] = eso_data['r_emit_m']
    eso_data['v_m'] = eso_data['v_tot_mps']
    
    # Run validation on each observation
    print("[2/4] Running SSZ validation...")
    results = []
    
    for idx, row in eso_data.iterrows():
        result = validate_ssz_observation(row, tolerance=0.10)
        result['case'] = row.get('case', f'obs_{idx}')
        result['category'] = row.get('category', 'unknown')
        results.append(result)
    
    results_df = pd.DataFrame(results)
    print(f"  Validated {len(results_df)} observations")
    print()
    
    # Calculate statistics
    print("[3/4] Analyzing results...")
    n_total = len(results_df)
    n_passed = results_df['passed'].sum()
    n_failed = n_total - n_passed
    success_rate = (n_passed / n_total) * 100
    
    print(f"  Total observations: {n_total}")
    print(f"  Passed: {n_passed}")
    print(f"  Failed: {n_failed}")
    print(f"  Success rate: {success_rate:.1f}%")
    print()
    
    # Compare with target
    target_rate = 97.9
    target_passed = int(n_total * target_rate / 100)
    
    if success_rate >= target_rate - 1:  # Allow 1% tolerance
        print(f"  [SUCCESS] Achieved target: {success_rate:.1f}% >= {target_rate}%")
        status = "PASS"
    else:
        print(f"  [WARNING] Below target: {success_rate:.1f}% < {target_rate}%")
        status = "FAIL"
    
    print()
    
    # Show statistics
    print("[4/4] Detailed statistics:")
    print()
    print(f"Error statistics:")
    print(f"  Mean error: {results_df['error'].mean()*100:.2f}%")
    print(f"  Median error: {results_df['error'].median()*100:.2f}%")
    print(f"  Std error: {results_df['error'].std()*100:.2f}%")
    print(f"  Max error: {results_df['error'].max()*100:.2f}%")
    print()
    
    print(f"Ratio statistics (v_SSZ / v_obs):")
    print(f"  Mean ratio: {results_df['ratio'].mean():.4f}")
    print(f"  Median ratio: {results_df['ratio'].median():.4f}")
    print(f"  Std ratio: {results_df['ratio'].std():.4f}")
    print()
    
    # Show failed cases
    if n_failed > 0:
        print(f"Failed observations ({n_failed}):")
        failed = results_df[~results_df['passed']]
        for _, row in failed.iterrows():
            print(f"  - {row['case']}: error={row['error']*100:.1f}%")
        print()
    
    # Show best cases
    print("Best 5 observations:")
    best = results_df.nsmallest(5, 'error')
    for _, row in best.iterrows():
        print(f"  - {row['case']}: error={row['error']*100:.2f}%")
    print()
    
    # Summary
    print("="*70)
    print("VALIDATION TEST SUMMARY")
    print("="*70)
    print()
    print(f"Data source: PRIMARY (ESO GRAVITY)")
    print(f"Observations: {n_total}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Target rate: {target_rate}%")
    print(f"Status: {status}")
    print()
    
    if status == "PASS":
        print("[OK] PRIMARY data source validated!")
        print("ESO spectroscopy is suitable for SSZ physics tests.")
    else:
        print("[WARNING] Validation below target")
        print("Check data quality or SSZ formula implementation")
    
    print()
    print("="*70)
    print()
    
    return results_df


def compare_with_gaia_baseline():
    """Compare ESO validation with GAIA baseline."""
    
    print("="*70)
    print("COMPARISON: PRIMARY vs AUXILIARY")
    print("="*70)
    print()
    
    print("PRIMARY (ESO Spectroscopy):")
    print("  Source: ESO GRAVITY")
    print("  Data: Br-gamma emission lines")
    print("  Observations: 47")
    print("  Expected success: 97.9% (46/47)")
    print("  Use for: SSZ validation tests")
    print()
    
    print("AUXILIARY (GAIA Catalogs):")
    print("  Source: GAIA DR3")
    print("  Data: Astrometry, parallax, photometry")
    print("  Observations: ~800 (nearby)")
    print("  Expected success: ~51% (for SSZ)")
    print("  Use for: Positions, comparisons ONLY")
    print()
    
    print("[IMPORTANT]")
    print("  - Use fetch_primary() for SSZ validation")
    print("  - Use fetch_nearby() ONLY for positions")
    print("  - DO NOT mix them up!")
    print()
    print("="*70)
    print()


if __name__ == "__main__":
    # Run validation test
    results = run_validation_test()
    
    # Show comparison
    compare_with_gaia_baseline()
    
    # Save results
    if results is not None:
        output_file = Path(__file__).parent / "validation_results_979.csv"
        results.to_csv(output_file, index=False)
        print(f"Results saved to: {output_file}")
        print()
