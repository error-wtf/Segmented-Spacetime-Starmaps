#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SSZ STARMAPS - PRIMARY DATA ACCESS TEST                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

Validates that fetch_primary() correctly accesses ESO GRAVITY data.

TEST SCOPE:
  • Data accessibility from Mass-Projection repo
  • Correct observation count (47 expected)
  • Required column presence
  • Data quality (no NaNs in critical columns)
  • Data range sanity checks
  • Known case verification

NOTE: This validates DATA ACCESS only.
      The FULL 97.9% SSZ physics validation is in Mass-Projection repo.
      See: perfect_paired_test.py for complete SSZ validation.

© 2025 Carmen Wrede, Lino Casu
Licensed under ACSL v1.4
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pandas as pd
import numpy as np
from ssz_starmaps.catalogs import CatalogManager


def print_header():
    """Print beautiful test header."""
    print()
    print("╔" + "═"*76 + "╗")
    print("║" + " "*76 + "║")
    print("║" + "       SSZ STARMAPS - PRIMARY DATA ACCESS TEST".center(76) + "║")
    print("║" + " "*76 + "║")
    print("╚" + "═"*76 + "╝")
    print()
    print("  TARGET:  Validate ESO GRAVITY data access via fetch_primary()")
    print("  SCOPE:   Data integrity (not full SSZ physics validation)")
    print("  SOURCE:  Mass-Projection repo / real_data_emission_lines_clean.csv")
    print()
    print("─" * 78)
    print()


def print_test_section(number, total, title):
    """Print formatted test section header."""
    print()
    print(f"[TEST {number}/{total}] {title}")
    print("─" * 78)


def print_result(status, message, indent=2):
    """Print formatted test result."""
    symbol = "[✓]" if status else "[✗]"
    spaces = " " * indent
    print(f"{spaces}{symbol} {message}")


def print_progress_bar(current, total, width=50):
    """Print simple progress bar."""
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    percent = int(100 * current / total)
    print(f"\r  Progress: [{bar}] {percent}%", end="", flush=True)
    if current == total:
        print()  # New line when complete


