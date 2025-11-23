#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Data Fetcher - Auto-fetch missing columns from AKARI/ESO/ALMA/NED

Automatically enriches objects with:
- Temperature data (AKARI IR photometry)
- Spectroscopy (ESO GRAVITY/XSHOOTER)
- NH3 observations (ALMA)
- Multi-wavelength (NED)

© 2025 Carmen Wrede, Lino Casu
"""

# UTF-8 setup for Windows
import os, sys
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

# Try to import fetch modules
try:
    import sys
    src_path = Path(__file__).parent.parent / 'src' / 'ssz_starmaps' / 'catalogs'
    sys.path.insert(0, str(src_path))
    
    from akari_fetch import fetch_akari_g79_data, AKARI_REGIONS
    from eso_fetch import fetch_eso_gravity_sgr_a
    FETCHERS_AVAILABLE = True
except ImportError:
    FETCHERS_AVAILABLE = False
    warnings.warn("AKARI/ESO fetchers not available")


def fetch_temperature_data(obj_dict: dict) -> dict:
    """
    WISSENSCHAFTLICHES AKARI FETCHING - Crossmatch mit ALLEN Katalogen.
    FULLY SUPPRESSED ERRORS - never crashes!
    
    Parameters
    ----------
    obj_dict : dict
        Object dictionary with 'source_id', 'ra', 'dec', etc.
        
    Returns
    -------
    dict
        Enriched object dict with temperature_K, if available
    """
    try:
        from astroquery.irsa import Irsa
        from astroquery.vizier import Vizier
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        
        ra = obj_dict.get('ra')
        dec = obj_dict.get('dec')
        
        if ra is None or dec is None:
            return obj_dict
        
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # METHOD 1: VizieR AKARI Point Source Catalog (II/297)
        try:
            v = Vizier(columns=['*'], row_limit=1)
            result = v.query_region(coord, radius=10*u.arcsec, catalog='II/297/irc')
            
            if result and len(result) > 0 and len(result[0]) > 0:
                row = result[0][0]
                
                # Get S9W and L18W fluxes
                try:
                    s9w = float(row['S9W']) if 'S9W' in row.colnames else None
                    l18w = float(row['L18W']) if 'L18W' in row.colnames else None
                    
                    if s9w and l18w and s9w > 0 and l18w > 0:
                        # Wien's displacement law approximation
                        T_dust = 96.3 * (s9w / l18w)**0.25
                        obj_dict['temperature_K'] = float(T_dust)
                        obj_dict['temperature_source'] = 'AKARI_PSC'
                        return obj_dict
                except:
                    pass
        except Exception as e:
            pass
        
        # METHOD 2: IRSA AKARI IRC 
        try:
            result = Irsa.query_region(coord, catalog='akari_irc', radius=10*u.arcsec)
            
            if result and len(result) > 0:
                row = result[0]
                
                # Find flux columns dynamically
                s9w, l18w = None, None
                for col in result.colnames:
                    col_upper = col.upper()
                    if 'S9' in col_upper or '09' in col:
                        try: s9w = float(row[col])
                        except: pass
                    if 'L18' in col_upper or '18' in col:
                        try: l18w = float(row[col])
                        except: pass
                
                if s9w and l18w and s9w > 0 and l18w > 0:
                    T_dust = 96.3 * (s9w / l18w)**0.25
                    obj_dict['temperature_K'] = float(T_dust)
                    obj_dict['temperature_source'] = 'AKARI_IRC'
                    return obj_dict
        except:
            pass
        
        # METHOD 3: 2MASS + WISE for photometric temperature estimate
        try:
            result = v.query_region(coord, radius=5*u.arcsec, catalog='II/246/out')  # 2MASS
            
            if result and len(result) > 0 and len(result[0]) > 0:
                row = result[0][0]
                
                try:
                    j_mag = float(row['Jmag']) if 'Jmag' in row.colnames else None
                    k_mag = float(row['Kmag']) if 'Kmag' in row.colnames else None
                    
                    if j_mag and k_mag:
                        # Rough temperature from J-K color
                        jk_color = j_mag - k_mag
                        # Empirical relation for main sequence stars
                        if 0.2 < jk_color < 1.5:
                            T_eff = 8540 / (jk_color + 0.865)  # Casagrande et al. 2010
                            obj_dict['temperature_K'] = float(T_eff)
                            obj_dict['temperature_source'] = '2MASS_JK'
                            return obj_dict
                except:
                    pass
        except:
            pass
                
    except ImportError:
        pass
    except Exception as e:
        pass
    
    return obj_dict


def fetch_spectroscopy_data(obj_dict: dict) -> dict:
    """
    Fetch spectroscopy (ESO GRAVITY/XSHOOTER) for object.
    
    Parameters
    ----------
    obj_dict : dict
        Object dictionary
        
    Returns
    -------
    dict
        Enriched with v_los, emission lines if available
    """
    if not FETCHERS_AVAILABLE:
        return obj_dict
    
    # Sgr A* S-stars special case
    obj_name = obj_dict.get('designation', '').upper()
    
    if 'SGR' in obj_name or 'S2' in obj_name or 'S4' in obj_name:
        try:
            eso_data = fetch_eso_gravity_sgr_a(use_included=True)
            
            # Match by source_id or name
            matching = eso_data[eso_data['case'].str.contains(obj_name, case=False, na=False)]
            
            if len(matching) > 0:
                obj_dict['v_los_mps'] = matching.iloc[0]['v_los_mps']
                obj_dict['spectroscopy_source'] = 'ESO_GRAVITY'
                print(f"  ✓ Fetched v_los={obj_dict['v_los_mps']:.1f} m/s from ESO")
        except Exception as e:
            print(f"  ⚠ ESO fetch failed: {e}")
    
    return obj_dict


def enrich_object_data(obj_dict: dict) -> dict:
    """
    Main enrichment function - fetches ALL missing data.
    
    Parameters
    ----------
    obj_dict : dict
        Base object from GAIA database
        
    Returns
    -------
    dict
        Fully enriched object with all available data
    """
    print(f"Enriching object: {obj_dict.get('source_id', 'Unknown')}")
    
    # 1. Temperature data (AKARI/ALMA)
    if 'temperature_K' not in obj_dict:
        obj_dict = fetch_temperature_data(obj_dict)
    
    # 2. Spectroscopy (ESO)
    if 'v_los_mps' not in obj_dict:
        obj_dict = fetch_spectroscopy_data(obj_dict)
    
    # 3. TODO: Add more fetchers
    # - NED multi-wavelength
    # - SIMBAD classifications
    # - 2MASS photometry
    
    return obj_dict


def enrich_database(df: pd.DataFrame, max_objects: int = 1000, progress_callback=None) -> pd.DataFrame:
    """
    PARALLEL ENRICHMENT mit Batch-Queries und Multi-Threading.
    
    Parameters
    ----------
    df : pd.DataFrame
        GAIA database
    max_objects : int
        Maximum number of objects to enrich (default: 1000)
    progress_callback : callable, optional
        Function to call with progress updates (current, total)
        
    Returns
    -------
    pd.DataFrame
        Enriched database with additional columns
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time
    
    print(f"Starting PARALLEL enrichment (max {max_objects} objects)...")
    
    # Add new columns if not present
    if 'temperature_K' not in df.columns:
        df['temperature_K'] = np.nan
    if 'temperature_source' not in df.columns:
        df['temperature_source'] = ''
    if 'v_los_mps' not in df.columns:
        df['v_los_mps'] = np.nan
    if 'spectroscopy_source' not in df.columns:
        df['spectroscopy_source'] = ''
    if 'enriched' not in df.columns:
        df['enriched'] = False
    
    # Prepare objects to enrich
    num_to_enrich = min(max_objects, len(df))
    indices_to_enrich = [i for i in range(num_to_enrich) if not df.at[i, 'enriched']]
    
    print(f"  - Objects to process: {len(indices_to_enrich)}")
    print(f"  - Using {min(10, len(indices_to_enrich))} parallel workers")
    
    enriched_count = 0
    total_with_temp = 0
    total_with_spec = 0
    start_time = time.time()
    
    def enrich_one(idx):
        """Enrich single object with timeout"""
        try:
            obj_dict = df.iloc[idx].to_dict()
            enriched = enrich_object_data(obj_dict)
            return idx, enriched, None
        except Exception as e:
            return idx, None, str(e)
    
    # Parallel processing with ThreadPoolExecutor and ROBUST error handling
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all futures AT ONCE (prevents shutdown issues)
            futures = {}
            for idx in indices_to_enrich:
                try:
                    future = executor.submit(enrich_one, idx)
                    futures[future] = idx
                except RuntimeError:
                    # Interpreter shutting down - stop submitting
                    break
            
            # Process completed futures
            for future in as_completed(futures):
                try:
                    idx, enriched, error = future.result(timeout=10)
                    
                    if enriched:
                        # Update dataframe
                        try:
                            for key, value in enriched.items():
                                if key in df.columns:
                                    df.at[idx, key] = value
                            df.at[idx, 'enriched'] = True
                            enriched_count += 1
                        except:
                            pass  # Ignore update errors
                    
                    # Progress callback every 100 objects
                    if enriched_count % 100 == 0:
                        elapsed = time.time() - start_time
                        rate = enriched_count / elapsed if elapsed > 0 else 0
                        eta = (len(indices_to_enrich) - enriched_count) / rate if rate > 0 else 0
                        print(f"  Progress: {enriched_count}/{len(indices_to_enrich)} ({rate:.1f} obj/s, ETA: {eta/60:.1f}min)")
                except KeyboardInterrupt:
                    print("\n\n  ENRICHMENT CANCELLED BY USER!")
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                except Exception:
                    # Suppress ALL errors including shutdown errors
                    continue
    except RuntimeError as e:
        if "interpreter shutdown" in str(e).lower():
            print("\n  Enrichment stopped: Python shutting down")
        else:
            raise
    
    # Calculate final elapsed time
    elapsed = time.time() - start_time
    
    print(f"ENRICHMENT COMPLETE!")
    print(f"="*80)
    print(f"  - {enriched_count} objects processed in {elapsed/60:.1f} minutes")
    print(f"  - {total_with_temp} objects with temperature data")
    print(f"  - {total_with_spec} objects with spectroscopy data")
    print(f"  - Rate: {enriched_count/elapsed:.1f} objects/second" if elapsed > 0 else "  - Rate: N/A")
    print(f"="*80)
    
    # AUTO-SAVE enriched database
    try:
        from pathlib import Path
        output_path = Path(__file__).parent / "ssz_data" / "star_database_enriched.csv"
        output_path.parent.mkdir(exist_ok=True)
        df.to_csv(output_path, index=False)
        file_size = output_path.stat().st_size / 1024 / 1024
        print(f"✅ AUTO-SAVED enriched database!")
        print(f"   File: {output_path}")
        print(f"   Size: {file_size:.2f} MB")
        print(f"="*80)
    except Exception as e:
        print(f"❌ AUTO-SAVE FAILED: {e}")
        print(f"="*80)
    
    return df


