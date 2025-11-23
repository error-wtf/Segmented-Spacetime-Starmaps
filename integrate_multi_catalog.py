#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrate Multi-Catalog Data into SSZ Database

Merges ALMA, AKARI, NED, 2MASS, WISE, SIMBAD sources into the main database.

© 2025 Carmen Wrede, Lino Casu
"""
import pandas as pd
import numpy as np
from pathlib import Path

def load_multi_catalog_csvs():
    """Load all multi-catalog CSV files."""
    catalog_files = list(Path('.').glob('multi_catalog_*.csv'))
    
    if not catalog_files:
        print("[X] No multi-catalog CSV files found!")
        return pd.DataFrame()
    
    all_data = []
    for file in catalog_files:
        try:
            df = pd.read_csv(file)
            print(f"[OK] Loaded {file.name}: {len(df)} sources")
            all_data.append(df)
        except Exception as e:
            print(f"[X] Failed to load {file.name}: {e}")
    
    if not all_data:
        return pd.DataFrame()
    
    combined = pd.concat(all_data, ignore_index=True)
    print(f"\n[OK] Total: {len(combined)} sources from {len(all_data)} files")
    
    return combined


def extract_coordinates(df):
    """Extract RA/Dec from multi-catalog data."""
    print("\n[INFO] Extracting coordinates...")
    
    # Try to find RA/Dec columns
    ra_cols = [col for col in df.columns if 'ra' in col.lower() or 's_ra' in col.lower()]
    dec_cols = [col for col in df.columns if 'dec' in col.lower() or 's_dec' in col.lower()]
    
    if not ra_cols or not dec_cols:
        print("[X] No RA/Dec columns found!")
        return df
    
    # Use first RA/Dec column found
    ra_col = ra_cols[0]
    dec_col = dec_cols[0]
    
    print(f"[OK] Using RA column: {ra_col}, Dec column: {dec_col}")
    
    # Rename to standard names
    df['ra'] = df[ra_col]
    df['dec'] = df[dec_col]
    
    # Remove rows with invalid coordinates
    before = len(df)
    df = df.dropna(subset=['ra', 'dec'])
    after = len(df)
    
    if before != after:
        print(f"[INFO] Removed {before - after} rows with invalid coordinates")
    
    return df


def add_ssz_parameters(df):
    """Calculate SSZ parameters for sources."""
    print("\n[INFO] Calculating SSZ parameters...")
    
    # Constants
    G = 6.67430e-11
    c = 2.99792458e8
    M_sun = 1.989e30
    PC_TO_M = 3.0857e16
    
    # Estimate masses and distances (simplified)
    # For real implementation, cross-match with GAIA or use spectral types
    
    # Default values
    df['mass_msun'] = 1.0  # Default 1 solar mass
    df['distance_pc'] = 1000.0  # Default 1000 pc
    df['distance_ly'] = df['distance_pc'] * 3.26156  # Convert to light-years
    
    # Calculate SSZ parameters
    df['r_s'] = 2 * G * (df['mass_msun'] * M_sun) / (c**2)  # Schwarzschild radius
    df['r_m'] = df['distance_pc'] * PC_TO_M  # Distance in meters
    df['r_ratio'] = df['r_m'] / df['r_s']  # r/r_s
    
    # Segment density (simplified)
    alpha = 0.12
    r_c = 1.9  # pc
    df['xi'] = 1 - alpha * np.exp(-(df['distance_pc'] / r_c)**2)
    
    print(f"[OK] Added SSZ parameters to {len(df)} sources")
    
    return df


def merge_with_existing_db(new_df, db_path='ssz_explorer/ssz_data/star_database_50k.csv'):
    """Merge new sources with existing database."""
    print(f"\n[INFO] Merging with existing database: {db_path}")
    
    try:
        existing_df = pd.read_csv(db_path)
        print(f"[OK] Loaded existing database: {len(existing_df)} stars")
        
        # Combine
        combined = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Remove duplicates based on coordinates (within 1 arcsec)
        print("[INFO] Removing duplicates...")
        before = len(combined)
        
        # Simple duplicate removal (exact ra/dec match)
        combined = combined.drop_duplicates(subset=['ra', 'dec'], keep='first')
        
        after = len(combined)
        print(f"[OK] Removed {before - after} duplicates")
        print(f"[OK] Final database: {after} sources")
        
        return combined
        
    except Exception as e:
        print(f"[X] Failed to merge: {e}")
        print(f"[INFO] Returning new sources only")
        return new_df


def save_enhanced_database(df, output_path='ssz_explorer/ssz_data/star_database_enhanced.csv'):
    """Save enhanced database."""
    print(f"\n[INFO] Saving enhanced database to: {output_path}")
    
    try:
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        df.to_csv(output_path, index=False)
        print(f"[OK] Saved {len(df)} sources to {output_path}")
        print(f"[OK] File size: {Path(output_path).stat().st_size / 1024 / 1024:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"[X] Failed to save: {e}")
        return False


if __name__ == "__main__":
    print("="*80)
    print("MULTI-CATALOG INTEGRATION")
    print("="*80)
    
    # Step 1: Load multi-catalog CSVs
    df = load_multi_catalog_csvs()
    
    if df.empty:
        print("\n[X] No data to integrate!")
        exit(1)
    
    # Step 2: Extract coordinates
    df = extract_coordinates(df)
    
    # Step 3: Add SSZ parameters
    df = add_ssz_parameters(df)
    
    # Step 4: Merge with existing database
    enhanced_df = merge_with_existing_db(df)
    
    # Step 5: Save enhanced database
    success = save_enhanced_database(enhanced_df)
    
    if success:
        print("\n" + "="*80)
        print("[OK] INTEGRATION COMPLETE!")
        print("="*80)
        print(f"\nEnhanced database statistics:")
        print(f"  Total sources: {len(enhanced_df)}")
        if 'catalog' in enhanced_df.columns:
            print(f"  By catalog:")
            for cat, count in enhanced_df['catalog'].value_counts().items():
                print(f"    {cat}: {count}")
    else:
        print("\n[X] Integration failed!")
        exit(1)