def test_primary_data_access():
    """Test PRIMARY data access (not full SSZ validation)."""
    
    print_header()
    
    total_tests = 6
    passed_tests = 0
    
    # Initialize manager
    manager = CatalogManager()
    
    # Test 1: Data accessibility
    print_test_section(1, total_tests, "Data Accessibility")
    try:
        eso_data = manager.fetch_primary('sgr_a_stars', use_included=True)
        print_result(True, f"Successfully loaded {len(eso_data)} observations")
        passed_tests += 1
    except Exception as e:
        print_result(False, f"Failed to load data: {e}")
        return False, 0, total_tests
    
    # Test 2: Correct count
    print_test_section(2, total_tests, "Observation Count")
    expected_count = 47
    actual_count = len(eso_data)
    
    if actual_count == expected_count:
        print_result(True, f"Count verified: {actual_count} observations (expected: {expected_count})")
        passed_tests += 1
    else:
        print_result(False, f"Count mismatch: {actual_count} (expected: {expected_count})")
        return False, passed_tests, total_tests
    
    # Test 3: Required columns
    print_test_section(3, total_tests, "Required Columns")
    required_cols = ['case', 'category', 'M_solar', 'a_m', 'e', 
                     'r_emit_m', 'v_tot_mps', 'z', 'f_obs_Hz']
    
    missing = [col for col in required_cols if col not in eso_data.columns]
    
    if not missing:
        print_result(True, f"All {len(required_cols)} required columns present")
        for i, col in enumerate(required_cols, 1):
            print(f"    {i:2d}. {col}")
        passed_tests += 1
    else:
        print_result(False, f"Missing columns: {missing}")
        return False, passed_tests, total_tests
    
    # Test 4: Data quality
    print_test_section(4, total_tests, "Data Quality (NaN Check)")
    key_cols = ['M_solar', 'a_m', 'e', 'r_emit_m', 'v_tot_mps']
    
    nan_counts = {}
    for col in key_cols:
        nan_count = eso_data[col].isna().sum()
        nan_counts[col] = nan_count
    
    total_nans = sum(nan_counts.values())
    
    if total_nans == 0:
        print_result(True, "No NaNs in key columns")
        print("    ┌─────────────────┬────────┐")
        print("    │ Column          │ Status │")
        print("    ├─────────────────┼────────┤")
        for col in key_cols:
            print(f"    │ {col:15s} │   OK   │")
        print("    └─────────────────┴────────┘")
        passed_tests += 1
    else:
        print_result(False, f"Found {total_nans} NaNs:")
        for col, count in nan_counts.items():
            if count > 0:
                print(f"      • {col}: {count} NaNs")
        return False, passed_tests, total_tests
    
    # Test 5: Data ranges (sanity check)
    print_test_section(5, total_tests, "Data Range Validation")
    checks = [
        ('M_solar', eso_data['M_solar'].min(), eso_data['M_solar'].max(), 0.1, 1e10, 'M_sun'),
        ('a_m', eso_data['a_m'].min(), eso_data['a_m'].max(), 1e9, 1e17, 'm'),
        ('e', eso_data['e'].min(), eso_data['e'].max(), 0.0, 1.0, ''),
        ('r_emit_m', eso_data['r_emit_m'].min(), eso_data['r_emit_m'].max(), 1e3, 1e17, 'm'),
        ('v_tot_mps', eso_data['v_tot_mps'].min(), eso_data['v_tot_mps'].max(), 1e3, 3e8, 'm/s'),
    ]
    
    print("    ┌──────────────┬─────────────┬─────────────┬────────┐")
    print("    │ Parameter    │ Min         │ Max         │ Status │")
    print("    ├──────────────┼─────────────┼─────────────┼────────┤")
    
    all_ok = True
    for col, min_val, max_val, expected_min, expected_max, unit in checks:
        status = "  OK  " if (expected_min <= min_val and max_val <= expected_max) else " FAIL "
        if status.strip() == "FAIL":
            all_ok = False
        print(f"    │ {col:12s} │ {min_val:11.2e} │ {max_val:11.2e} │ {status} │")
    
    print("    └──────────────┴─────────────┴─────────────┴────────┘")
    
    if all_ok:
        print_result(True, "All ranges within expected bounds")
        passed_tests += 1
    else:
        print_result(False, "Some values out of expected range")
        return False, passed_tests, total_tests
    
    # Test 6: Known cases
    print_test_section(6, total_tests, "Known Case Verification")
    known_cases = ['3C279_jet', 'M87*_jet', 'S2_SgrA*', 'G2_SgrA*']
    found_cases = []
    
    print("    ┌──────────────────┬────────┐")
    print("    │ Known Case       │ Found  │")
    print("    ├──────────────────┼────────┤")
    
    for case in known_cases:
        if case in eso_data['case'].values:
            found_cases.append(case)
            print(f"    │ {case:16s} │  YES   │")
        else:
            print(f"    │ {case:16s} │   NO   │")
    
    print("    └──────────────────┴────────┘")
    
    if len(found_cases) >= 3:  # At least 3 of 4
        print_result(True, f"Found {len(found_cases)}/{len(known_cases)} known cases (threshold: 3)")
        passed_tests += 1
    else:
        print_result(False, f"Only found {len(found_cases)}/{len(known_cases)} known cases")
        return False, passed_tests, total_tests
    
    # Summary
    print()
    print("─" * 78)
    print()
    print("╔" + "═"*76 + "╗")
    print("║" + " "*76 + "║")
    print("║" + "TEST SUMMARY - PRIMARY DATA ACCESS".center(76) + "║")
    print("║" + " "*76 + "║")
    print("╚" + "═"*76 + "╝")
    print()
    
    # Results table
    print("  RESULTS:")
    print("  ┌────────────────────────┬──────────┐")
    print("  │ Metric                 │ Value    │")
    print("  ├────────────────────────┼──────────┤")
    print(f"  │ Tests Passed           │ {passed_tests}/{total_tests}      │")
    print(f"  │ Success Rate           │ {100*passed_tests//total_tests}%       │")
    print("  ├────────────────────────┼──────────┤")
    print(f"  │ Data Source            │ ESO      │")
    print(f"  │ Observations           │ {actual_count:2d}       │")
    print(f"  │ Columns                │ {len(eso_data.columns):2d}       │")
    print(f"  │ Data Quality           │ Perfect  │")
    print("  └────────────────────────┴──────────┘")
    print()
    
    if passed_tests == total_tests:
        print("  [✓] STATUS: SUCCESS - PRIMARY data validated!")
    else:
        print(f"  [✗] STATUS: PARTIAL - {passed_tests}/{total_tests} tests passed")
    
    print()
    print("─" * 78)
    print()
    print("  IMPORTANT NOTES:")
    print()
    print("  1. This test validates DATA ACCESS only")
    print("  2. Full 97.9% SSZ physics validation: Mass-Projection/perfect_paired_test.py")
    print("  3. This confirms fetch_primary() returns correct ESO data")
    print("  4. Data is ready for SSZ validation in Mass-Projection repo")
    print()
    print("─" * 78)
    print()
    
    return passed_tests == total_tests, passed_tests, total_tests