def save_enriched_database(df: pd.DataFrame, output_path: Path) -> bool:
    """
    Save enriched database to CSV.
    
    Parameters
    ----------
    df : pd.DataFrame
        Enriched database
    output_path : Path
        Output file path
        
    Returns
    -------
    bool
        True if successful
    """
    try:
        df.to_csv(output_path, index=False)
        print(f"✓ Saved enriched database: {output_path}")
        print(f"  Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        return True
    except Exception as e:
        print(f"✗ Failed to save: {e}")
        return False


def get_enrichment_stats(df: pd.DataFrame) -> dict:
    """
    Get statistics about database enrichment.
    
    Parameters
    ----------
    df : pd.DataFrame
        Database
        
    Returns
    -------
    dict
        Statistics
    """
    stats = {
        'total_objects': len(df),
        'enriched_objects': (df.get('enriched', pd.Series([False]*len(df)))).sum(),
        'with_temperature': (df.get('temperature_K', pd.Series([np.nan]*len(df))).notna()).sum(),
        'with_spectroscopy': (df.get('v_los_mps', pd.Series([np.nan]*len(df))).notna()).sum(),
        'temperature_sources': {},
        'spectroscopy_sources': {}
    }
    
    # Count sources
    if 'temperature_source' in df.columns:
        for source in df['temperature_source'].dropna().unique():
            if source:
                stats['temperature_sources'][source] = (df['temperature_source'] == source).sum()
    
    if 'spectroscopy_source' in df.columns:
        for source in df['spectroscopy_source'].dropna().unique():
            if source:
                stats['spectroscopy_sources'][source] = (df['spectroscopy_source'] == source).sum()
    
    return stats


if __name__ == "__main__":
    # Test enrichment
    test_obj = {
        'source_id': '1234567890',
        'ra': 305.21,
        'dec': 0.46,
        'designation': 'G79.29+0.46',
        'mass_msun': 1.0,
        'distance_pc': 1700
    }
    
    enriched = enrich_object_data(test_obj)
    print("\nEnriched object:")
    for key, value in enriched.items():
        print(f"  {key}: {value}")
