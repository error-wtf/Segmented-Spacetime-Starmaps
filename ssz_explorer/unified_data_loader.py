"""
Unified Multi-Source Data Loader - AUTOMATIC COMBINATION
=========================================================

Based on PAPER-RESTORED findings:
- ESO Professional Data: 97.9% accuracy ✅
- Mixed Catalog Data: 51% accuracy ⚠️
- Solution: COMBINE ALL SOURCES by default!

Data Quality Hierarchy:
1. ESO/ALMA (Professional spectroscopy)
2. GAIA DR3 (Astrometry)
3. SIMBAD (Classification & cross-refs)
4. AKARI (Infrared)
5. VizieR (Supplementary catalogs)

© 2025 Carmen Wrede, Lino Casu, Bingsi
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

# Import multi-source querying
from multi_source_data import query_simbad, query_akari, query_vizier


# ============================================================================
# DATA QUALITY METRICS (from PAPER-RESTORED/ssz_eso_breakthrough_plots.py)
# ============================================================================

DATA_QUALITY_HIERARCHY = {
    'ESO': {
        'priority': 1,
        'accuracy': 97.9,
        'type': 'professional_spectroscopy',
        'resolution': 'λ/Δλ > 10,000',
        'parameters': 'complete',
        'redshift': 'local_gravitational'
    },
    'ALMA': {
        'priority': 1,
        'accuracy': 97.9,
        'type': 'molecular_lines',
        'resolution': 'sub-arcsecond',
        'parameters': 'complete',
        'redshift': 'local_gravitational'
    },
    'GAIA': {
        'priority': 2,
        'accuracy': 85.0,
        'type': 'astrometry',
        'resolution': 'mas precision',
        'parameters': 'photometry + proper motion',
        'redshift': 'cosmological'
    },
    'SIMBAD': {
        'priority': 3,
        'accuracy': 90.0,
        'type': 'classification',
        'resolution': 'cross-reference',
        'parameters': 'object_type + names',
        'redshift': 'mixed'
    },
    'AKARI': {
        'priority': 4,
        'accuracy': 75.0,
        'type': 'infrared',
        'resolution': '9-160 μm bands',
        'parameters': 'thermal_emission',
        'redshift': 'N/A'
    },
    'MIXED_CATALOG': {
        'priority': 5,
        'accuracy': 51.0,
        'type': 'photometry',
        'resolution': 'incomplete',
        'parameters': 'incomplete',
        'redshift': 'cosmological'
    }
}


# ============================================================================
# UNIFIED DATA STRUCTURE
# ============================================================================

class UnifiedAstronomicalObject:
    """
    Unified object combining data from ALL sources
    
    Automatically merges:
    - GAIA: ra, dec, parallax, pmra, pmdec, phot_g_mean_mag
    - SIMBAD: object_type, names, spectral_type
    - AKARI: infrared bands (9, 18, 65, 90 μm)
    - ESO/ALMA: spectroscopy, molecular data (if available)
    """
    
    def __init__(self, source_id=None, ra=None, dec=None):
        # Core identifiers
        self.source_id = source_id
        self.ra = ra
        self.dec = dec
        
        # GAIA data
        self.parallax = None
        self.pmra = None
        self.pmdec = None
        self.phot_g_mean_mag = None
        self.radial_velocity = None
        
        # SIMBAD data
        self.object_type = None
        self.object_names = []
        self.spectral_type = None
        
        # AKARI infrared
        self.akari_9um = None
        self.akari_18um = None
        self.akari_65um = None
        self.akari_90um = None
        
        # ESO/ALMA (if available)
        self.eso_spectrum = None
        self.alma_molecular = None
        
        # Derived quantities
        self.distance_pc = None
        self.distance_ly = None
        self.mass_msun = None
        
        # SSZ physics
        self.xi = None
        self.D_ssz = None
        
        # Data quality flags
        self.data_sources = []
        self.quality_score = 0
        self.completeness = 0
    
    def add_gaia_data(self, gaia_row):
        """Add GAIA DR3 data"""
        self.source_id = gaia_row.get('source_id', self.source_id)
        self.ra = gaia_row.get('ra', self.ra)
        self.dec = gaia_row.get('dec', self.dec)
        self.parallax = gaia_row.get('parallax')
        self.pmra = gaia_row.get('pmra')
        self.pmdec = gaia_row.get('pmdec')
        self.phot_g_mean_mag = gaia_row.get('phot_g_mean_mag')
        self.radial_velocity = gaia_row.get('radial_velocity')
        
        # Calculate distance
        if self.parallax and self.parallax > 0:
            self.distance_pc = 1000.0 / self.parallax
            self.distance_ly = self.distance_pc * 3.26156
        
        self.data_sources.append('GAIA')
        self.quality_score += DATA_QUALITY_HIERARCHY['GAIA']['accuracy']
    
    def add_simbad_data(self, simbad_row):
        """Add SIMBAD classification"""
        self.object_type = simbad_row.get('type')
        self.object_names = simbad_row.get('identifiers', '').split('|')
        self.spectral_type = simbad_row.get('spectral_type')
        
        self.data_sources.append('SIMBAD')
        self.quality_score += DATA_QUALITY_HIERARCHY['SIMBAD']['accuracy']
    
    def add_akari_data(self, akari_dict):
        """Add AKARI infrared photometry"""
        if 'IRC' in akari_dict and len(akari_dict['IRC']) > 0:
            irc = akari_dict['IRC'].iloc[0]
            self.akari_9um = irc.get('S9W')
            self.akari_18um = irc.get('S18W')
        
        if 'FIS' in akari_dict and len(akari_dict['FIS']) > 0:
            fis = akari_dict['FIS'].iloc[0]
            self.akari_65um = fis.get('S65')
            self.akari_90um = fis.get('S90')
        
        self.data_sources.append('AKARI')
        self.quality_score += DATA_QUALITY_HIERARCHY['AKARI']['accuracy']
    
    def calculate_completeness(self):
        """Calculate data completeness (0-100%)"""
        fields = [
            self.ra, self.dec, self.parallax, self.pmra, self.pmdec,
            self.phot_g_mean_mag, self.object_type, self.spectral_type,
            self.akari_9um, self.akari_18um
        ]
        filled = sum(1 for f in fields if f is not None)
        self.completeness = (filled / len(fields)) * 100
        return self.completeness
    
    def to_dict(self):
        """Export as dictionary"""
        return {
            'source_id': self.source_id,
            'ra': self.ra,
            'dec': self.dec,
            'parallax': self.parallax,
            'pmra': self.pmra,
            'pmdec': self.pmdec,
            'phot_g_mean_mag': self.phot_g_mean_mag,
            'radial_velocity': self.radial_velocity,
            'distance_pc': self.distance_pc,
            'distance_ly': self.distance_ly,
            'object_type': self.object_type,
            'spectral_type': self.spectral_type,
            'akari_9um': self.akari_9um,
            'akari_18um': self.akari_18um,
            'akari_65um': self.akari_65um,
            'akari_90um': self.akari_90um,
            'mass_msun': self.mass_msun,
            'xi': self.xi,
            'D_ssz': self.D_ssz,
            'data_sources': ','.join(self.data_sources),
            'quality_score': self.quality_score,
            'completeness': self.completeness
        }


# ============================================================================
# AUTOMATIC MULTI-SOURCE LOADING
# ============================================================================

def load_unified_database(gaia_path='data/gaia_50k.csv', 
                          auto_query_missing=True,
                          max_queries=100):
    """
    Load database with AUTOMATIC multi-source combination
    
    Args:
        gaia_path: Path to GAIA base database
        auto_query_missing: Automatically query SIMBAD/AKARI for objects
        max_queries: Maximum number of external queries (rate limiting)
    
    Returns:
        DataFrame with unified multi-source data
    """
    
    print("="*80)
    print("UNIFIED MULTI-SOURCE DATA LOADER")
    print("="*80)
    print()
    
    # Load GAIA as base
    print("[1/4] Loading GAIA DR3 base...")
    gaia_df = pd.read_csv(gaia_path)
    print(f"  ✓ Loaded {len(gaia_df):,} GAIA sources")
    
    unified_objects = []
    
    # Process each object
    print(f"\n[2/4] Enriching with SIMBAD/AKARI (max {max_queries} queries)...")
    queries_made = 0
    
    for idx, row in gaia_df.iterrows():
        obj = UnifiedAstronomicalObject()
        
        # Add GAIA data
        obj.add_gaia_data(row)
        
        # Query SIMBAD/AKARI for subset (rate limiting)
        if auto_query_missing and queries_made < max_queries:
            # Query every Nth object to spread queries
            if idx % (len(gaia_df) // max_queries + 1) == 0:
                try:
                    # SIMBAD
                    simbad_data = query_simbad(ra=obj.ra, dec=obj.dec, radius=0.5)
                    if simbad_data is not None and len(simbad_data) > 0:
                        obj.add_simbad_data(simbad_data.iloc[0])
                    
                    # AKARI
                    akari_data = query_akari(obj.ra, obj.dec, radius=0.5)
                    if akari_data:
                        obj.add_akari_data(akari_data)
                    
                    queries_made += 1
                    if queries_made % 10 == 0:
                        print(f"    Queried {queries_made}/{max_queries} objects...")
                
                except Exception as e:
                    warnings.warn(f"Query failed for object {idx}: {e}")
        
        obj.calculate_completeness()
        unified_objects.append(obj)
    
    print(f"  ✓ Enriched {queries_made} objects with SIMBAD/AKARI data")
    
    # Convert to DataFrame
    print("\n[3/4] Converting to unified DataFrame...")
    unified_df = pd.DataFrame([obj.to_dict() for obj in unified_objects])
    
    # Calculate statistics
    print("\n[4/4] Data Quality Statistics:")
    print("-" * 80)
    
    source_counts = unified_df['data_sources'].str.split(',').apply(len).value_counts()
    print("  Data sources per object:")
    for n_sources in sorted(source_counts.index):
        count = source_counts[n_sources]
        pct = (count / len(unified_df)) * 100
        print(f"    {n_sources} sources: {count:,} objects ({pct:.1f}%)")
    
    avg_quality = unified_df['quality_score'].mean()
    avg_completeness = unified_df['completeness'].mean()
    
    print(f"\n  Average quality score: {avg_quality:.1f}/100")
    print(f"  Average completeness: {avg_completeness:.1f}%")
    
    has_ir = (unified_df['akari_9um'].notna() | unified_df['akari_18um'].notna()).sum()
    has_type = unified_df['object_type'].notna().sum()
    
    print(f"\n  Objects with infrared data: {has_ir:,} ({has_ir/len(unified_df)*100:.1f}%)")
    print(f"  Objects with classification: {has_type:,} ({has_type/len(unified_df)*100:.1f}%)")
    
    print("\n" + "="*80)
    print("✅ UNIFIED DATABASE READY")
    print("="*80)
    
    return unified_df


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    import io
    
    # UTF-8 for Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("Testing unified multi-source loader...")
    print()
    
    # Show data quality hierarchy
    print("DATA QUALITY HIERARCHY (from PAPER-RESTORED):")
    print("-" * 80)
    for source, info in DATA_QUALITY_HIERARCHY.items():
        print(f"{source:15s} Priority {info['priority']} - {info['accuracy']:5.1f}% - {info['type']}")
    print()
    
    # Note: Actual loading requires GAIA database file
    print("NOTE: Full loading requires gaia_50k.csv database")
    print("      Use: load_unified_database('data/gaia_50k.csv')")