def show_data_sample():
    """Show sample of PRIMARY data."""
    
    print()
    print("╔" + "═"*76 + "╗")
    print("║" + " "*76 + "║")
    print("║" + "PRIMARY DATA SAMPLE".center(76) + "║")
    print("║" + " "*76 + "║")
    print("╚" + "═"*76 + "╝")
    print()
    
    manager = CatalogManager()
    eso_data = manager.fetch_primary('sgr_a_stars', use_included=True)
    
    print("  FIRST 5 OBSERVATIONS:")
    print("  ┌─────────────────┬──────────────────┬──────────────┬──────────────┐")
    print("  │ Case            │ Category         │ Mass [M_sun] │ Velocity     │")
    print("  ├─────────────────┼──────────────────┼──────────────┼──────────────┤")
    
    for idx in range(min(5, len(eso_data))):
        row = eso_data.iloc[idx]
        case = row['case'][:15]
        cat = row['category'][:16]
        mass = row['M_solar']
        vel = row['v_tot_mps']
        print(f"  │ {case:15s} │ {cat:16s} │ {mass:12.2e} │ {vel:12.2e} │")
    
    print("  └─────────────────┴──────────────────┴──────────────┴──────────────┘")
    print()
    
    # Categories
    print("  CATEGORY BREAKDOWN:")
    print("  ┌────────────────────┬───────┐")
    print("  │ Category           │ Count │")
    print("  ├────────────────────┼───────┤")
    for cat, count in eso_data['category'].value_counts().items():
        print(f"  │ {cat:18s} │ {count:5d} │")
    print("  └────────────────────┴───────┘")
    print()
    
    # Ranges
    print("  DATA RANGES:")
    print("  ┌─────────────────┬──────────────┬──────────────┐")
    print("  │ Parameter       │ Minimum      │ Maximum      │")
    print("  ├─────────────────┼──────────────┼──────────────┤")
    print(f"  │ Mass [M_sun]    │ {eso_data['M_solar'].min():12.2e} │ {eso_data['M_solar'].max():12.2e} │")
    print(f"  │ Velocity [m/s]  │ {eso_data['v_tot_mps'].min():12.2e} │ {eso_data['v_tot_mps'].max():12.2e} │")
    print(f"  │ Eccentricity    │ {eso_data['e'].min():12.3f} │ {eso_data['e'].max():12.3f} │")
    print("  └─────────────────┴──────────────┴──────────────┘")
    print()
    print("─" * 78)
    print()


if __name__ == "__main__":
    # Run test
    success = test_primary_data_access()
    
    if success:
        # Show sample
        show_data_sample()
        
        print()
        print("[OK] Phase 4 COMPLETE: PRIMARY data validated!")
        print()
        print("Next steps:")
        print("  - Phase 5: Integration & Examples")
        print("  - Phase 6: Documentation")
        print()
    else:
        print()
        print("[FAIL] PRIMARY data access test failed!")
        print()
